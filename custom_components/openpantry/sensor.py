from __future__ import annotations
from typing import Any
from homeassistant.components.sensor import SensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, add_entities: AddEntitiesCallback) -> None:
    coord = hass.data[DOMAIN][entry.entry_id]
    entities: list[SensorEntity] = [
        PantryExpirySensor(coord, entry.entry_id, i) for i in coord.all_items()
    ] + [PantryTotalsSensor(coord, "total_items"), PantryTotalsSensor(coord, "low_count")]
    add_entities(entities)

class PantryExpirySensor(CoordinatorEntity, SensorEntity):
    _attr_has_entity_name = True

    def __init__(self, coordinator, entry_id: str, item: dict[str, Any]) -> None:
        super().__init__(coordinator)
        self._item_id = item["id"]
        self._attr_unique_id = f"{entry_id}_{self._item_id}_next_expiry"
        self._attr_name = f"{item['name']} Next Expiry"

    @property
    def native_value(self) -> str | None:
        i = self.coordinator._find(self._item_id)
        if not i:
            return None
        expiries = i.get("expiries") or []
        return min(expiries) if expiries else None

class PantryTotalsSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, kind: str) -> None:
        super().__init__(coordinator)
        self._kind = kind
        self._attr_unique_id = f"openpantry_summary_{kind}"
        self._attr_name = (
            "Pantry Low Stock Count" if kind == "low_count" else "Pantry Total Items"
        )

    @property
    def native_value(self):
        items = self.coordinator.all_items()
        if self._kind == "low_count":
            return sum(
                1
                for i in items
                if i.get("par") is not None and i.get("quantity", 0.0) < i["par"]
            )
        return len(items)

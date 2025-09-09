from __future__ import annotations
from typing import Any
from homeassistant.components.number import NumberEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import PantryCoordinator

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, add_entities: AddEntitiesCallback) -> None:
    coord: PantryCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities: list[PantryQuantityNumber] = []

    for item in coord.all_items():
        entities.append(PantryQuantityNumber(coord, entry.entry_id, item))

    add_entities(entities)

class PantryQuantityNumber(CoordinatorEntity[PantryCoordinator], NumberEntity):
    _attr_has_entity_name = True

    def __init__(self, coordinator: PantryCoordinator, entry_id: str, item: dict[str, Any]) -> None:
        super().__init__(coordinator)
        self._item_id = item["id"]
        self._attr_unique_id = f"{entry_id}_{self._item_id}_quantity"
        self._attr_name = f"{item['name']} Quantity"
        self._attr_native_step = 0.1
        self._attr_native_min_value = 0.0
        self._attr_native_unit_of_measurement = item.get("unit")

    @property
    def native_value(self) -> float | None:
        i = self.coordinator._find(self._item_id)
        return i and i.get("quantity", 0.0)

    async def async_set_native_value(self, value: float) -> None:
        i = self.coordinator._find(self._item_id)
        if not i:
            return
        i["quantity"] = max(0.0, float(value))
        await self.coordinator.async_save()

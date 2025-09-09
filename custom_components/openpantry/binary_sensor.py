from __future__ import annotations
from typing import Any
from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorDeviceClass,
)
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, add_entities: AddEntitiesCallback) -> None:
    coord = hass.data[DOMAIN][entry.entry_id]
    add_entities([PantryLowSensor(coord, entry.entry_id, i) for i in coord.all_items()])

class PantryLowSensor(CoordinatorEntity, BinarySensorEntity):
    _attr_has_entity_name = True
    _attr_device_class = BinarySensorDeviceClass.PROBLEM

    def __init__(self, coordinator, entry_id: str, item: dict[str, Any]) -> None:
        super().__init__(coordinator)
        self._item_id = item["id"]
        self._attr_unique_id = f"{entry_id}_{self._item_id}_low"
        self._attr_name = f"{item['name']} Low Stock"

    @property
    def is_on(self) -> bool | None:
        i = self.coordinator._find(self._item_id)
        if not i:
            return None
        par = i.get("par")
        return par is not None and float(i.get("quantity", 0.0)) < float(par)

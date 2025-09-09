from __future__ import annotations
from datetime import timedelta
from typing import Any
import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.util import slugify

from .const import DOMAIN, EVENT_LOW, EVENT_RESTOCKED

_LOGGER = logging.getLogger(__name__)

def _earliest(exp: list[str]) -> str | None:
    return min(exp) if exp else None

class PantryCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    def __init__(self, hass: HomeAssistant, store) -> None:
        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=timedelta(minutes=1))
        self.store = store
        self.data: dict[str, Any] = {"items": []}
        self.entry_id: str | None = None

    async def async_load(self) -> None:
        self.data = await self.store.async_load()

    async def async_save(self) -> None:
        await self.store.async_save(self.data)
        await self.async_request_refresh()

    def _find(self, item_id: str) -> dict[str, Any] | None:
        return next((i for i in self.data["items"] if i["id"] == item_id), None)

    async def add_item(self, item: dict[str, Any]) -> dict[str, Any]:
        item["id"] = item.get("id") or slugify(item["name"])
        existing = self._find(item["id"])
        if existing:
            self.data["items"] = [i for i in self.data["items"] if i["id"] != item["id"]]
        self.data["items"].append(item)
        await self.async_save()
        return item

    async def adjust(self, item_id: str, delta: float, expiries: list[str] | None = None) -> None:
        i = self._find(item_id)
        if not i:
            raise ValueError(f"Item {item_id} not found")
        i["quantity"] = round(max(0.0, float(i.get("quantity", 0.0)) + float(delta)), 3)
        if expiries:
            i["expiries"] = (i.get("expiries") or []) + expiries
        await self.async_save()
        if delta > 0:
            self.hass.bus.async_fire(EVENT_RESTOCKED, {"id": item_id})
        if (par := i.get("par")) is not None and i["quantity"] < par:
            self.hass.bus.async_fire(EVENT_LOW, {"id": item_id})
            if i.get("link_shopping"):
                await self.hass.services.async_call(
                    "shopping_list", "add_item", {"name": i["name"]}
                )

    def all_items(self) -> list[dict[str, Any]]:
        return self.data.get("items", [])

    def earliest_expiry(self, item: dict[str, Any]) -> str | None:
        return _earliest(item.get("expiries") or [])

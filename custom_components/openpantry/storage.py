from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any
from homeassistant.helpers.storage import Store

@dataclass
class PantryItem:
    id: str
    name: str
    unit: str
    quantity: float = 0.0
    par: float | None = None
    location: str | None = None
    category: str | None = None
    barcode: str | None = None
    expiries: list[str] = field(default_factory=list)
    link_shopping: bool = False

class OpenPantryStore:
    def __init__(self, hass) -> None:
        self._store: Store = Store(hass, version=1, key="openpantry_items")

    async def async_load(self) -> dict[str, Any]:
        return (await self._store.async_load()) or {"items": []}

    async def async_save(self, data: dict[str, Any]) -> None:
        await self._store.async_save(data)

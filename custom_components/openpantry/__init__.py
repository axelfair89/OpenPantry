from __future__ import annotations
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType

from .const import DOMAIN, PLATFORMS
from .storage import OpenPantryStore
from .coordinator import PantryCoordinator

async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    store = OpenPantryStore(hass)
    coordinator = PantryCoordinator(hass, store)
    coordinator.entry_id = entry.entry_id
    await coordinator.async_load()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    _register_services(hass, coordinator)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unload_ok

def _register_services(hass: HomeAssistant, coord: PantryCoordinator) -> None:
    async def svc_add(call):
        item = {
            "name": call.data["name"],
            "unit": call.data["unit"],
            "par": call.data.get("par"),
            "location": call.data.get("location"),
            "category": call.data.get("category"),
            "barcode": call.data.get("barcode"),
            "quantity": 0.0,
            "expiries": [],
            "link_shopping": False,
        }
        await coord.add_item(item)
        if coord.entry_id:
            hass.async_create_task(hass.config_entries.async_reload(coord.entry_id))

    async def svc_consume(call):
        await coord.adjust(call.data["item_id"], -float(call.data["amount"]))

    async def svc_restock(call):
        await coord.adjust(
            call.data["item_id"], float(call.data["amount"]), call.data.get("expiries")
        )

    async def svc_set_par(call):
        item = next(i for i in coord.all_items() if i["id"] == call.data["item_id"])
        item["par"] = float(call.data["par"])
        await coord.async_save()

    async def svc_link_shopping(call):
        item = next(i for i in coord.all_items() if i["id"] == call.data["item_id"])
        enable = bool(call.data["enable"])
        item["link_shopping"] = enable
        await coord.async_save()
        if enable and item.get("par") is not None and item["quantity"] < item["par"]:
            await hass.services.async_call("shopping_list", "add_item", {"name": item["name"]})

    hass.services.async_register(DOMAIN, "add_item", svc_add)
    hass.services.async_register(DOMAIN, "consume", svc_consume)
    hass.services.async_register(DOMAIN, "restock", svc_restock)
    hass.services.async_register(DOMAIN, "set_par", svc_set_par)
    hass.services.async_register(DOMAIN, "link_shopping_list", svc_link_shopping)

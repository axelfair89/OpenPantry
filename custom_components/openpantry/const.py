from __future__ import annotations

DOMAIN = "openpantry"
PLATFORMS: list[str] = ["number", "binary_sensor", "sensor"]

STORAGE_KEY = "openpantry_items"
EVENT_LOW = f"{DOMAIN}_item_low"
EVENT_RESTOCKED = f"{DOMAIN}_item_restocked"

ATTR_NEXT_EXPIRY = "next_expiry"
ATTR_UNIT = "unit"
ATTR_PAR = "par"
ATTR_LOCATION = "location"
ATTR_CATEGORY = "category"
ATTR_BARCODE = "barcode"
ATTR_LINK_SHOPPING = "link_shopping"

CONF_ENTRY_TITLE = "Pantry"

# TODO(v0.2): options flow for item editing
# TODO(v0.2): webhook registration for barcode scans
# TODO(v0.2): Assist intents
# TODO(v0.2): Expiring soon configuration & sensor

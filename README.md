# OpenPantry

Pantry inventory tracking for Home Assistant with a bulk-buying vibe.

## Installation

1. In HACS, add this repository as a custom integration repository.
2. Install **OpenPantry** from HACS.
3. Restart Home Assistant and add the *OpenPantry* integration (`Configuration → Devices & services`).

## Services

- `openpantry.add_item`
- `openpantry.consume`
- `openpantry.restock`
- `openpantry.set_par`
- `openpantry.link_shopping_list`

See [`custom_components/openpantry/services.yaml`](custom_components/openpantry/services.yaml) for fields.

## Sample Lovelace view

```yaml
title: Pantry
path: pantry
cards:
  - type: entity-filter
    state_filter: ["on"]
    entities: []
    card:
      type: entities
      title: Low stock
  - type: entities
    title: Summary
    entities:
      - sensor.pantry_total_items
      - sensor.pantry_low_stock_count
```

## Blueprint

A sample automation to notify and add to the shopping list when low stock is detected is in [`example/blueprints/automation/pantry_low_stock.yaml`](example/blueprints/automation/pantry_low_stock.yaml).

## Roadmap

- Options flow with table editor for items
- Webhook registration for barcode scans
- Assist intents
- Expiring soon configuration & sensor

## Developer test snippet

```yaml
script:
  test_openpantry:
    sequence:
      - service: openpantry.add_item
        data: { name: "Head & Shoulders 1L", unit: "bottle", par: 2 }
      - service: openpantry.restock
        data: { item_id: "head_shoulders_1l", amount: 3, expiries: ["2027-03-15","2026-02-01"] }
      - delay: "00:00:01"
      - service: openpantry.consume
        data: { item_id: "head_shoulders_1l", amount: 2 }
```

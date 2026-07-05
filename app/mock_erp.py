"""
Stand-in for a real ERP/inventory system. Swap this for actual API calls
(or a small SQLite table) once the pipeline logic is proven out -- the
pipeline only depends on the two function signatures below, not on how
the data is stored.
"""

_CATALOG = {
    "widget-a": {"description": "Standard widget, type A", "unit_price_usd": 12.50, "stock": 500},
    "widget-b": {"description": "Heavy-duty widget, type B", "unit_price_usd": 34.00, "stock": 120},
    "bracket-steel": {"description": "Steel mounting bracket", "unit_price_usd": 8.75, "stock": 800},
    "sensor-temp": {"description": "Temperature sensor module", "unit_price_usd": 22.00, "stock": 60},
    "cable-10m": {"description": "10m shielded cable", "unit_price_usd": 15.00, "stock": 300},
}


def lookup_price(sku_or_description: str) -> dict | None:
    """Fuzzy-ish lookup: exact key match first, then substring match on description."""
    key = sku_or_description.strip().lower().replace(" ", "-")
    if key in _CATALOG:
        return {"sku": key, **_CATALOG[key]}

    for sku, info in _CATALOG.items():
        if sku_or_description.strip().lower() in info["description"].lower():
            return {"sku": sku, **info}

    return None


def check_stock(sku: str, quantity: int) -> bool:
    item = _CATALOG.get(sku)
    if not item:
        return False
    return item["stock"] >= quantity
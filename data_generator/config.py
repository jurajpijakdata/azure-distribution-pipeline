"""Central configuration for the synthetic data generator.

All tunable settings live here, so the generator code never contains
hardcoded numbers. The data is fully synthetic: the company, warehouses,
customers and orders are fictional.
"""
from dataclasses import dataclass
from datetime import date
from pathlib import Path

# --- Reproducibility ---------------------------------------------------------
# Same seed -> same data on every machine and every run.
SEED: int = 2026

# --- Paths -------------------------------------------------------------------
# Resolved from this file's location, so the script works no matter which
# folder it is started from.
PROJECT_ROOT: Path = Path(__file__).resolve().parent.parent
OUTPUT_DIR: Path = PROJECT_ROOT / "data" / "raw"

# --- Time range --------------------------------------------------------------
START_DATE: date = date(2025, 10, 1)
END_DATE: date = date(2026, 9, 30)


# --- Warehouses --------------------------------------------------------------
@dataclass(frozen=True)
class Warehouse:
    """One warehouse and how its ERP exports data."""

    code: str
    city: str
    country: str
    currency: str
    export_format: str   # "csv" or "xlsx"
    orders_per_workday: int


WAREHOUSES: tuple[Warehouse, ...] = (
    Warehouse("BA", "Bratislava", "SK", "EUR", "csv", 35),
    Warehouse("ZA", "Žilina", "SK", "EUR", "csv", 20),
    Warehouse("KE", "Košice", "SK", "EUR", "xlsx", 20),
    Warehouse("BRN", "Brno", "CZ", "CZK", "csv", 20),
)

# --- Customers ---------------------------------------------------------------
N_CUSTOMERS: int = 400

# Share of each customer type among all customers (must sum to 1.0).
CUSTOMER_TYPE_WEIGHTS: dict[str, float] = {
    "Electrician": 0.60,
    "Construction": 0.15,
    "Retail shop": 0.25,
}

# --- Order behaviour (assumptions, documented in docs/decisions.md) ----------
# Number of lines (different products) on one order, per customer type.
LINES_PER_ORDER: dict[str, tuple[int, int]] = {
    "Electrician": (1, 5),
    "Construction": (3, 12),
    "Retail shop": (2, 8),
}

# Quantity ranges: (min, max) for products sold in metres vs in pieces.
QTY_METRES: dict[str, tuple[int, int]] = {
    "Electrician": (50, 300),
    "Construction": (500, 3000),
    "Retail shop": (100, 500),
}
QTY_PIECES: dict[str, tuple[int, int]] = {
    "Electrician": (1, 20),
    "Construction": (20, 200),
    "Retail shop": (10, 50),
}

# Small consumables (boxes etc.) are bought in packs, not single pieces.
PACK_SIZE_CONSUMABLES: int = 25

# Seasonality: multiplier on order volume per month (building season peaks
# in spring and summer, December is quiet).
MONTH_SEASONALITY: dict[int, float] = {
    1: 0.70, 2: 0.75, 3: 0.95, 4: 1.10, 5: 1.20, 6: 1.20,
    7: 1.10, 8: 1.00, 9: 1.10, 10: 1.05, 11: 0.90, 12: 0.60,
}

# --- Money -------------------------------------------------------------------
# Sale price = cost price * random markup in this range.
MARKUP_RANGE: tuple[float, float] = (1.25, 1.55)

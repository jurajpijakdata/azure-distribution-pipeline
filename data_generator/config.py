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

# CZ branch sells from its own CZK price list, set once at this rate.
# (Reporting later converts CZK -> EUR with real daily ECB rates.)
CZK_PRICE_LIST_RATE: float = 25.0

# Customer discount off list price, per customer type (min, max).
DISCOUNT_RANGE: dict[str, tuple[float, float]] = {
    "Electrician": (0.03, 0.08),
    "Construction": (0.08, 0.15),
    "Retail shop": (0.05, 0.10),
}

# How much each customer type prefers each product category (relative weight).
CATEGORY_PREFERENCE: dict[str, dict[str, float]] = {
    "Electrician": {"Cables": 3, "Circuit breakers": 3, "Switches & sockets": 3,
                    "Installation material": 3, "Lighting": 2,
                    "Distribution boards": 1, "Tools": 1},
    "Construction": {"Cables": 5, "Circuit breakers": 3, "Switches & sockets": 2,
                     "Installation material": 3, "Lighting": 2,
                     "Distribution boards": 2, "Tools": 0.5},
    "Retail shop": {"Cables": 1, "Circuit breakers": 1, "Switches & sockets": 5,
                    "Installation material": 3, "Lighting": 5,
                    "Distribution boards": 0.3, "Tools": 2},
}

# Upper limit on pieces per line for categories nobody buys in bulk.
QTY_CAP_BY_CATEGORY: dict[str, int] = {"Tools": 5, "Distribution boards": 30}

# Share of order lines that are later returned (credit note, negative quantity).
RETURN_RATE: float = 0.015
RETURN_DELAY_DAYS: tuple[int, int] = (3, 30)

# Simplified list of main public holidays in the data range (no deliveries).
HOLIDAYS: dict[str, set[date]] = {
    "SK": {date(2025, 11, 1), date(2025, 12, 24), date(2025, 12, 25), date(2025, 12, 26),
           date(2026, 1, 1), date(2026, 1, 6), date(2026, 4, 3), date(2026, 4, 6),
           date(2026, 5, 1), date(2026, 7, 5), date(2026, 8, 29)},
    "CZ": {date(2025, 10, 28), date(2025, 11, 17), date(2025, 12, 24), date(2025, 12, 25),
           date(2025, 12, 26), date(2026, 1, 1), date(2026, 4, 3), date(2026, 4, 6),
           date(2026, 5, 1), date(2026, 5, 8), date(2026, 7, 6)},
}

# --- Shipments ---------------------------------------------------------------
# Fictional carriers only - never real company names.
# INJECTED PATTERN (documented in docs/decisions.md): Courier Beta is late
# more often and all carriers are slower in winter. This exists so the
# pipeline and dashboard can be shown to detect it - it is not a finding.
CARRIER_LATE_PROB: dict[str, float] = {
    "Own fleet": 0.04,
    "Courier Alpha": 0.06,
    "Courier Beta": 0.15,
}
COURIER_SHARE: dict[str, float] = {"Courier Alpha": 0.6, "Courier Beta": 0.4}
WINTER_MONTHS: set[int] = {12, 1, 2}
WINTER_LATE_MULTIPLIER: float = 1.8
LATE_EXTRA_DAYS: tuple[int, int] = (1, 4)
PICKING_DAYS: tuple[int, int] = (0, 1)       # order -> ship, in workdays
# Transit (ship -> delivered) and promise (order -> promised), in workdays.
# Promise = max picking + max transit, so shipments are late only when a
# delay event happens - which keeps the injected pattern controlled.
TRANSIT_DAYS: dict[str, tuple[int, int]] = {
    "Own fleet": (1, 1), "Courier Alpha": (1, 2), "Courier Beta": (1, 2),
}
PROMISE_DAYS: dict[str, int] = {"Own fleet": 2, "Courier Alpha": 3, "Courier Beta": 3}

# --- Inventory ---------------------------------------------------------------
SUPPLIER_LEAD_DAYS: tuple[int, int] = (3, 7)  # reorder -> goods arrive
SAFETY_DAYS: int = 7                          # extra days of demand kept as buffer
ORDER_UP_TO_DAYS: int = 30                    # replenish up to 30 days of demand
MIN_STOCK: dict[str, int] = {"m": 100, "pcs": 5}   # slow movers still stocked

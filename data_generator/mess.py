"""Plant known data problems into the clean tables and record every one.

Each planted problem gets a row in the manifest (issue type, table, key,
column, original and new value). The manifest is the answer key: later
tests prove the pipeline detects every issue listed there.
"""
import logging
import random
from datetime import date, timedelta

import pandas as pd

import config

logger = logging.getLogger(__name__)

CARRIER_VARIANTS: dict[str, tuple[str, ...]] = {
    "Own fleet": ("own fleet", "Own Fleet ", "OWN FLEET"),
    "Courier Alpha": ("courier alpha", "Alpha", "COURIER ALPHA"),
    "Courier Beta": ("courier beta", "Beta", "Courier  Beta"),
}


class Manifest:
    """Collects one record per planted problem."""

    def __init__(self) -> None:
        self.rows: list[dict] = []

    def add(self, issue: str, table: str, warehouse: str, key: str,
            column: str, original: object, injected: object) -> None:
        self.rows.append({"issue_type": issue, "table": table, "warehouse_code": warehouse,
                          "record_key": key, "column": column,
                          "original_value": "" if original is None else str(original),
                          "injected_value": "" if injected is None else str(injected)})

    def to_frame(self) -> pd.DataFrame:
        return pd.DataFrame(self.rows)


def _pick(df: pd.DataFrame, rate: float, rng: random.Random, used: set,
          mask: pd.Series | None = None) -> list:
    """Choose row labels for one issue, never reusing a row already changed."""
    pool = [i for i in (df.index[mask] if mask is not None else df.index) if i not in used]
    k = min(len(pool), max(1, round(len(df) * rate)))
    chosen = rng.sample(pool, k)
    used.update(chosen)
    return chosen


def _order_key(row: pd.Series) -> str:
    return f"{row['order_no']}/{row['line_no']}"


def _sku_typo(sku: str, rng: random.Random) -> str:
    """Typical manual-entry mistakes in a product code."""
    kind = rng.choice(["lower", "spaces", "o_for_0"])
    if kind == "lower":
        return sku.lower()
    if kind == "spaces":
        return f" {sku}  "
    return sku.replace("0", "O", 1) if "0" in sku else sku.lower()


def _impossible_date(d: date, style_warehouse: str) -> str:
    """A calendar day that does not exist, written in the warehouse's format."""
    day = 30 if d.month == 2 else 31
    if style_warehouse == "ZA":
        return f"{d.year}-{d.month:02d}-{day}"
    return f"{day:02d}.{d.month:02d}.{d.year}"


def mess_orders(orders: pd.DataFrame, rng: random.Random, m: Manifest) -> pd.DataFrame:
    """Plant row-level problems into order lines."""
    df = orders.copy()

    def record(issue: str, i: int, column: str, new: object) -> None:
        m.add(issue, "orders", df.at[i, "warehouse_code"], _order_key(df.loc[i]),
              column, df.at[i, column] if column in df.columns else "", new)

    for col in ("quantity", "order_date", "sku", "customer_id", "unit_price"):
        df[col] = df[col].astype(object)
    r, used = config.MESS_RATES, set()
    sale = df["order_type"] == "SALE"

    for i in _pick(df, r["sku_typo"], rng, used):
        new = _sku_typo(df.at[i, "sku"], rng)
        record("sku_typo", i, "sku", new)
        df.at[i, "sku"] = new
    for i in _pick(df, r["unknown_sku"], rng, used):
        new = df.at[i, "sku"] + "-OLD"          # discontinued code still used by a clerk
        record("unknown_sku", i, "sku", new)
        df.at[i, "sku"] = new
    for i in _pick(df, r["missing_customer"], rng, used):
        record("missing_customer", i, "customer_id", None)
        df.at[i, "customer_id"] = None
    for i in _pick(df, r["missing_price"], rng, used):
        record("missing_price", i, "unit_price", None)
        df.at[i, "unit_price"] = None
    for i in _pick(df, r["qty_as_text"], rng, used, mask=sale):
        unit = "ks" if df.at[i, "unit"] == "pcs" else "m"
        new = f"{df.at[i, 'quantity']} {unit}"
        record("qty_as_text", i, "quantity", new)
        df.at[i, "quantity"] = new
    for i in _pick(df, r["negative_sale_qty"], rng, used, mask=sale):
        new = -df.at[i, "quantity"]              # sign error: line_total stays positive
        record("negative_sale_qty", i, "quantity", new)
        df.at[i, "quantity"] = new
    dd_mm = df["warehouse_code"].isin(["BA", "BRN", "ZA"])
    for i in _pick(df, r["impossible_date"], rng, used, mask=dd_mm):
        new = _impossible_date(df.at[i, "order_date"], df.at[i, "warehouse_code"])
        record("impossible_date", i, "order_date", new)
        df.at[i, "order_date"] = new

    # Exact duplicates of untouched rows, inserted right after the original.
    dup_idx = _pick(df, r["duplicate_row"], rng, used)
    for i in dup_idx:
        m.add("duplicate_row", "orders", df.at[i, "warehouse_code"], _order_key(df.loc[i]),
              "*", "", "exact copy")
    df = pd.concat([df, df.loc[dup_idx]]).sort_index(kind="stable").reset_index(drop=True)
    return df


def mess_shipments(shipments: pd.DataFrame, rng: random.Random, m: Manifest) -> pd.DataFrame:
    """Plant problems into shipments: impossible dates order, dirty carrier names."""
    df = shipments.copy()
    for col in ("delivered_date", "carrier"):
        df[col] = df[col].astype(object)
    r, used = config.MESS_RATES, set()
    delivered = (df["status"] == "DELIVERED") & df["ship_date"].notna()
    for i in _pick(df, r["delivered_before_shipped"], rng, used, mask=delivered):
        new = df.at[i, "ship_date"] - timedelta(days=rng.randint(1, 3))
        m.add("delivered_before_shipped", "shipments", df.at[i, "warehouse_code"], df.at[i, "shipment_id"],
              "delivered_date", df.at[i, "delivered_date"], new)
        df.at[i, "delivered_date"] = new
    for i in _pick(df, r["carrier_variant"], rng, used):
        new = rng.choice(CARRIER_VARIANTS[df.at[i, "carrier"]])
        m.add("carrier_variant", "shipments", df.at[i, "warehouse_code"], df.at[i, "shipment_id"],
              "carrier", df.at[i, "carrier"], new)
        df.at[i, "carrier"] = new
    return df


def mess_inventory(inventory: pd.DataFrame, rng: random.Random, m: Manifest) -> pd.DataFrame:
    """Plant negative stock rows and remove one full snapshot week."""
    df = inventory.copy()
    used: set = set()
    for i in _pick(df, config.MESS_RATES["negative_stock"], rng, used):
        new = -rng.randint(1, 50)                # booking error in the ERP
        key = f"{df.at[i, 'snapshot_date']}/{df.at[i, 'sku']}"
        m.add("negative_stock", "inventory", df.at[i, "warehouse_code"], key,
              "qty_on_hand", df.at[i, "qty_on_hand"], new)
        df.at[i, "qty_on_hand"] = new
    wh, day = config.MISSING_INVENTORY_WEEK
    gone = (df["warehouse_code"] == wh) & (df["_date"] == day)
    m.add("missing_inventory_week", "inventory", wh, str(day), "*", f"{gone.sum()} rows", "removed")
    return df[~gone]


def inject_mess(tables: dict[str, pd.DataFrame], rng: random.Random) -> tuple[dict, pd.DataFrame]:
    """Return messy copies of the tables plus the manifest of every change."""
    m = Manifest()
    messy = dict(tables)
    messy["orders"] = mess_orders(tables["orders"], rng, m)
    messy["shipments"] = mess_shipments(tables["shipments"], rng, m)
    messy["inventory"] = mess_inventory(tables["inventory"], rng, m)
    manifest = m.to_frame()
    logger.info("Planted %d problems: %s", len(manifest), manifest["issue_type"].value_counts().to_dict())
    return messy, manifest

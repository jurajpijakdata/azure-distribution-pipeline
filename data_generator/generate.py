"""Run the whole synthetic data generator.

Usage (from the project root):
    python data_generator/generate.py

Steps: generate clean tables -> plant known problems -> write files the way
each warehouse ERP exports them. Outputs:
    data/raw/                           full data set (ignored by git)
    data/manifest/injected_issues.csv   answer key of every planted problem
    sample_data/                        one-week sample (committed)
All data is synthetic.
"""
import logging
import random
import shutil
import sys
from datetime import timedelta
from pathlib import Path

import pandas as pd

import config
from customers import generate_customers
from export import export_master, export_monthly, file_name
from inventory import generate_inventory
from mess import inject_mess
from orders import generate_orders
from products import generate_products
from shipments import generate_shipments

logger = logging.getLogger("generate")

MANIFEST_DIR: Path = config.PROJECT_ROOT / "data" / "manifest"
SAMPLE_DIR: Path = config.PROJECT_ROOT / "sample_data"
SAMPLE_DAYS: int = 7


def _reset_dir(path: Path) -> None:
    """Delete and recreate an output folder (only folders inside the project)."""
    if config.PROJECT_ROOT not in path.resolve().parents:
        raise ValueError(f"Refusing to delete a folder outside the project: {path}")
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True)


def _add_internal_dates(df: pd.DataFrame, date_col: str) -> pd.DataFrame:
    """Keep the true date in `_date`/`_month` before any date gets messed up."""
    df = df.copy()
    df["_date"] = df[date_col]
    df["_month"] = pd.to_datetime(df[date_col]).dt.strftime("%Y-%m")
    return df


def _export_all(tables: dict[str, pd.DataFrame], out_dir: Path) -> int:
    """Write master data and monthly per-warehouse files. Returns file count."""
    export_master(tables["products"], tables["customers"], out_dir)
    n = sum(export_monthly(tables[t], t, out_dir) for t in ("orders", "shipments", "inventory"))
    return n + 2


def _reexport_month(out_dir: Path, manifest: pd.DataFrame) -> pd.DataFrame:
    """Simulate a clerk exporting the same month twice (identical second file)."""
    wh, month = config.REEXPORT
    original = out_dir / file_name(wh, "orders", month)
    copy = original.with_name(original.stem + "_reexport" + original.suffix)
    shutil.copyfile(original, copy)
    row = {"issue_type": "reexported_month", "table": "orders", "warehouse_code": wh,
           "record_key": copy.name, "column": "*", "original_value": original.name,
           "injected_value": "identical second file"}
    return pd.concat([manifest, pd.DataFrame([row])], ignore_index=True)


def _schema_change_note(manifest: pd.DataFrame) -> pd.DataFrame:
    """Record the ERP update (renamed + added column) in the manifest."""
    wh, month = config.SCHEMA_CHANGE
    row = {"issue_type": "schema_change", "table": "orders", "warehouse_code": wh,
           "record_key": f"from {month}", "column": "qty / vat_rate",
           "original_value": "qty", "injected_value": "quantity + new column vat_rate"}
    return pd.concat([manifest, pd.DataFrame([row])], ignore_index=True)


def build_tables(seed: int = config.SEED) -> tuple[dict, dict, pd.DataFrame]:
    """Generate clean tables, then messy copies plus the manifest (no files written).

    Returns:
        (clean tables, messy tables, manifest). Used by main() and by the tests.
    """
    rng = random.Random(seed)
    products = generate_products(rng)
    customers = generate_customers(rng)
    orders = generate_orders(rng, products, customers)
    orders["product_name"] = orders["sku"].map(dict(zip(products["sku"], products["product_name"])))
    shipments = generate_shipments(rng, orders, customers)
    inventory = generate_inventory(rng, orders, products)

    clean = {
        "products": products,
        "customers": customers,
        "orders": _add_internal_dates(orders, "order_date"),
        "shipments": _add_internal_dates(shipments, "promised_date"),
        "inventory": _add_internal_dates(inventory, "snapshot_date"),
    }
    messy, manifest = inject_mess(clean, rng)
    return clean, messy, manifest


def main() -> int:
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s")
    _, messy, manifest = build_tables()

    _reset_dir(config.OUTPUT_DIR)
    n_files = _export_all(messy, config.OUTPUT_DIR)
    manifest = _reexport_month(config.OUTPUT_DIR, manifest)
    manifest = _schema_change_note(manifest)
    logger.info("Full data set: %d files in %s", n_files + 1, config.OUTPUT_DIR)

    _reset_dir(MANIFEST_DIR)
    manifest.to_csv(MANIFEST_DIR / "injected_issues.csv", index=False, encoding="utf-8")
    logger.info("Manifest: %d planted problems, %d types -> %s",
                len(manifest), manifest["issue_type"].nunique(), MANIFEST_DIR)

    # One-week sample for git: same styles and structure, taken from the messy data.
    end = config.START_DATE + timedelta(days=SAMPLE_DAYS - 1)
    sample = dict(messy)
    sample["orders"] = messy["orders"][messy["orders"]["_date"] <= end]
    sample["shipments"] = messy["shipments"][messy["shipments"]["order_no"].isin(sample["orders"]["order_no"])]
    sample["inventory"] = messy["inventory"][messy["inventory"]["_date"] <= end]
    _reset_dir(SAMPLE_DIR)
    n_sample = _export_all(sample, SAMPLE_DIR)
    logger.info("Sample (%d days): %d files in %s", SAMPLE_DAYS, n_sample, SAMPLE_DIR)
    return 0


if __name__ == "__main__":
    sys.exit(main())

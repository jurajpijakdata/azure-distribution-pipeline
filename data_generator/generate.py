"""Run the whole synthetic data generator.

Usage (from the project root):
    python data_generator/generate.py

Writes the full data set to data/raw/ (ignored by git) and a one-week
sample to sample_data/ (committed). All data is synthetic.
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
from export import export_master, export_monthly
from inventory import generate_inventory
from orders import generate_orders
from products import generate_products
from shipments import generate_shipments

logger = logging.getLogger("generate")

SAMPLE_DIR: Path = config.PROJECT_ROOT / "sample_data"
SAMPLE_DAYS: int = 7


def _reset_dir(path: Path) -> None:
    """Delete and recreate an output folder (only folders inside the project)."""
    if config.PROJECT_ROOT not in path.resolve().parents:
        raise ValueError(f"Refusing to delete a folder outside the project: {path}")
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True)


def _export_all(tables: dict[str, pd.DataFrame], out_dir: Path) -> int:
    """Write master data and monthly per-warehouse files. Returns file count."""
    export_master(tables["products"], tables["customers"], out_dir)
    n = export_monthly(tables["orders"], "orders", "order_date", out_dir)
    n += export_monthly(tables["shipments"], "shipments", "promised_date", out_dir)
    n += export_monthly(tables["inventory"], "inventory", "snapshot_date", out_dir)
    return n + 2


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(name)s | %(message)s")
    rng = random.Random(config.SEED)

    products = generate_products(rng)
    customers = generate_customers(rng)
    orders = generate_orders(rng, products, customers)
    names = dict(zip(products["sku"], products["product_name"]))
    orders["product_name"] = orders["sku"].map(names)
    shipments = generate_shipments(rng, orders, customers)
    inventory = generate_inventory(rng, orders, products)

    tables = {"products": products, "customers": customers, "orders": orders,
              "shipments": shipments, "inventory": inventory}

    _reset_dir(config.OUTPUT_DIR)
    n_files = _export_all(tables, config.OUTPUT_DIR)
    logger.info("Full data set: %d files in %s", n_files, config.OUTPUT_DIR)

    # One-week sample for git: same styles, same structure, tiny size.
    end = config.START_DATE + timedelta(days=SAMPLE_DAYS - 1)
    sample = dict(tables)
    sample["orders"] = orders[orders["order_date"] <= end]
    sample["shipments"] = shipments[shipments["order_no"].isin(sample["orders"]["order_no"])]
    sample["inventory"] = inventory[inventory["snapshot_date"] <= end]
    _reset_dir(SAMPLE_DIR)
    n_sample = _export_all(sample, SAMPLE_DIR)
    logger.info("Sample (%d days): %d files in %s", SAMPLE_DAYS, n_sample, SAMPLE_DIR)
    return 0


if __name__ == "__main__":
    sys.exit(main())

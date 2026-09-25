"""Simulate stock per warehouse and product; export weekly snapshots.

Stock moves day by day: minus sales, plus returns, plus supplier deliveries.
A simple reorder rule keeps stock from going negative, so the clean data is
consistent with the orders. Slow movers keep a minimum stock and pile up.
"""
import logging
import random
from collections import defaultdict
from datetime import timedelta

import pandas as pd

import config

logger = logging.getLogger(__name__)


def generate_inventory(rng: random.Random, orders: pd.DataFrame,
                       products: pd.DataFrame) -> pd.DataFrame:
    """Build weekly (Friday) stock snapshots.

    Args:
        rng: Seeded random generator.
        orders: Output of generate_orders() - sales reduce, returns add stock.
        products: Output of generate_products().

    Returns:
        One row per snapshot date x warehouse x product.
    """
    unit = dict(zip(products["sku"], products["unit"]))
    n_days = (config.END_DATE - config.START_DATE).days + 1

    # Daily movement per (warehouse, sku, date): sales negative, returns positive.
    moves: dict[tuple, int] = defaultdict(int)
    for wh, sku, d, qty in orders[["warehouse_code", "sku", "order_date", "quantity"]].itertuples(index=False):
        moves[(wh, sku, d)] -= qty           # SALE qty > 0 reduces, RETURN qty < 0 adds

    sales = orders[orders["order_type"] == "SALE"]
    avg_daily = (sales.groupby(["warehouse_code", "sku"])["quantity"].sum() / n_days).to_dict()

    rows = []
    for wh in config.WAREHOUSES:
        for sku in products["sku"]:
            demand = avg_daily.get((wh.code, sku), 0.0)
            reorder_point = demand * (config.SUPPLIER_LEAD_DAYS[1] + config.SAFETY_DAYS)
            order_up_to = max(demand * config.ORDER_UP_TO_DAYS, config.MIN_STOCK[unit[sku]])
            on_hand = round(order_up_to * rng.uniform(0.6, 1.0))
            pending: dict = {}                # arrival date -> quantity

            d = config.START_DATE
            while d <= config.END_DATE:
                on_hand += pending.pop(d, 0)
                on_hand += moves.get((wh.code, sku, d), 0)
                if on_hand < 0:               # emergency delivery, same day
                    on_hand = 0
                if on_hand <= reorder_point and not pending:
                    arrival = d + timedelta(days=rng.randint(*config.SUPPLIER_LEAD_DAYS))
                    pending[arrival] = round(order_up_to - on_hand)
                if d.weekday() == 4:          # Friday snapshot
                    rows.append({"snapshot_date": d, "warehouse_code": wh.code, "sku": sku,
                                 "qty_on_hand": on_hand, "unit": unit[sku]})
                d += timedelta(days=1)

    inventory = pd.DataFrame(rows)
    logger.info("Generated %d inventory snapshot rows", len(inventory))
    return inventory

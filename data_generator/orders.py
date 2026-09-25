"""Generate order lines (sales and returns) for all warehouses.

Grain: one row = one product line on one order document.
Sales have positive quantities; returns are separate documents with
negative quantities that point back to the original order.
"""
import logging
import random
from datetime import timedelta
from decimal import Decimal

import pandas as pd

import config
from calendar_utils import next_workday, workdays
from products import to_money

logger = logging.getLogger(__name__)


def _quantity(product: pd.Series, ctype: str, rng: random.Random) -> int:
    """Pick a realistic quantity for one order line."""
    if product["unit"] == "m":
        lo, hi = config.QTY_METRES[ctype]
        return round(rng.randint(lo, hi), -1) or 10   # cable is cut in 10 m steps
    lo, hi = config.QTY_PIECES[ctype]
    if product["is_consumable"]:
        return config.PACK_SIZE_CONSUMABLES * rng.randint(1, max(1, hi // 5))
    qty = rng.randint(lo, hi)
    cap = config.QTY_CAP_BY_CATEGORY.get(product["category"])
    return min(qty, cap) if cap else qty


def _pick_products(weights: list[float], k: int, rng: random.Random) -> list[int]:
    """Weighted sampling of k different product positions (no repeats)."""
    chosen: set[int] = set()
    k = min(k, sum(1 for w in weights if w > 0))
    while len(chosen) < k:
        chosen.add(rng.choices(range(len(weights)), weights)[0])
    return sorted(chosen)


def generate_orders(rng: random.Random, products: pd.DataFrame,
                    customers: pd.DataFrame) -> pd.DataFrame:
    """Build all order lines for the configured date range.

    Args:
        rng: Seeded random generator.
        products: Output of generate_products().
        customers: Output of generate_customers() (needs `_order_weight`).

    Returns:
        Order lines with Decimal prices in the warehouse's currency.
    """
    # Some products are fast movers, most sell occasionally.
    popularity = [rng.paretovariate(1.2) for _ in range(len(products))]
    product_weights = {
        ctype: [pop * prefs[cat] for pop, cat in zip(popularity, products["category"])]
        for ctype, prefs in config.CATEGORY_PREFERENCE.items()
    }
    discount = {cid: rng.uniform(*config.DISCOUNT_RANGE[ct])
                for cid, ct in zip(customers["customer_id"], customers["customer_type"])}

    rows: list[dict] = []
    for wh in config.WAREHOUSES:
        wh_customers = customers[customers["home_warehouse_code"] == wh.code]
        seq = 0
        for day in workdays(config.START_DATE, config.END_DATE, wh.country):
            active = wh_customers[wh_customers["created_date"] <= day]
            if active.empty:
                continue
            mean = wh.orders_per_workday * config.MONTH_SEASONALITY[day.month]
            n_orders = max(0, round(rng.gauss(mean, mean * 0.2)))
            buyers = rng.choices(list(active.index), list(active["_order_weight"]), k=n_orders)
            for idx in buyers:
                cust = customers.loc[idx]
                ctype = cust["customer_type"]
                seq += 1
                order_no = f"{wh.code}-{seq:06d}"
                n_lines = rng.randint(*config.LINES_PER_ORDER[ctype])
                for line_no, p_idx in enumerate(
                        _pick_products(product_weights[ctype], n_lines, rng), start=1):
                    p = products.iloc[p_idx]
                    price_eur = p["list_price_eur"] * (1 - Decimal(str(discount[cust["customer_id"]])))
                    unit_price = (to_money(float(price_eur) * config.CZK_PRICE_LIST_RATE)
                                  if wh.currency == "CZK" else to_money(float(price_eur)))
                    qty = _quantity(p, ctype, rng)
                    rows.append({
                        "order_no": order_no, "line_no": line_no, "order_type": "SALE",
                        "original_order_no": None, "order_date": day,
                        "warehouse_code": wh.code, "customer_id": cust["customer_id"],
                        "sku": p["sku"], "quantity": qty, "unit": p["unit"],
                        "unit_price": unit_price, "currency": wh.currency,
                        "line_total": unit_price * qty,
                    })
        logger.info("Warehouse %s: %d orders", wh.code, seq)

    orders = pd.DataFrame(rows)
    returns = _generate_returns(orders, rng)
    result = pd.concat([orders, returns], ignore_index=True)
    result = result.sort_values(["order_date", "order_no", "line_no"], ignore_index=True)
    logger.info("Generated %d order lines (%d sales, %d returns)",
                len(result), len(orders), len(returns))
    return result


def _generate_returns(orders: pd.DataFrame, rng: random.Random) -> pd.DataFrame:
    """Create return documents (negative quantities) for a share of sale lines.

    Return documents are numbered per warehouse in date order, like a real ERP.
    """
    country = {wh.code: wh.country for wh in config.WAREHOUSES}
    rows = []
    for line in orders.to_dict("records"):
        if rng.random() >= config.RETURN_RATE:
            continue
        ret_date = next_workday(
            line["order_date"] + timedelta(days=rng.randint(*config.RETURN_DELAY_DAYS)),
            country[line["warehouse_code"]])
        if ret_date > config.END_DATE:
            continue
        # Usually part of the line comes back, sometimes all of it.
        qty = -max(1, round(line["quantity"] * rng.choice([0.1, 0.25, 0.5, 1.0])))
        rows.append({**line, "line_no": 1, "order_type": "RETURN",
                     "original_order_no": line["order_no"], "order_date": ret_date,
                     "quantity": qty, "line_total": line["unit_price"] * qty})

    returns = pd.DataFrame(rows).sort_values(["warehouse_code", "order_date", "original_order_no"])
    seq = returns.groupby("warehouse_code").cumcount() + 1
    returns["order_no"] = returns["warehouse_code"] + "-R" + seq.map("{:05d}".format)
    return returns


if __name__ == "__main__":
    from customers import generate_customers
    from products import generate_products

    logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(name)s | %(message)s")
    rng = random.Random(config.SEED)
    prods = generate_products(rng)
    custs = generate_customers(rng)
    df = generate_orders(rng, prods, custs)
    print(df.head(8).to_string(index=False))
    print(df[df["order_type"] == "RETURN"].head(3).to_string(index=False))

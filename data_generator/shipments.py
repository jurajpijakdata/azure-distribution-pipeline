"""Generate one shipment per sale order.

Local customers get the own fleet, others a courier. The promised date
includes picking and transit time, so a shipment is late only when a delay
event happens. Delays follow the INJECTED pattern in config (Courier Beta
and winter are worse) - see docs/decisions.md.
"""
import logging
import random

import pandas as pd

import config
from calendar_utils import add_workdays

logger = logging.getLogger(__name__)


def generate_shipments(rng: random.Random, orders: pd.DataFrame,
                       customers: pd.DataFrame) -> pd.DataFrame:
    """Build shipments for all SALE orders.

    Args:
        rng: Seeded random generator.
        orders: Output of generate_orders().
        customers: Output of generate_customers().

    Returns:
        One row per shipment. Shipments not yet delivered at the end of the
        data range have status IN_TRANSIT and an empty delivered_date.
    """
    wh_info = {wh.code: wh for wh in config.WAREHOUSES}
    cust_city = dict(zip(customers["customer_id"], customers["city"]))
    couriers = list(config.COURIER_SHARE)
    courier_weights = list(config.COURIER_SHARE.values())

    headers = (orders[orders["order_type"] == "SALE"]
               .drop_duplicates("order_no")[["order_no", "order_date", "warehouse_code", "customer_id"]])

    rows = []
    for i, o in enumerate(headers.to_dict("records"), start=1):
        wh = wh_info[o["warehouse_code"]]
        local = cust_city[o["customer_id"]] == wh.city
        carrier = "Own fleet" if local else rng.choices(couriers, courier_weights)[0]

        ship_date = add_workdays(o["order_date"], rng.randint(*config.PICKING_DAYS), wh.country)
        promised = add_workdays(o["order_date"], config.PROMISE_DAYS[carrier], wh.country)
        delivered = add_workdays(ship_date, rng.randint(*config.TRANSIT_DAYS[carrier]), wh.country)

        late_prob = config.CARRIER_LATE_PROB[carrier]
        if o["order_date"].month in config.WINTER_MONTHS:
            late_prob *= config.WINTER_LATE_MULTIPLIER
        if rng.random() < late_prob:
            delivered = add_workdays(delivered, rng.randint(*config.LATE_EXTRA_DAYS), wh.country)

        in_transit = delivered > config.END_DATE
        rows.append({
            "shipment_id": f"SH-{o['warehouse_code']}-{i:06d}",
            "order_no": o["order_no"],
            "warehouse_code": o["warehouse_code"],
            "carrier": carrier,
            "ship_date": ship_date if ship_date <= config.END_DATE else None,
            "promised_date": promised,
            "delivered_date": None if in_transit else delivered,
            "status": "IN_TRANSIT" if in_transit else "DELIVERED",
        })

    shipments = pd.DataFrame(rows)
    logger.info("Generated %d shipments (%d in transit)", len(shipments),
                (shipments["status"] == "IN_TRANSIT").sum())
    return shipments

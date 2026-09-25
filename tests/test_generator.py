"""Tests for the synthetic data generator.

Unit tests check small helpers with hand-made inputs. Data tests generate the
full data set once and check the rules the pipeline relies on: unique keys,
valid references, correct signs, and that every planted problem is recorded.
"""
from datetime import date
from decimal import Decimal

import pandas as pd
import pytest

import config
from calendar_utils import add_workdays, is_workday, next_workday
from export import STYLES, format_value, style_for, write_table
from generate import build_tables
from mess import _impossible_date
from products import to_money


# --- Unit tests: helpers -----------------------------------------------------

@pytest.mark.parametrize("value, expected", [
    (0.125, Decimal("0.13")),      # commercial rounding, not banker's rounding
    (2.675, Decimal("2.68")),      # float 2.675 is 2.67499..., str() keeps 2.675
    (-1.005, Decimal("-1.01")),
    (10, Decimal("10.00")),
])
def test_to_money_rounds_half_up(value, expected):
    assert to_money(value) == expected


@pytest.mark.parametrize("warehouse, value, expected", [
    ("BA", Decimal("1234.56"), "1234,56"),
    ("BRN", Decimal("1234.56"), "1 234,56"),
    ("BRN", Decimal("-1234.56"), "-1 234,56"),   # sign must survive formatting
    ("ZA", Decimal("1234.56"), "1234.56"),
    ("BA", 12, "12"),
    ("BA", None, ""),
    ("BA", date(2025, 10, 1), "01.10.2025"),
    ("ZA", date(2025, 10, 1), "2025-10-01"),
])
def test_format_value_per_warehouse_style(warehouse, value, expected):
    assert format_value(value, STYLES[warehouse]) == expected


def test_add_workdays_skips_weekend():
    friday = date(2025, 10, 3)
    assert add_workdays(friday, 1, "SK") == date(2025, 10, 6)


def test_add_workdays_skips_holiday():
    before_christmas = date(2025, 12, 23)          # Tue; 24-26 Dec are holidays
    assert add_workdays(before_christmas, 1, "SK") == date(2025, 12, 29)


def test_next_workday_keeps_a_workday():
    assert next_workday(date(2025, 10, 1), "SK") == date(2025, 10, 1)


def test_country_specific_holidays():
    assert not is_workday(date(2025, 10, 28), "CZ")   # Czech national holiday
    assert is_workday(date(2025, 10, 28), "SK")


@pytest.mark.parametrize("d", [date(2026, 2, 10), date(2025, 11, 5), date(2026, 4, 20)])
def test_impossible_date_really_does_not_exist(d):
    text = _impossible_date(d, "BA")
    with pytest.raises(ValueError):
        pd.to_datetime(text, format="%d.%m.%Y")


def test_schema_change_only_from_configured_month():
    wh, month = config.SCHEMA_CHANGE
    before = style_for(wh, "2026-02")
    after = style_for(wh, month)
    assert before.columns["orders"]["quantity"] == "qty"
    assert after.columns["orders"]["quantity"] == "quantity"
    assert "vat_rate" in after.extra_columns["orders"]


# --- Data tests: full generated data set --------------------------------------

@pytest.fixture(scope="module")
def data():
    """Generate the full data set once for all data tests (takes ~10 s)."""
    return build_tables()


def test_generation_is_reproducible(data):
    clean, messy, manifest = data
    clean2, messy2, manifest2 = build_tables()
    pd.testing.assert_frame_equal(clean["orders"], clean2["orders"])
    pd.testing.assert_frame_equal(messy["shipments"], messy2["shipments"])
    pd.testing.assert_frame_equal(manifest, manifest2)


def test_products_unique_and_profitable(data):
    p = data[0]["products"]
    assert p["sku"].is_unique
    assert (p["list_price_eur"] > p["cost_eur"]).all()
    assert p["cost_eur"].map(type).eq(Decimal).all()       # money is never float


def test_order_key_is_unique(data):
    o = data[0]["orders"]
    assert not o.duplicated(["order_no", "line_no"]).any()


def test_sales_positive_returns_negative(data):
    o = data[0]["orders"]
    assert (o.loc[o["order_type"] == "SALE", "quantity"] > 0).all()
    assert (o.loc[o["order_type"] == "RETURN", "quantity"] < 0).all()


def test_returns_point_to_earlier_real_orders(data):
    o = data[0]["orders"]
    sale_dates = o[o["order_type"] == "SALE"].groupby("order_no")["order_date"].first()
    ret = o[o["order_type"] == "RETURN"]
    assert ret["original_order_no"].isin(sale_dates.index).all()
    assert (ret["order_date"] > ret["original_order_no"].map(sale_dates)).all()


def test_line_total_equals_quantity_times_price(data):
    o = data[0]["orders"]
    assert (o["unit_price"] * o["quantity"] == o["line_total"]).all()


def test_no_orders_on_weekends_or_holidays(data):
    o = data[0]["orders"]
    country = {wh.code: wh.country for wh in config.WAREHOUSES}
    assert all(is_workday(d, country[wh]) for d, wh in zip(o["order_date"], o["warehouse_code"]))


def test_customers_order_only_after_creation(data):
    clean = data[0]
    created = dict(zip(clean["customers"]["customer_id"], clean["customers"]["created_date"]))
    o = clean["orders"][clean["orders"]["order_type"] == "SALE"]
    assert (o["order_date"] >= o["customer_id"].map(created)).all()


def test_currency_matches_warehouse(data):
    o = data[0]["orders"]
    expected = {wh.code: wh.currency for wh in config.WAREHOUSES}
    assert (o["currency"] == o["warehouse_code"].map(expected)).all()


def test_one_shipment_per_sale_order(data):
    clean = data[0]
    sale_orders = set(clean["orders"].loc[clean["orders"]["order_type"] == "SALE", "order_no"])
    s = clean["shipments"]
    assert s["order_no"].is_unique
    assert set(s["order_no"]) == sale_orders


def test_clean_shipments_are_delivered_after_shipping(data):
    s = data[0]["shipments"]
    done = s[s["status"] == "DELIVERED"]
    assert (done["delivered_date"] >= done["ship_date"]).all()
    assert set(s["carrier"]) <= set(config.CARRIER_LATE_PROB)   # fictional carriers only


def test_clean_inventory_never_negative(data):
    inv = data[0]["inventory"]
    assert (inv["qty_on_hand"] >= 0).all()
    assert not inv.duplicated(["snapshot_date", "warehouse_code", "sku"]).any()


# --- Data tests: planted problems ---------------------------------------------

def test_every_planned_problem_type_is_planted(data):
    manifest = data[2]
    expected = set(config.MESS_RATES) | {"missing_inventory_week"}
    assert expected <= set(manifest["issue_type"])


def test_mess_does_not_change_the_clean_tables(data):
    clean, _, _ = data
    assert clean["orders"]["sku"].isin(clean["products"]["sku"]).all()
    assert clean["orders"]["customer_id"].notna().all()


def test_duplicates_match_manifest(data):
    clean, messy, manifest = data
    n_dup = (manifest["issue_type"] == "duplicate_row").sum()
    assert len(messy["orders"]) == len(clean["orders"]) + n_dup


def test_manifest_values_are_really_in_messy_data(data):
    _, messy, manifest = data
    o = messy["orders"]
    lookup = dict(zip(o["order_no"] + "/" + o["line_no"].astype(str), o["sku"]))
    typos = manifest[manifest["issue_type"] == "sku_typo"]
    assert all(lookup[k] == v for k, v in zip(typos["record_key"], typos["injected_value"]))


def test_missing_inventory_week_is_removed(data):
    wh, day = config.MISSING_INVENTORY_WEEK
    inv = data[1]["inventory"]
    assert not ((inv["warehouse_code"] == wh) & (inv["_date"] == day)).any()


# --- Export tests --------------------------------------------------------------

def test_brno_file_is_windows_1250(tmp_path):
    df = pd.DataFrame({"Název": ["Istič B16 1-pól ľ ô"], "Cena": [Decimal("1234.50")]})
    path = tmp_path / "brn.csv"
    write_table(df, path, STYLES["BRN"])
    raw = path.read_bytes()
    with pytest.raises(UnicodeDecodeError):
        raw.decode("utf-8")                                  # not UTF-8 ...
    assert "Istič B16 1-pól ľ ô;1 234,50" in raw.decode("cp1250")   # ... but cp1250


def test_excel_export_is_byte_reproducible(tmp_path):
    df = pd.DataFrame({"Kod": ["A"], "Mnozstvo": [1]})
    a, b = tmp_path / "a.xlsx", tmp_path / "b.xlsx"
    write_table(df, a, STYLES["KE"])
    write_table(df, b, STYLES["KE"])
    assert a.read_bytes() == b.read_bytes()

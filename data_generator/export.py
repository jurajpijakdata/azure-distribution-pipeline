"""Write the generated tables as files, the way each warehouse ERP exports them.

Every warehouse has its own export style: separator, decimal mark, encoding,
date format, language of column names and code values. This is where the
"four different ERP setups" of the scenario come from. The data itself is
clean here - planted problems are added in a separate step.
"""
import logging
from dataclasses import dataclass, field, replace
from datetime import date
from decimal import Decimal
from pathlib import Path

import pandas as pd
from openpyxl import Workbook

import config

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ExportStyle:
    """How one ERP writes its files."""

    file_format: str                 # "csv" or "xlsx"
    sep: str = ";"
    decimal: str = ","
    thousands: str = ""              # e.g. " " -> 1 234,56
    encoding: str = "utf-8"
    date_format: str = "%d.%m.%Y"
    columns: dict[str, dict[str, str]] = field(default_factory=dict)   # table -> {internal: exported}
    values: dict[str, dict[str, str]] = field(default_factory=dict)    # internal column -> {value: exported}
    title_rows: tuple[str, ...] = ()  # xlsx only: report title lines above the header
    extra_columns: dict[str, dict[str, str]] = field(default_factory=dict)  # table -> {column: constant}


ORDER_COLS = ["order_no", "line_no", "order_type", "original_order_no", "order_date",
              "warehouse_code", "customer_id", "sku", "product_name", "quantity", "unit",
              "unit_price", "currency", "line_total"]
SHIP_COLS = ["shipment_id", "order_no", "warehouse_code", "carrier", "ship_date",
             "promised_date", "delivered_date", "status"]
INV_COLS = ["snapshot_date", "warehouse_code", "sku", "qty_on_hand", "unit"]

STYLES: dict[str, ExportStyle] = {
    # Bratislava HQ: Slovak ERP, UTF-8 with BOM, ; and decimal comma.
    "BA": ExportStyle(
        file_format="csv", encoding="utf-8-sig",
        columns={
            "orders": dict(zip(ORDER_COLS, [
                "Číslo dokladu", "Riadok", "Typ dokladu", "Pôvodný doklad", "Dátum", "Sklad",
                "Zákazník", "Kód tovaru", "Názov tovaru", "Množstvo", "MJ", "Jedn. cena",
                "Mena", "Spolu"])),
            "shipments": dict(zip(SHIP_COLS, [
                "Číslo zásielky", "Číslo dokladu", "Sklad", "Dopravca", "Dátum expedície",
                "Sľúbený termín", "Dátum doručenia", "Stav"])),
            "inventory": dict(zip(INV_COLS, ["Dátum", "Sklad", "Kód tovaru", "Stav zásob", "MJ"])),
        },
        values={"order_type": {"SALE": "Predaj", "RETURN": "Vrátenie"},
                "unit": {"pcs": "ks", "m": "m"},
                "status": {"DELIVERED": "Doručené", "IN_TRANSIT": "Na ceste"}},
    ),
    # Žilina: different, English-language ERP, plain CSV with dots.
    "ZA": ExportStyle(
        file_format="csv", sep=",", decimal=".", date_format="%Y-%m-%d",
        columns={
            "orders": {"order_no": "order_id", "line_no": "line", "order_type": "doc_type",
                       "original_order_no": "ref_order", "order_date": "date",
                       "warehouse_code": "warehouse", "customer_id": "customer",
                       "sku": "item_code", "quantity": "qty", "unit": "uom",
                       "unit_price": "price", "currency": "currency", "line_total": "total"},
            "shipments": {"shipment_id": "shipment_id", "order_no": "order_id",
                          "warehouse_code": "warehouse", "carrier": "carrier",
                          "ship_date": "shipped", "promised_date": "promised",
                          "delivered_date": "delivered", "status": "status"},
            "inventory": {"snapshot_date": "date", "warehouse_code": "warehouse",
                          "sku": "item_code", "qty_on_hand": "on_hand", "unit": "uom"},
        },
    ),
    # Košice: Excel report with title rows, Slovak names without diacritics.
    "KE": ExportStyle(
        file_format="xlsx",
        columns={
            "orders": {"order_no": "Cislo objednavky", "line_no": "Polozka", "order_type": "Typ",
                       "original_order_no": "Povodny doklad", "order_date": "Datum",
                       "warehouse_code": "Sklad", "customer_id": "Odberatel", "sku": "Kod",
                       "quantity": "Mnozstvo", "unit": "MJ", "unit_price": "Cena",
                       "currency": "Mena", "line_total": "Suma"},
            "shipments": {"shipment_id": "Zasielka", "order_no": "Cislo objednavky",
                          "warehouse_code": "Sklad", "carrier": "Prepravca",
                          "ship_date": "Odoslane", "promised_date": "Termin",
                          "delivered_date": "Dorucene", "status": "Stav"},
            "inventory": {"snapshot_date": "Datum", "warehouse_code": "Sklad", "sku": "Kod",
                          "qty_on_hand": "Mnozstvo", "unit": "MJ"},
        },
        values={"order_type": {"SALE": "P", "RETURN": "V"},
                "unit": {"pcs": "ks", "m": "m"},
                "status": {"DELIVERED": "Dorucene", "IN_TRANSIT": "Na ceste"}},
        title_rows=("Export z ERP - Sklad Kosice", "Vygenerovane automaticky", ""),
    ),
    # Brno: Czech ERP, Windows-1250 encoding, space as thousands separator, CZK.
    "BRN": ExportStyle(
        file_format="csv", thousands=" ", encoding="cp1250",
        columns={
            "orders": dict(zip(ORDER_COLS, [
                "Číslo objednávky", "Řádek", "Typ dokladu", "Původní doklad", "Datum", "Sklad",
                "Odběratel", "Kód zboží", "Název zboží", "Množství", "MJ", "Cena za jednotku",
                "Měna", "Celkem"])),
            "shipments": dict(zip(SHIP_COLS, [
                "Číslo zásilky", "Číslo objednávky", "Sklad", "Dopravce", "Datum expedice",
                "Slíbený termín", "Datum doručení", "Stav"])),
            "inventory": dict(zip(INV_COLS, ["Datum", "Sklad", "Kód zboží", "Stav skladu", "MJ"])),
        },
        values={"order_type": {"SALE": "Prodej", "RETURN": "Vratka"},
                "unit": {"pcs": "ks", "m": "m"},
                "status": {"DELIVERED": "Doručeno", "IN_TRANSIT": "V přepravě"}},
    ),
}



def style_for(warehouse: str, month: str) -> ExportStyle:
    """Export style of a warehouse in a given month (YYYY-MM).

    Models an ERP update: from config.SCHEMA_CHANGE the warehouse renames
    one column and appends a new one.
    """
    style = STYLES[warehouse]
    changed_wh, from_month = config.SCHEMA_CHANGE
    if warehouse != changed_wh or month < from_month:
        return style
    columns = dict(style.columns)
    columns["orders"] = {**columns["orders"], "quantity": "quantity"}
    return replace(style, columns=columns, extra_columns={"orders": {"vat_rate": "23"}})


def file_name(warehouse: str, table: str, month: str) -> str:
    """Relative path of one export file, e.g. BA/orders_2025-10.csv."""
    return f"{warehouse}/{table}_{month}.{STYLES[warehouse].file_format}"


# Master data comes from the central (HQ) ERP in Bratislava style.
MASTER_STYLE = ExportStyle(file_format="csv", encoding="utf-8-sig")


def format_value(value: object, style: ExportStyle) -> str:
    """Turn one cell into text exactly as the ERP would write it."""
    if value is None or (not isinstance(value, (str, Decimal, date)) and pd.isna(value)):
        return ""
    if isinstance(value, bool):
        return "1" if value else "0"
    if isinstance(value, date):
        return value.strftime(style.date_format)
    if isinstance(value, (Decimal, int)):
        text = f"{value:,}" if style.thousands else str(value)   # "," marks thousands here
        text = text.replace(",", "\x00").replace(".", style.decimal)
        return text.replace("\x00", style.thousands)
    return str(value)


def _prepare(df: pd.DataFrame, table: str, style: ExportStyle) -> pd.DataFrame:
    """Select, recode and rename columns for one style."""
    mapping = style.columns[table]
    out = df[[c for c in mapping if c in df.columns]].copy()
    for col, codes in style.values.items():
        if col in out.columns:
            out[col] = out[col].map(lambda v, c=codes: c.get(v, v))
    out = out.rename(columns=mapping)
    for col, constant in style.extra_columns.get(table, {}).items():
        out[col] = constant
    return out


def write_table(df: pd.DataFrame, path: Path, style: ExportStyle) -> None:
    """Write a prepared table as CSV text or as an Excel report."""
    path.parent.mkdir(parents=True, exist_ok=True)
    if style.file_format == "xlsx":
        wb = Workbook()
        ws = wb.active
        ws.title = "Export"
        for line in style.title_rows:
            ws.append([line])
        ws.append(list(df.columns))
        for row in df.itertuples(index=False):
            # Excel stores numbers as numbers and dates as dates.
            ws.append([float(v) if isinstance(v, Decimal)
                       else None if not isinstance(v, (str, date)) and pd.isna(v)
                       else v for v in row])
        wb.save(path)
    else:
        text = df.map(lambda v: format_value(v, style))
        text.to_csv(path, sep=style.sep, index=False, encoding=style.encoding, lineterminator="\r\n")
    logger.debug("Wrote %s (%d rows)", path, len(df))


def export_monthly(df: pd.DataFrame, table: str, out_dir: Path) -> int:
    """Write one file per warehouse per month. Returns the number of files.

    Uses the internal `_month` column, because the visible date column may
    contain planted invalid dates.
    """
    n_files = 0
    for (wh, month), part in df.groupby(["warehouse_code", "_month"]):
        style = style_for(wh, month)
        write_table(_prepare(part, table, style), out_dir / file_name(wh, table, month), style)
        n_files += 1
    return n_files


def export_master(products: pd.DataFrame, customers: pd.DataFrame, out_dir: Path) -> None:
    """Write product and customer lists from the central ERP."""
    write_table(products, out_dir / "master" / "products.csv", MASTER_STYLE)
    public = customers[[c for c in customers.columns if not c.startswith("_")]]
    write_table(public, out_dir / "master" / "customers.csv", MASTER_STYLE)

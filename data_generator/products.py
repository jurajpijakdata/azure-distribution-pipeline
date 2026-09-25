"""Generate the product catalogue of the fictional wholesaler.

Products are built from category templates (e.g. breaker curve x rating x
poles), so the catalogue looks like a real electrical wholesaler without
typing hundreds of rows by hand. Brand names are invented or omitted on
purpose - no real manufacturer is referenced.
"""
import logging
import random
from decimal import ROUND_HALF_UP, Decimal

import pandas as pd

import config

logger = logging.getLogger(__name__)

CENT = Decimal("0.01")


def to_money(value: float) -> Decimal:
    """Round a float to a 2-decimal Decimal (commercial rounding)."""
    return Decimal(str(value)).quantize(CENT, rounding=ROUND_HALF_UP)


def _cables() -> list[dict]:
    rows = []
    # (cross-section label, cost EUR per metre)
    for size, cost in [("3x1,5", 0.62), ("3x2,5", 0.98), ("5x1,5", 1.05),
                       ("5x2,5", 1.62), ("5x4", 2.85), ("5x6", 4.10), ("5x10", 6.90)]:
        rows.append(("CAB-CYKYJ-" + size.replace(",", "."), f"Kábel CYKY-J {size}", cost))
    for size, cost in [("2x1,5", 0.45), ("3x1,5", 0.60)]:
        rows.append(("CAB-CYKYO-" + size.replace(",", "."), f"Kábel CYKY-O {size}", cost))
    for size, cost in [("3x1,5", 0.85), ("3x2,5", 1.30)]:
        rows.append(("CAB-CGSG-" + size.replace(",", "."), f"Kábel gumový CGSG {size}", cost))
    colours = {"BU": "modrý", "BK": "čierny", "BN": "hnedý", "GNYE": "zeleno-žltý"}
    for size, cost in [("1,5", 0.18), ("2,5", 0.27), ("4", 0.42), ("6", 0.71), ("10", 1.15)]:
        for code, colour in colours.items():
            rows.append((f"CAB-CYA-{size.replace(',', '.')}-{code}",
                         f"Vodič CYA {size} {colour}", cost))
    rows.append(("CAB-UTP-C6", "Dátový kábel UTP Cat6", 0.38))
    return [{"sku": s, "product_name": n, "category": "Cables", "unit": "m",
             "is_consumable": False, "base_cost": c} for s, n, c in rows]


def _conduits() -> list[dict]:
    rows = []
    for dia, cost in [(16, 0.22), (20, 0.29), (25, 0.41), (32, 0.62)]:
        rows.append((f"CON-FLEX-{dia}", f"Elektroinštalačná rúrka ohybná {dia} mm", cost))
    return [{"sku": s, "product_name": n, "category": "Installation material", "unit": "m",
             "is_consumable": False, "base_cost": c} for s, n, c in rows]


def _breakers() -> list[dict]:
    rows = []
    for curve in ("B", "C"):
        for amps in (6, 10, 13, 16, 20, 25, 32, 40):
            for poles, cost in ((1, 3.30), (3, 13.50)):
                rows.append((f"BRK-{curve}{amps}-{poles}P",
                             f"Istič {curve}{amps} {poles}-pól", cost + amps * 0.02))
    for amps in (25, 40, 63):
        for poles, cost in ((2, 19.0), (4, 27.0)):
            rows.append((f"RCD-{amps}-30-{poles}P",
                         f"Prúdový chránič {amps}A/30mA {poles}-pól", cost + amps * 0.05))
    for curve_amps in ("B10", "B16", "C16"):
        rows.append((f"RCBO-{curve_amps}-30", f"Istič s chráničom {curve_amps}/30mA", 24.50))
    return [{"sku": s, "product_name": n, "category": "Circuit breakers", "unit": "pcs",
             "is_consumable": False, "base_cost": c} for s, n, c in rows]


def _switches_sockets() -> list[dict]:
    rows = []
    series = {"CLS": ("Classic", 1.00), "NOV": ("Nova", 1.35), "ELG": ("Elegant", 1.90)}
    colours = {"WH": "biela", "IV": "slonová kosť", "AN": "antracit"}
    items = [("SW1", "Vypínač č.1", 2.10), ("SW5", "Prepínač sériový č.5", 2.80),
             ("SW6", "Prepínač striedavý č.6", 2.60), ("SW7", "Prepínač krížový č.7", 3.90),
             ("SOC1", "Zásuvka jednoduchá", 2.20), ("SOC2", "Zásuvka dvojitá", 3.90),
             ("FR1", "Rámik 1-násobný", 0.90), ("FR2", "Rámik 2-násobný", 1.60),
             ("FR3", "Rámik 3-násobný", 2.30)]
    for s_code, (s_name, factor) in series.items():
        for i_code, i_name, cost in items:
            for c_code, c_name in colours.items():
                rows.append((f"WD-{s_code}-{i_code}-{c_code}",
                             f"{i_name} {s_name} {c_name}", cost * factor))
    return [{"sku": s, "product_name": n, "category": "Switches & sockets", "unit": "pcs",
             "is_consumable": False, "base_cost": c} for s, n, c in rows]


def _consumables() -> list[dict]:
    rows = [("BOX-KU68-1", "Krabica prístrojová KU 68", 0.18),
            ("BOX-KU68-2", "Krabica prístrojová KU 68 dvojitá", 0.45),
            ("BOX-KO8", "Krabica odbočná KO 8", 0.55),
            ("BOX-KU68-HW", "Krabica do dutých stien KU 68", 0.32),
            ("TRM-2X25", "Svorka bezskrutková 2x2,5", 0.09),
            ("TRM-3X25", "Svorka bezskrutková 3x2,5", 0.11),
            ("TRM-5X25", "Svorka bezskrutková 5x2,5", 0.16),
            ("CLP-CAB-5-8", "Príchytka káblová 5-8 mm", 0.03),
            ("CLP-CAB-9-12", "Príchytka káblová 9-12 mm", 0.04),
            ("DWL-8", "Hmoždinka 8 mm", 0.02),
            ("TAP-PVC-BK", "Izolačná páska PVC čierna", 0.40)]
    return [{"sku": s, "product_name": n, "category": "Installation material", "unit": "pcs",
             "is_consumable": True, "base_cost": c} for s, n, c in rows]


def _lighting() -> list[dict]:
    rows = []
    for base, watts in (("E27", (6, 9, 10, 13)), ("E14", (5, 7)), ("GU10", (5, 7))):
        for w in watts:
            rows.append((f"LED-{base}-{w}W", f"LED žiarovka {base} {w}W", 0.90 + w * 0.08))
    for size, watts in (("30x30", (24,)), ("60x60", (36, 40))):
        for w in watts:
            rows.append((f"LED-PNL-{size}-{w}W", f"LED panel {size} {w}W", 8.0 + w * 0.25))
    for w in (20, 30, 50, 100):
        rows.append((f"LED-FLD-{w}W", f"LED reflektor {w}W IP65", 5.0 + w * 0.14))
    rows.append(("LED-STRIP-5M", "LED pásik 5 m teplá biela", 6.50))
    return [{"sku": s, "product_name": n, "category": "Lighting", "unit": "pcs",
             "is_consumable": False, "base_cost": c} for s, n, c in rows]


def _boards() -> list[dict]:
    rows = []
    for modules in (12, 24, 36, 48, 72):
        rows.append((f"DB-{modules}-FL", f"Rozvodnica {modules} modulov pod omietku",
                     8.0 + modules * 0.60))
        rows.append((f"DB-{modules}-SF", f"Rozvodnica {modules} modulov na omietku",
                     7.0 + modules * 0.55))
    return [{"sku": s, "product_name": n, "category": "Distribution boards", "unit": "pcs",
             "is_consumable": False, "base_cost": c} for s, n, c in rows]


def _tools() -> list[dict]:
    rows = [("TL-STRIP", "Odizolovacie kliešte", 9.60),
            ("TL-CRIMP", "Lisovacie kliešte na dutinky", 16.80),
            ("TL-PLIERS", "Kombinované kliešte VDE", 11.20),
            ("TL-CUTTER", "Štípacie kliešte VDE", 10.40),
            ("TL-SCRW-SET", "Sada skrutkovačov VDE 6 ks", 21.00),
            ("TL-TESTER", "Skúšačka napätia dvojpólová", 18.50),
            ("TL-MULTI", "Multimeter digitálny", 24.00),
            ("TL-KNIFE", "Nôž na odizolovanie káblov", 12.30),
            ("TL-LEVEL", "Vodováha 60 cm", 7.90),
            ("TL-DRILL-68", "Vykružovačka 68 mm", 13.50)]
    return [{"sku": s, "product_name": n, "category": "Tools", "unit": "pcs",
             "is_consumable": False, "base_cost": c} for s, n, c in rows]


def generate_products(rng: random.Random) -> pd.DataFrame:
    """Build the product catalogue.

    Args:
        rng: Seeded random generator, so the output is reproducible.

    Returns:
        One row per product with sku, name, category, unit, consumable flag,
        cost price and list price (both Decimal, EUR).
    """
    templates = (_cables() + _conduits() + _breakers() + _switches_sockets()
                 + _consumables() + _lighting() + _boards() + _tools())
    rows = []
    for t in templates:
        # +-5 % noise so prices do not look perfectly formula-made.
        cost = to_money(t["base_cost"] * rng.uniform(0.95, 1.05))
        price = to_money(float(cost) * rng.uniform(*config.MARKUP_RANGE))
        rows.append({"sku": t["sku"], "product_name": t["product_name"],
                     "category": t["category"], "unit": t["unit"],
                     "is_consumable": t["is_consumable"],
                     "cost_eur": cost, "list_price_eur": price})

    products = pd.DataFrame(rows)
    if products["sku"].duplicated().any():
        raise ValueError("Duplicate SKUs in product templates")
    logger.info("Generated %d products in %d categories",
                len(products), products["category"].nunique())
    return products


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(name)s | %(message)s")
    df = generate_products(random.Random(config.SEED))
    print(df.groupby("category").size().to_string())
    print(df.sample(8, random_state=1).to_string(index=False))

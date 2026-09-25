"""Generate the fictional customer base.

Customers are electricians (sole traders), construction companies and
retail shops in SK and CZ. Names and addresses come from Faker and are
fictional; e-mails use reserved example domains so they can never reach
a real person.
"""
import logging
import random
from datetime import timedelta

import pandas as pd
from faker import Faker

import config

logger = logging.getLogger(__name__)

# City -> (country, nearest warehouse, weight, postal code prefixes).
# Weight = relative number of customers, roughly following city size.
# Prefixes keep postal codes consistent with the city.
CITIES: dict[str, tuple[str, str, int, tuple[str, ...]]] = {
    "Bratislava": ("SK", "BA", 30, ("811", "821", "831", "841", "851")),
    "Trnava": ("SK", "BA", 8, ("917",)),
    "Nitra": ("SK", "BA", 8, ("949",)),
    "Trenčín": ("SK", "ZA", 6, ("911",)),
    "Žilina": ("SK", "ZA", 10, ("010",)),
    "Martin": ("SK", "ZA", 5, ("036",)),
    "Banská Bystrica": ("SK", "ZA", 8, ("974",)),
    "Košice": ("SK", "KE", 16, ("040",)),
    "Prešov": ("SK", "KE", 9, ("080",)),
    "Poprad": ("SK", "KE", 4, ("058",)),
    "Brno": ("CZ", "BRN", 20, ("602", "612", "615", "623")),
    "Olomouc": ("CZ", "BRN", 6, ("779",)),
    "Zlín": ("CZ", "BRN", 5, ("760",)),
}

COMPANY_PREFIX = ("Stav", "Elektro", "Monta", "Inštal", "Volt", "Kábel", "Tech")
COMPANY_SUFFIX = ("plus", "servis", "tech", "invest", "system", "pro", "trade")
SHOP_WORDS = ("Svetlo", "Iskra", "Kontakt", "Zásuvka", "Obvod", "Prúd")


def _customer_name(ctype: str, city: str, fake: Faker, rng: random.Random) -> str:
    """Build a realistic-looking but invented business name."""
    if ctype == "Electrician":
        return f"{fake.first_name_male()} {fake.last_name_male()} - Elektro"
    if ctype == "Construction":
        legal = "s.r.o." if CITIES[city][0] == "SK" else "spol. s r.o."
        return f"{rng.choice(COMPANY_PREFIX)}{rng.choice(COMPANY_SUFFIX)} {legal}"
    return f"Elektro {rng.choice(SHOP_WORDS)} {city}"


def generate_customers(rng: random.Random) -> pd.DataFrame:
    """Build the customer table.

    Args:
        rng: Seeded random generator, so the output is reproducible.

    Returns:
        One row per customer. The column `_order_weight` is internal: it
        controls how often a customer orders (a few big, many small ones)
        and must be dropped before the data is exported.
    """
    fakers = {"SK": Faker("sk_SK"), "CZ": Faker("cs_CZ")}
    for f in fakers.values():
        f.seed_instance(rng.randint(0, 10**9))

    cities = list(CITIES)
    city_weights = [CITIES[c][2] for c in cities]
    types = list(config.CUSTOMER_TYPE_WEIGHTS)
    type_weights = list(config.CUSTOMER_TYPE_WEIGHTS.values())

    rows = []
    for i in range(1, config.N_CUSTOMERS + 1):
        city = rng.choices(cities, city_weights)[0]
        country, warehouse, _, prefixes = CITIES[city]
        ctype = rng.choices(types, type_weights)[0]
        fake = fakers[country]
        rows.append({
            "customer_id": f"C{i:05d}",
            "customer_name": _customer_name(ctype, city, fake, rng),
            "customer_type": ctype,
            "street": fake.street_address(),
            "postal_code": f"{rng.choice(prefixes)} {rng.choice(('01', '04', '05', '08'))}",
            "city": city,
            "country": country,
            "email": f"customer{i:05d}@example.com",
            "home_warehouse_code": warehouse,
            # Some customers existed before the data range, some join during it.
            "created_date": config.START_DATE + timedelta(days=rng.randint(-900, 300)),
            # Pareto-like activity: most customers order rarely, a few very often.
            "_order_weight": rng.paretovariate(1.5),
        })

    customers = pd.DataFrame(rows)
    logger.info("Generated %d customers: %s", len(customers),
                customers["customer_type"].value_counts().to_dict())
    return customers


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(name)s | %(message)s")
    df = generate_customers(random.Random(config.SEED))
    print(df.groupby(["country", "home_warehouse_code"]).size().to_string())
    print(df.drop(columns="_order_weight").sample(6, random_state=1).to_string(index=False))

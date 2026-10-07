"""Download official ECB reference rates EUR -> CZK into a dbt seed.

Source: European Central Bank Data Portal, series EXR.D.CZK.EUR.SP00.A
(daily, CZK per 1 EUR). Run once; the result is committed as a seed.

Usage (from the project root):
    python scripts/download_ecb_rates.py
"""
import io
import requests
import logging
from pathlib import Path

import pandas as pd

URL = (
    "https://data-api.ecb.europa.eu/service/data/EXR/D.CZK.EUR.SP00.A"
    "?startPeriod=2025-09-01&endPeriod=2026-09-30&format=csvdata"
)
OUTPUT = Path(__file__).resolve().parent.parent / "dbt" / "seeds" / "ecb_eur_czk.csv"

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")

response = requests.get(URL, timeout=30)
response.raise_for_status()   # stop with a clear error if the ECB returns an error
rates = pd.read_csv(io.StringIO(response.text))[["TIME_PERIOD", "OBS_VALUE"]]
rates.columns = ["rate_date", "czk_per_eur"]
rates.to_csv(OUTPUT, index=False)
logging.info("Saved %d daily rates (%s to %s) to %s",
             len(rates), rates["rate_date"].min(), rates["rate_date"].max(), OUTPUT)

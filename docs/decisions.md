# Decision log

## 001 — Python 3.12 instead of 3.14
**Date:** 2026-09-25
**Decision:** The project uses Python 3.12.
**Why:** dbt adapters often lag behind the newest Python version. 3.12 is
supported by dbt-core and widely used in production.
**Trade-off:** Newest Python features are not available — not needed here.

## 002 — CZ branch sells from a fixed CZK price list
**Date:** 2026-09-25
**Decision:** The generator prices Brno orders from a CZK price list set once
at 25.0 CZK/EUR. Reporting converts CZK to EUR with real daily ECB rates.
**Why:** Real branches keep stable local price lists; daily conversion belongs
in reporting. The generator stays offline and reproducible.

## 003 — Returns are separate documents with negative quantities
**Date:** 2026-09-25
**Decision:** ~1.5 % of sale lines are returned 3–30 days later as RETURN
documents that reference the original order.
**Why:** Returns are normal business, and the pipeline must keep them negative
instead of turning refunds into charges.

## 004 — Known limitations of the synthetic data
**Date:** 2026-09-25
- Street names are not matched to cities (Faker uses a national list).
- Quantity ranges, discounts and category preferences are assumptions.

## 005 — Injected shipment delay pattern
**Date:** 2026-09-25
**Decision:** Courier Beta is late more often than the other carriers, and all
carriers are slower in winter (Dec–Feb). Carriers are fictional.
**Why:** This is a planted, known pattern. The dashboard is validated by
detecting it. It must never be presented as a finding about real carriers.

## 006 — Planted data problems with a manifest
**Date:** 2026-09-25
**Decision:** The generator plants 14 known problem types (duplicates, typos,
missing values, invalid dates, a re-exported month, a schema change...) into
under 1 % of rows, and records every one in data/manifest/injected_issues.csv.
**Why:** The manifest is the answer key. Pipeline quality is proven by
detecting every planted problem, not by claiming the data is "clean".

## 007 — Azure setup: EU region, budget alert first
**Date:** 2026-09-29
**Decision:** All resources live in one resource group
(`rg-distribution-pipeline`, Germany West Central). A €1 monthly budget
alert was created before any other resource.
**Why:** EU region keeps data in the EU (GDPR). One resource group means the
whole project can be removed in one step. The budget alert only warns — it
does not stop services — so the limit is set very low.

## 008 — Landing zone: private Blob container, keyless upload
**Date:** 2026-09-29
**Decision:** Raw files land unchanged in the private `raw` container of a
Standard LRS storage account. Uploads use `az login` + the "Storage Blob Data
Contributor" role on this one account (`--auth-mode login`), never access keys.
**Why:** Originals stay available for reprocessing; no secrets in code;
least privilege. Hierarchical namespace (ADLS Gen2) not needed at this size.

## 009 — Azure SQL Database: free offer, Entra-only authentication
**Date:** 2026-09-29
**Decision:** Free-offer serverless database `free-sql-db-8791495` on server
`sql-distpipeline-jp`, auto-pause when the free monthly limit is reached.
Only Microsoft Entra authentication (no SQL logins). Firewall allows Azure
services and the developer's current IP only.
**Why:** Zero cost, no passwords to leak; Data Factory will connect with its
managed identity. Trade-off: the database may pause until next month if the
free compute is used up.git add docs/decisions.md

## 010 — Data Factory with managed identity, least privilege
**Date:** 2026-10-06
**Decision:** Data Factory `adf-distpipeline-jp` uses its system-assigned
managed identity. Storage: "Storage Blob Data Reader" on the storage account
only. Database: SELECT/INSERT/DELETE on schema `staging` only; staging tables
are created by scripts in `sql/`, not by Data Factory.
**Why:** No passwords; the pipeline cannot change raw files or the table
structure; everything in the database is defined in Git.

## 011 — ELT: Data Factory copies as text, reloads are idempotent
**Date:** 2026-10-06
**Decision:** Data Factory copies files unchanged into `staging` tables where
all business columns are NVARCHAR, adding `_source_file` and `_loaded_at`.
A pre-copy script deletes the rows of the same file before loading.
**Why:** Nothing is lost or silently converted; dbt does the cleaning.
Running the same load twice gives the same result (tested: 205 rows twice).

## 012 — Load one file per copy (schema drift found in testing)
**Date:** 2026-10-06
**Decision:** The staging load lists each folder and copies files one by one
(parent `pl_load_staging` → child `pl_load_folder_csv` / `pl_load_folder_excel`).
Each copy first deletes the rows of that file (`_source_file`), so reloads are
idempotent per file.
**Why:** A wildcard copy used the first file's header for all files. Žilina's
schema change (qty → quantity + vat_rate from 2026-03) was silently hidden:
values shifted one column and `_source_file` was overwritten with "23".
Found by reconciliation (row counts) and lineage columns; fixed by per-file loads.
**Status:** partly superseded by 014 (per-file loading kept only for Žilina orders).

## 013 — Weekly schedule for the staging load
**Date:** 2026-10-06
**Decision:** Trigger `tr_weekly_staging_load` runs `pl_load_staging` every
Monday at 03:00 (Central Europe time, follows summer/winter time).
**Why:** Each run wakes the free serverless database for about an hour; weekly
runs stay well within the free monthly compute. A real client would run it
nightly after the ERP exports are complete.
**Status:** superseded by 014 (trigger stopped to avoid costs).

## 014 — Cost optimization: per-file loading only where needed
**Date:** 2026-10-07
**Decision:** Wildcard copies (one per source) for all sources with a stable
schema; per-file loading only for Žilina orders (known schema change).
Data integration units fixed at 4 (minimum). The schedule trigger is stopped;
runs are started manually.
**Why:** A €1 budget alert fired after testing (€4.41, all Data Factory):
every copy is billed for at least one minute, so ~150 per-file copies per run
were expensive. Now ~25 copies per run with identical results (reconciled).
The synthetic data does not change, so a running schedule adds cost, no value.
**Trade-off:** a future schema change in another source would not be handled
by wildcard copies; reconciliation counts and dbt tests must catch it.

## 015 — Data Factory definitions stored in Git
**Date:** 2026-10-07
**Decision:** ADF is connected to the GitHub repo (collaboration branch `main`,
root folder `/adf`, publish branch `adf_publish`).
**Why:** Pipelines are versioned and reviewable; the factory can be rebuilt
from the repo. Linked services use managed identity, so no secrets are stored.

## 016 — dbt Core with the sqlserver adapter and Azure CLI login
**Date:** 2026-10-08
**Decision:** dbt Core 1.12 + dbt-sqlserver 1.12 (pyodbc backend, ODBC Driver 18).
dbt authenticates with `authentication: CLI` (the developer's `az login`) and
builds into the schema `dbt_dev`. `profiles.yml` lives in the repo.
**Why:** No passwords, so the profile is safe to commit; staging stays untouched
because dbt writes into its own schema.

## 017 — dbt staging layer: one model per source, nothing hidden
**Date:** 2026-10-08
**Decision:** One staging view per source table (`stg_erp__<table>`): standard
English names, safe type conversion with `try_convert` (bad values become NULL),
raw text kept in `*_raw` columns, codes translated to standard values.
No rows are filtered or deduplicated in staging.
**Why:** Bad values stay visible and countable instead of becoming plausible
numbers (unlike `fillna(0)`). Profiling showed traps that a naive approach would
create: uppercasing SKUs would break 2,735 valid codes; Czech thousands
separators would turn 322 valid quantities into NULL.

## 018 — Real ECB rates for CZK -> EUR (and a known side effect)
**Date:** 2026-10-08
**Decision:** CZK amounts are converted with official ECB daily reference rates
(seed `ecb_eur_czk`, 277 days, downloaded by `scripts/download_ecb_rates.py`).
Days without a rate use the latest earlier rate.
**Known side effect:** the generator priced Brno from a fixed price list at
25.0 CZK/EUR, while the real rate was 24.08-24.56. Brno amounts in EUR are
therefore ~2-4 % higher than the same items sold in EUR. This is an artifact
of the simulated price list, not a finding.

## 019 — Generator bug found by dbt: "impossible" dates that were real
**Date:** 2026-10-08
**Finding:** dbt rejected 21 invalid order dates, but the manifest listed 51.
The generator set the day to 31 in every month except February, so in 31-day
months it created real (but wrong) dates. Its test covered only 3 months.
**Decision:** Data files unchanged (byte-identical). The manifest now labels
21 `impossible_date` and 30 `plausible_wrong_date`; tests cover all 12 months.
**Lesson:** format checks can only catch values that are impossible. A wrong
but plausible date needs a business rule (e.g. order date vs shipment date).

## 020 — Star schema with stated grain
**Date:** 2026-10-08
**Decision:** Marts are tables. Facts: `fact_orders` (one row per valid order
line), `fact_shipments` (one row per valid shipment), `fact_inventory` (one row
per product, warehouse and Friday snapshot). Dimensions: date, warehouse
(seed), product, customer. Natural keys (codes) are used as join keys.
Only rows without rejection reasons enter the facts.
**Why:** Stated grain makes every number traceable; relationship tests ensure
every fact row joins to its dimensions. `dim_customer` leaves out street and
e-mail (data minimisation).
**Limits:** one fixed product price list (no price history / SCD Type 2).
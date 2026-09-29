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
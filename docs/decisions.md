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
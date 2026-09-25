# Decision log

## 001 — Python 3.12 instead of 3.14
**Date:** 2026-09-25
**Decision:** The project uses Python 3.12.
**Why:** dbt adapters often lag behind the newest Python version. 3.12 is
supported by dbt-core and widely used in production.
**Trade-off:** Newest Python features are not available — not needed here.
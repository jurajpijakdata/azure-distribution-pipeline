"""Run `dbt build` and send a Discord alert if anything failed or warned.

Reads dbt/target/run_results.json after the run. Exits with dbt's exit code,
so a scheduler or CI still sees the failure.

Usage (from the project root, after `az login`):
    python scripts/run_dbt_and_notify.py
"""
import json
import logging
import subprocess
import sys
from collections import Counter
from pathlib import Path

from notify_discord import send

DBT_DIR = Path(__file__).resolve().parent.parent / "dbt"
RESULTS = DBT_DIR / "target" / "run_results.json"
ATTENTION = {"fail", "error", "warn"}


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
    exit_code = subprocess.run(["dbt", "build"], cwd=DBT_DIR).returncode

    results = json.loads(RESULTS.read_text(encoding="utf-8"))["results"]
    counts = Counter(r["status"] for r in results)
    problems = [r for r in results if r["status"] in ATTENTION]
    logging.info("dbt build finished: %s", dict(counts))

    if problems:
        icon = "🔴" if exit_code != 0 else "🟡"
        lines = [f"{icon} **dbt build** finished with {len(problems)} item(s) needing attention",
                 "Summary: " + ", ".join(f"{k}={v}" for k, v in sorted(counts.items()))]
        for r in problems:
            name = r["unique_id"].split(".")[-1]
            lines.append(f"• `{r['status'].upper()}` {name}: {r.get('failures') or ''} row(s)")
        send("\n".join(lines))
        logging.info("Alert sent to Discord")
    return exit_code


if __name__ == "__main__":
    sys.exit(main())

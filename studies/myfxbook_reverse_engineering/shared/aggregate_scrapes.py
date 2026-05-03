"""Convert all raw scrape JSONs → per-system trades.parquet + summary manifest.

Walks `data/trades/<system_id>/raw/scrape.json` for every entry in the
catalog, runs `parser.parse_trade_records`, persists `trades.parquet`, and
writes a `data/catalog/scrape_manifest.md` summarizing each system's status
(n_trades, deposits, range, errors). Pure local I/O — no network, no
Playwright.

Idempotent. Safe to re-run after re-scrape.

Run: `uv run python studies/myfxbook_reverse_engineering/shared/aggregate_scrapes.py`
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from studies.myfxbook_reverse_engineering.shared import config, parser  # noqa: E402

MANIFEST_PATH = config.CATALOG_ROOT / "scrape_manifest.md"


def aggregate_one(system_id: int) -> dict:
    raw_path = config.trades_raw_dir(system_id) / "scrape.json"
    parquet_path = config.trades_parquet_path(system_id)
    if not raw_path.exists():
        return {"system_id": system_id, "status": "MISSING_RAW", "raw_path": str(raw_path)}

    raw = json.loads(raw_path.read_text())
    if raw.get("error"):
        return {
            "system_id": system_id, "status": "SCRAPE_ERROR",
            "error": raw["error"], "n_collected": raw.get("n_collected", 0),
            "total_advertised": raw.get("total_advertised", 0),
        }
    trades_raw = raw.get("trades", [])
    if not trades_raw:
        return {"system_id": system_id, "status": "EMPTY", "n_collected": 0}

    df = parser.parse_trade_records(trades_raw)
    parquet_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(parquet_path, compression="snappy")

    is_trade = df["is_trade"].sum()
    is_deposit = df["is_deposit"].sum()
    other = len(df) - int(is_trade) - int(is_deposit)
    trades_only = df[df["is_trade"]]
    return {
        "system_id": system_id,
        "status": "OK",
        "n_rows_total": len(df),
        "n_trades": int(is_trade),
        "n_deposits": int(is_deposit),
        "n_other": other,
        "first_trade": str(trades_only["open_dt_utc"].min()) if len(trades_only) else None,
        "last_trade": str(trades_only["close_dt_utc"].max()) if len(trades_only) else None,
        "symbols": dict(trades_only["symbol"].value_counts()) if len(trades_only) else {},
        "total_advertised": raw.get("total_advertised", 0),
        "pages_fetched": raw.get("pages_fetched", 0),
        "total_pages": raw.get("total_pages", 0),
        "capped": raw.get("capped", False),
        "parquet_path": str(parquet_path.relative_to(REPO_ROOT)),
    }


def main() -> int:
    catalog_path = config.CATALOG_ROOT / "all_systems.parquet"
    catalog = pd.read_parquet(catalog_path).sort_values("gain_pct", ascending=False).reset_index(drop=True)
    print(f"Aggregating {len(catalog)} systems …")

    results: list[dict] = []
    for _, row in catalog.iterrows():
        sid = int(row["system_id"])
        info = aggregate_one(sid)
        info["name"] = row["name"]
        info["gain_pct"] = row.get("gain_pct")
        info["account_type"] = row.get("account_type")
        results.append(info)

    ok = [r for r in results if r["status"] == "OK"]
    err = [r for r in results if r["status"] != "OK"]

    lines: list[str] = []
    lines.append("# Scrape manifest — HappyForex systems")
    lines.append(f"\nGenerated: {pd.Timestamp.now('UTC').isoformat(timespec='seconds')}")
    lines.append(f"\nTotal: {len(results)} | OK: {len(ok)} | Issues: {len(err)}\n")

    lines.append("## OK systems (sorted by gain)")
    lines.append("| system_id | name | account | gain | trades | deposits | first | last |")
    lines.append("|---:|---|---|---:|---:|---:|---|---|")
    for r in ok:
        first = r["first_trade"][:10] if r["first_trade"] else "-"
        last = r["last_trade"][:10] if r["last_trade"] else "-"
        gain = f"{r['gain_pct']:.0f}%" if r['gain_pct'] is not None else "-"
        cap = " ⚠CAP" if r.get("capped") else ""
        lines.append(f"| {r['system_id']} | {r['name']} | {r['account_type']} | {gain} | {r['n_trades']}{cap} | {r['n_deposits']} | {first} | {last} |")

    if err:
        lines.append("\n## Issues")
        lines.append("| system_id | name | status | detail |")
        lines.append("|---:|---|---|---|")
        for r in err:
            detail = r.get("error") or r.get("raw_path", "")
            lines.append(f"| {r['system_id']} | {r['name']} | {r['status']} | {detail} |")

    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.write_text("\n".join(lines))
    print(f"Wrote {MANIFEST_PATH}")
    print(f"OK={len(ok)}, issues={len(err)}")
    return 0 if not err else 1


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Aggregate verdict.json files from one or more iters into a single comparison
table.

Use case: after running iter 056 (Part A, B4 reallocation) + iter 057 (Part B,
global hybrid fork), this script ingests their verdict files and produces a
unified `compare_table.csv` + `compare_table.md` keyed by config slug, with
columns:

    slug | iter | window | CAGR | MDD | Sharpe | %3y/5y/10y/15y win SPY | %win VT

Schema differences between iters are handled gracefully:
    - iter 056 (testfol.io engine) writes verdict.json with `ranking` list
      where each row has stats sub-dict (cagr in PERCENT, sharpe normalized).
    - iter 057 (internal engine) writes verdict.json with `ranking` list where
      each row has `metrics` sub-dict (cagr in DECIMAL, sharpe normalized).

Usage:
    uv run python scripts/long_term_portfolio/compare_portfolios.py \\
        studies/long_term_portfolio/iterations/056-2026-05-05-b4-reallocation \\
        studies/long_term_portfolio/iterations/057-2026-05-05-global-fork-hybrid \\
        --out studies/long_term_portfolio/B4_GLOBAL_FORK_compare_table

Outputs <out>.csv and <out>.md.

Citations:
    - Rolling-window robustness metric: studies/long_term_portfolio/rolling_windows.py:58
      (rolling_outperformance_pct).
    - Why aggregate per-iter: spy_beater_hunt/TOP_STRATEGIES.md pattern.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


def _normalize_row(row: dict[str, Any], iter_dir: Path) -> dict[str, Any]:
    """Map per-iter schema differences into a unified record.

    Output keys: slug, window, cagr_pct, mdd_pct, sharpe, drag_pct (or None),
                 win_spy_3y/5y/10y/15y, win_vt_3y/5y/10y/15y (each in %, or None).
    """
    iter_name = iter_dir.name

    # iter 056 (testfol.io): row has 'slug', 'stats', 'window', 'drag_pct',
    # 'windows_beat' = {bench_slug: {year: float|None}}.
    if "stats" in row:
        stats = row["stats"]
        wb = row.get("windows_beat", {})
        spy = wb.get("SPY_1x", {})
        vt = wb.get("VT_1x", {})
        return {
            "slug": row["slug"],
            "iter": iter_name,
            "window": row.get("window", ""),
            "cagr_pct": stats.get("cagr"),
            "mdd_pct": stats.get("max_drawdown"),
            "sharpe": stats.get("sharpe"),
            "drag_pct": row.get("drag_pct"),
            "win_spy_3y": _pct(spy.get("3")),
            "win_spy_5y": _pct(spy.get("5")),
            "win_spy_10y": _pct(spy.get("10")),
            "win_spy_15y": _pct(spy.get("15")),
            "win_vt_3y": _pct(vt.get("3")),
            "win_vt_5y": _pct(vt.get("5")),
            "win_vt_10y": _pct(vt.get("10")),
            "win_vt_15y": _pct(vt.get("15")),
        }

    # iter 057 (internal engine): row has 'name', 'metrics', 'windows_beat_spy',
    # 'windows_beat_vt' where each is dict[year_str -> {pct_strat_wins, n_windows, ...}].
    if "metrics" in row:
        m = row["metrics"]
        spy = row.get("windows_beat_spy", {})
        vt = row.get("windows_beat_vt", {})
        return {
            "slug": row["name"],
            "iter": iter_name,
            "window": (
                f"{m.get('start')} → {m.get('end')} ({m.get('years', 0):.1f}y)"
            ),
            "cagr_pct": (m.get("cagr") or 0) * 100,
            "mdd_pct": (m.get("mdd") or 0) * 100,
            "sharpe": m.get("sharpe"),
            "drag_pct": None,
            "win_spy_3y": _pct((spy.get("3") or {}).get("pct_strat_wins")),
            "win_spy_5y": _pct((spy.get("5") or {}).get("pct_strat_wins")),
            "win_spy_10y": _pct((spy.get("10") or {}).get("pct_strat_wins")),
            "win_spy_15y": _pct((spy.get("15") or {}).get("pct_strat_wins")),
            "win_vt_3y": _pct((vt.get("3") or {}).get("pct_strat_wins")),
            "win_vt_5y": _pct((vt.get("5") or {}).get("pct_strat_wins")),
            "win_vt_10y": _pct((vt.get("10") or {}).get("pct_strat_wins")),
            "win_vt_15y": _pct((vt.get("15") or {}).get("pct_strat_wins")),
        }

    raise ValueError(f"unrecognized row schema in {iter_dir.name}: keys={list(row.keys())}")


def _pct(v: float | None) -> float | None:
    if v is None:
        return None
    return v * 100.0


def collect_rows(iter_dirs: list[Path]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for d in iter_dirs:
        verdict_path = d / "verdict.json"
        if not verdict_path.exists():
            print(f"[compare] {d.name}: verdict.json missing — skip")
            continue
        verdict = json.loads(verdict_path.read_text())
        for r in verdict.get("ranking", []):
            rows.append(_normalize_row(r, d))
    return rows


def write_outputs(rows: list[dict[str, Any]], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    csv_path = out_path.with_suffix(".csv")
    md_path = out_path.with_suffix(".md")

    fields = [
        "slug", "iter", "window", "cagr_pct", "mdd_pct", "sharpe", "drag_pct",
        "win_spy_3y", "win_spy_5y", "win_spy_10y", "win_spy_15y",
        "win_vt_3y", "win_vt_5y", "win_vt_10y", "win_vt_15y",
    ]
    with csv_path.open("w") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow(r)
    print(f"[compare] wrote {csv_path}")

    # Markdown
    lines = [
        "# B4 Reallocation + Global Fork — comparison table",
        "",
        "Auto-generated from per-iter verdict.json. Columns:",
        "",
        "- `cagr_pct` / `mdd_pct` / `sharpe` — full-window metrics from the engine.",
        "- `win_spy_*y` — % of rolling N-y windows where strategy Sharpe > SPY Sharpe.",
        "- `win_vt_*y` — same vs VT.",
        "",
        "## Ranked by Sharpe",
        "",
        "| slug | iter | window | CAGR | MDD | Sharpe | %3y SPY | %5y SPY | %10y SPY | %15y SPY | %3y VT | %5y VT | %10y VT | %15y VT |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    ranked = sorted(rows, key=lambda r: -(r["sharpe"] or float("-inf")))
    for r in ranked:
        cells = [
            f"`{r['slug']}`",
            r["iter"],
            r["window"],
            _fmt_pct(r["cagr_pct"]),
            _fmt_pct(r["mdd_pct"]),
            _fmt_num(r["sharpe"], "{:.3f}"),
            _fmt_pct(r["win_spy_3y"]),
            _fmt_pct(r["win_spy_5y"]),
            _fmt_pct(r["win_spy_10y"]),
            _fmt_pct(r["win_spy_15y"]),
            _fmt_pct(r["win_vt_3y"]),
            _fmt_pct(r["win_vt_5y"]),
            _fmt_pct(r["win_vt_10y"]),
            _fmt_pct(r["win_vt_15y"]),
        ]
        lines.append("| " + " | ".join(cells) + " |")

    md_path.write_text("\n".join(lines) + "\n")
    print(f"[compare] wrote {md_path}")


def _fmt_num(v: float | None, fmt: str) -> str:
    if v is None:
        return "n/a"
    return fmt.format(v)


def _fmt_pct(v: float | None) -> str:
    if v is None:
        return "n/a"
    return f"{v:.2f}%"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("iter_dirs", type=Path, nargs="+",
                    help="One or more iter directories with verdict.json")
    ap.add_argument("--out", type=Path,
                    default=Path("studies/long_term_portfolio/B4_GLOBAL_FORK_compare_table"),
                    help="Output stem (writes <out>.csv and <out>.md).")
    args = ap.parse_args()

    rows = collect_rows(args.iter_dirs)
    if not rows:
        print("[compare] no rows collected; aborting")
        return 1
    write_outputs(rows, args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

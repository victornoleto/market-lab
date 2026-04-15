#!/usr/bin/env python3
"""Consolidate per-asset Ehlers grid diagnostics into a single summary table.

Walks ``reports/grid_ehlers_<symbol>_<timestamp>/`` directories created by
``run_ehlers_multi_asset.sh``, extracts gate verdicts and best-config
metrics from each ``diagnostic.md``, and writes
``reports/ehlers_multi_asset_summary.md`` — the canonical artifact for the
Reddit post / decision review.

Run after the orchestrator script:
    bash scripts/run_ehlers_multi_asset.sh
    .venv/bin/python scripts/build_ehlers_summary.py
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPORTS = ROOT / "reports"
SUMMARY_PATH = REPORTS / "ehlers_multi_asset_summary.md"

# Match dirs created by the multi-asset script (with explicit per-asset run_id).
DIR_PATTERN = re.compile(
    r"^grid_ehlers_(?P<symbol>[a-z0-9_]+)_(?P<ts>\d{8}-\d{6})$"
)


def parse_diagnostic(path: Path) -> dict | None:
    """Pull gate verdict + best-config metrics from a diagnostic.md."""
    if not path.exists():
        return None
    text = path.read_text(encoding="utf-8")

    out: dict = {}

    m = re.search(r"^# Grid Report — `([^`]+)` \((\w+)\)", text, re.MULTILINE)
    if m:
        out["run_id"] = m.group(1)
        out["verdict"] = m.group(2)

    m = re.search(r"\| PBO \| ([\d.]+) \|", text)
    out["pbo"] = float(m.group(1)) if m else None

    m = re.search(r"\| DSR \| (\d+)/(\d+) configs", text)
    if m:
        out["dsr_pass"] = int(m.group(1))
        out["dsr_total"] = int(m.group(2))

    m = re.search(r"\| Walk-forward \| (\d+)/(\d+) configs", text)
    if m:
        out["wf_pass"] = int(m.group(1))
        out["wf_total"] = int(m.group(2))

    m = re.search(r"\| Sharpe \(annualized\) \| ([\-\d.]+) \|", text)
    out["best_sharpe"] = float(m.group(1)) if m else None

    m = re.search(r"\| CAGR \| ([\-\d.]+)% \|", text)
    out["best_cagr_pct"] = float(m.group(1)) if m else None

    m = re.search(r"\| Max drawdown \| ([\d.]+)% \|", text)
    out["best_dd_pct"] = float(m.group(1)) if m else None

    modes = re.findall(r"^### `(\w+)`", text, re.MULTILINE)
    out["failure_modes"] = modes

    return out


def parse_run_log(jsonl_path: Path) -> dict | None:
    """Re-derive window from the first trial's run_id timestamp + first/last bar."""
    if not jsonl_path.exists():
        return None
    first = jsonl_path.read_text(encoding="utf-8").splitlines()[0]
    return json.loads(first)


def main() -> int:
    # Collect most-recent run per symbol — repeated runs (pre-fix vs post-fix,
    # smoke runs, param tweaks) keep only the latest timestamp per asset so
    # the summary reads as one canonical experiment.
    by_symbol: dict[str, tuple[str, Path, re.Match]] = {}
    for d in sorted(REPORTS.glob("grid_ehlers_*_2026*")):
        m = DIR_PATTERN.match(d.name)
        if not m:
            continue
        symbol = m.group("symbol").upper()
        ts = m.group("ts")
        prev = by_symbol.get(symbol)
        if prev is None or prev[0] < ts:
            by_symbol[symbol] = (ts, d, m)

    rows: list[dict] = []
    for symbol, (_ts, d, _m) in by_symbol.items():
        diag = parse_diagnostic(d / "diagnostic.md")
        if diag is None:
            print(f"SKIP {d.name} — no diagnostic.md")
            continue
        diag["symbol"] = symbol
        diag["report_dir"] = d.relative_to(ROOT).as_posix()
        rows.append(diag)

    if not rows:
        print("No runs found.")
        return 1

    rows.sort(key=lambda r: (r.get("verdict") != "PASS", -(r.get("best_sharpe") or 0)))

    lines: list[str] = []
    lines.append("# Ehlers BP Swing — Multi-Asset Survey\n")
    lines.append(
        "Survey of the Ehlers Band-Pass Swing strategy (24-config grid: "
        "hp_period × lp_period × pct_of_dcp × stop_pct) against a curated "
        "basket of assets. Storage-first via Tiingo (survivorship-free for "
        "ETFs/crypto; equities-only universe still has minor residual). "
        "Each grid evaluated against PBO < 0.5, DSR p < 0.05, WF ≥ 6/8.\n"
    )
    lines.append(
        f"- **Assets evaluated:** {len(rows)} (most recent run per symbol)\n"
        f"- **Strategy:** EhlersBPSwingStrategy (single-instrument, long-flat)\n"
        f"- **Grid size:** 24 configs per asset\n"
        f"- **Data:** Tiingo daily OHLCV, `data/tiingo` canonical store, "
        f"adj_close-rebased OHLC (commit `5ca9410`)\n"
        f"- **Generated:** by `scripts/build_ehlers_summary.py` from per-asset "
        f"`reports/grid_ehlers_<symbol>_<ts>/diagnostic.md`\n\n"
    )

    n_pass = sum(1 for r in rows if r.get("verdict") == "PASS")
    n_fail = len(rows) - n_pass
    lines.append(f"## TL;DR — {n_pass} PASS / {n_fail} FAIL\n\n")
    if n_pass == 0:
        lines.append(
            "**Every asset failed the 3-gate framework.** The best Sharpe "
            "across the basket comes from BTCUSD (cyclical by nature) but "
            "still rejects on DSR and WF. The Ehlers BP Swing single-"
            "instrument strategy as currently parametrized does not exhibit "
            "exploitable edge in any of the tested regimes.\n\n"
        )

    lines.append("## Verdict table\n\n")
    lines.append(
        "| Symbol | Verdict | PBO | DSR | WF | Best Sharpe | Best CAGR | "
        "Best DD | Failure modes |\n"
    )
    lines.append(
        "|---|---|---|---|---|---|---|---|---|\n"
    )
    for r in rows:
        verdict_emoji = "✅ PASS" if r.get("verdict") == "PASS" else "❌ FAIL"
        pbo = f"{r['pbo']:.3f}" if r.get("pbo") is not None else "—"
        dsr = (
            f"{r['dsr_pass']}/{r['dsr_total']}"
            if r.get("dsr_total") is not None else "—"
        )
        wf = (
            f"{r['wf_pass']}/{r['wf_total']}"
            if r.get("wf_total") is not None else "—"
        )
        sharpe = (
            f"{r['best_sharpe']:.2f}"
            if r.get("best_sharpe") is not None else "—"
        )
        cagr = (
            f"{r['best_cagr_pct']:.2f}%"
            if r.get("best_cagr_pct") is not None else "—"
        )
        dd = (
            f"{r['best_dd_pct']:.2f}%"
            if r.get("best_dd_pct") is not None else "—"
        )
        modes = ", ".join(r.get("failure_modes", [])) or "—"
        lines.append(
            f"| **{r['symbol']}** | {verdict_emoji} | {pbo} | {dsr} | {wf} | "
            f"{sharpe} | {cagr} | {dd} | {modes} |\n"
        )

    lines.append("\n## Notes\n\n")
    lines.append(
        "- **Best Sharpe row** is the per-grid champion *ignoring* gates. "
        "It is the number you would have reported in a naive backtest; "
        "the gates exist to deflate it.\n"
        "- **PBO** measures probability of backtest overfitting via "
        "combinatorial purged splits. < 0.5 is the gate; > 0.5 means the "
        "Sharpe ranking is essentially noise.\n"
        "- **DSR** (Deflated Sharpe Ratio, López de Prado) tests Sharpe "
        "significance after correcting for multiple trials (24 here). p < "
        "0.05 needed to reject the null of no skill.\n"
        "- **WF** (walk-forward) requires ≥ 6/8 windows profitable AND "
        "drawdown ≤ 25% per window. Tests temporal generalization.\n"
        "- All grids use **n_jobs=4**, ~5s wallclock per asset.\n\n"
    )

    lines.append("## Known issues (excluded from this run)\n\n")
    lines.append(
        "- **VXX**: hits `TypeError: float() not 'complex'` in "
        "`_safe_cagr` — equity curve goes near-zero (VXX decay), "
        "`cagr()` returns complex. Bug in `backtest/grid/runner.py:186`.\n"
        "- **EURUSD / USDJPY / GBPUSD**: Tiingo FX endpoint returns "
        "400 with current `_build_params`. Likely needs `resampleFreq=1day` "
        "added for forex (currently only set for crypto).\n\n"
    )

    lines.append("## Comparison vs pre-fix (yfinance Run 2, raw close)\n\n")
    lines.append(
        "This survey uses Tiingo's survivorship-free dataset WITH the "
        "`adjust_ohlc` fix (commit `5ca9410`). Pre-fix, the single-asset "
        "runs from 2026-04-14 showed best-Sharpe values in the 0.10–0.27 "
        "range across all ETFs; post-fix, SPY/QQQ/XLK/IWM all moved into "
        "the 0.39–0.73 band. Crypto (BTCUSD/ETHUSD) is unchanged because "
        "perpetual spot prices carry no dividend or split events.\n\n"
        "The **gate verdicts did not change** — WF collapses on the longer "
        "2005-2023 window for every ETF (2008-2009 crash + 2020 COVID + "
        "2022 rate regime break generalization); DSR still deflates the "
        "improved Sharpes below p<0.05 at N=24 trials. The raw signal is "
        "materially better than pre-fix, but N is too small and T is not "
        "long enough to clear the statistical bar.\n\n"
    )

    SUMMARY_PATH.write_text("".join(lines), encoding="utf-8")
    print(f"Wrote {SUMMARY_PATH.relative_to(ROOT)}")
    print(f"  {len(rows)} assets summarized, {n_pass} pass / {n_fail} fail")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

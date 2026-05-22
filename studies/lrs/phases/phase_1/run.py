"""studies.lrs phase-1 — SMA/EMA × lookback × risk-off sweep.

Sweep all combinations of:

* **Filter**: ``SMA`` or ``EMA``
* **Lookback**: ``{20, 25, 30, ..., 500}`` (97 values, step 5)
* **Risk-off**: ``CASH`` (0%), ``GLD`` (GLDSIM), ``IEF`` (IEFSIM), ``ZROZ`` (ZROZSIM)
* **On-leg**: ``SSO`` (2×), ``UPRO`` (3×)
* **Tax scenario**: ``tax_free`` and ``br_lei_14754`` (15% annual, Lei 14.754 art. 5°/6°)

Total: ``2 × 97 × 4 × 2 = 1,552`` strategies × 2 scenarios = **3,104 score reports**.

Each strategy is scored via :func:`studies.lrs.scripts.scoring.score_strategy`
against the universal B&H SPY (tax-free) benchmark. Outputs full sweep CSV,
top-20 per panel CSV, summary JSON, four heatmap PNGs, manifest, and a
``report.md`` with the top tables and embedded plots.

Discovery-only output (Investment Mandate §1). The top configs found here
ARE expected to be overfit to historical regime patterns; phase-2 will
validate top candidates via walk-forward + block bootstrap on the regime
parameters.

Usage::

    uv run python -m studies.lrs.phases.phase_1.run

Run time: ~5-10 minutes on a workstation.
"""
from __future__ import annotations

import hashlib
import json
import logging
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from market_lab.backtest.strategies.letf_rotation import compute_regime_signal
from studies.lrs.scripts.data import MODERN_ERA_START, PHASE_1_TICKERS, load_modern_data
from studies.lrs.scripts.plots import plot_sweep_heatmap
from studies.lrs.scripts.scoring import (
    COMPONENT_WEIGHTS,
    HORIZON_WEIGHTS,
    score_strategy,
)
from studies.lrs.scripts.tax import simulate_rotation_with_annual_tax
from studies.lrs.phases.phase_1.plot_top_curves import render_top_k_comparison

log = logging.getLogger("studies.lrs.phase_1")

PHASE_DIR = Path(__file__).resolve().parent
PLOTS_DIR = PHASE_DIR / "plots"
RESULTS_DIR = PHASE_DIR / "results"
REPORT_PATH = PHASE_DIR / "report.md"

# --- Sweep grid ---
FILTERS: tuple[str, ...] = ("SMA", "EMA")
# Lookbacks 20..500 step 5 (97 values). The 500-day ceiling was reached
# after the original 20..300 grid put its winners at SMA290-300 — too close
# to the edge to be a clean local maximum. Extending to 500 verifies the
# peak rather than chasing the grid boundary.
LOOKBACKS: tuple[int, ...] = tuple(range(20, 505, 5))   # 20, 25, ..., 500 (97 values)
RISK_OFFS: tuple[str, ...] = ("CASH", "GLD", "IEF", "ZROZ")
ON_LEGS: tuple[str, ...] = ("SSO", "UPRO")
TAX_SCENARIOS: tuple[str, ...] = ("tax_free", "br_lei_14754")
BAND_PCT = 0.0
TAX_RATE = 0.15
WINDOW_YEARS = (1, 3, 5, 10, 15, 20)
WINDOW_STEP_DAYS = 21

# Ticker mapping for off-leg series. CASH is the special-cased zero-return case
# (off_leg_returns=None in the tax simulator); the others use testfolio synths.
OFF_LEG_TICKER: dict[str, str | None] = {
    "CASH": None,
    "GLD":  "GLDSIM",
    "IEF":  "IEFSIM",
    "ZROZ": "ZROZSIM",
}

# Ticker mapping for on-leg series.
ON_LEG_TICKER: dict[str, str] = {"SSO": "SSOSIM", "UPRO": "UPROSIM"}


@dataclass(frozen=True)
class SweepRow:
    """One row of the sweep result table."""

    filter: str
    lookback: int
    on_leg: str
    risk_off: str
    tax_scenario: str
    final_score: float
    length_score_5y: float
    length_score_10y: float
    length_score_15y: float
    length_score_20y: float
    pct_outperforming_20y: float
    n_switches: int
    switches_per_year: float        # n_switches / years_in_scoring_window
    avg_regime_days: float          # scoring_bars / max(1, n_switches), the average days between regime flips
    n_tax_events: int
    total_tax_paid: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "filter": self.filter,
            "lookback": self.lookback,
            "on_leg": self.on_leg,
            "risk_off": self.risk_off,
            "tax_scenario": self.tax_scenario,
            "final_score": float(self.final_score),
            "length_score_5y": float(self.length_score_5y),
            "length_score_10y": float(self.length_score_10y),
            "length_score_15y": float(self.length_score_15y),
            "length_score_20y": float(self.length_score_20y),
            "pct_outperforming_20y": float(self.pct_outperforming_20y),
            "n_switches": int(self.n_switches),
            "switches_per_year": float(self.switches_per_year),
            "avg_regime_days": float(self.avg_regime_days),
            "n_tax_events": int(self.n_tax_events),
            "total_tax_paid": float(self.total_tax_paid),
        }


def _scenario_label(on_leg: str, filter_: str, lookback: int, risk_off: str) -> str:
    return f"LRS-{on_leg}-{filter_}{lookback}-{risk_off}"


def _build_benchmark(spy_rets: pd.Series, start_date: pd.Timestamp) -> pd.Series:
    """B&H SPY (tax-free) — universal benchmark for every panel."""
    r = spy_rets.loc[start_date:].astype(float).fillna(0.0)
    eq = (1.0 + r).cumprod()
    eq.iloc[0] = 1.0
    return eq


def _length_score(report, years: int) -> float:
    agg = report.per_length.get(years)
    return float(agg.length_score) if agg is not None else float("nan")


def _pct_outperforming(report, years: int) -> float:
    agg = report.per_length.get(years)
    return float(agg.pct_outperforming) if agg is not None else float("nan")


def _run_sweep(
    prices: pd.DataFrame,
    spy: pd.Series,
    benchmark: pd.Series,
    start_date: pd.Timestamp,
) -> list[SweepRow]:
    """Run the full sweep. Returns one SweepRow per (config × scenario)."""
    rows: list[SweepRow] = []
    n_total = len(FILTERS) * len(LOOKBACKS) * len(RISK_OFFS) * len(ON_LEGS) * len(TAX_SCENARIOS)

    # Scoring-window length in days/years for switches_per_year etc.
    scoring_bars = int(len(prices.loc[start_date:]))
    scoring_years = scoring_bars / 252.0

    # Pre-compute signals for every (filter, lookback). 114 signals total.
    log.info("precomputing %d signals (%d filters × %d lookbacks)...",
             len(FILTERS) * len(LOOKBACKS), len(FILTERS), len(LOOKBACKS))
    signal_cache: dict[tuple[str, int], pd.Series] = {}
    for f in FILTERS:
        for lb in LOOKBACKS:
            signal_cache[(f, lb)] = compute_regime_signal(
                spy, filter=f, lookback=lb, band_pct=BAND_PCT
            )

    # Pre-compute returns for each on-leg and off-leg (4 + 2 series).
    on_rets: dict[str, pd.Series] = {
        k: prices[ON_LEG_TICKER[k]].pct_change() for k in ON_LEGS
    }
    off_rets: dict[str, pd.Series | None] = {
        k: (None if OFF_LEG_TICKER[k] is None else prices[OFF_LEG_TICKER[k]].pct_change())
        for k in RISK_OFFS
    }

    log.info("scoring %d configs × %d scenarios = %d strategies...",
             n_total // 2, len(TAX_SCENARIOS), n_total)
    n_done = 0
    t_start = time.time()
    last_log = t_start
    for on_leg in ON_LEGS:
        on_ret_full = on_rets[on_leg]
        on_ret_sliced = on_ret_full.loc[start_date:]
        for risk_off in RISK_OFFS:
            off_ret_full = off_rets[risk_off]
            off_ret_sliced = off_ret_full.loc[start_date:] if off_ret_full is not None else None
            for filter_ in FILTERS:
                for lookback in LOOKBACKS:
                    signal = signal_cache[(filter_, lookback)].loc[start_date:]
                    sim = simulate_rotation_with_annual_tax(
                        on_ret_sliced,
                        signal,
                        tax_rate=TAX_RATE,
                        off_leg_returns=off_ret_sliced,
                    )
                    name = _scenario_label(on_leg, filter_, lookback, risk_off)
                    for scenario in TAX_SCENARIOS:
                        equity = sim.pretax_equity if scenario == "tax_free" else sim.equity
                        report = score_strategy(
                            equity,
                            benchmark,
                            strategy_name=name,
                            tax_scenario=scenario,
                            window_years=WINDOW_YEARS,
                            window_step_days=WINDOW_STEP_DAYS,
                        )
                        rows.append(SweepRow(
                            filter=filter_,
                            lookback=lookback,
                            on_leg=on_leg,
                            risk_off=risk_off,
                            tax_scenario=scenario,
                            final_score=report.final_score,
                            length_score_5y=_length_score(report, 5),
                            length_score_10y=_length_score(report, 10),
                            length_score_15y=_length_score(report, 15),
                            length_score_20y=_length_score(report, 20),
                            pct_outperforming_20y=_pct_outperforming(report, 20),
                            n_switches=sim.n_switches,
                            switches_per_year=sim.n_switches / scoring_years if scoring_years > 0 else 0.0,
                            avg_regime_days=scoring_bars / max(1, sim.n_switches),
                            n_tax_events=len(sim.tax_events) if scenario == "br_lei_14754" else 0,
                            total_tax_paid=(sim.total_tax_paid if scenario == "br_lei_14754" else 0.0),
                        ))
                        n_done += 1
                    now = time.time()
                    if now - last_log > 15:
                        elapsed = now - t_start
                        rate = n_done / max(0.001, elapsed)
                        eta = (n_total - n_done) / max(0.001, rate)
                        log.info("  progress: %d/%d (%.0f%%)  rate=%.1f/s  eta=%.0fs",
                                 n_done, n_total, n_done / n_total * 100, rate, eta)
                        last_log = now
    log.info("sweep finished in %.1fs", time.time() - t_start)
    return rows


def _top_n_per_panel(df: pd.DataFrame, n: int = 20) -> pd.DataFrame:
    """Top-N rows per (on_leg, tax_scenario) ranked by final_score."""
    return (
        df.sort_values("final_score", ascending=False)
          .groupby(["on_leg", "tax_scenario"], group_keys=False)
          .head(n)
          .reset_index(drop=True)
    )


def _neighborhood_robustness(
    df: pd.DataFrame, row: pd.Series, lookback_window: int = 25
) -> dict[str, float]:
    """For a given top config, compute the fraction of (filter, lookback±25) neighbors
    that are also positive-score, plus their mean score. Cheap overfit-vs-plateau check.
    """
    same_panel = df[
        (df["on_leg"] == row["on_leg"])
        & (df["tax_scenario"] == row["tax_scenario"])
        & (df["risk_off"] == row["risk_off"])
        & (df["filter"] == row["filter"])
        & (df["lookback"].between(row["lookback"] - lookback_window, row["lookback"] + lookback_window))
    ]
    n = int(len(same_panel))
    pct_pos = float((same_panel["final_score"] > 0).mean()) if n else float("nan")
    mean = float(same_panel["final_score"].mean()) if n else float("nan")
    return {"n_neighbors": n, "pct_positive": pct_pos, "mean_score": mean}


def _render_report(
    manifest: dict[str, Any],
    df: pd.DataFrame,
    top_df: pd.DataFrame,
    top_k_table: list[dict] | None = None,
) -> str:
    lines: list[str] = []
    lines.append("# studies/lrs — Phase 1 Report (SMA/EMA × lookback × risk-off sweep)\n")
    lines.append(
        f"Generated: {manifest['generated_at']}  ·  "
        f"sweep: {manifest['sweep']['n_configs']} configs × 2 tax scenarios "
        f"= {manifest['sweep']['n_reports']} score reports  ·  "
        f"scoring window: {manifest['curves']['start_date']} → "
        f"{manifest['curves']['end_date']} ({manifest['curves']['n_days']} bars)\n"
    )

    lines.append("## Sweep grid\n")
    lines.append("| Dimension | Values |")
    lines.append("|---|---|")
    lines.append(f"| Filter | {', '.join(FILTERS)} ({len(FILTERS)}) |")
    lines.append(
        f"| Lookback | {LOOKBACKS[0]}..{LOOKBACKS[-1]} step "
        f"{LOOKBACKS[1] - LOOKBACKS[0]} ({len(LOOKBACKS)} values) |"
    )
    lines.append(f"| Risk-off | {', '.join(RISK_OFFS)} ({len(RISK_OFFS)}) |")
    lines.append(f"| On-leg | {', '.join(ON_LEGS)} ({len(ON_LEGS)}) |")
    lines.append(f"| Tax scenario | {', '.join(TAX_SCENARIOS)} ({len(TAX_SCENARIOS)}) |")
    lines.append(
        f"| **Total** | **{len(FILTERS) * len(LOOKBACKS) * len(RISK_OFFS) * len(ON_LEGS)}** "
        f"configs, **× {len(TAX_SCENARIOS)}** scenarios |"
    )
    lines.append("")

    lines.append("## Heatmaps\n")
    lines.append("Each heatmap shows ``final_score`` over the ``(filter, lookback)`` grid for one ")
    lines.append("``(on_leg, tax_scenario)`` cell; one panel per risk-off asset. Star = best ")
    lines.append("config within that panel.\n")
    for on_leg in ON_LEGS:
        for scenario in TAX_SCENARIOS:
            fname = f"heatmap_{on_leg.lower()}_{scenario}.png"
            lines.append(f"### {on_leg} on-leg, {scenario}\n")
            lines.append(f"![{fname}](plots/{fname})\n")

    # Top-N per panel
    lines.append("## Top-10 per (on_leg × tax_scenario)\n")
    for on_leg in ON_LEGS:
        for scenario in TAX_SCENARIOS:
            sub = top_df[
                (top_df["on_leg"] == on_leg) & (top_df["tax_scenario"] == scenario)
            ].head(10).reset_index(drop=True)
            if sub.empty:
                continue
            lines.append(f"### {on_leg} on-leg, {scenario}\n")
            lines.append(
                "| # | filter | LB | risk-off | final | 10y | 15y | 20y | %win 20y | switches/y | regime-d | tax drag |"
            )
            lines.append(
                "|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|"
            )
            for idx, r in sub.iterrows():
                lines.append(
                    f"| {idx + 1} | {r['filter']} | {r['lookback']} | {r['risk_off']} | "
                    f"{r['final_score']:+.4f} | {r['length_score_10y']:+.3f} | "
                    f"{r['length_score_15y']:+.3f} | {r['length_score_20y']:+.3f} | "
                    f"{r['pct_outperforming_20y']:.0%} | {r['switches_per_year']:.1f} | "
                    f"{r['avg_regime_days']:.0f} | {r['total_tax_paid']:.2f} |"
                )
            lines.append("")

    # Headline winners with neighborhood-robustness diagnostic.
    lines.append("## Headline winners with neighbourhood robustness\n")
    lines.append(
        "Each panel's top config plus a cheap overfit-vs-plateau check: "
        "how many of its (filter, lookback ± 25) siblings also score positive."
    )
    lines.append("")
    lines.append(
        "| Panel | filter | LB | risk-off | final | neighbours | %positive | mean |"
    )
    lines.append("|---|---|---:|---|---:|---:|---:|---:|")
    for on_leg in ON_LEGS:
        for scenario in TAX_SCENARIOS:
            sub = top_df[
                (top_df["on_leg"] == on_leg) & (top_df["tax_scenario"] == scenario)
            ]
            if sub.empty:
                continue
            best = sub.iloc[0]
            nbr = _neighborhood_robustness(df, best, lookback_window=25)
            lines.append(
                f"| {on_leg} · {scenario} | {best['filter']} | {best['lookback']} | "
                f"{best['risk_off']} | {best['final_score']:+.4f} | "
                f"{nbr['n_neighbors']} | {nbr['pct_positive']:.0%} | "
                f"{nbr['mean_score']:+.4f} |"
            )
    lines.append("")

    # Top-K equity-curve comparison + terminal multiples (only if we built it).
    if top_k_table:
        lines.append("## Top-K equity comparison vs phase-0 baseline\n")
        lines.append(
            "Top-5 phase-1 winners per on-leg (ranked under the `br_lei_14754` "
            "scenario) re-simulated and compared against B&H benchmarks and "
            "the phase-0 SMA200/CASH baseline. Terminal multiples are over "
            "the full scoring window.\n"
        )
        lines.append("| Strategy | Tax-free terminal | BR-tax terminal | × B&H SPY (taxed) |")
        lines.append("|---|---:|---:|---:|")
        for row in top_k_table:
            highlight = "**" if row["kind"] == "phase1" else ""
            label = f"{highlight}{row['label']}{highlight}"
            tf = f"{highlight}{row['tax_free_terminal']:,.1f}×{highlight}"
            tx = f"{highlight}{row['taxed_terminal']:,.1f}×{highlight}"
            rs = f"{highlight}{row['taxed_ratio_to_spy']:,.2f}×{highlight}"
            lines.append(f"| {label} | {tf} | {tx} | {rs} |")
        lines.append("")
        lines.append("Plots (two panels: tax-free left, BR-tax right; log scale):\n")
        lines.append("![top_k_equity_overlay](plots/top_k_equity_overlay.png)\n")
        lines.append("![top_k_ratio_to_spy](plots/top_k_ratio_to_spy.png)\n")

    lines.append("## Caveats\n")
    lines.append(
        "- **Discovery-only**: the top configs here ARE expected to be overfit to the "
        "1980-2026 regime pattern. No PBO/DSR/walk-forward adjustment was applied. "
        "Phase-2 will validate top-N via honest walk-forward + block bootstrap on the "
        "regime parameters.\n"
        "- **No frictions modelled**: zero commission, zero spread, zero slippage. "
        "Whipsaw-heavy short-lookback configs will look better here than in production.\n"
        "- **Pre-1980 SMA warmup buffer** is used for the long lookbacks (up to "
        f"{LOOKBACKS[-1]} days). Pre-1980 bars do not enter scores.\n"
        "- **Synthetic pre-inception data**: SSO/UPRO/GLD pre-2006/2009/2004 are testfol.io "
        "modelled series.\n"
        "- **No FX gain modelling** for USD/BRL; ranks of strategies are preserved because "
        "every strategy faces the same FX.\n"
    )

    lines.append("## Files\n")
    lines.append(
        "- [`results/sweep_full.csv`](./results/sweep_full.csv) — all "
        f"{manifest['sweep']['n_reports']} rows.\n"
        "- [`results/sweep_top20.csv`](./results/sweep_top20.csv) — top-20 per panel.\n"
        "- [`results/sweep_summary.json`](./results/sweep_summary.json) — top-5 per "
        "panel for quick inspection.\n"
        "- [`results/manifest.json`](./results/manifest.json) — exact runtime config.\n"
        "- 4 heatmap PNGs (per `on_leg × tax_scenario`) under `plots/`.\n"
        "- 2 top-K comparison PNGs (`top_k_equity_overlay.png`, "
        "`top_k_ratio_to_spy.png`) under `plots/`. Regenerate independently via "
        "`uv run python -m studies.lrs.phases.phase_1.plot_top_curves`.\n"
    )

    lines.append("## Citations\n")
    lines.append(
        "- SMA / EMA regime signal: `[leverage_for_the_long_run, p.13]`\n"
        "- 2×/3× leverage tested in paper: `[leverage_for_the_long_run, p.17, Table 8]`\n"
        "- MA-window sweep: `[leverage_for_the_long_run, p.14, Table 6]`\n"
        "- Cash off-leg precedent: `[leverage_for_the_long_run, p.21]`\n"
        "- Lei 14.754/2023 art. 5°/6° (BR 15% annual + indefinite loss carry-forward): "
        "https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2023/lei/l14754.htm\n"
        "- Multiple-testing overfit concerns motivating phase-2 honest walk-forward: "
        "`[advances_fin_ml, p.208-211]`, `[advances_fin_ml, p.222-223]`.\n"
    )

    return "\n".join(lines) + "\n"


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

    PLOTS_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    log.info("loading testfolio data (modern era from %s)...", MODERN_ERA_START.date())
    # GLDSIM is the binding inception constraint (1968-04). Pre-1980 buffer
    # only used for SMA-N warmup (up to lookback 300 days).
    modern = load_modern_data(MODERN_ERA_START, tickers=PHASE_1_TICKERS)
    prices = modern.full
    start_date = modern.scoring_start
    required = list(PHASE_1_TICKERS)
    if start_date < prices.index[0]:
        start_date = prices.index[prices.index.searchsorted(MODERN_ERA_START, side="left")]
    log.info(
        "data: %d bars  %s → %s  ·  scoring starts %s",
        len(prices), prices.index[0].date(), prices.index[-1].date(), start_date.date(),
    )

    spy = prices["SPYSIM"]
    spy_rets = spy.pct_change()
    benchmark = _build_benchmark(spy_rets, start_date)

    rows = _run_sweep(prices, spy, benchmark, start_date)
    df = pd.DataFrame([r.to_dict() for r in rows])
    log.info("sweep produced %d rows", len(df))

    # Save full CSV (this one is gitignored — 1.8k rows × ~14 cols).
    df_path = RESULTS_DIR / "sweep_full.csv"
    df.to_csv(df_path, index=False, float_format="%.6f")
    log.info("wrote %s (%.1f KB)", df_path.name, df_path.stat().st_size / 1024)

    # Top-20 per panel CSV.
    top_df = _top_n_per_panel(df, n=20)
    top_path = RESULTS_DIR / "sweep_top20.csv"
    top_df.to_csv(top_path, index=False, float_format="%.6f")
    log.info("wrote %s (%.1f KB)", top_path.name, top_path.stat().st_size / 1024)

    # Summary JSON: top-5 per panel.
    summary: dict[str, list[dict[str, Any]]] = {}
    for on_leg in ON_LEGS:
        for scenario in TAX_SCENARIOS:
            key = f"{on_leg}_{scenario}"
            sub = top_df[
                (top_df["on_leg"] == on_leg) & (top_df["tax_scenario"] == scenario)
            ].head(5).reset_index(drop=True)
            summary[key] = sub.to_dict(orient="records")
    (RESULTS_DIR / "sweep_summary.json").write_text(
        json.dumps(summary, indent=2, default=float) + "\n", encoding="utf-8"
    )

    # Heatmaps: one per (on_leg × tax_scenario), 4 total.
    log.info("rendering heatmaps...")
    for on_leg in ON_LEGS:
        for scenario in TAX_SCENARIOS:
            out = PLOTS_DIR / f"heatmap_{on_leg.lower()}_{scenario}.png"
            plot_sweep_heatmap(
                df, out,
                on_leg=on_leg, tax_scenario=scenario,
                risk_offs=RISK_OFFS, filters=FILTERS,
            )
            log.info("  %s (%.1f KB)", out.name, out.stat().st_size / 1024)

    # Top-K equity-curve comparison: re-simulates the top-5 phase-1 configs
    # per on-leg + phase-0 baseline + B&H references, renders 2 plots and
    # returns the terminal-multiples table for embedding in report.md.
    log.info("rendering top-K equity comparison plots...")
    top_k_table = render_top_k_comparison(prices, start_date, top_df, plots_dir=PLOTS_DIR)

    # Manifest.
    data_hash = hashlib.sha256(
        prices.values.tobytes() + b"|" + ",".join(prices.columns).encode()
    ).hexdigest()[:16]
    manifest = {
        "generated_at": pd.Timestamp.now(tz="UTC").isoformat(),
        "study": "lrs",
        "phase": "phase_1",
        "framework_version": "scoring-v1",
        "sweep": {
            "filters": list(FILTERS),
            "lookbacks": list(LOOKBACKS),
            "risk_offs": list(RISK_OFFS),
            "on_legs": list(ON_LEGS),
            "tax_scenarios": list(TAX_SCENARIOS),
            "n_configs": len(FILTERS) * len(LOOKBACKS) * len(RISK_OFFS) * len(ON_LEGS),
            "n_reports": len(df),
        },
        "parameters": {
            "modern_era_start": str(MODERN_ERA_START.date()),
            "band_pct": BAND_PCT,
            "tax_rate": TAX_RATE,
            "execution": "signal_close_T_exposure_T+1",
            "commission_bps": 0.0,
            "spread_bps": 0.0,
            "window_years": list(WINDOW_YEARS),
            "window_step_days": WINDOW_STEP_DAYS,
            "component_weights": dict(COMPONENT_WEIGHTS),
            "horizon_weights": {str(k): v for k, v in HORIZON_WEIGHTS.items()},
            "length_aggregation": "0.60 * mean + 0.40 * p25",
            "benchmark": "B&H SPY (tax-free)",
        },
        "data": {
            "source": "testfol.io synthetic",
            "tickers": required,
            "full_first_date": prices.index[0].strftime("%Y-%m-%d"),
            "full_last_date": prices.index[-1].strftime("%Y-%m-%d"),
            "n_full_bars": int(len(prices)),
            "data_hash_sha256_16": data_hash,
        },
        "curves": {
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": prices.index[-1].strftime("%Y-%m-%d"),
            "n_days": int(len(prices.loc[start_date:])),
        },
    }
    (RESULTS_DIR / "manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )

    # Report.md
    REPORT_PATH.write_text(
        _render_report(manifest, df, top_df, top_k_table=top_k_table),
        encoding="utf-8",
    )
    log.info("done. artifacts under %s", PHASE_DIR)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""studies.lrs phase-0 runner — scoring-framework edition.

Builds 5 equity curves on the modern-era testfolio window (1980-01-01
onwards, with pre-1980 SMA warmup) under **two tax scenarios**:

* ``tax_free`` — pre-tax pretend world for the maximum-edge view.
* ``br_lei_14754`` — Brazil's offshore-financial-asset regime
  (annual 15% IR, indefinite loss carry-forward).

For each (strategy × scenario) it produces a rolling-window score via
:mod:`studies.lrs.scripts.scoring` against B&H SPY (tax-free) as the
universal benchmark, then writes plots and a report.

Usage::

    uv run python -m studies.lrs.phases.phase_0.run

See ``studies/lrs/SPEC.md`` for the framework definition.
"""
from __future__ import annotations

import hashlib
import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd

from market_lab.backtest.metrics.performance import (
    cagr,
    max_drawdown,
    returns_from_equity,
    sortino,
)
from market_lab.backtest.strategies.letf_rotation import compute_regime_signal
from studies.letf_rotation_hunt.core.plot_helper import (
    plot_tier_equity_overlay,
    plot_tier_relative_to_spy,
)
from studies.lrs.scripts.data import MODERN_ERA_START, load_modern_data
from studies.lrs.scripts.plots import plot_score_by_length, plot_score_timeline
from studies.lrs.scripts.scoring import (
    COMPONENT_WEIGHTS,
    HORIZON_WEIGHTS,
    ScoreReport,
    score_strategy,
)
from studies.lrs.scripts.tax import simulate_rotation_with_annual_tax

log = logging.getLogger("studies.lrs.phase_0")

PHASE_DIR = Path(__file__).resolve().parent
PLOTS_DIR = PHASE_DIR / "plots"
RESULTS_DIR = PHASE_DIR / "results"
REPORT_PATH = PHASE_DIR / "report.md"

# --- Phase-0 parameters (see SPEC.md for citations) ---
SMA_LOOKBACK = 200
SMA_FILTER = "SMA"
BAND_PCT = 0.0
TAX_RATE = 0.15
WINDOW_YEARS = (1, 3, 5, 10, 15, 20)
WINDOW_STEP_DAYS = 21    # ~ monthly cadence


@dataclass(frozen=True)
class CurvePair:
    """Tax-free + taxed equity curves for one strategy, plus diagnostics."""

    name: str
    tax_free_equity: pd.Series
    taxed_equity: pd.Series
    n_switches: int            # 0 for B&H
    n_tax_events: int          # 0 for B&H (no realised gains during window)
    total_tax_paid: float      # equity units debited as IR


def _build_curves(
    spy_rets: pd.Series,
    sso_rets: pd.Series,
    upro_rets: pd.Series,
    signal: pd.Series,
    start_date: pd.Timestamp,
) -> dict[str, CurvePair]:
    """Build the 5 strategies under both tax scenarios."""

    def _bh(name: str, rets: pd.Series) -> CurvePair:
        r = rets.loc[start_date:].astype(float).fillna(0.0)
        eq = (1.0 + r).cumprod()
        eq.iloc[0] = 1.0
        # Buy-and-hold never realises during the window → both scenarios identical.
        return CurvePair(name=name, tax_free_equity=eq, taxed_equity=eq.copy(),
                         n_switches=0, n_tax_events=0, total_tax_paid=0.0)

    def _lrs(name: str, rets: pd.Series) -> CurvePair:
        sim = simulate_rotation_with_annual_tax(
            rets.loc[start_date:],
            signal.loc[start_date:],
            tax_rate=TAX_RATE,
        )
        return CurvePair(
            name=name,
            tax_free_equity=sim.pretax_equity,
            taxed_equity=sim.equity,
            n_switches=sim.n_switches,
            n_tax_events=len(sim.tax_events),
            total_tax_paid=sim.total_tax_paid,
        )

    return {
        "B&H SPY":  _bh("B&H SPY",  spy_rets),
        "B&H SSO":  _bh("B&H SSO",  sso_rets),
        "B&H UPRO": _bh("B&H UPRO", upro_rets),
        "LRS-SSO":  _lrs("LRS-SSO",  sso_rets),
        "LRS-UPRO": _lrs("LRS-UPRO", upro_rets),
    }


def _full_period_metrics(equity: pd.Series) -> dict[str, float]:
    """Companion full-window stats (not part of the score itself)."""
    eq = equity.dropna()
    rets = returns_from_equity(eq)
    return {
        "start_date": eq.index[0].strftime("%Y-%m-%d"),
        "end_date": eq.index[-1].strftime("%Y-%m-%d"),
        "n_days": int(len(eq)),
        "terminal_multiple": float(eq.iloc[-1] / eq.iloc[0]),
        "cagr": float(cagr(eq)),
        "max_drawdown": float(max_drawdown(eq)),
        "sortino": float(sortino(rets)),
    }


def _sanity_checks(
    reports: dict[str, dict[str, ScoreReport]],
    curves: dict[str, CurvePair],
) -> list[str]:
    """Lightweight invariants. Returns a list of failure messages (empty = pass)."""
    failures: list[str] = []

    # 1. B&H SPY scored against B&H SPY must be ≈ 0 in both scenarios.
    for scenario in ("tax_free", "br_lei_14754"):
        rep = reports["B&H SPY"][scenario]
        if abs(rep.final_score) > 0.02:
            failures.append(
                f"B&H SPY self-score (scenario={scenario}) is {rep.final_score:+.4f}, "
                f"expected within ±0.02"
            )

    # 2. Tax can only hurt, never help, when there are realised gains.
    for name in ("LRS-SSO", "LRS-UPRO"):
        free_score = reports[name]["tax_free"].final_score
        taxed_score = reports[name]["br_lei_14754"].final_score
        if taxed_score > free_score + 1e-9:
            failures.append(
                f"{name} taxed score ({taxed_score:+.4f}) > tax-free ({free_score:+.4f}); "
                "tax should never improve the score"
            )

    # 3. B&H curves: tax-free and taxed scores identical (no realised gains).
    for name in ("B&H SPY", "B&H SSO", "B&H UPRO"):
        free_score = reports[name]["tax_free"].final_score
        taxed_score = reports[name]["br_lei_14754"].final_score
        if abs(free_score - taxed_score) > 1e-9:
            failures.append(
                f"{name} tax-free ({free_score:+.4f}) ≠ taxed ({taxed_score:+.4f}); "
                "B&H realises nothing during the window so they must match"
            )

    # 4. Tax drag non-negative and finite for rotation curves.
    for name in ("LRS-SSO", "LRS-UPRO"):
        t = curves[name].total_tax_paid
        if t < 0 or not pd.notna(t) or t == float("inf"):
            failures.append(f"{name} total_tax_paid invalid: {t}")

    # 5. Window counts in reasonable range (1y monthly ≈ 528, 20y ≈ 312 on 45y data).
    rep = reports["B&H SPY"]["tax_free"]
    expected = {1: 525, 3: 500, 5: 480, 10: 420, 15: 360, 20: 300}
    for years, exp in expected.items():
        agg = rep.per_length.get(years)
        if agg is None:
            failures.append(f"missing per-length aggregate for {years}y")
            continue
        if abs(agg.n_windows - exp) / exp > 0.20:
            failures.append(
                f"{years}y window count {agg.n_windows} far from expected ~{exp}"
            )

    return failures


def _render_report(
    manifest: dict[str, Any],
    reports: dict[str, dict[str, ScoreReport]],
    curves: dict[str, CurvePair],
    full_metrics: dict[str, dict[str, dict[str, float]]],
    failures: list[str],
) -> str:
    lines: list[str] = []
    lines.append("# studies/lrs — Phase 0 Report (scoring-framework edition)\n")
    lines.append(
        f"Generated: {manifest['generated_at']}  ·  "
        f"data: testfol.io  ·  scoring window: "
        f"{manifest['curves']['start_date']} → {manifest['curves']['end_date']} "
        f"({manifest['curves']['n_days']} bars)\n"
    )

    lines.append("## Hypothesis\n")
    lines.append(
        "When SPY closes above its 200-day SMA, a 2× or 3× S&P-500 LETF "
        "outperforms unlevered SPY net of BR taxes; when SPY closes below, "
        "holding cash dominates riding the LETF down. "
        "`[leverage_for_the_long_run, p.13]`\n"
    )

    lines.append("## Parameters\n")
    lines.append("| Parameter | Value |")
    lines.append("|---|---|")
    lines.append("| Data source | testfol.io synthetic (SPYSIM / SSOSIM / UPROSIM) |")
    lines.append(
        f"| Scoring window | {manifest['curves']['start_date']} → "
        f"{manifest['curves']['end_date']} ({manifest['curves']['n_days']} bars) |"
    )
    lines.append(f"| Filter / lookback / band | {SMA_FILTER} / {SMA_LOOKBACK}d / {BAND_PCT:.0%} |")
    lines.append("| Execution | signal close T → exposure T+1 (no lookahead) |")
    lines.append("| Cash off-leg yield | 0% |")
    lines.append("| Commission / spread | 0 bps |")
    lines.append(f"| Tax rate | {TAX_RATE:.0%} on net annual realised gain (Lei 14.754 art. 5°) |")
    lines.append(
        "| Tax cadence | annual settlement, first bar of next calendar year; "
        "loss carry-forward indefinite (Lei 14.754 art. 6°) |"
    )
    lines.append(
        f"| Window lengths | {', '.join(f'{y}y' for y in WINDOW_YEARS)}, "
        f"step ~{WINDOW_STEP_DAYS}d (monthly) |"
    )
    cw = COMPONENT_WEIGHTS
    lines.append(
        f"| Within-window weights | terminal {cw['terminal']:.0%}, time_above {cw['time_above']:.0%}, "
        f"sortino {cw['sortino']:.0%}, calmar {cw['calmar']:.0%} (signed, tanh-squashed) |"
    )
    lines.append("| Per-length aggregation | 0.60·mean + 0.40·p25 |")
    hw = HORIZON_WEIGHTS
    lines.append(
        f"| Across-length weights | 1y={hw[1]:.0%}, 3y={hw[3]:.0%}, 5y={hw[5]:.0%}, "
        f"10y={hw[10]:.0%}, 15y={hw[15]:.0%}, 20y={hw[20]:.0%} |"
    )
    lines.append("| Benchmark | B&H SPY (tax-free) for every strategy |")
    lines.append("")

    # Final-score panel for both scenarios.
    lines.append("## Final scores\n")
    lines.append("| Strategy | Tax-free | BR Lei 14.754 | Δ (tax cost) |")
    lines.append("|---|---:|---:|---:|")
    for name in ("B&H SPY", "B&H SSO", "B&H UPRO", "LRS-SSO", "LRS-UPRO"):
        f_free = reports[name]["tax_free"].final_score
        f_tax = reports[name]["br_lei_14754"].final_score
        lines.append(f"| {name} | {f_free:+.4f} | {f_tax:+.4f} | {f_tax - f_free:+.4f} |")
    lines.append("")

    # Winner highlight.
    free_ranked = sorted(
        ((n, reports[n]["tax_free"].final_score) for n in reports),
        key=lambda kv: -kv[1],
    )
    tax_ranked = sorted(
        ((n, reports[n]["br_lei_14754"].final_score) for n in reports),
        key=lambda kv: -kv[1],
    )
    lines.append(
        f"- **Tax-free leader**: {free_ranked[0][0]} (score {free_ranked[0][1]:+.4f}).\n"
        f"- **BR Lei 14.754 leader**: {tax_ranked[0][0]} (score {tax_ranked[0][1]:+.4f})."
    )
    lines.append("")

    # Per-length aggregates for the two LRS strategies (the interesting ones).
    for name in ("LRS-SSO", "LRS-UPRO"):
        lines.append(f"### Per-length aggregates — {name}\n")
        lines.append(
            "| Window | n | %win (free) | mean (free) | p25 (free) | length_score (free) "
            "| %win (tax) | mean (tax) | p25 (tax) | length_score (tax) |"
        )
        lines.append(
            "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|"
        )
        free_per = reports[name]["tax_free"].per_length
        tax_per = reports[name]["br_lei_14754"].per_length
        for years in WINDOW_YEARS:
            f = free_per.get(years)
            t = tax_per.get(years)
            if f is None or t is None:
                continue
            lines.append(
                f"| {years}y | {f.n_windows} "
                f"| {f.pct_outperforming:.0%} | {f.mean_score:+.3f} | {f.p25_score:+.3f} "
                f"| {f.length_score:+.3f} "
                f"| {t.pct_outperforming:.0%} | {t.mean_score:+.3f} | {t.p25_score:+.3f} "
                f"| {t.length_score:+.3f} |"
            )
        lines.append("")

    # Companion full-window metrics (legacy view — kept for context only).
    lines.append("## Companion full-window stats (context only — not part of the score)\n")
    lines.append("| Strategy | Scenario | Terminal× | CAGR | MDD | Sortino | Switches | Tax events | Tax drag |")
    lines.append("|---|---|---:|---:|---:|---:|---:|---:|---:|")
    for name in ("B&H SPY", "B&H SSO", "B&H UPRO", "LRS-SSO", "LRS-UPRO"):
        for scenario in ("tax_free", "br_lei_14754"):
            m = full_metrics[name][scenario]
            c = curves[name]
            switches = c.n_switches if scenario == "br_lei_14754" else (c.n_switches if name.startswith("LRS") else 0)
            tax_events = c.n_tax_events if scenario == "br_lei_14754" else 0
            tax_drag = c.total_tax_paid if scenario == "br_lei_14754" else 0.0
            lines.append(
                f"| {name} | {scenario} | {m['terminal_multiple']:,.1f}× | "
                f"{m['cagr']:.2%} | {m['max_drawdown']:.2%} | {m['sortino']:.2f} | "
                f"{switches} | {tax_events} | {tax_drag:.3f} |"
            )
    lines.append("")

    lines.append("## Plots\n")
    lines.append("Equity overlay (log scale, normalised at start):\n")
    lines.append("![equity overlay](plots/equity_overlay.png)\n")
    lines.append("Ratio to B&H SPY (log scale):\n")
    lines.append("![ratio to SPY](plots/ratio_to_spy.png)\n")
    lines.append("Rolling-window score timeline (one panel per window length, both tax scenarios):\n")
    lines.append("![score timeline](plots/score_timeline.png)\n")
    lines.append("Window-score distribution by length and tax scenario:\n")
    lines.append("![score by length](plots/score_by_length.png)\n")

    if failures:
        lines.append("## ⚠️ Sanity-check failures\n")
        for f in failures:
            lines.append(f"- {f}")
        lines.append("")
    else:
        lines.append("## Sanity checks — all passed ✔\n")

    lines.append("## Caveats\n")
    lines.append(
        "- Pre-2006/2009 SSO/UPRO bars are synthetic (Gayed `r = L·r_SPX − fee/252`), not measured.\n"
        "- No commission / spread / slippage modelled — a whipsaw-heavy signal looks better here than in production.\n"
        "- FX gain on USD/BRL is **not** modelled; real BR investors pay IR on FX appreciation. "
        "Ranks of strategies are preserved because all see the same FX.\n"
        "- Tax base assumes long-term 15% (Lei 14.754 art. 5°); day-trade and the BR-domiciled R$ 35k/month rules don't apply to US-listed ETFs.\n"
        "- B&H curves realise no gain during the window so their tax-free and taxed scores are identical "
        "— this matches a held-forever BR investor.\n"
        "- Single-window descriptive run — no walk-forward, no PBO/DSR. See out-of-scope section in SPEC.md.\n"
    )

    lines.append("## Suggestions for phase 1+\n")
    lines.append(
        "- Layer realistic frictions: Inter Internacional commission, ~5 bps spread per switch.\n"
        "- Cash off-leg via CASHX (Fed Funds proxy) — material when FFR > 3%.\n"
        "- Walk-forward + block bootstrap on the regime parameters (lookback, band).\n"
        "- Tiingo real-ETF overlay for 2009+ OOS sanity vs synthesised SSOSIM/UPROSIM.\n"
        "- Sweep MA window {50, 100, 125, 150, 200} per Gayed Table 6 "
        "`[leverage_for_the_long_run, p.14]`.\n"
    )

    lines.append("## Citations\n")
    lines.append(
        "- SMA200 regime signal: `[leverage_for_the_long_run, p.13]`\n"
        "- 2×/3× leverage tested in paper: `[leverage_for_the_long_run, p.17, Table 8]`\n"
        "- Cash off-leg (not BIL): `[leverage_for_the_long_run, p.21]`\n"
        "- Synthetic LETF formula: `[leverage_for_the_long_run, p.16]`\n"
        "- Lei 14.754/2023 art. 5°/6° (BR offshore IR, 15%, indefinite loss carry-forward): "
        "https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2023/lei/l14754.htm\n"
        "- Sortino & Price (1994) — downside-only volatility, precedent in `[advances_fin_ml, p.41-43]`.\n"
        "- Vectorized rolling-metric implementation precedent: "
        "`studies/static_spy_beater_portfolio/scripts/score_portfolio.py`.\n"
        "- BR mandate context: `docs/investment-mandate.md` §1.\n"
    )

    return "\n".join(lines) + "\n"


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

    PLOTS_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    log.info("loading testfolio data with modern-era cutoff %s...", MODERN_ERA_START.date())
    modern = load_modern_data(MODERN_ERA_START)
    prices = modern.full
    start_date = modern.scoring_start
    log.info(
        "  full data: %d bars  %s → %s  ·  scoring starts %s",
        len(prices), prices.index[0].date(), prices.index[-1].date(), start_date.date(),
    )

    spy = prices["SPYSIM"]
    sso = prices["SSOSIM"]
    upro = prices["UPROSIM"]
    spy_rets = spy.pct_change()
    sso_rets = sso.pct_change()
    upro_rets = upro.pct_change()

    log.info("computing SMA%d regime signal on SPY (pre-1980 buffer used for warmup)...",
             SMA_LOOKBACK)
    signal = compute_regime_signal(spy, filter=SMA_FILTER, lookback=SMA_LOOKBACK, band_pct=BAND_PCT)

    log.info("building 5 strategies under tax-free + br_lei_14754 scenarios...")
    curves = _build_curves(spy_rets, sso_rets, upro_rets, signal, start_date)
    benchmark = curves["B&H SPY"].tax_free_equity     # universal benchmark

    log.info("scoring (rolling windows %s, monthly step)...",
             [f"{y}y" for y in WINDOW_YEARS])
    reports: dict[str, dict[str, ScoreReport]] = {}
    for name, pair in curves.items():
        reports[name] = {
            "tax_free": score_strategy(
                pair.tax_free_equity, benchmark,
                strategy_name=name, tax_scenario="tax_free",
                window_years=WINDOW_YEARS, window_step_days=WINDOW_STEP_DAYS,
            ),
            "br_lei_14754": score_strategy(
                pair.taxed_equity, benchmark,
                strategy_name=name, tax_scenario="br_lei_14754",
                window_years=WINDOW_YEARS, window_step_days=WINDOW_STEP_DAYS,
            ),
        }
        f_free = reports[name]["tax_free"].final_score
        f_tax = reports[name]["br_lei_14754"].final_score
        log.info("  %-10s  tax-free=%+0.4f   br_lei_14754=%+0.4f   Δ=%+0.4f",
                 name, f_free, f_tax, f_tax - f_free)

    log.info("companion full-period metrics...")
    full_metrics: dict[str, dict[str, dict[str, float]]] = {}
    for name, pair in curves.items():
        full_metrics[name] = {
            "tax_free": _full_period_metrics(pair.tax_free_equity),
            "br_lei_14754": _full_period_metrics(pair.taxed_equity),
        }

    log.info("rendering plots...")
    overlay_curves = {name: pair.taxed_equity for name, pair in curves.items() if name != "B&H SPY"}
    rank_by = {name: reports[name]["br_lei_14754"].final_score for name in overlay_curves}
    plot_tier_equity_overlay(
        equity_curves=overlay_curves,
        spy_equity=benchmark,
        out_path=PLOTS_DIR / "equity_overlay.png",
        title=f"studies/lrs phase-0 — equity overlay 1980+ (BR Lei 14.754 scenario, log scale)",
        top_n_bold=len(overlay_curves),
        rank_by=rank_by,
    )
    plot_tier_relative_to_spy(
        equity_curves=overlay_curves,
        spy_equity=benchmark,
        out_path=PLOTS_DIR / "ratio_to_spy.png",
        title="studies/lrs phase-0 — strategy / B&H SPY (BR Lei 14.754 scenario, log scale)",
        top_n_bold=len(overlay_curves),
        rank_by=rank_by,
    )
    flat_reports = [r for s in reports.values() for r in s.values()]
    plot_score_timeline(flat_reports, PLOTS_DIR / "score_timeline.png", window_years=WINDOW_YEARS)
    plot_score_by_length(flat_reports, PLOTS_DIR / "score_by_length.png", window_years=WINDOW_YEARS)

    log.info("writing artifacts...")
    equity_df = pd.concat(
        {
            f"{name} ({scenario})": (pair.tax_free_equity if scenario == "tax_free" else pair.taxed_equity)
            for name, pair in curves.items()
            for scenario in ("tax_free", "br_lei_14754")
        },
        axis=1,
    )
    equity_df.index.name = "date"
    equity_df.to_csv(RESULTS_DIR / "equity.csv", float_format="%.10f")

    metrics_payload = {
        name: {scenario: full_metrics[name][scenario] for scenario in ("tax_free", "br_lei_14754")}
        for name in full_metrics
    }
    (RESULTS_DIR / "metrics.json").write_text(
        json.dumps(metrics_payload, indent=2) + "\n", encoding="utf-8"
    )

    # scores.json: aggregated summary only (small, committable). The raw
    # per-window scores are visible in the plots; if you need them numerically,
    # the timeline plot has all the detail, and re-running run.py regenerates
    # the same windows deterministically from the same data.
    scores_summary: dict[str, Any] = {
        name: {scenario: rep.summary_dict() for scenario, rep in scenarios.items()}
        for name, scenarios in reports.items()
    }
    (RESULTS_DIR / "scores.json").write_text(
        json.dumps(scores_summary, indent=2) + "\n", encoding="utf-8"
    )

    data_hash = hashlib.sha256(
        prices.values.tobytes() + b"|" + ",".join(prices.columns).encode()
    ).hexdigest()[:16]
    manifest = {
        "generated_at": pd.Timestamp.now(tz="UTC").isoformat(),
        "study": "lrs",
        "phase": "phase_0",
        "framework_version": "scoring-v1",
        "parameters": {
            "modern_era_start": str(MODERN_ERA_START.date()),
            "filter": SMA_FILTER,
            "lookback": SMA_LOOKBACK,
            "band_pct": BAND_PCT,
            "tax_rate": TAX_RATE,
            "tax_cadence": "annual_first_bar_next_year_lei_14754",
            "loss_carry_forward": "indefinite",
            "off_leg_yield": 0.0,
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
            "source": "testfol.io synthetic (SPYSIM/SSOSIM/UPROSIM)",
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

    log.info("running sanity checks...")
    failures = _sanity_checks(reports, curves)
    if failures:
        for f in failures:
            log.error("  SANITY FAIL: %s", f)
    else:
        log.info("  all sanity checks passed")

    log.info("rendering report.md...")
    REPORT_PATH.write_text(
        _render_report(manifest, reports, curves, full_metrics, failures),
        encoding="utf-8",
    )

    log.info("done. artifacts under %s", PHASE_DIR)
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())

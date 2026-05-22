"""studies.lrs phase-0 runner.

Builds 5 equity curves on the common testfolio history of SPYSIM /
SSOSIM / UPROSIM and writes plots, metrics, and a report into
``studies/lrs/phases/phase_0/``.

Usage::

    uv run python -m studies.lrs.phases.phase_0.run

See ``studies/lrs/SPEC.md`` for full parameters and citations.
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
    sharpe,
    sortino,
)
from market_lab.backtest.strategies.letf_rotation import compute_regime_signal
from studies.letf_rotation_hunt.core.plot_helper import (
    plot_tier_equity_overlay,
    plot_tier_relative_to_spy,
)
from studies.lrs.scripts.data import load_phase0_data
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


@dataclass(frozen=True)
class CurveResult:
    """Equity + metrics + ledger for one of the 5 curves."""

    name: str
    equity: pd.Series
    n_switches: int
    n_tax_events: int
    total_tax_paid: float


def _bh_curve(name: str, returns: pd.Series, start_date: pd.Timestamp) -> CurveResult:
    """Buy-and-hold equity from a returns series, starting at 1.0 on ``start_date``."""
    r = returns.loc[start_date:].astype(float).fillna(0.0)
    eq = (1.0 + r).cumprod()
    eq.iloc[0] = 1.0  # ensure normalisation
    return CurveResult(name=name, equity=eq, n_switches=0, n_tax_events=0, total_tax_paid=0.0)


def _lrs_curve(
    name: str,
    asset_returns: pd.Series,
    signal: pd.Series,
    start_date: pd.Timestamp,
    tax_rate: float,
) -> CurveResult:
    """Rotation curve with BR annual realized-gain tax."""
    rets = asset_returns.loc[start_date:]
    sig = signal.loc[start_date:]
    sim = simulate_rotation_with_annual_tax(rets, sig, tax_rate=tax_rate)
    return CurveResult(
        name=name,
        equity=sim.equity,
        n_switches=sim.n_switches,
        n_tax_events=len(sim.tax_events),
        total_tax_paid=sim.total_tax_paid,
    )


def _metrics(curve: CurveResult) -> dict[str, Any]:
    eq = curve.equity.dropna()
    rets = returns_from_equity(eq)
    out = {
        "start_date": eq.index[0].strftime("%Y-%m-%d"),
        "end_date": eq.index[-1].strftime("%Y-%m-%d"),
        "n_days": int(len(eq)),
        "terminal_multiple": float(eq.iloc[-1] / eq.iloc[0]),
        "cagr": float(cagr(eq)),
        "max_drawdown": float(max_drawdown(eq)),
        "sharpe": float(sharpe(rets)),
        "sortino": float(sortino(rets)),
        "n_switches": int(curve.n_switches),
        "n_tax_events": int(curve.n_tax_events),
        "total_tax_paid": float(curve.total_tax_paid),
    }
    return out


def _sanity_checks(curves: dict[str, CurveResult], metrics: dict[str, dict[str, Any]]) -> list[str]:
    """Phase-0 sanity checks. Returns list of failures (empty = pass)."""
    failures: list[str] = []

    # All 5 curves share start / end date.
    starts = {name: m["start_date"] for name, m in metrics.items()}
    ends = {name: m["end_date"] for name, m in metrics.items()}
    if len(set(starts.values())) != 1:
        failures.append(f"curves have different start_dates: {starts}")
    if len(set(ends.values())) != 1:
        failures.append(f"curves have different end_dates: {ends}")

    # No NaNs in any equity curve after the first bar.
    for name, c in curves.items():
        n_nan = int(c.equity.isna().sum())
        if n_nan > 0:
            failures.append(f"{name} has {n_nan} NaN values in equity")

    # B&H SSO CAGR > B&H SPY CAGR (long-history leverage premium).
    if metrics["B&H SSO"]["cagr"] <= metrics["B&H SPY"]["cagr"]:
        failures.append(
            f"B&H SSO CAGR ({metrics['B&H SSO']['cagr']:.4f}) not > "
            f"B&H SPY CAGR ({metrics['B&H SPY']['cagr']:.4f}) — suspicious"
        )

    # B&H UPRO MDD > B&H SSO MDD > B&H SPY MDD (more leverage = bigger drawdown).
    spy_mdd = metrics["B&H SPY"]["max_drawdown"]
    sso_mdd = metrics["B&H SSO"]["max_drawdown"]
    upro_mdd = metrics["B&H UPRO"]["max_drawdown"]
    if not (upro_mdd > sso_mdd > spy_mdd):
        failures.append(
            f"MDD ordering broken: SPY={spy_mdd:.4f} SSO={sso_mdd:.4f} UPRO={upro_mdd:.4f}"
        )

    # Tax drag non-negative and finite.
    for name in ("LRS-SSO", "LRS-UPRO"):
        tax = metrics[name]["total_tax_paid"]
        if tax < 0 or not pd.notna(tax) or tax == float("inf"):
            failures.append(f"{name} total_tax_paid invalid: {tax}")

    return failures


def _render_report(
    manifest: dict[str, Any],
    metrics: dict[str, dict[str, Any]],
    failures: list[str],
) -> str:
    """Produce the markdown report content."""
    lines: list[str] = []
    lines.append("# studies/lrs — Phase 0 Report\n")
    lines.append(
        f"Generated: {manifest['generated_at']}  ·  "
        f"data: testfol.io ({manifest['data']['common_first_date']} → "
        f"{manifest['data']['common_last_date']}, {manifest['data']['n_bars']} bars)\n"
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
    lines.append(f"| Data source | testfol.io synthetic (SPYSIM / SSOSIM / UPROSIM) |")
    lines.append(
        f"| Period | {manifest['curves']['start_date']} → "
        f"{manifest['curves']['end_date']} ({manifest['curves']['n_days']} bars) |"
    )
    lines.append(f"| Filter / lookback / band | {SMA_FILTER} / {SMA_LOOKBACK}d / {BAND_PCT:.0%} |")
    lines.append(f"| Execution | signal close T → exposure T+1 |")
    lines.append(f"| Cash off-leg yield | 0% |")
    lines.append(f"| Commission / spread | 0 bps |")
    lines.append(f"| Tax rate / cadence | {TAX_RATE:.0%} / annual, first bar of next year |")
    lines.append("")

    lines.append("## Metrics\n")
    header = ("| Curve | Start | End | Terminal× | CAGR | MDD | Sharpe | Sortino "
              "| Switches | Tax events | Tax drag |")
    sep = "|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|"
    lines.append(header)
    lines.append(sep)
    for name in ("B&H SPY", "B&H SSO", "B&H UPRO", "LRS-SSO", "LRS-UPRO"):
        m = metrics[name]
        lines.append(
            f"| {name} | {m['start_date']} | {m['end_date']} "
            f"| {m['terminal_multiple']:,.1f}× | {m['cagr']:.2%} | {m['max_drawdown']:.2%} "
            f"| {m['sharpe']:.2f} | {m['sortino']:.2f} "
            f"| {m['n_switches']} | {m['n_tax_events']} | {m['total_tax_paid']:.2f} |"
        )
    lines.append("")

    lines.append("## Plots\n")
    lines.append("Equity overlay (log scale, normalised to 1.0 at start):\n")
    lines.append("![equity overlay](plots/equity_overlay.png)\n")
    lines.append("Ratio to B&H SPY (log scale):\n")
    lines.append("![ratio to SPY](plots/ratio_to_spy.png)\n")

    lines.append("## Observations\n")
    spy_cagr = metrics["B&H SPY"]["cagr"]
    sso_cagr = metrics["B&H SSO"]["cagr"]
    upro_cagr = metrics["B&H UPRO"]["cagr"]
    lrs_sso_cagr = metrics["LRS-SSO"]["cagr"]
    lrs_upro_cagr = metrics["LRS-UPRO"]["cagr"]
    spy_mdd = metrics["B&H SPY"]["max_drawdown"]
    sso_mdd = metrics["B&H SSO"]["max_drawdown"]
    upro_mdd = metrics["B&H UPRO"]["max_drawdown"]
    lrs_sso_mdd = metrics["LRS-SSO"]["max_drawdown"]
    lrs_upro_mdd = metrics["LRS-UPRO"]["max_drawdown"]

    def _verdict_cagr(strat: str, bh: str, s_cagr: float, b_cagr: float) -> str:
        delta = s_cagr - b_cagr
        word = "beats" if delta > 0 else "trails"
        return f"{strat} {word} {bh} by {abs(delta):.2%} CAGR (post-BR-tax)."

    def _verdict_mdd(strat: str, bh: str, s_mdd: float, b_mdd: float) -> str:
        delta = b_mdd - s_mdd
        word = "reduces" if delta > 0 else "deepens"
        return f"{strat} {word} the {bh} drawdown by {abs(delta):.2%} ({s_mdd:.2%} vs {b_mdd:.2%})."

    lines.append(f"- {_verdict_cagr('LRS-SSO', 'B&H SSO', lrs_sso_cagr, sso_cagr)}")
    lines.append(f"- {_verdict_mdd('LRS-SSO', 'B&H SSO', lrs_sso_mdd, sso_mdd)}")
    lines.append(f"- {_verdict_cagr('LRS-UPRO', 'B&H UPRO', lrs_upro_cagr, upro_cagr)}")
    lines.append(f"- {_verdict_mdd('LRS-UPRO', 'B&H UPRO', lrs_upro_mdd, upro_mdd)}")
    lines.append(f"- {_verdict_cagr('LRS-SSO', 'B&H SPY', lrs_sso_cagr, spy_cagr)}")
    lines.append(f"- {_verdict_cagr('LRS-UPRO', 'B&H SPY', lrs_upro_cagr, spy_cagr)}")
    lines.append("")

    if failures:
        lines.append("## ⚠️ Sanity-check failures\n")
        for f in failures:
            lines.append(f"- {f}")
        lines.append("")
    else:
        lines.append("## Sanity checks — all passed ✔\n")

    lines.append("## Caveats\n")
    lines.append(
        "- Pre-2006/2009 SSO/UPRO bars are synthetic (Gayed `r = L·r_SPX − fee/252`), "
        "not measured.\n"
        "- No commission / spread / slippage modelled. A whipsaw-heavy signal will "
        "look better here than in production.\n"
        "- Single-window descriptive run — no walk-forward, no PBO/DSR. See SPEC.md "
        "out-of-scope section.\n"
        "- Cash off-leg yields 0%, ignoring Fed Funds. Layer CASHX in phase-1+ if "
        "signal proves out.\n"
    )

    lines.append("## Suggestions for phase 1+\n")
    lines.append(
        "- Add CASHX as off-leg (Fed Funds proxy) and re-measure.\n"
        "- Layer realistic frictions: Inter Internacional commission, ~5 bps spread per switch.\n"
        "- Walk-forward + bootstrap CI on the regime-rule parameters (lookback, band).\n"
        "- Tiingo real-ETF overlay (2009+) for SSO/UPRO post-inception OOS sanity check.\n"
        "- Regime stratification: bull/bear/sideways performance attribution.\n"
        "- Sweep MA window {50, 100, 125, 150, 200} per Gayed Table 6 "
        "`[leverage_for_the_long_run, p.14]`.\n"
    )

    lines.append("## Citations\n")
    lines.append(
        "- SMA200 regime signal: `[leverage_for_the_long_run, p.13]`\n"
        "- 2× / 3× leverage tested in paper: `[leverage_for_the_long_run, p.17, Table 8]`\n"
        "- Cash off-leg (not BIL): `[leverage_for_the_long_run, p.21]`\n"
        "- Synthetic LETF formula: `[leverage_for_the_long_run, p.16]`\n"
        "- BR 15% IR on US-listed ETF gains: `docs/investment-mandate.md` §1\n"
        "- testfol.io as long-history source: Phase 3.5b Task 7a cross-check\n"
    )

    return "\n".join(lines) + "\n"


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

    PLOTS_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    log.info("loading testfolio data (SPYSIM / SSOSIM / UPROSIM)...")
    prices = load_phase0_data()
    log.info("  %d bars  %s → %s", len(prices), prices.index[0].date(), prices.index[-1].date())

    spy = prices["SPYSIM"]
    sso = prices["SSOSIM"]
    upro = prices["UPROSIM"]
    spy_rets = spy.pct_change()
    sso_rets = sso.pct_change()
    upro_rets = upro.pct_change()

    log.info("computing SMA%d regime signal on SPY...", SMA_LOOKBACK)
    signal = compute_regime_signal(spy, filter=SMA_FILTER, lookback=SMA_LOOKBACK, band_pct=BAND_PCT)

    # Start all curves at the first bar with a valid prior signal,
    # i.e., the bar where signal.shift(1) is defined (== "ON" or "OFF").
    first_valid = signal.dropna().index[0]
    start_idx_pos = prices.index.get_loc(first_valid) + 1
    if start_idx_pos >= len(prices.index):
        raise RuntimeError("not enough data after SMA warmup")
    start_date = prices.index[start_idx_pos]
    log.info("  first signal valid: %s  →  curves start: %s",
             first_valid.date(), start_date.date())

    curves: dict[str, CurveResult] = {
        "B&H SPY":  _bh_curve("B&H SPY",  spy_rets, start_date),
        "B&H SSO":  _bh_curve("B&H SSO",  sso_rets, start_date),
        "B&H UPRO": _bh_curve("B&H UPRO", upro_rets, start_date),
        "LRS-SSO":  _lrs_curve("LRS-SSO",  sso_rets,  signal, start_date, TAX_RATE),
        "LRS-UPRO": _lrs_curve("LRS-UPRO", upro_rets, signal, start_date, TAX_RATE),
    }

    log.info("computing metrics...")
    metrics = {name: _metrics(c) for name, c in curves.items()}
    for name, m in metrics.items():
        log.info(
            "  %-10s  terminal=%.1f×  CAGR=%6.2f%%  MDD=%6.2f%%  Sharpe=%4.2f  switches=%d  tax=%.3f",
            name, m["terminal_multiple"], m["cagr"]*100, m["max_drawdown"]*100,
            m["sharpe"], m["n_switches"], m["total_tax_paid"],
        )

    log.info("rendering plots...")
    spy_eq = curves["B&H SPY"].equity
    strategy_curves = {name: c.equity for name, c in curves.items() if name != "B&H SPY"}
    rank_by = {name: metrics[name]["terminal_multiple"] for name in strategy_curves}
    plot_tier_equity_overlay(
        equity_curves=strategy_curves,
        spy_equity=spy_eq,
        out_path=PLOTS_DIR / "equity_overlay.png",
        title="studies/lrs phase-0 — equity overlay (B&H SPY in black, log scale)",
        top_n_bold=len(strategy_curves),
        rank_by=rank_by,
    )
    plot_tier_relative_to_spy(
        equity_curves=strategy_curves,
        spy_equity=spy_eq,
        out_path=PLOTS_DIR / "ratio_to_spy.png",
        title="studies/lrs phase-0 — strategy / B&H SPY (log scale)",
        top_n_bold=len(strategy_curves),
        rank_by=rank_by,
    )

    log.info("writing results artifacts...")
    equity_df = pd.concat({name: c.equity for name, c in curves.items()}, axis=1)
    equity_df.index.name = "date"
    equity_df.to_csv(RESULTS_DIR / "equity.csv", float_format="%.10f")

    (RESULTS_DIR / "metrics.json").write_text(
        json.dumps(metrics, indent=2) + "\n", encoding="utf-8"
    )

    data_hash = hashlib.sha256(
        prices.values.tobytes() + b"|" + ",".join(prices.columns).encode()
    ).hexdigest()[:16]
    manifest = {
        "generated_at": pd.Timestamp.now(tz="UTC").isoformat(),
        "study": "lrs",
        "phase": "phase_0",
        "parameters": {
            "filter": SMA_FILTER,
            "lookback": SMA_LOOKBACK,
            "band_pct": BAND_PCT,
            "tax_rate": TAX_RATE,
            "tax_cadence": "annual_first_bar_next_year",
            "off_leg_yield": 0.0,
            "execution": "signal_close_T_exposure_T+1",
            "commission_bps": 0.0,
            "spread_bps": 0.0,
        },
        "data": {
            "source": "testfol.io synthetic (SPYSIM/SSOSIM/UPROSIM)",
            "common_first_date": prices.index[0].strftime("%Y-%m-%d"),
            "common_last_date": prices.index[-1].strftime("%Y-%m-%d"),
            "n_bars": int(len(prices)),
            "data_hash_sha256_16": data_hash,
        },
        "curves": {
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": prices.index[-1].strftime("%Y-%m-%d"),
            "n_days": int(len(equity_df)),
        },
    }
    (RESULTS_DIR / "manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )

    log.info("running sanity checks...")
    failures = _sanity_checks(curves, metrics)
    if failures:
        for f in failures:
            log.error("  SANITY FAIL: %s", f)
    else:
        log.info("  all sanity checks passed")

    log.info("rendering report.md...")
    REPORT_PATH.write_text(_render_report(manifest, metrics, failures), encoding="utf-8")

    log.info("done. artifacts under %s", PHASE_DIR)
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Phase 3.5b supplementary — V1-V4 variants with LETF execution on QQQ/GLD legs.

Question: the production winner leverages only the SSO leg (2× via
Gayed regime filter). What if we also use QLD (2× QQQ) and UGL (2× GLD)
when the Donchian breakout says LONG — keeping the **signals** on the
1× underlying but executing at 2× when in position?

Four variants (all with SSO 2× baseline via SSOSIM, threshold-10pp rebal):

* **V1** — SSO / **QQQ 1×** / **GLD 1×** (current production winner)
* **V2** — SSO / **QLD 2×** / GLD 1× (leverage QQQ leg)
* **V3** — SSO / QQQ 1× / **UGL 2×** (leverage GLD leg)
* **V4** — SSO / **QLD 2×** / **UGL 2×** (leverage all 3 legs)

Ground-truth data: testfol.io SSOSIM / QQQSIM / QLDSIM / GLDSIM / UGLSIM
via ``data/testfolio/cache/history.parquet``. **Zero model risk** — no
``synthesize_letf_returns`` synthesis; testfol.io's FFR-aware cost model
is baked into each leveraged series directly (validated in Phase 3.5b
Task 7a).

Signals on 1× underlyings (SPYSIM for EMA100, QQQSIM/GLDSIM for
Donchian). Execution returns from the leveraged series (SSOSIM, QLDSIM
or UGLSIM) when regime = LONG; 0 when FLAT (cash).

Emits under ``reports/phase3_5b/variants_letf_execution/``:

* ``equity_vs_spy.png`` — 4 variants + SPYSIM B&H, log-scale 40y.
* ``drawdown_vs_spy.png`` — underwater curves.
* ``summary.json`` — per-variant metrics table.

Key caveat: **broker catalog dependency.** V2/V3/V4 require QLD/UGL
listed on Inter Global — not yet confirmed (only SSO is). If Inter
doesn't carry them, these variants are research-only.

Citations
---------
* testfol.io as ground-truth source for LETF cost: Phase 3.5b Task 7a.
* Regime filter (EMA strict cross): ``[leverage_for_the_long_run, p.8, p.13]``.
* Donchian 20/40 canonical: ``[trading_systems_methods, p.353]``.
* Threshold rebalance: ``[advances_fin_ml, p.275-278]``.
"""

from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path

import numpy as np
import pandas as pd

from ai_trade.backtest.data.testfolio_loader import load_testfolio_series
from ai_trade.backtest.metrics.rebalance_modes import apply_threshold_rebalance
from ai_trade.backtest.strategies.letf_rotation import compute_regime_signal
from ai_trade.backtest.strategies.tsmom import compute_donchian_signal

log = logging.getLogger("plano_b_variants_letf")

# Signal configs — identical to production winner.
LETF_FILTER = "EMA"
LETF_LOOKBACK = 100
LETF_BAND = 0.0
QQQ_ENTRY, QQQ_EXIT = 20, 10
GLD_ENTRY, GLD_EXIT = 40, 20

# Switch costs (applied on signal flips per leg).
SWITCH_COST_PCT = (10.0 + 5.0) / 10_000.0   # 10 bps commission + 5 bps spread
TAX_RATE = 0.15                              # BR IR on realized gain

# Variant weights dict
VARIANTS: dict[str, dict[str, str]] = {
    "V1_SSO_QQQ_GLD":  {"leg1": "SSOSIM", "leg2": "QQQSIM", "leg3": "GLDSIM"},
    "V2_SSO_QLD_GLD":  {"leg1": "SSOSIM", "leg2": "QLDSIM", "leg3": "GLDSIM"},
    "V3_SSO_QQQ_UGL":  {"leg1": "SSOSIM", "leg2": "QQQSIM", "leg3": "UGLSIM"},
    "V4_SSO_QLD_UGL":  {"leg1": "SSOSIM", "leg2": "QLDSIM", "leg3": "UGLSIM"},
}

VARIANT_COLORS = {
    "V1_SSO_QQQ_GLD": "#1f6feb",
    "V2_SSO_QLD_GLD": "#2ea043",
    "V3_SSO_QQQ_UGL": "#d4691a",
    "V4_SSO_QLD_UGL": "#e11d48",
}


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--output-dir", type=Path,
                    default=Path("reports/phase3_5b/variants_letf_execution"))
    ap.add_argument("--initial-capital", type=float, default=100_000.0)
    ap.add_argument("--threshold-pp", type=float, default=10.0)
    ap.add_argument("--log-level", default="INFO")
    return ap.parse_args(argv)


def _apply_regime_to_execution(
    in_position: pd.Series,
    execution_returns: pd.Series,
    switch_cost_pct: float,
    tax_rate: float,
) -> pd.Series:
    """Build net daily returns for a leg: execution_returns gated by in_position.

    * On each ``False → True`` transition (entry): deduct switch cost.
    * On each ``True → False`` transition (exit): deduct switch cost,
      then realize 15% tax on cumulative unrealized gain since entry.
    * While ``in_position`` is True: apply execution_returns[t].
    * Otherwise: 0.0 (cash).

    Returns a Series of daily net returns aligned to ``in_position.index``.
    """
    if not in_position.index.equals(execution_returns.index):
        raise ValueError("index mismatch between in_position and execution_returns")
    daily_net = pd.Series(0.0, index=in_position.index)
    equity = 1.0
    entry_equity = 1.0
    prev_state = False
    for ts in in_position.index:
        now_state = bool(in_position.loc[ts])
        prev_equity = equity
        if now_state != prev_state:
            equity -= equity * switch_cost_pct
            if prev_state:  # exiting — realize gain/tax
                gain = max(0.0, equity - entry_equity)
                equity -= gain * tax_rate
            if now_state:
                entry_equity = equity
            prev_state = now_state
        if now_state:
            r = float(execution_returns.loc[ts])
            equity *= (1.0 + r)
        daily_net.loc[ts] = (equity / prev_equity - 1.0) if prev_equity > 0 else 0.0
    return daily_net


def _build_leg_sso(
    spy_prices: pd.Series, sso_returns: pd.Series
) -> pd.Series:
    """SSO leg: EMA100 regime on SPY; execution via SSOSIM when ON."""
    regime = compute_regime_signal(
        spy_prices, filter=LETF_FILTER, lookback=LETF_LOOKBACK,
        band_pct=LETF_BAND,
    )
    in_pos = (regime == "ON").astype(bool).reindex(sso_returns.index, fill_value=False)
    return _apply_regime_to_execution(
        in_pos, sso_returns, SWITCH_COST_PCT, TAX_RATE,
    )


def _build_leg_donchian(
    signal_close: pd.Series, execution_returns: pd.Series,
    entry_lb: int, exit_lb: int,
) -> pd.Series:
    """Donchian leg: breakout on signal_close; execution via execution_returns."""
    signal = compute_donchian_signal(
        signal_close, signal_close, signal_close, entry_lb, exit_lb,
    )
    in_pos = (signal == "LONG").astype(bool).reindex(
        execution_returns.index, fill_value=False,
    )
    return _apply_regime_to_execution(
        in_pos, execution_returns, SWITCH_COST_PCT, TAX_RATE,
    )


def _metrics(equity: pd.Series, periods: int = 252) -> dict:
    e = equity.sort_index().astype(float)
    rets = e.pct_change().dropna()
    v0, vT = float(e.iloc[0]), float(e.iloc[-1])
    years = (e.index[-1] - e.index[0]).days / 365.25
    cagr = (vT / v0) ** (1.0 / years) - 1.0 if years > 0 and v0 > 0 else 0.0
    vol = float(rets.std()) * np.sqrt(periods) if len(rets) > 1 else 0.0
    sharpe = (float(rets.mean()) * periods) / vol if vol > 0 else 0.0
    peak = e.cummax()
    dd = (peak - e) / peak
    return {
        "start": e.index[0].strftime("%Y-%m-%d"),
        "end": e.index[-1].strftime("%Y-%m-%d"),
        "years": round(years, 2),
        "cagr_pct": round(cagr * 100.0, 2),
        "sharpe": round(sharpe, 3),
        "max_drawdown_pct": round(float(dd.max()) * 100.0, 2),
        "final_equity": round(vT, 2),
    }


def _plot(
    out_dir: Path,
    runs: list[tuple[str, pd.Series, dict, int]],
    spy_eq: pd.Series,
    spy_m: dict,
    threshold_pp: float,
) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(13, 6.5))
    for name, eq, m, n_rebal in runs:
        color = VARIANT_COLORS.get(name, "#333333")
        ax.plot(
            eq.index, eq.values,
            label=(f"{name} — CAGR {m['cagr_pct']:.2f}%  "
                   f"Sharpe {m['sharpe']:.2f}  "
                   f"MaxDD {m['max_drawdown_pct']:.2f}%  ({n_rebal} rebals)"),
            color=color, linewidth=1.25,
        )
    ax.plot(
        spy_eq.index, spy_eq.values,
        label=(f"SPYSIM buy&hold — CAGR {spy_m['cagr_pct']:.2f}%  "
               f"Sharpe {spy_m['sharpe']:.2f}  "
               f"MaxDD {spy_m['max_drawdown_pct']:.2f}%"),
        color="#8b949e", linewidth=1.0, linestyle="--",
    )
    for date_s, label in [
        ("1987-10-19", "Black Monday"),
        ("2000-03-24", "dot-com"),
        ("2008-09-15", "Lehman"),
        ("2020-02-19", "COVID"),
        ("2022-01-03", "2022"),
    ]:
        ts = pd.Timestamp(date_s)
        if spy_eq.index[0] <= ts <= spy_eq.index[-1]:
            ax.axvline(ts, color="#555", linewidth=0.5, linestyle=":",
                       alpha=0.5)
            ax.text(ts, ax.get_ylim()[1] * 0.97, label, rotation=90,
                    fontsize=7, alpha=0.6, verticalalignment="top")
    ax.set_yscale("log")
    ax.set_title(
        f"Plano B — V1/V2/V3/V4 (LETF execution on QQQ/GLD legs) vs SPYSIM B&H  "
        f"— threshold {threshold_pp:g}pp, {spy_m['start']} → {spy_m['end']} "
        f"({spy_m['years']}y, testfol.io ground truth)"
    )
    ax.set_xlabel("Date")
    ax.set_ylabel("Equity (USD, log scale)")
    ax.legend(loc="upper left", fontsize=8)
    ax.grid(True, which="both", alpha=0.25)
    fig.tight_layout()
    fig.savefig(out_dir / "equity_vs_spy.png", dpi=130)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(13, 4.8))
    for name, eq, m, _ in runs:
        color = VARIANT_COLORS.get(name, "#333333")
        peak = eq.cummax()
        dd_pct = (peak - eq) / peak * -100.0
        ax.plot(eq.index, dd_pct.values,
                color=color, linewidth=0.9,
                label=f"{name} (MaxDD {m['max_drawdown_pct']:.1f}%)")
    peak = spy_eq.cummax()
    spy_dd = (peak - spy_eq) / peak * -100.0
    ax.fill_between(spy_eq.index, spy_dd.values, 0.0,
                    alpha=0.2, color="#8b949e",
                    label=f"SPYSIM B&H (MaxDD {spy_m['max_drawdown_pct']:.1f}%)")
    ax.set_title("Drawdown underwater — V1/V2/V3/V4 (1986-2026)")
    ax.set_xlabel("Date")
    ax.set_ylabel("Drawdown (%)")
    ax.legend(loc="lower left", fontsize=8)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(out_dir / "drawdown_vs_spy.png", dpi=130)
    plt.close(fig)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    logging.basicConfig(
        level=args.log_level.upper(),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    args.output_dir.mkdir(parents=True, exist_ok=True)

    log.info("loading testfol.io ground-truth series …")
    spy = load_testfolio_series("SPYSIM")
    qqq = load_testfolio_series("QQQSIM")
    gld = load_testfolio_series("GLDSIM")
    sso = load_testfolio_series("SSOSIM")
    qld = load_testfolio_series("QLDSIM")
    ugl = load_testfolio_series("UGLSIM")
    log.info("all 6 series: %d bars  %s → %s",
             len(spy), spy.index[0].date(), spy.index[-1].date())

    # Pre-compute execution returns (ground-truth daily returns).
    sso_ret = sso.pct_change().fillna(0.0)
    qqq_ret = qqq.pct_change().fillna(0.0)
    qld_ret = qld.pct_change().fillna(0.0)
    gld_ret = gld.pct_change().fillna(0.0)
    ugl_ret = ugl.pct_change().fillna(0.0)

    # Sleeve 1 (SSO) shared across all 4 variants.
    log.info("building SSO leg (EMA100 on SPYSIM, execution = SSOSIM) …")
    sso_daily = _build_leg_sso(spy, sso_ret)

    # Sleeve 2 (QQQ or QLD) depending on variant — precompute both.
    log.info("building QQQ-leg 1× (signals on QQQSIM, execution = QQQSIM) …")
    qqq_leg = _build_leg_donchian(qqq, qqq_ret, QQQ_ENTRY, QQQ_EXIT)
    log.info("building QQQ-leg 2× (signals on QQQSIM, execution = QLDSIM) …")
    qld_leg = _build_leg_donchian(qqq, qld_ret, QQQ_ENTRY, QQQ_EXIT)

    # Sleeve 3 (GLD or UGL).
    log.info("building GLD-leg 1× (signals on GLDSIM, execution = GLDSIM) …")
    gld_leg = _build_leg_donchian(gld, gld_ret, GLD_ENTRY, GLD_EXIT)
    log.info("building GLD-leg 2× (signals on GLDSIM, execution = UGLSIM) …")
    ugl_leg = _build_leg_donchian(gld, ugl_ret, GLD_ENTRY, GLD_EXIT)

    leg_map = {
        "SSOSIM": sso_daily,
        "QQQSIM": qqq_leg, "QLDSIM": qld_leg,
        "GLDSIM": gld_leg, "UGLSIM": ugl_leg,
    }

    # SPYSIM B&H benchmark (aligned).
    spy_equity_full = args.initial_capital * spy / float(spy.iloc[0])

    runs: list[tuple[str, pd.Series, dict, int]] = []
    per_variant: list[dict] = []

    for name, cfg in VARIANTS.items():
        log.info("→ %s  legs=%s", name, cfg)
        rdf = pd.DataFrame({
            "leg1": leg_map[cfg["leg1"]],
            "leg2": leg_map[cfg["leg2"]],
            "leg3": leg_map[cfg["leg3"]],
        }).dropna()
        result = apply_threshold_rebalance(
            returns_df=rdf,
            target_weights={"leg1": 1 / 3, "leg2": 1 / 3, "leg3": 1 / 3},
            threshold_pp=args.threshold_pp,
            initial_capital=args.initial_capital,
            tax_rate=TAX_RATE,
        )
        m = _metrics(result.equity)
        runs.append((name, result.equity, m, result.n_taxable_events))
        per_variant.append({
            "variant": name,
            "legs": cfg,
            "metrics": m,
            "rebalance_events": result.n_taxable_events,
            "rebalance_tax_paid_usd": round(result.total_tax_paid, 2),
        })
        log.info("   CAGR %.2f%%  Sharpe %.3f  MaxDD %.2f%%  "
                 "rebals=%d  tax=$%.0f",
                 m["cagr_pct"], m["sharpe"], m["max_drawdown_pct"],
                 result.n_taxable_events, result.total_tax_paid)

    spy_window = spy_equity_full.loc[
        (spy_equity_full.index >= runs[0][1].index[0])
        & (spy_equity_full.index <= runs[0][1].index[-1])
    ]
    spy_m = _metrics(spy_window)
    log.info("SPYSIM B&H  CAGR %.2f%%  Sharpe %.3f  MaxDD %.2f%%",
             spy_m["cagr_pct"], spy_m["sharpe"], spy_m["max_drawdown_pct"])

    _plot(args.output_dir, runs, spy_window, spy_m, args.threshold_pp)

    summary = {
        "config": {
            "threshold_pp": args.threshold_pp,
            "tax_rate": TAX_RATE,
            "switch_cost_pct": SWITCH_COST_PCT,
            "initial_capital": args.initial_capital,
            "data_source": "testfol.io (SSOSIM/QLDSIM/UGLSIM ground truth)",
            "window": {
                "start": spy.index[0].strftime("%Y-%m-%d"),
                "end": spy.index[-1].strftime("%Y-%m-%d"),
                "bars": int(len(spy)),
            },
            "signals": {
                "SSO": f"EMA{LETF_LOOKBACK} band {LETF_BAND}",
                "QQQ/QLD": f"Donchian {QQQ_ENTRY}/{QQQ_EXIT}",
                "GLD/UGL": f"Donchian {GLD_ENTRY}/{GLD_EXIT}",
            },
        },
        "spy_buy_hold_SPYSIM": spy_m,
        "variants": per_variant,
        "caveats": [
            "Signals on 1× underlying (SPYSIM/QQQSIM/GLDSIM); execution "
            "via ground-truth leveraged series when in position.",
            "QLD/UGL availability on Inter Global NOT confirmed — V2/V3/V4 "
            "require broker catalog verification before real deploy.",
            "Close-only Donchian (testfol.io has no HLC).",
            "Pre-1999 QQQSIM and pre-2004 GLDSIM are testfol.io simulations "
            "from index returns + ETF drag (modelled, not measured).",
        ],
    }
    (args.output_dir / "summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    log.info("wrote artefacts → %s", args.output_dir)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())

"""Phase 4.0 T3 — Re-backtest V2-L2 winner with Index CFD price series.

Substitutes share-CFD inputs with index-equivalent series:

* ``SPY`` share CFD → SPX TR stitched series (Ken French pre-2001 +
  Tiingo SPY TR post-2001, via ``load_spx_tr_daily``). This is what
  a US500 CFD would track if Pepperstone's dividend-adjustment mechanism
  fully passes through dividends (optimistic scenario).
* ``QQQ`` share CFD → QQQ ``adj_close`` (which already includes
  dividend reinvestment). Substitutes for NDX TR / USTEC CFD.
* ``GLD`` share CFD → GLD ``adj_close`` (closest long-history proxy
  for XAUUSD CFD; XAUUSD parquet only has 2020+ data, insufficient
  for the V2 window). Caveat documented in output MD.

Cost model for Index CFD regime:

* ``commission_round_trip_bps = 0.0`` — assumes Razor Index tier is
  commission-free (pending T1 empirical validation in live account).
* ``spread_half_bps = 5.0`` — conservative vs 2.0 share CFD (Index
  CFD spreads are typically wider in bps because tight in points but
  underlying has higher absolute value).
* ``slippage_bps_round_trip = 3.0`` — same as share CFD.
* ``swap_daily_pct_long = -0.008`` — slightly worse than share CFD
  -0.005 (Index CFDs exposed to futures-basis drag vs spot share).

Sanity gates (from ``specs/phase_4_0_index_cfd_validation.md §3 T3``):

* OOS Sharpe ≥ 2.0 (tolerance −13% vs 2.285 share-CFD baseline)
* OOS CAGR ≥ 60% (tolerance −24% vs 79% baseline)
* OOS MaxDD ≤ −25% (no tolerance; mandate §5 cap)

Output:
  reports/phase4_0/index_cfd_validation/summary.json
  reports/phase4_0/index_cfd_validation/daily_returns.parquet
  reports/phase4_0/index_cfd_validation/standard_report.md

Citation:
  Phase 4.0 spec: specs/phase_4_0_index_cfd_validation.md
  V2-L2 winner baseline: reports/phase3_5a_v2/v2_l2_gayed_transported_cfd/AGGREGATE.md
  [leverage_for_the_long_run, p.11-14] (EMA-100 signal)
  [systematic_trading, p.185-188] (Index CFD cost regime)
"""

from __future__ import annotations

import json
import sys
from datetime import timezone, datetime
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from ai_trade.backtest.data.spx_tr_loader import load_spx_tr_daily  # noqa: E402
from ai_trade.backtest.strategies.plano_a_leveraged_rotation import (  # noqa: E402
    PlanoALeveragedRotationConfig,
    simulate_plano_a_rotation,
)

OUT_DIR = Path("reports/phase4_0/index_cfd_validation")
TIINGO_DAILY_DIR = Path("data/tiingo/daily/prices")

WINDOW_START = pd.Timestamp("2001-05-14")
WINDOW_END = pd.Timestamp("2026-04-14")
IS_RANGE = (pd.Timestamp("2001-05-14"), pd.Timestamp("2017-12-31"))
OOS_RANGE = (pd.Timestamp("2018-01-01"), pd.Timestamp("2023-12-31"))
FWD_RANGE = (pd.Timestamp("2024-01-01"), pd.Timestamp("2026-04-14"))


def _spx_tr_price_series() -> pd.DataFrame:
    """Build SPX TR price series via cumprod(1+r)*100 and return as close DF."""
    ret = load_spx_tr_daily(str(WINDOW_START.date()), str(WINDOW_END.date()))
    # ret is a Series of daily TR returns
    price = (1.0 + ret).cumprod() * 100.0
    price.name = "close"
    return pd.DataFrame({"close": price})


def _qqq_adj_close_series() -> pd.DataFrame:
    df = pd.read_parquet(TIINGO_DAILY_DIR / "QQQ.parquet")
    df.index = pd.DatetimeIndex(df.index)
    return pd.DataFrame({"close": df["adj_close"].astype(float)})


def _gold_adj_close_series() -> pd.DataFrame:
    """GLD adj_close as proxy for XAUUSD CFD (same caveat as V2-L2)."""
    df = pd.read_parquet(TIINGO_DAILY_DIR / "GLD.parquet")
    df.index = pd.DatetimeIndex(df.index)
    return pd.DataFrame({"close": df["adj_close"].astype(float)})


def _sharpe(ret: pd.Series) -> float:
    r = ret.dropna()
    if len(r) < 2 or r.std() == 0:
        return 0.0
    return float(r.mean() / r.std() * np.sqrt(252))


def _cagr(ret: pd.Series) -> float:
    r = ret.dropna()
    if len(r) < 2:
        return 0.0
    eq = (1.0 + r).cumprod()
    years = len(r) / 252.0
    return float(eq.iloc[-1] ** (1.0 / years) - 1.0)


def _max_dd(ret: pd.Series) -> float:
    r = ret.dropna()
    if r.empty:
        return 0.0
    eq = (1.0 + r).cumprod()
    return float((eq / eq.cummax() - 1.0).min())


def _slice_ret(ret: pd.Series, start: pd.Timestamp, end: pd.Timestamp) -> pd.Series:
    return ret.loc[(ret.index >= start) & (ret.index <= end)]


def _walk_forward(ret: pd.Series, n_windows: int = 8) -> tuple[float, float, bool]:
    r = ret.dropna()
    r = r.loc[r != 0.0]
    if len(r) < n_windows * 20:
        return 0.0, float("inf"), False
    size = len(r) // n_windows
    profitable = 0
    max_dd = 0.0
    for i in range(n_windows):
        window = r.iloc[i * size:(i + 1) * size]
        if window.empty:
            continue
        eq = (1.0 + window).cumprod()
        wdd = float((eq / eq.cummax() - 1.0).min())
        if eq.iloc[-1] > 1.0:
            profitable += 1
        if abs(wdd) > abs(max_dd):
            max_dd = wdd
    ratio = profitable / n_windows
    return ratio, abs(max_dd), (ratio >= 6 / 8 and abs(max_dd) <= 0.25)


def main() -> None:
    print("=" * 72)
    print("Phase 4.0 T3 — Index CFD substitution re-backtest")
    print("=" * 72)

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    print("\n[1/4] Loading substituted price panels...")
    spx_panel = _spx_tr_price_series()
    qqq_panel = _qqq_adj_close_series()
    gld_panel = _gold_adj_close_series()
    print(f"  SPX TR: {len(spx_panel)} bars "
          f"({spx_panel.index[0].date()} → {spx_panel.index[-1].date()})")
    print(f"  QQQ adj_close: {len(qqq_panel)} bars "
          f"({qqq_panel.index[0].date()} → {qqq_panel.index[-1].date()})")
    print(f"  GLD adj_close: {len(gld_panel)} bars "
          f"({gld_panel.index[0].date()} → {gld_panel.index[-1].date()})")

    # Build config with Index CFD cost model
    config = PlanoALeveragedRotationConfig(
        regime_signal="ema100",
        leverage=2.0,
        off_regime_asset="gld",
        risk_on_tickers=("SPY", "QQQ"),  # labels; data is SPX TR + QQQ adj_close
        spread_half_bps=5.0,
        commission_round_trip_bps=0.0,
        slippage_bps_round_trip=3.0,
        swap_daily_pct_long=-0.008,
    )
    print(f"\n[2/4] Config built — signal=ema100, L={config.leverage}, "
          f"off={config.off_regime_asset}, commission={config.commission_round_trip_bps}bps")

    # Label-based panel (strategy uses the names as keys, data is substituted)
    risk_on_panel = {"SPY": spx_panel, "QQQ": qqq_panel}
    off_panel = {"gld": gld_panel}

    print("\n[3/4] Running simulate_plano_a_rotation...")
    result = simulate_plano_a_rotation(
        risk_on_panel, config, off_regime_panel=off_panel
    )
    print(f"  bars: {len(result.daily_returns)}")
    print(f"  n_switches_total: {result.n_switches_total} "
          f"(vs V2-L2 share-CFD baseline: 616)")
    print(f"  switches_by_ticker: {result.switches_by_ticker.to_dict()}")
    print(f"  median_hold_days: {result.median_hold_days:.2f} "
          f"(vs V2-L2 baseline: 6.0)")
    print(f"  cum_cost_pct: {result.cum_cost_pct * 100:.2f}% "
          f"(vs V2-L2 baseline: 125.8%)")
    print(f"  cum_swap_pct: {result.cum_swap_pct * 100:.2f}% "
          f"(vs V2-L2 baseline: -44.93%)")

    ret = result.daily_returns

    is_ret = _slice_ret(ret, *IS_RANGE)
    oos_ret = _slice_ret(ret, *OOS_RANGE)
    fwd_ret = _slice_ret(ret, *FWD_RANGE)

    is_m = {"sharpe": _sharpe(is_ret), "cagr": _cagr(is_ret), "mdd": _max_dd(is_ret), "n": len(is_ret)}
    oos_m = {"sharpe": _sharpe(oos_ret), "cagr": _cagr(oos_ret), "mdd": _max_dd(oos_ret), "n": len(oos_ret)}
    fwd_m = {"sharpe": _sharpe(fwd_ret), "cagr": _cagr(fwd_ret), "mdd": _max_dd(fwd_ret), "n": len(fwd_ret)}

    wf_ratio, wf_max_dd, wf_pass = _walk_forward(ret, n_windows=8)

    print("\n[4/4] Metrics comparison vs V2-L2 share-CFD baseline:")
    print(f"                  IS               OOS               FWD")
    print(f"                  this  baseline   this   baseline   this   baseline")
    print(f"  Sharpe     {is_m['sharpe']:6.3f}  1.856   "
          f"{oos_m['sharpe']:6.3f}  2.285    {fwd_m['sharpe']:6.3f}  1.821")
    print(f"  CAGR       {is_m['cagr']:6.1%}  53.4%   "
          f"{oos_m['cagr']:6.1%}  79.1%    {fwd_m['cagr']:6.1%}  59.3%")
    print(f"  MDD        {is_m['mdd']:6.1%} -22.7%   "
          f"{oos_m['mdd']:6.1%} -21.0%    {fwd_m['mdd']:6.1%} -17.4%")

    # T3 sanity gates
    gate_sharpe = oos_m["sharpe"] >= 2.0
    gate_cagr = oos_m["cagr"] >= 0.60
    gate_mdd = oos_m["mdd"] >= -0.25
    t3_pass = gate_sharpe and gate_cagr and gate_mdd

    print("\n=== T3 Sanity Gates ===")
    print(f"  OOS Sharpe ≥ 2.0:   {oos_m['sharpe']:.3f}  {'✅' if gate_sharpe else '❌'}")
    print(f"  OOS CAGR ≥ 60%:     {oos_m['cagr']:.1%}  {'✅' if gate_cagr else '❌'}")
    print(f"  OOS MDD ≤ -25%:     {oos_m['mdd']:.1%}  {'✅' if gate_mdd else '❌'}")
    print(f"  Walk-fwd profitable ≥ 6/8: {wf_ratio:.3f} (max_dd {wf_max_dd:.1%})  "
          f"{'✅' if wf_pass else '❌'}")
    print(f"\n  VERDICT T3: {'✅ PASS' if t3_pass else '❌ FAIL — Caminho 3 inviável'}")

    # Save artefatos
    ret.to_frame(name="ret").to_parquet(OUT_DIR / "daily_returns.parquet")

    summary = {
        "phase": "4.0 T3 — Index CFD substitution",
        "config": {
            "regime_signal": config.regime_signal,
            "leverage": config.leverage,
            "off_regime_asset": config.off_regime_asset,
            "risk_on_labels": list(config.risk_on_tickers),
            "spread_half_bps": config.spread_half_bps,
            "commission_round_trip_bps": config.commission_round_trip_bps,
            "slippage_bps_round_trip": config.slippage_bps_round_trip,
            "swap_daily_pct_long": config.swap_daily_pct_long,
        },
        "substitution_map": {
            "SPY": "SPX TR stitched (KF pre-2001 + Tiingo SPY TR post-2001)",
            "QQQ": "QQQ adj_close (Tiingo; proxy for NDX TR / USTEC CFD)",
            "gld": "GLD adj_close (Tiingo; proxy for XAUUSD CFD — XAUUSD parquet insufficient history)",
        },
        "window": {
            "start": str(result.daily_returns.index[0].date()),
            "end": str(result.daily_returns.index[-1].date()),
            "n_bars": int(len(result.daily_returns)),
            "n_switches_total": int(result.n_switches_total),
            "median_hold_days": float(result.median_hold_days),
            "cum_cost_pct": float(result.cum_cost_pct),
            "cum_swap_pct": float(result.cum_swap_pct),
        },
        "splits": {"IS": is_m, "OOS": oos_m, "FWD": fwd_m},
        "walk_forward": {
            "n_windows": 8,
            "profitable_ratio": float(wf_ratio),
            "max_window_drawdown": float(wf_max_dd),
            "pass": bool(wf_pass),
        },
        "t3_gates": {
            "oos_sharpe_ge_2": {"value": oos_m["sharpe"], "pass": bool(gate_sharpe)},
            "oos_cagr_ge_60pct": {"value": oos_m["cagr"], "pass": bool(gate_cagr)},
            "oos_mdd_le_25pct": {"value": oos_m["mdd"], "pass": bool(gate_mdd)},
            "all_pass": bool(t3_pass),
        },
        "baseline_v2_l2": {
            "OOS_sharpe": 2.285,
            "OOS_cagr": 0.7914,
            "OOS_mdd": -0.2102,
            "n_switches_total": 616,
            "cum_cost_pct": 1.258,
            "cum_swap_pct": -0.4493,
        },
        "produced_at": datetime.now(timezone.utc).isoformat(),
    }
    (OUT_DIR / "summary.json").write_text(
        json.dumps(summary, indent=2, default=float), encoding="utf-8"
    )
    print(f"\nwrote {OUT_DIR / 'summary.json'}")
    print(f"wrote {OUT_DIR / 'daily_returns.parquet'}")

    # MD report
    md: list[str] = []
    md.append("# Phase 4.0 T3 — Index CFD substitution backtest")
    md.append("")
    md.append(f"**Status:** {'✅ PASS T3 sanity gates' if t3_pass else '❌ FAIL T3 sanity gates — Caminho 3 inviável'}")
    md.append(f"**Date:** {datetime.now(timezone.utc).date()}")
    md.append(f"**Window:** {result.daily_returns.index[0].date()} → {result.daily_returns.index[-1].date()} ({len(result.daily_returns)} bars)")
    md.append("")
    md.append("## Substitution map")
    md.append("")
    md.append("| Backtest label | V2-L2 share CFD data | Phase 4.0 Index CFD substitute |")
    md.append("|---|---|---|")
    md.append("| SPY | SPY `close` Tiingo parquet | SPX TR stitched (KF + SPY TR) |")
    md.append("| QQQ | QQQ `close` Tiingo parquet | QQQ `adj_close` Tiingo (≈ NDX TR) |")
    md.append("| gld | GLD `close` Tiingo parquet | GLD `adj_close` Tiingo (proxy for XAUUSD; XAUUSD data insufficient pre-2020) |")
    md.append("")
    md.append("## Cost model comparison")
    md.append("")
    md.append("| Parameter | V2-L2 (share CFD) | Phase 4.0 (Index CFD) | Rationale |")
    md.append("|---|---:|---:|---|")
    md.append(f"| spread_half_bps | 2.0 | {config.spread_half_bps:.1f} | Index CFD spread wider in bps |")
    md.append(f"| commission_round_trip_bps | 6.6 | {config.commission_round_trip_bps:.1f} | Razor Index typically commission-free (pending T1) |")
    md.append(f"| slippage_bps_round_trip | 3.0 | {config.slippage_bps_round_trip:.1f} | Same |")
    md.append(f"| swap_daily_pct_long | -0.005 | {config.swap_daily_pct_long:.3f} | Slightly worse (futures-basis drag) |")
    md.append("")
    md.append("## Split metrics")
    md.append("")
    md.append("| Split | Sharpe (this) | Sharpe (V2-L2) | CAGR (this) | CAGR (V2-L2) | MDD (this) | MDD (V2-L2) |")
    md.append("|---|---:|---:|---:|---:|---:|---:|")
    md.append(f"| IS | {is_m['sharpe']:.3f} | 1.856 | {is_m['cagr']:.2%} | 53.42% | {is_m['mdd']:.2%} | -22.67% |")
    md.append(f"| OOS | **{oos_m['sharpe']:.3f}** | 2.285 | **{oos_m['cagr']:.2%}** | 79.14% | **{oos_m['mdd']:.2%}** | -21.02% |")
    md.append(f"| FWD | {fwd_m['sharpe']:.3f} | 1.821 | {fwd_m['cagr']:.2%} | 59.28% | {fwd_m['mdd']:.2%} | -17.35% |")
    md.append("")
    md.append("## T3 sanity gates")
    md.append("")
    md.append("| Gate | Threshold | Observed | Pass |")
    md.append("|---|---:|---:|:--:|")
    md.append(f"| OOS Sharpe | ≥ 2.0 | {oos_m['sharpe']:.3f} | {'✅' if gate_sharpe else '❌'} |")
    md.append(f"| OOS CAGR | ≥ 60% | {oos_m['cagr']:.2%} | {'✅' if gate_cagr else '❌'} |")
    md.append(f"| OOS MDD | ≤ -25% | {oos_m['mdd']:.2%} | {'✅' if gate_mdd else '❌'} |")
    md.append(f"| WF 8-window profitable + max-DD | ≥ 6/8 + ≤ 25% | {wf_ratio:.3f}, {wf_max_dd:.2%} | {'✅' if wf_pass else '❌'} |")
    md.append("")
    if t3_pass:
        md.append("**Overall T3 verdict: ✅ PASS.** Proceed to T4 (full gates battery).")
    else:
        md.append("**Overall T3 verdict: ❌ FAIL.** Caminho 3 mathematically unviable. Do not proceed to T4.")
    md.append("")
    md.append("## Switch behaviour comparison")
    md.append("")
    md.append(f"- Total switches: **{result.n_switches_total}** (V2-L2 baseline: 616)")
    md.append(f"- By ticker: {result.switches_by_ticker.to_dict()}")
    md.append(f"- Median hold days: **{result.median_hold_days:.2f}** (V2-L2 baseline: 6.0)")
    md.append(f"- Cum. transaction cost: **{result.cum_cost_pct * 100:.2f}%** (V2-L2: 125.8%)")
    md.append(f"- Cum. overnight swap: **{result.cum_swap_pct * 100:.2f}%** (V2-L2: -44.93%)")
    md.append("")
    md.append("## Known caveats")
    md.append("")
    md.append("1. **GLD used as proxy for XAUUSD.** XAUUSD parquet starts 2020-01-02 (insufficient for V2 window). GLD inherits the silent-cash pre-2004 caveat from V2-L2 (14% of bars treated as 0% return when GLD data unavailable). Post-2004 behavior is authentic.")
    md.append("2. **Cost model assumes Razor Index commission-free.** Pending T1 empirical validation in live Pepperstone demo account. If T1 reveals commission > 0, T3 must be re-run.")
    md.append("3. **Dividend adjustment assumed perfect.** SPX TR and QQQ adj_close both include dividend reinvestment. If Pepperstone's Index CFD dividend-adjustment haircut is material (< 95%), actual live CAGR will be lower than this backtest.")
    md.append("4. **No PBO/DSR cross-config test here.** T3 is single-config; T4 runs bootstrap 99.9% CI + walk-forward as primary robustness gates (PBO/DSR trivialize at n_trials=1).")
    md.append("")

    (OUT_DIR / "standard_report.md").write_text("\n".join(md), encoding="utf-8")
    print(f"wrote {OUT_DIR / 'standard_report.md'}")
    print("=" * 72)


if __name__ == "__main__":
    main()

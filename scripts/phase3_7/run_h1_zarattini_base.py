"""Phase 3.7 H1.a — Zarattini-Aziz-Barbon 2024 base replication runner.

Loads SPY (primary) and QQQ (secondary) 1-min bars from Tiingo parquets,
runs the single-asset Zarattini noise-boundary intraday-momentum strategy
under the F2-patched ``prev_weight × ret`` convention, and emits a full
13-gate ``AGGREGATE.{md,json}`` per the Phase 3.7-3 hunt prompt.

Execution shape
---------------
1. Load SPY 1-min, QQQ 1-min (data/phase3_7/intraday/<TICKER>_1min.parquet).
2. Winner config simulation (both tickers).
3. IS / OOS / FWD split metrics + full-period.
4. Bootstrap 99.9% CI (stationary block, block_mean=5, n=2000).
5. Walk-forward 8-window verdict.
6. IR vs SPY buy-hold on OOS.
7. Cost×2 sensitivity.
8. 5-config sensitivity grid for PBO/DSR.
9. Vectorbt cross-lib concordance (SPY OOS).
10. Write AGGREGATE.{json,md} + per-split parquets + grid CSV.

Citations
---------
* Zarattini-Aziz-Barbon 2024 SSRN 4824172 — signal + windows.
* [advances_fin_ml, p.31-34] — prev_weight × ret lookahead convention.
* [advances_fin_ml, p.196-202] — stationary bootstrap.
* [advances_fin_ml, p.208-211, p.275] — CSCV PBO + DSR.
* docs/investment-mandate.md §2.4 — 13 gates.
* Pepperstone Razor CFD rate card — cost model.
"""

from __future__ import annotations

import json
import sys
import time
import warnings
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path("/var/www/pessoal/ai-trade")
sys.path.insert(0, str(ROOT / "src"))

from ai_trade.backtest.grid.letf_rotation_b1c import (  # noqa: E402
    TRADING_DAYS,
    bootstrap_sharpe_ci,
    compute_split_metrics,
    walk_forward_verdict_from_returns,
)
from ai_trade.backtest.strategies.phase3_7_h1_zarattini_base import (  # noqa: E402
    H1ZarattiniBaseConfig,
    simulate_h1_zarattini_base,
)
from ai_trade.backtest.validation.dsr import dsr as dsr_metric  # noqa: E402
from ai_trade.backtest.validation.pbo import pbo as cscv_pbo  # noqa: E402

OUT_DIR = ROOT / "reports/phase_3_7/h1_zarattini_base"
OUT_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR = ROOT / "data/phase3_7/intraday"

IS_RANGE = ("2017-06-01", "2021-12-31")
OOS_RANGE = ("2022-01-01", "2024-12-31")
FWD_RANGE = ("2025-01-01", "2026-04-14")

# Paper-literal baseline: ma=14d, ATR(20) daily-scaled, k=2.
WINNER_CFG = H1ZarattiniBaseConfig(
    ma_days=14,
    atr_period=20,
    atr_multiplier=2.0,
    atr_scale="daily",
)

# Sensitivity grid for CSCV/PBO (5 configs; brief §5).
GRID_CFGS: list[tuple[str, H1ZarattiniBaseConfig]] = [
    ("ma14_atr20_k2_daily", H1ZarattiniBaseConfig(ma_days=14, atr_period=20, atr_multiplier=2.0, atr_scale="daily")),
    ("ma10_atr20_k2_daily", H1ZarattiniBaseConfig(ma_days=10, atr_period=20, atr_multiplier=2.0, atr_scale="daily")),
    ("ma20_atr20_k2_daily", H1ZarattiniBaseConfig(ma_days=20, atr_period=20, atr_multiplier=2.0, atr_scale="daily")),
    ("ma14_atr20_k3_daily", H1ZarattiniBaseConfig(ma_days=14, atr_period=20, atr_multiplier=3.0, atr_scale="daily")),
    ("ma14_atr14_k2_daily", H1ZarattiniBaseConfig(ma_days=14, atr_period=14, atr_multiplier=2.0, atr_scale="daily")),
]


def _load_1min(ticker: str) -> pd.DataFrame:
    fp = DATA_DIR / f"{ticker}_1min.parquet"
    if not fp.exists():
        raise FileNotFoundError(fp)
    df = pd.read_parquet(fp)
    return df


def _naive_index(s: pd.Series) -> pd.Series:
    """Drop tz info for side-by-side comparison with SPY adj_close daily."""
    if isinstance(s.index, pd.DatetimeIndex) and s.index.tz is not None:
        s = s.copy()
        s.index = s.index.tz_localize(None)
    return s


def _slice_daily(s: pd.Series, start: str, end: str) -> pd.Series:
    a, b = pd.Timestamp(start), pd.Timestamp(end)
    return s.loc[(s.index >= a) & (s.index <= b)]


def _mdict(name: str, s: pd.Series) -> dict:
    m = compute_split_metrics(name, s)
    return {
        "name": m.name,
        "n_bars": m.n_bars,
        "sharpe": m.sharpe,
        "cagr": m.cagr,
        "max_drawdown": m.max_drawdown,
        "final_equity_from_unit": m.final_equity_from_unit,
    }


def _cagr_tier_rotaA(cagr: float) -> str:
    """Mandate §2.2 rota A tiers (Pepperstone, no DARF)."""
    if cagr < 0.13:
        return "Folclore"
    if cagr < 0.25:
        return "Marginal"
    if cagr < 0.50:
        return "Válido"
    if cagr < 1.00:
        return "Forte"
    return "Extraordinário (suspect)"


def _mdd_tier_rotaA(mdd_mag: float) -> str:
    """Mandate §2.3 rota A tiers (MDD magnitude)."""
    if mdd_mag <= 0.25:
        return "Excelente"
    if mdd_mag <= 0.40:
        return "Válido"
    if mdd_mag <= 0.75:
        return "Warning"
    return "Reject"


def _ir_vs_spy(port_oos: pd.Series, spy_oos: pd.Series) -> float:
    common = port_oos.index.intersection(spy_oos.index)
    if len(common) < 20:
        return float("nan")
    excess = port_oos.loc[common] - spy_oos.loc[common]
    mu, sd = float(excess.mean()), float(excess.std(ddof=1))
    if sd <= 0:
        return 0.0
    return mu / sd * np.sqrt(TRADING_DAYS)


def _vectorbt_cross_check(
    bars: pd.DataFrame,
    cfg: H1ZarattiniBaseConfig,
    ref_oos_daily: pd.Series,
) -> dict:
    """Vectorbt cross-lib concordance check on OOS window.

    We feed vectorbt the same signal/exit logic by turning our
    ``weights`` series into long/short signals, then letting vbt
    Portfolio.from_signals price execution at bar close with our spread.
    Cross-lib delta is measured in OOS CAGR pp.
    """
    try:
        import vectorbt as vbt  # noqa: F401
    except Exception as e:
        return {
            "status": "skipped",
            "reason": f"vectorbt unavailable: {e}",
            "delta_cagr_pp": None,
        }

    # Reference: run our pandas simulator, get bar-level weights + returns.
    res = simulate_h1_zarattini_base(bars, cfg)
    weights = res.weights  # ∈ {-1, 0, 1}
    close = bars["close"].astype(float)

    # Convert weights into entries/exits for vbt.Portfolio.from_signals.
    # vbt wants boolean arrays: entries, exits, short_entries, short_exits.
    prev_w = weights.shift(1).fillna(0.0)
    long_entries = (prev_w <= 0) & (weights > 0)
    long_exits = (prev_w > 0) & (weights <= 0)
    short_entries = (prev_w >= 0) & (weights < 0)
    short_exits = (prev_w < 0) & (weights >= 0)

    try:
        import vectorbt as vbt

        pf = vbt.Portfolio.from_signals(
            close=close,
            entries=long_entries,
            exits=long_exits,
            short_entries=short_entries,
            short_exits=short_exits,
            fees=cfg.spread_one_way,  # per side
            freq="1min",
            init_cash=1.0,
            size=1.0,
            size_type="value",  # 1 notional per position
        )
        vbt_minute_ret = pf.returns()
    except Exception as e:
        return {
            "status": "failed",
            "reason": f"vbt.Portfolio.from_signals raised: {e}",
            "delta_cagr_pp": None,
        }

    # Aggregate to daily + slice OOS.
    vbt_minute_ret = vbt_minute_ret.replace([np.inf, -np.inf], np.nan).fillna(0.0)
    vbt_daily = (1.0 + vbt_minute_ret).groupby(
        vbt_minute_ret.index.normalize()
    ).prod() - 1.0
    vbt_daily.index = pd.DatetimeIndex(vbt_daily.index).tz_localize(None)
    vbt_oos = _slice_daily(vbt_daily, *OOS_RANGE)
    if len(vbt_oos) < 20 or len(ref_oos_daily) < 20:
        return {
            "status": "insufficient_overlap",
            "reason": f"vbt_oos={len(vbt_oos)}, ref_oos={len(ref_oos_daily)}",
            "delta_cagr_pp": None,
        }
    # Align on intersection of dates.
    common = ref_oos_daily.index.intersection(vbt_oos.index)
    if len(common) < 20:
        return {
            "status": "insufficient_overlap_after_align",
            "reason": f"common={len(common)}",
            "delta_cagr_pp": None,
        }
    ref = ref_oos_daily.loc[common]
    vbt_r = vbt_oos.loc[common]

    def _cagr(r: pd.Series) -> float:
        if len(r) < 2:
            return 0.0
        eq = float((1.0 + r).prod())
        if eq <= 0:
            return -1.0
        y = len(r) / TRADING_DAYS
        return eq ** (1.0 / y) - 1.0 if y > 0 else 0.0

    ref_cagr = _cagr(ref)
    vbt_cagr = _cagr(vbt_r)
    delta_pp = abs(vbt_cagr - ref_cagr) * 100.0
    return {
        "status": "ok",
        "ref_cagr_oos": ref_cagr,
        "vbt_cagr_oos": vbt_cagr,
        "delta_cagr_pp": delta_pp,
        "n_common_days": int(len(common)),
    }


def _spy_daily_benchmark() -> pd.Series:
    """SPY daily buy-hold return series from 1-min data (last close per day)."""
    df = _load_1min("SPY")
    close = df["close"].astype(float)
    daily_close = close.groupby(close.index.normalize()).last()
    daily_close.index = daily_close.index.tz_localize(None)
    return daily_close.pct_change().dropna()


def main() -> None:
    t0 = time.time()
    print("=" * 80)
    print("Phase 3.7 H1.a — Zarattini-Aziz-Barbon 2024 base replication")
    print("=" * 80)

    # -- Step 1: load data
    print(f"\n[data] loading SPY, QQQ 1-min bars from {DATA_DIR}")
    spy = _load_1min("SPY")
    qqq = _load_1min("QQQ")
    print(f"[data] SPY {spy.shape} {spy.index[0]} -> {spy.index[-1]}")
    print(f"[data] QQQ {qqq.shape} {qqq.index[0]} -> {qqq.index[-1]}")

    # -- Step 2: winner run SPY + QQQ
    print(f"\n[winner] config = {WINNER_CFG}")
    ts = time.time()
    spy_res = simulate_h1_zarattini_base(spy, WINNER_CFG, ticker="SPY")
    print(f"[winner] SPY done in {time.time()-ts:.1f}s n_trades={spy_res.n_trades}")
    ts = time.time()
    qqq_res = simulate_h1_zarattini_base(qqq, WINNER_CFG, ticker="QQQ")
    print(f"[winner] QQQ done in {time.time()-ts:.1f}s n_trades={qqq_res.n_trades}")

    # -- Step 3: aggregate to daily + split SPY (primary)
    spy_daily = _naive_index(spy_res.daily_returns())
    qqq_daily = _naive_index(qqq_res.daily_returns())
    print(f"[winner] SPY daily ret: n={len(spy_daily)} mean={spy_daily.mean()*10000:.2f}bp")
    print(f"[winner] QQQ daily ret: n={len(qqq_daily)} mean={qqq_daily.mean()*10000:.2f}bp")

    is_ret = _slice_daily(spy_daily, *IS_RANGE)
    oos_ret = _slice_daily(spy_daily, *OOS_RANGE)
    fwd_ret = _slice_daily(spy_daily, *FWD_RANGE)
    full_ret = spy_daily

    is_m = _mdict("IS", is_ret)
    oos_m = _mdict("OOS", oos_ret)
    fwd_m = _mdict("FWD", fwd_ret)
    full_m = _mdict("FULL", full_ret)

    # QQQ splits for cross-asset confirmation (reported, not gate-binding).
    qqq_oos_m = _mdict("OOS_QQQ", _slice_daily(qqq_daily, *OOS_RANGE))

    print(f"[SPY IS]  S={is_m['sharpe']:.3f}  CAGR={is_m['cagr']*100:.2f}%  MDD={is_m['max_drawdown']*100:.2f}%  n={is_m['n_bars']}")
    print(f"[SPY OOS] S={oos_m['sharpe']:.3f}  CAGR={oos_m['cagr']*100:.2f}%  MDD={oos_m['max_drawdown']*100:.2f}%  n={oos_m['n_bars']}")
    print(f"[SPY FWD] S={fwd_m['sharpe']:.3f}  CAGR={fwd_m['cagr']*100:.2f}%  MDD={fwd_m['max_drawdown']*100:.2f}%  n={fwd_m['n_bars']}")
    print(f"[QQQ OOS] S={qqq_oos_m['sharpe']:.3f} CAGR={qqq_oos_m['cagr']*100:.2f}% MDD={qqq_oos_m['max_drawdown']*100:.2f}%")

    # -- Step 4: Bootstrap 99.9% CIs (stationary block, Politis-Romano 1994)
    if len(oos_ret) >= 20:
        oos_lo, oos_hi = bootstrap_sharpe_ci(
            oos_ret, alpha=0.001, n_resamples=2000, block_mean=5, seed=42
        )
    else:
        oos_lo, oos_hi = float("nan"), float("nan")
    if len(full_ret) >= 20:
        full_lo, full_hi = bootstrap_sharpe_ci(
            full_ret, alpha=0.001, n_resamples=2000, block_mean=5, seed=42
        )
    else:
        full_lo, full_hi = float("nan"), float("nan")
    print(f"[BOOT] SPY OOS 99.9% CI [{oos_lo:.4f}, {oos_hi:.4f}]")
    print(f"[BOOT] SPY FULL 99.9% CI [{full_lo:.4f}, {full_hi:.4f}]")

    # -- Step 5: Walk-forward 8 windows on FULL daily
    if len(full_ret) >= 8:
        wf_ratio, wf_mdd, _wf_pass = walk_forward_verdict_from_returns(
            full_ret, n_windows=8, max_drawdown_cap=0.50
        )
    else:
        wf_ratio, wf_mdd = 0.0, 0.0
    wf_profitable = int(round(wf_ratio * 8))
    wf_pass_ratio = wf_profitable >= 6
    print(f"[WF]  {wf_profitable}/8 profitable  max_window_mdd={wf_mdd*100:.2f}%")

    # -- Step 6: IR vs SPY buy-hold on OOS
    spy_bh = _spy_daily_benchmark()
    spy_oos_bh = _slice_daily(spy_bh, *OOS_RANGE)
    spy_oos_bh_m = _mdict("SPY_OOS_BH", spy_oos_bh)
    ir = _ir_vs_spy(oos_ret, spy_oos_bh)
    print(f"[IR]  vs SPY buy-hold OOS = {ir:.4f}  (SPY OOS BH S={spy_oos_bh_m['sharpe']:.3f})")

    # -- Step 7: Median hold (in minutes → hours)
    median_hold_bars = (
        float(np.median(spy_res.hold_bars)) if spy_res.hold_bars else float("nan")
    )
    median_hold_h = median_hold_bars / 60.0 if np.isfinite(median_hold_bars) else float("nan")
    print(f"[HOLD] median hold bars={median_hold_bars:.0f} (~{median_hold_h:.1f}h)  n_entries={len(spy_res.hold_bars)}")

    # -- Step 8: cost×2 sensitivity
    cost2x_cfg = H1ZarattiniBaseConfig(
        ma_days=WINNER_CFG.ma_days,
        atr_period=WINNER_CFG.atr_period,
        atr_multiplier=WINNER_CFG.atr_multiplier,
        atr_scale=WINNER_CFG.atr_scale,
        signal_start_bar=WINNER_CFG.signal_start_bar,
        flat_at_close=WINNER_CFG.flat_at_close,
        spread_one_way=WINNER_CFG.spread_one_way * 2.0,
        commission_round_trip=WINNER_CFG.commission_round_trip,
        swap_daily=WINNER_CFG.swap_daily,
        tax_rate=WINNER_CFG.tax_rate,
        no_reentry_after_stop_same_day=WINNER_CFG.no_reentry_after_stop_same_day,
    )
    print(f"\n[cost2x] running cost×2 (spread {cost2x_cfg.spread_one_way:.6f}, ≈{cost2x_cfg.spread_one_way*1e4:.2f} bps one-way)")
    ts = time.time()
    cost2x_res = simulate_h1_zarattini_base(spy, cost2x_cfg, ticker="SPY")
    print(f"[cost2x] done in {time.time()-ts:.1f}s")
    cost2x_oos_daily = _slice_daily(_naive_index(cost2x_res.daily_returns()), *OOS_RANGE)
    cost2x_m = _mdict("OOS_cost2x", cost2x_oos_daily)
    print(f"[cost2x] OOS Sharpe={cost2x_m['sharpe']:.3f}  CAGR={cost2x_m['cagr']*100:.2f}%")

    # -- Step 9: Grid run for PBO + DSR
    print(f"\n[grid] running {len(GRID_CFGS)} sibling configs for PBO/DSR...")
    grid_rets: dict[str, pd.Series] = {}
    for tag, cfg in GRID_CFGS:
        if cfg == WINNER_CFG:
            grid_rets[tag] = spy_daily
            print(f"  [grid] {tag} (reuse winner)")
            continue
        ts = time.time()
        r = simulate_h1_zarattini_base(spy, cfg, ticker="SPY")
        r_daily = _naive_index(r.daily_returns())
        grid_rets[tag] = r_daily
        sh = compute_split_metrics(tag, r_daily).sharpe
        print(f"  [grid] {tag} done in {time.time()-ts:.1f}s Sharpe_full={sh:.3f}")

    grid_df = pd.concat(grid_rets, axis=1).dropna(how="any")
    print(f"[grid] aligned matrix shape: {grid_df.shape}")

    pbo_result = None
    if grid_df.shape[0] >= 100 and grid_df.shape[1] >= 2:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")  # suppress small-N warning
            pbo_result = cscv_pbo(grid_df.to_numpy(), n_blocks=10)
        print(f"[PBO] value={pbo_result.pbo:.4f} n_combos={pbo_result.n_combinations}")
    else:
        print("[PBO] skipped — insufficient grid")

    dsr_res = dsr_metric(oos_ret.to_numpy(dtype=float), n_trials=len(GRID_CFGS))
    print(f"[DSR] p_value={dsr_res.p_value:.6f}  obs_SR={dsr_res.observed_sharpe:.4f}")

    # -- Step 10: cross-lib check (vectorbt)
    print("\n[cross-lib] running vectorbt concordance on SPY OOS...")
    ts = time.time()
    try:
        cross = _vectorbt_cross_check(spy, WINNER_CFG, oos_ret)
    except Exception as e:
        cross = {"status": "error", "reason": str(e), "delta_cagr_pp": None}
    print(f"[cross-lib] done in {time.time()-ts:.1f}s  status={cross.get('status')}  delta_cagr_pp={cross.get('delta_cagr_pp')}")

    # -- Step 11: 13 gates
    cagr_tier_oos = _cagr_tier_rotaA(oos_m["cagr"])
    mdd_tier_oos = _mdd_tier_rotaA(abs(oos_m["max_drawdown"]))
    leveraged = False  # base replication is unleveraged; cost×2 Sharpe gate > 1.0.

    # cross-lib: pass iff delta_pp <= 3 and status == "ok".
    cross_ok = (
        cross.get("status") == "ok"
        and cross.get("delta_cagr_pp") is not None
        and cross["delta_cagr_pp"] <= 3.0
    )

    def _b(x) -> bool | None:
        """Coerce numpy bool / any truthy value to plain Python bool;
        preserve None."""
        if x is None:
            return None
        return bool(x)

    gates = [
        (
            "gate_01_is_sharpe_gt_0_5",
            _b(is_m["sharpe"] > 0.5),
            f"{is_m['sharpe']:.3f}",
            "soft",
        ),
        (
            "gate_02_oos_sharpe_ge_1_3",
            _b(oos_m["sharpe"] >= 1.3),
            f"{oos_m['sharpe']:.3f}",
            "soft",
        ),
        (
            "gate_03_oos_cagr_tier",
            None,
            f"{oos_m['cagr']*100:.2f}% → {cagr_tier_oos}",
            "warning",
        ),
        (
            "gate_04_oos_mdd_tier",
            None,
            f"{oos_m['max_drawdown']*100:.2f}% → {mdd_tier_oos}",
            "warning",
        ),
        (
            "gate_05_fwd_sharpe_gt_0",
            _b(fwd_m["sharpe"] > 0),
            f"{fwd_m['sharpe']:.3f}",
            "soft",
        ),
        (
            "gate_06_wf_6_8_profitable",
            _b(wf_pass_ratio),
            f"{wf_profitable}/8  max_mdd={wf_mdd*100:.2f}%",
            "soft",
        ),
        (
            "gate_07_median_hold_ge_1h",
            _b(np.isfinite(median_hold_h) and median_hold_h >= 1.0),
            f"{median_hold_h:.1f}h ({median_hold_bars:.0f} bars)",
            "soft",
        ),
        (
            "gate_08_ir_vs_spy_ge_0_2",
            _b((not np.isnan(ir)) and ir >= 0.2),
            f"{ir:.4f}",
            "soft",
        ),
        (
            "gate_09_cross_lib_concordance_3pp",
            _b(cross_ok),
            f"status={cross.get('status')} Δ={cross.get('delta_cagr_pp')}pp",
            "hard",
        ),
        (
            "gate_10_bootstrap_oos_99p9_ci_low_gt_0",
            _b((not np.isnan(oos_lo)) and oos_lo > 0),
            f"OOS [{oos_lo:.4f},{oos_hi:.4f}]",
            "hard",
        ),
        (
            "gate_10b_bootstrap_full_99p9_ci_low_gt_0",
            _b((not np.isnan(full_lo)) and full_lo > 0),
            f"FULL [{full_lo:.4f},{full_hi:.4f}]",
            "hard",
        ),
        (
            "gate_11_pbo_lt_0_3",
            _b(pbo_result is not None and pbo_result.pbo < 0.3),
            f"{pbo_result.pbo:.4f}" if pbo_result else "N/A",
            "hard",
        ),
        (
            "gate_12_dsr_p_lt_0_05",
            _b(dsr_res.p_value < 0.05),
            f"{dsr_res.p_value:.6f}",
            "hard",
        ),
        (
            "gate_13_cost2x_sharpe_gt_1",
            _b(cost2x_m["sharpe"] > (0.8 if leveraged else 1.0)),
            f"{cost2x_m['sharpe']:.3f}",
            "soft",
        ),
    ]

    # Halt-contract check: n_trades OOS < 100 → FAIL.
    n_trades_oos_approx = int(
        pd.Series(spy_res.entry_bars).apply(
            lambda ts: pd.Timestamp(OOS_RANGE[0]) <= ts.tz_localize(None) <= pd.Timestamp(OOS_RANGE[1])
        ).sum() if spy_res.entry_bars else 0
    )
    halt_n_trades = n_trades_oos_approx < 100
    halt_status = "TRIGGERED" if halt_n_trades else "ok"
    print(f"\n[halt-check] OOS n_trades ≈ {n_trades_oos_approx} (< 100 would halt); status={halt_status}")

    n_pass = sum(1 for _, p, *_ in gates if p is True)
    n_fail = sum(1 for _, p, *_ in gates if p is False)
    n_warn = sum(1 for _, p, *_ in gates if p is None)
    hard_fails = [n for n, p, _, lvl in gates if (p is False and lvl == "hard")]
    soft_fails = [n for n, p, _, lvl in gates if (p is False and lvl == "soft")]

    if halt_n_trades:
        verdict = "FAIL (halt: OOS trades < 100)"
    elif hard_fails:
        verdict = "FAIL (hard gates)"
    elif soft_fails:
        verdict = "FAIL (soft gates)"
    else:
        verdict = "PASS"

    print(f"\n=== GATES ({n_pass} PASS / {n_fail} FAIL / {n_warn} WARNING-ONLY) ===")
    for n, p, v, lvl in gates:
        mark = "PASS" if p is True else ("FAIL" if p is False else "WARN")
        print(f"  [{mark}] [{lvl:4s}] {n:46s} = {v}")
    print(f"\nFINAL VERDICT: {verdict}")
    if hard_fails:
        print(f"HARD gate fails: {hard_fails}")
    if soft_fails:
        print(f"SOFT gate fails: {soft_fails}")

    # -- Step 12: persist artifacts
    pd.DataFrame({"ret": spy_daily}).to_parquet(OUT_DIR / "daily_returns_SPY.parquet")
    pd.DataFrame({"ret": qqq_daily}).to_parquet(OUT_DIR / "daily_returns_QQQ.parquet")
    pd.DataFrame({"ret": _naive_index(cost2x_res.daily_returns())}).to_parquet(
        OUT_DIR / "daily_returns_cost2x.parquet"
    )

    grid_cfg_rows = []
    for tag, cfg in GRID_CFGS:
        s = grid_rets[tag]
        sh = compute_split_metrics(tag, s).sharpe
        grid_cfg_rows.append(
            {
                "tag": tag,
                "ma_days": cfg.ma_days,
                "atr_period": cfg.atr_period,
                "atr_multiplier": cfg.atr_multiplier,
                "atr_scale": cfg.atr_scale,
                "sharpe_full": float(sh),
            }
        )
    (OUT_DIR / "config_grid.csv").write_text(
        "tag,ma_days,atr_period,atr_multiplier,atr_scale,sharpe_full\n"
        + "\n".join(
            f"{c['tag']},{c['ma_days']},{c['atr_period']},{c['atr_multiplier']},{c['atr_scale']},{c['sharpe_full']:.4f}"
            for c in grid_cfg_rows
        )
    )

    agg = {
        "phase": "phase_3_7",
        "family": "H1a_zarattini_aziz_barbon_2024_base",
        "slug": "h1_zarattini_base",
        "produced_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "broker_path": "Pepperstone Razor SPX500 CFD (no DARF per mandate §2.2 rota A)",
        "cost_model": {
            "spread_one_way_fraction": WINNER_CFG.spread_one_way,
            "spread_one_way_bps": WINNER_CFG.spread_one_way * 1e4,
            "commission_round_trip": WINNER_CFG.commission_round_trip,
            "swap_daily": WINNER_CFG.swap_daily,
            "tax_rate": WINNER_CFG.tax_rate,
        },
        "data_source": "Tiingo IEX 1-min 2017-01-03 → 2026-04-14 (data/phase3_7/intraday/)",
        "winner_config": {
            "ma_days": WINNER_CFG.ma_days,
            "atr_period": WINNER_CFG.atr_period,
            "atr_multiplier": WINNER_CFG.atr_multiplier,
            "atr_scale": WINNER_CFG.atr_scale,
            "signal_start_bar": WINNER_CFG.signal_start_bar,
            "flat_at_close": WINNER_CFG.flat_at_close,
            "no_reentry_after_stop_same_day": WINNER_CFG.no_reentry_after_stop_same_day,
        },
        "windows": {
            "IS": list(IS_RANGE),
            "OOS": list(OOS_RANGE),
            "FWD": list(FWD_RANGE),
        },
        "splits": {
            "IS_SPY": is_m,
            "OOS_SPY": oos_m,
            "FWD_SPY": fwd_m,
            "FULL_SPY": full_m,
            "OOS_QQQ": qqq_oos_m,
            "SPY_OOS_BH": spy_oos_bh_m,
        },
        "walk_forward": {
            "n_windows": 8,
            "profitable": wf_profitable,
            "max_window_drawdown": wf_mdd,
            "pass": wf_pass_ratio,
        },
        "pbo": {
            "value": (pbo_result.pbo if pbo_result else None),
            "n_blocks": (pbo_result.n_blocks if pbo_result else None),
            "n_combinations": (pbo_result.n_combinations if pbo_result else None),
            "pass": ((pbo_result.pbo < 0.3) if pbo_result else None),
        },
        "dsr": {
            "dsr": dsr_res.dsr,
            "p_value": dsr_res.p_value,
            "observed_sharpe": dsr_res.observed_sharpe,
            "n_trials": dsr_res.n_trials,
            "pass": dsr_res.p_value < 0.05,
        },
        "bootstrap_oos": {"ci_low": oos_lo, "ci_high": oos_hi, "pass": (not np.isnan(oos_lo) and oos_lo > 0)},
        "bootstrap_full": {"ci_low": full_lo, "ci_high": full_hi, "pass": (not np.isnan(full_lo) and full_lo > 0)},
        "cross_lib": cross,
        "ir_vs_spy_oos": ir,
        "median_hold_minutes": median_hold_bars,
        "median_hold_hours": median_hold_h,
        "n_entries_full": len(spy_res.hold_bars),
        "n_trades_full": spy_res.n_trades,
        "n_trades_oos_approx": n_trades_oos_approx,
        "cum_spread_pct": spy_res.cum_spread_pct,
        "cum_commission_pct": spy_res.cum_commission_pct,
        "cost2x_oos": cost2x_m,
        "cagr_tier_oos_rotaA": cagr_tier_oos,
        "mdd_tier_oos_rotaA": mdd_tier_oos,
        "gates": [
            {"name": n, "pass": p, "value": v, "level": lvl} for n, p, v, lvl in gates
        ],
        "verdict": verdict,
        "hard_fails": hard_fails,
        "soft_fails": soft_fails,
        "halt_n_trades_triggered": halt_n_trades,
        "grid_configs": grid_cfg_rows,
        # Structured top-level keys:
        "is_sharpe": is_m["sharpe"],
        "is_cagr": is_m["cagr"],
        "oos_sharpe": oos_m["sharpe"],
        "oos_cagr": oos_m["cagr"],
        "oos_mdd": oos_m["max_drawdown"],
        "fwd_sharpe": fwd_m["sharpe"],
        "fwd_cagr": fwd_m["cagr"],
        "cross_lib_max_delta_cagr_pp": cross.get("delta_cagr_pp"),
        "bootstrap_oos_ci_low": oos_lo,
        "bootstrap_full_ci_low": full_lo,
        "cost_x2_sharpe": cost2x_m["sharpe"],
    }

    out_json = OUT_DIR / "AGGREGATE.json"
    tmp = out_json.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(agg, indent=2, default=float))
    tmp.replace(out_json)
    print(f"\n[write] {out_json}")
    print(f"[write] {OUT_DIR / 'daily_returns_SPY.parquet'}")
    print(f"[write] {OUT_DIR / 'config_grid.csv'}")
    print(f"\nTotal runtime: {time.time()-t0:.1f}s")


if __name__ == "__main__":
    main()

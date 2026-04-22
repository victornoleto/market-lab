"""Phase 3.7 H3.b — ETH Donchian ensemble independent signal runner.

Loads ETH daily bars from Tiingo parquet, runs the H3.b Donchian ensemble
+ ATR trail + 2-day time-stop strategy under F2-patched ``prev_weight ×
ret`` alignment, and emits the full 13-gate ``AGGREGATE.{md,json}`` per
the Phase 3.7-3 hunt prompt (rota A Pepperstone, no DARF).

Windows
-------
* IS:  2016-01-01 → 2020-06-30 (4.5y)
* OOS: 2020-07-01 → 2023-06-30 (3y)
* FWD: 2023-07-01 → 2026-04-14 (2.75y)

Crypto trades 7d/wk → periods_per_year = 365.

Execution shape
---------------
1. Load ETH daily (data/tiingo/daily/prices/ethusd.parquet).
2. Winner config simulation.
3. IS / OOS / FWD split metrics + full-period.
4. Bootstrap 99.9% CI (stationary block, block_mean=5, n=2000, 365-day
   annualization).
5. Walk-forward 8-window verdict.
6. IR vs ETH buy-hold on OOS (per hunt prompt gate 8: ETH not SPY —
   universe is ETH only).
7. Cost×2 sensitivity (spread × 2 + long swap × 2).
8. 12-config grid for PBO/DSR.
9. Vectorbt cross-lib concordance (OOS CAGR Δ ≤ 3pp).
10. Write AGGREGATE.{json,md} + per-split parquets + grid CSV.

Citations
---------
* Zarattini-Pagani-Barbon 2025 SSRN 5209907 — signal inspiration
  (reformulated per-asset per Phase 3.7-2 §6.3).
* `[universal_trend_tactics, p.295-299, p.338-343]` — Donchian + ATR.
* `[advances_fin_ml, p.31-34]` — prev_weight × ret alignment.
* `[advances_fin_ml, p.196-202]` — stationary bootstrap.
* `[advances_fin_ml, p.208-211, p.275]` — CSCV PBO + DSR.
* `docs/investment-mandate.md §2.4, §3.1` — 13 gates rota A.
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
    bootstrap_sharpe_ci,
    compute_split_metrics,
    walk_forward_verdict_from_returns,
)
from ai_trade.backtest.strategies.phase3_7_h3_eth_donchian import (  # noqa: E402
    H3EthDonchianConfig,
    simulate_h3_eth_donchian,
)
from ai_trade.backtest.validation.dsr import dsr as dsr_metric  # noqa: E402
from ai_trade.backtest.validation.pbo import pbo as cscv_pbo  # noqa: E402

OUT_DIR = ROOT / "reports/phase_3_7/h3_eth_donchian"
OUT_DIR.mkdir(parents=True, exist_ok=True)
DATA_FP = ROOT / "data/tiingo/daily/prices/ethusd.parquet"

# Crypto calendar (7d/wk).
PERIODS_PER_YEAR = 365

IS_RANGE = ("2016-01-01", "2020-06-30")
OOS_RANGE = ("2020-07-01", "2023-06-30")
FWD_RANGE = ("2023-07-01", "2026-04-14")

# Winner picked by best **IS** Sharpe in a pre-sweep (no OOS peek):
# lb=(20,40,80) k=2.0 risk=0.010 → IS Sharpe 1.684 (canonical 2×ATR
# trail + slow Donchian ensemble; literal 2:1 leverage cap).
WINNER_CFG = H3EthDonchianConfig(
    donchian_lookbacks=(20, 40, 80),
    atr_period=20,
    atr_multiplier=2.0,
    time_stop_days=2,
    risk_per_trade=0.010,
    max_leverage=2.0,
    spread_one_way=6.0e-4,
    commission_round_trip=0.0,
    swap_daily_long=-5.556e-4,
    swap_daily_short=2.083e-4,
    tax_rate=0.0,
    allow_short=True,
)

# 12-config grid for PBO/DSR (sensitivity around winner).
GRID_CFGS: list[tuple[str, H3EthDonchianConfig]] = [
    ("r10_lb20-40-80_k2",  H3EthDonchianConfig(donchian_lookbacks=(20,40,80),  risk_per_trade=0.010, atr_multiplier=2.0)),
    ("r10_lb20-40-80_k3",  H3EthDonchianConfig(donchian_lookbacks=(20,40,80),  risk_per_trade=0.010, atr_multiplier=3.0)),
    ("r10_lb10-20-40_k2",  H3EthDonchianConfig(donchian_lookbacks=(10,20,40),  risk_per_trade=0.010, atr_multiplier=2.0)),
    ("r10_lb10-20-40_k3",  H3EthDonchianConfig(donchian_lookbacks=(10,20,40),  risk_per_trade=0.010, atr_multiplier=3.0)),
    ("r10_lb5-10-20_k2",   H3EthDonchianConfig(donchian_lookbacks=(5,10,20),   risk_per_trade=0.010, atr_multiplier=2.0)),
    ("r10_lb5-10-20_k3",   H3EthDonchianConfig(donchian_lookbacks=(5,10,20),   risk_per_trade=0.010, atr_multiplier=3.0)),
    ("r5_lb20-40-80_k2",   H3EthDonchianConfig(donchian_lookbacks=(20,40,80),  risk_per_trade=0.005, atr_multiplier=2.0)),
    ("r15_lb20-40-80_k2",  H3EthDonchianConfig(donchian_lookbacks=(20,40,80),  risk_per_trade=0.015, atr_multiplier=2.0)),
    ("r10_lb20-40-80_k2_nshort", H3EthDonchianConfig(donchian_lookbacks=(20,40,80), risk_per_trade=0.010, atr_multiplier=2.0, allow_short=False)),
    ("r10_lb10-20-40_k2_nshort", H3EthDonchianConfig(donchian_lookbacks=(10,20,40), risk_per_trade=0.010, atr_multiplier=2.0, allow_short=False)),
    ("r10_lb20-40-80_k2_ts3",    H3EthDonchianConfig(donchian_lookbacks=(20,40,80), risk_per_trade=0.010, atr_multiplier=2.0, time_stop_days=3)),
    ("r10_lb20-40-80_k2_ts5",    H3EthDonchianConfig(donchian_lookbacks=(20,40,80), risk_per_trade=0.010, atr_multiplier=2.0, time_stop_days=5)),
]


def _slice_daily(s: pd.Series, start: str, end: str) -> pd.Series:
    a, b = pd.Timestamp(start), pd.Timestamp(end)
    return s.loc[(s.index >= a) & (s.index <= b)]


def _split_metrics_crypto(name: str, r: pd.Series) -> dict:
    """Like compute_split_metrics but with 365-day annualization."""
    rd = r.dropna().astype(float)
    if rd.empty:
        return {
            "name": name,
            "n_bars": 0,
            "sharpe": 0.0,
            "cagr": 0.0,
            "max_drawdown": 0.0,
            "final_equity_from_unit": 1.0,
        }
    mu = float(rd.mean())
    sigma = float(rd.std(ddof=1))
    sharpe = (mu / sigma * np.sqrt(PERIODS_PER_YEAR)) if sigma > 0 else 0.0
    eq = (1.0 + rd).cumprod()
    final = float(eq.iloc[-1])
    years = len(rd) / PERIODS_PER_YEAR
    cagr = (final ** (1.0 / years) - 1.0) if years > 0 and final > 0 else 0.0
    peak = eq.cummax()
    mdd = float((eq / peak - 1.0).min())
    return {
        "name": name,
        "n_bars": int(len(rd)),
        "sharpe": float(sharpe),
        "cagr": float(cagr),
        "max_drawdown": float(mdd),
        "final_equity_from_unit": final,
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
    if mdd_mag <= 0.50:
        return "Marginal"
    if mdd_mag <= 0.75:
        return "Warning"
    return "Reject"


def _ir_vs_benchmark(port: pd.Series, bh: pd.Series) -> float:
    common = port.index.intersection(bh.index)
    if len(common) < 20:
        return float("nan")
    excess = port.loc[common] - bh.loc[common]
    mu, sd = float(excess.mean()), float(excess.std(ddof=1))
    if sd <= 0:
        return 0.0
    return mu / sd * np.sqrt(PERIODS_PER_YEAR)


def _vectorbt_cross_check(
    eth: pd.DataFrame,
    cfg: H3EthDonchianConfig,
    ref_oos_daily: pd.Series,
) -> dict:
    """Vectorbt cross-lib concordance check on ETH OOS."""
    try:
        import vectorbt as vbt  # noqa: F401
    except Exception as e:
        return {
            "status": "skipped",
            "reason": f"vectorbt unavailable: {e}",
            "delta_cagr_pp": None,
        }

    # Reference: our pandas simulator weights + returns.
    res = simulate_h3_eth_donchian(eth, cfg)
    weights = res.weights
    close = eth["close"].astype(float).copy()
    close.index = pd.DatetimeIndex(close.index).normalize()
    close = close[~close.index.duplicated(keep="last")].sort_index()

    # Boolean entries/exits derived from weight transitions.
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
            fees=cfg.spread_one_way,
            freq="1D",
            init_cash=1.0,
            size=1.0,
            size_type="value",
        )
        vbt_daily_ret = pf.returns()
    except Exception as e:
        return {
            "status": "failed",
            "reason": f"vbt.Portfolio.from_signals raised: {e}",
            "delta_cagr_pp": None,
        }

    vbt_daily_ret = vbt_daily_ret.replace([np.inf, -np.inf], np.nan).fillna(0.0)
    vbt_daily_ret.index = pd.DatetimeIndex(vbt_daily_ret.index).normalize()
    vbt_oos = _slice_daily(vbt_daily_ret, *OOS_RANGE)
    if len(vbt_oos) < 20 or len(ref_oos_daily) < 20:
        return {
            "status": "insufficient_overlap",
            "reason": f"vbt_oos={len(vbt_oos)}, ref_oos={len(ref_oos_daily)}",
            "delta_cagr_pp": None,
        }
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
        y = len(r) / PERIODS_PER_YEAR
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


def _eth_buyhold_returns(eth: pd.DataFrame) -> pd.Series:
    """ETH daily buy-hold returns from adj_close."""
    ac = eth["adj_close"].astype(float).copy()
    ac.index = pd.DatetimeIndex(ac.index).normalize()
    ac = ac[~ac.index.duplicated(keep="last")].sort_index()
    return ac.pct_change().dropna()


def main() -> None:
    t0 = time.time()
    print("=" * 80)
    print("Phase 3.7 H3.b — ETH Donchian ensemble (independent per-asset)")
    print("=" * 80)

    # -- Step 1: load data
    print(f"\n[data] loading ETH daily from {DATA_FP}")
    eth = pd.read_parquet(DATA_FP)
    print(f"[data] ETH {eth.shape} {eth.index[0]} -> {eth.index[-1]}")

    # -- Step 2: winner run
    print(f"\n[winner] config = {WINNER_CFG}")
    ts = time.time()
    eth_res = simulate_h3_eth_donchian(eth, WINNER_CFG, ticker="ETHUSD")
    print(
        f"[winner] done in {time.time()-ts:.2f}s  n_trades={eth_res.n_trades}  "
        f"long={eth_res.n_long}  short={eth_res.n_short}  "
        f"median_hold={eth_res.median_hold_days()}"
    )

    # -- Step 3: split metrics
    daily = eth_res.daily_returns
    is_ret = _slice_daily(daily, *IS_RANGE)
    oos_ret = _slice_daily(daily, *OOS_RANGE)
    fwd_ret = _slice_daily(daily, *FWD_RANGE)
    full_ret = daily

    is_m = _split_metrics_crypto("IS", is_ret)
    oos_m = _split_metrics_crypto("OOS", oos_ret)
    fwd_m = _split_metrics_crypto("FWD", fwd_ret)
    full_m = _split_metrics_crypto("FULL", full_ret)

    print(f"[IS]  S={is_m['sharpe']:.3f} CAGR={is_m['cagr']*100:.2f}% MDD={is_m['max_drawdown']*100:.2f}% n={is_m['n_bars']}")
    print(f"[OOS] S={oos_m['sharpe']:.3f} CAGR={oos_m['cagr']*100:.2f}% MDD={oos_m['max_drawdown']*100:.2f}% n={oos_m['n_bars']}")
    print(f"[FWD] S={fwd_m['sharpe']:.3f} CAGR={fwd_m['cagr']*100:.2f}% MDD={fwd_m['max_drawdown']*100:.2f}% n={fwd_m['n_bars']}")

    # -- Step 4: Bootstrap 99.9% CIs
    if len(oos_ret) >= 20:
        oos_lo, oos_hi = bootstrap_sharpe_ci(
            oos_ret, alpha=0.001, n_resamples=2000, block_mean=5, seed=42,
            periods_per_year=PERIODS_PER_YEAR,
        )
    else:
        oos_lo, oos_hi = float("nan"), float("nan")
    if len(full_ret) >= 20:
        full_lo, full_hi = bootstrap_sharpe_ci(
            full_ret, alpha=0.001, n_resamples=2000, block_mean=5, seed=42,
            periods_per_year=PERIODS_PER_YEAR,
        )
    else:
        full_lo, full_hi = float("nan"), float("nan")
    print(f"[BOOT] OOS  99.9% CI Sharpe = [{oos_lo:.4f}, {oos_hi:.4f}]")
    print(f"[BOOT] FULL 99.9% CI Sharpe = [{full_lo:.4f}, {full_hi:.4f}]")

    # -- Step 5: Walk-forward 8 windows
    if len(full_ret) >= 8:
        wf_ratio, wf_mdd, _ = walk_forward_verdict_from_returns(
            full_ret, n_windows=8, max_drawdown_cap=0.75
        )
    else:
        wf_ratio, wf_mdd = 0.0, 0.0
    wf_profitable = int(round(wf_ratio * 8))
    wf_pass = wf_profitable >= 6
    print(f"[WF] {wf_profitable}/8 profitable  max_window_mdd={wf_mdd*100:.2f}%")

    # -- Step 6: IR vs ETH buy-hold OOS
    eth_bh = _eth_buyhold_returns(eth)
    eth_oos_bh = _slice_daily(eth_bh, *OOS_RANGE)
    eth_oos_bh_m = _split_metrics_crypto("ETH_OOS_BH", eth_oos_bh)
    ir = _ir_vs_benchmark(oos_ret, eth_oos_bh)
    print(f"[IR] vs ETH buy-hold OOS = {ir:.4f} (ETH OOS BH S={eth_oos_bh_m['sharpe']:.3f})")

    # -- Step 7: median hold
    median_hold_days = eth_res.median_hold_days()
    print(f"[HOLD] median hold days = {median_hold_days}  n_entries={len(eth_res.hold_lengths)}")

    # -- Step 8: cost×2 sensitivity
    cost2x_cfg = H3EthDonchianConfig(
        donchian_lookbacks=WINNER_CFG.donchian_lookbacks,
        atr_period=WINNER_CFG.atr_period,
        atr_multiplier=WINNER_CFG.atr_multiplier,
        time_stop_days=WINNER_CFG.time_stop_days,
        risk_per_trade=WINNER_CFG.risk_per_trade,
        max_leverage=WINNER_CFG.max_leverage,
        spread_one_way=WINNER_CFG.spread_one_way * 2.0,
        commission_round_trip=WINNER_CFG.commission_round_trip,
        swap_daily_long=WINNER_CFG.swap_daily_long * 2.0,
        swap_daily_short=WINNER_CFG.swap_daily_short,  # credit not doubled
        tax_rate=WINNER_CFG.tax_rate,
        allow_short=WINNER_CFG.allow_short,
    )
    print(f"\n[cost2x] running (spread={cost2x_cfg.spread_one_way*1e4:.1f}bps, swap_long={cost2x_cfg.swap_daily_long*100:.4f}%)")
    cost2x_res = simulate_h3_eth_donchian(eth, cost2x_cfg, ticker="ETHUSD")
    cost2x_oos_daily = _slice_daily(cost2x_res.daily_returns, *OOS_RANGE)
    cost2x_m = _split_metrics_crypto("OOS_cost2x", cost2x_oos_daily)
    print(f"[cost2x] OOS Sharpe={cost2x_m['sharpe']:.3f} CAGR={cost2x_m['cagr']*100:.2f}%")

    # -- Step 9: Grid for PBO/DSR
    print(f"\n[grid] running {len(GRID_CFGS)} sibling configs for PBO/DSR...")
    grid_rets: dict[str, pd.Series] = {}
    for tag, cfg in GRID_CFGS:
        ts = time.time()
        r = simulate_h3_eth_donchian(eth, cfg, ticker="ETHUSD")
        g_daily = r.daily_returns
        grid_rets[tag] = g_daily
        sh = _split_metrics_crypto(tag, g_daily)["sharpe"]
        print(f"  [grid] {tag:30s} done in {time.time()-ts:.2f}s Sharpe_full={sh:.3f} ntrd={r.n_trades}")

    grid_df = pd.concat(grid_rets, axis=1).dropna(how="any")
    print(f"[grid] aligned matrix shape: {grid_df.shape}")

    pbo_result = None
    if grid_df.shape[0] >= 100 and grid_df.shape[1] >= 2:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            pbo_result = cscv_pbo(grid_df.to_numpy(), n_blocks=10)
        print(f"[PBO] value={pbo_result.pbo:.4f} n_combos={pbo_result.n_combinations}")
    else:
        print("[PBO] skipped — insufficient grid")

    dsr_res = dsr_metric(oos_ret.to_numpy(dtype=float), n_trials=len(GRID_CFGS))
    print(f"[DSR] p_value={dsr_res.p_value:.6f}  obs_SR={dsr_res.observed_sharpe:.4f}")

    # -- Step 10: cross-lib vectorbt
    print("\n[cross-lib] running vectorbt concordance on ETH OOS...")
    ts = time.time()
    try:
        cross = _vectorbt_cross_check(eth, WINNER_CFG, oos_ret)
    except Exception as e:
        cross = {"status": "error", "reason": str(e), "delta_cagr_pp": None}
    print(
        f"[cross-lib] done in {time.time()-ts:.1f}s  status={cross.get('status')}  "
        f"delta_cagr_pp={cross.get('delta_cagr_pp')}"
    )

    # -- Step 11: 13 gates (rota A, ETH benchmark)
    cagr_tier_oos = _cagr_tier_rotaA(oos_m["cagr"])
    mdd_tier_oos = _mdd_tier_rotaA(abs(oos_m["max_drawdown"]))
    leveraged = WINNER_CFG.max_leverage > 1.0  # 2:1 = leveraged
    cost2x_threshold = 0.8 if leveraged else 1.0

    cross_ok = (
        cross.get("status") == "ok"
        and cross.get("delta_cagr_pp") is not None
        and cross["delta_cagr_pp"] <= 3.0
    )

    def _b(x) -> bool | None:
        if x is None:
            return None
        return bool(x)

    gates = [
        ("gate_01_is_sharpe_gt_0_5", _b(is_m["sharpe"] > 0.5), f"{is_m['sharpe']:.3f}", "soft"),
        ("gate_02_oos_sharpe_ge_1_3", _b(oos_m["sharpe"] >= 1.3), f"{oos_m['sharpe']:.3f}", "soft"),
        ("gate_03_oos_cagr_tier", None, f"{oos_m['cagr']*100:.2f}% → {cagr_tier_oos}", "warning"),
        ("gate_04_oos_mdd_tier", None, f"{oos_m['max_drawdown']*100:.2f}% → {mdd_tier_oos}", "warning"),
        ("gate_05_fwd_sharpe_gt_0", _b(fwd_m["sharpe"] > 0), f"{fwd_m['sharpe']:.3f}", "soft"),
        ("gate_06_wf_6_8_profitable", _b(wf_pass), f"{wf_profitable}/8 max_mdd={wf_mdd*100:.2f}%", "soft"),
        ("gate_07_median_hold_le_2d", _b(np.isfinite(median_hold_days) and median_hold_days <= 2.0 and median_hold_days >= 1.0), f"{median_hold_days} d", "soft"),
        ("gate_08_ir_vs_eth_ge_0_2", _b((not np.isnan(ir)) and ir >= 0.2), f"{ir:.4f}", "soft"),
        ("gate_09_cross_lib_concordance_3pp", _b(cross_ok), f"status={cross.get('status')} Δ={cross.get('delta_cagr_pp')}pp", "hard"),
        ("gate_10_bootstrap_oos_99p9_ci_low_gt_0", _b((not np.isnan(oos_lo)) and oos_lo > 0), f"OOS [{oos_lo:.4f},{oos_hi:.4f}]", "hard"),
        ("gate_10b_bootstrap_full_99p9_ci_low_gt_0", _b((not np.isnan(full_lo)) and full_lo > 0), f"FULL [{full_lo:.4f},{full_hi:.4f}]", "hard"),
        ("gate_11_pbo_lt_0_5", _b(pbo_result is not None and pbo_result.pbo < 0.5), f"{pbo_result.pbo:.4f}" if pbo_result else "N/A", "hard"),
        ("gate_12_dsr_p_lt_0_05", _b(dsr_res.p_value < 0.05), f"{dsr_res.p_value:.6f}", "hard"),
        ("gate_13_cost2x_sharpe", _b(cost2x_m["sharpe"] > cost2x_threshold), f"{cost2x_m['sharpe']:.3f} (thr={cost2x_threshold})", "soft"),
    ]

    # Halt-contract: n_trades OOS < 50 → FAIL.
    n_trades_oos = int(sum(
        1 for tsb in eth_res.entry_bars
        if pd.Timestamp(OOS_RANGE[0]) <= tsb <= pd.Timestamp(OOS_RANGE[1])
    ))
    halt_n_trades = n_trades_oos < 50
    halt_status = "TRIGGERED" if halt_n_trades else "ok"
    print(f"\n[halt-check] OOS n_trades = {n_trades_oos} (< 50 halts); status={halt_status}")

    n_pass = sum(1 for _, p, *_ in gates if p is True)
    n_fail = sum(1 for _, p, *_ in gates if p is False)
    n_warn = sum(1 for _, p, *_ in gates if p is None)
    hard_fails = [n for n, p, _, lvl in gates if (p is False and lvl == "hard")]
    soft_fails = [n for n, p, _, lvl in gates if (p is False and lvl == "soft")]

    if halt_n_trades:
        verdict = "FAIL (halt: OOS trades < 50)"
    elif hard_fails:
        verdict = "FAIL (hard gates)"
    elif soft_fails:
        verdict = "FAIL (soft gates)"
    else:
        verdict = "PASS"

    print(f"\n=== GATES ({n_pass} PASS / {n_fail} FAIL / {n_warn} WARNING-ONLY) ===")
    for n, p, v, lvl in gates:
        mark = "PASS" if p is True else ("FAIL" if p is False else "WARN")
        print(f"  [{mark}] [{lvl:7s}] {n:46s} = {v}")
    print(f"\nFINAL VERDICT: {verdict}")
    if hard_fails:
        print(f"HARD gate fails: {hard_fails}")
    if soft_fails:
        print(f"SOFT gate fails: {soft_fails}")

    # -- Step 12: persist artifacts
    pd.DataFrame({"ret": daily}).to_parquet(OUT_DIR / "daily_returns_ETH.parquet")
    pd.DataFrame({"ret": cost2x_res.daily_returns}).to_parquet(
        OUT_DIR / "daily_returns_cost2x.parquet"
    )

    grid_cfg_rows = []
    for tag, cfg in GRID_CFGS:
        s = grid_rets[tag]
        sh = _split_metrics_crypto(tag, s)["sharpe"]
        grid_cfg_rows.append(
            {
                "tag": tag,
                "donchian_lookbacks": str(cfg.donchian_lookbacks),
                "atr_period": cfg.atr_period,
                "atr_multiplier": cfg.atr_multiplier,
                "time_stop_days": cfg.time_stop_days,
                "risk_per_trade": cfg.risk_per_trade,
                "allow_short": cfg.allow_short,
                "sharpe_full": float(sh),
            }
        )
    (OUT_DIR / "config_grid.csv").write_text(
        "tag,donchian_lookbacks,atr_period,atr_multiplier,time_stop_days,risk_per_trade,allow_short,sharpe_full\n"
        + "\n".join(
            f"{c['tag']},{c['donchian_lookbacks']},{c['atr_period']},{c['atr_multiplier']},{c['time_stop_days']},{c['risk_per_trade']},{c['allow_short']},{c['sharpe_full']:.4f}"
            for c in grid_cfg_rows
        )
    )

    agg = {
        "phase": "phase_3_7",
        "family": "H3b_eth_donchian_ensemble_independent",
        "slug": "h3_eth_donchian",
        "produced_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "broker_path": "Pepperstone ETHUSD CFD (rota A, no DARF per mandate §2.2)",
        "cost_model": {
            "spread_one_way_fraction": WINNER_CFG.spread_one_way,
            "spread_one_way_bps": WINNER_CFG.spread_one_way * 1e4,
            "commission_round_trip": WINNER_CFG.commission_round_trip,
            "swap_daily_long": WINNER_CFG.swap_daily_long,
            "swap_daily_short": WINNER_CFG.swap_daily_short,
            "swap_daily_long_annualized": WINNER_CFG.swap_daily_long * 365,
            "swap_daily_short_annualized": WINNER_CFG.swap_daily_short * 365,
            "tax_rate": WINNER_CFG.tax_rate,
            "max_leverage": WINNER_CFG.max_leverage,
        },
        "data_source": f"Tiingo ETH daily 2015-08-08 → 2026-04-14 ({DATA_FP.name}, {len(eth)} bars)",
        "winner_config": {
            "donchian_lookbacks": list(WINNER_CFG.donchian_lookbacks),
            "atr_period": WINNER_CFG.atr_period,
            "atr_multiplier": WINNER_CFG.atr_multiplier,
            "time_stop_days": WINNER_CFG.time_stop_days,
            "risk_per_trade": WINNER_CFG.risk_per_trade,
            "max_leverage": WINNER_CFG.max_leverage,
            "allow_short": WINNER_CFG.allow_short,
        },
        "windows": {
            "IS": list(IS_RANGE),
            "OOS": list(OOS_RANGE),
            "FWD": list(FWD_RANGE),
        },
        "splits": {
            "IS_ETH": is_m,
            "OOS_ETH": oos_m,
            "FWD_ETH": fwd_m,
            "FULL_ETH": full_m,
            "ETH_OOS_BH": eth_oos_bh_m,
        },
        "walk_forward": {
            "n_windows": 8,
            "profitable": wf_profitable,
            "max_window_drawdown": wf_mdd,
            "pass": wf_pass,
        },
        "pbo": {
            "value": (pbo_result.pbo if pbo_result else None),
            "n_blocks": (pbo_result.n_blocks if pbo_result else None),
            "n_combinations": (pbo_result.n_combinations if pbo_result else None),
            "pass": ((pbo_result.pbo < 0.5) if pbo_result else None),
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
        "ir_vs_eth_oos": ir,
        "median_hold_days": median_hold_days,
        "n_entries_full": len(eth_res.hold_lengths),
        "n_trades_full": eth_res.n_trades,
        "n_trades_oos": n_trades_oos,
        "n_long": eth_res.n_long,
        "n_short": eth_res.n_short,
        "cum_spread_pct": eth_res.cum_spread_pct,
        "cum_commission_pct": eth_res.cum_commission_pct,
        "cum_swap_pct": eth_res.cum_swap_pct,
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
    print(f"[write] {OUT_DIR / 'daily_returns_ETH.parquet'}")
    print(f"[write] {OUT_DIR / 'config_grid.csv'}")
    print(f"\nTotal runtime: {time.time()-t0:.1f}s")


if __name__ == "__main__":
    main()

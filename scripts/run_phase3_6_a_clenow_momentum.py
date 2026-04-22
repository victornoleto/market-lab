"""Phase 3.6 Family A — Clenow momentum honest 13-gate pipeline.

Loads the Tiingo panel, runs the swing-horizon Clenow momentum
(top-N cross-sectional adjusted-slope) under the F2-patched engine
conventions, and emits a full 13-gate AGGREGATE.{md,json} per plan
§5 with user-locked relaxations.

Execution shape
---------------
1. Build liquid universe on Tiingo panel (ADV ≥ $50M, 252d median).
2. Compute daily returns for the WINNER config (N=20, rebal=21d,
   regime ON) over IS+OOS+FWD inclusive.
3. IS/OOS/FWD split metrics + full bootstrap + WF + IR + cost×2.
4. Grid run (5 sibling configs) for CPCV/PBO + DSR.
5. Write AGGREGATE artifacts + daily_returns.parquet (local).

Citations
---------
* Cross-sectional momentum top-N: [stocks_on_the_move, p.60-98].
* 90-day regression slope × R²: [stocks_on_the_move, p.75-82].
* 200d market regime filter: [stocks_on_the_move, p.66-99].
* ATR-risk-parity sizing: [stocks_on_the_move, p.86-89].
* Bootstrap 99.9% CI / WF / PBO / DSR: [advances_fin_ml, p.196-211,
  p.273-275, ch.11].
* Look-ahead timing convention: [advances_fin_ml, p.31-34].
"""

from __future__ import annotations

import json
import sys
import time
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
from ai_trade.backtest.strategies.phase3_6_a_clenow_momentum import (  # noqa: E402
    ClenowMomentumConfig,
    simulate_clenow_momentum,
)
from ai_trade.backtest.validation.dsr import dsr as dsr_metric  # noqa: E402
from ai_trade.backtest.validation.pbo import pbo as cscv_pbo  # noqa: E402

OUT_DIR = ROOT / "reports/phase_3_6/a_clenow_momentum"
OUT_DIR.mkdir(parents=True, exist_ok=True)
TIINGO_DAILY = ROOT / "data/tiingo/daily/prices"

IS_RANGE = ("2001-05-14", "2017-12-31")
OOS_RANGE = ("2018-01-01", "2023-12-31")
FWD_RANGE = ("2024-01-01", "2026-04-14")
CDI_FLOOR = 0.13

# Winner config (plan brief default)
WINNER_CFG = ClenowMomentumConfig(
    top_n=20,
    rebalance_days=21,
    use_regime_filter=True,
)

# Sensitivity grid for CPCV/PBO (≥5 configs required for gates 11-12).
# 3 × 2 × 2 = 12 cells, subset to 5 representative ones to keep runtime
# manageable. Chosen to exercise top_n, rebal, regime-toggle dimensions.
GRID = [
    ClenowMomentumConfig(top_n=10, rebalance_days=21, use_regime_filter=True),
    ClenowMomentumConfig(top_n=20, rebalance_days=21, use_regime_filter=True),
    ClenowMomentumConfig(top_n=30, rebalance_days=21, use_regime_filter=True),
    ClenowMomentumConfig(top_n=20, rebalance_days=10, use_regime_filter=True),
    ClenowMomentumConfig(top_n=20, rebalance_days=21, use_regime_filter=False),
]


def _load_tiingo(ticker: str) -> pd.DataFrame | None:
    fp = TIINGO_DAILY / f"{ticker}.parquet"
    if not fp.exists():
        return None
    df = pd.read_parquet(fp)
    df.index = pd.DatetimeIndex(df.index)
    return df


def _build_universe(
    min_bars: int = 500, adv_floor_usd: float = 50_000_000.0
) -> dict[str, pd.DataFrame]:
    """Load every Tiingo ticker and keep those with:
    - ≥ min_bars rows (so they have enough history for screening)
    - max observed adv*close (rolling-252 mean) ≥ adv_floor_usd at any point.

    Returns dict {ticker → DataFrame}. SPY is excluded from the
    momentum universe (used as regime benchmark separately).
    """
    print(f"[universe] scanning {TIINGO_DAILY}...")
    paths = sorted(TIINGO_DAILY.glob("*.parquet"))
    panel: dict[str, pd.DataFrame] = {}
    exclude = {"SPY", "QQQ", "DIA", "IWM", "EFA", "EEM", "GLD", "TLT", "IEF", "SHY",
               "UPRO", "SSO", "TMF", "SPXL", "TQQQ", "SQQQ", "SPXS", "TMV", "UVXY",
               "VIXY", "BIL", "VTI", "IVV", "VOO", "SPLG", "USO", "UNG", "SLV",
               "XLK", "XLF", "XLE", "XLV", "XLY", "XLP", "XLI", "XLB", "XLRE",
               "XLU", "XLC"}
    for fp in paths:
        t = fp.stem
        # Skip non-stock tickers (crypto, FX, commodities) — detected by
        # lowercase names (Tiingo uses lowercase for these) and by
        # presence of weekend timestamps.
        if t.islower() or any(c in t.lower() for c in ("usd", "eur", "jpy", "gbp")):
            continue
        if t in exclude:
            continue
        try:
            df = pd.read_parquet(fp)
        except Exception:
            continue
        if len(df) < min_bars:
            continue
        df.index = pd.DatetimeIndex(df.index)
        # Hard guard: drop tickers with any weekend rows (crypto/FX).
        if df.index.dayofweek.isin([5, 6]).any():
            continue
        # Quick liquidity eyeball: max of (close × volume) mean over 252d
        cv = (df["close"].astype(float) * df["volume"].astype(float))
        try:
            max_adv = float(cv.rolling(252, min_periods=60).mean().max())
        except Exception:
            continue
        if not np.isfinite(max_adv) or max_adv < adv_floor_usd:
            continue
        panel[t] = df
    print(f"[universe] retained {len(panel)} tickers after ADV floor ${adv_floor_usd/1e6:.0f}M")
    return panel


def _slice(s: pd.Series, start: str, end: str) -> pd.Series:
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


def _ir_vs_spy(port_oos: pd.Series, spy_oos: pd.Series) -> float:
    common = port_oos.index.intersection(spy_oos.index)
    if len(common) < 20:
        return float("nan")
    excess = port_oos.loc[common] - spy_oos.loc[common]
    mu, sd = float(excess.mean()), float(excess.std(ddof=1))
    if sd <= 0:
        return 0.0
    return mu / sd * np.sqrt(TRADING_DAYS)


def _spy_daily() -> pd.DataFrame:
    return _load_tiingo("SPY")


def main() -> None:
    t0 = time.time()
    print("=" * 80)
    print("Phase 3.6 Family A — Clenow momentum honest 13-gate pipeline")
    print("=" * 80)

    # -- Step 1: universe + SPY
    panel = _build_universe()
    spy_df = _spy_daily()
    assert spy_df is not None, "SPY missing"

    # -- Step 2: winner config simulation
    print(f"\n[winner] running {WINNER_CFG}...")
    ts = time.time()
    winner = simulate_clenow_momentum(panel, spy_df, WINNER_CFG)
    print(f"[winner] done in {time.time()-ts:.1f}s")
    dr = winner.daily_returns.dropna()
    print(
        f"[winner] bars={len(dr)} span={dr.index[0].date()}→{dr.index[-1].date()} "
        f"avg_n_held={winner.n_held.mean():.1f}"
    )

    is_ret = _slice(dr, *IS_RANGE)
    oos_ret = _slice(dr, *OOS_RANGE)
    fwd_ret = _slice(dr, *FWD_RANGE)
    full_ret = dr
    is_m = _mdict("IS", is_ret)
    oos_m = _mdict("OOS", oos_ret)
    fwd_m = _mdict("FWD", fwd_ret)
    full_m = _mdict("FULL", full_ret)
    print(f"[IS]  S={is_m['sharpe']:.3f} CAGR={is_m['cagr']*100:.2f}% MDD={is_m['max_drawdown']*100:.2f}%")
    print(f"[OOS] S={oos_m['sharpe']:.3f} CAGR={oos_m['cagr']*100:.2f}% MDD={oos_m['max_drawdown']*100:.2f}%")
    print(f"[FWD] S={fwd_m['sharpe']:.3f} CAGR={fwd_m['cagr']*100:.2f}% MDD={fwd_m['max_drawdown']*100:.2f}%")

    # -- Step 3: WF
    if len(full_ret) >= 8:
        wf_ratio, wf_mdd, wf_pass = walk_forward_verdict_from_returns(
            full_ret, n_windows=8, max_drawdown_cap=0.30
        )
    else:
        wf_ratio, wf_mdd, wf_pass = 0.0, 0.0, False
    print(f"[WF]  ratio={wf_ratio:.3f} ({int(wf_ratio*8)}/8) mdd={wf_mdd*100:.2f}% pass={wf_pass}")

    # -- Step 4: Bootstrap CIs
    oos_lo, oos_hi = bootstrap_sharpe_ci(
        oos_ret, alpha=0.001, n_resamples=2000, block_mean=5, seed=42
    )
    full_lo, full_hi = bootstrap_sharpe_ci(
        full_ret, alpha=0.001, n_resamples=2000, block_mean=5, seed=42
    )
    print(f"[BOOT] OOS 99.9% CI [{oos_lo:.4f}, {oos_hi:.4f}]")
    print(f"[BOOT] FULL 99.9% CI [{full_lo:.4f}, {full_hi:.4f}]")

    # -- Step 5: IR vs SPY buy-hold
    spy_ret_full = spy_df["adj_close"].pct_change().dropna()
    spy_ret_full.index = pd.DatetimeIndex(spy_ret_full.index).normalize()
    dr.index = pd.DatetimeIndex(dr.index).normalize()
    oos_ret.index = pd.DatetimeIndex(oos_ret.index).normalize()
    spy_oos = _slice(spy_ret_full, *OOS_RANGE)
    spy_m = _mdict("SPY_OOS", spy_oos)
    ir = _ir_vs_spy(oos_ret, spy_oos)
    print(f"[IR]  vs SPY OOS={ir:.4f}  (SPY OOS Sharpe={spy_m['sharpe']:.3f} CAGR={spy_m['cagr']*100:.2f}%)")

    # -- Step 6: median hold from the winner simulation
    mh = winner.median_hold_days()
    print(f"[HOLD] median hold = {mh:.1f}d (n_entries={len(winner.hold_lengths)})")

    # -- Step 7: cost×2 sensitivity
    cost2x_cfg = ClenowMomentumConfig(
        top_n=WINNER_CFG.top_n,
        rebalance_days=WINNER_CFG.rebalance_days,
        use_regime_filter=WINNER_CFG.use_regime_filter,
        spread_one_way_pct=WINNER_CFG.spread_one_way_pct * 2.0,
        tax_rate=WINNER_CFG.tax_rate,
    )
    print(f"\n[cost2x] running cost×2 config (spread {cost2x_cfg.spread_one_way_pct:.4f})...")
    ts = time.time()
    cost2x = simulate_clenow_momentum(panel, spy_df, cost2x_cfg)
    print(f"[cost2x] done in {time.time()-ts:.1f}s")
    cost2x_oos = _slice(cost2x.daily_returns.dropna(), *OOS_RANGE)
    cost2x_m = _mdict("OOS_2x", cost2x_oos)
    print(f"[COST×2] OOS Sharpe={cost2x_m['sharpe']:.3f} CAGR={cost2x_m['cagr']*100:.2f}%")

    # -- Step 8: GRID run for CPCV/PBO + DSR
    print(f"\n[grid] running {len(GRID)} sibling configs for PBO/DSR...")
    grid_rets: dict[str, pd.Series] = {}
    for idx_g, cfg in enumerate(GRID):
        tag = (
            f"top{cfg.top_n}_rebal{cfg.rebalance_days}_"
            f"reg{'on' if cfg.use_regime_filter else 'off'}"
        )
        if cfg == WINNER_CFG:
            # reuse winner
            grid_rets[tag] = winner.daily_returns
            print(f"  [grid {idx_g+1}/{len(GRID)}] {tag} (reuse winner)")
            continue
        ts = time.time()
        r = simulate_clenow_momentum(panel, spy_df, cfg)
        print(f"  [grid {idx_g+1}/{len(GRID)}] {tag} done in {time.time()-ts:.1f}s  S_full={r.sharpe():.3f}")
        grid_rets[tag] = r.daily_returns

    # Align all on intersection of indices
    grid_df = pd.concat(grid_rets, axis=1).dropna(how="any")
    print(f"[grid] aligned matrix shape: {grid_df.shape}")
    if grid_df.shape[0] >= 100 and grid_df.shape[1] >= 2:
        pbo_result = cscv_pbo(grid_df.to_numpy(), n_blocks=10)
        print(f"[PBO] value={pbo_result.pbo:.4f} n_combinations={pbo_result.n_combinations}")
    else:
        pbo_result = None
        print("[PBO] skipped — insufficient grid")

    dsr_res = dsr_metric(oos_ret.dropna().to_numpy(dtype=float), n_trials=len(GRID))
    print(f"[DSR] p_value={dsr_res.p_value:.6f} obs_SR={dsr_res.observed_sharpe:.4f}")

    # -- Step 9: 13 gates evaluation
    gate_3_hard = oos_m["cagr"] >= 0.30
    gate_3_soft = oos_m["cagr"] >= CDI_FLOOR
    # Relaxation-aware: plan §5 uses gate 3 ≥13% (CDI) as the binding
    # threshold; ≥30% is target only. So we compute soft-PASS, but report
    # both rows for transparency.
    wf_mdd_cap = 0.30  # plan gate 6 relaxed
    wf_ratio_ok = wf_ratio >= 6 / 8
    wf_mdd_ok = wf_mdd <= wf_mdd_cap
    wf_pass_relaxed = wf_ratio_ok and wf_mdd_ok

    gates = [
        (
            "gate_01_bootstrap_oos_99p9_ci_low_gt_0",
            oos_lo > 0,
            f"{oos_lo:.4f}",
        ),
        (
            "gate_01b_bootstrap_full_99p9_ci_low_gt_0",
            full_lo > 0,
            f"{full_lo:.4f}",
        ),
        (
            "gate_02_oos_sharpe_ge_1_5",
            oos_m["sharpe"] >= 1.5,
            f"{oos_m['sharpe']:.3f}",
        ),
        (
            "gate_03_oos_cagr_ge_13pct_CDI",
            gate_3_soft,
            f"{oos_m['cagr']*100:.2f}%",
        ),
        (
            "gate_03_target_oos_cagr_ge_30pct",
            gate_3_hard,
            f"{oos_m['cagr']*100:.2f}%",
        ),
        (
            "gate_04_oos_maxdd_le_25pct",
            abs(oos_m["max_drawdown"]) <= 0.25,
            f"{oos_m['max_drawdown']*100:.2f}%",
        ),
        (
            "gate_05_fwd_sharpe_gt_0",
            fwd_m["sharpe"] > 0,
            f"{fwd_m['sharpe']:.3f}",
        ),
        (
            "gate_06_wf_6_8_and_mdd_le_30pct",
            wf_pass_relaxed,
            f"{int(wf_ratio*8)}/8 mdd={wf_mdd*100:.2f}%",
        ),
        (
            "gate_07_median_hold_ge_5d",
            mh >= 5.0 if np.isfinite(mh) else False,
            f"{mh:.1f}d",
        ),
        (
            "gate_08_ir_vs_spy_oos_ge_0_3",
            (not np.isnan(ir)) and ir >= 0.3,
            f"{ir:.4f}",
        ),
        (
            "gate_09_cross_lib_concordance",
            None,  # evaluated separately by cross-lib script
            "deferred (see cross_lib_check.md)",
        ),
        (
            "gate_10_stage2_data_concordance",
            None,
            "N/A — only one data source (Tiingo)",
        ),
        (
            "gate_11_pbo_lt_0_5",
            (pbo_result is not None and pbo_result.pbo < 0.5),
            f"{pbo_result.pbo:.4f}" if pbo_result else "N/A",
        ),
        (
            "gate_12_dsr_p_lt_0_05",
            dsr_res.p_value < 0.05,
            f"{dsr_res.p_value:.6f}",
        ),
        (
            "gate_13_cost_sensitivity_2x_sharpe_gt_1",
            cost2x_m["sharpe"] > 1.0,
            f"{cost2x_m['sharpe']:.3f}",
        ),
    ]

    n_pass = sum(1 for _, p, _ in gates if p is True)
    n_fail = sum(1 for _, p, _ in gates if p is False)
    n_def = sum(1 for _, p, _ in gates if p is None)
    failed = [n for n, p, _ in gates if p is False]
    # Verdict: WINNER = all binding gates pass (gates 2, 3_soft, 4, 5, 6, 7,
    # 8, 11, 12, 13, + boot 1 and 1b). Gate 9 needs separate cross-lib run.
    binding_names = {
        "gate_01_bootstrap_oos_99p9_ci_low_gt_0",
        "gate_01b_bootstrap_full_99p9_ci_low_gt_0",
        "gate_02_oos_sharpe_ge_1_5",
        "gate_03_oos_cagr_ge_13pct_CDI",
        "gate_04_oos_maxdd_le_25pct",
        "gate_05_fwd_sharpe_gt_0",
        "gate_06_wf_6_8_and_mdd_le_30pct",
        "gate_07_median_hold_ge_5d",
        "gate_08_ir_vs_spy_oos_ge_0_3",
        "gate_11_pbo_lt_0_5",
        "gate_12_dsr_p_lt_0_05",
        "gate_13_cost_sensitivity_2x_sharpe_gt_1",
    }
    binding_fail = [
        n for n, p, _ in gates if (n in binding_names and p is False)
    ]
    if not binding_fail:
        verdict = "WINNER (pending cross-lib)"
    elif len(binding_fail) == 1:
        verdict = "PARTIAL"
    else:
        verdict = "FAIL"

    print(f"\n=== GATES ({n_pass} PASS / {n_fail} FAIL / {n_def} DEFERRED) ===")
    for n, p, v in gates:
        mark = "PASS" if p is True else ("FAIL" if p is False else "DEFER")
        print(f"  [{mark}] {n:50s} = {v}")
    print(f"\nFINAL VERDICT: {verdict}")

    # -- Step 10: persist artifacts
    out_pq = OUT_DIR / "daily_returns.parquet"
    pd.DataFrame({"ret": dr}).to_parquet(out_pq)
    cost2x_pq = OUT_DIR / "daily_returns_cost2x.parquet"
    pd.DataFrame({"ret": cost2x.daily_returns.dropna()}).to_parquet(cost2x_pq)

    # Grid config summary
    grid_cfgs = [
        {
            "tag": tag,
            "top_n": GRID[i].top_n,
            "rebalance_days": GRID[i].rebalance_days,
            "use_regime_filter": GRID[i].use_regime_filter,
            "sharpe_full": float(grid_rets[tag].mean() / grid_rets[tag].std(ddof=1) * np.sqrt(TRADING_DAYS))
            if grid_rets[tag].std(ddof=1) > 0
            else 0.0,
        }
        for i, tag in enumerate(grid_rets.keys())
    ]
    (OUT_DIR / "config_grid.csv").write_text(
        "tag,top_n,rebalance_days,use_regime_filter,sharpe_full\n"
        + "\n".join(
            f"{c['tag']},{c['top_n']},{c['rebalance_days']},{c['use_regime_filter']},{c['sharpe_full']:.4f}"
            for c in grid_cfgs
        )
    )

    agg = {
        "phase": "phase_3_6",
        "family": "A_clenow_cross_sectional_momentum",
        "slug": "a_clenow_momentum",
        "produced_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "engine_fix_commit": "7b90a8f",
        "broker_path": "Banco Inter Internacional (US stocks, 15% BR CG tax)",
        "data_source": "Tiingo daily parquets (1695 tickers) + ADV ≥ $50M filter",
        "survivorship_caveat": (
            "Approximated liquid large-cap universe — no full PIT S&P 500 "
            "membership available in repo. Tiingo bulk is mostly listed-today "
            "(some delisted), so results may be modestly upward-biased. "
            "Per [stocks_on_the_move, p.238-239]."
        ),
        "universe_size": len(panel),
        "winner_config": {
            "top_n": WINNER_CFG.top_n,
            "rebalance_days": WINNER_CFG.rebalance_days,
            "use_regime_filter": WINNER_CFG.use_regime_filter,
            "regression_days": WINNER_CFG.regression_days,
            "per_stock_ma_days": WINNER_CFG.per_stock_ma_days,
            "market_ma_days": WINNER_CFG.market_ma_days,
            "gap_threshold": WINNER_CFG.gap_threshold,
            "atr_days": WINNER_CFG.atr_days,
            "atr_risk_factor": WINNER_CFG.atr_risk_factor,
            "spread_one_way_pct": WINNER_CFG.spread_one_way_pct,
            "commission_per_trade": WINNER_CFG.commission_per_trade,
            "tax_rate": WINNER_CFG.tax_rate,
            "adv_usd_floor": WINNER_CFG.adv_usd_floor,
        },
        "window": {
            "start": str(dr.index[0].date()),
            "end": str(dr.index[-1].date()),
            "n_bars": int(len(dr)),
        },
        "splits": {
            "IS": is_m,
            "OOS": oos_m,
            "FWD": fwd_m,
            "FULL": full_m,
            "SPY_OOS": spy_m,
        },
        "walk_forward": {
            "n_windows": 8,
            "profitable_ratio": wf_ratio,
            "max_window_drawdown": wf_mdd,
            "pass": wf_pass_relaxed,
            "mdd_cap": wf_mdd_cap,
        },
        "pbo": {
            "value": pbo_result.pbo if pbo_result else None,
            "n_blocks": pbo_result.n_blocks if pbo_result else None,
            "n_combinations": pbo_result.n_combinations if pbo_result else None,
            "pass": (pbo_result.pbo < 0.5) if pbo_result else None,
        },
        "dsr": {
            "dsr": dsr_res.dsr,
            "p_value": dsr_res.p_value,
            "observed_sharpe": dsr_res.observed_sharpe,
            "n_trials": dsr_res.n_trials,
            "pass": dsr_res.p_value < 0.05,
        },
        "bootstrap_oos": {"ci_low": oos_lo, "ci_high": oos_hi, "pass": oos_lo > 0},
        "bootstrap_full": {"ci_low": full_lo, "ci_high": full_hi, "pass": full_lo > 0},
        "ir_vs_spy_oos": ir,
        "median_hold_days": mh,
        "n_hold_entries": len(winner.hold_lengths),
        "cum_cost_pct_winner": winner.cum_cost_pct,
        "cum_tax_pct_winner": winner.cum_tax_pct,
        "cost_sensitivity_2x": cost2x_m,
        "gates": [{"name": n, "pass": p, "value": v} for n, p, v in gates],
        "verdict": verdict,
        "failed_gates": failed,
        "grid_configs": grid_cfgs,
        # Structured keys matching brief §Output-spec-5:
        "is_sharpe": is_m["sharpe"],
        "is_cagr": is_m["cagr"],
        "oos_sharpe": oos_m["sharpe"],
        "oos_cagr": oos_m["cagr"],
        "oos_mdd": oos_m["max_drawdown"],
        "fwd_sharpe": fwd_m["sharpe"],
        "fwd_cagr": fwd_m["cagr"],
        "wf_profitable_windows": int(wf_ratio * 8),
        "wf_max_dd": wf_mdd,
        "cross_lib_max_delta_cagr": None,  # filled by cross_lib runner
        "bootstrap_oos_ci_low": oos_lo,
        "bootstrap_full_ci_low": full_lo,
        "cost_x2_sharpe": cost2x_m["sharpe"],
    }

    out_json = OUT_DIR / "AGGREGATE.json"
    tmp = out_json.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(agg, indent=2, default=float))
    tmp.replace(out_json)
    print(f"\n[write] {out_json}")
    print(f"[write] {out_pq}")
    print(f"[write] {OUT_DIR / 'config_grid.csv'}")
    print(f"\nTotal runtime: {time.time()-t0:.1f}s")


if __name__ == "__main__":
    main()

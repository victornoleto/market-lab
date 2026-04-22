"""Phase 3.6 Family D — Chan MR pairs (non-Kalman) honest 13-gate pipeline.

Loads 5 sector-peer ETF pairs from Tiingo, runs rolling-OLS + EG-gate
cointegration pair trading, splits into IS/OOS/FWD, evaluates 13 gates
per plan §5 with user-locked relaxations.

Execution shape
---------------
1. Load the 5 ETF pairs (XLE/USO, TLT/IEF, HYG/LQD, GLD/SLV, XLU/XLP).
2. Run winner config (lookback=126, entry_z=2.0, exit_z=0.0, stop_z=4.0).
3. IS/OOS/FWD split metrics + bootstrap CI + WF + IR + cost×2.
4. Grid run of 5+ sibling configs for CPCV/PBO + DSR.
5. Write AGGREGATE.md / AGGREGATE.json / daily_returns.parquet.

Citations
---------
* Engle-Granger cointegration: [algo_trading_chan, p.51-54, p.42-43].
* Rolling OLS hedge ratio: [algo_trading_chan, ch.3 p.65-80].
* Z-score bands: [algo_trading_chan, p.71-73, p.94].
* Bootstrap CI / WF / PBO / DSR: [advances_fin_ml, p.196-211, p.273-275, ch.11].
* Look-ahead convention: [advances_fin_ml, p.31-34].
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
from ai_trade.backtest.strategies.phase3_6_d_chan_mr_pairs import (  # noqa: E402
    ChanPairsConfig,
    DEFAULT_PAIRS,
    simulate_chan_pairs,
)
from ai_trade.backtest.validation.dsr import dsr as dsr_metric  # noqa: E402
from ai_trade.backtest.validation.pbo import pbo as cscv_pbo  # noqa: E402

OUT_DIR = ROOT / "reports/phase_3_6/d_chan_mr_pairs"
OUT_DIR.mkdir(parents=True, exist_ok=True)
TIINGO_DAILY = ROOT / "data/tiingo/daily/prices"

IS_RANGE = ("2001-05-14", "2017-12-31")
OOS_RANGE = ("2018-01-01", "2023-12-31")
FWD_RANGE = ("2024-01-01", "2026-04-14")
CDI_FLOOR = 0.13

# Tickers referenced by DEFAULT_PAIRS
TICKERS = ["XLE", "USO", "TLT", "IEF", "HYG", "LQD", "GLD", "SLV", "XLU", "XLP"]

# Winner config baseline
WINNER_CFG = ChanPairsConfig(
    lookback=126,
    entry_z=2.0,
    exit_z=0.0,
    stop_z=4.0,
    coint_pvalue_gate=0.10,
)

# Grid for CPCV/PBO + DSR (≥5 configs). We sweep lookback, entry_z,
# exit_z, stop_z — each independently varies one dim.
GRID = [
    ChanPairsConfig(lookback=60,  entry_z=2.0, exit_z=0.0, stop_z=4.0),
    ChanPairsConfig(lookback=126, entry_z=2.0, exit_z=0.0, stop_z=4.0),  # winner
    ChanPairsConfig(lookback=252, entry_z=2.0, exit_z=0.0, stop_z=4.0),
    ChanPairsConfig(lookback=126, entry_z=1.5, exit_z=0.0, stop_z=4.0),
    ChanPairsConfig(lookback=126, entry_z=2.5, exit_z=0.5, stop_z=4.0),
    ChanPairsConfig(lookback=126, entry_z=2.0, exit_z=0.5, stop_z=3.5),
]


def _load_tiingo(ticker: str) -> pd.DataFrame:
    fp = TIINGO_DAILY / f"{ticker}.parquet"
    df = pd.read_parquet(fp)
    df.index = pd.DatetimeIndex(df.index).normalize()
    return df


def _load_pair_panel() -> tuple[dict[str, pd.Series], dict[str, pd.Series]]:
    prices: dict[str, pd.Series] = {}
    returns: dict[str, pd.Series] = {}
    for t in TICKERS:
        df = _load_tiingo(t)
        prices[t] = df["adj_close"].astype(float)
        returns[t] = prices[t].pct_change()
    return prices, returns


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


def _config_tag(cfg: ChanPairsConfig) -> str:
    return (
        f"lb{cfg.lookback}_enter{cfg.entry_z}_exit{cfg.exit_z}_stop{cfg.stop_z}"
    )


def main() -> None:
    t0 = time.time()
    print("=" * 80)
    print("Phase 3.6 Family D — Chan MR pairs (non-Kalman) honest pipeline")
    print("=" * 80)

    prices, returns = _load_pair_panel()
    for t in TICKERS:
        s = prices[t].dropna()
        print(f"  [data] {t}: {len(s)} bars {s.index[0].date()} -> {s.index[-1].date()}")

    # -- Step 1: winner config
    print(f"\n[winner] {_config_tag(WINNER_CFG)}")
    ts = time.time()
    winner = simulate_chan_pairs(prices, returns, WINNER_CFG, pairs=DEFAULT_PAIRS)
    print(f"[winner] done in {time.time()-ts:.1f}s")
    dr = winner.daily_returns.dropna()
    print(
        f"[winner] bars={len(dr)} span={dr.index[0].date()}->{dr.index[-1].date()} "
        f"cum_cost={winner.cum_cost_pct:.4f}"
    )
    print(f"[winner] trades/pair={winner.n_trades_per_pair}")
    print(f"[winner] coint_bars/pair={winner.n_coint_bars_per_pair}")
    print(f"[winner] total_bars/pair={winner.total_bars_per_pair}")

    is_ret = _slice(dr, *IS_RANGE)
    oos_ret = _slice(dr, *OOS_RANGE)
    fwd_ret = _slice(dr, *FWD_RANGE)
    is_m = _mdict("IS", is_ret)
    oos_m = _mdict("OOS", oos_ret)
    fwd_m = _mdict("FWD", fwd_ret)
    full_m = _mdict("FULL", dr)
    print(
        f"[IS]  S={is_m['sharpe']:.3f} CAGR={is_m['cagr']*100:.2f}% MDD={is_m['max_drawdown']*100:.2f}%"
    )
    print(
        f"[OOS] S={oos_m['sharpe']:.3f} CAGR={oos_m['cagr']*100:.2f}% MDD={oos_m['max_drawdown']*100:.2f}%"
    )
    print(
        f"[FWD] S={fwd_m['sharpe']:.3f} CAGR={fwd_m['cagr']*100:.2f}% MDD={fwd_m['max_drawdown']*100:.2f}%"
    )

    # -- Step 2: Walk-forward
    if len(dr) >= 8:
        wf_ratio, wf_mdd, wf_pass = walk_forward_verdict_from_returns(
            dr, n_windows=8, max_drawdown_cap=0.30
        )
    else:
        wf_ratio, wf_mdd, wf_pass = 0.0, 0.0, False
    print(f"[WF]  ratio={wf_ratio:.3f} ({int(wf_ratio*8)}/8) mdd={wf_mdd*100:.2f}% pass={wf_pass}")

    # -- Step 3: Bootstrap
    try:
        oos_lo, oos_hi = bootstrap_sharpe_ci(
            oos_ret, alpha=0.001, n_resamples=2000, block_mean=5, seed=42
        )
    except Exception as e:
        print(f"[BOOT] OOS bootstrap failed: {e}")
        oos_lo, oos_hi = float("nan"), float("nan")
    try:
        full_lo, full_hi = bootstrap_sharpe_ci(
            dr, alpha=0.001, n_resamples=2000, block_mean=5, seed=42
        )
    except Exception as e:
        print(f"[BOOT] FULL bootstrap failed: {e}")
        full_lo, full_hi = float("nan"), float("nan")
    print(f"[BOOT] OOS 99.9% CI [{oos_lo:.4f}, {oos_hi:.4f}]")
    print(f"[BOOT] FULL 99.9% CI [{full_lo:.4f}, {full_hi:.4f}]")

    # -- Step 4: IR vs SPY
    spy_df = _load_tiingo("SPY")
    spy_ret_full = spy_df["adj_close"].astype(float).pct_change().dropna()
    spy_ret_full.index = pd.DatetimeIndex(spy_ret_full.index).normalize()
    dr.index = pd.DatetimeIndex(dr.index).normalize()
    oos_ret.index = pd.DatetimeIndex(oos_ret.index).normalize()
    spy_oos = _slice(spy_ret_full, *OOS_RANGE)
    spy_m = _mdict("SPY_OOS", spy_oos)
    ir = _ir_vs_spy(oos_ret, spy_oos)
    print(f"[IR] vs SPY OOS={ir:.4f}  (SPY OOS Sharpe={spy_m['sharpe']:.3f} CAGR={spy_m['cagr']*100:.2f}%)")

    # -- Step 5: Median hold
    mh = winner.median_hold_days()
    n_trades_total = sum(winner.n_trades_per_pair.values())
    print(f"[HOLD] median hold = {mh:.1f}d (n_total_trades={n_trades_total})")

    # -- Step 6: Cost×2 sensitivity
    cost2x_cfg = ChanPairsConfig(
        lookback=WINNER_CFG.lookback,
        entry_z=WINNER_CFG.entry_z,
        exit_z=WINNER_CFG.exit_z,
        stop_z=WINNER_CFG.stop_z,
        coint_pvalue_gate=WINNER_CFG.coint_pvalue_gate,
        per_pair_gross_pct=WINNER_CFG.per_pair_gross_pct,
        spread_one_way_pct=WINNER_CFG.spread_one_way_pct * 2.0,
        commission_per_trade_pct=WINNER_CFG.commission_per_trade_pct * 2.0,
        swap_per_night_pct=WINNER_CFG.swap_per_night_pct * 2.0,
        tax_rate=WINNER_CFG.tax_rate,
    )
    ts = time.time()
    print(f"\n[cost2x] spread={cost2x_cfg.spread_one_way_pct:.4f} "
          f"comm={cost2x_cfg.commission_per_trade_pct:.6f} "
          f"swap={cost2x_cfg.swap_per_night_pct:.4f}")
    cost2x = simulate_chan_pairs(prices, returns, cost2x_cfg, pairs=DEFAULT_PAIRS)
    print(f"[cost2x] done in {time.time()-ts:.1f}s")
    cost2x_oos = _slice(cost2x.daily_returns.dropna(), *OOS_RANGE)
    cost2x_m = _mdict("OOS_2x", cost2x_oos)
    print(f"[COST×2] OOS Sharpe={cost2x_m['sharpe']:.3f} CAGR={cost2x_m['cagr']*100:.2f}%")

    # -- Step 7: Grid sweep for CPCV/PBO + DSR
    print(f"\n[grid] running {len(GRID)} sibling configs...")
    grid_rets: dict[str, pd.Series] = {}
    winner_tag = _config_tag(WINNER_CFG)
    for idx_g, cfg in enumerate(GRID):
        tag = _config_tag(cfg)
        if tag == winner_tag:
            grid_rets[tag] = winner.daily_returns
            print(f"  [grid {idx_g+1}/{len(GRID)}] {tag} (reuse winner)")
            continue
        ts = time.time()
        r = simulate_chan_pairs(prices, returns, cfg, pairs=DEFAULT_PAIRS)
        full_s = r.sharpe()
        print(f"  [grid {idx_g+1}/{len(GRID)}] {tag} done in {time.time()-ts:.1f}s  S_full={full_s:.3f}")
        grid_rets[tag] = r.daily_returns

    grid_df = pd.concat(grid_rets, axis=1).dropna(how="any")
    print(f"[grid] aligned matrix shape: {grid_df.shape}")
    if grid_df.shape[0] >= 100 and grid_df.shape[1] >= 2:
        pbo_result = cscv_pbo(grid_df.to_numpy(), n_blocks=10)
        print(
            f"[PBO] value={pbo_result.pbo:.4f} n_combinations={pbo_result.n_combinations}"
        )
    else:
        pbo_result = None
        print("[PBO] skipped — insufficient grid")

    dsr_res = dsr_metric(oos_ret.dropna().to_numpy(dtype=float), n_trials=len(GRID))
    print(f"[DSR] p_value={dsr_res.p_value:.6f} obs_SR={dsr_res.observed_sharpe:.4f}")

    # -- Step 8: 13-gate evaluation
    gate_3_hard = oos_m["cagr"] >= 0.30
    gate_3_soft = oos_m["cagr"] >= CDI_FLOOR
    wf_mdd_cap = 0.30
    wf_ratio_ok = wf_ratio >= 6 / 8
    wf_mdd_ok = wf_mdd <= wf_mdd_cap
    wf_pass_relaxed = wf_ratio_ok and wf_mdd_ok

    oos_ci_pass = (not np.isnan(oos_lo)) and oos_lo > 0
    full_ci_pass = (not np.isnan(full_lo)) and full_lo > 0

    gates = [
        ("gate_01_bootstrap_oos_99p9_ci_low_gt_0", bool(oos_ci_pass), f"{oos_lo:.4f}"),
        ("gate_01b_bootstrap_full_99p9_ci_low_gt_0", bool(full_ci_pass), f"{full_lo:.4f}"),
        ("gate_02_oos_sharpe_ge_1_5", bool(oos_m["sharpe"] >= 1.5), f"{oos_m['sharpe']:.3f}"),
        ("gate_03_oos_cagr_ge_13pct_CDI", bool(gate_3_soft), f"{oos_m['cagr']*100:.2f}%"),
        ("gate_03_target_oos_cagr_ge_30pct", bool(gate_3_hard), f"{oos_m['cagr']*100:.2f}%"),
        ("gate_04_oos_maxdd_le_25pct", bool(abs(oos_m["max_drawdown"]) <= 0.25),
         f"{oos_m['max_drawdown']*100:.2f}%"),
        ("gate_05_fwd_sharpe_gt_0", bool(fwd_m["sharpe"] > 0), f"{fwd_m['sharpe']:.3f}"),
        ("gate_06_wf_6_8_and_mdd_le_30pct", bool(wf_pass_relaxed),
         f"{int(wf_ratio*8)}/8 mdd={wf_mdd*100:.2f}%"),
        ("gate_07_median_hold_ge_5d", bool((mh >= 5.0) if np.isfinite(mh) else False),
         f"{mh:.1f}d"),
        ("gate_08_ir_vs_spy_oos_ge_0_3",
         bool((not np.isnan(ir)) and ir >= 0.3), f"{ir:.4f}"),
        ("gate_09_cross_lib_concordance", None, "deferred (see cross_lib_check.md)"),
        ("gate_10_stage2_data_concordance", None,
         "N/A — only one data source (Tiingo)"),
        ("gate_11_pbo_lt_0_5",
         bool(pbo_result is not None and pbo_result.pbo < 0.5),
         f"{pbo_result.pbo:.4f}" if pbo_result else "N/A"),
        ("gate_12_dsr_p_lt_0_05", bool(dsr_res.p_value < 0.05), f"{dsr_res.p_value:.6f}"),
        ("gate_13_cost_sensitivity_2x_sharpe_gt_1", bool(cost2x_m["sharpe"] > 1.0),
         f"{cost2x_m['sharpe']:.3f}"),
    ]
    n_pass = sum(1 for _, p, _ in gates if p is True)
    n_fail = sum(1 for _, p, _ in gates if p is False)
    n_def = sum(1 for _, p, _ in gates if p is None)
    failed = [n for n, p, _ in gates if p is False]

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
    binding_fail = [n for n, p, _ in gates if (n in binding_names and p is False)]
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

    # -- Step 9: persist artifacts
    pd.DataFrame({"ret": dr}).to_parquet(OUT_DIR / "daily_returns.parquet")
    pd.DataFrame({"ret": cost2x.daily_returns.dropna()}).to_parquet(
        OUT_DIR / "daily_returns_cost2x.parquet"
    )

    grid_cfgs = []
    for i, cfg in enumerate(GRID):
        tag = _config_tag(cfg)
        s_full = 0.0
        if tag in grid_rets and grid_rets[tag].std(ddof=1) > 0:
            s_full = float(
                grid_rets[tag].mean() / grid_rets[tag].std(ddof=1)
                * np.sqrt(TRADING_DAYS)
            )
        grid_cfgs.append(
            {
                "tag": tag,
                "lookback": cfg.lookback,
                "entry_z": cfg.entry_z,
                "exit_z": cfg.exit_z,
                "stop_z": cfg.stop_z,
                "sharpe_full": s_full,
            }
        )
    (OUT_DIR / "config_grid.csv").write_text(
        "tag,lookback,entry_z,exit_z,stop_z,sharpe_full\n"
        + "\n".join(
            f"{c['tag']},{c['lookback']},{c['entry_z']},{c['exit_z']},"
            f"{c['stop_z']},{c['sharpe_full']:.4f}"
            for c in grid_cfgs
        )
    )

    # Stocks inception-aware caveat: summarize per-pair bar counts + coint %.
    pair_stats = []
    for p_spec in DEFAULT_PAIRS:
        label = p_spec.label
        tot = winner.total_bars_per_pair.get(label, 0)
        coint = winner.n_coint_bars_per_pair.get(label, 0)
        tr = winner.n_trades_per_pair.get(label, 0)
        pair_stats.append(
            {
                "label": label,
                "y": p_spec.y,
                "x": p_spec.x,
                "total_bars": tot,
                "coint_bars": coint,
                "coint_pct": (coint / tot) if tot > 0 else 0.0,
                "trades": tr,
            }
        )

    agg = {
        "phase": "phase_3_6",
        "family": "D_chan_mr_pairs_non_kalman",
        "slug": "d_chan_mr_pairs",
        "produced_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "engine_fix_commit": "7b90a8f",
        "broker_path": "Pepperstone Razor CFD (plan §3.1) — spread 5bps/leg, "
                       "commission $0.35/100k, swap −2bps/night/leg, no BR tax",
        "data_source": "Tiingo daily parquets (5 ETF pairs; HYG inception 2007-04-11)",
        "survivorship_caveat": (
            "All 5 pairs are liquid US sector ETFs that remained tradable "
            "through the full 2007-2026 span. IS effective start is "
            "2007-04-11 (HYG inception) — the 2001-2017 IS is "
            "truncated ~6 years on the left. This is documented and not "
            "silently backfilled. Per [algo_trading_chan, p.88-89] the "
            "ETF pair space is known to compress edge over time as "
            "institutional arbitrage grows."
        ),
        "pair_universe": [
            {"y": p.y, "x": p.x, "label": p.label} for p in DEFAULT_PAIRS
        ],
        "pair_statistics_winner_cfg": pair_stats,
        "winner_config": {
            "lookback": WINNER_CFG.lookback,
            "entry_z": WINNER_CFG.entry_z,
            "exit_z": WINNER_CFG.exit_z,
            "stop_z": WINNER_CFG.stop_z,
            "coint_pvalue_gate": WINNER_CFG.coint_pvalue_gate,
            "per_pair_gross_pct": WINNER_CFG.per_pair_gross_pct,
            "spread_one_way_pct": WINNER_CFG.spread_one_way_pct,
            "commission_per_trade_pct": WINNER_CFG.commission_per_trade_pct,
            "swap_per_night_pct": WINNER_CFG.swap_per_night_pct,
            "tax_rate": WINNER_CFG.tax_rate,
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
        "bootstrap_oos": {"ci_low": oos_lo, "ci_high": oos_hi, "pass": oos_ci_pass},
        "bootstrap_full": {"ci_low": full_lo, "ci_high": full_hi, "pass": full_ci_pass},
        "ir_vs_spy_oos": ir,
        "median_hold_days": mh,
        "n_trades_total_winner": n_trades_total,
        "n_trades_per_pair": winner.n_trades_per_pair,
        "cum_cost_pct_winner": winner.cum_cost_pct,
        "cum_tax_pct_winner": winner.cum_tax_pct,
        "cost_sensitivity_2x": cost2x_m,
        "gates": [{"name": n, "pass": p, "value": v} for n, p, v in gates],
        "verdict": verdict,
        "failed_gates": failed,
        "grid_configs": grid_cfgs,
        # Structured keys matching Family A schema:
        "is_sharpe": is_m["sharpe"],
        "is_cagr": is_m["cagr"],
        "oos_sharpe": oos_m["sharpe"],
        "oos_cagr": oos_m["cagr"],
        "oos_mdd": oos_m["max_drawdown"],
        "fwd_sharpe": fwd_m["sharpe"],
        "fwd_cagr": fwd_m["cagr"],
        "wf_profitable_windows": int(wf_ratio * 8),
        "wf_max_dd": wf_mdd,
        "cross_lib_max_delta_cagr": None,
        "bootstrap_oos_ci_low": oos_lo,
        "bootstrap_full_ci_low": full_lo,
        "cost_x2_sharpe": cost2x_m["sharpe"],
    }
    out_json = OUT_DIR / "AGGREGATE.json"
    tmp = out_json.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(agg, indent=2, default=float))
    tmp.replace(out_json)
    print(f"\n[write] {out_json}")
    print(f"[write] {OUT_DIR / 'daily_returns.parquet'}")
    print(f"[write] {OUT_DIR / 'config_grid.csv'}")
    print(f"\nTotal runtime: {time.time()-t0:.1f}s")


if __name__ == "__main__":
    main()

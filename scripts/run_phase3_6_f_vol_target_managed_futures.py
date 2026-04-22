"""Phase 3.6 Family F — Vol-targeting managed-futures basket honest pipeline.

Loads the Tiingo 6-asset MF-proxy panel (SPY, TLT, GLD, USO, EFA, IEF),
runs Carver EWMAC vol-targeted sizing under Pepperstone Razor retail
costs, emits a 13-gate AGGREGATE.{md,json} per Phase 3.6 plan §5 with
user-locked relaxations.

Differentiation from V2-L1 TSMOM (mandatory)
--------------------------------------------
* Signal: Carver continuous EWMAC (not V2-L1 binary past-return).
* Vol target: portfolio-level with IDM (not per-leg).
* Universe: 6 multi-asset-class ETFs (equities/bonds/commodities),
  not 30-asset FX-dominant mix.
See strategy module docstring for full rationale.

Citations
---------
* EWMAC + vol targeting: [systematic_trading, p.112-119, p.137-148,
  p.282-285].
* Lookahead audit: [advances_fin_ml, p.31-34].
* Bootstrap / PBO / DSR: [advances_fin_ml, p.196-211, p.273-275].
* Walk-forward 6/8: [advances_fin_ml, ch.11].
* Pepperstone cost model: plan §3.1.
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
from ai_trade.backtest.strategies.phase3_6_f_vol_target_managed_futures import (  # noqa: E402
    EWMAC_SCALARS,
    VolTargetMFConfig,
    simulate_vol_target_mf,
)
from ai_trade.backtest.validation.dsr import dsr as dsr_metric  # noqa: E402
from ai_trade.backtest.validation.pbo import pbo as cscv_pbo  # noqa: E402

OUT_DIR = ROOT / "reports/phase_3_6/f_vol_target_managed_futures"
OUT_DIR.mkdir(parents=True, exist_ok=True)
TIINGO_DAILY = ROOT / "data/tiingo/daily/prices"

IS_RANGE = ("2001-05-14", "2017-12-31")
OOS_RANGE = ("2018-01-01", "2023-12-31")
FWD_RANGE = ("2024-01-01", "2026-04-14")
CDI_FLOOR = 0.13

# Universe: 6-asset multi-class managed-futures proxy. Dynamic inclusion
# via active-mask — each asset joins the basket when it has sufficient
# history. Full panel stabilizes ~2006-04-10 (USO inception).
UNIVERSE = ("SPY", "TLT", "GLD", "USO", "EFA", "IEF")

# Winner config per plan brief: EWMAC 16:64 (swing-horizon trend rule),
# 15% portfolio vol target, 10d rebalance cadence.
WINNER_CFG = VolTargetMFConfig(
    fast_span=16,
    slow_span=64,
    target_vol_annual=0.15,
    rebalance_days=10,
)

# Grid for CPCV/PBO (16 cells: 4 EWMAC pairs × 2 vol targets × 2 cadences).
# Winner cell included; other cells exercise all three grid axes.
GRID: list[VolTargetMFConfig] = [
    VolTargetMFConfig(fast_span=f, slow_span=s, target_vol_annual=v, rebalance_days=r)
    for (f, s) in [(8, 32), (16, 64), (32, 128), (64, 256)]
    for v in (0.10, 0.15)
    for r in (10, 20)
]


def _load_tiingo(ticker: str) -> pd.DataFrame:
    fp = TIINGO_DAILY / f"{ticker}.parquet"
    df = pd.read_parquet(fp)
    df.index = pd.DatetimeIndex(df.index).normalize()
    return df


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


def _ir_vs_spy(port: pd.Series, spy: pd.Series) -> float:
    common = port.index.intersection(spy.index)
    if len(common) < 20:
        return float("nan")
    excess = port.loc[common] - spy.loc[common]
    mu, sd = float(excess.mean()), float(excess.std(ddof=1))
    if sd <= 0:
        return 0.0
    return mu / sd * np.sqrt(TRADING_DAYS)


def _cfg_tag(cfg: VolTargetMFConfig) -> str:
    return (
        f"ewmac{cfg.fast_span}_{cfg.slow_span}_"
        f"vt{int(cfg.target_vol_annual * 100)}_"
        f"rb{cfg.rebalance_days}"
    )


def main() -> None:
    t0 = time.time()
    print("=" * 80)
    print("Phase 3.6 Family F — Vol-targeting MF basket honest 13-gate pipeline")
    print("=" * 80)

    # -- Step 1: panel
    print(f"[data] loading universe: {UNIVERSE}")
    panel = {t: _load_tiingo(t) for t in UNIVERSE}
    for t in UNIVERSE:
        d = panel[t]
        print(f"  {t:6s} {d.index[0].date()} -> {d.index[-1].date()}  rows={len(d)}")

    # -- Step 2: winner config simulation
    print(f"\n[winner] running {_cfg_tag(WINNER_CFG)}...")
    ts = time.time()
    winner = simulate_vol_target_mf(panel, WINNER_CFG)
    print(f"[winner] done in {time.time()-ts:.1f}s")
    dr = winner.daily_returns.dropna()
    print(
        f"[winner] bars={len(dr)} span={dr.index[0].date()}→{dr.index[-1].date()} "
        f"avg_n_active={winner.active_count.mean():.2f} avg_gross="
        f"{winner.weights.abs().sum(axis=1).mean():.3f}"
    )
    print(
        f"[winner] cum_cost={winner.cum_cost_pct*100:.1f}% "
        f"cum_swap={winner.cum_swap_pct*100:.1f}% "
        f"cum_comm={winner.cum_commission_pct*100:.2f}% "
        f"n_rebal={winner.n_rebalances}"
    )

    is_ret = _slice(dr, *IS_RANGE)
    oos_ret = _slice(dr, *OOS_RANGE)
    fwd_ret = _slice(dr, *FWD_RANGE)
    full_ret = dr
    is_m = _mdict("IS", is_ret)
    oos_m = _mdict("OOS", oos_ret)
    fwd_m = _mdict("FWD", fwd_ret)
    full_m = _mdict("FULL", full_ret)
    print(
        f"[IS]  S={is_m['sharpe']:.3f} CAGR={is_m['cagr']*100:+.2f}% MDD={is_m['max_drawdown']*100:.2f}%"
    )
    print(
        f"[OOS] S={oos_m['sharpe']:.3f} CAGR={oos_m['cagr']*100:+.2f}% MDD={oos_m['max_drawdown']*100:.2f}%"
    )
    print(
        f"[FWD] S={fwd_m['sharpe']:.3f} CAGR={fwd_m['cagr']*100:+.2f}% MDD={fwd_m['max_drawdown']*100:.2f}%"
    )

    # -- Step 3: WF
    if len(full_ret) >= 8:
        wf_ratio, wf_mdd, wf_pass = walk_forward_verdict_from_returns(
            full_ret, n_windows=8, max_drawdown_cap=0.30
        )
    else:
        wf_ratio, wf_mdd, wf_pass = 0.0, 0.0, False
    print(
        f"[WF]  ratio={wf_ratio:.3f} ({int(wf_ratio*8)}/8) mdd={wf_mdd*100:.2f}% pass={wf_pass}"
    )

    # -- Step 4: Bootstrap CIs (99.9%, block_mean=5).
    oos_lo, oos_hi = bootstrap_sharpe_ci(
        oos_ret, alpha=0.001, n_resamples=2000, block_mean=5, seed=42
    )
    full_lo, full_hi = bootstrap_sharpe_ci(
        full_ret, alpha=0.001, n_resamples=2000, block_mean=5, seed=42
    )
    print(f"[BOOT] OOS 99.9% CI [{oos_lo:.4f}, {oos_hi:.4f}]")
    print(f"[BOOT] FULL 99.9% CI [{full_lo:.4f}, {full_hi:.4f}]")

    # -- Step 5: IR vs SPY
    spy_df = panel["SPY"]
    spy_ret_full = spy_df["adj_close"].pct_change(fill_method=None).dropna()
    spy_ret_full.index = pd.DatetimeIndex(spy_ret_full.index).normalize()
    spy_oos = _slice(spy_ret_full, *OOS_RANGE)
    spy_m = _mdict("SPY_OOS", spy_oos)
    ir = _ir_vs_spy(oos_ret, spy_oos)
    print(
        f"[IR]  vs SPY OOS={ir:.4f}  (SPY OOS Sharpe={spy_m['sharpe']:.3f} "
        f"CAGR={spy_m['cagr']*100:.2f}%)"
    )

    # -- Step 6: median hold
    mh = winner.median_hold_days()
    print(f"[HOLD] median hold = {mh:.1f}d (n_segments={len(winner.hold_lengths)})")

    # -- Step 7: cost×2 sensitivity
    cost2x_spread = {
        k: v * 2.0 for k, v in WINNER_CFG.spread_one_way.items()
    }
    cost2x_cfg = VolTargetMFConfig(
        fast_span=WINNER_CFG.fast_span,
        slow_span=WINNER_CFG.slow_span,
        target_vol_annual=WINNER_CFG.target_vol_annual,
        rebalance_days=WINNER_CFG.rebalance_days,
        sigma_ewma_span=WINNER_CFG.sigma_ewma_span,
        inertia_frac=WINNER_CFG.inertia_frac,
        max_per_leg=WINNER_CFG.max_per_leg,
        max_gross_leverage=WINNER_CFG.max_gross_leverage,
        idm_cap=WINNER_CFG.idm_cap,
        min_active_assets=WINNER_CFG.min_active_assets,
        forecast_cap=WINNER_CFG.forecast_cap,
        spread_one_way=cost2x_spread,
        commission_round_trip=WINNER_CFG.commission_round_trip * 2.0,
        swap_daily_long=WINNER_CFG.swap_daily_long * 2.0,
        swap_daily_short=WINNER_CFG.swap_daily_short * 2.0,
        tax_rate=WINNER_CFG.tax_rate,
    )
    print(f"\n[cost2x] running cost×2 config...")
    ts = time.time()
    cost2x = simulate_vol_target_mf(panel, cost2x_cfg)
    print(f"[cost2x] done in {time.time()-ts:.1f}s")
    cost2x_oos = _slice(cost2x.daily_returns.dropna(), *OOS_RANGE)
    cost2x_m = _mdict("OOS_2x", cost2x_oos)
    print(
        f"[COST×2] OOS Sharpe={cost2x_m['sharpe']:.3f} CAGR={cost2x_m['cagr']*100:+.2f}%"
    )

    # -- Step 8: GRID run for CPCV/PBO + DSR
    print(f"\n[grid] running {len(GRID)} sibling configs for PBO/DSR...")
    grid_rets: dict[str, pd.Series] = {}
    for idx_g, cfg in enumerate(GRID):
        tag = _cfg_tag(cfg)
        if (
            cfg.fast_span == WINNER_CFG.fast_span
            and cfg.slow_span == WINNER_CFG.slow_span
            and abs(cfg.target_vol_annual - WINNER_CFG.target_vol_annual) < 1e-9
            and cfg.rebalance_days == WINNER_CFG.rebalance_days
        ):
            grid_rets[tag] = winner.daily_returns
            print(f"  [grid {idx_g+1}/{len(GRID)}] {tag} (reuse winner)")
            continue
        ts = time.time()
        r = simulate_vol_target_mf(panel, cfg)
        s_full = r.sharpe()
        print(
            f"  [grid {idx_g+1}/{len(GRID)}] {tag} done in {time.time()-ts:.1f}s "
            f"S_full={s_full:.3f}"
        )
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

    # -- Step 9: gates
    gate_3_hard = oos_m["cagr"] >= 0.30
    gate_3_soft = oos_m["cagr"] >= CDI_FLOOR
    wf_mdd_cap = 0.30
    wf_ratio_ok = wf_ratio >= 6 / 8
    wf_mdd_ok = wf_mdd <= wf_mdd_cap
    wf_pass_relaxed = wf_ratio_ok and wf_mdd_ok

    gates = [
        ("gate_01_bootstrap_oos_99p9_ci_low_gt_0", bool(oos_lo > 0), f"{oos_lo:.4f}"),
        ("gate_01b_bootstrap_full_99p9_ci_low_gt_0", bool(full_lo > 0), f"{full_lo:.4f}"),
        ("gate_02_oos_sharpe_ge_1_5", bool(oos_m["sharpe"] >= 1.5), f"{oos_m['sharpe']:.3f}"),
        ("gate_03_oos_cagr_ge_13pct_CDI", bool(gate_3_soft), f"{oos_m['cagr']*100:+.2f}%"),
        ("gate_03_target_oos_cagr_ge_30pct", bool(gate_3_hard), f"{oos_m['cagr']*100:+.2f}%"),
        (
            "gate_04_oos_maxdd_le_25pct",
            bool(abs(oos_m["max_drawdown"]) <= 0.25),
            f"{oos_m['max_drawdown']*100:.2f}%",
        ),
        ("gate_05_fwd_sharpe_gt_0", bool(fwd_m["sharpe"] > 0), f"{fwd_m['sharpe']:.3f}"),
        (
            "gate_06_wf_6_8_and_mdd_le_30pct",
            bool(wf_pass_relaxed),
            f"{int(wf_ratio*8)}/8 mdd={wf_mdd*100:.2f}%",
        ),
        (
            "gate_07_median_hold_ge_5d",
            bool(mh >= 5.0) if np.isfinite(mh) else False,
            f"{mh:.1f}d",
        ),
        (
            "gate_08_ir_vs_spy_oos_ge_0_3",
            bool((not np.isnan(ir)) and ir >= 0.3),
            f"{ir:.4f}",
        ),
        (
            "gate_09_cross_lib_concordance",
            None,
            "deferred (see cross_lib_check.md)",
        ),
        (
            "gate_10_stage2_data_concordance",
            None,
            "N/A — only one data source (Tiingo)",
        ),
        (
            "gate_11_pbo_lt_0_5",
            bool(pbo_result is not None and pbo_result.pbo < 0.5),
            f"{pbo_result.pbo:.4f}" if pbo_result else "N/A",
        ),
        (
            "gate_12_dsr_p_lt_0_05",
            bool(dsr_res.p_value < 0.05),
            f"{dsr_res.p_value:.6f}",
        ),
        (
            "gate_13_cost_sensitivity_2x_sharpe_gt_1",
            bool(cost2x_m["sharpe"] > 1.0),
            f"{cost2x_m['sharpe']:.3f}",
        ),
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

    # -- Step 10: persist artifacts
    out_pq = OUT_DIR / "daily_returns.parquet"
    pd.DataFrame({"ret": dr}).to_parquet(out_pq)
    cost2x_pq = OUT_DIR / "daily_returns_cost2x.parquet"
    pd.DataFrame({"ret": cost2x.daily_returns.dropna()}).to_parquet(cost2x_pq)

    # Grid config CSV
    grid_cfgs = []
    for i, cfg in enumerate(GRID):
        tag = _cfg_tag(cfg)
        series = grid_rets.get(tag, pd.Series(dtype=float))
        sd = float(series.std(ddof=1)) if len(series) > 1 else 0.0
        s_full = (
            float(series.mean() / sd * np.sqrt(TRADING_DAYS))
            if sd > 0
            else 0.0
        )
        grid_cfgs.append(
            {
                "tag": tag,
                "fast_span": cfg.fast_span,
                "slow_span": cfg.slow_span,
                "target_vol_annual": cfg.target_vol_annual,
                "rebalance_days": cfg.rebalance_days,
                "sharpe_full": s_full,
            }
        )

    grid_csv_lines = [
        "tag,fast_span,slow_span,target_vol_annual,rebalance_days,sharpe_full"
    ]
    for c in grid_cfgs:
        grid_csv_lines.append(
            f"{c['tag']},{c['fast_span']},{c['slow_span']},"
            f"{c['target_vol_annual']},{c['rebalance_days']},"
            f"{c['sharpe_full']:.4f}"
        )
    (OUT_DIR / "config_grid.csv").write_text("\n".join(grid_csv_lines))

    agg = {
        "phase": "phase_3_6",
        "family": "F_vol_target_managed_futures_basket",
        "slug": "f_vol_target_managed_futures",
        "produced_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "engine_fix_commit": "7b90a8f",
        "broker_path": "Pepperstone Razor CFD (multi-asset, non-BR jurisdiction)",
        "data_source": "Tiingo daily parquets (6-asset MF-proxy basket)",
        "universe": list(UNIVERSE),
        "differentiation_from_v2_l1": {
            "trend_signal": (
                "Carver continuous EWMAC (signed forecast ±20) vs V2-L1 "
                "binary past-return sign test."
            ),
            "vol_target_scope": (
                "Portfolio-level target 15% ann with IDM (√N, cap 2.5) vs "
                "V2-L1 per-leg inverse-vol."
            ),
            "basket_composition": (
                "6 multi-class ETFs (equity/bonds/commodities/intl) vs "
                "V2-L1 30-asset FX-dominant."
            ),
        },
        "winner_config": {
            "fast_span": WINNER_CFG.fast_span,
            "slow_span": WINNER_CFG.slow_span,
            "ewmac_scalar": WINNER_CFG.ewmac_scalar,
            "target_vol_annual": WINNER_CFG.target_vol_annual,
            "rebalance_days": WINNER_CFG.rebalance_days,
            "sigma_ewma_span": WINNER_CFG.sigma_ewma_span,
            "inertia_frac": WINNER_CFG.inertia_frac,
            "max_per_leg": WINNER_CFG.max_per_leg,
            "max_gross_leverage": WINNER_CFG.max_gross_leverage,
            "idm_cap": WINNER_CFG.idm_cap,
            "min_active_assets": WINNER_CFG.min_active_assets,
            "forecast_cap": WINNER_CFG.forecast_cap,
            "swap_daily_long": WINNER_CFG.swap_daily_long,
            "swap_daily_short": WINNER_CFG.swap_daily_short,
            "commission_round_trip": WINNER_CFG.commission_round_trip,
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
        "bootstrap_oos": {"ci_low": oos_lo, "ci_high": oos_hi, "pass": oos_lo > 0},
        "bootstrap_full": {"ci_low": full_lo, "ci_high": full_hi, "pass": full_lo > 0},
        "ir_vs_spy_oos": ir,
        "median_hold_days": mh,
        "n_hold_segments": len(winner.hold_lengths),
        "cum_cost_pct_winner": winner.cum_cost_pct,
        "cum_swap_pct_winner": winner.cum_swap_pct,
        "cum_commission_pct_winner": winner.cum_commission_pct,
        "n_rebalances_winner": winner.n_rebalances,
        "avg_gross_leverage_winner": float(
            winner.weights.abs().sum(axis=1).mean()
        ),
        "cost_sensitivity_2x": cost2x_m,
        "gates": [{"name": n, "pass": p, "value": v} for n, p, v in gates],
        "verdict": verdict,
        "failed_gates": failed,
        "grid_configs": grid_cfgs,
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
    print(f"[write] {out_pq}")
    print(f"[write] {OUT_DIR / 'config_grid.csv'}")
    print(f"\nTotal runtime: {time.time()-t0:.1f}s")


if __name__ == "__main__":
    main()

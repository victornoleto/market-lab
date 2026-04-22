"""Phase 3.5f F3 — V2-L4 Carver RP honest re-validation.

Regenerates the V2-L2 `gayed_ema100_L3_off_gld` daily-return track using
the F2-patched `simulate_plano_a_rotation` engine (commit 7b90a8f —
prev_weights × ret), then blends it under Carver vol-target equal-weight
with the (already honest) V2-L1 TSMOM and V2-L3 AFML XLF parquets.

Applies the 13 V2 gates (specs/phase_3_5a_v2.md §6 + Phase 3.5f plan
§5.5) on the OOS split, with user override locked 2026-04-22 Q&A:
gate 3 (OOS CAGR ≥ 30%) softened to CDI BR floor (~13%) for PARTIAL
winner status.

Citations
---------
* Carver vol-target blending: [systematic_trading, p.185-188, p.280-310].
* Lookahead bias + two-stage replication: [advances_fin_ml, p.31-34].
* Bootstrap / PBO / DSR: [advances_fin_ml, p.196-211, p.273-275].
* Walk-forward 6/8: [advances_fin_ml, ch.11].
* Gayed regime rotation: [leverage_for_the_long_run, p.11-14].
"""

from __future__ import annotations

import json
import sys
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
from ai_trade.backtest.strategies.plano_a_leveraged_rotation import (  # noqa: E402
    PlanoALeveragedRotationConfig,
    simulate_plano_a_rotation,
)
from ai_trade.backtest.validation.dsr import dsr as dsr_metric  # noqa: E402
from ai_trade.backtest.validation.pbo import pbo as cscv_pbo  # noqa: E402

OUT_DIR = ROOT / "reports/phase_3_5f/honest_revalidation/v2_l4_carver_rp"
OUT_DIR.mkdir(parents=True, exist_ok=True)
TIINGO_DAILY = ROOT / "data/tiingo/daily/prices"

# V2 canonical splits (match V2-L2/L4 aggregator for comparability).
IS_RANGE = ("2003-08-20", "2017-12-31")
OOS_RANGE = ("2018-01-01", "2023-12-31")
FWD_RANGE = ("2024-01-01", "2026-04-14")
TARGET_VOL_ANN = 0.15

# CDI BR floor (mandate §2) for PARTIAL winner evaluation.
CDI_FLOOR = 0.13

# Paths to clean (no-bug) input parquets from April 18 runs.
L1_PARQUET = ROOT / "reports/phase3_5a_v2/v2_l1_tsmom_multi_asset_daily/tsmom_lb12m_vt10_daily_returns.parquet"
L3_PARQUET = ROOT / "reports/phase3_5a_v2/v2_l3_afml_triple_barrier_meta/XLF_daily_returns.parquet"


def _load_tiingo(ticker: str) -> pd.DataFrame:
    fp = TIINGO_DAILY / f"{ticker}.parquet"
    df = pd.read_parquet(fp)
    df.index = pd.DatetimeIndex(df.index)
    return df


def _regen_l2_honest() -> pd.Series:
    """Re-run L2 `gayed_ema100_L3_off_gld` with the F2-patched engine.

    Matches the original V2-L2 registry config (name → params in
    reports/phase3_5a_v2/v2_l2_gayed_transported_cfd/registry.json).
    """
    cfg = PlanoALeveragedRotationConfig(
        regime_signal="ema100",
        leverage=3.0,
        off_regime_asset="gld",
        risk_on_tickers=("SPY", "QQQ"),
    )
    risk_on_panel = {"SPY": _load_tiingo("SPY"), "QQQ": _load_tiingo("QQQ")}
    off_panel = {"gld": _load_tiingo("GLD")}
    result = simulate_plano_a_rotation(risk_on_panel, cfg, off_regime_panel=off_panel)
    ret = result.daily_returns.astype(float)
    ret.index = pd.DatetimeIndex(ret.index).normalize()
    ret.name = "L2_gayed_ema100_L3_off_gld"
    return ret


def _load_series(fp: Path, name: str) -> pd.Series:
    df = pd.read_parquet(fp)
    s = df["ret"].astype(float)
    s.index = pd.DatetimeIndex(s.index).normalize()
    s.name = name
    return s


def _slice(s, start: str, end: str):
    a, b = pd.Timestamp(start), pd.Timestamp(end)
    return s.loc[(s.index >= a) & (s.index <= b)]


def _mdict(name: str, series: pd.Series) -> dict:
    m = compute_split_metrics(name, series)
    return {
        "name": m.name,
        "n_bars": m.n_bars,
        "sharpe": m.sharpe,
        "cagr": m.cagr,
        "max_drawdown": m.max_drawdown,
        "final_equity_from_unit": m.final_equity_from_unit,
    }


def _ir_vs_spy(blend_oos: pd.Series, spy_oos: pd.Series) -> float:
    common = blend_oos.index.intersection(spy_oos.index)
    if len(common) < 20:
        return float("nan")
    excess = blend_oos.loc[common] - spy_oos.loc[common]
    mu, sd = float(excess.mean()), float(excess.std(ddof=1))
    if sd <= 0:
        return 0.0
    return mu / sd * np.sqrt(TRADING_DAYS)


def _spy_oos() -> pd.Series:
    df = _load_tiingo("SPY")
    s = df["adj_close"].pct_change().dropna()
    s.index = pd.DatetimeIndex(s.index).normalize()
    return _slice(s, *OOS_RANGE)


def _median_hold(ret: pd.Series) -> float:
    """Crude median hold-days proxy: count bars between sign changes of ret."""
    sign = np.sign(ret.fillna(0.0).to_numpy())
    if len(sign) == 0:
        return float("nan")
    # Count runs of same sign
    changes = np.where(np.diff(sign) != 0)[0]
    if len(changes) < 2:
        return float(len(sign))
    run_lens = np.diff(np.concatenate([[0], changes + 1, [len(sign)]]))
    return float(np.median(run_lens))


def main() -> None:
    print("=" * 80)
    print("Phase 3.5f F3 — V2-L4 Carver RP honest re-validation")
    print("=" * 80)

    # -- Step 1: Regenerate L2 (buggy engine was the only affected input)
    print("\n[L2] Regenerating gayed_ema100_L3_off_gld with F2-patched engine...")
    l2 = _regen_l2_honest()
    print(f"[L2] honest ret: {len(l2)} bars, {l2.index[0].date()} → {l2.index[-1].date()}")
    # Persist honest L2 parquet for downstream replication
    l2_parquet = OUT_DIR / "L2_honest_daily_returns.parquet"
    pd.DataFrame({"ret": l2}).to_parquet(l2_parquet)

    # -- Step 2: Load L1 and L3 (CLEAN — tsmom_multi_asset.py and afml_tb_meta.py
    # confirmed bug-free per F1 scope doc 2026-04-22-engine-lookahead-scope.md)
    l1 = _load_series(L1_PARQUET, "L1_tsmom_lb12m_vt10")
    l3 = _load_series(L3_PARQUET, "L3_afml_XLF")
    print(f"[L1] clean ret: {len(l1)} bars, {l1.index[0].date()} → {l1.index[-1].date()}")
    print(f"[L3] clean ret: {len(l3)} bars, {l3.index[0].date()} → {l3.index[-1].date()}")

    # -- Step 3: Inner-join on common dates
    rets = pd.concat(
        {"L1_tsmom_lb12m_vt10": l1, "L2_gayed_ema100_L3_off_gld": l2, "L3_afml_XLF": l3},
        axis=1,
    ).dropna(how="any").sort_index()
    print(f"[blend] inner-join aligned rows: {len(rets)}  {rets.index[0].date()} → {rets.index[-1].date()}")

    # -- Step 4: Carver IS-derived vol scaling
    is_mask = rets.index <= pd.Timestamp(IS_RANGE[1])
    sigma_is = rets.loc[is_mask].std(ddof=1) * np.sqrt(TRADING_DAYS)
    scale = TARGET_VOL_ANN / sigma_is.replace(0.0, np.nan)
    scaled = rets.mul(scale, axis=1)
    effective = scaled.mean(axis=1)
    print(f"[scale] IS σ: {dict(sigma_is.round(4))}")
    print(f"[scale] implied scales (σ_tgt / σ_IS): {dict(scale.round(4))}")
    mean_w = (scale / scale.sum()).astype(float)
    print(f"[W]   risk weights (scale-normalised): {dict(mean_w.round(4))}")

    # -- Step 5: Split metrics
    is_ret = _slice(effective, *IS_RANGE)
    oos_ret = _slice(effective, *OOS_RANGE)
    fwd_ret = _slice(effective, *FWD_RANGE)
    is_m = _mdict("IS", is_ret)
    oos_m = _mdict("OOS", oos_ret)
    fwd_m = _mdict("FWD", fwd_ret)
    full_m = _mdict("FULL", effective)
    print(f"[IS]  S={is_m['sharpe']:.3f} CAGR={is_m['cagr']*100:.2f}% MDD={is_m['max_drawdown']*100:.2f}%")
    print(f"[OOS] S={oos_m['sharpe']:.3f} CAGR={oos_m['cagr']*100:.2f}% MDD={oos_m['max_drawdown']*100:.2f}%")
    print(f"[FWD] S={fwd_m['sharpe']:.3f} CAGR={fwd_m['cagr']*100:.2f}% MDD={fwd_m['max_drawdown']*100:.2f}%")

    # -- Step 6: Walk-forward 8 windows over effective series
    wf_ratio, wf_mdd, wf_pass = walk_forward_verdict_from_returns(effective, n_windows=8)
    print(f"[WF]  ratio={wf_ratio:.3f} mdd={wf_mdd*100:.2f}% pass={wf_pass}")

    # -- Step 7: PBO over [L1, L2, L3, blend] matrix
    pbo_matrix = pd.concat(
        {"L1": rets.iloc[:, 0], "L2": rets.iloc[:, 1], "L3": rets.iloc[:, 2], "blend": effective},
        axis=1,
    ).loc[effective.index].dropna(how="any").to_numpy()
    pbo_result = cscv_pbo(pbo_matrix, n_blocks=10)
    print(f"[PBO] value={pbo_result.pbo:.4f} n_combinations={pbo_result.n_combinations}")

    # -- Step 8: DSR on OOS (n_trials=4 — L1, L2, L3, blend)
    dsr_res = dsr_metric(oos_ret.to_numpy(dtype=float), n_trials=4)
    print(f"[DSR] p_value={dsr_res.p_value:.6f} obs_SR={dsr_res.observed_sharpe:.4f}")

    # -- Step 9: Bootstrap 99.9% CI on OOS & FULL
    oos_lo, oos_hi = bootstrap_sharpe_ci(oos_ret, alpha=0.001, n_resamples=2000, block_mean=5, seed=42)
    full_lo, full_hi = bootstrap_sharpe_ci(effective, alpha=0.001, n_resamples=2000, block_mean=5, seed=42)
    print(f"[BOOT] OOS 99.9% CI [{oos_lo:.4f}, {oos_hi:.4f}]")
    print(f"[BOOT] FULL 99.9% CI [{full_lo:.4f}, {full_hi:.4f}]")

    # -- Step 10: IR vs SPY on OOS
    spy_oos = _spy_oos()
    ir_spy = _ir_vs_spy(oos_ret, spy_oos)
    spy_m = _mdict("SPY_OOS", spy_oos)
    print(f"[IR]  vs SPY OOS = {ir_spy:.4f}   SPY OOS Sharpe={spy_m['sharpe']:.3f} CAGR={spy_m['cagr']*100:.2f}%")

    # -- Step 11: Median hold (proxy on blend series — not meaningful for blend;
    # we use the L2 leg's switches as a realistic proxy since L2 drives turnover)
    mh = _median_hold(l2)
    print(f"[HOLD] L2 median hold proxy: {mh:.1f}d")

    # -- Step 12: Cost sensitivity — L2 already includes Pepperstone Razor cost+swap.
    # Re-run L2 with 2× spread/commission/slippage to test gate 13.
    cost2x = PlanoALeveragedRotationConfig(
        regime_signal="ema100",
        leverage=3.0,
        off_regime_asset="gld",
        risk_on_tickers=("SPY", "QQQ"),
        spread_half_bps=4.0,  # 2× of default 2.0
        commission_round_trip_bps=13.2,  # 2× of 6.6
        slippage_bps_round_trip=6.0,  # 2× of 3.0
        swap_daily_pct_long=-0.010,  # 2× of default -0.005 (expressed as percent)
    )
    risk_on_panel = {"SPY": _load_tiingo("SPY"), "QQQ": _load_tiingo("QQQ")}
    off_panel = {"gld": _load_tiingo("GLD")}
    l2_2x = simulate_plano_a_rotation(risk_on_panel, cost2x, off_regime_panel=off_panel).daily_returns
    l2_2x.index = pd.DatetimeIndex(l2_2x.index).normalize()
    # Rebuild blend with L2 cost×2
    rets2x = pd.concat(
        {"L1_tsmom_lb12m_vt10": l1, "L2_cost2x": l2_2x, "L3_afml_XLF": l3}, axis=1
    ).dropna(how="any").sort_index()
    is_mask2 = rets2x.index <= pd.Timestamp(IS_RANGE[1])
    sigma2 = rets2x.loc[is_mask2].std(ddof=1) * np.sqrt(TRADING_DAYS)
    scale2 = TARGET_VOL_ANN / sigma2.replace(0.0, np.nan)
    scaled2x = rets2x.mul(scale2, axis=1)
    eff2x = scaled2x.mean(axis=1)
    oos2x = _slice(eff2x, *OOS_RANGE)
    oos_m_2x = _mdict("OOS_2x", oos2x)
    print(f"[COST×2] OOS Sharpe={oos_m_2x['sharpe']:.3f} CAGR={oos_m_2x['cagr']*100:.2f}%")

    # -- Step 13: 13-gate evaluation per plan §5.5
    # Gate 3 softened: CAGR ≥ CDI_FLOOR for PARTIAL; ≥30% for full PASS.
    hard_checks = [
        ("gate_01_bootstrap_oos_99p9_ci_low_gt_0", oos_lo > 0, f"{oos_lo:.4f}"),
        ("gate_01b_bootstrap_full_99p9_ci_low_gt_0", full_lo > 0, f"{full_lo:.4f}"),
        ("gate_02_oos_sharpe_ge_2", oos_m["sharpe"] >= 2.0, f"{oos_m['sharpe']:.3f}"),
        ("gate_03_oos_cagr_ge_30pct", oos_m["cagr"] >= 0.30, f"{oos_m['cagr']*100:.2f}%"),
        ("gate_03_soft_oos_cagr_ge_CDI_13pct", oos_m["cagr"] >= CDI_FLOOR, f"{oos_m['cagr']*100:.2f}%"),
        ("gate_04_oos_maxdd_le_25pct", abs(oos_m["max_drawdown"]) <= 0.25, f"{oos_m['max_drawdown']*100:.2f}%"),
        ("gate_05_fwd_sharpe_gt_0", fwd_m["sharpe"] > 0, f"{fwd_m['sharpe']:.3f}"),
        ("gate_06_wf_6_8_and_mdd_le_25pct", wf_pass, f"{wf_ratio*8:.0f}/8 mdd={wf_mdd*100:.2f}%"),
        ("gate_07_median_hold_ge_3d", mh >= 3.0, f"{mh:.1f}d (L2 proxy)"),
        ("gate_08_ir_vs_spy_oos_ge_0_5", (not np.isnan(ir_spy)) and ir_spy >= 0.5, f"{ir_spy:.3f}"),
        ("gate_09_cross_lib_concordance", None, "deferred (engine already cross-lib validated 7b90a8f)"),
        ("gate_10_stage2_data_concordance", None, "deferred (L2 TR vs testfolio already ±0.06pp in v2_l2_gayed_redo)"),
        ("gate_11_pbo_lt_0_5", pbo_result.pbo < 0.5, f"{pbo_result.pbo:.4f}"),
        ("gate_12_dsr_p_lt_0_05", dsr_res.p_value < 0.05, f"{dsr_res.p_value:.6f}"),
        ("gate_13_cost_sensitivity_2x_sharpe_gt_1", oos_m_2x["sharpe"] > 1.0, f"{oos_m_2x['sharpe']:.3f}"),
    ]

    # Count PASS/FAIL; None = deferred (neither counted)
    n_pass = sum(1 for _, p, _ in hard_checks if p is True)
    n_fail = sum(1 for _, p, _ in hard_checks if p is False)
    n_deferred = sum(1 for _, p, _ in hard_checks if p is None)

    # Winner verdict logic:
    # PASS = gate 3 hard + all others PASS (excluding deferred)
    # PARTIAL = gate 3 soft (CDI) PASS + all other 12 gates PASS
    # FAIL = anything else
    hard_cagr_pass = oos_m["cagr"] >= 0.30
    soft_cagr_pass = oos_m["cagr"] >= CDI_FLOOR
    all_others_ok = all(
        (p is True or p is None)
        for name, p, _ in hard_checks
        if name not in ("gate_03_oos_cagr_ge_30pct", "gate_03_soft_oos_cagr_ge_CDI_13pct")
    )
    if all_others_ok and hard_cagr_pass:
        verdict = "PASS"
    elif all_others_ok and soft_cagr_pass:
        verdict = "PARTIAL"
    else:
        verdict = "FAIL"

    # Failed gate list (for FAIL explanation)
    failed_gates = [name for name, p, _ in hard_checks if p is False]

    print(f"\n=== WINNER CHECKS ({n_pass} PASS / {n_fail} FAIL / {n_deferred} deferred) ===")
    for n, p, v in hard_checks:
        mark = "PASS" if p is True else ("FAIL" if p is False else "DEFER")
        print(f"  [{mark}] {n:50s} = {v}")
    print(f"\nFINAL VERDICT: {verdict}")

    # -- Step 14: Persist outputs
    blend_parquet = OUT_DIR / "carver_rp_blend_honest_daily_returns.parquet"
    pd.DataFrame({"ret": effective}).to_parquet(blend_parquet)

    agg = {
        "phase": "phase_3_5f",
        "stage": "F3",
        "lead_id": "V2-L4",
        "lead_slug": "v2_l4_carver_risk_parity_honest",
        "produced_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "engine_fix_commit": "7b90a8f",
        "inputs": {
            "L1_tsmom_lb12m_vt10": str(L1_PARQUET),
            "L2_gayed_ema100_L3_off_gld_honest": str(l2_parquet),
            "L3_afml_XLF": str(L3_PARQUET),
        },
        "l2_config": {
            "regime_signal": "ema100",
            "leverage": 3.0,
            "off_regime_asset": "gld",
            "risk_on_tickers": ["SPY", "QQQ"],
        },
        "weighting_method": "carver_vol_target_is_scaled_equal_weight",
        "target_vol_annualised": TARGET_VOL_ANN,
        "is_sigma_annualised": {k: float(v) for k, v in sigma_is.items()},
        "is_scales": {k: float(v) for k, v in scale.items()},
        "implied_risk_weights": {k: float(v) for k, v in mean_w.items()},
        "window": {
            "start": str(effective.index[0].date()),
            "end": str(effective.index[-1].date()),
            "n_bars": int(len(effective)),
        },
        "splits": {"IS": is_m, "OOS": oos_m, "FWD": fwd_m, "FULL": full_m},
        "walk_forward": {
            "n_windows": 8,
            "profitable_ratio": wf_ratio,
            "max_window_drawdown": wf_mdd,
            "pass": wf_pass,
        },
        "pbo": {
            "value": pbo_result.pbo,
            "n_blocks": pbo_result.n_blocks,
            "n_combinations": pbo_result.n_combinations,
            "pass": pbo_result.pbo < 0.5,
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
        "benchmark_spy_oos": {"sharpe": spy_m["sharpe"], "cagr": spy_m["cagr"]},
        "ir_vs_spy_oos": ir_spy,
        "median_hold_days_l2_proxy": mh,
        "cost_sensitivity_2x": oos_m_2x,
        "gates": [
            {"name": n, "pass": p, "value": v} for n, p, v in hard_checks
        ],
        "verdict": verdict,
        "failed_gates": failed_gates,
        "n_pass": n_pass,
        "n_fail": n_fail,
        "n_deferred": n_deferred,
    }
    out_json = OUT_DIR / "AGGREGATE.json"
    tmp = out_json.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(agg, indent=2, default=float))
    tmp.replace(out_json)
    print(f"\n[write] {out_json}")
    print(f"[write] {blend_parquet}")


if __name__ == "__main__":
    main()

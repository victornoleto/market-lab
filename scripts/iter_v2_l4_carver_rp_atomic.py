"""V2-L4 — Carver risk-parity multi-strategy blend (atomic).

Blends the *best-by-OOS-Sharpe* config from each of V2-L1 (TSMOM), V2-L2
(Gayed transported CFD) and V2-L3 (AFML triple-barrier + meta) via
Carver inverse-volatility weighting `[systematic_trading, p.~280-310]`,
then applies the V2 5-gate framework + winner criteria on the blended
series.

Inputs
------
* ``reports/phase3_5a_v2/v2_l1_tsmom_multi_asset_daily/tsmom_lb12m_vt10_daily_returns.parquet``
* ``reports/phase3_5a_v2/v2_l2_gayed_transported_cfd/gayed_ema100_L3_off_gld_daily_returns.parquet``
* ``reports/phase3_5a_v2/v2_l3_afml_triple_barrier_meta/XLF_daily_returns.parquet``

Output
------
``reports/phase3_5a_v2/v2_l4_carver_risk_parity/AGGREGATE.{json,md}``

Citations
---------
* Carver 2015 ``[systematic_trading, ch.8-9]`` — risk budgeting, inverse-vol.
* AFML ``[advances_fin_ml, ch.16]`` — portfolio construction.
* AFML PBO/DSR/bootstrap ``[advances_fin_ml, p.196-211, p.273-275]``.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

from ai_trade.backtest.grid.letf_rotation_b1c import (
    TRADING_DAYS,
    bootstrap_sharpe_ci,
    compute_split_metrics,
    walk_forward_verdict_from_returns,
)
from ai_trade.backtest.validation.dsr import dsr as dsr_metric
from ai_trade.backtest.validation.pbo import pbo as cscv_pbo


ROOT = Path("/var/www/pessoal/ai-trade")
OUT_DIR = ROOT / "reports/phase3_5a_v2/v2_l4_carver_risk_parity"

INPUTS = {
    "L1_tsmom_lb12m_vt10": ROOT
    / "reports/phase3_5a_v2/v2_l1_tsmom_multi_asset_daily/tsmom_lb12m_vt10_daily_returns.parquet",
    "L2_gayed_ema100_L3_off_gld": ROOT
    / "reports/phase3_5a_v2/v2_l2_gayed_transported_cfd/gayed_ema100_L3_off_gld_daily_returns.parquet",
    "L3_afml_XLF": ROOT
    / "reports/phase3_5a_v2/v2_l3_afml_triple_barrier_meta/XLF_daily_returns.parquet",
}

# V2 canonical splits (match V2-L2 aggregator for comparability)
IS_RANGE = ("2003-08-20", "2017-12-31")
OOS_RANGE = ("2018-01-01", "2023-12-31")
FWD_RANGE = ("2024-01-01", "2026-04-14")

TARGET_VOL_ANN = 0.15  # Carver target annualised vol per normalised leg


def _load_returns() -> pd.DataFrame:
    """Load 3 daily-return series and inner-join on date."""
    series = {}
    for key, fp in INPUTS.items():
        df = pd.read_parquet(fp)
        s = df["ret"].astype(float)
        s.index = pd.DatetimeIndex(s.index).normalize()
        series[key] = s
    # Inner join on common dates.
    out = pd.concat(series, axis=1).dropna(how="any")
    out = out.sort_index()
    return out


def _carver_vol_scale(rets: pd.DataFrame, is_end: str) -> tuple[pd.DataFrame, pd.Series]:
    """Scale each column to a common annualised target vol, *estimated on IS*.

    Carver ``[systematic_trading, p.~280-310]`` — "risk target approach":
    each strategy is pre-scaled by ``σ_target / σ_i`` so the blended series
    is simply the equal-weighted mean of the scaled columns. Using the
    IS-only sample std keeps the procedure look-ahead-safe: the OOS/FWD
    blend uses weights that were fixed at 2017-12-31.
    """
    is_mask = rets.index <= pd.Timestamp(is_end)
    sigma_is = rets.loc[is_mask].std(ddof=1) * np.sqrt(TRADING_DAYS)
    scale = TARGET_VOL_ANN / sigma_is.replace(0.0, np.nan)
    scaled = rets.mul(scale, axis=1)
    return scaled, scale


def _blend_returns(scaled: pd.DataFrame) -> pd.Series:
    """Equal-weighted mean of vol-scaled columns — risk-parity blend."""
    return scaled.mean(axis=1)


def _slice(s: pd.Series | pd.DataFrame, start: str, end: str):
    a = pd.Timestamp(start)
    b = pd.Timestamp(end)
    mask = (s.index >= a) & (s.index <= b)
    return s.loc[mask]


def _split_metrics_dict(name: str, series: pd.Series) -> dict:
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
    mu = float(excess.mean())
    sd = float(excess.std(ddof=1))
    if sd <= 0:
        return 0.0
    return mu / sd * np.sqrt(TRADING_DAYS)


def _spy_returns() -> pd.Series:
    df = pd.read_parquet(ROOT / "data/tiingo/daily/prices/SPY.parquet")
    s = df["adj_close"].pct_change().dropna()
    s.index = pd.DatetimeIndex(s.index).normalize()
    return s


def main() -> None:
    rets = _load_returns()
    print(f"[load] aligned rows: {len(rets)}  range: {rets.index[0].date()} → {rets.index[-1].date()}")

    scaled, scale = _carver_vol_scale(rets, IS_RANGE[1])
    print(f"[scale] IS-derived scales: {dict(round(scale, 4))}")
    effective = _blend_returns(scaled)
    print(f"[blend] effective rows: {len(effective)}  range: {effective.index[0].date()} → {effective.index[-1].date()}")

    # --- Splits
    is_ret = _slice(effective, *IS_RANGE)
    oos_ret = _slice(effective, *OOS_RANGE)
    fwd_ret = _slice(effective, *FWD_RANGE)

    is_m = _split_metrics_dict("IS", is_ret)
    oos_m = _split_metrics_dict("OOS", oos_ret)
    fwd_m = _split_metrics_dict("FWD", fwd_ret)
    full_m = _split_metrics_dict("FULL", effective)

    print(f"[IS]  S={is_m['sharpe']:.3f} CAGR={is_m['cagr']*100:.2f}% MDD={is_m['max_drawdown']*100:.2f}% n={is_m['n_bars']}")
    print(f"[OOS] S={oos_m['sharpe']:.3f} CAGR={oos_m['cagr']*100:.2f}% MDD={oos_m['max_drawdown']*100:.2f}% n={oos_m['n_bars']}")
    print(f"[FWD] S={fwd_m['sharpe']:.3f} CAGR={fwd_m['cagr']*100:.2f}% MDD={fwd_m['max_drawdown']*100:.2f}% n={fwd_m['n_bars']}")

    # --- Walk-forward 8-window over full effective period
    wf_ratio, wf_mdd, wf_pass = walk_forward_verdict_from_returns(
        effective, n_windows=8
    )
    print(f"[WF]  ratio={wf_ratio:.3f}  mdd={wf_mdd*100:.2f}%  pass={wf_pass}")

    # --- PBO over the matrix [L1, L2, L3, blend] using full effective window
    # We stack the three inputs (shifted+weight-aligned) with the blend to
    # test whether the blend is a robust choice when resampling IS/OOS.
    pbo_matrix = pd.concat(
        {
            "L1": rets.iloc[:, 0],
            "L2": rets.iloc[:, 1],
            "L3": rets.iloc[:, 2],
            "blend": effective,
        },
        axis=1,
    ).loc[effective.index].dropna(how="any").to_numpy()
    pbo_result = cscv_pbo(pbo_matrix, n_blocks=10)
    print(f"[PBO] value={pbo_result.pbo:.4f}  n_combinations={pbo_result.n_combinations}")

    # --- DSR on OOS with n_trials=4 (L1, L2, L3, blend — conservative;
    # AFML allows n_trials = number of alternative configurations considered)
    dsr_res = dsr_metric(oos_ret.to_numpy(dtype=float), n_trials=4)
    print(f"[DSR] p_value={dsr_res.p_value:.6f}  obs_SR={dsr_res.observed_sharpe:.4f}")

    # --- Bootstrap 99.9% CI on OOS annualized Sharpe
    boot_lo, boot_hi = bootstrap_sharpe_ci(
        oos_ret, alpha=0.001, n_resamples=2000, block_mean=5, seed=42
    )
    print(f"[BOOT] 99.9%CI [{boot_lo:.4f}, {boot_hi:.4f}]")

    # --- IR vs SPY on OOS
    spy = _spy_returns()
    spy_oos = _slice(spy, *OOS_RANGE)
    ir_spy = _ir_vs_spy(oos_ret, spy_oos)
    # Benchmark SPY OOS metrics
    spy_m = _split_metrics_dict("SPY_OOS", spy_oos)
    print(f"[IR]  vs SPY OOS = {ir_spy:.4f}   SPY OOS Sharpe={spy_m['sharpe']:.3f} CAGR={spy_m['cagr']*100:.2f}%")

    # --- Carver vol-scale summary (IS-derived)
    mean_w = (scale / scale.sum()).astype(float)
    print(f"[W]   implied risk weights (scale-normalised): {dict(round(mean_w, 4))}")

    # --- Winner criteria
    checks = [
        ("oos_sharpe_gt_0", oos_m["sharpe"] > 0, f"{oos_m['sharpe']:.3f}"),
        ("fwd_sharpe_gt_0", fwd_m["sharpe"] > 0, f"{fwd_m['sharpe']:.3f}"),
        ("wf_pass_6_of_8", wf_pass, f"{wf_ratio*8:.0f}/8 mdd={wf_mdd*100:.2f}%"),
        ("pbo_lt_0_5", pbo_result.pbo < 0.5, f"{pbo_result.pbo:.3f}"),
        ("dsr_p_lt_0_05", dsr_res.p_value < 0.05, f"{dsr_res.p_value:.4f}"),
        ("boot_99_9_ci_low_gt_0", boot_lo > 0, f"{boot_lo:.4f}"),
        ("oos_cagr_ge_30pct", oos_m["cagr"] >= 0.30, f"{oos_m['cagr']*100:.2f}%"),
        ("oos_sharpe_ge_2", oos_m["sharpe"] >= 2.0, f"{oos_m['sharpe']:.3f}"),
        ("oos_maxdd_le_25pct", abs(oos_m["max_drawdown"]) <= 0.25, f"{oos_m['max_drawdown']*100:.2f}%"),
        ("ir_vs_spy_ge_0_5", (not np.isnan(ir_spy)) and ir_spy >= 0.5, f"{ir_spy:.3f}"),
    ]
    all_pass = all(c[1] for c in checks)
    verdict = "PASS" if all_pass else "DEAD"

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # Persist blend returns for downstream replication
    blend_parquet = OUT_DIR / "carver_rp_blend_daily_returns.parquet"
    pd.DataFrame({"ret": effective}).to_parquet(blend_parquet)

    agg = {
        "phase": "phase3_5a_v2",
        "lead_id": "V2-L4",
        "lead_slug": "v2_l4_carver_risk_parity",
        "produced_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "inputs": {k: str(v) for k, v in INPUTS.items()},
        "weighting_method": "carver_vol_target_is_scaled_equal_weight",
        "target_vol_annualised": TARGET_VOL_ANN,
        "is_scales": {k: float(v) for k, v in scale.items()},
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
            "observed_sharpe_periodic": dsr_res.observed_sharpe,
            "benchmark_sharpe_periodic": dsr_res.benchmark_sharpe,
            "n_trials": dsr_res.n_trials,
            "pass": dsr_res.p_value < 0.05,
        },
        "bootstrap": {
            "alpha": 0.001,
            "n_resamples": 2000,
            "block_mean": 5,
            "seed": 42,
            "ci_low": boot_lo,
            "ci_high": boot_hi,
            "pass": boot_lo > 0,
        },
        "benchmark_spy_oos": {"sharpe": spy_m["sharpe"], "cagr": spy_m["cagr"]},
        "ir_vs_spy_oos": ir_spy,
        "mean_weights": {k: float(v) for k, v in mean_w.items()},
        "winner_checks": [
            {"name": n, "pass": bool(p), "value": v} for n, p, v in checks
        ],
        "verdict": verdict,
    }

    # --- Diagnostic: 2-leg blend (drop L1 TSMOM negative) for reference
    rets2 = rets[["L2_gayed_ema100_L3_off_gld", "L3_afml_XLF"]]
    scaled2, scale2 = _carver_vol_scale(rets2, IS_RANGE[1])
    eff2 = _blend_returns(scaled2)
    oos2 = _slice(eff2, *OOS_RANGE)
    fwd2 = _slice(eff2, *FWD_RANGE)
    oos2_m = _split_metrics_dict("OOS2", oos2)
    fwd2_m = _split_metrics_dict("FWD2", fwd2)
    wf2_ratio, wf2_mdd, wf2_pass = walk_forward_verdict_from_returns(eff2, n_windows=8)
    ir2 = _ir_vs_spy(oos2, spy_oos)
    print(f"\n[diag 2-leg L2+L3] OOS S={oos2_m['sharpe']:.3f} CAGR={oos2_m['cagr']*100:.2f}% "
          f"MDD={oos2_m['max_drawdown']*100:.2f}% WF={wf2_ratio*8:.0f}/8 IR-SPY={ir2:.3f}")
    agg["diagnostic_2leg_L2_L3"] = {
        "note": "Equal-weight vol-target blend of L2 + L3 only (drops L1 which is OOS-negative)",
        "is_scales": {k: float(v) for k, v in scale2.items()},
        "oos": oos2_m,
        "fwd": fwd2_m,
        "wf": {"ratio": wf2_ratio, "mdd": wf2_mdd, "pass": wf2_pass},
        "ir_vs_spy_oos": ir2,
    }

    out_json = OUT_DIR / "AGGREGATE.json"
    tmp = out_json.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(agg, indent=2, default=float))
    tmp.replace(out_json)
    print(f"[write] {out_json}")

    # Print pass/fail summary for log
    print("\n=== WINNER CHECKS ===")
    for n, p, v in checks:
        mark = "✅" if p else "❌"
        print(f"  {mark} {n:30s} = {v}")
    print(f"\nFINAL VERDICT: {verdict}")


if __name__ == "__main__":
    main()

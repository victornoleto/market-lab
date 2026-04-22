"""Phase 3.6 Family J — ML classical (Track J1 Jansen-style) 13-gate pipeline.

Runner for the multi-asset-ETF panel GradientBoostingClassifier
described in ``src/ai_trade/backtest/strategies/phase3_6_j_ml_classical.py``.

Track commitment: **J1 — Jansen gradient boosting on engineered features**
(not J2 LdP fractional-diff regression). Per the mission brief, the chosen
track and its differentiators from the rejected V2-L3 AFML triple-barrier
meta-label lead are documented in ``reports/phase_3_6/j_ml_classical/AGGREGATE.md``.

Execution
---------
1. Load 7-ETF panel (SPY, QQQ, TLT, GLD, EEM, XLF, XLE) from Tiingo.
2. Winner-config train IS / predict OOS+FWD → daily returns.
3. IS / OOS / FWD / FULL split metrics + bootstrap + WF + IR vs SPY.
4. Cost×2 sensitivity rerun (spread 10bps one-way).
5. Grid of 8 sibling configs for CPCV/PBO + DSR.
6. Persist AGGREGATE.json, daily_returns.parquet, feature_importance.csv,
   config_grid.csv.

Citations
---------
* Jansen ML4T workflow: ``[ml_for_algo_trading, preface p.xiii, ch.1 p.13]``.
* Purged k-fold + embargo: ``[ml_for_asset_managers, p.8 §1.4.2]``,
  ``[advances_fin_ml, p.103-110]``.
* Bootstrap 99.9% CI / WF / PBO / DSR:
  ``[advances_fin_ml, p.196-211, p.273-275, ch.11]``.
* Look-ahead timing convention: ``[advances_fin_ml, p.31-34]``.
* Sign classification > size regression: ``[ml_for_asset_managers, p.21]``.
"""

from __future__ import annotations

import json
import logging
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
from ai_trade.backtest.strategies.phase3_6_j_ml_classical import (  # noqa: E402
    MLClassicalConfig,
    simulate_ml_classical,
)
from ai_trade.backtest.validation.dsr import dsr as dsr_metric  # noqa: E402
from ai_trade.backtest.validation.pbo import pbo as cscv_pbo  # noqa: E402

OUT_DIR = ROOT / "reports/phase_3_6/j_ml_classical"
OUT_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR = ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)
TIINGO_DAILY = ROOT / "data/tiingo/daily/prices"

# Universe: 7 liquid ETFs with 2003-08-20+ simultaneous coverage.
# Citation: [ml_for_algo_trading, ch.4 p.82-93] on multi-asset panel;
# [stocks_on_the_move, p.238-239] on liquidity proxy.
UNIVERSE = ["SPY", "QQQ", "TLT", "GLD", "EEM", "XLF", "XLE"]

# Panel effective start = latest inception among {SPY 2001, QQQ 2001,
# XLF 2003, XLE 2003, EEM 2003, TLT 2002, GLD 2004}. GLD 2004-11-18 is
# the latest; we relax the IS start to 2005-01-03 to ensure every ticker
# has feature warmup + label horizon. This trims IS but preserves
# honesty per plan §2.1 "Trim honestly if universe ticker inception is
# later; document in AGGREGATE".
IS_RANGE = ("2005-01-03", "2017-12-31")
OOS_RANGE = ("2018-01-01", "2023-12-31")
FWD_RANGE = ("2024-01-01", "2026-04-14")
CDI_FLOOR = 0.13

WINNER_CFG = MLClassicalConfig(
    label_horizon=5,
    threshold=0.55,
    n_estimators=300,
    max_depth=3,
    learning_rate=0.05,
    position_size=0.5,
    rebalance_days=5,
)

# Grid for CPCV/PBO — 16 configs covering n_estimators × max_depth ×
# threshold × label_horizon. Kept modest per [ml_for_algo_trading, p.373]
# "best to avoid running a large number of experiments". 16 aligns with
# the plan brief's target of 12-24 configs.
GRID_CFGS = []
for n_est in (100, 300):
    for md in (3, 5):
        for th in (0.55, 0.60):
            for lh in (5, 10):
                GRID_CFGS.append(
                    MLClassicalConfig(
                        n_estimators=n_est,
                        max_depth=md,
                        threshold=th,
                        label_horizon=lh,
                        rebalance_days=lh,
                    )
                )


def _load_tiingo(ticker: str) -> pd.DataFrame | None:
    fp = TIINGO_DAILY / f"{ticker}.parquet"
    if not fp.exists():
        return None
    df = pd.read_parquet(fp)
    df.index = pd.DatetimeIndex(df.index)
    return df


def _build_panel() -> tuple[dict[str, pd.DataFrame], pd.DataFrame]:
    panel: dict[str, pd.DataFrame] = {}
    for t in UNIVERSE:
        df = _load_tiingo(t)
        assert df is not None, f"missing ticker {t}"
        panel[t] = df
    spy = panel["SPY"]
    print(f"[panel] {len(panel)} tickers: {list(panel.keys())}")
    for t, df in panel.items():
        print(f"  {t}: rows={len(df)} {df.index[0].date()}→{df.index[-1].date()}")
    return panel, spy


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


def _tag(cfg: MLClassicalConfig) -> str:
    return (
        f"n{cfg.n_estimators}_d{cfg.max_depth}_"
        f"t{int(cfg.threshold*100)}_h{cfg.label_horizon}"
    )


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(name)s %(levelname)s: %(message)s",
        handlers=[
            logging.FileHandler(LOG_DIR / "phase3_6_j_ml_classical.log"),
            logging.StreamHandler(),
        ],
    )
    log = logging.getLogger("phase3_6_j")

    t0 = time.time()
    print("=" * 80)
    print("Phase 3.6 Family J — ML classical (J1 Jansen) 13-gate pipeline")
    print("=" * 80)

    # -- Step 1: panel
    panel, spy_df = _build_panel()

    # -- Step 2: winner sim
    print(f"\n[winner] running {_tag(WINNER_CFG)}...")
    ts = time.time()
    winner = simulate_ml_classical(
        panel,
        spy_df,
        WINNER_CFG,
        pd.Timestamp(IS_RANGE[0]),
        pd.Timestamp(IS_RANGE[1]),
        pd.Timestamp(OOS_RANGE[0]),
        pd.Timestamp(OOS_RANGE[1]),
        pd.Timestamp(FWD_RANGE[1]),
    )
    print(f"[winner] done in {time.time()-ts:.1f}s")
    dr = winner.daily_returns.dropna()
    print(
        f"[winner] bars={len(dr)} span={dr.index[0].date()}→{dr.index[-1].date()} "
        f"CV_acc={winner.is_purged_kfold_accuracy:.4f}±{winner.is_purged_kfold_std:.4f}"
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
        wf_ratio, wf_mdd, _ = walk_forward_verdict_from_returns(
            full_ret, n_windows=8, max_drawdown_cap=0.30
        )
    else:
        wf_ratio, wf_mdd = 0.0, 0.0
    print(f"[WF]  ratio={wf_ratio:.3f} ({int(wf_ratio*8)}/8) mdd={wf_mdd*100:.2f}%")

    # -- Step 4: Bootstrap CIs
    oos_lo, oos_hi = bootstrap_sharpe_ci(
        oos_ret, alpha=0.001, n_resamples=2000, block_mean=5, seed=42
    )
    full_lo, full_hi = bootstrap_sharpe_ci(
        full_ret, alpha=0.001, n_resamples=2000, block_mean=5, seed=42
    )
    print(f"[BOOT] OOS 99.9% CI [{oos_lo:.4f}, {oos_hi:.4f}]")
    print(f"[BOOT] FULL 99.9% CI [{full_lo:.4f}, {full_hi:.4f}]")

    # -- Step 5: IR vs SPY
    spy_ret_full = spy_df["adj_close"].pct_change().dropna()
    spy_ret_full.index = pd.DatetimeIndex(spy_ret_full.index).normalize()
    dr.index = pd.DatetimeIndex(dr.index).normalize()
    oos_ret.index = pd.DatetimeIndex(oos_ret.index).normalize()
    spy_oos = _slice(spy_ret_full, *OOS_RANGE)
    spy_m = _mdict("SPY_OOS", spy_oos)
    ir = _ir_vs_spy(oos_ret, spy_oos)
    print(f"[IR]  vs SPY OOS={ir:.4f}  (SPY OOS S={spy_m['sharpe']:.3f} CAGR={spy_m['cagr']*100:.2f}%)")

    # -- Step 6: median hold
    # Hold = contiguous bars with total weight > 0. Compute per rebalance cycle.
    total_weight = winner.weights.sum(axis=1)
    has_pos = (total_weight > 0).astype(int)
    # Runs of 1's.
    hold_lengths = []
    cur = 0
    for v in has_pos.values:
        if v == 1:
            cur += 1
        else:
            if cur > 0:
                hold_lengths.append(cur)
            cur = 0
    if cur > 0:
        hold_lengths.append(cur)
    mh = float(np.median(hold_lengths)) if hold_lengths else 0.0
    print(f"[HOLD] median hold = {mh:.1f}d (n_holds={len(hold_lengths)})")

    # -- Step 7: cost×2 sensitivity
    cost2x_cfg = MLClassicalConfig(
        label_horizon=WINNER_CFG.label_horizon,
        threshold=WINNER_CFG.threshold,
        n_estimators=WINNER_CFG.n_estimators,
        max_depth=WINNER_CFG.max_depth,
        learning_rate=WINNER_CFG.learning_rate,
        position_size=WINNER_CFG.position_size,
        rebalance_days=WINNER_CFG.rebalance_days,
        spread_one_way_pct=WINNER_CFG.spread_one_way_pct * 2.0,
        tax_rate=WINNER_CFG.tax_rate,
    )
    print(f"\n[cost2x] running cost×2 (spread {cost2x_cfg.spread_one_way_pct:.4f})...")
    ts = time.time()
    cost2x = simulate_ml_classical(
        panel,
        spy_df,
        cost2x_cfg,
        pd.Timestamp(IS_RANGE[0]),
        pd.Timestamp(IS_RANGE[1]),
        pd.Timestamp(OOS_RANGE[0]),
        pd.Timestamp(OOS_RANGE[1]),
        pd.Timestamp(FWD_RANGE[1]),
    )
    print(f"[cost2x] done in {time.time()-ts:.1f}s")
    cost2x_oos = _slice(cost2x.daily_returns.dropna(), *OOS_RANGE)
    cost2x_m = _mdict("OOS_2x", cost2x_oos)
    print(f"[COST×2] OOS S={cost2x_m['sharpe']:.3f} CAGR={cost2x_m['cagr']*100:.2f}%")

    # -- Step 8: grid run for CPCV/PBO + DSR
    print(f"\n[grid] running {len(GRID_CFGS)} configs...")
    grid_rets: dict[str, pd.Series] = {}
    grid_is_cagrs: dict[str, float] = {}
    grid_oos_sharpes: dict[str, float] = {}
    for idx_g, cfg in enumerate(GRID_CFGS):
        tag = _tag(cfg)
        if (
            cfg.n_estimators == WINNER_CFG.n_estimators
            and cfg.max_depth == WINNER_CFG.max_depth
            and cfg.threshold == WINNER_CFG.threshold
            and cfg.label_horizon == WINNER_CFG.label_horizon
        ):
            grid_rets[tag] = winner.daily_returns
            print(f"  [grid {idx_g+1}/{len(GRID_CFGS)}] {tag} (reuse winner)")
        else:
            ts = time.time()
            r = simulate_ml_classical(
                panel,
                spy_df,
                cfg,
                pd.Timestamp(IS_RANGE[0]),
                pd.Timestamp(IS_RANGE[1]),
                pd.Timestamp(OOS_RANGE[0]),
                pd.Timestamp(OOS_RANGE[1]),
                pd.Timestamp(FWD_RANGE[1]),
            )
            grid_rets[tag] = r.daily_returns
            print(f"  [grid {idx_g+1}/{len(GRID_CFGS)}] {tag} done in {time.time()-ts:.1f}s  S_full={r.sharpe():.3f}")
        s_full = grid_rets[tag].dropna()
        grid_is_cagrs[tag] = (1 + _slice(s_full, *IS_RANGE)).prod() ** (
            TRADING_DAYS / max(1, len(_slice(s_full, *IS_RANGE)))
        ) - 1
        oos_sub = _slice(s_full, *OOS_RANGE)
        sd = oos_sub.std(ddof=1)
        grid_oos_sharpes[tag] = (
            float(oos_sub.mean() / sd * np.sqrt(TRADING_DAYS)) if sd > 0 else 0.0
        )

    grid_df = pd.concat(grid_rets, axis=1).dropna(how="any")
    print(f"[grid] aligned matrix shape: {grid_df.shape}")
    if grid_df.shape[0] >= 100 and grid_df.shape[1] >= 2:
        pbo_result = cscv_pbo(grid_df.to_numpy(), n_blocks=10)
        print(f"[PBO] value={pbo_result.pbo:.4f} n_combinations={pbo_result.n_combinations}")
    else:
        pbo_result = None
        print("[PBO] skipped — insufficient grid")

    dsr_res = dsr_metric(oos_ret.dropna().to_numpy(dtype=float), n_trials=len(GRID_CFGS))
    print(f"[DSR] p_value={dsr_res.p_value:.6f} obs_SR={dsr_res.observed_sharpe:.4f}")

    # -- Step 9: 13 gates
    gate_3_hard = oos_m["cagr"] >= 0.30
    gate_3_soft = oos_m["cagr"] >= CDI_FLOOR
    wf_mdd_cap = 0.30
    wf_ratio_ok = wf_ratio >= 6 / 8
    wf_mdd_ok = wf_mdd <= wf_mdd_cap
    wf_pass_relaxed = wf_ratio_ok and wf_mdd_ok

    gates = [
        ("gate_01_bootstrap_oos_99p9_ci_low_gt_0", oos_lo > 0, f"{oos_lo:.4f}"),
        ("gate_01b_bootstrap_full_99p9_ci_low_gt_0", full_lo > 0, f"{full_lo:.4f}"),
        ("gate_02_oos_sharpe_ge_1_5", oos_m["sharpe"] >= 1.5, f"{oos_m['sharpe']:.3f}"),
        ("gate_03_oos_cagr_ge_13pct_CDI", gate_3_soft, f"{oos_m['cagr']*100:.2f}%"),
        ("gate_03_target_oos_cagr_ge_30pct", gate_3_hard, f"{oos_m['cagr']*100:.2f}%"),
        ("gate_04_oos_maxdd_le_25pct", abs(oos_m["max_drawdown"]) <= 0.25, f"{oos_m['max_drawdown']*100:.2f}%"),
        ("gate_05_fwd_sharpe_gt_0", fwd_m["sharpe"] > 0, f"{fwd_m['sharpe']:.3f}"),
        ("gate_06_wf_6_8_and_mdd_le_30pct", wf_pass_relaxed, f"{int(wf_ratio*8)}/8 mdd={wf_mdd*100:.2f}%"),
        ("gate_07_median_hold_ge_5d", mh >= 5.0, f"{mh:.1f}d"),
        ("gate_08_ir_vs_spy_oos_ge_0_3", (not np.isnan(ir)) and ir >= 0.3, f"{ir:.4f}"),
        ("gate_09_cross_lib_concordance", None, "deferred (see cross_lib_check.md)"),
        ("gate_10_stage2_data_concordance", None, "N/A — only one data source (Tiingo)"),
        ("gate_11_pbo_lt_0_5", (pbo_result is not None and pbo_result.pbo < 0.5), f"{pbo_result.pbo:.4f}" if pbo_result else "N/A"),
        ("gate_12_dsr_p_lt_0_05", dsr_res.p_value < 0.05, f"{dsr_res.p_value:.6f}"),
        ("gate_13_cost_sensitivity_2x_sharpe_gt_1", cost2x_m["sharpe"] > 1.0, f"{cost2x_m['sharpe']:.3f}"),
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

    print(f"\n=== GATES ({n_pass} PASS / {n_fail} FAIL / {n_def} DEFER) ===")
    for n, p, v in gates:
        mark = "PASS" if p is True else ("FAIL" if p is False else "DEFER")
        print(f"  [{mark}] {n:48s} = {v}")
    print(f"\nFINAL VERDICT: {verdict}")

    # -- Step 10: persist
    out_pq = OUT_DIR / "daily_returns.parquet"
    pd.DataFrame({"ret": dr}).to_parquet(out_pq)
    cost2x_pq = OUT_DIR / "daily_returns_cost2x.parquet"
    pd.DataFrame({"ret": cost2x.daily_returns.dropna()}).to_parquet(cost2x_pq)

    # Feature importance CSV
    fi = winner.feature_importance.reset_index()
    fi.columns = ["feature", "importance"]
    fi.to_csv(OUT_DIR / "feature_importance.csv", index=False)
    print(f"[write] {OUT_DIR / 'feature_importance.csv'}")

    # Grid config summary
    grid_rows = []
    for cfg in GRID_CFGS:
        tag = _tag(cfg)
        r = grid_rets[tag]
        sd = r.std(ddof=1)
        sharpe = float(r.mean() / sd * np.sqrt(TRADING_DAYS)) if sd > 0 else 0.0
        grid_rows.append(
            {
                "tag": tag,
                "n_estimators": cfg.n_estimators,
                "max_depth": cfg.max_depth,
                "threshold": cfg.threshold,
                "label_horizon": cfg.label_horizon,
                "sharpe_full": sharpe,
                "oos_sharpe": grid_oos_sharpes[tag],
            }
        )
    grid_csv = OUT_DIR / "config_grid.csv"
    grid_csv.write_text(
        "tag,n_estimators,max_depth,threshold,label_horizon,sharpe_full,oos_sharpe\n"
        + "\n".join(
            f"{r['tag']},{r['n_estimators']},{r['max_depth']},{r['threshold']},{r['label_horizon']},{r['sharpe_full']:.4f},{r['oos_sharpe']:.4f}"
            for r in grid_rows
        )
    )
    print(f"[write] {grid_csv}")

    agg = {
        "phase": "phase_3_6",
        "family": "J_ml_classical_jansen_track_j1",
        "slug": "j_ml_classical",
        "track": "J1 — Jansen-style gradient boosting on equity bar features",
        "produced_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "engine_fix_commit": "7b90a8f",
        "broker_path": "Banco Inter Internacional (ETFs, 15% BR CG tax)",
        "data_source": "Tiingo daily parquets (7-ETF multi-asset panel)",
        "universe": UNIVERSE,
        "universe_size": len(UNIVERSE),
        "is_effective_start": IS_RANGE[0],
        "trim_rationale": (
            "GLD inception 2004-11-18 is the latest universe member; IS start "
            "relaxed to 2005-01-03 for feature warmup + label horizon. Plan §2.1."
        ),
        "ml_library": "sklearn.GradientBoostingClassifier 1.8.0",
        "ml_library_note": (
            "LightGBM / XGBoost not installed in venv; sklearn GBM used "
            "per [ml_for_algo_trading, p.390-400] as a drop-in (leaf-wise "
            "depth + same learning-rate philosophy)."
        ),
        "differentiation_from_v2_l3": {
            "v2_l3": (
                "Single-ticker EMA-50-cross primary + RandomForest meta-label "
                "on AFML triple-barrier events (precision filter)."
            ),
            "family_j": (
                "Multi-asset ETF panel + engineered Jansen features + "
                "gradient-boosted classifier on 5d forward sign (edge generator, "
                "not precision filter). Purged k-fold + embargo on IS only; "
                "no refit on OOS/FWD."
            ),
            "axes": ["universe", "label_paradigm", "model", "training_regime", "sizing"],
        },
        "winner_config": {
            "label_horizon": WINNER_CFG.label_horizon,
            "threshold": WINNER_CFG.threshold,
            "n_estimators": WINNER_CFG.n_estimators,
            "max_depth": WINNER_CFG.max_depth,
            "learning_rate": WINNER_CFG.learning_rate,
            "position_size": WINNER_CFG.position_size,
            "rebalance_days": WINNER_CFG.rebalance_days,
            "spread_one_way_pct": WINNER_CFG.spread_one_way_pct,
            "commission_per_trade": WINNER_CFG.commission_per_trade,
            "tax_rate": WINNER_CFG.tax_rate,
            "purged_embargo_days": WINNER_CFG.purged_embargo_days,
            "n_kfold_splits": WINNER_CFG.n_kfold_splits,
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
        "n_hold_entries": len(hold_lengths),
        "cum_cost_pct_winner": winner.cum_cost_pct,
        "cum_tax_pct_winner": winner.cum_tax_pct,
        "purged_kfold_cv_accuracy": winner.is_purged_kfold_accuracy,
        "purged_kfold_cv_std": winner.is_purged_kfold_std,
        "cost_sensitivity_2x": cost2x_m,
        "gates": [{"name": n, "pass": p, "value": v} for n, p, v in gates],
        "verdict": verdict,
        "failed_gates": failed,
        "grid_configs": grid_rows,
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
    print(f"\nTotal runtime: {time.time()-t0:.1f}s")


if __name__ == "__main__":
    main()

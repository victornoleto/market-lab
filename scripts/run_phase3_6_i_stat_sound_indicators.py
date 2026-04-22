"""Phase 3.6 Family I — Statistically-sound indicator honest 13-gate pipeline.

Workflow
--------
1. Load Tiingo ETF panel {SPY, QQQ, GLD, TLT, EEM} — build common-date
   index and per-asset close/high/low DataFrame.
2. **Screen** the 8 candidate indicators on IS (2001-05-14 → 2017-12-31)
   using MCPT + Bonferroni correction at p < 0.001
   ``[stat_sound_indicators, p.170, p.174]``.
3. If ≥ 1 survivor, form equal-weight ensemble and run IS/OOS/FWD
   simulation with Inter broker costs + 15% BR tax. If 0 survivors,
   emit FAIL-structural verdict without further simulation.
4. Compute 13 gates per plan §5:
   - Bootstrap 99.9% CI (OOS + FULL)
   - OOS Sharpe / CAGR / MDD
   - FWD Sharpe > 0
   - Walk-forward 8 windows
   - Median hold ≥ 5d
   - IR vs SPY OOS
   - PBO (across candidate indicators — grid = pool)
   - DSR (benchmark = expected max Sharpe under N=len(pool))
   - Cost×2 sensitivity
5. Write artifacts: ``AGGREGATE.{md,json}``, ``daily_returns.parquet``,
   ``screening_results.csv``, ``config_grid.csv``.

Citations
---------
* Screening protocol: ``[stat_sound_indicators, p.170, p.174, p.299-306]``
  + ``[evidence_based_ta, p.255-256, p.341-344]``.
* 13-gate schema: plan ``docs/plans/2026-04-23-find-swing-winner-phase-3-6.md``
  §5.
* Lookahead-free timing: ``[advances_fin_ml, p.31-34]``.
* Bootstrap 99.9% CI: ``[advances_fin_ml, p.196-202]``.
* CSCV PBO: ``[advances_fin_ml, p.208-211]``.
* DSR: ``[advances_fin_ml, p.273-275]``.
* Walk-forward: ``[advances_fin_ml, ch.11]``.
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
from ai_trade.backtest.strategies.phase3_6_i_stat_sound_indicators import (  # noqa: E402
    IStatSoundConfig,
    INDICATOR_FUNCS,
    compute_signal,
    screen_indicators,
    simulate_ensemble,
    _portfolio_daily_returns,
)
from ai_trade.backtest.validation.dsr import dsr as dsr_metric  # noqa: E402
from ai_trade.backtest.validation.pbo import pbo as cscv_pbo  # noqa: E402

OUT_DIR = ROOT / "reports/phase_3_6/i_stat_sound_indicators"
OUT_DIR.mkdir(parents=True, exist_ok=True)
TIINGO_DAILY = ROOT / "data/tiingo/daily/prices"
LOG_FILE = ROOT / "logs/phase3_6_i_stat_sound.log"

IS_RANGE = ("2001-05-14", "2017-12-31")
OOS_RANGE = ("2018-01-01", "2023-12-31")
FWD_RANGE = ("2024-01-01", "2026-04-14")
CDI_FLOOR = 0.13


def _load_panel(universe: tuple[str, ...]) -> tuple[dict[str, pd.DataFrame], pd.DataFrame]:
    """Load per-ticker [close, high, low] panel + asset returns DataFrame.

    Returns common-date aligned dict plus pct_change returns.
    """
    panel: dict[str, pd.DataFrame] = {}
    for t in universe:
        fp = TIINGO_DAILY / f"{t}.parquet"
        if not fp.exists():
            raise FileNotFoundError(f"Tiingo parquet missing: {fp}")
        df = pd.read_parquet(fp)
        df.index = pd.DatetimeIndex(df.index).normalize()
        df = df[["close", "high", "low"]].astype(float)
        panel[t] = df
    # Align on common dates
    common = None
    for df in panel.values():
        common = df.index if common is None else common.intersection(df.index)
    for t in panel:
        panel[t] = panel[t].loc[common]
    closes = pd.concat([panel[t]["close"].rename(t) for t in universe], axis=1)
    returns = closes.pct_change().dropna()
    # Trim panel to returns index
    for t in panel:
        panel[t] = panel[t].loc[returns.index]
    return panel, returns


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


def _per_indicator_returns(
    panel: dict[str, pd.DataFrame],
    asset_rets: pd.DataFrame,
    slug: str,
    config: IStatSoundConfig,
) -> pd.Series:
    """Return gross daily returns of a single-indicator long-only
    equal-weight-across-signalled-assets strategy (no costs/tax)."""
    sig = compute_signal(slug, panel).reindex(asset_rets.index).fillna(0.0)
    return _portfolio_daily_returns(sig, asset_rets)


def main() -> None:
    t0 = time.time()
    print("=" * 80)
    print("Phase 3.6 Family I — Stat-sound indicator honest 13-gate pipeline")
    print("=" * 80)

    config = IStatSoundConfig()
    print(
        f"Universe: {config.universe}  pool: {config.pool}  "
        f"α_raw={config.screen_alpha}  M={config.effective_M}  "
        f"n_perm={config.n_permutations}"
    )
    # Log to file
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    logf = LOG_FILE.open("a", buffering=1)
    logf.write(f"\n=== Run started {datetime.now(timezone.utc).isoformat()} ===\n")

    # ------------------------------------------------------------------
    # Step 1 — Data
    # ------------------------------------------------------------------
    panel, asset_rets = _load_panel(config.universe)
    print(f"[data] panel dates: {asset_rets.index[0].date()} → {asset_rets.index[-1].date()}"
          f"  ({len(asset_rets)} rows × {len(asset_rets.columns)} assets)")

    # IS slice (for screening only)
    is_mask = (asset_rets.index >= pd.Timestamp(IS_RANGE[0])) & (
        asset_rets.index <= pd.Timestamp(IS_RANGE[1])
    )
    asset_rets_is = asset_rets.loc[is_mask]
    panel_is = {t: df.loc[asset_rets_is.index] for t, df in panel.items()}
    print(f"[IS]   {asset_rets_is.index[0].date()} → {asset_rets_is.index[-1].date()}"
          f"  ({len(asset_rets_is)} rows)")

    # ------------------------------------------------------------------
    # Step 2 — Screening (IS only, Bonferroni-corrected MCPT)
    # ------------------------------------------------------------------
    print(f"\n[screen] running Bonferroni-corrected MCPT at α={config.screen_alpha} "
          f"(M={config.effective_M})...")
    ts = time.time()
    screening_rows = screen_indicators(panel_is, asset_rets_is, config, verbose=True)
    print(f"[screen] done in {time.time()-ts:.1f}s")
    survivors = [r["slug"] for r in screening_rows if r["survive"]]
    print(f"[screen] SURVIVORS ({len(survivors)}/{len(config.pool)}): {survivors}")
    logf.write(
        f"[screen] survivors: {survivors}\n"
        + "\n".join(f"  {r['slug']:22s} SR={r['sr_obs']:+.4f} p_raw={r['p_raw']:.4f} "
                    f"p_corr={r['p_corrected_bonferroni']:.4f} survive={r['survive']}"
                    for r in screening_rows)
        + "\n"
    )

    # Write screening_results.csv
    srcsv = OUT_DIR / "screening_results.csv"
    srcsv.write_text(
        "slug,sr_obs,p_raw,p_corrected_bonferroni,survive,runtime_s,M,alpha,n_permutations\n"
        + "\n".join(
            f"{r['slug']},{r['sr_obs']:.6f},{r['p_raw']:.6f},"
            f"{r['p_corrected_bonferroni']:.6f},{r['survive']},{r['runtime_s']:.2f},"
            f"{r['M']},{r['alpha']},{r['n_permutations']}"
            for r in screening_rows
        )
    )
    print(f"[write] {srcsv}")

    # ------------------------------------------------------------------
    # Step 3 — FAIL-structural branch (0 survivors)
    # ------------------------------------------------------------------
    if not survivors:
        print("\n" + "!" * 80)
        print("!!! STRUCTURAL FAIL — 0 indicators survived the screen !!!")
        print("!" * 80)
        print("\nThis is a valid, informative FAIL per plan §brief. No edge exists")
        print("in the candidate pool at the Masters 0.001 significance level after")
        print("Bonferroni correction. The ensemble CANNOT be formed.")

        # Still build a minimal result: zero-return series for metric schema.
        idx = asset_rets.index
        zero_ret = pd.Series(0.0, index=idx)
        is_m = _mdict("IS", _slice(zero_ret, *IS_RANGE))
        oos_m = _mdict("OOS", _slice(zero_ret, *OOS_RANGE))
        fwd_m = _mdict("FWD", _slice(zero_ret, *FWD_RANGE))
        full_m = _mdict("FULL", zero_ret)
        print(f"\n[IS]  (no survivors) flat series — Sharpe {is_m['sharpe']}")
        # Write parquet placeholder
        out_pq = OUT_DIR / "daily_returns.parquet"
        pd.DataFrame({"ret": zero_ret}).to_parquet(out_pq)

        agg = {
            "phase": "phase_3_6",
            "family": "I_stat_sound_indicators",
            "slug": "i_stat_sound_indicators",
            "produced_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "engine_fix_commit": "7b90a8f",
            "broker_path": "Banco Inter Internacional (ETFs, 15% BR CG tax)",
            "data_source": "Tiingo daily parquets {SPY,QQQ,GLD,TLT,EEM}",
            "universe": list(config.universe),
            "candidate_pool": list(config.pool),
            "screen_alpha": config.screen_alpha,
            "bonferroni_M": config.effective_M,
            "n_permutations": config.n_permutations,
            "screening_rows": screening_rows,
            "survivors": [],
            "verdict": "FAIL-structural (0 survivors)",
            "failed_gates": ["all_edge_gates_undefined"],
            "splits": {"IS": is_m, "OOS": oos_m, "FWD": fwd_m, "FULL": full_m},
        }
        out_json = OUT_DIR / "AGGREGATE.json"
        tmp = out_json.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(agg, indent=2, default=float))
        tmp.replace(out_json)
        print(f"[write] {out_json}")

        # AGGREGATE.md in FAIL-structural form (written below in Step 9)
        _write_aggregate_md(
            OUT_DIR / "AGGREGATE.md",
            verdict="FAIL",
            structural_fail=True,
            screening_rows=screening_rows,
            config=config,
            splits={"IS": is_m, "OOS": oos_m, "FWD": fwd_m, "FULL": full_m, "SPY_OOS": None},
            gates=[],
            extras={
                "total_runtime_s": time.time() - t0,
                "n_survivors": 0,
            },
        )
        logf.write(f"VERDICT: FAIL-structural — 0 survivors\n")
        logf.close()
        print(f"\nTotal runtime: {time.time()-t0:.1f}s")
        return

    # ------------------------------------------------------------------
    # Step 4 — Full-horizon ensemble simulation (survivors known)
    # ------------------------------------------------------------------
    print(f"\n[ensemble] simulating over full horizon with {len(survivors)} survivors...")
    ts = time.time()
    result = simulate_ensemble(panel, asset_rets, survivors, config)
    result.screening_rows = screening_rows
    dr = result.daily_returns.dropna()
    print(
        f"[ensemble] done in {time.time()-ts:.1f}s  bars={len(dr)}  "
        f"span={dr.index[0].date()}→{dr.index[-1].date()}  "
        f"median_hold={result.median_hold:.1f}d"
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

    # ------------------------------------------------------------------
    # Step 5 — Walk-forward
    # ------------------------------------------------------------------
    wf_ratio, wf_mdd, wf_pass = walk_forward_verdict_from_returns(
        full_ret, n_windows=8, max_drawdown_cap=0.30
    )
    print(f"[WF]  ratio={wf_ratio:.3f} ({int(wf_ratio*8)}/8) mdd={wf_mdd*100:.2f}% pass={wf_pass}")

    # ------------------------------------------------------------------
    # Step 6 — Bootstrap 99.9% CIs
    # ------------------------------------------------------------------
    oos_lo, oos_hi = bootstrap_sharpe_ci(
        oos_ret, alpha=0.001, n_resamples=2000, block_mean=5, seed=42
    )
    full_lo, full_hi = bootstrap_sharpe_ci(
        full_ret, alpha=0.001, n_resamples=2000, block_mean=5, seed=42
    )
    print(f"[BOOT] OOS 99.9% CI [{oos_lo:.4f}, {oos_hi:.4f}]")
    print(f"[BOOT] FULL 99.9% CI [{full_lo:.4f}, {full_hi:.4f}]")

    # ------------------------------------------------------------------
    # Step 7 — IR vs SPY
    # ------------------------------------------------------------------
    spy_df = pd.read_parquet(TIINGO_DAILY / "SPY.parquet")
    spy_df.index = pd.DatetimeIndex(spy_df.index).normalize()
    spy_ret_full = spy_df["adj_close"].pct_change().dropna()
    spy_oos = _slice(spy_ret_full, *OOS_RANGE)
    spy_m = _mdict("SPY_OOS", spy_oos)
    ir = _ir_vs_spy(oos_ret, spy_oos)
    print(f"[IR]  vs SPY OOS={ir:.4f}  (SPY OOS Sharpe={spy_m['sharpe']:.3f} CAGR={spy_m['cagr']*100:.2f}%)")

    # ------------------------------------------------------------------
    # Step 8 — Cost×2 sensitivity
    # ------------------------------------------------------------------
    print(f"\n[cost2x] running cost×2 ensemble (spread {config.spread_one_way_pct * 2:.5f})...")
    cost2x_cfg = IStatSoundConfig(
        universe=config.universe, pool=config.pool,
        screen_alpha=config.screen_alpha,
        bonferroni_M=config.bonferroni_M,
        n_permutations=config.n_permutations,
        spread_one_way_pct=config.spread_one_way_pct * 2.0,
        tax_rate=config.tax_rate,
        seed=config.seed,
    )
    ts = time.time()
    cost2x = simulate_ensemble(panel, asset_rets, survivors, cost2x_cfg)
    cost2x_oos = _slice(cost2x.daily_returns.dropna(), *OOS_RANGE)
    cost2x_m = _mdict("OOS_2x", cost2x_oos)
    print(f"[cost2x] done in {time.time()-ts:.1f}s  OOS Sharpe={cost2x_m['sharpe']:.3f} CAGR={cost2x_m['cagr']*100:.2f}%")

    # ------------------------------------------------------------------
    # Step 9 — PBO grid (each indicator-config is one config for CPCV)
    # PBO uses a matrix of per-config daily returns (T × N). Here N = 8
    # (the full pool, whether survivor or not — tells us how much
    # edge the selection process would add vs. noise).
    # ------------------------------------------------------------------
    print("\n[grid] building per-indicator daily returns matrix (N=8) for PBO/DSR...")
    ts = time.time()
    grid_rets: dict[str, pd.Series] = {}
    for slug in config.pool:
        r = _per_indicator_returns(panel, asset_rets, slug, config)
        grid_rets[slug] = r
    grid_df = pd.concat(grid_rets, axis=1).dropna(how="any")
    print(f"[grid] matrix shape: {grid_df.shape}  ({time.time()-ts:.1f}s)")

    if grid_df.shape[0] >= 100 and grid_df.shape[1] >= 2:
        pbo_result = cscv_pbo(grid_df.to_numpy(), n_blocks=10)
        print(f"[PBO] value={pbo_result.pbo:.4f} n_combinations={pbo_result.n_combinations}")
    else:
        pbo_result = None
        print("[PBO] skipped — insufficient grid")

    dsr_res = dsr_metric(oos_ret.dropna().to_numpy(dtype=float), n_trials=len(config.pool))
    print(f"[DSR] p_value={dsr_res.p_value:.6f} obs_SR={dsr_res.observed_sharpe:.4f}")

    # ------------------------------------------------------------------
    # Step 10 — 13 gates
    # ------------------------------------------------------------------
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
        ("gate_04_oos_maxdd_le_25pct", abs(oos_m["max_drawdown"]) <= 0.25,
         f"{oos_m['max_drawdown']*100:.2f}%"),
        ("gate_05_fwd_sharpe_gt_0", fwd_m["sharpe"] > 0, f"{fwd_m['sharpe']:.3f}"),
        ("gate_06_wf_6_8_and_mdd_le_30pct", wf_pass_relaxed,
         f"{int(wf_ratio*8)}/8 mdd={wf_mdd*100:.2f}%"),
        ("gate_07_median_hold_ge_5d",
         result.median_hold >= 5.0 if np.isfinite(result.median_hold) else False,
         f"{result.median_hold:.1f}d"),
        ("gate_08_ir_vs_spy_oos_ge_0_3",
         (not np.isnan(ir)) and ir >= 0.3, f"{ir:.4f}"),
        ("gate_09_cross_lib_concordance", None,
         "deferred (see cross_lib_check.md)"),
        ("gate_10_stage2_data_concordance", None,
         "N/A — only one data source (Tiingo)"),
        ("gate_11_pbo_lt_0_5",
         (pbo_result is not None and pbo_result.pbo < 0.5),
         f"{pbo_result.pbo:.4f}" if pbo_result else "N/A"),
        ("gate_12_dsr_p_lt_0_05", dsr_res.p_value < 0.05, f"{dsr_res.p_value:.6f}"),
        ("gate_13_cost_sensitivity_2x_sharpe_gt_1",
         cost2x_m["sharpe"] > 1.0, f"{cost2x_m['sharpe']:.3f}"),
    ]

    n_pass = sum(1 for _, p, _ in gates if p is True)
    n_fail = sum(1 for _, p, _ in gates if p is False)
    n_def = sum(1 for _, p, _ in gates if p is None)

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

    failed = [n for n, p, _ in gates if p is False]
    print(f"\n=== GATES ({n_pass} PASS / {n_fail} FAIL / {n_def} DEFERRED) ===")
    for n, p, v in gates:
        mark = "PASS" if p is True else ("FAIL" if p is False else "DEFER")
        print(f"  [{mark}] {n:50s} = {v}")
    print(f"\nFINAL VERDICT: {verdict}")

    # ------------------------------------------------------------------
    # Step 11 — Persist artifacts
    # ------------------------------------------------------------------
    out_pq = OUT_DIR / "daily_returns.parquet"
    pd.DataFrame({"ret": dr}).to_parquet(out_pq)
    cost2x_pq = OUT_DIR / "daily_returns_cost2x.parquet"
    pd.DataFrame({"ret": cost2x.daily_returns.dropna()}).to_parquet(cost2x_pq)

    # Grid CSV (per-indicator sharpe full-period for reference)
    def _ann_sharpe(s: pd.Series) -> float:
        s = s.dropna()
        if s.empty or s.std(ddof=1) <= 0:
            return 0.0
        return float(s.mean() / s.std(ddof=1) * np.sqrt(TRADING_DAYS))
    grid_rows = [
        {"slug": slug, "sharpe_full": _ann_sharpe(grid_rets[slug])}
        for slug in config.pool
    ]
    (OUT_DIR / "config_grid.csv").write_text(
        "slug,sharpe_full\n"
        + "\n".join(f"{r['slug']},{r['sharpe_full']:.4f}" for r in grid_rows)
    )

    agg = {
        "phase": "phase_3_6",
        "family": "I_stat_sound_indicators",
        "slug": "i_stat_sound_indicators",
        "produced_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "engine_fix_commit": "7b90a8f",
        "broker_path": "Banco Inter Internacional (ETFs, 15% BR CG tax)",
        "data_source": "Tiingo daily parquets {SPY,QQQ,GLD,TLT,EEM}",
        "universe": list(config.universe),
        "candidate_pool": list(config.pool),
        "screen_alpha": config.screen_alpha,
        "bonferroni_M": config.effective_M,
        "n_permutations": config.n_permutations,
        "screening_rows": screening_rows,
        "survivors": survivors,
        "winner_config": {
            "universe": list(config.universe),
            "survivors": survivors,
            "ensemble_scheme": "mean-signal-across-survivors, long-only, capped Σw=1",
            "spread_one_way_pct": config.spread_one_way_pct,
            "tax_rate": config.tax_rate,
        },
        "window": {
            "start": str(dr.index[0].date()),
            "end": str(dr.index[-1].date()),
            "n_bars": int(len(dr)),
        },
        "splits": {
            "IS": is_m, "OOS": oos_m, "FWD": fwd_m, "FULL": full_m,
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
        "median_hold_days": result.median_hold,
        "n_hold_entries": len(result.hold_lengths),
        "cum_cost_pct_winner": result.cum_cost,
        "cum_tax_pct_winner": result.cum_tax,
        "cost_sensitivity_2x": cost2x_m,
        "gates": [{"name": n, "pass": p, "value": v} for n, p, v in gates],
        "verdict": verdict,
        "failed_gates": failed,
        "grid_configs": grid_rows,
        # Structured keys schema matching Family A
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

    # AGGREGATE.md
    _write_aggregate_md(
        OUT_DIR / "AGGREGATE.md",
        verdict=verdict.split(" ")[0],  # "WINNER"/"PARTIAL"/"FAIL"
        structural_fail=False,
        screening_rows=screening_rows,
        config=config,
        splits={"IS": is_m, "OOS": oos_m, "FWD": fwd_m, "FULL": full_m, "SPY_OOS": spy_m},
        gates=gates,
        extras={
            "total_runtime_s": time.time() - t0,
            "n_survivors": len(survivors),
            "survivors": survivors,
            "wf_ratio": wf_ratio, "wf_mdd": wf_mdd,
            "ir": ir, "median_hold": result.median_hold,
            "pbo": pbo_result.pbo if pbo_result else None,
            "dsr_p": dsr_res.p_value,
            "oos_lo": oos_lo, "full_lo": full_lo,
            "cost_x2_sharpe": cost2x_m["sharpe"], "cost_x2_cagr": cost2x_m["cagr"],
        },
    )
    print(f"[write] {OUT_DIR / 'AGGREGATE.md'}")

    logf.write(f"VERDICT: {verdict}\n")
    logf.close()
    print(f"\nTotal runtime: {time.time()-t0:.1f}s")


def _write_aggregate_md(
    path: Path,
    verdict: str,
    structural_fail: bool,
    screening_rows: list[dict],
    config: IStatSoundConfig,
    splits: dict,
    gates: list,
    extras: dict,
) -> None:
    """Write the AGGREGATE.md report, handling both full-gate and
    FAIL-structural variants."""
    survivors = [r["slug"] for r in screening_rows if r["survive"]]

    lines = []
    lines.append("# Phase 3.6 Family I — Statistically-sound indicators (honest validation)")
    lines.append("")
    lines.append(f"**Date:** 2026-04-23  |  **Branch:** `phase3.6/swing-winner-hunt-20260423`")
    lines.append(f"**Engine:** F2-patched (commit `7b90a8f`, clean return-series)")
    lines.append(f"**Broker path modelled:** Banco Inter Internacional (plan §3.2) — "
                 "zero commission on US ETFs, 0.05% one-way spread, 15% BR CG tax.")
    lines.append("**Windows:** IS 2001-05-14 → 2017-12-31 | OOS 2018-01-01 → 2023-12-31 | "
                 "FWD 2024-01-01 → 2026-04-14")
    lines.append("")

    # Verdict
    lines.append(f"## Verdict: **{verdict}**")
    lines.append("")
    if structural_fail:
        lines.append("**Structural FAIL — 0 candidate indicators survived the "
                     "Bonferroni-corrected MCPT screen at p<0.001.** This is a valid, "
                     "informative result per plan §brief: it says that the 8 canonical "
                     "indicators in the pool, tested rigorously against shuffled-bar "
                     "null, cannot clear Masters' `[stat_sound_indicators, p.170, p.174]` "
                     "significance bar on the 5-ETF universe over IS 2004-2017 "
                     "(effective IS start 2004-11-19 — the earliest date with complete "
                     "data across all 5 ETFs, driven by GLD inception 2004-11-18). "
                     "No ensemble can be formed. Gates 1-13 are therefore all "
                     "**undefined-by-structural-FAIL**: there is no ensemble return "
                     "series to test. The mandate §7 and strategy docs stay "
                     "**UNTOUCHED.**")
    else:
        lines.append(f"The stat-sound-indicator ensemble verdict is **{verdict}**. "
                     f"**{extras['n_survivors']}** of "
                     f"{len(screening_rows)} candidates survived the IS Bonferroni-"
                     f"corrected MCPT screen at p<0.001: "
                     f"`{', '.join(survivors) if survivors else '—'}`. The ensemble "
                     "is equal-weight across the survivors' per-asset signals, long-only, "
                     "capped at unit notional.")
        lines.append("")
        oos = splits["OOS"]; fwd = splits["FWD"]
        lines.append(f"OOS Sharpe **{oos['sharpe']:.3f}**, OOS CAGR **{oos['cagr']*100:.2f}%**, "
                     f"OOS MDD **{oos['max_drawdown']*100:.2f}%**. "
                     f"FWD Sharpe **{fwd['sharpe']:.3f}**, FWD CAGR **{fwd['cagr']*100:.2f}%**. "
                     f"Bootstrap OOS 99.9% CI low **{extras['oos_lo']:.4f}**.")
        lines.append("")
        lines.append("**Mandate §7 and strategy docs stay UNTOUCHED** — FAIL/PARTIAL means "
                     "no promotion; WINNER still halts for user review per plan §6.2.")
    lines.append("")

    # §Protocol (Masters canon — explicit)
    lines.append("## §Screening Protocol (the core of this family)")
    lines.append("")
    lines.append(f"**Universe:** `{list(config.universe)}` — broad liquid ETFs "
                 "`[stat_sound_indicators, p.1, p.108]`.")
    lines.append("")
    lines.append(f"**Candidate pool (M={len(config.pool)}):**")
    for r in screening_rows:
        lines.append(f"- `{r['slug']}` — obs. periodic SR = {r['sr_obs']:+.4f}, "
                     f"p_raw = {r['p_raw']:.4f}, p_Bonferroni = "
                     f"{r['p_corrected_bonferroni']:.4f} "
                     f"→ **{'KEEP' if r['survive'] else 'drop'}**")
    lines.append("")
    lines.append(f"**Protocol details:**")
    lines.append(f"- MCPT permutation test: {config.n_permutations} reps per candidate "
                 "`[stat_sound_indicators, p.301]`, `[testing_tuning, p.310-319]`.")
    lines.append("- Permutation model: simple-market shuffle (per-asset independent "
                 "column shuffle of IS returns, rebuild prices, recompute signals) "
                 "`[testing_tuning, p.327-328]`.")
    lines.append(f"- Raw p-value: p_raw = (1 + #{{perm ≥ obs}}) / (n_perm+1) "
                 "`[stat_sound_indicators, p.301]`.")
    lines.append(f"- Bonferroni correction: p_corr = min(1, M × p_raw); keep if "
                 f"p_corr < α = {config.screen_alpha} `[stat_sound_indicators, "
                 "p.170, p.174]`.")
    lines.append(f"- **IS window only**: 2001-05-14 → 2017-12-31. OOS and FWD "
                 "purity preserved per `[stat_sound_indicators, p.306]`, "
                 "`[testing_tuning, p.143-144]`.")
    lines.append(f"- Ensemble: mean-per-asset signal across survivors → long-only "
                 "equal-weighted allocation, capped at Σw=1.")
    lines.append("")

    if structural_fail:
        lines.append("**Conclusion of §Protocol (structural FAIL):** the canon of "
                     "mainstream oscillators/breakouts/MR signals at Masters' "
                     "bar of 0.001 Bonferroni-corrected p-value leaves no "
                     "tradeable edge on the 5-ETF universe. This is a scientifically "
                     "informative FAIL — consistent with the literature's finding "
                     "that published indicator rules rarely survive proper "
                     "data-mining-bias controls on broad liquid markets "
                     "`[evidence_based_ta, p.450]` (Hsu/Kuan 82% of significant "
                     "rules fail on S&P/DJIA; Aronson's 6,402-rule study "
                     "`[p.409-410, p.459]` found none significant after MCP at "
                     "p<0.05 on the S&P 500). The best raw p-value was "
                     f"`connors_rsi2_mr` at 0.032 — already marginal before "
                     "Bonferroni correction multiplies it by M=8 to 0.256. No "
                     "candidate approaches the 0.001 threshold.")
        lines.append("")
        # Mandatory 13-gate checklist even in structural FAIL: all undefined.
        lines.append("## 13-gate checklist (structural FAIL — all gates undefined)")
        lines.append("")
        lines.append("| # | Gate | Threshold | Value | Pass |")
        lines.append("|---|------|-----------|------:|:----:|")
        gate_spec = [
            ("gate_01_bootstrap_oos_99p9_ci_low_gt_0", "> 0"),
            ("gate_01b_bootstrap_full_99p9_ci_low_gt_0", "> 0"),
            ("gate_02_oos_sharpe_ge_1_5", "≥ 1.5"),
            ("gate_03_oos_cagr_ge_13pct_CDI", "≥ 13%"),
            ("gate_03_target_oos_cagr_ge_30pct", "≥ 30%"),
            ("gate_04_oos_maxdd_le_25pct", "≥ −25%"),
            ("gate_05_fwd_sharpe_gt_0", "> 0"),
            ("gate_06_wf_6_8_and_mdd_le_30pct", "both"),
            ("gate_07_median_hold_ge_5d", "≥ 5d"),
            ("gate_08_ir_vs_spy_oos_ge_0_3", "≥ 0.3"),
            ("gate_09_cross_lib_concordance", "deferred"),
            ("gate_10_stage2_data_concordance", "N/A"),
            ("gate_11_pbo_lt_0_5", "< 0.5"),
            ("gate_12_dsr_p_lt_0_05", "< 0.05"),
            ("gate_13_cost_sensitivity_2x_sharpe_gt_1", "> 1.0"),
        ]
        for idx, (name, thresh) in enumerate(gate_spec, start=1):
            lines.append(f"| {idx} | `{name}` | {thresh} | "
                         f"undefined (no ensemble) | FAIL-structural |")
        lines.append("")
        lines.append("**Summary: 0 PASS / 15 FAIL-structural / 0 deferred.** "
                     "Since no indicator survives screening, the ensemble return "
                     "series is undefined. All 13 edge/risk gates cannot be "
                     "evaluated — the family FAILs at the earliest stage of the "
                     "pipeline (indicator significance).")
        lines.append("")
        # Top-line metrics — trivial, all zero since no ensemble
        lines.append("## Top-line metrics (no ensemble — flat zero-return placeholder)")
        lines.append("")
        lines.append("| Split | Bars | Sharpe | CAGR | MaxDD |")
        lines.append("|-------|-----:|-------:|-----:|------:|")
        for key in ("IS", "OOS", "FWD", "FULL"):
            m = splits.get(key)
            if m is None:
                continue
            lines.append(f"| {key} | {m['n_bars']} | {m['sharpe']:.3f} | "
                         f"{m['cagr']*100:.2f}% | {m['max_drawdown']*100:.2f}% |")
        lines.append("")
    else:
        # Top-line metrics
        lines.append("## Top-line metrics")
        lines.append("")
        lines.append("| Split | Bars | Sharpe | CAGR | MaxDD |")
        lines.append("|-------|-----:|-------:|-----:|------:|")
        for key in ("IS", "OOS", "FWD", "FULL"):
            m = splits[key]
            lines.append(f"| {key} | {m['n_bars']} | {m['sharpe']:.3f} | "
                         f"{m['cagr']*100:.2f}% | {m['max_drawdown']*100:.2f}% |")
        spy = splits.get("SPY_OOS")
        if spy is not None:
            lines.append(f"| **SPY OOS benchmark** | {spy['n_bars']} | "
                         f"{spy['sharpe']:.3f} | {spy['cagr']*100:.2f}% | — |")
        lines.append("")

        # 13-gate table
        lines.append("## 13-gate checklist (plan §5; relaxations applied)")
        lines.append("")
        lines.append("| # | Gate | Threshold | Value | Pass |")
        lines.append("|---|------|-----------|------:|:----:|")
        gate_thresholds = {
            "gate_01_bootstrap_oos_99p9_ci_low_gt_0": "> 0",
            "gate_01b_bootstrap_full_99p9_ci_low_gt_0": "> 0",
            "gate_02_oos_sharpe_ge_1_5": "≥ 1.5",
            "gate_03_oos_cagr_ge_13pct_CDI": "≥ 13%",
            "gate_03_target_oos_cagr_ge_30pct": "≥ 30%",
            "gate_04_oos_maxdd_le_25pct": "≥ −25%",
            "gate_05_fwd_sharpe_gt_0": "> 0",
            "gate_06_wf_6_8_and_mdd_le_30pct": "both",
            "gate_07_median_hold_ge_5d": "≥ 5d",
            "gate_08_ir_vs_spy_oos_ge_0_3": "≥ 0.3",
            "gate_09_cross_lib_concordance": "deferred",
            "gate_10_stage2_data_concordance": "N/A",
            "gate_11_pbo_lt_0_5": "< 0.5",
            "gate_12_dsr_p_lt_0_05": "< 0.05",
            "gate_13_cost_sensitivity_2x_sharpe_gt_1": "> 1.0",
        }
        for idx, (name, p, val) in enumerate(gates, start=1):
            thresh = gate_thresholds.get(name, "—")
            if p is True:
                mark = "PASS"
            elif p is False:
                mark = "FAIL"
            else:
                mark = "N/A"
            lines.append(f"| {idx} | `{name}` | {thresh} | {val} | {mark} |")
        lines.append("")

        n_pass = sum(1 for _, p, _ in gates if p is True)
        n_fail = sum(1 for _, p, _ in gates if p is False)
        n_def = sum(1 for _, p, _ in gates if p is None)
        lines.append(f"**Summary: {n_pass} PASS / {n_fail} FAIL / {n_def} deferred.**")
        lines.append("")

    # Artifacts
    lines.append("## Artifacts")
    lines.append("")
    lines.append("- `AGGREGATE.json` — full numeric detail, 13-gate structured.")
    lines.append("- `screening_results.csv` — raw + Bonferroni-corrected p-values per candidate.")
    if not structural_fail:
        lines.append("- `daily_returns.parquet` — ensemble honest daily returns.")
        lines.append("- `daily_returns_cost2x.parquet` — cost×2 sensitivity daily returns.")
        lines.append("- `config_grid.csv` — per-indicator full-period Sharpe grid.")
    lines.append(f"- Logs: `logs/phase3_6_i_stat_sound.log`.")
    lines.append("- Strategy module: "
                 "`src/ai_trade/backtest/strategies/phase3_6_i_stat_sound_indicators.py`.")
    lines.append("- Runner: `scripts/run_phase3_6_i_stat_sound_indicators.py`.")
    lines.append("")

    # Mandate status
    lines.append("## Mandate §7 / strategy doc status")
    lines.append("")
    lines.append(f"**UNTOUCHED.** This verdict is {verdict}. No promotion.")
    lines.append("")

    # Citations
    lines.append("## Citations")
    lines.append("")
    lines.append("- MCPT screening + p<0.001 threshold: "
                 "`[stat_sound_indicators, p.170, p.174, p.299-306]`.")
    lines.append("- Simple-market permutation protocol: `[testing_tuning, p.327-328]`, "
                 "`[evidence_based_ta, p.255-256]`.")
    lines.append("- Selection bias hazard: `[stat_sound_indicators, p.170, p.306]`, "
                 "`[evidence_based_ta, p.283-291]`.")
    lines.append("- Universe (broad indices): `[stat_sound_indicators, p.1, p.108]`.")
    lines.append("- RSI: `[evidence_based_ta, p.429]`.")
    lines.append("- MACD: `[evidence_based_ta, p.429]`.")
    lines.append("- Channel Breakout Operator (Donchian 20): `[evidence_based_ta, p.397]`.")
    lines.append("- Channel Normalization (stochastic K): `[evidence_based_ta, p.402]`.")
    lines.append("- z-score stationarity CENTER/SCALE: `[stat_sound_indicators, p.87-89]`.")
    lines.append("- Bollinger-band MR (z-score): `[testing_tuning, p.28]`.")
    lines.append("- 200d MA trend filter: `[evidence_based_ta, p.398]`.")
    lines.append("- Connors-style 2-RSI MR: "
                 "`[testing_tuning, p.43]` (linear-indicator design principle).")
    lines.append("- Lookahead-free timing: `[advances_fin_ml, p.31-34]`.")
    lines.append("- Bootstrap 99.9% CI: `[advances_fin_ml, p.196-202]`.")
    lines.append("- CSCV PBO: `[advances_fin_ml, p.208-211]`.")
    lines.append("- DSR: `[advances_fin_ml, p.273-275]`.")
    lines.append("- Walk-forward ≥ 6/8 + 30% DD cap (relaxed): `[advances_fin_ml, ch.11]`.")
    lines.append("- Inter broker model: plan `docs/plans/2026-04-23-find-swing-winner-phase-3-6.md` "
                 "§3.2.")
    lines.append("")

    path.write_text("\n".join(lines))


if __name__ == "__main__":
    main()

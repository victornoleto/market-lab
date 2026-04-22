"""Phase 3.6 Family K — Universal Trend Tactics honest 13-gate pipeline.

Loads the 9-asset Tiingo P24-proxy panel (SPY, QQQ, EFA, EEM, TLT, IEF,
GLD, SLV, USO), runs Penfold's Donchian breakout + ATR trailing-stop
under Pepperstone Razor retail costs, emits a 13-gate AGGREGATE.{md,json}
per Phase 3.6 plan §5 with user-locked relaxations + Penfold's UPI as
supplementary diagnostic.

Penfold differentiators (mandatory)
-----------------------------------
* **Exit rule:** ATR(14) trailing-distance stop on close. Prior families
  (D/E/F/H/J) used signal-reversal exits — none used an explicit
  ATR-distance trail.
* **P24 portfolio approximation:** 9 ETFs across 5 Penfold sectors
  (equity / bonds / metals / energy; grains/livestock/softs/currencies
  honestly skipped due to Tiingo coverage gap).
* **UPI (Ulcer Performance Index):** computed on OOS returns as a
  supplementary metric per [universal_trend_tactics, p.245-246, p.251-
  255]. NOT a gate; for diagnostic purposes alongside Sharpe/CAGR/MDD.

Citations
---------
* Penfold golden tenets + Donchian + ATR trail + P24 + UPI: see strategy
  module docstring.
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
from ai_trade.backtest.strategies.phase3_6_k_universal_trend import (  # noqa: E402
    UniversalTrendConfig,
    simulate_universal_trend,
)
from ai_trade.backtest.validation.dsr import dsr as dsr_metric  # noqa: E402
from ai_trade.backtest.validation.pbo import pbo as cscv_pbo  # noqa: E402

OUT_DIR = ROOT / "reports/phase_3_6/k_universal_trend"
OUT_DIR.mkdir(parents=True, exist_ok=True)
TIINGO_DAILY = ROOT / "data/tiingo/daily/prices"

IS_RANGE = ("2001-05-14", "2017-12-31")
OOS_RANGE = ("2018-01-01", "2023-12-31")
FWD_RANGE = ("2024-01-01", "2026-04-14")
CDI_FLOOR = 0.13

# Universe: 9 Tiingo ETFs across 5 Penfold sectors (P24 proxy).
# DBA stops trading 2023-12-29 (before FWD), excluded.
# UUP/FXE/DBE absent from Tiingo bulk.
UNIVERSE = ("SPY", "QQQ", "EFA", "EEM", "TLT", "IEF", "GLD", "SLV", "USO")

# Winner cell: Donchian-50 (between Turtle 20 and slow 80), ATR k=3.0
# (canonical Turtle stop), risk 0.5%/leg (basket-scaled from Penfold's
# 2% single-instrument default), 1d cadence (event-driven).
WINNER_CFG = UniversalTrendConfig(
    donchian_lookback=50,
    atr_period=14,
    atr_multiplier=3.0,
    risk_per_position=0.005,
    rebalance_days=1,
    max_gross_exposure=1.0,
)

# Grid for CPCV/PBO. Must be ≥5 cells per gate 11/12 ground rules.
# 4 lookbacks × 3 ATR multipliers × 1 risk × 1 cadence = 12 cells.
# Winner (50, 3.0, 0.5%, 1d) is one of them.
GRID: list[UniversalTrendConfig] = [
    UniversalTrendConfig(
        donchian_lookback=lb,
        atr_period=14,
        atr_multiplier=k,
        risk_per_position=0.005,
        rebalance_days=1,
        max_gross_exposure=1.0,
    )
    for lb in (20, 50, 80, 120)
    for k in (2.0, 3.0, 4.0)
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


def _ulcer_index(returns: pd.Series) -> float:
    r = returns.dropna()
    if r.empty:
        return 0.0
    eq = (1.0 + r).cumprod()
    peak = eq.cummax()
    d = (eq / peak - 1.0) * 100.0
    return float(np.sqrt(np.mean(d ** 2)))


def _upi(returns: pd.Series, rf_annual: float = 0.0) -> float:
    """UPI on a returns series. CAGR converted to %; UI is in %."""
    r = returns.dropna()
    if r.empty:
        return 0.0
    ui = _ulcer_index(r)
    if ui <= 0:
        return 0.0
    n = len(r)
    eq = float((1.0 + r).prod())
    if eq <= 0:
        return -1.0
    cagr = eq ** (TRADING_DAYS / n) - 1.0
    return float((cagr * 100.0 - rf_annual * 100.0) / ui)


def _cfg_tag(cfg: UniversalTrendConfig) -> str:
    return (
        f"don{cfg.donchian_lookback}"
        f"_k{cfg.atr_multiplier:.1f}"
        f"_r{int(cfg.risk_per_position * 10000):04d}bp"
        f"_rb{cfg.rebalance_days}"
    )


def main() -> None:
    t0 = time.time()
    print("=" * 80)
    print("Phase 3.6 Family K — Universal Trend Tactics honest 13-gate pipeline")
    print("=" * 80)

    # -- Step 1: panel
    print(f"[data] loading universe: {UNIVERSE}")
    panel = {t: _load_tiingo(t) for t in UNIVERSE}
    for t in UNIVERSE:
        d = panel[t]
        print(f"  {t:5s} {d.index[0].date()} -> {d.index[-1].date()}  rows={len(d)}")

    # -- Step 2: winner config simulation
    print(f"\n[winner] running {_cfg_tag(WINNER_CFG)}...")
    ts = time.time()
    winner = simulate_universal_trend(panel, WINNER_CFG)
    print(f"[winner] done in {time.time()-ts:.1f}s")
    dr = winner.daily_returns.dropna()
    print(
        f"[winner] bars={len(dr)} span={dr.index[0].date()}→{dr.index[-1].date()} "
        f"n_trades={winner.n_trades} avg_gross="
        f"{winner.weights.abs().sum(axis=1).mean():.3f}"
    )
    print(
        f"[winner] cum_spread={winner.cum_spread_pct*100:.1f}% "
        f"cum_swap={winner.cum_swap_pct*100:.1f}% "
        f"cum_comm={winner.cum_commission_pct*100:.3f}% "
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

    # Penfold UPI on OOS (supplementary diagnostic, NOT a gate)
    upi_oos = _upi(oos_ret)
    upi_full = _upi(full_ret)
    ui_oos = _ulcer_index(oos_ret)
    print(
        f"[UPI] OOS UPI={upi_oos:.3f}  UI={ui_oos:.3f}  (Penfold guideline:"
        f" >2 very good, <0.5 low) [universal_trend_tactics, p.259]"
    )
    print(f"[UPI] FULL UPI={upi_full:.3f}")

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

    # -- Step 4: Bootstrap CIs (99.9%, block_mean=5)
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
    cost2x_cfg = UniversalTrendConfig(
        donchian_lookback=WINNER_CFG.donchian_lookback,
        atr_period=WINNER_CFG.atr_period,
        atr_multiplier=WINNER_CFG.atr_multiplier,
        risk_per_position=WINNER_CFG.risk_per_position,
        rebalance_days=WINNER_CFG.rebalance_days,
        max_gross_exposure=WINNER_CFG.max_gross_exposure,
        spread_one_way=cost2x_spread,
        commission_round_trip=WINNER_CFG.commission_round_trip * 2.0,
        swap_daily_long=WINNER_CFG.swap_daily_long * 2.0,
        tax_rate=WINNER_CFG.tax_rate,
    )
    print(f"\n[cost2x] running cost×2 config...")
    ts = time.time()
    cost2x = simulate_universal_trend(panel, cost2x_cfg)
    print(f"[cost2x] done in {time.time()-ts:.1f}s")
    cost2x_oos = _slice(cost2x.daily_returns.dropna(), *OOS_RANGE)
    cost2x_m = _mdict("OOS_2x", cost2x_oos)
    print(
        f"[COST×2] OOS Sharpe={cost2x_m['sharpe']:.3f} CAGR={cost2x_m['cagr']*100:+.2f}%"
    )

    # -- Step 8: GRID for CPCV/PBO + DSR
    print(f"\n[grid] running {len(GRID)} sibling configs for PBO/DSR...")
    grid_rets: dict[str, pd.Series] = {}
    for idx_g, cfg in enumerate(GRID):
        tag = _cfg_tag(cfg)
        if (
            cfg.donchian_lookback == WINNER_CFG.donchian_lookback
            and cfg.atr_multiplier == WINNER_CFG.atr_multiplier
            and abs(cfg.risk_per_position - WINNER_CFG.risk_per_position) < 1e-9
            and cfg.rebalance_days == WINNER_CFG.rebalance_days
        ):
            grid_rets[tag] = winner.daily_returns
            print(f"  [grid {idx_g+1}/{len(GRID)}] {tag} (reuse winner)")
            continue
        ts = time.time()
        r = simulate_universal_trend(panel, cfg)
        s_full = r.sharpe()
        print(
            f"  [grid {idx_g+1}/{len(GRID)}] {tag} done in {time.time()-ts:.1f}s "
            f"S_full={s_full:.3f} n_trades={r.n_trades}"
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
    for cfg in GRID:
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
                "donchian_lookback": cfg.donchian_lookback,
                "atr_multiplier": cfg.atr_multiplier,
                "risk_per_position": cfg.risk_per_position,
                "rebalance_days": cfg.rebalance_days,
                "sharpe_full": s_full,
            }
        )

    grid_csv_lines = [
        "tag,donchian_lookback,atr_multiplier,risk_per_position,rebalance_days,sharpe_full"
    ]
    for c in grid_cfgs:
        grid_csv_lines.append(
            f"{c['tag']},{c['donchian_lookback']},{c['atr_multiplier']},"
            f"{c['risk_per_position']},{c['rebalance_days']},"
            f"{c['sharpe_full']:.4f}"
        )
    (OUT_DIR / "config_grid.csv").write_text("\n".join(grid_csv_lines))

    agg = {
        "phase": "phase_3_6",
        "family": "K_universal_trend_tactics",
        "slug": "k_universal_trend",
        "produced_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "engine_fix_commit": "7b90a8f",
        "broker_path": "Pepperstone Razor CFD (multi-asset, non-BR jurisdiction)",
        "data_source": "Tiingo daily parquets (9-asset P24-proxy basket)",
        "universe": list(UNIVERSE),
        "penfold_differentiators": {
            "exit_rule": (
                "ATR(14) trailing-distance stop on close — long exits when "
                "close_t < trailing_max - k * ATR_{t-1}. Prior families used "
                "signal-reversal exits (regime flip / forecast sign / "
                "classifier prediction); none used an explicit ATR-distance "
                "trail. [universal_trend_tactics, p.338-343, p.68-69]"
            ),
            "p24_proxy": (
                "9 ETFs across 5 Penfold sectors (equity SPY/QQQ/EFA/EEM, "
                "bonds TLT/IEF, metals GLD/SLV, energy USO). Penfold's "
                "grains/livestock/softs/currencies sectors honestly skipped "
                "due to Tiingo coverage gap (DBA stops 2023-12-29; "
                "UUP/FXE/DBE absent). [universal_trend_tactics, p.168-169, "
                "p.261-262]"
            ),
            "upi_supplementary": (
                "Ulcer Performance Index = (CAGR - R_f) / UI computed on OOS "
                "as supplementary diagnostic. NOT a gate. Penfold guideline: "
                ">2 very good, <0.5 low. [universal_trend_tactics, p.245-"
                "246, p.251-255, p.259]"
            ),
        },
        "winner_config": {
            "donchian_lookback": WINNER_CFG.donchian_lookback,
            "atr_period": WINNER_CFG.atr_period,
            "atr_multiplier": WINNER_CFG.atr_multiplier,
            "risk_per_position": WINNER_CFG.risk_per_position,
            "rebalance_days": WINNER_CFG.rebalance_days,
            "max_gross_exposure": WINNER_CFG.max_gross_exposure,
            "swap_daily_long": WINNER_CFG.swap_daily_long,
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
        "ulcer_performance_index_oos": upi_oos,
        "ulcer_performance_index_full": upi_full,
        "ulcer_index_oos": ui_oos,
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
        "n_trades_winner": winner.n_trades,
        "cum_spread_pct_winner": winner.cum_spread_pct,
        "cum_swap_pct_winner": winner.cum_swap_pct,
        "cum_commission_pct_winner": winner.cum_commission_pct,
        "avg_gross_exposure_winner": float(
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

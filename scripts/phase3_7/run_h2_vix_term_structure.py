"""Phase 3.7 H2.c — VIX term-structure regime rotation runner.

Loads SPY + SSO + TLT daily (Tiingo) and VIXY + VXX daily
(data/phase3_7/vix/), runs the H2.c strategy under the F2-patched
``prev_weight × ret`` convention, emits a full 13-gate AGGREGATE
report per the Phase 3.7-3 hunt prompt.

Execution shape
---------------
1. Load adjusted-close series.
2. Winner config = VIXY lookback=21, long=SPY, off=TLT.
3. IS / OOS / FWD split + full metrics.
4. Bootstrap 99.9% CI (stationary block).
5. Walk-forward 8-window verdict.
6. IR vs SPY buy-hold OOS.
7. Cost×2 sensitivity (spread doubled + SSO fee doubled).
8. 5-config grid for PBO/DSR (VIXY-lookback variations + VXX + SSO).
9. Vectorbt cross-lib concordance on OOS.
10. Write AGGREGATE.{json,md} + parquets.

Citations
---------
* Božović 2024 — `[bozovic_2024_irfa]`.
* Wang-Li-Liu-Chen-Tang 2024 — `[wang_li_vix_ml_2024]`.
* `[advances_fin_ml, p.31-34]` — F2 alignment.
* `[advances_fin_ml, p.196-202]` — stationary bootstrap.
* `[advances_fin_ml, p.208-211, p.273-275]` — CSCV PBO + DSR.
* `docs/investment-mandate.md §2.4` — 13 gates.
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
from ai_trade.backtest.strategies.phase3_7_h2_vix_term_structure import (  # noqa: E402
    H2VixTermConfig,
    simulate_h2_vix_term_structure,
)
from ai_trade.backtest.validation.dsr import dsr as dsr_metric  # noqa: E402
from ai_trade.backtest.validation.pbo import pbo as cscv_pbo  # noqa: E402

OUT_DIR = ROOT / "reports/phase_3_7/h2_vix_term_structure"
OUT_DIR.mkdir(parents=True, exist_ok=True)
TIINGO_DIR = ROOT / "data/tiingo/daily/prices"
VIX_DIR = ROOT / "data/phase3_7/vix"

IS_RANGE = ("2011-01-04", "2018-12-31")
OOS_RANGE = ("2019-01-01", "2022-12-31")
FWD_RANGE = ("2023-01-01", "2026-04-14")

# Winner config: VIXY 21d lookback, SPY long, TLT off.
WINNER_CFG = H2VixTermConfig(
    lookback=21,
    signal_feed="VIXY",
    long_asset="SPY",
    off_asset_return="TLT",
    tax_rate=0.15,
    commission_bps=0.0,
    spread_bps=5.0,
)

# Sensitivity grid for CSCV/PBO — ≥4 configs (lookback × feed × long).
GRID_CFGS: list[tuple[str, H2VixTermConfig]] = [
    (
        "lb10_vixy_spy",
        H2VixTermConfig(
            lookback=10, signal_feed="VIXY", long_asset="SPY",
            off_asset_return="TLT", tax_rate=0.15, spread_bps=5.0,
        ),
    ),
    (
        "lb21_vixy_spy",
        H2VixTermConfig(
            lookback=21, signal_feed="VIXY", long_asset="SPY",
            off_asset_return="TLT", tax_rate=0.15, spread_bps=5.0,
        ),
    ),
    (
        "lb42_vixy_spy",
        H2VixTermConfig(
            lookback=42, signal_feed="VIXY", long_asset="SPY",
            off_asset_return="TLT", tax_rate=0.15, spread_bps=5.0,
        ),
    ),
    (
        "lb63_vixy_spy",
        H2VixTermConfig(
            lookback=63, signal_feed="VIXY", long_asset="SPY",
            off_asset_return="TLT", tax_rate=0.15, spread_bps=5.0,
        ),
    ),
    (
        "lb21_vxx_spy",
        H2VixTermConfig(
            lookback=21, signal_feed="VXX", long_asset="SPY",
            off_asset_return="TLT", tax_rate=0.15, spread_bps=5.0,
        ),
    ),
    (
        "lb21_vixy_sso",
        H2VixTermConfig(
            lookback=21, signal_feed="VIXY", long_asset="SSO",
            off_asset_return="TLT", tax_rate=0.15, spread_bps=5.0,
        ),
    ),
]


def _load_daily(ticker: str, source: str = "tiingo") -> pd.Series:
    if source == "tiingo":
        fp = TIINGO_DIR / f"{ticker}.parquet"
    else:
        fp = VIX_DIR / f"{ticker}.parquet"
    if not fp.exists():
        raise FileNotFoundError(fp)
    df = pd.read_parquet(fp)
    # Prefer adj_close; VIXCLS has only close.
    col = "adj_close" if "adj_close" in df.columns else "close"
    s = df[col].astype(float).sort_index()
    # Drop tz if any.
    if isinstance(s.index, pd.DatetimeIndex) and s.index.tz is not None:
        s.index = s.index.tz_localize(None)
    return s


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


def _cagr_tier_rotaB(cagr: float) -> str:
    """Mandate §2.2 rota B tiers (Inter post-15% DARF)."""
    if cagr < 0.11:
        return "Folclore"
    if cagr < 0.17:
        return "Marginal"
    if cagr < 0.25:
        return "Válido"
    if cagr < 0.40:
        return "Forte"
    return "Extraordinário (suspect)"


def _mdd_tier_rotaB(mdd_mag: float) -> str:
    """Mandate §2.3 rota B tiers."""
    if mdd_mag <= 0.15:
        return "Excelente"
    if mdd_mag <= 0.25:
        return "Válido"
    if mdd_mag <= 0.35:
        return "Marginal"
    if mdd_mag <= 0.50:
        return "Forte warning"
    return "Reject"


def _ir_vs_spy(port: pd.Series, spy_ret: pd.Series) -> float:
    common = port.index.intersection(spy_ret.index)
    if len(common) < 20:
        return float("nan")
    excess = port.loc[common] - spy_ret.loc[common]
    mu, sd = float(excess.mean()), float(excess.std(ddof=1))
    if sd <= 0:
        return 0.0
    return mu / sd * np.sqrt(TRADING_DAYS)


def _vectorbt_cross_check(
    spy_c: pd.Series,
    tlt_c: pd.Series,
    vixy_c: pd.Series,
    vxx_c: pd.Series,
    cfg: H2VixTermConfig,
    ref_oos_daily: pd.Series,
) -> dict:
    """Reconstruct the rotation via vbt.Portfolio.from_orders on a long/off
    basket (SPY vs TLT). vectorbt cannot exactly mirror the custom
    switch-cost + DARF book-keeping — we pass-through fees=spread only
    (per-side) and compare OOS CAGR pp delta to the reference."""
    try:
        import vectorbt as vbt
    except Exception as e:
        return {"status": "skipped", "reason": f"vectorbt unavailable: {e}",
                "delta_cagr_pp": None}

    from ai_trade.backtest.strategies.phase3_7_h2_vix_term_structure import (
        compute_vix_regime_signal,
    )

    # Common index
    idx = spy_c.index.intersection(tlt_c.index)
    feed = vixy_c if cfg.signal_feed == "VIXY" else vxx_c
    idx = idx.intersection(feed.index).sort_values()
    spy = spy_c.loc[idx].astype(float)
    tlt = tlt_c.loc[idx].astype(float)
    f = feed.loc[idx].astype(float)

    regime = compute_vix_regime_signal(f, lookback=cfg.lookback, threshold=cfg.threshold)
    reg = regime.fillna(0.0)  # warmup → flat cash approximated as 0 weight

    try:
        # Build target-weight matrix: 1.0 SPY or 1.0 TLT per day.
        cols = ["SPY", "TLT"]
        close_mat = pd.concat([spy, tlt], axis=1)
        close_mat.columns = cols
        target_w = pd.DataFrame(0.0, index=idx, columns=cols)
        target_w.loc[:, "SPY"] = reg.to_numpy()
        target_w.loc[:, "TLT"] = (1.0 - reg).to_numpy()
        # apply shift(1) for t-1 decision → t execution:
        target_w = target_w.shift(1).fillna(0.0)

        pf = vbt.Portfolio.from_orders(
            close=close_mat,
            size=target_w,
            size_type="targetpercent",
            group_by=True,
            cash_sharing=True,
            fees=cfg.spread_bps / 10_000.0 / 2.0,
            freq="1D",
            init_cash=1.0,
        )
        vbt_daily = pf.returns()
        if isinstance(vbt_daily, pd.DataFrame):
            vbt_daily = vbt_daily.iloc[:, 0]
        vbt_daily = vbt_daily.replace([np.inf, -np.inf], np.nan).fillna(0.0)
        vbt_daily.index = pd.DatetimeIndex(vbt_daily.index).tz_localize(None) \
            if getattr(vbt_daily.index, "tz", None) else vbt_daily.index
    except Exception as e:
        return {"status": "failed", "reason": f"vbt.Portfolio.from_orders raised: {e}",
                "delta_cagr_pp": None}

    vbt_oos = _slice(vbt_daily, *OOS_RANGE)
    if len(vbt_oos) < 20 or len(ref_oos_daily) < 20:
        return {"status": "insufficient_overlap",
                "reason": f"vbt_oos={len(vbt_oos)}, ref_oos={len(ref_oos_daily)}",
                "delta_cagr_pp": None}
    common = ref_oos_daily.index.intersection(vbt_oos.index)
    if len(common) < 20:
        return {"status": "insufficient_overlap_after_align",
                "reason": f"common={len(common)}", "delta_cagr_pp": None}
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
    return {"status": "ok", "ref_cagr_oos": ref_cagr, "vbt_cagr_oos": vbt_cagr,
            "delta_cagr_pp": delta_pp, "n_common_days": int(len(common))}


def main() -> None:
    t0 = time.time()
    print("=" * 80)
    print("Phase 3.7 H2.c — VIX term-structure regime rotation (VIXY→SPY/TLT)")
    print("=" * 80)

    # -- Step 1: load data
    print("\n[data] loading daily series…")
    spy = _load_daily("SPY", source="tiingo")
    sso = _load_daily("SSO", source="tiingo")
    tlt = _load_daily("TLT", source="tiingo")
    vixy = _load_daily("VIXY", source="vix")
    vxx = _load_daily("VXX", source="vix")
    print(f"[data] SPY {spy.index[0].date()} → {spy.index[-1].date()} n={len(spy)}")
    print(f"[data] SSO {sso.index[0].date()} → {sso.index[-1].date()} n={len(sso)}")
    print(f"[data] TLT {tlt.index[0].date()} → {tlt.index[-1].date()} n={len(tlt)}")
    print(f"[data] VIXY {vixy.index[0].date()} → {vixy.index[-1].date()} n={len(vixy)}")
    print(f"[data] VXX {vxx.index[0].date()} → {vxx.index[-1].date()} n={len(vxx)}")

    # -- Step 2: winner run
    print(f"\n[winner] config = {WINNER_CFG}")
    ts = time.time()
    winner = simulate_h2_vix_term_structure(
        spy_close=spy, tlt_close=tlt,
        vixy_close=vixy, vxx_close=vxx,
        config=WINNER_CFG, sso_close=None,
    )
    print(f"[winner] done in {time.time()-ts:.2f}s  n_switches={winner.n_switches} "
          f"long_days={winner.long_days}  off_days={winner.off_days}  "
          f"cum_cost={winner.cum_cost_pct:.4f}  cum_tax={winner.cum_tax_pct:.4f}")

    daily = winner.daily_returns

    # Halt-contract 1: if regime is almost-always one value → degenerate.
    reg = winner.regime.dropna()
    frac_on = float((reg == 1.0).mean()) if len(reg) else float("nan")
    degenerate = (frac_on >= 0.98) or (frac_on <= 0.02)
    print(f"[halt-check] frac risk-on = {frac_on*100:.2f}%  "
          f"(degenerate?→{degenerate})")

    # -- Step 3: splits
    is_ret = _slice(daily, *IS_RANGE)
    oos_ret = _slice(daily, *OOS_RANGE)
    fwd_ret = _slice(daily, *FWD_RANGE)
    full_ret = daily

    is_m = _mdict("IS", is_ret)
    oos_m = _mdict("OOS", oos_ret)
    fwd_m = _mdict("FWD", fwd_ret)
    full_m = _mdict("FULL", full_ret)

    print(f"[IS]   S={is_m['sharpe']:.3f}  CAGR={is_m['cagr']*100:.2f}%  "
          f"MDD={is_m['max_drawdown']*100:.2f}%  n={is_m['n_bars']}")
    print(f"[OOS]  S={oos_m['sharpe']:.3f}  CAGR={oos_m['cagr']*100:.2f}%  "
          f"MDD={oos_m['max_drawdown']*100:.2f}%  n={oos_m['n_bars']}")
    print(f"[FWD]  S={fwd_m['sharpe']:.3f}  CAGR={fwd_m['cagr']*100:.2f}%  "
          f"MDD={fwd_m['max_drawdown']*100:.2f}%  n={fwd_m['n_bars']}")
    print(f"[FULL] S={full_m['sharpe']:.3f}  CAGR={full_m['cagr']*100:.2f}%  "
          f"MDD={full_m['max_drawdown']*100:.2f}%  n={full_m['n_bars']}")

    # -- Step 4: bootstrap 99.9% CI
    if len(oos_ret) >= 20:
        oos_lo, oos_hi = bootstrap_sharpe_ci(oos_ret, alpha=0.001,
                                              n_resamples=2000, block_mean=5,
                                              seed=42)
    else:
        oos_lo, oos_hi = float("nan"), float("nan")
    if len(full_ret) >= 20:
        full_lo, full_hi = bootstrap_sharpe_ci(full_ret, alpha=0.001,
                                                n_resamples=2000, block_mean=5,
                                                seed=42)
    else:
        full_lo, full_hi = float("nan"), float("nan")
    print(f"[BOOT] OOS 99.9% CI [{oos_lo:.4f}, {oos_hi:.4f}]")
    print(f"[BOOT] FULL 99.9% CI [{full_lo:.4f}, {full_hi:.4f}]")

    # -- Step 5: walk-forward 8 windows
    if len(full_ret) >= 8:
        wf_ratio, wf_mdd, _ = walk_forward_verdict_from_returns(
            full_ret, n_windows=8, max_drawdown_cap=0.50
        )
    else:
        wf_ratio, wf_mdd = 0.0, 0.0
    wf_profitable = int(round(wf_ratio * 8))
    wf_pass_ratio = wf_profitable >= 6
    print(f"[WF]   {wf_profitable}/8 profitable  max_window_mdd={wf_mdd*100:.2f}%")

    # -- Step 6: IR vs SPY buy-hold OOS
    spy_ret = spy.pct_change().fillna(0.0)
    spy_oos_bh = _slice(spy_ret, *OOS_RANGE)
    spy_oos_bh_m = _mdict("SPY_OOS_BH", spy_oos_bh)
    ir = _ir_vs_spy(oos_ret, spy_oos_bh)
    print(f"[IR]   vs SPY BH OOS = {ir:.4f}  (SPY OOS BH S={spy_oos_bh_m['sharpe']:.3f}  "
          f"CAGR={spy_oos_bh_m['cagr']*100:.2f}%)")

    # -- Step 7: median hold (on-regime blocks)
    median_hold_days = winner.median_hold_days()
    print(f"[HOLD] median risk-on block = {median_hold_days:.1f} days  "
          f"n_switches={winner.n_switches}")

    # -- Step 8: cost×2 sensitivity (spread_bps×2, DARF→30%, SSO fee×2)
    cost2x_cfg = H2VixTermConfig(
        lookback=WINNER_CFG.lookback,
        signal_feed=WINNER_CFG.signal_feed,
        long_asset=WINNER_CFG.long_asset,
        off_asset_return=WINNER_CFG.off_asset_return,
        sso_expense_annual=WINNER_CFG.sso_expense_annual * 2.0,
        commission_bps=WINNER_CFG.commission_bps,
        spread_bps=WINNER_CFG.spread_bps * 2.0,
        tax_rate=0.30,  # mandate cost×2: DARF 30%
        threshold=WINNER_CFG.threshold,
    )
    print(f"\n[cost2x] spread={cost2x_cfg.spread_bps:.1f}bps tax={cost2x_cfg.tax_rate:.2f}")
    ts = time.time()
    cost2x_res = simulate_h2_vix_term_structure(
        spy_close=spy, tlt_close=tlt,
        vixy_close=vixy, vxx_close=vxx,
        config=cost2x_cfg, sso_close=None,
    )
    print(f"[cost2x] done in {time.time()-ts:.2f}s")
    cost2x_oos_daily = _slice(cost2x_res.daily_returns, *OOS_RANGE)
    cost2x_m = _mdict("OOS_cost2x", cost2x_oos_daily)
    print(f"[cost2x] OOS Sharpe={cost2x_m['sharpe']:.3f}  "
          f"CAGR={cost2x_m['cagr']*100:.2f}%")

    # -- Step 9: grid run for PBO + DSR
    print(f"\n[grid] running {len(GRID_CFGS)} sibling configs for PBO/DSR…")
    grid_rets: dict[str, pd.Series] = {}
    for tag, cfg in GRID_CFGS:
        ts = time.time()
        r = simulate_h2_vix_term_structure(
            spy_close=spy, tlt_close=tlt,
            vixy_close=vixy, vxx_close=vxx,
            config=cfg,
            sso_close=sso if cfg.long_asset == "SSO" else None,
        )
        grid_rets[tag] = r.daily_returns
        sh = compute_split_metrics(tag, r.daily_returns).sharpe
        print(f"  [grid] {tag:20s} done in {time.time()-ts:.2f}s  "
              f"Sharpe_full={sh:.3f}  n_switches={r.n_switches}")

    grid_df = pd.concat(grid_rets, axis=1).dropna(how="any")
    print(f"[grid] aligned matrix shape: {grid_df.shape}")

    pbo_result = None
    if grid_df.shape[0] >= 100 and grid_df.shape[1] >= 2:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            pbo_result = cscv_pbo(grid_df.to_numpy(), n_blocks=10)
        print(f"[PBO] value={pbo_result.pbo:.4f}  n_combos={pbo_result.n_combinations}")
    else:
        print("[PBO] skipped — insufficient grid")

    dsr_res = dsr_metric(oos_ret.to_numpy(dtype=float), n_trials=len(GRID_CFGS))
    print(f"[DSR] p_value={dsr_res.p_value:.6f}  obs_SR={dsr_res.observed_sharpe:.4f}")

    # -- Step 10: cross-lib concordance (vectorbt)
    print("\n[cross-lib] vectorbt concordance on OOS…")
    ts = time.time()
    try:
        cross = _vectorbt_cross_check(spy, tlt, vixy, vxx, WINNER_CFG, oos_ret)
    except Exception as e:
        cross = {"status": "error", "reason": str(e), "delta_cagr_pp": None}
    print(f"[cross-lib] done in {time.time()-ts:.2f}s status={cross.get('status')} "
          f"delta_cagr_pp={cross.get('delta_cagr_pp')}")

    # -- Step 11: 13-gate table (rota B)
    cagr_tier_oos = _cagr_tier_rotaB(oos_m["cagr"])
    mdd_tier_oos = _mdd_tier_rotaB(abs(oos_m["max_drawdown"]))
    leveraged = (WINNER_CFG.long_asset == "SSO")
    cross_ok = (
        cross.get("status") == "ok"
        and cross.get("delta_cagr_pp") is not None
        and cross["delta_cagr_pp"] <= 3.0
    )

    def _b(x):
        if x is None:
            return None
        return bool(x)

    gates = [
        ("gate_01_is_sharpe_gt_0_5",
         _b(is_m["sharpe"] > 0.5),
         f"{is_m['sharpe']:.3f}", "soft"),
        ("gate_02_oos_sharpe_ge_1_3",
         _b(oos_m["sharpe"] >= 1.3),
         f"{oos_m['sharpe']:.3f}", "soft"),
        ("gate_03_oos_cagr_tier",
         None,
         f"{oos_m['cagr']*100:.2f}% → {cagr_tier_oos}", "warning"),
        ("gate_04_oos_mdd_tier",
         None,
         f"{oos_m['max_drawdown']*100:.2f}% → {mdd_tier_oos}", "warning"),
        ("gate_05_fwd_sharpe_gt_0",
         _b(fwd_m["sharpe"] > 0),
         f"{fwd_m['sharpe']:.3f}", "soft"),
        ("gate_06_wf_6_8_profitable",
         _b(wf_pass_ratio),
         f"{wf_profitable}/8  max_mdd={wf_mdd*100:.2f}%", "soft"),
        ("gate_07_median_hold_ge_5d",
         _b(np.isfinite(median_hold_days) and median_hold_days >= 5.0),
         f"{median_hold_days:.1f}d", "soft"),
        ("gate_08_ir_vs_spy_ge_0_2",
         _b((not np.isnan(ir)) and ir >= 0.2),
         f"{ir:.4f}", "soft"),
        ("gate_09_cross_lib_concordance_3pp",
         _b(cross_ok),
         f"status={cross.get('status')} Δ={cross.get('delta_cagr_pp')}pp", "hard"),
        ("gate_10_bootstrap_oos_99p9_ci_low_gt_0",
         _b((not np.isnan(oos_lo)) and oos_lo > 0),
         f"OOS [{oos_lo:.4f},{oos_hi:.4f}]", "hard"),
        ("gate_10b_bootstrap_full_99p9_ci_low_gt_0",
         _b((not np.isnan(full_lo)) and full_lo > 0),
         f"FULL [{full_lo:.4f},{full_hi:.4f}]", "hard"),
        ("gate_11_pbo_lt_0_5",
         _b(pbo_result is not None and pbo_result.pbo < 0.5),
         f"{pbo_result.pbo:.4f}" if pbo_result else "N/A", "hard"),
        ("gate_12_dsr_p_lt_0_05",
         _b(dsr_res.p_value < 0.05),
         f"{dsr_res.p_value:.6f}", "hard"),
        ("gate_13_cost2x_sharpe_gt_1",
         _b(cost2x_m["sharpe"] > (0.8 if leveraged else 1.0)),
         f"{cost2x_m['sharpe']:.3f}", "soft"),
    ]

    n_pass = sum(1 for _, p, *_ in gates if p is True)
    n_fail = sum(1 for _, p, *_ in gates if p is False)
    n_warn = sum(1 for _, p, *_ in gates if p is None)
    hard_fails = [n for n, p, _, lvl in gates if (p is False and lvl == "hard")]
    soft_fails = [n for n, p, _, lvl in gates if (p is False and lvl == "soft")]

    if degenerate:
        verdict = "FAIL (halt: degenerate regime)"
    elif hard_fails:
        verdict = "FAIL (hard gates)"
    elif soft_fails:
        verdict = "FAIL (soft gates)"
    else:
        verdict = "PASS"

    print(f"\n=== GATES ({n_pass} PASS / {n_fail} FAIL / {n_warn} WARN) ===")
    for n, p, v, lvl in gates:
        mark = "PASS" if p is True else ("FAIL" if p is False else "WARN")
        print(f"  [{mark}] [{lvl:4s}] {n:46s} = {v}")
    print(f"\nFINAL VERDICT: {verdict}")
    if hard_fails:
        print(f"HARD gate fails: {hard_fails}")
    if soft_fails:
        print(f"SOFT gate fails: {soft_fails}")

    # -- Step 12: persist artifacts
    pd.DataFrame({"ret": daily}).to_parquet(OUT_DIR / "daily_returns_winner.parquet")
    pd.DataFrame({"ret": cost2x_res.daily_returns}).to_parquet(
        OUT_DIR / "daily_returns_cost2x.parquet"
    )

    grid_cfg_rows = []
    for tag, cfg in GRID_CFGS:
        s = grid_rets[tag]
        sh = compute_split_metrics(tag, s).sharpe
        grid_cfg_rows.append({
            "tag": tag,
            "lookback": cfg.lookback,
            "signal_feed": cfg.signal_feed,
            "long_asset": cfg.long_asset,
            "off_asset_return": cfg.off_asset_return,
            "sharpe_full": float(sh),
        })
    (OUT_DIR / "config_grid.csv").write_text(
        "tag,lookback,signal_feed,long_asset,off_asset_return,sharpe_full\n"
        + "\n".join(
            f"{c['tag']},{c['lookback']},{c['signal_feed']},{c['long_asset']},"
            f"{c['off_asset_return']},{c['sharpe_full']:.4f}"
            for c in grid_cfg_rows
        )
    )

    agg = {
        "phase": "phase_3_7",
        "family": "H2c_vix_term_structure_rotation",
        "slug": "h2_vix_term_structure",
        "produced_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "broker_path": "Banco Inter BRL→USD (rota B; 15% DARF; spread_bps=5)",
        "cost_model": {
            "spread_bps": WINNER_CFG.spread_bps,
            "commission_bps": WINNER_CFG.commission_bps,
            "sso_expense_annual": WINNER_CFG.sso_expense_annual,
            "tax_rate": WINNER_CFG.tax_rate,
            "threshold": WINNER_CFG.threshold,
        },
        "data_source": (
            "Tiingo daily SPY/SSO/TLT + data/phase3_7/vix/{VIXY,VXX} daily"
        ),
        "winner_config": {
            "lookback": WINNER_CFG.lookback,
            "signal_feed": WINNER_CFG.signal_feed,
            "long_asset": WINNER_CFG.long_asset,
            "off_asset_return": WINNER_CFG.off_asset_return,
            "threshold": WINNER_CFG.threshold,
        },
        "windows": {
            "IS": list(IS_RANGE),
            "OOS": list(OOS_RANGE),
            "FWD": list(FWD_RANGE),
        },
        "splits": {
            "IS": is_m,
            "OOS": oos_m,
            "FWD": fwd_m,
            "FULL": full_m,
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
            "pass": ((pbo_result.pbo < 0.5) if pbo_result else None),
        },
        "dsr": {
            "dsr": dsr_res.dsr,
            "p_value": dsr_res.p_value,
            "observed_sharpe": dsr_res.observed_sharpe,
            "n_trials": dsr_res.n_trials,
            "pass": dsr_res.p_value < 0.05,
        },
        "bootstrap_oos": {"ci_low": oos_lo, "ci_high": oos_hi,
                           "pass": (not np.isnan(oos_lo) and oos_lo > 0)},
        "bootstrap_full": {"ci_low": full_lo, "ci_high": full_hi,
                            "pass": (not np.isnan(full_lo) and full_lo > 0)},
        "cross_lib": cross,
        "ir_vs_spy_oos": ir,
        "median_hold_days": median_hold_days,
        "n_switches_full": winner.n_switches,
        "long_days_full": winner.long_days,
        "off_days_full": winner.off_days,
        "frac_risk_on": frac_on,
        "degenerate_regime": degenerate,
        "cum_cost_pct": winner.cum_cost_pct,
        "cum_tax_pct": winner.cum_tax_pct,
        "cost2x_oos": cost2x_m,
        "cagr_tier_oos_rotaB": cagr_tier_oos,
        "mdd_tier_oos_rotaB": mdd_tier_oos,
        "gates": [{"name": n, "pass": p, "value": v, "level": lvl}
                  for n, p, v, lvl in gates],
        "verdict": verdict,
        "hard_fails": hard_fails,
        "soft_fails": soft_fails,
        "grid_configs": grid_cfg_rows,
        # top-level
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
    print(f"[write] {OUT_DIR / 'daily_returns_winner.parquet'}")
    print(f"[write] {OUT_DIR / 'config_grid.csv'}")
    print(f"\nTotal runtime: {time.time()-t0:.1f}s")


if __name__ == "__main__":
    main()

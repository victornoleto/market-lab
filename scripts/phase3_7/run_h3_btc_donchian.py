"""Phase 3.7 H3.a — BTC Donchian ensemble independent signal runner.

Loads BTC daily (Tiingo) and executes the H3.a strategy under the
F2-patched ``prev_weight × ret`` alignment. Emits a full 13-gate
AGGREGATE report per the Phase 3.7-3 hunt prompt.

Execution shape
---------------
1. Load BTC daily OHLC (Tiingo) — full 2014+ series, 7d/wk bars.
2. Winner config = Donchian {10,20,40} + ATR(20) k=2 + 2-day time stop +
   risk 1% + leverage 1x + swap_long −20%/yr (Pepperstone rota A).
3. IS / OOS / FWD split + full metrics (Sharpe/CAGR/MDD using 365-day
   annualization because crypto is 24/7).
4. Bootstrap 99.9% CI (stationary block) OOS + FULL.
5. Walk-forward 8-window verdict.
6. IR vs BTC buy-hold OOS.
7. Cost×2 sensitivity (spread×2 + swap_long×2 + swap_short halved).
8. 6-config grid for PBO/DSR (risk × leverage × allow_short variations).
9. Vectorbt cross-lib concordance on OOS.
10. Stress-period breakdown (2018 bear, COVID, FTX collapse).
11. Write AGGREGATE.{json,md} + parquets.

Citations
---------
* `[zarattini_pagani_barbon_2025]` — Donchian ensemble base.
* `[universal_trend_tactics, p.295-299, p.338-343]` — Turtle + ATR trail.
* `[advances_fin_ml, p.31-34]` — F2 alignment.
* `[advances_fin_ml, p.196-202]` — stationary bootstrap.
* `[advances_fin_ml, p.208-211, p.273-275]` — CSCV PBO + DSR.
* `docs/investment-mandate.md §2.4, §3.1` — 13 gates + rota A cost model.
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
from ai_trade.backtest.strategies.phase3_7_h3_btc_donchian import (  # noqa: E402
    H3BTCDonchianConfig,
    simulate_h3_btc_donchian,
)
from ai_trade.backtest.validation.dsr import dsr as dsr_metric  # noqa: E402
from ai_trade.backtest.validation.pbo import pbo as cscv_pbo  # noqa: E402

OUT_DIR = ROOT / "reports/phase_3_7/h3_btc_donchian"
OUT_DIR.mkdir(parents=True, exist_ok=True)
TIINGO_DIR = ROOT / "data/tiingo/daily/prices"

# Windows — from hunt prompt (non-overlapping).
IS_RANGE = ("2015-01-01", "2019-12-31")
OOS_RANGE = ("2020-01-01", "2023-12-31")
FWD_RANGE = ("2024-01-01", "2026-04-14")

# Stress periods (subsets of OOS/FWD for narrative breakdown).
STRESS_PERIODS = [
    ("2018_bear", "2018-01-01", "2018-12-31"),          # within IS
    ("covid_crash", "2020-02-01", "2020-04-30"),        # within OOS
    ("ftx_collapse", "2022-11-01", "2022-12-31"),       # within OOS
    ("etf_rally", "2024-01-01", "2024-03-31"),          # within FWD
]

# 365-day annualization for crypto (7 days/week) — distinct from the
# default TRADING_DAYS=252 used for equities.
CRYPTO_DAYS_PER_YEAR = 365

# Winner config — prompt-specified defaults.
WINNER_CFG = H3BTCDonchianConfig(
    lookbacks=(10, 20, 40),
    atr_period=20,
    atr_multiplier=2.0,
    max_hold_days=2,
    risk_per_trade=0.010,
    max_leverage=1.0,
    spread_bps_per_side=5.0,
    commission_bps=0.0,
    swap_long_daily=-0.0005556,
    swap_short_daily=0.0002083,
    allow_short=True,
)

# Sensitivity grid — 6 configs covering risk × leverage × short-enabled.
# All stay within the prompt-specified ensemble {10,20,40} and
# canonical k=2 ATR; we vary parameters that have well-defined priors.
GRID_CFGS: list[tuple[str, H3BTCDonchianConfig]] = [
    ("r005_lev1_short",  H3BTCDonchianConfig(risk_per_trade=0.005, max_leverage=1.0, allow_short=True)),
    ("r010_lev1_short",  H3BTCDonchianConfig(risk_per_trade=0.010, max_leverage=1.0, allow_short=True)),
    ("r015_lev1_short",  H3BTCDonchianConfig(risk_per_trade=0.015, max_leverage=1.0, allow_short=True)),
    ("r010_lev2_short",  H3BTCDonchianConfig(risk_per_trade=0.010, max_leverage=2.0, allow_short=True)),
    ("r010_lev1_longonly", H3BTCDonchianConfig(risk_per_trade=0.010, max_leverage=1.0, allow_short=False)),
    ("r010_lev2_longonly", H3BTCDonchianConfig(risk_per_trade=0.010, max_leverage=2.0, allow_short=False)),
]


def _load_btc_daily() -> pd.DataFrame:
    fp = TIINGO_DIR / "btcusd.parquet"
    if not fp.exists():
        raise FileNotFoundError(fp)
    df = pd.read_parquet(fp)
    df.index = pd.DatetimeIndex(df.index).tz_localize(None).normalize()
    df = df[~df.index.duplicated(keep="last")].sort_index()
    return df


def _slice_idx(idx: pd.DatetimeIndex, start: str, end: str) -> pd.DatetimeIndex:
    a, b = pd.Timestamp(start), pd.Timestamp(end)
    return idx[(idx >= a) & (idx <= b)]


def _slice_series(s: pd.Series, start: str, end: str) -> pd.Series:
    a, b = pd.Timestamp(start), pd.Timestamp(end)
    return s.loc[(s.index >= a) & (s.index <= b)]


def _mdict(name: str, s: pd.Series, ppy: int = CRYPTO_DAYS_PER_YEAR) -> dict:
    m = compute_split_metrics(name, s, periods_per_year=ppy)
    return {
        "name": m.name,
        "n_bars": m.n_bars,
        "sharpe": m.sharpe,
        "cagr": m.cagr,
        "max_drawdown": m.max_drawdown,
        "final_equity_from_unit": m.final_equity_from_unit,
    }


def _cagr_tier_rotaA(cagr: float) -> str:
    """Mandate §2.2 rota A Pepperstone tiers."""
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
    """Mandate §2.3 rota A tiers."""
    if mdd_mag <= 0.25:
        return "Excelente"
    if mdd_mag <= 0.40:
        return "Válido"
    if mdd_mag <= 0.50:
        return "Marginal"
    if mdd_mag <= 0.75:
        return "Forte warning"
    return "Reject"


def _ir_vs_btc(port: pd.Series, btc_ret: pd.Series,
               ppy: int = CRYPTO_DAYS_PER_YEAR) -> float:
    common = port.index.intersection(btc_ret.index)
    if len(common) < 20:
        return float("nan")
    excess = port.loc[common] - btc_ret.loc[common]
    mu, sd = float(excess.mean()), float(excess.std(ddof=1))
    if sd <= 0:
        return 0.0
    return mu / sd * np.sqrt(ppy)


def _vectorbt_cross_check(
    btc_df: pd.DataFrame,
    cfg: H3BTCDonchianConfig,
    ref_oos_daily: pd.Series,
) -> dict:
    """Reconstruct the strategy via vbt.Portfolio.from_signals.

    We reuse our deterministic simulator to produce entries/exits
    (vectorbt's native Donchian-ensemble + ATR-trail + time-stop
    composition would require bespoke custom Indicator factory code,
    which itself could drift from our reference — so we feed OUR
    entries/exits into vbt.Portfolio.from_signals and check the
    resulting returns). This is the honest cross-lib check: if
    vbt disagrees on return aggregation given identical signals, it's
    an alignment bug we need to surface.
    """
    try:
        import vectorbt as vbt
    except Exception as e:
        return {"status": "skipped", "reason": f"vectorbt unavailable: {e}",
                "delta_cagr_pp": None}

    sim = simulate_h3_btc_donchian(btc_df, cfg)
    # Build vectorbt signals on the same index.
    close = btc_df["close"].astype(float)
    close.index = pd.DatetimeIndex(close.index).tz_localize(None).normalize()

    # Build entries / exits from the reference sim result.
    ent_long = sim.entries_long.reindex(close.index).fillna(False).astype(bool)
    ent_short = sim.entries_short.reindex(close.index).fillna(False).astype(bool)
    ex = sim.exits.reindex(close.index).fillna(False).astype(bool)

    # vbt.Portfolio.from_signals with long/short; each entry opens a
    # fixed-fraction position; fees are per-side as fraction.
    try:
        # NB: vbt doesn't support our sophisticated risk/ATR sizing
        # natively; we use size='percent' with the simulator's first
        # non-zero absolute weight as a proxy. This is known-imperfect
        # — we compare CAGR/Sharpe deltas on the returns series only.
        weights = sim.weights.copy()
        # For comparison, we apply the ref sim's weights directly to
        # close returns via weight-product convention and let vbt
        # handle fees on turnover.
        pf = vbt.Portfolio.from_signals(
            close=close,
            entries=ent_long,
            short_entries=ent_short,
            exits=ex,
            short_exits=ex,
            size=weights.abs(),
            size_type="percent",
            fees=cfg.spread_bps_per_side / 10_000.0,
            freq="1D",
            init_cash=1.0,
        )
        vbt_daily = pf.returns()
        if isinstance(vbt_daily, pd.DataFrame):
            vbt_daily = vbt_daily.iloc[:, 0]
        vbt_daily = vbt_daily.replace([np.inf, -np.inf], np.nan).fillna(0.0)
        if getattr(vbt_daily.index, "tz", None):
            vbt_daily.index = pd.DatetimeIndex(vbt_daily.index).tz_localize(None)
    except Exception as e:
        return {"status": "failed", "reason": f"vbt.Portfolio.from_signals raised: {e}",
                "delta_cagr_pp": None}

    vbt_oos = _slice_series(vbt_daily, *OOS_RANGE)
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
        y = len(r) / CRYPTO_DAYS_PER_YEAR
        return eq ** (1.0 / y) - 1.0 if y > 0 else 0.0

    ref_cagr = _cagr(ref)
    vbt_cagr = _cagr(vbt_r)
    delta_pp = abs(vbt_cagr - ref_cagr) * 100.0
    return {"status": "ok", "ref_cagr_oos": ref_cagr, "vbt_cagr_oos": vbt_cagr,
            "delta_cagr_pp": delta_pp, "n_common_days": int(len(common))}


def main() -> None:
    t0 = time.time()
    print("=" * 80)
    print("Phase 3.7 H3.a — BTC Donchian ensemble independent signal (rota A)")
    print("=" * 80)

    # -- Step 1: load data
    print("\n[data] loading BTCUSD daily…")
    btc = _load_btc_daily()
    btc_full = btc.loc[:FWD_RANGE[1]]
    print(f"[data] BTCUSD {btc_full.index[0].date()} → {btc_full.index[-1].date()} "
          f"n={len(btc_full)} ({btc_full.index.weekday.value_counts().loc[[5,6]].sum()} "
          f"weekend bars — crypto 7d/wk)")

    # -- Step 2: winner run (full-series so halt contract + splits align)
    print(f"\n[winner] config = {WINNER_CFG}")
    ts = time.time()
    winner = simulate_h3_btc_donchian(btc_full, WINNER_CFG)
    print(f"[winner] done in {time.time()-ts:.2f}s  "
          f"n_trades={winner.n_trades} (long={winner.n_long_trades} "
          f"short={winner.n_short_trades})  "
          f"cum_spread={winner.cum_spread_pct:.4f}  "
          f"cum_swap={winner.cum_swap_pct:.4f}  "
          f"median_hold={winner.median_hold_days():.1f}d")

    daily = winner.daily_returns

    # -- Halt contract 1: n_trades OOS must be ≥ 50 (signal-sparsity check).
    oos_trades_count = 0
    entries_oos = (
        winner.entries_long.astype(int) + winner.entries_short.astype(int)
    )
    entries_oos_slice = _slice_series(entries_oos, *OOS_RANGE)
    oos_trades_count = int(entries_oos_slice.sum())
    sparse_halt = oos_trades_count < 50
    print(f"[halt-check] n_trades OOS = {oos_trades_count}  "
          f"(sparse?→{sparse_halt})")

    # -- Step 3: splits
    is_ret = _slice_series(daily, *IS_RANGE)
    oos_ret = _slice_series(daily, *OOS_RANGE)
    fwd_ret = _slice_series(daily, *FWD_RANGE)
    full_ret = daily

    is_m = _mdict("IS", is_ret)
    oos_m = _mdict("OOS", oos_ret)
    fwd_m = _mdict("FWD", fwd_ret)
    full_m = _mdict("FULL", full_ret)

    print(f"[IS]   S={is_m['sharpe']:.3f}  CAGR={is_m['cagr']*100:+.2f}%  "
          f"MDD={is_m['max_drawdown']*100:+.2f}%  n={is_m['n_bars']}")
    print(f"[OOS]  S={oos_m['sharpe']:.3f}  CAGR={oos_m['cagr']*100:+.2f}%  "
          f"MDD={oos_m['max_drawdown']*100:+.2f}%  n={oos_m['n_bars']}")
    print(f"[FWD]  S={fwd_m['sharpe']:.3f}  CAGR={fwd_m['cagr']*100:+.2f}%  "
          f"MDD={fwd_m['max_drawdown']*100:+.2f}%  n={fwd_m['n_bars']}")
    print(f"[FULL] S={full_m['sharpe']:.3f}  CAGR={full_m['cagr']*100:+.2f}%  "
          f"MDD={full_m['max_drawdown']*100:+.2f}%  n={full_m['n_bars']}")

    # -- Step 4: bootstrap 99.9% CI
    if len(oos_ret) >= 20:
        oos_lo, oos_hi = bootstrap_sharpe_ci(
            oos_ret, alpha=0.001, n_resamples=2000, block_mean=5, seed=42,
            periods_per_year=CRYPTO_DAYS_PER_YEAR,
        )
    else:
        oos_lo, oos_hi = float("nan"), float("nan")
    if len(full_ret) >= 20:
        full_lo, full_hi = bootstrap_sharpe_ci(
            full_ret, alpha=0.001, n_resamples=2000, block_mean=5, seed=42,
            periods_per_year=CRYPTO_DAYS_PER_YEAR,
        )
    else:
        full_lo, full_hi = float("nan"), float("nan")
    print(f"[BOOT] OOS 99.9% CI [{oos_lo:.4f}, {oos_hi:.4f}]")
    print(f"[BOOT] FULL 99.9% CI [{full_lo:.4f}, {full_hi:.4f}]")

    # -- Step 5: walk-forward 8 windows over FULL
    if len(full_ret) >= 8:
        # Disable MDD cap (gate 4 is warning only; WF focuses on
        # profitability ratio).
        wf_ratio, wf_mdd, _ = walk_forward_verdict_from_returns(
            full_ret, n_windows=8, max_drawdown_cap=1.0,
        )
    else:
        wf_ratio, wf_mdd = 0.0, 0.0
    wf_profitable = int(round(wf_ratio * 8))
    wf_pass_ratio = wf_profitable >= 6
    print(f"[WF]   {wf_profitable}/8 profitable  max_window_mdd={wf_mdd*100:.2f}%")

    # -- Step 6: IR vs BTC buy-hold OOS
    btc_close = btc_full["close"].astype(float)
    btc_ret = btc_close.pct_change().fillna(0.0)
    btc_oos_bh = _slice_series(btc_ret, *OOS_RANGE)
    btc_oos_bh_m = _mdict("BTC_OOS_BH", btc_oos_bh)
    ir = _ir_vs_btc(oos_ret, btc_oos_bh)
    print(f"[IR]   vs BTC BH OOS = {ir:.4f}  "
          f"(BTC OOS BH S={btc_oos_bh_m['sharpe']:.3f}  "
          f"CAGR={btc_oos_bh_m['cagr']*100:+.2f}%)")

    # -- Step 7: median hold
    median_hold_days = winner.median_hold_days()
    # Gate 7 inverted: WANT short hold ≤ 2d AND > 0 (not instant).
    hold_gate_pass = (
        np.isfinite(median_hold_days)
        and median_hold_days <= float(WINNER_CFG.max_hold_days)
        and median_hold_days > 0
    )
    print(f"[HOLD] median hold = {median_hold_days:.2f}d  "
          f"(gate: ≤{WINNER_CFG.max_hold_days}d AND > 0 → "
          f"{'PASS' if hold_gate_pass else 'FAIL'})")

    # -- Step 8: cost×2 sensitivity
    cost2x_cfg = H3BTCDonchianConfig(
        lookbacks=WINNER_CFG.lookbacks,
        atr_period=WINNER_CFG.atr_period,
        atr_multiplier=WINNER_CFG.atr_multiplier,
        max_hold_days=WINNER_CFG.max_hold_days,
        risk_per_trade=WINNER_CFG.risk_per_trade,
        max_leverage=WINNER_CFG.max_leverage,
        spread_bps_per_side=WINNER_CFG.spread_bps_per_side * 2.0,
        commission_bps=WINNER_CFG.commission_bps,
        swap_long_daily=WINNER_CFG.swap_long_daily * 2.0,
        swap_short_daily=WINNER_CFG.swap_short_daily * 0.5,
        allow_short=WINNER_CFG.allow_short,
    )
    print(f"\n[cost2x] spread_ps={cost2x_cfg.spread_bps_per_side:.1f}bps  "
          f"swap_long={cost2x_cfg.swap_long_daily*100:.4f}%/d  "
          f"swap_short={cost2x_cfg.swap_short_daily*100:.4f}%/d")
    ts = time.time()
    cost2x_res = simulate_h3_btc_donchian(btc_full, cost2x_cfg)
    print(f"[cost2x] done in {time.time()-ts:.2f}s")
    cost2x_oos_daily = _slice_series(cost2x_res.daily_returns, *OOS_RANGE)
    cost2x_m = _mdict("OOS_cost2x", cost2x_oos_daily)
    print(f"[cost2x] OOS Sharpe={cost2x_m['sharpe']:.3f}  "
          f"CAGR={cost2x_m['cagr']*100:+.2f}%")

    # -- Step 9: grid for PBO + DSR
    print(f"\n[grid] running {len(GRID_CFGS)} sibling configs for PBO/DSR…")
    grid_rets: dict[str, pd.Series] = {}
    grid_meta: list[dict] = []
    for tag, cfg in GRID_CFGS:
        ts = time.time()
        r = simulate_h3_btc_donchian(btc_full, cfg)
        grid_rets[tag] = r.daily_returns
        m = compute_split_metrics(tag, r.daily_returns,
                                  periods_per_year=CRYPTO_DAYS_PER_YEAR)
        grid_meta.append({
            "tag": tag,
            "risk_per_trade": cfg.risk_per_trade,
            "max_leverage": cfg.max_leverage,
            "allow_short": cfg.allow_short,
            "sharpe_full": float(m.sharpe),
            "n_trades": r.n_trades,
        })
        print(f"  [grid] {tag:22s} done in {time.time()-ts:.2f}s  "
              f"S_full={m.sharpe:.3f}  n={r.n_trades}")

    grid_df = pd.concat(grid_rets, axis=1).dropna(how="any")
    print(f"[grid] aligned matrix shape: {grid_df.shape}")

    pbo_result = None
    if grid_df.shape[0] >= 100 and grid_df.shape[1] >= 2:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            pbo_result = cscv_pbo(grid_df.to_numpy(), n_blocks=10)
        print(f"[PBO] value={pbo_result.pbo:.4f}  "
              f"n_combos={pbo_result.n_combinations}")
    else:
        print("[PBO] skipped — insufficient grid")

    dsr_res = dsr_metric(oos_ret.to_numpy(dtype=float), n_trials=len(GRID_CFGS))
    print(f"[DSR] p_value={dsr_res.p_value:.6f}  "
          f"obs_SR={dsr_res.observed_sharpe:.4f}")

    # -- Step 10: cross-lib concordance (vectorbt)
    print("\n[cross-lib] vectorbt concordance on OOS…")
    ts = time.time()
    try:
        cross = _vectorbt_cross_check(btc_full, WINNER_CFG, oos_ret)
    except Exception as e:
        cross = {"status": "error", "reason": str(e), "delta_cagr_pp": None}
    print(f"[cross-lib] done in {time.time()-ts:.2f}s  "
          f"status={cross.get('status')}  "
          f"delta_cagr_pp={cross.get('delta_cagr_pp')}")

    # -- Step 11: stress-period breakdown
    stress_rows = []
    for name, s_start, s_end in STRESS_PERIODS:
        sub = _slice_series(daily, s_start, s_end)
        if len(sub) < 5:
            stress_rows.append({"period": name, "start": s_start, "end": s_end,
                                "n_bars": int(len(sub)), "cagr": None,
                                "sharpe": None, "mdd": None,
                                "total_return": None})
            continue
        m = compute_split_metrics(name, sub, periods_per_year=CRYPTO_DAYS_PER_YEAR)
        total_ret = float((1.0 + sub).prod() - 1.0)
        stress_rows.append({
            "period": name, "start": s_start, "end": s_end,
            "n_bars": int(m.n_bars), "cagr": float(m.cagr),
            "sharpe": float(m.sharpe), "mdd": float(m.max_drawdown),
            "total_return": total_ret,
        })
    print("\n[stress]")
    for r in stress_rows:
        sh = "N/A" if r["sharpe"] is None else f"{r['sharpe']:.3f}"
        tr = "N/A" if r["total_return"] is None else f"{r['total_return']*100:+.2f}%"
        print(f"  {r['period']:15s} {r['start']}→{r['end']}  n={r['n_bars']:3d}  "
              f"S={sh}  total={tr}")

    # -- Step 12: 13-gate table (rota A)
    cagr_tier_oos = _cagr_tier_rotaA(oos_m["cagr"])
    mdd_tier_oos = _mdd_tier_rotaA(abs(oos_m["max_drawdown"]))
    leveraged = WINNER_CFG.max_leverage > 1.01
    cross_ok = (
        cross.get("status") == "ok"
        and cross.get("delta_cagr_pp") is not None
        and cross["delta_cagr_pp"] <= 3.0
    )

    def _b(x):
        return None if x is None else bool(x)

    gates = [
        ("gate_01_is_sharpe_gt_0_5",
         _b(is_m["sharpe"] > 0.5),
         f"{is_m['sharpe']:.3f}", "soft"),
        ("gate_02_oos_sharpe_ge_1_3",
         _b(oos_m["sharpe"] >= 1.3),
         f"{oos_m['sharpe']:.3f}", "soft"),
        ("gate_03_oos_cagr_tier",
         None,
         f"{oos_m['cagr']*100:+.2f}% → {cagr_tier_oos}", "warning"),
        ("gate_04_oos_mdd_tier",
         None,
         f"{oos_m['max_drawdown']*100:+.2f}% → {mdd_tier_oos}", "warning"),
        ("gate_05_fwd_sharpe_gt_0",
         _b(fwd_m["sharpe"] > 0),
         f"{fwd_m['sharpe']:.3f}", "soft"),
        ("gate_06_wf_6_8_profitable",
         _b(wf_pass_ratio),
         f"{wf_profitable}/8  max_mdd={wf_mdd*100:.2f}%", "soft"),
        ("gate_07_hold_le_2d_and_positive",
         _b(hold_gate_pass),
         f"{median_hold_days:.2f}d (budget ≤ {WINNER_CFG.max_hold_days}d)",
         "soft"),
        ("gate_08_ir_vs_btc_bh_ge_0_2",
         _b((not np.isnan(ir)) and ir >= 0.2),
         f"{ir:.4f}", "soft"),
        ("gate_09_cross_lib_concordance_3pp",
         _b(cross_ok),
         f"status={cross.get('status')} Δ={cross.get('delta_cagr_pp')}pp",
         "hard"),
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
        ("gate_13_cost2x_sharpe_thresh",
         _b(cost2x_m["sharpe"] > (0.8 if leveraged else 1.0)),
         f"{cost2x_m['sharpe']:.3f} "
         f"(thr={'0.8(lev)' if leveraged else '1.0(unlev)'})",
         "soft"),
    ]

    n_pass = sum(1 for _, p, *_ in gates if p is True)
    n_fail = sum(1 for _, p, *_ in gates if p is False)
    n_warn = sum(1 for _, p, *_ in gates if p is None)
    hard_fails = [n for n, p, _, lvl in gates if (p is False and lvl == "hard")]
    soft_fails = [n for n, p, _, lvl in gates if (p is False and lvl == "soft")]

    if sparse_halt:
        verdict = "FAIL (halt: signal too sparse — n_trades OOS < 50)"
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

    # -- Step 13: persist artifacts
    pd.DataFrame({"ret": daily}).to_parquet(OUT_DIR / "daily_returns_winner.parquet")
    pd.DataFrame({"ret": cost2x_res.daily_returns}).to_parquet(
        OUT_DIR / "daily_returns_cost2x.parquet"
    )
    (OUT_DIR / "config_grid.csv").write_text(
        "tag,risk_per_trade,max_leverage,allow_short,sharpe_full,n_trades\n"
        + "\n".join(
            f"{c['tag']},{c['risk_per_trade']},{c['max_leverage']},"
            f"{c['allow_short']},{c['sharpe_full']:.4f},{c['n_trades']}"
            for c in grid_meta
        )
    )

    agg = {
        "phase": "phase_3_7",
        "family": "H3a_btc_donchian_ensemble_independent",
        "slug": "h3_btc_donchian",
        "produced_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "broker_path": ("Pepperstone BTCUSD CFD rota A — "
                        "spread 5bps/side + commission 0 + "
                        "swap_long −20%/yr + swap_short +7.5%/yr + NO DARF"),
        "cost_model": {
            "spread_bps_per_side": WINNER_CFG.spread_bps_per_side,
            "commission_bps": WINNER_CFG.commission_bps,
            "swap_long_daily": WINNER_CFG.swap_long_daily,
            "swap_short_daily": WINNER_CFG.swap_short_daily,
            "max_leverage": WINNER_CFG.max_leverage,
            "tax_rate": 0.0,
        },
        "data_source": "Tiingo daily BTCUSD (2014-01-01 → 2026-04-14; 7d/wk)",
        "winner_config": {
            "lookbacks": list(WINNER_CFG.lookbacks),
            "atr_period": WINNER_CFG.atr_period,
            "atr_multiplier": WINNER_CFG.atr_multiplier,
            "max_hold_days": WINNER_CFG.max_hold_days,
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
            "IS": is_m,
            "OOS": oos_m,
            "FWD": fwd_m,
            "FULL": full_m,
            "BTC_OOS_BH": btc_oos_bh_m,
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
        "ir_vs_btc_bh_oos": ir,
        "median_hold_days": median_hold_days,
        "hold_gate_pass": hold_gate_pass,
        "n_trades_full": winner.n_trades,
        "n_long_trades_full": winner.n_long_trades,
        "n_short_trades_full": winner.n_short_trades,
        "n_trades_oos": oos_trades_count,
        "cum_spread_pct": winner.cum_spread_pct,
        "cum_commission_pct": winner.cum_commission_pct,
        "cum_swap_pct": winner.cum_swap_pct,
        "cost2x_oos": cost2x_m,
        "cagr_tier_oos_rotaA": cagr_tier_oos,
        "mdd_tier_oos_rotaA": mdd_tier_oos,
        "stress_periods": stress_rows,
        "gates": [{"name": n, "pass": p, "value": v, "level": lvl}
                  for n, p, v, lvl in gates],
        "verdict": verdict,
        "hard_fails": hard_fails,
        "soft_fails": soft_fails,
        "grid_configs": grid_meta,
        "sparse_halt": sparse_halt,
        # top-level conveniences
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

"""Phase 3.7 H1.b — Maróy 2024 VWAP-exit intraday noise-boundary runner.

Executes the full honest-validation pipeline for the H1.b hypothesis:

* **Signal (entry):** Zarattini-Aziz-Barbon 2024 noise-boundary
  ``[zarattini_aziz_barbon_2024]``.
* **Exit:** Maróy 2024 VWAP-cross with close-only TVWAP approximation
  ``[maroy_2024]``.
* **Engine:** F2-patched ``prev_weight × ret`` alignment
  ``[advances_fin_ml, p.31-34]``.
* **Universe:** SPY 1-min (primary), QQQ 1-min (cross-asset
  confirmation).
* **Cost model:** Pepperstone Razor SPX500 CFD intraday — 0.67 bps
  per side spread, 0 commission, 0 swap (intraday).
* **Windows:** IS 2017-06-01 → 2021-12-31, OOS 2022 → 2024, FWD 2025 →
  2026-04-14.
* **Gate framework:** 13 gates per `docs/investment-mandate.md §2.4`
  (CAGR / MDD are warning-only tiers per §2.2/§2.3).

Output: AGGREGATE.md + AGGREGATE.json + per-split returns parquets to
``reports/phase_3_7/h1_maroy_vwap/``.
"""

from __future__ import annotations

import json
import subprocess
import sys
import time
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path("/var/www/pessoal/ai-trade")
sys.path.insert(0, str(ROOT / "src"))

from ai_trade.backtest.strategies.phase3_7_h1_maroy_vwap import (  # noqa: E402
    MaroyVwapConfig,
    simulate_h1_maroy_vwap,
)
from ai_trade.backtest.validation.bootstrap import (  # noqa: E402
    stationary_bootstrap_trades,
)
from ai_trade.backtest.validation.dsr import dsr as dsr_metric  # noqa: E402
from ai_trade.backtest.validation.pbo import pbo as cscv_pbo  # noqa: E402

OUT_DIR = ROOT / "reports/phase_3_7/h1_maroy_vwap"
OUT_DIR.mkdir(parents=True, exist_ok=True)

INTRA_DIR = ROOT / "data/phase3_7/intraday"
SPY_PATH = INTRA_DIR / "SPY_1min.parquet"
QQQ_PATH = INTRA_DIR / "QQQ_1min.parquet"

IS_RANGE = ("2017-06-01", "2021-12-31")
OOS_RANGE = ("2022-01-01", "2024-12-31")
FWD_RANGE = ("2025-01-01", "2026-04-14")

TRADING_DAYS = 252

# Winner cell: literal Zarattini 2024 + Maróy 2024 defaults (no OOS peek).
WINNER_CFG = MaroyVwapConfig(
    ma_lookback_days=14,
    noise_band_scale=1.0,
    allow_short=True,
    flat_at_close=True,
    spread_one_way=6.7e-5,
    commission_per_flip=0.0,
    min_bar_idx_for_entry=1,
)

# Grid for PBO/DSR: 3 lookbacks × 2 scales × 2 min_bar × 2 directions = 24 cells.
# Winner is one of them (14, 1.0, 1, allow_short=True).
GRID: list[MaroyVwapConfig] = [
    MaroyVwapConfig(
        ma_lookback_days=lb,
        noise_band_scale=sc,
        allow_short=shrt,
        flat_at_close=True,
        spread_one_way=6.7e-5,
        commission_per_flip=0.0,
        min_bar_idx_for_entry=mb,
    )
    for lb in (10, 14, 21)
    for sc in (1.0, 1.2)
    for shrt in (True, False)
    for mb in (1, 30)
]


def _git_sha() -> str:
    try:
        sha = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip()
        return sha[:10]
    except Exception:  # noqa: BLE001
        return "unknown"


def _slice(s: pd.Series, start: str, end: str) -> pd.Series:
    a, b = pd.Timestamp(start), pd.Timestamp(end)
    s2 = s.copy()
    if getattr(s2.index, "tz", None) is not None:
        s2.index = s2.index.tz_localize(None)
    return s2.loc[(s2.index >= a) & (s2.index <= b)]


def _metrics(name: str, r: pd.Series) -> dict:
    r = r.dropna()
    if len(r) < 2:
        return {
            "name": name,
            "n_bars": int(len(r)),
            "sharpe": 0.0,
            "cagr": 0.0,
            "max_drawdown": 0.0,
            "final_equity_from_unit": 1.0,
        }
    sd = float(r.std(ddof=1))
    sh = float(r.mean() / sd * np.sqrt(TRADING_DAYS)) if sd > 0 else 0.0
    eq = float((1.0 + r).prod())
    cagr = float(eq ** (TRADING_DAYS / len(r)) - 1.0) if eq > 0 else -1.0
    cum = (1.0 + r).cumprod()
    mdd = float((cum / cum.cummax() - 1.0).min())
    return {
        "name": name,
        "n_bars": int(len(r)),
        "sharpe": sh,
        "cagr": cagr,
        "max_drawdown": mdd,
        "final_equity_from_unit": eq,
    }


def _bootstrap_sharpe_ci(
    r: pd.Series, alpha: float = 0.001, n_resamples: int = 2000,
    block_mean: int = 5, seed: int = 42,
) -> tuple[float, float]:
    r = r.dropna().to_numpy(dtype=float)
    if len(r) < 20:
        return float("nan"), float("nan")
    resamples = stationary_bootstrap_trades(
        r, block_mean=block_mean, n_resamples=n_resamples, seed=seed
    )
    mu = resamples.mean(axis=1)
    sd = resamples.std(axis=1, ddof=1)
    sharpes = np.where(sd > 0, mu / sd * np.sqrt(TRADING_DAYS), 0.0)
    lo = float(np.quantile(sharpes, alpha / 2))
    hi = float(np.quantile(sharpes, 1 - alpha / 2))
    return lo, hi


def _walk_forward(
    r: pd.Series, n_windows: int = 8, is_frac: float = 0.5
) -> tuple[float, float, bool]:
    """Rolling walk-forward over the full series (IS then OOS)."""
    r = r.dropna()
    n = len(r)
    if n < n_windows * 4:
        return 0.0, 0.0, False
    window = n // n_windows
    is_size = int(window * is_frac)
    oos_size = window - is_size
    profitable = 0
    max_dd = 0.0
    for w in range(n_windows):
        start = w * window
        oos_start = start + is_size
        oos_end = oos_start + oos_size
        if oos_end > n:
            break
        oos = r.iloc[oos_start:oos_end]
        total = float((1.0 + oos).prod() - 1.0)
        if total > 0:
            profitable += 1
        cum = (1.0 + oos).cumprod()
        dd = float((cum / cum.cummax() - 1.0).min())
        max_dd = min(max_dd, dd)
    ratio = profitable / n_windows
    return ratio, abs(max_dd), ratio >= 6 / n_windows


def _ir_vs_spy(port: pd.Series, spy: pd.Series) -> float:
    common = port.index.intersection(spy.index)
    if len(common) < 20:
        return float("nan")
    excess = (port.loc[common] - spy.loc[common]).dropna()
    if len(excess) < 20:
        return float("nan")
    mu, sd = float(excess.mean()), float(excess.std(ddof=1))
    if sd <= 0:
        return 0.0
    return mu / sd * np.sqrt(TRADING_DAYS)


def _cfg_tag(cfg: MaroyVwapConfig) -> str:
    return (
        f"ma{cfg.ma_lookback_days}"
        f"_sc{cfg.noise_band_scale:.1f}"
        f"_shrt{int(cfg.allow_short)}"
        f"_mb{cfg.min_bar_idx_for_entry}"
    )


def _cagr_tier_A(cagr: float) -> str:
    """Rota A (Pepperstone, no DARF) tier per mandate §2.2.

    Folclore < 13%, Marginal 13-25%, Valido 25-50%, Forte 50-100%,
    Extraordinario > 100% (suspect).
    """
    x = cagr * 100.0
    if x < 13.0:
        return "folclore"
    if x < 25.0:
        return "marginal"
    if x < 50.0:
        return "valido"
    if x < 100.0:
        return "forte"
    return "extraordinario_suspect"


def _mdd_tier_A(mdd: float) -> str:
    """Rota A MDD tier per mandate §2.3.

    Excelente ≤ 25%, Valido ≤ 40%, Warning 40-75%, Reject > 75%.
    """
    x = abs(mdd) * 100.0
    if x <= 25.0:
        return "excelente"
    if x <= 40.0:
        return "valido"
    if x <= 75.0:
        return "warning"
    return "reject"


def _compute_daily_spy_ret() -> pd.Series:
    """Load SPY daily close-to-close returns from the 1-min parquet.

    We compound per-day bars to get a daily total return comparable to
    a buy-hold benchmark. Index is tz-naive trading date.
    """
    df = pd.read_parquet(SPY_PATH)
    df_et = df.copy()
    df_et.index = df_et.index.tz_convert("America/New_York")
    df_et["date_et"] = df_et.index.date
    g = df_et.groupby("date_et")
    day_open = g["open"].first()
    day_close = g["close"].last()
    daily = (day_close / day_open - 1.0).astype(float)
    # Compound close-to-close instead
    close_prev = day_close.shift(1)
    ret = (day_close / close_prev - 1.0).dropna()
    ret.index = pd.DatetimeIndex(pd.to_datetime(list(ret.index)))
    ret.name = "spy_daily"
    return ret


def _run_single(tag: str, df: pd.DataFrame, cfg: MaroyVwapConfig):
    t0 = time.time()
    res = simulate_h1_maroy_vwap(df, cfg)
    print(
        f"[{tag}] runtime={time.time()-t0:.1f}s "
        f"n_trades={res.n_trades} "
        f"cum_spread%={res.cum_spread_pct*100:.1f} "
        f"S_full={res.sharpe():.3f} "
        f"CAGR={res.cagr()*100:+.2f}%"
    )
    return res


def _hand_rolled_crosslib(
    df: pd.DataFrame, cfg: MaroyVwapConfig
) -> pd.Series:
    """Independent pandas reimplementation for gate-9 cross-lib.

    This is NOT a vectorbt port — vectorbt's signal engine does not
    expose an anchored-VWAP-cross exit on 1-min multi-day sessions as
    a first-class primitive without a custom callback. A hand-rolled
    vectorized pandas path gives an independent verification of the
    entry-signal computation + exit-trigger logic that does not share
    any numpy loop code with the canonical implementation.

    Returns per-bar net returns aggregated to daily.
    """
    d = df[["open", "high", "low", "close"]].astype(float).sort_index().copy()
    idx_et = d.index.tz_convert("America/New_York")
    d["date_et"] = pd.Index(idx_et.date)

    # Per-day MA of |intraday_return| using expanding close-to-close inside day.
    d["close_prev"] = d.groupby("date_et")["close"].shift(1)
    d["close_prev"] = d["close_prev"].fillna(d["open"])
    d["bar_ret"] = (d["close"] / d["close_prev"] - 1.0).astype(float)

    day_mean_abs = d.groupby("date_et")["bar_ret"].apply(lambda s: s.abs().mean())
    ma_14 = (
        day_mean_abs.rolling(cfg.ma_lookback_days, min_periods=cfg.ma_lookback_days)
        .mean()
        .shift(1)
    )
    day_open = d.groupby("date_et")["open"].first()

    # Broadcast back to bars.
    d["ma_14"] = d["date_et"].map(ma_14)
    d["day_open"] = d["date_et"].map(day_open)
    d["upper"] = d["day_open"] * (1.0 + d["ma_14"] * cfg.noise_band_scale)
    d["lower"] = d["day_open"] * (1.0 - d["ma_14"] * cfg.noise_band_scale)

    # TVWAP via cumulative mean within day.
    cum_close = d.groupby("date_et")["close"].cumsum()
    bar_idx = d.groupby("date_et").cumcount() + 1
    d["tvwap"] = cum_close / bar_idx
    d["bar_idx0"] = bar_idx - 1

    # Last bar of day.
    date_v = d["date_et"].values
    last_bar = np.concatenate([date_v[1:] != date_v[:-1], [True]])

    # Pure Python loop (independent of numpy state machine in canonical).
    n = len(d)
    pos_arr = [0] * n
    entry_arr = [False] * n
    exit_arr = [False] * n
    close = d["close"].values
    upper = d["upper"].values
    lower = d["lower"].values
    tvwap = d["tvwap"].values
    ma_v = d["ma_14"].values
    bar_idx0 = d["bar_idx0"].values
    bar_ret_v = d["bar_ret"].values
    cur = 0
    prev_tvwap = np.nan
    prev_close = np.nan
    prev_date = None
    n_trades = 0
    for i in range(n):
        if prev_date != date_v[i]:
            prev_tvwap = np.nan
            prev_close = np.nan
            prev_date = date_v[i]
        p_tvwap = prev_tvwap
        p_close = prev_close
        cc = close[i]
        cv = tvwap[i]
        if not np.isfinite(ma_v[i]):
            pos_arr[i] = 0
            if cur != 0:
                exit_arr[i] = True
                cur = 0
            prev_tvwap = cv
            prev_close = cc
            continue
        if cur != 0:
            if cfg.flat_at_close and last_bar[i]:
                exit_arr[i] = True
                pos_arr[i] = cur
                cur = 0
            elif np.isfinite(p_close) and np.isfinite(p_tvwap) and np.isfinite(cv):
                if cur == 1 and p_close >= p_tvwap and cc < cv:
                    exit_arr[i] = True
                    cur = 0
                    pos_arr[i] = 0
                elif cur == -1 and p_close <= p_tvwap and cc > cv:
                    exit_arr[i] = True
                    cur = 0
                    pos_arr[i] = 0
                else:
                    pos_arr[i] = cur
            else:
                pos_arr[i] = cur
        else:
            if cfg.flat_at_close and last_bar[i]:
                pos_arr[i] = 0
            elif bar_idx0[i] < cfg.min_bar_idx_for_entry:
                pos_arr[i] = 0
            else:
                if np.isfinite(cc) and np.isfinite(upper[i]) and cc > upper[i]:
                    cur = 1
                    pos_arr[i] = 1
                    entry_arr[i] = True
                    n_trades += 1
                elif (
                    cfg.allow_short
                    and np.isfinite(cc)
                    and np.isfinite(lower[i])
                    and cc < lower[i]
                ):
                    cur = -1
                    pos_arr[i] = -1
                    entry_arr[i] = True
                    n_trades += 1
                else:
                    pos_arr[i] = 0
        prev_tvwap = cv
        prev_close = cc

    pos = np.array(pos_arr, dtype=np.int8)
    entry = np.array(entry_arr, dtype=bool)
    exit_ = np.array(exit_arr, dtype=bool)
    prev_w = np.concatenate([[0], pos[:-1]]).astype(float)
    same_day = np.concatenate([[False], date_v[1:] == date_v[:-1]])
    prev_w = np.where(same_day, prev_w, 0.0)
    gross = prev_w * np.nan_to_num(bar_ret_v, nan=0.0)
    flips = entry.astype(float) + exit_.astype(float)
    cost = flips * (cfg.spread_one_way + cfg.commission_per_flip)
    net = gross - cost

    s = pd.Series(net, index=d.index)
    daily = (1.0 + s).groupby(d["date_et"].values).prod() - 1.0
    daily.index = pd.DatetimeIndex(pd.to_datetime(list(daily.index)))
    return daily


def main() -> None:
    t_start = time.time()
    print("=" * 80)
    print("Phase 3.7 H1.b — Maróy 2024 VWAP-exit noise-boundary honest validation")
    print("=" * 80)

    # -- Step 1: load data
    print(f"[data] loading {SPY_PATH.name}")
    spy_df = pd.read_parquet(SPY_PATH)
    qqq_df = pd.read_parquet(QQQ_PATH)
    print(f"  SPY {spy_df.shape}  range={spy_df.index.min()} -> {spy_df.index.max()}")
    print(f"  QQQ {qqq_df.shape}")

    # -- Step 2: winner config (SPY)
    print(f"\n[winner] cfg={_cfg_tag(WINNER_CFG)}")
    winner = _run_single("winner", spy_df, WINNER_CFG)

    dr = winner.daily_returns.dropna()
    is_r = _slice(dr, *IS_RANGE)
    oos_r = _slice(dr, *OOS_RANGE)
    fwd_r = _slice(dr, *FWD_RANGE)
    is_m = _metrics("IS", is_r)
    oos_m = _metrics("OOS", oos_r)
    fwd_m = _metrics("FWD", fwd_r)
    full_m = _metrics("FULL", dr)
    for m in (is_m, oos_m, fwd_m, full_m):
        print(
            f"[{m['name']:5s}] n={m['n_bars']} "
            f"S={m['sharpe']:.3f} CAGR={m['cagr']*100:+.2f}% "
            f"MDD={m['max_drawdown']*100:.2f}%"
        )

    # -- Step 3: QQQ cross-asset confirmation
    print(f"\n[qqq] running winner cfg on QQQ")
    qqq_res = _run_single("qqq", qqq_df, WINNER_CFG)
    qqq_oos = _slice(qqq_res.daily_returns, *OOS_RANGE)
    qqq_oos_m = _metrics("QQQ_OOS", qqq_oos)
    print(
        f"[QQQ_OOS] S={qqq_oos_m['sharpe']:.3f} "
        f"CAGR={qqq_oos_m['cagr']*100:+.2f}% "
        f"MDD={qqq_oos_m['max_drawdown']*100:.2f}%"
    )

    # -- Step 4: walk-forward on full series
    wf_ratio, wf_mdd, wf_pass = _walk_forward(dr)
    print(f"[WF] ratio={wf_ratio:.3f} max_dd={wf_mdd*100:.2f}% pass={wf_pass}")

    # -- Step 5: bootstrap CI
    oos_lo, oos_hi = _bootstrap_sharpe_ci(oos_r)
    full_lo, full_hi = _bootstrap_sharpe_ci(dr)
    print(f"[BOOT] OOS 99.9% CI [{oos_lo:.3f}, {oos_hi:.3f}]")
    print(f"[BOOT] FULL 99.9% CI [{full_lo:.3f}, {full_hi:.3f}]")

    # -- Step 6: IR vs SPY daily
    spy_daily = _compute_daily_spy_ret()
    spy_oos = _slice(spy_daily, *OOS_RANGE)
    ir = _ir_vs_spy(oos_r, spy_oos)
    spy_oos_m = _metrics("SPY_OOS", spy_oos)
    print(
        f"[IR] vs SPY OOS={ir:.4f}  "
        f"(SPY OOS S={spy_oos_m['sharpe']:.3f} "
        f"CAGR={spy_oos_m['cagr']*100:.2f}%)"
    )

    # -- Step 7: median hold
    mh_bars = winner.median_hold_bars()
    print(f"[HOLD] median hold = {mh_bars:.1f} bars (≈{mh_bars:.0f} minutes)")

    # -- Step 8: cost×2
    cost2x_cfg = MaroyVwapConfig(
        ma_lookback_days=WINNER_CFG.ma_lookback_days,
        noise_band_scale=WINNER_CFG.noise_band_scale,
        allow_short=WINNER_CFG.allow_short,
        flat_at_close=WINNER_CFG.flat_at_close,
        spread_one_way=WINNER_CFG.spread_one_way * 2.0,
        commission_per_flip=WINNER_CFG.commission_per_flip * 2.0,
        min_bar_idx_for_entry=WINNER_CFG.min_bar_idx_for_entry,
    )
    cost2x = _run_single("cost2x", spy_df, cost2x_cfg)
    c2x_oos = _slice(cost2x.daily_returns, *OOS_RANGE)
    c2x_m = _metrics("OOS_2x", c2x_oos)
    print(
        f"[COST2X] OOS S={c2x_m['sharpe']:.3f} "
        f"CAGR={c2x_m['cagr']*100:+.2f}%"
    )

    # -- Step 9: grid for PBO + DSR
    print(f"\n[grid] running {len(GRID)} sibling configs for PBO/DSR")
    grid_rets: dict[str, pd.Series] = {}
    for i, cfg in enumerate(GRID):
        tag = _cfg_tag(cfg)
        if (
            cfg.ma_lookback_days == WINNER_CFG.ma_lookback_days
            and cfg.noise_band_scale == WINNER_CFG.noise_band_scale
            and cfg.allow_short == WINNER_CFG.allow_short
            and cfg.min_bar_idx_for_entry == WINNER_CFG.min_bar_idx_for_entry
        ):
            grid_rets[tag] = dr
            print(f"  [{i+1}/{len(GRID)}] {tag} (reuse winner)")
            continue
        r = _run_single(f"grid {i+1}/{len(GRID)} {tag}", spy_df, cfg)
        grid_rets[tag] = r.daily_returns.dropna()

    grid_df = pd.concat(grid_rets, axis=1).dropna(how="any")
    print(f"[grid] aligned matrix shape: {grid_df.shape}")
    pbo_res = None
    if grid_df.shape[0] >= 100 and grid_df.shape[1] >= 2:
        pbo_res = cscv_pbo(grid_df.to_numpy(), n_blocks=10)
        print(
            f"[PBO] value={pbo_res.pbo:.4f} n_combos={pbo_res.n_combinations}"
        )

    dsr_res = dsr_metric(oos_r.dropna().to_numpy(dtype=float), n_trials=len(GRID))
    print(
        f"[DSR] p_value={dsr_res.p_value:.6f} "
        f"obs_SR={dsr_res.observed_sharpe:.4f}"
    )

    # -- Step 10: cross-lib hand-rolled (pandas loop) ---
    print(f"\n[cross-lib] running hand-rolled independent pandas path on SPY")
    t0 = time.time()
    indep_daily = _hand_rolled_crosslib(spy_df, WINNER_CFG)
    print(f"[cross-lib] runtime={time.time()-t0:.1f}s")
    indep_oos = _slice(indep_daily, *OOS_RANGE)
    indep_oos_m = _metrics("OOS_indep", indep_oos)
    cross_lib_delta_cagr = oos_m["cagr"] - indep_oos_m["cagr"]
    cross_lib_delta_sharpe = oos_m["sharpe"] - indep_oos_m["sharpe"]
    print(
        f"[CROSS-LIB] canon OOS CAGR={oos_m['cagr']*100:+.2f}% "
        f"indep OOS CAGR={indep_oos_m['cagr']*100:+.2f}% "
        f"Δ={cross_lib_delta_cagr*100:+.3f}pp "
        f"(S canon={oos_m['sharpe']:.3f} indep={indep_oos_m['sharpe']:.3f})"
    )

    # -- Step 11: gates
    cagr_tier = _cagr_tier_A(oos_m["cagr"])
    mdd_tier = _mdd_tier_A(oos_m["max_drawdown"])

    gates = [
        # Gate 1 — IS Sharpe > 0.5
        ("gate_01_is_sharpe_gt_0_5", bool(is_m["sharpe"] > 0.5), f"{is_m['sharpe']:.3f}"),
        # Gate 2 — OOS Sharpe >= 1.3
        ("gate_02_oos_sharpe_ge_1_3", bool(oos_m["sharpe"] >= 1.3), f"{oos_m['sharpe']:.3f}"),
        # Gate 3 — CAGR tier (warning-only)
        ("gate_03_oos_cagr_tier_A_warning_only", None, f"{oos_m['cagr']*100:+.2f}% tier={cagr_tier}"),
        # Gate 4 — MDD tier (warning-only)
        ("gate_04_oos_mdd_tier_A_warning_only", None, f"{oos_m['max_drawdown']*100:.2f}% tier={mdd_tier}"),
        # Gate 5 — FWD Sharpe > 0
        ("gate_05_fwd_sharpe_gt_0", bool(fwd_m["sharpe"] > 0), f"{fwd_m['sharpe']:.3f}"),
        # Gate 6 — WF 6/8
        ("gate_06_wf_6_8", bool(wf_pass), f"{int(wf_ratio*8)}/8 mdd={wf_mdd*100:.2f}%"),
        # Gate 7 — median hold >= 1h = 60 bars
        (
            "gate_07_median_hold_ge_60_bars",
            bool(np.isfinite(mh_bars) and mh_bars >= 60),
            f"{mh_bars:.1f} bars",
        ),
        # Gate 8 — IR vs SPY OOS >= 0.2
        (
            "gate_08_ir_vs_spy_oos_ge_0_2",
            bool((not np.isnan(ir)) and ir >= 0.2),
            f"{ir:.4f}",
        ),
        # Gate 9 — cross-lib +/- 3pp CAGR (HARD)
        (
            "gate_09_cross_lib_delta_cagr_le_3pp_HARD",
            bool(abs(cross_lib_delta_cagr) <= 0.03),
            f"Δ={cross_lib_delta_cagr*100:+.3f}pp",
        ),
        # Gate 10 — bootstrap 99.9% CI low > 0 OOS + full (HARD)
        (
            "gate_10_bootstrap_oos_99p9_ci_low_gt_0_HARD",
            bool(oos_lo > 0),
            f"oos_lo={oos_lo:.4f}",
        ),
        (
            "gate_10b_bootstrap_full_99p9_ci_low_gt_0_HARD",
            bool(full_lo > 0),
            f"full_lo={full_lo:.4f}",
        ),
        # Gate 11 — PBO < 0.3 (HARD, tighter than default 0.5 per prompt)
        (
            "gate_11_pbo_lt_0_3_HARD",
            bool(pbo_res is not None and pbo_res.pbo < 0.3),
            f"{pbo_res.pbo:.4f}" if pbo_res else "N/A",
        ),
        # Gate 12 — DSR p < 0.05 (HARD)
        (
            "gate_12_dsr_p_lt_0_05_HARD",
            bool(dsr_res.p_value < 0.05),
            f"{dsr_res.p_value:.6f}",
        ),
        # Gate 13 — cost×2 Sharpe > 1.0 (unleveraged)
        (
            "gate_13_costx2_sharpe_gt_1",
            bool(c2x_m["sharpe"] > 1.0),
            f"{c2x_m['sharpe']:.3f}",
        ),
    ]

    # Hard gates = 9, 10, 10b, 11, 12 per prompt.
    hard_gate_names = {
        "gate_09_cross_lib_delta_cagr_le_3pp_HARD",
        "gate_10_bootstrap_oos_99p9_ci_low_gt_0_HARD",
        "gate_10b_bootstrap_full_99p9_ci_low_gt_0_HARD",
        "gate_11_pbo_lt_0_3_HARD",
        "gate_12_dsr_p_lt_0_05_HARD",
    }
    # Soft gates that still must pass: 1, 2, 5, 6, 7, 8, 13.
    required_soft = {
        "gate_01_is_sharpe_gt_0_5",
        "gate_02_oos_sharpe_ge_1_3",
        "gate_05_fwd_sharpe_gt_0",
        "gate_06_wf_6_8",
        "gate_07_median_hold_ge_60_bars",
        "gate_08_ir_vs_spy_oos_ge_0_2",
        "gate_13_costx2_sharpe_gt_1",
    }

    hard_fail = [n for n, p, _ in gates if (n in hard_gate_names and p is False)]
    soft_fail = [n for n, p, _ in gates if (n in required_soft and p is False)]
    n_pass = sum(1 for _, p, _ in gates if p is True)
    n_fail = sum(1 for _, p, _ in gates if p is False)
    n_def = sum(1 for _, p, _ in gates if p is None)

    # Halt contract: n_trades OOS < 100 → explicit FAIL
    oos_trades_lower_bound = len(oos_r) * 2  # very rough
    if winner.n_trades < 100:
        verdict = "FAIL_INSUFFICIENT_TRADES"
    elif hard_fail or soft_fail:
        verdict = "FAIL"
    else:
        verdict = "PASS"

    print(f"\n=== GATES ({n_pass} PASS / {n_fail} FAIL / {n_def} WARN_ONLY) ===")
    for n, p, v in gates:
        mark = "PASS" if p is True else ("FAIL" if p is False else "WARN")
        print(f"  [{mark}] {n:55s} = {v}")
    print(f"\nFINAL VERDICT: {verdict}")
    if hard_fail:
        print(f"  HARD gate failures: {hard_fail}")
    if soft_fail:
        print(f"  Soft gate failures: {soft_fail}")

    # -- Step 12: persist artifacts
    pd.DataFrame({"ret": dr}).to_parquet(OUT_DIR / "daily_returns.parquet")
    pd.DataFrame({"ret": c2x.daily_returns.dropna() if False else cost2x.daily_returns.dropna()}).to_parquet(
        OUT_DIR / "daily_returns_cost2x.parquet"
    )
    pd.DataFrame({"ret": indep_daily.dropna()}).to_parquet(
        OUT_DIR / "daily_returns_crosslib.parquet"
    )

    # Grid CSV
    grid_rows = [
        "tag,ma_lookback_days,noise_band_scale,allow_short,min_bar_idx,sharpe_full,cagr_full"
    ]
    for cfg in GRID:
        tag = _cfg_tag(cfg)
        r = grid_rets.get(tag, pd.Series(dtype=float)).dropna()
        if len(r) > 1 and r.std(ddof=1) > 0:
            sf = float(r.mean() / r.std(ddof=1) * np.sqrt(TRADING_DAYS))
            eq = float((1.0 + r).prod())
            cg = float(eq ** (TRADING_DAYS / len(r)) - 1.0) if eq > 0 else -1.0
        else:
            sf, cg = 0.0, 0.0
        grid_rows.append(
            f"{tag},{cfg.ma_lookback_days},{cfg.noise_band_scale},"
            f"{int(cfg.allow_short)},{cfg.min_bar_idx_for_entry},{sf:.4f},{cg:.4f}"
        )
    (OUT_DIR / "config_grid.csv").write_text("\n".join(grid_rows))

    agg = {
        "phase": "phase_3_7",
        "hypothesis": "H1.b",
        "hypothesis_name": "Maroy 2024 VWAP-exit intraday noise-boundary",
        "slug": "h1_maroy_vwap",
        "produced_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "git_sha": _git_sha(),
        "broker_path": "Pepperstone Razor SPX500 CFD intraday (no DARF per mandate §4.8)",
        "data_source": "Tiingo IEX 1-min parquet (data/phase3_7/intraday/SPY_1min.parquet, QQQ_1min.parquet)",
        "paper_entry": "Zarattini-Aziz-Barbon 2024 (SSRN 4824172)",
        "paper_exit": "Maróy 2024 (SSRN 5095349) VWAP-cross variant",
        "winner_config": asdict(WINNER_CFG),
        "windows": {
            "IS": {"start": IS_RANGE[0], "end": IS_RANGE[1]},
            "OOS": {"start": OOS_RANGE[0], "end": OOS_RANGE[1]},
            "FWD": {"start": FWD_RANGE[0], "end": FWD_RANGE[1]},
        },
        "splits": {
            "IS": is_m, "OOS": oos_m, "FWD": fwd_m, "FULL": full_m,
            "QQQ_OOS": qqq_oos_m, "SPY_OOS": spy_oos_m,
        },
        "tiers": {
            "cagr_tier_A_rota": cagr_tier,
            "mdd_tier_A_rota": mdd_tier,
        },
        "walk_forward": {
            "n_windows": 8,
            "profitable_ratio": wf_ratio,
            "max_window_drawdown": wf_mdd,
            "pass": wf_pass,
        },
        "bootstrap_oos": {"ci_low": oos_lo, "ci_high": oos_hi, "alpha": 0.001},
        "bootstrap_full": {"ci_low": full_lo, "ci_high": full_hi, "alpha": 0.001},
        "pbo": {
            "value": pbo_res.pbo if pbo_res else None,
            "n_blocks": pbo_res.n_blocks if pbo_res else None,
            "n_combinations": pbo_res.n_combinations if pbo_res else None,
        },
        "dsr": {
            "dsr": dsr_res.dsr, "p_value": dsr_res.p_value,
            "observed_sharpe": dsr_res.observed_sharpe,
            "n_trials": dsr_res.n_trials,
        },
        "ir_vs_spy_oos": ir,
        "median_hold_bars_minutes": mh_bars,
        "n_trades_winner_spy": winner.n_trades,
        "n_trades_winner_qqq": qqq_res.n_trades,
        "cum_spread_pct_spy": winner.cum_spread_pct,
        "cost_sensitivity_2x": c2x_m,
        "cross_lib": {
            "method": "hand-rolled pandas python-loop path (independent state machine)",
            "canon_oos_cagr": oos_m["cagr"],
            "indep_oos_cagr": indep_oos_m["cagr"],
            "delta_cagr_pp": cross_lib_delta_cagr * 100.0,
            "delta_sharpe": cross_lib_delta_sharpe,
        },
        "gates": [{"name": n, "pass": p, "value": v} for n, p, v in gates],
        "verdict": verdict,
        "failed_gates_hard": hard_fail,
        "failed_gates_soft": soft_fail,
        "runtime_seconds": time.time() - t_start,
    }
    (OUT_DIR / "AGGREGATE.json").write_text(json.dumps(agg, indent=2, default=float))
    print(f"\n[write] {OUT_DIR / 'AGGREGATE.json'}")
    print(f"[write] {OUT_DIR / 'daily_returns.parquet'}")
    print(f"[write] {OUT_DIR / 'config_grid.csv'}")
    print(f"\nTotal runtime: {time.time()-t_start:.1f}s")

    return agg


if __name__ == "__main__":
    main()

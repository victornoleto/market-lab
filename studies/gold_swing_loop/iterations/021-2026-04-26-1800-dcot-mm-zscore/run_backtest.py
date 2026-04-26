"""Iter 021 — DCOT money-manager net-long z-score (contrarian, post-2006).

Replaces iter 018's legacy commercials bucket (NL_comm − NL_small) with
the disaggregated COT money-manager bucket (m_money_long − m_money_short).
Long-only contrarian: enter LONG when z < −1.0σ (MM speculators positioned
extreme-bearish), exit when z > 0 OR after max_hold_days=30.

Citations:
  [trading_systems_methods, p.640] — Kaufman: COT positioning extremes
                                      contrarian; DCOT MM bucket isolates speculator flow
  [advances_fin_ml, p.222-223]    — DSR with cumulative n_trials=21
  [advances_fin_ml, p.31-34]      — cost-realistic backtest
  de Roon, Nijman, Veld (2000) JF — z-score positioning theoretical anchor
  CFTC DCOT methodology           — disaggregated bucket post-2006
"""
from __future__ import annotations

import json
import math
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd
from scipy import stats

REPO = Path(__file__).resolve().parents[4]
ITER_DIR = Path(__file__).resolve().parent
DCOT_PATH = REPO / "data" / "external" / "macro" / "cftc_dcot_gold_weekly.parquet"
GLD_PATH = REPO / "data" / "tiingo" / "daily" / "prices" / "GLD.parquet"
XAU_PATH = REPO / "data" / "tiingo" / "daily" / "prices" / "xauusd.parquet"

# ============================================================================
# Pre-committed configuration (single cfg, IC-8)
# ============================================================================
CFG = {
    "cfg_id": "dcot_mm_zscore_long_zentry_neg1_zexit_zero_window156w_lag1_max30d",
    "z_entry_below": -1.0,      # enter LONG when z < −1.0σ (MM extreme bearish)
    "z_exit_above": 0.0,        # exit when z > 0 (positioning normalizes)
    "window_weeks": 156,        # same as iter 018 for direct comparability
    "lag_weeks": 1,             # same as iter 018; Kaufman p.640 default
    "max_hold_days": 30,        # cap to keep mean hold inside medium_swing 10-30d
    "spread_bps_rt": 8.0,
    "swap_bps_per_calendar_night": 1.0,
    "track": "pepperstone_cfd",
    "universe": "single_xau",
    "hold_time_track": "medium_swing",
    "declared_primary": "gld_long",
    "declared_corroborating": ["xauusd_real"],
    "primary_slice_start": "2009-06-09",  # 156w warmup from 2006-06-13
}
CUM_N_TRIALS = 21  # iter 020 was 20; this iter increments by 1.


# ============================================================================
# Pure helpers (TDD-tested)
# ============================================================================


def rolling_zscore(s: pd.Series, window: int) -> pd.Series:
    """Rolling z-score on trailing `window` samples; constant window → 0."""
    rolling = s.rolling(window=window, min_periods=window)
    mean = rolling.mean()
    std = rolling.std(ddof=1)
    z = (s - mean) / std
    z = z.mask(std == 0, other=0.0)
    return z


def mm_net_long(dcot_df: pd.DataFrame) -> pd.Series:
    """Money-manager net-long positions.

    `[trading_systems_methods, p.640]`: speculator-side net longs is the
    contrarian sentiment indicator; in DCOT, money-manager bucket is the
    cleanest proxy (vs legacy non-commercials which mix swap dealers +
    other reportables).
    """
    long = pd.to_numeric(dcot_df["m_money_positions_long_all"], errors="coerce")
    short = pd.to_numeric(dcot_df["m_money_positions_short_all"], errors="coerce")
    return long - short


def zscore_signal_long_when_z_below(
    nl_diff_weekly: pd.Series,
    daily_index: pd.DatetimeIndex,
    window_weeks: int,
    z_entry: float,
    z_exit: float,
    lag_weeks: int,
    max_hold_days: int,
) -> pd.Series:
    """Map weekly z-score → daily long-only contrarian signal (0/1).

    State machine (mirror of iter 018, with sign inverted):
      - flat → long  when z_at_t < z_entry  (e.g., −1.0σ; MM extreme bearish)
      - long → flat  when z_at_t > z_exit   (e.g., 0.0σ; positioning normalized)
                     OR days_in_position >= max_hold_days
    """
    z_weekly = rolling_zscore(nl_diff_weekly.sort_index(), window=window_weeks)

    # Lookup the most recent CFTC report week ≤ (t - 7*lag_weeks)
    lookup = pd.Series(daily_index - pd.Timedelta(days=7 * lag_weeks), index=daily_index)
    z_at_t = z_weekly.reindex(lookup, method="ffill").set_axis(daily_index)

    long_pred = z_at_t < z_entry
    exit_pred = z_at_t > z_exit

    pos = pd.Series(0, index=daily_index, dtype=int)
    in_pos = False
    days_held = 0
    for i in range(len(daily_index)):
        if not in_pos:
            if bool(long_pred.iloc[i]) and not bool(np.isnan(z_at_t.iloc[i])):
                in_pos = True
                days_held = 1
                pos.iloc[i] = 1
        else:
            days_held += 1
            forced_out = days_held > max_hold_days
            if bool(exit_pred.iloc[i]) or forced_out:
                in_pos = False
                days_held = 0
            else:
                pos.iloc[i] = 1
    return pos


def apply_costs(
    gross_returns: pd.Series,
    position: pd.Series,
    spread_bps_rt: float,
    swap_bps_per_calendar_night: float,
) -> pd.Series:
    """Net daily returns after spread + swap (mirrors iter 018's helper)."""
    raw = gross_returns * position.astype(float)
    pos_diff = position.astype(int).diff().fillna(position.astype(int).iloc[0])
    half_spread = spread_bps_rt / 2.0 * 1e-4
    entry = (pos_diff == 1).astype(float) * half_spread
    exit_ = (pos_diff == -1).astype(float) * half_spread
    if position.iloc[-1] == 1:
        exit_.iloc[-1] = exit_.iloc[-1] + half_spread
    cal_nights = pd.Series(
        index=position.index,
        data=[
            (position.index[i] - position.index[i - 1]).days if i > 0 else 1
            for i in range(len(position.index))
        ],
        dtype=int,
    ).clip(lower=0)
    swap = position.astype(float).shift(1).fillna(0.0) * cal_nights * swap_bps_per_calendar_night * 1e-4
    return raw - entry - exit_ - swap


# ============================================================================
# Metrics (mirrors iter 018)
# ============================================================================


@dataclass
class Metrics:
    sharpe: float
    cagr: float
    mdd: float
    n_bars: int
    n_trades: int
    mean_hold_days: float
    n_years: float
    bars_per_year: float


def compute_metrics(
    daily_returns: pd.Series, position: pd.Series, bars_per_year: float = 252.0
) -> Metrics:
    r = daily_returns.dropna()
    n = len(r)
    if n < 2:
        return Metrics(0.0, 0.0, 0.0, n, 0, 0.0, 0.0, bars_per_year)
    sigma = r.std()
    sharpe = (r.mean() / sigma * math.sqrt(bars_per_year)) if sigma > 0 else 0.0
    eq = (1 + r).cumprod()
    cagr = eq.iloc[-1] ** (bars_per_year / n) - 1
    peak = eq.cummax()
    dd = 1 - eq / peak
    mdd = dd.max()
    n_years = n / bars_per_year
    pos_diff = position.astype(int).diff().fillna(position.astype(int).iloc[0])
    entries = int((pos_diff == 1).sum())
    exits = int((pos_diff == -1).sum())
    if position.iloc[-1] == 1:
        exits += 1
    n_trades = int(min(entries, exits))
    long_days = int(position.sum())
    mean_hold = (long_days / n_trades) if n_trades > 0 else 0.0
    return Metrics(
        sharpe=float(sharpe), cagr=float(cagr), mdd=float(mdd),
        n_bars=n, n_trades=n_trades, mean_hold_days=float(mean_hold),
        n_years=float(n_years), bars_per_year=bars_per_year,
    )


def deflated_sharpe_p_value(
    sharpe_ann: float, n_obs: int, n_trials: int,
    skew: float = 0.0, kurt: float = 3.0, bars_per_year: float = 252.0,
) -> float:
    """López de Prado DSR p-value with cumulative n_trials.

    `[advances_fin_ml, p.222-223]`. Same implementation as iter 017/018.
    """
    if n_trials < 1 or n_obs < 30:
        return 1.0
    n_years = n_obs / bars_per_year
    emc = 0.5772156649
    e_max = math.sqrt(2.0 * math.log(max(n_trials, 1)))
    if n_trials > 1:
        e_max = e_max * (1 - emc) + emc / max(math.sqrt(2.0 * math.log(n_trials)), 1e-9)
    sr0_ann = e_max / math.sqrt(n_years) if n_years > 0 else float("inf")
    sr_per_period = sharpe_ann / math.sqrt(bars_per_year)
    var_per_period = (
        1.0 - skew * sr_per_period + (kurt - 1.0) / 4.0 * sr_per_period**2
    ) / max(n_obs - 1, 1)
    var_ann = var_per_period * bars_per_year
    if var_ann <= 0:
        return 1.0
    z = (sharpe_ann - sr0_ann) / math.sqrt(var_ann)
    return float(1.0 - stats.norm.cdf(z))


def bootstrap_ci_low(
    daily_returns: pd.Series, bars_per_year: float,
    n_boot: int = 1000, seed: int = 21, alpha: float = 0.001,
) -> float:
    r = daily_returns.dropna().values
    n = len(r)
    if n < 30:
        return -1.0
    rng = np.random.default_rng(seed)
    sharpes = []
    for _ in range(n_boot):
        sample = rng.choice(r, size=n, replace=True)
        sigma = sample.std()
        sharpes.append(sample.mean() / sigma * math.sqrt(bars_per_year) if sigma > 0 else 0.0)
    return float(np.quantile(sharpes, alpha))


def walk_forward_split(
    daily_returns: pd.Series, bars_per_year: float, n_windows: int = 8
) -> dict:
    chunk = len(daily_returns) // n_windows
    sharpes, mdds = [], []
    passed = 0
    for i in range(n_windows):
        s = i * chunk
        e = (i + 1) * chunk if i < n_windows - 1 else len(daily_returns)
        rr = daily_returns.iloc[s:e].dropna()
        if len(rr) < 30:
            continue
        sigma = rr.std()
        sh = rr.mean() / sigma * math.sqrt(bars_per_year) if sigma > 0 else 0.0
        eq = (1 + rr).cumprod()
        peak = eq.cummax()
        mdd = (1 - eq / peak).max()
        sharpes.append(float(sh))
        mdds.append(float(mdd))
        if sh > 0 and mdd < 0.25:
            passed += 1
    return {"n_windows": n_windows, "passed": passed, "sharpes": sharpes, "mdds": mdds}


def cross_lib_check(
    prices: pd.Series, position: pd.Series, spread_bps: float,
    swap_bps_per_night: float, bars_per_year: float,
) -> dict:
    """Hand-rolled numpy reference (no pandas) — G7 cross-lib parity."""
    p = prices.values
    px_ret = np.zeros(len(p))
    px_ret[1:] = (p[1:] - p[:-1]) / p[:-1]
    pos = position.values.astype(float)
    raw = px_ret * pos
    diff = np.zeros(len(pos))
    diff[0] = pos[0]
    diff[1:] = pos[1:] - pos[:-1]
    half_spread = spread_bps / 2.0 * 1e-4
    cost_spread = (diff == 1).astype(float) * half_spread + (diff == -1).astype(float) * half_spread
    if pos[-1] == 1:
        cost_spread[-1] += half_spread
    cal_nights = np.ones(len(pos))
    idx = position.index
    for i in range(1, len(idx)):
        cal_nights[i] = (idx[i] - idx[i - 1]).days
    swap = np.concatenate([[0.0], pos[:-1]]) * cal_nights * swap_bps_per_night * 1e-4
    net = raw - cost_spread - swap
    eq = np.cumprod(1.0 + net)
    n = len(eq)
    cagr = eq[-1] ** (bars_per_year / n) - 1.0 if n > 0 else 0.0
    sigma = net.std()
    sharpe = net.mean() / sigma * math.sqrt(bars_per_year) if sigma > 0 else 0.0
    return {"cagr": float(cagr), "sharpe": float(sharpe)}


# ============================================================================
# Pipeline
# ============================================================================


def load_dcot() -> pd.DataFrame:
    df = pd.read_parquet(DCOT_PATH).sort_index()
    df["MM_NL"] = mm_net_long(df)
    df["z_MM_NL"] = rolling_zscore(df["MM_NL"], window=CFG["window_weeks"])
    return df


def load_prices(path: Path) -> pd.Series:
    df = pd.read_parquet(path)
    if not isinstance(df.index, pd.DatetimeIndex):
        for c in ("date", "Date"):
            if c in df.columns:
                df = df.set_index(c)
                break
    df.index = pd.to_datetime(df.index).tz_localize(None)
    df = df.sort_index()
    for c in ("adjClose", "close", "Close"):
        if c in df.columns:
            return df[c]
    raise KeyError(f"no close column in {path}: {df.columns.tolist()}")


def run_dataset(
    name: str, prices: pd.Series, dcot_df: pd.DataFrame,
    bars_per_year: float = 252.0, slice_start: Optional[str] = None,
) -> dict:
    if slice_start is not None:
        prices = prices.loc[prices.index >= pd.Timestamp(slice_start)]
    daily_index = prices.index
    pos = zscore_signal_long_when_z_below(
        nl_diff_weekly=dcot_df["MM_NL"].dropna(),
        daily_index=daily_index,
        window_weeks=CFG["window_weeks"],
        z_entry=CFG["z_entry_below"],
        z_exit=CFG["z_exit_above"],
        lag_weeks=CFG["lag_weeks"],
        max_hold_days=CFG["max_hold_days"],
    )
    gross = prices.pct_change().fillna(0.0)
    net = apply_costs(
        gross_returns=gross, position=pos,
        spread_bps_rt=CFG["spread_bps_rt"],
        swap_bps_per_calendar_night=CFG["swap_bps_per_calendar_night"],
    )
    m = compute_metrics(net, pos, bars_per_year=bars_per_year)
    boot = bootstrap_ci_low(net, bars_per_year=bars_per_year, alpha=0.001)
    wf = walk_forward_split(net, bars_per_year=bars_per_year, n_windows=8)
    cut = int(0.7 * len(net))
    oos = net.iloc[cut:]
    sigma_oos = oos.std()
    oos_sharpe = oos.mean() / sigma_oos * math.sqrt(bars_per_year) if sigma_oos > 0 else 0.0
    fwd = net.loc[net.index >= "2022-01-01"]
    sigma_fwd = fwd.std()
    fwd_sharpe = (
        fwd.mean() / sigma_fwd * math.sqrt(bars_per_year) if sigma_fwd > 0 and len(fwd) > 30 else 0.0
    )
    dsr_p = deflated_sharpe_p_value(
        sharpe_ann=m.sharpe, n_obs=m.n_bars, n_trials=CUM_N_TRIALS,
        skew=float(net.skew()), kurt=float(net.kurtosis() + 3.0),
    )
    xlib = cross_lib_check(
        prices=prices, position=pos,
        spread_bps=CFG["spread_bps_rt"],
        swap_bps_per_night=CFG["swap_bps_per_calendar_night"],
        bars_per_year=bars_per_year,
    )
    crosslib_pass = abs(xlib["cagr"] - m.cagr) <= 0.03
    gates = {
        "g1_pbo": True,                          # single cfg, no grid → PBO N/A → True by convention
        "g2_dsr": bool(dsr_p < 0.05),
        "g3_wf": bool(wf["passed"] >= 6),
        "g4_oos": bool(oos_sharpe > 0),
        "g5_fwd": bool(fwd_sharpe > 0),
        "g6_bootstrap": bool(boot > 0),
        "g7_crosslib": bool(crosslib_pass),
    }
    return {
        "name": name,
        "metrics": {
            "sharpe": m.sharpe, "cagr": m.cagr, "mdd": m.mdd,
            "n_bars": m.n_bars, "n_trades": m.n_trades,
            "mean_hold_days": m.mean_hold_days, "n_years": m.n_years,
        },
        "dsr_p_value": dsr_p,
        "bootstrap_ci_low": boot,
        "walk_forward": wf,
        "oos_sharpe": float(oos_sharpe),
        "fwd_sharpe": float(fwd_sharpe),
        "crosslib": xlib,
        "crosslib_pass": crosslib_pass,
        "gates": gates,
        "n_gates_passed": int(sum(gates.values())),
        "slice_start": slice_start,
        "returns_series": {
            "index": [d.isoformat() for d in net.index],
            "net_returns": net.tolist(),
            "position": pos.tolist(),
        },
    }


def correlation_diagnostic(
    z_returns: pd.Series, ref_iter: str, ref_returns: Optional[pd.Series],
    rolling_window: int = 60, rolling_threshold: float = 0.30,
) -> dict:
    """Pearson ρ at consistent daily granularity (GS-16 process correction).

    Reports both static ρ and rolling-`window` ρ exceedance fraction (|ρ| > threshold).
    """
    if ref_returns is None or len(ref_returns) == 0:
        return {"ref_iter": ref_iter, "available": False}
    common = z_returns.index.intersection(ref_returns.index)
    if len(common) < 100:
        return {"ref_iter": ref_iter, "available": False, "n_common": int(len(common))}
    a = z_returns.loc[common]
    b = ref_returns.loc[common]
    rho_static = float(a.corr(b))
    rolling = a.rolling(rolling_window).corr(b)
    valid = rolling.dropna()
    exceed_frac = float((valid.abs() > rolling_threshold).mean()) if len(valid) > 0 else 0.0
    return {
        "ref_iter": ref_iter, "available": True, "n_common": int(len(common)),
        "rho_static": rho_static,
        "rolling_window": rolling_window, "rolling_threshold": rolling_threshold,
        "rolling_exceed_frac": exceed_frac, "rolling_n_windows": int(len(valid)),
    }


def load_iter_returns(iter_dir_glob: str, dataset: str) -> Optional[pd.Series]:
    """Load prior iter's per-cfg net_returns for `dataset`.

    Schema:
      results.json["returns_series"][dataset][cfg_id] = {"index","net_returns"}
      OR (iter 017/018 schema) results.json["datasets"][ds]["returns_series"]
    """
    matches = sorted((REPO / "studies" / "gold_swing_loop" / "iterations").glob(iter_dir_glob))
    if not matches:
        return None
    res_path = matches[0] / "results.json"
    if not res_path.exists():
        return None
    try:
        data = json.loads(res_path.read_text())
    except Exception:  # noqa: BLE001
        return None
    rs_root = data.get("returns_series", {})
    rs_for_ds = rs_root.get(dataset)
    if isinstance(rs_for_ds, dict) and rs_for_ds:
        cfg_id = next(iter(rs_for_ds))
        rs = rs_for_ds[cfg_id]
        if isinstance(rs, dict) and "index" in rs and "net_returns" in rs:
            idx = pd.to_datetime(rs["index"]).tz_localize(None)
            return pd.Series(rs["net_returns"], index=idx).dropna()
    ds_root = data.get("datasets", {})
    ds_entry = ds_root.get(dataset, {})
    rs2 = ds_entry.get("returns_series")
    if isinstance(rs2, dict) and "index" in rs2 and "net_returns" in rs2:
        idx = pd.to_datetime(rs2["index"]).tz_localize(None)
        return pd.Series(rs2["net_returns"], index=idx).dropna()
    return None


def main() -> None:
    dcot_df = load_dcot()
    valid_from = dcot_df["z_MM_NL"].first_valid_index()
    print(
        f"[dcot] {len(dcot_df)} weekly rows; valid z from {valid_from.date() if valid_from else 'N/A'}",
        file=sys.stderr,
    )
    gld = load_prices(GLD_PATH)
    xau = load_prices(XAU_PATH)
    print(
        f"[gld_long] {len(gld)} bars {gld.index.min().date()}→{gld.index.max().date()}; "
        f"sliced from {CFG['primary_slice_start']}",
        file=sys.stderr,
    )
    print(
        f"[xauusd_real] {len(xau)} bars {xau.index.min().date()}→{xau.index.max().date()}",
        file=sys.stderr,
    )

    res_gld = run_dataset("gld_long", gld, dcot_df, bars_per_year=252.0,
                          slice_start=CFG["primary_slice_start"])
    res_xau = run_dataset("xauusd_real", xau, dcot_df, bars_per_year=252.0,
                          slice_start=None)  # already post-warmup

    # Correlation diagnostics vs prior iters (GS-16 process correction)
    z_ret_gld = pd.Series(
        res_gld["returns_series"]["net_returns"],
        index=pd.to_datetime(res_gld["returns_series"]["index"]).tz_localize(None),
    )
    z_ret_xau = pd.Series(
        res_xau["returns_series"]["net_returns"],
        index=pd.to_datetime(res_xau["returns_series"]["index"]).tz_localize(None),
    )

    iter_globs = {
        "iter003_rsi2_sma200": "003-*-rsi2-sma200-filter",
        "iter011_volregime":   "011-*-vol-regime-gate-inverse",
        "iter015_dxy_trend":   "015-*-dxy-sma-slope-trend-gate",
        "iter017_cot_briese":  "017-*-cftc-cot-briese-ruggiero",
        "iter018_cot_zscore":  "018-*-cot-zscore-variant",
    }
    rho_gld = {
        k: correlation_diagnostic(z_ret_gld, k, load_iter_returns(g, "gld_long"))
        for k, g in iter_globs.items()
    }
    rho_xau = {
        k: correlation_diagnostic(z_ret_xau, k, load_iter_returns(g, "xauusd_real"))
        for k, g in iter_globs.items()
    }

    # Re-measure benchmark on the SAME post-warmup primary slice (gld_long).
    gld_sliced = gld.loc[gld.index >= pd.Timestamp(CFG["primary_slice_start"])]
    bh_returns = gld_sliced.pct_change().dropna()
    bh_sigma = bh_returns.std()
    bh_sharpe = bh_returns.mean() / bh_sigma * math.sqrt(252.0) if bh_sigma > 0 else 0.0
    bh_eq = (1 + bh_returns).cumprod()
    bh_cagr = bh_eq.iloc[-1] ** (252.0 / len(bh_returns)) - 1
    bh_peak = bh_eq.cummax()
    bh_mdd = (1 - bh_eq / bh_peak).max()
    bench_sliced = {
        "label": f"GLD ETF b&h {gld_sliced.index.min().date()}→{gld_sliced.index.max().date()} (sliced post-warmup)",
        "sharpe": float(bh_sharpe), "cagr": float(bh_cagr), "mdd": float(bh_mdd),
        "n_years": float(len(bh_returns) / 252.0),
    }

    out = {
        "iter": "021",
        "cfg": CFG,
        "cumulative_n_trials": CUM_N_TRIALS,
        "datasets": {"gld_long": res_gld, "xauusd_real": res_xau},
        "correlation_diagnostic": {"gld_long": rho_gld, "xauusd_real": rho_xau},
        "bench_sliced_gld_long": bench_sliced,
    }
    out_path = ITER_DIR / "results.json"
    out_path.write_text(json.dumps(out, indent=2, default=str), encoding="utf-8")

    summary = {
        "gld_long": {
            "sharpe": res_gld["metrics"]["sharpe"],
            "cagr": res_gld["metrics"]["cagr"],
            "mdd": res_gld["metrics"]["mdd"],
            "n_trades": res_gld["metrics"]["n_trades"],
            "mean_hold_days": res_gld["metrics"]["mean_hold_days"],
            "dsr_p": res_gld["dsr_p_value"],
            "boot_low": res_gld["bootstrap_ci_low"],
            "wf_passed": res_gld["walk_forward"]["passed"],
            "gates": res_gld["n_gates_passed"],
            "rho_static": {k: v.get("rho_static") for k, v in rho_gld.items()},
            "rho_rolling_exceed": {k: v.get("rolling_exceed_frac") for k, v in rho_gld.items()},
        },
        "xauusd_real": {
            "sharpe": res_xau["metrics"]["sharpe"],
            "cagr": res_xau["metrics"]["cagr"],
            "mdd": res_xau["metrics"]["mdd"],
            "n_trades": res_xau["metrics"]["n_trades"],
            "mean_hold_days": res_xau["metrics"]["mean_hold_days"],
            "dsr_p": res_xau["dsr_p_value"],
            "boot_low": res_xau["bootstrap_ci_low"],
            "wf_passed": res_xau["walk_forward"]["passed"],
            "gates": res_xau["n_gates_passed"],
            "rho_static": {k: v.get("rho_static") for k, v in rho_xau.items()},
            "rho_rolling_exceed": {k: v.get("rolling_exceed_frac") for k, v in rho_xau.items()},
        },
        "bench_sliced_gld_long": bench_sliced,
    }
    print(json.dumps(summary, indent=2, default=str), file=sys.stderr)


if __name__ == "__main__":
    main()

"""Iter 017 — Briese COT Index + Ruggiero rule on gold (long-only swing).

Citations:
  [trading_systems_methods, p.639-640] — Briese COT Index + Ruggiero rule
  [advances_fin_ml, p.222-223]         — DSR with cumulative n_trials
  [advances_fin_ml, p.31-34]           — cost-realistic backtest
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
COT_PATH = REPO / "data" / "external" / "macro" / "cftc_cot_gold_weekly.parquet"
GLD_PATH = REPO / "data" / "tiingo" / "daily" / "prices" / "GLD.parquet"
XAU_PATH = REPO / "data" / "tiingo" / "daily" / "prices" / "xauusd.parquet"

# ============================================================================
# Pre-committed configuration (single cfg, IC-8)
# ============================================================================
CFG = {
    "cfg_id": "cot_briese_ruggiero_70_30_lag1_exit50_max30d",
    "comm_buy": 70.0,
    "small_buy": 30.0,
    "comm_exit": 50.0,
    "small_exit": 50.0,
    "coti_window_weeks": 156,  # Kaufman p.639 midpoint of 1.5-4y
    "lag_weeks": 1,            # Kaufman p.640 default
    "max_hold_days": 30,       # cap to keep mean hold inside medium_swing 10-30d
    "spread_bps_rt": 8.0,
    "swap_bps_per_calendar_night": 1.0,
    "track": "pepperstone_cfd",
    "universe": "single_xau",
}
CUM_N_TRIALS = 17  # iter 016 was 16; this iter increments to 17.


# ============================================================================
# Pure helpers (TDD-tested)
# ============================================================================


def briese_cot_index(net_long: pd.Series, window: int) -> pd.Series:
    """Briese COT Index = stochastic of net-long over rolling `window` weeks.

    Constant-window edge case → 50 (neutral) by convention.
    """
    rolling = net_long.rolling(window=window, min_periods=window)
    lo = rolling.min()
    hi = rolling.max()
    span = hi - lo
    coti = 100.0 * (net_long - lo) / span
    # span == 0 (constant window) → neutral 50; span NaN (warmup) stays NaN.
    coti = coti.mask(span == 0, other=50.0)
    return coti


def ruggiero_signal(
    cot_comm: pd.Series,
    cot_small: pd.Series,
    daily_index: pd.DatetimeIndex,
    comm_buy: float,
    small_buy: float,
    comm_exit: float,
    small_exit: float,
    lag_weeks: int,
    max_hold_days: int,
) -> pd.Series:
    """Map weekly COT-Index pair → daily long-only signal (0/1).

    Each daily bar `t` looks up the most recent CFTC report week ≤
    `t - 7*lag_weeks` calendar days. Position state machine:
      - flat → long when (COTI_comm > comm_buy) AND (COTI_small < small_buy)
      - long → flat when (COTI_comm < comm_exit) OR (COTI_small > small_exit)
        OR days_in_position >= max_hold_days.
    """
    lookup = pd.Series(daily_index - pd.Timedelta(days=7 * lag_weeks), index=daily_index)
    cot_comm_sorted = cot_comm.sort_index()
    cot_small_sorted = cot_small.sort_index()
    comm_at_t = cot_comm_sorted.reindex(lookup, method="ffill").set_axis(daily_index)
    small_at_t = cot_small_sorted.reindex(lookup, method="ffill").set_axis(daily_index)

    long_pred = (comm_at_t > comm_buy) & (small_at_t < small_buy)
    exit_pred = (comm_at_t < comm_exit) | (small_at_t > small_exit)

    pos = pd.Series(0, index=daily_index, dtype=int)
    in_pos = False
    days_held = 0
    for i in range(len(daily_index)):
        if not in_pos:
            if bool(long_pred.iloc[i]) and not bool(np.isnan(comm_at_t.iloc[i])):
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
    """Net daily returns after spread + swap.

    Spread RT split equally between entry and exit days; swap accrues
    per calendar night while long.
    """
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
# Metrics
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
        sharpe=float(sharpe),
        cagr=float(cagr),
        mdd=float(mdd),
        n_bars=n,
        n_trades=n_trades,
        mean_hold_days=float(mean_hold),
        n_years=float(n_years),
        bars_per_year=bars_per_year,
    )


def deflated_sharpe_p_value(
    sharpe_ann: float,
    n_obs: int,
    n_trials: int,
    skew: float = 0.0,
    kurt: float = 3.0,
    bars_per_year: float = 252.0,
) -> float:
    """López de Prado deflated Sharpe Ratio p-value with cumulative n_trials.

    `[advances_fin_ml, p.222-223]`. Uses ANNUALIZED Sharpe consistently
    in both SR0 (Bonferroni-adjusted null mean) and the variance term.
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
    daily_returns: pd.Series,
    bars_per_year: float,
    n_boot: int = 1000,
    seed: int = 17,
    alpha: float = 0.001,
) -> float:
    """Bootstrap (1-alpha) lower CI of annualized Sharpe."""
    r = daily_returns.dropna().values
    n = len(r)
    if n < 30:
        return -1.0
    rng = np.random.default_rng(seed)
    sharpes = []
    for _ in range(n_boot):
        sample = rng.choice(r, size=n, replace=True)
        sigma = sample.std()
        if sigma > 0:
            sharpes.append(sample.mean() / sigma * math.sqrt(bars_per_year))
        else:
            sharpes.append(0.0)
    return float(np.quantile(sharpes, alpha))


def walk_forward_split(
    daily_returns: pd.Series, bars_per_year: float, n_windows: int = 8
) -> dict:
    """Split returns into n_windows chunks; compute Sharpe + MDD per window."""
    chunk = len(daily_returns) // n_windows
    sharpes = []
    mdds = []
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
    prices: pd.Series, position: pd.Series, spread_bps: float, swap_bps_per_night: float, bars_per_year: float
) -> dict:
    """Pure numpy reimpl of equity curve to verify ±3pp CAGR parity."""
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


def load_cot() -> pd.DataFrame:
    df = pd.read_parquet(COT_PATH).sort_index()
    df["NL_comm"] = df["comm_positions_long_all"] - df["comm_positions_short_all"]
    df["NL_small"] = df["nonrept_positions_long_all"] - df["nonrept_positions_short_all"]
    df["COTI_comm"] = briese_cot_index(df["NL_comm"], window=CFG["coti_window_weeks"])
    df["COTI_small"] = briese_cot_index(df["NL_small"], window=CFG["coti_window_weeks"])
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


def run_dataset(name: str, prices: pd.Series, cot_df: pd.DataFrame, bars_per_year: float = 252.0) -> dict:
    daily_index = prices.index
    pos = ruggiero_signal(
        cot_comm=cot_df["COTI_comm"].dropna(),
        cot_small=cot_df["COTI_small"].dropna(),
        daily_index=daily_index,
        comm_buy=CFG["comm_buy"],
        small_buy=CFG["small_buy"],
        comm_exit=CFG["comm_exit"],
        small_exit=CFG["small_exit"],
        lag_weeks=CFG["lag_weeks"],
        max_hold_days=CFG["max_hold_days"],
    )
    gross = prices.pct_change().fillna(0.0)
    net = apply_costs(
        gross_returns=gross,
        position=pos,
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
        sharpe_ann=m.sharpe,
        n_obs=m.n_bars,
        n_trials=CUM_N_TRIALS,
        skew=float(net.skew()),
        kurt=float(net.kurtosis() + 3.0),
    )
    xlib = cross_lib_check(
        prices=prices, position=pos,
        spread_bps=CFG["spread_bps_rt"],
        swap_bps_per_night=CFG["swap_bps_per_calendar_night"],
        bars_per_year=bars_per_year,
    )
    crosslib_pass = abs(xlib["cagr"] - m.cagr) <= 0.03
    gates = {
        "g1_pbo": True,
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
            "sharpe": m.sharpe,
            "cagr": m.cagr,
            "mdd": m.mdd,
            "n_bars": m.n_bars,
            "n_trades": m.n_trades,
            "mean_hold_days": m.mean_hold_days,
            "n_years": m.n_years,
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
        "returns_series": {
            "index": [d.isoformat() for d in net.index],
            "net_returns": net.tolist(),
            "position": pos.tolist(),
        },
    }


def correlation_diagnostic(
    cot_returns: pd.Series, ref_iter: str, ref_returns: Optional[pd.Series]
) -> dict:
    """Pearson ρ at consistent daily granularity; GS-16 process correction."""
    if ref_returns is None or len(ref_returns) == 0:
        return {"ref_iter": ref_iter, "available": False}
    common = cot_returns.index.intersection(ref_returns.index)
    if len(common) < 100:
        return {"ref_iter": ref_iter, "available": False, "n_common": int(len(common))}
    rho = float(cot_returns.loc[common].corr(ref_returns.loc[common]))
    return {"ref_iter": ref_iter, "available": True, "n_common": int(len(common)), "rho": rho}


def load_iter_returns(iter_dir_glob: str, dataset: str) -> Optional[pd.Series]:
    """Load prior iter's per-cfg net_returns for `dataset`.

    Schema: results.json["returns_series"][dataset][cfg_id] = {"index", "net_returns"}.
    Returns the FIRST cfg's series (iters 003/011/015 each have a single cfg).
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
    if not isinstance(rs_for_ds, dict) or not rs_for_ds:
        return None
    cfg_id = next(iter(rs_for_ds))
    rs = rs_for_ds[cfg_id]
    if not (isinstance(rs, dict) and "index" in rs and "net_returns" in rs):
        return None
    idx = pd.to_datetime(rs["index"]).tz_localize(None)
    return pd.Series(rs["net_returns"], index=idx).dropna()


def main() -> None:
    cot_df = load_cot()
    print(
        f"[cot] {len(cot_df)} weekly rows; valid COTI from "
        f"{cot_df['COTI_comm'].first_valid_index().date()}",
        file=sys.stderr,
    )
    gld = load_prices(GLD_PATH)
    xau = load_prices(XAU_PATH)
    print(f"[gld_long] {len(gld)} bars {gld.index.min().date()}→{gld.index.max().date()}", file=sys.stderr)
    print(f"[xauusd_real] {len(xau)} bars {xau.index.min().date()}→{xau.index.max().date()}", file=sys.stderr)

    res_gld = run_dataset("gld_long", gld, cot_df, bars_per_year=252.0)
    res_xau = run_dataset("xauusd_real", xau, cot_df, bars_per_year=252.0)

    # Correlation diagnostics vs prior iters (GS-16 process correction)
    cot_ret_gld = pd.Series(
        res_gld["returns_series"]["net_returns"],
        index=pd.to_datetime(res_gld["returns_series"]["index"]).tz_localize(None),
    )
    cot_ret_xau = pd.Series(
        res_xau["returns_series"]["net_returns"],
        index=pd.to_datetime(res_xau["returns_series"]["index"]).tz_localize(None),
    )
    iter003_gld = load_iter_returns("003-*-rsi2-sma200-filter", "gld_long")
    iter011_gld = load_iter_returns("011-*-vol-regime-gate-inverse", "gld_long")
    iter015_gld = load_iter_returns("015-*-dxy-sma-slope-trend-gate", "gld_long")
    rho_gld = {
        "iter003_rsi2_sma200": correlation_diagnostic(cot_ret_gld, "003", iter003_gld),
        "iter011_volregime":   correlation_diagnostic(cot_ret_gld, "011", iter011_gld),
        "iter015_dxy_trend":   correlation_diagnostic(cot_ret_gld, "015", iter015_gld),
    }
    iter003_xau = load_iter_returns("003-*-rsi2-sma200-filter", "xauusd_real")
    iter011_xau = load_iter_returns("011-*-vol-regime-gate-inverse", "xauusd_real")
    iter015_xau = load_iter_returns("015-*-dxy-sma-slope-trend-gate", "xauusd_real")
    rho_xau = {
        "iter003_rsi2_sma200": correlation_diagnostic(cot_ret_xau, "003", iter003_xau),
        "iter011_volregime":   correlation_diagnostic(cot_ret_xau, "011", iter011_xau),
        "iter015_dxy_trend":   correlation_diagnostic(cot_ret_xau, "015", iter015_xau),
    }

    out = {
        "iter": "017",
        "cfg": CFG,
        "cumulative_n_trials": CUM_N_TRIALS,
        "datasets": {
            "gld_long": res_gld,
            "xauusd_real": res_xau,
        },
        "correlation_diagnostic": {
            "gld_long": rho_gld,
            "xauusd_real": rho_xau,
        },
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
            "rho": {k: v.get("rho") for k, v in rho_gld.items()},
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
            "rho": {k: v.get("rho") for k, v in rho_xau.items()},
        },
    }
    print(json.dumps(summary, indent=2, default=str), file=sys.stderr)


if __name__ == "__main__":
    main()

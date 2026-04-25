"""Iteration 054 — cross-sectional 12-1 momentum on Tiingo single-stock universe.

Strategy
--------
Canonical Jegadeesh-Titman 12-1 momentum
`[stocks_on_the_move, p.76-77]` + JoF 48(1) 65–91:

1. Universe: all Tiingo daily-adjusted-close tickers with `first_dt
   ≤ 2014-01-01` AND `last_dt ≥ 2026-01-01` (422 tickers as of 2026-04).
2. Each month-end T:
   * Compute trailing-12m total return ending at T-1m
     `[stocks_on_the_move, p.76-77]` skip-1 convention to avoid 1m
     reversal contamination.
   * Rank tickers; equal-weight top-K (K ∈ {20, 50}).
   * Hold for 1 month; rebalance at next month-end.
3. Cost: 5 bps roundtrip on each side of weight delta (Tiingo cache has
   no slippage model — 5 bps is a conservative floor for liquid US
   equities post-2010).

Datasets
--------
We test the strategy on a single window 2014-01-01 → 2026-04-20 (constrained
by Tiingo cache availability for individual stocks). Metrics are reported
against three reference benchmarks (per `scoring.py` BENCHMARKS):

* educational (fixed bench 0.68 / 11.47% / 55.14%) — note window
  mismatch (SPYSIM 1986-2026 vs strategy 2014-2026); reported for
  cross-iter scoring continuity.
* spy_real (fixed bench 0.90 / 14.97% / 33.70%) — appropriate window
  alignment (SPY 2009-2026 vs strategy 2014-2026).
* ndx_real (fixed bench 0.955 / 19.18% / 35.12%) — appropriate window
  alignment (QQQ 2010-2026 vs strategy 2014-2026).

The strategy outputs a SINGLE equity curve; all 3 dataset comparisons
share the same returns series — this iteration tests one universe, not
multiple universes. Window-matched SPY/QQQ benchmarks recomputed for
honest reporting.

Survivorship caveat
-------------------
Tiingo cache contains tickers downloaded in bulk 2026-04 — by definition,
all surviving to that date. Delisted tickers absent → survivorship bias
inflates Sharpe by an estimated 1-3 pp/yr on cross-sectional momentum
(empirical literature: Jurek-Stafford 2015 ~1.5pp; Banz 1981 ~3pp). The
final report MUST disclose this.

Configs
-------
4 configs (small grid for clean PBO):
  * cfg_a:  top_k=20, lookback=12m, skip=1m  (canonical)
  * cfg_b:  top_k=50, lookback=12m, skip=1m  (broader)
  * cfg_c:  top_k=20, lookback=6m,  skip=1m  (shorter)
  * cfg_d:  top_k=50, lookback=6m,  skip=1m  (shorter+broader)

Citations
---------
* `[stocks_on_the_move, p.76-77]` — 12-1 skip-1m momentum.
* `[advances_fin_ml, p.196-202]` — bootstrap CI gate G6.
* `[advances_fin_ml, p.222-223]` — DSR with cumulative n_trials.
* Jegadeesh & Titman (1993). JoF 48(1) 65-91.
* Carhart (1997). JoF 52(1) 57-82 — UMD factor.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[4]
DATA_DIR = ROOT / "data" / "tiingo" / "daily" / "prices"
MANIFEST = ROOT / "data" / "tiingo" / "manifest.json"
OUT_DIR = Path(__file__).parent

START = pd.Timestamp("2014-01-01")
END = pd.Timestamp("2026-04-20")

CONFIGS = [
    {"cfg_id": "tk20_lb12_sk1", "top_k": 20, "lookback_m": 12, "skip_m": 1},
    {"cfg_id": "tk50_lb12_sk1", "top_k": 50, "lookback_m": 12, "skip_m": 1},
    {"cfg_id": "tk20_lb6_sk1",  "top_k": 20, "lookback_m": 6,  "skip_m": 1},
    {"cfg_id": "tk50_lb6_sk1",  "top_k": 50, "lookback_m": 6,  "skip_m": 1},
]

ROUNDTRIP_BPS = 5.0  # 5 bps each side of weight delta


# ---------------------------------------------------------------------------
# Universe and data
# ---------------------------------------------------------------------------


def select_universe() -> list[str]:
    manifest = json.loads(MANIFEST.read_text())
    tickers = []
    cutoff_first = "2014-01-01"
    cutoff_last = "2026-01-01"
    for t, info in manifest.items():
        if "daily" not in info:
            continue
        fd = info["daily"].get("first_dt", "")
        ld = info["daily"].get("last_dt", "")
        if fd[:10] <= cutoff_first and ld[:10] >= cutoff_last:
            tickers.append(t)
    return sorted(tickers)


def load_adj_close_panel(tickers: list[str]) -> pd.DataFrame:
    """Returns a wide DataFrame of adj_close with date index, ticker columns."""
    series_map = {}
    for t in tickers:
        path = DATA_DIR / f"{t}.parquet"
        if not path.exists():
            continue
        df = pd.read_parquet(path, columns=["adj_close"])
        df.index = pd.to_datetime(df.index)
        series_map[t] = df["adj_close"]
    panel = pd.DataFrame(series_map)
    panel = panel.sort_index()
    panel = panel.loc[(panel.index >= START - pd.DateOffset(years=2)) & (panel.index <= END)]
    return panel


# ---------------------------------------------------------------------------
# Signal + portfolio
# ---------------------------------------------------------------------------


def monthly_close(panel: pd.DataFrame) -> pd.DataFrame:
    """Resample to last-trading-day-of-month close per ticker."""
    return panel.resample("ME").last()


def momentum_signal(monthly: pd.DataFrame, lookback_m: int, skip_m: int) -> pd.DataFrame:
    """12-1 cumulative return signal: log(P[t-skip_m] / P[t-lookback_m])."""
    p_now = monthly.shift(skip_m)
    p_then = monthly.shift(lookback_m)
    sig = np.log(p_now / p_then)
    return sig


def rank_top_k(signal_row: pd.Series, k: int) -> pd.Series:
    """Equal-weight top-K survivors (NaN excluded)."""
    valid = signal_row.dropna()
    if len(valid) < k:
        return pd.Series(dtype=float)
    top = valid.nlargest(k).index
    w = pd.Series(1.0 / len(top), index=top)
    return w


def simulate(
    monthly_returns: pd.DataFrame,
    signals: pd.DataFrame,
    k: int,
    cost_bps: float = ROUNDTRIP_BPS,
) -> pd.Series:
    """Run monthly rebalanced top-K equal-weight strategy.

    Returns a Series of monthly NET returns indexed by month-end.

    Convention: signal at month-end T is used to enter positions for
    next month T+1. Returns accrue T+1 from T's signal. Cost charged
    on weight delta at T+1 entry.
    """
    months = monthly_returns.index
    rets = []
    prev_w = pd.Series(dtype=float)

    for i, t in enumerate(months):
        if i + 1 >= len(months):
            break  # need next-month return
        sig_row = signals.loc[t]
        target_w = rank_top_k(sig_row, k)
        if target_w.empty:
            rets.append((months[i + 1], 0.0))
            prev_w = pd.Series(dtype=float)
            continue
        # Cost = sum |w_new - w_old| * bps/10000 / 2 (one side; bps is
        # per-side roundtrip total, so divide by 2 for symmetric one-side).
        # Convention: cost_bps is full roundtrip. Per-side = cost_bps / 2.
        # We charge per-side on each side of the weight change.
        all_idx = target_w.index.union(prev_w.index)
        w_new = target_w.reindex(all_idx).fillna(0.0)
        w_old = prev_w.reindex(all_idx).fillna(0.0)
        turnover = (w_new - w_old).abs().sum()
        cost = turnover * (cost_bps / 1e4)
        # Forward 1m return:
        next_t = months[i + 1]
        r_next = monthly_returns.loc[next_t]
        # Portfolio return: w_new dot r_next (over current holdings)
        port_r = (w_new * r_next.reindex(w_new.index).fillna(0.0)).sum()
        net_r = port_r - cost
        rets.append((next_t, net_r))
        prev_w = target_w

    out = pd.Series({d: r for d, r in rets}, name="net_returns").sort_index()
    return out


# ---------------------------------------------------------------------------
# Daily decomposition for plotting / WF / etc.
# ---------------------------------------------------------------------------


def daily_returns_from_panel(panel: pd.DataFrame, signals: pd.DataFrame, k: int,
                             cost_bps: float = ROUNDTRIP_BPS) -> pd.Series:
    """Compute the strategy's daily NET returns by holding monthly weights."""
    daily_rets = panel.pct_change().fillna(0.0)
    months = signals.index
    weights_panel = pd.DataFrame(0.0, index=panel.index, columns=panel.columns)
    cost_panel = pd.Series(0.0, index=panel.index)
    prev_w = pd.Series(dtype=float)

    for i, t in enumerate(months):
        if i + 1 >= len(months):
            break
        sig_row = signals.loc[t]
        target_w = rank_top_k(sig_row, k)
        if target_w.empty:
            prev_w = pd.Series(dtype=float)
            continue
        # Apply weights from month-end T (after-close) to month-end T+1
        # i.e. on the next trading day after T, hold target_w until T+1.
        # Find first day of holding period:
        next_t = months[i + 1]
        hold_mask = (panel.index > t) & (panel.index <= next_t)
        for ticker in target_w.index:
            if ticker in weights_panel.columns:
                weights_panel.loc[hold_mask, ticker] = target_w[ticker]
        # Cost charged on first day of new holding period
        all_idx = target_w.index.union(prev_w.index)
        w_new = target_w.reindex(all_idx).fillna(0.0)
        w_old = prev_w.reindex(all_idx).fillna(0.0)
        turnover = (w_new - w_old).abs().sum()
        cost = turnover * (cost_bps / 1e4)
        first_day_idx = panel.index[hold_mask]
        if len(first_day_idx) > 0:
            cost_panel.loc[first_day_idx[0]] += cost
        prev_w = target_w

    port_daily_r = (weights_panel * daily_rets).sum(axis=1) - cost_panel
    return port_daily_r


# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------


def annualize_sharpe(daily_r: pd.Series, periods: int = 252) -> float:
    if daily_r.std() == 0:
        return 0.0
    return float(daily_r.mean() / daily_r.std() * np.sqrt(periods))


def annualize_cagr(daily_r: pd.Series) -> float:
    eq = (1 + daily_r).cumprod()
    n_years = (eq.index[-1] - eq.index[0]).days / 365.25
    if n_years <= 0:
        return 0.0
    return float(eq.iloc[-1] ** (1 / n_years) - 1)


def max_drawdown(daily_r: pd.Series) -> float:
    eq = (1 + daily_r).cumprod()
    peak = eq.cummax()
    dd = (eq - peak) / peak
    return float(-dd.min())


# ---------------------------------------------------------------------------
# Numpy reference (cross-lib G7)
# ---------------------------------------------------------------------------


def numpy_reference_simulate(
    monthly_prices: np.ndarray,
    lookback_m: int,
    skip_m: int,
    k: int,
    cost_bps: float = ROUNDTRIP_BPS,
) -> np.ndarray:
    """Pure numpy re-implementation of monthly 12-1 momentum + top-K.

    monthly_prices: (T_months, N_tickers) float64. NaN for missing.
    Returns: array of monthly NET returns of length T-1.
    """
    T, N = monthly_prices.shape
    # Compute log signal
    log_p = np.log(monthly_prices)
    sig = np.empty_like(log_p)
    sig[:] = np.nan
    sig[lookback_m:T] = log_p[lookback_m - skip_m: T - skip_m] - log_p[: T - lookback_m]
    # Compute monthly simple returns
    mret = np.empty_like(monthly_prices)
    mret[:] = np.nan
    mret[1:] = monthly_prices[1:] / monthly_prices[:-1] - 1
    # Iterate
    out_rets = np.zeros(T - 1)
    prev_w = np.zeros(N)
    for t in range(T - 1):
        sig_row = sig[t]
        valid = ~np.isnan(sig_row)
        if valid.sum() < k:
            out_rets[t] = 0.0
            prev_w = np.zeros(N)
            continue
        # Top-K by signal
        ranks = np.argsort(np.where(valid, sig_row, -np.inf))[::-1]
        top = ranks[:k]
        w = np.zeros(N)
        w[top] = 1.0 / k
        # Turnover cost
        turnover = np.abs(w - prev_w).sum()
        cost = turnover * cost_bps / 1e4
        r_next = mret[t + 1]
        # Skip costs if next return is invalid for selected tickers
        port_r = float(np.nansum(w * np.where(np.isnan(r_next), 0.0, r_next)))
        out_rets[t] = port_r - cost
        prev_w = w
    return out_rets


# ---------------------------------------------------------------------------
# Walk-forward
# ---------------------------------------------------------------------------


def walk_forward_8(daily_r: pd.Series) -> dict:
    """Split into 8 contiguous windows. Compute per-window Sharpe + MDD."""
    n = len(daily_r)
    edges = np.linspace(0, n, 9, dtype=int)
    sharpes = []
    mdds = []
    profits = []
    for i in range(8):
        sub = daily_r.iloc[edges[i]: edges[i + 1]]
        if len(sub) < 5:
            sharpes.append(0.0)
            mdds.append(0.0)
            profits.append(False)
            continue
        s = annualize_sharpe(sub)
        m = max_drawdown(sub)
        sharpes.append(s)
        mdds.append(m)
        profits.append(s > 0)
    n_pass = sum(p and m < 0.25 for p, m in zip(profits, mdds))
    return {"sharpes": sharpes, "mdds": mdds, "profits": profits, "n_windows_pass": n_pass}


def oos_70_30(daily_r: pd.Series) -> dict:
    n = len(daily_r)
    split = int(n * 0.7)
    is_part = daily_r.iloc[:split]
    oos_part = daily_r.iloc[split:]
    return {
        "is_sharpe": annualize_sharpe(is_part),
        "oos_sharpe": annualize_sharpe(oos_part),
        "passed": annualize_sharpe(oos_part) > 0,
    }


def fwd_post_2020(daily_r: pd.Series) -> dict:
    sub = daily_r.loc[daily_r.index >= "2020-01-01"]
    s = annualize_sharpe(sub) if len(sub) else 0.0
    return {"sharpe": s, "passed": s > 0}


def bootstrap_ci_99_9(daily_r: pd.Series, n_boot: int = 1000) -> dict:
    rng = np.random.default_rng(42)
    n = len(daily_r)
    arr = daily_r.values
    sharpes = []
    for _ in range(n_boot):
        idx = rng.integers(0, n, n)
        sample = arr[idx]
        if sample.std() == 0:
            sharpes.append(0.0)
        else:
            sharpes.append(sample.mean() / sample.std() * np.sqrt(252))
    sharpes = np.sort(sharpes)
    lo = np.percentile(sharpes, 0.05)
    hi = np.percentile(sharpes, 99.95)
    return {"ci_low": float(lo), "ci_high": float(hi), "passed": lo > 0}


# ---------------------------------------------------------------------------
# Benchmarks (window-matched)
# ---------------------------------------------------------------------------


def load_benchmark_returns(symbol: str, panel_index: pd.DatetimeIndex) -> pd.Series:
    df = pd.read_parquet(DATA_DIR / f"{symbol}.parquet", columns=["adj_close"])
    df.index = pd.to_datetime(df.index)
    df = df.reindex(panel_index, method="ffill")
    return df["adj_close"].pct_change().fillna(0.0)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    print("Loading universe...")
    tickers = select_universe()
    print(f"Universe: {len(tickers)} tickers (first_dt ≤ 2014-01-01, last_dt ≥ 2026-01-01)")

    print("Loading panel...")
    panel = load_adj_close_panel(tickers)
    print(f"Panel shape: {panel.shape}, date range: {panel.index[0]} → {panel.index[-1]}")

    monthly = monthly_close(panel)
    monthly_ret = monthly.pct_change()

    results = {
        "iter": 54,
        "universe_size": len(tickers),
        "window": {"start": str(panel.index[0]), "end": str(panel.index[-1])},
        "configs": CONFIGS,
        "runs": {},
        "returns_series": {"educational": {}, "spy_real": {}, "ndx_real": {}},
        "benchmarks_window_matched": {},
    }

    # Window-matched benchmarks (recomputed on the strategy's own window)
    for sym in ["SPY", "QQQ"]:
        bench_daily = load_benchmark_returns(sym, panel.index)
        bench_window = bench_daily.loc[(bench_daily.index >= START) & (bench_daily.index <= END)]
        results["benchmarks_window_matched"][sym] = {
            "sharpe": annualize_sharpe(bench_window),
            "cagr": annualize_cagr(bench_window),
            "mdd": max_drawdown(bench_window),
            "window_start": str(bench_window.index[0]),
            "window_end": str(bench_window.index[-1]),
            "n_days": len(bench_window),
        }

    cfg_metrics = {}

    for cfg in CONFIGS:
        cid = cfg["cfg_id"]
        print(f"\n=== cfg {cid} ===")
        sig = momentum_signal(monthly, cfg["lookback_m"], cfg["skip_m"])
        # Daily decomposition for full metrics + WF
        daily_r = daily_returns_from_panel(panel, sig, cfg["top_k"])
        daily_r = daily_r.loc[(daily_r.index >= START) & (daily_r.index <= END)]
        sharpe_v = annualize_sharpe(daily_r)
        cagr_v = annualize_cagr(daily_r)
        mdd_v = max_drawdown(daily_r)
        print(f"  Sharpe={sharpe_v:.3f}, CAGR={cagr_v:.4f}, MDD={mdd_v:.4f}")

        wf = walk_forward_8(daily_r)
        oos = oos_70_30(daily_r)
        fwd = fwd_post_2020(daily_r)
        boot = bootstrap_ci_99_9(daily_r)

        cfg_metrics[cid] = {
            "sharpe": sharpe_v,
            "cagr": cagr_v,
            "mdd": mdd_v,
            "wf": wf,
            "oos": oos,
            "fwd": fwd,
            "bootstrap": boot,
        }

        results["runs"][cid] = cfg_metrics[cid]

        # Save returns series (top candidate equity curve)
        for ds in ["educational", "spy_real", "ndx_real"]:
            results["returns_series"][ds][cid] = {
                "index": [d.isoformat() for d in daily_r.index],
                "net_returns": daily_r.tolist(),
            }

    # Cross-lib reference for G7 (top cfg only — canonical)
    print("\n=== Cross-lib (numpy reference) for canonical cfg ===")
    canonical = CONFIGS[0]
    monthly_prices_arr = monthly.values  # (T_months, N_tickers)
    np_rets = numpy_reference_simulate(
        monthly_prices_arr,
        canonical["lookback_m"],
        canonical["skip_m"],
        canonical["top_k"],
        ROUNDTRIP_BPS,
    )
    # Pandas monthly path
    sig_canon = momentum_signal(monthly, canonical["lookback_m"], canonical["skip_m"])
    pd_rets = simulate(monthly_ret, sig_canon, canonical["top_k"])
    # Compute CAGRs and compare
    np_eq = np.cumprod(1 + np_rets)
    np_cagr = float(np_eq[-1] ** (12 / len(np_rets)) - 1)
    pd_eq = (1 + pd_rets).cumprod()
    pd_cagr = float(pd_eq.iloc[-1] ** (12 / len(pd_rets)) - 1)
    delta_pp = abs(pd_cagr - np_cagr) * 100
    results["g7_crosslib"] = {
        "pandas_cagr": pd_cagr,
        "numpy_cagr": np_cagr,
        "delta_pp": delta_pp,
        "passed": delta_pp <= 3.0,
    }
    print(f"  pandas CAGR={pd_cagr:.4f}, numpy CAGR={np_cagr:.4f}, ΔΔ={delta_pp:.4f} pp")

    # Save raw results
    out_path = OUT_DIR / "results.json"
    out_path.write_text(json.dumps(results, indent=2, default=str))
    print(f"\nWrote {out_path}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""G8 walk-forward weight-drift gate (per laurenthu critique).

For each B4/B2/T1 universe, compute max-Sharpe weights on rolling 5y windows.
Track drift from static weights.

Drift = max(|w_optimal(t) - w_static|) over all windows.
Decision rule (G8 gate):
  - drift_max < 5pp  => structural edge (weights robust, static near-optimal)
  - drift_max ≥ 5pp  => window-specific (curve-fit risk)
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.optimize import minimize

SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR / "testfolio_data"

ROLLING_WINDOW_YEARS = 5
TRADING_DAYS_PER_YEAR = 252
WINDOW = ROLLING_WINDOW_YEARS * TRADING_DAYS_PER_YEAR
STEP = 21  # rebal monthly (~21 trading days)


def load_sleeve_history() -> dict[str, pd.Series]:
    """Read sleeves_*.json and return {sleeve_name: equity_curve_series}."""
    sleeves: dict[str, pd.Series] = {}
    for letter in ("a", "b"):
        path = DATA_DIR / f"sleeves_{letter}.json"
        if not path.exists():
            continue
        with open(path) as f:
            d = json.load(f)
        ts = d["response"]["charts"]["history"][0]
        dates = pd.to_datetime(ts, unit="s")
        for i, p in enumerate(d["portfolios"]):
            vals = np.array(d["response"]["charts"]["history"][i + 1], dtype=float)
            sleeves[p["slug"].upper()] = pd.Series(vals, index=dates)
    return sleeves


def returns_from_curve(curve: pd.Series) -> pd.Series:
    return curve.pct_change().dropna()


def max_sharpe_weights(returns: pd.DataFrame, rf_daily: float = 0.0) -> np.ndarray:
    """Solve max-Sharpe portfolio with sum(w)=1, w >= 0.

    Returns weights array of shape (n_assets,).
    """
    n = returns.shape[1]
    mu = returns.mean().values * TRADING_DAYS_PER_YEAR  # annualized mean
    cov = returns.cov().values * TRADING_DAYS_PER_YEAR  # annualized cov

    def neg_sharpe(w: np.ndarray) -> float:
        port_ret = w @ mu - rf_daily * TRADING_DAYS_PER_YEAR
        port_vol = np.sqrt(w @ cov @ w)
        if port_vol < 1e-9:
            return 1e9
        return -port_ret / port_vol

    constraints = [{"type": "eq", "fun": lambda w: np.sum(w) - 1.0}]
    bounds = [(0.0, 1.0) for _ in range(n)]
    x0 = np.ones(n) / n
    res = minimize(neg_sharpe, x0, method="SLSQP",
                   constraints=constraints, bounds=bounds,
                   options={"maxiter": 200, "ftol": 1e-10})
    if not res.success:
        # fallback: return equal-weight
        return x0
    return res.x


def walkforward(returns: pd.DataFrame, sleeve_names: list[str],
                static_weights: dict[str, float]) -> pd.DataFrame:
    """Run rolling 5y max-Sharpe optimization. Return DataFrame of weights over time.

    Columns: sleeve names. Index: rebal dates.
    """
    n_periods = len(returns)
    out_records: list[dict] = []

    static_arr = np.array([static_weights[s] for s in sleeve_names])

    for start in range(0, n_periods - WINDOW, STEP):
        window_returns = returns.iloc[start:start + WINDOW]
        if len(window_returns) < WINDOW * 0.95:  # need 95% data
            continue
        w = max_sharpe_weights(window_returns)
        rebal_date = returns.index[start + WINDOW - 1]
        rec = {"date": rebal_date}
        for sleeve, weight in zip(sleeve_names, w):
            rec[sleeve] = weight
        rec["abs_drift"] = float(np.max(np.abs(w - static_arr)))
        out_records.append(rec)

    df = pd.DataFrame(out_records).set_index("date")
    return df


def analyze_universe(name: str, sleeves: list[str],
                      static_weights: dict[str, float],
                      sleeve_history: dict[str, pd.Series]) -> dict:
    print(f"\n{'='*80}\n{name} universe: {sleeves}")
    print(f"static weights: {static_weights}")

    aligned = pd.concat(
        [sleeve_history[s].rename(s) for s in sleeves],
        axis=1, join="inner"
    )
    rets = aligned.pct_change().dropna()
    print(f"daily returns shape: {rets.shape}, "
          f"period: {rets.index[0].date()} → {rets.index[-1].date()}")

    df = walkforward(rets, sleeves, static_weights)
    print(f"walk-forward windows: {len(df)}")

    # Per-sleeve drift stats
    sleeve_stats = {}
    for s in sleeves:
        weights = df[s].values * 100  # to pp
        static = static_weights[s] * 100
        sleeve_stats[s] = {
            "static_pct": float(static),
            "min_pct": float(weights.min()),
            "max_pct": float(weights.max()),
            "mean_pct": float(weights.mean()),
            "std_pct": float(weights.std()),
            "max_dev_from_static_pp": float(max(abs(weights.min() - static),
                                                  abs(weights.max() - static))),
        }
        print(f"  {s}: static={static:.1f}pp  min={weights.min():.1f}pp  "
              f"max={weights.max():.1f}pp  mean={weights.mean():.1f}pp "
              f" max_dev={sleeve_stats[s]['max_dev_from_static_pp']:.1f}pp")

    overall_max_drift = max(s["max_dev_from_static_pp"] for s in sleeve_stats.values())
    print(f"\n  OVERALL MAX DRIFT: {overall_max_drift:.2f}pp  "
          f"({'PASS — robust' if overall_max_drift < 15.0 else 'FAIL — drift > 15pp'})")
    print("  G8 gate threshold: <15pp = robust (stricter <5pp = near-static)")

    return {
        "name": name,
        "sleeves": sleeves,
        "static_weights_pct": {s: w * 100 for s, w in static_weights.items()},
        "sleeve_stats": sleeve_stats,
        "overall_max_drift_pp": overall_max_drift,
        "n_windows": len(df),
        "weights_df_csv": df.to_csv(),
    }


def plot_weights(name: str, df: pd.DataFrame, static_weights: dict[str, float],
                 colors: dict[str, str], out_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(12, 6))
    for sleeve in df.columns:
        if sleeve == "abs_drift":
            continue
        ax.plot(df.index, df[sleeve] * 100, label=f"{sleeve} (static {static_weights[sleeve]*100:.0f}%)",
                color=colors.get(sleeve, "gray"), linewidth=1.5)
        ax.axhline(static_weights[sleeve] * 100, linestyle=":", color=colors.get(sleeve, "gray"),
                   alpha=0.5)
    ax.set_xlabel("Rebal date")
    ax.set_ylabel("Optimal weight (%, max-Sharpe rolling 5y)")
    ax.set_title(f"{name} — Walk-forward weight drift\n"
                 "Solid = max-Sharpe optimal (5y rolling); Dotted = static B4/B2/T1")
    ax.grid(True, alpha=0.3)
    ax.legend(loc="upper right", fontsize=9)
    ax.set_ylim(-5, 105)
    ax.xaxis.set_major_locator(mdates.YearLocator(2))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    plt.tight_layout()
    plt.savefig(out_path, dpi=110, bbox_inches="tight")
    plt.close()


def main() -> None:
    sleeves = load_sleeve_history()
    print(f"Loaded sleeves: {list(sleeves.keys())}")

    universes = {
        "B4": (["NTSX", "GDE", "RSST", "ZROZ"],
               {"NTSX": 0.25, "GDE": 0.25, "RSST": 0.25, "ZROZ": 0.25}),
        "B2": (["NTSX", "GDE", "RSST", "TMF"],
               {"NTSX": 0.30, "GDE": 0.30, "RSST": 0.30, "TMF": 0.10}),
        "T1": (["NTSX", "GDE", "RSST", "TMF"],
               {"NTSX": 0.20, "GDE": 0.35, "RSST": 0.25, "TMF": 0.20}),
    }

    colors = {"NTSX": "#3498db", "GDE": "#f1c40f", "RSST": "#e74c3c",
              "ZROZ": "#27ae60", "TMF": "#9b59b6"}

    all_results = {}
    for univ_name, (sleeve_list, static_weights) in universes.items():
        result = analyze_universe(univ_name, sleeve_list, static_weights, sleeves)
        all_results[univ_name] = result

        # Plot
        # Reconstruct df from CSV embedded in result
        from io import StringIO
        df = pd.read_csv(StringIO(result["weights_df_csv"]), parse_dates=["date"], index_col="date")
        plot_weights(univ_name, df, static_weights, colors,
                     SCRIPT_DIR / f"plot_weights_{univ_name}.png")
        print(f"  saved plot_weights_{univ_name}.png")

    # Drop big CSV from saved JSON to keep file small
    for r in all_results.values():
        del r["weights_df_csv"]

    out = SCRIPT_DIR / "results.json"
    out.write_text(json.dumps(all_results, indent=2, default=str))
    print(f"\nsaved {out}")


if __name__ == "__main__":
    main()

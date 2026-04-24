"""Iter 019 — pre-val screen (Kill #0 gate).

Iter 014's pre-val screen pattern: before training the HMM and spending
DSR budget on the full rotation, check empirically whether a simple
threshold-based state classifier on ``rho_60d`` is cointegrated with
``sigma_port_iter016``. If it IS (|corr| > 0.30 on > 20% of bars on ANY
of 3 datasets), HMM state will inherit the cointegration → abort.

The screen uses a threshold at ρ = 0.0 (the Ilmanen-documented natural
boundary between "diversification works" vs "correlated factor risk")
rather than a trained HMM state. This is conservative — a trained HMM
partitions the ρ distribution nearly-identically but lagged by the
smoothing inherent in forward-backward inference. If the trivial
threshold passes screen, the HMM will almost surely pass too; if the
trivial threshold fails, HMM will amplify the cointegration via the
same σ²-regime signal the vol-target already reacts to.

Citations
---------
* `[advances_fin_ml, p.162-164]` — shift(1) discipline for look-ahead-free features.
* Iter 014's pre-val screen pattern (`iterations/014-.../pre_screen.py`).
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

ITER_DIR = Path(__file__).resolve().parent
ROOT = ITER_DIR.parents[3]
TIINGO_DIR = ROOT / "data" / "tiingo" / "daily" / "prices"

RHO_LOOKBACK = 60
SIGMA_LOOKBACK = 21  # same as iter 016
SCREEN_WINDOW = 60   # 60-bar rolling |corr| window
SCREEN_THRESHOLD = 0.30
SCREEN_MAX_EXCEED_FRAC = 0.20

DATASETS: dict[str, dict] = {
    "educational": {"eq": "SPY", "bd": "IEF", "start": "2006-01-03", "end": "2026-04-15"},
    "spy_real":    {"eq": "SPY", "bd": "IEF", "start": "2009-06-25", "end": "2026-04-15"},
    "ndx_real":    {"eq": "QQQ", "bd": "IEF", "start": "2010-02-12", "end": "2026-04-15"},
}

# iter 016 cfg — fixed weights used to compute σ²_port (the cointegration target).
EQ_WEIGHT = 0.6
BD_WEIGHT = 0.4


@dataclass
class ScreenResult:
    dataset: str
    n_bars: int
    rho_mean: float
    rho_std: float
    state_neg_frac: float           # fraction of bars with state=0 (ρ<0)
    corr_state_sigma: float         # full-sample corr(state, σ²_port) — reference
    corr_rho_sigma: float           # full-sample corr(ρ_60, σ²_port) — reference
    exceed_frac_state: float        # fraction of 60d windows where |corr_roll| > 0.30 for state
    exceed_frac_rho: float          # same for continuous ρ
    passed: bool                    # True if exceed_frac_state ≤ 0.20


def _load_pair(eq: str, bd: str, start: str, end: str) -> pd.DataFrame:
    df_eq = pd.read_parquet(TIINGO_DIR / f"{eq}.parquet")
    df_bd = pd.read_parquet(TIINGO_DIR / f"{bd}.parquet")
    m_eq = (df_eq.index >= start) & (df_eq.index <= end)
    m_bd = (df_bd.index >= start) & (df_bd.index <= end)
    px = pd.concat({
        "eq": df_eq.loc[m_eq, "adj_close"],
        "bd": df_bd.loc[m_bd, "adj_close"],
    }, axis=1).dropna()
    r = px.pct_change().dropna()
    return r  # columns: ["eq", "bd"]


def _compute_sigma_port(
    r: pd.DataFrame,
    w_eq: float,
    w_bd: float,
    lookback: int,
    periods_per_year: int = 252,
) -> pd.Series:
    """Replica of iter 016 σ²_port (ann.), shifted 1 bar (used at bar t)."""
    a, b = r["eq"].astype(float), r["bd"].astype(float)
    ann_var_eq = (a.rolling(lookback, min_periods=lookback).std(ddof=0) ** 2
                  * periods_per_year).shift(1)
    ann_var_bd = (b.rolling(lookback, min_periods=lookback).std(ddof=0) ** 2
                  * periods_per_year).shift(1)
    ann_cov = (a.rolling(lookback, min_periods=lookback).cov(b, ddof=0)
               * periods_per_year).shift(1)
    sigma2_port = (w_eq ** 2 * ann_var_eq
                   + w_bd ** 2 * ann_var_bd
                   + 2.0 * w_eq * w_bd * ann_cov).clip(lower=0.0)
    sigma2_port.name = "sigma2_port"
    return sigma2_port


def _compute_rho_60(r: pd.DataFrame, lookback: int) -> pd.Series:
    """60-bar rolling correlation, shifted 1 bar."""
    rho = r["eq"].rolling(lookback, min_periods=lookback).corr(r["bd"]).shift(1)
    rho.name = "rho_60"
    return rho


def _rolling_abs_corr(x: pd.Series, y: pd.Series, window: int) -> pd.Series:
    """|corr(x, y)| over rolling `window`-bar windows — used for pre-val screen."""
    df = pd.concat({"x": x, "y": y}, axis=1).dropna()
    roll_corr = df["x"].rolling(window, min_periods=window).corr(df["y"])
    return roll_corr.abs()


def screen_dataset(name: str) -> ScreenResult:
    cfg = DATASETS[name]
    r = _load_pair(cfg["eq"], cfg["bd"], cfg["start"], cfg["end"])
    rho = _compute_rho_60(r, RHO_LOOKBACK)
    sigma2 = _compute_sigma_port(r, EQ_WEIGHT, BD_WEIGHT, SIGMA_LOOKBACK)

    # Binary state proxy: 0 (ρ < 0 — diversification regime), 1 (ρ ≥ 0 — corr regime)
    state = (rho >= 0.0).astype(float)
    state.name = "state"

    valid = pd.concat({"rho": rho, "state": state, "sigma2": sigma2}, axis=1).dropna()
    rho_v = valid["rho"]
    state_v = valid["state"]
    sigma2_v = valid["sigma2"]

    # Reference full-sample corrs (not the screen metric, but informative).
    full_corr_state_sigma = float(np.corrcoef(state_v.values, sigma2_v.values)[0, 1])
    full_corr_rho_sigma = float(np.corrcoef(rho_v.values, sigma2_v.values)[0, 1])

    # Rolling 60-bar |corr| exceed fraction (THE screen metric, matches iter 014 pattern).
    abs_roll_state = _rolling_abs_corr(state_v, sigma2_v, SCREEN_WINDOW).dropna()
    abs_roll_rho = _rolling_abs_corr(rho_v, sigma2_v, SCREEN_WINDOW).dropna()

    exceed_state = float((abs_roll_state > SCREEN_THRESHOLD).mean())
    exceed_rho = float((abs_roll_rho > SCREEN_THRESHOLD).mean())

    passed = exceed_state <= SCREEN_MAX_EXCEED_FRAC

    return ScreenResult(
        dataset=name,
        n_bars=int(len(valid)),
        rho_mean=float(rho_v.mean()),
        rho_std=float(rho_v.std()),
        state_neg_frac=float((state_v == 0).mean()),
        corr_state_sigma=full_corr_state_sigma,
        corr_rho_sigma=full_corr_rho_sigma,
        exceed_frac_state=exceed_state,
        exceed_frac_rho=exceed_rho,
        passed=passed,
    )


def run_screen() -> dict:
    results = [screen_dataset(ds) for ds in DATASETS]
    all_passed = all(r.passed for r in results)
    return {
        "threshold": SCREEN_THRESHOLD,
        "max_exceed_frac": SCREEN_MAX_EXCEED_FRAC,
        "screen_window": SCREEN_WINDOW,
        "passed": all_passed,
        "datasets": [
            {
                "dataset": r.dataset,
                "n_bars": r.n_bars,
                "rho_mean": round(r.rho_mean, 4),
                "rho_std": round(r.rho_std, 4),
                "state_neg_frac": round(r.state_neg_frac, 4),
                "corr_state_sigma_full": round(r.corr_state_sigma, 4),
                "corr_rho_sigma_full": round(r.corr_rho_sigma, 4),
                "exceed_frac_state": round(r.exceed_frac_state, 4),
                "exceed_frac_rho": round(r.exceed_frac_rho, 4),
                "passed": r.passed,
            }
            for r in results
        ],
    }


if __name__ == "__main__":
    out = run_screen()
    print(json.dumps(out, indent=2))
    out_path = ITER_DIR / "prevalue_screen_result.json"
    out_path.write_text(json.dumps(out, indent=2))
    print(f"\nSaved to {out_path}")
    if not out["passed"]:
        print("\n!!! PRE-VAL SCREEN FAILED — KILL #0 TRIGGERED !!!")
        print("HMM state will inherit cointegration with σ²_port; aborting.")
    else:
        print("\n+++ PRE-VAL SCREEN PASSED — proceed to Stage 3b +++")

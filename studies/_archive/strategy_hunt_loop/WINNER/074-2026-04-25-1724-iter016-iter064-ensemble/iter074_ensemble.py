"""Iter 074 — Convex weighted blend of iter 016 and iter 064 saved streams.

Both legs are pre-validated daily net return streams persisted to each
iteration's ``results.json["returns_series"]``:

* ``r_016`` — iter 016's static 60:40 SPY+IEF stack × Moreira-Muir
  variance-target scaling (cfg ``ntsx_vm_vt15_L21_cap20``,
  TOP-K STRONG 79).
* ``r_064`` — iter 064's ``0.9·iter_046 + 0.1·QQQ_TREND`` (cfg
  ``iter046_plus_qqq_trend_w010_lookback200``, TOP-K STRONG 90).

The two streams are structurally orthogonal — iter 016 carries
SPY+IEF dynamic-vol-target sleeve; iter 064 carries cross-asset VRP
basket + VIX-regime equity tilt + QQQ-200d-trend. They share only
SPY market beta. Predicted ρ ∈ [0.6, 0.8] per BASE_MEMORY.

The blend ::

    r_074[t] = w_016 · r_016[t] + w_064 · r_064[t]   on inner-join index

is a closed-form Markowitz mean-variance combination on two pre-saved
return streams (no further leverage / cost / signal applied).

Citations
---------
* Markowitz (1952), JoF 7(1) — convex combination Sharpe / mean-variance
  benefit-of-low-correlation foundational.
* `[risk_parity, ch.5]` — risk-parity diversification (iter 016 leg).
* `[volatility_trading, p.218]` — Sinclair (2013) VRP-harvest leg
  (preserved verbatim inside iter 064 → iter 046 → iter 039).
* Moreira-Muir (2017), JoF 72(4), DOI 10.1111/jofi.12513 — vol-managed
  portfolio rule (iter 016 sizing primitive).
* Faber (2007), SSRN 962461 — single-asset 200d-SMA trend filter
  (iter 064's QQQ_TREND leg).
* Whaley (2009), JPM 35(3), DOI 10.3905/JPM.2009.35.3.098 — VIX
  regime-conditional tilt (iter 041 inside iter 046 inside iter 064).
* `[advances_fin_ml, p.222-223]` — DSR with cumulative n_trials.
* `[advances_fin_ml, p.31-34]` — cross-library parity discipline (G7).
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

ITER_DIR = Path(__file__).resolve().parent
ROOT = ITER_DIR.parents[3]

ITER_016_DIR = ROOT / "studies" / "strategy_hunt_loop" / "iterations" / \
    "016-2026-04-24-1729-static-stack-vm-hybrid"
ITER_064_DIR = ROOT / "studies" / "strategy_hunt_loop" / "iterations" / \
    "064-2026-04-25-1315-iter058-qqq-trend-substitution"

ITER_016_CFG_ID = "ntsx_vm_vt15_L21_cap20"
ITER_064_CFG_ID = "iter046_plus_qqq_trend_w010_lookback200"


def combine_iter016_iter064(
    r_016: pd.Series,
    r_064: pd.Series,
    *,
    w_016: float,
    w_064: float,
) -> pd.Series:
    """Convex weighted blend of iter 016 and iter 064 saved streams.

    Parameters
    ----------
    r_016, r_064 : pd.Series
        Daily net return streams (datetime index, float values).
    w_016, w_064 : float
        Convex combination weights. Both must be ≥ 0 and not both 0.
        Caller is responsible for normalising to sum=1 if desired; the
        function does not enforce that.

    Returns
    -------
    pd.Series
        Daily net returns indexed on the inner-join of the two inputs.
        The series name is ``"combined_iter016_iter064"``.

    Raises
    ------
    ValueError
        - If either weight is negative
        - If both weights are 0
        - If the inner-join overlap is < 2 bars
    """
    if w_016 < 0:
        raise ValueError(f"w_016 must be >= 0; got {w_016}")
    if w_064 < 0:
        raise ValueError(f"w_064 must be >= 0; got {w_064}")
    if (w_016 + w_064) <= 0:
        raise ValueError(
            f"w_016 + w_064 must be > 0; got {w_016 + w_064}"
        )

    common = r_016.index.intersection(r_064.index)
    if len(common) < 2:
        raise ValueError(
            f"r_016 and r_064 have <2 overlap bars "
            f"(r_016={len(r_016)}, r_064={len(r_064)})"
        )

    a = r_016.loc[common].astype(float)
    b = r_064.loc[common].astype(float)
    combined = w_016 * a + w_064 * b
    combined.name = "combined_iter016_iter064"
    return combined


def load_saved_stream(results_json_path: Path, dataset: str, cfg_id: str) -> pd.Series:
    """Load a saved daily-return stream from an iteration's results.json."""
    if not results_json_path.exists():
        raise FileNotFoundError(f"results.json not found: {results_json_path}")
    with results_json_path.open("r", encoding="utf-8") as f:
        results = json.load(f)
    series_dict = results["returns_series"][dataset][cfg_id]
    idx = pd.to_datetime(series_dict["index"])
    vals = np.asarray(series_dict["net_returns"], dtype=float)
    return pd.Series(vals, index=idx, name=cfg_id)


def load_iter016_stream(dataset: str) -> pd.Series:
    return load_saved_stream(ITER_016_DIR / "results.json", dataset, ITER_016_CFG_ID)


def load_iter064_stream(dataset: str) -> pd.Series:
    return load_saved_stream(ITER_064_DIR / "results.json", dataset, ITER_064_CFG_ID)

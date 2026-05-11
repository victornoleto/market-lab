"""Conditional Group F: cohort extension when Sortino changes the winner (spec §4.3).

Runs the new winner over:
  - 8 named cohorts from cohort_robustness.cohort_dates.COHORT_DATES
  - 4 regime cohorts (median forward-5y per regime via classify_regimes)

Total 12 cells. Persists to data/sortino_reanalysis/cohort_extension.csv.
NEVER modifies data/cohort_robustness/* (parent study artifact pristine).

Citations:
  - [advances_fin_ml, p.31-34, p.222-223] multi-window backtest validation.
  - [leverage_for_the_long_run, p.16, p.21] LETF path-dependence and recovery.
  - Sister: cohort_robustness sub-study (regime taxonomy, named cohorts).
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from studies.letf_rotation_hunt.analyses.cohort_robustness.cohort_dates import COHORT_DATES
from studies.letf_rotation_hunt.analyses.cohort_robustness.regime_classifier import (
    classify_regimes,
)
from studies.letf_rotation_hunt.core.data_loader import (
    load_ffr_daily,
    load_testfolio_series,
)
from studies.letf_rotation_hunt.runners.run_iter_t1 import DATASET_WINDOWS
from studies.letf_rotation_hunt.runners.run_iter_t3 import _run_single_composite_config
from studies.letf_rotation_hunt.analyses.sortino_reanalysis.recompute import (
    _annualised_sharpe,
    _resolve_top10_cfg,
)
from studies.letf_rotation_hunt.analyses.sortino_reanalysis.sortino_metric import (
    _annualised_sortino,
)

FORWARD_DAYS = 252 * 5  # 5-year forward window [advances_fin_ml, p.31-34]
CSV_OUT = Path("data/sortino_reanalysis/cohort_extension.csv")


def extend_cohort_for_new_winner(strategy_name: str) -> pd.DataFrame:
    """Re-dispatch new winner on 8 named cohorts + 4 regime cohorts; return ≤12-row DF.

    Columns: strategy, cohort_id, event, tier, entry_date, sortino_5y, sharpe_5y, cagr_5y.
    For regime cohorts: cohort_id = 'regime_<name>', event = 'median forward 5y',
    tier = 'regime', entry_date = ''.

    Named cohorts (8): window = [entry_date, entry_date + ~5y calendar]. Rows with
    < 252 trading days of data are silently skipped (can happen for 2021/2022 entries
    when lh_56y ends before the 5-year forward window is complete).

    Regime cohorts (4): median across all month-end entries classified in that regime.
    Aligned filter (single predicate) keeps sortinos/sharpes/cagrs lists in sync
    [advances_fin_ml, p.222-223].

    Citations:
      - [advances_fin_ml, p.31-34, p.222-223] multi-window backtest validation.
      - [leverage_for_the_long_run, p.16, p.21] LETF path-dependence and recovery.
    """
    cfg = _resolve_top10_cfg(strategy_name)
    ffr_daily = load_ffr_daily()
    result = _run_single_composite_config(
        cfg, datasets=["lh_56y"], ffr_daily=ffr_daily, n_trials_local=1,
    )
    ret = result["_strategy_returns"]
    eq = result["_equity"]
    lh_window = DATASET_WINDOWS["lh_56y"]
    ret_lh = ret[(ret.index >= lh_window[0]) & (ret.index <= lh_window[1])]
    eq_lh = eq[(eq.index >= lh_window[0]) & (eq.index <= lh_window[1])]

    rows: list[dict] = []

    # --- 8 named cohorts -------------------------------------------------------
    for cohort in COHORT_DATES:
        entry = pd.Timestamp(cohort["date"])
        if entry < ret_lh.index[0] or entry >= ret_lh.index[-1]:
            continue
        end = entry + pd.Timedelta(days=int(FORWARD_DAYS * 365 / 252))
        window_ret = ret_lh[(ret_lh.index >= entry) & (ret_lh.index <= end)]
        window_eq = eq_lh[(eq_lh.index >= entry) & (eq_lh.index <= end)]
        if len(window_ret) < 252 or len(window_eq) < 2:
            continue
        n_years = (window_eq.index[-1] - window_eq.index[0]).days / 365.25
        cagr = (
            (window_eq.iloc[-1] / window_eq.iloc[0]) ** (1 / n_years) - 1
            if n_years > 0
            else float("nan")
        )
        rows.append({
            "strategy": strategy_name,
            "cohort_id": cohort["cohort_id"],
            "event": cohort["event"],
            "tier": cohort["tier"],
            "entry_date": str(entry.date()),
            "sortino_5y": _annualised_sortino(window_ret, target=0.0),
            "sharpe_5y": _annualised_sharpe(window_ret),
            "cagr_5y": float(cagr),
        })

    # --- 4 regime cohorts (median forward-5y) ----------------------------------
    qqq_prices = load_testfolio_series("QQQSIM").dropna()
    regime_df = classify_regimes(qqq_prices)
    REGIMES = ["All-on", "Mostly-on", "Borderline", "Risk-off"]
    for regime in REGIMES:
        entries = regime_df.index[regime_df["regime"] == regime].tolist()
        sortinos: list[float] = []
        sharpes: list[float] = []
        cagrs: list[float] = []
        for entry in entries:
            if entry < ret_lh.index[0] or entry >= ret_lh.index[-1]:
                continue
            end = entry + pd.Timedelta(days=int(FORWARD_DAYS * 365 / 252))
            window_ret = ret_lh[(ret_lh.index >= entry) & (ret_lh.index <= end)]
            window_eq = eq_lh[(eq_lh.index >= entry) & (eq_lh.index <= end)]
            if len(window_ret) < 252 or len(window_eq) < 2:
                continue
            s = _annualised_sortino(window_ret, target=0.0)
            h = _annualised_sharpe(window_ret)
            n_years = (window_eq.index[-1] - window_eq.index[0]).days / 365.25
            c = (
                (window_eq.iloc[-1] / window_eq.iloc[0]) ** (1 / n_years) - 1
                if n_years > 0
                else float("nan")
            )
            # Aligned filter: discard window if ANY metric is non-finite.
            # Keeps sortinos/sharpes/cagrs lists index-aligned so medians
            # are computed over the same set of windows [advances_fin_ml, p.222-223].
            if np.isnan(s) or np.isinf(s) or np.isnan(h) or np.isnan(c):
                continue
            sortinos.append(s)
            sharpes.append(h)
            cagrs.append(c)
        if not sortinos:
            continue
        rows.append({
            "strategy": strategy_name,
            "cohort_id": f"regime_{regime}",
            "event": "median forward 5y",
            "tier": "regime",
            "entry_date": "",
            "sortino_5y": float(np.median(sortinos)),
            "sharpe_5y": float(np.median(sharpes)),
            "cagr_5y": float(np.median(cagrs)),
        })

    return pd.DataFrame(rows)

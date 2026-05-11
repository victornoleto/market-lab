"""Recompute Sortino across strategies × datasets × tracks (spec §2.1).

Groups:
  A. SPY anchors — 4 datasets, gross only (4 rows)
  B. Canonical (qld_vote_k2_off_zroz) — 4 datasets × 3 tracks (12 rows)
  C. Top-10 from tax_comparison — lh_56y × 3 tracks (30 rows)
  D. Top-3 cohort × regime — lh_56y × 4 regimes × 3 strategies (12 rows)
  E. 12 threshold sweep variants — lh_56y × 3 tracks (36 rows)

Total: 94 rows.

Citations:
  - [sortino_1991] Sortino & van der Meer (1991), downside-deviation form.
  - [advances_fin_ml, p.275] net-of-cost evaluation rationale.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from studies.letf_rotation_hunt.core.data_loader import (
    load_ffr_daily,
    load_testfolio_series,
)
from studies.letf_rotation_hunt.runners.run_iter_t1 import DATASET_WINDOWS
from studies.letf_rotation_hunt.runners.run_iter_t3 import _run_single_composite_config
from studies.letf_rotation_hunt.analyses.sortino_reanalysis.sortino_metric import (
    _annualised_sortino,
)
from studies.letf_rotation_hunt.analyses.tax_comparison.per_swing import simulate_per_swing
from studies.letf_rotation_hunt.core.tax_layer import apply_annual_darf

INITIAL_CAPITAL = 10_000.0
TAX_RATE = 0.15
TRADING_DAYS_PER_YEAR = 252
DATASETS = ["lh_56y", "modern_1990", "spy_real", "ndx_real"]

CANONICAL_CFG = {
    "name": "qld_vote_k2_off_zroz",
    "on_asset": "QLD",
    "off_asset": "ZROZ",
    "signal_type": "vote_of_k",
    "k": 2,
    "sma_long_buffer_on": 0.0,
    "sma_long_buffer_off": 0.0,
    "sma_short_buffer_on": 0.0,
    "sma_short_buffer_off": 0.0,
    "ar1_buffer": 0.0,
}


def _annualised_sharpe(returns: pd.Series) -> float:
    if returns.std() == 0 or len(returns) < 2:
        return float("nan")
    return float(returns.mean() / returns.std() * np.sqrt(TRADING_DAYS_PER_YEAR))


def _slice_by_dataset(eq: pd.Series, ret: pd.Series, dataset: str) -> tuple[pd.Series, pd.Series]:
    win = DATASET_WINDOWS.get(dataset)
    if win is None:
        return eq, ret
    start, end = win
    mask_eq = (eq.index >= start) & (eq.index <= end)
    mask_ret = (ret.index >= start) & (ret.index <= end)
    return eq[mask_eq], ret[mask_ret]


def _compute_track_metrics(
    gross_eq: pd.Series,
    gross_returns: pd.Series,
    positions: pd.DataFrame,
    asset_returns_aligned: pd.DataFrame,
) -> dict[str, dict[str, float]]:
    """Return dict{track: {sharpe, sortino, final_equity, n_returns}} for gross/m1/m2.

    asset_returns_aligned columns must already be clean asset names (no suffix).
    The _run_single_composite_config helper returns asset_returns_aligned with
    clean names at construction time; no stripping is needed.

    Citations:
      - [sortino_1991] downside-dev Sortino form used throughout.
      - [advances_fin_ml, p.275] net-of-cost rationale for M1/M2 tracks.
    """
    out: dict[str, dict] = {}

    # Gross track
    rets_gross = gross_eq.pct_change().dropna()
    out["gross"] = {
        "sharpe": _annualised_sharpe(rets_gross),
        "sortino": _annualised_sortino(rets_gross, target=0.0),
        "final_equity": float(gross_eq.iloc[-1]),
        "n_returns": len(rets_gross),
    }

    # M1: per-swing 15% DARF (Lei 14.754/2023, per-swing mode)
    m1 = simulate_per_swing(
        positions, asset_returns_aligned,
        initial_capital=INITIAL_CAPITAL, tax_rate=TAX_RATE,
    )
    eq_m1 = m1["net_equity"].reindex(gross_eq.index)
    rets_m1 = eq_m1.pct_change().dropna()
    out["m1"] = {
        "sharpe": _annualised_sharpe(rets_m1),
        "sortino": _annualised_sortino(rets_m1, target=0.0),
        "final_equity": float(eq_m1.iloc[-1]),
        "n_returns": len(rets_m1),
    }

    # M2: annual realize 15% DARF (Lei 14.754/2023, annual mode)
    eq_m2 = apply_annual_darf(
        gross_eq, gross_returns, mode="annual_realize", initial=INITIAL_CAPITAL,
    )
    rets_m2 = eq_m2.pct_change().dropna()
    out["m2"] = {
        "sharpe": _annualised_sharpe(rets_m2),
        "sortino": _annualised_sortino(rets_m2, target=0.0),
        "final_equity": float(eq_m2.iloc[-1]),
        "n_returns": len(rets_m2),
    }

    return out


def recompute_spy_anchors() -> list[dict]:
    """Group A: SPY 1× buy-and-hold, 4 datasets, gross only.

    Returns Sortino + Sharpe per dataset for SPY. Used to anchor sortino_edge_vs_spy.

    Citations:
      - [sortino_1991] downside-dev form.
    """
    spy_full = load_testfolio_series("SPYSIM").dropna()
    spy_returns_full = spy_full.pct_change().dropna()

    rows: list[dict] = []
    for ds in DATASETS:
        ds_eq, ds_ret = _slice_by_dataset(spy_full, spy_returns_full, ds)
        if len(ds_ret) < 252:
            continue
        rows.append({
            "group": "A_spy_anchor",
            "strategy": "SPY",
            "dataset": ds,
            "track": "gross",
            "sharpe": _annualised_sharpe(ds_ret),
            "sortino": _annualised_sortino(ds_ret, target=0.0),
            "final_equity": float(ds_eq.iloc[-1]),
            "n_returns": len(ds_ret),
        })
    return rows


TOP10_CSV = Path("studies/letf_rotation_hunt/reports/tax_comparison/top10_metrics_by_dataset.csv")


def _load_top10_strategies() -> list[dict]:
    """Read tax_comparison top-10 CSV → unique config_name list, build cfg dicts.

    The top10 CSV has 10 strategies × 4 datasets × 3 tax_models = 120 rows.
    We need just the unique config_names + recover their cfg dicts from the
    parent study's iteration registry. For T3d configs, all share the
    vote_of_k signal_type; the per-strategy params (sma_long_period, vol_window,
    ar1_window, off_asset) need to be reconstructed.

    For this sub-study, we mirror the tax_comparison.select_top10 behavior:
    a config is identified by name + parent iter_id, and we infer params from
    the name suffix.
    """
    df = pd.read_csv(TOP10_CSV)
    unique_names = df["config_name"].drop_duplicates().tolist()
    return [_resolve_top10_cfg(name) for name in unique_names]


def _resolve_top10_cfg(config_name: str) -> dict:
    """Reconstruct cfg dict from a top-10 config name.

    Naming conventions seen in the top-10 set:

    T3d-extended-grid (iter 022):
      qld_voteK2_sma200_50_vol21_40_ar30_off_zroz  → sma200/50, vol21/40%, ar30
      qld_voteK2_sma200_50_vol42_40_ar30_off_zroz  → vol_window=42
      qld_voteK2_sma200_50_vol21_30_ar30_off_zroz  → vol_threshold=0.30
      qld_voteK2_sma250_100_vol21_40_ar30_off_zroz → sma_long=250, sma_short=100

    T3d-multi-asset-grid (iter 023, simple names — no sma/vol/ar suffixes):
      qld_voteK2_off_zroz_alt                      → QLD/ZROZ, canonical params
      qld_voteK2_off_edv                            → QLD/EDV, canonical params
      qld_voteK2_off_tlt                            → QLD/TLT, canonical params
      qld_voteK2_off_ief                            → QLD/IEF, canonical params
      tqqq_voteK2_off_zroz                          → TQQQ/ZROZ, canonical params

    Canonical T3d (iter 014, underscore vote_k2):
      qld_vote_k2_off_zroz                          → QLD/ZROZ, canonical params

    All signal_type=vote_of_k, k=2, buffers=0.0.
    Default params match run_iter_t3.py:208-212 (sma_long=200, sma_short=50,
    vol_window=21, vol_threshold=0.40, ar1_window=30).
    """
    # Defaults match run_iter_t3.py § vote_of_k defaults [advances_fin_ml, p.275]
    cfg: dict = {
        "name": config_name,
        "on_asset": "QLD",
        "off_asset": "ZROZ",
        "signal_type": "vote_of_k",
        "k": 2,
        "sma_long_period": 200,
        "sma_short_period": 50,
        "vol_window": 21,
        "vol_threshold": 0.40,
        "ar1_window": 30,
        "sma_long_buffer_on": 0.0,
        "sma_long_buffer_off": 0.0,
        "sma_short_buffer_on": 0.0,
        "sma_short_buffer_off": 0.0,
        "ar1_buffer": 0.0,
    }
    if config_name.startswith("tqqq_"):
        cfg["on_asset"] = "TQQQ"
    elif config_name.startswith("upro_"):
        cfg["on_asset"] = "UPRO"
    parts = config_name.split("_")
    # Detect off_asset suffix: ..._off_<asset> — take part immediately after "off"
    if "off" in parts:
        idx = parts.index("off")
        if idx + 1 < len(parts):
            cfg["off_asset"] = parts[idx + 1].upper()
    # Detect sma_long from sma<N> token (e.g. sma200, sma250)
    for p in parts:
        if p.startswith("sma") and len(p) > 3 and p[3:].isdigit():
            cfg["sma_long_period"] = int(p[3:])
            break
    # Detect vol_window from vol<N> token (e.g. vol21, vol42)
    for p in parts:
        if p.startswith("vol") and len(p) > 3 and p[3:].isdigit():
            cfg["vol_window"] = int(p[3:])
            break
    # Detect vol_threshold from the token after vol<N>: e.g. ..._vol21_40_... → 40 → 0.40
    # Guard: nxt.isdigit() filters out adjacent tokens like `ar30` (e.g. when the
    # name is `vol30_ar30_off_zroz` with no explicit threshold), in which case the
    # default 0.40 is preserved. Only purely-numeric next tokens become thresholds.
    for i, p in enumerate(parts):
        if p.startswith("vol") and len(p) > 3 and p[3:].isdigit() and i + 1 < len(parts):
            nxt = parts[i + 1]
            if nxt.isdigit():
                cfg["vol_threshold"] = int(nxt) / 100.0
            break
    # Detect sma_short from token after sma<N>: e.g. ..._sma200_50_... → 50
    for i, p in enumerate(parts):
        if p.startswith("sma") and len(p) > 3 and p[3:].isdigit() and i + 1 < len(parts):
            nxt = parts[i + 1]
            if nxt.isdigit():
                cfg["sma_short_period"] = int(nxt)
            break
    # Detect ar1_window from ar<N> token (e.g. ar30, ar60)
    for p in parts:
        if p.startswith("ar") and len(p) > 2 and p[2:].isdigit():
            cfg["ar1_window"] = int(p[2:])
            break
    return cfg


def recompute_top10() -> list[dict]:
    """Group C: top-10 strategies (lh_56y only) × 3 tracks = 30 rows.

    Loads unique configs from the tax_comparison top-10 CSV, runs each through
    the T3d pipeline end-to-end, and computes gross/M1/M2 Sortino+Sharpe on
    the lh_56y window.

    Note: _run_single_composite_config returns `_asset_returns_aligned` with
    clean asset column names — no suffix stripping required (same as Group B).

    Citations:
      - [sortino_1991] downside-dev Sortino form.
      - [advances_fin_ml, p.275] net-of-cost evaluation.
    """
    import warnings
    ffr_daily = load_ffr_daily()
    cfgs = _load_top10_strategies()
    rows: list[dict] = []
    for cfg in cfgs:
        try:
            result = _run_single_composite_config(
                cfg, datasets=["lh_56y"], ffr_daily=ffr_daily, n_trials_local=1,
            )
        except Exception as e:
            # Resilient continue-on-error: a broken config drops 3 rows from the
            # final 30-row Group C output. Use warnings.warn so dropped configs
            # surface in the test/CI log instead of silently disappearing.
            warnings.warn(
                f"[recompute_top10] dropping {cfg['name']!r} from Group C: {e}",
                RuntimeWarning, stacklevel=2,
            )
            continue

        full_eq = result["_equity"]
        full_ret = result["_strategy_returns"]
        positions = result["_positions"]
        asset_returns = result["_asset_returns_aligned"]
        ds_eq, ds_ret = _slice_by_dataset(full_eq, full_ret, "lh_56y")
        pos_ds = positions.loc[positions.index.intersection(ds_ret.index)]
        ar_ds = asset_returns.loc[asset_returns.index.intersection(ds_ret.index)]

        track_metrics = _compute_track_metrics(ds_eq, ds_ret, pos_ds, ar_ds)
        for track, m in track_metrics.items():
            rows.append({
                "group": "C_top10",
                "strategy": cfg["name"],
                "dataset": "lh_56y",
                "track": track,
                **m,
            })
    return rows


def recompute_threshold_variants() -> list[dict]:
    """Group E: 12 threshold sweep variants (lh_56y) × 3 tracks = 36 rows.

    Reuses VARIANTS from threshold_sweep.variant_grid (import is lazy to avoid
    circular dep on module-load). Dispatches each variant through the T3d pipeline
    and computes gross/M1/M2 Sortino+Sharpe on the lh_56y window.

    Note: _run_single_composite_config returns `_asset_returns_aligned` with
    clean asset column names — no suffix stripping required.

    No try/except resilience here (unlike `recompute_top10`): VARIANTS is a
    static grid declared in threshold_sweep/variant_grid.py:31-48 with
    explicit cfg dicts known to be valid (already validated in the canonical
    threshold_sweep run). A failure here indicates a system-level issue
    (missing data, OOM) where silent continuation would mask a real bug.

    Citations:
      - [sortino_1991] downside-dev Sortino form.
      - [advances_fin_ml, p.275] net-of-cost evaluation.
    """
    from studies.letf_rotation_hunt.analyses.threshold_sweep.variant_grid import VARIANTS

    ffr_daily = load_ffr_daily()
    rows: list[dict] = []
    for variant in VARIANTS:
        result = _run_single_composite_config(
            variant, datasets=["lh_56y"], ffr_daily=ffr_daily,
            n_trials_local=len(VARIANTS),
        )
        full_eq = result["_equity"]
        full_ret = result["_strategy_returns"]
        positions = result["_positions"]
        asset_returns = result["_asset_returns_aligned"]
        ds_eq, ds_ret = _slice_by_dataset(full_eq, full_ret, "lh_56y")
        pos_ds = positions.loc[positions.index.intersection(ds_ret.index)]
        ar_ds = asset_returns.loc[asset_returns.index.intersection(ds_ret.index)]

        track_metrics = _compute_track_metrics(ds_eq, ds_ret, pos_ds, ar_ds)
        for track, m in track_metrics.items():
            rows.append({
                "group": "E_threshold_sweep",
                "strategy": variant["name"],
                "dataset": "lh_56y",
                "track": track,
                **m,
            })
    return rows


TOP3_COHORT_NAMES = [
    "qld_vote_k2_off_zroz",
    "qld_voteK2_sma250_100_vol21_40_ar30_off_zroz",
    "tqqq_voteK2_off_zroz",
]


def recompute_regime_medians() -> list[dict]:
    """Group D: top-3 cohort × 4 regimes, median forward-5y Sortino.

    For each (strategy, regime) pair:
      1. Re-dispatch the strategy on lh_56y.
      2. Use classify_regimes(QQQ_prices) to get monthly K-counts.
      3. For each month-end classified into the regime, slice forward 5y
         returns and compute Sortino on that 5y window.
      4. Take the median Sortino across all entry months in the regime.

    Regime taxonomy: All-on (K=4), Mostly-on (K=3), Borderline (K=2),
    Risk-off (K∈{0,1}) [spec §4.1 regime_classifier.py].

    Citations:
      - [sortino_1991] downside-dev Sortino form for each forward window.
      - [advances_fin_ml, p.275] net-of-cost evaluation rationale (gross only
        used here — regime signal is regime-entry at classification time, not
        portfolio entry; full M1/M2 carried in Groups B/C/E).
    """
    from studies.letf_rotation_hunt.analyses.cohort_robustness.regime_classifier import (
        classify_regimes,
    )

    ffr_daily = load_ffr_daily()
    qqq_prices = load_testfolio_series("QQQSIM").dropna()
    regime_df = classify_regimes(qqq_prices)  # indexed by month-end, has `regime` column

    REGIMES = ["All-on", "Mostly-on", "Borderline", "Risk-off"]
    FORWARD_DAYS = 252 * 5  # 5-year forward window

    rows: list[dict] = []
    for strat_name in TOP3_COHORT_NAMES:
        cfg = _resolve_top10_cfg(strat_name)
        result = _run_single_composite_config(
            cfg, datasets=["lh_56y"], ffr_daily=ffr_daily, n_trials_local=1,
        )
        ret = result["_strategy_returns"]
        ret_lh = ret[(ret.index >= DATASET_WINDOWS["lh_56y"][0]) & (ret.index <= DATASET_WINDOWS["lh_56y"][1])]

        for regime in REGIMES:
            regime_entries = regime_df.index[regime_df["regime"] == regime].tolist()
            sortinos: list[float] = []
            sharpes: list[float] = []
            for entry in regime_entries:
                if entry < ret_lh.index[0] or entry >= ret_lh.index[-1]:
                    continue
                # Forward 5y window (~1825 calendar days; ~365.7 cal days per 252 trading days)
                end = entry + pd.Timedelta(days=FORWARD_DAYS * 365 / 252)
                window_ret = ret_lh[(ret_lh.index >= entry) & (ret_lh.index <= end)]
                if len(window_ret) < 252:
                    continue
                s = _annualised_sortino(window_ret, target=0.0)
                h = _annualised_sharpe(window_ret)
                # Filter both metrics with the SAME predicate to keep sortinos
                # and sharpes lists aligned (same windows in both medians).
                # Sortino can produce ±inf when all returns >= target (rare on
                # lh_56y but possible on shorter windows); Sharpe can produce
                # NaN when std==0. Either condition disqualifies the window.
                if np.isnan(s) or np.isinf(s) or np.isnan(h):
                    continue
                sortinos.append(s)
                sharpes.append(h)
            if not sortinos:
                continue
            rows.append({
                "group": "D_regime_median",
                "strategy": strat_name,
                "dataset": "lh_56y",
                "track": "gross",
                "regime": regime,
                "sortino": float(np.median(sortinos)),
                "sharpe": float(np.median(sharpes)),
                "n_entries": len(sortinos),
            })
    return rows


def recompute_canonical() -> list[dict]:
    """Group B: canonical (qld_vote_k2_off_zroz), 4 datasets × 3 tracks.

    Dispatches the T3d pipeline end-to-end (~30-90 s) and slices the full-history
    equity/positions/asset_returns into each dataset window before computing
    gross/M1/M2 Sortino+Sharpe metrics.

    Note: _run_single_composite_config returns `_asset_returns_aligned` with
    clean asset column names (built as {c: aligned[f'{c}_r']} at run_iter_t3.py:401),
    so no suffix stripping is required here.

    Citations:
      - [sortino_1991] downside-dev Sortino form.
      - [advances_fin_ml, p.275] net-of-cost evaluation.
    """
    ffr_daily = load_ffr_daily()
    result = _run_single_composite_config(
        CANONICAL_CFG, datasets=DATASETS, ffr_daily=ffr_daily, n_trials_local=1,
    )
    full_eq = result["_equity"]
    full_ret = result["_strategy_returns"]
    positions = result["_positions"]
    asset_returns = result["_asset_returns_aligned"]

    rows: list[dict] = []
    for ds in DATASETS:
        ds_eq, ds_ret = _slice_by_dataset(full_eq, full_ret, ds)
        if len(ds_ret) < 252:
            continue
        # Slice positions/asset_returns to same date window
        pos_ds = positions.loc[positions.index.intersection(ds_ret.index)]
        ar_ds = asset_returns.loc[asset_returns.index.intersection(ds_ret.index)]

        track_metrics = _compute_track_metrics(ds_eq, ds_ret, pos_ds, ar_ds)
        for track, m in track_metrics.items():
            rows.append({
                "group": "B_canonical",
                "strategy": CANONICAL_CFG["name"],
                "dataset": ds,
                "track": track,
                **m,
            })
    return rows

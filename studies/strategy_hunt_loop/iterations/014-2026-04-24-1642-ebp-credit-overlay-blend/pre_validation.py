"""Iter 014 — Pre-validation gate: |ρ(EBP_z, σ²_port)| screening.

Before committing DSR budget to a full run, measure whether EBP is
empirically non-cointegrated with iter 008 blend's portfolio variance
at the business-cycle timescale (60-day rolling window).

Screen rule: if fraction of bars with |ρ| > 0.30 exceeds 20 % on ANY
of the 3 datasets → ABORT iteration (write ``pre_val_failed.json``,
iterator falls through to final_report with pre-val failure).

This is the primary defense against re-opening the cointegration
failure mode observed in iter 009/012/013 (T10Y3M, asymmetric T10Y3M,
meta-labeling with ρ+VIX features — all showed 100 % gate-fire
/ bottom-20 %-scale overlap on SPY-based datasets).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ITER_DIR = Path(__file__).resolve().parent
ITER006_DIR = ITER_DIR.parent / "006-2026-04-24-1027-vol-managed-60-40"
ROOT = ITER_DIR.parents[3]

sys.path.insert(0, str(ITER_DIR))
sys.path.insert(0, str(ITER006_DIR))

from ebp_credit_overlay import compute_ebp_zscore, load_ebp_daily  # noqa: E402
from stock_bond_blend import apply_blend_variance_target  # noqa: E402


TIINGO_DIR = ROOT / "data" / "tiingo" / "daily" / "prices"
MACRO_DIR = ROOT / "data" / "external" / "macro"
EBP_PATH = MACRO_DIR / "ebp_monthly.parquet"


DATASETS: dict[str, dict] = {
    "educational": {
        "equity_symbol": "SPY",
        "bond_symbol": "TLT",
        "start": "2002-07-26",
        "end": "2026-04-15",
    },
    "spy_real": {
        "equity_symbol": "SPY",
        "bond_symbol": "TLT",
        "start": "2009-06-25",
        "end": "2026-04-15",
    },
    "ndx_real": {
        "equity_symbol": "QQQ",
        "bond_symbol": "TLT",
        "start": "2010-02-12",
        "end": "2026-04-15",
    },
}


# Iter 008 pre-committed blend cfg — reused unchanged.
BLEND_CFG: dict = {
    "cfg_id": "vt15_L21_cap20",
    "target_vol": 0.15,
    "lookback": 21,
    "max_leverage": 2.0,
}

# Pre-validation thresholds (pre-committed).
PREVAL_CFG: dict = {
    "rolling_window": 60,
    "rho_threshold": 0.30,
    "max_exceed_frac": 0.20,
}


def load_paired_returns(eq: str, bd: str, start: str, end: str) -> pd.DataFrame:
    df_eq = pd.read_parquet(TIINGO_DIR / f"{eq}.parquet")
    df_bd = pd.read_parquet(TIINGO_DIR / f"{bd}.parquet")
    mask_eq = (df_eq.index >= start) & (df_eq.index <= end)
    mask_bd = (df_bd.index >= start) & (df_bd.index <= end)
    p_eq = df_eq.loc[mask_eq, "adj_close"]
    p_bd = df_bd.loc[mask_bd, "adj_close"]
    joined = pd.concat({"eq": p_eq, "bd": p_bd}, axis=1, join="inner").dropna()
    r = joined.pct_change().dropna()
    r.columns = [eq, bd]
    return r


def compute_sigma2_port(
    returns: pd.DataFrame, *, realised_window: int = 60
) -> pd.Series:
    """Realised annualised portfolio variance from iter 008 blend net returns.

    Computes the un-gated blend on the 2-leg returns, then takes the
    rolling ``realised_window``-bar variance of the resulting NET
    return series, annualised. This is the actual σ²_port(blend) —
    avoids the ``target_var / scale`` saturation artifact (at the cap,
    the identity yields a constant that does not reflect the real
    portfolio variance dynamics).
    """
    eq_col, bd_col = returns.columns
    net, _, _, _ = apply_blend_variance_target(
        returns[eq_col], returns[bd_col],
        target_vol=BLEND_CFG["target_vol"],
        lookback=BLEND_CFG["lookback"],
        max_leverage=BLEND_CFG["max_leverage"],
    )
    # Realised rolling variance of blend net returns, annualised.
    sigma2 = (net.rolling(realised_window, min_periods=realised_window)
              .std(ddof=0) ** 2 * 252.0)
    sigma2.name = "sigma2_port"
    return sigma2


def rolling_corr(x: pd.Series, y: pd.Series, window: int) -> pd.Series:
    """Rolling Pearson correlation with window=window bars (inf-safe)."""
    df = pd.concat({"x": x, "y": y}, axis=1, join="inner")
    rho = df["x"].rolling(window, min_periods=window).corr(df["y"])
    # Cleanup: if either series is constant within the window, pandas
    # emits inf; treat as missing (not measurable).
    rho = rho.replace([np.inf, -np.inf], np.nan)
    return rho


def pre_validate_dataset(
    dataset_name: str,
    returns: pd.DataFrame,
    ebp_z: pd.Series,
) -> dict:
    """Pre-validation stats for one dataset."""
    sigma2 = compute_sigma2_port(returns)
    rho = rolling_corr(ebp_z, sigma2, PREVAL_CFG["rolling_window"])
    rho_valid = rho.dropna()
    n_valid = len(rho_valid)
    if n_valid == 0:
        return {
            "dataset": dataset_name,
            "n_valid": 0,
            "status": "degenerate",
            "exceed_frac": None,
            "frac_nan_in_window": None,
        }
    exceed = (rho_valid.abs() > PREVAL_CFG["rho_threshold"]).mean()
    pass_screen = exceed <= PREVAL_CFG["max_exceed_frac"]
    return {
        "dataset": dataset_name,
        "n_valid": int(n_valid),
        "exceed_frac": float(exceed),
        "max_abs_rho": float(rho_valid.abs().max()),
        "mean_abs_rho": float(rho_valid.abs().mean()),
        "rho_positive_frac": float((rho_valid > 0).mean()),
        "rho_negative_frac": float((rho_valid < 0).mean()),
        "passes_screen": bool(pass_screen),
    }


def main() -> None:
    print("=" * 70)
    print("Iter 014 — EBP credit overlay: PRE-VALIDATION SCREEN")
    print("=" * 70)
    print(f"Rolling window: {PREVAL_CFG['rolling_window']} bars")
    print(f"|ρ| threshold: {PREVAL_CFG['rho_threshold']}")
    print(f"Max exceed fraction allowed: {PREVAL_CFG['max_exceed_frac']}")
    print()

    report: dict = {
        "preval_cfg": PREVAL_CFG,
        "blend_cfg": BLEND_CFG,
        "ebp_column": "ebp",
        "datasets": {},
        "all_pass": None,
    }

    all_pass = True
    for ds_name, ds in DATASETS.items():
        r = load_paired_returns(ds["equity_symbol"], ds["bond_symbol"],
                                ds["start"], ds["end"])
        ebp_raw = load_ebp_daily(EBP_PATH, r.index, lag_bars=1, column="ebp")
        ebp_z = compute_ebp_zscore(ebp_raw, window=252)
        stats = pre_validate_dataset(ds_name, r, ebp_z)
        report["datasets"][ds_name] = stats
        status = "PASS" if stats.get("passes_screen") else "FAIL"
        exceed = stats.get("exceed_frac")
        max_abs = stats.get("max_abs_rho")
        print(f"[{status}] {ds_name:12s}  "
              f"|ρ|>0.30 frac={exceed:.3f}  "
              f"max|ρ|={max_abs:.3f}  "
              f"mean|ρ|={stats.get('mean_abs_rho', 0):.3f}  "
              f"n={stats['n_valid']}")
        if not stats.get("passes_screen", False):
            all_pass = False

    report["all_pass"] = all_pass
    print()
    print("=" * 70)
    if all_pass:
        print("VERDICT: PRE-VALIDATION PASSED — proceed to full backtest.")
    else:
        print("VERDICT: PRE-VALIDATION FAILED — abort iteration before DSR spent.")
    print("=" * 70)

    out_path = ITER_DIR / "pre_validation.json"
    out_path.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()

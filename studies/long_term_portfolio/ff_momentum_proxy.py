"""Pre-1988 KMLM proxy via Fama-French daily momentum factor (UMD).

KMLMSIM (testfolio synth for KMLM, the KFA MLM Index ETF) starts 1987-12-31.
The lh_56y dataset spans 1970-01-02 → 2026-04-24, so KMLM-using strategies
need a proxy for the 1970-1988 portion of the KMLM allocation.

Choice: the academic Fama-French momentum factor (UMD/Mom) plus the daily
risk-free rate, sourced from Ken French's public data library:

  - Mom returns: data/ken_french/F-F_Momentum_Factor_daily.csv
  - RF rate:     data/ken_french/F-F_Research_Data_Factors_daily.csv

UMD is a long-short cross-sectional equity momentum factor, NOT a perfect
proxy for KMLM's multi-asset trend-following mechanics. It is the standard
academic reference for "momentum/trend pre-managed-futures-ETFs". Treat
the resulting backtest pre-1988 as approximate; full lh_56y comparisons
must disclose the splice window in `final_report.md`.

Citations:
  - Jegadeesh-Titman 1993 momentum effect (UMD construction).
  - Moskowitz-Ooi-Pedersen 2012 Time-Series Momentum (similar shape).
  - Asness-Frazzini-Pedersen 2014 momentum premium ~7%/yr historical.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[2]
DEFAULT_MOM_CSV = REPO / "data/ken_french/F-F_Momentum_Factor_daily.csv"
DEFAULT_RF_CSV = REPO / "data/ken_french/F-F_Research_Data_Factors_daily.csv"


def _parse_ff_csv(path: Path, value_col: str) -> pd.Series:
    """Parse a Ken French daily-frequency CSV and return one column as decimal returns.

    The header row starts with a leading comma (`,col1,col2,...`) because the
    date column is unnamed. We auto-detect that line, skip the descriptive
    text above it, then load with pandas. Daily rows are `YYYYMMDD,val1,...`
    in PERCENT — divided by 100 on return.
    """
    if not path.exists():
        raise FileNotFoundError(
            f"{path} not found — download from Ken French data library."
        )

    header_idx = None
    with path.open("r") as fh:
        for i, line in enumerate(fh):
            if line.startswith(",") and not line.strip() == ",":
                header_idx = i
                break
    if header_idx is None:
        raise ValueError(f"Could not find header row in {path}")

    raw = pd.read_csv(path, skiprows=header_idx, na_values=["-99.99", "-999"])
    raw = raw.rename(columns={raw.columns[0]: "date"})
    raw = raw[raw["date"].astype(str).str.match(r"^\d{8}$", na=False)]
    raw["date"] = pd.to_datetime(raw["date"].astype(str), format="%Y%m%d")
    raw = raw.set_index("date").sort_index()
    if value_col not in raw.columns:
        raise KeyError(
            f"{value_col!r} not in columns of {path.name}: {list(raw.columns)}"
        )
    s = raw[value_col].astype(float) / 100.0
    s.name = value_col
    return s.dropna()


def ff_momentum_proxy(
    mom_csv: Path = DEFAULT_MOM_CSV,
    rf_csv: Path = DEFAULT_RF_CSV,
) -> pd.Series:
    """Daily UMD + RF total return, decimal scale, full available history.

    Returns a pd.Series indexed by date covering ~1926-11-03 → present
    (whatever both source files agree on). Caller slices to the splice
    window 1970-01-02 → 1987-12-30 when used as pre-1988 KMLM proxy.
    """
    mom = _parse_ff_csv(mom_csv, "Mom")
    rf = _parse_ff_csv(rf_csv, "RF")
    common = mom.index.intersection(rf.index)
    out = (mom.loc[common] + rf.loc[common]).rename("ff_momentum_proxy")
    return out


def splice_kmlm_pre_1988(
    kmlmsim: pd.Series,
    inception: str = "1987-12-31",
) -> pd.Series:
    """Build a continuous KMLM-flavor return series 1970+ by splicing UMD+RF before inception.

    Args:
        kmlmsim: KMLMSIM equity-curve or returns from testfolio cache. If
            equity-curve (monotonic), pct_change is taken; if already returns,
            used as-is (heuristic: equity > 1 always).
        inception: cutoff date; pre-cutoff comes from `ff_momentum_proxy`,
            post-cutoff from `kmlmsim`.

    Returns:
        pd.Series of daily returns (decimal) covering 1970-01-02 → kmlmsim.end.
    """
    cutoff = pd.Timestamp(inception)
    # Decide: equity-curve vs returns. Equity has min > 0 typically; returns center ~0.
    if kmlmsim.min() > 0.5 and kmlmsim.max() > 1.5:
        kmlm_returns = kmlmsim.pct_change().dropna()
    else:
        kmlm_returns = kmlmsim.dropna()

    proxy = ff_momentum_proxy().loc["1970-01-02":cutoff]
    post = kmlm_returns.loc[kmlm_returns.index > cutoff]
    spliced = pd.concat([proxy, post]).sort_index()
    spliced.name = "kmlm_spliced"
    return spliced[~spliced.index.duplicated(keep="last")]


if __name__ == "__main__":
    s = ff_momentum_proxy()
    print(f"FF MoM proxy: {s.index[0].date()} → {s.index[-1].date()}, n={len(s)}")
    window = s.loc["1970-01-02":"1987-12-30"]
    import numpy as np
    ann_mean = window.mean() * 252 * 100
    ann_vol = window.std() * np.sqrt(252) * 100
    print(f"1970-1987 ann mean={ann_mean:.2f}%/yr  vol={ann_vol:.2f}%/yr  Sharpe={ann_mean/ann_vol:.2f}")

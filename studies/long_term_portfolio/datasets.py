"""Central dataset registry for the long-term portfolio loop.

Iterations import `DATASETS` (window metadata) and `load_prices(name)` to
get a price DataFrame ready for the strategy code. The loader handles the
KMLMSIM pre-1988 splice for `lh_56y` so iterations don't have to.

Datasets:

  - ``lh_56y``: 1970-01-02 → 2026-04-24 (the long-history window). Replaces
    the legacy ``educational`` dataset (which was a 31y slice of the same
    universe). KMLMSIM column is splice-aware: pre-1988-12-31 returns come
    from `ff_momentum_proxy.ff_momentum_proxy()` (UMD + RF, Ken French),
    1988+ comes from KMLMSIM testfolio synth as-is. The splice makes
    KMLM-using strategies testable on the full 56y window — caveat: UMD
    is academic equity-momentum, not multi-asset trend, so the 1970-87
    portion is approximate (likely overstates KMLM-style returns by a
    factor of ~3 in Sharpe terms).
  - ``vt_real``: 2008-06-01 → 2026-04-24 (live VT proxy era).
  - ``ndx_real``: 2010-02-01 → 2026-04-24 (live QQQ stretch test).

The benchmark Sharpe values in `scoring.py` BENCHMARKS were always
computed on the lh_56y window (the previous "educational" name was
misleading); see the rename note in scoring.py.

Citations:
  - Capital efficiency / return stacking: [risk_parity, ch.5, p.10]
  - Momentum factor as managed-futures proxy: [stocks_on_the_move, p.21-30]
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from studies.long_term_portfolio.ff_momentum_proxy import ff_momentum_proxy


DATASETS: dict[str, dict[str, str]] = {
    "lh_56y": {
        "start": "1970-01-02",
        "end": "2026-04-24",
        "benchmark": "VTSIM",
        "description": "Long-history 56y window (1970+); KMLMSIM splice-aware (UMD+RF pre-1988).",
    },
    "vt_real": {
        "start": "2008-06-01",
        "end": "2026-04-24",
        "benchmark": "VTSIM",
        "description": "Live-VT-era stretch test (17y, VT proxy via VTSIM).",
    },
    "ndx_real": {
        "start": "2010-02-01",
        "end": "2026-04-24",
        "benchmark": "QQQSIM",
        "description": "Live-QQQ-era NDX stretch test (16y).",
    },
    "spy_real": {
        "start": "2003-08-20",
        "end": "2026-04-14",
        "benchmark": "SPY",
        "description": (
            "SPY Tiingo daily real (22.7y, 2003-08-20 → 2026-04-14). "
            "Captures 2003-07 housing bull, 2007-09 GFC peak-to-trough -56%, "
            "2009-19 super-bull, 2020 COVID, 2022 inflation. "
            "Strategy returns still use testfolio synths (UPROSIM/SSOSIM/IEFSIM); "
            "the 'real' part is the SPY benchmark reference (Tiingo adj_close) "
            "in scoring.py — replaces vt_real/ndx_real as the post-GFC anchor "
            "for spy_beater_hunt 2-dataset setup."
        ),
    },
}


KMLM_INCEPTION = pd.Timestamp("1987-12-31")


def _build_spliced_kmlmsim(
    raw_kmlmsim: pd.Series,
    splice_start: pd.Timestamp = pd.Timestamp("1970-01-02"),
) -> pd.Series:
    """Build a continuous equity curve for KMLMSIM with FF MoM proxy pre-1988.

    raw_kmlmsim is the testfolio cache column (equity-curve-like, normalised
    to ~10000 at first bar). We replace the pre-1988 NaN region with a
    cumprod of FF MoM returns scaled to chain continuously into the
    KMLMSIM curve at its inception (1987-12-31).
    """
    raw = raw_kmlmsim.dropna().sort_index()
    inception = raw.index[0]

    proxy_returns = ff_momentum_proxy().loc[splice_start:inception]
    proxy_returns_pre = proxy_returns.loc[proxy_returns.index < inception]
    if proxy_returns_pre.empty:
        return raw

    pre_equity = (1.0 + proxy_returns_pre).cumprod()
    scale = float(raw.iloc[0]) / float(pre_equity.iloc[-1])
    pre_scaled = pre_equity * scale

    spliced = pd.concat([pre_scaled, raw])
    spliced = spliced[~spliced.index.duplicated(keep="last")]
    spliced = spliced.sort_index()
    spliced.name = "KMLMSIM"
    return spliced


def load_prices(name: str) -> pd.DataFrame:
    """Return prices DataFrame for ``name``, sliced to the dataset's window.

    The DataFrame includes all SIM tickers from the testfolio cache. For
    ``lh_56y`` only, the KMLMSIM column is replaced with a splice-aware
    series (FF MoM proxy pre-1988 chained continuously into the 1988+ curve).
    """
    if name not in DATASETS:
        raise KeyError(
            f"unknown dataset {name!r}; choose from {list(DATASETS.keys())}"
        )

    from src.ai_trade.backtest.data.testfolio_loader import load_testfolio_frame

    meta = DATASETS[name]
    df = load_testfolio_frame()
    df = df.sort_index()

    if name == "lh_56y":
        spliced = _build_spliced_kmlmsim(df["KMLMSIM"])
        df = df.copy()
        df["KMLMSIM"] = df.index.map(spliced).astype(float)
        df.loc[spliced.index, "KMLMSIM"] = spliced.values

    return df.loc[meta["start"]:meta["end"]]


def get_meta(name: str) -> dict[str, str]:
    """Returns the dataset metadata dict (start/end/benchmark/description)."""
    if name not in DATASETS:
        raise KeyError(f"unknown dataset {name!r}")
    return dict(DATASETS[name])


if __name__ == "__main__":
    for ds in DATASETS:
        df = load_prices(ds)
        print(f"{ds}: {df.index[0].date()} → {df.index[-1].date()}, n={len(df)}, cols={len(df.columns)}")
        kmlm_pre = df.loc[:"1987-12-30", "KMLMSIM"] if ds == "lh_56y" else None
        if kmlm_pre is not None:
            print(f"  KMLMSIM pre-1988: n_non_nan={kmlm_pre.notna().sum()} (splice OK)")

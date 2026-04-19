"""Universe screener — orchestrates per-ticker metrics and ranks candidates.

The screener takes a TiingoStorage instance + a list of (ticker, asset_class)
candidates and returns a DataFrame with one row per ticker:

    columns = [
        ticker, asset_class, frequency,
        n_bars, first_dt, last_dt,
        hurst, hurst_r2, hurst_ci_low, hurst_ci_high,
        atr_pct, realized_vol, dollar_volume,
        mr_score, liquidity_rank, composite_rank,
        notes,
    ]

The composite rank ranks (a) MR-favorability — lower Hurst preferred — and
(b) tradability — higher dollar-volume preferred — and averages them. The
caller picks Top-N for Strategy A multi-asset expansion.

Citations
---------
- Hurst: ``[algo_trading_chan, p.44-46]``
- ATR / dollar-volume: ``[stocks_on_the_move, p.81, p.88]``
- Equal-weight rank combo: ``[algo_trading_chan, p.6-7, ch.1]`` (Kahneman
  2011 — equal-weight predictors often beat optimised weights).
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

import numpy as np
import pandas as pd

from ..data.tiingo_storage import TiingoStorage
from .hurst import hurst_exponent
from .metrics import atr_pct, dollar_volume, realized_vol_annualized

log = logging.getLogger(__name__)

__all__ = ["Candidate", "screen_universe"]


@dataclass(frozen=True)
class Candidate:
    """A (ticker, asset_class) pair to screen."""

    ticker: str
    asset_class: str  # "equity" | "etf" | "crypto" | "forex" | "index"


def _compute_row(
    cand: Candidate,
    df: pd.DataFrame,
    *,
    frequency: str,
    bars_per_year: int,
    bootstrap: int,
    random_state: int | None,
) -> dict[str, object]:
    row: dict[str, object] = {
        "ticker": cand.ticker,
        "asset_class": cand.asset_class,
        "frequency": frequency,
        "n_bars": int(len(df)),
        "first_dt": df.index[0],
        "last_dt": df.index[-1],
    }
    notes: list[str] = []
    try:
        h = hurst_exponent(
            df["close"],
            min_obs=252,
            n_lags=20,
            bootstrap=bootstrap,
            random_state=random_state,
        )
        row["hurst"] = h.h
        row["hurst_r2"] = h.r2
        row["hurst_ci_low"] = h.ci_low
        row["hurst_ci_high"] = h.ci_high
    except ValueError as exc:
        notes.append(f"hurst_failed:{exc}")
        row["hurst"] = float("nan")
        row["hurst_r2"] = float("nan")
        row["hurst_ci_low"] = None
        row["hurst_ci_high"] = None
    try:
        row["atr_pct"] = atr_pct(df, lookback=20)
    except ValueError as exc:
        notes.append(f"atr_failed:{exc}")
        row["atr_pct"] = float("nan")
    try:
        row["realized_vol"] = realized_vol_annualized(
            df, lookback=252, bars_per_year=bars_per_year
        )
    except ValueError as exc:
        notes.append(f"vol_failed:{exc}")
        row["realized_vol"] = float("nan")
    try:
        dv = dollar_volume(df, lookback=252)
        row["dollar_volume"] = dv if dv > 0 else float("nan")
        if dv == 0:
            notes.append("dollar_volume=0 (no volume data)")
    except ValueError as exc:
        notes.append(f"dvol_failed:{exc}")
        row["dollar_volume"] = float("nan")
    row["notes"] = ";".join(notes) if notes else ""
    return row


def _rank_descending(series: pd.Series) -> pd.Series:
    return series.rank(method="average", ascending=False, na_option="bottom")


def _rank_ascending(series: pd.Series) -> pd.Series:
    return series.rank(method="average", ascending=True, na_option="bottom")


def screen_universe(
    candidates: list[Candidate],
    storage: TiingoStorage,
    *,
    frequency: str = "daily",
    bars_per_year: int = 252,
    bootstrap: int = 0,
    random_state: int | None = 7,
) -> pd.DataFrame:
    """Return a DataFrame with screening metrics + composite rank.

    Reads each candidate's longest available history from ``storage`` (the
    Phase 3 mandate: ALWAYS use the longest available window per
    ``(ticker, frequency)``). Computes Hurst, ATR%, realized vol, dollar
    volume; ranks by:

    * ``mr_score`` = ``1 - hurst`` (clamped to [0, 1]); higher = more
      mean-reverting, which is what Strategy A (BollingerMR) needs.
    * ``liquidity_rank`` = descending rank by ``dollar_volume`` (or by
      ATR%·n_bars when volume is missing — crypto/FX edge case).

    The composite rank averages the two ranks (equal-weight, per
    ``[algo_trading_chan, p.6-7]``).

    Tickers with insufficient history (< 252 + 21 bars) are dropped before
    ranking but kept in the output with NaN columns + a note.
    """

    rows: list[dict[str, object]] = []
    for cand in candidates:
        try:
            df = storage.read(cand.ticker, frequency=frequency)
        except (KeyError, FileNotFoundError):
            log.warning("screener: %s/%s not in storage", cand.ticker, frequency)
            rows.append(
                {
                    "ticker": cand.ticker,
                    "asset_class": cand.asset_class,
                    "frequency": frequency,
                    "n_bars": 0,
                    "first_dt": pd.NaT,
                    "last_dt": pd.NaT,
                    "hurst": float("nan"),
                    "hurst_r2": float("nan"),
                    "hurst_ci_low": None,
                    "hurst_ci_high": None,
                    "atr_pct": float("nan"),
                    "realized_vol": float("nan"),
                    "dollar_volume": float("nan"),
                    "notes": "not_in_storage",
                }
            )
            continue
        if len(df) < 252 + 21:
            rows.append(
                {
                    "ticker": cand.ticker,
                    "asset_class": cand.asset_class,
                    "frequency": frequency,
                    "n_bars": int(len(df)),
                    "first_dt": df.index[0] if len(df) else pd.NaT,
                    "last_dt": df.index[-1] if len(df) else pd.NaT,
                    "hurst": float("nan"),
                    "hurst_r2": float("nan"),
                    "hurst_ci_low": None,
                    "hurst_ci_high": None,
                    "atr_pct": float("nan"),
                    "realized_vol": float("nan"),
                    "dollar_volume": float("nan"),
                    "notes": "insufficient_history",
                }
            )
            continue
        rows.append(
            _compute_row(
                cand,
                df,
                frequency=frequency,
                bars_per_year=bars_per_year,
                bootstrap=bootstrap,
                random_state=random_state,
            )
        )

    df_out = pd.DataFrame(rows)

    h = df_out["hurst"]
    df_out["mr_score"] = (1.0 - h).clip(lower=0.0, upper=1.0)

    # liquidity_rank: prefer dollar_volume; if all NaN within an asset class,
    # fall back to atr_pct (cheap proxy: more vol → easier to size around
    # spread). Equal-weight composite of the two ranks.
    dv = df_out["dollar_volume"]
    if dv.notna().any():
        df_out["liquidity_rank"] = _rank_descending(dv)
    else:
        df_out["liquidity_rank"] = _rank_descending(df_out["atr_pct"])

    df_out["mr_rank"] = _rank_ascending(h)  # ascending: lower H ranks 1st
    df_out["composite_rank"] = (
        df_out["mr_rank"] + df_out["liquidity_rank"]
    ) / 2.0

    return df_out.sort_values("composite_rank", kind="mergesort").reset_index(
        drop=True
    )

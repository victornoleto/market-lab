"""Entry-time multi-timeframe feature extraction.

For each trade in `trades.parquet` (`is_trade==True`), anchor at `open_dt_utc`
and compute features using ONLY data strictly before the anchor (lookback only).

Feature pack:

  Calendar:
    - hour_utc, dow, is_first_min_of_hour, is_first_5min_of_hour
    - session ∈ {Tokyo, London, NY, Late_NY, Quiet}

  Multi-timeframe (∀ tf ∈ {M1, M5, M15, H1, H4}):
    - ret_1[tf], ret_3[tf], ret_10[tf]   — log-returns of last 1/3/10 bars
    - ema_dist_20[tf]                    — (last_close - EMA20) / ATR14
    - atr_ratio[tf]                      — ATR14[tf] / ATR14[H1]
    - bb_pos_20_2[tf]                    — (last_close - SMA20) / (2*std20)
    - range_norm[tf]                     — (high - low) / ATR14, last bar
    - prior_bar_sign[tf]                 — sign(close - open) of last bar
    - close_vs_session_open[tf]          — sign(last_close - open_at_session_start)

  Cross-pair (computed on H1 closes from peer pairs in the system universe):
    - dollar_index_proxy                 — mean sign of last H1 close move across USD pairs
    - pair_cluster_dispersion            — std of last H1 returns across system universe

Citations:
- [advances_fin_ml, ch.5] — feature importance + clustered MDA
- [evidence_based_ta, Aronson, p.367-380] — session/hour FX regime
- [advances_fin_ml, ch.7] — purged k-fold (downstream consumer)
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Iterable

import numpy as np
import pandas as pd

from .ohlc_dukascopy import _DUKAS_PAIR_MAP, OhlcLoader

TIMEFRAMES = ("M1", "M5", "M15", "H1", "H4")
EMA_LEN = 20
BB_LEN = 20
ATR_LEN = 14

# Coverage required for indicator computation: enough bars to fill EMA20/BB20/ATR14.
_TF_LOOKBACK_BARS = max(EMA_LEN, BB_LEN, ATR_LEN) + 30


@dataclass(frozen=True)
class FeatureExtractionStats:
    n_trades: int
    n_features: int
    n_skipped_no_ohlc: int
    n_skipped_short_history: int


def _session_label(hour_utc: int) -> str:
    """Label FX session by entry hour (UTC).

    Conventions are slightly broker-dependent; we use the dominant overlap:
      Tokyo:    23–08 (open Tokyo, with Sydney pre-overlap)
      London:    7–16
      NY:       12–21
      Late_NY:  21–23 (post-NY-close, pre-Asian; thin liquidity, mean-reversion regime)

    [evidence_based_ta, Aronson, p.367-380]
    """
    if 21 <= hour_utc < 23:
        return "Late_NY"
    if hour_utc >= 23 or hour_utc < 7:
        return "Tokyo"
    if 7 <= hour_utc < 12:
        return "London"
    if 12 <= hour_utc < 21:
        return "NY"
    return "Quiet"


def _session_start_dt(anchor: datetime) -> datetime:
    """Return UTC datetime for the start of the current session containing `anchor`."""
    h = anchor.hour
    if 21 <= h < 23:
        return anchor.replace(hour=21, minute=0, second=0, microsecond=0)
    if h >= 23:
        return anchor.replace(hour=23, minute=0, second=0, microsecond=0)
    if h < 7:
        # Tokyo session that started 23:00 of the previous day
        prev = anchor - timedelta(days=1)
        return prev.replace(hour=23, minute=0, second=0, microsecond=0)
    if 7 <= h < 12:
        return anchor.replace(hour=7, minute=0, second=0, microsecond=0)
    return anchor.replace(hour=12, minute=0, second=0, microsecond=0)


def _calendar_features(anchor: datetime) -> dict[str, float | int | str]:
    return {
        "hour_utc": int(anchor.hour),
        "minute": int(anchor.minute),
        "dow": int(anchor.weekday()),  # 0=Mon
        "is_first_min_of_hour": int(anchor.minute == 0),
        "is_first_5min_of_hour": int(anchor.minute < 5),
        "session": _session_label(anchor.hour),
    }


def _ema(series: pd.Series, length: int) -> float:
    if len(series) < length:
        return float("nan")
    return float(series.ewm(span=length, adjust=False, min_periods=length).mean().iloc[-1])


def _atr(df: pd.DataFrame, length: int = ATR_LEN) -> float:
    if len(df) < length + 1:
        return float("nan")
    high = df["high"].astype(float)
    low = df["low"].astype(float)
    close = df["close"].astype(float)
    prev_close = close.shift(1)
    tr = pd.concat([high - low, (high - prev_close).abs(), (low - prev_close).abs()], axis=1).max(axis=1)
    return float(tr.rolling(length, min_periods=length).mean().iloc[-1])


def _bb_pos(series: pd.Series, length: int = BB_LEN, k: float = 2.0) -> float:
    if len(series) < length:
        return float("nan")
    sma = series.rolling(length, min_periods=length).mean().iloc[-1]
    std = series.rolling(length, min_periods=length).std().iloc[-1]
    if std == 0 or pd.isna(std):
        return float("nan")
    return float((series.iloc[-1] - sma) / (k * std))


def _log_return(series: pd.Series, n: int) -> float:
    if len(series) < n + 1 or series.iloc[-1] <= 0 or series.iloc[-(n + 1)] <= 0:
        return float("nan")
    return float(np.log(series.iloc[-1] / series.iloc[-(n + 1)]))


def _tf_features(
    loader: OhlcLoader,
    pair: str,
    anchor: datetime,
    freq: str,
    h1_atr: float,
    session_open_close: float | None,
) -> dict[str, float]:
    """Compute multi-tf features for one (pair, anchor, freq).

    `h1_atr` is precomputed once per trade and reused across timeframes for the
    `atr_ratio[tf]` denominator.
    """
    df = loader.lookback(pair, anchor, _TF_LOOKBACK_BARS, freq=freq)
    if len(df) < ATR_LEN + 1:
        return {f"{k}_{freq}": float("nan") for k in (
            "ret_1", "ret_3", "ret_10", "ema_dist_20", "atr_ratio",
            "bb_pos_20_2", "range_norm", "prior_bar_sign", "close_vs_session_open",
        )}
    close = df["close"]
    last_close = float(close.iloc[-1])
    last_open = float(df["open"].iloc[-1])
    last_high = float(df["high"].iloc[-1])
    last_low = float(df["low"].iloc[-1])

    atr = _atr(df, ATR_LEN)
    ema = _ema(close, EMA_LEN)
    ema_dist = (last_close - ema) / atr if atr and not pd.isna(atr) and atr > 0 else float("nan")
    range_norm = (last_high - last_low) / atr if atr and atr > 0 else float("nan")
    atr_ratio = (atr / h1_atr) if h1_atr and not pd.isna(h1_atr) and h1_atr > 0 else float("nan")
    prior_sign = float(np.sign(last_close - last_open))
    cvso = (
        float(np.sign(last_close - session_open_close))
        if session_open_close is not None and not pd.isna(session_open_close)
        else float("nan")
    )

    return {
        f"ret_1_{freq}": _log_return(close, 1),
        f"ret_3_{freq}": _log_return(close, 3),
        f"ret_10_{freq}": _log_return(close, 10),
        f"ema_dist_20_{freq}": ema_dist,
        f"atr_ratio_{freq}": atr_ratio,
        f"bb_pos_20_2_{freq}": _bb_pos(close, BB_LEN, 2.0),
        f"range_norm_{freq}": range_norm,
        f"prior_bar_sign_{freq}": prior_sign,
        f"close_vs_session_open_{freq}": cvso,
    }


def _session_open_close_h1(loader: OhlcLoader, pair: str, anchor: datetime) -> float | None:
    """H1 close at the bar that opened the current session — proxy for session-open price."""
    sstart = _session_start_dt(anchor)
    df = loader.load(pair, sstart, sstart + timedelta(hours=1), freq="H1")
    if df.empty:
        return None
    return float(df["close"].iloc[0])


def _cross_pair_features(
    loader: OhlcLoader, peer_pairs: Iterable[str], anchor: datetime
) -> dict[str, float]:
    rets: list[float] = []
    usd_signs: list[float] = []
    for pair in peer_pairs:
        df = loader.lookback(pair, anchor, 2, freq="H1")
        if len(df) < 2:
            continue
        r = _log_return(df["close"], 1)
        if pd.isna(r):
            continue
        rets.append(r)
        # USD-relative direction: if pair is XYZ/USD, +ret = USD weakens; if USD/XYZ, +ret = USD strengthens.
        if pair.startswith("USD"):
            usd_signs.append(float(np.sign(r)))
        elif pair.endswith("USD"):
            usd_signs.append(float(-np.sign(r)))
    return {
        "dollar_index_proxy": float(np.mean(usd_signs)) if usd_signs else float("nan"),
        "pair_cluster_dispersion": float(np.std(rets)) if rets else float("nan"),
    }


def compute_entry_features(
    trades_df: pd.DataFrame,
    loader: OhlcLoader,
    *,
    peer_pairs: Iterable[str] | None = None,
    progress: bool = True,
) -> tuple[pd.DataFrame, FeatureExtractionStats]:
    """Compute multi-tf entry features for every `is_trade==True` row.

    Args:
        trades_df: parsed trade history (must include open_dt_utc, symbol, action).
        loader: shared OhlcLoader (in-memory + parquet cache).
        peer_pairs: pairs used for cross-pair features. If None, derives from
            `trades_df["symbol"].unique()`.
        progress: print a heartbeat every 200 trades.

    Returns: (features_df indexed by trades_df index, stats).
    """
    trades = trades_df[trades_df.get("is_trade", True).astype(bool)].copy()
    # Drop trades on symbols Dukascopy can't supply OHLC for. Logged once for the report.
    supported = set(_DUKAS_PAIR_MAP.keys())
    unsupported_mask = ~trades["symbol"].astype(str).str.replace("/", "").str.upper().isin(supported)
    n_unsupported = int(unsupported_mask.sum())
    if n_unsupported:
        unsupported_syms = sorted(trades.loc[unsupported_mask, "symbol"].dropna().unique().tolist())
        print(f"  [features] skipping {n_unsupported} trades on unsupported pairs: {unsupported_syms}", flush=True)
        trades = trades[~unsupported_mask].copy()
    if peer_pairs is None:
        peer_pairs = sorted(trades["symbol"].dropna().unique().tolist())

    rows: list[dict] = []
    skipped_no_ohlc = 0
    skipped_short = 0

    iterator = trades.iterrows()
    for i, (idx, row) in enumerate(iterator):
        anchor: datetime = row["open_dt_utc"].to_pydatetime()
        if anchor.tzinfo is None:
            anchor = anchor.replace(tzinfo=timezone.utc)
        pair = str(row["symbol"])
        side = str(row.get("action", ""))

        feats: dict[str, float | int | str] = {
            "trade_idx": idx,
            "pair": pair,
            "side": side,
            "y_buy": int(side == "Buy"),
            **_calendar_features(anchor),
        }

        # H1 ATR is the denominator for atr_ratio across timeframes.
        df_h1 = loader.lookback(pair, anchor, _TF_LOOKBACK_BARS, freq="H1")
        h1_atr = _atr(df_h1, ATR_LEN) if len(df_h1) >= ATR_LEN + 1 else float("nan")
        if pd.isna(h1_atr):
            skipped_short += 1

        sopen = _session_open_close_h1(loader, pair, anchor)
        if sopen is None and df_h1.empty:
            skipped_no_ohlc += 1

        for tf in TIMEFRAMES:
            feats.update(_tf_features(loader, pair, anchor, tf, h1_atr, sopen))

        feats.update(_cross_pair_features(loader, [p for p in peer_pairs if p != pair], anchor))
        rows.append(feats)

        if progress and (i + 1) % 200 == 0:
            print(f"  features: {i + 1}/{len(trades)} trades extracted", flush=True)

    fdf = pd.DataFrame(rows)
    if not fdf.empty:
        fdf = fdf.set_index("trade_idx")
    stats = FeatureExtractionStats(
        n_trades=len(trades),
        n_features=int(len(fdf.columns)),
        n_skipped_no_ohlc=skipped_no_ohlc,
        n_skipped_short_history=skipped_short,
    )
    return fdf, stats

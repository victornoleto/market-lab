"""Assembles reference_prices.parquet — the single source of truth for Stage 1.

Post-inception of each real LETF (SSO 2006-06-21, QLD 2006-06-21, UGL 2008-12-03)
we use real OHLCV from yfinance (SSO/QLD/UGL are not in the Tiingo bulk cache — only
SPY/QQQ/GLD are available there).  Pre-inception, we synthesize via
``synthesize_letf_returns_ffr_aware`` — matching the methodology our engine uses
internally.  Synthetic OHLC collapses high=low=close=open=synthetic_close (no intraday).

The underlying tickers (SPY/QQQ/GLD) use Tiingo storage (absolute path to main repo
cache) because the worktree ``data/tiingo/`` directory only carries the manifest
symlink, not the parquet files themselves.

Citations
---------
- Synthetic formula: ``[leverage_for_the_long_run, p.16]``
- FFR-aware cost model: ``[leverage_for_the_long_run, p.16-17]``
- Two-stage isolation rationale: ``[advances_fin_ml, p.31-34]``
"""
from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path

import pandas as pd
import yfinance as yf

from ai_trade.backtest.data.spx_tr_loader import load_spx_tr_daily
from ai_trade.backtest.data.tiingo_storage import TiingoStorage
from ai_trade.backtest.helpers.synthetic_letf import (
    DEFAULT_EXPENSE_RATIO,
    DEFAULT_FFR_SPREAD,
    DEFAULT_SWAP_EXPOSURE,
    synthesize_letf_returns_ffr_aware,
)

# ---------------------------------------------------------------------------
# Module-level Tiingo singleton — absolute path to main repo bulk cache.
# The worktree data/tiingo/ only holds the manifest; parquet files live in
# the main repo at /var/www/pessoal/ai-trade/data/tiingo.
# Driven by AI_TRADE_TIINGO_ROOT env var; default points to main repo.
# ---------------------------------------------------------------------------
_TIINGO_ROOT = Path(
    os.environ.get("AI_TRADE_TIINGO_ROOT", "/var/www/pessoal/ai-trade/data/tiingo")
)
_STORAGE = TiingoStorage(root=_TIINGO_ROOT)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

REFERENCE_PARQUET = Path(
    "reports/phase_3_5c/cross_lib/data/reference_prices.parquet"
)

UNDERLYING_TICKERS: tuple[str, ...] = ("SPY", "QQQ", "GLD")


@dataclass(frozen=True)
class LetfSpec:
    """Specification for a leveraged ETF used in Plano B V4.

    Fields
    ------
    ticker : str
        Exchange ticker (e.g. "SSO").
    underlying : str
        Signal-generating underlying ticker ("SPY", "QQQ", "GLD").
    leverage : float
        Daily leverage factor (e.g. 2.0 for a 2× ETF).
    inception : str
        First trading date of the real ETF, ISO-format (YYYY-MM-DD).
        Used as the synthetic/real boundary.
    expense_ratio : float
        Annualized expense ratio, decimal (e.g. 0.0089 = 0.89%).
        Passed directly to ``synthesize_letf_returns_ffr_aware``.
    """

    ticker: str
    underlying: str
    leverage: float
    inception: str
    expense_ratio: float


LETF_SPECS: tuple[LetfSpec, ...] = (
    # SSO — ProShares Ultra S&P 500 (2×), inception 2006-06-21, ER 0.89 %
    # [leverage_for_the_long_run, p.16] — 2× SPY is the primary LRS vehicle.
    LetfSpec("SSO", "SPY", 2.0, "2006-06-21", 0.0089),
    # QLD — ProShares Ultra QQQ (2×), inception 2006-06-21, ER 0.95 %
    LetfSpec("QLD", "QQQ", 2.0, "2006-06-21", 0.0095),
    # UGL — ProShares Ultra Gold (2×), inception 2008-12-03, ER 0.95 %
    LetfSpec("UGL", "GLD", 2.0, "2008-12-03", 0.0095),
)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def build_reference_prices(
    canonical_start: str = "2004-10-01",
    canonical_end: str = "2026-04-18",
    extended_start: str = "1986-01-02",
    extended_end: str = "2026-04-18",
) -> pd.DataFrame:
    """Assemble the reference price table for Stage 1 cross-lib validation.

    Returns a long-format DataFrame with columns
    ``[date, ticker, open, high, low, close, volume]`` sorted by
    ``(ticker, date)``.  Six tickers are present: SPY, QQQ, GLD (raw
    Tiingo daily OHLCV) and SSO, QLD, UGL (synthetic pre-inception +
    yfinance real post-inception, stitched and dedup'd by date).

    Parameters
    ----------
    canonical_start, canonical_end : str
        The canonical Plano B OOS window boundaries (ISO dates).
        Not used for slicing here — the parquet covers the extended
        window; callers slice themselves.
    extended_start, extended_end : str
        Outer window for synthetic pre-inception synthesis and
        Tiingo loads.
    """
    frames: list[pd.DataFrame] = []

    # ------------------------------------------------------------------
    # 1. Underlying tickers — direct Tiingo OHLCV
    # ------------------------------------------------------------------
    for ticker in UNDERLYING_TICKERS:
        df = _tiingo_ohlcv(ticker, start=extended_start, end=extended_end)
        frames.append(df)

    # ------------------------------------------------------------------
    # 2. LETFs — synthetic pre-inception + yfinance real post-inception
    # ------------------------------------------------------------------
    ffr = _load_ffr_series(extended_start, extended_end)

    for spec in LETF_SPECS:
        underlying_tr = _load_underlying_tr(
            spec.underlying, extended_start, extended_end
        )
        synthetic = _synthetic_pre_inception(spec, underlying_tr, ffr, extended_start)
        real = _real_post_inception(spec.ticker, extended_end)

        # Scale synthetic so its terminal value matches the first real close.
        # This ensures a continuous price path at the inception seam — required
        # because event-driven engines (bt, vectorbt, backtrader) compute max_dd
        # from the equity curve (price × shares), not from daily returns.
        # [advances_fin_ml, p.31-34] — data integrity for cross-lib replication.
        if not synthetic.empty and not real.empty:
            last_synth_close = synthetic["close"].iloc[-1]
            first_real_close = real["close"].iloc[0]
            if last_synth_close > 0:
                scale = first_real_close / last_synth_close
                for col in ("open", "high", "low", "close"):
                    synthetic[col] = synthetic[col] * scale

        combined = pd.concat([synthetic, real], ignore_index=True).sort_values("date")
        combined = combined.drop_duplicates(subset="date", keep="last")
        frames.append(combined)

    full = pd.concat(frames, ignore_index=True)
    full = full.sort_values(["ticker", "date"]).reset_index(drop=True)
    return full


def save_reference_parquet(
    df: pd.DataFrame,
    path: Path = REFERENCE_PARQUET,
) -> None:
    """Persist ``df`` to parquet (pyarrow engine, no index)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(path, index=False, engine="pyarrow")


def load_reference_parquet(path: Path = REFERENCE_PARQUET) -> pd.DataFrame:
    """Load reference_prices.parquet from ``path``."""
    return pd.read_parquet(path, engine="pyarrow")


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------


def _tiingo_ohlcv(ticker: str, start: str, end: str) -> pd.DataFrame:
    """Load Tiingo daily OHLCV for an underlying ticker and reshape to long format."""
    raw = _STORAGE.read(ticker, frequency="daily")
    # Tiingo returns DatetimeIndex; filter to requested window.
    mask = (raw.index >= pd.Timestamp(start)) & (raw.index <= pd.Timestamp(end))
    raw = raw.loc[mask].copy()
    raw = raw.reset_index().rename(columns={"index": "date"})
    # Tiingo columns include adj_close; we keep standard OHLCV only.
    raw["ticker"] = ticker
    return raw[["date", "ticker", "open", "high", "low", "close", "volume"]]


def _synthetic_pre_inception(
    spec: LetfSpec,
    underlying_tr: pd.Series,
    ffr: pd.Series,
    start_date: str,
) -> pd.DataFrame:
    """Build synthetic OHLC for ``spec.ticker`` from ``start_date`` up to (but not
    including) ``spec.inception``.

    Prices start at an arbitrary 10.0; they are rescaled in ``build_reference_prices``
    to match the first real close at inception for seam continuity.
    OHLC is flat: open = high = low = close = synthetic_close.  Volume = 0.

    ``[leverage_for_the_long_run, p.16]`` — daily synthetic return formula.
    """
    end_exclusive = pd.Timestamp(spec.inception) - pd.Timedelta(days=1)
    tr_slice = underlying_tr.loc[
        pd.Timestamp(start_date) : end_exclusive  # noqa: E203
    ]
    if tr_slice.empty:
        # underlying has no history before inception — return empty frame
        return pd.DataFrame(
            columns=["date", "ticker", "open", "high", "low", "close", "volume"]
        )

    ffr_slice = ffr.reindex(tr_slice.index).ffill().bfill()

    synth_rets = synthesize_letf_returns_ffr_aware(
        spx_tr_returns=tr_slice,
        leverage=spec.leverage,
        ffr_annualized=ffr_slice,
        swap_exposure=DEFAULT_SWAP_EXPOSURE,
        ffr_spread=DEFAULT_FFR_SPREAD,
        expense_ratio=spec.expense_ratio,
    ).fillna(0.0)

    prices = (1.0 + synth_rets).cumprod() * 10.0  # arbitrary start value

    return pd.DataFrame(
        {
            "date": prices.index,
            "ticker": spec.ticker,
            "open": prices.values,
            "high": prices.values,
            "low": prices.values,
            "close": prices.values,
            "volume": 0,
        }
    )


def _real_post_inception(ticker: str, end_date: str) -> pd.DataFrame:
    """Fetch real post-inception OHLCV from yfinance for SSO/QLD/UGL.

    SSO, QLD, and UGL are not present in the Tiingo bulk cache, so we
    fall back to yfinance (adjusted prices, split/dividend-corrected).
    yfinance is also used by Stage 2 independent adapters, so this
    introduces no extra dependency.

    Returns long-format DataFrame with ``[date, ticker, open, high, low, close,
    volume]``.
    """
    spec = next(s for s in LETF_SPECS if s.ticker == ticker)
    raw = yf.download(
        ticker,
        start=spec.inception,
        end=end_date,
        progress=False,
        auto_adjust=True,
    )
    if raw.empty:
        return pd.DataFrame(
            columns=["date", "ticker", "open", "high", "low", "close", "volume"]
        )

    # yfinance column handling: guard against MultiIndex vs single-level columns.
    # Some versions/edge cases return single-level; others return MultiIndex tuples.
    # For MultiIndex, prefer level 0 (metric name), fallback to level 1 if level 0 is empty.
    if isinstance(raw.columns, pd.MultiIndex):
        raw.columns = [col[0].lower() if col[0] else col[1].lower() for col in raw.columns]
    else:
        raw.columns = [str(c).lower() for c in raw.columns]

    # Reset index and normalize the date column name (DatetimeIndex is named "Date").
    raw = raw.reset_index()
    raw.columns = [str(c).lower() if isinstance(c, str) else str(c[0]).lower() for c in raw.columns]

    raw["ticker"] = ticker
    return raw[["date", "ticker", "open", "high", "low", "close", "volume"]]


def _load_underlying_tr(underlying: str, start: str, end: str) -> pd.Series:
    """Return a daily total-return decimal series for the underlying index.

    SPY → SPX TR stitched series (Ken French pre-2001 + Tiingo SPY post-2001)
      via ``load_spx_tr_daily``.  Covers 1928+.
      ``[leverage_for_the_long_run, p.13, p.17]``

    QQQ → Tiingo QQQ close pct_change (available from 2001-05-14).
    GLD → Tiingo GLD close pct_change (available from 2004-11-18).

    For QQQ/GLD the synthetic pre-inception window is bounded by the Tiingo
    history start — no synthetic extension before the underlying itself exists.
    """
    if underlying == "SPY":
        return load_spx_tr_daily(
            start=start,
            end=end,
            tiingo_storage_root=str(_TIINGO_ROOT),
        )
    if underlying in ("QQQ", "GLD"):
        raw = _STORAGE.read(underlying, frequency="daily")
        mask = (raw.index >= pd.Timestamp(start)) & (raw.index <= pd.Timestamp(end))
        return raw.loc[mask, "close"].pct_change().dropna()
    raise ValueError(f"Unknown underlying: {underlying!r}")


def _load_ffr_series(start: str, end: str) -> pd.Series:
    """Federal Funds Rate daily series (annualized fraction, e.g. 0.05 = 5%).

    Loaded from ``data/external/ffr.csv`` (FRED series DFF, columns: date, rate).
    Path is driven by AI_TRADE_ROOT env var; default points to main repo.
    If the file is absent, falls back to a flat 3% over a business-day index —
    this is a conservative approximation sufficient for the cross-lib Stage 1
    comparison where absolute CAGR tolerances are ±2 pp.

    FFR-aware cost model: ``[leverage_for_the_long_run, p.16-17]``.
    """
    ffr_path = Path(
        os.environ.get("AI_TRADE_ROOT", "/var/www/pessoal/ai-trade")
    ) / "data" / "external" / "ffr.csv"
    if ffr_path.exists():
        df = pd.read_csv(ffr_path, parse_dates=["date"]).set_index("date")["rate"]
        return df.loc[start:end]
    # Fallback: flat 3% annualized over business days
    idx = pd.date_range(start, end, freq="B")
    return pd.Series(0.03, index=idx, name="ffr_flat_3pct")


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    df = build_reference_prices()
    save_reference_parquet(df)
    print(f"Wrote {len(df)} rows to {REFERENCE_PARQUET}")
    for tkr in ("SPY", "QQQ", "GLD", "SSO", "QLD", "UGL"):
        sub = df[df["ticker"] == tkr]
        if sub.empty:
            print(f"  {tkr}: 0 rows (MISSING)")
        else:
            print(
                f"  {tkr}: {len(sub)} rows, "
                f"{sub['date'].min().date()} → {sub['date'].max().date()}"
            )

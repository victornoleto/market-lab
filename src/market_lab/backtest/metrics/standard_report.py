"""Standard backtest report — ``backtesting.py``-style metrics table + SPY benchmark.

Purpose
-------
Phase 3.5b spec §4.5 requires a single, canonical output table per strategy
and per portfolio. Shape mimics the ``backtesting.py`` ``Stats`` object so a
reader familiar with that library can audit without relearning fields.

Three concerns live here:

1. Trade record dataclass + trade-log rendering with 15% BR capital-gains tax
   applied **per winning trade** (worst-case model; real BR compensates
   losses intra-month).
2. Standard-report dataclass with all §4.5 metrics (duration, exposure,
   returns, risk, drawdown stats, trade stats, Profit Factor, SQN, Kelly).
3. SPY benchmark + strategy-vs-SPY comparison block. SPY is always the base
   of comparison regardless of the traded asset — explicit user rule, see
   ``specs/phase_3_5b_winners_validation.md`` §4.5.

Conventions
-----------
- All rates are annualized with ``periods_per_year`` (default 252 for daily).
- ``equity`` is a ``pd.Series`` indexed by date; ``equity[0]`` is the
  starting capital.
- Drawdown durations use calendar days (``(t_end - t_start).days``). This
  matches backtesting.py behavior on daily bars.
- Sharpe uses population std (``ddof=0``) for consistency with
  ``validation.dsr.sharpe_periodic`` so the printed Sharpe here matches DSR
  input — the convention already used across ``metrics/performance.py``.

References
----------
- van Tharp (1998) — SQN ``sqrt(N) * mean(R) / std(R)``, where ``R`` is the
  per-trade return. Used by ``backtesting.py`` as ``SQN``.
- Kelly (1956) fraction ``W − (1 − W) / RR`` — cited in López de Prado
  (2018) ``[advances_fin_ml, p.220-223]`` for the "bet sizing" chapter.
- Profit Factor, Expectancy — classic definitions, e.g. Chan (2013)
  ``[quantitative_trading, ch.3]``.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

import numpy as np
import pandas as pd

from ai_trade.backtest.metrics._fmt import _fmt_num, _fmt_pct
from ai_trade.backtest.metrics.performance import (
    cagr as _cagr,
    calmar as _calmar,
    max_drawdown as _max_drawdown,
    returns_from_equity,
    sharpe as _sharpe,
    sortino as _sortino,
    volatility as _volatility,
)

DEFAULT_SPY_PARQUET = Path("data/tiingo/daily/prices/SPY.parquet")


# ---------------------------------------------------------------------------
# Trade record
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Trade:
    """A single round-trip trade used for the standard report + trade log.

    ``notional`` is the BRL capital allocated to this trade (defaults to the
    strategy's current equity — callers that size positions should pass the
    actual notional used). ``direction="long"`` means profit when
    ``exit_price > entry_price``; ``"short"`` flips the sign.
    """

    asset: str
    entry_date: pd.Timestamp
    exit_date: pd.Timestamp
    entry_price: float
    exit_price: float
    notional: float = 1.0
    direction: Literal["long", "short"] = "long"

    def __post_init__(self) -> None:
        if self.entry_price <= 0 or self.exit_price <= 0:
            raise ValueError(
                f"entry_price={self.entry_price} exit_price={self.exit_price} "
                "must both be positive"
            )
        if self.exit_date < self.entry_date:
            raise ValueError(
                f"exit_date {self.exit_date} precedes entry_date {self.entry_date}"
            )
        if self.direction not in {"long", "short"}:
            raise ValueError(f"direction must be 'long' or 'short', got {self.direction}")

    @property
    def gross_pnl_pct(self) -> float:
        raw = (self.exit_price - self.entry_price) / self.entry_price
        return raw if self.direction == "long" else -raw

    @property
    def gross_pnl_brl(self) -> float:
        return self.notional * self.gross_pnl_pct

    @property
    def hold_days(self) -> int:
        return (pd.Timestamp(self.exit_date) - pd.Timestamp(self.entry_date)).days

    def tax_brl(self, tax_rate: float = 0.15) -> float:
        """15% BR capital-gains tax — applied only on profitable trades."""
        pnl = self.gross_pnl_brl
        return tax_rate * pnl if pnl > 0 else 0.0

    def net_pnl_brl(self, tax_rate: float = 0.15) -> float:
        return self.gross_pnl_brl - self.tax_brl(tax_rate)


# ---------------------------------------------------------------------------
# Drawdown periods
# ---------------------------------------------------------------------------


def drawdown_periods(equity: pd.Series) -> list[tuple[pd.Timestamp, pd.Timestamp, int]]:
    """Return ``(start_peak, recovery_date, days)`` for each drawdown episode.

    A drawdown starts at the last equity peak before ``equity < peak`` and
    ends on the first date where ``equity >= peak`` again. If the series
    ends still underwater, the final drawdown is recorded with the series'
    last timestamp as its recovery date.
    """
    if len(equity) < 2:
        return []
    peak = equity.cummax()
    below = equity < peak
    periods: list[tuple[pd.Timestamp, pd.Timestamp, int]] = []
    n = len(equity)
    i = 0
    while i < n:
        if not bool(below.iloc[i]):
            i += 1
            continue
        p_val = float(peak.iloc[i])
        # walk back to the last timestamp where equity == this peak value
        j = i - 1
        while j >= 0 and float(equity.iloc[j]) != p_val:
            j -= 1
        start = equity.index[j] if j >= 0 else equity.index[0]
        # walk forward until equity >= p_val (recovery)
        k = i
        while k < n and float(equity.iloc[k]) < p_val:
            k += 1
        end = equity.index[k] if k < n else equity.index[-1]
        days = (pd.Timestamp(end) - pd.Timestamp(start)).days
        periods.append((pd.Timestamp(start), pd.Timestamp(end), days))
        i = max(k, i + 1)
    return periods


# ---------------------------------------------------------------------------
# Trade-level statistics
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class _TradeStats:
    n_trades: int
    win_rate: float
    best_trade_pct: float
    worst_trade_pct: float
    avg_trade_pct: float
    max_hold_days: int
    avg_hold_days: float
    profit_factor: float
    expectancy_pct: float
    sqn: float
    kelly: float


def _trade_stats(trades: list[Trade]) -> _TradeStats:
    """Compute per-trade aggregates. Empty list → zeroes (nothing to print)."""
    if not trades:
        return _TradeStats(
            n_trades=0,
            win_rate=0.0,
            best_trade_pct=0.0,
            worst_trade_pct=0.0,
            avg_trade_pct=0.0,
            max_hold_days=0,
            avg_hold_days=0.0,
            profit_factor=0.0,
            expectancy_pct=0.0,
            sqn=0.0,
            kelly=0.0,
        )
    pcts = np.array([t.gross_pnl_pct for t in trades], dtype=float)
    holds = np.array([t.hold_days for t in trades], dtype=float)
    wins = pcts[pcts > 0]
    losses = pcts[pcts < 0]
    n = len(pcts)

    win_rate = len(wins) / n
    avg_win = float(wins.mean()) if len(wins) else 0.0
    avg_loss = float(losses.mean()) if len(losses) else 0.0  # negative

    gross_win = float(wins.sum())
    gross_loss = float(-losses.sum())  # positive magnitude
    profit_factor = gross_win / gross_loss if gross_loss > 0 else float("inf")

    # Expectancy: average per-trade return.
    expectancy_pct = float(pcts.mean())

    # SQN (van Tharp): sqrt(N) * mean / std of per-trade pnl.
    std = float(pcts.std(ddof=0))
    sqn = float(np.sqrt(n)) * expectancy_pct / std if std > 1e-12 else 0.0

    # Kelly fraction: W − (1 − W) / RR where RR = avg_win / |avg_loss|.
    if avg_loss < 0 and avg_win > 0:
        rr = avg_win / -avg_loss
        kelly = win_rate - (1.0 - win_rate) / rr
    else:
        kelly = 0.0

    return _TradeStats(
        n_trades=n,
        win_rate=win_rate,
        best_trade_pct=float(pcts.max()),
        worst_trade_pct=float(pcts.min()),
        avg_trade_pct=expectancy_pct,
        max_hold_days=int(holds.max()) if n > 0 else 0,
        avg_hold_days=float(holds.mean()),
        profit_factor=profit_factor,
        expectancy_pct=expectancy_pct,
        sqn=sqn,
        kelly=kelly,
    )


# ---------------------------------------------------------------------------
# Standard report dataclass
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class StandardReport:
    """All metrics from spec §4.5. Missing fields printed as zeros."""

    strategy_name: str
    params: str
    start: pd.Timestamp
    end: pd.Timestamp
    duration_days: int
    exposure_time_pct: float
    equity_start: float
    equity_final: float
    equity_peak: float
    return_pct: float
    return_ann_pct: float
    volatility_ann_pct: float
    cagr_pct: float
    sharpe: float
    sortino: float
    calmar: float
    max_drawdown_pct: float
    avg_drawdown_pct: float
    max_drawdown_duration_days: int
    avg_drawdown_duration_days: float
    n_trades: int
    win_rate_pct: float
    best_trade_pct: float
    worst_trade_pct: float
    avg_trade_pct: float
    max_trade_duration_days: int
    avg_trade_duration_days: float
    profit_factor: float
    expectancy_pct: float
    sqn: float
    kelly: float
    equity_curve: pd.Series = field(default_factory=lambda: pd.Series(dtype=float))


@dataclass(frozen=True)
class SpyBenchmark:
    """Minimal SPY buy-and-hold block — §4.5 template only needs four fields."""

    return_pct: float
    cagr_pct: float
    max_drawdown_pct: float
    sharpe: float
    equity_curve: pd.Series = field(default_factory=lambda: pd.Series(dtype=float))


@dataclass(frozen=True)
class SpyComparison:
    excess_return_pct: float
    excess_cagr_pct: float
    delta_max_dd_pct: float
    information_ratio: float
    correlation: float
    beta: float


# ---------------------------------------------------------------------------
# Builders
# ---------------------------------------------------------------------------


def _compute_exposure(equity: pd.Series, trades: list[Trade]) -> float:
    if not trades or len(equity) < 2:
        return 0.0
    idx = equity.index
    bars_in = 0
    for t in trades:
        i0 = int(idx.searchsorted(pd.Timestamp(t.entry_date), side="left"))
        i1 = int(idx.searchsorted(pd.Timestamp(t.exit_date), side="right"))
        bars_in += max(i1 - i0, 0)
    return min(bars_in / len(idx), 1.0)


def build_standard_report(
    *,
    equity: pd.Series,
    trades: list[Trade],
    strategy_name: str,
    params: str = "",
    periods_per_year: int = 252,
) -> StandardReport:
    """Collapse an equity curve + trade list into a §4.5 report dataclass."""
    if len(equity) < 2:
        raise ValueError("equity series must have at least 2 points")
    equity = equity.sort_index()
    rets = returns_from_equity(equity)
    start = pd.Timestamp(equity.index[0])
    end = pd.Timestamp(equity.index[-1])

    v0 = float(equity.iloc[0])
    vT = float(equity.iloc[-1])
    peak = float(equity.cummax().iloc[-1])
    ret_total = (vT - v0) / v0
    years = (end - start).days / 365.25
    ret_ann = (vT / v0) ** (1.0 / years) - 1.0 if years > 0 and v0 > 0 else 0.0

    dd_periods = drawdown_periods(equity)
    dd_durations = [d for _, _, d in dd_periods]
    max_dd_dur = max(dd_durations) if dd_durations else 0
    avg_dd_dur = float(np.mean(dd_durations)) if dd_durations else 0.0

    # Per-drawdown magnitude (peak-to-trough within each episode) for avg DD.
    peak_series = equity.cummax()
    dd_curve = (peak_series - equity) / peak_series
    ep_mags: list[float] = []
    for s, e, _ in dd_periods:
        slice_ = dd_curve.loc[s:e]
        if len(slice_):
            ep_mags.append(float(slice_.max()))
    avg_dd = float(np.mean(ep_mags)) if ep_mags else 0.0

    ts = _trade_stats(trades)

    return StandardReport(
        strategy_name=strategy_name,
        params=params,
        start=start,
        end=end,
        duration_days=(end - start).days,
        exposure_time_pct=_compute_exposure(equity, trades),
        equity_start=v0,
        equity_final=vT,
        equity_peak=peak,
        return_pct=ret_total,
        return_ann_pct=ret_ann,
        volatility_ann_pct=_volatility(rets, periods_per_year),
        cagr_pct=_cagr(equity, periods_per_year),
        sharpe=_sharpe(rets, periods_per_year),
        sortino=_sortino(rets, periods_per_year),
        calmar=_calmar(equity, periods_per_year),
        max_drawdown_pct=_max_drawdown(equity),
        avg_drawdown_pct=avg_dd,
        max_drawdown_duration_days=max_dd_dur,
        avg_drawdown_duration_days=avg_dd_dur,
        n_trades=ts.n_trades,
        win_rate_pct=ts.win_rate,
        best_trade_pct=ts.best_trade_pct,
        worst_trade_pct=ts.worst_trade_pct,
        avg_trade_pct=ts.avg_trade_pct,
        max_trade_duration_days=ts.max_hold_days,
        avg_trade_duration_days=ts.avg_hold_days,
        profit_factor=ts.profit_factor,
        expectancy_pct=ts.expectancy_pct,
        sqn=ts.sqn,
        kelly=ts.kelly,
        equity_curve=equity,
    )


def load_spy_series(path: str | Path = DEFAULT_SPY_PARQUET) -> pd.Series:
    """Load the Tiingo daily SPY adjusted-close series.

    Returns a ``pd.Series`` indexed by date, values = adj_close. The Tiingo
    cache lives at ``data/tiingo/daily/prices/SPY.parquet`` (note: parquet,
    not CSV — the literal path in the spec was outdated).
    """
    df = pd.read_parquet(Path(path))
    if "adj_close" not in df.columns:
        raise KeyError(f"SPY parquet missing adj_close column (got {list(df.columns)})")
    s = df["adj_close"].astype(float)
    s.index = pd.DatetimeIndex(s.index)
    s.name = "SPY"
    return s.sort_index()


def build_spy_benchmark(
    spy_series: pd.Series,
    initial_capital: float,
    window_start: pd.Timestamp | None = None,
    window_end: pd.Timestamp | None = None,
    periods_per_year: int = 252,
) -> SpyBenchmark:
    """Buy-and-hold SPY benchmark aligned to the strategy's time window.

    The strategy window wins — SPY is truncated, not the other way around.
    """
    if initial_capital <= 0:
        raise ValueError(f"initial_capital={initial_capital} must be positive")
    s = spy_series.sort_index()
    if window_start is not None:
        s = s.loc[s.index >= pd.Timestamp(window_start)]
    if window_end is not None:
        s = s.loc[s.index <= pd.Timestamp(window_end)]
    if len(s) < 2:
        raise ValueError(
            f"SPY series has {len(s)} points in [{window_start}, {window_end}] "
            "— need at least 2 for a benchmark"
        )
    equity = initial_capital * s / float(s.iloc[0])
    rets = returns_from_equity(equity)
    return SpyBenchmark(
        return_pct=float(equity.iloc[-1] / equity.iloc[0] - 1.0),
        cagr_pct=_cagr(equity, periods_per_year),
        max_drawdown_pct=_max_drawdown(equity),
        sharpe=_sharpe(rets, periods_per_year),
        equity_curve=equity,
    )


def compare_vs_spy(
    strategy_equity: pd.Series,
    spy_equity: pd.Series,
    periods_per_year: int = 252,
) -> SpyComparison:
    """Strategy-vs-SPY: excess return/CAGR, IR, correlation, beta.

    Both series are inner-joined on date before computing returns, so a
    strategy that trades on a subset of SPY's dates won't bias the metrics.
    """
    strat = strategy_equity.sort_index()
    spy = spy_equity.sort_index()
    joined = pd.concat(
        {"strat": strat, "spy": spy}, axis=1, join="inner"
    ).dropna()
    if len(joined) < 3:
        raise ValueError(
            f"Overlap between strategy ({len(strat)} bars) and SPY "
            f"({len(spy)} bars) has only {len(joined)} shared dates"
        )
    strat_al = joined["strat"]
    spy_al = joined["spy"]

    strat_ret_total = float(strat_al.iloc[-1] / strat_al.iloc[0] - 1.0)
    spy_ret_total = float(spy_al.iloc[-1] / spy_al.iloc[0] - 1.0)

    strat_cagr = _cagr(strat_al, periods_per_year)
    spy_cagr = _cagr(spy_al, periods_per_year)

    strat_dd = _max_drawdown(strat_al)
    spy_dd = _max_drawdown(spy_al)

    strat_rets = returns_from_equity(strat_al)
    spy_rets = returns_from_equity(spy_al)
    excess_rets = strat_rets - spy_rets

    # IR: annualized Sharpe of the excess-return series (rf = 0 since we
    # already subtracted the benchmark).
    ir = _sharpe(excess_rets, periods_per_year)

    # Correlation + beta on the aligned per-period returns.
    if strat_rets.std(ddof=0) < 1e-12 or spy_rets.std(ddof=0) < 1e-12:
        corr = 0.0
        beta = 0.0
    else:
        corr = float(strat_rets.corr(spy_rets))
        var_spy = float(spy_rets.var(ddof=0))
        beta = (
            float(((strat_rets - strat_rets.mean()) * (spy_rets - spy_rets.mean())).mean())
            / var_spy
            if var_spy > 1e-12
            else 0.0
        )

    return SpyComparison(
        excess_return_pct=strat_ret_total - spy_ret_total,
        excess_cagr_pct=strat_cagr - spy_cagr,
        delta_max_dd_pct=strat_dd - spy_dd,
        information_ratio=ir,
        correlation=corr,
        beta=beta,
    )


# ---------------------------------------------------------------------------
# Markdown rendering
# ---------------------------------------------------------------------------


_FIELD_WIDTH = 26


def _row(name: str, value: str) -> str:
    return f"{name:<{_FIELD_WIDTH}}{value}"


def _fmt_days(days: int | float) -> str:
    return f"{int(round(float(days)))} days"


def render_markdown(
    report: StandardReport,
    spy_benchmark: SpyBenchmark | None = None,
    spy_comparison: SpyComparison | None = None,
) -> str:
    """Render the §4.5 plain-text block (wrapped in a fenced code block).

    Returns a complete Markdown document: ``# <name> / ## Metrics / ##
    SPY … / ## Strategy vs SPY``. The metrics block is emitted inside
    triple-backticks so alignment survives Markdown rendering.
    """
    strat = report
    metrics_lines = [
        _row("Start", str(strat.start)),
        _row("End", str(strat.end)),
        _row("Duration", _fmt_days(strat.duration_days)),
        _row("Exposure Time [%]", _fmt_pct(strat.exposure_time_pct)),
        _row("Equity Final [$]", f"{strat.equity_final:,.2f}"),
        _row("Equity Peak [$]", f"{strat.equity_peak:,.2f}"),
        _row("Return [%]", _fmt_pct(strat.return_pct)),
        _row("Return (Ann.) [%]", _fmt_pct(strat.return_ann_pct)),
        _row("Volatility (Ann.) [%]", _fmt_pct(strat.volatility_ann_pct)),
        _row("CAGR [%]", _fmt_pct(strat.cagr_pct)),
        _row("Sharpe Ratio", _fmt_num(strat.sharpe, 3)),
        _row("Sortino Ratio", _fmt_num(strat.sortino, 3)),
        _row("Calmar Ratio", _fmt_num(strat.calmar, 3)),
        _row("Max. Drawdown [%]", _fmt_pct(strat.max_drawdown_pct)),
        _row("Avg. Drawdown [%]", _fmt_pct(strat.avg_drawdown_pct)),
        _row("Max. Drawdown Duration", _fmt_days(strat.max_drawdown_duration_days)),
        _row("Avg. Drawdown Duration", _fmt_days(strat.avg_drawdown_duration_days)),
        _row("# Trades", str(strat.n_trades)),
        _row("Win Rate [%]", _fmt_pct(strat.win_rate_pct)),
        _row("Best Trade [%]", _fmt_pct(strat.best_trade_pct)),
        _row("Worst Trade [%]", _fmt_pct(strat.worst_trade_pct)),
        _row("Avg. Trade [%]", _fmt_pct(strat.avg_trade_pct)),
        _row("Max. Trade Duration", _fmt_days(strat.max_trade_duration_days)),
        _row("Avg. Trade Duration", _fmt_days(strat.avg_trade_duration_days)),
        _row("Profit Factor", _fmt_num(strat.profit_factor, 3)),
        _row("Expectancy [%]", _fmt_pct(strat.expectancy_pct)),
        _row("SQN", _fmt_num(strat.sqn, 3)),
        _row("Kelly Criterion", _fmt_num(strat.kelly, 3)),
        _row("_strategy", strat.params or strat.strategy_name),
    ]

    out = [
        f"# {strat.strategy_name}",
        "",
        "## Metrics",
        "",
        "```",
        *metrics_lines,
        "```",
    ]

    if spy_benchmark is not None:
        spy_lines = [
            _row("SPY Return [%]", _fmt_pct(spy_benchmark.return_pct)),
            _row("SPY CAGR [%]", _fmt_pct(spy_benchmark.cagr_pct)),
            _row("SPY Max. Drawdown [%]", _fmt_pct(spy_benchmark.max_drawdown_pct)),
            _row("SPY Sharpe Ratio", _fmt_num(spy_benchmark.sharpe, 3)),
        ]
        out += [
            "",
            "## SPY Buy & Hold Benchmark (same window, same starting capital)",
            "",
            "```",
            *spy_lines,
            "```",
        ]

    if spy_comparison is not None:
        cmp_ = spy_comparison
        cmp_lines = [
            _row("Excess Return [%]", _fmt_pct(cmp_.excess_return_pct)),
            _row("Excess CAGR [%]", _fmt_pct(cmp_.excess_cagr_pct)),
            _row("Delta Max DD [%]", _fmt_pct(cmp_.delta_max_dd_pct)),
            _row("Information Ratio", _fmt_num(cmp_.information_ratio, 3)),
            _row("Correlation (daily)", _fmt_num(cmp_.correlation, 3)),
            _row("Beta vs SPY", _fmt_num(cmp_.beta, 3)),
        ]
        out += [
            "",
            "## Strategy vs SPY",
            "",
            "```",
            *cmp_lines,
            "```",
        ]

    return "\n".join(out) + "\n"


def render_trade_log(
    trades: list[Trade],
    initial_capital: float,
    tax_rate: float = 0.15,
) -> tuple[str, str]:
    """Return ``(csv_text, markdown_text)`` for the trade log.

    Columns: ``entry_date, entry_price, exit_date, exit_price, hold_days,
    gross_pnl_pct, gross_pnl_brl, tax_brl, net_pnl_brl,
    cumulative_equity_brl``. Tax is applied only when ``gross_pnl_brl > 0``
    (worst-case BR model; losses don't offset future gains).

    The ``cumulative_equity_brl`` column starts at ``initial_capital`` and
    adds the net PnL of each trade — it is NOT compounded per trade. For
    compounded reporting, callers should resize ``notional`` between trades.
    """
    if initial_capital <= 0:
        raise ValueError(f"initial_capital={initial_capital} must be positive")

    rows: list[dict] = []
    running = float(initial_capital)
    # Trades must be processed chronologically for cumulative equity to make sense.
    for t in sorted(trades, key=lambda x: pd.Timestamp(x.exit_date)):
        gross = t.gross_pnl_brl
        tax = t.tax_brl(tax_rate)
        net = gross - tax
        running += net
        rows.append(
            {
                "asset": t.asset,
                "entry_date": pd.Timestamp(t.entry_date).isoformat(),
                "entry_price": t.entry_price,
                "exit_date": pd.Timestamp(t.exit_date).isoformat(),
                "exit_price": t.exit_price,
                "hold_days": t.hold_days,
                "direction": t.direction,
                "notional": t.notional,
                "gross_pnl_pct": t.gross_pnl_pct,
                "gross_pnl_brl": gross,
                "tax_brl": tax,
                "net_pnl_brl": net,
                "cumulative_equity_brl": running,
            }
        )

    df = pd.DataFrame(rows)
    if df.empty:
        csv_text = (
            "asset,entry_date,entry_price,exit_date,exit_price,hold_days,"
            "direction,notional,gross_pnl_pct,gross_pnl_brl,tax_brl,"
            "net_pnl_brl,cumulative_equity_brl\n"
        )
        md_text = "_No trades._\n"
        return csv_text, md_text

    csv_text = df.to_csv(index=False)

    md_df = df.copy()
    md_df["entry_price"] = md_df["entry_price"].map(lambda x: f"{x:,.4f}")
    md_df["exit_price"] = md_df["exit_price"].map(lambda x: f"{x:,.4f}")
    md_df["notional"] = md_df["notional"].map(lambda x: f"{x:,.2f}")
    md_df["gross_pnl_pct"] = md_df["gross_pnl_pct"].map(lambda x: f"{x * 100:.2f}%")
    md_df["gross_pnl_brl"] = md_df["gross_pnl_brl"].map(lambda x: f"{x:,.2f}")
    md_df["tax_brl"] = md_df["tax_brl"].map(lambda x: f"{x:,.2f}")
    md_df["net_pnl_brl"] = md_df["net_pnl_brl"].map(lambda x: f"{x:,.2f}")
    md_df["cumulative_equity_brl"] = md_df["cumulative_equity_brl"].map(
        lambda x: f"{x:,.2f}"
    )

    from ai_trade.backtest.metrics._fmt import _dataframe_to_markdown

    md_text = _dataframe_to_markdown(md_df) + "\n"
    return csv_text, md_text


__all__ = [
    "DEFAULT_SPY_PARQUET",
    "SpyBenchmark",
    "SpyComparison",
    "StandardReport",
    "Trade",
    "build_spy_benchmark",
    "build_standard_report",
    "compare_vs_spy",
    "drawdown_periods",
    "load_spy_series",
    "render_markdown",
    "render_trade_log",
]

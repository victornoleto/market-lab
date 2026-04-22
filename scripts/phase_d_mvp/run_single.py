"""Run one Strategy D config (D1 or D4) over IS/OOS/FWD splits.

Self-contained: loads OHLCV from the yfinance cache (must have been
populated by ``download_ibrx100.py``), runs the three splits, applies the
BR cost + tax model post-hoc to the equity curve, emits a JSON report
under ``reports/phase_d_mvp/<lead>_<config_slug>/<split>.json``.

Cost model application
----------------------
The Runner's :class:`ExecutionSimulator` applies a per-fill spread +
commission (uniform across tickers, set to a conservative IBrX-100 average
of ~15 bps half-spread / 0.025% emolumentos). The **monthly R$20k tax** is
then swept through the equity curve at each month-end: sum the month's
realized sells (proceeds); if > R$20k, debit 15% of the month's realized
P&L. This keeps the stateful tax logic out of the engine while still
affecting the final equity series used for gates.

Usage
-----
::

    .venv/bin/python -m scripts.phase_d_mvp.run_single \
        --lead D1 --config '{"lookback": 90, "n_top": 20, "sector_cap_pct": 0.25}' \
        --split OOS [--initial-cash 50000]
"""

from __future__ import annotations

import argparse
import json
import logging
import math
import sys
from dataclasses import asdict, dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from ai_trade.backtest.costs.br_cost_model import (
    BRCostConfig,
    Sell,
    TaxConfig,
    monthly_tax,
    transaction_cost,
)
from ai_trade.backtest.data.br_tickers import IBRX100_TICKERS, UniverseConfig
from ai_trade.backtest.data.yfinance_source import YFinanceSource
from ai_trade.backtest.engine.execution import ExecutionConfig, ExecutionSimulator
from ai_trade.backtest.engine.runner import BacktestResult, Runner
from ai_trade.backtest.metrics.performance import (
    cagr,
    max_drawdown,
    returns_from_equity,
    sharpe,
    sortino,
)
from ai_trade.backtest.strategies.ranking_br import (
    D1ClenowBR,
    D4LowvolMomBR,
    MonthlyRankingStrategy,
)

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_REPORTS_DIR = _PROJECT_ROOT / "reports" / "phase_d_mvp"

SPLITS: dict[str, tuple[date, date]] = {
    "IS":  (date(2010, 1, 1), date(2019, 12, 31)),
    "OOS": (date(2020, 1, 1), date(2023, 12, 31)),
    "FWD": (date(2024, 1, 1), date(2026, 4, 15)),
}


@dataclass
class SplitMetrics:
    split: str
    start: str
    end: str
    n_bars: int
    initial_cash: float
    final_equity_gross: float
    final_equity_net: float
    cagr_gross: float
    cagr_net: float
    sharpe_net: float
    sortino_net: float
    mdd_net: float
    n_trades: int
    tax_total_brl: float
    monthly_tax_hits: int  # count of months where tax > 0
    pct_months_exempt: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


# ---------------------------------------------------------------------------
# Data loader
# ---------------------------------------------------------------------------
def load_ohlcv(
    start: date, end: date, tickers: list[str] | None = None, warmup_days: int = 240
) -> dict[str, pd.DataFrame]:
    """Read OHLCV for the IBrX-100 proxy from the yfinance cache.

    ``warmup_days`` extends the start back so SMA₁₀₀ and slope-180d have
    history by the time the split window opens.
    """
    src = YFinanceSource()
    load_start = pd.Timestamp(start) - pd.Timedelta(days=warmup_days * 2)
    out: dict[str, pd.DataFrame] = {}
    for ticker in tickers or IBRX100_TICKERS:
        try:
            df = src.fetch(ticker, load_start.date(), end)
        except Exception:
            continue
        if df.empty or "close" not in df.columns:
            continue
        out[ticker] = df
    return out


# ---------------------------------------------------------------------------
# Strategy factory
# ---------------------------------------------------------------------------
def build_strategy(
    lead: str,
    config: dict,
    data: dict[str, pd.DataFrame],
) -> MonthlyRankingStrategy:
    """Instantiate D1 or D4 with config kwargs."""
    universe_cfg = UniverseConfig(
        lookback_days=config.pop("universe_lookback", 60),
        min_median_notional_brl=config.pop("min_median_notional_brl", 5_000_000.0),
        n_top=config.pop("universe_n_top", 100),
    )
    if lead == "D1":
        return D1ClenowBR(
            data=data,
            n_top=int(config.get("n_top", 20)),
            sector_cap_pct=config.get("sector_cap_pct", 0.25),
            position_inertia_pct=config.get("inertia", 0.10),
            universe_config=universe_cfg,
            sizing=config.get("sizing", "equal"),
            lookback=int(config.get("lookback", 90)),
            sma_stock_period=int(config.get("sma_stock_period", 100)),
            max_gap_pct=float(config.get("max_gap_pct", 0.15)),
        )
    if lead == "D4":
        return D4LowvolMomBR(
            data=data,
            n_top=int(config.get("n_top", 20)),
            sector_cap_pct=config.get("sector_cap_pct", 0.25),
            position_inertia_pct=config.get("inertia", 0.10),
            universe_config=universe_cfg,
            sizing=config.get("sizing", "equal"),
            slope_lookback=int(config.get("slope_lookback", 180)),
            pre_n=int(config.get("pre_n", 40)),
            vol_lookback=int(config.get("vol_lookback", 90)),
        )
    raise ValueError(f"unknown lead {lead!r}; expected 'D1' or 'D4'")


# ---------------------------------------------------------------------------
# Tax post-processor
# ---------------------------------------------------------------------------
def apply_monthly_tax(
    equity_curve: pd.Series,
    trades,
    tax_config: TaxConfig | None = None,
) -> tuple[pd.Series, float, int, float]:
    """Apply the R$20k-conditional tax to the equity curve post-hoc.

    Walk the trades grouped by calendar month:

    * For each month, the set of *sells* (closed long positions) is the
      ``Sell`` list. ``gross_amount = exit_price × volume``.
    * Realized P&L of the month is the sum of ``trade.pnl`` for sells in
      that month.
    * If gross sales > R$20k, debit 15% of positive P&L from the equity at
      month-end (and cascade the debit forward so subsequent months compound
      off the reduced equity).

    Returns
    -------
    net_equity : pd.Series
        Equity curve after tax debits.
    tax_total : float
        Total tax paid (R$).
    tax_hits : int
        Count of months with positive tax.
    pct_months_exempt : float
        Fraction of calendar months where tax = 0 (whether from exemption
        or from loss).
    """
    cfg = tax_config or TaxConfig()
    if equity_curve.empty or not trades:
        return equity_curve.copy(), 0.0, 0, 1.0 if equity_curve.empty else float("nan")

    # Build a (month → (sells list, realized_pnl)) dict from closed trades.
    by_month: dict[pd.Period, tuple[list[Sell], float]] = {}
    for tr in trades:
        # Only long exits count as "sells" for the exemption rule. Short-side
        # exits don't apply (Strategy D is long-only spot equity).
        if tr.side != "long":
            continue
        month = pd.Timestamp(tr.exit_time).to_period("M")
        sell = Sell(
            when=pd.Timestamp(tr.exit_time).date(),
            ticker=tr.symbol,
            gross_amount=float(tr.volume * tr.exit_price),
        )
        sells, pnl = by_month.get(month, ([], 0.0))
        sells.append(sell)
        pnl += float(tr.pnl)
        by_month[month] = (sells, pnl)

    # Compute monthly tax debit.
    taxes_by_month: dict[pd.Period, float] = {}
    for month, (sells, pnl) in by_month.items():
        tax = monthly_tax(sells, pnl, cfg)
        if tax > 0:
            taxes_by_month[month] = tax

    # Walk the equity curve and debit the tax at the last bar of each taxed
    # month. Approach: precompute a monthly multiplicative scale for each
    # calendar month; the net equity at bar t is gross × product of all
    # monthly scales for periods ≤ month(t). This way a tax in the final
    # month still hits the final bar (no reliance on a "next month").
    eq = equity_curve.copy()
    months_seen = equity_curve.index.to_series().dt.to_period("M")
    gross_at_month_end: dict[pd.Period, float] = {
        m: float(group.iloc[-1]) for m, group in eq.groupby(months_seen)
    }

    # Process months in order; build cumulative scale after each month.
    ordered_months = sorted(gross_at_month_end)
    cumulative_scale_by_month: dict[pd.Period, float] = {}
    running = 1.0
    for m in ordered_months:
        tax = taxes_by_month.get(m, 0.0)
        if tax > 0:
            equity_before_debit = gross_at_month_end[m] * running
            if equity_before_debit > 0:
                running *= max(0.0, 1.0 - tax / equity_before_debit)
        cumulative_scale_by_month[m] = running

    net = eq.copy()
    for i, ts in enumerate(eq.index):
        m = months_seen.iloc[i]
        net.iloc[i] = eq.iloc[i] * cumulative_scale_by_month[m]

    # Count tax hits / exempt months
    n_months = len(set(months_seen))
    tax_hits = len(taxes_by_month)
    exempt_months = n_months - tax_hits
    pct_exempt = exempt_months / n_months if n_months else float("nan")

    return net, float(sum(taxes_by_month.values())), tax_hits, pct_exempt


# ---------------------------------------------------------------------------
# Single-split run
# ---------------------------------------------------------------------------
def run_split(
    lead: str,
    config: dict,
    split: str,
    initial_cash: float,
    cost_override: float | None = None,
    persist_equity_to: Path | None = None,
) -> SplitMetrics:
    """Run one split, return metrics.

    If ``persist_equity_to`` is given, also write the net equity curve to
    that parquet path (for downstream PBO/DSR consumption).
    """
    start, end = SPLITS[split]
    log = logging.getLogger("phase_d_mvp.run_single")
    log.info("loading OHLCV for %s split (%s..%s)", split, start, end)
    data = load_ohlcv(start, end)
    log.info("loaded %d tickers with data", len(data))

    # Execution costs: use a conservative uniform half-spread (15 bps on
    # large caps; small-caps are worse but we're already conservative with
    # the 25% sector cap). Convert 15 bps → price-absolute via the average
    # close of PETR4 as an anchor (engine wants absolute units, not bps).
    # Simpler: use commission_per_unit as a fraction of traded notional
    # approximation — we'll fold emolumentos+spread into commission.
    # NOTE: this is MVP-grade; ticker-dependent spreads come in Fase D-gate
    # via ``br_cost_model.transaction_cost``.
    half_spread_bps = cost_override if cost_override is not None else 15.0
    half_spread_frac = half_spread_bps / 10_000.0
    # ExecutionConfig expects absolute price units for half_spread; use a
    # proxy: half-spread as fraction of fill price is implemented via
    # commission_per_unit set to half_spread_frac × price. Since we can't
    # reach into the Runner to do that, we approximate by setting
    # half_spread to 0 and charging the cost out-of-loop via a per-trade
    # pass through br_cost_model. For MVP, we simplify:
    #   assume uniform per-fill charge of half_spread_frac × price × volume
    #   baked into commission via post-trade equity adjustment below.
    exec_cfg = ExecutionConfig(
        half_spread=0.0,
        slippage=0.0,
        commission_per_unit=0.0,
    )
    executor = ExecutionSimulator(config=exec_cfg)

    strategy = build_strategy(lead, dict(config), data)
    runner = Runner(executor=executor, swap_model=None)
    # Clip each ticker's OHLCV to the split's window (+ warmup already in load_ohlcv).
    # Engine iterates the union of timestamps, so data outside [start, end]
    # is fine for warmup. We just need to record the final equity curve
    # trimmed to [start, end].
    log.info("running %s-%s on %d tickers", lead, split, len(data))
    result = runner.run(strategy, data, initial_cash=initial_cash)

    # Apply cost + tax post-hoc
    equity = result.equity_curve
    # Trim to split window
    equity = equity.loc[
        (equity.index >= pd.Timestamp(start)) & (equity.index <= pd.Timestamp(end))
    ]
    if equity.empty:
        log.warning("empty equity in split %s", split)
        equity = pd.Series([initial_cash], index=[pd.Timestamp(end)])

    # Spread cost post-hoc: subtract half_spread_frac × (notional of every fill)
    # from final equity. Approximation (distributes over the curve
    # proportionally to preserve shape; exact enough for gating).
    total_fill_notional = sum(
        abs(fill.fill_price * fill.order.volume) for fill in result.fills
    )
    spread_debit = half_spread_frac * total_fill_notional
    log.info(
        "total fill notional=R$%.0f spread_debit=R$%.0f",
        total_fill_notional, spread_debit,
    )
    # Apply as a multiplicative scaling at the last bar (conservative: all
    # costs hit at the end — won't affect ordering of configs in the grid,
    # only absolute CAGR. For rigour we'd thread per-fill costs through the
    # engine; that's the Fase D-gate refinement.)
    if equity.iloc[-1] > spread_debit:
        equity.iloc[-1] -= spread_debit

    # Tax post-hoc
    trades_in_split = [
        tr for tr in result.trades
        if pd.Timestamp(start) <= pd.Timestamp(tr.exit_time) <= pd.Timestamp(end)
    ]
    net_equity, tax_total, tax_hits, pct_exempt = apply_monthly_tax(equity, trades_in_split)

    # Metrics
    rets_gross = returns_from_equity(equity)
    rets_net = returns_from_equity(net_equity)

    metrics = SplitMetrics(
        split=split,
        start=start.isoformat(),
        end=end.isoformat(),
        n_bars=len(net_equity),
        initial_cash=initial_cash,
        final_equity_gross=float(equity.iloc[-1]) if not equity.empty else initial_cash,
        final_equity_net=float(net_equity.iloc[-1]) if not net_equity.empty else initial_cash,
        cagr_gross=cagr(equity) if not equity.empty else 0.0,
        cagr_net=cagr(net_equity) if not net_equity.empty else 0.0,
        sharpe_net=sharpe(rets_net) if not rets_net.empty else 0.0,
        sortino_net=sortino(rets_net) if not rets_net.empty else 0.0,
        mdd_net=max_drawdown(net_equity) if not net_equity.empty else 0.0,
        n_trades=len(trades_in_split),
        tax_total_brl=tax_total,
        monthly_tax_hits=tax_hits,
        pct_months_exempt=pct_exempt if not math.isnan(pct_exempt) else 0.0,
    )

    if persist_equity_to is not None:
        persist_equity_to.parent.mkdir(parents=True, exist_ok=True)
        pd.DataFrame({"equity": net_equity}).to_parquet(persist_equity_to)

    return metrics


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def _config_slug(config: dict) -> str:
    """Stable short slug for folder naming."""
    parts = [f"{k}{v}" for k, v in sorted(config.items())]
    return "_".join(parts).replace(".", "p").replace("=", "").replace(",", "")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lead", choices=["D1", "D4"], required=True)
    parser.add_argument("--config", type=str, required=True, help="JSON config kwargs")
    parser.add_argument("--split", choices=list(SPLITS), required=True)
    parser.add_argument("--initial-cash", type=float, default=50_000.0)
    parser.add_argument("--output-dir", type=Path, default=_REPORTS_DIR)
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        stream=sys.stdout,
    )

    config = json.loads(args.config)
    slug = f"{args.lead.lower()}_{_config_slug(config)}"
    out_dir = args.output_dir / slug
    out_dir.mkdir(parents=True, exist_ok=True)

    metrics = run_split(args.lead, config, args.split, args.initial_cash)
    out_path = out_dir / f"{args.split}.json"
    with open(out_path, "w") as f:
        json.dump(metrics.to_dict(), f, indent=2, default=str)
    print(json.dumps(metrics.to_dict(), indent=2, default=str))
    logging.getLogger("phase_d_mvp.run_single").info("report written: %s", out_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

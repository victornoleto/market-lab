"""Fast per-config backtest with PRELOADED OHLCV (no I/O in hot loop).

Addresses the Phase D-MVP bottleneck: ``phase_d_mvp.run_single.run_split``
called ``load_ohlcv`` every invocation, re-reading ~100 parquet files
per run × 126 runs = 12,600 disk reads total. Phase E loads once in the
orchestrator and passes the dict to every config.

Other optimizations vs phase_d:

* ``build_strategy`` skips universe_config.n_top keyword pop (phase_d
  mutated the config dict as side-effect).
* Trades list is not re-filtered here — the Runner already limits the
  equity curve to the split window via the timestamp union.

Exposes:

* :class:`SplitMetricsE` — same shape as phase_d.SplitMetrics but with
  per-market tax fields.
* :func:`run_config_split` — one config, one split, returning metrics +
  equity series. Pure function (no disk writes unless caller passes
  ``persist_equity_to``).
"""

from __future__ import annotations

import logging
import math
from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from ai_trade.backtest.costs.br_cost_model import (
    BRCostConfig,
    Sell,
    TaxConfig,
)
from ai_trade.backtest.data.br_tickers import UniverseConfig
from ai_trade.backtest.engine.execution import ExecutionConfig, ExecutionSimulator
from ai_trade.backtest.engine.runner import Runner
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
from scripts.phase_e_mvp.cost_model import (
    USCostConfig,
    USTaxConfig,
    monthly_tax_multimarket,
    transaction_cost,
)
from scripts.phase_e_mvp.universe import market_of

log = logging.getLogger(__name__)


SPLITS: dict[str, tuple[date, date]] = {
    "IS":  (date(2010, 1, 1), date(2019, 12, 31)),
    "OOS": (date(2020, 1, 1), date(2023, 12, 31)),
    "FWD": (date(2024, 1, 1), date(2026, 4, 15)),
}


@dataclass
class SplitMetricsE:
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
    n_trades_br: int
    n_trades_us: int
    tax_total_brl: float
    monthly_tax_hits: int
    pct_months_exempt_br: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def build_strategy_e(
    lead: str, config: dict, data: dict[str, pd.DataFrame]
) -> MonthlyRankingStrategy:
    """Instantiate D1/D4 (reused unchanged from Strategy D). The subclass
    doesn't care about market — the universe is determined by
    ``data`` + ``UniverseConfig``.
    """
    cfg = dict(config)  # don't mutate caller's config
    universe_cfg = UniverseConfig(
        lookback_days=cfg.pop("universe_lookback", 60),
        min_median_notional_brl=cfg.pop("min_median_notional_brl", 5_000_000.0),
        n_top=cfg.pop("universe_n_top", 300),
    )
    common = dict(
        data=data,
        n_top=int(cfg.get("n_top", 20)),
        sector_cap_pct=cfg.get("sector_cap_pct", 0.25),
        position_inertia_pct=cfg.get("inertia", 0.10),
        universe_config=universe_cfg,
        sizing=cfg.get("sizing", "equal"),
    )
    if lead == "D1":
        return D1ClenowBR(
            **common,
            lookback=int(cfg.get("lookback", 90)),
            sma_stock_period=int(cfg.get("sma_stock_period", 100)),
            max_gap_pct=float(cfg.get("max_gap_pct", 0.15)),
        )
    if lead == "D4":
        return D4LowvolMomBR(
            **common,
            slope_lookback=int(cfg.get("slope_lookback", 180)),
            pre_n=int(cfg.get("pre_n", 40)),
            vol_lookback=int(cfg.get("vol_lookback", 90)),
        )
    raise ValueError(f"unknown lead {lead!r}")


def _split_trades_by_market(trades: list) -> tuple[list, list]:
    """Split long-exit trades into (BR, US) groups."""
    br, us = [], []
    for tr in trades:
        if getattr(tr, "side", None) != "long":
            continue
        mkt = market_of(tr.symbol)
        if mkt == "BR":
            br.append(tr)
        elif mkt == "US":
            us.append(tr)
    return br, us


def apply_multimarket_tax(
    equity_curve: pd.Series, trades: list
) -> tuple[pd.Series, float, int, float]:
    """Apply monthly multi-market tax to the equity curve.

    BR sells checked against R$20k exemption; US sells always 15% DARF.
    Multiplicative scale per month cascades debits forward (same pattern
    as ``phase_d_mvp.run_single.apply_monthly_tax``).
    """
    if equity_curve.empty or not trades:
        return equity_curve.copy(), 0.0, 0, 1.0 if equity_curve.empty else float("nan")

    br_by_month: dict[pd.Period, tuple[list[Sell], float]] = {}
    us_pnl_by_month: dict[pd.Period, float] = {}

    for tr in trades:
        if getattr(tr, "side", None) != "long":
            continue
        month = pd.Timestamp(tr.exit_time).to_period("M")
        mkt = market_of(tr.symbol)
        pnl = float(tr.pnl)
        gross = float(tr.volume * tr.exit_price)
        if mkt == "BR":
            sells, acc = br_by_month.get(month, ([], 0.0))
            sells.append(Sell(
                when=pd.Timestamp(tr.exit_time).date(),
                ticker=tr.symbol,
                gross_amount=gross,
            ))
            br_by_month[month] = (sells, acc + pnl)
        else:
            us_pnl_by_month[month] = us_pnl_by_month.get(month, 0.0) + pnl

    all_months = set(br_by_month) | set(us_pnl_by_month)
    taxes_by_month: dict[pd.Period, float] = {}
    for m in all_months:
        br_sells, br_pnl = br_by_month.get(m, ([], 0.0))
        us_pnl = us_pnl_by_month.get(m, 0.0)
        tax = monthly_tax_multimarket(br_sells, br_pnl, us_pnl)
        if tax > 0:
            taxes_by_month[m] = tax

    # Multiplicative scale per month
    months_seen = equity_curve.index.to_series().dt.to_period("M")
    gross_at_month_end: dict[pd.Period, float] = {
        m: float(group.iloc[-1])
        for m, group in equity_curve.groupby(months_seen)
    }

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

    net = equity_curve.copy()
    for i in range(len(equity_curve)):
        m = months_seen.iloc[i]
        net.iloc[i] = equity_curve.iloc[i] * cumulative_scale_by_month[m]

    # Exemption stat: BR-only (US never exempt)
    br_months = len(set(br_by_month))
    br_tax_hits = sum(1 for m in br_by_month
                      if monthly_tax_multimarket(*br_by_month[m], us_pnl=0.0) > 0)
    pct_exempt = ((br_months - br_tax_hits) / br_months) if br_months else float("nan")

    return net, float(sum(taxes_by_month.values())), len(taxes_by_month), pct_exempt


def run_config_split(
    lead: str,
    config: dict,
    split: str,
    data: dict[str, pd.DataFrame],
    initial_cash: float,
    persist_equity_to: Path | None = None,
    half_spread_bps: float = 8.0,  # weighted-avg US 3 bps + BR 15 bps
) -> SplitMetricsE:
    """Run one config on one split using PRELOADED ``data`` dict.

    No disk I/O on the hot path (aside from optional ``persist_equity_to``).
    """
    start, end = SPLITS[split]

    exec_cfg = ExecutionConfig(
        half_spread=0.0, slippage=0.0, commission_per_unit=0.0,
    )
    executor = ExecutionSimulator(config=exec_cfg)
    strategy = build_strategy_e(lead, config, data)
    runner = Runner(executor=executor, swap_model=None)
    result = runner.run(strategy, data, initial_cash=initial_cash)

    equity = result.equity_curve
    equity = equity.loc[
        (equity.index >= pd.Timestamp(start)) & (equity.index <= pd.Timestamp(end))
    ]
    if equity.empty:
        equity = pd.Series([initial_cash], index=[pd.Timestamp(end)])

    # Spread cost post-hoc (uniform approximation — refine in Fase E-gate)
    half_spread_frac = half_spread_bps / 10_000.0 / 2.0
    total_notional = sum(
        abs(f.fill_price * f.order.volume) for f in result.fills
    )
    spread_debit = half_spread_frac * total_notional
    if equity.iloc[-1] > spread_debit:
        equity.iloc[-1] = equity.iloc[-1] - spread_debit

    trades_in_split = [
        tr for tr in result.trades
        if pd.Timestamp(start) <= pd.Timestamp(tr.exit_time) <= pd.Timestamp(end)
    ]
    net_equity, tax_total, tax_hits, pct_exempt_br = apply_multimarket_tax(
        equity, trades_in_split,
    )

    br_trades, us_trades = _split_trades_by_market(trades_in_split)
    rets_net = returns_from_equity(net_equity)

    metrics = SplitMetricsE(
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
        n_trades_br=len(br_trades),
        n_trades_us=len(us_trades),
        tax_total_brl=tax_total,
        monthly_tax_hits=tax_hits,
        pct_months_exempt_br=pct_exempt_br if not math.isnan(pct_exempt_br) else 0.0,
    )

    if persist_equity_to is not None:
        persist_equity_to.parent.mkdir(parents=True, exist_ok=True)
        pd.DataFrame({"equity": net_equity}).to_parquet(persist_equity_to)

    return metrics


__all__ = [
    "SPLITS",
    "SplitMetricsE",
    "apply_multimarket_tax",
    "build_strategy_e",
    "run_config_split",
]

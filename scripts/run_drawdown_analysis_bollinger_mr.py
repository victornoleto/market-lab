#!/usr/bin/env python3
"""Drawdown & losing streak analysis for Bollinger MR best config.

Identifies the worst drawdown periods, analyzes WHEN the strategy loses,
and computes losing streak statistics. This is production-readiness item #11:
the user needs to know what to expect in live trading.

Config: window=20, std_mult=1.5, stop_pct=0.02, max_hold=24 on SPY 1h 2021-2025.

Citations:
- Drawdown analysis for strategy assessment: [advances_fin_ml, p.208-211, ch.12].
- Mean-reversion entry logic: [algo_trading_chan, p.28-30, ch.2].
- Time-stop / risk control: [machine_trading, p.126, ch.4].
"""

from __future__ import annotations

import sys
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd


def find_drawdown_periods(equity: pd.Series, top_n: int = 5) -> list[dict]:
    """Identify the top N drawdown periods (peak-to-trough).

    Returns list of dicts with: peak_date, trough_date, recovery_date,
    peak_equity, trough_equity, dd_pct, duration_bars, recovery_bars.
    """
    peak = equity.cummax()
    dd = (equity - peak) / peak

    # Find all drawdown segments (contiguous periods below prior peak).
    in_dd = dd < 0
    segments: list[dict] = []
    seg_start = None

    for i, (ts, is_dd) in enumerate(in_dd.items()):
        if is_dd and seg_start is None:
            seg_start = i
        elif not is_dd and seg_start is not None:
            # End of drawdown segment — recovery at index i.
            seg_dd = dd.iloc[seg_start:i]
            trough_idx = seg_dd.idxmin()
            trough_pos = equity.index.get_loc(trough_idx)
            peak_ts = equity.index[seg_start - 1] if seg_start > 0 else equity.index[0]
            segments.append({
                "peak_date": peak_ts,
                "trough_date": trough_idx,
                "recovery_date": ts,
                "peak_equity": float(equity.iloc[seg_start - 1]) if seg_start > 0 else float(equity.iloc[0]),
                "trough_equity": float(equity.loc[trough_idx]),
                "dd_pct": float(seg_dd.min()),
                "duration_bars": trough_pos - seg_start + 1,
                "recovery_bars": i - seg_start,
            })
            seg_start = None

    # Handle ongoing drawdown at end of series.
    if seg_start is not None:
        seg_dd = dd.iloc[seg_start:]
        trough_idx = seg_dd.idxmin()
        trough_pos = equity.index.get_loc(trough_idx)
        peak_ts = equity.index[seg_start - 1] if seg_start > 0 else equity.index[0]
        segments.append({
            "peak_date": peak_ts,
            "trough_date": trough_idx,
            "recovery_date": None,
            "peak_equity": float(equity.iloc[seg_start - 1]) if seg_start > 0 else float(equity.iloc[0]),
            "trough_equity": float(equity.loc[trough_idx]),
            "dd_pct": float(seg_dd.min()),
            "duration_bars": trough_pos - seg_start + 1,
            "recovery_bars": None,
        })

    # Sort by severity and take top N.
    segments.sort(key=lambda s: s["dd_pct"])
    return segments[:top_n]


def analyze_losing_streaks(trades: list) -> dict:
    """Compute losing streak statistics from trade list."""
    if not trades:
        return {}

    pnls = [t.pnl for t in trades]
    wins = sum(1 for p in pnls if p > 0)
    losses = sum(1 for p in pnls if p <= 0)

    # Consecutive losing streaks.
    streaks: list[int] = []
    current_streak = 0
    for p in pnls:
        if p <= 0:
            current_streak += 1
        else:
            if current_streak > 0:
                streaks.append(current_streak)
            current_streak = 0
    if current_streak > 0:
        streaks.append(current_streak)

    # Consecutive winning streaks.
    win_streaks: list[int] = []
    current_win = 0
    for p in pnls:
        if p > 0:
            current_win += 1
        else:
            if current_win > 0:
                win_streaks.append(current_win)
            current_win = 0
    if current_win > 0:
        win_streaks.append(current_win)

    return {
        "total_trades": len(pnls),
        "wins": wins,
        "losses": losses,
        "win_rate": wins / len(pnls),
        "avg_win": float(np.mean([p for p in pnls if p > 0])) if wins else 0,
        "avg_loss": float(np.mean([p for p in pnls if p <= 0])) if losses else 0,
        "max_win": float(max(pnls)),
        "max_loss": float(min(pnls)),
        "max_losing_streak": max(streaks) if streaks else 0,
        "avg_losing_streak": float(np.mean(streaks)) if streaks else 0,
        "max_winning_streak": max(win_streaks) if win_streaks else 0,
        "avg_winning_streak": float(np.mean(win_streaks)) if win_streaks else 0,
        "profit_factor": (
            abs(sum(p for p in pnls if p > 0) / sum(p for p in pnls if p <= 0))
            if losses else float("inf")
        ),
    }


def trades_during_period(trades: list, start: pd.Timestamp, end: pd.Timestamp) -> list:
    """Filter trades that overlap with a date range."""
    return [
        t for t in trades
        if t.entry_time <= end and t.exit_time >= start
    ]


def monthly_returns(equity: pd.Series) -> pd.Series:
    """Compute monthly returns from hourly equity curve."""
    # Resample to last value per month.
    monthly_eq = equity.resample("ME").last().dropna()
    return monthly_eq.pct_change().dropna()


def main() -> int:
    from ai_trade.backtest.data.tiingo_source import TiingoSource
    from ai_trade.backtest.data.tiingo_storage import TiingoStorage
    from ai_trade.backtest.engine import (
        BacktestResult,
        ExecutionConfig,
        ExecutionSimulator,
        Runner,
    )
    from ai_trade.backtest.strategies.bollinger_mr import BollingerMRStrategy

    symbol = "SPY"
    start = date(2021, 1, 1)
    end = date(2025, 12, 31)
    cash = 100_000.0
    warmup_days = 100
    periods_per_year = 252 * 7  # 1h bars

    # Fixed best config from gate-passing Iteration 2.
    window, std_mult, stop_pct, max_hold = 20, 1.5, 0.02, 24

    # Fetch data.
    fetch_start = start - timedelta(days=warmup_days)
    print(f"Fetching {symbol} 1h: {fetch_start} → {end}")
    src = TiingoSource(storage=TiingoStorage(root=Path("data/tiingo")))
    raw = src.fetch_many(
        [symbol], fetch_start, end, asset_class="etf", frequency="1hour",
    )
    if symbol not in raw or raw[symbol].empty:
        print(f"ERROR: No data for {symbol}")
        return 1

    data_full = {symbol: raw[symbol]}
    data_bounded = {
        symbol: raw[symbol].loc[pd.Timestamp(start):pd.Timestamp(end)]
    }
    n_bars = len(data_bounded[symbol])
    print(f"Data: {n_bars} bars in [{start}, {end}]")
    print(f"Config: w={window}, std={std_mult}, stop={stop_pct}, max_hold={max_hold}")

    # Run backtest (zero cost — drawdown analysis focuses on signal quality).
    exec_cfg = ExecutionConfig(half_spread=0.0, slippage=0.0, commission_per_unit=0.0)
    strategy = BollingerMRStrategy(
        data=data_full,
        symbol=symbol,
        window=window,
        std_mult=std_mult,
        stop_pct=stop_pct,
        max_hold=max_hold,
        risk_pct_of_equity=0.95,
    )
    runner = Runner(executor=ExecutionSimulator(exec_cfg))
    bt: BacktestResult = runner.run(
        strategy=strategy, data=data_bounded, initial_cash=cash,
    )

    eq = bt.equity_curve
    trades = bt.trades

    # ====================================================================
    # 1. OVERALL TRADE STATISTICS
    # ====================================================================
    print("\n" + "=" * 80)
    print("BOLLINGER MR SPY 1h — DRAWDOWN & STRESS ANALYSIS")
    print("=" * 80)

    stats = analyze_losing_streaks(trades)
    print("\n--- Trade Statistics ---")
    print(f"Total trades:           {stats['total_trades']}")
    print(f"Wins / Losses:          {stats['wins']} / {stats['losses']}")
    print(f"Win rate:               {stats['win_rate']*100:.1f}%")
    print(f"Avg win:                ${stats['avg_win']:,.2f}")
    print(f"Avg loss:               ${stats['avg_loss']:,.2f}")
    print(f"Max single win:         ${stats['max_win']:,.2f}")
    print(f"Max single loss:        ${stats['max_loss']:,.2f}")
    print(f"Profit factor:          {stats['profit_factor']:.2f}")
    print(f"Max losing streak:      {stats['max_losing_streak']} trades")
    print(f"Avg losing streak:      {stats['avg_losing_streak']:.1f} trades")
    print(f"Max winning streak:     {stats['max_winning_streak']} trades")
    print(f"Avg winning streak:     {stats['avg_winning_streak']:.1f} trades")

    # Avg hold time.
    hold_bars = [(t.exit_time - t.entry_time).total_seconds() / 3600 for t in trades]
    print(f"\nAvg hold time:          {np.mean(hold_bars):.1f} hours")
    print(f"Median hold time:       {np.median(hold_bars):.1f} hours")
    print(f"Max hold time:          {max(hold_bars):.1f} hours")

    # ====================================================================
    # 2. TOP 5 DRAWDOWN PERIODS
    # ====================================================================
    print("\n--- Top 5 Drawdown Periods ---")
    dd_periods = find_drawdown_periods(eq, top_n=5)

    for i, dd in enumerate(dd_periods, 1):
        print(f"\n  #{i}: {dd['dd_pct']*100:.2f}% drawdown")
        print(f"      Peak:     {dd['peak_date']} (equity ${dd['peak_equity']:,.0f})")
        print(f"      Trough:   {dd['trough_date']} (equity ${dd['trough_equity']:,.0f})")
        if dd['recovery_date'] is not None:
            print(f"      Recovery: {dd['recovery_date']}")
            recovery_days = (dd['recovery_date'] - dd['peak_date']).days
            print(f"      Duration: {recovery_days} calendar days peak-to-recovery")
        else:
            print(f"      Recovery: ONGOING (not recovered by end of data)")
        print(f"      Peak→trough: {dd['duration_bars']} bars")

        # Find trades during this drawdown.
        dd_trades = trades_during_period(
            trades, dd['peak_date'], dd['trough_date'],
        )
        if dd_trades:
            dd_pnl = sum(t.pnl for t in dd_trades)
            dd_wins = sum(1 for t in dd_trades if t.pnl > 0)
            dd_losses = sum(1 for t in dd_trades if t.pnl <= 0)
            print(f"      Trades during DD: {len(dd_trades)} ({dd_wins}W/{dd_losses}L, P&L ${dd_pnl:,.2f})")

            # Show each trade in this DD period.
            for t in dd_trades:
                marker = "W" if t.pnl > 0 else "L"
                hold_h = (t.exit_time - t.entry_time).total_seconds() / 3600
                print(f"        [{marker}] {t.entry_time.strftime('%Y-%m-%d %H:%M')} → "
                      f"{t.exit_time.strftime('%Y-%m-%d %H:%M')} "
                      f"(hold {hold_h:.0f}h) P&L ${t.pnl:,.2f}")

    # ====================================================================
    # 3. MONTHLY RETURNS DISTRIBUTION
    # ====================================================================
    print("\n--- Monthly Returns ---")
    mret = monthly_returns(eq)
    neg_months = (mret < 0).sum()
    total_months = len(mret)
    print(f"Total months:           {total_months}")
    print(f"Positive months:        {total_months - neg_months} ({(total_months - neg_months)/total_months*100:.0f}%)")
    print(f"Negative months:        {neg_months} ({neg_months/total_months*100:.0f}%)")
    print(f"Best month:             {mret.max()*100:+.2f}%")
    print(f"Worst month:            {mret.min()*100:+.2f}%")
    print(f"Mean monthly return:    {mret.mean()*100:+.2f}%")
    print(f"Median monthly return:  {mret.median()*100:+.2f}%")
    print(f"Monthly return std:     {mret.std()*100:.2f}%")

    # Worst months detail.
    print("\n  5 Worst Months:")
    worst = mret.nsmallest(5)
    for ts, ret in worst.items():
        # Count trades in that month.
        month_start = ts.replace(day=1)
        month_end = ts
        mt = trades_during_period(trades, pd.Timestamp(month_start), pd.Timestamp(month_end))
        print(f"    {ts.strftime('%Y-%m')}: {ret*100:+.2f}% ({len(mt)} trades)")

    # ====================================================================
    # 4. YEARLY BREAKDOWN
    # ====================================================================
    print("\n--- Yearly Breakdown ---")
    yearly_eq = eq.resample("YE").last().dropna()
    prev = cash
    for ts, val in yearly_eq.items():
        yr_ret = (val - prev) / prev
        yr_trades = [t for t in trades if t.entry_time.year == ts.year]
        yr_wins = sum(1 for t in yr_trades if t.pnl > 0)
        yr_losses = sum(1 for t in yr_trades if t.pnl <= 0)
        yr_pnl = sum(t.pnl for t in yr_trades)

        # Yearly max DD.
        yr_mask = (eq.index >= pd.Timestamp(f"{ts.year}-01-01")) & (eq.index <= ts)
        yr_eq = eq[yr_mask]
        yr_peak = yr_eq.cummax()
        yr_dd = ((yr_eq - yr_peak) / yr_peak).min()

        print(f"  {ts.year}: return {yr_ret*100:+.2f}%, "
              f"MaxDD {yr_dd*100:.2f}%, "
              f"trades {len(yr_trades)} ({yr_wins}W/{yr_losses}L), "
              f"P&L ${yr_pnl:,.0f}")
        prev = val

    # ====================================================================
    # 5. EXIT REASON ANALYSIS
    # ====================================================================
    # We can infer exit reasons from hold time and P&L:
    # - Stop-loss: pnl ≈ -(entry_price * volume * stop_pct)
    # - MA reversion: pnl > 0, hold < max_hold bars
    # - Time-stop: hold ≈ max_hold bars (24h)
    print("\n--- Exit Reason Estimation ---")
    stop_loss_count = 0
    ma_revert_count = 0
    time_stop_count = 0
    stop_loss_pnl = 0.0
    ma_revert_pnl = 0.0
    time_stop_pnl = 0.0

    for t in trades:
        hold_h = (t.exit_time - t.entry_time).total_seconds() / 3600
        ret_pct = (t.exit_price - t.entry_price) / t.entry_price

        if ret_pct <= -stop_pct * 0.8:  # near stop level
            stop_loss_count += 1
            stop_loss_pnl += t.pnl
        elif hold_h >= max_hold - 1:  # near or at max_hold
            time_stop_count += 1
            time_stop_pnl += t.pnl
        else:
            ma_revert_count += 1
            ma_revert_pnl += t.pnl

    total = len(trades)
    print(f"  MA reversion (target): {ma_revert_count} ({ma_revert_count/total*100:.0f}%) — P&L ${ma_revert_pnl:,.0f}")
    print(f"  Stop-loss:             {stop_loss_count} ({stop_loss_count/total*100:.0f}%) — P&L ${stop_loss_pnl:,.0f}")
    print(f"  Time-stop:             {time_stop_count} ({time_stop_count/total*100:.0f}%) — P&L ${time_stop_pnl:,.0f}")

    # ====================================================================
    # 6. WHEN DOES THE STRATEGY LOSE?
    # ====================================================================
    print("\n--- When Does the Strategy Lose? ---")

    # Get SPY price data for context.
    spy_close = data_bounded[symbol]["close"]

    # Compute 20-day rolling return of SPY (trend context).
    spy_daily = spy_close.resample("D").last().dropna()
    spy_20d_ret = spy_daily.pct_change(20)

    # For each losing trade, check market context.
    losing_trades = [t for t in trades if t.pnl <= 0]
    losing_in_downtrend = 0
    losing_in_uptrend = 0
    losing_in_flat = 0

    for t in losing_trades:
        # Get SPY 20d return at entry time.
        entry_date = t.entry_time.normalize()
        mask = spy_20d_ret.index <= entry_date
        if mask.any():
            recent_ret = spy_20d_ret[mask].iloc[-1]
            if np.isnan(recent_ret):
                continue
            if recent_ret < -0.03:  # >3% decline in 20 days
                losing_in_downtrend += 1
            elif recent_ret > 0.03:  # >3% rise in 20 days
                losing_in_uptrend += 1
            else:
                losing_in_flat += 1

    total_losing = len(losing_trades)
    if total_losing > 0:
        print(f"  Losses during SPY downtrend (20d ret < -3%):  {losing_in_downtrend} ({losing_in_downtrend/total_losing*100:.0f}%)")
        print(f"  Losses during SPY uptrend (20d ret > +3%):    {losing_in_uptrend} ({losing_in_uptrend/total_losing*100:.0f}%)")
        print(f"  Losses during flat market (|20d ret| ≤ 3%):   {losing_in_flat} ({losing_in_flat/total_losing*100:.0f}%)")

    # Day-of-week analysis.
    print("\n  Day-of-week performance:")
    dow_names = ["Mon", "Tue", "Wed", "Thu", "Fri"]
    for dow in range(5):
        dow_trades = [t for t in trades if t.entry_time.dayofweek == dow]
        if dow_trades:
            dow_pnl = sum(t.pnl for t in dow_trades)
            dow_wins = sum(1 for t in dow_trades if t.pnl > 0)
            dow_wr = dow_wins / len(dow_trades) * 100
            print(f"    {dow_names[dow]}: {len(dow_trades)} trades, "
                  f"{dow_wr:.0f}% WR, P&L ${dow_pnl:,.0f}")

    # Hour-of-day analysis for entries.
    print("\n  Entry hour distribution (top 5):")
    hour_counts: dict[int, list] = {}
    for t in trades:
        h = t.entry_time.hour
        hour_counts.setdefault(h, []).append(t)
    sorted_hours = sorted(hour_counts.items(), key=lambda x: len(x[1]), reverse=True)
    for h, h_trades in sorted_hours[:5]:
        h_wr = sum(1 for t in h_trades if t.pnl > 0) / len(h_trades) * 100
        h_pnl = sum(t.pnl for t in h_trades)
        print(f"    {h:02d}:00 — {len(h_trades)} trades, {h_wr:.0f}% WR, P&L ${h_pnl:,.0f}")

    print("\n" + "=" * 80)
    print("END OF DRAWDOWN ANALYSIS")
    print("=" * 80)

    return 0


if __name__ == "__main__":
    sys.exit(main())

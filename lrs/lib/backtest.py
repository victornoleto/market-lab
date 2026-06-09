from __future__ import annotations

from dataclasses import dataclass
import math
from pathlib import Path

import numpy as np
import pandas as pd

from market_lab.backtest.data.testfolio_loader import load_testfolio_frame
from studies._shared.tax_engine import AnnualDarfEngine


TRADING_DAYS = 252
INITIAL_CAPITAL = 10_000.0
HORIZON_YEARS = [3, 5, 10, 15, 20]
HIT_TOLERANCE = 1e-10


@dataclass(frozen=True)
class Metrics:
    start: str
    end: str
    years: float
    cagr: float
    mdd: float
    sharpe: float
    sortino: float
    calmar: float
    terminal: float


def fmt_pct(value: float, digits: int = 2) -> str:
    if pd.isna(value):
        return "n/a"
    return f"{100.0 * value:.{digits}f}%"


def fmt_pp(value: float, digits: int = 2) -> str:
    if pd.isna(value):
        return "n/a"
    sign = "+" if value >= 0 else ""
    return f"{sign}{100.0 * value:.{digits}f}pp"


def fmt_num(value: float, digits: int = 3) -> str:
    if pd.isna(value):
        return "n/a"
    return f"{value:.{digits}f}"


def fmt_x(value: float, digits: int = 2) -> str:
    if pd.isna(value):
        return "n/a"
    return f"{value:.{digits}f}x"


def md_table(rows: list[dict[str, object]], columns: list[str]) -> str:
    if not rows:
        return "_No rows._\n"
    header = "| " + " | ".join(columns) + " |"
    sep = "|" + "|".join("---" for _ in columns) + "|"
    body = [
        "| " + " | ".join(str(row.get(col, "")) for col in columns) + " |"
        for row in rows
    ]
    return "\n".join([header, sep, *body]) + "\n"


def load_price_frame(required_assets: list[str]) -> pd.DataFrame:
    frame = load_testfolio_frame()
    missing = [asset for asset in required_assets if asset not in frame.columns]
    if missing:
        raise KeyError(f"missing Testfol.io assets: {missing}")
    return frame[required_assets].dropna().astype(float)


def first_weekly_bar_mask(index: pd.DatetimeIndex) -> pd.Series:
    periods = index.to_period("W")
    values = np.r_[True, periods[1:].to_numpy() != periods[:-1].to_numpy()]
    return pd.Series(values, index=index)


def clean_weights(weights: dict[str, float]) -> dict[str, float]:
    return {asset: float(weight) for asset, weight in weights.items() if float(weight) > 1e-10}


def weights_equal(left: dict[str, float], right: dict[str, float]) -> bool:
    keys = set(left) | set(right)
    return all(abs(left.get(key, 0.0) - right.get(key, 0.0)) <= 1e-10 for key in keys)


def weights_label(weights: dict[str, float]) -> str:
    cleaned = clean_weights(weights)
    if not cleaned:
        return "none"
    return " / ".join(
        f"{weight * 100:.0f} {asset.replace('SIM', '')}" for asset, weight in cleaned.items()
    )


def build_sma_signal(prices: pd.Series, lookback: int = 200) -> pd.Series:
    """Lagged SMA regime signal, avoiding same-close lookahead.

    The original LRS rule is risk-on when price closes above its moving average
    `[leverage_for_the_long_run, p.13]`. The one-bar shift ensures execution
    only uses information known at the previous close `[testing_tuning,
    p.327-335]`.
    """

    sma = prices.rolling(lookback).mean()
    signal = prices.shift(1) > sma.shift(1)
    return signal.fillna(False).astype(bool)


def build_weekly_lrs_weights(
    index: pd.DatetimeIndex,
    signal: pd.Series,
    risk_on_weights: dict[str, float],
    risk_off_weights: dict[str, float],
    lag_days: int,
    cash_asset: str = "CASHX",
) -> tuple[pd.DataFrame, dict[str, float]]:
    """Create daily weights from weekly LRS state updates.

    If state changes and lag_days > 0, the old sleeve is liquidated into CASHX
    and the new sleeve is entered after lag_days daily return bars. This models
    settlement/operational delay without assuming margin availability.
    """

    signal = signal.reindex(index).fillna(False).astype(bool)
    assets = sorted(set(risk_on_weights) | set(risk_off_weights) | {cash_asset})
    desired = pd.DataFrame(0.0, index=index, columns=assets)
    for asset in assets:
        desired[asset] = np.where(
            signal,
            risk_on_weights.get(asset, 0.0),
            risk_off_weights.get(asset, 0.0),
        )
    return build_weekly_lagged_weights(
        desired,
        lag_days=lag_days,
        cash_asset=cash_asset,
        risk_on_weights=risk_on_weights,
    )


def build_weekly_lagged_weights(
    desired_weights: pd.DataFrame,
    lag_days: int,
    cash_asset: str = "CASHX",
    risk_on_weights: dict[str, float] | None = None,
) -> tuple[pd.DataFrame, dict[str, float]]:
    """Convert daily desired targets into executable weekly weights.

    Desired targets are sampled only on the first trading day of each week. Any
    target change is routed through cash for ``lag_days`` daily bars, modeling
    broker settlement/operational delay. This generalizes the baseline LRS rule
    to dynamic risk-off targets while preserving the same execution convention
    `[testing_tuning, p.327-335]`.
    """

    if lag_days < 0:
        raise ValueError("lag_days must be non-negative")

    index = pd.DatetimeIndex(desired_weights.index)
    assets = sorted(set(desired_weights.columns) | {cash_asset})
    desired_weights = desired_weights.reindex(index=index, columns=assets).fillna(0.0)
    weekly_mask = first_weekly_bar_mask(index)
    cash_weights = {cash_asset: 1.0}

    current = clean_weights(desired_weights.iloc[0].to_dict())
    pending: dict[str, float] | None = None
    remaining_delay = 0
    active_target = current.copy()
    state_changes = 0
    delayed_entries = 0
    risk_on_days = 0
    rows: list[dict[str, float]] = []

    for date in index:
        if pending is not None and remaining_delay <= 0:
            current = pending
            active_target = pending
            pending = None

        if bool(weekly_mask.loc[date]):
            desired = clean_weights(desired_weights.loc[date].to_dict())
            if not weights_equal(desired, active_target):
                state_changes += 1
                active_target = desired
                if lag_days == 0:
                    current = desired
                    pending = None
                    remaining_delay = 0
                else:
                    current = cash_weights.copy()
                    pending = desired
                    remaining_delay = lag_days
                    delayed_entries += 1

        rows.append({asset: current.get(asset, 0.0) for asset in assets})
        if risk_on_weights is not None and weights_equal(current, risk_on_weights):
            risk_on_days += 1

        if pending is not None and remaining_delay > 0:
            remaining_delay -= 1

    frame = pd.DataFrame(rows, index=index, columns=assets).fillna(0.0)
    summary = {
        "state_changes": float(state_changes),
        "delayed_entries": float(delayed_entries),
        "pct_risk_on_days": float(risk_on_days / len(index)) if len(index) else math.nan,
        "weekly_events": float(weekly_mask.sum()),
    }
    return frame, summary


def constant_weight_frame(index: pd.DatetimeIndex, weights: dict[str, float]) -> pd.DataFrame:
    columns = sorted(clean_weights(weights)) or ["CASHX"]
    frame = pd.DataFrame(0.0, index=index, columns=columns)
    for asset, weight in clean_weights(weights).items():
        frame[asset] = weight
    return frame


def dict_from_weight_array(columns: list[str], weights: np.ndarray) -> dict[str, float]:
    return {asset: float(weight) for asset, weight in zip(columns, weights) if float(weight) > 1e-10}


def simulate_weight_frame(
    asset_returns: pd.DataFrame,
    target_weights: pd.DataFrame,
    taxable: bool,
    force_rebalance_mask: pd.Series | None = None,
) -> tuple[pd.Series, dict[str, float]]:
    """Simulate a daily target-weight frame, rebalancing on target changes.

    ``force_rebalance_mask`` (optional): dates marked True rebalance back to the
    target even if it is unchanged, so a constant-weight frame can express a
    periodically rebalanced static portfolio with its turnover taxed by the
    engine. Default ``None`` preserves the original change-only behavior.
    """
    columns = sorted(set(target_weights.columns) | set(asset_returns.columns))
    returns = asset_returns.reindex(index=target_weights.index, columns=columns).fillna(0.0)
    targets = target_weights.reindex(index=returns.index, columns=columns).fillna(0.0)
    force_arr = (
        force_rebalance_mask.reindex(returns.index).fillna(False).to_numpy(dtype=bool)
        if force_rebalance_mask is not None
        else None
    )

    returns_arr = returns.to_numpy(dtype=np.float64)
    target_arr = targets.to_numpy(dtype=np.float64)
    current_arr = target_arr[0].copy()
    current_arr = current_arr / current_arr.sum() if current_arr.sum() > 0 else current_arr
    values = current_arr * INITIAL_CAPITAL
    engine = AnnualDarfEngine(initial_investment=INITIAL_CAPITAL) if taxable else None

    out: list[float] = []
    total_turnover = 0.0
    trade_count = 0
    final_liquidation_recorded = False
    previous_target: np.ndarray | None = None
    dates = returns.index

    for i, date in enumerate(dates):
        target = target_arr[i]
        target = target / target.sum() if target.sum() > 0 else target
        equity_pre = float(values.sum())
        current_weights = values / equity_pre if equity_pre > 0 else np.zeros_like(values)

        target_changed = (
            previous_target is None
            or (force_arr is not None and bool(force_arr[i]))
            or not np.allclose(target, previous_target, atol=1e-10)
        )
        if target_changed:
            turnover = 0.5 * float(np.abs(target - current_weights).sum())
            if turnover > 1e-8:
                total_turnover += turnover
                trade_count += 1
                if engine is not None:
                    engine.record_trade(
                        date,
                        dict_from_weight_array(columns, current_weights),
                        dict_from_weight_array(columns, target),
                    )
            values = equity_pre * target
            previous_target = target.copy()

        before = float(engine.port_value if engine is not None else values.sum())
        values = values * (1.0 + returns_arr[i])
        after_pre_tax = float(values.sum())
        gross_ret = after_pre_tax / equity_pre - 1.0 if equity_pre > 0 else 0.0

        if engine is None:
            daily_ret = gross_ret
        else:
            engine.apply_return(after_pre_tax / before - 1.0 if before > 0 else 0.0)
            next_date = dates[i + 1] if i + 1 < len(dates) else None
            is_last = next_date is None
            if is_last and not final_liquidation_recorded:
                final_weights = values / after_pre_tax if after_pre_tax > 0 else np.zeros_like(values)
                engine.record_trade(date, dict_from_weight_array(columns, final_weights), {})
                final_liquidation_recorded = True
            if is_last or pd.Timestamp(next_date).year != pd.Timestamp(date).year:
                engine.year_end_settlement(pd.Timestamp(date).year, force=is_last)
                if after_pre_tax > 0:
                    values *= engine.port_value / after_pre_tax
            daily_ret = engine.port_value / before - 1.0 if before > 0 else 0.0
        out.append(float(daily_ret))

    summary = {
        "turnover_per_year": float(total_turnover / (len(dates) / TRADING_DAYS)),
        "trade_count": float(trade_count),
        "total_tax_paid_pct_initial": 0.0,
        "tax_events": 0.0,
    }
    if engine is not None:
        summary["total_tax_paid_pct_initial"] = float(engine.total_darf_paid / INITIAL_CAPITAL)
        summary["tax_events"] = float(sum(1 for event in engine.events if event.get("darf", 0.0) > 0.0))
    return pd.Series(out, index=dates, name="taxed" if taxable else "gross"), summary


def metrics_from_returns(returns: pd.Series, periods_per_year: int = TRADING_DAYS) -> Metrics:
    clean = returns.dropna().astype(float)
    if clean.empty:
        return Metrics("n/a", "n/a", math.nan, math.nan, math.nan, math.nan, math.nan, math.nan, math.nan)
    equity = (1.0 + clean).cumprod()
    years = len(clean) / periods_per_year
    drawdown = equity / equity.cummax() - 1.0
    vol = clean.std(ddof=0)
    downside = clean[clean < 0.0].std(ddof=0)
    cagr = equity.iloc[-1] ** (1.0 / years) - 1.0 if years > 0 else math.nan
    mdd = float(drawdown.min())
    return Metrics(
        start=str(clean.index[0].date()),
        end=str(clean.index[-1].date()),
        years=float(years),
        cagr=float(cagr),
        mdd=mdd,
        sharpe=float(clean.mean() / vol * math.sqrt(periods_per_year)) if vol and vol > 0 else math.nan,
        sortino=float(clean.mean() / downside * math.sqrt(periods_per_year)) if downside and downside > 0 else math.nan,
        calmar=float(cagr / abs(mdd)) if mdd < 0 else math.nan,
        terminal=float(equity.iloc[-1]),
    )


def equity_curve(returns: pd.Series) -> pd.Series:
    return (1.0 + returns.dropna().astype(float)).cumprod()


def rolling_relative_stats(portfolio_returns: pd.Series, benchmark_returns: pd.Series) -> dict[str, float]:
    aligned = pd.concat({"portfolio": portfolio_returns, "benchmark": benchmark_returns}, axis=1).dropna()
    peq = equity_curve(aligned["portfolio"]).to_numpy(dtype=np.float64)
    beq = equity_curve(aligned["benchmark"]).to_numpy(dtype=np.float64)
    out: dict[str, float] = {}
    n = len(aligned)
    for horizon in HORIZON_YEARS:
        days = horizon * TRADING_DAYS
        if n <= days:
            continue
        pprev = np.concatenate([[1.0], peq[: n - days]])
        bprev = np.concatenate([[1.0], beq[: n - days]])
        pend = peq[days - 1 :]
        bend = beq[days - 1 :]
        relative = (pend / pprev) / (bend / bprev) - 1.0
        relative[np.abs(relative) <= HIT_TOLERANCE] = 0.0
        out[f"hit_{horizon}y"] = float((relative > HIT_TOLERANCE).mean())
        out[f"p10_{horizon}y"] = float(np.quantile(relative, 0.10))
        out[f"median_{horizon}y"] = float(np.quantile(relative, 0.50))
        out[f"min_{horizon}y"] = float(relative.min())
        out[f"latest_{horizon}y"] = float(relative[-1])
    return out


def relative_stats(portfolio_returns: pd.Series, benchmark_returns: pd.Series) -> dict[str, float]:
    aligned = pd.concat({"portfolio": portfolio_returns, "benchmark": benchmark_returns}, axis=1).dropna()
    portfolio_equity = equity_curve(aligned["portfolio"])
    benchmark_equity = equity_curve(aligned["benchmark"])
    relative = portfolio_equity / benchmark_equity
    rel_drawdown = relative / relative.cummax() - 1.0
    return {
        "terminal_vs_benchmark": float(relative.iloc[-1]),
        "min_relative_equity": float(relative.min()),
        "worst_relative_drawdown": float(rel_drawdown.min()),
        **rolling_relative_stats(aligned["portfolio"], aligned["benchmark"]),
    }

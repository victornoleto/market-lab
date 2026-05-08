"""Trial + grid containers + safe serialization (parquet + JSON).

A :class:`TrialResult` bundles a strategy-parameter config (any frozen
``@dataclass``) with the :class:`BacktestResult` it produced. Scalar
metrics (Sharpe, CAGR, max DD) are cached so gate evaluation doesn't
re-compute them per trial.

A :class:`GridResult` stacks trials and exposes ``returns_matrix`` (T, N)
— the input format :func:`market_lab.backtest.validation.pbo.pbo` expects.
Error trials are excluded from the matrix.

The config type is generic (``ConfigT``) — ``TrialResult`` and
``GridResult`` don't know or care what strategy they were built for.
``trial_to_dir`` serialises ``config.__dict__`` (works for any frozen
dataclass); ``trial_from_dir`` takes ``config_cls`` to rebuild the
correct type.

Checkpoint layout for crash-resume:

    {checkpoint_dir}/trial_{id}/
        equity.parquet   — BacktestResult.equity_curve as a one-column frame
        trades.parquet   — BacktestResult.trades flattened to rows
        fills.parquet    — BacktestResult.fills flattened (order fields inlined)
        meta.json        — config dict + scalar metrics + status + error_msg
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Generic, TypeVar

import numpy as np
import pandas as pd

from market_lab.backtest.engine.execution import Fill, Order
from market_lab.backtest.engine.portfolio import Trade
from market_lab.backtest.engine.runner import BacktestResult
from market_lab.backtest.grid.bollinger_mr_config import BollingerMRGridConfig


ConfigT = TypeVar("ConfigT")


@dataclass
class TrialResult(Generic[ConfigT]):
    """One grid cell's outcome.

    ``result`` is ``None`` iff ``status == "error"`` (the backtest crashed or
    the strategy refused to run — e.g. insufficient warmup data). Error
    trials are persisted so the diagnostic layer can report *which* configs
    died, but they don't contribute to PBO/DSR matrices.
    """

    config_id: int
    config: ConfigT
    result: BacktestResult | None
    sharpe: float
    cagr: float
    max_drawdown: float
    status: str                     # "ok" | "error"
    error_msg: str | None = None


@dataclass
class GridResult(Generic[ConfigT]):
    """Collection of trials for one grid run."""

    trials: list[TrialResult[ConfigT]]
    run_id: str

    @property
    def configs(self) -> list[ConfigT]:
        return [t.config for t in self.trials]

    @property
    def ok_trials(self) -> list[TrialResult]:
        """Trials that completed successfully (have a BacktestResult)."""
        return [t for t in self.trials if t.status == "ok" and t.result is not None]

    @property
    def returns_matrix(self) -> np.ndarray:
        """(T, N) matrix of aligned daily returns — excludes error trials.

        Configs with larger lookbacks start trading later, so the equity
        curves have different DatetimeIndexes. We intersect indices and
        compute ``pct_change`` on the aligned slice. The result is ready
        to feed :func:`market_lab.backtest.validation.pbo.pbo`.
        """
        ok = self.ok_trials
        if not ok:
            return np.empty((0, 0), dtype=float)
        curves = [t.result.equity_curve for t in ok]
        return _align_returns(curves)


def _align_returns(equity_curves: list[pd.Series]) -> np.ndarray:
    """Align a list of equity Series on their DatetimeIndex intersection
    and return a (T, N) matrix of daily returns without NaN.

    Configs with different lookbacks produce curves that don't share endpoints.
    Taking the intersection drops the warmup-only rows and guarantees every
    column has a price at every retained timestamp. ``pct_change`` introduces
    one NaN at the top; we drop that row so the matrix is clean.
    """
    if not equity_curves:
        raise ValueError("equity_curves must be non-empty")

    indexes = [eq.index for eq in equity_curves]
    common = indexes[0]
    for idx in indexes[1:]:
        common = common.intersection(idx)
    if len(common) == 0:
        return np.zeros((0, len(equity_curves)), dtype=float)

    aligned = np.column_stack(
        [eq.reindex(common).ffill().to_numpy(dtype=float) for eq in equity_curves]
    )
    rets = np.diff(aligned, axis=0) / aligned[:-1, :]
    return rets


def _trade_to_row(trade: Trade) -> dict:
    return {
        "symbol": trade.symbol,
        "side": trade.side,
        "volume": float(trade.volume),
        "entry_price": float(trade.entry_price),
        "exit_price": float(trade.exit_price),
        "entry_time": trade.entry_time,
        "exit_time": trade.exit_time,
        "pnl": float(trade.pnl),
    }


def _fill_to_row(fill: Fill) -> dict:
    return {
        "order_symbol": fill.order.symbol,
        "order_side": fill.order.side,
        "order_volume": float(fill.order.volume),
        "order_kind": fill.order.kind,
        "fill_price": float(fill.fill_price),
        "fill_time": fill.fill_time,
        "commission": float(fill.commission),
        "slippage_cost": float(fill.slippage_cost),
    }


def _row_to_trade(row: pd.Series) -> Trade:
    return Trade(
        symbol=str(row["symbol"]),
        side=str(row["side"]),
        volume=float(row["volume"]),
        entry_price=float(row["entry_price"]),
        exit_price=float(row["exit_price"]),
        entry_time=pd.Timestamp(row["entry_time"]),
        exit_time=pd.Timestamp(row["exit_time"]),
        pnl=float(row["pnl"]),
    )


def _row_to_fill(row: pd.Series) -> Fill:
    order = Order(
        symbol=str(row["order_symbol"]),
        side=str(row["order_side"]),
        volume=float(row["order_volume"]),
        kind=str(row["order_kind"]),
    )
    return Fill(
        order=order,
        fill_price=float(row["fill_price"]),
        fill_time=pd.Timestamp(row["fill_time"]),
        commission=float(row["commission"]),
        slippage_cost=float(row["slippage_cost"]),
    )


_TRADE_COLUMNS = [
    "symbol", "side", "volume", "entry_price", "exit_price",
    "entry_time", "exit_time", "pnl",
]
_FILL_COLUMNS = [
    "order_symbol", "order_side", "order_volume", "order_kind",
    "fill_price", "fill_time", "commission", "slippage_cost",
]


def trial_to_dir(trial: TrialResult, directory: Path) -> None:
    """Persist a TrialResult to ``directory`` as parquet + JSON."""
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)

    meta = {
        "config_id": trial.config_id,
        "config": trial.config.__dict__,
        "sharpe": _json_safe(trial.sharpe),
        "cagr": _json_safe(trial.cagr),
        "max_drawdown": _json_safe(trial.max_drawdown),
        "status": trial.status,
        "error_msg": trial.error_msg,
    }
    if trial.result is not None:
        meta["initial_cash"] = float(trial.result.initial_cash)
        meta["final_equity"] = float(trial.result.final_equity)

    (directory / "meta.json").write_text(json.dumps(meta, default=str, indent=2))

    if trial.result is not None:
        eq_df = trial.result.equity_curve.to_frame(name="equity")
        eq_df.to_parquet(directory / "equity.parquet")

        trades_df = pd.DataFrame(
            [_trade_to_row(t) for t in trial.result.trades], columns=_TRADE_COLUMNS,
        )
        trades_df.to_parquet(directory / "trades.parquet", index=False)

        fills_df = pd.DataFrame(
            [_fill_to_row(f) for f in trial.result.fills], columns=_FILL_COLUMNS,
        )
        fills_df.to_parquet(directory / "fills.parquet", index=False)
    else:
        pd.DataFrame(columns=["equity"]).to_parquet(directory / "equity.parquet")
        pd.DataFrame(columns=_TRADE_COLUMNS).to_parquet(
            directory / "trades.parquet", index=False,
        )
        pd.DataFrame(columns=_FILL_COLUMNS).to_parquet(
            directory / "fills.parquet", index=False,
        )


def trial_from_dir(
    directory: Path,
    config_cls: type[ConfigT] = BollingerMRGridConfig,  # type: ignore[assignment]
) -> TrialResult[Any]:
    """Reconstruct a TrialResult from ``directory``.

    Parameters
    ----------
    directory : Path
        Path to the ``trial_{id}/`` directory.
    config_cls : type, optional
        Dataclass to rebuild the config with. Defaults to
        :class:`BollingerMRGridConfig` (the surviving Path A winner config
        after the 2026-04-16 cleanup); pass any other frozen dataclass for
        new strategies.
    """
    directory = Path(directory)
    meta = json.loads((directory / "meta.json").read_text())
    config = config_cls(**meta["config"])

    if meta["status"] == "error":
        return TrialResult(
            config_id=meta["config_id"],
            config=config,
            result=None,
            sharpe=_from_json_safe(meta["sharpe"]),
            cagr=_from_json_safe(meta["cagr"]),
            max_drawdown=_from_json_safe(meta["max_drawdown"]),
            status="error",
            error_msg=meta.get("error_msg"),
        )

    eq_df = pd.read_parquet(directory / "equity.parquet")
    equity_curve = eq_df["equity"]

    trades_df = pd.read_parquet(directory / "trades.parquet")
    trades = [_row_to_trade(row) for _, row in trades_df.iterrows()]

    fills_df = pd.read_parquet(directory / "fills.parquet")
    fills = [_row_to_fill(row) for _, row in fills_df.iterrows()]

    result = BacktestResult(
        equity_curve=equity_curve,
        trades=trades,
        fills=fills,
        initial_cash=float(meta["initial_cash"]),
        final_equity=float(meta["final_equity"]),
    )
    return TrialResult(
        config_id=meta["config_id"],
        config=config,
        result=result,
        sharpe=_from_json_safe(meta["sharpe"]),
        cagr=_from_json_safe(meta["cagr"]),
        max_drawdown=_from_json_safe(meta["max_drawdown"]),
        status="ok",
        error_msg=None,
    )


def _json_safe(x: float) -> float | str:
    """NaN and ±inf are not valid JSON — encode as strings."""
    if np.isnan(x):
        return "nan"
    if np.isposinf(x):
        return "inf"
    if np.isneginf(x):
        return "-inf"
    return float(x)


def _from_json_safe(x) -> float:
    if isinstance(x, str):
        return float(x)
    return float(x)

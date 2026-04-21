"""bt adapter — Plano B V4 in Philippe Morissette's `bt` library.

Strategy composition:
1. For each leg, compute signal (ema_regime or donchian) on signal_ticker prices.
2. Map signal → target weight on execution_ticker (weight * 1/N if LONG, 0 if FLAT).
3. Pass to bt.Strategy with TargetWeights algo + threshold rebalance.
4. Backtest on DataFrame of execution_ticker prices.
"""
from __future__ import annotations

import traceback
from typing import Any

import numpy as np
import pandas as pd

from reports.phase_3_5c.cross_lib.adapters.signals import (
    donchian_signal,
    ema_regime,
)
from reports.phase_3_5c.cross_lib.data.reference_prices import (
    load_reference_parquet,
)
from reports.phase_3_5c.cross_lib.types import (
    Outcome,
    RunResult,
    VariantConfig,
)


class BtAdapter:
    name: str = "bt"

    def run(
        self,
        variant: VariantConfig,
        window: tuple[str, str],
        stage: int,
    ) -> RunResult:
        try:
            import bt  # noqa: F401
        except ImportError as exc:
            return self._skipped_result(variant, window, stage, str(exc))

        try:
            prices = self._load_prices(variant, window, stage)
            weights = self._compute_target_weights(variant, prices)
            equity = self._run_bt(variant, prices, weights)
            return self._finalize_result(variant, window, stage, equity, prices)
        except FileNotFoundError as exc:
            return self._data_unavailable(variant, window, stage, str(exc))
        except Exception as exc:  # pragma: no cover - adapter must not raise
            return self._error_result(variant, window, stage, exc)

    def _load_prices(
        self, variant: VariantConfig, window: tuple[str, str], stage: int
    ) -> pd.DataFrame:
        """Return wide-format price DataFrame: index=date, columns=tickers."""
        if stage == 1:
            df = load_reference_parquet()
        else:  # stage 2 — independent fetch
            from reports.phase_3_5c.cross_lib.data.independent_fetchers.yf_fetcher import (
                fetch_yf,
            )

            tickers = list(
                {leg.signal_ticker for leg in variant.legs}
                | {leg.execution_ticker for leg in variant.legs}
            )
            df = fetch_yf(tickers, window[0], window[1])

        df = df[(df["date"] >= window[0]) & (df["date"] <= window[1])]
        wide = df.pivot(index="date", columns="ticker", values="close")
        return wide.ffill().dropna(how="all")

    def _compute_target_weights(
        self, variant: VariantConfig, prices: pd.DataFrame
    ) -> pd.DataFrame:
        """Return per-date target weights for each execution ticker.

        Allocation rule: leg's target weight is `1/N` when signal is LONG,
        0 when signal is FLAT. Unallocated weight stays as cash (no
        cross-leg reallocation except on threshold event — bt's weighting
        algo handles the threshold logic).
        """
        n = len(variant.legs)
        weight_per_leg = 1.0 / n
        weights = pd.DataFrame(0.0, index=prices.index, columns=[leg.execution_ticker for leg in variant.legs])

        for leg in variant.legs:
            signal_prices = prices[leg.signal_ticker]
            if leg.signal_type == "ema_regime":
                state = ema_regime(signal_prices, leg.signal_params["lookback"])
            elif leg.signal_type == "donchian":
                state = donchian_signal(
                    signal_prices,
                    leg.signal_params["entry"],
                    leg.signal_params["exit"],
                )
            else:
                raise ValueError(f"Unknown signal_type: {leg.signal_type}")
            weights[leg.execution_ticker] = state.astype(float) * weight_per_leg

        return weights

    def _run_bt(
        self,
        variant: VariantConfig,
        prices: pd.DataFrame,
        weights: pd.DataFrame,
    ) -> pd.Series:
        import bt

        exec_tickers = [leg.execution_ticker for leg in variant.legs]
        exec_prices = prices[exec_tickers]

        # Threshold rebalance: bt's RebalanceOverTime with threshold check.
        # For simplicity, use a WeighTarget algo + PeriodicRebalance monthly
        # combined with a threshold guard. bt's canonical idiom:
        if variant.rebalance.mode == "daily":
            rebal_algo = bt.algos.RunDaily()
        elif variant.rebalance.mode == "threshold":
            rebal_algo = _ThresholdRebalance(variant.rebalance.threshold_pp / 100.0)
        else:
            rebal_algo = bt.algos.RunMonthly()

        strat = bt.Strategy(
            variant.variant_id,
            [
                rebal_algo,
                bt.algos.WeighTarget(weights),
                bt.algos.Rebalance(),
            ],
        )
        backtest = bt.Backtest(strat, exec_prices)
        result = bt.run(backtest)
        return result.prices[variant.variant_id].rename("equity")

    def _finalize_result(
        self,
        variant: VariantConfig,
        window: tuple[str, str],
        stage: int,
        equity: pd.Series,
        prices: pd.DataFrame,
    ) -> RunResult:
        rets = equity.pct_change().dropna()
        cagr = _cagr(equity)
        sharpe = _sharpe(rets)
        max_dd = _max_drawdown(equity)
        monthly = rets.resample("ME").apply(lambda x: (1 + x).prod() - 1)
        wf_splits = _walk_forward_sharpe(rets, n_splits=8)

        return RunResult(
            variant_id=variant.variant_id,
            lib=self.name,
            window=window,
            stage=stage,
            equity_curve=equity,
            monthly_returns=monthly,
            trade_dates=[],  # bt exposes via transactions; left empty here, filled per-report
            cagr=cagr,
            sharpe=sharpe,
            max_dd=max_dd,
            wf_splits_8=wf_splits,
            dsr_pval=_dsr_pval(sharpe, rets),
            outcome="OK",
            error_detail=None,
        )

    def _skipped_result(
        self, variant: VariantConfig, window: tuple[str, str], stage: int, msg: str
    ) -> RunResult:
        return _empty_result(
            variant, self.name, window, stage, outcome="SKIPPED", error_detail=msg
        )

    def _data_unavailable(
        self, variant: VariantConfig, window: tuple[str, str], stage: int, msg: str
    ) -> RunResult:
        return _empty_result(
            variant,
            self.name,
            window,
            stage,
            outcome="DATA_UNAVAILABLE",
            error_detail=msg,
        )

    def _error_result(
        self,
        variant: VariantConfig,
        window: tuple[str, str],
        stage: int,
        exc: Exception,
    ) -> RunResult:
        return _empty_result(
            variant,
            self.name,
            window,
            stage,
            outcome="ERROR",
            error_detail=f"{exc}\n{traceback.format_exc()}",
        )


def _empty_result(
    variant: VariantConfig,
    lib: str,
    window: tuple[str, str],
    stage: int,
    outcome: Outcome,
    error_detail: str | None,
) -> RunResult:
    return RunResult(
        variant_id=variant.variant_id,
        lib=lib,
        window=window,
        stage=stage,
        equity_curve=pd.Series(dtype=float),
        monthly_returns=pd.Series(dtype=float),
        trade_dates=[],
        cagr=float("nan"),
        sharpe=float("nan"),
        max_dd=float("nan"),
        wf_splits_8=[],
        dsr_pval=float("nan"),
        outcome=outcome,
        error_detail=error_detail,
    )


def _cagr(equity: pd.Series) -> float:
    if len(equity) < 2:
        return float("nan")
    years = (equity.index[-1] - equity.index[0]).days / 365.25
    return (equity.iloc[-1] / equity.iloc[0]) ** (1 / years) - 1


def _sharpe(returns: pd.Series, periods_per_year: int = 252) -> float:
    if returns.std() == 0 or len(returns) < 30:
        return float("nan")
    return returns.mean() / returns.std() * np.sqrt(periods_per_year)


def _max_drawdown(equity: pd.Series) -> float:
    running_max = equity.expanding().max()
    dd = (equity - running_max) / running_max
    return float(dd.min())


def _walk_forward_sharpe(returns: pd.Series, n_splits: int) -> list[float]:
    if len(returns) < n_splits * 30:
        return []
    slice_len = len(returns) // n_splits
    return [
        _sharpe(returns.iloc[i * slice_len : (i + 1) * slice_len])
        for i in range(n_splits)
    ]


def _dsr_pval(sharpe: float, returns: pd.Series, n_trials: int = 4) -> float:
    """Deflated Sharpe Ratio p-value [advances_fin_ml, p.231-234].

    Simplified: assumes skew=0, kurt=3. Production should use full formula.
    """
    from scipy.stats import norm

    if not np.isfinite(sharpe):
        return float("nan")
    t = len(returns)
    expected_max_sr = ((1 - 0.5772) * norm.ppf(1 - 1 / n_trials) +
                       0.5772 * norm.ppf(1 - 1 / (n_trials * np.e)))
    z = (sharpe * np.sqrt(t - 1) - expected_max_sr) / np.sqrt(1 - 0)
    return float(1 - norm.cdf(z))


class _ThresholdRebalance:
    """bt algo — rebalance only when any weight drifts beyond threshold."""

    def __init__(self, threshold_fraction: float) -> None:
        self.threshold = threshold_fraction

    def __call__(self, target: Any) -> bool:
        if not hasattr(target, "temp") or "weights" not in target.temp:
            return True
        current = target.children
        targets = target.temp["weights"]
        for k, w in targets.items():
            actual = current[k].weight if k in current else 0.0
            if abs(actual - w) > self.threshold:
                return True
        return False

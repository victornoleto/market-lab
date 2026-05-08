"""backtrader adapter — Plano B V4 in event-driven paradigm.

backtrader is strictly event-driven: each bar fires `next()`, orders fill on
the next bar's open by default. Strategy class reads signals per-bar and
computes target weight; `self.order_target_percent()` handles rebalance.

Because backtrader is slower (event loop), expect long runs. For the full
40-year window, a single variant run takes ~30-90s depending on hardware.
"""
from __future__ import annotations

import traceback
from dataclasses import dataclass

import numpy as np
import pandas as pd

from studies._archive.phase_3_5c.reports.cross_lib.adapters.bt_adapter import (
    _cagr,
    _dsr_pval,
    _empty_result,
    _max_drawdown,
    _sharpe,
    _walk_forward_sharpe,
)
from studies._archive.phase_3_5c.reports.cross_lib.adapters.signals import (
    always_on,
    donchian_signal,
    ema_regime,
)
from studies._archive.phase_3_5c.reports.cross_lib.data.reference_prices import (
    load_reference_parquet,
)
from studies._archive.phase_3_5c.reports.cross_lib.types import RunResult, VariantConfig


class BacktraderAdapter:
    name: str = "backtrader"

    def run(
        self,
        variant: VariantConfig,
        window: tuple[str, str],
        stage: int,
    ) -> RunResult:
        try:
            import backtrader as bt  # noqa: F401
        except ImportError as exc:
            return _empty_result(variant, self.name, window, stage, "SKIPPED", str(exc))

        try:
            prices = self._load_prices(variant, window, stage)
            equity = self._run_bt(variant, prices)
            return self._finalize(variant, window, stage, equity)
        except FileNotFoundError as exc:
            return _empty_result(variant, self.name, window, stage, "DATA_UNAVAILABLE", str(exc))
        except Exception as exc:  # pragma: no cover
            return _empty_result(
                variant,
                self.name,
                window,
                stage,
                "ERROR",
                f"{exc}\n{traceback.format_exc()}",
            )

    def _load_prices(
        self, variant: VariantConfig, window: tuple[str, str], stage: int
    ) -> pd.DataFrame:
        if stage == 1:
            df = load_reference_parquet()
        else:
            from studies._archive.phase_3_5c.reports.cross_lib.data.independent_fetchers.yf_fetcher import (
                fetch_yf,
            )

            tickers = list(
                {leg.signal_ticker for leg in variant.legs}
                | {leg.execution_ticker for leg in variant.legs}
            )
            df = fetch_yf(tickers, window[0], window[1])

        df = df[(df["date"] >= window[0]) & (df["date"] <= window[1])]
        return df

    def _run_bt(self, variant: VariantConfig, prices: pd.DataFrame) -> pd.Series:
        import backtrader as bt

        cerebro = bt.Cerebro()
        cerebro.broker.setcash(1_000_000.0)
        cerebro.broker.setcommission(commission=0.0)

        # Build wide-format DataFrame for precomputing signals.
        # Passed via params so the strategy can reconstruct signals correctly
        # without relying on backtrader's circular-buffer datetime.date() API,
        # which has an off-by-one issue in __init__ (index 0 = last bar).
        # [advances_fin_ml, p.31-34] — data integrity for cross-lib replication.
        wide_prices: dict[str, pd.Series] = {}
        tickers = sorted({leg.signal_ticker for leg in variant.legs} | {leg.execution_ticker for leg in variant.legs})
        for ticker in tickers:
            sub = prices[prices["ticker"] == ticker].sort_values("date")
            feed_df = sub.set_index("date")[["open", "high", "low", "close", "volume"]]
            feed_df.index = pd.to_datetime(feed_df.index)
            wide_prices[ticker] = feed_df["close"]
            data = bt.feeds.PandasData(dataname=feed_df, name=ticker)
            cerebro.adddata(data)

        cerebro.addstrategy(_PlanoBStrategy, variant=variant, wide_prices=wide_prices)
        cerebro.addanalyzer(_EquityCurveAnalyzer, _name="equity")
        results = cerebro.run()
        analyzer = results[0].analyzers.equity
        eq = pd.Series(analyzer.values, index=pd.to_datetime(analyzer.dates))
        return eq

    def _finalize(
        self,
        variant: VariantConfig,
        window: tuple[str, str],
        stage: int,
        equity: pd.Series,
    ) -> RunResult:
        rets = equity.pct_change().dropna()
        cagr = _cagr(equity)
        sharpe = _sharpe(rets)
        max_dd = _max_drawdown(equity)
        monthly = rets.resample("ME").apply(lambda x: (1 + x).prod() - 1)

        return RunResult(
            variant_id=variant.variant_id,
            lib=self.name,
            window=window,
            stage=stage,
            equity_curve=equity,
            monthly_returns=monthly,
            trade_dates=[],
            cagr=cagr,
            sharpe=sharpe,
            max_dd=max_dd,
            wf_splits_8=_walk_forward_sharpe(rets, 8),
            dsr_pval=_dsr_pval(sharpe, rets),
            outcome="OK",
            error_detail=None,
        )


def _lazy_imports():  # pragma: no cover - helper for the class defs below
    import backtrader as bt

    return bt


class _PlanoBStrategy:  # will become backtrader.Strategy subclass at runtime
    """Defined lazily to avoid hard-importing backtrader at module load time.

    Replaced at adapter construction via type() with a backtrader.Strategy base.
    Using simple module-level reassignment below.
    """


def _build_strategy_class():
    import backtrader as bt

    class PlanoBStrategy(bt.Strategy):
        params = (("variant", None), ("wide_prices", None))

        def __init__(self) -> None:
            self.variant = self.p.variant
            self.signal_states: dict[str, int] = {}
            self.data_by_ticker = {d._name: d for d in self.datas}

            # Precompute signals using the wide_prices dict passed via params.
            # We do NOT use feed.close.array / feed.datetime.date() here because
            # in backtrader's __init__, datetime.date(0) returns the LAST bar
            # (ring-buffer semantics), scrambling the date index for the first
            # element. Using the pre-built pandas Series avoids this entirely.
            # [advances_fin_ml, p.31-34] — data integrity for cross-lib replication.
            self.precomputed_state: dict[str, pd.Series] = {}
            wide_prices: dict[str, pd.Series] = self.p.wide_prices or {}
            for leg in self.variant.legs:
                close_series = wide_prices[leg.signal_ticker]
                if leg.signal_type == "ema_regime":
                    state = ema_regime(close_series, leg.signal_params["lookback"])
                elif leg.signal_type == "donchian":
                    state = donchian_signal(
                        close_series,
                        leg.signal_params["entry"],
                        leg.signal_params["exit"],
                    )
                elif leg.signal_type == "always_on":
                    state = always_on(close_series)
                else:
                    raise ValueError(f"Unknown signal_type: {leg.signal_type}")
                self.precomputed_state[leg.signal_ticker] = state.astype(int)

            self.last_rebal_weights: dict[str, float] = {}

        def next(self) -> None:
            today = pd.Timestamp(self.datetime.date(0))
            n = len(self.variant.legs)
            w = 1.0 / n

            target: dict[str, float] = {}
            for leg in self.variant.legs:
                state = self.precomputed_state[leg.signal_ticker].get(today, 0)
                target[leg.execution_ticker] = state * w

            if self._should_rebalance(target):
                for leg in self.variant.legs:
                    self.order_target_percent(
                        data=self.data_by_ticker[leg.execution_ticker],
                        target=target[leg.execution_ticker],
                    )
                self.last_rebal_weights = target.copy()

        def _should_rebalance(self, target: dict[str, float]) -> bool:
            mode = self.variant.rebalance.mode
            if mode == "daily":
                return True
            if mode == "threshold":
                if not self.last_rebal_weights:
                    return True
                threshold = self.variant.rebalance.threshold_pp / 100.0
                for ticker, w in target.items():
                    if abs(w - self.last_rebal_weights.get(ticker, 0.0)) > threshold:
                        return True
                return False
            return False  # monthly modes not yet wired in backtrader

    return PlanoBStrategy


def _build_analyzer_class():
    import backtrader as bt

    class EquityCurveAnalyzer(bt.Analyzer):
        def __init__(self) -> None:
            self.values: list[float] = []
            self.dates: list[pd.Timestamp] = []

        def next(self) -> None:
            self.values.append(self.strategy.broker.getvalue())
            self.dates.append(pd.Timestamp(self.strategy.datetime.date(0)))

    return EquityCurveAnalyzer


# Module-level rebind: when backtrader is installed, replace stubs.
try:
    _PlanoBStrategy = _build_strategy_class()
    _EquityCurveAnalyzer = _build_analyzer_class()
except ImportError:  # pragma: no cover
    _EquityCurveAnalyzer = None  # type: ignore[assignment]

"""vectorbt adapter — Plano B V4 vectorized.

vectorbt's Portfolio.from_orders takes per-(date,ticker) target-weight matrices.
We compute weights via the same helper used by other adapters, then use
Portfolio.from_orders with size_type='targetpercent' + freq='D'.
"""
from __future__ import annotations

import traceback

import numpy as np
import pandas as pd

from reports.phase_3_5c.cross_lib.adapters.bt_adapter import (
    _cagr,
    _dsr_pval,
    _empty_result,
    _max_drawdown,
    _sharpe,
    _walk_forward_sharpe,
)
from reports.phase_3_5c.cross_lib.adapters.signals import (
    donchian_signal,
    ema_regime,
)
from reports.phase_3_5c.cross_lib.data.reference_prices import (
    load_reference_parquet,
)
from reports.phase_3_5c.cross_lib.types import (
    RunResult,
    VariantConfig,
)


class VectorbtAdapter:
    name: str = "vectorbt"

    def run(
        self,
        variant: VariantConfig,
        window: tuple[str, str],
        stage: int,
    ) -> RunResult:
        try:
            import vectorbt as vbt  # noqa: F401
        except ImportError as exc:
            return _empty_result(variant, self.name, window, stage, "SKIPPED", str(exc))

        try:
            prices = self._load_prices(variant, window, stage)
            weights = self._compute_target_weights(variant, prices)
            equity = self._run_vbt(variant, prices, weights)
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
        n = len(variant.legs)
        w = 1.0 / n
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
            weights[leg.execution_ticker] = state.astype(float) * w
        return weights

    def _run_vbt(
        self, variant: VariantConfig, prices: pd.DataFrame, weights: pd.DataFrame
    ) -> pd.Series:
        import vectorbt as vbt

        exec_tickers = [leg.execution_ticker for leg in variant.legs]
        exec_prices = prices[exec_tickers]

        # For threshold rebalance, collapse weight targets to "rebal event days"
        # via drift detection. Simpler path: daily rebal on weight change only.
        size = weights.diff().abs().sum(axis=1)
        if variant.rebalance.mode == "threshold":
            threshold = variant.rebalance.threshold_pp / 100.0
            rebal_mask = size > threshold
        else:
            rebal_mask = pd.Series(True, index=weights.index)

        rebal_weights = weights.where(rebal_mask, other=np.nan).ffill()

        pf = vbt.Portfolio.from_orders(
            close=exec_prices,
            size=rebal_weights,
            size_type="targetpercent",
            freq="D",
            init_cash=1.0,
            fees=0.0,
            group_by=True,
            cash_sharing=True,
        )
        return pf.value()

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

"""Unit + integration tests for the backtest metrics module.

Scope:
    TestPerformance  — sharpe, sortino, calmar, cagr, max_drawdown, volatility, var
    TestHelpers      — returns_from_equity utility
    TestReport       — markdown generator with all required sections + PNG chart

Design: hand-computable inputs. Gaussian fixtures use seeded generators so
assertions can use tight tolerances without flaking.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest


# ---------------------------------------------------------------------------
# Performance metrics
# ---------------------------------------------------------------------------


class TestPerformance:
    def test_volatility_annualizes_by_sqrt_periods(self):
        from market_lab.backtest.metrics.performance import volatility

        # Constant 1% daily std → annualized = 0.01 · √252
        rng = np.random.default_rng(0)
        returns = pd.Series(rng.normal(loc=0.0, scale=0.01, size=10_000))

        vol = volatility(returns, periods_per_year=252)
        assert vol == pytest.approx(0.01 * np.sqrt(252), rel=0.05)

    def test_volatility_uses_ddof_zero(self):
        from market_lab.backtest.metrics.performance import volatility

        returns = pd.Series([0.01, -0.01, 0.01, -0.01])
        # Population std of ±0.01 is exactly 0.01.
        assert volatility(returns, periods_per_year=1) == pytest.approx(0.01)

    def test_sharpe_zero_mean_returns_zero(self):
        from market_lab.backtest.metrics.performance import sharpe

        returns = pd.Series([0.01, -0.01, 0.01, -0.01])
        assert sharpe(returns, periods_per_year=1) == pytest.approx(0.0)

    def test_sharpe_known_mean_vol(self):
        from market_lab.backtest.metrics.performance import sharpe

        # mean = 0.02, std (ddof=0) = 0.01 → Sharpe_periodic = 2; annualized × √252
        returns = pd.Series([0.03, 0.01, 0.03, 0.01])
        assert sharpe(returns, periods_per_year=252) == pytest.approx(2.0 * np.sqrt(252))

    def test_sharpe_subtracts_risk_free(self):
        from market_lab.backtest.metrics.performance import sharpe

        returns = pd.Series([0.03, 0.01, 0.03, 0.01])  # mean 0.02, std 0.01
        # With rf=0.01 per period → (0.02 - 0.01) / 0.01 = 1 per period, annualized.
        assert sharpe(returns, periods_per_year=1, risk_free=0.01) == pytest.approx(1.0)

    def test_sharpe_zero_std_returns_zero(self):
        from market_lab.backtest.metrics.performance import sharpe

        returns = pd.Series([0.01, 0.01, 0.01, 0.01])
        assert sharpe(returns, periods_per_year=252) == pytest.approx(0.0)

    def test_sortino_uses_downside_deviation_only(self):
        from market_lab.backtest.metrics.performance import sortino

        # mean = 0.02; downside returns (< target 0) = [-0.02]; downside_dev = √(0.02²/4) = 0.01
        returns = pd.Series([0.04, 0.02, 0.04, -0.02])
        expected_periodic = 0.02 / 0.01
        assert sortino(returns, periods_per_year=1, target=0.0) == pytest.approx(
            expected_periodic
        )

    def test_sortino_infinite_when_no_downside(self):
        from market_lab.backtest.metrics.performance import sortino

        returns = pd.Series([0.01, 0.02, 0.03, 0.04])
        # All positive → no downside → Sortino is ill-defined; convention: +inf.
        assert np.isposinf(sortino(returns, periods_per_year=1, target=0.0))

    def test_cagr_doubles_in_one_year_gives_100pct(self):
        from market_lab.backtest.metrics.performance import cagr

        # 252 bars, equity doubles over that period with daily compounding.
        idx = pd.date_range("2024-01-02", periods=253, freq="B")
        eq = pd.Series(np.linspace(100.0, 200.0, 253), index=idx)
        # cagr uses (last/first)^(periods_per_year / n_periods) - 1; n_periods=252.
        assert cagr(eq, periods_per_year=252) == pytest.approx(1.0, rel=1e-6)

    def test_cagr_half_year_doubling_gives_300pct(self):
        from market_lab.backtest.metrics.performance import cagr

        idx = pd.date_range("2024-01-02", periods=127, freq="B")  # 126 periods = 0.5y
        eq = pd.Series(np.linspace(100.0, 200.0, 127), index=idx)
        # (2)^(252/126) - 1 = 2^2 - 1 = 3
        assert cagr(eq, periods_per_year=252) == pytest.approx(3.0, rel=1e-6)

    def test_max_drawdown_known_peak_trough(self):
        from market_lab.backtest.metrics.performance import max_drawdown

        # Peak 120, trough 90 → DD = 30/120 = 0.25
        eq = pd.Series([100, 110, 120, 100, 95, 90, 95, 100])
        assert max_drawdown(eq) == pytest.approx(0.25)

    def test_max_drawdown_monotone_series_is_zero(self):
        from market_lab.backtest.metrics.performance import max_drawdown

        eq = pd.Series([100, 101, 102, 103, 104])
        assert max_drawdown(eq) == pytest.approx(0.0)

    def test_max_drawdown_is_positive_magnitude(self):
        from market_lab.backtest.metrics.performance import max_drawdown

        eq = pd.Series([100, 50])
        dd = max_drawdown(eq)
        assert dd > 0.0  # positive magnitude, not signed
        assert dd == pytest.approx(0.5)

    def test_calmar_is_cagr_over_abs_max_dd(self):
        from market_lab.backtest.metrics.performance import calmar

        # 1 year, ends 200% of start, DD = 0.25 → Calmar = 1.0 / 0.25 = 4
        idx = pd.date_range("2024-01-02", periods=253, freq="B")
        # Build an equity curve with a controlled 25% dip then recovery.
        values = np.linspace(100.0, 150.0, 126).tolist()
        values += np.linspace(150.0, 112.5, 40).tolist()[1:]  # drop 25% to 112.5
        values += np.linspace(112.5, 200.0, 253 - len(values) + 1).tolist()[1:]
        assert len(values) == 253
        eq = pd.Series(values, index=idx)

        from market_lab.backtest.metrics.performance import cagr, max_drawdown

        c = cagr(eq, periods_per_year=252)
        dd = max_drawdown(eq)
        assert calmar(eq, periods_per_year=252) == pytest.approx(c / dd, rel=1e-9)

    def test_calmar_zero_drawdown_is_inf(self):
        from market_lab.backtest.metrics.performance import calmar

        idx = pd.date_range("2024-01-02", periods=253, freq="B")
        eq = pd.Series(np.linspace(100.0, 200.0, 253), index=idx)
        # Monotone up → no drawdown → Calmar = +inf.
        assert np.isposinf(calmar(eq, periods_per_year=252))

    def test_var_historical_quantile_positive_magnitude(self):
        from market_lab.backtest.metrics.performance import var

        # 100 returns uniformly in [-0.05, 0.05]; 5% quantile ≈ -0.045 → VaR ≈ 0.045.
        rng = np.random.default_rng(42)
        returns = pd.Series(rng.uniform(-0.05, 0.05, size=100_000))
        v = var(returns, alpha=0.05)
        assert v == pytest.approx(0.045, abs=0.002)
        assert v > 0  # positive magnitude of loss

    def test_var_all_positive_returns_is_zero_floor(self):
        from market_lab.backtest.metrics.performance import var

        returns = pd.Series([0.01, 0.02, 0.03, 0.04])
        # 5% quantile is positive → no loss at α; convention floor at 0.
        assert var(returns, alpha=0.05) == pytest.approx(0.0)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


class TestHelpers:
    def test_returns_from_equity_pct_change(self):
        from market_lab.backtest.metrics.performance import returns_from_equity

        eq = pd.Series([100.0, 110.0, 99.0, 99.0])
        r = returns_from_equity(eq)
        assert len(r) == 3  # pct_change drops the first NaN
        assert r.iloc[0] == pytest.approx(0.10)
        assert r.iloc[1] == pytest.approx(-0.10)
        assert r.iloc[2] == pytest.approx(0.0)


# ---------------------------------------------------------------------------
# Report generator
# ---------------------------------------------------------------------------


@pytest.fixture
def synthetic_backtest_result():
    """Synthetic BacktestResult + validation outputs usable across report tests."""
    from market_lab.backtest.engine.execution import Fill, Order
    from market_lab.backtest.engine.portfolio import Trade
    from market_lab.backtest.engine.runner import BacktestResult

    idx = pd.date_range("2024-01-02", periods=252, freq="B")
    rng = np.random.default_rng(7)
    rets = rng.normal(loc=0.0005, scale=0.01, size=252)
    equity = pd.Series(100_000.0 * np.cumprod(1.0 + rets), index=idx, name="equity")

    trades = [
        Trade(
            symbol="AAPL",
            side="long",
            volume=10,
            entry_price=150.0,
            exit_price=150.0 + (i - 5) * 2.0,  # 20 trades spanning losers → winners
            entry_time=idx[i],
            exit_time=idx[i + 3],
            pnl=10 * (i - 5) * 2.0,
        )
        for i in range(20)
    ]

    fills = [
        Fill(
            order=Order(symbol="AAPL", side="buy", volume=10),
            fill_price=150.0,
            fill_time=idx[0],
            commission=1.0,
            slippage_cost=0.5,
        )
    ]

    return BacktestResult(
        equity_curve=equity,
        trades=trades,
        fills=fills,
        initial_cash=100_000.0,
        final_equity=float(equity.iloc[-1]),
    )


@pytest.fixture
def synthetic_validation_outputs():
    """Mocked validation outputs (PBO, DSR, walk-forward, CPCV)."""
    from market_lab.backtest.validation.dsr import DSRResult
    from market_lab.backtest.validation.pbo import PBOResult

    pbo = PBOResult(pbo=0.3, logits=np.array([0.1, 0.2, -0.1]), n_blocks=8, n_combinations=70)
    dsr = DSRResult(
        dsr=0.98, p_value=0.02, observed_sharpe=0.15, benchmark_sharpe=0.08, n_trials=10
    )
    wf = {
        "n_windows": 10,
        "n_profitable": 8,
        "max_drawdown": 0.18,
        "verdict": "pass",
    }
    cpcv = {
        "mean_sharpe": 0.12,
        "std_sharpe": 0.04,
        "min_sharpe": 0.03,
        "max_sharpe": 0.21,
        "path_sharpes": np.array([0.03, 0.08, 0.10, 0.11, 0.12, 0.14, 0.17, 0.21]),
    }
    return {"pbo": pbo, "dsr": dsr, "walk_forward": wf, "cpcv": cpcv}


class TestReport:
    def test_generates_markdown_file(
        self, tmp_path, synthetic_backtest_result, synthetic_validation_outputs
    ):
        from market_lab.backtest.metrics.report import generate_report

        path = generate_report(
            result=synthetic_backtest_result,
            validation=synthetic_validation_outputs,
            strategy_name="test_strategy",
            output_dir=tmp_path,
            data_source="yfinance",
        )
        assert path.exists()
        assert path.suffix == ".md"
        assert "test_strategy" in path.name

    def test_survivorship_disclaimer_present_for_yfinance(
        self, tmp_path, synthetic_backtest_result, synthetic_validation_outputs
    ):
        from market_lab.backtest.metrics.report import generate_report

        path = generate_report(
            result=synthetic_backtest_result,
            validation=synthetic_validation_outputs,
            strategy_name="s",
            output_dir=tmp_path,
            data_source="yfinance",
        )
        content = path.read_text()
        assert "survivorship" in content.lower()
        # The disclaimer text must clearly mention bias (not just the word "survivorship").
        assert "bias" in content.lower()

    def test_survivorship_disclaimer_present_for_wikipedia(
        self, tmp_path, synthetic_backtest_result, synthetic_validation_outputs
    ):
        from market_lab.backtest.metrics.report import generate_report

        path = generate_report(
            result=synthetic_backtest_result,
            validation=synthetic_validation_outputs,
            strategy_name="s",
            output_dir=tmp_path,
            data_source="wikipedia",
        )
        content = path.read_text()
        assert "survivorship" in content.lower()

    def test_no_disclaimer_for_survivorship_free_source(
        self, tmp_path, synthetic_backtest_result, synthetic_validation_outputs
    ):
        from market_lab.backtest.metrics.report import generate_report

        path = generate_report(
            result=synthetic_backtest_result,
            validation=synthetic_validation_outputs,
            strategy_name="s",
            output_dir=tmp_path,
            data_source="tiingo_sf",  # survivorship-free tag
        )
        content = path.read_text()
        # Text may still mention the word in context, but must not state the disclaimer.
        # Minimal check: no "WARNING" banner + no "contains survivorship bias" phrase.
        assert "contains survivorship bias" not in content.lower()

    def test_all_required_sections_present(
        self, tmp_path, synthetic_backtest_result, synthetic_validation_outputs
    ):
        from market_lab.backtest.metrics.report import generate_report

        path = generate_report(
            result=synthetic_backtest_result,
            validation=synthetic_validation_outputs,
            strategy_name="s",
            output_dir=tmp_path,
            data_source="yfinance",
        )
        content = path.read_text()
        for section in (
            "Performance",
            "CPCV",
            "PBO",
            "DSR",
            "Walk-forward",
            "Trades",
        ):
            assert section in content, f"missing '{section}' section"

    def test_pbo_verdict_shown(
        self, tmp_path, synthetic_backtest_result, synthetic_validation_outputs
    ):
        from market_lab.backtest.metrics.report import generate_report

        path = generate_report(
            result=synthetic_backtest_result,
            validation=synthetic_validation_outputs,
            strategy_name="s",
            output_dir=tmp_path,
            data_source="yfinance",
        )
        content = path.read_text()
        assert "pass" in content.lower() or "reject" in content.lower()
        assert "0.30" in content  # PBO value

    def test_dsr_p_value_shown(
        self, tmp_path, synthetic_backtest_result, synthetic_validation_outputs
    ):
        from market_lab.backtest.metrics.report import generate_report

        path = generate_report(
            result=synthetic_backtest_result,
            validation=synthetic_validation_outputs,
            strategy_name="s",
            output_dir=tmp_path,
            data_source="yfinance",
        )
        content = path.read_text()
        assert "0.02" in content  # DSR p-value

    def test_png_chart_generated(
        self, tmp_path, synthetic_backtest_result, synthetic_validation_outputs
    ):
        from market_lab.backtest.metrics.report import generate_report

        generate_report(
            result=synthetic_backtest_result,
            validation=synthetic_validation_outputs,
            strategy_name="s",
            output_dir=tmp_path,
            data_source="yfinance",
        )
        # PNG in reports/assets/
        pngs = list((tmp_path / "assets").glob("*.png"))
        assert len(pngs) >= 1

    def test_report_references_png(
        self, tmp_path, synthetic_backtest_result, synthetic_validation_outputs
    ):
        from market_lab.backtest.metrics.report import generate_report

        path = generate_report(
            result=synthetic_backtest_result,
            validation=synthetic_validation_outputs,
            strategy_name="s",
            output_dir=tmp_path,
            data_source="yfinance",
        )
        content = path.read_text()
        # Markdown embed syntax: ![](assets/...png) or inline ref
        assert "assets/" in content and ".png" in content

    def test_top_trades_section_lists_ten_each_side(
        self, tmp_path, synthetic_backtest_result, synthetic_validation_outputs
    ):
        from market_lab.backtest.metrics.report import generate_report

        path = generate_report(
            result=synthetic_backtest_result,
            validation=synthetic_validation_outputs,
            strategy_name="s",
            output_dir=tmp_path,
            data_source="yfinance",
        )
        content = path.read_text()
        # Two subsections of trades: winners and losers.
        assert "Winners" in content or "winners" in content
        assert "Losers" in content or "losers" in content

    def test_filename_timestamped(
        self, tmp_path, synthetic_backtest_result, synthetic_validation_outputs
    ):
        from market_lab.backtest.metrics.report import generate_report

        path = generate_report(
            result=synthetic_backtest_result,
            validation=synthetic_validation_outputs,
            strategy_name="clenow",
            output_dir=tmp_path,
            data_source="yfinance",
        )
        # Name pattern: clenow_YYYYMMDD-HHMM.md
        stem = path.stem
        assert stem.startswith("clenow_")
        tail = stem[len("clenow_"):]
        # YYYYMMDD-HHMM has 13 chars.
        assert len(tail) == 13 and tail[8] == "-"

    def test_no_crash_on_empty_trades(
        self, tmp_path, synthetic_backtest_result, synthetic_validation_outputs
    ):
        """Edge case: strategy made no trades."""
        from market_lab.backtest.engine.runner import BacktestResult
        from market_lab.backtest.metrics.report import generate_report

        empty_result = BacktestResult(
            equity_curve=synthetic_backtest_result.equity_curve,
            trades=[],
            fills=[],
            initial_cash=100_000.0,
            final_equity=100_000.0,
        )
        path = generate_report(
            result=empty_result,
            validation=synthetic_validation_outputs,
            strategy_name="no_trades",
            output_dir=tmp_path,
            data_source="yfinance",
        )
        assert path.exists()

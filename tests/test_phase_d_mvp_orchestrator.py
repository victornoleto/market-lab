"""Tests for ``scripts.phase_d_mvp`` orchestrator helpers.

Covers grid generation, tier classification, tax post-processor, and the
SUMMARY.md writer. No network, no full backtest runs — those belong to
end-to-end tests triggered only when OHLCV cache is populated.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from ai_trade.backtest.engine.portfolio import Trade

from scripts.phase_d_mvp.orchestrator import (
    GridRecord,
    _classify_cagr_b,
    _classify_mdd_b,
    _collect_oos_matrix,
    d1_grid,
    d4_grid,
    write_summary,
)
from scripts.phase_d_mvp.run_single import (
    SplitMetrics,
    _config_slug,
    apply_monthly_tax,
)


# ---------------------------------------------------------------------------
# Grid sizing
# ---------------------------------------------------------------------------
class TestGridGeneration:
    def test_d1_grid_size_is_24(self):
        """D1 grid = lookback(2) × n_top(4) × sector_cap(3) = 24."""
        grid = d1_grid()
        assert len(grid) == 24
        # Every config has the three expected keys.
        for cfg in grid:
            assert set(cfg) == {"lookback", "n_top", "sector_cap_pct"}

    def test_d4_grid_respects_pre_n_gte_n_top(self):
        """D4 skips impossible configs where n_top > pre_n."""
        grid = d4_grid()
        for cfg in grid:
            assert cfg["n_top"] <= cfg["pre_n"]
        # pre_n∈{30,40,50} × n_top∈{15,20,25} × vol_lookback∈{60,90} = 18
        # (all n_top ≤ 30, so no configs are skipped)
        assert len(grid) == 18

    def test_grid_lookback_values_match_clenow(self):
        """D1 lookback ∈ {90, 180} per [stocks_on_the_move, p.76]."""
        grid = d1_grid()
        lookbacks = {cfg["lookback"] for cfg in grid}
        assert lookbacks == {90, 180}

    def test_d1_n_top_range(self):
        grid = d1_grid()
        tops = {cfg["n_top"] for cfg in grid}
        assert tops == {15, 20, 25, 30}

    def test_no_duplicates(self):
        assert len({tuple(sorted(c.items())) for c in d1_grid()}) == 24
        assert len({tuple(sorted(c.items())) for c in d4_grid()}) == 18


# ---------------------------------------------------------------------------
# Tier classification (Strategy D shares comparator with B — mandate §2.2/§2.3)
# ---------------------------------------------------------------------------
class TestTierClassification:
    @pytest.mark.parametrize("cagr_value,expected", [
        (0.05, "Folclore"),       # < 11% CDI líquido
        (0.10, "Folclore"),
        (0.12, "Marginal"),       # 11-17%
        (0.15, "Marginal"),
        (0.18, "Válido"),         # 17-25% — target tier
        (0.24, "Válido"),
        (0.30, "Forte"),          # 25-40%
        (0.50, "Extraordinário"),  # > 40% — suspect by default
    ])
    def test_cagr_tiers(self, cagr_value, expected):
        assert _classify_cagr_b(cagr_value) == expected

    @pytest.mark.parametrize("mdd,expected", [
        (0.10, "Excelente"),        # ≤ 15%
        (0.15, "Excelente"),
        (0.20, "Válido"),           # 15-25%
        (0.25, "Válido"),
        (0.30, "Marginal"),         # 25-35%
        (0.40, "Forte warning"),    # 35-50%
        (0.60, "Reject"),           # > 50%
    ])
    def test_mdd_tiers(self, mdd, expected):
        assert _classify_mdd_b(mdd) == expected


# ---------------------------------------------------------------------------
# Config slug
# ---------------------------------------------------------------------------
class TestConfigSlug:
    def test_deterministic_ordering(self):
        """Slug is sorted by key, so different dict order → same slug."""
        a = _config_slug({"n_top": 20, "lookback": 90, "sector_cap_pct": 0.25})
        b = _config_slug({"sector_cap_pct": 0.25, "n_top": 20, "lookback": 90})
        assert a == b

    def test_replaces_dots(self):
        slug = _config_slug({"sector_cap_pct": 0.25})
        assert "." not in slug
        assert "0p25" in slug


# ---------------------------------------------------------------------------
# apply_monthly_tax
# ---------------------------------------------------------------------------
def _make_trade(
    symbol: str,
    volume: float,
    exit_price: float,
    pnl: float,
    exit_time: str,
    entry_price: float | None = None,
) -> Trade:
    exit_ts = pd.Timestamp(exit_time)
    entry_ts = exit_ts - pd.Timedelta(days=10)
    return Trade(
        symbol=symbol,
        side="long",
        volume=volume,
        entry_price=entry_price if entry_price is not None else exit_price - pnl / max(volume, 1e-9),
        exit_price=exit_price,
        entry_time=entry_ts,
        exit_time=exit_ts,
        pnl=pnl,
    )


class TestApplyMonthlyTax:
    def test_no_trades_returns_unchanged(self):
        eq = pd.Series([50_000.0, 50_100.0, 50_200.0],
                       index=pd.bdate_range("2024-03-01", periods=3))
        net, tax, hits, _ = apply_monthly_tax(eq, [])
        assert tax == 0.0
        assert hits == 0
        pd.testing.assert_series_equal(net, eq)

    def test_small_month_stays_exempt(self):
        """One sell of R$15k (≤ 20k) → no tax."""
        eq = pd.Series(
            np.linspace(50_000, 51_000, 21),
            index=pd.bdate_range("2024-03-01", periods=21),
        )
        trades = [_make_trade("PETR4.SA", volume=500, exit_price=30.0,
                               pnl=1_000, exit_time="2024-03-15")]
        # gross_amount = 500 × 30 = R$15,000 → exempt
        net, tax, hits, _ = apply_monthly_tax(eq, trades)
        assert tax == 0.0
        assert hits == 0
        assert net.iloc[-1] == eq.iloc[-1]

    def test_large_month_applies_15pct_on_profit(self):
        """Sells > R$20k → 15% of positive month P&L debited at month-end."""
        eq = pd.Series(
            np.linspace(50_000, 55_000, 21),  # +R$5k over the month
            index=pd.bdate_range("2024-03-01", periods=21),
        )
        trades = [
            _make_trade("PETR4.SA", volume=500, exit_price=30.0,
                        pnl=3_000, exit_time="2024-03-15"),
            _make_trade("VALE3.SA", volume=300, exit_price=40.0,
                        pnl=2_000, exit_time="2024-03-22"),
        ]
        # Gross sales = 500×30 + 300×40 = 15_000 + 12_000 = R$27_000 > R$20k
        # Realized P&L = 3_000 + 2_000 = R$5_000
        # Tax = 0.15 × 5_000 = R$750
        # Applied at end of March → net equity decreases by ~R$750 / (R$55k / 1) = 1.36%
        net, tax, hits, _ = apply_monthly_tax(eq, trades)
        assert tax == pytest.approx(750.0, abs=0.01)
        assert hits == 1
        assert net.iloc[-1] < eq.iloc[-1]
        # Net final equity: the tax debit cascades forward (multiplicative).
        # Since the tax month is the last, the scale only applies to the last
        # bar: 55_000 × (1 - 750/55_000) ≈ 54_250.
        assert net.iloc[-1] == pytest.approx(54_250.0, abs=5.0)

    def test_loss_month_no_tax_even_above_threshold(self):
        """Gross > R$20k but month P&L < 0 → no tax."""
        eq = pd.Series(
            np.linspace(50_000, 48_000, 21),  # losing month
            index=pd.bdate_range("2024-03-01", periods=21),
        )
        trades = [_make_trade("PETR4.SA", volume=1000, exit_price=30.0,
                               pnl=-2_000, exit_time="2024-03-15")]
        # Gross = R$30k > R$20k but pnl = -R$2k → no tax
        net, tax, hits, _ = apply_monthly_tax(eq, trades)
        assert tax == 0.0
        assert hits == 0


# ---------------------------------------------------------------------------
# _collect_oos_matrix
# ---------------------------------------------------------------------------
class TestCollectOOSMatrix:
    def test_empty_records_returns_none(self):
        matrix, slugs = _collect_oos_matrix([])
        assert matrix is None
        assert slugs == []

    def test_records_without_returns_are_skipped(self):
        r1 = GridRecord(
            lead="D1", config={}, slug="r1",
            is_metrics=None, oos_metrics=None, fwd_metrics=None,
            oos_daily_returns=None,
        )
        r2 = GridRecord(
            lead="D1", config={}, slug="r2",
            is_metrics=None, oos_metrics=None, fwd_metrics=None,
            oos_daily_returns=np.array([0.01, -0.01, 0.005]),
        )
        matrix, slugs = _collect_oos_matrix([r1, r2])
        assert slugs == ["r2"]
        assert matrix.shape == (3, 1)

    def test_truncates_to_common_length(self):
        r1 = GridRecord(
            lead="D1", config={}, slug="r1",
            is_metrics=None, oos_metrics=None, fwd_metrics=None,
            oos_daily_returns=np.array([0.01, -0.01, 0.005]),
        )
        r2 = GridRecord(
            lead="D4", config={}, slug="r2",
            is_metrics=None, oos_metrics=None, fwd_metrics=None,
            oos_daily_returns=np.array([0.02, 0.0, -0.005, 0.01]),
        )
        matrix, slugs = _collect_oos_matrix([r1, r2])
        assert matrix.shape == (3, 2)  # truncated to min length


# ---------------------------------------------------------------------------
# write_summary
# ---------------------------------------------------------------------------
def _make_metrics(sharpe_net=1.0, cagr_net=0.20, mdd_net=0.15, n_trades=50):
    return SplitMetrics(
        split="OOS", start="2020-01-01", end="2023-12-31", n_bars=1000,
        initial_cash=50_000, final_equity_gross=90_000, final_equity_net=85_000,
        cagr_gross=cagr_net + 0.02, cagr_net=cagr_net,
        sharpe_net=sharpe_net, sortino_net=sharpe_net * 1.3,
        mdd_net=mdd_net, n_trades=n_trades,
        tax_total_brl=500.0, monthly_tax_hits=3, pct_months_exempt=0.93,
    )


class TestWriteSummary:
    def test_summary_includes_header_and_table(self, tmp_path: Path):
        records = [
            GridRecord(
                lead="D1", config={"lookback": 90, "n_top": 20, "sector_cap_pct": 0.25},
                slug="d1_lookback90_n_top20",
                is_metrics=_make_metrics(),
                oos_metrics=_make_metrics(sharpe_net=0.80, cagr_net=0.15, mdd_net=0.20),
                fwd_metrics=_make_metrics(),
                oos_daily_returns=np.random.default_rng(0).normal(0.001, 0.01, 1000),
            ),
        ]
        dsr_results = {"d1_lookback90_n_top20": {"p_value": 0.08, "dsr": 0.92}}

        class _PBOMock:
            pbo = 0.42
            n_blocks = 10
            n_combinations = 252
        pbo_mock = _PBOMock()

        output = tmp_path / "SUMMARY.md"
        write_summary(records, pbo_mock, dsr_results, output, 50_000, early_abort=False)

        text = output.read_text()
        assert "# Phase D-MVP" in text
        assert "**PBO = 0.420**" in text
        assert "PASS" in text
        assert "Proceed to Fase D-ampliada" in text
        assert "D1" in text
        assert "Marginal" in text or "Válido" in text
        assert "advances_fin_ml, p.208-211" in text

    def test_early_abort_written(self, tmp_path: Path):
        records: list[GridRecord] = []
        output = tmp_path / "SUMMARY.md"
        write_summary(records, None, {}, output, 50_000, early_abort=True)

        text = output.read_text()
        assert "ABORT Fase D-ampliada" in text
        assert "BREADTH_NO_WINNER_D" in text


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

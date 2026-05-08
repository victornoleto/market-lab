"""Tests for ``backtest.costs.br_cost_model``: transaction cost + R$20k tax."""

from __future__ import annotations

from datetime import date

import pytest

from market_lab.backtest.costs.br_cost_model import (
    BRCostConfig,
    Sell,
    TaxConfig,
    monthly_tax,
    transaction_cost,
)


# ---------------------------------------------------------------------------
# transaction_cost
# ---------------------------------------------------------------------------
class TestTransactionCost:
    def test_top30_default_fee(self):
        """PETR4 (top 30) at R$100k volume: 0 + 25 emol + 75 half-spread."""
        cost = transaction_cost("PETR4.SA", 100_000.0, "buy")
        assert cost == pytest.approx(100.0, abs=0.01)

    def test_smallcap_default_fee(self):
        """Ticker not in top 30 uses 50 bps spread → 250 half-spread."""
        cost = transaction_cost("PETZ3.SA", 100_000.0, "buy")
        # 0 + 100_000 × 0.00025 (emol=25) + 100_000 × 0.005 / 2 (half=250) = 275
        assert cost == pytest.approx(275.0, abs=0.01)

    def test_corretagem_added(self):
        """R$5 corretagem adds to each side."""
        cfg = BRCostConfig(corretagem_per_side=5.0)
        cost = transaction_cost("PETR4.SA", 100_000.0, "sell", cfg)
        assert cost == pytest.approx(105.0, abs=0.01)

    def test_side_is_symmetric(self):
        """Buy and sell currently cost the same (API stable for future asymm)."""
        buy = transaction_cost("ITUB4.SA", 50_000.0, "buy")
        sell = transaction_cost("ITUB4.SA", 50_000.0, "sell")
        assert buy == sell

    def test_zero_volume_returns_zero(self):
        assert transaction_cost("PETR4.SA", 0.0, "buy") == 0.0

    def test_negative_volume_returns_zero(self):
        assert transaction_cost("PETR4.SA", -1000.0, "buy") == 0.0

    def test_custom_spread_override(self):
        """Custom spread_bps_top30 honored."""
        cfg = BRCostConfig(spread_bps_top30=30.0)
        cost = transaction_cost("PETR4.SA", 100_000.0, "buy", cfg)
        # 0 + 25 emol + 100_000 × 0.003 / 2 = 25 + 150 = 175
        assert cost == pytest.approx(175.0, abs=0.01)

    def test_custom_top30_set(self):
        """If PETZ3 is moved into ``top30_tickers``, spread falls."""
        cfg = BRCostConfig(top30_tickers=frozenset(["PETZ3.SA"]))
        cost = transaction_cost("PETZ3.SA", 100_000.0, "buy", cfg)
        # 0 + 25 emol + 100_000 × 0.0015 / 2 (top30 15 bps half-spread = 75) = 100
        assert cost == pytest.approx(100.0, abs=0.01)


# ---------------------------------------------------------------------------
# monthly_tax
# ---------------------------------------------------------------------------
def _sells(*amounts: float) -> list[Sell]:
    """Convenience: build Sell list with fixed date/ticker."""
    return [
        Sell(when=date(2024, 3, 15), ticker="PETR4.SA", gross_amount=a)
        for a in amounts
    ]


class TestMonthlyTax:
    def test_exempt_at_exactly_threshold(self):
        """Sells totaling exactly R$20k are exempt (≤, not <)."""
        tax = monthly_tax(_sells(20_000.0), realized_pnl_brl=5_000.0)
        assert tax == 0.0

    def test_exempt_below_threshold(self):
        """R$18k sales, R$5k profit → zero tax."""
        tax = monthly_tax(_sells(10_000.0, 8_000.0), realized_pnl_brl=5_000.0)
        assert tax == 0.0

    def test_taxable_above_threshold(self):
        """R$25k sales, R$5k profit → R$750 (15%)."""
        tax = monthly_tax(_sells(15_000.0, 10_000.0), realized_pnl_brl=5_000.0)
        assert tax == pytest.approx(750.0, abs=0.01)

    def test_loss_month_zero_tax(self):
        """R$25k sales but loss → zero tax (carry-forward owned by caller)."""
        tax = monthly_tax(_sells(25_000.0), realized_pnl_brl=-1_000.0)
        assert tax == 0.0

    def test_zero_pnl_above_threshold(self):
        """R$25k sales, R$0 realized → zero tax (no gain to tax)."""
        tax = monthly_tax(_sells(25_000.0), realized_pnl_brl=0.0)
        assert tax == 0.0

    def test_full_gain_taxed_not_only_excess(self):
        """
        Common misconception: only the excess above R$20k is taxable.
        Reality: once you cross R$20k, ALL the month's realized gain is taxable.
        """
        # R$21k sales (just over threshold), R$10k profit
        tax = monthly_tax(_sells(21_000.0), realized_pnl_brl=10_000.0)
        # Tax is 15% of full R$10k, NOT 15% of R$9.5k or some pro-rata.
        assert tax == pytest.approx(1_500.0, abs=0.01)

    def test_empty_sells_list(self):
        """No sells → no gross → exempt by default."""
        tax = monthly_tax([], realized_pnl_brl=5_000.0)
        assert tax == 0.0

    def test_custom_threshold(self):
        """If the legislation changed the threshold (future-proofing)."""
        cfg = TaxConfig(monthly_exemption_brl=35_000.0)
        # R$25k sales, R$5k profit → still exempt under R$35k ceiling
        tax = monthly_tax(_sells(25_000.0), 5_000.0, cfg)
        assert tax == 0.0

    def test_custom_rate(self):
        """If rate changes (e.g., 20% hypothetical)."""
        cfg = TaxConfig(swing_rate=0.20)
        tax = monthly_tax(_sells(25_000.0), realized_pnl_brl=5_000.0, config=cfg)
        assert tax == pytest.approx(1_000.0, abs=0.01)

    def test_many_small_sells_aggregate_correctly(self):
        """20 sells of R$1,500 each = R$30k gross → over threshold."""
        tax = monthly_tax(_sells(*([1_500.0] * 20)), realized_pnl_brl=2_000.0)
        assert tax == pytest.approx(300.0, abs=0.01)


# ---------------------------------------------------------------------------
# Package re-exports
# ---------------------------------------------------------------------------
def test_package_reexports():
    from market_lab.backtest.costs import (
        BRCostConfig as BRCfgExport,
        Sell as SellExport,
        TaxConfig as TaxCfgExport,
        monthly_tax as mt_export,
        transaction_cost as tc_export,
    )

    assert BRCfgExport is BRCostConfig
    assert SellExport is Sell
    assert TaxCfgExport is TaxConfig
    assert mt_export is monthly_tax
    assert tc_export is transaction_cost


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

"""Offline tests for the momentum_v2 study (no live database).

Covers config merge, grid expansion, scoring/simulation determinism, rolling
dominance, the unified result row, validate-phase gates, and an end-to-end
broad -> evolution -> validate funnel run with a synthetic in-memory panel.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from studies.momentum_v2 import config as cfg
from studies.momentum_v2 import grid as gridlib
from studies.momentum_v2 import run as runner
from studies.momentum_v2 import validation as val
from studies.momentum_v2.core import (
    LookbackProfile,
    StrategyConfig,
    apply_br_foreign_annual_tax,
    precompute_scores,
    simulate_config,
    simulate_config_holdings_loop,
)
from studies.momentum_v2.dominance import rolling_relative_equity_metrics
from studies.momentum_v2.filters import FilterResult


# --- fixtures ---------------------------------------------------------------

def _synthetic_prices(n_assets: int = 12, years: int = 22, seed: int = 11) -> pd.DataFrame:
    idx = pd.bdate_range("2003-01-01", periods=252 * years)
    rng = np.random.default_rng(seed)
    cols = [f"A{i:02d}" for i in range(n_assets)]
    drift = np.linspace(0.0002, 0.0010, n_assets)
    out = pd.DataFrame(index=idx, columns=cols, dtype=float)
    for j, col in enumerate(cols):
        rets = rng.normal(drift[j], 0.013, len(idx))
        out[col] = 60.0 * np.cumprod(1.0 + rets)
    return out


def _synthetic_benchmark(idx: pd.DatetimeIndex, seed: int = 99) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    return pd.DataFrame({"SPY": 100.0 * np.cumprod(1.0 + rng.normal(0.0003, 0.01, len(idx)))}, index=idx)


@pytest.fixture(scope="module")
def panel():
    prices = _synthetic_prices()
    volumes = pd.DataFrame(2_000_000.0, index=prices.index, columns=prices.columns)
    bench = _synthetic_benchmark(prices.index)
    return prices, volumes, bench


# --- config & grid ----------------------------------------------------------

def test_config_merge_overrides_filters_and_sets_universe():
    config = cfg.load_config("us_stocks")
    assert config["run"]["universe"] == "us_stocks"
    assert cfg.benchmark_symbol(config) == "SPY"
    # us_stocks.yaml tightens the us_stock filter slice
    merged = cfg.merged_filter_config(config, "us_stocks")
    assert merged["min_history_months"] == 60
    assert merged["min_median_dollar_volume"] == 5_000_000


def test_filter_key_handles_country_asset_and_crypto():
    assert cfg.filter_key("us_stocks") == "us_stock"
    assert cfg.filter_key("br_etfs") == "br_etf"
    assert cfg.filter_key("crypto") == "crypto"


def test_grid_dedups_lookback_independent_score_modes():
    grid_cfg = {
        "score_modes": ["raw_13612", "mom_12_1", "clenow_trend"],
        "lookback_profiles": ["1_3_6_12", "6"],
        "top_n": [5],
        "rebalance_months": [3],
        "rebalance_offsets": [0],
        "weight_modes": ["equal"],
        "absolute_filter": [False],
    }
    configs = gridlib.build_strategy_grid(grid_cfg, universe="us_stocks", assets=tuple("ABCDEF"))
    by_mode = {}
    for c in configs:
        by_mode.setdefault(c.score_mode, set()).add(c.lookback.label)
    assert by_mode["raw_13612"] == {"lb1_3_6_12", "lb6"}
    assert by_mode["mom_12_1"] == {"lb1_3_6_12"}  # emitted once
    assert by_mode["clenow_trend"] == {"lb1_3_6_12"}


def test_grid_offsets_all_expands_to_every_offset():
    grid_cfg = {
        "score_modes": ["raw_13612"], "lookback_profiles": ["6"], "top_n": [5],
        "rebalance_months": [3], "rebalance_offsets": "all", "weight_modes": ["equal"],
        "absolute_filter": [False],
    }
    configs = gridlib.build_strategy_grid(grid_cfg, universe="us_stocks", assets=tuple("ABCDEF"))
    assert sorted(c.rebalance_offset for c in configs) == [0, 1, 2]


# --- scoring & simulation ---------------------------------------------------

def test_vectorized_matches_independent_holdings_loop(panel):
    prices, _vol, _bench = panel
    assets = tuple(prices.columns)
    bundle = precompute_scores(prices, assets, lookback_months=(6,))
    config = StrategyConfig(
        name="x", universe="us_stocks", assets=assets, top_n=3, rebalance_months=3,
        rebalance_offset=0, score_mode="raw_13612", lookback=LookbackProfile("lb6", (6,)),
    )
    sim = simulate_config(prices, bundle, config)
    loop = simulate_config_holdings_loop(prices, bundle, config)
    common = sim.returns.index.intersection(loop.index)
    assert len(common) > 100
    assert float((sim.returns.reindex(common) - loop.reindex(common)).abs().max()) < 1e-9


def test_precompute_includes_mom_12_1_and_all_modes(panel):
    prices, _vol, _bench = panel
    bundle = precompute_scores(prices, tuple(prices.columns), lookback_months=(1, 3, 6, 12))
    assert set(bundle.scores) == {
        "raw_13612", "mom_12_1", "vol_adjusted_13612", "clenow_trend", "composite_mom_lowvol"
    }


def test_rolling_dominance_high_when_strategy_always_beats_benchmark():
    idx = pd.bdate_range("2003-01-01", periods=252 * 16)
    strat = pd.Series(0.0006, index=idx)  # steady winner
    bench = pd.Series(0.0002, index=idx)
    metrics = rolling_relative_equity_metrics(strat, bench)
    assert metrics["rolling_rel_score"] > 0.95


# --- result row & gates -----------------------------------------------------

def test_result_row_marks_research_only_and_carries_dominance(panel):
    prices, _vol, bench = panel
    assets = tuple(prices.columns)
    bundle = precompute_scores(prices, assets, lookback_months=(6,))
    config = StrategyConfig(
        name="x", universe="us_stocks", assets=assets, top_n=3, rebalance_months=3,
        rebalance_offset=0, score_mode="raw_13612", lookback=LookbackProfile("lb6", (6,)),
    )
    sim = simulate_config(prices, bundle, config)
    tax = apply_br_foreign_annual_tax(sim.returns, sim.daily_weights)
    row = val.result_row(config, sim, bench, n_trials=100, ranked_returns=tax.returns, tax_summary=tax.summary)
    assert row["promotion_eligible"] is False
    assert "rolling_rel_score" in row and "gfc_mdd" in row
    assert row["after_tax_cagr"] == row["cagr"]


def test_validate_gates_fail_on_pure_noise():
    rng = np.random.default_rng(3)
    idx = pd.bdate_range("2005-01-01", periods=252 * 6)
    returns_by_name = {
        f"noise_{k}": pd.Series(rng.normal(0.0, 0.01, len(idx)), index=idx) for k in range(5)
    }
    verdict = val.validate_gates(returns_by_name, n_trials=500, bootstrap_resamples=100)
    assert verdict["overall_pass"] is False


# --- end-to-end funnel with a fake data source ------------------------------

def _install_fake_panel(monkeypatch, tmp_path, panel):
    """Point run.STUDY_DIR at tmp and stub _load_panel with synthetic data."""
    prices, volumes, bench = panel
    metadata = pd.DataFrame({"yf_symbol": list(prices.columns), "asset_class": "stock", "country": "us"})
    diagnostics = pd.DataFrame(
        {"yf_symbol": list(prices.columns), "pass_filter": True, "reason": "pass"}
    )

    class _FakeSource:
        def audit(self):
            return pd.DataFrame(
                [{"country": "us", "asset_class": "stock", "n_tickers": len(prices.columns),
                  "first_date": "2003-01-02", "last_date": "2024-12-31",
                  "n_active": len(prices.columns), "n_with_error": 0}]
            )

    def fake_load_panel(config, universe, args):
        result = FilterResult(prices, volumes, metadata, diagnostics)
        start = runner.effective_start(config, args)
        window = runner.window_tag(start)
        return _FakeSource(), len(metadata), result, bench, "SPY", start, window

    monkeypatch.setattr(runner, "STUDY_DIR", tmp_path)
    monkeypatch.setattr(runner, "_load_panel", fake_load_panel)


def _tiny_config():
    config = cfg.load_config("us_stocks")
    config["grid"] = {
        "score_modes": ["raw_13612", "vol_adjusted_13612"],
        "lookback_profiles": ["6", "6_12"],
        "top_n": [3, 5],
        "rebalance_months": [3],
        "rebalance_offsets": [0],
        "weight_modes": ["equal"],
        "absolute_filter": [False],
    }
    config["evolution"]["max_finalists"] = 2
    config["validation"]["bootstrap_resamples"] = 50
    return config


def test_full_funnel_broad_evolution_validate(monkeypatch, tmp_path, panel):
    _install_fake_panel(monkeypatch, tmp_path, panel)
    config = _tiny_config()
    args = runner.parse_args(["--universe", "us_stocks", "--no-plots"])

    udir = tmp_path / "universes" / "us_stocks" / "from_1990"
    assert runner.run_broad(config, "us_stocks", args) == 0
    broad = pd.read_csv(udir / "results" / "broad_results.csv")
    assert len(broad) >= 6
    assert (broad["promotion_eligible"] == False).all()  # noqa: E712
    assert (udir / "reports" / "BROAD_REPORT.md").exists()

    assert runner.run_evolution(config, "us_stocks", args) == 0
    evo = pd.read_csv(udir / "results" / "evolution_results.csv")
    # 2 finalists x 6 overlays x 2 offset modes = up to 24 rows
    assert len(evo) >= 12
    assert set(evo["overlay"].unique()) <= {
        "none", "market_sma200_monthly", "market_sma200_daily", "stock_sma100",
        "market_sma200_monthly_stock_sma100", "market_sma200_daily_stock_sma100",
    }

    assert runner.run_validate(config, "us_stocks", args) == 0
    verdict_md = udir / "reports" / "VALIDATE_REPORT.md"
    assert verdict_md.exists()
    text = verdict_md.read_text(encoding="utf-8")
    assert "promotion_eligible=false" in text


def test_evolution_requires_broad_first(monkeypatch, tmp_path, panel):
    _install_fake_panel(monkeypatch, tmp_path, panel)
    config = _tiny_config()
    args = runner.parse_args(["--universe", "us_stocks", "--no-plots"])
    # no broad run yet -> evolution should refuse
    assert runner.run_evolution(config, "us_stocks", args) == 1


def test_vol_target_caps_at_max_leverage_when_calm():
    from studies.momentum_v2.overlays import vol_target_returns

    idx = pd.bdate_range("2005-01-01", periods=500)
    rng = np.random.default_rng(1)
    # ~8% annualized vol, below the 15% target -> scale clips to 1.0 (no lever up)
    calm = pd.Series(rng.normal(0.0003, 0.005, len(idx)), index=idx, name="s")
    vt = vol_target_returns(calm, target_vol=0.15, lookback_days=63, max_leverage=1.0)
    post = slice(63, None)
    assert np.allclose(vt.iloc[post].to_numpy(), calm.iloc[post].to_numpy())


def test_vol_target_derisks_and_has_no_lookahead():
    from studies.momentum_v2.overlays import vol_target_returns

    idx = pd.bdate_range("2005-01-01", periods=600)
    rng = np.random.default_rng(2)
    # ~63% annualized vol, far above target -> exposure cut, realized vol drops
    wild = pd.Series(rng.normal(0.0, 0.04, len(idx)), index=idx, name="s")
    vt = vol_target_returns(wild, target_vol=0.15, lookback_days=63)
    assert float(vt.iloc[63:].std()) < float(wild.iloc[63:].std())  # de-risked
    assert np.allclose(vt.iloc[:63].to_numpy(), 0.0)  # warmup has no signal -> flat (no look-ahead)


def test_window_tag_namespaces_by_start_year():
    assert runner.window_tag("1990-01-01") == "from_1990"
    assert runner.window_tag("2000-01-01") == "from_2000"
    assert runner.window_tag(None) == "from_all"


def test_topn_view_filters_and_ranks():
    from studies.momentum_v2 import topn_view

    df = pd.DataFrame(
        {
            "name": [f"c{i}" for i in range(5)],
            "mechanism": "raw_13612",
            "lookback_label": "lb6",
            "top_n": [3, 5, 10, 15, 20],
            "rebalance_months": 3,
            "after_tax_cagr": [0.1, 0.2, 0.3, 0.9, 0.95],
            "after_tax_mdd": [-0.4, -0.5, -0.6, -0.8, -0.85],
            "after_tax_sharpe": [0.5, 0.7, 0.9, 1.5, 1.6],
            "after_tax_calmar": [0.3, 0.4, 0.5, 0.9, 0.95],
            "rolling_rel_score": [0.6, 0.7, 0.8, 0.97, 0.98],
        }
    )
    kept = topn_view.filter_by_topn(df, 3, 10)
    assert sorted(kept["top_n"]) == [3, 5, 10]  # 15/20 excluded
    report = topn_view.build_report(df, universe="us_stocks", window="from_1990", min_top_n=3, max_top_n=10, k=20)
    assert "top_n in [3, 10]" in report
    assert "Top 20 by rolling dominance" in report and "after-tax Calmar" in report
    assert "c3" not in report and "c4" not in report  # the top_n 15/20 rows


def test_panel_cache_round_trip(tmp_path, panel):
    prices, volumes, bench = panel
    metadata = pd.DataFrame({"yf_symbol": list(prices.columns), "asset_class": "stock"})
    diagnostics = pd.DataFrame({"yf_symbol": list(prices.columns), "pass_filter": True, "reason": "pass"})
    result = FilterResult(prices, volumes, metadata, diagnostics)
    cache_dir = tmp_path / "cache"
    runner._write_panel_cache(cache_dir, result, bench, total=7136)
    assert runner._cache_ready(cache_dir)
    loaded, loaded_bench, total = runner._read_panel_cache(cache_dir)
    assert total == 7136
    # parquet drops the DatetimeIndex freq attribute; values/index are identical
    pd.testing.assert_frame_equal(loaded.prices, prices, check_freq=False)
    pd.testing.assert_frame_equal(loaded_bench, bench, check_freq=False)

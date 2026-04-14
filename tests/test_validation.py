"""Unit tests for the backtest validation layer (anti-overfit framework).

Scope:
    TestPurgedKFold      — Purged K-Fold CV from AFML ch.7 p.149-154
    TestCPCV             — Combinatorial Purged CV from AFML ch.12 p.219-222

All fixtures are hand-constructed so expected numbers are verifiable without
re-running the code. No network, no real market data. Seeds fixed everywhere.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest


# ---------------------------------------------------------------------------
# Purged K-Fold (AFML ch.7, p.149-154)
# ---------------------------------------------------------------------------


class TestPurgedKFold:
    def test_single_horizon_labels_produces_k_splits(self):
        from ai_trade.backtest.validation.cpcv import purged_kfold_splits

        idx = pd.date_range("2024-01-01", periods=20, freq="D")
        times = pd.Series(idx, index=idx)  # t1 == t0: no overlap, no purge

        splits = list(purged_kfold_splits(times, n_splits=5))

        assert len(splits) == 5
        for train_idx, test_idx in splits:
            assert len(test_idx) == 4  # 20 / 5
            assert len(np.intersect1d(train_idx, test_idx)) == 0

    def test_union_of_test_sets_covers_all_observations(self):
        from ai_trade.backtest.validation.cpcv import purged_kfold_splits

        idx = pd.date_range("2024-01-01", periods=20, freq="D")
        times = pd.Series(idx, index=idx)

        all_test = np.concatenate(
            [test for _, test in purged_kfold_splits(times, n_splits=5)]
        )
        assert sorted(all_test.tolist()) == list(range(20))

    def test_overlap_labels_purges_train_observations_that_cross_test_boundary(self):
        from ai_trade.backtest.validation.cpcv import purged_kfold_splits

        # 20 obs, each label lasts 3 bars → t1_i = t0_i + 2 days.
        # Split 0 = test[0..3] → test_t0_min = 2024-01-01, test_t1_max = 2024-01-06.
        # Train keeps obs i iff (t1_i < test_t0_min) OR (t0_i > test_t1_max).
        # Obs 4 (t0=01-05, t1=01-07): t0 ≤ 01-06 AND t1 ≥ 01-01 → overlap → purged.
        # Obs 5 (t0=01-06): t0 ≤ 01-06 → overlap → purged.
        # Obs 6 (t0=01-07): t0 > 01-06 → kept.
        idx = pd.date_range("2024-01-01", periods=20, freq="D")
        t1 = idx + pd.Timedelta(days=2)
        times = pd.Series(t1, index=idx)

        splits = list(purged_kfold_splits(times, n_splits=5))
        train_idx, test_idx = splits[0]

        assert list(test_idx) == [0, 1, 2, 3]
        assert 4 not in train_idx
        assert 5 not in train_idx
        assert 6 in train_idx
        assert 19 in train_idx

    def test_embargo_extends_purge_beyond_test_end(self):
        from ai_trade.backtest.validation.cpcv import purged_kfold_splits

        idx = pd.date_range("2024-01-01", periods=20, freq="D")
        times = pd.Series(idx, index=idx)  # no label overlap

        # Split 0 = test[0..3]; embargo 0.1 of 20 obs = 2 obs after.
        # Obs 4 and 5 should also be excluded.
        splits = list(purged_kfold_splits(times, n_splits=5, embargo_pct=0.1))
        train_idx, test_idx = splits[0]

        assert list(test_idx) == [0, 1, 2, 3]
        assert 4 not in train_idx
        assert 5 not in train_idx
        assert 6 in train_idx

    def test_middle_split_purges_both_sides(self):
        from ai_trade.backtest.validation.cpcv import purged_kfold_splits

        idx = pd.date_range("2024-01-01", periods=20, freq="D")
        t1 = idx + pd.Timedelta(days=1)  # 2-bar labels
        times = pd.Series(t1, index=idx)

        # Split 2: test[8..11]; test_t0_min=01-09, test_t1_max=01-13 (idx[11]+1 day).
        # Obs 7 (t1=01-09): t1 ≥ 01-09 and t0=01-08 ≤ 01-13 → overlap → purged.
        # Obs 12 (t0=01-13): t0 ≤ 01-13 → overlap → purged.
        # Obs 13 (t0=01-14): t0 > 01-13 → kept.
        splits = list(purged_kfold_splits(times, n_splits=5))
        train_idx, test_idx = splits[2]
        assert list(test_idx) == [8, 9, 10, 11]
        assert 7 not in train_idx
        assert 12 not in train_idx
        assert 13 in train_idx

    def test_invalid_n_splits_raises(self):
        from ai_trade.backtest.validation.cpcv import purged_kfold_splits

        idx = pd.date_range("2024-01-01", periods=20, freq="D")
        times = pd.Series(idx, index=idx)

        with pytest.raises(ValueError, match="n_splits"):
            list(purged_kfold_splits(times, n_splits=1))


# ---------------------------------------------------------------------------
# CPCV (AFML ch.12, p.219-222)
# ---------------------------------------------------------------------------


class TestPBO:
    """CSCV / PBO from AFML ch.11 p.208-211; cross-check Masters CSCV_CORE.CPP."""

    def test_random_iid_returns_give_pbo_near_half_on_average(self):
        """Under the null (iid noise), E[PBO] → 0.5 across independent trials.

        A single matrix can swing wildly (seed=42 alone gives PBO ≈ 0.89 by
        chance) because CSCV partitions share blocks and are NOT independent.
        Averaging over ≥20 fresh matrices brings the estimate within range.
        """
        from ai_trade.backtest.validation.pbo import pbo

        rng = np.random.default_rng(seed=42)
        pbos = [pbo(rng.standard_normal((500, 50)), n_blocks=8).pbo for _ in range(20)]
        assert 0.35 <= np.mean(pbos) <= 0.65

    def test_perfectly_mirrored_returns_give_high_pbo(self):
        """If second half = -first half, IS-best is by construction OOS-worst
        for every partition that isn't itself a union of mirror-block pairs.

        With ``n_blocks=8`` the 4 mirror pairs are (0,4)(1,5)(2,6)(3,7) →
        ``C(4,2) = 6`` zero-sum partitions out of ``C(8,4) = 70`` → upper bound
        on PBO ≈ 64/70 = 0.914. Assert ≥ 0.90 with slack for numerical ties.
        """
        from ai_trade.backtest.validation.pbo import pbo

        rng = np.random.default_rng(seed=42)
        T, N = 400, 20
        returns = rng.standard_normal((T, N))
        returns[T // 2 :] = -returns[: T // 2]

        result = pbo(returns, n_blocks=8)
        assert result.pbo >= 0.90

    def test_dominant_strategy_gives_pbo_near_0(self):
        from ai_trade.backtest.validation.pbo import pbo

        rng = np.random.default_rng(seed=42)
        T, N = 500, 10
        returns = rng.standard_normal((T, N)) * 0.1
        returns[:, 0] += 1.0  # column 0 dominates every possible split

        result = pbo(returns, n_blocks=8)
        assert result.pbo < 0.05

    def test_pbo_in_unit_interval(self):
        from ai_trade.backtest.validation.pbo import pbo

        rng = np.random.default_rng(seed=0)
        result = pbo(rng.standard_normal((200, 10)), n_blocks=6)
        assert 0.0 <= result.pbo <= 1.0

    def test_logits_length_matches_number_of_combinations(self):
        from ai_trade.backtest.validation.pbo import pbo
        from math import comb

        rng = np.random.default_rng(seed=0)
        result = pbo(rng.standard_normal((200, 10)), n_blocks=8)
        assert len(result.logits) == comb(8, 4)

    def test_odd_n_blocks_rounded_down_to_even(self):
        from ai_trade.backtest.validation.pbo import pbo

        rng = np.random.default_rng(seed=0)
        result = pbo(rng.standard_normal((200, 10)), n_blocks=9)
        assert result.n_blocks == 8

    def test_requires_multiple_strategies(self):
        from ai_trade.backtest.validation.pbo import pbo

        with pytest.raises(ValueError, match="at least 2"):
            pbo(np.ones((100, 1)), n_blocks=4)

    def test_gate_rejects_when_above_threshold(self):
        """PBO > 0.5 → reject. AFML rule p.208-211."""
        from ai_trade.backtest.validation.pbo import pbo_gate

        assert pbo_gate(0.6) == "reject"
        assert pbo_gate(0.5) == "reject"  # boundary inclusive on the bad side
        assert pbo_gate(0.3) == "pass"


class TestDSR:
    """Deflated Sharpe Ratio from AFML ch.14 p.273-275."""

    def test_psr_equals_half_when_observed_equals_benchmark(self):
        """PSR[SR* = SR_hat] = Φ(0) = 0.5 (zero numerator)."""
        from ai_trade.backtest.validation.dsr import psr

        rng = np.random.default_rng(seed=0)
        returns = rng.standard_normal(500) * 0.01 + 0.001
        from ai_trade.backtest.validation.dsr import sharpe_periodic

        sr = sharpe_periodic(returns)
        assert psr(returns, benchmark=sr) == pytest.approx(0.5, abs=1e-10)

    def test_psr_increases_with_higher_observed_sharpe(self):
        from ai_trade.backtest.validation.dsr import psr

        rng = np.random.default_rng(seed=0)
        noise = rng.standard_normal(500) * 0.01
        low_sr = noise + 0.0005  # weak alpha
        high_sr = noise + 0.005  # strong alpha

        assert psr(high_sr, benchmark=0.0) > psr(low_sr, benchmark=0.0)

    def test_psr_in_unit_interval(self):
        from ai_trade.backtest.validation.dsr import psr

        rng = np.random.default_rng(seed=0)
        returns = rng.standard_normal(300) * 0.01
        for bench in [-2.0, -0.5, 0.0, 0.5, 2.0]:
            p = psr(returns, benchmark=bench)
            assert 0.0 <= p <= 1.0

    def test_expected_max_sharpe_monotone_in_n(self):
        from ai_trade.backtest.validation.dsr import expected_max_sharpe

        # E[SR_max] should grow with N (more trials → higher max of iid draws).
        values = [expected_max_sharpe(n) for n in [2, 5, 10, 100, 1000]]
        assert all(b > a for a, b in zip(values, values[1:]))

    def test_expected_max_sharpe_matches_monte_carlo(self):
        """Formula from AFML p.222 must track the Monte Carlo max of N iid N(0,1)."""
        from ai_trade.backtest.validation.dsr import expected_max_sharpe

        rng = np.random.default_rng(seed=0)
        for n in [5, 10, 100, 1000]:
            mc = np.mean([rng.standard_normal(n).max() for _ in range(3000)])
            formula = expected_max_sharpe(n)
            assert abs(formula - mc) / mc < 0.05

    def test_expected_max_sharpe_rejects_n_less_than_2(self):
        from ai_trade.backtest.validation.dsr import expected_max_sharpe

        with pytest.raises(ValueError):
            expected_max_sharpe(1)

    def test_dsr_sits_near_half_when_observed_matches_benchmark(self):
        """A Sharpe exactly at the multiple-testing benchmark gives DSR ≈ 0.5."""
        from ai_trade.backtest.validation.dsr import dsr, expected_max_sharpe

        T = 500
        rng = np.random.default_rng(seed=0)
        returns = rng.standard_normal(T) * 0.01
        # Force observed periodic SR to equal the iid-null benchmark for N=1000.
        target_sr = expected_max_sharpe(1000, var_sharpe=1.0 / (T - 1))
        returns = returns - returns.mean() + target_sr * returns.std(ddof=0)

        result = dsr(returns, n_trials=1000)
        assert 0.45 <= result.dsr <= 0.55

    def test_dsr_accepts_truly_exceptional_sharpe(self):
        from ai_trade.backtest.validation.dsr import dsr

        rng = np.random.default_rng(seed=0)
        returns = rng.standard_normal(500) * 0.01 + 0.003  # strong alpha
        result = dsr(returns, n_trials=5)
        assert result.dsr > 0.95

    def test_dsr_result_has_p_value_and_benchmark(self):
        from ai_trade.backtest.validation.dsr import dsr

        rng = np.random.default_rng(seed=0)
        result = dsr(rng.standard_normal(300) * 0.01, n_trials=10)
        assert 0.0 <= result.dsr <= 1.0
        assert 0.0 <= result.p_value <= 1.0
        assert result.p_value == pytest.approx(1 - result.dsr)
        assert result.n_trials == 10
        assert result.benchmark_sharpe > 0

    def test_sharpe_periodic_matches_mean_over_std(self):
        from ai_trade.backtest.validation.dsr import sharpe_periodic

        returns = np.array([0.01, -0.02, 0.015, 0.005, -0.01, 0.02])
        expected = returns.mean() / returns.std(ddof=0)
        assert sharpe_periodic(returns) == pytest.approx(expected)

    def test_sharpe_annualized_scales_by_sqrt_periods(self):
        from ai_trade.backtest.validation.dsr import sharpe_annualized, sharpe_periodic

        rng = np.random.default_rng(seed=0)
        returns = rng.standard_normal(252) * 0.01 + 0.0005
        base = sharpe_periodic(returns)
        annual = sharpe_annualized(returns, periods_per_year=252)
        assert annual == pytest.approx(base * np.sqrt(252))


class TestWalkForward:
    """Rolling IS/OOS splits with reoptimization (Pardo; Kaufman; Masters)."""

    def test_number_of_windows_matches_formula(self):
        """``n_windows = floor((T - is - oos) / step) + 1``."""
        from ai_trade.backtest.validation.walk_forward import walk_forward_splits

        # T=1000, is=500, oos=100, step=100 → (1000-500-100)//100 + 1 = 5
        splits = list(walk_forward_splits(n_obs=1000, is_size=500, oos_size=100, step=100))
        assert len(splits) == 5

    def test_first_window_starts_at_zero(self):
        from ai_trade.backtest.validation.walk_forward import walk_forward_splits

        (train, test), *_ = list(
            walk_forward_splits(n_obs=1000, is_size=500, oos_size=100, step=100)
        )
        assert train == range(0, 500)
        assert test == range(500, 600)

    def test_subsequent_windows_slide_by_step(self):
        from ai_trade.backtest.validation.walk_forward import walk_forward_splits

        splits = list(walk_forward_splits(n_obs=1000, is_size=500, oos_size=100, step=100))
        assert splits[1] == (range(100, 600), range(600, 700))
        assert splits[4] == (range(400, 900), range(900, 1000))

    def test_train_and_test_never_overlap(self):
        from ai_trade.backtest.validation.walk_forward import walk_forward_splits

        for train, test in walk_forward_splits(
            n_obs=500, is_size=200, oos_size=50, step=25
        ):
            train_set = set(train)
            test_set = set(test)
            assert train_set.isdisjoint(test_set)

    def test_last_window_does_not_exceed_data(self):
        from ai_trade.backtest.validation.walk_forward import walk_forward_splits

        *_, last = list(walk_forward_splits(n_obs=500, is_size=200, oos_size=50, step=25))
        assert last[1].stop <= 500

    def test_raises_if_data_too_short_for_one_window(self):
        from ai_trade.backtest.validation.walk_forward import walk_forward_splits

        with pytest.raises(ValueError, match="at least"):
            list(walk_forward_splits(n_obs=100, is_size=200, oos_size=50, step=10))

    def test_raises_on_invalid_step(self):
        from ai_trade.backtest.validation.walk_forward import walk_forward_splits

        with pytest.raises(ValueError):
            list(walk_forward_splits(n_obs=500, is_size=100, oos_size=50, step=0))

    # -- gate ------------------------------------------------------------

    def test_gate_passes_when_rule5_satisfied(self):
        """Rule #5: ≥8 windows, ≥6 profitable, max DD ≤ 25%."""
        from ai_trade.backtest.validation.walk_forward import walk_forward_gate

        oos_returns_per_window = [0.05] * 7 + [-0.05]  # 7 profitable out of 8
        drawdowns = [0.10] * 8  # all DD under 25%
        assert walk_forward_gate(oos_returns_per_window, drawdowns) == "pass"

    def test_gate_rejects_when_too_few_windows(self):
        from ai_trade.backtest.validation.walk_forward import walk_forward_gate

        assert (
            walk_forward_gate([0.1] * 5, [0.05] * 5) == "reject"
        )  # only 5 windows, need ≥8

    def test_gate_rejects_when_drawdown_exceeds_threshold(self):
        from ai_trade.backtest.validation.walk_forward import walk_forward_gate

        assert (
            walk_forward_gate([0.05] * 8, [0.10] * 7 + [0.30]) == "reject"
        )  # one DD at 30% > 25%

    def test_gate_rejects_when_too_few_profitable(self):
        from ai_trade.backtest.validation.walk_forward import walk_forward_gate

        assert walk_forward_gate([0.05] * 5 + [-0.05] * 3, [0.10] * 8) == "reject"


class TestPermutation:
    """MCPT from Masters' ``MCPT_TRN.CPP`` / ``MCPT_BARS.CPP``."""

    def test_permuted_prices_preserve_first_and_last(self):
        from ai_trade.backtest.validation.permutation import permute_prices

        rng = np.random.default_rng(seed=0)
        prices = np.log(np.cumsum(rng.standard_normal(100) + 0.01) + 100)
        permuted = permute_prices(prices, rng)
        assert permuted[0] == pytest.approx(prices[0])
        assert permuted[-1] == pytest.approx(prices[-1])

    def test_permuted_prices_preserve_return_distribution(self):
        """Sorted changes must match — only their order is shuffled."""
        from ai_trade.backtest.validation.permutation import permute_prices

        rng = np.random.default_rng(seed=0)
        prices = np.cumsum(rng.standard_normal(200))
        permuted = permute_prices(prices, rng)

        orig_changes = np.sort(np.diff(prices))
        perm_changes = np.sort(np.diff(permuted))
        np.testing.assert_allclose(orig_changes, perm_changes)

    def test_permuted_prices_actually_shuffle_interior(self):
        from ai_trade.backtest.validation.permutation import permute_prices

        rng = np.random.default_rng(seed=0)
        prices = np.cumsum(rng.standard_normal(200))
        permuted = permute_prices(prices, rng)
        # Overwhelmingly unlikely to match any interior point by chance
        n_same = int(np.sum(np.isclose(permuted[1:-1], prices[1:-1])))
        assert n_same < 5

    def test_mcpt_p_value_rejects_ar1_momentum_under_null_of_iid(self):
        """AR(1) prices have serial autocorr; shuffling destroys it → low p-value."""
        from ai_trade.backtest.validation.permutation import monte_carlo_permutation_test

        rng = np.random.default_rng(seed=42)
        # Strong AR(1) returns: r_t = 0.5·r_{t-1} + ε_t
        T = 300
        eps = rng.standard_normal(T)
        r = np.zeros(T)
        for t in range(1, T):
            r[t] = 0.5 * r[t - 1] + eps[t]
        prices = np.cumsum(r)

        def lag1_autocorr(p):
            d = np.diff(p)
            return float(np.corrcoef(d[:-1], d[1:])[0, 1])

        result = monte_carlo_permutation_test(
            prices, lag1_autocorr, n_permutations=200, rng=rng
        )
        assert result.p_value < 0.05

    def test_mcpt_p_value_for_iid_returns_is_uniform_ish(self):
        """Under the null (iid returns), p-value distribution is ≈ Uniform[0, 1]."""
        from ai_trade.backtest.validation.permutation import monte_carlo_permutation_test

        rng = np.random.default_rng(seed=0)
        p_values = []
        for _ in range(30):
            prices = np.cumsum(rng.standard_normal(200))

            def lag1_autocorr(p):
                d = np.diff(p)
                return float(np.corrcoef(d[:-1], d[1:])[0, 1])

            r = monte_carlo_permutation_test(
                prices, lag1_autocorr, n_permutations=100, rng=rng
            )
            p_values.append(r.p_value)
        # Mean of Uniform[0, 1] is 0.5; allow wide tolerance for 30 draws.
        assert 0.30 <= np.mean(p_values) <= 0.70

    def test_mcpt_p_value_in_unit_interval(self):
        from ai_trade.backtest.validation.permutation import monte_carlo_permutation_test

        rng = np.random.default_rng(seed=0)
        prices = np.cumsum(rng.standard_normal(100))
        result = monte_carlo_permutation_test(
            prices, lambda p: float(p[-1] - p[0]), n_permutations=50, rng=rng
        )
        assert 0.0 <= result.p_value <= 1.0

    def test_mcpt_deterministic_with_seed(self):
        from ai_trade.backtest.validation.permutation import monte_carlo_permutation_test

        def stat(p):
            d = np.diff(p)
            return float(np.corrcoef(d[:-1], d[1:])[0, 1])

        rng1 = np.random.default_rng(seed=123)
        rng2 = np.random.default_rng(seed=123)
        rng_data = np.random.default_rng(seed=7)
        prices = np.cumsum(rng_data.standard_normal(100))
        r1 = monte_carlo_permutation_test(prices, stat, n_permutations=50, rng=rng1)
        r2 = monte_carlo_permutation_test(prices, stat, n_permutations=50, rng=rng2)
        assert r1.p_value == r2.p_value

    def test_mcpt_result_contains_observed_and_distribution(self):
        from ai_trade.backtest.validation.permutation import monte_carlo_permutation_test

        rng = np.random.default_rng(seed=0)
        prices = np.cumsum(rng.standard_normal(100))
        r = monte_carlo_permutation_test(
            prices, lambda p: float(p[-1] - p[0]), n_permutations=50, rng=rng
        )
        assert hasattr(r, "observed")
        assert len(r.permuted_statistics) == 50


class TestCPCV:
    def test_path_count_formula_N6_k2_gives_5_paths(self):
        """φ[N, k] = C(N,k) · k / N. For N=6, k=2: C(6,2)=15, φ=5 [p.219-220]."""
        from ai_trade.backtest.validation.cpcv import cpcv_path_count

        assert cpcv_path_count(6, 2) == 5

    def test_path_count_formula_N10_k2_gives_9_paths(self):
        from ai_trade.backtest.validation.cpcv import cpcv_path_count

        # C(10, 2) = 45, k/N = 2/10 → φ = 9
        assert cpcv_path_count(10, 2) == 9

    def test_path_count_invalid_k_raises(self):
        from ai_trade.backtest.validation.cpcv import cpcv_path_count

        with pytest.raises(ValueError):
            cpcv_path_count(5, 6)
        with pytest.raises(ValueError):
            cpcv_path_count(5, 0)

    def test_generates_combinations_of_test_groups(self):
        """N=6, k=2 → C(6,2) = 15 splits. [p.219]"""
        from ai_trade.backtest.validation.cpcv import cpcv_splits

        idx = pd.date_range("2024-01-01", periods=60, freq="D")
        times = pd.Series(idx, index=idx)

        splits = list(cpcv_splits(times, n_groups=6, n_test_groups=2))
        assert len(splits) == 15

    def test_each_group_appears_in_phi_test_sets(self):
        """Each group belongs to φ[N,k] test sets by symmetry. [p.219-220]"""
        from ai_trade.backtest.validation.cpcv import cpcv_splits

        idx = pd.date_range("2024-01-01", periods=60, freq="D")
        times = pd.Series(idx, index=idx)

        splits = list(cpcv_splits(times, n_groups=6, n_test_groups=2))
        # 60 obs → 10 per group. For each group, count splits that include it.
        counts = np.zeros(6, dtype=int)
        for _, test_idx in splits:
            for group in range(6):
                group_start = group * 10
                group_end = group_start + 10
                if np.any((test_idx >= group_start) & (test_idx < group_end)):
                    counts[group] += 1

        # Each group in exactly φ = 5 test sets
        assert list(counts) == [5, 5, 5, 5, 5, 5]

    def test_train_and_test_never_overlap(self):
        from ai_trade.backtest.validation.cpcv import cpcv_splits

        idx = pd.date_range("2024-01-01", periods=60, freq="D")
        times = pd.Series(idx, index=idx)

        for train_idx, test_idx in cpcv_splits(times, n_groups=6, n_test_groups=2):
            assert len(np.intersect1d(train_idx, test_idx)) == 0

    def test_test_sets_concatenate_two_groups_worth_of_observations(self):
        from ai_trade.backtest.validation.cpcv import cpcv_splits

        idx = pd.date_range("2024-01-01", periods=60, freq="D")
        times = pd.Series(idx, index=idx)

        for _, test_idx in cpcv_splits(times, n_groups=6, n_test_groups=2):
            assert len(test_idx) == 20  # 2 groups × 10 obs

    def test_purge_and_embargo_applied_per_combination(self):
        """With overlapping labels, each test set's span purges train obs. [p.149-154]"""
        from ai_trade.backtest.validation.cpcv import cpcv_splits

        idx = pd.date_range("2024-01-01", periods=60, freq="D")
        t1 = idx + pd.Timedelta(days=2)  # 3-bar labels
        times = pd.Series(t1, index=idx)

        splits = list(cpcv_splits(times, n_groups=6, n_test_groups=2, embargo_pct=0.05))

        # First combination = groups (0, 1) → test[0..19]; h = int(0.05 * 60) = 3.
        # test_t1_max = idx[19] + 2 = 2024-01-22.
        # Obs 20 (t0=01-21, t1=01-23): label overlaps → purged.
        # Obs 21 (t0=01-22): t0 ≤ 01-22 → overlap → purged.
        # Obs 22: t0=01-23 > 01-22 no overlap, but position 22 in embargo (20,21,22).
        # Obs 23: position 23 outside embargo, no label overlap → kept.
        train_idx, test_idx = splits[0]
        assert list(test_idx) == list(range(20))
        assert 20 not in train_idx
        assert 21 not in train_idx
        assert 22 not in train_idx
        assert 23 in train_idx
        assert 59 in train_idx

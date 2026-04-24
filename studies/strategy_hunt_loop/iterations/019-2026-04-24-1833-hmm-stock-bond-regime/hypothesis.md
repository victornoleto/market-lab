# Iteration 019 — HMM stock-bond correlation regime rotation on iter 016 base (WITH pre-val screen)

## Hypothesis

Iter 016 (`ntsx_vm_vt15_L21_cap20`, hunt-loop top-K #1, 79/100 STRONG, 4/5
winner) locks a **single** 60:40 equity:bond ratio. The stock-bond
correlation ρ(SPY, IEF) is **time-varying**: it spends long stretches
negative (post-GFC ZIRP era, most of 2009-2020) — the regime where
60:40 diversification is maximal — but flips positive in inflation
regimes (2022 rate-hike cycle, pre-2000 bond-equity positive
correlation era per Ilmanen Ch.1) where 60:40 degenerates to a levered
single-factor bet.

A **2-state Hidden Markov Model** fit to 60-day rolling ρ(SPY, IEF) can
separate:

- **Regime A (ρ < 0 — negative correlation)**: diversification works
  → hold iter 016 60:40 stack at full target_vol=0.15, max_leverage=2.0
- **Regime B (ρ ≥ 0 — positive correlation)**: diversification fails
  → shift to defensive **30:70** ratio (smaller equity, larger bond)
  + same vol-target, same max_leverage cap

The structural novelty vs iter 009/012/013/014 (all linear signals that
cointegrated with σ²_port): HMM state is **discrete** ∈ {0, 1}, not
continuous, so it cannot be dominated by the same rolling-variance
signal the vol-target already uses. Iter 014's pre-val screen will tell
us empirically whether discretization is sufficient — if |ρ(HMM state,
σ²_port(iter 016))| > 0.30 on > 20% of bars on ANY dataset, we abort
before spending DSR budget.

## Primary citation

`[regime_change, p.14-17, ch.2]` (Chen & Tsang, 2021, *Detecting
Regime Change in Computational Finance*, CRC Press) — HMM as the
canonical probabilistic tool for inferring hidden market-regime state
from observable returns / correlations; 2-state HMM is specifically
recommended and demonstrated throughout their empirical chapters
(ch.2-6). They explicitly frame the use case as "consistently reduce
maximum drawdown in algorithmic trading" via regime-conditional
position sizing `[regime_change, p.89-91, ch.6]`.

## Additional citations

- `[ml_for_algo_trading, ch.20 p.625, ch.9 p.274-275]` — HMM
  implementation / training in quant pipelines (Baum-Welch /
  Expectation-Maximization) and the TrainSize ≥ 10 years convention
  for multi-regime coverage.
- `[advances_fin_ml, p.208-211]` — PBO; vacuous PASS at N=1
  pre-committed cfg (we test ONE cfg, not a grid).
- `[advances_fin_ml, p.222-223]` — DSR with cumulative n_trials
  (iter 019 adds +1 new cfg → cumulative advances 4264 → 4265).
- `[advances_fin_ml, p.31-34]` — Cross-lib parity for new simulator.
- `[advances_fin_ml, p.162-164]` — Lag-1-bar HMM state and ρ_60
  features (no look-ahead; state inferred from `returns[:t-1]` used at
  bar `t`).
- `[risk_parity, p.10-11, ch.1]` + `[risk_parity, p.80-84, ch.4]` —
  Naïve risk parity + negative stock-bond correlation as
  diversification driver; state A mechanism.
- `[ilmanen_expected_returns, ch.1-3]` — Stock-bond correlation is
  regime-dependent: negative in low-inflation / flight-to-quality
  regimes, positive in high-inflation / simultaneous-rate-shock
  regimes (e.g., 2022).
- Web: Ang, A., & Bekaert, G. (2002). "Regime Switches in Interest
  Rates." *Journal of Business & Economic Statistics* 20(2), 163-182.
  DOI [10.1198/073500102317351930](https://doi.org/10.1198/073500102317351930) —
  canonical regime-switching framework for fixed-income;
  complementary framing to Chen-Tsang HMM approach.

## Edge source

SPY 1x buy-hold carries **single-factor equity risk** and cannot hedge
inflation-shock regimes (2022 drawdown −25% for SPY). Iter 016's
static 60:40 stack **improves** diversification during negative
correlation regimes (2009-2020 most bars) but **degrades** during
positive correlation regimes (2022 both legs down together). HMM
regime rotation captures the REGIME SHIFT itself — conditioning equity
exposure on whether the bond leg is diversifying — which the static
iter 016 stack cannot capture by construction.

## Datasets

- **educational** (SPYSIM synth 1986-2026, SPY+IEF post-2006): primary
  multi-regime test; includes 2022 rate-hike regime and pre-GFC
  correlation baseline. IEF-inception-aligned from 2006-01-03.
- **spy_real** (SPY+IEF, 2009-06-25 → 2026-04-20): 17y window with
  the 2022 positive-correlation shock as the critical stress test.
- **ndx_real** (QQQ+IEF, 2010-02-12 → 2026-04-20): 16y tech-heavy
  variant; QQQ has higher σ so regime mis-timing has larger magnitude
  impact.

## Kill criteria (pre-committed)

Each kill is individually triggering — hitting ANY one marks the
hypothesis as falsified and triggers specific dead-end documentation.

- **Kill #0 (pre-val screen, cheapest)**: If `|corr_60d(HMM_state_lag1,
  σ²_port_iter016_lag1)| > 0.30` on `> 20%` of bars on **any** of the 3
  datasets, abort before training the final HMM. Write partial
  final_report.md documenting that HMM discretization does NOT break
  the σ²_port cointegration class; add 1-line to DEAD_ENDS.md "HMM
  state-overlay on iter 016 blend". Score = NEAR_FAIL (~25/100) by
  default (zero Sharpe improvement + discovered dead-end).

- **Kill #1 (Sharpe regress)**: Post-cost Sharpe of iter 019 strategy
  < iter 016's **post-funding-cost** Sharpe − 0.03 on ≥ 2/3 datasets
  (i.e., < 0.858 edu, < 1.035 spy, < 1.110 ndx). This means HMM
  rotation actively HURTS. Close 2-state HMM on stock-bond ρ_60 with
  N=2 states and 30:70 defensive response.

- **Kill #2 (DSR regress worse than iter 018)**: Worst DSR p-value
  across datasets ≥ 0.40. Iter 018 reached 0.370 worst — if we cannot
  even maintain that, the added cfg trial for no Sharpe uplift has
  moved backward.

- **Kill #3 (Turnover blows costs)**: If mean turnover > 20× / year
  (iter 016 was 4.6-7.4 / yr), the regime-switching cost absorbs
  whatever edge the signal provides. HMM state-switches should be
  rare (< 1 / month); more means we're picking up noise.

- **Kill #4 (Single-dataset-only edge)**: If Sharpe_iter019 >
  Sharpe_iter018 on ≤ 1 / 3 datasets (not cross-dataset), cross-ds
  requirement fails. Don't claim edge on one dataset — mandate's
  cross-dataset rule is non-negotiable.

## Expected budget

- **Configs to test:** 1 pre-committed cfg
  (`ntsx_vm_hmm_rho_60_def30_70` — 60d rolling ρ, 2-state HMM, 30:70
  defensive). NO grid, NO sweep. cumulative_n_trials: 4264 → 4265.
- **Wall-time:** ~90 minutes total
  - Pre-val screen: ~20 min (fast abort path if triggered)
  - HMM training + simulation: ~30 min
  - Gates + numpy reference + tests: ~20 min
  - Reports + plots + memory update: ~20 min
- **Files to create:**
  - `hmm_regime_rotation.py` — HMM fit + state inference + dynamic
    weight rotation (pandas/hmmlearn or hand-rolled EM)
  - `numpy_reference_hmm.py` — cross-lib parity check (hand-rolled
    numpy HMM forward-backward)
  - `run_backtests.py` — orchestrator with pre-val screen short-circuit
  - `prevalue_screen.py` — separable pre-val logic (keeps it
    auditable)
  - `compute_gates_and_score.py` — 7-gate battery + scoring.py call
  - `tests/test_hmm_regime_rotation.py` — TDD for HMM logic + parity
  - `results.json`, `verdict.json`, `final_report.md`
  - `plot_vs_benchmark_spy_real.png`, `plot_vs_benchmark_ndx_real.png`

## Implementation plan

### Stage 3a — Pre-val screen (gate-before-spend, mandatory)

1. Load SPY+IEF (or QQQ+IEF) daily returns for each of the 3 datasets.
2. Compute `rho_60[t] = rolling_corr(r_eq, r_bd, 60).shift(1)` — 60d
   rolling correlation, lagged 1 bar to avoid look-ahead.
3. Fit preliminary 2-state HMM on `rho_60` (Gaussian emissions); infer
   `state[t] ∈ {0, 1}`, lag by 1 bar.
4. Load iter 016's σ²_port[t] (recompute from cfg = iter 016 exactly)
   for the same dataset / window.
5. Compute `corr_60d(state_lag1, σ²_port_lag1)` — the "overlap" test.
   Also compute `mean(|state_lag1 - 0.5| × sign(σ²_port_lag1 -
   median))` as robustness backup.
6. **If** `rolling_60d |corr| > 0.30` on `> 20%` of bars on any of
   the 3 datasets → **ABORT** (Kill #0 triggered). Write partial
   report, add dead-end, exit.
7. **If** screen passes → proceed to Stage 3b.

### Stage 3b — HMM regime rotation strategy (conditional on screen pass)

1. HMM model: 2 hidden states, Gaussian emissions on 60d rolling ρ
   feature. Training window = first 252 bars (1 year) of each
   dataset; state inferred on remaining bars (strict walk-forward —
   NO peek at future data).
2. Dynamic weight logic:
   ```
   if state_lag1[t] == state_with_neg_rho_mean:
       eq_weight[t], bd_weight[t] = 0.6, 0.4   # iter 016 baseline
   else:
       eq_weight[t], bd_weight[t] = 0.3, 0.7   # defensive
   ```
3. Everything else of iter 016 wrapper preserved: target_vol=0.15,
   lookback=21 for σ²_port, max_leverage=2.0, daily rebalance, 2 bps
   per-leg cost, funding-cost modeled per iter 018 (SHV Tbill lagged).
4. Save `results.json` with per-dataset: Sharpe, CAGR, MDD, turnover,
   state-dwell statistics, regime-conditioned returns, and
   `returns_series` key (net_returns by date) for plot helper.

### Stage 3c — Cross-lib parity (numpy reference)

1. Hand-rolled forward-backward HMM in pure numpy (no hmmlearn).
2. Compare: state inference, regime-conditioned CAGR.
3. Gate G7: |CAGR_pandas − CAGR_numpy| < 3 pp per dataset.

### Stage 3d — Tests + baseline

1. TDD: `tests/test_hmm_regime_rotation.py`:
   - Deterministic toy data: known 2-regime switch every 100 bars →
     HMM recovers state with > 0.95 accuracy.
   - Lag-1 bar check: state at bar t uses only returns[:t].
   - Baseline: with HMM ALWAYS regime A (state=0), strategy returns
     match iter 016 exactly (mechanism reduces to iter 016 if no
     regime switch).
   - Cross-lib: pandas and numpy implementations agree ±3pp.
2. Run full pytest suite (baseline ~796 collected) — must not
   reduce passing count.

### Stage 4 — Gates + score

1. 7-gate battery per dataset using existing validators (PBO / DSR /
   WF / OOS 70:30 / FWD post-2020 / Bootstrap 99.9% CI / Cross-lib).
2. DSR uses cumulative_n_trials = **4265** (iter 018's 4264 + 1 new
   cfg this iter).
3. Call `scoring.score_strategy(...)` to compute ScoreResult.
4. Produce `verdict.json` per canonical schema.

### Stage 5 — Reports + memory

1. `final_report.md` honest verdict.
2. `plot_helper.py` to produce PNGs for spy_real / ndx_real.
3. `BASE_MEMORY.md` update: bump iteration, cumulative_n_trials,
   append 6-field entry; top-K update if score ≥ 74 (enters top-K
   ties with iter 008/010).
4. `DEAD_ENDS.md` if kill #0 or #1 triggered.

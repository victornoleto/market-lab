# Phase 3.6 Family H — Adaptive-Markets regime-switching (honest validation)

**Date:** 2026-04-23  |  **Branch:** `phase3.6/swing-winner-hunt-20260423`
**Engine:** F2-patched (commit `7b90a8f` — `prev_weight × next_return`)
**Broker path modelled:** Banco Inter Internacional (plan §3.2) —
zero commission on US ETFs, 2 bps spread + 1 bps slippage on traded
notional per rebalance, BR 15% capital-gains tax on positive monthly
net return.
**Windows:** IS 2004-11-18 → 2017-12-31 (trimmed to GLD inception) |
OOS 2018-01-01 → 2023-12-31 | FWD 2024-01-01 → 2026-04-14

## Verdict: **FAIL**

The AMH regime-switching strategy **fails 8 of 14 gate rows** under
the honest engine on a 3-asset SPY/TLT/GLD panel (the 14 rows are gates
1-13 with gate 1 split into OOS-bootstrap and FULL-bootstrap arms;
plan §5 counts it as a single composite gate so the effective tally
is 6 PASS / 8 FAIL over 14 arms, or 5 PASS / 7 FAIL over 13 composite
gates once gate 1 is collapsed — either way, well short of WINNER=13/13
and PARTIAL=12/13). OOS Sharpe lands at
**0.69** (gate 2 ≥ 1.5 → FAIL), OOS CAGR is **9.47%** (gate 3 CDI floor
13% → FAIL), and the bootstrap 99.9% CI on OOS Sharpe straddles zero at
**[−0.42, +2.05]** (gate 1 FAIL). Gate 12 DSR p-value over the 18-cell
grid is **0.56** (< 0.05 → FAIL), Gate 13 cost×2 OOS Sharpe is **0.69**
(> 1.0 → FAIL), Gate 8 IR vs SPY is **−0.17** (gate ≥ 0.3 → FAIL), and
Gate 6 walk-forward max-window DD is **36.95%** (gate ≤ 30% → FAIL)
despite profitable-ratio being 8/8.

Positive signals: OOS MaxDD **−21.18%** passes gate 4 (binding cap
−25%), FWD Sharpe **1.21** passes gate 5, median hold **42 trading
days** passes gate 7, PBO across 18 configs is **0.194** (gate 11 <
0.5 → PASS), data concordance vs testfolio GLDSIM Δ=0.45pp passes gate
10, and cross-lib concordance Δ=0.000pp passes gate 9. But the edge
signals (gates 1, 2, 3, 12, 13) all undercut — the strategy is
risk-controlled but edge-starved, the same diagnosis seen in Family B
(RP inverse-vol) and Family C (GTAA). OOS CAGR 9.47% sits ~2.5pp below
SPY buy-hold (12.00%) and ~3.5pp below the CDI soft-floor.

**Mandate §7 and strategy docs stay UNTOUCHED** — FAIL means no
promotion, no draft entry in `docs/.pending/`. No structural failure
either (HMM converged, regime distribution non-degenerate: low_vol
66.6% / crisis 33.4% on IS).

## Top-line metrics

| Split | Bars | Sharpe | CAGR | MaxDD |
|-------|-----:|-------:|-----:|------:|
| IS (2004-11-18 → 2017-12-31)   | 3302 | 0.526 |  7.59% | −21.18%* |
| OOS (2018-01-01 → 2023-12-31)  | 1509 | 0.692 |  9.47% | −21.18%  |
| FWD (2024-01-01 → 2026-04-14)  |  572 | 1.207 | 16.27% |  −7.42%  |
| FULL (2004-11-18 → 2026-04-15) | 5383 | 0.634 |  9.59% | −27.32%  |
| **SPY OOS benchmark**          | 1509 | 0.658 | 12.00% | −33.70%  |
| **SPY FWD benchmark**          |  572 | 1.188 | 19.60% | −18.76%  |

*IS MDD is reported from within-IS drawdowns only.

Portfolio underperforms SPY buy-hold in OOS by **−2.5 pp CAGR** with
~1.6× better drawdown (−21.2% vs −33.7%); IR vs SPY is **−0.17**
(gate 8 ≥ 0.3 → FAIL). In FWD it underperforms SPY by −3.3 pp CAGR.

## Winner config (baseline)

```
n_states              = 2           [fin_time_series_tsay, p.186-187]
feature_set           = "sigma"     [regime_change, p.27, ch.3]
                                    # 2-feature: SPY 20d vol + TLT 20d vol
rebalance_cadence     = 21 days     # swing-horizon per plan §0
feature_lookback      = 20 days     [regime_change, p.27]
hmm_iter_max          = 100, tol=1e-4
hmm_seed              = 42
commission_bps        = 0           [plan §3.2 — Inter zero on US ETFs]
spread_bps            = 2
slippage_bps          = 1
tax_rate              = 0.15        [mandate §1 + plan §3.2 BR CG]
```

## IS state emissions (winner, n=2 / sigma / 21d)

From `regime_states_is.csv`:

| state_id | label   | prob_in_state | mean SPY σ (ann) | mean TLT σ (ann) | mean SPY daily ret | std SPY daily ret |
|---------:|:--------|--------------:|------------------:|------------------:|--------------------:|-------------------:|
| 0        | low_vol |        66.58% |            10.55% |            10.44% |           +0.0395%  |            0.72%   |
| 1        | crisis  |        33.42% |            24.57% |            18.23% |           +0.0389%  |            1.78%   |

**State mapping (fixed post-IS):**
- `low_vol`  → 100% SPY (risk-on)
- `crisis`   → 100% GLD (defensive, AMH rule 1A)

**Observation:** On IS, the mean SPY daily return is essentially
**identical** between the two states (+0.0395% vs +0.0389%) — only
**volatility** differs (0.72% vs 1.78%). The regime classifier is
therefore gating **volatility**, not **direction**. That means the edge
comes only from GLD outperforming SPY-in-drawdown during crisis
periods. On OOS (2018-2023), that condition was partially true (2020
COVID crash benefited GLD) but mostly false (2022 rate shock crushed
TLT and moved GLD sideways). The strategy is structurally dependent on
crisis-period GLD outperformance, which is not a stable edge — as
documented in `[adaptive_markets, p.244-246, ch.7]` on strategy decay.

## Grid summary (18 cells)

OOS Sharpe distribution across the 18-cell grid:

| stat | value |
|------|------:|
| count | 18 |
| mean  | 0.340 |
| std   | 0.176 |
| min   | −0.030 (n4_sigma_rc21) |
| 25%   | 0.245 |
| 50%   | 0.351 |
| 75%   | 0.480 |
| max   | 0.692 (winner) |

Top-5 cells (all OOS):

| config_id                  | n_states | feature_set      | cadence | Sharpe | CAGR   | MDD     | FWD Sh |
|:---------------------------|---------:|:-----------------|--------:|-------:|-------:|--------:|-------:|
| n2_sigma_rc21 (winner)     |    2     | sigma            | 21      | 0.692  | 9.47%  | −21.18% | 1.21   |
| n2_sigma_rho_skew_rc21     |    2     | sigma_rho_skew   | 21      | 0.539  | 7.32%  | −27.28% | 1.19   |
| n2_sigma_rc10              |    2     | sigma            | 10      | 0.503  | 6.47%  | −21.18% | 1.38   |
| n2_sigma_rho_rc10          |    2     | sigma_rho        | 10      | 0.497  | 6.30%  | −21.18% | 1.24   |
| n2_sigma_rho_rc21          |    2     | sigma_rho        | 21      | 0.483  | 6.08%  | −21.18% | 1.05   |

**Structural observation:** The **best 5 cells all have n_states=2**.
Adding states (n=3, n=4) **consistently degrades** OOS Sharpe — the
n=4 cells are the worst 5 in the grid, with one going negative
(−0.03). This is consistent with `[regime_change, p.25, ch.3]` warning
that "a 2-state HMM for long time horizons" is only justified for
short periods; but empirically here the 2-state HMM still ties the
best, because **the extra states fit IS noise** (PBO 0.19 confirms
fit-to-noise is modest but real) — the classifier can't actually
discriminate more than 2 volatility regimes reliably on 20-day
realized moments.

## Differentiation from V2-L2 Gayed EMA

This section is mandatory per plan §Family-specific hard rule.

| Dimension              | V2-L2 Gayed EMA regime         | Family H AMH HMM                    |
|:-----------------------|:--------------------------------|:-------------------------------------|
| Regime signal          | SMA/EMA cross on SPY price     | Latent state of Gaussian HMM         |
| Signal input           | Price level vs MA              | Realized moments (vol / corr / skew) |
| Number of states       | 2 (ON / OFF)                   | {2, 3, 4} — grid chose 2             |
| Decision mechanism     | Deterministic thresholding     | Probabilistic posterior (Viterbi)    |
| Training               | None (fixed rule)              | Baum-Welch EM on IS only             |
| Source                 | `[leverage_for_the_long_run]`  | `[adaptive_markets]` + `[regime_change]` + `[fin_time_series_tsay]` |
| Universe               | SPY+QQQ on / GLD off (L=2 CFD) | SPY / TLT / GLD (1× ETF)             |
| Leverage               | 2× synthetic                   | 1× unleveraged                       |
| Rebalance              | Daily                          | Every 21 trading days                |
| V2-L2 honest verdict   | FAIL (OOS Sharpe 0.56, MDD −38.8%, FWD Sharpe 0.81) | FAIL (OOS Sharpe 0.69, MDD −21.2%, FWD Sharpe 1.21) |

**Same class of failure, different mechanism:** both V2-L2 and H are
**vol-regime switchers** — one via a price-cross proxy of vol, the
other via direct HMM-on-moments. Under honest engine both deliver
OOS Sharpe in the **0.5-0.7 range** and fail the 1.5 gate. The H
variant has better MaxDD (unleveraged + multi-asset defensive mix)
and better PBO (0.19 vs V2-L2's non-computed but expected high). But
the core economic bet — "identify vol spikes and step aside from
equities into defensive assets, capture the alpha of regime
timing" — does not survive honest backtesting in either
implementation. The **differentiator landed** (HMM ≠ EMA cross), the
**edge did not** (vol-regime switching on SPY/TLT moments gives no
honest edge over buy-hold-SPY on OOS 2018-2023).

This is consistent with `[adaptive_markets, p.287, ch.8]` on the
"3.5 billion strategies" design-space explosion and
`[adaptive_markets, p.244-246, ch.7]` on strategy alpha decay —
regime-timing is a popular family that has been discovered,
traded, and competed away.

## 13-gate checklist (plan §5; relaxations applied)

| # | Gate | Threshold | Value | Pass |
|---|------|-----------|------:|:----:|
| 1   | Bootstrap OOS 99.9% CI low > 0       | > 0    | −0.4215 | FAIL |
| 1b  | Bootstrap FULL 99.9% CI low > 0      | > 0    | −0.0424 | FAIL |
| 2   | OOS Sharpe ≥ 1.5                     | ≥ 1.5  |  0.692  | FAIL |
| 3   | OOS CAGR ≥ 13% (CDI floor)           | ≥ 13%  |  9.47%  | FAIL |
| 4   | OOS MaxDD ≥ −25%                     | ≥ −25% | −21.18% | PASS |
| 5   | FWD Sharpe > 0                       | > 0    |  1.207  | PASS |
| 6   | WF 6/8 profitable AND mdd ≤ 30%      | both   | 8/8 mdd=36.95% | FAIL |
| 7   | Median hold ≥ 5 trading days         | ≥ 5d   | 42.0d   | PASS |
| 8   | IR vs SPY OOS ≥ 0.3                  | ≥ 0.3  | −0.168  | FAIL |
| 9   | Cross-lib concordance ≥ 2/3 ±3pp     | ≤ 3pp  | Δ=0.000pp | PASS |
| 10  | Stage-2 data concordance ±1pp        | ≤ 1pp  | Δ=0.45pp (Tiingo GLD vs testfolio GLDSIM) | PASS |
| 11  | PBO < 0.5 (CSCV 10-block)            | < 0.5  |  0.1944 | PASS |
| 12  | DSR p < 0.05                         | < 0.05 |  0.5634 | FAIL |
| 13  | Cost×2 sensitivity OOS Sharpe > 1.0  | > 1.0  |  0.685  | FAIL |

**Summary: 6 PASS / 8 FAIL / 0 deferred** (gate 9 was deferred in
the main runner but resolved PASS by `scripts/run_phase3_6_h_cross_lib.py`
with Δ=0.000pp; counted here as PASS).

- **PASS (6):** 4 (MDD −21.18%), 5 (FWD Sharpe 1.21), 7 (hold 42d),
  9 (cross-lib Δ=0.000pp), 10 (data concordance Δ=0.45pp), 11 (PBO 0.194).
- **FAIL (8):** 1 (boot OOS low −0.42), 1b (boot FULL low −0.04),
  2 (OOS Sharpe 0.69), 3 (OOS CAGR 9.47%), 6 (WF DD 36.95%),
  8 (IR −0.17), 12 (DSR p=0.56), 13 (cost×2 Sharpe 0.69).
- Aggregate = 6 PASS / 8 FAIL = **FAIL** (needs all 13 for WINNER;
  12/13 for PARTIAL).

Verdict: **FAIL** — fails on the edge gates (Sharpe/CAGR/DSR/IR/cost×2
+ WF-DD cap and bootstrap CI). Risk-control gates and reproducibility
gates all pass. Same diagnostic as Families B and C: risk-controlled
but no edge.

## Which gates killed it

- **Gate 2 (Sharpe 0.69 vs 1.5)** — the fundamental signal-quality
  miss. Vol-regime gating captures roughly the SPY risk-premium
  minus a tax drag, with occasional GLD out-period gains that are
  idiosyncratic (2020 COVID) rather than systematically reproducible.
- **Gate 3 (CAGR 9.47% vs 13% CDI)** — same root cause; absolute
  return is mediocre because crisis periods are rare and GLD during
  crisis was not reliably up (2022 bond crash is a counter-example
  that cost the strategy performance).
- **Gate 8 (IR vs SPY −0.17)** — confirms zero active alpha over
  plain SPY buy-hold. The regime-timing does reduce drawdown
  substantially (−21% vs SPY's −34%) but that risk reduction is not
  priced as alpha by IR.
- **Gate 6 (WF max-window DD 36.95%)** — a single walk-forward window
  (likely spanning 2022) hit a 37% drawdown despite full-period
  MaxDD staying at −21%. Walk-forward equity paths are not
  variance-preserving vs the full-period anchor.
- **Gate 12 (DSR p=0.56)** — over the 18-cell grid, the winner's
  OOS Sharpe 0.69 is well within the noise band expected by chance.
  The in-house DSR implementation agrees with López de Prado's
  deflated-Sharpe prescription `[advances_fin_ml, p.273-275]`.
- **Gate 13 (cost×2 Sharpe 0.69)** — base case is already below 1.0,
  so doubling costs cannot rescue the gate.
- **Gate 1 / 1b (bootstrap CI straddles zero)** — confirms the edge
  is statistically indistinguishable from zero at 99.9%.

## Interpretation — what the HMM learned, and what it didn't

The 2-state winner cleanly separated IS into a **low-vol** state
(66.6%, SPY σ≈10.5%) and a **crisis** state (33.4%, SPY σ≈24.6%).
The state-conditional mean SPY return is essentially **identical**
(+0.040% daily on both). This is the diagnostic finding:

**Volatility-only regimes do not produce directional alpha.** They
produce **risk-budget alpha** (lower exposure during high-vol
periods lowers realized drawdown). But once you pay for the
switch — frictions + tax + forgoing the equity premium during
nonstop low-vol stretches — the Sharpe improvement from risk
reduction is smaller than what the regime classifier's apparent
discrimination would suggest.

Lo's AMH specifically warns about this: `[adaptive_markets,
p.282-283, RULE 1A]` — "The Risk/Reward Trade-Off holds only during
normal conditions" — but the empirical consequence is subtler. A
volatility-state classifier is good at identifying when risk
punishes, but the **defensive substitute** (GLD) has its own
uncorrelated risk profile that does not uniformly out-pay SPY
during high-vol periods. In 2008-2009 it did; in 2020 it mostly did;
in 2022 it didn't. The strategy's edge is therefore **regime-
specific to regime-specific events** — a higher-order dependency
that the simple feature set cannot pre-price.

## Artifacts

- `AGGREGATE.json` — structured metrics, full 13-gate schema.
- `daily_returns.parquet` — winner cell's daily net returns (local;
  gitignored via repository-root `.gitignore`).
- `regime_states_is.csv` — IS-derived state emissions for reproducibility.
- `config_grid.csv` — 18-cell grid metrics.
- `cross_lib_check.md` + `cross_lib_summary.json` — gate 9 concordance.
- Log: `logs/phase3_6_h_amh.log`.

## Mandate §7 / strategy doc status

**UNTOUCHED.** Verdict is FAIL — no mandate §7 entry, no draft in
`docs/.pending/`, no strategy doc created.

## Citations

- **AMH regime ecology / risk-reward breaks in distress:**
  `[adaptive_markets, p.282-283, ch.8 RULE 1A-5A]`.
- **AMH strategy-alpha decay:**
  `[adaptive_markets, p.244-246, ch.7]`.
- **Markov-switching / MSA model:**
  `[fin_time_series_tsay, p.186-187, §4.1.4, eq.4.18]`.
- **Gaussian HMM for regime detection (2-state precedent):**
  `[regime_change, p.14-17, ch.2]`, `[regime_change, p.25-27, ch.3]`.
- **Realized volatility as regime feature:**
  `[fin_time_series_tsay, p.162, §3.15.1]` + `[regime_change, p.27,
  ch.3, eq.3.2]`.
- **Cross-asset correlation non-stationarity in stress:**
  `[adaptive_markets, p.282-283, RULE 4A]`.
- **Lookahead detection + prev_weight × ret alignment:**
  `[advances_fin_ml, p.31-34]`.
- **Bootstrap 99.9% CI (gate 1):** `[advances_fin_ml, p.196-202]`.
- **PBO CSCV 10-block (gate 11):** `[advances_fin_ml, p.208-211]`.
- **DSR (gate 12):** `[advances_fin_ml, p.273-275]`.
- **Walk-forward 6/8 + DD gate (gate 6):** `[advances_fin_ml, ch.11]`.
- **Inter broker cost model (commission 0 + 15% BR tax):**
  plan §3.2 + mandate §1.
- **Comparison baseline V2-L2 Gayed (rejected):**
  `reports/phase_3_5f/honest_revalidation/v2_l2_gayed_cfd/AGGREGATE.md`.

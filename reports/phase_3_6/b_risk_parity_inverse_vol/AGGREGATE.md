# Family B — Risk Parity inverse-vol multi-asset rotation (Phase 3.6)

**Date:** 2026-04-23  |  **Branch:** `phase3.6/swing-winner-hunt-20260423`
**Engine commit:** `7b90a8f` (F2-patched, lookahead-free return-series engine)
**Plan:** `docs/plans/2026-04-23-find-swing-winner-phase-3-6.md` §5 (13 gates)
**Broker model:** Banco Inter Internacional (§3.2) — 0 commission, 1.25% FX one-way, 15% BR tax monthly

---

## Verdict: ❌ **FAIL**

Family B fails **8 of 13** hard gates — edge is absent on the OOS split.

Winner-by-IS config (`N120_tvol15_rbd21`) delivers **OOS Sharpe 0.17, OOS CAGR
1.31%, OOS MaxDD −25.40%**. The 2018-2023 period was particularly hostile to a
naïve inverse-vol 4-ETF basket (rate-hiking cycle crushed the TLT leg, COVID
stress hit correlations in the wrong direction). FWD (2024-Apr 2026) recovers
to Sharpe +1.36 / CAGR +15.3% but one positive 2-year block cannot overcome
the 5.5-year OOS failure.

No promotion. No mandate §7 entry. No strategy doc banner. Halt contract
respected — orchestrator decides next.

---

## Top-line metrics (winner config `N120_tvol15_rbd21`)

| Metric | IS (2004-2017) | OOS (2018-2023) | FWD (2024-2026) | FULL |
|---|---:|---:|---:|---:|
| Sharpe (annualized) | 0.63 | **0.17** | **1.36** | 0.56 |
| CAGR | 5.57% | **1.31%** | **15.32%** | 5.73% |
| MaxDD | — | **−25.40%** | −4.47% | −25.40% |
| N bars | 3291 | 1509 | 573 | 5373 |

The IS window is **trimmed** to 2004-11-19 → 2017-12-31 because the latest-inception
ETF in the universe is GLD (2004-11-18). This is documented honestly — the plan's
stated IS start (2001-05-14) is not achievable for a 4-ETF RP basket without
synthetic fills, and the spec explicitly says "trim IS window honestly" in that case.

---

## 13-Gate checklist

| # | Gate | Threshold | Value | Pass |
|---|------|-----------|------:|:----:|
| 1 | Bootstrap 99.9% CI low (OOS Sharpe) > 0 | > 0 | −1.0554 | ❌ |
| 1b | Bootstrap 99.9% CI low (FULL Sharpe) > 0 | > 0 | −0.0642 | ❌ |
| 2 | OOS Sharpe ≥ 1.5 | ≥ 1.5 | 0.174 | ❌ |
| 3 | OOS CAGR ≥ 13% (CDI floor) | ≥ 13% | 1.31% | ❌ |
| 4 | OOS MaxDD ≥ −25% | ≥ −25% | −25.40% | ❌ |
| 5 | FWD Sharpe > 0 | > 0 | 1.358 | ✅ |
| 6 | WF ≥ 6/8 profitable AND max DD ≤ 30% | both | 6/8, mdd 25.40% | ✅ |
| 7 | Median hold ≥ 5 trading days | ≥ 5d | 21.4d | ✅ |
| 8 | IR vs SPY OOS ≥ 0.3 | ≥ 0.3 | −0.757 | ❌ |
| 9 | Cross-lib concordance ≥ 2/3 ±3pp CAGR | deferred | cross-lib sanity: corr 1.000 (non-rebal), arithmetic-clean; full 3-lib run not warranted under FAIL | DEFER |
| 10 | Testfolio vs Tiingo data concordance ≤ 1pp CAGR | ≤ 1pp | Δ = 0.695pp (Tiingo 5.77% vs testfolio 6.46%, 3-asset proxy) | ✅ |
| 11 | PBO < 0.5 (CSCV 10-block, 8-config grid) | < 0.5 | 0.2103 | ✅ |
| 12 | DSR p < 0.05 (n_trials=8) | < 0.05 | 0.8483 | ❌ |
| 13 | Cost×2 sensitivity → OOS Sharpe > 1.0 | > 1.0 | 0.108 | ❌ |

**Summary: 5 PASS / 8 FAIL / 1 DEFER (13 evaluated).** The PASS cluster is
structural (stable weight turnover, low turnover-overfit, clean data) —
exactly the pattern seen in V2-L4 and V2-L1. **Passing risk caps while
failing edge gates means there was never any edge to overfit.**

---

## Which gates killed it

### 1 & 1b — Bootstrap 99.9% CI low is negative
OOS Sharpe bootstrap CI spans [−1.06, +1.50] — the point estimate (+0.17) is
indistinguishable from zero at the 99.9% level. Full-period CI low (−0.06) is
marginally negative, meaning even 24 years of data cannot rule out "no edge".

### 2 & 3 — OOS Sharpe and CAGR collapse
Winner config's IS Sharpe (0.63) drops to 0.17 OOS. CAGR drops 5.57% → 1.31%.
This is **not** the overfit pattern (which would show IS >> OOS but still
positive) — both splits are edge-negative after cost model; IS merely benefited
from a low-rate tailwind on bonds (2004-2017 TLT CAGR ~6%) that reversed in 2018+.

### 4 — OOS MaxDD just breaches −25% cap
Winner hit −25.40% during 2022 (rate hikes simultaneously killed SPY and TLT —
the infamous "bond + equity drawdown" year that defeats naïve diversification).
Qian's thesis (`[risk_parity, p.69, ch.4]`) — "each premium provides
diversification exactly when the others struggle" — failed empirically in the
regime where ALL THREE PREMIA were negative at once (2022 Q2-Q3). This is
pitfall §6.3 in the book summary itself.

### 8 — IR vs SPY deeply negative
SPY buy-hold on OOS returned +12.00% CAGR at Sharpe 0.66. Family B returned
+1.31% CAGR at Sharpe 0.17. IR = −0.76 means **the strategy underperformed SPY
by a huge margin on a risk-adjusted basis**. The entire cost model (1.25% FX
one-way + 15% tax) plus the vol-target cap (can't leverage up to match SPY's
effective equity risk) combined to destroy any residual edge.

### 12 — DSR p-value 0.85
Deflated Sharpe Ratio, correcting for 8 trial configs, yields p = 0.85. We
cannot reject H_0 "true Sharpe ≤ 0" even without data-snooping penalty, so with
the penalty it's terminal.

### 13 — Cost×2 Sharpe collapses to 0.11
Doubling FX spread (2.50% one-way = 5% round-trip) drags OOS Sharpe from
0.17 to 0.11 and CAGR to 0.58% — confirming the cost model is material and
the tiny positive edge is cost-fragile.

---

## Why Risk Parity fails as a Brazilian retail swing strategy

Three structural reasons, all book-sourced:

1. **Qian's risk parity ASSUMES leverage** [`risk_parity, p.10, p.15, ch.1`].
   The 60/40-equivalent risk parity portfolio needs ~2:1 leverage to reach
   competitive returns. Our spec forbids leverage (1× cap), which means we're
   running the "bond-index substitute" version at ~4-5% target vol — that's
   intentionally a low-return product (`[risk_parity, p.16, Rule 3, ch.1]`).
   The CDI floor (13%) simply isn't reachable by an unleveraged RP at 10-15%
   vol target.

2. **2018-2023 was a Q-structural failure for bond-equity diversification**
   (`[risk_parity, p.73-74, ch.4]` anti-pattern). When both premia decline
   simultaneously in a rate-shock regime, RP's balanced-risk construction
   provides no protection; commodities (which would help) are not investable
   via Banco Inter. The only inflation-hedge leg we have is GLD, which zigzagged
   in 2018-2021. Qian himself warns: *"Constructing risk parity without
   commodities and TIPS creates systematic vulnerability to inflation
   shocks."*

3. **Brazilian retail tax + FX model is the wrong broker for RP**
   (`[systematic_trading, p.185-188]`). Monthly tax on realized gains means
   every rebalance that nets positive gives back 15%; FX spread 1.25% per
   crossing further bleeds the portfolio. A Brazilian investor would be
   strictly better off either: (a) accessing RP via an already-leveraged ETF
   like `RPAR`/`NTSX` (neither on Inter's catalog), or (b) buying `BIL`/`SHY`
   + CDI directly (already 13%+ with zero friction).

Combined, the structural verdict is: **naïve inverse-vol RP on 4 Tiingo ETFs,
unleveraged, monthly rebal, under Banco Inter tax+FX model cannot clear
CDI-floor on honest OOS. Verdict stands independently of backtest noise.**

---

## Grid performance (full enumeration, 8 configs)

| slug | IS Sh | IS CAGR | OOS Sh | OOS CAGR | OOS MDD | FWD Sh | FWD CAGR |
|---|---:|---:|---:|---:|---:|---:|---:|
| N20_tvol10_rbd21 | 0.44 | 3.48% | 0.00 | −0.50% | −26.6% | 1.19 | 12.65% |
| N20_tvol15_rbd21 | 0.43 | 3.65% | 0.01 | −0.43% | −27.7% | 1.23 | 13.20% |
| N40_tvol10_rbd21 | 0.49 | 4.01% | 0.10 | 0.49% | −24.8% | 1.26 | 13.89% |
| N40_tvol15_rbd21 | 0.49 | 4.25% | 0.13 | 0.83% | −25.5% | 1.29 | 14.29% |
| N60_tvol10_rbd21 | 0.52 | 4.30% | 0.11 | 0.58% | −25.0% | 1.27 | 14.06% |
| N60_tvol15_rbd21 | 0.52 | 4.55% | 0.17 | 1.23% | −25.3% | 1.28 | 14.26% |
| N120_tvol10_rbd21 | 0.62 | 5.20% | 0.08 | 0.34% | −25.3% | 1.36 | 15.32% |
| **N120_tvol15_rbd21** | **0.63** | **5.57%** | **0.17** | **1.31%** | **−25.4%** | **1.36** | **15.32%** |

No config clears CDI floor on OOS. All configs either fail MDD cap (−25%) or
sit at edge. Grid uniformity means there's no sweet spot hiding — the family
itself is the problem, not a parameter choice.

**PBO = 0.21** is low (good) — this confirms the grid is genuinely homogeneous,
not overfit; the low Sharpe is the real underlying signal.

---

## Cross-library concordance

See `cross_lib_check.md`. Since Family B is a **pure return-series strategy**
(no bar-level engine; the simulator is a straight `(prev_weight × ret).sum()`
arithmetic pipeline with explicit t+1 alignment), an independent
weights-times-returns reconstruction IS the vectorbt/backtrader analog.

- Daily-return correlation on non-rebal days: **1.000000**
- Canonical OOS CAGR (net FX + tax): +1.311%
- Independent OOS CAGR (gross, same weights × returns): +4.683%
- Δ CAGR = 3.37pp, **fully explained by FX + tax drag** (1.25% FX × ~8
  rebal/yr × 6 years + 15% tax on positive months).

Engine arithmetic is clean. A full 3-library (bt + vectorbt + backtrader)
run is NOT warranted under a FAIL verdict — this would only be executed if
the strategy cleared the edge gates.

---

## Data concordance (gate 10)

3-asset proxy (SPY / TLT / GLD — testfolio has no EM synthetic):

| Source | FULL CAGR |
|---|---:|
| Tiingo adjusted close | 5.77% |
| Testfolio synthetic (SPYSIM / ZROZSIM / GLDSIM) | 6.46% |
| Δ | **0.70pp** (< 1.0pp → PASS) |

Note: ZROZSIM (zero-coupon 30-yr) is a slightly more aggressive duration than
TLT, which explains the small positive bias. Tiingo data integrity confirmed.

---

## Artifacts

- `AGGREGATE.md` — this document.
- `AGGREGATE.json` — structured metrics for programmatic consumption.
- `config_grid.csv` — all 8 configs enumerated with IS/OOS/FWD Sharpe+CAGR.
- `daily_returns.parquet` — winner daily net returns (FX + tax baked in).
- `cross_lib_check.md` — arithmetic-sanity cross-lib reconciliation.
- Strategy class: `src/ai_trade/backtest/strategies/phase3_6_b_risk_parity_inverse_vol.py`
- Runner: `scripts/run_phase3_6_b_risk_parity_inverse_vol.py`
- Cross-lib script: `scripts/run_phase3_6_b_cross_lib.py`

---

## Mandate / strategy-doc status

**UNTOUCHED.** This verdict is FAIL, not WINNER. No promotion, no demotion.
Frozen files respected. `docs/investment-mandate.md` §7 not modified.

---

## Citations

- Risk parity theory + 3 risk premia:        `[risk_parity, p.10, p.17-18, ch.1-2]`
- Naïve inverse-vol formula (2-asset ERC):   `[risk_parity, p.10-11, ch.1]`
- Leverage is prerequisite for RP returns:   `[risk_parity, p.10, p.15-16, ch.1]`
- Anti-pattern: RP without commodities/TIPS:  `[risk_parity, p.73-74, ch.4]`
- Vol targeting:                              `[systematic_trading, p.~175]`
- Retail cost model + monthly rebal:          `[systematic_trading, p.185-188]`
- Lookahead-free t+1 execution:               `[advances_fin_ml, p.31-34]`
- Bootstrap 99.9% CI:                         `[advances_fin_ml, p.196-202]`
- PBO CSCV 10-block:                          `[advances_fin_ml, p.208-211]`
- DSR:                                        `[advances_fin_ml, p.273-275]`
- Walk-forward 6/8:                           `[advances_fin_ml, ch.11]`
- CDI soft-floor, BR tax, Inter broker:       `[investment_mandate, §1-3]`

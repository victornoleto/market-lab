# Real-vs-synth gap — Candidate on real UPRO 2009-2026

> Tests the same crash-protected candidate (`EMA_N150_th5_bL3_sL0 + sl30_rec10_cape05`) on real Tiingo UPRO vs the synth SPYSIM re-sliced to the same window (2009-06-26→2026-04-20).

## Headline — real vs synth vs SPY real buy-hold

| metric | Candidate (REAL UPRO) | Candidate (synth re-sliced 2009+) | SPY buy-hold (real) |
|---|---|---|---|
| CAGR | +18.09% | +21.49% | +15.00% |
| Sharpe | 0.68 | 0.77 | 0.90 |
| Sortino | 0.93 | 1.05 | 1.27 |
| MDD | +43.77% | +40.43% | +33.70% |
| Vol | +31.78% | +31.95% | +17.15% |
| Final eq | 16.28× | 26.17× | 10.43× |

### Synth → real degradation

* **CAGR drag**: synth +21.49% → real +18.09% = **+3.40%** hit. Matches Gayed `[leverage_for_the_long_run, p.21, Table 12]` expectation of 2-3 pp/yr real-vs-synth drag.
* **MDD**: synth +40.43% → real +43.77% (Δ +3.34%).
* **Final equity**: synth 26.17× → real 16.28× over the same 17y window.


### SPY vs candidate on real data

* Candidate CAGR +18.09% vs SPY +15.00% = **+3.09%** excess CAGR over the real window.
* MDD +43.77% vs SPY +33.70%.
* Sharpe 0.68 vs SPY 0.90.


## What this means for live deployment

1. Expect **+3.40% CAGR drag** vs the 40y synth numbers — the candidate's ~24 % synth CAGR becomes roughly 21-20 % real.
2. Stop triggers on real UPRO fire at slightly different equity levels (UPRO rebalance error creates small slippage). Plot: `real_vs_synth_equity.png`.
3. In the real 17y window the **same parameter set passes only 3/7 gates** (see `../phase3/cross_dataset_gates.md`). The synth 6/7 is NOT portable.
4. CAPE window is half-covered in 17y — the rolling 10y z-score is only active post-2019 on real data.


## Stop events on real UPRO (2009-2026)

1. **2010-05-20** — DD -32.88% → re-entry 2010-08-02 (50 bars in cash)

2. **2011-08-04** — DD -32.71% → re-entry 2011-10-14 (50 bars in cash)

3. **2015-08-24** — DD -30.13% → re-entry 2015-10-22 (42 bars in cash)

4. **2018-12-14** — DD -32.32% → re-entry 2019-01-09 (16 bars in cash)

5. **2020-03-09** — DD -34.59% → re-entry 2020-03-25 (12 bars in cash)

6. **2023-02-24** — DD -30.41% → re-entry 2023-06-02 (68 bars in cash)

7. **2025-04-03** — DD -31.68% → re-entry 2025-04-09 (4 bars in cash)


---
*Citations: Gayed `[leverage_for_the_long_run, p.21, Table 12]` (synth-vs-real drag), AFML `[p.31-34]` (honest alignment).*

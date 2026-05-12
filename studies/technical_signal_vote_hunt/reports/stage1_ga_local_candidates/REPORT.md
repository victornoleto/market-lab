# Stage 1 GA + Local-Search Candidate Registry

Status: candidate registry for post-validation discovery. These are not validated
winners. Every GA/local-search evaluation must be included in later DSR trial
accounting `[advances_fin_ml, p.222-223]`, and any candidate still requires
PBO/DSR/WF/OOS/FWD/bootstrap validation `[advances_fin_ml, p.208-211]`.

## Current Incumbents

| tier | branch | risk-on | off-leg | n | k | sortino | cagr | mdd | fitness | role | signals |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---|---|
| A | QQQ | QLD_2x | ZROZSIM | 7 | 5 | 1.3776 | 32.79% | -56.38% | 1.5632 | balanced incumbent | px_gt_sma10\|px_gt_sma20\|px_gt_ema100\|px_gt_ema200\|px_gt_ema250\|roc20_gt_0\|roc60_gt_0 |
| B | QQQ | TQQQ_3x | ZROZSIM | 8 | 6 | 1.2557 | 39.71% | -65.58% | 1.4570 | performance-first challenger | px_gt_sma10\|px_gt_sma20\|px_gt_ema100\|px_gt_ema200\|px_gt_ema250\|roc20_gt_0\|roc60_gt_0\|roc120_gt_0 |
| C | QQQ | QLD_2x | CASHX | 8 | 6 | 0.9257 | 23.99% | -39.69% | 1.0870 | cash-off diagnostic | px_gt_sma10\|px_gt_sma20\|px_gt_ema100\|px_gt_ema200\|px_gt_ema250\|roc20_gt_0\|roc60_gt_0\|roc120_gt_0 |
| D | QQQ | TQQQ_3x | CASHX | 7 | 5 | 0.8846 | 31.41% | -63.02% | 1.0368 | cash-off aggressive diagnostic | px_gt_sma10\|px_gt_sma20\|px_gt_ema200\|px_gt_ema250\|roc20_gt_0\|roc60_gt_0\|roc120_gt_0 |
| E | SPY | SSO_2x | ZROZSIM | 7 | 5 | 1.1101 | 19.04% | -59.25% | 1.1707 | SPY transplant diagnostic | px_gt_sma10\|px_gt_sma20\|px_gt_ema100\|px_gt_ema200\|px_gt_ema250\|roc60_gt_0\|rv21_pct_lt_70 |
| F | SPY | UPRO_3x | ZROZSIM | 7 | 5 | 1.0094 | 21.95% | -68.93% | 1.0694 | SPY aggressive transplant diagnostic | px_gt_sma10\|px_gt_sma20\|px_gt_ema100\|px_gt_ema200\|px_gt_ema250\|roc60_gt_0\|rv21_pct_lt_70 |

## Search Evidence

- QQQ→QLD ZROZSIM GA seed42: 25,600 evaluations; best `n=6/k=4`, Sortino 1.3516, CAGR 33.13%, MDD -61.08%.
- QQQ→QLD ZROZSIM GA seed43: 1,024,000 evaluations; best `n=7/k=5`, Sortino 1.3776, CAGR 32.79%, MDD -56.38%.
- QQQ→QLD ZROZSIM GA seed44: 1,024,000 evaluations over `n=7..12`, high mutation, 444,474 unique candidates; rediscovered the same `n=7/k=5` incumbent.
- QQQ→QLD ZROZSIM local-search: 216 one-edit subsets / 1,531 configs; incumbent remained #1 by fitness.
- QQQ→QLD CASHX local-search: best shifted to `n=8/k=6` with `ROC120`, but Sortino/CAGR fell materially; ZROZSIM is central to risk-adjusted performance.
- QQQ→TQQQ ZROZSIM local-search: best shifted to `n=8/k=6` with `ROC120`; CAGR rose to 39.71%, but MDD worsened to -65.58% and Sortino fell to 1.2557.
- QQQ→TQQQ CASHX local-search: best remained materially weaker risk-adjusted than ZROZSIM.
- SPY→SSO ZROZSIM local-search: best replaced `ROC20` with `rv21_pct_lt_70`, reaching Sortino 1.1101 and CAGR 19.04%; substantially below QQQ→QLD.
- SPY→UPRO ZROZSIM local-search: same `rv21_pct_lt_70` replacement, Sortino 1.0094 and CAGR 21.95%; aggressive SPY transplant remains weak.

## Interpretation

The current evidence supports a Nasdaq-duration regime-rotation cluster: QQQ
trend/momentum gates allocate to leveraged Nasdaq risk-on and use ZROZ as the
defensive leg. CASHX variants show that the gate alone is weaker; the duration
off-leg is a major contributor to Sortino and CAGR. SPY transplants are weaker
and prefer replacing `ROC20` with a volatility-percentile filter, so the current
lead is not a broad equity-market gate.

The strongest balanced candidate is QQQ→QLD with ZROZSIM. The strongest
performance-first candidate is QQQ→TQQQ with ZROZSIM plus `ROC120`, but its
drawdown profile is materially harsher.

## Trial Accounting So Far

Minimum known discovery trials for this branch family before any new validation:

| source | trials |
|---|---:|
| exact grid `n<=5` all branches | 5,471,268 |
| GA seed42 QQQ→QLD | 25,600 |
| GA seed43 QQQ→QLD | 1,024,000 |
| GA seed44 QQQ→QLD | 1,024,000 |
| local QQQ→QLD ZROZSIM | 1,531 |
| local QQQ→QLD CASHX | 1,531 |
| local QQQ→TQQQ ZROZSIM | 1,531 |
| local QQQ→TQQQ CASHX | 1,531 |
| local SPY→SSO ZROZSIM | 1,531 |
| local SPY→UPRO ZROZSIM | 1,531 |
| **minimum total** | **7,554,054** |

Note: additional live GA/local-search runs must be added before any honest claim.

## Next Diagnostics

1. Skip SPY CASHX unless needed for completeness; SPY ZROZSIM transplants are already clearly behind QQQ.
2. If QQQ remains dominant, validate only the top balanced and performance-first
   QQQ candidates with accumulated trial accounting.

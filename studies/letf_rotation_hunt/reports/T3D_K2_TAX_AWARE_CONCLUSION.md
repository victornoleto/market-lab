# T3d-K2 Tax-Aware Conclusion

**Status:** research-only consolidation after post-close loop iters 027-032.
**Mandate reminder:** no deployment authorization; capital remains 100% Plano C.
**Primary citations:** `[leverage_for_the_long_run, ch.4-5, p.40-60]`, `[advances_fin_ml, p.208-211]`, `[advances_fin_ml, p.222-223]`.

## TL;DR

T3d-K2 remains the simplest strong core discovered by `letf_rotation_hunt`:

```text
ON when at least 2 of 4 QLD/NDX regime votes are true:
- close > SMA250
- close > SMA100
- 21d realized volatility < 40%
- AR(1) 30d > 0

ON asset: QLD
OFF asset: ZROZ
```

Under Brazilian annual tax modeling, the best practical interpretations are:

| Role | Strategy | CAGR | Sortino | MDD | Comment |
|---|---|---:|---:|---:|---|
| Simple baseline | T3d-K2 annual-tax | 24.24% | 1.0826 | -59.43% | Cleanest implementation. |
| Balanced upgrade | Iter 30 proxy annual-tax | 25.05% | 1.0966 | -59.29% | Slightly better, but adds rearm/turbo complexity. |
| Performance-first challenger | T3d-K2 with TQQQ annual-tax | 27.88% | 1.0279 | -70.74% | Higher compounding, materially worse drawdown. |
| Rejected variants | T3d-K2 SPY/SSO and SPY/UPRO | ~13.1% | 0.70-0.76 | -70% to -86% | Do not compete. |

The most defensible operational conclusion is:

```text
If simplicity matters: use T3d-K2 annual-tax as the baseline.
If a monitoring app can automate the extra state cleanly: iter 30 proxy is the best balanced upgrade.
If maximizing CAGR is the priority and -70% drawdown is acceptable: T3d-K2 with TQQQ is the performance-first challenger.
```

None of these conclusions override the mandate. They are research conclusions only.

---

## 1. What T3d-K2 Solved

The closed study winner was:

```text
qld_voteK2_sma250_100_vol21_40_ar30_off_zroz
```

It solved the central problem better than most alternatives: participate in leveraged Nasdaq uptrends while avoiding the worst buy-and-hold LETF path dependence. The four-vote design is a simple regime filter around trend, realized volatility, and short autocorrelation. The `K=2` threshold avoids relying on a single indicator while staying responsive enough to avoid fully de-risking too late `[leverage_for_the_long_run, ch.4-5, p.40-60]`.

Gross closed-study profile:

| Strategy | CAGR | Sortino | MDD | Status |
|---|---:|---:|---:|---|
| T3d-K2 gross | 31.08-31.09% | 1.3246 | -64.50% | Closed-study winner. |

Tax-aware profile from iter 031/032:

| Strategy | CAGR | Sortino | MDD | Tax events |
|---|---:|---:|---:|---:|
| T3d-K2 annual-tax | 24.24% | 1.0826 | -59.43% | 366 sales, 31 tax years paid. |

The annual-tax model materially compresses CAGR and Sortino. This is expected because T3d-K2 realizes gains/losses whenever it switches QLD/ZROZ, while SPY/NDX buy-and-hold have no interim taxable sale events.

---

## 2. Benchmark-Relative Finding

T3d-K2 tax-aware still strongly dominates static SPY and NDX/QQQ buy-and-hold on long-run wealth in the tested long-history data.

| Strategy | CAGR | Sortino | MDD | Terminal vs taxed T3d-K2 |
|---|---:|---:|---:|---:|
| T3d-K2 annual-tax | 24.24% | 1.0826 | -59.43% | 1.000x |
| SPY buyhold no-tax | 11.47% | 0.9571 | -55.14% | 0.013x |
| NDX/QQQ buyhold no-tax | 14.59% | 0.9429 | -82.97% | 0.038x |

Relative-equity observation:

| Strategy | Benchmark | % time equity/benchmark < 1 | Interpretation |
|---|---|---:|---|
| T3d-K2 annual-tax | SPY | ~0.23% | Only the tiny initial 1986 window. |
| T3d-K2 annual-tax | NDX/QQQ | ~0.23% | Only the tiny initial 1986 window. |
| T3d-K2 with TQQQ annual-tax | SPY | ~0.23% | Also only the tiny initial 1986 window. |
| T3d-K2 with TQQQ annual-tax | NDX/QQQ | ~0.23% | Also only the tiny initial 1986 window. |

This supports the statement: T3d-style dynamic LETF rotation was persistently ahead of SPY/NDX in cumulative wealth after the start-up window. It does not mean it is lower risk than SPY; absolute drawdowns remain severe.

---

## 3. Iter 027-030: Why T35D60 + LRS1.20 Emerged

Post-close Phase 4 refined the iter 017 post-crash rearm family. The central idea was: after a long OFF stretch, the first return to ON may mark a recovery phase worth sizing more aggressively.

The final gross research winner was iter 030:

```text
T3d-K2 core
+ T35D60 rearm gate
+ LRS1.20 exposure overlay
```

Definition:

```text
If today turns ON after at least 35 contiguous prior OFF days:
    open a 60-trading-day rearm window.

During eligible ON/rearm periods:
    apply the LRS1.20 overlay.
```

Important implementation nuance:

```text
D60 is not a waiting period.
It is the active post-flip rearm window.
OFF always exits risk immediately; if ON resumes inside the original D60 window, rearm can resume until the original window expires.
```

Gross Phase 4 frontier:

| Variant | CAGR | Sortino | End equity vs T3d-K2 | Read |
|---|---:|---:|---:|---|
| T40D60 + LRS1.05 | 33.43% | 1.4068 | 2.049x | First formal LRS improvement. |
| T40D60 + LRS1.10 | 34.39% | 1.3968 | 2.730x | Higher CAGR, lower Sortino. |
| T40D60 + LRS1.15 | 35.32% | 1.3874 | 3.610x | Monotonic frontier held. |
| T40D60 + LRS1.20 | 36.22% | 1.3786 | 4.710x | Iter 027 frontier. |
| T35D60 + LRS1.20 | 36.68% | 1.3839 | 5.395x | Iter 030 gross winner. |

Iter 030 falsified the T40 anchor:

| T_crash | Sortino | CAGR | End equity vs T3d-K2 | Verdict |
|---:|---:|---:|---:|---|
| 35 | 1.3839 | 36.68% | 5.395x | Best tested point. |
| 40 | 1.3786 | 36.22% | 4.710x | Inferior to T35. |
| 45 | 1.3689 | 35.77% | 4.133x | Below Sortino beater threshold. |
| 50 | 1.3379 | 34.27% | 2.635x | Below Sortino beater threshold. |

Gross conclusion: T35D60 + LRS1.20 was a genuine research improvement over T3d-K2, but gross LRS1.20 is not directly executable without either margin/synthetic exposure or a proxy.

---

## 4. Tax-Aware Iter 30 Proxy

The practical no-margin proxy tested in iter 031 was:

| State | Allocation |
|---|---:|
| OFF | 100% ZROZ |
| ON normal | 100% QLD |
| ON rearm/turbo | 80% TQQQ + 20% CASHX |

Tax-aware result:

| Strategy | CAGR | Sortino | MDD | Terminal vs taxed T3d-K2 |
|---|---:|---:|---:|---:|
| T3d-K2 annual-tax | 24.24% | 1.0826 | -59.43% | 1.000x |
| Iter 30 proxy annual-tax | 25.05% | 1.0966 | -59.29% | 1.299x |

Rolling windows versus taxed T3d-K2:

| Window | Iter 30 proxy win-rate | Mean end-ratio | Median end-ratio | Worst end-ratio |
|---|---:|---:|---:|---:|
| 1y | 53.37% | 1.007x | 1.000x | 0.950x |
| 3y | 60.38% | 1.020x | 1.008x | 0.902x |
| 5y | 67.34% | 1.033x | 1.017x | 0.902x |
| 10y | 60.22% | 1.040x | 1.009x | 0.888x |
| 15y | 57.82% | 1.036x | 1.017x | 0.910x |
| 20y | 53.92% | 1.046x | 1.046x | 0.929x |

Interpretation: the iter 30 proxy is better in aggregate and slightly better on risk-adjusted metrics, but the advantage is not overwhelming. It adds an extra state machine and TQQQ/CASH execution step for about +0.81pp CAGR, +0.014 Sortino, and 1.299x terminal wealth versus taxed T3d-K2.

The extra complexity is only justified if monitoring/execution is automated and reliable.

---

## 5. T3d-K2 with TQQQ Risk-On

The simplest performance-first variant is:

```text
Same T3d-K2 QLD/NDX signal
ON asset: TQQQ
OFF asset: ZROZ
Annual tax on realized gains/losses
```

Result:

| Strategy | CAGR | Sortino | MDD | Terminal vs taxed T3d-K2 |
|---|---:|---:|---:|---:|
| T3d-K2 annual-tax | 24.24% | 1.0826 | -59.43% | 1.000x |
| T3d-K2 with TQQQ annual-tax | 27.88% | 1.0279 | -70.74% | 3.194x |

Rolling windows versus taxed T3d-K2:

| Window | Win-rate | Mean end-ratio | Min end-ratio |
|---|---:|---:|---:|
| 1y | 55.70% | 1.041x | 0.623x |
| 3y | 68.91% | 1.120x | 0.539x |
| 5y | 66.72% | 1.215x | 0.600x |
| 10y | 77.37% | 1.435x | 0.544x |

Interpretation: TQQQ is not a balanced upgrade. It is a performance-first leverage increase. It delivers the highest CAGR and terminal wealth among the tax-aware variants tested, but the cost is a much worse drawdown and lower Sortino than both T3d-K2 and iter 30 proxy.

Use this only if the objective function explicitly prioritizes terminal compounding over drawdown comfort.

---

## 6. Why SPY/SSO/UPRO Underperformed

The SPY/SSO and SPY/UPRO variants tested:

```text
Signal underlying: SPY
Risk-on asset: SSO or UPRO
Risk-off asset: ZROZ
Annual tax on realized gains/losses
```

Results:

| Strategy | CAGR | Sortino | MDD | Terminal vs taxed T3d-K2 |
|---|---:|---:|---:|---:|
| T3d-K2 SPY/SSO annual-tax | 13.12% | 0.7556 | -70.19% | 0.023x |
| T3d-K2 SPY/UPRO annual-tax | 13.08% | 0.6965 | -86.06% | 0.023x |

Why they were inferior:

1. The original edge is Nasdaq/QLD-specific, not generic equity beta.

T3d-K2 was discovered on QLD/NDX behavior. The QLD/NDX regime has higher trend convexity in long bull markets, which pays for the times it gets whipsawed. SPY has lower upside convexity, so the same switching/tax machinery has less return to harvest.

2. SPY/SSO gives up too much upside but keeps meaningful risk.

SSO is only 2x SPY. The lower beta reduces compounding relative to QLD/TQQQ, but the strategy still pays taxes on state changes and still suffers bond/equity regime mistakes. The result is neither high enough CAGR nor enough drawdown reduction.

3. SPY/UPRO adds leverage to the wrong payoff shape.

UPRO increases SPY exposure, but SPY's path did not provide enough post-tax trend payoff to compensate for 3x volatility drag and bad windows. It ended with MDD -86.06%, worse than NDX/QQQ buy-and-hold, while CAGR stayed around 13.08%.

4. The signal/risk-on pairing lost the Nasdaq recovery asymmetry.

The best results came from QLD/NDX signal with QLD/TQQQ-related risk-on assets. Replacing the underlying with SPY weakens the exact recovery/continuation behavior that made T3d-K2 work.

5. Tax drag is not the main reason SPY variants failed.

Tax paid was much smaller for SPY/SSO and SPY/UPRO than for QLD/TQQQ variants because they compounded much less. Lower tax paid here is a symptom of weaker gains, not an advantage.

Conclusion: SPY/SSO and SPY/UPRO are rejected for this family. If SPY is used, it likely needs a different signal design rather than a direct transplant of T3d-K2.

---

## 7. Current Ranking

### Best Simple Strategy

```text
T3d-K2 annual-tax
```

Use when simplicity and fewer moving parts matter most. It has one ON/OFF decision and one risk-on asset.

### Best Balanced Upgrade

```text
Iter 30 proxy annual-tax
```

Use only if an app can reliably track OFF streak, T35D60 rearm windows, and TQQQ/CASH turbo execution. The advantage over T3d-K2 is real but modest.

### Best Performance-First Variant

```text
T3d-K2 with TQQQ annual-tax
```

Use only if the investor accepts drawdowns around -70% and explicitly prioritizes terminal compounding.

### Rejected Variants

```text
T3d-K2 SPY/SSO annual-tax
T3d-K2 SPY/UPRO annual-tax
```

These do not compete with T3d-K2, iter 30 proxy, or even static NDX/QQQ in the tested long-history panel.

---

## 8. Operational Conclusion

For a future monitoring app, the most rational order is:

1. Implement T3d-K2 first as the baseline.
2. Add iter 30 proxy only after T3d-K2 state tracking is bit-exact.
3. Treat T3d-K2 with TQQQ as a separate aggressive profile, not as the default.
4. Do not implement SPY/SSO or SPY/UPRO variants unless a new SPY-specific hypothesis is designed.

Minimum app state for T3d-K2:

```text
date
vote_sma250
vote_sma100
vote_vol21_lt_40
vote_ar30_gt_0
vote_count
on_signal
target_asset: QLD or ZROZ
```

Additional app state for iter 30 proxy:

```text
prior_off_streak
off_to_on_flip
rearm_window_start
rearm_days_remaining
rearm_active
target_asset_mix: QLD, ZROZ, or 80% TQQQ + 20% CASHX
```

Tax accounting needed for either dynamic strategy:

```text
average cost per asset
realized gains/losses per sale
annual net realized P&L
loss carryforward
15% annual tax liability
```

Until this is implemented and reconciled against the historical backtest, the output remains research-only.

---

## 9. Source Files

- Closed-study report: `studies/letf_rotation_hunt/reports/STUDY_FINAL_REPORT.md`
- Post-close continuation: `studies/letf_rotation_hunt/reports/POST_CLOSE_LOOP_REPORT.md`
- Iter 030 gross winner: `studies/letf_rotation_hunt/runs/post_close/030-2026-05-10-tcrash-scan-lrs120-rearmonly/SUMMARY.md`
- Iter 031 tax proxy: `studies/letf_rotation_hunt/runs/post_close/031-2026-05-10-tqqq-cash-proxy-annual-tax/SUMMARY.md`
- Iter 032 variant report and plots: `studies/letf_rotation_hunt/runs/post_close/032-2026-05-10-taxed-underlying-riskon-variants/REPORT.md`

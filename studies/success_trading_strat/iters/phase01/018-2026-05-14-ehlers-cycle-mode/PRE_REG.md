# PRE_REG — 018 Ehlers cycle-mode overlay

## Hypothesis

Test a small Ehlers-inspired market-mode overlay: when smoothed price is far from
an instantaneous trendline, treat the market as Trend Mode; otherwise use a
fixed-cycle sine/lead-sine phase proxy for Cycle Mode. The goal is to test a
genuinely different signal-processing mechanism after beta, VIX, crypto trend,
credit, realized-volatility and Carver/EWMAC families failed. Ehlers frames price
as alternating Trend Mode and Cycle Mode, with smoothing before signal operations,
instantaneous trendline, sine/lead-sine phase and a trend-mode override
`[rocket_science, p.3-4]`, `[rocket_science, p.11-14]`, `[rocket_science,
p.99-100]`, `[rocket_science, p.107]`, `[rocket_science, p.114-117]`.

This is research only. Capital remains 100% Plano C per
`docs/investment-mandate.md`.

## Exact Configs

Four configs, all long-only risky asset or `SHV`, one-bar lagged signal:

| name | asset | cycle_period | trend_threshold | defensive |
|---|---:|---:|---:|---|
| `spy_ehlers_c20_t15` | `SPY` | 20 | 1.5% | `SHV` |
| `qqq_ehlers_c20_t15` | `QQQ` | 20 | 1.5% | `SHV` |
| `spy_ehlers_c30_t15` | `SPY` | 30 | 1.5% | `SHV` |
| `qqq_ehlers_c30_t15` | `QQQ` | 30 | 1.5% | `SHV` |

Rationale: 1.5% is Ehlers' market-mode trend override example; 20 and 30 bars
are fixed dominant-cycle proxies within the common trading-cycle range and avoid
adding adaptive optimization in this first diagnostic `[rocket_science, p.3-4]`,
`[rocket_science, p.114-117]`. Using only 4 configs preserves small-grid trial
discipline `[testing_tuning, p.327-335]`.

## Data And Window

- Local Tiingo daily adjusted closes from `data/tiingo/daily/prices/`.
- Required files: `SPY`, `QQQ`, `SHV`.
- Common window starts at `2010-01-01`; stale block if common end is before
  `2026-03-31`.
- Any missing required file or insufficient common history triggers
  `data_blocked` and consumes zero trials.

## Benchmark

Each config must beat same-asset buy-and-hold Sharpe over the aligned strategy
return window. CAGR/MDD are reported but do not override hard gates.

## Planned Gates

- Data freshness.
- Same-asset benchmark Sharpe.
- IS MCPT with 200 permutations, requiring `p <= 0.01`
  `[testing_tuning, p.318-320]`.
- WF MCPT with 100 permutations, requiring `p <= 0.05`
  `[testing_tuning, p.318-320]`.
- PBO over the 4 configs with 8 blocks, requiring `<0.5`
  `[advances_fin_ml, p.208-211]`.
- DSR on best config using cumulative trials after this iteration
  `[advances_fin_ml, p.222-223]`.
- Walk-forward positive windows, OOS, latest 63d FWD stress, 99.9% bootstrap mean
  daily CI low, and cross-lib CAGR agreement `[advances_fin_ml, p.196-202]`,
  `[testing_tuning, p.148-150]`, `[testing_tuning, p.246-247]`.

## Kill Rules

- If required data are unavailable, stop as `data_blocked`; do not substitute a
  new asset after pre-registration.
- If MCPT/PBO/DSR fail, mark the family as a dead end and do not tune cycle
  periods or thresholds locally without a new economic mechanism.
- If the result only improves drawdown while failing same-asset benchmark Sharpe,
  mark `fail`.
- Any ambiguity is resolved conservatively and recorded in `SUMMARY.md`.

## Trial Accounting

- `cumulative_n_trials` before: 56.
- `n_trials` planned: 4.
- `cumulative_n_trials` after if data available: 60.
- `cumulative_n_trials` after if data blocked: 56.

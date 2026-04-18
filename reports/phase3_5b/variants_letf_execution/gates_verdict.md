# Phase 3.5b — V1/V2/V3/V4 gate verdict

**Threshold:** 10pp | **Tax:** 15% | **Source:** testfol.io ground truth | **Signals:** EMA100(SPY), Donchian 20/10 (QQQ), Donchian 40/20 (GLD)

**DSR n_trials:** 4 | **WF windows:** 8 (≥6 profitable, ≤25% DD each) | **Bootstrap:** 99.9% CI on OOS Sharpe (stationary block, n_resamples=2000)


## Window — `canonical_2004_2026`

IS: `2004-11-18 → 2014-12-31`  |  OOS: `2015-01-01 → 2019-12-31`  |  Stress: `2020-01-01 → 2026-04-17`

| Rank | Variant | Verdict | IS Sh | OOS Sh | Stress Sh | Full CAGR | Full MaxDD | WF ratio | WF max DD | DSR p | Boot 99.9% CI lo | Failed |
|---:|---|:-:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | V4_SSO_QLD_UGL | ✅ PASS | 1.970 | 2.609 | 2.172 | 39.19% | 12.22% | 1.00 | 12.22% | 0.0000 | 1.274 | — |
| 2 | V2_SSO_QLD_GLD | ✅ PASS | 1.996 | 2.595 | 2.176 | 35.03% | 12.62% | 1.00 | 12.62% | 0.0000 | 1.304 | — |
| 3 | V1_SSO_QQQ_GLD | ✅ PASS | 1.962 | 2.478 | 2.137 | 26.53% | 9.39% | 1.00 | 9.39% | 0.0000 | 1.043 | — |
| 4 | V3_SSO_QQQ_UGL | ✅ PASS | 1.923 | 2.392 | 2.058 | 30.89% | 10.88% | 1.00 | 10.88% | 0.0000 | 1.081 | — |


## Window — `extended_1986_2026`

IS: `1986-01-02 → 2010-12-31`  |  OOS: `2011-01-01 → 2019-12-31`  |  Stress: `2020-01-01 → 2026-04-17`

| Rank | Variant | Verdict | IS Sh | OOS Sh | Stress Sh | Full CAGR | Full MaxDD | WF ratio | WF max DD | DSR p | Boot 99.9% CI lo | Failed |
|---:|---|:-:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | V4_SSO_QLD_UGL | ✅ PASS | 1.852 | 2.320 | 2.172 | 37.93% | 16.91% | 1.00 | 16.91% | 0.0000 | 1.357 | — |
| 2 | V2_SSO_QLD_GLD | ✅ PASS | 1.852 | 2.294 | 2.176 | 35.00% | 15.81% | 1.00 | 15.81% | 0.0000 | 1.305 | — |
| 3 | V1_SSO_QQQ_GLD | ✅ PASS | 1.875 | 2.195 | 2.137 | 25.94% | 11.13% | 1.00 | 11.13% | 0.0000 | 1.262 | — |
| 4 | V3_SSO_QQQ_UGL | ✅ PASS | 1.834 | 2.174 | 2.058 | 28.92% | 13.70% | 1.00 | 13.70% | 0.0000 | 1.229 | — |


## Legend

* **OOS Sharpe > 0** (gate 1) — simple sign test.
* **Stress Sharpe > 0** (gate 2) — post-cutoff regime.
* **WF ratio ≥ 0.75** AND **per-window MaxDD ≤ 25%** (gate 3) — 8 windows over full range.
* **DSR p < 0.05** (gate 4) — multiple-testing adjusted Sharpe significance (n_trials=4).
* **Bootstrap 99.9% CI lower > 0** (gate 5) — stationary-block bootstrap on OOS returns.

## Interpretação

* Uma variante só é **promotable** se passar os 5 gates **no window canônico 2004-2026**.
* O window supplementary 1986-2026 é **cross-check confirmatório** — PASS adicional eleva confiança; FAIL adicional é flag amarelo mas não bloqueio.
* Ranking dentro do window ordena: (PASS > FAIL) e (OOS Sharpe desc).
* **A decisão operacional vem do window canônico.**

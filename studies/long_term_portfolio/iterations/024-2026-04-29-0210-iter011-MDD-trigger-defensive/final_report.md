# Iter 024 — Final Report — `iter011-MDD-trigger-defensive`

**Verdict NEW**: **STRONG 82/100**, `winner_conds=True` (4 conds met,
score < 90 driven by gates partial + CAGR floor warning).

**Verdict LEGACY**: **STRONG 87/100**, `winner_conds=True`.

**Substantive vs iter 011**: marginal +signal across all 3 datasets (loose
+0.099/+0.022/+0.019), but **dominated by iter 023 TLT-static** (1.189/1.004/1.135
vs iter 024 1.145/0.982/1.123 — iter 023 wins every dataset).

## Selected config

`mdd_trigger_10pct_TLT` — selected by max mean(S/SPY) = 1.351; cluster of 3
configs within 0.005 mean.

| state | NTSX | GDE | KMLM | TLT |
|---|---:|---:|---:|---:|
| ON (base, default 99% of time) | 35% | 25% | 40% | 0% |
| OFF (trigger fires, SPY 21d < −10%) | 17.5% | 25% | 40% | 17.5% |

---

## Per-dataset metrics

| dataset | Sharpe (loose) | Sharpe (strict) | CAGR | MDD | gates | DSR p | pct_on |
|---|---:|---:|---:|---:|---:|---:|---:|
| lh_56y | **1.145** | 1.062 | 11.74% | 25.20% | 5/7 | 1.4e-14 | 1% |
| vt_real | **0.982** | 0.979 | 10.63% | 19.07% | 6/7 | 5.5e-4 | 2% |
| ndx_real | **1.123** | 1.120 | 11.44% | 12.02% | 6/7 | 1.5e-4 | 1% |

**Trigger pct_on = 1-2%** — signal fires very rarely. The 10% 21d drawdown
threshold catches 2008 GFC, 2020 COVID, 2022 grinding bear. Effective
strategy is iter 011 base 99% of the time + brief defensive shifts during
crisis windows.

---

## NEW Sharpe edges vs SPY

| dataset | bench | hurdle | candidate | edge | passes? |
|---|---:|---:|---:|---:|:-:|
| lh_56y | 0.680 | 0.730 | 1.145 | +0.465 | ✅ |
| vt_real | 0.900 | 0.950 | 0.982 | +0.082 | ✅ |
| ndx_real | 0.900 | 0.950 | 1.123 | +0.223 | ✅ |

3/3 clear NEW hurdle.

## Substantive vs iter 011

| dataset | iter 011 | iter 024 (loose) | Δ loose | iter 024 (strict) | Δ strict |
|---|---:|---:|---:|---:|---:|
| lh_56y | 1.046 | 1.145 | +0.099 | 1.062 | +0.017 |
| vt_real | 0.960 | 0.982 | +0.022 | 0.979 | +0.019 |
| ndx_real | 1.104 | 1.123 | +0.019 | 1.120 | +0.016 |

3/3 datasets positive (loose AND strict). lh_56y comes close to +0.10
substantive hurdle (+0.099) but doesn't clear it. Dominated by iter 023
which delivered +0.143/+0.044/+0.031 on the same 3 datasets.

---

## Score breakdown NEW

| # | criterion | pts | max | note |
|---|---|---:|---:|---|
| 1 | Sharpe edge (SPY+0.05) | 25 | 25 | 3/3 |
| 2 | Gates | 17 | 25 | 5+5+5+2 = 17 (lh_56y 5/7 misses bonus tier) |
| 3 | DSR | 15 | 15 | worst 5.5e-4 |
| 4 | CAGR floor (warning-only) | 5 | 15 | only lh_56y 11.74% > 9.18% |
| 5 | MDD ceiling | 15 | 15 | 3/3 |
| 6 | Robustness | 5 | 5 | rolling positive |
| **Total** | | **82** | **100** | **STRONG** |

## Cross-config grid (gross Sharpe, 3 configs)

| config | threshold | defensive | lh_56y | vt_real | ndx_real | pct_on (avg) |
|---|---:|---|---:|---:|---:|---:|
| `mdd_trigger_10pct_TLT` ✅ | −10% | TLTSIM | **1.145** | **0.982** | 1.123 | 1.3% |
| `mdd_trigger_15pct_TLT` | −15% | TLTSIM | 1.141 | 0.978 | **1.124** | 0.7% |
| `mdd_trigger_15pct_CASH` | −15% | CASHX | 1.138 | 0.981 | 1.117 | 0.7% |

Configs cluster within 0.01 Sharpe. KILL #2 monotonic (10%→15% pct_on
declines) does NOT fire — Sharpe roughly flat. KILL #1 whipsaw (pct_on >30%)
does NOT fire — opposite end (under-active rather than over-active).

PBO N=3 warning (CSCV unstable below N=4); reported informationally.

---

## Key honesty observations

1. **Trigger pct_on = 1-2%** — defensive almost never activates. This is
   not a "regime-conditional" strategy in any meaningful sense; it's
   iter 011 base 99% of the time + 3 days/year defensive average.

2. **Marginal edge consistent with rare-event capture**: in the few days
   the trigger fires (2008 Q3-Q4, 2020-Q1, 2022-Q2), the +17.5% TLT
   sleeve dampens MDD slightly. Over ~40y of lh_56y, this concentrates
   benefit in <1% of trading days but materially reduces tail risk.

3. **Dominated by iter 023 TLT-static**: keeping 15% TLT 100% of the
   time delivers +0.044-0.143 Sharpe edge vs +0.019-0.099 of iter 024.
   TLT continuously contributes more than TLT episodically.

4. **Forward-looking signal** (no peek): `compute_signal` uses
   `pct_change(21).shift(1)` — signal observed at close-of-day-t-1
   reflects 21d return ending day-t-1, action takes effect at close-of-day-t.

5. **vt_real edge +0.022 below noise**: bootstrap 99.9% CI low > 0
   (g6_bootstrap pass) but +0.022 is within typical PBO selection
   variance — mostly statistical noise rather than real edge.

---

## Decisão

**STRONG NEW + LEGACY**, but **NOT advance** — iter 023 dominates on every
dataset by Sharpe AND MDD (vt_real 17.40% iter 023 vs 19.07% iter 024;
ndx_real 11.76% vs 12.02%). The dynamic shift is strictly suboptimal vs
keeping TLT in continuously.

**Lesson DE-024**: rare-event defensive trigger fires <2% of trading days,
recovers <1% of the static-TLT-benefit. Concentrate Sharpe alpha in
continuous defensive sleeve, not gated.

**Direction B.2 (regime-trigger defensive)**: closed if iter 023 holds.
The cleanest case for trigger-based defensive would be 10x more frequent
firing (3-5% pct_on) on a milder threshold (e.g., −5% 21d), but PBO
discipline limits us to 3 configs per iter — would need a separate iter
to test that variant.

---

## Citations

- `[risk_parity, ch.5, p.10]` Carlson capital-efficient stacking base
- `[systematic_trading, p.137-148]` Carver position sizing / regime weights
- `[advances_fin_ml, p.208-211]` PBO discipline (N=3 warning)
- `[advances_fin_ml, p.222-223]` DSR cumulative n_trials

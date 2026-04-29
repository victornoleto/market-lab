# Iter 025 — Final Report — `iter011-VXX-real-diagnostic`

**Verdict NEW**: **STRONG 83/100**, `winner_conds=True` (2/3 Sharpe edges
+0.05 vs SPY; vt_real +0.021 misses hurdle).

**Verdict LEGACY**: **WINNER 93/100**, `winner_conds=True` (clears
LEGACY +0.10 avg(SPY,VT) on 3/3, easier under broader baseline).

**Substantive vs iter 011**: LOSES on vt_real (−0.039) and ndx_real (−0.007).
Wins marginally on lh_56y (+0.061 loose, +0.033 strict).

**Methodological diagnostic — KILL #1 PASS**: Sharpe decreases monotonically
as VXX % rises 2.5% → 10% in all 3 datasets. **Decay structurally beats
tail-hedge benefit** at any non-trivial VXX weight.

---

## No-free-lunch sanity check (pre-run, observable)

| metric | value | expected | status |
|---|---|---|---|
| VXX standalone Sharpe | **−0.738** | < 0 | ✅ confirms decay |
| VXX standalone CAGR | **−51.34%/yr** | < −30% | ✅ brutal decay |
| VXX standalone MDD | **−100%** | < −90% | ✅ "going to zero" |

Backtest aborts via `RuntimeError` if VXX standalone Sharpe ≥ 0 (impossible
in 2009+ data, but invariant is asserted as guard).

---

## Selected config

`vxx_lite_3525_375_25` — **35% NTSX + 25% GDE + 37.5% KMLM + 2.5% VXX**.

VXX substitutes from KMLM (preserving NTSX+GDE cap-efficient core).

---

## Per-dataset metrics

| dataset | Sharpe (loose) | Sharpe (strict) | CAGR | MDD | gates | DSR p |
|---|---:|---:|---:|---:|---:|---:|
| lh_56y | **1.107** | 1.078 | 11.25% | 25.61% | 6/7 | 7.2e-13 |
| vt_real | **0.921** | 1.078 | 9.64% | 21.41% | 7/7 | 2.2e-03 |
| ndx_real | **1.097** | 1.093 | 10.40% | 11.57% | 7/7 | 4.2e-04 |

**Strict-loose gap on vt_real** (0.921 loose vs 1.078 strict): vt_real
window 2008-06-2026 includes 7 months pre-VXX-inception (2008-06 to
2009-01) where VXX-leg = 0 — strategy effectively under-weight at 97.5%
notional. Strict drops those rows; the post-2009 portion has cleaner
+VXX hedge contribution but with full 17y of decay drag. The high strict
Sharpe is a window-length artifact (shorter window concentrates 2020 spike).

---

## NEW Sharpe edges vs SPY

| dataset | bench | hurdle | candidate | edge | passes? |
|---|---:|---:|---:|---:|:-:|
| lh_56y | 0.680 | 0.730 | 1.107 | +0.427 | ✅ |
| vt_real | 0.900 | 0.950 | 0.921 | +0.021 | ❌ misses by 0.029 |
| ndx_real | 0.900 | 0.950 | 1.097 | +0.197 | ✅ |

**2/3 clear NEW hurdle**, satisfying winner_conditions_met (Sharpe edge
required ≥2/3, this gives exactly 2). vt_real misses by 0.029 — VXX decay
in 2010-2015 low-vol period eats into Sharpe.

## Cross-config monotonic check ✅ KILL #1 PASS

| config | VXX% | lh_56y | Δ | vt_real | Δ | ndx_real | Δ |
|---|---:|---:|---:|---:|---:|---:|---:|
| `vxx_lite` | 2.5% | **1.107** | – | **0.921** | – | **1.097** | – |
| `vxx_mod` | 5.0% | 1.077 | −0.030 | 0.858 | −0.063 | 1.061 | −0.036 |
| `vxx_balanced` | 7.5% | 1.035 | −0.041 | 0.765 | −0.093 | 0.983 | −0.078 |
| `vxx_heavy` | 10.0% | 0.982 | −0.053 | 0.641 | −0.124 | 0.854 | −0.128 |

**Monotonic decline 3/3 datasets** as VXX% rises. Decay accumulates
proportionally (and worse than linear in vt_real/ndx_real). Each +1pp
VXX costs ~1pp Sharpe on live windows (vt_real, ndx_real).

This is the **honest signature of a decay asset** — exactly the opposite
of iter 022's synthetic model (+5pp Sharpe edge, monotonic UP with weight).

---

## Substantive vs iter 011

| dataset | iter 011 | iter 025 (loose) | Δ loose | Δ strict |
|---|---:|---:|---:|---:|
| lh_56y | 1.046 | 1.107 | **+0.061** | +0.033 |
| vt_real | 0.960 | 0.921 | **−0.039** | (window mismatch) |
| ndx_real | 1.104 | 1.097 | **−0.007** | −0.011 |

**1/3 positive vs iter 011**. lh_56y advance is mostly noise (0.033 strict).
vt_real and ndx_real LOSE marginally. Iter 011 dominates iter 025 on the
two live windows.

---

## Score breakdown NEW

| # | criterion | pts | max |
|---|---|---:|---:|
| 1 | Sharpe edge SPY+0.05 (2/3) | 20 | 25 |
| 2 | Gates | 23 | 25 (6+7+7+3) |
| 3 | DSR | 15 | 15 |
| 4 | CAGR floor (warning-only) | 5 | 15 (lh_56y only) |
| 5 | MDD ≤ SPY | 15 | 15 |
| 6 | Robustness | 5 | 5 |
| **Total** | | **83** | **100** | STRONG |

## Score breakdown LEGACY

| # | criterion | pts | max |
|---|---|---:|---:|
| 1 | Sharpe edge avg+0.10 (3/3) | 25 | 25 |
| 2 | Gates | 23 | 25 |
| 3 | DSR | 15 | 15 |
| 4 | CAGR floor (warning-only) | 10 | 15 (vt_real fails 9.64% < 9.51%) |
| 5 | MDD ≤ avg+5pp | 15 | 15 |
| 6 | Robustness | 5 | 5 |
| **Total** | | **93** | **100** | WINNER LEGACY |

LEGACY tier WINNER artifact comes from the easier vt_real hurdle (avg+0.10 =
0.807, vs SPY+0.05 = 0.950): the 0.921 Sharpe of iter 025 clears 0.807 by
+0.114 but misses 0.950 by 0.029. Sob LEGACY rules, this looked like a winner.

---

## Methodological lesson — quantifying iter 022 synthetic gap

| metric | iter 022 synthetic (10% hedge) | iter 025 real (10% VXX) | gap |
|---|---:|---:|---:|
| lh_56y Sharpe | 1.520 | 0.982 | **−0.538** |
| vt_real Sharpe | 1.710 | 0.641 | **−1.069** |
| ndx_real Sharpe | 1.684 | 0.854 | **−0.830** |
| score | 100/100 | (10% VXX would be much worse) | model artifact |

iter 022's synthetic model overstates Sharpe by **0.5-1.1 points across
datasets** at 10% hedge weight. This is the price of:
- modeling premium as fixed −0.04%/day decay (vs realized −51%/yr)
- hindsight via 21d trigger (model only pays in non-drawdown windows)
- wrong path-dependence (2× daily compound vs strike−spot at expiry)
- no spread/liquidity drag

**Conclusion**: iter 022 score 100/100 was 100% model failure. Realistic
deployable tail-hedge ≈ iter 025: marginal lh_56y win, vt/ndx losses.

---

## Decisão

**STRONG NEW (83) / WINNER LEGACY (93)** — but **NOT advance** vs iter 011.
1/3 substantively positive (lh_56y noise), 2/3 negative (vt_real, ndx_real).

**DE-025**: continuous 2.5% VXX hedge structurally subordinate to iter 011
in this universe. Higher % uniformly worse (KILL #1 confirms decay).

**Direction B.3 closed**: tail-hedge with deployable VXX is a **net Sharpe
loss** at every weight tested. Spitznagel's Universa real-implementation
+1-2pp CAGR uplift (vs +5pp Sharpe of iter 022 model) is what's actually
achievable — using OTM put options + short-vol overlay, not just buying
VXX. iter 025 captures only the negative side of that ledger.

**Methodological value high**: confirms iter 022 synthetic was 100% artifact.

---

## Citations

- Spitznagel *Safe Haven* (2021) — convex tail-hedge thesis
- `[risk_parity, ch.5, p.10]` Carlson capital-efficient base
- `[advances_fin_ml, p.208-211]` PBO + monotonic check (KILL #1)
- iter 022 (synthetic model) — gap quantified here

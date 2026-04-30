# spy_beater_hunt — Promising Directions (ranked)

**Created**: 2026-04-29.

Ranked list of hypotheses to test in spy_beater_hunt. Tier 1 = strongest literature backing + deployable. Tier 3 = exploratory.

---

## Tier 1 — Literature-strong, deployable

### A1. Gayed LRS — UPRO + 200d SMA gate ⭐ HIGHEST PRIORITY

**Hypothesis**: 100% UPRO (3× SPY) when SPY > 200d MA, else 100% IEF (or CASHX). Daily check, T+1 execution lag, no peek.

**Literature**: `[leverage_for_the_long_run, ch.3-4, p.40-60]` — Gayed shows 200d SMA gate dramatically reduces LETF decay and produces ~18-22% CAGR in backtests with MDD 25-35%.

**Configs to test (4)**:
- a1_pure_lrs: 100% UPRO when SPY>200d, else 100% IEF
- a1_lrs_cash: 100% UPRO when SPY>200d, else 100% CASHX
- a1_lrs_split: 50% UPRO + 50% SSO when on, else 100% IEF (lower vol)
- a1_lrs_kmlm_off: 100% UPRO when on, else 50% IEF + 50% KMLM (crisis-alpha when off)

**Expected outcome**: CAGR 16-22%, MDD 25-40%. KILL #6 fires if even pure LRS UPRO can't reach CAGR 13.80%.

**Why might fail**: 
- Whipsaw cost in choppy markets (signal flips back-forth)
- 2022 inflation: 200d SMA was triggered, but TLT/IEF also crashed
- LETF decay is real even with gate (~1-3%/y)

### A2. Gayed LRS — TQQQ + 200d SMA on QQQ

**Hypothesis**: same as A1 but on QQQ (more concentrated growth). 100% TQQQ when QQQ > 200d MA, else IEF.

**Literature**: same as A1, applied to NDX.

**Configs to test (4)**: similar to A1 but with TQQQ + QQQSIM signal.

**Expected outcome**: CAGR 20-30%, MDD 35-50%. Volatile but high CAGR.

**Why might fail**:
- 2000-02 dot-com (NDX -78%): TQQQ would be wiped out before 200d SMA caught
- Same regime gate weakness as A1

### B1. HFEA classical — 55% UPRO + 45% TMF (Hedgefundie's Excellent Adventure)

**Hypothesis**: 55% UPRO + 45% TMF (3× LTT) quarterly rebalanced. Classic HFEA from Bogleheads 2019.

**Literature**: HFEA forum thread + multiple academic papers on leveraged barbell. Long-history backtest shows ~22% CAGR + ~30% MDD pre-2022.

**Configs to test (4)**:
- b1_classic_5545: 55% UPRO + 45% TMF
- b1_modern_6040: 60% UPRO + 40% TMF
- b1_balanced_5050: 50% UPRO + 50% TMF
- b1_aggressive_7030: 70% UPRO + 30% TMF

**Expected outcome**: CAGR 18-25%, MDD 30-50%. Pre-2022 was excellent; 2022 was catastrophic (~70% MDD per backtests).

**Why might fail**:
- 2022 "60/40 worst year ever": TMF lost ~70%, UPRO lost ~50% — combined ~60-70% MDD
- Stagflation regime: both stocks AND bonds fall, no diversification
- TMF is a 3× LETF on long-duration Treasury — daily decay is significant (~3-5%/y)

**Need synth**: TMFSIM = `TLTSIM × 3 - 1.5%/y daily-reset decay`. Add to synths.py.

---

## Tier 2 — Literature-supported, more uncertainty

### A3. Mixed Gayed — UPRO + KMLM + TLT with regime gate

**Hypothesis**: leverage + crisis-alpha hybrid. 50% UPRO + 30% KMLM + 20% TLT when SPY>200d MA, else 30% UPRO + 50% KMLM + 20% TLT (defensive shift).

**Literature**: combines `[leverage_for_the_long_run]` Gayed + `[ilmanen, ch.19]` MF crisis-alpha.

**Configs (4)**: vary weights and gate thresholds.

**Expected outcome**: CAGR 14-18%, MDD 20-30%. More balanced than pure A1.

### C1. Vol-targeted SPY 1.5-2× leverage

**Hypothesis**: dynamic leverage based on realized 60d vol. When vol < 15%, leverage 1.5× (NTSX or 50/50 SPY+SSO). When vol > 25%, leverage 0.5× (50% SPY + 50% IEF).

**Literature**: vol-targeting literature (Carver `[systematic_trading]`).

**Configs (4)**: vary vol thresholds and leverage levels.

### B2. HFEA modern variants — UPRO + TMF + KMLM

**Hypothesis**: HFEA + 10-15% KMLM as crisis-alpha (mitigates 2022-style failure).

**Configs (4)**: 
- 50% UPRO + 35% TMF + 15% KMLM
- 55% UPRO + 30% TMF + 15% KMLM  
- 45% UPRO + 35% TMF + 20% KMLM
- 50% UPRO + 30% TMF + 10% KMLM + 10% TLT

---

## Tier 3 — Exploratory

### D1. Concentrated growth + monthly momentum gate

**Hypothesis**: 100% QQQ (or TQQQ at 33% leverage) with monthly momentum gate (in if 6m return > 0).

### C2. CAPE-timing — Shiller CAPE-based equity exposure

**Hypothesis**: equity exposure scales with `(median_CAPE / current_CAPE)` clamped [0.5, 2.0]. CAPE-low → leverage in, CAPE-high → reduce.

**Literature**: Shiller `[irrational_exuberance]`, `[asness_gmo_returns]`.

**Caveat**: CAPE has been "high" for 20+ years and timing has been wrong. Out-of-sample reliability questionable.

### D2. Stacked equity heavy — NTSX + UPRO + AVUV

**Hypothesis**: 35% NTSX + 35% UPRO + 30% AVUV with quarterly rebalance. Pure equity stacking, no bonds, no MF.

**Why interesting**: if pure equity stacking can hit CAGR 14-16% with manageable MDD.

**Why risky**: bear market → no diversification, MDD could be 50-60%.

---

## Stress test priorities (every iter)

Mandatory stress windows to evaluate:
1. **2008 GFC** (peak SPY −56%, peak QQQ −53%): how does strategy hold?
2. **2022 inflation** (60/40 worst year, SPY −20%, TLT −31%): leveraged barbells failed
3. **2020 COVID** (fast crash, fast recovery): regime gate whipsaw test
4. **2000-02 dot-com** (QQQ −78%): TQQQ-style strategies wiped out
5. **1973-74 stagflation** (sintético only): CAPE-low + bonds in

---

## Recommended execution order

**Iter 001**: A1 Gayed LRS UPRO 200d-SMA (highest literature priority)  
**Iter 002**: B1 HFEA classical 55/45  
**Iter 003**: A2 Gayed LRS TQQQ 200d-SMA  
**Iter 004**: A3 Mixed Gayed (UPRO + KMLM + TLT)  
**Iter 005**: B2 HFEA + KMLM crisis-alpha  
**Iter 006**: C1 Vol-targeted SPY  

After 6 iters, decide:
- If 0/6 produced WINNER → close hunt, F1+SPLIT confirmed as deploy. Document the impossibility result.
- If ≥ 1/6 produced WINNER → declare winner, run sensitivity analysis (iter 007+) on best winner before final report.

---

## What we're NOT testing (explicit closures from long_term_portfolio)

These directions are CLOSED per long_term_portfolio iters 027-038 (cumulative_n_trials=156):
- ❌ NTSD ex-US developed equity stack
- ❌ AVUV / AVDV / AVEM (Avantis SCV/profitability/value family at non-leveraged 1×)
- ❌ IDMO intl momentum (within noise)
- ❌ Substituting TLT with RSSB or removing TLT from F1 baseline

Knowledge negativo persisted in long_term_portfolio/PHASE_1_WINNERS.md.

---

## Citations

- `[leverage_for_the_long_run, ch.3-4, p.40-60]` Gayed — 200d SMA on LETFs
- `[risk_parity, ch.5, p.10]` Carlson — capital-efficient stacking baseline
- HFEA classical (Hedgefundie Bogleheads 2019)
- `[ilmanen_expected_returns, ch.19]` — MF crisis-alpha role
- `[advances_fin_ml, p.208-211, p.222-223, p.196-202, p.31-34]` — gate framework
- Carver `[systematic_trading]` — vol-targeting
- Shiller `[irrational_exuberance]` — CAPE-timing rationale (caveat: CAPE failed for 20y)

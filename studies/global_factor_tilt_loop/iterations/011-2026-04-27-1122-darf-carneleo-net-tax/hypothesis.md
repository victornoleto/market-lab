# Iter 011 — DARF + Carnê-Leão Net-of-Tax Cost Model on Iter 009

**Date**: 2026-04-27  
**Slug**: darf-carneleo-net-tax  
**Type**: Tax post-processing analysis (USER_DIRECTIVE — Tier 0 from BASE_MEMORY)

---

## Hypothesis

Iter 009 HAA+Gold WINNER (gross Sharpe 1.120, CAGR 13.89%, MDD 20.81% on edu 31y) is a
gross-return result. For a Brazilian retail investor using Inter Internacional (zero
commission), the real-world net return requires applying the full Brazilian-retail tax
pipeline:

1. **DARF 15%** on every month's realized capital gain from HAA position switches
   (Receita Federal IN 1.585/2015, Lei 13.043/2014). No R$35k exemption for foreign ETFs.
   12-month rolling loss carryforward. Applied using portfolio-level average-cost method.

2. **Carnê-Leão 27.5%** incremental on distributed dividends from KMLM (~3%/y yield)
   and GDE (~1%/y yield, S&P futures collateral income). Incremental burden vs DARF baseline:
   ~(27.5% − 15%) × weighted_annual_yield ≈ 5–8 bps/y. Applied as fixed annual deduction.

3. **Spread câmbio Inter Internacional ~1%** one-time on USD entry + exit.
   **IOF câmbio 0.38%** on FX conversion. Total FX drag ≈ 2.76% one-time,
   ≈ 9 bps/y amortized over 30y. Applied at start and end.

4. **Zero brokerage** (Inter Internacional confirmed per project memory).

The question this iter answers: *After Brazilian taxes, does HAA+Gold still beat
Plano C V3_1 v3.5 net-of-tax (buy-hold, 15% DARF terminal sale formula)?*

---

## Edge source

VT, Plano C, and V_HYBRID+MF are all compared at gross returns. HAA's advantage in this
loop has been ~3pp CAGR (13.89% vs 10.94% on edu). But HAA switches positions every
1–3 months on average, triggering DARF at each switch. Plano C is a static buy-hold that
defers all DARF to a terminal sale 30 years out — dramatically lower effective tax rate.
This iteration quantifies whether HAA's gross alpha survives the Brazilian tax regime.

---

## What iter 009/VT/Plano C miss

- **VT b&h**: zero intra-holding tax events; DARF only at terminal sale → ~0.1%/y drag
- **Plano C V3_1 v3.5**: same as VT — buy-hold → minimal DARF during accumulation
- **V_HYBRID+MF**: not modeled in this loop (separate deploy_studies analysis)
- **HAA+Gold**: monthly switches = frequent DARF events; estimated ~0.5–2%/y drag

---

## Datasets

- `educational` (~31y, 1995–2026): primary long-window test
- `vt_real` (~17y, 2008–2026): real-world window
- `ndx_real` (16y, 2010–2026): carryover stress test (QQQ benchmark)

Simulation method: re-run iter 009 HAA+Gold logic (same parameters, single config)
with monthly weight extraction → apply tax pipeline → derive net daily returns.

---

## Implementation plan

1. Duplicate iter 009 simulation logic with weight extraction
2. Implement `DarfCostBasisEngine` (portfolio-level average-cost method):
   - Track `cost_basis` (dollars) and `port_value` (current market value)
   - At each month-end: compute `sold_fraction`, `realized_gain`, DARF amount
   - Apply 12-month rolling loss carryforward (deque of 12 monthly balances)
   - Deduct DARF from equity curve; rebase cost_basis for new purchases
3. Add Carnê-Leão incremental as a fixed annual deduction (~6 bps/y)
4. Add FX costs as one-time start/end deductions
5. Derive net daily returns from modified equity curve
6. Run 7-gate battery on net returns
7. Run standard scoring rubric on net metrics vs gross benchmarks
8. Compute Plano C net-of-tax using terminal sale formula
9. Report gross vs net per dataset + net HAA vs net Plano C comparison

---

## Pre-committed kill criteria

- **Kill 1 (INCOMPLETE)**: annualized turnover (sum of monthly sold_fractions) > 150%
  → means cost basis detection is broken; HAA cannot have that much turnover
- **Kill 2 (TAX_MODEL_ERROR)**: net CAGR < 0.8 × gross CAGR on any dataset
  → DARF drag > 20% of gross gains, which is impossible under 15% rate + average holding

---

## Expected budget

- N configs: 1 (deterministic tax post-processing; no grid)
- Wall-time: < 5 min (re-run + tax model is light computation)
- Cumulative n_trials after this iter: 28

---

## Decision criterion (from BASE_MEMORY)

- Net margin (net HAA CAGR − net Plano C CAGR) > 2pp/y → **Significant** (HAA preferred)
- Net margin 1–2pp/y → **Borderline** (operational complexity may not be worth it)
- Net margin < 1pp/y → **Marginal** (Plano C preferred for retirement context)

---

## Primary citations

- `[testing_tuning, ch.5-6]` — cost-aware backtest methodology; out-of-sample cost simulation
- `[risk_parity, ch.5]` — capital efficiency; multi-asset cost considerations
- `[trading_evolved, p.197]` — managed futures cost and tax friction
- `[advances_fin_ml, p.196-202]` — gate battery calibration
- Receita Federal IN 1.585/2015 + Lei 13.043/2014 — DARF on foreign ETFs (regulatory refs)

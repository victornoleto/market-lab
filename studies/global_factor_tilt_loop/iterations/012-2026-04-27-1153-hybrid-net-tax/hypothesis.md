# Iter 012 Hypothesis — 50/50 Hybrid Net-of-Tax (HAA+Gold + Plano C V3_1)

## Loop context

Iter 011 showed HAA+Gold net-of-DARF has ~1.6pp CAGR advantage over Plano C net (BORDERLINE by
user's decision table). The 1.76pp annual DARF drag arises because HAA pays DARF ~2.5×/year on
monthly rebalancing, while Plano C defers all tax to terminal sale.

**Hypothesis**: A 50/50 blend of HAA+Gold (active, high-DARF) and Plano C V3_1 (passive, zero-DARF
until terminal) should:
1. Cut monthly DARF events by ~50% (from 2.5/year to ~1.3/year on the combined portfolio)
2. Preserve ~80%+ of HAA's Sharpe advantage via diversification benefit
3. Produce a net CAGR > Plano C net by a clearer margin than the borderline ~1.6pp

**Test question**: Is the hybrid a Pareto improvement — better risk-adjusted return than 100% Plano C
AND materially lower operational complexity than 100% HAA?

**Kill criterion**: hybrid net Sharpe < 100% Plano C net Sharpe on the educational dataset.

---

## Portfolio construction

| sleeve | weight | implementation | monthly DARF | terminal DARF |
|---|---|---|---|---|
| HAA+Gold (iter 009) | 50% | NTSXSIM/NTSI/NTSE/GDESIM top-2 + KMLM10% + GLD5% | YES (monthly) | NO (already realized) |
| Plano C V3_1 v3.5 | 50% | GDESIM/SPYSIM/VEASIM/VWOSIM/VBRSIM/GLDSIM proxy | NO | YES (one-time) |

Annual 50/50 rebalance between sleeves: small DARF event when balance delta > 0.
(Expected < 10bps/year — see iter 011 DARF mechanics analysis.)

---

## Plano C V3_1 v3.5 proxy weights

Copied from `studies/strategy_hunt_loop/deploy_studies/v1_vs_planoc/v1_vs_planoc_validator.py`:

```
GDE  = 25%  → GDESIM  (90% S&P + 90% gold)
AVUS = 12%  → SPYSIM  (US large core proxy)
AVDE = 20%  → VEASIM  (DM developed proxy)
AVEM = 13%  → VWOSIM  (EM proxy; binding from 1994-05)
AVUV = 10%  → VBRSIM  (US small cap value)
AVDV =  5%  → 0.5×VEASIM + 0.5×VBRSIM  (DM SCV rough proxy)
SPMO =  7%  → SPYSIM  (no momentum synth)
IDMO =  3%  → VEASIM  (no DM momentum synth)
BTGD =  5%  → GLDSIM  (BTC proxy underestimates — conservative)
```

Known proxy biases (conservative = understates Plano C):
- SPMO: SPY understates momentum premium by ~0.5-1pp/year
- BTGD: no BTC synth pre-2014; gold understates by ~50-200bps/year
- Factor premium: AVUV/AVDV/AVES value tilts not fully captured by VBRSIM
Citations: `[trading_evolved, p.197]`, `[risk_parity, ch.5]`, `[testing_tuning, ch.5-6]`

---

## Tax model

### HAA sleeve (50%)
- Identical to iter 011 DarfCostBasisEngine
- DARF 15% on monthly realized gains (portfolio avg-cost method, 12m loss carryforward)
- Carnê-Leão 27.5% incremental on KMLM/GDE yield: ~4.7bps/year on HAA sleeve only
- Starting value: $5,000 (half of $10,000 initial)
- FX entry 1.38%: applied proportionally ($5,000 → $4,931 effective)

### Plano C sleeve (50%)  
- No monthly DARF (pure buy-hold internally)
- No Carnê-Leão (Plano C has no KMLM; GDE dividend yield ~0.1% → incremental < 1bps; ignored)
- Starting value: $5,000 → $4,931 effective after FX entry
- DARF only at:
  (a) Annual 50/50 rebalance: if Plano C sleeve sold, pay DARF on gain of sold fraction
  (b) Terminal sale: DARF 15% on total accumulated gain

### Combined portfolio
- FX exit 1.38%: applied to total terminal value (proportional to each sleeve's terminal value)
- Annual rebalance DARF expected < 10bps/year (estimated from iter 011 CAGR differential)

---

## Datasets (same as iter 011)

- **educational**: 1994-05-01 → 2026-04-24 (~31y; VWOSIM inception)
- **vt_real**: 2008-06-01 → 2026-04-24 (~17y; GFC through present)  
- **ndx_real**: 2010-02-01 → 2026-04-24 (~16y; QQQ benchmark)

---

## Gate battery (same 7-gate spec)

G1 PBO (N=1 → auto-pass), G2 DSR, G3' WF-8 adapted, G4 OOS 70/30, G5 FWD post-2020,
G6 Bootstrap 99.9%, G7 cross-lib ±3pp. Applied to HYBRID net returns.

---

## Expected outcome

Based on iter 011 results:
- Hybrid net CAGR ≈ 0.5 × 12.13% + 0.5 × 10.27% ≈ 11.2% (arithmetic blend, ignoring correlation bonus)
- Hybrid net Sharpe: harder to predict — depends on correlation between HAA and Plano C returns
- Hybrid MDD: expected to be between HAA (21.83%) and Plano C (~52%)
- Monthly DARF events: ~1.2-1.5/year (HAA half only)

Kill criterion: hybrid net Sharpe ≥ Plano C net Sharpe (empirical, computed on proxy returns)

---

## Citations

- `[testing_tuning, ch.5-6]`: cost-aware backtest; out-of-sample simulation
- `[risk_parity, ch.5]`: capital efficiency; multi-asset blend mechanics
- `[trading_evolved, p.197]`: MF cost and tax friction
- `[advances_fin_ml, p.208-211]`: G1 PBO; `[p.222-223]`: G2 DSR; `[p.196-202]`: G6 Bootstrap
- Receita Federal IN 1.585/2015: DARF on foreign ETFs
- Lei 13.043/2014: capital gains taxation

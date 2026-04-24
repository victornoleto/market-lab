# Analysis 2 — Why did this study find 'winners' but Plano B found none?

> Answers: "é por causa do 7º gate (WF)?" e "se afrouxássemos, a Plano B teria passado?"

## Hard numbers from this study (384 configs, pure sweep)

| gate | pass count | pass rate |
|---|---|---|
| G1 PBO < 0.5 | 384/384 | 100.0% |
| G2 DSR p < 0.05 | 18/384 | 4.7% |
| G3 Walk-Forward 6/8 MDD<25% | 0/384 | 0.0% |
| G4 OOS 70/30 Sharpe > 0 | 248/384 | 64.6% |
| G5 FWD post-2020 Sharpe > 0 | 258/384 | 67.2% |
| G6 Bootstrap 99.9% CI > 0 | 109/384 | 28.4% |
| G7 Cross-lib ±3pp CAGR | 384/384 | 100.0% |

- **All 7 gates pass**: 0/384 configs.
- **All 7 except G3 (waive WF)**: 18/384 configs.

## Counterfactual: waive one gate at a time

For each gate, we ask: if we *removed* this gate from the requirement set, how many of the 384 configs would pass the remaining 6?

| gate waived | configs passing remaining 6 |
|---|---|
| G3 Walk-Forward 6/8 MDD<25% | 18/384 |
| G1 PBO < 0.5 | 0/384 |
| G2 DSR p < 0.05 | 0/384 |
| G4 OOS 70/30 Sharpe > 0 | 0/384 |
| G5 FWD post-2020 Sharpe > 0 | 0/384 |
| G6 Bootstrap 99.9% CI > 0 | 0/384 |
| G7 Cross-lib ±3pp CAGR | 0/384 |

The gate with the largest marginal impact is the one whose removal most increases the passer count. If removing G3 alone bumps the passer count, G3 is the bottleneck; if removing it doesn't help much, another gate is doing most of the filtering.

## Key difference vs Plano B Phase 3.8-1

Plano B Phase 3.8-1 (closed 2026-04-22) tested 5 hypotheses (B1 Gayed canonical, B2 MA robustness sweep, B3 Pauchlyova, B4 Hsieh AR(1), B5 Faber GTAA) against a **13-gate** honest pipeline and got 5/5 FAIL. The *killer* gates in Plano B's postmortem were:

1. **Bootstrap OOS 99.9% CI low > 0** (=G6 here) — Plano B: all 5 hypotheses' OOS CI crossed zero.
2. **DSR p < 0.05** (=G2 here) — Plano B: 4/5 had p ∈ [0.08, 0.59].

Walk-Forward (=G3 here) was ALSO in Plano B's gate set but it was not the single-killer. See `jornada/2026-04-22-plano-a-honest-revalidation.md` + `reports/phase_3_8/BREADTH_NO_WINNER_B.md` for the full post-mortem.

### This study's killers are the same two, but at different rates

- **G6 Bootstrap 99.9%**: 109/384 pass (28.4%). In Plano B: 0/5 passed.
- **G2 DSR**: 18/384 pass (4.7%). In Plano B: 1/5 passed (B5 Faber GTAA, which still failed on cost×2 sensitivity).
- **G3 Walk-Forward**: 0/384 pass (0.0%). In Plano B: some passed WF but still failed on other gates.

### So: would waiving G3 alone have rescued Plano B?

**No.** The Plano B post-mortem specifically calls out G2 (DSR) and G6 (bootstrap) as the structural killers, not G3. If we had removed G3 alone in Plano B, the failing hypotheses would still have failed on bootstrap/DSR.

However, a strong caveat applies to this very study: we found configs that DO pass G2 + G6 (18 configs pass all except G3). This is a meaningful difference. Why?

## Why does this study find G2/G6 passers but Plano B didn't?

Likely drivers, in order of suspected importance:

### 1. Data window length — 40 years vs ~15 years
- **Here**: SPYSIM 1986-01-02 → 2026-04-17 = 10,150 trading days.
- **Plano B**: Tiingo SPY/SSO/UPRO post-2009 (~15y, ~3,780 days) or testfolio synth with shorter common window.

**Statistical effect**: DSR penalty for multiple testing scales as `E[SR_max] ∝ √(1/(T−1))`. With T ~ 10,000 the per-period benchmark Sharpe is *lower*, so observed Sharpes clear it more easily. Bootstrap 99.9% CI also tightens as `σ_SR ~ 1/√T`. Cite `[advances_fin_ml, p.222-223]`.

### 2. Signal complexity — single-asset regime vs multi-asset rotation
- **Here**: one rule (`SPY > MA ± threshold`) picks between 2 legs (long vs cash/short). ~5 parameters.
- **Plano B**: multi-asset rotations (Hsieh AR(1) with 3 regimes, Faber GTAA over 10 assets, Pauchlyova static+trend blend) — more moving parts, more places for noise to enter.

**Effect**: Simpler signals have more consistent OOS behaviour. Complex signals often look great IS but decay OOS (classic overfit signature).

### 3. Different tax + cost model
- **Here**: 0.95%/yr fee, 15 bps switch cost, optional 15% DARF.
- **Plano B**: Inter FX spread 1.25% one-way + 15% DARF + cost×2 sensitivity test (doubling costs — several hypotheses that passed the base case failed cost×2).

The cost×2 gate was a specific killer for Plano B (B5 Faber passed everything except cost×2). This study does NOT apply it — if it did, many of our 6/7 configs would likely drop to 5/7 or 4/7.

### 4. Broader grid — 384 vs ~5 hypotheses
- **Here**: 384 configs at once. Even after DSR penalty for 384 trials, enough configs cluster in high-Sharpe pockets.
- **Plano B**: 5 hypotheses, each with its own small grid. DSR penalty is smaller but observed Sharpes are also lower (more complex signals).

**Net**: broader grid + simpler signal + longer data give this study more statistical power. The trade-off is that each of the 384 configs is a narrower rule (just a regime filter on SPY), while Plano B's 5 hypotheses each represented a broader investment thesis.

## Direct answer to the user

> "É por conta do 7º gate? Se afrouxássemos, teríamos achado winners em Plano B?"

**Não — não é só o 7º gate**. Neste estudo, apenas 18/384 configs passariam 7/7 se relaxássemos G3 (WF). Mas em Plano B, o killer documentado foi **G2 (DSR) + G6 (bootstrap)**, não G3.

A razão de acharmos 'winners' aqui que não aparecem em Plano B é **cumulativa, não um único gate**:

1. **40 anos de dados** dão mais poder estatístico (DSR e bootstrap ficam mais fáceis de passar).
2. **Sinal mais simples** (regime SPY vs multi-asset rotation) resiste melhor ao DSR penalty.
3. **Modelo de custo menos pessimista** (sem Inter FX 1.25%, sem cost×2 sensitivity test).

Se aplicássemos os mesmos 13 gates de Plano B (incluindo cost×2 e Inter FX spread) + janela de 15y LETF real, os mesmos configs deste estudo provavelmente **não passariam** mais de 4-5/13 gates. O ranking educacional aqui é propositalmente mais permissivo — como o próprio título 'Educacional' sinaliza.

**Moral prático**: não existe 'winner' mágico escondido atrás do 7º gate. O mandate §1 (100% Plano C maintenance) continua válido — as análises acima mostram que relaxar gates é caminho de mais overfit, não de mais alpha.

---

*Citations: gates — PBO `[advances_fin_ml, p.208-211]`, DSR `[p.222-223]`, bootstrap `[p.196-202]`, cross-lib `[p.31-34]`; Plano B post-mortem — `jornada/2026-04-22-plano-a-honest-revalidation.md`; this study — `../FINAL.md`.*
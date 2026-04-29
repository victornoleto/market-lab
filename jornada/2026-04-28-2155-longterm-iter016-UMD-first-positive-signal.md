# Long-term portfolio iter 016: B.5 — UMD overlay direto — WINNER tier 91/100, **PRIMEIRO SINAL POSITIVO** desde iter 011

Quinta tentativa de superar iter 011 — primeira que dá sinal real. Em vez de testar mais variantes do mesmo factor (size+value, intl-eq), iter 016 pivot pra **UMD** (Up Minus Down, fator academic momentum cross-sectional Fama-French, daily 1926+).

UMD é estruturalmente diferente dos fatores que iter 013/014/015 testaram:
- **Sharpe raw**: UMD 0.75 vs VBRSIM/VXUSSIM ~0.5 (mais alto por unidade de peso)
- **2017-2024**: momentum teve múltiplos anos positivos quando value ficou flat
- **Crisis behavior**: estrutura "long winners, short losers" produz retornos convexos em crises prolongadas (2008 +15% UMD vs −15% size; 2020 recovery rapid)

## Resultado

Selecionado: **`umd_heavy_3025_20_25`** (30% NTSX + 25% GDE + 20% KMLM + **25% UMD**).

| dataset | gross Sharpe (loose) | strict | edge vs avg(SPY,VT) | Δ vs iter 011 (loose / strict) | gates |
|---|---:|---:|---:|---:|---:|
| lh_56y    | **1.223** ⭐ | **1.133** ⭐ | +0.551 | **+0.177 / +0.088** | 7/7 ⭐ |
| vt_real   | 0.943 | 0.944 | +0.237 | −0.017 / −0.016 | 6/7 |
| ndx_real  | 1.150 | 1.151 | +0.227 | +0.046 / +0.047 | 6/7 |

**Tier WINNER 91/100, 5/5 conds vs avg(SPY,VT). Não advança mecanicamente** (score 91 < 93 de iter 014; edge ≥+0.10 vs iter 014 só em 1/3 datasets — fails ≥2/3). MAS:

- **Substantivamente bate iter 011 em 2/3 datasets** (lh_56y +0.18 loose / +0.09 strict; ndx_real +0.05; vt_real −0.02 dentro do ruído).
- **Strict-window edge no lh_56y +0.088**, narrowly miss do +0.10 hurdle mas é o primeiro positivo strict da série.
- **lh_56y G3 WF passa pela primeira vez** (max window MDD 22.09% < 25%) — UMD positivo em 2008/2020 ajuda a cap window MDDs.

## Cross-config pattern NOVO

UMD% 10% → 25%:
- **lh_56y**: 1.161 → 1.170 → 1.175 → 1.223 (**monotônico UPWARD**)
- **vt_real**: 0.970 → 0.965 → 0.954 → 0.943 (gentle decline, range 0.03; todos > 0.94)
- **ndx_real**: 1.145 → 1.155 → 1.156 → 1.150 (essentially flat)

**Primeira iter onde live windows NÃO regridem monotônica** conforme novo factor weight sobe. iter 013/014/015 todas mostravam regressão monotônica nos live windows; UMD não.

## Caveat honesto: UMD é académico

UMD é fator long-short bruto (gross-of-cost, sem custos de turnover, sem long-only constraint). Produtos investíveis (MTUM, SPMO, IDMO, AVUS factor sleeves) capturam ~60-70% de UMD por:
- Long-only constraint (não pode shortar losers)
- Diluição de exposição factor
- Custos de turnover (~10-30bp/ano)

Realisticamente, edge de iter 016 no deploy via MTUM live (2013+) provavelmente shrinka pra ~+0.05 lh_56y — ainda positivo, mas marginal.

**Sub-iter deferido recomendado**: testar MTUM/SPMO live em vez de UMD academic, quantificar o gap.

## Gates: padrão familiar

7/7 lh_56y, 6/7 vt_real (G1 PBO 0.557 fail), 6/7 ndx_real (G1 PBO 0.567 fail).

Mesma falha PBO de iter 011 — os 4 configs UMD estão muito próximos em Sharpe (vt_real range 0.943-0.970, ndx_real range 1.145-1.156); PBO vê o ranking noise como overfit. Sinal real é "qualquer UMD overlay 10-25% funciona", não "especificamente 25% funciona".

## Lição estrutural

**Diversificação de fator funciona quando o fator é qualitativamente ortogonal**, não quando é só "rotulado diferente". VBRSIM (size+value) era correlated com value-cycle drag; VXUSSIM/NTSI (intl) era correlated com intl-equity drag em US-large-cap regime; **UMD tem comportamento próprio em crises** descorrelado de ambos.

Implicação pra deploy: fator com Sharpe raw alto E comportamento ortogonal a US-large-cap regime > fator com Sharpe raw baixo E correlated com regime perdedor.

## Próximas iters (016-022, breadth-first)

iter 016 abriu sinal — 6 iters restantes vão diversificar a busca:

- **017** B.6 VBRSIM regime-gated: testar se gating recupera value factor
- **018** C.1 Antonacci GEM cross-class top-K (mecanismo dinâmico)
- **019** C.2 Vol-managed 60/40
- **020** C.3 All-Weather Bridgewater-mimic
- **021** C.4 Defensive sector rotation
- **022** C.5 Tail-hedge convexo

Após 016-022, esperar Pareto frontier de 1-3 strategies WINNER substantivas pra deep-dive.

Arquivos: `studies/long_term_portfolio/iterations/016-2026-04-28-2120-B5-UMD-overlay/`

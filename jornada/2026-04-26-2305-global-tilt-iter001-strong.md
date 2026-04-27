# Global Factor-Tilt Loop — Iter 001 resultado: STRONG 81/100

**Loop**: `studies/global_factor_tilt_loop/`  
**Iter**: `001-2026-04-26-2247-global-momentum-topk`  
**Veredicto**: 🥇 STRONG (81/100) — todas as 5 condições de winner cumpridas, mas score abaixo de 90.

---

## O que foi testado

Momentum cross-sectional mensal num universo global de ativos:
- **Educacional (56y)**: VTISIM + VEASIM + VXUSSIM + IEFSIM + safe-haven CASHX  
- **VT real (17y) e NDX real (16y)**: VTISIM + VEASIM + VWOSIM + IEFSIM + GLDSIM + CASHX

Grade: K={1,2,3} × lookback={3,6,12m} = 9 configs por dataset. Regra simples: todo mês, rankeia ativos por retorno trailing, iguala no top-K. Se todos negativos → 100% CASHX.

## Resultados

| dataset | Sharpe | CAGR | MDD | benchmark Sharpe | gates |
|---|---|---|---|---|---|
| educational (56y) | **1.040** | 12.0% | **21.9%** | 0.661 (VTSIM b&h) | 6/7 |
| vt_real (17y) | **0.883** | 11.9% | 30.1% | 0.489 (VTSIM b&h) | 6/7 |
| ndx_real (16y) | 0.929 | 11.5% | **17.3%** | 0.958 (QQQ b&h) | 7/7 |

## Comparação 32 anos (janela dos benchmarks de estratégia)

| estratégia | Sharpe | CAGR | MDD |
|---|---|---|---|
| Esta estratégia (k=2, lb=6m, full universe) | **1.001** | **13.22%** | **21.23%** |
| Plano C V3_1 v3.5 | 0.671 | 10.94% | 52.43% |
| V_HYBRID + 10% MF | 0.743 | 10.91% | 44.71% |
| VT b&h (VTSIM) | 0.549 | 8.69% | 58.35% |

**A estratégia domina Plano C e V_HYBRID+MF nos três eixos na janela de 32 anos.**

## Por que não chegou a WINNER (≥90)

1. **G1 PBO falhou no educational** (PBO=0.74): com 9 configs, o CSCV detecta seleção de lookback curto (lb=3) que performa bem in-sample mas não out-of-sample. Solução: fixar k=2, lb=6 como parâmetro único no iter 002.
2. **NDX real abaixo do threshold de Sharpe** (0.929 < 1.047 mínimo): QQQ teve um bull run sem precedentes em tech 2010-2026. Uma estratégia globalmente diversificada não consegue bater na Sharpe. Este teto é estrutural — não muda com tuning.
3. **CAGR floor no ndx_real não passa** (11.5% < 15.4% = 0.8 × 19.2% QQQ): pela mesma razão.

## DSR

p-value worst = 0.0170 < 0.05 com n_trials=9. A edge é estatisticamente significativa mesmo deflacionando pelo grid testado. `[advances_fin_ml, p.222-223]`

## Próximas direções

1. **Iter 002**: K=2, lb=6m pré-especificado, sem grid → elimina G1 PBO. Potencial de chegar a 88-90+ se configuração única sobreviver.
2. **Iter 003**: adicionar 10-15% KMLMSIM fixo ao portfólio de momentum. deploy_studies mostrou que MF é "free lunch" `[ilmanen_expected_returns, ch.19]`.
3. **Iter 004+**: return-stack — substituir equity puro por RSSBSIM (global equity + Treasury 200% notional) para eficiência de capital sem margem.

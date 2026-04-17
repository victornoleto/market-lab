# A3d — 3-leg portfolio {LETF EMA100/2x + QQQ Donchian 20/10 + GLD Donchian 40/20} ★ PASS

**Tag:** `[SWING BROKER]` · **Fase 3 lead:** A3d · **Iter loop:** 38 · **Verdict:** ★ PASS (winner: GLD como 3ª perna).

## Contexto

Iter 37 (A3c) testou o portfolio 2-leg {LETF EMA100/2x + QQQ Donchian 20/10}
e detectou o mesmo problema que todo livro de alocação já apontou: as duas
pernas eram long-equity US com ρ=0.555; o blend passou em Sharpe mas falhou
em **Diversification Ratio** (EW DR=1.124 < 1.2, teto prático de duas pernas
correlatas). O investment mandate/Prado dizem que pra extrair
"true diversification" a gente precisa combinar regimes —
`[advances_fin_ml, p.302-313, ch.16]`. Logo: **adicionar uma 3ª perna
descorrelata** (TLT = long-duration Treasury, regime risk-off; GLD = ouro,
hedge macro clássico) e blendar com **EW / IVP / HRP** (López de Prado
Listing 16.2). Meta: DR ≥ **1.3** (subimos o sarrafo vs A3c porque agora
pagamos 3 pernas de custo/tax 15% BR).

## Setup

- **Leg 1** — LETF rotation EMA100 band=0% lev=2x (winner B1c, iter 32) sobre
  SPX TR stitched 1970-2026 (KF+Tiingo).
- **Leg 2** — QQQ Donchian 20/10 (winner A3b, iter 36) sobre Tiingo daily
  2001-05-14 → 2026-04-14.
- **Candidatos 3ª perna:** TLT Donchian 55/20 e GLD Donchian 40/20, ambos
  parâmetros canônicos Turtle `[trading_systems_methods, p.353]`. Janela
  longest per-ticker do manifest Tiingo (TLT 2002-07-26, GLD 2004-11-18).
- **Splits mutuamente exclusivos:** IS 60% / OOS 25% / Stress 15% sobre a
  janela comum das 3 séries — mesma convenção de A3b/A3c.
- **Gates A3d:** OOS Sharpe > max(leg_Sharpe_OOS), DR_full > 1.3, DSR p<0.05,
  WF ≥ 6/8 com MaxDD ≤ 25%, OOS/Stress Sharpe > 0, bootstrap 99.9% CI
  low > 0.
- **Implementação:** `src/ai_trade/backtest/grid/portfolio_3leg.py` +
  `scripts/run_a3d_3leg_portfolio.py`. HRP via scipy single-linkage sobre
  `d=√((1-ρ)/2)` + recursive bisection Listing 16.2 `[advances_fin_ml,
  p.308]`. +15 testes; pytest **550 passed** (era 535 baseline iter 37).

## Resultados — candidato **TLT Donchian 55/20**

Janela comum 2002-07-26 → 2026-04-14 (5967 bars). Baseline OOS Sharpe =
2.072 (LETF domina).

| Perna | IS | OOS | Stress | CAGR(oos) |
|---|---|---|---|---|
| LETF_EMA100_2x | 1.782 | **2.072** | 1.959 | 54.47% |
| QQQ_Donchian_20_10 | 1.239 | 1.781 | 1.651 | 22.24% |
| TLT_Donchian_55_20 | 0.839 | 0.451 | **-0.121** | 3.57% |

Pair correlations (full): ρ(LETF,QQQ)=+0.568 · ρ(LETF,TLT)=-0.140 ·
ρ(QQQ,TLT)=-0.101. Screening TLT: **PASS** (|ρ|<0.2 AND Sharpe>0).

| Blend | w | OOS Sh | DR | DSR p | CAGR(oos) | MDD(oos) | Verdict |
|---|---|---|---|---|---|---|---|
| EW (1/3,1/3,1/3) | — | **2.297** | 1.397 | 0.0000 | 25.87% | -9.77% | ★ PASS |
| IVP | (0.097,0.323,0.580) | 1.939 | 1.606 | 0.0001 | 14.08% | -6.93% | FAIL (Sh≤baseline) |
| HRP | (0.077,0.256,0.667) | 1.691 | 1.569 | 0.0010 | 11.86% | -7.97% | FAIL (Sh≤baseline) |

EW PASS, boot 99.9% CI [0.975, 3.642]. IVP/HRP falham porque sobre-pesam
TLT (baixa vol) e TLT tem Stress Sharpe **negativo** (Fed hikes 2022-24
quebraram o regime do ativo).

## Resultados — candidato **GLD Donchian 40/20** ★

Janela comum 2004-11-18 → 2026-04-14 (5383 bars). Baseline OOS Sharpe =
2.013.

| Perna | IS | OOS | Stress | CAGR(oos) |
|---|---|---|---|---|
| LETF_EMA100_2x | 1.794 | **2.013** | 1.930 | 56.44% |
| QQQ_Donchian_20_10 | 1.380 | 1.676 | 1.777 | 22.64% |
| GLD_Donchian_40_20 | 0.803 | 1.010 | 1.324 | 9.76% |

Pair correlations (full): ρ(LETF,QQQ)=+0.588 · ρ(LETF,GLD)=+0.063 ·
ρ(QQQ,GLD)=+0.033. Screening GLD: **PASS**. GLD tem Sharpe positivo em
todos os 3 splits — diferente de TLT.

| Blend | w | OOS Sh | DR | DSR p | CAGR(oos) | MDD(oos) | Verdict |
|---|---|---|---|---|---|---|---|
| EW (1/3,1/3,1/3) | — | **2.251** | 1.376 | 0.0000 | 29.06% | -10.86% | ★ PASS |
| IVP | (0.121,0.502,0.377) | 2.142 | 1.435 | 0.0000 | 21.73% | -8.83% | ★ PASS |
| HRP | (0.104,0.430,0.466) | 2.128 | **1.456** | 0.0000 | 20.01% | -8.08% | ★ PASS |

**Winner por OOS Sharpe: EW** (Sh 2.251 > baseline 2.013, DR 1.376 > 1.3,
boot CI [0.946, 3.612]). HRP dá o melhor DR 1.456 mas ~5bps a menos de
Sharpe. Todos 3 métodos passam — signal forte de robustez ao método de
combinação.

## Gates — tabela síntese

| Gate | Alvo | TLT/EW | GLD/EW | GLD/IVP | GLD/HRP |
|---|---|---|---|---|---|
| OOS Sharpe > baseline | > 2.072 / 2.013 | ✅ 2.297 | ✅ 2.251 | ✅ 2.142 | ✅ 2.128 |
| DR_full | > 1.3 | ✅ 1.397 | ✅ 1.376 | ✅ 1.435 | ✅ 1.456 |
| DSR p-value | < 0.05 | ✅ 0.0000 | ✅ 0.0000 | ✅ 0.0000 | ✅ 0.0000 |
| WF profitable | ≥ 6/8 | ✅ 8/8 | ✅ 8/8 | ✅ 8/8 | ✅ 8/8 |
| OOS Sharpe | > 0 | ✅ | ✅ | ✅ | ✅ |
| Stress Sharpe | > 0 | ✅ 1.97 | ✅ 2.38 | ✅ 2.37 | ✅ 2.29 |
| Boot 99.9% CI low | > 0 | ✅ 0.975 | ✅ 0.946 | ✅ 0.891 | ✅ 0.867 |

## Decisão de produção

**Path B operacional passa a ser 3-leg:** `{LETF EMA100/2x (42-47%), QQQ
Donchian 20/10 (30-43%), GLD Donchian 40/20 (33-47%)}` — pesos EW/IVP/HRP
todos válidos. Recomendação:

- **Produção default: EW 1/3/1/3/1/3.** Simplicidade máxima (zero estimação
  IS), OOS Sharpe 2.251, CAGR 29.06%, MDD -10.86%. Regra Prado 1:
  covariance-estimation error kills optimizers primeiro `[advances_fin_ml,
  p.298-299]`.
- **Alternativa conservadora: HRP.** DR 1.456 > EW (1.376), OOS só 12bps
  menor, CAGR 20.01%. Interpretação HRP `[advances_fin_ml, p.313]` é que
  OOS variância empírica < IVP < CLA — ganhamos estabilidade de pesos em
  regimes adversos. Trade-off aceitável.

**TLT 3rd leg rejeitada em produção** — Stress Sharpe negativo (2022-2024
era de hikes massivas) e só EW passou. Deixar TLT como comparação
científica; readmitir apenas se Fed reverter ciclo.

## Citations consolidadas

- HRP recursive bisection + IVP cluster var: `[advances_fin_ml, p.302-313,
  ch.16]`, Listing 16.2 p.308.
- DR Choueifaty-Coignard: `[advances_fin_ml, p.302-313, ch.16]`.
- Donchian 55/20 + 40/20 canônicos Turtle: `[trading_systems_methods,
  p.353]`.
- Markowitz instability rationale: `[advances_fin_ml, p.298-299]`.
- PBO/CSCV: `[advances_fin_ml, p.208-211]`.
- DSR: `[advances_fin_ml, p.196-202, p.273-275]`.
- Stationary block bootstrap: `[advances_fin_ml, p.196-202, ch.11]`.
- Gayed LRS EMA/SMA filter: `[leverage_for_the_long_run, p.13, p.14]`.
- BR 15% swing tax: Investment Mandate §4.

## Artefatos

- Código: `src/ai_trade/backtest/grid/portfolio_3leg.py`
- Script: `scripts/run_a3d_3leg_portfolio.py`
- Testes: `tests/test_portfolio_3leg.py` (15 casos, todos verdes)
- Reports:
  - `reports/a3d_3leg_TLT_Donchian_55_20.json`
  - `reports/a3d_3leg_GLD_Donchian_40_20.json`
  - `reports/a3d_summary.json`
- Pytest: **550 passed** (era 535 iter 37 baseline).

## Próximo passo

Os 5 leads da Fase 3 agora têm verdict: A1 PARTIAL-GO, B1 PASS, A2 PASS, B2
REPLACE, A3 (a=FAIL, b=PASS QQQ, c=PARTIAL, d=PASS GLD). Próxima iter
deveria produzir **summary jornada consolidada** `jornada/2026-04-XX-phase3-summary.md`
com decisão GO/NO-GO por lead → flip do `status: done`. O loop termina
limpo.

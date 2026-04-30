# spy_beater_hunt iter 008 — HFEA clássico bate o teto de CAGR mas falha estruturalmente o bar de MDD (KILL #24 fired)

**Data**: 2026-04-30 01h00
**Iter slug**: `008-2026-04-30-B1-hfea-classical`
**Tier**: PROMISING **63/100** (winner_conditions_met = **FALSE**, MDD bar falhou)
**Selected**: `b1_balanced_5050` (50% UPRO + 50% TMF)

## O que mudou

Iter 007 fechou TQQQ-track saturado em 67 — `a6_tqqq_split_kmlm30_tlt10`
(iter 006) e `a7_tqqq_split_kmlm40_tlt10` (iter 007) empataram em 67
trocando CAGR ↔ MDD 1:1 dentro do rubric. Para quebrar o teto,
iter 008 mudou de **geometria**: pivot do A2 LRS-gated TQQQ-track para
**B1 HFEA clássico** — barbell alavancado clássico do Bogleheads
(UPRO + TMF, sem regime gate). Era o teste falsificável do livro:
HFEA promete CAGR ~22% com MDD ~30% pré-2022, mas 2022 destruiu
o regime (TMF -70% e UPRO -50% concorrentes). A pergunta era se a
tese sobrevive **considerando** 2022 (que está em ambos os datasets).

## O que aconteceu

Os 3 configs (50/50, 55/45, 60/40 em UPRO/TMF) **todos falharam o bar
de MDD** (≤ 55,17%). MDDs caíram em 67-72%. Mas o lado oposto do rubric
brilhou: HFEA gerou a **maior CAGR de todas as 8 iters** — score 29/30
no critério 1.

| config             | mean CAGR | mean MDD | Sharpe (lh, spy_real) |
|--------------------|----------:|---------:|----------------------:|
| b1_classic_5545    | 20,00%    | 67,13%   | 0,737 / 0,723         |
| b1_modern_6040     | 20,14%    | 72,70%   | 0,713 / 0,713         |
| **b1_balanced_5050** | **19,68%** | **67,48%** | **0,755 / 0,724** |

**KILL #24 disparou** exatamente como hypothesis.md previa: HFEA 5545
no spy_real bateu MDD 67,13% > 65% bar — 2022 quebra a tese. Direção
B1 HFEA clássico **fechada**.

## Achados não previstos

A **alegação canônica do Bogleheads de 55/45 ser risk-parity ótimo
foi falsificada pelo nosso synth**. A dose-response em peso UPRO no
intervalo [50, 60] é **monotônica negativa em Sharpe** — quanto MAIS
TMF (menos UPRO), MELHOR o Sharpe. A 50/50 venceu 5545 que venceu 6040
em ambos datasets. O rebalance instantâneo daily da nossa simulação
pode estar exagerando a auto-correlação UPRO-TMF, mas o resultado é
direcional: o HFEA "ótimo" estaria **abaixo de 50% UPRO**, não em 55%.

CAGR é praticamente flat entre os 3 configs (19,68% a 20,14%, range
0,46pp em 10pp de UPRO). MDD sobe forte só de 5545 → 6040 (+5,6pp).
A 165%+ de notional em equity alavancado, contribuição marginal de
mais UPRO está com retornos decrescentes enquanto contribuição
marginal de MDD acelera.

## Score 63 — abaixo do closest-to-winner

iter 006 a6_tqqq_split_kmlm30_tlt10 **mantém** closest-to-winner em 67.
Diff:

| critério | iter 006 | iter 008 | delta |
|---|---:|---:|---:|
| 1. CAGR | 25 (17,33%) | **29 (19,68%)** | **+4** |
| 2. MDD  | 7 (49,73%) | **0 (67,48%)** | **−7** |
| 3. Gates | 13 | 12 | −1 |
| **Total** | **67** | **63** | **−4** |

Trade-off azedo: HFEA paga 7pp de MDD para ganhar 4pp de CAGR num
critério já saturado (29/30). No rubric CAGR-anchored isso é loss.

## Próximo passo

**Iter 009 = B2 HFEA + KMLM crisis-alpha**. A literatura predisse que
B1 falharia em 2022 e B2 (HFEA com 15-20% KMLM como hedge) era a
resposta natural. A dose-response do KMLM já foi validada
empiricamente em iter 003-005 (SPY-track) e iter 006-007 (TQQQ-track):
+30% KMLM corta MDD ~15pp pagando <2pp de CAGR, com Sharpe monotônico
positivo até 40%. Aplicado ao backbone HFEA: 50% UPRO + 35% TMF +
15% KMLM deve trazer MDD para ~50-55% mantendo CAGR em 16-19%, score
esperado ~70-72.

Se B2 também capar em ~70 ou falhar MDD, iter 010 pivota para
**C1 vol-targeted** (geometria diferente — leverage dinâmico ao invés
de barbell estático).

## Mudança de infra

Adicionei route `TMFSIM` em
`studies/long_term_portfolio/run_iter.py::_resolve_tickers_to_returns`
para chamar `synths.tmf_synth_returns_from_cache()` (synth pré-existente:
3× TLTSIM − 1,5%/y daily-reset decay, validado por 3 testes anteriores).
Adicionei 1 novo teste de routing
(`test_resolve_tickers_routes_tmfsim_to_synth`) — 25/25 testes do
spy_beater passam.

## Citações

- `[leverage_for_the_long_run, ch.3-4, p.40-60]` Gayed LETF decay —
  validação empírica: HFEA 2022 MDD 67-73% espelha o backtest documentado
  Bogleheads 2022.
- `[risk_parity, ch.5, p.10]` Carlson capital-efficient stacking —
  alavancagem 165-180% sem hedge **não consegue** entregar MDD ≤ 55%
  no regime 2022.
- HFEA Bogleheads 2019 — claim de risk-parity 55/45 **falsificado**:
  Sharpe peak está em 50/50 ou abaixo no nosso synth. Claim é
  regime-specific 1986-2019 (rates-falling).
- `[advances_fin_ml, p.222-223]` DSR cumulative_n_trials=29, worst p
  4,91e-03 << 0,05.

## Onde estamos hoje

- 8 iters cumulativas (target 50). Closest-to-winner segue iter 006
  em 67.
- B1 HFEA classical CLOSED via KILL #24.
- B2 HFEA + KMLM = recomendação para iter 009.
- F1+SPLIT continua incumbente fallback caso o hunt termine em 50
  iters sem winner (mandate §1 MAINTENANCE MODE em todo caso).

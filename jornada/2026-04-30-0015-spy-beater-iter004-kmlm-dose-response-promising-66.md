# spy_beater_hunt iter 004 — A3 KMLM dose-response: a curva ainda não inflectou

**Data**: 2026-04-30 00h15
**Vertente**: studies/spy_beater_hunt (4ª iteração; meta 50)
**Tier**: PROMISING — score **66/100**, todos 3 bars PASS
**Selected**: `a4_lrs_split_kmlm30` (35% UPRO + 35% SSO + 30% KMLM ON, 100% IEF OFF, SMA 200, sem buffer)

## O que foi testado

Iter 003 mostrou que adicionar KMLM (managed-futures crisis-alpha)
sempre-ligado no sleeve ON do regime gate é bom: 0% → 20% KMLM derrubou
MDD de 51,60% para 41,87% (queda 9,73pp) e CAGR só caiu 1,24pp.
Faltava saber onde a curva inflecta. Iter 004 testou 25% e 30% KMLM
(mais um head-to-head TLT 20% vs KMLM 20% para fechar a comparação
de dose).

## Achados

A curva continua **monótona positiva ALL THE WAY de 0 a 30% KMLM**, e
é côncava (custo marginal de CAGR decai, benefício marginal de MDD
sustenta). Nenhuma dos 4 KILLs pre-comitadas disparou:

| KMLM % | mean CAGR | mean MDD | mean Sharpe |
|---:|---:|---:|---:|
| 0 | 16.23% | 51.60% | 0.657 |
| 10 | 15.47% | 46.65% | 0.673 |
| 20 | 14.99% | 41.87% | 0.706 |
| 25 | 14.70% | 39.37% | 0.724 |
| **30** | **14.39%** | **36.79%** | **0.744** |

`a4_kmlm30` é o novo closest-to-winner: bars 3/3 PASS, score 66 (subiu
2pts vs iter 003 KMLM 20% via +2 MDD pts e +1 Sharpe pts, com −1 CAGR
pts). TLT 20% empatou com KMLM 20% em Sharpe (marginal vantagem), mas
KMLM escala melhor no range 25-30%, então TLT continua subordinada
quando a comparação é estritamente paired.

## Implicações

- A família A3 KMLM dose-response é a **única direção promissora viva**
  (A1, A2-todas-variantes encerradas; A3-mixed-original dominado).
- Realistic ceiling pra essa família com mais 2-3 iters: score 70-75.
  WINNER (≥90) provavelmente exige uma alavanca estruturalmente
  diferente (TQQQ-track, vol-targeting, ou momentum overlay).
- DSR com n_trials=17 ainda passa folgado (worst p 5.56e-03 << 0.05).
  Headroom pra ~3-4 iters mais com 3 configs cada antes de a
  penalidade DSR começar a apertar.
- Próximo iter (005): probar inflection com KMLM 35% / 40% + um blend
  KMLM30+TLT10 que mistura as duas crisis-alphas. Se KMLM 35% for
  pior que KMLM 30%, achamos a inflection point e fechamos a direção.

`[leverage_for_the_long_run, ch.3-4, p.40-60]` Gayed gate 200d SMA
inalterado; `[risk_parity, ch.5, p.10]` Carlson capital-efficient
stacking validada empiricamente em 5 doses; `[advances_fin_ml,
p.222-223]` DSR com n_trials cumulativo.

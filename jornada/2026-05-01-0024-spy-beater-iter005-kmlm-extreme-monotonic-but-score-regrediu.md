# spy_beater_hunt iter 005 — KMLM 35-40% continua monótona positiva, mas o score regrediu

**Data**: 2026-05-01 00h24
**Vertente**: studies/spy_beater_hunt (5ª iteração; meta 50)
**Tier**: PROMISING — score **63/100**, todos 3 bars PASS
**Selected**: `a5_lrs_split_kmlm30_tlt10` (30% UPRO + 30% SSO + 30% KMLM + 10% TLT ON, 100% IEF OFF, SMA 200)

## O que foi testado

Iter 004 mostrou KMLM dose-response monótona positiva até 30%, sem
inflexão. Iter 005 atacou o problema em três frentes: KMLM 35%, KMLM 40%
(para encontrar onde a curva quebra) e um blend KMLM 30% + TLT 10%
(para testar se duration-on-top-of-trend dá ainda mais alívio de MDD).

## Achados

Nenhum dos 4 KILLs pre-comitados (#6, #16, #17, #18) disparou. A curva
KMLM continua **monótona positiva ALL THE WAY até 40%** em ambos
datasets — Sharpe sobe consistentemente:

| KMLM % | mean CAGR | mean MDD | mean Sharpe |
|---:|---:|---:|---:|
| 30 | 14.39% | 36.79% | 0.744 |
| 35 | 14.05% | 34.14% | 0.765 |
| 40 | 13.68% | 31.62% | 0.788 |

Mais: o blend `a5_kmlm30_tlt10` bateu o iter 004 winner em Sharpe nos
DOIS datasets (0.818/0.768 vs 0.765/0.722), confirmando que adicionar
TLT em cima do KMLM 30% ajuda mecanicamente.

**MAS o score regrediu de 66 → 63.** Apesar de melhor MDD (−4,22pp)
e melhor Sharpe (+0,049), o rubric tem o eixo CAGR ancorado em 5-20%
range valendo 30 pts vs MDD ancorado em 15-70% valendo 20 pts. O
trade-off de −0,82pp CAGR custou 2 pts e o ganho de 4,22pp MDD valeu
só 1 pt. Mais 1 pt perdido em gates (lh_56y caiu 6/7 → 5/7) e 1 pt
em robustness (rolling 5y pass-rate caiu 83,3% → 66,7% — KMLM-heavy
fica pra trás do SPY em janelas curtas durante bull longo).

## Implicações

- iter 004 `a4_kmlm30` permanece o closest-to-winner (66). Não foi
  deslocado.
- A direção KMLM dose-response **está estruturalmente bloqueada
  dentro do rubric**: cada +5% KMLM custa ~0,7 pts CAGR e ganha ~1 pt
  MDD. Empate aproximado. Mais doses não levantam o score.
- O blend TLT-on-top-of-KMLM30 é uma **nova direção promissora** —
  poderia testar KMLM30+TLT15 ou KMLM30+TLT20 num iter 006 leve.
- **Recomendação principal**: pivotar pra alavancas estruturalmente
  diferentes — B1 HFEA classical (55% UPRO + 45% TMF) ou A2 TQQQ-track
  com 200d SMA gate. Sem isso, atingir score ≥ 90 (WINNER) parece
  improvável com KMLM-dose sozinho.
- DSR com n_trials=20 ainda folgado (worst p 2.93e-03 << 0.05).
  Headroom pra ~3-4 iters mais a 3 configs cada antes da penalidade
  apertar.

`[leverage_for_the_long_run, ch.3-4, p.40-60]` Gayed gate 200d SMA
inalterado; `[risk_parity, ch.5, p.10]` Carlson capital-efficient
stacking validada empiricamente em 7 doses (0% → 40% KMLM, todos
monótonos positivos em Sharpe); `[advances_fin_ml, p.222-223]` DSR
com n_trials=20 cumulativo.

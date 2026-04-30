# spy_beater_hunt iter 019 — 3-way meta-ensemble quebra teto de novo (71/100)

Continuando o spy_beater_hunt: iter 019 testou a sugestão deixada pelo
iter 018 (que tinha quebrado o teto histórico de 67 pontos do hunt
chegando a 70 com uma blend 50/50 de duas estratégias gated).

## O que foi feito

Rodamos 6 configs (em vez de 3) — primeiro porque o iter 018 tinha um
warning de instabilidade estatística (PBO calculado com N=3 configs é
ruim; com N=6 fica decente), segundo porque a recomendação explícita
era varrer pesos e testar 3-way blends.

Configs:

1. **Reproducibility** — repetir o vencedor do iter 018 (50/50 A2 + G2
   IEF) para conferir se o 70 era N=3 artifact ou resultado real.
2. **2-way weight sweep** — testar 55/45 e 45/55 ao redor do 50/50 ótimo.
3. **3-way blends** — adicionar o F1 stack (always-on multi-asset
   diversifier do iter 015) em três pesos: 40/30/30, 50/25/25 e 33/33/34.

## Resultado

**Score 71/100 PROMISING — sobe +1 pt vs iter 018.** O vencedor é o
3-way equal-weight 33/33/34 (A2 33% + G2 IEF 33% + F1 stack 34%):

- CAGR mean 15.04% (passa o bar de 11.21%)
- MDD mean 28.50% — segundo-melhor entre estratégias que passam o CAGR
  bar no hunt inteiro (só o G2 BLEND com 26.76% era melhor, e ele
  scoreou 63 < 71)
- **Sharpe mean 1.025 — primeiro Sharpe > 1.0 EVER entre os
  CAGR-passers do hunt** (G1 IEF tinha 1.080 mas falhava o CAGR bar)
- Gates 6/7 + 6/7 (margem de 1 nas duas datasets)
- **6/6 configs passam todos os 3 bars — primeiro sweep 100% bar-pass
  do hunt em 19 iters / 62 trials**

## O que aprendemos

1. **A reprodutibilidade do iter 018 confirmou-se exatamente** —
   mesmas métricas per-dataset. Isso resolve uma dúvida estrutural:
   o PBO 0.603 do spy_real no iter 018 (que estourava o gate G1) não
   era overfitting genuíno, era artefato da grade N=3. Com N=6 caiu
   pra 0.0040.

2. **3-way bate 2-way** — KILL #65 disparou. Mas com nuance: o iter
   018 tinha rejeitado o "F1 stack always-on adicionado a uma gated
   strategy" (60/40 mixed-gate score ~64 < 70 same-gate). Aqui no iter
   019 a estrutura 3-way (33% A2 + 33% G2 IEF + 34% F1 stack) bate o
   2-way 50/50. **Princípio refinado**: F1 stack só agrega valor
   quando há DOIS constituintes gated; um só não chega para a
   bear-avoidance, dois compensam o always-on diluir o gate.

3. **Triple decorrelation entrega ganho super-linear**:
   - MDD: linear 36.76% → observado 28.50% (−8.26pp ganho)
   - Sharpe: linear 0.931 → observado 1.025 (+10.1% boost)
   - CAGR: linear 14.43% → observado 15.04% (+0.61pp ganho)

4. **Path to STRONG (≥75)** — meta-axis cresceu de 67-cap pra 70 pra
   71 em duas iters consecutivas. Continua sendo o único axis no hunt
   com trajetória empírica positiva monotônica. iter 020 (recomendado)
   testaria 4-way blends + outros pares 3-way (e.g., A2 + G1 IEF +
   F1 stack para usar o melhor-Sharpe G1 IEF que falha CAGR).

## Status

- Hunt continua **REOPENED at meta-ensemble axis** (KILL #59 do iter
  018 confirmado pela reprodutibilidade; KILL #65 do iter 019
  consolida a tendência).
- Tier ainda PROMISING (71 < 90 WINNER threshold).
- Mandate §1 (100% Plano C) **inalterado** — score precisa chegar a
  90 pra mexer. Iter 019 é research, não deploy.
- Cumulative n_trials = 62, DSR worst p = 1.55e-04 (margem forte).
- 768 testes baseline preservados (sem novo módulo — reaproveitamos a
  spec type "blend" que o iter 018 introduziu).

## Citação principal

`[advances_fin_ml, ch.16, p.241-256]` portfolio construction over
multiple alpha streams, agora estendido empiricamente pra 3-way no
spy_beater rubric. `[risk_parity, ch.5, p.10]` Carlson capital-
efficient stacking generalizado pra strategy-level. `[advances_fin_ml,
p.208-211]` PBO N=6 stability resolveu o warning N=3 do iter 018.

## O que vem a seguir

Iter 020 sugerido (não execute na mesma sessão por convenção do loop):
- 6 configs com 4-way blends + pares 3-way alternativos
- Cumulative n_trials → 68
- KILL pré-comprometido: se iter-020 ≤ 71 → ceiling do meta-axis em
  71 com diminishing returns; se ≥ 75 → STRONG tier alcançável.

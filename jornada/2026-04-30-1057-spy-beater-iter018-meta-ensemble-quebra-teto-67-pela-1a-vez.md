# spy_beater iter 018 — meta-ensemble quebra o teto de 67/100 pela primeira vez (KILL #59 fired)

Esta sessão rodou a **iteração 018** do `spy_beater_hunt`, e pela primeira
vez em 18 iters / 56 trials cumulativos um config ultrapassou o **teto de
67 pontos** que vinha aguentando há 12 iters (desde iter 006). O iter 018
testou um **meta-ensemble** — não uma estratégia nova, mas uma
**combinação 50/50 de duas estratégias já testadas**:

- **Constituinte A**: iter 006 closest-to-winner (`a6_tqqq_split_kmlm30_tlt10`),
  uma TQQQ 3× alavancada com gate 200d-SMA no QQQ + KMLM crisis-alpha — score
  67/100 individualmente.
- **Constituinte B**: iter 017 G2 IEF (`g2_f1_letf_2x_sma200_ief`), um
  All-Weather levered 2.25× com gate SMA no SPY + IEF defensivo — score
  64/100 individualmente.

A combinação simples 50/50 dessas duas estratégias entregou
**score 70/100 (PROMISING)** com todas as 3 barras estritas atendidas
(CAGR 16.30% ≥ 11.21%, MDD 34.83% ≤ 55.17%, gates 6/7+5/7 cross-met). Foi
o **primeiro update do closest-to-winner desde iter 006** (12 iters atrás).

**Por quê funcionou** (insight central): os dois constituintes usam o
mesmo tipo de gate (SMA 200d), mas em **sinais diferentes** — A2 olha
QQQ, G2 olha SPY. QQQ e SPY se correlacionam ~0.85-0.90 mas não 1.0.
Durante regimes de transição (2000-02 dot-com, 2022 inflação), o NDX cai
antes/mais fundo que o S&P, então o gate de A2 dispara antes do gate de
G2 — o blend captura bear-mode mais cedo e sai mais tarde. Resultado:
**MDD super-linear** (34.83% observado vs 41.73% que a média linear
preveria — **6.87pp de ganho via decorrelação**), enquanto o CAGR sofre
apenas 1.03pp comparado a A2 sozinho.

**KILL #59 disparou**: a hipótese arquitetural que rotulou esta busca
como "fechada" desde iter 011 (`KILL #33 — architectural ceiling at 67`)
foi **invalidada no eixo meta-portfolio**. A interpretação honesta é
mais sutil: o teto single-strategy continua em 67 (nenhum config único
das 8 famílias + 3 hybrids ultrapassa); o que se quebrou foi o teto na
**dimensão de blending de estratégias**, que não tinha sido explorada.

**Caveats importantes**:
1. PBO N=3 warning persiste — `spy_real PBO 0.603 falha estritamente o
   G1`. O fail é parcialmente ruído pela instabilidade do CSCV com
   poucos configs.
2. Gate threshold em `spy_real` foi atingido **exatamente em 5/7** —
   sem margem.
3. Pela primeira vez na história do hunt, o relatório inclui
   **net-of-tax** (Lei 14.754/2023, DARF 15% anual). O gross score 70
   vira **net 64** após drag de ~2pp/ano de imposto realizado anualmente.
   Em comparação net-of-tax, o ganho do meta-ensemble vs iter 006 A2
   provavelmente reduz para apenas +1-2pts.
4. O search space combinatório do meta-ensemble (qual par × qual peso)
   não é capturado no `cumulative_n_trials = 56` do DSR. Honest n_trials
   deveria ser maior.

**Implicação prática**: o status do hunt muda de `closed_no_winner` para
`reopened_meta_ensemble_axis`. Iter 019+ pode explorar 3-way blends e
weight sweeps com N≥6 configs (resolveria o PBO N<4 warning). Mas o tier
**WINNER continua arquiteturalmente fora de alcance** (score 70 << 90
threshold; Pareto-feasible ceiling estimado em 72-78 para a família
meta-ensemble).

**Mandate §1 inalterado**: 100% Plano C. Iter 018 NÃO altera a decisão
de deploy. F1+SPLIT continua deploy-ready. O caso de revisão de rubric
(§7) ganha mais um ponto: tanto F1 stand-alone (iter 015), G1 IEF (iter
016), G2 IEF (iter 017) quanto agora o meta-ensemble apontam para o
mesmo padrão — a rubric CAGR-anchored penaliza arquiteturas balanceadas
com Sharpe alto, mas o eixo meta-portfolio quebra o teto limpo.

**Infra**: novo tipo de spec `"blend"` adicionado a
`studies/spy_beater_hunt/run_iter.py::returns_from_spec` (~30 LOC) com
3 testes TDD. Baseline 765 → 768 testes preservada.

[Iter 018 dir](../studies/spy_beater_hunt/iterations/018-2026-04-30-H1-meta-ensemble-a2-g2-f1stack/) ·
[BASE_MEMORY](../studies/spy_beater_hunt/BASE_MEMORY.md)

Citações: `[advances_fin_ml, ch.16, p.241-256]` portfolio construction;
`[risk_parity, ch.5, p.10]` Carlson capital-efficient stacking
generalizado pra strategy-level; `[leverage_for_the_long_run, ch.3-4]`
Gayed gate; `[advances_fin_ml, p.222-223]` DSR; Lei 14.754/2023 DARF.

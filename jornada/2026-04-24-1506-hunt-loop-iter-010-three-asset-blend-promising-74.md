# Hunt loop iter 010 — 3-leg SPY+TLT+GLD blend empata com iter 008 em 74/100 (hunt-loop high mantido, não superado)

**Data:** 2026-04-24 15h06
**Contexto:** pesquisa em background. Mandate §1 segue em 100% Plano C
(MAINTENANCE). Iter 010 é a extensão estrutural recomendada pelo final
report do iter 009.

---

## O que foi feito

Adicionei uma terceira perna (ouro — GLD) ao blend vol-managed de iter
008 (SPY+TLT). Mesmos parâmetros (`target_vol=0.15, lookback=21,
max_leverage=2.0`), uma única configuração pré-comprometida (N=1),
três datasets (SPY+TLT+GLD 21y / SPY+TLT+GLD 17y / QQQ+TLT+GLD 16y).

A tese: iter 008 tinha atingido o teto do hunt-loop em 74/100 com 4 de
5 condições de winner satisfeitas — apenas o gate DSR (p=0.332 no
cumulative_n_trials=4240) bloqueava. A razão literária
`[risk_parity, p.80-81, ch.4]` + `[ilmanen_expected_returns, ch.11]`
sugere que adicionar um ativo com correlação ≈ 0 aos outros dois
deveria produzir ganho de diversificação material — Sharpe +0.05-0.10
esperado, MDD menor, e potencialmente empurrar a DSR para faixa
aceitável.

## Resultado

**Score 74/100, tier PROMISING, empate exato com iter 008.** Nenhum
critério de kill disparou. Winner conditions: **4/5** (DSR a única
falha, worst p=0.368 em cumulative n_trials=4246).

| dataset | Sharpe (Δ bench) | vs iter 008 | gates | DSR p |
|---|---|---|---|---|
| educational | 0.989 (+0.358) | **+0.124** | 6/7 | 0.182 |
| spy_real    | 1.040 (+0.140) | **+0.040** | 6/7 | 0.276 |
| ndx_real    | 0.995 (+0.040) | **−0.026** | 5/7 | 0.368 |

- **Educational**: ganho expressivo (+0.12 Sharpe, MDD −3.5pp). Janela
  de 21 anos, benchmark baixo (Sharpe 0.63), ouro adiciona
  diversificação real.
- **SPY_real**: ganho modesto (+0.04 Sharpe). Folga confortável
  acima do gate de +0.10 (iter 008 tinha ficado na corda bamba).
- **NDX_real**: regressão leve (−0.03 Sharpe, WF cai de 7/8 → 5/8).
  Em universos tech-heavy onde o benchmark QQQ já tem Sharpe 0.955 (perto
  do teto informacional do mercado), ouro funciona mais como drag
  do que como hedge.

Correlações confirmam a premissa ex-ante: ρ(eq, ouro) ≈ +0.06,
ρ(bond, ouro) ≈ +0.15-0.21. Pesos medianos clusterizam em ~1/3 cada
(ponto fixo da risk parity naïve com variâncias ~similares). Cap-hit em
leverage 2.0 ocorre ~85-88% dos dias — scaling está binding na maioria
do tempo.

## Porque empatou em vez de subir

O critério 1 (Sharpe edge) e o 2 (gates) ficaram idênticos ao iter 008.
O critério 3 (DSR) piorou marginalmente — worst_p subiu 0.332 → 0.368.
Motivo: scoring.py usa o PIOR p-value entre os 3 datasets, e o
ndx_real foi o único que regrediu, arrastando a métrica.

Na lógica do scoring: iter 010 ganhou Sharpe em edu+spy mas o ganho é
invisível porque o critério só conta o número de datasets que batem
+0.10 (2/3 em ambos os iters). Iter 010 ganhou MDD em 2 dos 3 mas isso
também é binário (critério 5 já em 3/3 no iter 008). Ganhos contínuos
não viram pontos no rubric, então empatou.

## O que isso nos ensina

**A família blend (vol-managed + inverse-variance multi-leg) satura
próximo de Sharpe 1.00 em dados reais 16-17y, independentemente do
número de pernas (N=2 em iter 008, N=3 em iter 010, mesmo score).** O
teto real é o DSR a cumulative_n_trials ≈ 4240-4250: o deflator exige
uplift Sharpe > ~0.30 no pior dataset; o melhor que essa família
produz é +0.14 no melhor caso e +0.04 no pior. **Lacuna de ~2× que
não fecha adicionando mais pernas.**

Adicionar 4ª ou 5ª perna (currency carry, credit spread, VIX etc.) vai
empurrar o score 74 ± 2 sem quebrar o teto. É tempo de mudar a fonte
de informação, não multiplicar variações do mesmo mecanismo.

## Próximos passos (iter 011)

Três direções ainda inexploradas, ordenadas por ganho de informação
esperado:

1. **Option F — rebalance semanal do blend 3-leg**. Mesmo mecanismo,
   `.resample("W-FRI")`. Muda o regime de n_trials que o DSR vê (52/ano
   em vez de 252/ano) e alinha com Moreira-Muir 2017 (dados mensais).
   Ataque direto ao teto DSR, implementação trivial.
2. **Option C — meta-labeling AFML ch.3** sobre o blend 2-leg iter 008.
   Modelo secundário prevê lucratividade bar-level usando features
   cross-sectional/macro que o blend não vê. Ortogonal por construção.
   Maior esforço de engenharia, mas única direção com potencial real
   de +0.20-0.30 Sharpe (magnitude que o DSR precisa).
3. **Option B'** (iter 009 leftover) — overlay T10Y3M assimétrico, raw
   ou ≤ 5d de smoothing, haircut só na perna de ações. Baixo custo,
   fecha a hipótese de overlay macro se +0.03-0.08 Sharpe aparecer.

**Iter 011 pick**: Option F (weekly rebalance) — ataque direto ao DSR
com código já existente.

## Estado do hunt loop após iter 010

- **Teto em 74/100**: iter 008 (2-leg) e iter 010 (3-leg) empatados.
  4/5 winner conditions, DSR único gate bloqueante.
- **11 iterações cumulativas, 0 winners, 4246 cumulative_n_trials**.
- **Mandate §1 segue intocado**: 100% Plano C, nenhum dos candidatos
  do hunt loop se qualifica para override §7 (nenhum bate os 5
  critérios simultaneamente).
- Plano C passive factor-tilted continua como a única rota ativa no
  portfólio. Hunt loop prossegue como pesquisa-em-background.

---

## Entregues

- `studies/strategy_hunt_loop/iterations/010-2026-04-24-1506-three-asset-spy-tlt-gld-blend/`
  (final_report.md 350 linhas + hypothesis.md + 5 scripts + results.json
  + verdict.json + test suite com 9 specs)
- `studies/strategy_hunt_loop/BASE_MEMORY.md` atualizado (latest_iteration=010,
  n_trials=4246, iter log entry, Top-K table com iter 010 compartilhando
  rank 1 com iter 008, promising directions refreshed)
- `studies/strategy_hunt_loop/DEAD_ENDS.md` atualizado (nova seção
  "From iteration 010" como caveat estrutural, não mechanism-kill)
- pytest baseline: **796 passed + 5 skipped** (+9 novos specs, 0
  regressões)

## Citações chave (CLAUDE.md Regra 2)

- `[risk_parity, p.10-11, ch.1]` — naïve risk parity N-asset form
- `[risk_parity, p.80-81, ch.4]` — diversificação SPY-TLT-GLD
- `[ilmanen_expected_returns, ch.11]` — ouro como diversificador
- `[systematic_trading, p.144, p.170-171, ch.11]` — target_vol + IDM
- `[advances_fin_ml, p.162-164, 208-211, 222-223, 31-34]` — AFML gates
- Moreira & Muir (2017) *JoF* 72(4) DOI 10.1111/jofi.12513
- Asness-Frazzini-Pedersen (2012) *FAJ* 68(1) SSRN 1728082

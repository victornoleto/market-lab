# Hunt loop iter 012: overlay assimétrico T10Y3M (5d EMA, equity-only) dá 58/100 MARGINAL, Kill #1 + #3 + #4 TRIGGERED — família T10Y3M-overlay FECHADA

**Contexto (mandate §1 — MAINTENANCE 100% Plano C):** pesquisa em
background rodando no strategy hunt loop. Toda alocação real segue
consolidada em Plano C passive factor-tilted; strategy A/B/D
continuam DORMANT. O loop produz CANDIDATOS pra revisão futura,
nunca posições live.

## O que foi testado

**Option B'** (conforme recomendação explícita do BASE_MEMORY no final
da iter 011): adicionar um **haircut assimétrico ao blend de iter 008**
(SPY+TLT vol-managed daily) — quando o T10Y3M (spread 10Y−3M dos
Treasuries) inverte (< 0), reduzir APENAS a perna de SPY pela metade,
mantendo a perna de TLT em peso cheio. Com smoothing leve (EMA 5 dias,
não 21 como iter 009). Single config pre-commitada:
`vt15_L21_cap20 × ts_inv5_h50_eq`.

A ideia estrutural vinha de duas correções do iter 009 (que havia
fechado como dead-end em 64/100):

1. **Preservar o lead-time de 6-18 meses do T10Y3M** (Estrella-Mishkin
   1998). Em iter 009 o EMA de 21 dias destruiu esse lead — o sinal
   virava concomitante ao vol-regime detectado pelo variance-scaling.
   Com 5 dias, o número de zero-crossings cai de 958 (raw, "flickery")
   para 44 ao longo de 44 anos (≈1 episódio/ano — alinha com ciclos
   econômicos reais).
2. **Respeitar o flight-to-quality bond-leg**. Em recessões típicas,
   TLT sobe enquanto SPY cai (ρ ≈ −0.30). Iter 009 cortava AMBAS as
   pernas pela metade, abrindo mão exatamente do bônus que faz o
   sinal valer a pena. Equity-only preserva isso.

## O resultado honesto

🥉 **MARGINAL — 58/100. 0/5 condições de winner, regressão vs iter
008 (4/5).** Score cai 16 pontos vs iter 008 baseline e 6 pontos vs
iter 009 (o próprio dead-end que B' pretendia melhorar).

| dataset | Sharpe | Δ vs bench | Δ vs iter 008 | gates | DSR p | overlap_b20 |
|---|---|---|---|---|---|---|
| educational | 0.824 | +0.162 | **−0.041** | 6/7 | 0.362 | **100%** |
| spy_real | 0.965 | +0.065 (abaixo do +0.10 gate) | **−0.035** | 6/7 | 0.385 | **100%** |
| ndx_real | 0.968 | +0.013 (abaixo do +0.10 gate) | **−0.053** | 6/7 | 0.410 | 40.5% |

**Kill criteria triggered (pré-commitados na hypothesis.md)**:

- **Kill #1** — Sharpe REGRIDE em ambos os slots reais (spy −0.035 AND
  ndx −0.053 vs iter 008). O princípio "asymmetric equity-only haircut
  resgata o overlay de iter 009" é empiricamente falsificado.
- **Kill #3** — score 58 < 70 (threshold de continuidade do mecanismo).
- **Kill #4** — **gate-fire/bottom-20%-scale overlap de 100% em 2/3
  datasets** (edu + spy). Exatamente o mesmo diagnóstico do iter 009.
  O EMA de 5 dias NÃO resolveu a redundância com variance-scaling.

## O que isso fecha estruturalmente

Iter 009 (symmetric, 21d EMA) + iter 012 (asymmetric, 5d EMA) juntos
**fecham a matriz 2×2 combinatorial {smoothing × asymmetry}** do
T10Y3M-overlay em blend vol-managed. Os dois cantos testados mostram
100% de overlap com o bottom-20% do blend scale em datasets baseados
em SPY. Os dois cantos não-testados (heavy+asymmetric e
light+symmetric) não têm razão teórica pra serem melhores — o primeiro
é estritamente pior que light+asymmetric, o segundo é estruturalmente
o mesmo que 009.

**A redundância é cointegração estrutural, não escolha de parâmetro.**
T10Y3M e realized-vol de SPY co-movem na escala de tempo do ciclo
econômico. Quando o T10Y3M fica invertido tempo suficiente pra passar
o filtro binário (em qualquer smoothing), a vol realizada já
acelerou o bastante pra variance-scaling estar de-alavancando.
Nenhum parâmetro quebra isso.

**Subproduto**: a preservação assimétrica da perna de TLT foi **a
direção errada** pro regime pós-2008. Em 2022 a correlação SPY-TLT
virou positiva (tanto ações quanto bonds caíram no choque de juros);
manter TLT em peso cheio enquanto cortava SPY significou carregar uma
posição perdedora em bonds no pior momento.

## Próximos passos (iter 013 — proibido T10Y3M e derivados)

O final_report e o DEAD_ENDS.md do iter 012 declaram a **família
T10Y3M-overlay CLOSED** pra esse mecanismo. Qualquer variante de
yield-curve-slope (T10Y2M, T5Y3M, SOFR-IOER...) também cai fora porque
cointegram no mesmo timescale.

Direções que restam estruturalmente válidas:

1. **Option C — Meta-labeling (AFML ch.3 + ch.5)** — PICK PRIMÁRIO.
   Modelo ML secundário prevê lucratividade bar-a-bar do blend de
   iter 008 usando features cross-sectional que o blend não vê
   (momentum cross-asset, breadth, options skew, macro state regime).
   Ortogonal por construção, ataca o teto DSR via o lado do Sharpe
   observado. Custo de engenharia ~2-3h.
2. **Option E — EBP overlay (Gilchrist-Zakrajšek 2012)** — sinal de
   credit-spread, distinto do rates-term-structure. Episódios
   históricos diferentes (1998 LTCM, 2008 GFC, 2020 COVID). Precisa
   validar empiricamente que EBP-SPY-vol correlation < T10Y3M's
   antes de gastar n_trials.
3. **Option G — Return-stacked ETF rotation (NTSX/NTSI/NTSE)** — track
   paralelo; universo + mecanismo novos.

## Estado do hunt loop pós iter 012

Matriz de tetos mapeados:

- **Daily-cadence ceiling do blend family**: 74/100 (iter 008 = iter
  010 tied, não quebrado).
- **Timeframe-change quadrant**: FECHADO (iter 011 weekly = 52).
- **Momentum-overlay quadrant**: FECHADO (iter 007 = 50).
- **T10Y3M-overlay quadrant**: FECHADO (iter 009 = 64 + iter 012 = 58).

Cumulative n_trials: 4252. Próximo ataque produtivo precisa de
**informação genuinamente ortogonal**, não de mais um sinal macro
correlacionado no mesmo universo.

## Artefatos

- `studies/strategy_hunt_loop/iterations/012-2026-04-24-1556-asymmetric-term-spread-overlay/`
  — hypothesis.md + final_report.md + verdict.json + results.json +
  asymmetric_term_spread_overlay.py + overlay_numpy_reference.py +
  run_backtests.py + compute_gates_and_score.py
- `tests/test_asymmetric_term_spread_overlay.py` — 9 TDD specs all
  green (gate semantics, asymmetric application, no-lookahead, EMA
  ordering, numpy parity).
- `studies/strategy_hunt_loop/DEAD_ENDS.md` — nova seção "From
  iteration 012" + bullet atualizado em "Structural dead-end
  categories".
- `studies/strategy_hunt_loop/BASE_MEMORY.md` — entrada iter 012 em
  6-field completo; auto-prune aplicado (17737 bytes, dentro do
  limite de 18000).

## Citações

- `[regime_change, p.5-6, ch.2]` — princípio de regime-change; T10Y3M
  testado como proxy canônico e **falsificado como ortogonal** nesse
  mecanismo específico.
- `[risk_parity, p.10-11, ch.1, p.80-81, ch.4]` — naïve risk parity +
  racional de correlação negativa SPY-TLT pra asymmetry (que não
  resolve o overlay).
- `[systematic_trading, p.144, ch.9]` — tier-2 half-exposure haircut.
- `[advances_fin_ml, p.162-164, 208-211, 222-223, 31-34]` — lag sem
  lookahead, PBO, DSR deflator, cross-lib parity.
- Moreira & Muir (2017), *JoF* 72(4), DOI
  [10.1111/jofi.12513](https://doi.org/10.1111/jofi.12513) — base
  variance-scaling.
- Estrella & Mishkin (1998), *REStat* 80(1), DOI
  [10.1162/003465398557320](https://doi.org/10.1162/003465398557320)
  — T10Y3M como recession leading indicator.

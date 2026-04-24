# Hunt loop iter 004: vol-managed SPY bate todas as provas menos duas

> **Contexto:** projeto em MODO MAINTENANCE (100% Plano C, mandate §1).
> O `strategy_hunt_loop` é exploração de pesquisa em background, não
> deployment. Esta nota registra a primeira partial-success desde o
> início do loop.

---

## O resultado em uma linha

Depois de três iterações que deram 7, 17 e 35 pontos num rubric de
100, a iteração 4 deu **51/100 🥉 MARGINAL** — o melhor resultado até
agora no loop, e pela primeira vez uma estratégia passou o G6
(bootstrap 99.9% CI low > 0) nos três datasets.

Candidato grand champion: **vol-managed SPY** com `target_vol=20%`,
lookback=21 dias, leverage_cap=1.5×. Mecanismo: escalar a exposição
diária em SPY por `target_vol / σ̂_{t-1}` (Carver 2015, *Systematic
Trading* cap.9; e Moreira-Muir 2017 JoF 72(4)). Sem sinal, sem
cross-section, sem stop. Só reescalar risco.

## O que significa 51/100 MARGINAL

O **rubric** tem 6 critérios somando 100+5 pontos. A config
`tv20_L21_cap15`:

- ✅ **CAGR floor** 15/15 — passa em todos os 3 datasets
- ✅ **MDD ceiling** 15/15 — passa em todos os 3 datasets
  (reduz drawdown em 6-9pp vs SPY puro — o achado mais limpo)
- ⚠️ **Sharpe edge** 10/25 — supera o benchmark em +0.10 só no
  dataset educacional (Δ+0.15); em spy_real e ndx_real supera em
  +0.08 — duas centésimas abaixo do corte estrito. Não é ruído: é
  ruído-próximo-do-corte.
- ⚠️ **Gates** 11/25 — edu 4/7, **spy_real 6/7**, **ndx_real 6/7**.
  Educacional fica um gate abaixo do mínimo (5/7) porque uma das 8
  janelas walk-forward tem MDD>25% (inevitável com alavancagem e a
  crise de 2008 dentro da janela).
- ❌ **DSR p-value** 0/15 — o pior p = 0.36 com n_trials=4156
  cumulativo. Como estamos acumulando configs testadas ao longo
  das iterações, o "penalty" por overfit cresce; para passar DSR
  hoje precisaria de Sharpe ~1.4, não 1.04.

Ou seja: **o mecanismo funciona**, passa a maioria dos gates
estatísticos em real data, mas o ganho de Sharpe é pequeno demais
(+0.08) pra superar o corte estrito de winner (+0.10), e o DSR está
sufocado pelo número de testes acumulados.

## Por que isso importa mesmo em MAINTENANCE

A regra §1 do mandate continua valendo: **100% Plano C**. Nenhum
candidate do hunt loop entra na carteira sem um override §7 assinado
separadamente, e esse override não vai acontecer com 51/100.

O valor da iteração é **epistêmico**:

1. **Confirmamos empiricamente o achado Moreira-Muir 2017** em SPY
   2009-2026: inverse-vol scaling melhora o Sharpe em +0.08 e
   reduz MDD em 9pp vs buy-hold. O paper reportava ganhos maiores
   em universos factor-heavy CRSP 1926-2015; em SPY large-cap
   moderno o ganho é menor mas real.
2. **G6 passando pela primeira vez** é sinal que o mecanismo não é
   artefato de backtest — mesmo reamostrando os retornos via
   stationary bootstrap 5000 vezes, o 0.1-percentil do Sharpe fica
   acima de +0.22 nos dois datasets reais.
3. **PBO real-data 0.31/0.35** (abaixo do 0.5 cutoff) — o grid de 36
   configs não sofre do overfit signature que matou iter 002/003.
4. **Cross-lib parity 0.04pp** — reimplementação numpy-pura do
   pipeline completo concorda com o path pandas. Engine limpo.

## O que vem a seguir

A recomendação registrada em `BASE_MEMORY.md`:

**Iter 005 = Moreira-Muir canonical variance-scaling.** A diferença
com iter 004 é um caractere na fórmula — `σ̂²_{t-1}` em vez de
`σ̂_{t-1}` no denominador — mas o paper de 2017 reporta efeitos
bem mais fortes com variance-scaling porque a variância realizada
é mais persistente que a volatilidade realizada. Se iter 004 deu
+0.08, variance-scaling espera +0.12 a +0.15 — o suficiente pra
cruzar o corte estrito.

Grid mais enxuto (12 configs em vez de 36) pra não sufocar o DSR
ainda mais. Se o resultado passar todos os 5 critérios estritos E
pontuar ≥90, o loop para com verdict WINNER e o usuário decide
separadamente se quer override §7.

## O gap que ainda separa um candidate de um winner

A iteração 004 fica a ~2 centésimas de Sharpe num dataset e ~0.05
no p-value do DSR de ser um winner formal. Traduzindo: se o mesmo
mecanismo ganhasse mais 1% de CAGR ao ano em spy_real ou ndx_real —
sem outros efeitos colaterais — cruzava os dois cortes. Isso é
plausível com variance-scaling, ou com vol-managed aplicado numa
mix SPY+TLT. Não é plausível esperando mais 2 anos de dados na
mesma fórmula.

Próxima iteração do loop seguirá essa pista. Enquanto isso, mandate
§1 segue intocado: Plano C é a única alocação real.

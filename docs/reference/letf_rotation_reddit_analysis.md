# LETF Rotation — Reddit /r/LETFs post summary (user's prior study)

> ⚠️ **Disclaimer (adicionado 2026-04-16 21:50 pelo próprio usuário):
> este post é trial-and-error, NÃO ciência.** A única âncora científica
> válida pra Strategy B é `books/summaries/leverage_for_the_long_run.md`
> (Gayed). Este documento existe como **exemplo ilustrativo de um tipo
> de estratégia simples e eficaz** (regime-rotation com LETF) —
> Strategy B não precisa replicar esses params. O Lead B1 deve projetar
> uma LETF rotation ancorada em Gayed, submeter ao framework de gates
> do ai-trade, e o resultado *pode ou não* parecer com esta config.
> Os params abaixo valem como um de vários seed points, não como
> target a reproduzir.

**Fonte:** Post do usuário `u/noletovictor` em `/r/LETFs`, há ~5 meses
(publicado ~2025-11).
**URL:** https://www.reddit.com/r/LETFs/comments/1p4t114/the_best_optimization_for_leveraged_rotation/
**Arquivo local (print):** `docs/reference/letf_rotation_reddit_post.pdf`
(24 páginas, 4.6 MB, Shift+P do navegador em 2026-04-16).
**Resposta testfol.io da config escolhida:**
`docs/reference/testfolio_letf_spy_ema_125_response.json` (12 MB,
cashflow + equity curve + stats da config chosen de 1968-01-01 a
2026-04-16).

---

## TL;DR

O usuário rodou **220.000+ backtests** (960 combos × 230 janelas) em
testfol.io via script Python chamando a cURL API, procurando a melhor
combinação para uma Leveraged Rotation Strategy (LRS) sobre SPY.

- **Universo de parâmetros:** MA_type (EMA/SMA) × MA_period (várias) ×
  tolerância_% (0%, 3%, 5%) × leverage (1x, 2x, 3x) × alocação_gold
  (0%, 25%, 50%, 75%, 100%).
- **Janelas temporais:** 5y, 10y, 15y, 20y, 25y, 30y — rolling 1970
  até 2025, totalizando ~230 pontos de backtest por combo.
- **Scoring:** Calmar (peso 0.5) + Sortino (0.35) + Sharpe (0.15),
  média ponderada; janelas maiores (30y) pesam mais que janelas menores
  (5y).

## Top 10 pelo scoring composto

| # | Config | Score |
|---|--------|-------|
| 1 | **SPY EMA 125 5% \| Lev 2x \| Gold 75%** | 0.99999999... |
| 2 | SPY EMA 125 5% \| Lev 2x \| Gold 50% | 0.99999... |
| 3 | SPY EMA 125 5% \| Lev 2x \| Gold 100% | 0.99999... |
| 4 | SPY EMA 125 5% \| Lev 2x \| Gold 25% | 0.99999... |
| 5 | SPY SMA 150 3% \| Lev 2x \| Gold 100% | 0.99999... |
| 6 | SPY SMA 150 3% \| Lev 2x \| Gold 75% | 0.99999... |
| 7 | SPY EMA 125 5% \| Lev 3x \| Gold 75% | 0.99999... |
| 8 | SPY EMA 125 5% \| Lev 3x \| Gold 50% | 0.99999... |
| 9 | **SPY EMA 125 5% \| Lev 2x \| Gold 0%** (rank 9) | 0.99999... |
| 10 | SPY EMA 125 5% \| Lev 3x \| Gold 100% | 0.99999... |

**Observações do usuário:**
- EMA dominou SMA em quase todos os top slots.
- Tolerância entre 3% e 5% é sweet spot (0% gera ruído excessivo).
- 3x leverage aparece 3x no top 10 mas sempre nos slots inferiores —
  o Calmar penaliza o MaxDD maior do 3x.

## Winner pelo ranking (conservador)

**SPY EMA 125 5% | Lev 2x | Gold 75%**
- 12× cumulative vs SPY B&H (SPY final 24.739% vs strategy 4.19M%)
- MaxDD 12.80% *melhor* que SPY B&H
- É o recomendado pro leitor normal que quer menor DD.

## Config CHOSEN pelo usuário (mais agressivo, mais simples)

**SPY EMA 125 5% | Leverage 3x | Gold 0%**

Justificativa do usuário:
1. Mais fácil de manter mentalmente usando 0% ou 100% (sem gold
   allocation parcial pra rebalancear);
2. Menor fricção tributária (gold requer 2 pontos de capital gains:
   entrada no gold quando sai da leveraged, saída do gold quando
   volta).

Stats (1968-2026, 58 anos, da resposta testfol.io e tabela do post):

| Métrica | Leveraged SPY (buy&hold 3x) | Cash (Gold 0%) | SPY benchmark | **SPY EMA 125 5% \| Lev 3x \| Gold 0%** |
|---------|-----|-----|-----|-----|
| Final $ (de $1k) | $75,460 | $13,149 | $338,334 | **$9,707,866** |
| Cumulative | 7,546% | 1,248% | 33,733% | **970,686%** |
| CAGR | 7.78% | 4.60% | 10.58% | **17.19%** |
| MaxDD | -98.43% | -0.00% | -55.15% | **-57.88%** |
| Volatility | 51.87% | 0.21% | 17.09% | **34.48%** |
| Sharpe | 0.32 | NaN | 0.41 | **0.50** |
| Sortino | 0.48 | NaN | 0.58 | **0.71** |
| Calmar | 0.08 | N/A | 0.19 | **0.30** |
| Ulcer Index | 60.03 | 0.00 | 13.11 | **25.86** |
| Beta | 3.00 | -0.00 | 1.00 | **1.35** |

**Trade stats:**
- 42 total trades em ~58 anos (~0.75 trades/ano)
- 21 switches em leveraged SPY side, 21 em cash side
- Leveraged SPY side: win rate 80.95% (% do tempo 74.16%), CAGR 24.02%,
  vol 40.41% quando in-position
- Cash side: win rate 100% (trivial, cash não perde), CAGR 4.63%

**Comparação com SPY SMA 200 0% | Lev 3x | Gold 0% (estratégia "naïve
popular"):**

| Métrica | SPY SMA 200 0% \| Lev 3x | **SPY EMA 125 5% \| Lev 3x** |
|---------|---|---|
| Final $ | $4,252,670 | **$9,707,866** (2.3× better) |
| CAGR | 16.13% | **17.19%** |
| MaxDD | -71.51% | **-57.88%** |
| Total trades | 322 | **42** (7.7× fewer) |
| Win rate | 60.56% | **90.48%** |
| Switches/year | 5.76 | **0.75** |

O ajuste de EMA vs SMA + tolerância 5% vs 0% reduz drasticamente o
número de trades (e portanto fees/IR) e também o MaxDD.

## Regra de execução exata (confirmada pelo usuário nos comments)

Tolerância 5% é banda simétrica em torno do EMA:

- Se preço > EMA × 1.05 → **entrar/manter** leveraged position (3x SPY
  via UPRO ou SPXL).
- Se preço < EMA × 0.95 → **sair** da leveraged e ir para cash (ou
  gold, se `gold_alloc > 0%`).
- **Re-entry:** quando preço cruza 105% EMA de volta (não em 95% —
  assimétrico na saída vs entrada).

No comment à Ecstatic_Feeling7407, o usuário confirma: "You buy again
after 105%" (não buy back em 95%). Isso evita o "whipsaw" em
consolidações perto do EMA.

## Intenção operacional do usuário

"I will dedicate about 25% of my capital to this strategy." —
confirmado no post. Alinhado com o mandate ai-trade que aloca 20-40%
para strategies ativas (Path A + Path B); LETF rotation entra como a
tese primária do Path B, consumindo ~metade desse bucket (os outros
~10-20% do capital ativo ficam com Path A Pepperstone).

## Críticas relevantes dos comentaristas (a endereçar no Lead B1)

### ChemicalStats (quant profissional)
- "Sem block permutation analysis / stationary bootstrap, o risco de
  overfit é alto demais pra ter qualquer conclusão robusta."
- Recomendação: stationary block bootstrap + Markov chain Monte Carlo
  regime switching sobre um conjunto estreito de parâmetros a nível
  0.001 de significância.

### DysphoriaGML / Destrolas
- O teste de robustez 1970-2010 vs 1970-2025 **não vale** — overlap de
  dados contamina a correlação.
- Split válido: 1970-2010 vs 2010-2025 (mutuamente exclusivos) →
  comparar rankings.
- Cross-validation canonical também aplicável.

### James___G
- Re-rodar a análise inteira em outros mercados de equity (Japan, UK,
  DE). Se os mesmos params vencerem em mercados independentes, sinal de
  robustez; senão, é overfit US-específico.

### dimonoid123
- "Mesmo se não for overfit, impostos vão matar você." — Precisa
  modelar 15% IR BR + eventual withholding US 30% sobre distribuições
  de LETFs.

### Snoo72726 (quant)
- "Single-factor EMA crossover em índice trending é fair-weather —
  colapsa quando mercado para de trending ou vol spike. Sem macro +
  volatility conditioning, não é robusto."

### PecanPlan
- 48% MaxDD teórico (do GoldY variant) vira 67%+ na prática quando
  sequência adversa bate. "Precisa fazer 100% depois de -50% pra
  zerar — leva anos."

## Defesas do usuário (pro registro)

- "960 combos × 230 janelas diluem o overfit sobre as combinações."
  — parcialmente mitiga mas não resolve (Destrolas tinha razão).
- "Limitei o período até 2023 e o ranking era quase idêntico." — bom
  sinal mas não é CPCV rigoroso.
- "Vou usar só 25% do capital." — mitigação de risco operacional, não
  de viés estatístico.
- "Se tudo isso não valer nada (nothing at all), então por que
  investir em qualquer coisa?" — reductio pragmático; aceitável como
  convicção pessoal, mas não como prova científica.

## O que o Lead B1 precisa fazer

Traduzir o achado empírico do user em **winner auditado pelo framework
ai-trade**:

1. **Re-implementar a strategy** `src/ai_trade/backtest/strategies/
   letf_rotation.py` com params (ma_type, ma_period, band_pct,
   leverage, gold_alloc) default nos valores chosen (EMA, 125, 5%,
   3x, 0%) — mas o grid submete ~50-100 configs.
2. **UPRO synthetic pre-2009** conforme §4.4 do mandate:
   `r_UPRO = 3 × r_SPX_TR − 0.87%/252 − 0.92%/252` (drag + expense);
   post-2009 usar UPRO real (Tiingo daily).
3. **CPCV + PBO** sobre o grid (não confiar na metodologia overlapping
   do testfol.io). Window IS = 1970-2000 (30y), OOS = 2001-2015 (15y),
   stress = 2016-2026 (10y recente) — splits mutuamente exclusivos
   conforme Destrolas.
4. **Stationary block bootstrap** para CI do Sharpe (block_size =
   auto via Politis-Romano) — conforme ChemicalStats.
5. **Tax model:** 15% IR BR sobre cada lucro de switch (entrada ou
   saída da leveraged). Rodar smoke em SPY EMA 125 5% | Lev 2x |
   Gold 75% (ranking winner) **e** SPY EMA 125 5% | Lev 3x | Gold 0%
   (chosen user), reportar net CAGR pós-tax de ambos.
6. **Multi-market robustness** (stretch, opcional): re-rodar top-3
   configs em NIKKEI (N225) e FTSE (UKX) usando Tiingo internacional.
   Se winner US também vencer nos outros 2, robustez confirmada.

---

*Documento criado 2026-04-16 21:30 após usuário fornecer print do post
via Shift+P do browser (WebFetch bloqueado pelo Reddit).*

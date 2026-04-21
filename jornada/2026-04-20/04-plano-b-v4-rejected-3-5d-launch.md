# Plano B V4 rejeitado — abrindo Phase 3.5d com 3× LETFs

> **Tipo:** pivot de estratégia. Encerra um ciclo, abre outro.
> **Status:** Plano B V4 rejeitado cientificamente. Plano A em **stand-by**. Phase 3.5d **prep-ready** (não rodado).
> **Decisão de:** usuário (2026-04-20 noite).

## O resumo (1 parágrafo)

A cross-lib validation da Phase 3.5c expôs que o winner Plano B V4
(3-leg EW SSO+QLD+UGL, Sharpe OOS 2.25, CAGR 25.56%) foi validado
contra dados sintéticos proprietários de testfol.io. Quando 3 libs
independentes (bt, vectorbt, backtrader) reimplementam a mesma
estratégia em nossa pipeline (synthetic_letf + yfinance), o resultado
converge em CAGR ≈ 11.6% / max_dd ≈ -28.8% / Sharpe ≈ 0.78. Análise
head-to-head contra SSO buy-and-hold (real yfinance) confirmou que **o
regime filter EMA100 reduz drawdown 40pp ao custo de ~5pp de CAGR** —
numa posição alavancada, essa troca é neutra em Sharpe e **perde para
buy-and-hold puro**. Phase 3.5b numbers de 37.92% e 44.69% CAGR são
artifacts de modelagem sintética otimista em testfol.io. **Plano B V4
não passa nos gates do investment mandate.** Phase 3.5d é aberta com
foco em 3× LETFs e disciplina anti-overfit reforçada.

## O que estava errado no ciclo anterior

**1. Validation single-source.** Phase 3.5b validou Plano B V4 rodando
a engine `letf_rotation.py` + `portfolio_3leg_ew` em cima de dados
testfol.io. Nunca foi reproduzido em engine diferente nem em data
source alternativa. Todo o "ele passa 5 gates formais" era com o
mesmo stack — resultado formal sem poder explicativo.

**2. Modelo synthetic inflado.** testfol.io SSOSIM/QLDSIM/UGLSIM
modela LETFs de forma materialmente diferente do nosso
`synthesize_letf_returns_ffr_aware(SPX_TR)`. Em 40 anos, essa
diferença acumula em CAGR off by factor of 3-6×. Não sabemos ainda se
testfol.io está otimista ou nosso está pessimista — mas **nossa stack
concorda com 3 libs independentes**, então o peso da evidência está
do nosso lado.

**3. Indicator picks sem fair-comparison.** O V4 winner usa EMA100
regime na perna SPY (de Gayed `[leverage_for_the_long_run]`), Donchian
20/10 na perna QQQ (de Kaufman `[trading_systems_methods]`), e
Donchian 40/20 na perna GLD (mesmo). **Três indicadores diferentes em
três legs é uma forma silenciosa de expandir o search space.** Cada
escolha foi justificada isoladamente com citação, mas o conjunto não
foi testado contra alternativas homogêneas (ex: EMA em todas as
legs, ou Donchian em todas as legs). É a "multiple hypothesis
testing" clássica que o AFML alerta em p.208-211.

**4. Winner não supera buy-and-hold real.** Quando testado pós-inception
com dado real (2006-06-21+), nossa `leg_sso_only` dá CAGR 10.23%
contra SSO buy-and-hold 14.96% na canonical (21.5y), ou 13.55% vs
23.60% pós-2009 (17.3y). **O filtro de regime não adiciona valor em
bull market alavancado — só reduz drawdown pagando CAGR.** Essa é a
constatação fundamental que invalida a premissa da família LETF
rotation como montada.

## O que ficou provado (vale ouro pra próximo ciclo)

- **Infraestrutura cross-lib funciona.** 3 libs independentes (bt,
  vectorbt, backtrader) concordaram dentro de 1-2pp em todos os
  variants que rodei. É evidência forte contra implementation bugs.
- **2 bugs reais descobertos e consertados** nessa validação:
  - Stitching bug em `reference_prices.py` (synthetic pulava 42× na
    inception SSO) — fix: scaling à primeira close real.
  - Ring-buffer em backtrader adapter (`datetime.date(i)` retornava
    last bar como index 0) — fix: pre-build pandas Series via
    strategy params.
- **Engine de 3-leg EW rebalance está correta.** Múltiplos paradigmas
  produzem o mesmo resultado.
- **Regime filter EMA100 corta max_dd pela metade** (-84% SSO B&H →
  -43% filtered). Isso é um trade-off real, não bug. Só não é um
  trade-off lucrativo em bull market alavancado.

## Pergunta do usuário que precisa ser enfrentada

> "Por que no SPY/SSO foi usado EMA100 e nas outras legs foi usado
> Donchian?"

A resposta honesta: **porque foi uma escolha ad-hoc do designer da
Phase 3.5b, com citações post-hoc**. EMA veio de Gayed pra SPY (faz
sentido histórico — Gayed é a referência canônica pra LRS regime em
equities). Donchian veio de Kaufman/Clenow pra QQQ/GLD (justificado
por breakouts serem "bons pra assets com trends longos") — mas isso é
uma racionalização fraca. O Phase 3.5d vai EXIGIR ou indicator family
única em todas as legs, ou justificação por leg com p.X concreta +
teste formal contra alternativa.

## Plano A status

**Stand-by.** O winner V2-L2 Gayed CFD L=2 também foi validado contra
`synthesize_letf_returns_ffr_aware(SPX_TR)` — portanto pode estar sujeito
ao mesmo artifact que Plano B V4. Quando Phase 3.5d produzir um winner
Plano B robusto, Plano A deve ser re-validado em cross-lib também antes
de ir pra live. Até lá, não tocar, não descartar.

## Phase 3.5d — o novo ciclo

Objetivo: **encontrar uma estratégia de swing trade com 3× LETFs
(SPXL/UPRO, TQQQ, TMF opcional) que supere SPY buy-and-hold
pós-imposto (15% IR BR) na pipeline nossa, validada cross-lib desde o
primeiro passo.**

- Spec autoritativo: `specs/phase_3_5d_plano_b_v2_3x_letf.md`
- Launch prompt: `docs/self_improvement/phase_3_5d_launch_prompt.md`
- Executar via: `SWEEP_MODE=fanout bash scripts/self_improve_loop.sh`
  em feature branch dedicada (não main)
- Gates: PBO<0.5, DSR p<0.05, WF≥6/8 + **cross-lib concordância ≥
  2/3 libs PASS** + **beat-SPY gate (CAGR_net_tax > SPY_B&H CAGR)**
- Dados: reference_prices.parquet (seam-corrigida) + yfinance
  independent para Stage 2
- Duração estimada: 2-4 sessões autônomas de loop + 1-2 sessões
  interativas de arbitragem final

## Citações

- `[advances_fin_ml, p.31-34]` — two-stage replication protocol
- `[advances_fin_ml, p.208-211]` — PBO como gate obrigatório
- `[advances_fin_ml, p.273-275, p.298-299]` — DSR + WF
- `[leverage_for_the_long_run, p.13, p.16]` — LRS formula + Gayed framework
- `[trading_systems_methods, p.353]` — Donchian canonical
- `[stocks_on_the_move]` — Clenow momentum
- `[antonacci_dual_momentum]` — Dual momentum

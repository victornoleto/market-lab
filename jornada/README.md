# JORNADA — ai-trade

> Diretório de sincronização para humanos. Conta em linguagem acessível o que
> este projeto é, onde está e pra onde vai. Formato: seções fixas abaixo
> (**atualizadas a cada sessão**) + entradas datadas em arquivos individuais
> (imutáveis).
>
> Não substitui `ROADMAP.md` (mapa técnico), `README.md` (setup) nem `specs/`
> (detalhes de implementação). Complementa.

---

## O que é isso?

Um projeto pessoal que tentou construir um sistema de trading automatizado
rodando sobre **CFDs da corretora Pepperstone** (ações, índices, ouro,
crypto, forex), usando uma API programática chamada **cTrader Open API**.

Antes de ligar qualquer dinheiro real, o sistema passa por fases: primeiro
absorver livros sérios de trading/ML (pronto); depois construir um motor
de backtest rigoroso (pronto); depois encontrar uma estratégia que
sobreviva a testes estatísticos severos (**falhou — 113/113 honest FAIL**);
depois paper trading e live em passos pequenos (pausado).

A regra inviolável é que **toda decisão técnica cita um livro específico**
(`[book.slug, p.X]`). Nada de "o Claude acha que…" — só "a página 104 do
AFML diz que…". Isso blinda o projeto contra o maior risco de usar LLM em
trading: palpite disfarçado de análise.

---

## Onde estamos hoje (2026-04-24 — MODO MAINTENANCE; alocação 100% Plano C; repo consolidado via cleanup)

**Estado:** ⛵ **MAINTENANCE MODE.** Após 113/113 honest FAIL em 2 semanas
(71 phases Plano A/B + Strategy D + 42 Phase E-MVP multi-market), usuário
consolidou mandate §1 em **100% Plano C passive factor-tilted**
(`portfolio-aposentadoria.md` + `reports/portfolio_aposentadoria_v2/`);
Strategy A/B/D marcadas DORMANT (0% capital, infra retida). Override
`docs/mandate_overrides/2026-04-23-consolidate-plano-c-final.md` **Signed**.
§7 do mandate registra a consolidação. CLAUDE.md + `.claude/CLAUDE.md`
atualizados. Infra preservada para reativação futura: engine cross-lib
validada (3 libs + numpy reference concordam a 1e-6), 33 livros em
`books/summaries/`, gates honest, cost/tax models BR+US.

**Revisão programada:** 6 meses (2026-10-23) e 12 meses (2027-04-23) —
re-rodar grids contra novos dados OOS; se nada passar, projeto fecha como
"proof of rigor" / due-diligence infrastructure.

**2026-04-24 repo cleanup:** ops/ removido (39 arquivos, zero imports —
substituído por `/app` GUI). 15+ subpastas DORMANT em `reports/` consolidadas
em `reports/_dormant_summary.md` + arquivos-chave em `reports/_archive/`.
38 jornadas DORMANT consolidadas em `jornada/_archive/DORMANT_HUNTS.md`.
Ver `docs/CLEANUP_2026-04-24_LOG.md` para audit trail completo.

---

## Hunts DORMANT consolidadas

Todas as tentativas de encontrar uma estratégia ativa vencedora falharam.
O histórico narrativo detalhado (38 entries cobrindo Phase 3.5d→E-MVP,
2026-04-21→23) está em:

- **`jornada/_archive/DORMANT_HUNTS.md`** — timeline + verdict por phase
  em tabelas
- **`reports/_archive/`** — BREADTH_NO_WINNER.md de cada fase (837 linhas
  de análise detalhada preservadas)
- **`reports/_dormant_summary.md`** — overview das pastas removidas +
  killer gates comuns + recovery cheatsheet

Padrão comum dos 113 FAIL: **PBO grid-level > 0.5** + **DSR p > 0.05 após
deflator** + **bootstrap OOS 99.9% CI low cruzando zero**. Citação:
`[advances_fin_ml, p.208-211, p.196-202, p.31-34]`.

---

## Glossário mínimo

Termos que aparecem ao longo das entradas do changelog:

- **Backtest** — simular a estratégia em dados históricos pra ver como
  teria performado. Ponto de partida. Risco: parecer bom no simulado e
  falhar em live.
- **Sharpe** — medida de retorno por unidade de risco. Quanto maior,
  melhor. ~1.0 é "bom", ~2.0 é "excelente", ~0.5 é "fraco".
- **DSR (Deflated Sharpe Ratio)** — Sharpe corrigido pelo número de
  hipóteses testadas. Gate: p-value < 0.05. Fonte: AFML cap.14.
- **PBO (Probability of Backtest Overfitting)** — probabilidade da
  melhor config ter sido escolhida por overfitting. Gate: < 0.5.
- **Walk-forward** — reroda a estratégia em janelas temporais
  deslizantes. Gate: ≥ 6 de 8 janelas lucrativas + drawdown ≤ 25%.
- **CPCV** — validação cruzada temporal combinatória (purged). Dá uma
  *distribuição* de Sharpes em vez de um ponto único.
- **Survivorship bias** — usar só empresas que "sobreviveram" até hoje
  mente sobre a realidade. Correção: universo ponto-no-tempo com
  empresas delistadas inclusas.
- **CFD** — Contrato por Diferença. É como apostar no preço do ativo
  sem possuir o ativo. Cobra *swap* diário pra manter a posição.
- **AFML** — "Advances in Financial Machine Learning" (López de Prado,
  2018). Livro-fonte das técnicas anti-overfitting + meta-labeling.
- **Meta-labeling** — treinar um segundo modelo pra decidir
  "tradear/não tradear" cada sinal da estratégia primária. Filtra
  ruído, eleva precisão, pode salvar o DSR.
- **Path A / Path B** — dois "caminhos de execução" do projeto. Path A
  é Strategy A (principal, short-hold CFD Pepperstone, agressiva
  alavancada). Path B é Strategy B (secundária, swing em broker BR,
  moderada). Definidos no Investment Mandate.
- **SHORT-HOLD CFD** — posição mantida por horas a poucos dias em
  Contratos por Diferença (Pepperstone). Curta o suficiente pra evitar
  swap overnight relevante.
- **SWING BROKER** — posição mantida por dias a meses em ações/ETFs
  via broker BR tradicional (15% IR sobre lucro). Não há swap.
- **LETF rotation** — família de estratégias da Strategy B: usar uma
  média móvel (SMA ou EMA) sobre SPY como filtro de regime, alocando
  em ETF alavancado (UPRO 3x ou SSO 2x) em on-regime e em cash (ou
  ouro) em off-regime. Base científica em Gayed
  `[leverage_for_the_long_run]`.
- **Investment Mandate** — `docs/investment-mandate.md`. Consolidado
  2026-04-23: §1 = **100% Plano C passive factor-tilted**; A/B/D
  DORMANT. §2.2/§2.3 CAGR e MDD são tiers warning-only.
- **CDI BR** — taxa interbancária brasileira, ~11-14%/ano em 2026.
  Floor mínimo do mandate (estratégias ativas): estratégia que rinde
  menos que isso não é winner — é folclore.
- **Strategy D** — 3º slot proposto em 2026-04-22, FAIL 10/42 e
  marcado DORMANT em 2026-04-23. Swing-trade de ações BR (IBrX-100)
  com ranking mensal. Spec preservado em `specs/strategy_d_br_ranking.md`.
- **IBrX-100** — índice da B3 com ~100 ações mais negociadas. Liquidez
  média ≥ R$5M/dia. Concentração setorial ~35-40% em bancos + commodities
  (vs ~50% no IBOV).
- **Isenção R$20k** — isenção de IR sobre ganhos em vendas de ações no
  mercado à vista até R$20k/mês. Só vale pra swing-trade.
- **Adjusted Slope** — métrica Clenow de momentum: anualiza o slope de
  regressão log-linear sobre N dias e multiplica por R². Penaliza momentum
  ruidoso, favorece momentum suave. `[stocks_on_the_move, p.76-77]`.
- **Magic Formula** — ranking de Greenblatt: `rank(ROIC) + rank(Earnings
  Yield)` composite. `[quant_trading_chan, ch.1, p.7]`.
- **Plano C** — 3ª rota, única vencedora. Portfolio passivo long-term
  factor-tilted (AVUS/AVUV/AVDE/AVEM/AVDV/GDE/BTGD/etc), glidepath por
  idade, rebalance anual, zero alpha hunt. Master doc:
  `portfolio-aposentadoria.md`.

---

## Entradas (mais recente primeiro)

> **Estrutura:** entradas históricas pre-2026-04-20 organizadas em
> `jornada/YYYY-MM-DD/NN-slug.md`. Entradas Apr 21+ ficam no top-level
> `YYYY-MM-DD-HHMM-slug.md`. 38 entries de hunts FAIL foram consolidadas
> em `_archive/DORMANT_HUNTS.md` no cleanup 2026-04-24.

📦 **Retratadas arquivadas (9 entries):** ver
[`_archive/2026-04-16-retracted-entries.md`](_archive/2026-04-16-retracted-entries.md)
— bug Tiingo IEX em US holidays.

### 2026-04-24
- [2026-04-24 10h47 — **Hunt loop iter 007: momentum overlay no blend vol-managed dá 50/100 MARGINAL, regressão vs iter 006 (KILL #1 + #3)** [HUNT LOOP]](2026-04-24-1047-hunt-loop-iter-007-momentum-overlay-marginal.md) — Pesquisa em background (mandate §1 segue 100% Plano C). 12-1 canonical momentum overlay reduz Sharpe vs iter 006 (spy 0.941 vs 1.000; ndx 0.872 vs 1.021). Momentum é REDUNDANTE com variance-scaling — ambos rastreiam vol-regime. Moreira-Muir Table IV NÃO replica em blend vol-managed. DEAD_ENDS: signal overlay correlacionado em blend fechado. Iter 008: sinais ortogonais (carry, macro, meta-labeling) ou single-cfg verification.
- [2026-04-24 10h27 — **Hunt loop iter 006: vol-managed 60/40 SPY+TLT dá 67/100 PROMISING (novo top-K #1 do loop, 4/5 winner conditions, primeiro iter a bater +0.10 Sharpe em 2 datasets)** [HUNT LOOP]](2026-04-24-1027-hunt-loop-iter-006-vol-managed-60-40-promising.md) — Pesquisa em background (mandate §1 segue 100% Plano C). Naïve risk parity inverse-variance + Moreira-Muir portfolio scaling. +0.27 Sharpe em 24y edu, +0.10 exact em spy_real, MDD 3/3 + CAGR 3/3. DSR ainda falha; grid de 12 cfgs inflou PBO de 0.24→0.69 (Kill #3). Iter 007: pré-commit single cfg OR blend + momentum overlay.
- [2026-04-24 10h00 — **Hunt loop iter 004: vol-managed SPY dá 51/100 MARGINAL (melhor resultado do loop, passa 6/7 gates em real data, mas cai 0.02 Sharpe abaixo do corte)** [HUNT LOOP]](2026-04-24-1000-hunt-loop-iter-004-vol-managed-spy-marginal.md) — Pesquisa em background (mandate §1 segue 100% Plano C). Single-asset vol scaling Carver/Moreira-Muir. G6 bootstrap CI > 0 pela primeira vez no loop. Próxima iteração: variance-scaling canônico (Moreira 2017).
- [2026-04-24 00h30 — **Estudo de proteção a crash fecha em resultado negativo honesto — 0/16 cross-dataset winners** [EDUCACIONAL]](2026-04-24-0030-crash-protection-study-closes-negative.md) — Phase 1+2+3 sobre top-1 EMA/SMA threshold com 3× UPRO synth. 4020 configs testadas, 0 passam spec §0. 3 killers: WF MDD universal, PBO spy/ndx (0.78/0.60), DSR n=4020. Consistente com 113/113 honest FAIL.

### 2026-04-23
- [2026-04-23 23h59 — **Plano C sessão encerrada** [PASSIVE LONG-TERM]](2026-04-23-2359-plano-c-sessao-encerrada.md) — Endorse final pós-revisões.
- [2026-04-23 23h00 — **Plano C v3.5 CONSOLIDADO** [PASSIVE LONG-TERM]](2026-04-23-2300-plano-c-v3.5-consolidated.md) — Composição final 11 tickers GDE/AVUS/AVDE/AVEM/AVUV/AVDV/SPMO/IDMO/BTGD. 92.5% equity + 27.5% gold + 5% BTC. Zero US bonds.
- [2026-04-23 15h00 — **Plano C v3 BR fixed-income + stacked alts** [PASSIVE LONG-TERM]](2026-04-23-1500-plano-c-v3-br-fi-stacked-alts.md) — Bonds em BRL não USD (Campbell-Viceira 2010).
- [2026-04-23 10h03 — **Estudo educacional: EMA/SMA threshold crossover + post-mortem lookahead** [EDUCACIONAL]](2026-04-23-1003-educacional-ema_sma_threshold_sweep.md) — Sweep 384 configs. V1 tinha bug lookahead idêntico ao corrigido em commit 7b90a8f. Pós-fix: 0/384 passam 7/7 gates. Flag: `letf_rotation.py` tem pattern idêntico (não corrigido).
- [2026-04-23 07h56 — **MODO MAINTENANCE — consolidação 100% Plano C** [CONSOLIDAÇÃO FINAL]](2026-04-23-0756-maintenance-mode.md) — Usuário aprovou consolidação. Strategy A/B/D DORMANT. Override Signed. Revisão 6-12m.
- [2026-04-23 07h — **Resumo madrugada Phase 3.5f** [SHORT-HOLD CFD]](2026-04-23-0700-overnight-summary.md) — 918 testes verdes. V2-L2 Gayed cai de Sharpe 2.28 pra 0.56 (65pp lookahead inflation). Escalação com 4 opções.
- [2026-04-23 05h00 — **Plano C v2 — análise otimização portfolio aposentadoria** [PASSIVE LONG-TERM]](2026-04-23-0500-plano-c-v2-analysis.md) — Return stacking + LETFs + factor investing. 4 carteiras finais. SSO 50% do user: Sharpe pior. NTSX 100% domina. US Estate Tax 40% pra brasileiros identificado.

### 2026-04-22
- [2026-04-22 22h — **Engine lookahead bias descoberto + plano fix** [SHORT-HOLD CFD]](2026-04-22-2212-engine-lookahead-bias-descoberto.md) — Cross-lib expõe bug. Plano fix 5 fases. Detalhe técnico da descoberta.
- [2026-04-22 — **O bug da engine: apostar em cara depois de ver a moeda cair** [SHORT-HOLD CFD]](2026-04-22-engine-lookahead-bug.md) — Narrativa humana do lookahead em `plano_a_leveraged_rotation.py:462`. `letf_rotation.py` estava clean. Plano B preservado.
- [2026-04-22 12h52 — **CAGR/MDD viram tiers warning-only (mandate §2.2/§2.3)** [ARQUITETURA]](2026-04-22-1252-cagr-mdd-gates-relaxados-tier-framework.md) — Framework de tiers (Folclore→Extraordinário per rota A/B). Pepperstone ganha §4.8 staging. DARF não modelado em Pepperstone.

### 2026-04-21
- [2026-04-21 14h — **Pivot Tiingo-first + testfol.io Stage-2** [INFRA]](2026-04-21-14-data-pipeline-tiingo-first.md) — Pipeline yfinance-vs-yfinance diagnosticado (ΔCAGR 8-15pp). Fix: Tiingo-first + stage2_validation.py. Spec §3.1 proíbe yfinance direto.

### 2026-04-20 e antes
- Entradas históricas pre-2026-04-20 estão em subdiretórios datados
  `jornada/YYYY-MM-DD/NN-slug.md`. Principais marcos:
  - **2026-04-18** — Phase 3.5b Plano B: V4 (SSO+QLD+UGL) PROMOTED; V5-V8 expanded; rejected SSO/ZROZ/GLD; extended window 1986-2026 PASS. Phase 3.5a DEAD ends (T1-T2 FX/metais 1h).
  - **2026-04-17** — Phase 3 SUMMARY: 5 leads verdictados (A1/B1/A2/B2/A3). Winner #1: BollingerMR GARCH SPY 1h. Winner #2: ETF Monthly Rotation. LETF rotation PASS (EMA100/2x). 3-leg portfolio {LETF + QQQ Donchian + GLD Donchian} OOS Sharpe 2.25.
  - **2026-04-16** — Tag `v0.1-phase-2.5-winners`. Cleanup pós-winners. Investment Mandate registrado. Bug Tiingo IEX postmortem.
  - **2026-04-13 → 2026-04-15** — Runs 1-3 (Clenow + Ehlers + AFML meta). Pivô pra intraday short-hold.
  - **2026-04-11 → 2026-04-12** — Phase 0 (knowledge base dos 33 livros) + Phase 2 backtest engine.
  - **≤ 2026-03-31** — Decisões fundacionais.

Para detalhes técnicos completos dessas entradas históricas:
`git log --oneline --until=2026-04-20 -- jornada/` ou navegar
`jornada/YYYY-MM-DD/` manualmente.

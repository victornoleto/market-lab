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

Um projeto pessoal que tenta construir um sistema de trading automatizado
rodando sobre **CFDs da corretora Pepperstone** (ações, índices, ouro,
crypto, forex), usando uma API programática chamada **cTrader Open API**.

Antes de ligar qualquer dinheiro real, o sistema passa por fases: primeiro
absorver livros sérios de trading/ML (pronto); depois construir um motor
de backtest rigoroso (pronto); depois encontrar uma estratégia que
sobreviva a testes estatísticos severos (**onde estamos**); depois paper
trading e live em passos pequenos (futuro).

A regra inviolável é que **toda decisão técnica cita um livro específico**
(`[book.slug, p.X]`). Nada de "o Claude acha que…" — só "a página 104 do
AFML diz que…". Isso blinda o projeto contra o maior risco de usar LLM em
trading: palpite disfarçado de análise.

---

## Onde estamos hoje (2026-04-16 evening)

**Estado:** loop autônomo da Phase 2.5 fechado. 2 winners production-ready
+ Investment Mandate formalizado. Repositório enxugado pelo cleanup
pós-winners (`specs/post-winners-cleanup.md`).

- **Fase 0 — Biblioteca de conhecimento** ✅ 34 livros absorvidos
  (`leverage_for_the_long_run` adicionado 2026-04-16 como base científica
  da Strategy B LETF rotation). Toda afirmação tem citação `[p.X]`,
  `[ch.Y]` ou `N/A` explícito.
- **Fase 0.5 — Skill agregada** ✅ `knowledge/SKILL.md` regenerado pós-cleanup
  com 12 slugs citados nos winners + 4 slugs protegidos pelo Investment
  Mandate (22 summaries não-citados arquivados em `books/summaries/_archive/`,
  raw PDFs preservados).
- **Fase 1 — Infra Pepperstone/cTrader** 🔄 Código pronto, bloqueada pela
  Spotware (e-mail OAuth ainda não chegou).
- **Fase 2 — Motor de backtest** ✅ Engine + validation completo, baseline
  de testes pós-cleanup documentado em `ROADMAP.md`. 5 testes anti-overfit
  da literatura (CPCV, PBO, DSR, Walk-forward, Permutação) ativos como
  gates obrigatórios.
- **Fase 2.5 — Phase A + Phase B CONCLUÍDAS** ✅ Loop autônomo
  iter 19-27. **2 winners production-ready** sobreviveram a custos
  reais + bootstrap CI + regime decomp + transport cross-asset:
  - ✅ **Winner 1 [SHORT-HOLD CFD, Path A]:** Bollinger MR (20, 2σ) +
    GARCH sizing SPY 1h. IS Sharpe 0.995, OOS Sharpe 0.945. **GO-WITH-CAVEATS:**
    edge SPY-only (não transporta a XLF), viável a partir de $1k, CAGR
    líquido ~5.9%/ano (abaixo da meta CDI BR ~13-14%/ano — ver mandate).
  - ✅ **Winner 2 [SWING BROKER, Path B]:** ETF Rotation top-1 diário
    (universo SPY/QQQ/IWM/GLD/TLT, lookback 90/SMA200 filter). IS
    Sharpe 0.708, OOS Sharpe 1.477. **GO** com 22 anos de histórico, MC
    bootstrap CI95=[0.449, 1.254] lower bound > 0.
  - ❌ **Variante NO-GO:** ETFRotation top-2 — costs-sensitive (WF 5/8
    com custos reais). Documentada em `2026-04-16-1416-etf-rotation-top2-PASS.md`
    pra comparação científica.
- **Investment Mandate registrado** ✅ `docs/investment-mandate.md` define
  7 regras invioláveis: (1) capital allocation 60-80% passive + 20-40%
  ativas, (2) CAGR mínimo = CDI BR, (3) Strategy A multi-asset
  obrigatório com sweep 1:1→1:200, (4) Strategy B é família LETF rotation
  ancorada em Gayed, (5) gates sempre, (6) threading-model live, (7)
  dynamic sizing.
- **Fases 3-7** ⏳ Phase 3 inicia com 5 leads derivados do mandate
  (3 Path A: leverage sweep + screener multi-asset + threading;
  2 Path B: design LETF do zero base Gayed + benchmark vs ETFRotation).
  Execução em branch separada após cleanup.

**Fatos concretos úteis pra contexto:**
- Pytest verde com baseline pós-cleanup documentado em `ROADMAP.md`.
- Tiingo bulk completo: 1660 tickers survivorship-free, 145 MB em backup.
- Cache intraday limpo (2026-04-16): 4296 bars placeholder removidos.
- Bug-fix permanente: `_filter_orphan_intraday_bars()` rejeita bars
  intraday cuja data não bata com sessão DAILY válida — defesa contra
  bars-fake da Tiingo IEX em US holidays.

---

## O que vem a seguir (Phase 3 leads, ordem de execução)

**Onde paramos:** 2 winners production-ready, ambos com CAGR líquido
abaixo da meta (CDI BR ~13-14%/ano). Conclusão do mandate: BollingerMR
SPY 1h é base de Strategy A mas precisa virar **multi-asset + alavancado**
pra atingir 5-10%/mês; ETFRotation diário é base de Strategy B mas
precisa ser substituído por **LETF rotation** ancorada em Gayed pra
atingir ≥15%/ano.

5 leads registrados em `ROADMAP.md` §"Post-cleanup evolution (Phase 3)".
Execução em branch separada (`phase3/letf-and-multi-asset-<date>`).

**Path A — Strategy A (short-hold CFD Pepperstone, agressiva):**
1. **Lead A1 — BollingerMR leverage sweep SPY 1h.** risk_pct ∈ {0.95,
   2.0, 5.0, 10.0, 20.0} simulando margin-call bar-a-bar; Kelly f/2
   cross-check; prob-of-ruin MC 10k paths. Cita
   `[math_money_mgmt, Vince]` + `[leverage_space, Vince]` +
   `[leverage_for_the_long_run, p.7]`.
2. **Lead A2 — Multi-asset universe screener.** Pré-screener
   (Hurst/ATR/spread/volume) sobre SPY+QQQ+GLD+BTC+ETH+FX majors antes
   do backtest. Cita `[machine_trading, Chan]` +
   `[volatility_trading, Sinclair]`.
3. **Lead A3 — Per-asset BollingerMR + threading-ready code.** State
   isolado por ticker; perks opcionais (FX session filter, equity
   pre/post-market, crypto 24/7, gold news filter); output multi-asset
   portfolio metrics + correlation. Cita
   `[advances_fin_ml, ch.7/11]` (CPCV multi-asset).

**Path B — Strategy B (swing broker BR, moderada):**
4. **Lead B1 — LETF rotation, design from scratch base Gayed.**
   Objetivo: encontrar UMA config simples da família LETF rotation
   que passe rigorosamente os gates. Grid 360 configs (EMA/SMA ×
   {100, 125, 150, 200} × band {0, 3%, 5%} × lev {1x, 2x, 3x} × gold
   {0, 25, 50, 75, 100%}). Priorizar Gayed canonical (SMA 200 / band
   0% / Cash 100%) priority 1; Reddit config (EMA 125 / band 5% /
   Lev 3x / Gold 0%) é 1 seed entre outros, NÃO gospel a validar.
   Splits IS 1970-2000 / OOS 2001-2015 / Stress 2016-2026, mutuamente
   exclusivos. Stationary block bootstrap a 0.001. UPRO/SSO sintéticos
   pre-2009/2006. 15% IR BR por switch. Winner decidido pelos gates,
   não afinidade. Cita `[leverage_for_the_long_run, p.13, p.17, p.21]`.
5. **Lead B2 — LETF rotation vs ETFRotation benchmark.** Correlação dos
   sinais, blend risk-parity, MAR ratio comparison; decidir se ambos
   coexistem ou se LETF substitui ETFRotation como winner Path B.
   Cita `[advances_fin_ml, p.196-202]` (PSR) +
   `[stocks_on_the_move, p.81]`.

**Não-prioridades:**
- AFML meta-labeling — DEFERRED (não há strategy órfã precisando de
  filtro hoje).
- Carver multi-asset trend — DEFERRED (multi-day, contraditório com
  Path A; só reabre se Phase 3 falhar).

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
- **Investment Mandate** — `docs/investment-mandate.md`. 7 regras
  invioláveis sobre capital allocation, CAGR mínimo (CDI BR),
  Strategy A multi-asset obrigatório, Strategy B ancorada em Gayed,
  gates sempre, threading model live, dynamic sizing.
- **CDI BR** — taxa interbancária brasileira, ~13-14%/ano em 2026.
  Floor mínimo do mandate: estratégia que rinde menos que isso não é
  winner — é folclore.

---

## Entradas (mais recente primeiro)

📦 **Entradas retratadas arquivadas (9 entries):** ver
[`_archive/2026-04-16-retracted-entries.md`](_archive/2026-04-16-retracted-entries.md)
— bug Tiingo IEX em US holidays, fix em
`_filter_orphan_intraday_bars()`. O postmortem
[`2026-04-16-1245-data-bug-winners-retracted.md`](2026-04-16-1245-data-bug-winners-retracted.md)
permanece no top-level como documento histórico.

- [2026-04-17 0005 — B1b-i [SWING BROKER]: grid runner LETF rotation + smoke 16 configs SPY. Pipeline OK, smoke encoraja (EMA125/3x OOS Sharpe 1.94) mas NÃO é winner — gates B1c pendentes](2026-04-17-0005-b1b-i-letf-rotation-grid-smoke.md)
- [2026-04-16 2355 — B1a [SWING BROKER]: módulo LETF rotation + synthetic LETF helper entregues com 36 testes. Fundação para grid de 360 configs (B1b/B1c)](2026-04-16-2355-b1a-letf-rotation-module.md)
- [2026-04-16 2310 — A1 [SHORT-HOLD CFD]: Leverage sweep BollingerMR SPY 1h. L=2 único GO (CAGR 10.76% < CDI). L=5 bate CAGR 19.77% mas fura DD -69.84%. L≥10 ruína](2026-04-16-2310-a1-leverage-sweep-bollinger-mr-spy-1h.md)
- [2026-04-16 2254 — 🏷️ Tag `v0.1-phase-2.5-winners` liberado: snapshot reprodutível dos 2 winners, main congelada, Phase 3 abre em branch separada](2026-04-16-2254-tag-v0.1-released.md)
- [2026-04-16 2235 — ✅ Cleanup pós-winners completo: repo enxugado (520→345 tests, 18 books archived, 6 strategies removed), Phase 3 leads registrados](2026-04-16-2235-post-winners-cleanup-completed.md)
- [2026-04-16 1930 — 📌 Investment Mandate registrado; CAGRs dos winners insuficientes vs CDI BR; direção agressiva Phase 3 (5 leads)](2026-04-16-1930-investment-mandate-registered.md)
- [2026-04-16 1600 — 🏁 Phase B CONCLUÍDA: Production Readiness Summary — BollingerMR GO-WITH-CAVEATS, ETFRotation top-1 GO, ETFRotation top-2 NO-GO (costs-sensitive)](2026-04-16-1600-production-readiness-summary.md)
- [2026-04-16 1549 — Phase B Leads #4+#5: Cross-asset transport + correlação. ETFRotation expanded_8 PASS; BollingerMR XLF FAIL (SPY-only). Correlação ρ=0.252 — INDEPENDENTES, 50/50 blend Sharpe=1.020](2026-04-16-1549-cross-asset-transport-correlation-phase-b.md)
- [2026-04-16 1520 — Phase B Lead #3: MC Bootstrap CI — ETFRotation IS CI=[0.449,1.254] ROBUSTO; BollingerMR bar-level Sharpe IS=0.995/OOS=0.945](2026-04-16-1520-mc-bootstrap-ci-phase-b.md)
- [2026-04-16 1507 — Phase B Leads #7+#8: Vol-sizing ETFRotation NEUTRAL; BollingerMR scale-invariante, viável a partir de $1k](2026-04-16-1507-vol-sizing-account-sensitivity-phase-b.md)
- [2026-04-16 1458 — Phase B Lead #6: Regime decomp — BollingerMR sem quintil perdedor; ETFRotation protegida por SMA200 em bears; nenhum trigger de pausa VIX necessário](2026-04-16-1458-regime-decomp-phase-b.md)
- [2026-04-16 1435 — Phase B Lead #2: Custo-ablação — BollingerMR PASS, ETFRotation_top1 PASS, ETFRotation_top2 ⚠️ costs-sensitive (WF 5/8)](2026-04-16-1435-cost-ablation-phase-b-winners.md)
- [2026-04-16 1420 — ★ WINNER #2 [SWING BROKER, Path B]: ETF Monthly Rotation SPY/QQQ/IWM/GLD/TLT — Sharpe 0.708, OOS 2025 Sharpe 1.477, 2026-Q1 Sharpe 1.081](2026-04-16-1420-etf-rotation-monthly-PASS.md)
- [2026-04-16 1416 — Variante NO-GO [SWING BROKER]: ETF Rotation top-2 — Sharpe 0.708 mas WF costs-sensitive 5/8 com IR BR 15%](2026-04-16-1416-etf-rotation-top2-PASS.md)
- [2026-04-16 1347 — ★ WINNER #1 [SHORT-HOLD CFD, Path A]: Bollinger MR + GARCH Sizing SPY 1h — Sharpe 0.995, OOS Sharpe 0.945](2026-04-16-1347-bollinger-mr-garch-spy-1h-PASS.md)
- [2026-04-16 1245 — 🚨 BUG CRÍTICO: bars-fake da Tiingo IEX em US holidays (postmortem)](2026-04-16-1245-data-bug-winners-retracted.md)
- [2026-04-15 2301 — Vol-Expansion Breakout SPY+GLD+TLT 1h ❌](2026-04-15-2301-vol-expansion-1h.md)
- [2026-04-15 2109 — Chan pairs GLD-SLV 1h ❌](2026-04-15-2109-chan-pairs-1h.md)
- [2026-04-15 1830 — tiingo_service lazy-cache ✅](2026-04-15-1830-tiingo-service.md)
- [2026-04-15 1800 — Pivô intraday short-hold](2026-04-15-1800-pivot-intraday.md)
- [2026-04-15 1541 — F3.D Portfolio Clenow+Ehlers](2026-04-15-1541-portfolio-f3d.md)
- [2026-04-15 1353 — Long-history Ehlers SPY](2026-04-15-1353-long-history-ehlers.md)
- [2026-04-15 1349 — AFML meta-labeling Run 4 Step 1](2026-04-15-1349-afml-meta-run4s1.md)
- [2026-04-15 0900 — Sincronização + decisões](2026-04-15-0900-sincronizacao-decisoes.md)
- [2026-04-14 — Tiingo + Run 3](2026-04-14-0000-tiingo-run3.md)
- [2026-04-13 — Runs 1-2 (Clenow + Ehlers)](2026-04-13-0000-runs-1-2-clenow-ehlers.md)
- [2026-04-12 — Phase 2 concluída](2026-04-12-0000-phase2-backtest-done.md)
- [2026-04-11 — Phase 0 (knowledge base)](2026-04-11-0000-phase0-knowledge-base.md)
- [≤ 2026-03-31 — Decisões fundacionais](2026-03-31-0000-decisoes-fundacionais.md)

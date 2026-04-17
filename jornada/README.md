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

- [2026-04-17 0940 — Phase 3.5b Task 3 [SWING BROKER]: LETF rotation EMA100/2x full validation. Janela longest 1970-2026 (14191 bars, 56.3y). Sharpe 1.848, CAGR 44.69%, MaxDD 20.55%, IR vs SPY 1.60, Excess CAGR +37.18%, Corr 0.59 (25y overlap). 296 trades, avg hold 49d. ⚠️ 3 FLAGs documentadas (win rate 100% = artefato de def. de trade; $108T equity = simulação pura; benchmark SPY label "same window" é overlap 2001-2026). Winner Phase 3 íntegro](2026-04-17-0940-phase3.5b-task3-letf-full-validation.md)
- [2026-04-17 0935 — Phase 3.5b Task 2 [SWING BROKER]: hooks `get_trades()` em `letf_rotation` + `tsmom` + `aggregate_leg_trades` em `portfolio_3leg`. Script `validate_phase3_winners.py` (NEW) emite `standard_report.md`, `trade_log.{csv,md}`, `equity_curve.png`, `summary.json` por strategy + portfolio. Smoke end-to-end OK; 15 novos testes (pytest 572 → 587). ⚠️ FLAG: trade log LETF tem 100% win rate por definição de "1 bloco ON = 1 trade" — Tasks 3-6 precisam explicitar isso no jornada](2026-04-17-0935-phase3.5b-task2-get-trades-hooks.md)
- [2026-04-17 0921 — Phase 3.5b Task 1 [SWING BROKER]: módulo `standard_report.py` (Trade, StandardReport, SpyBenchmark, SpyComparison + render MD/trade-log). 22 novos testes; pytest 550 → 572. Próximo: Task 2 — ganchos `get_trades()` nos 3 winners](2026-04-17-0921-phase3.5b-task1-standard-report.md)
- [2026-04-17 0200 — ★★ Phase 3 SUMMARY [SHORT-HOLD CFD] + [SWING BROKER]: 5 leads A1/B1/A2/B2/A3 verdictados (A1 PARTIAL-GO · B1 PASS · A2 PASS · B2 DONE REPLACE_B_WITH_A · A3a FAIL · A3b PASS · A3c PARTIAL · A3d PASS). Strategy A Phase 4 = BollingerMR GARCH SPY 1h stand-alone. Strategy B Phase 4 = EW 3-leg {LETF EMA100/2x + QQQ Don 20/10 + GLD Don 40/20} OOS Sharpe 2.251, CAGR 29.06%, MDD -10.86%. Loop status: done. Gap pre-live: FX majors bulk pull Tiingo](2026-04-17-0200-phase3-summary.md)
- [2026-04-17 0040 — ★ A3d PASS [SWING BROKER]: portfolio 3-leg {LETF EMA100/2x + QQQ Donchian 20/10 + **GLD Donchian 40/20**}. Todos 3 blends (EW/IVP/HRP) passam gates. EW wins OOS Sharpe 2.251 vs baseline 2.013, DR 1.376 (HRP 1.456), DSR p=0, WF 8/8, CAGR(oos) 29.06%, MDD -10.86%, boot CI [0.946, 3.612]. TLT 3rd-leg também passa mas só via EW (Stress Sh negativo em 2022-24 hikes). ρ(LETF,GLD)=+0.063 quase ortogonal — screening confirmado](2026-04-17-0040-a3d-3leg-letf-qqq-gld-PASS.md)
- [2026-04-17 0030 — A3c [SWING BROKER]: portfolio {LETF EMA100/2x, QQQ Donchian 20/10}. Equal-weight blend OOS Sharpe 2.098 > LETF-alone 1.990 (Sharpe gate ✅), mas DR=1.12 < 1.2 (FAIL). ρ=0.555 alta demais — duas pernas são long-equity. Path B operacional continua LETF-only; buscar 3ª perna descorrelacionada (TLT/GLD)](2026-04-17-0030-a3c-portfolio-letf-donchian-FAIL-DR.md)
- [2026-04-17 0120 — ★ A3b PASS [SWING BROKER]: Donchian breakout QQQ daily 20/10 — OOS Sharpe 1.738 (marginal > LETF B1c 1.724), OOS CAGR 20.38%, WF 8/8, DSR p=0.004, bootstrap 99.9% CI [0.557, 2.954]. TLT e xrpusd FAIL. Confirma tese "match strategy family ao ativo": MR→SPY, trend→QQQ](2026-04-17-0120-a3b-tsmom-donchian-per-asset-PASS.md)
- [2026-04-17 0008 — A3a [SHORT-HOLD CFD]: BollingerMR GARCH NÃO transporta de SPY → IWM / TLT / xrpusd. Todos 3 ativos FAIL em PBO+DSR+WF. Confirma dead end: Strategy A é SPY-only; sem portfólio equal-weight viável. Próximo: A3b multi-strategy per-asset ou pivô](2026-04-17-0008-a3a-bollinger-mr-garch-per-asset-FAIL.md)
- [2026-04-17 0005 — ★ B2 [SWING BROKER]: LETF rotation vs ETFRotation top-1 benchmark. LETF domina em Sharpe/CAGR/MaxDD/MAR, blend inverse-vol destrói alpha. `REPLACE_B_WITH_A` — Path B passa a ser só LETF rotation](2026-04-17-0005-b2-letf-vs-etf-rotation-benchmark.md)
- [2026-04-16 2353 — A2 [SHORT-HOLD CFD]: Multi-asset universe screener (Hurst+ATR+vol+$vol) sobre 14 candidatos (5 ETFs + 9 cryptos). Top: IWM (H=0.447), SPY, TLT (H=0.470). Cryptos majores BTC/ETH H~0.585 trending — não MR-favorable. FX gap documentado](2026-04-16-2353-a2-multi-asset-screener.md)
- [2026-04-17 0055 — ★ B1c PASS [SWING BROKER]: LETF rotation grid 72 configs × gates 5x. Winner EMA100/2x band=0% — OOS Sharpe 1.724, OOS CAGR 41%, PBO 0.0, DSR p=0, bootstrap 99.9% CI [1.037, 2.468]. 13/72 passam. Mandate CAGR ≥15% clearado por +21pp](2026-04-17-0055-b1c-letf-rotation-gates-PASS.md)
- [2026-04-17 0030 — B1b-ii [SWING BROKER]: SPX TR loader 1970-2026 stitched (Ken French Mkt+RF pré-2001 + Tiingo SPY pós). 14,191 bars, zero NaN, 11 testes. Pipeline pronto pra Lead B1c](2026-04-17-0030-b1b-ii-spx-tr-loader.md)
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

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

### 2026-04-25
- [2026-04-25 01h42 — **Hunt loop iter 035: drop-in IEF→GLD substitution na static stack do iter 015 vira 77/100 STRONG, **TIES o teto iter 015 vindo de uma classe de ativo qualitativamente diferente** — gold (zero carry, slight contango) e IEF (term premium positivo) AMBOS extraem Sharpe ~1.05-1.10 no mesmo 90/60 levered static stack, hitting o mesmo DSR-bound 77 ceiling. Isso reclassifica a lição do iter 032/033/034: o platô do iter 015 a 77 NÃO era bond-specific edge — é uma propriedade INTRÍNSECA da arquitetura "static-stack 2-perna 90/60 leverage 1.5×" no n_trials atual. Iter 035 bate iter 015 em Sharpe (Δ015 +0.094/+0.026/+0.040 POSITIVO 3/3) AND DSR (worst-p 0.344 vs 0.548 — biggest static-stack DSR improvement ever) AND ndx MDD (−2.56pp), mas score empata em 77 porque ganhos não cruzam thresholds. **Closes ALL single-asset diversifier substitutions on 2-leg static stack** (commodity baskets, REITs, EM bonds, ultra-long bonds — todos batidos pelo mesmo teto). F-FX (recomendação top do iter 034) **DATA-BLOCKED** — Tiingo cache só tem FX spots desde 2020-01-01 (6y, insuficiente). Iter 036 PICK: G-3LEG additive 3-leg static (SPY+IEF+GLD compound, NÃO substituição) — única direção cheap ainda untouched [HUNT LOOP]](2026-04-25-0142-hunt-loop-iter-035-static-stack-spy-gld-strong-77.md) — Pesquisa em background (mandate §1 segue 100% Plano C).
- [2026-04-25 01h20 — **Hunt loop iter 034: NTSX bond-carry sleeve (zero-net-notional spread, 0.9 SPY + 0.4 IEF + 0.2 TLT) vira 72/100 PROMISING — variance-control hipótese vindicada (MDD ndx 47%→42% / spy 38%→33% vs iter 033) e Sharpe Δ015 POSITIVO em todos 3 datasets, MAS uplift +0.011/+0.014/+0.012 pequeno demais pra mover DSR worst-p 0.529 abaixo do Kill C threshold 0.20; **bond-axis FECHADO** com triple-tie em 72 de TRÊS mecânicas independentes (032 composição, 033 substituição, 034 spread sleeve)** [HUNT LOOP]](2026-04-25-0120-hunt-loop-iter-034-ntsx-bond-carry-sleeve-promising-72.md) — Pesquisa em background (mandate §1 segue 100% Plano C). Iter 034 implementou recomendação B-Sleeve do BASE_MEMORY: realocou 1/3 do bond sleeve do iter 015 (0.4 IEF + 0.2 TLT, total 0.6 preservado) — capturando carry premium da TLT sem dobrar variância (KMPV 2018 cross-sectional bond carry). **Receita matemática validada**: ρ(IEF, TLT) medida = +0.916 confirma spread vol baixo (~5.4% bond-leg vol vs iter 033 8.4% / iter 015 4.2%); MDD melhorou 4-5pp em todos os datasets reais vs iter 033. **Sharpe Δ015 POSITIVO em todos 3** (+0.011/+0.014/+0.012) — Kill A clean, primeira vez que uma variação no eixo bond bate iter 015 em Sharpe nos 3 datasets. Mas o uplift é estruturalmente pequeno demais (~1/3 da magnitude que mexe DSR a n=4291) — DSR worst-p 0.529 (edu) > 0.20 (Kill C threshold), score 72 PROMISING. **Achado estrutural**: três iters consecutivos (032/033/034) com mecânicas qualitativamente diferentes (composição, substituição, spread sleeve) **todos cravam 72/100 com decomposição IDÊNTICA byte-por-byte** (1:25 + 2:17 + 3:0 + 4:15 + 5:10 + 6:5). Isso é prova empírica de que o eixo bond saturou — o platô do iter 015 a 77 é a fronteira eficiente real. **MDD pode mover sem Sharpe mover** em portfolios vol-constrained (regra nova). Iter 035 PICK: **F-FX FX carry overlay** (long AUDUSD + short USDJPY) — eixo distribution-orthogonal de verdade, dados já em cache, ~30-45 min. Bond-axis variations (qualquer α-sweep, ZROZ/EDV, bond+commodity) explicitamente fechadas.
- [2026-04-25 00h56 — **Hunt loop iter 033: NTSX long-duration variant (0.9 SPY + 0.6 TLT static stack, IEF→TLT swap) vira 72/100 PROMISING — Kill C DSR triggered; Sharpe TIED com iter 015 nos dados reais (Δ +0.001/ndx, −0.007/spy), MDD ndx breach +6.93pp (47.04% vs 40.12% ceiling) por 2022 rate-spike + tech-selloff dual stress; score-tied byte-for-byte com iter 032 (também 72) de mecânica diferente — platô iter 015 a 77 STRONG é resistente a variações no eixo bond** [HUNT LOOP]](2026-04-25-0056-hunt-loop-iter-033-ntsx-tlt-promising-72.md) — Pesquisa em background (mandate §1 segue 100% Plano C). Iter 033 trocou IEF (7-10y, ~6y dur) por **TLT (20-30y, ~17-18y dur)** no mesmo NTSX 0.9/0.6 do iter 015, testando KMPV 2018 thesis de que long-end term premium é maior. **Resultado**: prêmio aparece (CAGR +0.4-1.0pp 3/3 datasets) mas é cancelado pela variância do bond leg dobrar (~7% IEF vol → ~14% TLT vol) na curva de Sharpe — net Sharpe Δ ≈ 0 nos windows post-2009 reais. O +0.067 Sharpe edu uplift vem dos 4 anos extras de janela (2002-2008 bond bull), não da troca de ticker. DSR worst-p 0.31 fails Kill C (0.20 threshold) — todas 3 datasets fail; com Sharpe ≈ iter 015 e n_trials=4288, DSR não pode melhorar. ndx 2022 dual stress (QQQ −33% + TLT −31%) compõe pra ~47% MDD breach. **Achado estrutural**: bond-duration é CAGR-MDD trade-off, NÃO Sharpe lever em static stacks — variance scales with duration² e cancela carry premium gain. **Empate suspeito iter 032=iter 033=72** com mesma decomposição (1:25 + 2:17 + 3:0 + 4:15 + 5:10 + 6:5) de mecânicas estruturalmente diferentes confirma que o platô do iter 015 a 77 é a fronteira eficiente real do family "stack estático SPY + 1 título". Iter 034 PICK: **bond carry SLEEVE** (zero-net-notional duration spread on iter 015 base) — preserva variância e adiciona prêmio.

### 2026-04-24
- [2026-04-24 22h59 — **Hunt loop iter 030: R-2 VIX z-score gate (60d window, 2σ threshold) vira 71/100 PROMISING — 1ª vez 7/7 gates no spy_real + 1ª passagem DSR sub-0.05 no spy_real (p=0.0345), mas Kill A+B triggered: estrutura single-axis VIX-gate fechada após 3 iters convergirem em 71** [HUNT LOOP]](2026-04-24-2259-hunt-loop-iter-030-vix-zscore-vrp-promising-71.md) — Pesquisa em background (mandate §1 segue 100% Plano C). Iter 030 implementou a R-2 sugerida por iter 029 — só abrir o put credit spread se VIX z-score sobre 60d < 2σ. **Resultado dual mais agudo do loop**: spy_real explodiu (Sharpe 1.36 vs iter 026 1.28; +0.080; **1ª vez 7/7 gates** + **1ª passagem DSR sub-0.05 ever no spy_real, p=0.0345**), mas educational regrediu (Sharpe 1.14 vs iter 028/029 ~1.27; Kill B 0.021 below floor — rolling-mean de 60d **absorve o spike inicial da GFC em ~3 meses**, então sustained Q4 2008 fica unfiltered) e ndx_real regrediu mais ainda (Sharpe 1.24 vs iter 026 1.37; −0.131; Kill A clean 2.6× threshold — z-score over-fires em tech-conditional mini-spikes). Score 71 **empata iter 028 e iter 029**. **DESCOBERTA ESTRUTURAL**: 3 iters sucessivas (028 level / 029 level+persistence / 030 z-score) todas convergem em 71/100, cada uma com sub-0.05 DSR record num dataset *diferente* (iter 026 ndx, iter 028/029 edu, iter 030 spy). Single-axis VIX-gate family no iter 026 base agora estruturalmente FECHADA. iter 031 PICK: **R-1+R-2 AND-composite** (skip só quando level+persistência AND z-score ambos firam) — única path estruturalmente nova no VIX-gate family.
- [2026-04-24 22h36 — **Hunt loop iter 029: R-1 VIX-persistence gate (VIX≥35 por 3 dias consecutivos) vira 71/100 PROMISING — Kill A triggered, mas DSR direction-correct (spy 0.136→0.100 caminhou 27%; edu 0.029→0.025 NOVO RECORDE) e revela assimetria estrutural entre os 3 datasets** [HUNT LOOP]](2026-04-24-2236-hunt-loop-iter-029-vix-persistence-vrp-promising-71.md) — Pesquisa em background (mandate §1 segue 100% Plano C). Iter 029 implementou a refinação R-1 indicada por iter 028 — só skip a abertura do put credit spread se VIX ≥ 35 por 3 dias consecutivos (Bondarenko 2014 §3 sustained-regime def). **Educational preservado E levemente melhorado** vs iter 028 (Sharpe +0.014, **DSR p=0.0251 NOVO RECORDE no longest window** vs 0.0287 de iter 028). **spy_real recuperação parcial** vs iter 028 (Sharpe +0.048, 3/6 triggers transientes corretamente liberados — Mar/2020 e mini-spikes 2022). **ndx_real idêntico ao iter 028** (todos os 4 triggers já eram clusters persistentes — R-1 não tem o que refinar). DSR worst-p melhorou 27% relativo (0.136 → 0.100) MAS perdeu o threshold de 10 pts por **0.0003** (knife-edge categórico) → score empata iter 028 a 71. **Kill A triggered** (spy −0.052 e ndx −0.067 vs iter 026). **Achado estrutural NOVO**: os 3 datasets têm regime-structure qualitativamente diferentes pra high-VIX (edu deeply-persistent GFC; spy mixed transient/persistent; ndx all-clustered) — gate single-parameter não consegue otimizar todos 3 simultaneamente. iter 030 PICK: **R-2 VIX z-score gate** (filter quando z>2 sobre 60d, ortogonal a level + persistência) — strongest path to WINNER agora.
- [2026-04-24 22h07 — **Hunt loop iter 028: VIX-filter VRP (Sinclair p.217 `VIX<35`) vira 71/100 PROMISING — Kill A triggered (spy −0.10, ndx −0.07 Sharpe), mas educational 1st-ever 7/7 gates + 1st-ever DSR PASS (p=0.029, 5100 bars); filtro é regime-conditional** [HUNT LOOP]](2026-04-24-2207-hunt-loop-iter-028-vix-filter-vrp-promising-71.md) — Pesquisa em background (mandate §1 segue 100% Plano C). Iter 028 adicionou à base iter 026 a regra explícita de Sinclair p.217: só abrir put-credit-spread quando VIX<35. Resultado dual: educational (2006-2026, contém 2008 GFC) **explodiu** (Sharpe 1.26 vs 1.13, 7/7 gates 🔥, DSR p=0.029 🔥 — 1ª sub-0.05 DSR nesse dataset); mas spy_real e ndx_real (post-GFC) regrediram (Sharpe −0.10/−0.07 vs iter 026, DSR p 0.07→0.14 e 0.04→0.06). **Kill A TRIGGERED** pré-committed (regressão > 0.05 em 2/3). Achado estrutural: a regra de Sinclair é **regime-conditional não universal** — lifta em samples com regime sustentado de vol (2008-Q4) mas regride em samples pós-GFC onde spikes de VIX são transientes-mean-reverting (Mar-2020, 2022-rate-hike) que iter 026 captura lucrativamente. Assimetria é **persistência**, não nível. Score 76→71 (regressão inteiramente via DSR worst-p criterion). iter 029 PICK: **R-1 VIX-persistence gate** (filtrar só quando VIX > 35 por ≥ 3 dias consecutivos) — preserva spy/ndx + mantém educational lift → candidato strongest-ever a WINNER.
- [2026-04-24 21h44 — **Hunt loop iter 027: Levered VRP-primary (`harvest_notional=3.5`) vira 74/100 PROMISING — Kill A triggered, leverage NÃO é Sharpe-neutral em total-return; CAGR floor 3/3 ✓ mas DSR colapsa 0.083→0.517** [HUNT LOOP]](2026-04-24-2144-hunt-loop-iter-027-levered-vrp-promising-74.md) — Pesquisa em background (mandate §1 segue 100% Plano C). Iter 027 alavancou iter 026 (1.0→3.5×) esperando manter Sharpe (teoria) e limpar CAGR floor. Resultado: CAGR 3/3 ✓ (11.43/12.05/16.82% — gain estrutural), MDD 3/3 ✓ (50.7/23.1/28.8%), mas Sharpe regrediu 0.31-0.37 em todos 3 datasets (edu 1.13→0.80, spy 1.28→0.91, ndx 1.37→1.06) e DSR p colapsou (0.083→0.517 edu; 0.070→0.464 spy; **0.038→0.281 ndx — 1ª passagem DSR de iter 026 revertida**). Achado álgebra: `Sharpe(N) = overlay_sharpe + rf_d/(N×σ_h)×√252` — bonus rf é diluído por leverage. iter 026's +0.38-0.45 alpha era N=1-específico. 4/5 winner conditions (DSR sole gap). Score 76→74 PROMISING. iter 028 PICK: **V-3 VIX-filter VRP** (Sinclair p.217) em iter 026 base — lift overlay_sharpe diretamente.
- [2026-04-24 21h22 — **Hunt loop iter 026: VRP-primary stand-alone (T-bill + short SPY put credit spread) vira 76/100 STRONG (#5 top-K), com 3 marcos inéditos do loop — 1ª passagem DSR ever (ndx p=0.038), 1ª vez 7/7 gates (ndx), maior edge Sharpe cross-ds (+0.38 a +0.45)** [HUNT LOOP]](2026-04-24-2122-hunt-loop-iter-026-vrp-primary-strong-76.md) — Pesquisa em background (mandate §1 segue 100% Plano C). Removendo o vol-target wrapper iter 020/021 e usando T-bill direto como colateral, o harvest VRP vira o motor único do retorno. Sharpe 1.13/1.28/1.37 (Δ frozen +0.45/+0.38/+0.41), MDD 16.8/6.4/8.2% (vs benchmarks 55/34/35% — redução dramática), gates 6/6/**7** (ndx 7/7), DSR p=0.083/0.070/**0.038** (ndx **1ª passagem DSR de qualquer dataset no loop inteiro**, n=4279), G3 WF 8/8 em todos, G7 xlib **0.0000pp** (paridade pandas-vs-numpy perfeita). Não é WINNER (3/5: DSR worst-p edu/spy + CAGR floor 0/3 estrutural — harvest unlevered tem teto 5-6%/yr). Score 76 entra top-K #5 (entre iter 015 a 77 e iter 008 a 74). Iter 027 PICK provável: Option V-2 (levered VRP, harvest_notional=2.0) — pode produzir o **primeiro WINNER do loop**.
- [2026-04-24 17h29 — **Hunt loop iter 016: static 60:40 × vol-target híbrido vira 79/100 STRONG, NOVO TOPO do loop, 4/5 winner conditions, DSR p cai pra 0.13 no melhor dataset** [HUNT LOOP]](2026-04-24-1729-hunt-loop-iter-016-static-vm-hybrid-strong-79.md) — Pesquisa em background (mandate §1 segue 100% Plano C). Combinação do iter 015 (razão fixa 60:40) + iter 008 (vol-target scaling Moreira-Muir). **Resultado supera ambos os pais:** Sharpe 0.98/1.14/1.19 (Δ vs iter 015 +0.20/+0.09/+0.13; Δ vs iter 008 +0.12/+0.14/+0.17), MDD 31.3%/26.7%/**23.2%** (edu −13pp, ndx −16pp), G3 WF 8/8 em spy+ndx (1ª vez). DSR p=0.226/0.163/0.132 — metade do iter 015, ainda > 0.05 mas 3 datasets dentro de 1σ. Score **79/100** (25+19+0+15+15+5), 4/5 winner conditions, DSR único gate falhando. Pós-funding-cost: os 3 datasets continuam passando +0.10 gate (mais robusto que iter 015). Iter 017 PICK: Option R (NTSX/NTSI/NTSE regional rotation) — adicionar dimensão cross-sectional ortogonal.
- [2026-04-24 17h04 — **Hunt loop iter 015: synth NTSX 90/60 SPY+IEF stack é o NOVO TOPO do loop — 77/100 STRONG, 4/5 winner conditions, DSR é o único bloqueio** [HUNT LOOP]](2026-04-24-1704-hunt-loop-iter-015-static-ntsx-strong-77.md) — Pesquisa em background (mandate §1 segue 100% Plano C). Primeira iteração após 4 overlays consecutivos morrerem em cointegração com σ²_port (009/012/013/014). Mudou MECANISMO: Option G (return-stacked) na forma mais simples — peso fixo 0.9 SPY + 0.6 IEF, rebalance diário, single cfg `ntsx_synth_90_60_daily`, sem overlay. Resultado: **primeira vez no loop com Sharpe edge +0.10 em 3/3 datasets** (edu +0.10, spy +0.14, ndx +0.11), 9/9 sub-janelas positivas, gates 5/7-6/7-6/7, CAGR+MDD floor 3/3. Score **77/100 STRONG** — novo recorde (era 74 PROMISING). Apenas DSR (worst p=0.548 com n_trials=4258) impede WINNER. Pegadinha honesta: synth NTSX não modela funding cost dos futuros (~75-100 bps/ano drag); pós-cost o edge real provavelmente cai pra +0.04-0.10 (BORDERLINE em 2/3 ds). Iter 016 PICK: Option P (static stack × vol-mgmt hybrid) pra atacar DSR via Sharpe uplift sem reabrir cointegração.
- [2026-04-24 16h42 — **Hunt loop iter 014: EBP credit-cycle overlay rejeitado pelo pre-validation screen, overlay family do iter 008 blend FECHADA** [HUNT LOOP]](2026-04-24-1642-hunt-loop-iter-014-ebp-credit-pre-val-fail.md) — Pesquisa em background (mandate §1 segue 100% Plano C). Option E testada com nova metodologia: **pre-validation screen** (60d |ρ(EBP_z, σ²_port(blend))| > 0.30 exceed > 20% → abort) antes de gastar DSR budget. Screen FAILS nos 3 datasets — exceed_frac 68.4%/69.1%/70.6% (3.4× sobre o cap), mean |ρ| ≈ 0.47, max 0.96. EBP's residual não é ortogonal a σ²_port em 60d. **Quarta overlay consecutiva a falhar em iter 008 blend com mesmo diagnóstico** (009 T10Y3M sym / 012 T10Y3M asym / 013 LR meta / 014 EBP) — overlay family FECHADA no mecanismo. `cumulative_n_trials` inalterado em 4255. Próximo iter precisa MUDAR mecanismo: Option G (return-stacked ETF), cross-sectional factor momentum, ou options-skew em SPY plain. Pre-validation screen agora MANDATORY em qualquer overlay/meta-label futuro em vol-managed blend.
- [2026-04-24 15h56 — **Hunt loop iter 012: overlay assimétrico T10Y3M (5d EMA, equity-only) dá 58/100 MARGINAL, Kill #1 + #3 + #4 TRIGGERED — família T10Y3M-overlay FECHADA** [HUNT LOOP]](2026-04-24-1556-hunt-loop-iter-012-asymmetric-term-spread-overlay-marginal-58.md) — Pesquisa em background (mandate §1 segue 100% Plano C). Option B' (recomendado pelo BASE_MEMORY após iter 011). Sharpe REGRIDE em 3/3 datasets vs iter 008 (edu −0.041, spy −0.035, ndx −0.053). **Gate-fire/bottom-20%-scale overlap é 100% em edu+spy** — mesmo diagnóstico do iter 009, 5d EMA NÃO resolveu redundância com variance-scaling. Iter 009 (symmetric+21d) + iter 012 (asymmetric+5d) juntos FECHAM a matriz 2×2 {smoothing × asymmetry} da família T10Y3M-overlay. Redundância é cointegração estrutural, não escolha de parâmetro. Iter 013 picks (proibido re-testar T10Y3M/yield-curve): (C) meta-labeling AFML ch.3 [ortogonal por construção, primary], (E) EBP credit-cycle, (G) return-stacked ETF.
- [2026-04-24 15h27 — **Hunt loop iter 011: weekly rebalance 3-leg blend dá 52/100 MARGINAL, Kill #1 + #3 TRIGGERED** [HUNT LOOP]](2026-04-24-1527-hunt-loop-iter-011-weekly-blend-marginal-52.md) — Pesquisa em background (mandate §1 segue 100% Plano C). Option F empiricamente falsificada: Sharpe regride em 3/3 datasets vs iter 010 daily (edu −0.05, spy −0.02, ndx −0.10). **MDD explode +10-14 pp** (vol-targeting requer cadência diária). DSR **piora** (0.368→0.515) — reduzir T cancela crescimento do Sharpe periódico em primeira ordem. Turnover UP. Cross-asset correlation mais fraca em semanal. **Teto DSR via timeframe change é estruturalmente indisponível** pra variance-targeting blends. Iter 012 picks: (B') overlay assimétrico daily, (C) meta-labeling daily.
- [2026-04-24 15h06 — **Hunt loop iter 010: 3-leg SPY+TLT+GLD blend empata com iter 008 em 74/100 PROMISING (hunt-loop high mantido, não superado)** [HUNT LOOP]](2026-04-24-1506-hunt-loop-iter-010-three-asset-blend-promising-74.md) — Pesquisa em background (mandate §1 segue 100% Plano C). Extensão estrutural: naïve risk parity + Moreira-Muir a N=3 pernas. Sharpe edu +0.12 / spy +0.04 / ndx −0.03 vs iter 008. Family satura ~1.00 Sharpe em dados reais independente de N=2/3; DSR é o teto real (worst p=0.368 em n_trials=4246). 4/5 winner conditions. Iter 011 candidates: (F) weekly rebalance, (C) meta-labeling, (B') overlay assimétrico. Pick: F (ataque direto ao DSR).
- [2026-04-24 14h47 — **Hunt loop iter 009: term-spread overlay no blend vol-managed dá 64/100 PROMISING, regressão vs iter 008 (Kill #3 TRIGGERED)** [HUNT LOOP]](2026-04-24-1447-hunt-loop-iter-009-term-spread-overlay-promising-64.md) — Pesquisa em background (mandate §1 segue 100% Plano C). T10Y3M binary haircut EMA21 threshold=0 haircut=0.5 symmetric. Sharpe cai −0.01 a −0.03 em todos os datasets. 100% overlap com bottom-20% blend scale em 2/3 datasets — EMA de 21d destruiu a propriedade de lead-time de 6-18 meses do sinal macro. DEAD_ENDS: smoothing ≥ 21d em sinal macro leading destrói ortogonalidade. Iter 010: 3-asset blend SPY+TLT+GLD (extensão estrutural).
- [2026-04-24 14h11 — **Hunt loop iter 008: single-cfg ex-ante blend vol-managed dá 74/100 PROMISING (novo top-K #1, G1 PBO neutralizado, 4/5 winner)** [HUNT LOOP]](2026-04-24-1411-hunt-loop-iter-008-single-cfg-ex-ante-blend-promising-74.md) — Novo recorde do loop. Verifica iter 006 edge estrutural. Ver arquivo se ainda não existe (gerado pelo loop anterior).
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

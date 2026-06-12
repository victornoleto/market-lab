# LRS — Relatório Consolidado e Comparação com RSC-US 35/40/25

> **Status:** research-only / diagnóstico. Este documento **não** autoriza deploy,
> paper-trade nem mudança de mandato. Mandate §1 inalterado. Sintetiza o que foi
> estudado na linha `lrs/` (Phases 0–5, 2026-06-07/08) e compara com a
> estratégia estática RSC-US 35/40/25 (`studies/return_stacked_core/`).

---

## 1. O que é o LRS

Restart local da família **Gayed / Leverage for the Long Run**: regra base
`underlying.shift(1) > SMA200.shift(1)` → exposição alavancada (LETF); caso
contrário, sleeve defensiva. Execução **semanal**, lag operacional `n=0..5`,
imposto **DARF anual** (15% sobre ganho realizado, Lei 14.754/2023). A SMA é um
proxy de regime de volatilidade/downside, não um otimizador de retorno
`[leverage_for_the_long_run, p.13]`, `[leverage_for_the_long_run, p.7-8]`.

---

## 2. O que fizemos — fase a fase

| Fase | O que testou | Linhas | Resultado-chave |
|---|---|---|---|
| **0** Baseline Gayed | SPY/QQQ 2x/3x × lag, risk-off=CASHX | 24 | Retorno existe, **drawdown ruin** (−88% a −92%). |
| **1** Risk-off | 4 branches × 11 sleeves × lag | 264 | Risk-off diversificado importa muito; SPY 2x fica "usável" (MDD ~−41%). |
| **2** Alavancagem-alvo + throttle de vol | SPY/QQQ × 8 alav × 5 risk-off × 5 vol × lag | 2.400 | **Driver real.** Geometria de exposição resolve a maior parte do drawdown. |
| **3A** Filtros risk-on (AND) | 3 bases × 9 filtros × lag | 324 | **Negativo:** nenhum filtro bate o controle `none`. Histerese como AND ≡ `none`. |
| **3A-2** Formas de regime (substituem SMA) | 6 bases × 6 formas × lag | 216 | **Negativo:** nenhuma forma bate SMA200 nas 2 branches; histerese/ROC/Clenow como gate pioram muito o MDD (whipsaw alavancado). |
| **3C** Estudo de lookback ("por que 200?") | 13 janelas × {SMA,EMA} × 6 bases × lag | 936 | Pela regra de platô pré-registrada, **frágil**; janela "natural" teórica (~22–41d) é muito menor que 200; **adaptativo não ajuda** (pior líquido de turnover). |
| **4** Gates do mandate (diagnóstico) | 6 bases SMA200 × suíte de 7 gates | 6 | **0/6 passam.** Gate vinculante = walk-forward; QQQ também PBO/DSR. |
| **5** Overlay RSC rebuilt-sleeve | RSC reconstruído (`GDESIM/RSSTSIM/ZROZSIM`) + satélites LRS/T3d em `90/10`, `80/20`, `70/30` | 9 overlays | **Negativo no strict com RSST proxy revisado:** 0/9 passam; maior CAGR é `70% RSC / 30% T3d-K2`, mas com MDD muito pior. |
| **Top-20 CAGR** | Todos os CSVs `lrs/results/*.csv`, sem filtro de drawdown | 4.183 rows | Top row: QQQ L3.00/ZROZ/RV63<=40%/lag5, CAGR 25,84%, MDD −71,05%. |

**Conclusão transversal:** a **geometria de exposição** (alavancagem-alvo +
risk-off diversificado + throttle de volatilidade realizada) é o que entrega o
resultado. Nenhum **filtro** (3A), **forma de regime** (3A-2), **janela** ou
**adaptatividade** (3C) supera a base SMA200-level — e a própria base **não
clareia os gates** do mandate (4) `[trading_systems_methods, p.939]`,
`[advances_fin_ml, p.208-211]`. A Phase 5 não resgata LRS standalone; com o RSST
tracking proxy revisado, nenhum overlay passa o screen estrito. O Top-20 por CAGR
foi gerado para escolha manual do próximo lead, sem filtro de drawdown.

---

## 3. Melhores leads do LRS (varredura dos CSVs de resultado)

Por branch, dentro de bandas de drawdown. **São números de backtest, selecionados
entre ~3.876 configs; nenhum passou os gates (Phase 4) → otimistas por seleção.**

### SPY (underlying after-tax ~10,56%/ano, 1968–2026)

| Lead | Config | CAGR | MDD | Sharpe | Calmar | Terminal/U |
|---|---|---|---|---|---|---|
| **Headline** (carregado p/ 3A→3C→P4) | P2 · L2,00 · lag3 · 50 ZROZ/25 GLD/25 CASH · RV21≤30% | 15,44% | −39,28% | 0,718 | 0,393 | 12,28x |
| Melhor Calmar (≤40%) | P2 · L1,75 · lag3 · 50 ZROZ/25 GLD/25 CASH · RV63≤40% | 14,82% | −37,40% | — | 0,396 | 8,97x |
| Maior CAGR (≤50%) | P2 · L2,50 · lag3 · 50 ZROZ/50 GLD · RV21≤30% | 17,38% | −48,54% | — | 0,358 | 32,39x |

### QQQ (underlying after-tax ~14,36%/ano, 1986–2026)

| Lead | Config | CAGR | MDD | Sharpe | Calmar | Terminal/U |
|---|---|---|---|---|---|---|
| **Headline** (carregado p/ P4) | P2 · L1,75 · lag0 · SMA200 · 40/40/20 · RV63≤40% | 19,46% | −42,58% | 0,725 | 0,457 | 5,82x |
| Melhor Calmar (≤40%) — **frágil, não promovido** | P3C · L1,50 · lag0 · EMA w100 · 40/40/20 · RV63≤40% | 19,29% | −37,40% | — | 0,516 | 5,50x |
| Maior CAGR (≤50%) — **frágil, não promovido** | P3C · L1,75 · lag1 · SMA w175 · 40/40/20 · RV63≤40% | 21,53% | −42,55% | — | 0,506 | 11,66x |

> Extremos só de referência (ruin-tier, **não candidatos**): Phase 0 QQQ 3x
> CAGR 21,34% / MDD −91,97%; SPY 3x 16,91% / −88,33%.

---

## 4. Phase 4 — resultado dos gates (diagnóstico)

`n_trials = 3876` (linhagem Phase 2+3A+3A-2+3C). Matriz PBO = grade de geometria
Phase 2 em SMA200 (200 configs/branch). WF: ≥6/8 janelas OOS de ~3 anos batendo o
underlying after-tax.

| Base | G1 PBO | G2 DSR p | G3 WF | G4 OOS | G5 FWD | G6 Boot 99,9% | G7 xlib | **Geral** |
|---|---|---|---|---|---|---|---|---|
| SPY spy_top | 0,016 ✅ | 0,034 ✅ | 12/17 ❌ | ✅ | ✅ | ✅ | ✅ | **FAIL** |
| SPY spy_alt_off | 0,016 ✅ | 0,029 ✅ | 12/17 ❌ | ✅ | ✅ | ✅ | ✅ | **FAIL** |
| SPY spy_lower_lev | 0,016 ✅ | 0,024 ✅ | 10/17 ❌ | ❌ | ✅ | ✅ | ✅ | **FAIL** |
| QQQ qqq_top | 0,643 ❌ | 0,164 ❌ | 6/11 ❌ | ✅ | ✅ | ✅ | ✅ | **FAIL** |
| QQQ qqq_alt_vol | 0,643 ❌ | 0,164 ❌ | 7/11 ❌ | ✅ | ✅ | ✅ | ✅ | **FAIL** |
| QQQ qqq_lower_lev | 0,643 ❌ | 0,145 ❌ | 4/11 ❌ | ✅ | ✅ | ✅ | ✅ | **FAIL** |

- **SPY é o menos-rejeitado (6/7):** passa PBO e DSR mesmo com n_trials=3876;
  só falha o walk-forward (70,6% < 75%) e, no `spy_lower_lev`, o OOS.
- **QQQ é claramente rejeitado:** falha PBO, DSR e WF.

---

## 5. A estratégia de comparação — RSC-US 35/40/25

**Return-Stacked Core (US):** `35% GDE / 40% RSST / 25% ZROZ` — exposição
return-stacked/capital-efficient (≈ 71,5% ações + 40% managed futures + 31,5%
ouro + 25% Treasuries longas), **gross leverage ~1,68x**, **estática** (rebalance
periódico, turnover baixíssimo → **tax-efficient**). Fonte:
`studies/return_stacked_core/us_core/REPORT.md`.

| Janela | CAGR | MDD | Sharpe | Calmar | Terminal |
|---|---|---|---|---|---|
| 1988–2026 (proxy sintético) | **15,70%** | **−29,94%** | **1,04** | **0,524** | 265x |
| pós-2010 (ETFs reais GDE/RSST/ZROZ) | 14,81% | −21,46% | 1,062 | 0,69 | 8,6x |
| 100% SPY (1988–2026, referência) | 11,46% | −55,14% | 0,69 | 0,208 | 64x |

Sequence-risk (MC 20a, bootstrap de blocos): terminal p10/med/p90 =
7,91x / 18,81x / 39,90x, MDD mediano −24,49% (vs SPY −35,62%). Research-only;
**ainda sem a suíte completa de 7 gates** `[testing_tuning, p.318-320]`,
`[advances_fin_ml, p.208-211]`.

### Rerun atual com RSSTSIM ajustado

Após o ajuste pedido no `RSSTSIM` (`SPYSIM + 70% DBMFSIM + 30% KMLMSIM -
(CASHX + 200 bps/ano)`), a janela comum passa a ser 2000+ porque `DBMFSIM` começa
em 2000. Nessa base, o RSC-US `35/40/25` continua batendo SPYSIM com drawdown bem
menor:

| Curva | Janela | CAGR | MDD | Sharpe | Sortino | Calmar | Terminal |
|---|---|---:|---:|---:|---:|---:|---:|
| RSC-US ajustado | 2000-01-04..2026-05-21 | 12,40% | −30,76% | 0,838 | 1,153 | 0,403 | 21,71x |
| SPYSIM | 2000-01-04..2026-05-21 | 8,39% | −55,14% | 0,514 | 0,653 | 0,152 | 8,34x |

Terminal relativo RSC/SPYSIM: `2,60x`; spread de CAGR `+4,01pp/ano`; melhora de
MDD `+24,38pp` `[risk_parity, p.80-81]`, `[systematic_trading, p.185-188]`.

---

## 6. Comparação LRS × RSC-US 35/40/25

| Dimensão | LRS SPY headline | LRS QQQ headline | **RSC-US 35/40/25** |
|---|---|---|---|
| Janela | 1968–2026 (58a) | 1986–2026 (40a) | 1988–2026 (38a) |
| Base fiscal do número | **after-tax** | after-tax | **gross (proxy)** |
| CAGR | 15,44% | 19,46% | **15,70%** |
| MDD | −39,28% | −42,58% | **−29,94%** |
| Sharpe | 0,718 | 0,725 | **1,04** |
| Calmar | 0,393 | 0,457 | **0,524** |
| Mecanismo | 2x LETF + timing SMA200 semanal | 1,75x LETF + timing | return-stacked **estático** ~1,68x |
| Turnover / imposto | alto (giro ~5–6/ano, DARF pesado) | alto | **~zero (tax-efficient)** |
| Path-dependence | alta (decay/whipsaw de LETF) | alta | baixa (sem timing) |
| Diversificação | single-index | single-index | ações+MF+ouro+bonds |
| Validação | **reprovou Phase 4 (0/6)** | reprovou (PBO/DSR/WF) | research-only (sem 7 gates ainda) |

### Leitura

1. **RSC domina o risco-ajustado sem ambiguidade:** Sharpe **1,04 vs 0,72**,
   Calmar **0,524 vs 0,393**, MDD **−30% vs −39%**, com CAGR igual ou melhor.
   Mesma rentabilidade, ~10pp menos de drawdown e retorno de qualidade muito
   superior `[leverage_for_the_long_run, p.4-7]`, `[risk_parity, p.80-81]`.
2. **RSC é tax-efficient por ser estática.** O número de 15,70% é gross, mas com
   turnover quase nulo o after-tax fica próximo dele. O LRS já está after-tax —
   pagou DARF pesado pelo giro semanal para chegar aos 15,44% (o gross era maior).
   Na base maçã-com-maçã (após imposto) a vantagem do RSC **aumenta**
   `[testing_tuning, p.327-335]`.
3. **Por que o LRS "não faz sentido":** obtém-se **melhor retorno ajustado a
   risco, com muito menos drawdown e quase nenhum atrito fiscal/operacional, de um
   portfólio ESTÁTICO** return-stacked — sem timing. O timing alavancado adiciona
   giro, imposto, drawdown e path-dependence, e o edge **não sobrevive ao
   walk-forward**.

### Caveats honestos (não é maçã-com-maçã)

- **Janelas diferentes:** RSC 1988+ (38a), LRS SPY 1968+ (58a), QQQ 1986+ (40a).
  O ranking de CAGR é embaçado por janela e base fiscal. **Mas o domínio do RSC em
  drawdown/Sharpe/Calmar é estrutural, não artefato de janela.**
- **Ambas usam séries sintéticas em parte** (RSC reconstrói GDE/RSST pré-ETF; LRS
  usa SSOSIM/UPROSIM/QLDSIM/TQQQSIM) e **ambas são research-only**.
- **Diferença de status de validação:** o LRS **passou** pela suíte de 7 gates e
  **reprovou**; o RSC **ainda não foi submetido** à suíte completa.

---

## 7. Veredito

A linha **LRS standalone está encerrada/arquivada** como research-only de viés
negativo: a geometria de exposição é o único driver real, nenhum refinamento
(filtro/forma/janela/adaptativo) a melhora, e a base não clareia os gates do
mandate (vinculante: robustez temporal / walk-forward; QQQ também PBO/DSR).

O **RSC-US 35/40/25 continua sendo a âncora limpa** nas dimensões principais:
risco-ajustado, drawdown, eficiência fiscal, simplicidade operacional,
diversificação e tese. Isso continua impedindo promover LRS como substituto do
RSC.

**Nuance adicionada pela Phase 5 revisada:** com RSC-US reconstruído por sleeves
`GDESIM/RSSTSIM/ZROZSIM` e `RSSTSIM = SPYSIM + 70% DBMFSIM + 30% KMLMSIM -
(CASHX + 200 bps/ano)`, nenhum overlay passa o screen estrito (`0/9`). Maior CAGR
de overlay: `70% RSC / 30% T3d-K2`, CAGR `14,24%`, MDD `-48,65%`, Calmar `0,293`
vs RSC reconstruído CAGR `12,40%`, MDD `-30,76%`, Calmar `0,403`.

**Top-20 independente de drawdown:** `lrs/TOP20_BY_CAGR.md` ranqueia 4.183 rows
por CAGR desc, sem filtro de MDD. O top é `QQQ L3.00 / ZROZ / RV63<=40% / lag5`,
CAGR `25,84%`, MDD `-71,05%`, Sharpe `0,707`, Calmar `0,364`. Isso responde ao
pedido de ver retorno bruto antes da escolha manual, mas não é promoção.

Essa nuance **não é promoção**. A Phase 5 reconstrói RSC-US por uma matriz local de
sleeves, mas `RSSTSIM` é proxy de tracking, começa em 2000 por depender de
`DBMFSIM`, e o teste ainda mistura RSC gross/static com satélites LRS after-tax.
Próximo passo honesto, se houver continuação: o usuário escolhe uma row/lead,
pre-registramos a próxima fase, modelamos tax/friction account-level e só então
aplicamos gates do mandate com `n_trials` honesto incluindo toda a linhagem LRS
`[testing_tuning, p.327-335]`, `[systematic_trading, p.185-188]`, `[risk_parity,
p.80-81]`, `[advances_fin_ml, p.208-211]`.

---

## 7.1 Adendo — Rodada Phase 6 (2026-06-09): fronteira after-tax muda a leitura do mix

A rodada 6C/6B/6D/6A (pré-registrada, research-only) respondeu a pergunta que a
Phase 5 não respondia: **"existe mix static×satélite que compense ceder parte do
100% static, com MDD ≤ −50%?"** — contra 3 benchmarks, com modelo fiscal
corrigido pelo usuário: o core static rebalanceia **via aportes** (sem DARF
intermediário; 15% só na liquidação final), enquanto o satélite LRS mantém o
engine DARF anual porque o giro semanal vende de verdade.

- **6C (forense WF, +0 trials):** as falhas do gate vinculante são 90,9% em
  janelas bull; `bear_high` tem beat rate 100% (+154pp médio) e `bear_mid` 0%
  (whipsaw alavancado). O edge é de crise profunda — coerente com satélite
  pequeno, não standalone `[leverage_for_the_long_run, p.7-8]`.
- **6B (vol-targeting contínuo, +72):** SPY FAIL; QQQ SUCCESS diagnóstico
  (σ40%/RV21/lag1: WF 7/11 vs 6/11) `[systematic_trading, p.137-148]`.
- **6D (sleeve inversa capada, +36):** FAIL nas duas branches — todo `f` piora
  CAGR e MDD `[trading_systems_methods, p.354]`.
- **6A (fronteira after-tax, +21 → linhagem 4005; REVISADA):** na janela 2000+,
  o RSC after-tax é `11,74% / −30,76% / Calmar 0,382` (12,40% gross; só DARF de
  liquidação final). Mesmo assim, **13/18 mixes batem o RSC em CAGR E Calmar
  reduzindo MDD**: top Calmar `80/20 RSC×SPY-headline` (`12,12%`, `−25,18%`,
  `0,481`); maior CAGR unified `70/30 RSC×QQQ-voltarget` (`12,83%`, `−27,67%`).
- **6A Part 2 (simulação de aportes, +0 trials):** 10k + 1k/mês, comprando só o
  componente mais abaixo do target (mínimo de ordens, à la IBKR), sem vendas.
  **Todos os 18 mixes batem 100% RSC em IRR money-weighted** (RSC `13,72%`,
  terminal $2,96M em $326k aportados). Destaque: `70/30 RSC×QQQ-voltarget` IRR
  `15,21%` ($3,87M) com path MDD `−28,4%` ≈ RSC (`−27,6%`). `mix_t3d_30` topa
  IRR (`17,66%`, $6,0M) mas path MDD `−50,3%`; SSO B&H tem IRR alto (`15,81%`)
  inflado pelo DCA, com path MDD `−80,8%` (ruin) `[systematic_trading,
  p.185-188]`.

**Leitura honesta:** a conclusão da seção 7 ("RSC domina sem ambiguidade") era
verdadeira para **substituição total** — e continua. O que muda é a margem: para
**mixes pequenos (5–30%)**, a diversificação do satélite melhora o portfolio nas
três métricas ao mesmo tempo (time-weighted) e em IRR no cenário real de aportes
— o que reabre a decisão do usuário sobre ceder parte da posição static. Isso
**não é promoção**: os satélites individualmente reprovaram (ou nunca rodaram)
os gates; qualquer claim exige a suíte completa do mandate sobre o MIX escolhido
com `n_trials >= 4005` `[advances_fin_ml, p.208-211]`, `[advances_fin_ml,
p.273-275]`. Tabela de decisão: `lrs/phases/phase06a_aftertax_frontier/REPORT.md`.

---

## 7.2 Adendo — Rodada Phase 7 (2026-06-09): atacando o gate vinculante (WF)

A rodada 7A→7B→7C→7D→7E→7F (pré-registrada, research-only, ledger 4005→**4377**)
atacou diretamente o gate que reprovou tudo até aqui — o walk-forward — com seis
famílias de mecanismo, uma por fase, critério pré-registrado = WF beats vs
controle pareado:

| Fase | Mecanismo | Veredito | Número-chave |
|---|---|---|---|
| 7A | Ensemble multi-lookback fracionário `[systematic_trading, p.118-133]` | **SPY SUCCESS** | WF **13/17 (76,5%)** vs 12/17 — primeira linha do restart no nível do G3; CAGR 14,49%, MDD −43,16% |
| 7B | Portfólio EW de rotações (SPY/QQQ/IWM/XLK/GLD) | FAIL 0/3 | EW5 WF 9/11, mas empata a melhor leg ex-post; MDD −53% |
| 7C | Macro gate GTT/UNRATE (exceção de citação aprovada) | FAIL 0/2 (MDD) | Maior lift de WF do restart: SPY 14/17, QQQ **10/11**; zero rows com MDD ≥ −50% |
| 7D | Vol-targeting quadrático σ²/RV² `[volatility_trading, p.135-140]` | **QQQ SUCCESS** | WF 8/11 vs 7/11; CAGR 19,53% > headline; MDD −42,63% |
| 7E | Risk-off managed futures (DBMF/KMLM, 2000+, low-power) | SPY weak SUCCESS | 100% DBMF: WF 5/6, MDD −31,6% vs −39,3% (6 janelas) |
| 7F | Composição 7A×7D (parâmetros congelados) | FAIL 0/2 | Mecanismos não se somam (SPY 12/17, QQQ 6/11) |

**Leitura honesta:** (1) o custo de timing em janelas bull É tratável — o gate
macro 7C praticamente zera as falhas de WF, mas devolve exatamente o drawdown
que a SMA200 protegia; o trade-off WF×MDD é estrutural nesta família. (2) Os
ganhos sustentáveis vieram de mecanismos *suaves*: média de janelas (7A) e
sizing contínuo por variância (7D) — e eles **não** se compõem (7F). (3) O
nível nominal do G3 foi alcançado em SPY pela primeira vez (13/17 = 76,5% ≥
75%), mas isso NÃO é gate pass: a Phase 8 exigiria a suíte completa
(PBO/DSR/WF/OOS/FWD/bootstrap/xlib) com `n_trials = 4377` sobre ≤2 configs
escolhidas pelo usuário. QQQ a 8/11 falharia o G3 como está. Nada validado,
nada promovido; mandate §1 inalterado `[advances_fin_ml, p.208-211]`,
`[advances_fin_ml, p.273-275]`.

---

## 7.3 Adendo — Phase 8 (2026-06-10): suíte completa nos sobreviventes; linha RE-FECHADA

O usuário escolheu validar os dois sobreviventes naturais da rodada 7. Suíte
SS5 completa, `n_trials = 4377`, PBO matrix = grid da família por branch,
+0 trials:

| Config | G1 PBO | G2 DSR p | G3 WF | G4-G7 | **Geral** |
|---|---|---|---|---|---|
| `spy_7a_ensemble` (7A, narrow/lag2) | 0,397 ✅ | **0,052 ❌** | **13/17 ✅** | ✅✅✅✅ | **FAIL 6/7** |
| `qqq_7d_quadratic` (7D, σ40/RV21/lag2) | 0,651 ❌ | 0,138 ❌ | 8/11 ❌ | ✅✅✅✅ | **FAIL 4/7** |

**Leitura final da linha:** a rodada 7 conseguiu o que nenhuma fase anterior
conseguiu — o gate vinculante (walk-forward) **passou** no SPY pela primeira
vez. Mas o Sharpe não sobrevive à deflação contra a busca de 4.377 trials que
o produziu (p 0,052 vs 0,05; com o letf-lab excluído do ledger, o p honesto é
ainda maior). Pela regra pré-registrada e pelo mandate ("quase lá" não passa):
sem re-runs, sem ajuste de threshold, ambos re-fechados. O veredito honesto da
linha inteira: **a geometria de timing é real, mas o edge é pequeno demais
para sobreviver ao accounting honesto de múltiplos testes**
`[advances_fin_ml, p.273-275]`, `[advances_fin_ml, p.208-211]`. O RSC-US
estático segue como âncora limpa (seção 7), e a tabela de decisão da 6A
continua disponível para a discussão de mix — fora do escopo desta linha.

---

## 7.4 Adendo — Phase 11 (2026-06-12): suíte completa no mix 6A escolhido

O próximo lead natural da 6A era `mix_lrs_spy_headline_20`: `80%` RSC after-tax
+ `20%` `lrs_spy_headline`. A linha reproduziu o ganho local contra `bench_rsc`
(`12,12%` CAGR, MDD `−25,18%`, Calmar `0,481` vs RSC `11,74%`, `−30,76%`,
`0,382`), mas a suíte formal falhou:

| Config | G1 PBO | G2 DSR p | G3 WF | G4-G7 | **Geral** |
|---|---|---|---|---|---|
| `mix_lrs_spy_headline_20` | 0,933 ❌ | 0,306 ❌ | 6/10 ❌ | ✅✅✅✅ | **FAIL 4/7** |

Pré-registro: +0 trials, `n_trials = 4569`, PBO = todos os 18 mixes Phase 6A,
WF `5y/2y` para preservar `>=8` janelas na janela 2000+. Diagnósticos extras:
DSR stress incluindo os trials raw do RSC evolution = p `0,582`; WF 7y/3y
low-power = `5/6`. Relatório: `lrs/phases/phase11_mix_final_gates/REPORT.md`.

**Leitura:** a fronteira 6A gerou uma melhoria local útil como diagnóstico, mas
o lead não sobrevive a PBO/DSR/WF. A tabela de mix fica arquivada; nada é
promovido e o mandate §1 permanece inalterado `[advances_fin_ml, p.208-211]`,
`[advances_fin_ml, p.273-275]`, `[testing_tuning, p.318-320]`.

---

## 8. Referências

- `lrs/phases/phase0{0,1}_*`, `phase02_target_leverage_vol`,
  `phase03_sparse_risk_on_vote`, `phase03b_regime_signals`,
  `phase03c_lookback_study`, `phase04_validation_gates`,
  `phase05_rsc_overlay_proxy`, `phase11_mix_final_gates` (REPORT.md + results CSV).
- `lrs/SPEC.md`, `lrs/MEMORY.md`, `lrs/NEXT_STEPS.md`.
- `studies/return_stacked_core/us_core/REPORT.md`,
  `studies/return_stacked_core/README.md`.
- Citações: `[leverage_for_the_long_run, p.4-7, p.13]`, `[systematic_trading,
  p.137-148, p.283]`, `[volatility_trading, p.39, p.53-54]`,
  `[trading_systems_methods, p.939]`, `[risk_parity, p.80-81]`,
  `[testing_tuning, p.318-320, p.327-335]`, `[advances_fin_ml, p.208-211,
  p.273-275]`.

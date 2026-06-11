# Estado atual — market-lab (2026-06-11)

> **Propósito:** onboard rápido para humanos e agentes. Este doc é o
> snapshot vivo — a verdade canônica vive nos arquivos referenciados.

---

## TL;DR (2026-06-11)

🛑 **MAINTENANCE MODE** desde 2026-04-23 (mandate §1, §7).

- **Capital:** 100% **Plano C** passivo factor-tilted. Documentação pessoal movida para `victor-ia/verticals/investments/`.
- **Strategies A/B/D:** **DORMANT** (0% capital, infra retida).
- **113/113 honest FAIL** acumulado entre 2026-04-08 e 2026-04-23 (Phase 3.5f-3.8 + D-MVP + E-MVP). Pattern previsto por López de Prado DSR + Aronson 6402-rule + Li-Ferreira 2025 Network Momentum.
- **Sem hunt ativo de alocação;** estudos remanescentes são research-only e a revisão consolidada do mandato fica para 6-12 meses.
- **LETF rotation spin-off concluído:** `studies/lrs/`, `studies/letf_rotation_hunt/` e `studies/spy_leveraged_rotation_hunt/` agora são canônicos em `/var/www/victor/finances/letf-lab`. `market-lab` mantém apenas infra compartilhada, referências históricas e estudos não migrados. Ver `MIGRATED.md`.
- **Restart research-only em `lrs/` — standalone CONCLUÍDO (Phase 4) + overlay rebuilt-sleeve (Phase 5):** linha SMA/LRS reaberta localmente (Gayed do zero, execução semanal, lag `n=0..5`, DARF anual, risk-off, filtros, formas de regime, estudo de lookback) e levada até os gates de validação do mandate. **0/6 bases standalone passaram** (gate vinculante = walk-forward; QQQ também PBO/DSR). Phase 5 reconstruiu RSC-US `35/40/25` via matriz local `GDESIM/RSSTSIM/ZROZSIM` com RSST tracking proxy `SPYSIM + 70% DBMFSIM + 30% KMLMSIM - CASHX?E=-2`; `0/9` overlays passaram screen estrito. Um Top-20 CAGR bruto independente de drawdown foi gerado em `lrs/TOP20_BY_CAGR.md`. Sem deploy e mandate §1 inalterado.
- **RSC four-asset grid corrigido:** `studies/return_stacked_core/us_core/four_asset_grid/` baixou payload Testfol.io com `NTSXSIM/GDESIM/ZROZSIM` e `RSST70_30 = SPYSIM + 70% DBMFSIM + 30% KMLMSIM - CASHX?E=-2` (`CASHX?E=2` anterior invalidado por erro de sinal), depois avaliou `1.771` portfolios mensais em passos de `5%`. Top por fitness rank-based: `40% GDESIM / 25% RSST70_30 / 35% ZROZSIM`, CAGR `12,15%`, MDD `-27,80%`, Sharpe `0,851`, Calmar `0,437`. É screen research-only; não é promoção nem gate validado.
- **WF anti-overfit do grid RSC:** `WF_REPORT.md` usa `8y` IS -> `2y` OOS, rolando `2y`, com os mesmos `1.771` portfolios. A seleção WF combinada ficou CAGR `12,57%`, MDD `-34,47%`, Sharpe `0,821`, terminal `8,37x`, mas bateu o RSC-like fixo `35/40/25` em só `3/9` janelas (requisito `7/9`). `9/9` seleções foram únicas; Spearman médio IS->OOS `0,144`. Veredito: full-sample top é overfit-prone; manter como diagnóstico, não como proporção promovida.
- **Robustez CPCV/PBO do grid RSC:** `ROBUSTNESS_REPORT.md` roda WF sensitivity, top-decile stability e CPCV/PBO. PBO do grid completo = `0,655` (`reject`); CPCV bate RSC-like em só `7/28` splits (requisito `21/28`); Spearman médio CPCV IS->OOS `0,031`; nenhuma sensibilidade WF atingiu 75% de consistência. Entre regras fixas testadas no OOS default, `35/40/25` foi a melhor por terminal/CAGR (`12,63%`, MDD `-30,76%`). Conclusão: não otimizar pesos; usar tese fixa se for seguir.
- **Margin overlay IBKR corrigido:** sobre o novo top four-asset, sweep `CASHX?E=-2` mostra `1,25x` CAGR `13,97%`/MDD `-34,14%`, `1,50x` CAGR `15,66%`/MDD `-40,18%`, `2,00x` CAGR `18,69%`/MDD `-51,98%` e `3,00x` CAGR `23,13%`/MDD `-71,40%`. Leitura: a correção removeu o headline atrativo; se retomado, pesquisar só `1,10x..1,25x` com requisitos reais de margem/financing/liquidação/tax.
- **KMLM-only MF proxy corrigido:** trocar o sleeve MF por `100% KMLMSIM` com `CASHX?E=-2` estende a janela para `1987-2026`: 1x CAGR `13,00%`, MDD `-26,70%`; `1,25x` CAGR `14,73%`, MDD `-33,01%`; `1,50x` CAGR `16,35%`, MDD `-38,92%`. Leitura: útil como lente de janela longa, mas NÃO muda a conclusão conservadora contra margem externa.
- **Cleanup consolidation iniciado:** `studies/SUMMARY.md` agora é o ledger compacto de estratégias testadas, métricas, vereditos, arquivos canônicos e política de remoção de artefatos gerados. O objetivo é reduzir a codebase sem perda de conhecimento; mandate §1 segue inalterado.
- **Rodada Phase 7 do `lrs/` (2026-06-09) concluída:** 6 fases pré-registradas (7A ensemble multi-lookback, 7B portfólio multi-asset EW, 7C macro gate GTT/UNRATE, 7D vol-targeting quadrático, 7E risk-off managed futures, 7F composição), ledger de trials 4005 → **4377**. Sobreviventes: **7A-SPY** (ensemble `{150..225}`, WF **13/17 = 76,5%**, primeira linha do restart no nível do gate G3) e **7D-QQQ** (σ²/RV² σ40/RV21, WF 8/11, CAGR 19,53% > headline). 7C entregou o maior lift de WF já visto (SPY 14/17, QQQ 10/11) mas nenhuma row segura MDD ≥ −50%; 7F provou que os mecanismos não se somam. Research-only; mandate §1 inalterado.
- **Phase 8 do `lrs/` (2026-06-10): FAIL 0/2 — linha RE-FECHADA.** Suíte SS5 completa (`n_trials = 4377`, PBO matrix = grid da família por branch, +0 trials) sobre os dois sobreviventes escolhidos pelo usuário. `spy_7a_ensemble` faz **6/7**: o walk-forward (gate vinculante histórico) **passa pela primeira vez** (13/17), mas o DSR falha em p `0,052` vs `0,05` — e como o ledger exclui o letf-lab, o p honesto é maior. `qqq_7d_quadratic` faz 4/7 (PBO 0,651, DSR p 0,138, WF 8/11). Regra pré-registrada aplicada: sem re-runs nem ajuste de threshold, ambos re-fechados. Veredito da linha: a geometria de timing é real, mas o edge não sobrevive ao accounting honesto de múltiplos testes. Mandate §1 inalterado.
- **Estudo `lrs/` ENCERRADO (2026-06-10) com relatório consolidado:** `lrs/REPORT.md` (gerado por `lrs/final_report.py`) + 10 plots em `lrs/plots/` — veredito, status de validação (Phase 8 FAIL 0/2), 3 finalistas research-only nas lentes time-weighted e de aportes (F1 ensemble 14,5%/IRR 15,1%; F2 cap-2.5x 16,8%/IRR 17,6%; F3 QQQ-L2 21,1%/IRR 21,1%), fichas operacionais e linha do tempo do ledger (4569). Nada promovido; mandate §1 inalterado.
- **Phase 10 do `lrs/` (2026-06-10, user-directed, ledger 4425 → 4569): FAIL 0/2 — o negativo mais limpo do restart.** Família contrária "buy the dip" (L_base normal, escala para L_dip quando o DD do underlying cruza −10/−20/−30%, desescala na recuperação): **zero rows entre 144 seguram MDD ≥ −50%** (faixa −69,8% a −102,7%; 8 configs = ruína total). O CAGR também não paga (melhor SPY 12,65% vs headline 15,44%; maioria das rows QQQ perde do B&H sem alavancagem). O trigger escala cedo em todo bear longo (1929-32, 2000-02) e cavalga alavancagem máxima até o fundo. A tese Gayed sobrevive ao teste da sua inversão direta: dip = regime de alta vol = alavancagem deve ser BAIXA. Nuance preservada: dip-buying funciona no repo só como fluxo de aportes (6A Part 2), não como escalada de leverage sobre capital existente. Mandate §1 inalterado.
- **Phase 9 do `lrs/` (2026-06-10, user-directed return-first, ledger 4377 → 4425):** teto da família 7D elevado para 2.5x/3.0x (degraus UPRO/TQQQ). **SPY SUCCESS no screen return-first:** `L_max 2.50 / σ40 / RV21 / lag 3` = CAGR 16,81% (+1,4pp), MDD −47,47%, WF 12/17 mantido. **QQQ FAIL: zero rows dentro do teto −50%** (melhor: 24,7% / −61,8%) — QQQ acima de ~2x efetivo é ruin-adjacent em toda variação testada. Leitura mecânica honesta: com σ40-45 o escalar fica pinado no cap ~99% dos dias — o ganho vem da alavancagem, não do sizing (empata com a row binária L2.50 da Phase 2). Diagnóstico return-first, sem promoção; odds de validação SS5 registradas como baixas (DSR já matou candidato mais forte). Mandate §1 inalterado.

- **RSC evolution hunt (2026-06-11, user-directed, 8 rodadas pré-registradas): FAIL honesto TERMINAL — nada passa todos os gates; candidato único morto pela bateria profunda.** `studies/return_stacked_core/evolution/` — hunt por CAGR maior que o CORE `35/40/25` mantendo MDD ≤ 30%; PLAN.md pré-registrado, emendas antes de cada rodada, zero ajuste de threshold pós-resultado. R1-R3: 95.601 trials estáticos (74.193 únicos; sleeves novos RSBT/RSSB/GLD/KMLM/QQQ + carriers SSO/UPRO **dominados**) → 0 finalistas, todo ganho in-cap é artefato da década do ouro (todos perdem do CORE-1988). R4: frequência de calendário = sorte de offset; **bandas de tolerância = platô de parâmetro real**. R5-R7: simplexes 3/4/5-ativos × bandas + lastro IEF/CASHX (~132k configs) → **G1∩G2 = ∅ em todo o espaço**; candidato máximo ÚNICO = `45/25/30 + banda 20%` (5/6 gates: 13,39%/−29,52%, G1 7/8, G4 73%, 1988+ empata CORE com MDD 3,2pp mais raso, turnover 1,44/ano; falha G2: vizinhos ZROZ ≤ 25% furam −32% — **ZROZ ≥ 30% é fronteira dura sob bandas**). R8 bateria profunda no candidato único: **2/4 — FAIL terminal**: B1 ✓ (bate CORE em 61/68 starts trimestrais), B4 ✓ (cadência semanal), mas B2 ✗ (contínuo de bandas: cap raspado por 5-25bps nas bandas 12-18%; CAGR > CORE em todas as 21) e **B3 ✗ decisivo** (bootstrap conjunto de blocos 63d: spread > 0 em só 83,8% dos paths, vantagem de MDD vira moeda — o edge da banda é colheita da estrutura de tendência multi-mês da sequência histórica específica, não propriedade distribucional). Squeeze provado: cap × vizinhança × starts não tem solução conjunta — o platô do CORE já está precificado. Resíduo: EW 33/33/33 b50 = standout drawdown-first (12,94%/−24,7% e 14,24%/−24,7% em 1988+, G1 2/8); RSBT = diversificador de implementação (tier CTAP); rebalance anual = knob de MDD em 2000+ mas não em 1988+. Research-only; mandate §1 inalterado.
- **RSC discussion — suite GLOBAL (2026-06-11, benchmark VT) concluída:** pipeline g00→g07 em `studies/return_stacked_core/discussion/` (gate: VT reproduz exato a curva salva; composição do canônico global corr 1.0000, delta de financiamento −0,60pp/ano documentado). Scan de 10.626 nós no simplex {GDE,NTSD,RSST,RSIT,ZROZ}: **o ótimo irrestrito é US-only em todas as janelas e o CORE-GLOBAL 20/15/20/20/25 fica FORA do platô de Sharpe (0/8 datas de início)**; curva de preço da globalness ≈ −0,01 Sharpe por +5pp de mangas internacionais; equity internacional não é diversificador de crise (corr mensal SPY~VXUS 0,854; nos piores meses do VT, VEA/VXUS/VWO caem MAIS que o VT). Regras de desenho se for global: 10-20% intl via RSIT primeiro (−2% em 2022) e NTSD por último (−74% no GFC), ZROZ 25-30%, nunca RSSB no lugar de ZROZ. Contrapeso honesto: na janela 1970+ o half-intl (27.5/7.5/30/10/25) empata o Sharpe de 56 anos do US core. Verdict em 3 tiers em `discussion/REPORT_GLOBAL.md`; todos os tiers esmagam o VT (+3,6 a +5,3pp CAGR, MDD 21-28pp mais raso). Add-on g08 (ratio fixo 60/40 e 66/34 US/intl, banda ±2,5pp sobre o grid): os tops in-band concordam em NTSD=0, intl 100% via RSIT e ZROZ 30-35; expressão recomendada 66/34 = **30 GDE / 15 RSST / 20 RSIT / 35 ZROZ** (4 fundos; bate o CORE-GLOBAL em CAGR/MDD/Sharpe nas duas janelas modernas com a mesma geografia), 60/40 = 30/10/25/35; alternativa MF-heavy para quem pesa estagflação: 20/5/25/20/30 (REPORT_GLOBAL §6). Research-only; mandate §1 inalterado.
- **RSC discussion package (2026-06-11) concluído:** `studies/return_stacked_core/discussion/` — pipeline determinístico (s00 anchor gate → s07 figures) com análise de regimes (15 episódios 1970-2026), descorrelação condicional (piores meses do SPY: GLD +1,8%/MF +2,4%/ZROZ +3,8% ao mês), scan completo do simplex GDE/RSST/ZROZ (231 nós: platô contíguo de 60 nós ≥95% do Sharpe máximo; `35/40/25` dentro do platô em 8/8 datas de início — "o argmax anda, o platô não"), ablations (sem-ZROZ, NTSX swap, SSO/UPRO, HFEA −69% MDD vs CORE −31%, RSSX BTC-driven, RSSY carry proxy AQR reduz Sharpe) e 3 posts Reddit prontos (master + r/ETFs + r/LETFs) com 12 figuras. Caveat #1 documentado: sensibilidade ao proxy de MF (GFC −23,1% no tracking proxy vs −13,8% na curva 1988 antiga). Research-only; mandate §1 inalterado.

Ver `docs/investment-mandate.md` para regras canônicas, e `docs/CLEANUP_2026-04-24_LOG.md` + `docs/CLEANUP_2026-05-05_LOG.md` para audit trail dos cleanups.

---

## Status por linha de pesquisa (2026-06-09)

### Plano C — buy-hold passivo factor-tilted ✅ ATIVO
- **Status:** sole winner. 100% do capital. Zero alterações.
- **Refs:** documentação pessoal fora do repo público, em `victor-ia/verticals/investments/`.
- **Mandate §:** §1, §4.7

### Plano A (Pepperstone CFD short-hold) 🛑 DORMANT
- **Status:** V2 encerrado 2026-04-23 (6 leads honest re-validation FAIL após engine fix `7b90a8f`).
- **Reativação exige (mandate §3):** multi-asset (SPY/QQQ/Gold/BTC/ETH/FX), sweep alavancagem 1:1→1:200 × Kelly f/2, staging USD 500-1k → cap 5-10k. Single-asset edge não aceito.

### Plano B (Inter swing US LETF rotation) 🛑 DORMANT
- **Status:** Phase 3.5b/3.5c canonical preserved; Phase 3.5e c06-c12 pausado em 26%; Phase 3.8-1 hunt FAIL 5/5.
- **Reativação exige (mandate §4):** Inter Internacional, tese Gayed-anchored única fonte, CPCV+PBO+splits-mutex+bootstrap 0.001+15% DARF.

### Plano D (BR ranking mensal IBrX) 🛑 DORMANT
- **Status:** Phase E-MVP (2026-04-23) failed catastroficamente (PBO 0.786).
- **Reativação exige (mandate §4b):** literatura/regime novos. Specs novas devem viver em `docs/specs/`.

---

## Linhas exploratórias locais (2026-06-09)

### lrs/ 🔴 LINHA RE-FECHADA após Phase 8 (2026-06-10) — FAIL 0/2 na suíte completa (research-only)
- **Conclusão atual (2026-06-10, Phase 8 = suíte final SS5 nos 2 sobreviventes):**
  usuário escolheu validar `spy_7a_ensemble` (7A: `spy_alt_off / narrow
  {150,175,200,225} / lag 2`) e `qqq_7d_quadratic` (7D: `σ40%/RV21/lag2`).
  Suíte completa com `n_trials = 4377`, PBO matrix = grid da família por
  branch (36 configs cada), +0 trials, sanity ~1e-17 vs CSVs da Phase 7.
  **Resultado: 0/2 passam.** `spy_7a_ensemble` = **6/7**: G3 walk-forward
  (gate vinculante desde a Phase 4) **PASSA pela primeira vez** (13/17), G1
  PBO 0,397 ✅, G4-G7 ✅, mas **G2 DSR p = 0,052 vs 0,05 ❌** — margem de
  0,002 com undercount honesto (letf-lab fora do ledger ⇒ p verdadeiro
  maior). `qqq_7d_quadratic` = 4/7 (PBO 0,651 ❌, DSR p 0,138 ❌, WF 8/11 ❌ —
  o prior registrado). Regra pré-registrada: sem re-runs, sem ajuste de
  threshold, ambos re-fechados. Veredito da linha inteira: timing geometry é
  real (o WF foi destravado), mas o edge é pequeno demais para sobreviver à
  deflação por múltiplos testes `[advances_fin_ml, p.273-275]`. Mandate §1
  inalterado.
- **Conclusão anterior (2026-06-09, rodada Phase 7 = 7A→7B→7C→7D→7E→7F; ledger 4005→4377):**
  rodada pré-registrada para atacar o gate vinculante (G3 walk-forward) com 6
  famílias de mecanismo, uma por fase. Vereditos: **7A ensemble multi-lookback
  fracionário = SPY SUCCESS** (`spy_alt_off / narrow {150,175,200,225} / lag 2`:
  WF **13/17 = 76,5%** vs 12/17 — primeira linha do restart a alcançar o nível
  do G3; CAGR 14,49%, MDD −43,16%); **7B portfólio EW de rotações = FAIL 0/3**
  (EW5 WF 9/11 mas empata a melhor leg ex-post e MDD −53%); **7C macro gate
  GTT/UNRATE = FAIL 0/2 por MDD** (maior lift de WF do restart: SPY 14/17, QQQ
  10/11, CAGR acima do headline — mas zero rows seguram MDD ≥ −50%; exceção de
  citação aprovada pelo usuário, lag de publicação honesto 25 td, caveat
  vintage); **7D vol-targeting quadrático σ²/RV² = QQQ SUCCESS** (σ40/RV21/lag2:
  WF 8/11 vs 7/11, CAGR 19,53% > headline, MDD −42,63%); **7E risk-off managed
  futures = SPY weak SUCCESS low-power** (100% DBMF: WF 5/6, MDD −31,6% vs
  −39,3%, só 6 janelas 2000+); **7F composição 7A×7D = FAIL 0/2** (mecanismos
  não se somam). Próximo passo honesto = Phase 8: usuário escolhe ≤2 configs
  (candidatos naturais: 7A-SPY e 7D-QQQ) e roda a suíte completa SS5 com
  `n_trials = 4377`. QQQ a 8/11 falharia o G3 como está; SPY a 13/17 passa o G3
  nominalmente mas precisa sobreviver aos outros 6 gates. Nada validado, nada
  promovido; mandate §1 inalterado.
- **Conclusão anterior (2026-06-09, rodada Phase 6 = 6C→6B→6D→6A, 6A revisada):**
  responde a pergunta do usuário "vale ceder parte de um portfolio 100% static?"
  na janela 2000+, benchmarks RSC-US 35/40/25, SSO B&H e SPY B&H. Modelo fiscal
  corrigido pelo usuário: core static rebalanceia **via aportes** → sem DARF
  intermediário, 15% só na liquidação final; satélites LRS mantêm DARF anual
  (giro semanal vende). **6C** (forense WF, +0 trials): falhas do gate
  vinculante são 90,9% bull; `bear_high` beat 100%, `bear_mid` 0% — edge de
  crise profunda. **6B** (vol-targeting contínuo, +72): SPY FAIL, QQQ SUCCESS
  diagnóstico (σ40%/RV21/lag1, WF 7/11 vs 6/11). **6D** (sleeve inversa capada,
  +36): FAIL nas duas branches. **6A** (fronteira, +21 → linhagem n_trials
  4005): RSC after-tax `11,74% / −30,76% / Calmar 0,382`; **13/18 mixes batem o
  RSC em CAGR E Calmar reduzindo MDD** — top Calmar `80/20 RSC×SPY-headline`
  (`12,12%`, `−25,18%`, `0,481`); maior CAGR unified `70/30 RSC×QQQ-voltarget`
  (`12,83%`, `−27,67%`). **6A Part 2** (aportes 10k + 1k/mês, compra só o
  componente mais abaixo do target, sem vendas): **todos os 18 mixes batem 100%
  RSC em IRR** (RSC 13,72%; `70/30 RSC×QQQ-voltarget` 15,21% com path MDD ≈
  RSC; T3d 30% topa 17,66% mas path MDD −50,3%; SSO B&H IRR 15,81% com path MDD
  −80,8% ruin). É tabela de decisão, não promoção: o mix escolhido ainda
  precisaria da suíte completa de gates com `n_trials >= 4005`. Mandate §1
  inalterado.
- **Conclusão anterior (2026-06-08/09, Phase 5):** LRS standalone continua encerrado
  após Phase 4 (**0/6 bases passaram** nos 7 gates; gate vinculante = WF), mas a
  Phase 5 agora reconstrói RSC-US `35/40/25` a partir da matriz local de sleeves
  `GDESIM/RSSTSIM/ZROZSIM`, com `RSSTSIM = SPYSIM + 70% DBMFSIM + 30% KMLMSIM -
  (CASHX + 200 bps/ano)` como tracking proxy do cURL Testfol.io. Com essa fórmula,
  `0/9` overlays passam o screen estrito; o maior CAGR de overlay é `70% RSC / 30%
  T3d-K2`, CAGR `14,24%`, MDD `-48,65%`, vs RSC reconstruído `12,40%`, MDD
  `-30,76%`. Também foi gerado `lrs/TOP20_BY_CAGR.md`: top row `QQQ L3.00 / ZROZ /
  RV63<=40% / lag5`, CAGR `25,84%`, MDD `-71,05%`. Isso não é promoção: falta
  tax/friction account-level e gates de mandato. Mandate §1 inalterado.
- Criado em 2026-06-07 como restart local da família Gayed/LRS, apesar do
  spin-off LETF canônico para `letf-lab`. Objetivo: recomeçar pelo baseline
  original `price > SMA200 => leveraged risk-on; otherwise risk-off` e evoluir
  com execução semanal, lag operacional `n=0..5`, modelo DARF anual, risk-off
  alternativo, filtros risk-on esparsos e sleeve bear-market com inverse ETFs.
- Phase 0 em `lrs/phases/phase00_gayed_baseline/`: 24 linhas avaliadas
  (`SPY_2x`, `SPY_3x`, `QQQ_2x`, `QQQ_3x` x `n=0..5`) usando
  `risk-off=CASHX`. Top score: `SPY_3x` lag `2`, after-tax CAGR `16,91%`, MDD
  `-88,33%`, Calmar `0,191`, terminal `8798,16x` vs SPY after-tax. Melhor QQQ:
  `QQQ_3x` lag `0`, after-tax CAGR `21,34%`, MDD `-91,97%`, terminal `10,95x`
  vs QQQ after-tax. Leitura: baseline confirma retorno, mas drawdown segue em
  território de ruin; Phase 1 deve priorizar risk-off antes de indicadores.
  Overfit gates são diagnósticos para evolução, não stop-rule desta linha; sem
  deploy e mandate §1 inalterado `[leverage_for_the_long_run, p.13]`,
  `[leverage_for_the_long_run, p.4-7]`, `[advances_fin_ml, p.208-211]`.
- Phase 1 em `lrs/phases/phase01_risk_off/`: 264 linhas avaliadas (4 branches x
  11 risk-off sleeves x `n=0..5`) em janelas comuns por branch incluindo
  `GLDSIM`/`IEFSIM`/`ZROZSIM` (SPY começa `1968-04-02`, QQQ `1986-01-03`). Top
  score: `SPY_2x` com risk-off `40 ZROZ / 40 GLD / 20 IEF`, lag `5`, after-tax
  CAGR `15,23%`, MDD `-41,34%`, Calmar `0,368`, terminal `11,03x` vs SPY
  after-tax. `34` linhas bateram underlying after-tax com MDD `<=50%`, todas
  SPY 2x nesta superfície. SPY 3x segue warning (`-61,04%` MDD no melhor caso) e
  QQQ 2x/3x seguem em ruin territory. Próximo passo técnico: target leverage
  menor/volatility throttle/bear sleeve antes de votos multi-indicador amplos
  `[leverage_for_the_long_run, p.4-7]`, `[systematic_trading, p.137-148]`.
- Phase 2 em `lrs/phases/phase02_target_leverage_vol/`: 2.400 linhas avaliadas
  (SPY/QQQ x 8 target leverages x 5 risk-off sleeves x 5 filtros de volatilidade
  x `n=0..5`). Top score: `SPY` L`2,00`, risk-off
  `50 ZROZ / 25 GLD / 25 CASH`, `RV21 <= 30%`, lag `3`, after-tax CAGR
  `15,44%`, MDD `-39,28%`, Calmar `0,393`, terminal `12,28x` vs SPY after-tax
  (tier preferred). `875` linhas bateram underlying after-tax com MDD `<=50%` e
  `394` chegaram a MDD `<=40%`. Melhor QQQ: L`1,75`, risk-off
  `40 ZROZ / 40 GLD / 20 IEF`, `RV63 <= 40%`, lag `0`, after-tax CAGR `19,46%`,
  MDD `-42,58%`, Calmar `0,457`, terminal `5,82x` vs QQQ after-tax. Leitura:
  geometry de exposição resolveu parte relevante do drawdown antes de adicionar
  indicadores; próxima fase deve usar essa base para voto risk-on pequeno ou
  sleeve bear separado. Sem deploy e mandate §1 inalterado
  `[leverage_for_the_long_run, p.4-7]`, `[systematic_trading, p.137-148]`,
  `[advances_fin_ml, p.208-211]`.
- Phase 3A em `lrs/phases/phase03_sparse_risk_on_vote/`: 324 linhas avaliadas
  (SPY/QQQ x 3 bases por branch — top da Phase 2 + 2 vizinhos de 1 alavanca — x
  9 filtros = `none` controle + 4 famílias x 2 variantes x `n=0..5`). Cada linha
  faz AND de no máximo UM filtro de confirmação risk-on sobre o sinal base
  (`sma & vol_gate & confirm_gate`), comparado contra o controle `none`; sem
  vote-of-K. Scoring e `practical_pass` da Phase 2 mantidos verbatim. Resultado
  NEGATIVO: o top geral é o controle `none` (`SPY` `spy_top` L`2,00` lag `3`,
  after-tax CAGR `15,44%`, MDD `-39,28%` — reproduz a Phase 2 exatamente, sanity
  check passou). Nenhum filtro bate `none` em nenhuma branch; Clenow/ROC/ADX
  divergem mas reduzem CAGR (ADX é proxy close-only degradado, sem OHLC no cache,
  não super-interpretado). Insight estrutural: a banda de histerese SMA é
  IDÊNTICA a `none` em 36/36 configs — como AND-gate sobre `price > SMA200` só
  pode restringir mais, e seu comportamento distinto (segurar numa queda abaixo
  da SMA) vive nos dias em que a SMA já bloqueia; testá-la exige SUBSTITUIR o
  gate SMA, não fazer AND. Leitura: complexidade de filtro risk-on não se
  justifica — a geometria de exposição da Phase 2 é o driver real. Famílias e
  fontes: Clenow slope x R² `[stocks_on_the_move, p.70-77, p.98]`, ROC
  `[stocks_on_the_move, p.58, p.60]`, histerese `[trading_systems_methods,
  p.383]`, ADX `[trading_systems_methods, p.387]`. Bear sleeve (Phase 3B) segue
  BLOQUEADO: sem inverse tickers no cache. Sem deploy, sem paper-trade label,
  mandate §1 inalterado `[trading_systems_methods, p.939]`, `[advances_fin_ml,
  p.208-211]`.
- Phase 3A-2 em `lrs/phases/phase03b_regime_signals/`: 216 linhas avaliadas
  (SPY/QQQ x 3 bases por branch x 6 formas de regime x lag `0..5`). Diferente da
  3A, cada forma SUBSTITUI o gate SMA200 (`signal = G & vol_gate`), não faz AND —
  é o follow-up direto do insight da 3A. Lookback FIXO em 200 para isolar *forma*
  de *janela* (a janela é a pergunta da Phase 3C). Formas: SMA200 controle,
  EMA200, histerese band5%/8%, ROC200>0, Clenow200>0. Sanity PASSOU: a forma
  SMA200 reproduz a Phase 2 em `36` linhas casadas, max abs diff after-tax
  CAGR/MDD `8,33e-17` (~0). Resultado NEGATIVO para "bate as DUAS branches":
  nenhuma forma supera a SMA200 por score em SPY e QQQ. Top geral segue o controle
  SMA200 (`SPY spy_top` L`2,00` lag `3`, CAGR `15,44%`, MDD `-39,28%`). EMA200 é a
  única alternativa competitiva e só em QQQ (score `3,828` vs `3,830`: `+1,36pp`
  CAGR mas `-3,57pp` MDD em `qqq_top` lag `0`); em SPY a EMA perde em CAGR e MDD.
  Histerese/ROC/Clenow como gate substituto pioram muito o drawdown nas duas
  branches (MDD `-50%` a `-74%`, warning/ruin) — custo de whipsaw amplificado por
  alavancagem: um gate de tendência mais ruidoso/"grudento" segura exposição
  alavancada em quedas que o nível SMA200 limpo já sairia. Leitura: o *nível*
  SMA200 é gate de regime robusto para esta geometria; histerese NÃO promovida.
  Pela design aprovada, Phase 3C estuda só SMA + EMA (histerese excluída), com
  SMA200 como controle. Sem deploy, sem paper-trade label, mandate §1 inalterado
  `[leverage_for_the_long_run, p.13]`, `[leverage_for_the_long_run, p.4-7]`,
  `[systematic_trading, p.283]`, `[trading_systems_methods, p.939]`,
  `[advances_fin_ml, p.208-211]`.
- Phase 3C em `lrs/phases/phase03c_lookback_study/`: responde "por que SMA 200?"
  com regra de platô PRÉ-REGISTRADA (NÃO promove o argmax). 936 linhas (13 janelas
  `50..400` x {SMA, EMA} x 6 bases x lag `0..5`); mecanismo da 3A-2 (gate
  substitui SMA, `signal = G & vol_gate`, scoring Phase 2 verbatim). Platô robusto
  = banda contígua de Calmar dentro de 10% do melhor, largura `>=150` dias, lida
  no melhor lag por janela. Resultado matizado: pela regra estrita, AMBAS as
  curvas SMA primárias são picos estreitos (frágeis): SPY `200-225`, QQQ
  `175-225` (abaixo de 150). A fragilidade vem da sensibilidade de MDD/Calmar na
  sleeve alavancada — janelas longas colapsam para ~`-59%` MDD (SPY `>=275`, QQQ
  `>=250`, saída tardia do regime). Há uma região *adequada* ampla (~`150-250`,
  MDD tolerable/preferred) onde 200 fica no/perto do Calmar-best. Âncora teórica
  ex-ante: half-life de persistência de vol (ACF de retorno² ~ GARCH `α+β`) é
  CURTA (SPY `10,9d`, QQQ `14,3d` → EWMA span ~`32/41`, `2×HL` ~`22/29`), muito
  abaixo da janela empírica; autocorrelação de retorno assinado `n/a` (quase
  ruído branco) — logo 200 NÃO é janela ancorada em persistência, é filtro de
  regime/level lento. Part 3 (adaptativo, acionada pela fragilidade): janela
  vol-scaled NÃO supera a fixa líquida de turnover em nenhuma branch (SPY Calmar
  `0,284` vs `0,393`; QQQ `0,436` vs fixo-200 `0,457` / best-fixed-175 `0,483`),
  confirmando o custo de troca de lookback amplificado por alavancagem. Veredito:
  manter janela FIXA `~175-225` (200 é default sólido), EVITAR `>=250`, geometria
  de exposição segue o driver real, e NÃO adotar adaptativo apesar do flag de
  fragilidade; argmax não promovido. Sem deploy, sem paper-trade label, mandate §1
  inalterado `[leverage_for_the_long_run, p.4-7]`, `[volatility_trading, p.39,
  p.53-54]`, `[systematic_trading, p.283]`, `[trading_systems_methods, p.939]`,
  `[advances_fin_ml, p.208-211]`.
- Phase 4 em `lrs/phases/phase04_validation_gates/`: gates de validação do mandate
  (DIAGNÓSTICO, não promoção) sobre as 6 bases SMA200 (3 SPY + 3 QQQ, melhor lag
  por base). Wrappers em `lrs/lib/validation.py` sobre o core canônico
  `market_lab.backtest.validation` (sem import de studies/). DSR `n_trials=3876`
  (linhagem Phase 2+3A+3A-2+3C); matriz PBO = grade de geometria Phase 2 em SMA200
  (200 configs/branch); WF is1764/oos756/step756, `≥6/8` janelas OOS batendo o
  underlying after-tax (MDD por janela diagnóstico, sem cap). Resultado NEGATIVO:
  **0/6 bases passam nos 7 gates**. Gate vinculante universal = G3 walk-forward
  (falha 6/6): `≥75%` das janelas OOS de ~3 anos precisam bater o underlying; o
  melhor é SPY `12/17` (70,6%), logo abaixo. SPY é o menos-rejeitado: as 3 bases
  SPY PASSAM G1 PBO (`0,016`) e G2 DSR (p `0,024-0,034 < 0,05`) mesmo com
  n_trials=3876 (track record de 58 anos sobrevive à deflação); só falham G3 (WF,
  por pouco) e `spy_lower_lev` também G4 (OOS). QQQ é claramente rejeitado: falha
  G1 PBO (`0,643`), G2 DSR (p `0,145-0,164`) e G3. G4-G7 passam amplamente (G6
  bootstrap 99,9% CI-low Sharpe `0,28-0,34>0`; G7 cross-lib ~`0`). Métricas
  (tiers warning, não gates): SPY `spy_top` CAGR `15,44%`/MDD `-39,28%`/Sharpe
  `0,718`; QQQ `qqq_top` CAGR `19,46%`/MDD `-42,58%`/Sharpe `0,725`. Veredito:
  família LRS não passa nos gates → encerrada/arquivada como research-only. Sem
  deploy, sem paper-trade label, mandate §1 inalterado `[advances_fin_ml,
  p.208-211]`, `[advances_fin_ml, p.273-275]`, `[testing_tuning, p.318-320]`,
  `[leverage_for_the_long_run, p.4-7]`.
- Phase 5 em `lrs/phases/phase05_rsc_overlay_proxy/`: diagnóstico pós-fechamento
  para responder se LRS/T3d tem valor como satélite pequeno sobre RSC-US
  `35/40/25`. Usa matriz canônica local de sleeves em
  `studies/return_stacked_core/us_core/series/return_stacked_core_sleeve_returns.parquet`
  (`GDESIM`, `RSSTSIM = SPYSIM + 70% DBMFSIM + 30% KMLMSIM - (CASHX + 200 bps/ano)`,
  `ZROZSIM`), satélites LRS locais after-tax, e curva T3d-K2 salva em
  `/var/www/victor/finances/letf-lab`.
  Testou `9` overlays (`90/10`, `80/20`, `70/30` para satélites SPY LRS, QQQ LRS,
  T3d-K2) com rebalanceamento mensal diagnóstico e métricas de
  underwater/recovery. Resultado: `0/9` passam screen estrito. Maior CAGR de overlay:
  `70/30 T3d`, CAGR `14,24%`, MDD `-48,65%`, Calmar `0,293`, vs RSC reconstruído
  CAGR `12,40%`, MDD `-30,76%`, Calmar `0,403`. Veredito: nenhum overlay estrito;
  a decisão seguinte deve vir do Top-20 CAGR bruto ou de nova escolha explícita do
  usuário, com account-level tax/friction + gates com `n_trials` honesto
  `[testing_tuning, p.327-335]`, `[systematic_trading, p.185-188]`,
  `[advances_fin_ml, p.208-211]`.

### studies/SUMMARY.md ✅ CANONICAL COMPACT LEDGER
- Criado em 2026-06-03 para concentrar em um único arquivo o resumo de todas as
  estratégias locais testadas/avaliadas, linhas LETF migradas, melhores leads,
  métricas essenciais, vereditos, ponteiros canônicos e política de cleanup. Este
  arquivo vira a primeira leitura para limpeza futura: preservar conhecimento nos
  reports/memórias finais e remover apenas artefatos gerados/regeneráveis. Sem
  deploy, sem paper trade e sem mudança no mandate `[testing_tuning, p.327-335]`,
  `[advances_fin_ml, p.208-211]`.

### studies/return_stacked_core/ ✅ CANONICAL CONSOLIDATED RSC FOLDER
- Criado em 2026-06-03 para substituir seis árvores antigas:
  `b4-v2/`, `static_spy_beater_portfolio/`, `spy_beater_hunt/`,
  `spy_beater_hunt_v2/`, `long_term_portfolio/` e `global_factor_tilt_loop/`.
- Nome consolidado: **Return-Stacked Core (RSC)**. Vertente canônica RSC-US:
  `35% GDE / 40% RSST / 25% ZROZ`; vertente RSC-Global:
  `20% GDE / 15% NTSD / 20% RSST / 20% RSIT / 25% ZROZ`.
- Conhecimento preservado em `README.md`, `STRATEGY.md`, `EVOLUTION.md`,
  `ROBUSTNESS_REPORT.md`, `us_core/`, `global_variant/`, `robustness_tables/`,
  `history/`, `legacy_spy_beater/` e `legacy_algorithms/`. Isso inclui old B4
  `25/25/25/25`, B4+evo02 `70/30`, os no-winner hunts, a linhagem global, plots
  comparativos e source reports.
- Leitura: RSC-US `35/40/25` segue como âncora mais limpa (1988-2026 CAGR
  `15,65%` vs SPY `11,35%`, MDD `-29,94%` vs `-55,14%`; pós-2010 o edge de CAGR
  é menor, mas drawdown segue materialmente melhor). `CTAP`/`RSSX` são refinamentos
  opcionais de implementação; RSC-Global é diversificação, não substituto por
  retorno absoluto. Research-only, sem deploy e sem mudança no mandate
  `[testing_tuning, p.318-320]`, `[testing_tuning, p.327-335]`,
  `[advances_fin_ml, p.208-211]`, `[leverage_for_the_long_run, p.13]`.
- Rerun atual com `RSSTSIM` ajustado (`SPY + 70% DBMF + 30% KMLM - CASHX?E=-2`)
  começa em 2000 por causa de `DBMFSIM`: RSC-US `35/40/25` CAGR `12,40%`, MDD
  `-30,76%`, Sharpe `0,838`, Calmar `0,403`, terminal `21,71x`; SPYSIM same-window
  CAGR `8,39%`, MDD `-55,14%`, Sharpe `0,514`, Calmar `0,152`, terminal `8,34x`.
  RSC termina em `2,60x` SPYSIM, com `+4,01pp/ano` de CAGR e `+24,38pp` de melhora
  em MDD `[risk_parity, p.80-81]`, `[systematic_trading, p.185-188]`.
- Matriz parcial de sleeves RSC-US adicionada em 2026-06-09:
  `us_core/series/return_stacked_core_sleeve_returns.parquet` com `GDESIM`,
  `RSSTSIM`, `ZROZSIM`, `SPYSIM`, `KMLMSIM`, `DBMFSIM`, `GLDSIM`, `CASHX`. Ela
  usa `RSSTSIM` como tracking proxy do payload Testfol.io (`SPY + 70% DBMF + 30%
  KMLM - CASHX?E=-2`), começa em 2000 por causa de `DBMFSIM`, e não reproduz a
  curva salva antiga de forma de-minimis; ainda não cobre todos os sleeves globais/CTAP/RSSX
  `[risk_parity, p.80-81]`, `[systematic_trading, p.185-188]`.
- Four-asset grid 2026-06-09 em
  `us_core/four_asset_grid/`: payload Testfol.io separado com `NTSXSIM`,
  `GDESIM`, `ZROZSIM` e `RSST70_30 = SPYSIM + 70% DBMFSIM + 30% KMLMSIM -
  CASHX?E=-2`. O run anterior com `CASHX?E=2` foi invalidado por erro de sinal do
  financing leg. Grid mensal `5%` sobre `[a,b,c,d]` gerou `1.771` portfolios. Top
  fitness rank-based corrigido: `40% GDESIM / 25% RSST70_30 / 35% ZROZSIM`, CAGR
  `12,15%`, MDD `-27,80%`, Sharpe `0,851`, Calmar `0,437`. Referências corrigidas:
  B4 `25/25/25/25` CAGR `11,23%`, MDD `-29,26%`; RSC-like `35/40/25` CAGR
  `12,29%`, MDD `-30,76%`. Veredito: screen de implementação, não promoção;
  métricas não substituem gates de validação `[testing_tuning, p.327-335]`,
  `[systematic_trading, p.185-188]`, `[advances_fin_ml, p.208-211]`.
- Walk-forward anti-overfit em `us_core/four_asset_grid/WF_REPORT.md`: otimiza os
  mesmos `1.771` pesos somente dentro de cada janela IS (`8y`) e aplica o peso
  escolhido no OOS seguinte (`2y`, step `2y`). Resultado combinado OOS da seleção
  WF: CAGR `12,57%`, MDD `-34,47%`, Sharpe `0,821`, terminal `8,37x`. O RSC-like
  fixo `35/40/25` no mesmo OOS fica CAGR `12,63%`, MDD `-30,76%`, Sharpe `0,840`,
  terminal `8,45x`. A seleção WF bate o RSC-like em só `3/9` janelas (precisaria
  `7/9` para a leitura de 75%), escolhe `9/9` portfolios diferentes e tem Spearman
  médio IS->OOS `0,144`. Veredito: escolher a melhor proporção pelo full backtest
  é overfit-prone; `40/25/35` fica como top screen, não como alocação promovida
  `[testing_tuning, p.318-320]`, `[testing_tuning, p.327-335]`,
  `[advances_fin_ml, p.208-211]`.
- Robustez complementar em `us_core/four_asset_grid/ROBUSTNESS_REPORT.md`: sensibilidade
  WF (`5y/1y`, `8y/2y`, `10y/2y`, `12y/3y`, expanding `8y/2y`), top-decile
  stability e CPCV/PBO sobre os `1.771` pesos. Nenhum cenário WF atinge 75% de
  consistência contra RSC-like; PBO = `0,655` (`reject`); CPCV seleciona `20`
  portfolios únicos em `28` splits, bate RSC-like em só `7/28` (requisito `21/28`),
  mediana rank OOS `44,41%` e Spearman médio IS->OOS `0,031`. O mapa top-decile
  de treino não inclui RSC-like em nenhuma das `8y` janelas, mas isso justamente
  confirma que o rank IS não prediz OOS. No comparativo de regras fixas default,
  `35/40/25` é o melhor por OOS terminal/CAGR: CAGR `12,63%`, MDD `-30,76%`, Sharpe
  `0,840`, terminal `8,45x`; `40/30/30` vem perto, mas inferior em terminal.
  Veredito: grid útil para vizinhança/stress, não para otimização de pesos
  `[advances_fin_ml, p.208-211]`, `[testing_tuning, p.318-320]`,
  `[systematic_trading, p.185-188]`.
- Margin overlay analysis corrigida em `us_core/four_asset_grid/MARGIN_ANALYSIS.md`:
  sweep exato sobre o novo top com `CASHX?E=-2` mostra `1,25x` CAGR `13,97%`/MDD
  `-34,14%`, `1,50x` CAGR `15,66%`/MDD `-40,18%`, `2,00x` CAGR `18,69%`/MDD
  `-51,98%` e `3,00x` CAGR `23,13%`/MDD `-71,40%`. Veredito prático: a correção
  removeu o caso atrativo de margem; se retomado, testar só `1,10x..1,25x` com
  requisitos reais da IBKR, financiamento, liquidação forçada, tax/friction e
  gates; `1,50x+` permanece stress diagnóstico `[systematic_trading, p.185-188]`,
  `[leverage_for_the_long_run, p.4-7]`, `[testing_tuning, p.327-335]`.
- KMLM-only analysis corrigida em `us_core/four_asset_grid/KMLM_ONLY_ANALYSIS.md`:
  substitui o MF proxy por `100% KMLMSIM` com `CASHX?E=-2` para ganhar janela
  `1987-2026`. Resultado: 1x CAGR `13,00%`, MDD `-26,70%`, Sharpe `0,706`, Calmar
  `0,487`; `1,25x` CAGR `14,73%`, MDD `-33,01%`; `1,50x` CAGR `16,35%`, MDD
  `-38,92%`. Leitura: útil como lente de janela longa, mas não fortalece o caso
  de margem externa `[testing_tuning, p.327-335]`, `[advances_fin_ml, p.208-211]`.
- Comparativo Reddit 2026-06-05 em
  `studies/return_stacked_core/us_core/reddit_leveraged_backtests/`: 5 payloads
  Testfol.io executados sem Bearer, 19 instâncias / 13 portfolios únicos. Melhor
  bruto teórico: 4-3-2-1 2x margin quarterly, CAGR `17,17%`, MDD `-27,98%`,
  Calmar `0,614`, mas depende de `CASHX=-100`/margem. Melhor lead Reddit sem
  caixa negativo explícito: `mine` QQQ/TLT/GLD 3x, CAGR `16,11%`, MDD `-27,65%`,
  Calmar `0,583`, mas depende de sleeves 3x sintéticos. Veredito: RSC-US
  `35/40/25` continua anchor implementável; próxima hipótese válida seria
  traduzir essas exposições para return-stacked/no-margin e validar gates
  `[systematic_trading, p.185-188]`, `[leverage_for_the_long_run, p.21]`,
  `[advances_fin_ml, p.208-211]`.
- Diagnóstico factor-sleeve 2026-06-05 em
  `studies/return_stacked_core/us_core/factor_sleeve_diagnostics/`: AVUV/SCV e
  SPMO foram testados como pequenas sleeves financiadas por menor exposição
  efetiva de GDE/ZROZ no proxy RSC. Resultado: fatores aumentam CAGR/terminal
  marginalmente (`15,11%` baseline proxy → até `15,33%`), mas pioram MDD
  (`-27,47%` → até `-31,08%`), beta/correlação com SPY e Calmar. Veredito:
  nenhum variant domina; manter `35/40/25` como core headline
  `[ml_for_algo_trading, ch.7 p.190-191]`, `[stocks_on_the_move, p.60]`,
  `[systematic_trading, p.185-188]`.
- Screen de universo ETF return-stacked/capital-efficient 2026-06-05 em
  `studies/return_stacked_core/us_core/return_stacked_etf_universe/`: fontes
  públicas Return Stacked, SignalBloom, WisdomTree/Simplify/UPAR snippets,
  AlphaStacking `MATE`, JPMorgan `JPFP` e Direxion `SPXP`; 3 payloads Testfol.io
  de wrappers live executados sem Bearer (`HTTP 200`). Veredito: nenhum ETF novo
  substitui RSC-US `35/40/25`; `CTAP` continua apenas split opcional de
  managed-futures, `RSSX` segue BTC-convexity pequena/opcional, `MATE`/`JPFP`/
  `SPXP` entram só como watchlist por histórico curto, e crypto/income/single-name
  leverage são rejeitados como core. Follow-up de custo CTAP: expense wrapper
  `0,10%` atual / `0,28%` gross, `CTA` embutido `0,75%` e spread ponderado dos
  swaps CTA `~94,5 bps` sobre SOFR; leitura: CTAP é split de processo/gestor,
  não tese de fee menor. Mandate §1 inalterado
  `[testing_tuning, p.327-335]`, `[advances_fin_ml, p.208-211]`,
  `[systematic_trading, p.185-188]`, `[leverage_for_the_long_run, p.21]`.

### studies/spy_sso_upro_replacement/ 🌱 ACTIVE PRACTICAL-TAXED SPY REPLACEMENT
- Novo estudo iniciado em 2026-05-25 para testar substituto estático/baixo-turnover
  de SPY usando `SPYSIM`, `SSOSIM`, `UPROSIM` e diversificadores Testfol.io
  (`ZROZSIM`, `GLDSIM`, `IEFSIM`, `CASHX`). Phase 1 estática rodou grid 5% de
  `72.427` candidatos no common window 1968-2026, com triagem mensal e recomputação
  diária exata de finalistas em rebalance monthly/quarterly/annual. Resultado:
  **monthly static não passa** o alvo preferido, mas rebalance **quarterly/annual**
  encontra candidatos modestos que passam 10y+ hit rate >=90%; lead atual:
  `80% SPY / 5% SSO / 5% UPRO / 5% ZROZ / 5% GLD` quarterly, CAGR `11,47%`, MDD
  `-55,18%`, min 10y+ hit `93,3%`, terminal `1,37x` vs SPY. Strict 5y+ 90% com
  MDD no worse than SPY **falha**. Phase 1b rodou grid local 1% de `722.791`
  linhas e `1.260` recomputações exatas: `647` rows ainda passam preferred 10y+,
  mas `0` passam strict 5y+. Top por hit-rate: `89% SPY / 1% SSO / 4% UPRO /
  3% ZROZ / 3% GLD` quarterly, CAGR `11,24%`, MDD `-55,13%`, min 10y+ hit `93,9%`,
  min 5y+ hit `79,8%`, terminal `1,21x` vs SPY. Drag stress conservador nos
  finalistas preferred: `70` sobrevivem a 10 bps/ano, `0` sobrevivem a 25 bps/ano
  ou 50 bps/ano. Status: static branch é near-miss frágil a custos; próximo passo,
  se a meta "near-always" continuar, é Phase 2 low-turnover tactical/LRS. Sem deploy
  e mandate §1 inalterado `[testing_tuning, p.327-335]`,
  `[advances_fin_ml, p.208-211]`, `[leverage_for_the_long_run, p.13]`.
- Pivot de objetivo 2026-05-25: em vez de exigir MDD parecido com SPY, a fase
  `EQUITY_DOMINANCE_REPORT.md` ranqueia `portfolio_equity / SPY_equity`; MDD vira
  diagnóstico e a alavancagem é parametrizada por target leverage adjacente
  (`1x-2x = SPY/SSO`, `2x-3x = SSO/UPRO`) para evitar mix livre redundante. Resultado:
  `1.907` candidatos (`1.107` estáticos, `800` táticos), `173` passes de dominância
  após warmup 10y e `0` passes de dominância full-period. Todos os passes são táticos;
  estáticos continuam sem dominância. Lead: `SMA200 L3.00 off 60 ZROZ / 40 GLD daily`,
  CAGR `19,38%`, MDD `-63,28%`, terminal `73,13x` vs SPY, min relative equity após
  10y `1,31x`, 10y+ hit `95,1%`, sustained-above desde `1970-12-04`. Status:
  objetivo correto para "ativo com leverage" identificado, mas ainda sem validação
  formal/sem deploy `[testing_tuning, p.327-335]`, `[advances_fin_ml, p.208-211]`,
  `[leverage_for_the_long_run, p.13]`.
- Seleção prática pós-imposto 2026-05-25 em `PRACTICAL_TAXED_REPORT.md`: daily
  update/rebalance foi excluído, a máscara de cadência foi auditada por contagem
  real de eventos (monthly `698`, quarterly `233`, annual `59`) e o ranking usa
  `AnnualDarfEngine` com Lei 14.754/2023, 15% anual sobre ganho líquido realizado,
  compensação/carregamento de perdas e liquidação final. Foram `847` candidatos
  (`280` active monthly/quarterly, `567` static monthly/quarterly/annual). Resultado:
  `3` passes práticos after-tax, todos active; `0` static. Lead active:
  `SMA300 L2.75 off 60 ZROZ / 40 GLD monthly`, after-tax CAGR `16,76%`, MDD
  `-73,74%`, terminal `23,75x` vs SPY after-tax, min relative equity após 10y
  `1,28x`, 10y+ hit `92,0%`. Melhor static: `static L3.00 E60% GLD annual`,
  after-tax CAGR `13,11%`, MDD `-70,80%`, terminal `3,75x`, mas min relative after
  10y `0,68x` e 10y+ hit `53,1%`, portanto sem dominância. Status: seleção apenas;
  validação/stress estreito dos winners ainda é obrigatório e não há deploy nem
  mudança no mandate `[testing_tuning, p.327-335]`, `[advances_fin_ml, p.208-211]`,
  `[leverage_for_the_long_run, p.13]`.

### studies/success_trading_strat/ 🛑 CLOSED / NO WINNER
- Estado consolidado: Phase 3 fechou em 30/30 iterações, `cumulative_n_trials=312`, zero strict winners, zero paper-trade candidates e sem deploy. `MEMORY.md` é a leitura canônica curta; reviews preservados em `reports/`.
- Novo estudo iniciado em 2026-05-14 para aplicar o processo do vídeo Neurotrader `NLBXgSmRBgU`: excelência in-sample, MCPT in-sample, walk-forward e WF-MCPT como gates adicionais ao stack do repo `[testing_tuning, p.318-320]`, `[advances_fin_ml, p.208-211]`.
- Scaffold criado com `scripts/`, `reports/`, `plots/`, `iters/`, `SPEC.md`, `MEMORY.md`, `LOOP_PROTOCOL.md`, `LOOP_PROMPT.md` e `loop.sh`. Iteração 001 foi infrastructure-only: audit final do Tiingo, refresh de ETF/crypto/forex/NDX100, refresh parcial SPX500 e backup `data/tiingo_backup_20260514-0311.tar.gz` (210.8 MB).
- Coverage pós-refresh: 1.755 tickers no manifesto, 0 tickers críticos ausentes, ETFs críticos até 2026-05-13; crypto/FX permanecem stale por endpoint retornando até abril. Sem strategy claim; mandate §1 inalterado.
- Iteração 002 adicionou `validation_scaffold.py` para IS MCPT e WF-MCPT com teste focado (`5 passed`) e coleta pytest (`1100 tests collected`). Iterações 003-006 testaram famílias pequenas pré-registradas e fecharam `fail`: SMA/momentum SPY/QQQ falhou PBO/MCPT; cross-sectional ETF momentum (`SPY/QQQ/IWM/TLT/GLD` + `SHV`) passou PBO/DSR mas falhou Sharpe vs benchmark, IS MCPT, WF MCPT e FWD stress; volatility-targeted static sleeves melhoraram Sharpe/MDD vs 60/40, mas falharam IS MCPT, WF MCPT e PBO; `RSI(2)` mean reversion em `SPY/QQQ` passou PBO/DSR, mas falhou Sharpe vs buy-and-hold e MCPT. Iteração 007 pré-registrou proxy de volatility-carry via `VIXY`, mas fechou `data_blocked` porque `data/tiingo/daily/prices/VIXY.parquet` estava ausente; nenhum trial consumido. Iteração 008 re-registrou o mecanismo com `VXX` confirmado e fechou `fail`: melhor `vxx_neg21_spy` teve CAGR 9,86%, Sharpe 0,935 e MDD -29,54% vs SPY buy-hold CAGR 14,74%, Sharpe 0,910 e MDD -33,70%, mas falhou IS MCPT (`p=0,145`), WF MCPT (`p=0,10`), PBO (`0,686`) e DSR (`p=0,0554`). Iteração 009 pivotou para EWMAC multi-asset ETF (`SPY/QQQ/TLT/IEF/GLD` + `SHV`) e também fechou `fail`: melhor `ewmac_16_64_risk3` teve CAGR 11,40%, Sharpe 0,814 e MDD -24,97% vs equal-weight `SPY/QQQ/TLT` Sharpe 1,049, falhando benchmark Sharpe, IS MCPT (`p=0,165`), WF MCPT (`p=0,43`), PBO (`0,814`) e DSR (`p=0,1017`). Iteração 010 pivotou para pares ETF market-neutral por z-score (`GLD/SLV`, `TLT/IEF`, `SPY/QQQ`) e fechou `fail`: melhor `tlt_ief_z60_e1` teve CAGR 0,69%, Sharpe 0,183 e MDD -12,05% vs SHV Sharpe 5,425, falhando benchmark Sharpe, IS MCPT (`p=0,365`), WF MCPT (`p=0,53`), DSR (`p=0,9049`) e bootstrap. Iteração 011 pivotou para VIX-managed exposure (`SPY/QQQ` escalados por média VIX 21d) e foi o melhor diagnóstico estatístico até aqui: `qqq_vix15_w21` passou benchmark Sharpe, IS MCPT (`p=0,000`), WF MCPT (`p=0,010`), PBO (`0,400`), DSR (`p=0,04697`), WF/OOS/bootstrap/cross-lib, mas fechou `fail` por FWD stress 63d negativo (`-1,18%`). `cumulative_n_trials=32`; sem strategy claim; próxima etapa pode stressar VIX com trials explícitos ou pivotar mecanismo `[paper.bozovic_2024_vix_managed, §methodology]`, `[testing_tuning, p.318-320]`, `[testing_tuning, p.327-335]`, `[advances_fin_ml, p.222-223]`.
- Iteração 012 de `success_trading_strat` estressou a família VIX-managed com floors, janela VIX 42d e basket SPY/QQQ. Melhor `qqq_vix15_w21_floor50` melhorou para CAGR 16,57%, Sharpe 0,954 e MDD -30,99% vs QQQ buy-hold Sharpe 0,945, mas fechou `fail` por IS MCPT (`p=0,030`), PBO (`0,729`) e FWD 63d ainda negativo (`-0,41%`). `cumulative_n_trials=36`; mandate §1 inalterado `[paper.bozovic_2024_vix_managed, §methodology]`, `[testing_tuning, p.327-335]`, `[advances_fin_ml, p.208-211]`.
- Iteração 013 de `success_trading_strat` pivotou para Donchian trend em `BTCUSD/ETHUSD` com `SHV`. Melhor `eth_don20` teve CAGR 66,12%, Sharpe 1,364 e MDD -35,51% vs ETH buy-hold Sharpe 1,160 e MDD -92,94%; passou IS MCPT (`p=0,000`), WF MCPT (`p=0,050`), PBO (`0,286`), DSR (`p=0,00364`), OOS/bootstrap/cross-lib, mas fechou `fail` por WF 5/6 positivo vs requisito 6 e FWD 63d negativo (`-6,85%`). `cumulative_n_trials=40`; mandate §1 inalterado `[paper.zarattini_2025_crypto_trends, §methodology]`, `[testing_tuning, p.318-320]`, `[advances_fin_ml, p.208-211]`.
- Iteração 014 de `success_trading_strat` testou momentum BTC/ETH com volatility targeting (100d vol, alvo 20%, cap 1.0) como pivot não-Donchian. Melhor `btc_mom63_vt20` teve CAGR 25,57%, Sharpe 1,377 e MDD -22,70% vs BTC buy-hold Sharpe 1,112 e MDD -83,15%; passou DSR (`p=0,0189`), OOS, FWD 63d, bootstrap e cross-lib, mas fechou `fail` por IS MCPT (`p=0,015`), WF MCPT (`p=0,110`), PBO (`0,857`) e WF 5/6. `cumulative_n_trials=44`; mandate §1 inalterado `[systematic_trading, p.40]`, `[systematic_trading, p.137-148]`, `[advances_fin_ml, p.208-211]`.
- Iteração 015 de `success_trading_strat` pivotou para compressão de volatilidade realizada + momentum positivo em `SPY/QQQ` com `SHV`. Melhor `qqq_rv20_p60_m63` teve CAGR 7,63%, Sharpe 0,727 e MDD -21,20% vs QQQ buy-hold CAGR 19,09%, Sharpe 0,948 e MDD -35,12%; passou WF 9/12, OOS, FWD 63d e cross-lib, mas fechou `fail` por Sharpe vs benchmark, IS MCPT (`p=0,425`), WF MCPT (`p=0,490`), PBO (`0,514`), DSR (`p=0,2850`) e bootstrap. `cumulative_n_trials=48`; mandate §1 inalterado `[volatility_trading, p.36]`, `[volatility_trading, p.58-59]`, `[advances_fin_ml, p.208-211]`.
- Iteração 016 de `success_trading_strat` testou filtro cross-asset de apetite a risco por crédito (`HYG/IEF`) + momentum próprio em `SPY/QQQ`. Melhor `spy_hygief126_m63` teve CAGR 6,35%, Sharpe 0,730 e MDD -23,25% vs SPY buy-hold CAGR 15,12%, Sharpe 0,913 e MDD -33,70%; passou WF 9/12, OOS, FWD 63d e cross-lib, mas fechou `fail` por Sharpe vs benchmark, IS MCPT (`p=0,310`), WF MCPT (`p=0,430`), PBO (`0,900`), DSR (`p=0,2749`) e bootstrap. `cumulative_n_trials=52`; mandate §1 inalterado `[systematic_trading, p.42]`, `[trading_systems_methods, p.13]`, `[advances_fin_ml, p.208-211]`.
- Iteração 017 de `success_trading_strat` testou combinação multi-asset de forecasts EWMAC positivos em estilo Carver com pesos inverse-vol e volatility targeting. Melhor `risk4_ewmac16_64_vt10` teve CAGR 9,85%, Sharpe 0,930 e MDD -20,92% vs equal-weight `SPY/QQQ/TLT/GLD` CAGR 12,30%, Sharpe 1,156 e MDD -25,16%; passou WF 9/12, OOS, bootstrap e cross-lib, mas fechou `fail` por Sharpe vs benchmark, IS MCPT (`p=0,250`), WF MCPT (`p=0,530`), PBO (`0,600`), DSR (`p=0,0874`) e FWD 63d (`-3,62%`). `cumulative_n_trials=56`; mandate §1 inalterado `[systematic_trading, p.40]`, `[systematic_trading, p.118-119]`, `[advances_fin_ml, p.208-211]`.
- Iteração 018 de `success_trading_strat` testou overlay Ehlers de market-mode/ciclo em `SPY/QQQ` com `SHV`. Melhor `qqq_ehlers_c30_t15` teve CAGR 12,51%, Sharpe 1,004 e MDD -18,48% vs QQQ buy-hold CAGR 19,80%, Sharpe 0,980 e MDD -35,12%; passou PBO (`0,314`), DSR (`p=0,0476`), WF 9/12, OOS, FWD 63d, bootstrap e cross-lib, mas fechou `fail` por IS MCPT (`p=0,075`) e WF MCPT (`p=0,300`). `cumulative_n_trials=60`; mandate §1 inalterado `[rocket_science, p.99-100]`, `[rocket_science, p.114-117]`, `[testing_tuning, p.318-320]`.
- Iteração 019 de `success_trading_strat` pivotou para rotação carry/yield com dividend yield de `SPY`, yields Treasury 3m/10y/30y e sleeves `SPY/IEF/TLT/SHV`. Melhor `spy_div_gt_cash_ief_term` teve CAGR 11,15%, Sharpe 0,783 e MDD -33,70% vs 60/40 `SPY/IEF` CAGR 9,95%, Sharpe 1,004 e MDD -21,02%; passou WF 11/12, OOS, bootstrap e cross-lib, mas fechou `fail` por Sharpe vs benchmark, IS MCPT (`p=0,415`), WF MCPT (`p=0,460`), PBO (`0,629`), DSR (`p=0,2194`) e FWD 63d (`-0,21%`). `cumulative_n_trials=64`; mandate §1 inalterado `[systematic_trading, p.119]`, `[systematic_trading, p.288]`, `[testing_tuning, p.318-320]`.
- Iteração 020 de `success_trading_strat` testou sazonalidade turn-of-month em `SPY/QQQ` vs `SHV`. Melhor `spy_tom_l1_f4` teve CAGR 6,11%, Sharpe 0,744 e MDD -16,65% vs SPY buy-hold CAGR 14,20%, Sharpe 0,861 e MDD -33,70%; passou WF 9/12, OOS, FWD 63d, bootstrap e cross-lib, mas fechou `fail` por Sharpe vs benchmark, IS MCPT (`p=0,205`), WF MCPT (`p=0,260`), PBO (`0,500`, não `<0,5`) e DSR (`p=0,2735`). `cumulative_n_trials=68`; mandate §1 inalterado `[trading_systems_methods, p.479-481]`, `[testing_tuning, p.318-320]`, `[advances_fin_ml, p.208-211]`.
- Iteração 021 de `success_trading_strat` testou decomposição intraday/overnight via OHLC ajustado em `SPY/QQQ`. Melhor `qqq_close_to_open` teve CAGR 12,44%, Sharpe 0,998 e MDD -27,43% vs QQQ buy-hold CAGR 19,25%, Sharpe 0,958 e MDD -35,12%; passou Sharpe benchmark, PBO (`0,086`), WF 11/12, OOS, FWD 63d, bootstrap e cross-lib, mas fechou `fail` por IS MCPT (`p=1,000`), WF MCPT (`p=0,430`) e DSR (`p=0,0600`). `cumulative_n_trials=72`; mandate §1 inalterado `[paper.zarattini_2024_intraday_spy, §methodology]`, `[testing_tuning, p.318-320]`, `[advances_fin_ml, p.222-223]`.
- Iteração 022 de `success_trading_strat` testou timing adaptativo KAMA/Efficiency Ratio em `SPY/QQQ` com `SHV`. Melhor `qqq_kama_er20` teve CAGR 8,63%, Sharpe 0,889 e MDD -16,57% vs QQQ buy-hold CAGR 19,25%, Sharpe 0,958 e MDD -35,12%; passou PBO (`0,257`), WF 9/12, OOS, FWD 63d, bootstrap e cross-lib, mas fechou `fail` por Sharpe vs benchmark, IS MCPT (`p=0,110`), WF MCPT (`p=0,520`) e DSR (`p=0,1264`). `cumulative_n_trials=76`; mandate §1 inalterado `[trading_systems_methods, p.10-11]`, `[trading_systems_methods, p.780-782]`, `[advances_fin_ml, p.222-223]`.
- Iteração 023 de `success_trading_strat` testou confirmação por OBV/volume em `SPY/QQQ` com `SHV`. Melhor `qqq_obv21` teve CAGR 14,09%, Sharpe 1,136 e MDD -21,25% vs QQQ buy-hold CAGR 19,25%, Sharpe 0,958 e MDD -35,12%; passou Sharpe benchmark, PBO (`0,086`), DSR (`p=0,0173`), WF 9/12, OOS, FWD 63d, bootstrap e cross-lib, mas fechou `fail` por IS MCPT (`p=0,020`) e WF MCPT (`p=0,180`). `cumulative_n_trials=80`; mandate §1 inalterado `[trading_systems_methods, p.537]`, `[testing_tuning, p.318-320]`, `[advances_fin_ml, p.222-223]`.
- Iteração 024 de `success_trading_strat` pivotou para pressão de volume por localização do fechamento (`Accumulation/Distribution` e `Intraday Intensity`) em `SPY/QQQ` com `SHV`. Melhor `qqq_ad21` teve CAGR 9,21%, Sharpe 0,700 e MDD -39,94% vs QQQ buy-hold CAGR 19,25%, Sharpe 0,958 e MDD -35,12%; passou WF 11/12, OOS, FWD 63d e cross-lib, mas fechou `fail` por Sharpe vs benchmark, IS MCPT (`p=0,530`), WF MCPT (`p=0,830`), PBO (`0,900`), DSR (`p=0,3641`) e bootstrap. `cumulative_n_trials=84`; mandate §1 inalterado `[trading_systems_methods, p.540-541]`, `[testing_tuning, p.327-335]`, `[advances_fin_ml, p.208-211]`.
- Iteração 025 de `success_trading_strat` pivotou para breadth de mercado via proxy current-constituent large-cap em `SPY/QQQ` com `SHV`. Melhor `spy_breadth_sma63_gt55` teve CAGR 8,82%, Sharpe 0,886 e MDD -16,25% vs SPY buy-hold CAGR 15,08%, Sharpe 0,924 e MDD -33,70%; passou WF MCPT (`p=0,010`), WF 9/9, OOS, FWD 63d, bootstrap e cross-lib, mas fechou `fail` por Sharpe vs benchmark, IS MCPT (`p=0,210`), PBO (`0,829`) e DSR (`p=0,2173`). Caveat de survivorship do proxy atual também bloquearia promoção. `cumulative_n_trials=88`; mandate §1 inalterado `[trading_systems_methods, p.548-549]`, `[trading_systems_methods, p.941]`, `[advances_fin_ml, p.208-211]`.
- Iteração 026 de `success_trading_strat` pivotou para apetite a risco por liderança setorial (`XLY/XLP` e `XLK/XLU`) em `SPY/QQQ` com `SHV`. Melhor `spy_xly_xlp_m126` teve CAGR 8,18%, Sharpe 0,825 e MDD -16,18% vs SPY buy-hold CAGR 14,22%, Sharpe 0,862 e MDD -33,70%; passou WF 10/12, OOS, FWD 63d, bootstrap e cross-lib, mas fechou `fail` por Sharpe vs benchmark, IS MCPT (`p=0,250`), WF MCPT (`p=0,210`), PBO (`0,800`) e DSR (`p=0,2082`). `cumulative_n_trials=92`; mandate §1 inalterado `[trading_systems_methods, p.13]`, `[trading_systems_methods, p.542-544]`, `[advances_fin_ml, p.208-211]`.
- Iteração 027 de `success_trading_strat` pré-registrou filtro macro por commodities (`DBC`/`GLD` momentum) para `SPY/TLT`, mas fechou `data_blocked` antes de testar porque `data/tiingo/daily/prices/DBC.parquet` estava ausente. Por conservadorismo, nenhum proxy substituto foi usado após o pré-registro; `n_trials=0`, `cumulative_n_trials=92`, mandate §1 inalterado `[trading_systems_methods, p.939]`, `[trading_systems_methods, p.285]`, `[testing_tuning, p.327-335]`.
- Iteração 028 de `success_trading_strat` pivotou para rotação LETF estilo Gayed usando `QQQ > SMA200` defasado para segurar `QLD/TQQQ` ou `SHV`, com variantes esparsas de filtro de volatilidade realizada. Melhor `qld_qqq_sma200_rv70` teve CAGR 22,64%, Sharpe 0,978 e MDD -34,54% vs QLD buy-hold CAGR 33,80%, Sharpe 0,916 e MDD -63,68%; passou WF MCPT (`p=0,010`), WF 11/12, OOS, FWD 63d, bootstrap e cross-lib, mas fechou `fail` por IS MCPT (`p=0,035`), PBO (`0,686`) e DSR (`p=0,0816`). `cumulative_n_trials=96`; mandate §1 inalterado `[leverage_for_the_long_run, p.13]`, `[leverage_for_the_long_run, p.16-17]`, `[advances_fin_ml, p.208-211]`.
- Iteração 029 de `success_trading_strat` testou filtro de quebra de diversificação por correlação equity/Treasury: segurar `SPY/QQQ` apenas quando a correlação rolante defasada com `TLT` está negativa, senão `SHV`. Melhor `spy_corr63_lt0` teve CAGR 9,03%, Sharpe 0,562 e MDD -55,20% vs SPY buy-hold CAGR 10,97%, Sharpe 0,627 e MDD -55,20%; passou PBO (`0,103`), WF 14/16, OOS, FWD 63d e cross-lib, mas fechou `fail` por Sharpe vs benchmark, IS MCPT (`p=0,810`), WF MCPT (`p=0,580`), DSR (`p=0,5240`) e bootstrap. `cumulative_n_trials=100`; mandate §1 inalterado `[risk_parity, p.80-81]`, `[systematic_trading, p.170-171]`, `[advances_fin_ml, p.222-223]`.
- Iteração 030 de `success_trading_strat` fez closure/audit no cap planejado de 30 iterações, sem novos trials. Confirmou 30 diretórios, 29 resultados prévios parseados, `n_trials` somado = 100, zero winners e artefatos obrigatórios presentes; fechou `fail` conservador porque a iteração 002 usa schema legado (`verdict`/`n_strategy_trials`) sem os campos atuais `status`/`pre_registered`. Resultado público: estudo fechado sem winner, sem deploy, mandate §1 inalterado `[testing_tuning, p.327-335]`, `[advances_fin_ml, p.222-223]`.
- Review consolidado pós-loop em `studies/success_trading_strat/reports/overnight_30_iter_review/`: compara todas as iterações, plota equity/drawdown/equity-over-SPY, rolling 1/3/5/10/15y e gate failures; adiciona classificação pragmática `candidate_watchlist` sem alterar `strict_winner`. Próxima fase documentada em `PHASE2_INTRADAY_SWING_SPEC.md`: tracks daily swing, short swing 1h/daily hybrid e gold/XAUUSD, com audit obrigatório de arquivos 15m/1h antes de testar `[testing_tuning, p.327-335]`, `[advances_fin_ml, p.222-223]`.
- Phase 1 artifacts foram movidos para `iters/phase01/`; Phase 2 escreve em `iters/phase02/`. `MEMORY.md` está reaberto com `active_phase=2`, `total_iterations=21`, `target_total_iterations=30` e `cumulative_n_trials=184`; `loop.sh` aceita `LOOP_PHASE=phase02`.
- Phase 2 iter 001 testou daily gold/XAUUSD Donchian-compression breakout após auditoria física: `GLD`/`xauusd` daily existem, mas `data/tiingo/1hour/prices/` tem 0 parquets, então intraday 1h segue bloqueado. Melhor `xau_dc100_rv20_p30` teve CAGR 7,11%, Sharpe 0,726 e MDD -14,68% vs XAU buy-hold CAGR 18,17%, Sharpe 1,099 e MDD -20,36%; fechou `fail` por benchmark Sharpe, IS MCPT (`p=0,315`), WF MCPT (`p=0,220`), PBO (`0,615`), DSR (`p=0,7716`), WF insuficiente, FWD 63d e bootstrap. `cumulative_n_trials=104`; mandate §1 inalterado `[trading_systems_methods, p.353]`, `[trading_systems_methods, p.481]`, `[advances_fin_ml, p.208-211]`.
- Phase 2 iter 005 testou daily SPY/QQQ down-gap recovery continuation com OHLC ajustado após auditoria física: daily `SPY`/`QQQ`/`SHV` existem até 2026-05-13, mas `data/tiingo/1hour/prices/` segue com 0 parquets e `15min/prices` ausente. Melhor `spy_gap10_recover` teve CAGR 1,84%, Sharpe 0,370 e MDD -12,70% vs SPY buy-hold CAGR 10,83%, Sharpe 0,646 e MDD -55,20%; passou WF MCPT (`p=0,010`), PBO (`0,171`), WF 21/30, OOS, FWD 63d e cross-lib, mas fechou `fail` por Sharpe vs benchmark, IS MCPT (`p=0,035`), DSR (`p=0,6884`) e bootstrap. `cumulative_n_trials=120`; mandate §1 inalterado `[trading_systems_methods, p.635]`, `[testing_tuning, p.318-320]`, `[advances_fin_ml, p.208-211]`.
- Phase 2 iter 006 testou daily SPY/QQQ pullback em tendência (`SMA200` + queda curta + hold fixo) após auditoria física: daily `SPY`/`QQQ`/`SHV` existem até 2026-05-13, mas `data/tiingo/1hour/prices/` segue com 0 parquets e `15min/prices` ausente. Melhor `spy_pb3_m2_hold5` teve CAGR 5,29%, Sharpe 0,862 e MDD -9,58% vs SPY buy-hold CAGR 10,92%, Sharpe 0,621 e MDD -54,67%; passou Sharpe vs benchmark, IS MCPT (`p=0,010`), WF MCPT (`p=0,010`), PBO (`0,310`), WF 15/15, OOS e cross-lib, mas fechou `fail` por DSR (`p=0,1414`), FWD 63d (`-2,55%`) e bootstrap. `cumulative_n_trials=124`; mandate §1 inalterado `[trading_systems_methods, p.172]`, `[quant_trading_chan, p.142-143]`, `[advances_fin_ml, p.222-223]`.
- Phase 2 iter 007 testou daily SPY/QQQ Bollinger lower-band mean reversion (`SMA200` + saída por banda média/tempo) após auditoria física: daily `SPY`/`QQQ`/`SHV` existem até 2026-05-13, mas `data/tiingo/1hour/prices/` segue com 0 parquets e `15min/prices` ausente. Melhor `spy_bb20_2_hold10` teve CAGR 3,38%, Sharpe 0,551 e MDD -17,17% vs SPY buy-hold CAGR 10,92%, Sharpe 0,621 e MDD -54,67%; passou WF 12/15, OOS e cross-lib, mas fechou `fail` por Sharpe vs benchmark, IS MCPT (`p=0,230`), WF MCPT (`p=0,330`), PBO (`0,734`), DSR (`p=0,5942`), FWD 63d (`-2,56%`) e bootstrap. `cumulative_n_trials=128`; mandate §1 inalterado `[trading_systems_methods, p.323-324]`, `[quant_trading_chan, p.51-53]`, `[advances_fin_ml, p.208-211]`.
- Phase 2 iter 008 testou daily `GLD`/`xauusd` MACD trend continuation com `SHV` após auditoria física: daily `GLD`/`xauusd`/`SHV`/`SPY` existem, mas `data/tiingo/1hour/prices/` segue com 0 parquets e `15min/prices` ausente. Melhor `xau_macd_12_26_9` teve CAGR 12,10%, Sharpe 0,875 e MDD -17,83% vs XAU buy-hold CAGR 16,66%, Sharpe 0,948 e MDD -20,36%; passou PBO (`0,099`), OOS e cross-lib, mas fechou `fail` por Sharpe vs benchmark, IS MCPT (`p=0,365`), WF MCPT (`p=0,310`), DSR (`p=0,6581`), WF insuficiente (`3/3`, <8), FWD 63d (`-6,49%`) e bootstrap. `cumulative_n_trials=132`; mandate §1 inalterado `[trading_systems_methods, p.382]`, `[testing_tuning, p.318-320]`, `[advances_fin_ml, p.222-223]`.
- Phase 2 iter 009 testou daily `SPY`/`QQQ` ADX/Directional Movement trend continuation com `SHV` após auditoria física: daily `SPY`/`QQQ`/`SHV` existem até 2026-05-13, mas `data/tiingo/1hour/prices/` segue com 0 parquets e `15min/prices` ausente. Melhor `spy_adx14_t25` teve CAGR 2,86%, Sharpe 0,547 e MDD -15,90% vs SPY buy-hold CAGR 10,80%, Sharpe 0,644 e MDD -55,20%; passou WF 20/30, OOS, FWD 63d, bootstrap e cross-lib, mas fechou `fail` por Sharpe vs benchmark, IS MCPT (`p=0,680`), WF MCPT (`p=0,830`), PBO (`0,635`) e DSR (`p=0,3040`). `cumulative_n_trials=136`; mandate §1 inalterado `[trading_systems_methods, p.387]`, `[testing_tuning, p.318-320]`, `[advances_fin_ml, p.208-211]`.
- Phase 2 iter 010 testou daily `GLD`/`xauusd` Keltner/ATR breakout com `SHV` após auditoria física: daily `GLD`/`xauusd`/`SHV`/`SPY` existem, mas `data/tiingo/1hour/prices/` segue com 0 parquets e `15min/prices` ausente. Melhor `xau_kel40_20_exit0` teve CAGR 8,94%, Sharpe 0,782 e MDD -18,05% vs XAU buy-hold CAGR 16,97%, Sharpe 1,059 e MDD -20,36%; passou PBO (`0,099`), OOS e cross-lib, mas fechou `fail` por Sharpe vs benchmark, IS MCPT (`p=0,500`), WF MCPT (`p=0,530`), DSR (`p=0,7391`), WF insuficiente (`3/3`, <8), FWD 63d (`-6,27%`) e bootstrap. `cumulative_n_trials=140`; mandate §1 inalterado `[trading_systems_methods, p.352-353]`, `[trading_systems_methods, p.1057-1059]`, `[advances_fin_ml, p.222-223]`.
- Phase 2 iter 011 testou daily `SPY`/`QQQ` stochastic close-location pullback com `SMA200`, `SHV` e sinais defasados após auditoria física: daily `SPY`/`QQQ`/`SHV` existem, mas `data/tiingo/1hour/prices/` segue com 0 parquets e `15min/prices` ausente. Melhor `qqq_stoch14_os20_exit50_hold10` teve CAGR 6,64%, Sharpe 0,699 e MDD -24,60% vs QQQ buy-hold CAGR 8,89%, Sharpe 0,454 e MDD -82,97%; passou Sharpe vs benchmark, IS MCPT (`p=0,005`), WF MCPT (`p=0,010`), WF 19/23, OOS, bootstrap e cross-lib, mas fechou `fail` pelo kill de CAGR vs buy-hold, PBO (`0,512`), DSR (`p=0,1815`) e FWD 63d (`-1,00%`). `cumulative_n_trials=144`; mandate §1 inalterado `[trading_systems_methods, p.385-386]`, `[trading_systems_methods, p.172]`, `[advances_fin_ml, p.208-211]`.
- Phase 2 iter 012 testou daily DeMark setup reversal em `SPY`/`QQQ`/`GLD`/`xauusd` com `SMA200`, `SHV` e sinais defasados após auditoria física: daily existem para todos os tickers, mas `data/tiingo/1hour/prices/` segue com 0 parquets e `15min/prices` ausente. Melhor `xau_demark9_sma200_hold13` teve CAGR 3,38%, Sharpe 1,512 e MDD -2,33% vs XAU buy-hold CAGR 17,30%, Sharpe 1,061 e MDD -20,36%; passou Sharpe vs benchmark, OOS, FWD 63d, bootstrap e cross-lib, mas fechou `fail` pelo kill de CAGR vs buy-hold, IS MCPT (`p=0,460`), WF MCPT (`p=0,340`), PBO (`0,730`), DSR (`p=0,1483`) e WF insuficiente (`2/2`, <8). `cumulative_n_trials=148`; mandate §1 inalterado `[trading_systems_methods, ch.4, p.173-175]`, `[trading_systems_methods, p.285]`, `[advances_fin_ml, p.208-211]`.
- Phase 2 iter 013 testou daily gold relative-strength (`GLD`/`xauusd` vs `SPY`) com momentum próprio, `SHV` e sinais defasados após auditoria física: daily existem, mas `data/tiingo/1hour/prices/` segue com 0 parquets e `15min/prices` ausente. Melhor `xau_rs200_m126` teve CAGR 14,31%, Sharpe 0,915 e MDD -20,09% vs XAU buy-hold CAGR 22,84%, Sharpe 1,247 e MDD -20,51%; passou PBO (`0,484`), OOS e cross-lib, mas fechou `fail` pelo kill de CAGR vs buy-hold, Sharpe vs benchmark, IS MCPT (`p=0,395`), WF MCPT (`p=0,410`), DSR (`p=0,7467`), WF insuficiente (`1/1`, <8), FWD 63d (`-10,44%`) e bootstrap. `cumulative_n_trials=152`; mandate §1 inalterado `[trading_systems_methods, p.542-544]`, `[trading_systems_methods, p.939]`, `[advances_fin_ml, p.208-211]`.
- Phase 2 iter 014 testou daily VIDYA adaptive trend em `SPY`/`QQQ`/`GLD`/`xauusd` com `SHV` e sinais defasados após auditoria física: daily existem, mas `data/tiingo/1hour/prices/` segue com 0 parquets e `15min/prices` ausente. Melhor `xau_vidya9_30` teve CAGR 14,80%, Sharpe 0,989 e MDD -21,49% vs XAU buy-hold CAGR 17,48%, Sharpe 0,987 e MDD -20,36%; passou PBO (`0,294`), OOS e cross-lib, mas fechou `fail` pelo kill de CAGR vs buy-hold, IS MCPT (`p=0,350`), WF MCPT (`p=0,120`), DSR (`p=0,5534`), WF insuficiente (`3/3`, <8), FWD 63d (`-10,38%`) e bootstrap. `cumulative_n_trials=156`; mandate §1 inalterado `[trading_systems_methods, p.784-785]`, `[testing_tuning, p.318-320]`, `[advances_fin_ml, p.208-211]`.
- Phase 2 iter 015 testou daily upper-Bollinger breakout após compressão de volatilidade realizada em `SPY`/`QQQ`/`GLD`/`xauusd` com `SHV` e sinais defasados após auditoria física: daily existem, mas `data/tiingo/1hour/prices/` segue com 0 parquets e `15min/prices` ausente. Melhor `xau_bb20_2_rv20_p30_exit_mid` teve CAGR 4,25%, Sharpe 0,699 e MDD -9,24% vs XAU buy-hold CAGR 17,58%, Sharpe 0,994 e MDD -20,36%; passou PBO (`0,234`), OOS, FWD 63d e cross-lib, mas fechou `fail` pelo kill de CAGR vs buy-hold, Sharpe vs benchmark, IS MCPT (`p=0,445`), WF MCPT (`p=0,530`), DSR (`p=0,7957`), WF insuficiente (`3/3`, <8) e bootstrap. `cumulative_n_trials=160`; mandate §1 inalterado `[trading_systems_methods, p.323-324]`, `[volatility_trading, p.36]`, `[advances_fin_ml, p.208-211]`.
- Phase 2 iter 016 testou daily TRIX trend continuation em `SPY`/`QQQ`/`GLD`/`xauusd` com `SHV` e sinais defasados após auditoria física: daily existem, mas `data/tiingo/1hour/prices/` segue com 0 parquets e `15min/prices` ausente. Melhor `xau_trix18_zero` teve CAGR 10,99%, Sharpe 0,831 e MDD -19,44% vs XAU buy-hold CAGR 14,30%, Sharpe 0,915 e MDD -20,36%; passou OOS e cross-lib, mas fechou `fail` pelo kill de CAGR vs buy-hold, Sharpe vs benchmark, IS MCPT (`p=0,175`), WF MCPT (`p=0,070`), PBO (`0,556`), DSR (`p=0,7106`), WF insuficiente (`3/3`, <8), FWD 63d (`-17,15%`) e bootstrap. `cumulative_n_trials=164`; mandate §1 inalterado `[trading_systems_methods, p.334]`, `[testing_tuning, p.318-320]`, `[advances_fin_ml, p.208-211]`.
- Phase 2 iter 017 testou daily Woodshedder ROC em `SPY`/`QQQ`/`GLD`/`xauusd` com `SHV` e sinais defasados após auditoria física: daily existem, mas `data/tiingo/1hour/prices/` segue com 0 parquets e `15min/prices` ausente. Melhor `xau_roc5_252_x2` teve CAGR 14,64%, Sharpe 0,960 e MDD -20,09% vs XAU buy-hold CAGR 18,00%, Sharpe 1,094 e MDD -20,36%; passou OOS e cross-lib, mas fechou `fail` pelo kill de CAGR vs buy-hold, Sharpe vs benchmark, IS MCPT (`p=0,305`), WF MCPT (`p=0,460`), PBO (`0,905`), DSR (`p=0,6476`), WF insuficiente (`2/2`, <8), FWD 63d (`-13,26%`) e bootstrap. `cumulative_n_trials=168`; mandate §1 inalterado `[trading_systems_methods, p.355]`, `[testing_tuning, p.318-320]`, `[advances_fin_ml, p.208-211]`.
- Phase 2 iter 018 testou daily Clenow adjusted-slope trend em `SPY`/`QQQ`/`GLD`/`xauusd` com `SHV` e sinais defasados após auditoria física: daily existem, mas `data/tiingo/1hour/prices/` segue com 0 parquets e `15min/prices` ausente. Melhor `xau_slope90_sma200` teve CAGR 14,57%, Sharpe 0,994 e MDD -20,09% vs XAU buy-hold CAGR 17,36%, Sharpe 1,070 e MDD -20,36%; passou OOS e cross-lib, mas fechou `fail` pelo kill de CAGR vs buy-hold, Sharpe vs benchmark, IS MCPT (`p=0,145`), WF MCPT (`p=0,320`), PBO (`0,885`), DSR (`p=0,6040`), WF insuficiente (`3/3`, <8), FWD 63d (`-11,54%`) e bootstrap. `cumulative_n_trials=172`; mandate §1 inalterado `[stocks_on_the_move, p.66-67]`, `[stocks_on_the_move, p.77]`, `[advances_fin_ml, p.208-211]`.
- Phase 2 iter 019 testou daily Force Index volume impulse em `SPY`/`QQQ`/`GLD` com `SHV`; `xauusd` ficou apenas como contexto de ouro porque o indicador exige volume confiável. Melhor `gld_fi13_z126_e05_x0_sma200_h20` teve CAGR 5,63%, Sharpe 0,601 e MDD -21,96% vs GLD buy-hold CAGR 11,44%, Sharpe 0,683 e MDD -45,56%; passou WF 13/17, OOS, FWD 63d e cross-lib, mas fechou `fail` pelo kill de CAGR vs buy-hold, Sharpe vs benchmark, IS MCPT (`p=0,445`), WF MCPT (`p=0,880`), PBO (`0,663`), DSR (`p=0,4985`) e bootstrap. `cumulative_n_trials=176`; mandate §1 inalterado `[trading_systems_methods, p.836]`, `[trading_systems_methods, p.13]`, `[advances_fin_ml, p.208-211]`.
- Phase 2 iter 020 testou proxy diário Elder-Ray Triple Screen em `SPY`/`QQQ`/`GLD`/`xauusd` com `SHV` após auditoria física: daily existem, mas `data/tiingo/1hour/prices/` segue com 0 parquets e `15min/prices` ausente. Melhor `xau_eray_12_26_9_ema13_bear3_h10` teve CAGR 2,85%, Sharpe 3,106 e MDD -1,03% vs XAU buy-hold CAGR 14,18%, Sharpe 0,909 e MDD -20,36%; passou PBO (`0,302`), DSR (`p=0,000815`), OOS, FWD 63d, bootstrap e cross-lib, mas fechou `fail` pelo kill de CAGR vs buy-hold, IS MCPT (`p=0,870`), WF MCPT (`p=0,920`) e WF insuficiente (`3/3`, <8). `cumulative_n_trials=180`; mandate §1 inalterado `[trading_systems_methods, p.835-838]`, `[trading_systems_methods, p.837]`, `[advances_fin_ml, p.208-211]`.
- Phase 2 iter 021 testou daily Wilder ASI breakout em `SPY`/`QQQ`/`GLD`/`xauusd` com `SHV` após auditoria física: daily existem com OHLC, mas `data/tiingo/1hour/prices/` segue com 0 parquets e `15min/prices` ausente. Melhor `xau_asi20_10_h20` teve CAGR 8,80%, Sharpe 0,683 e MDD -18,68% vs XAU buy-hold CAGR 17,51%, Sharpe 0,990 e MDD -20,36%; passou OOS e cross-lib, mas fechou `fail` pelo kill de CAGR vs buy-hold, Sharpe vs benchmark, IS MCPT (`p=0,715`), WF MCPT (`p=0,530`), PBO (`0,516`), DSR (`p=0,8587`), WF insuficiente (`3/3`, <8), FWD 63d (`-8,17%`) e bootstrap. O loop abortou por timeout de 1800s depois de gerar resultados; o fechamento documental foi completado manualmente. `cumulative_n_trials=184`; mandate §1 inalterado `[trading_systems_methods, p.193-195]`, `[trading_systems_methods, p.165-172]`, `[advances_fin_ml, p.208-211]`.
- Phase 2 iter 022 testou daily regression-channel breakout em `SPY`/`QQQ`/`GLD`/`xauusd` com `SHV` após auditoria física: daily existem com OHLC, mas `data/tiingo/1hour/prices/` segue com 0 parquets e `15min/prices` ausente. Melhor `xau_regch63_h30` teve CAGR 3,62%, Sharpe 0,787 e MDD -10,78% vs XAU buy-hold CAGR 14,32%, Sharpe 0,916 e MDD -20,36%; passou PBO (`0,480`), OOS, FWD 63d e cross-lib, mas fechou `fail` pelo kill de CAGR vs buy-hold, Sharpe vs benchmark, IS MCPT (`p=0,460`), WF MCPT (`p=0,250`), DSR (`p=0,7751`), WF insuficiente (`3/3`, <8) e bootstrap. `cumulative_n_trials=188`; mandate §1 inalterado `[trading_systems_methods, p.167-169]`, `[trading_systems_methods, p.168]`, `[advances_fin_ml, p.222-223]`.
- Phase 2 iter 023 testou daily Money Flow Index pullback em `SPY`/`QQQ`/`GLD` com `SHV`; `xauusd` ficou apenas como contexto porque MFI exige volume. Auditoria física: daily existem e volume ETF está presente, mas `data/tiingo/1hour/prices/` segue com 0 parquets e `15min/prices` ausente. Melhor `gld_mfi14_os20_x50_sma200_h10` teve CAGR 1,90%, Sharpe 0,730 e MDD -4,88% vs GLD buy-hold CAGR 11,64%, Sharpe 0,693 e MDD -45,56%; passou Sharpe vs benchmark, PBO (`0,246`), WF 14/17, OOS, FWD 63d, bootstrap e cross-lib, mas fechou `fail` pelo kill de CAGR vs buy-hold, IS MCPT (`p=0,475`), WF MCPT (`p=0,100`) e DSR (`p=0,2840`). `cumulative_n_trials=192`; mandate §1 inalterado `[trading_systems_methods, p.540]`, `[trading_systems_methods, p.285]`, `[advances_fin_ml, p.222-223]`.
- Phase 2 iter 024 testou daily dual MA+ATR breakout em `SPY`/`QQQ`/`GLD`/`xauusd` com `SHV` e sinais defasados após auditoria física: daily existem com OHLC, mas `data/tiingo/1hour/prices/` segue com 0 parquets e `15min/prices` ausente. Melhor `xau_ma5_20_atr20_k1` teve CAGR 10,89%, Sharpe 0,816 e MDD -15,36% vs XAU buy-hold CAGR 17,41%, Sharpe 0,985 e MDD -20,36%; passou OOS e cross-lib, mas fechou `fail` pelo kill de CAGR vs buy-hold, Sharpe vs benchmark, IS MCPT (`p=0,380`), WF MCPT (`p=0,580`), PBO (`0,607`), DSR (`p=0,7628`), WF insuficiente (`3/3`, <8), FWD 63d (`-4,22%`) e bootstrap. `cumulative_n_trials=196`; mandate §1 inalterado `[trading_systems_methods, p.352-353]`, `[trading_systems_methods, p.107]`, `[advances_fin_ml, p.208-211]`.
- Phase 2 iter 025 testou daily swing-point breakout conservador em `SPY`/`QQQ`/`GLD`/`xauusd` com `SHV` e sinais defasados após auditoria física: daily existem com OHLC, mas `data/tiingo/1hour/prices/` segue com 0 parquets e `15min/prices` ausente. Melhor `xau_swing5_break_prev_high` teve CAGR 10,06%, Sharpe 1,117 e MDD -11,13% vs XAU buy-hold CAGR 17,33%, Sharpe 0,984 e MDD -20,36%; passou Sharpe vs benchmark, PBO (`0,278`), OOS e cross-lib, mas fechou `fail` pelo kill de CAGR vs buy-hold, IS MCPT (`p=0,080`), WF MCPT (`p=0,320`), DSR (`p=0,4410`), WF insuficiente (`2/3`, <8), FWD 63d (`-10,95%`) e bootstrap. `cumulative_n_trials=200`; mandate §1 inalterado `[trading_systems_methods, p.165]`, `[trading_systems_methods, p.168]`, `[advances_fin_ml, p.222-223]`.
- Phase 2 iter 026 testou daily Price Density trend filter em `SPY`/`QQQ`/`GLD`/`xauusd` com `SHV` e sinais defasados após auditoria física: daily existem com OHLC, mas `data/tiingo/1hour/prices/` segue com 0 parquets e `15min/prices` ausente. Melhor `spy_pd20_lt4_sma200` teve CAGR 6,45%, Sharpe 0,797 e MDD -20,04% vs SPY buy-hold CAGR 10,87%, Sharpe 0,644 e MDD -55,20%; passou Sharpe vs benchmark, IS MCPT (`p=0,000`), DSR (`p=0,0413`), WF 21/29, OOS, FWD 63d, bootstrap e cross-lib, mas fechou `fail` pelo kill de CAGR vs buy-hold, WF MCPT (`p=0,060`) e PBO (`0,512`). `cumulative_n_trials=204`; mandate §1 inalterado `[trading_systems_methods, p.12]`, `[trading_systems_methods, p.13]`, `[advances_fin_ml, p.208-211]`.
- Phase 2 iter 027 testou daily Williams %R exhaustion reversal em `SPY`/`QQQ`/`GLD`/`xauusd` com `SHV` e sinais defasados após auditoria física: daily existem com OHLC, mas `data/tiingo/1hour/prices/` segue com 0 parquets e `15min/prices` ausente. Melhor `qqq_wr14_os90_x50_sma200_h10` teve CAGR 6,07%, Sharpe 0,788 e MDD -15,45% vs QQQ buy-hold CAGR 9,38%, Sharpe 0,469 e MDD -82,97%; passou Sharpe vs benchmark, IS MCPT (`p=0,005`), WF MCPT (`p=0,010`), WF 17/23, OOS, bootstrap e cross-lib, mas fechou `fail` pelo kill de CAGR vs buy-hold, PBO (`0,651`), DSR (`p=0,0918`) e FWD 63d (`-1,96%`). `cumulative_n_trials=208`; mandate §1 inalterado `[trading_systems_methods, p.385-386]`, `[trading_systems_methods, p.172]`, `[advances_fin_ml, p.208-211]`.
- Phase 3 spec criada em `studies/success_trading_strat/PHASE3_BH_BEATER_SPEC.md`: a próxima fase deixa de priorizar filtros defensivos long/flat e passa a exigir mecanismos com motor plausível para bater buy-and-hold em CAGR e terminal wealth, como LETF/alavancagem controlada, rotação high-beta, crash-rearm e long/short com gross exposure modelado. A spec preserva gates MCPT/PBO/DSR/WF/OOS/FWD/bootstrap/cross-lib, mantém capital 100% Plano C e bloqueia qualquer label acima de `fail` sem bater B&H alinhado `[systematic_trading, p.40]`, `[leverage_for_the_long_run, p.13]`, `[advances_fin_ml, p.222-223]`.
- Phase 3 foi aberta operacionalmente em `MEMORY.md` com contador local resetado (`total_iterations=0`, `target_total_iterations=30`) e `cumulative_n_trials=216` preservado para DSR. `LOOP_PROMPT.md` agora aponta para `PHASE3_BH_BEATER_SPEC.md` e `iters/phase03/`.
- Phase 2 iter 028 testou daily CMO momentum continuation em `SPY`/`QQQ`/`GLD`/`xauusd` com `SHV` e sinais defasados após auditoria física: daily existem, mas `data/tiingo/1hour/prices/` segue com 0 parquets e `15min/prices` ausente. Melhor `xau_cmo20_e50_x0_sma200_h20` teve CAGR 5,91%, Sharpe 0,638 e MDD -14,68% vs XAU buy-hold CAGR 17,28%, Sharpe 1,060 e MDD -20,36%; passou OOS, FWD 63d e cross-lib, mas fechou `fail` pelo kill de CAGR vs buy-hold, Sharpe vs benchmark, IS MCPT (`p=0,470`), WF MCPT (`p=0,790`), PBO (`0,885`), DSR (`p=0,8738`), WF insuficiente (`2/2`, <8) e bootstrap. `cumulative_n_trials=212`; mandate §1 inalterado `[trading_systems_methods, p.388]`, `[trading_systems_methods, p.284]`, `[advances_fin_ml, p.208-211]`.
- Phase 2 iter 029 testou daily Fisher Transform cycle reversal em `SPY`/`QQQ`/`GLD`/`xauusd` com `SMA200`, `SHV` e sinais defasados após auditoria física: daily existem, mas `data/tiingo/1hour/prices/` segue com 0 parquets e `15min/prices` ausente. Melhor `spy_fisher10_reversal_sma200_h10` teve CAGR 4,70%, Sharpe 0,729 e MDD -11,09% vs SPY buy-hold CAGR 10,90%, Sharpe 0,646 e MDD -55,20%; passou Sharpe vs benchmark, IS MCPT (`p=0,000`), WF MCPT (`p=0,050`), WF 23/29, OOS, bootstrap e cross-lib, mas fechou `fail` pelo kill de CAGR vs buy-hold, PBO (`0,587`), DSR (`p=0,0882`) e FWD 63d (`-2,76%`). `cumulative_n_trials=216`; mandate §1 inalterado `[cycle_analytics, p.195-197]`, `[trading_systems_methods, p.284]`, `[advances_fin_ml, p.208-211]`.
- Phase 2 iter 030 fez closure/audit no cap planejado de 30 iterações, sem novos trials. Confirmou 29 resultados prévios parseáveis, todos `fail`, zero `winner=true`, zero `strict_winner`, zero `candidate_watchlist`/`paper_trade_candidate`, artefatos obrigatórios completos e soma local Phase 2 `n_trials=116` reconciliada com `cumulative_n_trials=216`. Fechou `fail` porque a Phase 2 não encontrou estratégia validada; `MEMORY.md` ficou `phase2_closed_no_winner`, sem deploy e mandate §1 inalterado `[testing_tuning, p.318-320]`, `[testing_tuning, p.327-335]`, `[advances_fin_ml, p.222-223]`.
- Phase 3 iter 001 testou exposição Nasdaq LETF volatility-targeted (`QLD`/`TQQQ`) após auditoria física dos arquivos daily Phase 3. Melhor `qld_vt35_rv21_dd25_half` bateu `QQQ` buy-hold em CAGR (22,12% vs 17,16%) e terminal wealth (52,01x vs 22,90x), mas fechou `economic_beater_not_validated`: falhou IS MCPT (`p=0,050`), WF MCPT (`p=0,310`) e DSR (`p=0,1472`, `cumulative_n_trials=222`), apesar de passar PBO (`0,421`), WF/OOS/FWD/bootstrap/cross-lib. Também ficou abaixo de `QLD` buy-hold em terminal wealth; sem winner, sem deploy e mandate §1 inalterado `[leverage_for_the_long_run, p.13]`, `[systematic_trading, p.137-148]`, `[advances_fin_ml, p.222-223]`.
- Phase 3 iter 002 testou exposição S&P LETF volatility-targeted (`SSO`/`UPRO`) como mecanismo distinto de retorno. Melhor `upro_vt40_rv63_dd30_half` bateu `SPY` buy-hold em CAGR (20,54% vs 14,57%) e terminal wealth (22,19x vs 9,56x), mas fechou `economic_beater_not_validated`: falhou IS MCPT (`p=0,565`), WF MCPT (`p=0,370`), DSR (`p=0,4551`, `cumulative_n_trials=228`) e bootstrap 99,9% (CI low negativo), apesar de passar PBO (`0,206`), WF 9/13, OOS, FWD 63d e cross-lib. Também ficou abaixo de `UPRO` buy-hold em terminal wealth; sem winner, sem deploy e mandate §1 inalterado `[leverage_for_the_long_run, p.5-7]`, `[leverage_for_the_long_run, p.13]`, `[systematic_trading, p.137-148]`, `[advances_fin_ml, p.222-223]`.
- Phase 3 iter 003 testou exposição semiconductor/technology LETF volatility-targeted (`SOXL`/`TECL`) com benchmarks primários conservadores `QQQ` e equal-weight `SMH/SOXX`. Melhor `tecl_vt40_rv63` bateu ambos em CAGR (34,00% vs 21,02% `QQQ` e 27,89% `SMH/SOXX`) e terminal wealth (148,14x vs 25,99x e 66,76x), mas fechou `economic_beater_not_validated`: falhou IS MCPT (`p=0,490`), WF MCPT (`p=0,670`) e DSR (`p=0,1636`, `cumulative_n_trials=234`), apesar de passar PBO (`0,206`), WF 10/14, OOS, FWD 63d, bootstrap e cross-lib. Também ficou abaixo de `TECL` buy-hold em terminal wealth; sem winner, sem deploy e mandate §1 inalterado `[leverage_for_the_long_run, p.5-7]`, `[leverage_for_the_long_run, p.13]`, `[systematic_trading, p.137-148]`, `[advances_fin_ml, p.222-223]`.
- Phase 3 iter 004 testou crash-rearm Nasdaq (`QQQ` core + booster temporário `QLD` após drawdown e recuperação acima de SMA). Melhor `qqq_qld_rearm_dd35_sma100_h189` bateu `QQQ` buy-hold em CAGR (18,64% vs 16,39%) e terminal wealth (27,79x vs 19,18x), mas fechou `economic_beater_not_validated`: falhou IS MCPT (`p=0,135`), WF MCPT (`p=0,550`) e DSR (`p=0,2006`, `cumulative_n_trials=240`), apesar de passar PBO (`0,230`), WF 15/16, OOS, FWD 63d, bootstrap e cross-lib. Há caveat adicional: MCPT usou proxy sintético 2x `QQQ`, não permutação conjunta `QQQ`/`QLD`; sem winner, sem deploy e mandate §1 inalterado `[leverage_for_the_long_run, p.16-17]`, `[systematic_trading, p.119]`, `[testing_tuning, p.318-320]`, `[advances_fin_ml, p.222-223]`.
- Phase 3 iter 005 testou crash-rearm S&P (`SPY` core + booster temporário `SSO` após drawdown e recuperação acima de SMA). Melhor `spy_sso_rearm_dd35_sma100_h189` bateu `SPY` buy-hold em CAGR (13,05% vs 11,05%) e terminal wealth (10,87x vs 7,69x), mas fechou `economic_beater_not_validated`: falhou IS MCPT (`p=0,095`), WF MCPT (`p=0,500`), PBO (`0,778`), DSR (`p=0,4147`, `cumulative_n_trials=246`) e bootstrap 99,9% (CI low negativo), apesar de passar WF 15/16, OOS, FWD 63d e cross-lib. Há caveat adicional: MCPT usou proxy sintético 2x `SPY`, não permutação conjunta `SPY`/`SSO`; sem winner, sem deploy e mandate §1 inalterado `[leverage_for_the_long_run, p.16-17]`, `[systematic_trading, p.119]`, `[testing_tuning, p.318-320]`, `[advances_fin_ml, p.222-223]`.
- Phase 3 iter 006 pivotou para rotação relativa high-beta sempre investida (`QQQ/SMH/SOXX/XLK`). Melhor `top2_m63` bateu o benchmark primário equal-weight em CAGR (15,98% vs 15,50%) e terminal wealth (37,92x vs 34,28x), mas fechou `economic_beater_not_validated`: falhou IS MCPT (`p=0,055`), WF MCPT (`p=0,850`) e DSR (`p=0,2983`, `cumulative_n_trials=252`), apesar de passar PBO (`0,345`), WF 19/21, OOS, FWD 63d, bootstrap e cross-lib. Não bateu `SMH` buy-hold e turnover anual bruto foi alto (16,05); sem winner, sem deploy e mandate §1 inalterado `[stocks_on_the_move, p.66-67]`, `[trading_systems_methods, p.542-544]`, `[testing_tuning, p.318-320]`, `[advances_fin_ml, p.222-223]`.
- Phase 3 iter 007 pré-registrou rotação crypto/equity sempre investida (`BTCUSD/ETHUSD/QQQ/GLD`), mas fechou `data_blocked` antes de qualquer backtest porque os parquets físicos obrigatórios `data/tiingo/daily/prices/BTCUSD.parquet` e `ETHUSD.parquet` estavam ausentes. `QQQ`, `GLD`, `SPY` e `SHV` existem até 2026-05-13; nenhum proxy foi substituído após preregistro. `n_trials=0`, `cumulative_n_trials=252`; sem winner, sem deploy e mandate §1 inalterado `[stocks_on_the_move, p.66-67]`, `[trading_systems_methods, p.542-544]`, `[testing_tuning, p.327-335]`.
- Phase 3 iter 008 testou sizing drawdown-adaptive com gross exposure no universo high-beta confirmado (`QQQ/SMH/SOXX/XLK`). Melhor `top2_m63_dd15_boost125_cap150` bateu o benchmark primário equal-weight em CAGR (17,02% vs 15,50%) e terminal wealth (47,19x vs 34,28x), mas fechou `economic_beater_not_validated`: falhou IS MCPT (`p=0,105`), WF MCPT (`p=0,960`), PBO (`0,623`) e DSR (`p=0,3293`, `cumulative_n_trials=256`), apesar de passar WF 19/21, OOS, FWD 63d, bootstrap e cross-lib. Turnover anual alto (`18,03`) e ausência de financing/tax model bloqueiam qualquer leitura promocional adicional; sem winner, sem deploy e mandate §1 inalterado `[leverage_space, p.149-167]`, `[systematic_trading, p.137-148]`, `[advances_fin_ml, p.222-223]`.
- Phase 3 iter 009 testou long/short high-beta por momentum relativo (`QQQ/SMH/SOXX/XLK`) com gross exposure e proxy explícito de financing/borrow de 5% a.a. Melhor `ls_m63_top1_bottom1_g100` fechou `fail`: CAGR -3,77% e terminal wealth 0,48x vs benchmark primário equal-weight CAGR 19,18% e terminal wealth 28,26x; também falhou IS MCPT (`p=0,750`), WF MCPT (`p=0,640`), DSR (`p=0,999999`), WF 5/16 e bootstrap, apesar de passar PBO (`0,433`), OOS, FWD 63d e cross-lib. `cumulative_n_trials=260`; sem winner, sem deploy e mandate §1 inalterado `[stocks_on_the_move, p.66-67]`, `[trading_systems_methods, p.542-544]`, `[systematic_trading, p.137-148]`.
- Phase 3 iter 010 testou sleeve balanceado fixo com `UPRO/TLT/GLD` e rebalance mensal/trimestral. Melhor `upro50_tlt25_gld25_quarterly` bateu o benchmark primário conservador duplo em CAGR/terminal wealth: 24,13% e 38,16x vs `SPY` 15,23% e 10,89x, e vs equal-weight `UPRO/TLT/GLD` 18,59% e 17,68x. Fechou `economic_beater_not_validated`: passou IS MCPT (`p=0,000`), PBO (`0,357`), WF 12/13, OOS, FWD 63d, bootstrap e cross-lib, mas falhou WF MCPT (`p=0,490`) e DSR (`p=0,09769`, `cumulative_n_trials=264`). Sem winner, sem deploy e mandate §1 inalterado `[leverage_for_the_long_run, p.13]`, `[systematic_trading, p.137-148]`, `[testing_tuning, p.318-320]`, `[advances_fin_ml, p.222-223]`.
- Phase 3 iter 011 estressou o mesmo mecanismo de sleeve balanceado substituindo `UPRO` por `SSO` com `TLT/GLD`. Melhor `sso75_tlt15_gld10_quarterly` bateu o benchmark primário conservador duplo em CAGR/terminal wealth: 14,76% e 14,27x vs `SPY` 10,97% e 7,45x, e vs equal-weight `SSO/TLT/GLD` 12,06% e 9,00x. Fechou `economic_beater_not_validated`: passou PBO (`0,389`), WF 13/16, OOS, FWD 63d e cross-lib, mas falhou IS MCPT (`p=0,035`), WF MCPT (`p=0,420`), DSR (`p=0,5123`, `cumulative_n_trials=268`) e bootstrap 99,9% (CI low negativo). Também não bateu `SSO` buy-hold puro; sem winner, sem deploy e mandate §1 inalterado `[leverage_for_the_long_run, p.13]`, `[systematic_trading, p.137-148]`, `[testing_tuning, p.318-320]`, `[advances_fin_ml, p.222-223]`.
- Phase 3 iters 012-018 continuaram o foco em beaters economicos e auditorias conservadoras. Iter 012 (`UPRO/TMF/GLD` HFEA), iter 013 (Nasdaq drawdown-rearm) e iter 014 (`UPRO/TLT` gross spread) encontraram beaters economicos, mas todos falharam MCPT/DSR e/ou gates de stress; iter 015 (`QLD/SSO/TLT/GLD` dual momentum) fechou `fail` por perder para o equal-weight primario; iter 016 mostrou fragilidade de inception no `UPRO/TMF/GLD`; iter 017 auditou janelas rolling 3y/5y dos beaters 010-014 e fechou `fail` porque 128/534 linhas candidato-janela perderam em CAGR ou terminal wealth para o B&H primario; iter 018 (`VXX` crash-rearm) bateu `QQQ` B&H em CAGR/terminal wealth, mas fechou `economic_beater_not_validated` por falhar IS MCPT (`p=0,070`), WF MCPT (`p=0,070`), PBO (`0,790`) e DSR (`p=0,1111`). `cumulative_n_trials=288`; sem winner, sem deploy e mandate §1 inalterado `[testing_tuning, p.327-335]`, `[leverage_for_the_long_run, p.4-7]`, `[leverage_space, p.149-167]`, `[advances_fin_ml, p.222-223]`.
- Phase 3 iters 019-022 mantiveram o foco em mecanismos com motor para bater B&H: iter 019 (`QLD/SSO/SMH/SOXX` gross rotation) e iter 022 (`QQQ` core + `QLD` overlay) bateram seus benchmarks primários em CAGR/terminal wealth, mas falharam MCPT/PBO/DSR/bootstrap; iter 020 risk-parity LETF fechou `fail` por perder para o equal-weight primário; iter 021 auditou os 20 primeiros diretórios Phase 3 e confirmou zero winner/promotional labels. Iter 022 melhor `mom126_vol63_cap25`: CAGR 23,19% e terminal wealth 56,02x vs `QQQ` 16,31% e 18,46x, mas falhou IS MCPT (`p=0,065`), WF MCPT (`p=0,260`), PBO (`0,738`), DSR (`p=0,2723`) e bootstrap. `cumulative_n_trials=300`; sem winner, sem deploy e mandate §1 inalterado `[leverage_for_the_long_run, p.13]`, `[systematic_trading, p.137-148]`, `[testing_tuning, p.327-335]`, `[advances_fin_ml, p.222-223]`.
- Phase 3 iter 023 testou `QQQ` core + overlay setorial `SOXL/TECL` por liderança relativa `SMH/SOXX` vs `QQQ`. Melhor `soxx_qqq_m126_v63_tecl25` bateu `QQQ` em CAGR/terminal wealth (20,93% e 21,48x vs 19,34% e 17,37x), mas fechou `fail` por perder para o benchmark primário equal-weight `SMH/SOXX` (26,80% e 46,22x) e por falhar WF MCPT (`p=0,680`) e DSR (`p=0,1319`), apesar de passar IS MCPT, PBO, WF/OOS/FWD/bootstrap/cross-lib. `cumulative_n_trials=304`; sem winner, sem deploy e mandate §1 inalterado `[leverage_for_the_long_run, p.13]`, `[stocks_on_the_move, p.66-67]`, `[testing_tuning, p.327-335]`, `[advances_fin_ml, p.222-223]`.
- Phase 3 iter 024 testou sleeve mensal `QLD/TLT/GLD` com migração de risco: boost bruto em `QLD` quando a equity da própria estratégia entra em drawdown, com financiamento 5% a.a. sobre gross > 1.0. Melhor `qld70_tlt15_gld15_dd25_boost50` bateu os benchmarks primários em CAGR/terminal wealth (23,62% e 59,95x vs `QQQ` 16,31% e 18,46x; vs equal-weight `QLD/TLT/GLD` 15,78% e 16,90x), mas fechou `economic_beater_not_validated`: falhou IS MCPT (`p=0,740`), WF MCPT (`p=0,780`), DSR (`p=0,3668`) e o guardrail de MDD 1,5x (`-80,45%`), apesar de passar PBO (`0,135`), WF 14/16, OOS, FWD 63d, bootstrap e cross-lib. `cumulative_n_trials=308`; sem winner, sem deploy e mandate §1 inalterado `[leverage_space, p.149-167]`, `[leverage_for_the_long_run, p.13]`, `[testing_tuning, p.327-335]`, `[advances_fin_ml, p.222-223]`.
- Phase 3 iter 025 auditou 16 economic beaters anteriores sob stress uniforme de fricção/financiamento adicional (25/50/100 bps a.a. descontados dos retornos da estratégia). Fechou `fail`: 47/48 linhas candidato-stress preservaram o gate econômico, mas `006_high_beta_rotation` / `top2_m63` falhou sob 100 bps (CAGR 14,43% e terminal wealth 26,36x vs equal-weight `QQQ/SMH/SOXX/XLK` 14,82% e 28,63x). `n_trials=0`, `cumulative_n_trials=308`; falhas MCPT/PBO/DSR anteriores seguem vinculantes, sem winner/deploy `[leverage_for_the_long_run, p.21]`, `[systematic_trading, p.185-188]`, `[testing_tuning, p.327-335]`, `[advances_fin_ml, p.222-223]`.
- Phase 3 iters 026-030 encerraram a fase com auditorias e um último stress do sleeve `QLD/TLT/GLD` com volatility throttle. Iter 027 ainda encontrou beater econômico (25,34% CAGR e 78,26x vs `QQQ` 16,28% e 18,37x), mas falhou IS MCPT, WF MCPT e DSR; iter 028 mostrou fragilidade rolling 3y/5y; iters 029-030 auditaram todos os artefatos e fecharam a Phase 3 em 30/30 iterações: 29 resultados prévios parseados, `economic_beater_not_validated=17`, `fail=11`, `data_blocked=1`, zero `winner=true`, zero `strict_winner`, zero `candidate_watchlist`/`paper_trade_candidate`, `cumulative_n_trials=312`. Resultado: Phase 3 fechada sem winner, sem paper trade e sem deploy; review consolidado com tabelas e plots comparativos em `studies/success_trading_strat/reports/phase3_bh_beater_review/`. Ranking econômico/visual Top 10 Phases 1-3 por `equity/equity_SPY` foi adicionado em `studies/success_trading_strat/reports/top10_phase123_spy_relative/`, sem alterar o veredito de validação. Mandate §1 inalterado `[testing_tuning, p.318-320]`, `[testing_tuning, p.327-335]`, `[advances_fin_ml, p.208-211]`, `[advances_fin_ml, p.222-223]`.

### studies/myfxbook_reverse_engineering/ 🛑 CLOSED 2026-05-04
- Veredito final: `CLOSED_NO_OPERABLE_EDGE`.
- 55 systems avaliados Fase 1; 0 elegíveis Fase 2 (synthetics distinguíveis do real, decoder não captura regra robusta).
- Plano A continua DORMANT — não há base operacional.
- Refs: `studies/myfxbook_reverse_engineering/_diagnostics/PIPELINE_V4_CLOSURE.md`.
- Cleanup 2026-05-05: bulk OHLC (1.8GB) + trades (406MB) deletados (regeneráveis via Dukascopy se reativar).

### Former long_term_portfolio/global_factor_tilt_loop 📚 FOLDED INTO RSC
- `long_term_portfolio/` and `global_factor_tilt_loop/` were folded into
  `studies/return_stacked_core/`. Their key reports, plots, source ledgers and
  importable helpers now live under `history/`, `legacy_algorithms/` and the RSC
  Python modules.
- Preserved conclusions include old B4 `25/25/25/25`, B4+evo02 `70/30`, HAA+Gold
  Sharpe frontier, HAA+ZROZ CAGR frontier and annual-DARF lineage. No deploy
  authorization: GA/LETF-derived sleeves remain research-only until hard gates clear
  `[advances_fin_ml, p.196-202]`, `[advances_fin_ml, p.208-211]`.

### LETF rotation studies -> migrated to letf-lab
- `studies/lrs/`, `studies/letf_rotation_hunt/` and `studies/spy_leveraged_rotation_hunt/` were extracted to `/var/www/victor/finances/letf-lab` on 2026-05-23.
- `market-lab` no longer has canonical local copies of those study trees. Use `MIGRATED.md` for the moved inventory, import rewrites, known residual runtime path references and validation notes.
- Historical references in this document before the spin-off remain research history only. For current LETF CLI/webapp work, use `letf-lab`.

### studies/day_swing_strategy_hunt/ 🛑 CLOSED / DEAD-END
- Initial A-E cycle closed with no winner; later closed-state verification iterations kept the hunt shut. Reopen only with explicit user request plus a new multi-asset literature thesis or reliable carry/rates data `[advances_fin_ml, p.208-211]`.

### studies/weekly_momentum/ 🛑 CLOSED 2026-05-10
- Veredito final: nenhum deploy. `studies/weekly_momentum/FINAL_REPORT.md` consolida a evolução por fase, plots finais contra SPY e rejeição após Tiingo backfill, PIT expandido, Phase 5 ADV5M e gates DSR/PBO/bootstrap `[advances_fin_ml, p.208-211]`.
- Melhor lead S&P 500 pós-Phase 4: `lb80/k5/SMA250` com CAGR 19.36%, MDD -37.77%, Sharpe 0.817 vs SPY Sharpe 0.884; falha DSR (p=0.418) e bootstrap low CAGR (-2.10%).
- Melhor branch all-stocks ADV5M pós-Phase 5c: CAGR 48.09%, MDD -36.26%, Sharpe 1.184, mas falha PBO (0.579) e bootstrap low (-3.11%); otimizações locais melhoraram PBO apenas sacrificando DSR/bootstrap/performance.
- 2026-05-12 post-close ETF focus: runner `scripts/etf_focus_evolution.py` testou rotação ETF-specific (`lb80/100/126`, `k=10/20`, `SMA200/250`, defensivos `cash/IEF/ZROZ`). Universo completo WF melhorou para CAGR 11.29%, MDD -26.03%, Sharpe 0.712 vs SPY Sharpe 0.619, com PBO 0.313 e bootstrap low +0.06%, mas falha DSR (`p=0.152`). Sem ETFs alavancados/inversos cai para CAGR 6.65%, Sharpe 0.647 e falha DSR/bootstrap. Branch encerrada: research-only, dependente de alavancados, sem novos sweeps locais sem hipótese nova `[advances_fin_ml, p.208-211]`, `[advances_fin_ml, p.273-275]`.
- Estrutura limpa em 2026-05-10: relatórios em `studies/weekly_momentum/reports/`, evidências pequenas em `evidence/`, plots finais em `plots/final/` e comparação Phase 5 ADV5M em `plots/phase5/`; bulk generated artifacts removidos (~437 MB → ~3.3 MB).
- Código importável preservado na raiz (`core.py`, `data.py`, `reporting.py`); runners/análises em `scripts/`; `REPORT_SPEC.md` preservado. Novos bundles gerados continuam fora do registro canônico final.

### studies/qld_nasdaq_ath_gate/ 🌱 QUICK DIAGNOSTIC
- Novo estudo rápido para regra QQQ/QLD: risco em `QQQSIM?L=2` quando `QQQSIM` fecha acima de `85%` do high-watermark das últimas `46` semanas; caso contrário `CASHX`.
- Dados testfol.io long-history para `QQQSIM`, alavancagens via sintaxe `?L` (`QQQSIM?L=2`→`QLDSIM`, `QQQSIM?L=3`→`TQQQSIM`) e `CASHX`; sinal semanal aplicado no próximo pregão para evitar same-close look-ahead.
- Run `results/default/` (1986-11-14..2026-04-17): CAGR 23.42%, MDD -63.67%, Sharpe 0.744 vs QQQSIM CAGR 14.66%, QQQSIM?L=2 CAGR 17.44% e QQQSIM?L=3 CAGR 12.28%.
- Report/plots: `studies/qld_nasdaq_ath_gate/results/default/report.md`, incluindo equity, drawdown, signal line, rolling Sharpe e rolling windows 1/3/5/10y.

### studies/technical_signal_vote_hunt/ 🛑 CLOSED / RESEARCH-ONLY LETF-ADJACENT
- Estado consolidado: nenhum winner honesto. T3d-K2/iter030 seguem como anchors históricos, mas os artefatos canônicos de LETF agora vivem em `/var/www/victor/finances/letf-lab`; runners residuais que dependem de iter030/T3d-K2 precisam ser redirecionados antes de uso. Ver `MIGRATED.md` e `reports/long_term_strategy_review/REPORT.md`.
- Novo estudo para generalizar a T3d-K2 em grids `n` sinais / `k` votos, com branches nativas SPY→SSO/UPRO e QQQ→QLD/TQQQ.
- Stage 1 close-only usa testfolio long-history e sinais baseados em preço; runners em `runners/run_stage1_close_only.py` e `runners/run_stage1_close_only_fast.py` geram rankings, benchmarks nativos e importância de indicadores.
- Run exploratório inicial lento `max_n=2` gerou 4.356 configs em `results/stage1_close_only/`.
- Runner NumPy rápido validado em 2026-05-11: `max_n=5` gerou **5.471.268 configs** em `results/stage1_close_only_fast/`; top preliminar QQQ→QLD usa `n=5/k=4` com `EMA200 + EMA250 + MACD + ROC20 + ROC60` (Sortino 1.3375, CAGR 30.21%). Busca exata `n=1..33` é inviável (**566.9 bilhões** de configs antes de gates).
- GA runner adicionado em `runners/run_stage1_ga.py` para busca ampla monitorável por geração; smoke `QQQ→QLD`, population 24 × 5 generations passou e escreveu `results/stage1_ga/QQQ_QLD_2x_seed7/`.
- Stage 1 deep-dive report adicionado em `reports/stage1_top_strategies/`: seleciona top-3 por branch/risk-on do grid `max_n=5`, gera plots de equity, relative equity, drawdown, rolling CAGR e rolling Sortino. Top QQQ→QLD `n=5/k=4` (`EMA200 + EMA250 + MACD + ROC20 + ROC60`) tem Sortino 1.3375 / CAGR 30.21% vs iter030-like QQQ→QLD Sortino 1.0581 / CAGR 27.64%.
- Stage 1 validation completa (12 candidatos, bootstrap 2.000, DSR `n_trials=5.471.268`) fechou **0/12 pass**: todos passaram OOS/FWD/WF/bootstrap, mas todos falharam DSR (`p=0.1890..0.4631`, gate `<0.05`) e PBO diagnóstico do painel top-k (`0.8095..0.9921`, gate `<0.5`). Veredito: leads econômicos in-sample, nenhum winner honesto `[advances_fin_ml, p.208-211]`, `[advances_fin_ml, p.222-223]`. Report: `studies/technical_signal_vote_hunt/reports/stage1_validation/REPORT.md`.
- Pós-validação, GA QQQ→QLD seed43 (1.024.000 avaliações) encontrou incumbent in-sample mais forte `n=7/k=5` (`SMA10 + SMA20 + EMA100 + EMA200 + EMA250 + ROC20 + ROC60`): Sortino 1.3776 / CAGR 32.79% / MDD -56.38%. Local-search exato de 1 edição (`216` subsets, `1.531` configs) confirmou que a base vence todos drops/adds/swaps por fitness; isso é apenas discovery e exige nova validação com trial accounting acumulado. Report: `studies/technical_signal_vote_hunt/results/stage1_local_search/QQQ_QLD_2x_ZROZSIM_local/REPORT.md` `[advances_fin_ml, p.222-223]`.
- Pós-GA/local-search validation dos 2 incumbents QQQ (`QQQ→QLD n=7/k=5` e `QQQ→TQQQ n=8/k=6`) com DSR `n_trials=7.554.054` também fechou **0/2 pass**: ambos passaram OOS/FWD/WF/bootstrap e PBO diagnóstico de painel branch (`0.2302`), mas falharam DSR (`p=0.1444` e `0.2260`, gate `<0.05`). Report: `studies/technical_signal_vote_hunt/reports/stage1_ga_local_validation/REPORT.md` `[advances_fin_ml, p.196-202]`, `[advances_fin_ml, p.222-223]`.
- Stage 2 Tiingo OHLC implementado em `runners/run_stage2_tiingo_ohlc.py`: usa Tiingo real-inception, ajusta OHLC via `adj_close/close`, e testa replay + neighborhood OHLC de uma edição. Primeiro diagnóstico QQQ: `QQQ→QLD + ZROZ` replay caiu para Sortino 1.2775 / CAGR 26.31%; melhor OHLC local `+atr14_pct_lt_3` ficou só marginalmente melhor. `QQQ→TQQQ + ZROZ` replay ficou Sortino 1.2337 / CAGR 34.75%; melhor OHLC local `-roc120_gt_0+atr14_pct_lt_3` subiu para Sortino 1.3307 / CAGR 38.77% / MDD -62.06%. Ainda é discovery local, não validação honesta; precisa runner Stage 2 de WF/OOS/FWD/bootstrap/PBO/DSR antes de qualquer claim `[quant_trading_chan, p.37]`, `[trading_systems_methods, p.732-733]`, `[advances_fin_ml, p.208-211]`.
- Overnight Stage 2 exact grids revisados em `reports/stage2_grid_overnight/REPORT.md`: 115.029.492 configs persistidos (`QQQ+ZROZ n<=5`, `QQQ+BIL n<=5`, `SPY+ZROZ n<=5`, `QQQ→TQQQ+ZROZ n=6`). Top QQQ→TQQQ+ZROZ `n=5/k=2` marcou CAGR 62.19% / Sortino 1.6280 / MDD -62.37%; top QQQ→QLD+ZROZ CAGR 40.94%; top SPY→UPRO+ZROZ CAGR 50.07%. Recomputação pandas independente reproduziu CAGR/MDD, sem bug imediato de cálculo ou same-close lookahead identificado. Porém extra lag derruba QQQ→TQQQ+ZROZ para ~15% CAGR, e o trial count acumulado mínimo já é >=122.583.546; veredito continua discovery-only, suspect-by-default, aguardando validação Stage 2 `[advances_fin_ml, p.196-202]`, `[advances_fin_ml, p.222-223]`.
- Stage 2 grid operacional atualizado em 2026-05-12: runner agora suporta `CASH_USD`, `--extra-lag-days` e exclusão default de sinais redundantes dentro da mesma config (MACD equivalente e thresholds nested). Grids QQQ `CASH_USD + extra_lag_days=1 + n<=5` completos: `QQQ→TQQQ` testou 7.067.694 configs e topou `n=5/k=3` com Sortino 1.4124 / CAGR 53.00% / MDD -51.03%; `QQQ→QLD` testou 7.067.694 configs e topou `n=5/k=2` com Sortino 1.3181 / CAGR 34.54% / MDD -53.09%. Estimativas QQQ QLD+TQQQ deduped: `n<=6` 115.350.684, `n<=7` 761.622.940, `n<=8` 4.183.106.396; exact `n<=7/8` não é rotina, GA/beam search é o caminho prático. PSR pode entrar como diagnóstico, mas DSR segue hard gate pelo mandate `[advances_fin_ml, p.196-202]`, `[advances_fin_ml, p.222-223]`.
- Stage 2 window audit: a comparação QQQ→TQQQ vs QQQ→QLD era contaminada por janela (`QLD` incluía 2008; `TQQQ` começa em 2010). Re-rodando QLD desde 2010-02-12, o top vira a mesma regra do TQQQ (`sma100_gt_sma250|roc10_gt_0|roc120_gt_0|stochrsi14_gt_50|rv21_pct_lt_70`, `k=3`) com Sortino 1.4209 / CAGR 36.26% / MDD -37.54%; TQQQ na mesma regra fica Sortino 1.4124 / CAGR 53.00% / MDD -51.03%. Testfolio 1986+ é possível apenas para essa regra close-only e enfraquece o resultado: `QLDSIM+CASHX` CAGR 17.06% / MDD -76.73%, `TQQQSIM+CASHX` CAGR 18.90% / MDD -93.95%. Report: `studies/technical_signal_vote_hunt/reports/stage2_window_and_testfolio_audit/REPORT.md` `[advances_fin_ml, p.208-211]`.
- Comparativo dedicado T3d-K2 vs iter030 vs configs selecionadas criado em `studies/technical_signal_vote_hunt/reports/t3d_iter030_topk_comparison/REPORT.md`, com tabelas e plots de equity/drawdown/rolling windows. Leitura: Cfg01-Cfg05 dominam proxies QLD T3d/iter030 no Tiingo pós-2010, mas as configs close-only replicáveis perdem amplamente para T3d-K2 e iter030 no painel testfolio 1986+; logo são leads modernos/regime-specific, não substitutos robustos dos anchors long-history `[leverage_for_the_long_run, p.5-7]`, `[advances_fin_ml, p.222-223]`.
- Próxima prioridade definida pelo usuário em 2026-05-12: procurar primeiro uma estratégia melhor que T3d-K2/iter030 no testfolio 1986+ price-only, confirmar depois no Tiingo 2006/2010+, e só então rodar GA/beam Tiingo `n>=8`. Runner Stage 3 adicionado em `runners/run_stage3_testfolio_price_ga.py`: GA `n>=8` sobre sinais close-only, fitness relativa aos anchors T3d-K2/iter030-like e outputs monitoráveis em `results/stage3_testfolio_price_ga/`. Smoke `QQQ→QLD+ZROZSIM`, population 12 × 2 generations, `signal_limit=12`, passou. Primeiros GAs reais: `QQQ→QLD+ZROZSIM seed42` avaliou 6.250 candidatos únicos e topou `n=8/k=6` com Sortino 1.3747 / CAGR 32.06% / MDD -57.81%, batendo anchors branch-native T3d-K2 e iter030-like in-sample; `QQQ→TQQQ+ZROZSIM seed42` avaliou 5.576 únicos e topou `n=8/k=6` com Sortino 1.2680 / CAGR 40.28% / MDD -64.24%, também batendo anchors branch-native. Veredito: leads long-history promissores, mas discovery-only até validação WF/OOS/FWD/bootstrap/PBO/DSR com trial accounting acumulado `[advances_fin_ml, p.196-202]`, `[advances_fin_ml, p.222-223]`.
- Validação Stage 3 completa em `reports/stage3_validation/REPORT.md`: top-200 QLD + top-200 TQQQ, DSR `n_trials=122.644.986`, bootstrap 2.000, PBO branch-risk-on. Veredito **0/400 honest PASS**. Todos passaram OOS/FWD/bootstrap; QLD teve 191/200 WF pass e TQQQ 200/200 WF pass; todos falharam DSR (`p=0.3118..0.5915`) e PBO (`0.9881` QLD, `0.9643` TQQQ). A regra compartilhada `px_gt_sma10|px_gt_ema200|px_gt_sma250|px_gt_ema250|roc20_gt_0|roc60_gt_0|roc120_gt_0|rsi14_gt_50`, `n=8/k=6`, fica como challenger fixo para confirmação Tiingo, não winner `[advances_fin_ml, p.196-202]`, `[advances_fin_ml, p.208-211]`.
- Confirmação/expansão Tiingo da regra Stage 3 em `reports/stage2_tiingo_validation/REPORT.md`: runner local Tiingo agora suporta `--extra-lag-days`, `--start-date`, `--end-date`; novo validator `runners/validate_stage2_tiingo_candidates.py` aplica OOS/FWD/WF/bootstrap/PBO/DSR em candidatos Tiingo. Com `CASH_USD + extra_lag_days=1`, top-40 QLD same-window + top-40 TQQQ fecharam **0/80 pass**. Todos passaram OOS/FWD/bootstrap, mas falharam DSR (`p=0.9324..0.9875`) e PBO (`0.6905/0.6746`); WF passou 26/40 QLD e 30/40 TQQQ. Os melhores locais (`ATR14% < 5`, `k=1`) pioram drawdown e não batem os Stage 2 leads anteriores; logo o caminho promissor é GA/beam Tiingo controlado a partir dos winners Stage 2, não expansão local dessa regra `[quant_trading_chan, p.37]`, `[advances_fin_ml, p.208-211]`.
- Validação honesta dos Stage 2 operacionais em `reports/stage2_tiingo_validation/REPORT.md`: top-200 `QQQ→QLD+CASH_USD lag1 from2010` e top-200 `QQQ→TQQQ+CASH_USD lag1`, DSR `n_trials=136.784.374`, fecharam **0/400 PASS**. Ambos passaram OOS/FWD/bootstrap 200/200; WF 187/200 QLD e 186/200 TQQQ; todos falharam DSR (`p=0.8339..0.9541`) e PBO (`0.6230/0.6349`). Econômicamente continuam os melhores leads Tiingo modernos, mas não são winners honestos `[advances_fin_ml, p.196-202]`, `[advances_fin_ml, p.222-223]`.
- Follow-up Stage 3 com fitness `--pbo-proxy-weight 0.75` adicionado em `runners/run_stage3_testfolio_price_ga.py`: proxy individual de estabilidade por janelas, não PBO real. Runs seed52 QLD/TQQQ também fecharam **0/400 PASS**; PBO não melhorou (QLD 0.9960, TQQQ 0.9365). Conclusão: problema é cluster de candidatos técnicos similares; sem hipótese nova/diversidade explícita, mais GA local tende a só adicionar trials correlacionados `[advances_fin_ml, p.208-211]`.
- Research direction review consolidado em `reports/research_direction_review/REPORT.md`: T3d-K2 e iter030 seguem como anchors long-history; Stage 2 QLD/TQQQ cash+lag1 seguem apenas como challengers modernos; próximo avanço recomendado é Stage 4 regime-gated Tiingo/testfolio bridge ou seleção com diversidade de painel, não novos grids/GA locais irrestritos na mesma família `[advances_fin_ml, p.196-202]`, `[advances_fin_ml, p.208-211]`.
- Stage 4 regime-gated bridge implementado em `runners/run_stage4_regime_bridge.py` com visão **economic-first**: PBO/DSR ficam fora de `economic_pass` por pedido do usuário, mas `mandate_pass` permanece falso sem esses gates. Primeira rodada QQQ `CASH_USD + extra_lag_days=1` mostrou que o base vote sem gate continua melhor: QLD Sortino 1.4209 / CAGR 36.26% / MDD -37.54%, TQQQ Sortino 1.4124 / CAGR 53.00% / MDD -51.03%, ambos com 100% dos rolling 3/5/10/15y positivos no Tiingo 2010+. Gates simples de drawdown 252d passam mas não melhoram; MA/vol/relative-strength falham WF. Report: `studies/technical_signal_vote_hunt/reports/stage4_regime_bridge/REPORT.md` `[leverage_for_the_long_run, p.5-7]`, `[leverage_for_the_long_run, p.13]`.
- Comparativo equity/benchmark do Stage 4 criado em `reports/stage4_equity_benchmark_comparison/REPORT.md`: contra SPY buy-hold, QQQ como proxy NDX, T3d-K2/iter030 proxies Tiingo QLD/CASH e anchors canônicos fatiados na mesma janela, a regra base QLD termina 17.14× SPY / 8.89× QQQ e a TQQQ termina 111.17× SPY / 57.66× QQQ no Tiingo 2010+. Anchors canônicos fatiados 2010+ continuam fortes: T3d-K2 CAGR 27.89%, iter030 CAGR 34.27%; o valor baixo anterior era proxy, não canônico. Plots de equity e relative equity salvos em `plots/`.
- Reprodução Stage 4 testfolio 1986+ criada em `reports/stage4_testfolio_reproduction/REPORT.md` e `_zroz/`: a regra é reproduzível por ser close-only, mas perde para os anchors canônicos long-history. Com `ZROZSIM`, QLD fica CAGR 19.38% / MDD -70.07% e TQQQ CAGR 21.48% / MDD -87.69%, contra T3d-K2 CAGR 31.06% / MDD -64.50% e iter030 CAGR 36.66% / MDD -55.48%. Conclusão: Stage 4 é superior no Tiingo moderno, não no painel 1986+ `[advances_fin_ml, p.208-211]`.
- Teste `Stage4 inside iter030` criado em `runners/run_stage4_inside_iter030.py` e `reports/stage4_inside_iter030/REPORT.md`: preserva o shell defensivo do iter030 e usa Stage4 apenas como gate de upgrade QLD→TQQQ. Resultado: `inside_rearm_or_stage4` aumenta CAGR para 38.46% e terminal para 492k× vs iter030 36.66% / 290k×, mas piora MDD para -64.54% e Sortino para 1.0838; `inside_rearm_and_stage4` preserva MDD mas reduz CAGR/Sortino. Iter030 segue melhor risk-adjusted, Stage4 turbo é performance-first `[advances_fin_ml, p.31-34]`.
- Busca `Stage4 Pareto Hybrid Search` em `runners/run_stage4_pareto_hybrid_search.py` testou 225 híbridos economic-first com shell iter030, gates turbo Stage4, pesos parciais TQQQ e LRS 1.00/1.10/1.20. Resultado: **0 strict Pareto** vs iter030 em CAGR+Sortino+MDD. Trade-off dominante: reduzir LRS/TQQQ melhora Sortino/MDD mas perde CAGR; adicionar turbo Stage4 melhora CAGR/terminal mas piora drawdown/Sortino. Report: `reports/stage4_pareto_hybrid_search/REPORT.md`.
- GA constrangido `run_stage4_hybrid_ga.py` testou 623 genes únicos de meta-gates Stage4 dentro do shell iter030 (population 72 × 35, seed42). Resultado: convergiu de volta para iter030 (`rearm`, peso TQQQ 1.00, LRS1.20); **0 strict Pareto** no top-20. Leitura: GA ajuda como confirmação/exploração, mas a gramática atual de filtros Stage4 não encontra híbrido que melhore simultaneamente CAGR, Sortino e MDD.
- GA amplo de parâmetros iter030 em `runners/run_iter030_param_ga.py` rodou smoke economic-first (population 36 × 8, seed43), avaliou 195 genes únicos e achou **6 strict Pareto** no top-30. Melhor candidato: `ga_s100_250_vw21_vt0.40_ar30_k2_rearm_T20D120_w1.00_lrs1.20_g0.25_rv60_0.70`, CAGR 39.01% vs iter030 36.66%, Sortino 1.2074 vs 1.2073, MDD igual -55.48%, terminal 577.8k× vs 290.6k×. Diagnóstico em `reports/iter030_param_ga/CANDIDATE_DIAGNOSTICS.md`: melhora rolling 5/10/15y mínimo, piora levemente rolling 3y mínimo. Validação honesta em `reports/iter030_param_ga/validation/REPORT.md` fechou **0/7 PASS**: todos passam OOS/FWD/WF/bootstrap, mas falham DSR (`p=0.2985..0.3711`) e PBO panel dos 195 genes (`0.619`). Veredito: sensibilidade econômica útil, não winner `[advances_fin_ml, p.196-202]`, `[advances_fin_ml, p.208-211]`.
- Sensibilidade final `T/D` em `runners/run_iter030_td_sensitivity.py` testou grade pré-especificada `T={20,35,45}` × `D={60,90,120}` e comparou a "nova winner" econômica contra T3d-K2, iter030, Stage3 shared, Stage4 base e Stage4-inside. `T20D120` é o melhor por CAGR/terminal (39.01%, 577.8k×), mas `T20D90` é melhor balanceado por Sortino (1.2278) com CAGR quase igual (38.99%) e mesmo MDD. Conclusão: ganho vem de trigger mais rápido + rearm mais longo; como a validação formal já falhou DSR/PBO, parar esta branch e manter iter030 como anchor. Report/plots: `reports/iter030_td_sensitivity/REPORT.md`.
- Revisão consolidada 2026-05-13 em `reports/long_term_strategy_review/REPORT.md`: após rerun do comparativo T/D, auditoria de tabelas e gate-check manual de `T20D90`, a melhor referência de longo prazo do estudo permanece **iter030 canonical QLD/ZROZ LRS1.20**. `T20D90` é o melhor challenger balanceado local e `T20D120` o melhor performance-first, mas ambos ficam research-only por DSR/PBO; Stage4 QLD/TQQQ continua modern-regime monitor, não anchor 1986+ `[advances_fin_ml, p.196-202]`, `[advances_fin_ml, p.208-211]`.
- Audit 2026-05-13 em `reports/underlying_signal_audit/REPORT.md`: a família iter030/T20D90/T20D120 usa **QLD como ativo de sinal**, não QQQ. Forçar o mesmo algoritmo a usar `QQQ` como sinal degrada fortemente: iter030 CAGR 36.66%→28.38% e MDD -55.48%→-91.09%; T20D90 CAGR 38.99%→29.18% e MDD -55.48%→-93.72%; T20D120 CAGR 39.01%→30.22% e MDD -55.48%→-94.10%. Conclusão: classificar como **LETF self-regime**, não LRS-underlying puro `[leverage_for_the_long_run, p.5-7]`, `[leverage_for_the_long_run, p.13]`.
- Repair GA evolutions 2026-05-13 em `reports/repair_ga_evolutions/REPORT.md`: 6 evoluções sequenciais completadas, >=82.623 candidatos únicos nos manifests finais. QQQ-signal foi reparado de MDD ~-91/-94% para leads com MDD -32/-40% e CAGR 27-32%, mas abaixo do QLD-self-signal. Melhor discovery econômico é `evo04_qld_simplify` (`QLD_s100_200_vw21_vt0.50_ar30_k2_T15D120_w1.00_lrs1.10_g0.50_rv90_0.80`): Sortino 1.3751, CAGR 43.42%, MDD -52.73%. Ainda é discovery-only; próxima etapa é validação pequena com DSR/PBO acumulados `[advances_fin_ml, p.222-223]`.
- Long-term portfolio iter 058, now preserved in `studies/return_stacked_core/history/b4_evo02_70_30/`, testou 6 carteiras com rebalanceamento mensal, aporte inicial USD 10k e aportes mensais USD 1k. A escolha de pesquisa atual era **70% B4 + 30% evo02**: CAGR 20.01%, MDD -21.60%, Sharpe 1.2038 e XIRR 19.74% vs B4 puro CAGR 14.62%, MDD -28.38%, Sharpe 1.0234 e XIRR 14.17%. `75% B4 + 25% evo02` ficou como alternativa mais conservadora (CAGR 19.15%, MDD -22.58%); `75% B4 + 25% evo01` teve maior Sharpe (1.2272). Research-only; GA sleeves ainda exigem validação hard antes de qualquer claim `[advances_fin_ml, p.196-202]`, `[advances_fin_ml, p.208-211]`.

### studies/bestfolio_meta_wf_hunt/ 🛑 CLOSED 2026-04-29
- iter 001 dead-end: walk-forward solver sobre sleeves gate-screened com Sharpe density tight = noise (turnover 177-222%/ano sem edge).
- Lesson preservada (anti-pattern documentado).

### studies/_shared/ 🔒 CRITICAL INFRA
- `tax_engine.py` preserva o AnnualDarfEngine canônico Lei 14.754 derivado da antiga linhagem `global_factor_tilt_loop`. Não tocar.

### studies/_archive/ 📦 PRESERVED
- strategy_hunt_loop (78 iters, 1 strict winner iter 079); gold_swing_loop (25 iters, 0 winner, structural ceiling); ema_sma_threshold (Phase 1 legacy).

---

## Engine status (pós-2026-04-22)

| Componente | Status | Ref |
|---|---|---|
| `src/market_lab/backtest/strategies/plano_a_leveraged_rotation.py` | ✅ HONEST (fix 7b90a8f) | `tests/test_plano_a_lookahead_bias.py` |
| `letf_rotation.py` | ✅ NEVER HAD BUG | F1 audit |
| Cross-lib validation (bt/vectorbt/backtrader/numpy) | ✅ 1e-6 concordance | `studies/_archive/phase_3_5f/reports/v2_l2_gayed_redo/cross_lib_report.md` |
| Pytest baseline | ✅ **969 collected** (updated 2026-05-08 T5 expansion) | — |

---

## Regras invioláveis (lembrete operacional)

Sumário do mandate (`docs/investment-mandate.md` é canônico):

1. **Capital:** 100% Plano C; A/B/D = 0% DORMANT.
2. **CAGR/MDD = tiers warning-only** (mandate §2.2/§2.3 desde 2026-04-22).
3. **Plano A reativação:** multi-asset + sweep leverage + staging USD 500-1k → 5-10k.
4. **Plano B reativação:** Inter Internacional + Gayed-anchored + CPCV/PBO/15% DARF.
4b. **Plano D reativação:** literatura/regime novos exigidos.
5. **Gates hard-block (zero bypass):** PBO<0.5, DSR p<0.05, WF≥6/8, single-block OOS, FWD stress, bootstrap 99.9% CI low > 0, cross-lib ±3pp CAGR.
6. **Threading model live (Phase 4)** pausado.
7. **Dynamic sizing preservado.**

**Citação obrigatória** em toda decisão: `[book.slug, p.X]`. 33 livros em `books/summaries/`, skill em `knowledge/SKILL.md`.

---

## Referências cruzadas

- **Mandate canônico:** `docs/investment-mandate.md`
- **Setup + arquitetura:** `README.md`
- **Cleanup playbook:** `docs/CLEANUP.md`; logs forenses `docs/CLEANUP_2026-04-24_LOG.md` + `docs/CLEANUP_2026-05-05_LOG.md`
- **Histórico público:** `docs/PROJECT_HISTORY.md`
- **Knowledge base:** `books/MAPPING.md` + `knowledge/SKILL.md`
- **Convenções:** `CLAUDE.md`

---

## Changelog

- **2026-06-08/09:** `lrs/` Phase 5 RSC overlay rebuilt-sleeve rodada e ajustada
  para o RSST tracking proxy `SPY + 70% DBMF + 30% KMLM - CASHX?E=-2`. Standalone
  LRS segue reprovado pela Phase 4 (`0/6` gates); com o novo proxy, `0/9` overlays
  passam strict. Maior CAGR de overlay: `70% RSC / 30% T3d-K2`, CAGR `14,24%`, MDD
  `-48,65%`; RSC reconstruído: CAGR `12,40%`, MDD `-30,76%`. Também foi gerado
  `lrs/TOP20_BY_CAGR.md`, ranking de `4183` rows por CAGR sem filtro de drawdown;
  top row `QQQ L3.00 / ZROZ / RV63<=40% / lag5`, CAGR `25,84%`, MDD `-71,05%`.
  Sem deploy e sem mudança no mandate; próximo passo exigiria escolha explícita,
  tax/friction account-level + gates.
- **2026-06-05:** comparativo Reddit leveraged portfolios vs RSC-US adicionado em
  `studies/return_stacked_core/us_core/reddit_leveraged_backtests/`. Resultado:
  4-3-2-1 2x margin é o melhor backtest bruto, `mine` QQQ/TLT/GLD 3x é o melhor
  lead Reddit sem caixa negativo explícito, mas RSC-US `35/40/25` permanece a
  âncora implementável por construção return-stacked e comportamento pós-2010;
  sem deploy e sem mudança no mandate.
- **2026-06-05:** factor-sleeve diagnostics para AVUV/SCV e SPMO sobre o proxy
  efetivo do RSC-US: nenhum variant domina o baseline; fator aumenta terminal
  marginalmente, mas reduz Calmar e torna o portfolio mais equity-like. Sem
  mudança no core.
- **2026-06-05:** screen de universo ETF return-stacked/capital-efficient em
  `studies/return_stacked_core/us_core/return_stacked_etf_universe/`: nenhum ETF
  novo substitui RSC-US `35/40/25`; `CTAP` e `RSSX` seguem opcionais, enquanto
  `MATE`/`JPFP`/`SPXP` ficam em watchlist por histórico curto. Sem mudança no
  mandate.
- **2026-06-03:** cleanup parcial de consolidação: `studies/SUMMARY.md` criado como ledger compacto de estudos/estratégias, docs públicos apontam para ele, broad-grid CSVs gerados de `spy_sso_upro_replacement` foram removidos após preservação das conclusões, e seis árvores antigas (`b4-v2/`, `static_spy_beater_portfolio/`, `spy_beater_hunt/`, `spy_beater_hunt_v2/`, `long_term_portfolio/`, `global_factor_tilt_loop/`) foram consolidadas em `studies/return_stacked_core/` sem mudar o mandate.
- **2026-05-13:** `studies/technical_signal_vote_hunt/` ganhou revisão consolidada de melhor estratégia de longo prazo. Rerun do T/D sensitivity e gate-check manual de `T20D90` confirmam a conclusão: iter030 canonical segue como anchor; `T20D90/T20D120` são sensibilidades econômicas, não winners; mandate §1 inalterado.
- **2026-05-13:** `technical_signal_vote_hunt` adicionou audit de ativo de sinal: QLD-signal é parte essencial da performance da família iter030; variantes QQQ-signal mantêm CAGR alto mas sofrem MDD >90%, então a família deve ser rotulada como LETF self-regime, não LRS-underlying puro.
- **2026-05-13:** `technical_signal_vote_hunt` adicionou repair GA suite com 6 evoluções. QQQ-signal repair encontrou alternativas conceitualmente limpas com MDD controlado; QLD-self-signal gerou novo challenger econômico `evo04`, mas sem validação honesta ainda.
- **2026-05-13:** `studies/spy_leveraged_rotation_hunt/` bootstrapped e rodou baseline + GA discovery inicial para `SPY/SSO/UPRO`. Baselines simples não passam o screen econômico vs SPY; GA encontrou 5/6 melhores candidatos por evolução que batem SPY em CAGR, Sharpe/Sortino e MaxDD, liderados por `SSO` self-signal `evo05`, mas todos seguem discovery-only pendentes de OOS/FWD/WF/bootstrap/PBO/DSR.
- **2026-05-12:** `studies/weekly_momentum/` ganhou e encerrou evolução ETF-specific pós-fechamento. `focused_full_universe` melhorou o WF para CAGR 11.29% / Sharpe 0.712 vs SPY 10.63% / 0.619, mas falha DSR (`p=0.152`); `focused_no_leveraged` caiu para CAGR 6.65% e falha DSR/bootstrap. Conclusão: lead diagnóstico dependente de alavancados, sem autorização de deploy e sem novos sweeps locais sem hipótese nova `[advances_fin_ml, p.208-211]`, `[advances_fin_ml, p.273-275]`.
- **2026-05-13:** antigo `studies/spy_beater_hunt_v2/` bootstrapped como novo hunt ativo para tentar bater SPY buy-and-hold com gates hard-block de overfit. O estudo depois fechou 10/10 hipóteses sem winner e foi incorporado a `studies/return_stacked_core/EVOLUTION.md`; sem deploy e sem mudança no mandate `[advances_fin_ml, p.196-202]`, `[advances_fin_ml, p.208-211]`, `[advances_fin_ml, p.222-223]`.
- **2026-05-14:** `studies/success_trading_strat/` bootstrapped para aplicar o workflow Neurotrader/Masters de IS MCPT + WF MCPT sobre novas hipóteses de trading. Como ação urgente de último dia Tiingo, o estudo registrou audit/backup final: ETF/crypto/forex/NDX100 refresh, SPX500 best-effort parcial, 1.755 tickers no manifesto e backup `data/tiingo_backup_20260514-0311.tar.gz`; sem claim de estratégia e sem mudança no mandate `[testing_tuning, p.318-320]`, `[advances_fin_ml, p.196-202]`.
- **2026-05-14:** `success_trading_strat` completou iteração 002 infrastructure-only com scaffold reutilizável de IS MCPT/WF-MCPT e testes focados. Próxima iteração pode testar a primeira família pequena pré-registrada; `cumulative_n_trials` segue 0.
- **2026-05-14:** `success_trading_strat` completou iterações 003-004 com duas famílias pequenas de estratégia. Ambas fecharam `fail`: SMA/momentum diário falhou PBO/MCPT; cross-sectional ETF momentum mensal passou PBO/DSR, mas falhou MCPT, Sharpe vs benchmark e FWD stress. `cumulative_n_trials=8`; mandate §1 inalterado.
- **2026-05-14:** `success_trading_strat` completou iteração 005 com volatility-targeted static sleeves. Melhor sleeve (`35% SPY / 15% QQQ / 30% IEF / 20% GLD`, alvo vol 10%) melhorou Sharpe/MDD contra 60/40, mas falhou IS MCPT (`p=0.12`), WF MCPT (`p=0.43`) e PBO (`0.657`). `cumulative_n_trials=12`; mandate §1 inalterado.
- **2026-05-14:** `success_trading_strat` completou iteração 006 com `RSI(2)` mean reversion em `SPY/QQQ`. Melhor config `qqq_rsi2_e5_x70` reduziu MDD para -16.09%, mas perdeu em CAGR/Sharpe para QQQ buy-and-hold e falhou IS MCPT (`p=0.05`) e WF MCPT (`p=0.35`). PBO (`0.214`) e DSR (`p=0.0441`) passaram com `cumulative_n_trials=16`; mandate §1 inalterado.
- **2026-05-14:** `success_trading_strat` completou iteração 007 como `data_blocked`: proxy de volatility-carry via `VIXY` foi pré-registrado, mas o arquivo `data/tiingo/daily/prices/VIXY.parquet` estava ausente. Por conservadorismo, `VXX` não foi substituído após o pré-registro; `n_trials=0`, `cumulative_n_trials=16`, mandate §1 inalterado `[testing_tuning, p.327-335]`.
- **2026-05-14:** `success_trading_strat` completou iteração 029 com filtro de correlação equity/Treasury e fechou `fail`: passou PBO/WF/OOS/FWD/cross-lib, mas falhou benchmark Sharpe, IS MCPT, WF MCPT, DSR e bootstrap. `cumulative_n_trials=100`; próximo passo é iteração 030 final com mecanismo novo ou closure/audit.
- **2026-05-14:** `success_trading_strat` completou iteração 008 com proxy de volatility-carry via `VXX` confirmado. Melhor config `vxx_neg21_spy` melhorou levemente Sharpe/MDD contra SPY, mas perdeu CAGR e falhou IS MCPT, WF MCPT, PBO e DSR; `n_trials=4`, `cumulative_n_trials=20`, mandate §1 inalterado `[systematic_trading, p.119]`, `[testing_tuning, p.318-320]`, `[advances_fin_ml, p.208-211]`.
- **2026-05-14:** `success_trading_strat` completou iteração 009 com EWMAC multi-asset ETF. Melhor config `ewmac_16_64_risk3` teve CAGR positivo e MDD menor, mas perdeu Sharpe para equal-weight `SPY/QQQ/TLT` e falhou IS MCPT, WF MCPT, PBO e DSR; `n_trials=4`, `cumulative_n_trials=24`, mandate §1 inalterado `[systematic_trading, p.118-119]`, `[testing_tuning, p.318-320]`, `[advances_fin_ml, p.208-211]`.
- **2026-05-14:** `success_trading_strat` completou iteração 010 com pares ETF z-score market-neutral. Melhor config `tlt_ief_z60_e1` teve CAGR 0,69%, Sharpe 0,183 e MDD -12,05%, mas perdeu para SHV em Sharpe e falhou IS MCPT, WF MCPT, DSR e bootstrap; PBO passou (`0,429`). `n_trials=4`, `cumulative_n_trials=28`, mandate §1 inalterado `[algo_trading_chan, p.65-66]`, `[algo_trading_chan, p.71-73]`, `[testing_tuning, p.318-320]`.
- **2026-05-14:** `success_trading_strat` completou iteração 011 com VIX-managed exposure. Melhor config `qqq_vix15_w21` teve CAGR 14,10%, Sharpe 0,945 e MDD -27,01% vs QQQ buy-hold CAGR 18,94%, Sharpe 0,945 e MDD -35,12%; passou IS MCPT, WF MCPT, PBO, DSR, WF/OOS/bootstrap/cross-lib, mas falhou FWD stress 63d (`-1,18%`). `n_trials=4`, `cumulative_n_trials=32`, mandate §1 inalterado `[paper.bozovic_2024_vix_managed, §methodology]`, `[advances_fin_ml, p.222-223]`.
- **2026-05-14:** `success_trading_strat` completou iteração 012 como stress VIX-managed. O floor de 50% em QQQ (`qqq_vix15_w21_floor50`) elevou CAGR/Sharpe para 16,57%/0,954, mas não resgatou a família: IS MCPT falhou (`p=0,030`), PBO falhou (`0,729`) e FWD 63d continuou negativo (`-0,41%`). `n_trials=4`, `cumulative_n_trials=36`; sem winner e sem mudança no mandate `[testing_tuning, p.327-335]`, `[advances_fin_ml, p.208-211]`.
- **2026-05-14:** `success_trading_strat` completou iteração 013 com Donchian trend BTC/ETH. `eth_don20` foi forte em Sharpe e anti-overfit diagnostics, mas falhou WF positivo mínimo e FWD 63d; `n_trials=4`, `cumulative_n_trials=40`; sem winner e sem mudança no mandate `[paper.zarattini_2025_crypto_trends, §methodology]`, `[advances_fin_ml, p.196-202]`.
- **2026-05-14:** `success_trading_strat` completou iteração 025 com breadth de mercado current-constituent. Melhor `spy_breadth_sma63_gt55` reduziu MDD vs SPY, mas perdeu Sharpe e falhou IS MCPT, PBO e DSR; `n_trials=4`, `cumulative_n_trials=88`; sem winner e sem mudança no mandate `[trading_systems_methods, p.548-549]`, `[advances_fin_ml, p.208-211]`.
- **2026-05-14:** `success_trading_strat` completou iteração 026 com apetite a risco por liderança setorial. Melhor `spy_xly_xlp_m126` reduziu MDD vs SPY, mas perdeu Sharpe/CAGR e falhou IS/WF MCPT, PBO e DSR; `n_trials=4`, `cumulative_n_trials=92`; sem winner e sem mudança no mandate `[trading_systems_methods, p.13]`, `[advances_fin_ml, p.208-211]`.
- **2026-05-14:** `success_trading_strat` completou iteração 014 com crypto volatility-targeted momentum. `btc_mom63_vt20` resolveu o FWD 63d e melhorou Sharpe/MDD vs BTC buy-hold, mas falhou IS/WF MCPT, PBO e WF mínimo; `n_trials=4`, `cumulative_n_trials=44`; sem winner e sem mudança no mandate `[systematic_trading, p.40]`, `[testing_tuning, p.318-320]`, `[advances_fin_ml, p.208-211]`.
- **2026-05-14:** `success_trading_strat` completou iteração 016 com filtro de apetite a risco por crédito `HYG/IEF`. O melhor caso reduziu drawdown, mas perdeu Sharpe/CAGR para SPY e falhou IS/WF MCPT, PBO, DSR e bootstrap; `n_trials=4`, `cumulative_n_trials=52`; sem winner e sem mudança no mandate `[systematic_trading, p.42]`, `[trading_systems_methods, p.13]`, `[advances_fin_ml, p.208-211]`.
- **2026-05-14:** `success_trading_strat` completou iteração 018 com overlay Ehlers de ciclo/Trend Mode. O melhor caso bateu QQQ em Sharpe e reduziu MDD, mas falhou IS/WF MCPT; `n_trials=4`, `cumulative_n_trials=60`; sem winner e sem mudança no mandate `[rocket_science, p.99-100]`, `[testing_tuning, p.318-320]`.
- **2026-05-14:** `success_trading_strat` completou iteração 019 com rotação carry/yield usando dividend yield e term spreads. A melhor config melhorou CAGR vs 60/40, mas falhou Sharpe, MCPT, PBO, DSR e FWD; `n_trials=4`, `cumulative_n_trials=64`; sem winner e sem mudança no mandate `[systematic_trading, p.119]`, `[testing_tuning, p.318-320]`.
- **2026-05-14:** `success_trading_strat` completou iteração 020 com sazonalidade turn-of-month em `SPY/QQQ`. A melhor config reduziu drawdown, mas perdeu Sharpe/CAGR para SPY buy-hold e falhou MCPT, PBO e DSR; `n_trials=4`, `cumulative_n_trials=68`; sem winner e sem mudança no mandate `[trading_systems_methods, p.479-481]`, `[testing_tuning, p.318-320]`.
- **2026-05-14:** `success_trading_strat` completou iteração 021 com decomposição intraday/overnight em `SPY/QQQ`. A melhor config `qqq_close_to_open` melhorou Sharpe/MDD vs QQQ buy-hold, mas falhou IS/WF MCPT e DSR; `n_trials=4`, `cumulative_n_trials=72`; sem winner e sem mudança no mandate `[paper.zarattini_2024_intraday_spy, §methodology]`, `[testing_tuning, p.318-320]`.
- **2026-05-14:** `success_trading_strat` completou iteração 022 com KAMA/Efficiency Ratio em `SPY/QQQ`. A melhor config `qqq_kama_er20` reduziu MDD vs QQQ buy-hold, mas perdeu Sharpe e falhou IS/WF MCPT e DSR; `n_trials=4`, `cumulative_n_trials=76`; sem winner e sem mudança no mandate `[trading_systems_methods, p.10-11]`, `[trading_systems_methods, p.780-782]`.
- **2026-05-14:** `success_trading_strat` completou iteração 023 com confirmação OBV/volume em `SPY/QQQ`. A melhor config `qqq_obv21` bateu QQQ em Sharpe e passou PBO/DSR, mas falhou IS/WF MCPT; `n_trials=4`, `cumulative_n_trials=80`; sem winner e sem mudança no mandate `[trading_systems_methods, p.537]`, `[testing_tuning, p.318-320]`.
- **2026-05-14:** `success_trading_strat` ganhou review consolidado das 30 iterações em `reports/overnight_30_iter_review/` com tabelas, equity/drawdown, equity-over-SPY, rolling 1/3/5/10/15y e classificação `candidate_watchlist`. `PHASE2_INTRADAY_SWING_SPEC.md` orienta a próxima fase 15m/1h/1d e gold/XAUUSD; sem deploy e sem mudança no mandate.
- **2026-05-14:** `success_trading_strat` reorganizou iterações por fase: Phase 1 movida para `iters/phase01/`, Phase 2 preparada em `iters/phase02/`, com contador ativo resetado para 30 novas iterações e trial accounting cumulativo preservado em 100.
- **2026-05-12:** `studies/technical_signal_vote_hunt/` adicionou Stage 2 operacional com `CASH_USD`, `extra_lag_days` e dedupe de sinais redundantes; QQQ `n<=5` cash+lag1 completo para TQQQ/QLD gerou leads discovery-only, e estimativas mostram `n<=7/8` exato grande demais para rotina.
- **2026-05-12:** `studies/technical_signal_vote_hunt/` adicionou Stage 3 testfolio price-only GA para priorizar long-history 1986+ contra T3d-K2/iter030 antes de qualquer expansão Tiingo `n>=8`.
- **2026-05-12:** Stage 3 validation fechou 0/400 honest PASS após DSR/PBO; a regra compartilhada dos tops QLD/TQQQ segue apenas como challenger fixo para Tiingo.
- **2026-05-12:** Stage 2 Tiingo validation da regra Stage 3 também fechou 0/80 PASS; validator Tiingo dedicado foi adicionado e os leads Stage 2 anteriores seguem superiores.
- **2026-05-12:** Stage 2 operational top-200 validation fechou 0/400 PASS por DSR/PBO; Stage 3 PBO-proxy GA também não reduziu PBO.
- **2026-05-12:** `technical_signal_vote_hunt` consolidou direction review: sem winner honesto; interromper otimização local redundante e seguir apenas com hipótese nova de regime gate, diversidade de painel ou PSR diagnóstico.
- **2026-05-12:** Stage 4 regime-gated bridge economic-first rodou QQQ→QLD/TQQQ `CASH_USD lag1`; o base vote sem gate segue melhor e passa OOS/FWD/WF/bootstrap/rolling-cycle diagnostics quando PBO/DSR são tratados como diagnóstico, não bloqueio.
- **2026-05-12:** Stage 4 ganhou comparação de equity/relative equity contra SPY, QQQ/NDX proxy, T3d-K2 proxy e iter030-like proxy.
- **2026-05-12:** Stage 4 foi reproduzido em testfolio 1986+; regra é válida tecnicamente mas não supera T3d-K2/iter030 canônicos long-history.
- **2026-05-12:** Stage4-inside-iter030 testado; melhora CAGR apenas com custo claro em drawdown/Sortino, então não domina iter030.
- **2026-05-12:** Pareto hybrid search testou 225 combinações Stage4/T3d/iter030; nenhuma bate iter030 simultaneamente em CAGR, Sortino e MDD.
- **2026-05-23:** `studies/lrs/` **Phase 17 cross-lib check FECHA 5/5 GATES §5 PARA EQ5_3x**. Lib `ta` (https://github.com/bukosabino/ta) instalada via `uv pip install ta`; `ta.trend.sma_indicator` / `ta.trend.ema_indicator` aplicados a 9 single-asset strategies + EQ5_3x portfolio em cohort 1987-2026. **Single-asset: Δ CAGR = 0.000pp exato** (9/9 strategies), zero sinal disagreements em todos os ~9k-35k bars — implementação custom numericamente identical à `ta`. **EQ5_3x portfolio: Δ −1.593pp** (cumulativa de EMA initialization × 5 legs × monthly rebalance × 40y; dentro do threshold ±3pp). **19/19 strategies passam mandate §5 cross-lib gate**. **EQ5_3x agora cumpre TODOS os 5 gates §5**: PBO 0.041 ✅ + WF 5/6 ✅ + Bootstrap 99.9% low +10.83% ✅ + DSR p=0.011 ✅ + Cross-lib Δ=−1.59pp ✅. **Primeira strategy em todo o estudo LRS (Phase 0-17) a fechar 5/5 gates §5 mandate**. Mandate §1 maintenance mode ainda preserva capital 100% Plano C — strategy fica "fully validated" mas dormant até revisão de mandate (6-12 meses). Report: `studies/lrs/phases/phase_17_cross_lib/report.md`.
- **2026-05-23:** `studies/lrs/` **Phase 16 correção GLD@2x UGL (no real 3× gold ETF exists)** — refator `recipe_max_leverage()` em `phase_10_portfolio/run.py`; propaga para Phase 12/13/14/15. Antes EQ5_3x usava GLD synth 3× hypothetical; agora usa UGL 2× (max-leverage achievable). **Números corrigidos**: EQ5_3x CAGR 31.21% (era 32.71%), MDD −61.0%, Sortino 1.418, PBO 0.041 ✅, bootstrap CI [+10.8%, +54.1%] ✅, WF 5/6 ✅, **DSR p=0.011 ✅**. EQ4_3x (no QQQ, 1980+): CAGR 33.17% (era 34.53%), Sortino 1.534, DSR p=0.0005 ✅ — sem mudança qualitativa, ainda mais robust que EQ5. Real-ETF OOS Phase 13 já usava UGL 2× (correto desde sempre); CAGR real 21.85% inalterado; production estimate w/ friction 10bps ~19.2% CAGR. **Nenhum gate §5 mudou de status** — ambos EQ5/EQ4 ainda passam 4/5 (PBO, WF, bootstrap, DSR). Strategy doc atualizada `studies/lrs/EQ5_3X_STRATEGY.md`.
- **2026-05-23:** `studies/lrs/` **FECHAMENTO FINAL: Phase 13-15 fecham 4/5 gates §5 para EQ5_3x + descobrem EQ4 alternative superior**. **Phase 13 real-ETF OOS expandido** (yfinance, 5 families × 16y OOS post-2010): EQ5_3x real CAGR +21.85%, MDD -60.2%, Sortino 1.105 vs synth same-cohort +27.18% (Δ-5.33pp por leverage decay empírico). Per-family: SPY/UPRO tracks perfeito (-0.13pp), QQQ/TQQQ surpreende +1.20pp, IWM/TNA -3.06pp, XLK/TECL -3.26pp, GLD/UGL 2× -3.77pp. **Phase 14 friction-aware portfolio backtest** (per-leg switch + monthly rebalance 5-25 bps): EQ5_3x post-2010 baseline +28.42% → 10bps +25.72% (-2.70pp drag) → 25bps +21.77% (-6.65pp). **Production estimate realistic** (real-ETF + 10bps friction): **~+19.15% CAGR/yr** com Sortino ~1.10. **Phase 15 DSR + EQ4 alternative**: DSR (Bailey-Lopez-de-Prado 2014, N_trials=30k aggregate) **EQ5_3x p=0.008 ✅**, EQ4 (no QQQ, 1980+) **p=0.0005 ✅** + Sortino 1.534 + CAGR 34.53% — **EQ4 supera EQ5** em janela estendida. Single-asset que passam DSR: IWM-EMA50/TNA (p=0.002), XLK-SMA85/TECL (p=0.043). SPY/QQQ/GLD single falham DSR (consistente Phase 7 PBO). **EQ5_3x agora cumpre 4 dos 5 gates §5: PBO ✅ (0.039), WF ✅ (5/6), bootstrap ✅ ([+11.8%, +56.4%]), DSR ✅ (0.008)**. Sobra apenas cross-lib pandas-ta (deferred). EQ5_3X_STRATEGY.md doc operacional canônica criada. Mandate §1 maintenance mode inalterado. Reports: `studies/lrs/phases/phase_{13_real_etf_all,14_portfolio_friction,15_dsr_eq4}/` `[advances_fin_ml, p.222-223]` (DSR), `[leverage_for_the_long_run, p.21]` (decay).
- **2026-05-23:** `studies/lrs/` **Phase 12 cross-study comparison rodada** vs `studies/letf_rotation_hunt/` (T3d-K2 e Iter030). T3d-K2 recriado importando `studies.letf_rotation_hunt.core.signals` (vote-K=2 sobre SMA250, SMA100, vol21<40%, AR(1)>0); QLD/TQQQ via testfolio QLDSIM/TQQQSIM puxado fresh (alias QQQSIM?L=2/3); rodado em nosso `simulate_rotation_with_annual_tax`. Iter030 não recriado (state machine complexa T35D60+LRS1.20), métricas gross reportadas + tax adjustment via T3d-K2 ratio (0.905). **Cohort comum 1987-2026 (~39.4y)**. **Headline (br_lei_14754, BR investor)**: EQ5_3x Sortino **1.448 (BEST)**, CAGR 32.7%, MDD −61.7%; Iter030 est. Sortino 1.253, CAGR 33.2%, MDD −55.5%; T3d-K2 recreated Sortino 1.03, CAGR 24.0%, MDD −84%; EMA255/IEF (TQQQ) Sortino 0.99, CAGR 26.5%. **EQ5_3x bate Iter030 em Sortino** (diversificação cross-asset cancela vol per-leg); Iter030 ganha CAGR por margem mínima (+0.5pp). T3d-K2 recreated subperforma reportado (gap CAGR ~7pp, Sortino ~0.3) provavelmente por cohort 1987+ vs 1986+ + sutilezas fee/synth. Nosso QQQ Phase-5 (EMA255/IEF) bate T3d-K2 em CAGR br_tax (+26.5% vs +24.0%) com Sortino próximo. Mandate §1 inalterado, sem capital implications. Report: `studies/lrs/phases/phase_12_cross_study/{report.md, comparison_matrix.csv}` `[advances_fin_ml]`, T3d-K2 origem `studies/letf_rotation_hunt/configs/iter_014_t3d_vote_of_k.yaml`.
- **2026-05-23:** `studies/lrs/` **LINHA LRS CONCLUÍDA com survivor honesto identificado (Phase 6-10 marathon)**. Pipeline completo em ~30 min compute. **Phase 6**: IWM/XLK/GLD deep dives parallel (9312 reports em 4.7 min) — IWM EMA50/ZROZ TNA CAGR +40.6%, XLK SMA85/ZROZ TECL +33.5%, GLD EMA290/ZROZ UGL +16% mas score +0.58 (maior absoluto). **Phase 7 validação honesta** (PBO/WF/bootstrap nos top-50 panels de Phase 1+5+6, 20 painéis total): **0/20 passam todos os gates** — Phase 1 SPY-SMA295 PBO=0.92, Phase 5 QQQ-EMA255 PBO=0.78, Phase 6 IWM PBO=0.13-0.19 (único <0.5 mas falha WF 5/7). Todos single-asset winners overfit. **Phase 8 friction**: SPY 3.8sw/y → −1.1pp CAGR @25bps; IWM 16sw/y → −5.6pp (alto turnover machuca). **Phase 9 real-ETF OOS 2010+ (yfinance)**: TQQQ EMA255/IEF real CAGR +27.3% vs synth +30.4% br_lei → leverage decay confirmado ~3pp/yr para 3× (`[leverage_for_the_long_run, p.21]`). **Phase 10 multi-asset portfolio**: 6 variants equal-weight + vol-weighted dos 5 winners. **🎯 EQ5_3x portfolio (equal-weight 5 underlyings × 3×) é o PRIMEIRO HONEST SURVIVOR de todo o estudo LRS**: CAGR +32.70% br_lei, MDD −61.7% (vs −78% a −96% individuais), final_score +0.6466 (maior do estudo). Mandate §5: **PBO=0.039 ✅** (12× margem vs 0.5), **WF 5/6 ✅** (83% vs 75% threshold), **bootstrap 99.9% CI [+11.8%, +56.4%] ✅** lower>0. Diversificação cross-asset cancela o overfit per-asset confirmado empiricamente. DSR e cross-lib não cobertos (consistente com phase-3 escopo). **Capital implications: ZERO**. Mandate §1 maintenance mode inalterado; Plano A/B/D dormant; Plano C 100% capital. LRS line **officially concluded** com survivor research-only identificado. Closing summary: `studies/lrs/CLOSING_SUMMARY.md` `[advances_fin_ml, p.208-211, ch.14]`, `[leverage_for_the_long_run, p.16, p.21]`.
- **2026-05-23:** `studies/lrs/` **phase-5 QQQ deep dive (Phase 1-style sweep)** rodado: mirror exato da Phase 1 mas com QQQSIM como underlying e QLD (2×) / TQQQ (3×) como on-legs synthesizadas via `synthesize_letf_returns(fee=0.95%)`. Grid 2 filtros × 97 lookbacks (20-500) × 4 off-legs × 2 on-legs × 2 tax = 3104 reports em 3.5 min. **Findings**: QQQ tem recipe COMPLETAMENTE DIFERENTE do SPY. (1) **EMA vence SMA** universalmente (todos top-10 são EMA — oposto da Phase 1 onde SMA > EMA). NASDAQ-100 tech-vol pede filtro mais responsivo. (2) **Lookback ótimo ~220-255** (centro 245), não 295. Plateau estável de 40 pontos. (3) **Off-leg IEF e ZROZ empatam** — IEF é top max-score, ZROZ é top mean-score. ZROZ não é universal como off-leg; QQQ-vol cresce demais com long-duration. **Top winners** (br_lei_14754, 100% win 20y): QLD `EMA245/IEF` → +0.412, CAGR +25.31%, sw/y=5.6; TQQQ `EMA255/IEF` → +0.506, CAGR +34.41%, sw/y=5.5. Comparação Test 1 (Phase 4, só SMA): TQQQ SMA250 +0.45 vs Phase 5 EMA255 +0.55 — ganho de +0.10 ao incluir EMA. Discovery-only, mandate §1 maintenance mode inalterado. Report: `studies/lrs/phases/phase_5_qqq_deep_dive/report.md` `[leverage_for_the_long_run, p.13, p.14, p.16]`.
- **2026-05-23:** `studies/lrs/` **phase-4 testes rodado**: dois experimentos discovery-only não-validatórios. **Test 1 (multi-asset robustez)**: SMA(lookback)/ZROZ sobre 6 underlyings (SPY/QQQ/IWM/XLK/DIA/GLD) × 3 leverages × 8 lookbacks = 288 reports. **SMA295 NÃO é universal**: SPY/GLD pedem 250-300, QQQ→250, IWM/XLK/DIA pedem 100 (sectoral/small-cap precisa de LB curto). Maior achievement inesperado: **GLD 2× SMA300/ZROZ** com final +0.54, CAGR +15.6%, 89% win 5y (filtro funciona excepcionalmente em commodity). Maior CAGR absoluto 3×: SPY SMA295 +31.8% (3.8 sw/y) > XLK SMA100 +32.7% (10.8 sw/y, alto turnover compromete edge real). **Test 2 (metamorfose adaptive selector)**: 24 combos (L × A) × 6 painéis vs static SMA200/SMA295. **Metamorfose ganha em SPY 1×** (+0.044 a +0.052 vs SMA295 nos 2 tax scenarios) mas **perde em SSO/UPRO leveraged** — leverage amplifica custo de lookback switches. Avg picked lookback ≈ 245-265 (não 295!) sugere SMA250 standalone pode ser melhor OOS optimum no 1×. L=24m / A=12m é o sweet spot. Veredito: **stop here** consistente com maintenance mode; SMA295 standalone permanece a config canônica do LRS para LETF, mas há evidência indireta de que SMA250 é mais robusto OOS no 1×. Mandate §1 inalterado, sem capital implications `[leverage_for_the_long_run, p.16, p.21]`, `[advances_fin_ml, p.222-223]`. Report: `studies/lrs/phases/phase_4/{summary,test_1_multi_asset/report,test_2_metamorfose/report}.md`.
- **2026-05-22:** `studies/lrs/` **phase-3 multi-indicador GA + validação rodado**: 6 GAs paralelos (pop=200, gens=60, seed=42) sobre genome `(indicators × params, k, h)` com 12 indicadores no pool e voting k-of-n com hysteresis assimétrica. 7 WF folds (train 10y/test 5y/step 5y). Compute total ~10 min. Validação pós-GA: PBO (CSCV 16 blocos, 2000 splits) + block bootstrap (10k reps, block 21d, 99.9% CI) + WF per-fold + sub-period. **Veredito honesto: nenhum multi-indicador bate SMA295 standalone + passa todos os gates para investor BR realista**. 3 de 6 painéis falham PBO (SSO/br_lei PBO=0.92, UPRO/tax_free=0.55, UPRO/br_lei=0.69) — GA encontra optima IS que não generalizam. Único survivor honesto: SSO/tax_free (PBO=0.31, WF 5/7, CAGR +25.4% vs SMA295 +21.6% = +3.8pp) — mas tax_free é irrelevante para BR. Painéis SPY passam todos gates mas top-1 underperforma SMA295 por 2-3pp. Winners GA têm padrão consistente: n=7-8, k=5-6 (essencialmente AND), h=2-4 (hysteresis material) — confirma que para suprimir whipsaw precisa de wide ensemble + high agreement threshold + hysteresis. Mandate §5 parcial (DSR + cross-lib deferred), maintenance mode §1 inalterado, Plano A/B/D dormant `[advances_fin_ml, p.208-211]`, `[leverage_for_the_long_run, p.13]`. Report: `studies/lrs/phases/phase_3/{report,summary}.md`. **LRS frontier consolidado em SMA295/ZROZ standalone**.
- **2026-05-22:** `studies/lrs/` **phase-2 indicator screening rodado**: 12 indicadores em 3 famílias (trend / momentum / vol) × seus param grids = 116 configs únicas × 3 on-legs (SPY/SSO/UPRO) × ZROZ off-leg × 2 cenários fiscais = 696 score reports. Veredito: **SMA295/ZROZ continua intocável** como single-indicator. Top-1 por indicador no SSO/BR-tax: sma295 +0.347 (phase-1 winner reproduzido exato), golden(100/295) +0.340, ema50 +0.296, donchian200 +0.296, roc252 +0.267, ichimoku +0.255, rsi14 +0.109, supertrend −0.04, bb_width −0.07, atr_pct −0.10, macd −0.18, vix_sma −0.28. **Família trend domina** (5 de 6 top); momentum mixed (só ROC passa); **volatilidade falha completamente standalone**. Sub-period split (1980-2000/2000-2010/2010-2026) flagou donchian e roc como regime-dependent (spread >0.6); golden100/295 é o mais estável (spread 0.30, 0.5 switches/y). VIXSIM (1990+) puxado fresh para o parquet cache. Phase-3 candidatos promovidos: sma295, golden100/295, donchian200, roc252, ichimoku, ema-longo (validação PBO/WF/bootstrap obrigatória). Mandate §1 inalterado `[leverage_for_the_long_run, p.13]`, `[trading_systems_methods]`, `[advances_fin_ml, p.208-211]`. Report: `studies/lrs/phases/phase_2/{report,summary}.md`.
- **2026-05-22:** `studies/lrs/` phase-1 sweep rodado: 2 filtros (SMA/EMA) × 57 lookbacks (20-300 passo 5) × 4 risk-off (CASH/GLD/IEF/ZROZ) × 2 on-legs (SSO/UPRO) × 2 cenários fiscais = 1.824 score reports. Resultado discovery-only com finding dominante: **a escolha do risk-off importa muito mais que filtro ou lookback**. ZROZ vence todos os 4 painéis com `SMA295/ZROZ` (final tax-free +0.43 / taxed +0.35 vs phase-0 CASH winner +0.12 / +0.02). CASH (default do phase-0) é o pior off-leg em todos os painéis. 100% das janelas 20y são vencedoras nos top configs — sinal forte mas com exposição grande a multiple-testing; phase-2 deve validar top-N via walk-forward + bootstrap. Mandate §1 inalterado, sem winner/deploy `[leverage_for_the_long_run, p.13]`, `[leverage_for_the_long_run, p.14, Table 6]`, `[advances_fin_ml, p.208-211]`.
- **2026-05-22:** `studies/lrs/` ganhou framework de scoring padronizado e re-rodou phase-0 sobre era moderna (1980-01-02 → 2026-05-21, 11.692 bars). Cada estratégia recebe dois scores em paralelo: tax-free e BR Lei 14.754/2023 (15% anual sobre ganho líquido realizado, com compensação de prejuízos indefinida art. 6°). Janelas rolling 1/3/5/10/15/20y passo mensal × score composto signed-tanh (40% terminal_excess, 25% time_above_excess, 20% sortino, 15% calmar) × agregação 0.60·mean + 0.40·p25 × pesos crescentes por horizonte (1y=5% até 20y=25%). Resultado discovery-only: tax-free vencedor LRS-UPRO (+0.124), tax-aware vencedor B&H SSO (+0.031) — a tributação anual por turnover faz holding superar rotação leveraged. Sem winner/deploy; mandate §1 inalterado `[leverage_for_the_long_run, p.13]`, `[leverage_for_the_long_run, p.21]`, `docs/investment-mandate.md` §1.
- **2026-05-22:** `studies/lrs/` (Leveraged Rotation Strategies) bootstrapped como restart limpo da linhagem `letf_rotation_hunt`/`spy_leveraged_rotation_hunt`, em layout `phases/phase_N/`. Phase 0 inicial (commit 3067ed2) rodou baseline em 141 anos testfol.io — depois substituído pelo framework de scoring acima.
- **2026-05-12:** GA constrangido de híbridos Stage4/iter030 convergiu para o próprio iter030; nenhum meta-gate Stage4 virou strict Pareto.
- **2026-05-12:** GA amplo dos parâmetros iter030 encontrou 6 candidatos strict Pareto em smoke pequeno; melhor candidato `T20D120` melhora CAGR/terminal e rolling 5/10/15y, mas validação formal fechou 0/7 PASS por DSR/PBO.
- **2026-05-12:** Sensibilidade final `T/D` confirmou que `D90/D120` com `T20` explica o ganho econômico; `T20D120` vence por CAGR, `T20D90` por Sortino, mas ambos ficam research-only e a branch deve parar.
- **2026-05-12:** added `docs/plans/2026-05-12-ai-etf-exit-monitoring.md`, an educational operational plan for monitoring a tactical AI/semis ETF sleeve (`DRAM`, `SMH`, `AIS`, `SOXL`, `TQQQ`, `POW`) with yellow/red exits, profit-taking, allocation critique and a proposed Python monitor. This does not override maintenance mode or mandate §1.
- **2026-05-09:** `studies/letf_rotation_hunt/` ganhou suplemento QQQ/NDX para responder benchmark criticism: top-20 original reavaliado contra `QQQSIM`, sem reotimização; winner T3d sma250/100 permanece #1 por robustez composta vs QQQ.
- **2026-05-09:** `studies/letf_rotation_hunt/` ganhou loop pós-fechamento isolado em `runs/post_close/`, com state próprio, limite de 50 iters, critério `beats_winner` congelado e trial accounting global para DSR.
- **2026-05-09:** `studies/letf_rotation_hunt/` consolidou relatório loop 001-010. Iters 009-010 bateram o winner T3d-K2 pelo critério congelado; iter 010 é o melhor research beater (Sortino 1.4670, score 81.5), sem autorização de deploy.
- **2026-05-10:** `studies/letf_rotation_hunt/` rodou Phase 3 performance-first (iters 011-020). Iter 012 foi o primeiro strict-superset CAGR+Sortino; iter 017 virou melhor research incumbent balanceado (CAGR 32.66%, Sortino 1.4030, terminal 1.61× T3d-K2), ainda sem deploy.
- **2026-05-10:** `studies/letf_rotation_hunt/` concluiu Phase 4 focused loop (iters 021-030). Iter 030 `T35D60 + LRS1.20` virou novo research winner pós-fechamento (Sortino 1.3839, CAGR 36.68%, terminal ~5.4× T3d-K2, PBO 0.0357), documentado em `reports/POST_CLOSE_LOOP_REPORT.md`; segue sem deploy por score <90 e mandate §1.
- **2026-05-10:** `studies/letf_rotation_hunt/` adicionou iter 031 para testar proxy sem margem `80% TQQQ + 20% CASHX` com tributação anual de 15% sobre lucro líquido realizado, comparando também T3d-K2 taxada e SPY/NDX buy-hold sem venda. Proxy annual-tax bate T3d-K2 taxada modestamente (25.05% vs 24.24% CAGR; terminal 1.299×), mas fica muito abaixo da iter 030 gross; veredito continua sem deploy.
- **2026-05-10:** `studies/letf_rotation_hunt/` adicionou iter 032 para comparar variantes tax-aware de underlying/risk-on. T3d-K2 com TQQQ melhora CAGR/terminal (27.88%, 3.194× taxed T3d-K2), mas com Sortino menor e MDD -70.74%; SPY/SSO e SPY/UPRO não competem.
- **2026-05-10:** `studies/letf_rotation_hunt/` consolidou a conclusão tax-aware da T3d-K2 em `reports/T3D_K2_TAX_AWARE_CONCLUSION.md`, separando ranking operacional simples/balanceado/performance-first/rejeitado sem mudar o mandate.
- **2026-05-09:** `studies/weekly_momentum/` bootstrapped for weekly cross-sectional momentum over cached Tiingo stocks/ETFs, then adjusted to an honest daily-bar timing model and standardized report bundle: Thursday signal, Friday sale, Monday/Tuesday buy via `settlement_delay_days`, outputs under `results/{variation}/{config_slug}/`.
- **2026-05-09:** `studies/weekly_momentum/` added controlled stock sweeps and walk-forward diagnostics over 200 configs per universe. S&P 500 WF: CAGR 42.30%, MDD -50.84%, Sharpe 1.216; full stock cache WF: CAGR 61.83%, MDD -60.52%, Sharpe 1.200. Verdict remains research-only pending PIT universe, costs and PBO/DSR/bootstrap.
- **2026-05-09:** `studies/weekly_momentum/` froze 4 deploy candidates and generated a comparable validation panel under `deploy_candidates/`; candidates remain research-only pending operational/statistical hard gates.
- **2026-05-09:** `studies/weekly_momentum/` added proxy transaction-cost, annual DARF and ADV20 liquidity stress to the deploy-candidate panel. Gross edge survives transaction-cost stress, but tax drag materially reduces fixed-candidate attractiveness.
- **2026-05-09:** `studies/weekly_momentum/` added required candidate plots plus first anti-overfit gate pass (PBO/DSR/OOS/bootstrap). Only `fixed_aggressive_sp500` passes this first statistical screen, still research-only.
- **2026-05-09:** `studies/weekly_momentum/` Phase 2 ran the fixed-aggressive neighborhood and filtered all-stocks exploratory WF. Fixed neighborhood is robust enough to continue; all-stocks remains exploratory after PBO/DSR failures.
- **2026-05-10:** `studies/weekly_momentum/` Phase 3 added approximate PIT S&P membership. Original fixed-aggressive lead weakened materially; `lb80_k5_sma200/sma250` remain the only worthwhile leads, still research-only.
- **2026-05-10:** `studies/weekly_momentum/` consolidated `STRATEGY_TESTED_SUMMARY.md` with all tested families, top-6 strategy comparison versus SPY and final non-deploy verdict.
- **2026-05-10:** `studies/weekly_momentum/` completed Phase 4 Tiingo survivorship audit/backfill and expanded-cache PIT rerun. Coverage improved, but `lb80/k5/SMA200-250` failed DSR/bootstrap and lost risk-adjusted appeal versus SPY; family stopped.
- **2026-05-10:** `studies/weekly_momentum/` added Phase 5 dynamic all-stocks WF branch with PIT tradability filters and SPMO/FMTM benchmarks. ADV5M is economically strong but fails PBO/bootstrap; branch remains research-only.
- **2026-05-10:** `studies/weekly_momentum/` finalized cleanup after closure: canonical reports moved to `reports/`, decision evidence to `evidence/`, final plots to `plots/final/`, and regenerable bulk outputs removed.
- **2026-05-09:** `studies/qld_nasdaq_ath_gate/` added as a quick diagnostic for QQQ 46-week high-watermark threshold gating into QLD/CASHX, then migrated to long-history testfol.io `QQQSIM` with `?L` leverage aliases (`QQQSIM?L=2/3`) and regenerated `results/default/`.
- **2026-05-11:** `studies/technical_signal_vote_hunt/` bootstrapped para buscar combinações `n`/`k` de sinais técnicos em branches SPY e QQQ. Stage 1 close-only gerou runner inicial (`max_n=2`, 4.356 configs), runner NumPy rápido (`max_n=5`, 5.471.268 configs), runner GA monitorável por geração, deep-dive report com plots dos top-3 por branch e validação completa. Veredito Stage 1: **0/12 honest PASS** após DSR global e PBO diagnóstico; Stage 2 Tiingo OHLC ficou especificado para implementação posterior.
- **2026-05-11:** `technical_signal_vote_hunt` adicionou GA longo + local-search QQQ→QLD pós-validação: novo incumbent in-sample `n=7/k=5` melhorou Sortino/MDD e venceu neighborhood exato de 1 edição, mas permanece não validado até nova rodada honesta com trials acumulados.
- **2026-05-08:** T5 expansion of `letf_rotation_hunt` completed (post-close methodology amendment). 20 new configs added (iters 022-025); DSR cumulative re-computed at N=426; KILL T5-expansion FIRES (best Sortino 1.1399 < 1.272); Track A winner confirmed. Pytest baseline updated to 969. §17 disclosure in STUDY_FINAL_REPORT.md. `studies/letf_rotation_hunt/` entry added to state.
- **2026-05-05:** refresh total. MAINTENANCE MODE consolidado; status de studies/ atualizado (myfxbook CLOSED 2026-05-04, spy_beater B4 deploy-ready, long_term_portfolio BLOCKED, factor_tilt FROZEN, day_swing bootstrap). Pytest baseline 813.
- **2026-04-23:** rewrite total após Phase 3.5f fechar sem winner. Plano A V2 encerrado; Plano B c06-c12 pausado.
- **2026-04-19:** versão inicial.

---

## 2026-05-23 — LETF rotation spin-off

The three LETF rotation studies (`lrs`, `letf_rotation_hunt`,
`spy_leveraged_rotation_hunt`) were extracted to a dedicated sibling
repository at `/var/www/victor/finances/letf-lab`. That repo combines
the CLI workbench (`studies/`) with a webapp (Angular 21 + FastAPI)
that monitors registered strategies, generates daily signals, and
emails alerts on swings.

See `MIGRATED.md` for the inventory of what moved vs what stayed.

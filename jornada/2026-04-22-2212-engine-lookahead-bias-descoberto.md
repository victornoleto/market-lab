# Engine lookahead bias descoberto — V2-L2 winner sob suspeita, plano de fix gerado

**Data:** 2026-04-22 22:12
**Sessão:** Phase 3.5f Stage A (validação cross-lib do Plano A V2-L2)
**Branch:** `phase3.5f/plano-a-v2-l2-cross-lib-redo-20260422`
**Pytest:** 914 green (baseline preservado)

---

## O que a sessão tentava fazer

A sessão abriu com tarefa direta: "validar cientificamente se o winner
V2-L2 Gayed `gayed_ema100_L2_off_gld` (Plano A) sobrevive cross-lib
limpa sobre a pipeline Tiingo-first consertada em 2026-04-21."

O plano aprovado pelo usuário era:

1. **Stage A** — replicar canonical sobre Tiingo current pipeline.
2. **Stage-2** — cross-source concordance via testfolio SSOSIM/QQQSIM/GLDSIM.
3. **Cross-lib** — replicar em bt/vectorbt/backtrader.
4. **Stage C** — janela sensibilidade 1986+.
5. Decidir: winner real ou artifact.

## O que deu certo primeiro

**Stage A (canonical Tiingo raw close):** reproduziu o baseline V2-L2
ao ponto decimal. Sharpe OOS 2.284 vs baseline 2.285, CAGR OOS 79.14%
idêntico, MaxDD −21.02% idêntico, n_switches 616 idêntico, median hold
6.0 dias idêntico. **Zero drift na engine**, zero regressão.

**Stage-2 (testfolio TR):** descobri que o baseline V2-L2 tinha
subestimado a performance real esperada. O runner original usava Tiingo
`close` raw (sem dividendos — drops de ex-div viravam perdas). Share
CFD da Pepperstone paga dividend cash adjustment, então o comportamento
correto é `adj_close` (TR). Quando rodei a mesma strategy com `adj_close`,
Sharpe OOS foi 2.433 / CAGR 87.44% — e bateu essencialmente perfeito com
testfolio SPYSIM/QQQSIM/GLDSIM (Sharpe 2.437 / CAGR 87.66%, Δ 0.004 Sharpe).

Dois achados até aqui (ambos positivos):
- Engine não tem drift desde a última rodagem.
- Cross-source (Tiingo adj_close vs testfolio) concorda perfeitamente.

Aqui a conversa virou pra escolha metodológica: manter `close` raw ou
migrar canonical pra `adj_close` TR (mais correto pra share CFD com
dividend pass-through). O usuário escolheu "siga sua sugestão" → rodar
cross-lib em raw primeiro (apples-to-apples com baseline), depois TR,
depois Stage C, depois decidir migração formal.

## Quando a sessão virou

No Task #5 (cross-lib), rodei o teste feeding as mesmas weights matrix
+ mesmos preços para bt, vectorbt, backtrader e um numpy reference
dot-product. Esperava concordância dentro de ±3pp CAGR.

**Resultado:** canonical CAGR 71% vs numpy/vbt/backtrader todos em
CAGR 15-21%. Diferença de ~50-70pp em CAGR por split. Fator de ~19,000×
em equity final ao longo de 25 anos.

Três libs independentes + uma reimplementação manual batendo entre si,
e apenas o canonical divergindo catastroficamente, é assinatura
inequívoca de bug na canonical.

## O diagnóstico

Olhei o loop em `plano_a_leveraged_rotation.py` e encontrei o padrão:

```python
for bar_i, ts in enumerate(common_idx):
    state = regime_df.iloc[bar_i][t]     # signal usa close[bar_i]
    new_w[k] = L * budget if state == "ON" else 0  # today's weight
    # ...
    per_asset = ret_vals[bar_i]           # today's return (close[i]/close[i-1]-1)
    on_ret = sum(new_w[:n_assets] * per_asset)   # w_i × r_i   ← LOOK-AHEAD
```

O `state` no bar `i` consome `close[i]`. O `ret` no bar `i` também.
Multiplicar "peso decidido por hoje" por "retorno que aconteceu hoje"
é equivalente a saber o resultado antes de apostar. Classic Oracle
trading.

**Convenção honesta:** `w_{i-1} × r_i` (peso decidido ontem, retorno
de hoje). Standard em qualquer backtest que separa decisão de execução.

Verificação numérica atômica com a mesma weights matrix:
- `w_i × r_i` (canonical): CAGR 71.16%, equity 660,440×.
- `w_{i-1} × r_i` (honest): CAGR 15.29%, equity 34.8×.
- Max abs daily return diff entre canonical e shift version: **0.126**
  (12.6pp num único dia — magnitude clássica de look-ahead em dias de
  regime flip).

## As ramificações (preliminares)

- **V2-L2 Plano A winner (Sharpe 2.28 / CAGR 79%)** é provavelmente
  artifact. CAGR honesto estimado 15-18% OOS após cost+swap — abaixo do
  CDI BR (~13-14%) num ativo alavancado 2×, ou seja, pior que Tesouro
  Selic sem risco.
- **Plano B V4 — Phase 3.5c cross-lib** reportou o mesmo padrão de
  divergência (canonical 37.9% vs libs 11.6%) e na época atribuímos a
  "dados sintéticos testfol.io proprietários". **Agora descoberto: o
  cross-lib estava correto o tempo todo.** A refutação de Plano B V4
  foi pelo motivo certo mas pelo argumento errado.
- **Phase 3.5d + 3.5e Plano B breadth hunt** (8+5 famílias, zero
  winners) rodou com engine buggada. Comparações "strategy vs SPY
  buy-hold" compararam `w_i × r_i` (biased) contra b&h (unbiased).
  Gates foram calibrados na linha errada. Alguns "DEAD" ends podem
  ter sido honest winners.
- **Phase 4.0 Index CFD validation** (Sharpe 2.400, CAGR 85.76%) —
  mesma engine, mesmo bias. Artifact também.
- **5 DEAD leads da Phase 3.5a-V2** (TSMOM, AFML, Carver, pairs,
  vol-breakout) compartilham engines de `src/ai_trade/backtest/strategies/`
  — alguns podem ter sido descartados em vão.

## Decisão do usuário

Usuário foi explícito na conversa:

> "Esse bug/erro é totalmente incompreensível. Ele deve ser corrigido
> imediatamente e TUDO relacionado a ele precisa ser recalculado/revisto.
> Nós precisamos analisar o que pode ter sido descartado em vão e
> principalmente o que está sendo considerado, que não era pra ser."

Também:

> "Seu foco é UNICAMENTE E EXCLUSIVAMENTE encontrar uma estratégia
> vencedora e estável para o nosso plano A."

Plano B fica em stand-by. Plano C não se mexe. Plano A é a prioridade
total; se nenhum lead sobrevive, escalação.

## O que foi entregue nesta sessão

1. **Diagnóstico técnico completo** com evidência numérica reprodutível
   em 3 libs independentes + numpy reference.
2. **Plano de execução detalhado** em `docs/plans/2026-04-22-engine-lookahead-fix-and-plano-a-winner-hunt.md`:
   - **F0** — 4 testes cirúrgicos confirmando o bug.
   - **F1** — inventário de todo código/report afetado.
   - **F2** — fix + testes anti-regressão, pytest green.
   - **F3** — re-validação honesta dos 6 V2 leads (não só V2-L2).
   - **F4** — documentação, mandate update, banners forenses nos
     reports históricos.
3. **Scripts reutilizáveis prontos** em `scripts/`:
   - `run_phase3_5f_stage_a.py` — Stage A 3 variantes (raw/adj/SIM).
   - `run_phase3_5f_cross_lib.py` — engine replication test 3 libs.
4. **Reports preservados** em `reports/phase_3_5f/v2_l2_gayed_redo/`:
   - `summary.json` + `report.md` — Stage A PASS (14/16 gates).
   - `cross_lib_summary.json` + `cross_lib_report.md` — o teste que
     expôs o bug.

Nada na main foi tocado. `memory.md`, `trial_count.json`, reports
históricos — tudo preservado. Branch isolada, pytest ainda 914 green.

## O que NÃO fizemos (deliberadamente)

- Não patchei engine. F2 é separada, em sessão nova com os testes
  cirúrgicos F0 já escritos e confirmando o bug.
- Não re-rodei nenhum lead V2 com engine honesta. F3 é a fase de
  re-validação.
- Não atualizei `docs/strategies/plano_a_v2_l2_gayed_cfd.md` — o
  banner de "REJECTED / HONEST NUMBERS" será escrito em F4 baseado no
  veredict de F3.
- Não rodei self_improve_loop.sh (instrução do usuário).

## Lição meta

Phase 3.5c já havia detectado a divergência (cross-lib 11.6% vs
canonical 37.9%) em 2026-04-20, exatos 2 dias atrás. Na época
diagnosticamos como "synthetic LETF data source issue". Se tivéssemos
investigado a hipótese "engine bug" em paralelo naquela sessão, a
descoberta teria sido antes — e Phase 3.5d/3.5e talvez nem tivessem
precisado rodar.

**Regra a internalizar:** quando cross-lib mostra >1pp CAGR divergência,
bug na engine é hipótese de primeira prioridade, empatada com
"data source divergence". Não pular pra conclusão fácil.

## Próximo passo concreto

Usuário vai iniciar sessão nova com o plano em
`docs/plans/2026-04-22-engine-lookahead-fix-and-plano-a-winner-hunt.md`.
Fase F0 primeiro (testes cirúrgicos), gates a cada fase, user reviews
verdict final de F3 antes de qualquer promoção de winner.

Objetivo da próxima campanha: **achar uma strategy vencedora e
estável para Plano A** — se V2-L2 honest passa, pronto; se não, 5
outros leads re-avaliados; se nenhum passa, escalação para V3 vs
abandono Plano A.

## Citações

- Two-stage replication + engine cross-check: `[advances_fin_ml, p.31-34]`
- PBO CSCV: `[advances_fin_ml, p.208-211]`
- Bootstrap 99.9% CI: `[advances_fin_ml, p.196-202]`
- Walk-forward 6/8 gate: `[advances_fin_ml, ch.11]`
- V2-L2 thesis source: `[leverage_for_the_long_run, Gayed, p.11-14]`
- Retail cost discipline: `[systematic_trading, Carver, p.185-188]`

## Links

- **Plano executável:** `docs/plans/2026-04-22-engine-lookahead-fix-and-plano-a-winner-hunt.md`
- Evidência técnica:
  - `reports/phase_3_5f/v2_l2_gayed_redo/report.md`
  - `reports/phase_3_5f/v2_l2_gayed_redo/cross_lib_report.md`
  - `reports/phase_3_5f/v2_l2_gayed_redo/summary.json`
  - `reports/phase_3_5f/v2_l2_gayed_redo/cross_lib_summary.json`
- Scripts:
  - `scripts/run_phase3_5f_stage_a.py`
  - `scripts/run_phase3_5f_cross_lib.py`
- Contexto histórico:
  - `jornada/2026-04-19/07-phase3.5a-v2-summary-WINNER-FOUND.md` — o
    "winner" sob suspeita.
  - `jornada/2026-04-20/03-phase-3-5c-cross-lib-exposed-baseline-mismatch.md`
    — o early warning que não foi escutado.
  - `jornada/2026-04-18/23-phase3.5a-v2-WINNER-humana.md` — narrativa
    original em linguagem humana do V2-L2 winner.

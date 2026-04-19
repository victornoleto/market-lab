# Bug crítico: TODOS os 3 winners falham com dados limpos — RETRATAÇÃO

**Verdict:** Os 3 "winners" (SPY/XLK/XLE Bollinger MR 1h) eram artefato de
bars sintéticos da Tiingo IEX em dias de mercado fechado (US holidays).
Após limpeza dos dados e re-validação, **0 strategies passam o gate**.

A demoção do EEM (iter 16) e Kalman (iter 13) permanece, mas pelos
motivos pelos certos agora — não pelos do report original.

---

## Como descobri

Task 1D (regime decomp por VIX quintile) inspecionou os trade returns
do XLK e mostrou trades com return > 100% em 3-4 dias. Uma rápida
análise de `entry_price` vs `exit_price` no parquet 1h mostrou: bars
em 2021-01-18 (MLK Day) com OHLC todos iguais a $127.54 — mesmo preço
RAW unadjusted que aparece no daily 2021-01-19 (que é a próxima sessão).

Tiingo IEX retorna 6 placeholder bars em dias de mercado fechado:
- volume = 0
- OHLC todos idênticos
- preço RAW (não adjusted) — porque o daily não tem aquela data, e o
  split-adjust silently falha de volta para ratio=1.0 (era o "latent
  bug" do audit Task 0A que eu subestimei)

Para tickers com split histórico (XLK ratio adj/raw ≈ 0.48, XLE ≈ 0.41),
esses bars sentam a 2× o preço das barras vizinhas. Strategy entra
quinta-feira ao close, segura o weekend + holiday, "sai" na segunda
no bar fake = +100% gain.

## Magnitude da contaminação (pré-cleanup)

Trades dos winners que fazem entry OU exit num US holiday + contribuição
ao retorno total:

| Ticker | n contam | % | retorno total | retorno contam | % do total |
|---|---|---|---|---|---|
| SPY | 8/217 | 3.7% | 80.8% | 36.2% | **44.8%** |
| XLK | 13/232 | 5.6% | 1603% | 1361% | **84.9%** |
| XLE | 9/215 | 4.2% | 1214% | 1080% | **89.0%** |

XLK e XLE eram **quase inteiramente** fake. SPY ~half.

## O que foi feito

### 1. Code fix em `tiingo_source.py`

Novo método `_filter_orphan_intraday_bars(ticker, df_intraday)` que
**dropa** bars cujo dia calendário não está no daily cache. Chamado em
`fetch()` antes do `_apply_split_adjust_from_daily`. Defesa
deterministica — usa daily como source-of-truth para "dia de mercado".

2 testes novos, 2 testes superseded (substituídos pelos novos):
- `test_iex_filters_orphan_holiday_bars_with_warning` — orphan dropped + warn
- `test_iex_no_filter_warning_when_all_intraday_dates_in_daily` — caminho normal
- removed: `test_iex_warns_when_daily_cache_lags_intraday_dates` (split-adjust fallback agora não dispara — orphans filtrados antes)
- removed: `test_iex_no_warning_when_daily_covers_all_intraday_dates` (caminho normal coberto pelo novo)

Tests: 515 verdes (mesmo total, +2 -2 net zero).

### 2. Cleanup script `scripts/clean_intraday_orphans.py`

Roda em loop por todos os 1h parquets, identifica bars com data não
presente no daily counterpart, dropa, atualiza manifest. Backup
automático (`.bak_orphan_clean_<ts>`) por arquivo. `--dry-run` opt-in.

Executado em produção: **12 tickers afetados, 4296 bars dropados**
(SPY 384, IWM 372, XLK/XLE/EEM/etc. 354 cada). Backup intacto se
precisarmos rollback.

### 3. Re-validação dos 3 winners

Re-rodados os grids iter 15 (`run_grid_bollinger_mr.py`) com run-id
`grid_bollinger_mr_<SYM>_1h_post_clean`. Resultado:

| Ticker | Best Sharpe (pre) | Best Sharpe (post) | PBO pre→post | DSR pre→post | WF pre→post | Verdict |
|---|---|---|---|---|---|---|
| SPY | 1.314 | **0.78** | 0.254 → 0.480 | 1/4 → 0/4 | 7/8 → 3/4 | FAIL DSR_ALL_FAIL |
| XLK | 1.930 | **0.75** | 0.004 → 0.631 | 4/4 → 0/4 | 4/4 → 2/4 | FAIL PBO+DSR+COMBINED |
| XLE | 1.584 | **0.42** | 0.206 → 0.786 | 3/4 → 0/4 | 3/4 → 1/4 | FAIL PBO+DSR+COMBINED |

Reports: `reports/grid_bollinger_mr_{SPY,XLK,XLE}_1h_post_clean/`.

**Nenhum dos 3 winners passa o gate com dados limpos.** O OOS hold-out
e Q1-2026 stress não foram re-rodados — sem grid pass não há candidato
para validar adicionalmente.

## O que isso retira

### Reports invalidados

- `reports/grid_bollinger_mr_spy_1h_8wf_20260415-235041/` (iter 5)
- `reports/grid_bollinger_mr_{XLK,XLE,EEM,EFA,XLF}_1h_iter15/`
- `reports/grid_bollinger_mr_DIA_1h_iter17/` (DIA já era FAIL, mas pelo motivo errado)

### Jornada entries afetadas (mantidas com nota de retratação)

- `2026-04-15-2350-bollinger-mr-1h-PASS.md` — RETRACTED
- `2026-04-16-0010-bollinger-mr-oos-2025-PASS.md` — RETRACTED
- `2026-04-16-0045-kalman-pairs-spy-iwm-PASS.md` — Kalman também usava
  os mesmos dados intraday; resultado provavelmente também tainted (mas
  já estava demoted em iter 13 por OOS FAIL, então nada muda na
  conclusão final). Adiciono nota.
- `2026-04-16-0059-bollinger-mr-2026q1-stress-test.md` — RETRACTED
- `2026-04-16-0100-bollinger-mr-sector-etfs-PASS.md` — RETRACTED
- `2026-04-16-0833-tiingo-cache-audit.md` — minha conclusão de "latent
  não-material" estava errada; adiciono addendum
- `2026-04-16-1230-bollinger-mr-mc-bootstrap.md` — TASK 1A — bootstrap
  CIs centradas em pontos contaminados; CIs não significam nada agora
- `2026-04-16-1300-bollinger-mr-overlap.md` — TASK 1B — correlations
  computadas com PnL contaminado; coverage ainda válida (entry timing
  dos trades não muda muito), mas magnitudes não

Memory.md vai ser atualizado pra refletir winner count = **0/10**.

## Por que o audit Task 0A (commit `adf067e`) errou

Foquei só no caso forward (intraday termina em 2026-04-15 mas daily
até 2026-04-14, gap de 1 dia). Não cobri o caso histórico — cada US
holiday ao longo de 5+ anos cria um orphan day no intraday cache. O
spec §3.3 disse "no silent fallback" mas implementei como `log.warning`
em vez de raise, achando que era um edge case raro.

O que deveria ter feito naquele audit:
1. Listar TODOS os orphan-intraday-days (não só os do final do range).
2. Para cada, conferir se o ticker tem split histórico (ratio adj/raw ≠ 1).
3. Se sim, sinalizar como CONTAMINATION ATIVA, não latent.

Lição: audits de cache devem cobrir o histórico inteiro, não só a
borda recente. O fix preventivo foi insuficiente. O fix corretivo
(filtro + cleanup) é o que efetivamente resolve.

## Próximos passos

**Task 1A-1H ficam suspensas até decidir o caminho.** Não faz sentido
fazer regime decomp / sizing sensitivity / GARCH variant em strategies
que não passam o gate inicial.

Opções para o user:

1. **Voltar a procurar winners do zero** com dados limpos. Re-rodar o
   universo testado nos iters 1-17, agora com cache limpa, ver se algum
   dos "FAIL" anteriores na verdade era PASS contaminado-ao-contrário
   (puxado pra baixo por bars fake no DSR).
2. **Pivotar pra outras estratégias** — daily long-history Ehlers,
   PEAD, GARCH-sized variants, etc.
3. **Re-pensar o framework** — talvez bar-by-bar 1h é hard demais para
   detectar edges genuínos. Considerar timeframe diferente (5m, 15m)
   ou outra source.

Tests permanecem 515 verdes; a infraestrutura de validação não foi
afetada — só os dados que ela consumia.

## Citações

- `[advances_fin_ml, p.184-186, ch.11]` — backtests sob silent data
  contamination; "garbage in, garbage out" reforçado.
- `[quant_trading_chan, p.37]` — split-adjust multiplier; o silent
  fallback ratio=1.0 viola o intent dessa fórmula em datas órfãs.

## Arquivos

- `src/ai_trade/backtest/data/tiingo_source.py` — `_filter_orphan_intraday_bars`
- `tests/test_tiingo_source.py` — 2 novos, 2 superseded
- `scripts/clean_intraday_orphans.py` — cleanup one-shot
- `data/tiingo/manifest.json` — atualizado pós-cleanup
- `data/tiingo/1hour/prices/*.parquet` — limpos
- `data/tiingo/1hour/prices/*.bak_orphan_clean_*` — backup
- `reports/grid_bollinger_mr_{SPY,XLK,XLE}_1h_post_clean/` — verdict FAIL

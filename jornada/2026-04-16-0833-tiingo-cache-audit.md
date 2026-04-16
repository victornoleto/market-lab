# Tiingo cache audit — Q1-2026 forward stress é confiável

**Verdict:** ✅ **Trustworthy.** O lazy-cache está fazendo o que o spec
prometeu. As três conclusões dos winners (SPY/XLK/XLE Bollinger MR 1h)
e a demoção do EEM no stress 2026-Q1 não foram contaminadas por dados
stale nem por look-ahead. Um *latent bug* foi encontrado (silent
fallback no split-adjust quando o cache daily fica atrás do intraday)
mas está inativo para os winners atuais — proposta de fix no fim.

---

## Por que o audit existia

Task 0A do plan `docs/superpowers/plans/2026-04-16-winners-deep-validation.md`:
"Confirme que o cache não serve dado stale, que o forward-stress 2026-Q1
não foi look-ahead, e que a lazy-cache logic funciona como projetada".

É a primeira coisa do plan porque, se o cache estivesse contaminado, todo
o resto (bootstrap, regime decomp, sizing, long-history) herdaria o
viés. 30-45 min para destravar 5+ tarefas downstream.

## O que o cache promete

O `TiingoSource.fetch(ticker, start, end, frequency)` é "storage-first":
1. `storage.has(ticker, start, end, freq)` retorna `True` iff o range
   pedido cabe em `[manifest.first_dt, manifest.last_dt]` mais um *slack*.
2. Se `has()` → True: retorna do parquet local sem HTTP.
3. Se `has()` → False: chama Tiingo, persiste, retorna do parquet.

O slack para `(equity|etf, 1hour)` é **12h** — escolhido para cobrir o
gap noturno US (16:00 ET → 09:30 ET = 17.5h). É o mínimo confortável
para não mascarar gaps reais de feed.

## Estado atual do cache (snapshot 2026-04-16 08:30 -03)

Manifest dos winners + comparators:

| Ticker | freq | last_dt | n_bars | fetched_at |
|---|---|---|---|---|
| SPY  | 1hour | 2026-04-15T19:00 | 9978 | 2026-04-15T23:39 |
| SPY  | daily | 2026-04-14       | 5698 | 2026-04-15T10:38 |
| XLK  | 1hour | 2026-04-15T19:00 | 9396 | 2026-04-15T22:28 |
| XLE  | 1hour | 2026-04-15T19:00 | 9396 | 2026-04-15T22:28 |
| EEM  | 1hour | 2026-04-15T19:00 | 9396 | 2026-04-15T22:28 |
| QQQ  | 1hour | 2026-04-15T19:00 | 9396 | 2026-04-15T22:27 |
| IWM  | 1hour | 2026-04-15T19:00 | 9840 | 2026-04-16T00:41 |
| DIA  | 1hour | 2026-04-15T19:00 | 9396 | 2026-04-15T22:28 |
| GLD  | 1hour | 2026-04-15T19:00 | 9396 | 2026-04-15T19:22 |
| TLT  | 1hour | 2026-04-15T19:00 | 9396 | 2026-04-15T22:28 |

Todos os 1h fecham na barra `19:00` UTC do dia 2026-04-15 (= 15:00 ET,
última barra RTH da sessão de ontem). Todos os fetches aconteceram
**depois** do close, então as caches têm a sessão inteira de ontem.

## Cross-reference: cache state × report timestamps

| Report | Run time | Cache `last_dt` na hora | Cache `fetched_at` | Look-ahead? |
|---|---|---|---|---|
| `grid_bollinger_mr_spy_1h_8wf_20260415-235041` | 2026-04-15 23:50 | SPY 1h tinha até 2026-04-15T19:00 (fetched 23:39) | 11min antes do report | ✗ Não |
| `grid_bollinger_mr_XLK_1h_iter15` | 2026-04-16 00:55 | XLK 1h até 2026-04-15T19:00 (fetched 22:28) | 2.5h antes | ✗ Não |
| `grid_bollinger_mr_XLE_1h_iter15` | 2026-04-16 00:55 | XLE 1h idem | 2.5h antes | ✗ Não |
| Q1-2026 stress (SPY/XLK/XLE/EEM, OOS `..2026-04-15`) | 2026-04-16 ~01:00 | Caches já no estado descrito | múltiplas horas antes | ✗ Não |

Todos os IS-grids e o forward stress aconteceram com a barra de
encerramento de 2026-04-15 já no cache. Nenhum precisou refetch
durante a execução, e o que estava no parquet representa fielmente o
mercado real até 16:00 ET.

## Audit ativo: a lazy-cache reage à passagem do tempo?

Rodei agora (2026-04-16 08:34) um `TiingoSource.fetch('SPY', date(2026,4,9),
date(2026,4,16), frequency='1hour')`. Hoje é dia 16, mercado ainda não
abriu. Esperado: como o `end` cai no dia atual e o slack de 12h não
cobre `2026-04-16T23:59:59` (cobre só até `2026-04-16T07:00`), o `has()`
deveria retornar False e disparar HTTP.

Resultado:

```
INFO ai_trade.backtest.data.tiingo_source: HTTP fetch SPY [2026-04-09..2026-04-16] (etf freq=1hour)
returned 30 bars; first=2026-04-09 14:00:00 last=2026-04-15 19:00:00
manifest after: last_dt=2026-04-15T19:00:00 (unchanged), fetched_at=2026-04-16T08:34:44 (updated)
```

✅ Confirmado:
- HTTP foi chamado.
- Tiingo retornou só os bars que já existiam (mercado fechado, sem barras
  novas de hoje).
- Dedup funcionou (n_bars não inflou).
- `fetched_at` atualizou (rastreabilidade ok).

## Disciplina do hold-out OOS

`scripts/run_oos_bollinger_mr.py` (linha 39-48 + 65-69 + 137-141): aceita
`--oos-start`/`--oos-end` arbitrários, faz fetch único do range completo
com warmup, depois usa `pd.Timestamp` slicing para isolar `data_oos =
[oos_start..oos_end]` e `data_train_bounded = [2021-01-01..2024-12-31]`
(este último hardcoded, propositalmente). O strategy é instanciado com
`data_full` (com warmup para a SMA), mas o `runner.run(data_oos)`
restringe a execução de trades ao range OOS. Sem leakage temporal.

Para Q1-2026 stress: `--oos-start 2026-01-01 --oos-end 2026-04-15`,
training comparison fica fixo em 2021-2024 (não inclui 2025; correto
pois 2025 já era o hold-out anterior).

## Edge case latente: silent fallback no split-adjust intraday

`tiingo_source.py:_apply_split_adjust_from_daily` deriva o ratio
`adj_close_daily / close_daily` por dia de calendário e aplica às barras
intraday do mesmo dia. O lookup é:

```python
ratios = pd.Series(
    [date_to_ratio.get(d, 1.0) for d in intraday_dates],
    index=df_intraday.index,
)
```

**Problema:** quando o cache daily fica atrás do cache intraday (estado
atual: daily até 2026-04-14, intraday até 2026-04-15), as barras
intraday do dia "extra" (2026-04-15) caem no `dict.get(d, 1.0)` →
ratio default = 1.0 → **sem ajuste de split/dividendo silenciosamente**.

O spec `2026-04-15-tiingo-service-lazy-cache-design.md §3.3` foi
explícito: "**não** fallback silencioso para `close`. Mensagem:
'baixe o daily primeiro para obter `adj_close`, ou pré-autorize via
flag `--skip-adjust` se você sabe o que está fazendo'". Mas isso só
dispara quando o ticker não está NO daily cache de jeito nenhum, não
quando ele está mas com janela mais curta.

**Impacto nos winners atuais:** verifiquei nos parquets daily de
SPY/XLK/XLE/EEM — nenhum split/dividendo aconteceu em 2026-04-15
(o ratio adj_close/close de 2026-04-14 é exatamente 1.0; a única
sessão sem ajuste no cache intraday é 2026-04-15, que é o dia atual
de descobertas). A delta intraday-vs-daily para 2026-04-14 fica em
±0.06%, atribuível a "intraday last bar termina antes do close oficial",
não a falta de adjust. **Zero impacto material no Q1-2026 stress.**

Mas é uma latent bug — se o próximo backtest envolver um ticker que
splite no dia "extra", o resultado seria silenciosamente errado, e o
DSR não captaria.

## Conclusões

1. **Q1-2026 forward stress é trustworthy.** Cache continha sessão
   inteira de 2026-04-15 antes de qualquer OOS rodar; a 12h slack
   deixou o `has()` retornar True corretamente; nenhum HTTP foi
   precisado durante o stress.
2. **Lazy-cache funciona como projetada.** Active probe demonstra que
   o slack de 12h NÃO mascara staleness para `end > today`; HTTP fires.
3. **Disciplina temporal OK no script de OOS.** Hold-out limpo via
   `pd.Timestamp` slicing.
4. **Latent edge case detectado (não material agora).** Quando daily
   cache fica atrás do intraday cache, dias intraday "extras" não
   recebem split-adjust — silently. Inativo para os winners porque
   nenhum split aconteceu nesses dias.

## Risco operacional (não-código, processo)

Há **uma situação** em que o cache PODE servir dados incompletos sem
warning: rodar backtest **durante o pregão** (e.g., 12:00 ET) pedindo
`--end today`. Cache pode ter `last_dt = today T11:00`, slack 12h cobre
até `today T23:00`, `has()` retorna True com `today T23:59:59` →
servirá só barras até 11:00 (barras das 12:00, 13:00, etc. estarão
ausentes silenciosamente).

**Mitigação:** sempre rodar backtests após o close (≥17:00 ET = 18:00
BRT). Os 3 winners + a demoção do EEM foram todos validados após o
close, então nada a corrigir retroativamente.

## Fix do latent bug (implementado neste mesmo dia)

**User aprovou — fix landed em commit separado** logo após este audit.
A opção escolhida foi `log.warning` v1 (vs raise), porque é compatível
com runs em curso e o bug é latente (nenhum dado distorcido até
agora). Promover a raise fica para v2 do spec lazy-cache, depois que
todo o pipeline esteja adaptado a refrescar daily junto com intraday.

A mudança em `tiingo_source.py:_apply_split_adjust_from_daily` foi:

```python
missing_dates = sorted(set(intraday_dates) - set(daily_dates))
if missing_dates:
    log.warning(
        "split-adjust fallback ratio=1.0 for %s on %d intraday day(s) "
        "missing from daily cache: %s. Refresh the daily cache so "
        "split/dividend ratios are applied; spec §3.3 forbids silent "
        "fallback.",
        ticker, len(missing_dates),
        [d.isoformat() for d in missing_dates],
    )
```

Comportamento numérico inalterado — ainda usa ratio=1.0 nos dias
órfãos. A diferença é que agora o operador vê no log quais datas
estão sem ajuste e pode refrescar o daily antes de re-rodar.

Cobertura: 2 testes novos em `tests/test_tiingo_source.py`:
- `test_iex_warns_when_daily_cache_lags_intraday_dates` — daily cobre
  só 2024-01-02, intraday inclui 2024-01-03 → warn emitido com a data
  correta + bar_03 fica raw (200) e bar_02 é ajustado (100×0.5=50).
- `test_iex_no_warning_when_daily_covers_all_intraday_dates` —
  caminho normal, sem warning.

Total: **501 → 503 testes verdes**.

## Próximos passos

Próxima rodada: Task **1A — Monte Carlo bootstrap** dos winners.

## Citações

- `[advances_fin_ml, p.208-211, ch.12]` — protocolo de OOS validation
  citado no docstring do `run_oos_bollinger_mr.py`.
- `[quant_trading_chan, p.37]` — fórmula canônica do split-adjust
  multiplier (referência de §3.3 do spec lazy-cache).

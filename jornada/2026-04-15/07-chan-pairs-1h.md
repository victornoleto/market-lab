# 2026-04-15 (madrugada) — Primeira estratégia intraday rodou: Chan pairs GLD-SLV 1h ❌

**Verdict:** FAIL — pair não-cointegrada no timeframe 1h (gate upstream
do backtest).

Primeiro item do catálogo intraday pós-pivô: `ChanBollingerPairsStrategy`
(spec `docs/superpowers/specs/2026-04-15-chan-pairs-1h-design.md`,
plan `docs/superpowers/plans/2026-04-15-chan-pairs-1h.md`). Pair
canônico mean-reversion via z-score Bollinger sobre o spread
`log(GLD) − β·log(SLV)`, com β fit por OLS two-ordering
`[algo_trading_chan, p.54, ch.2]` e half-life via OU regression
`[algo_trading_chan, p.47-48, ch.2]`.

**Setup do grid:**
- 4 configs (2×2: `lookback_multiplier ∈ {1, 2}` × `entry_z ∈ {1.0, 1.5}`).
- Dados Tiingo IEX 1h via `tiingo_service` (entregue na sessão anterior),
  6258 bars na janela 2022-04-15 → 2026-04-15.
- Cash $100k, n_jobs=4, wallclock < 1s.

**Resultado:** os 4 trials abortam **na construção da strategy**, antes
de qualquer barra ser processada. O gate de cointegração via t-stat OU
rejeita o pair:

```
t_stat_OU = -2.956 (threshold = -3.4)
half_life = 55 bars (≈ 8.5 dias trading)
```

Half-life cai dentro do range admissível [4, 60], mas a *força* da
mean-reversion (t-stat) é insuficiente. GLD e SLV co-movem (correlação
alta), mas o spread não é fortemente mean-revertor em 1h sobre estes 4
anos. O squeeze de 2022 na prata + a corrida do ouro 2023-2026 a all-
time-highs decoupled o ratio estrutural o bastante para a OU não passar.

**Sem Sharpe / CAGR / MaxDD pra reportar:** zero trials produziram
equity curve. Diagnostic counters (`pct_exited_by`, `median_hold_hours`,
`hard_cap_pct`) também N/A.

**Citação central:** Chan já avisa em `[p.88-89, ch.4]` que pair-trading
edge é não-confiável fora de pares com relação fundamental forte
(mesmo setor, mesma cobertura analista). A regra agora se mostra
extensível a ETFs em 1h.

**Próximo passo (per spec §7.5):** pivotar pra **volatility breakouts
Sinclair** `[volatility_trading]` como segundo item do catálogo intraday.
Antes de descartar Chan inteiro, o spec admite voltar em §7.2 (basket
de 3 pares: GLD-SLV + XLE-XOP + SPY-IWM com Fisher's combine
`[masters_permutation_tests]`) — fica em backlog secundário.

**Achado adjacente (não bloqueante):** `DiagnosticAnalyzer.analyze()`
hoje raise `ValueError("grid has no OK trials")` quando 100% dos trials
abortam upstream do backtest. O CLI runner não escreve diagnostic.md
nesse caso. Workaround manual aplicado pra esta sessão; melhoria de
infra anotada como follow-up (degenerate diagnostic quando todos os
trials falharem por gate de construção).

**Arquivos:**
- `reports/grid_chan_pairs_20260415-2109/diagnostic.md` (manual)
- `reports/grid_chan_pairs_20260415-2109/trials.jsonl` (4 trials × erro)
- `.cache/grid_runs/grid_chan_pairs_20260415-2109/` (debug.log + status.md)

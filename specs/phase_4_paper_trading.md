# Spec — Phase 4 (Dual-path paper trading: Plano A + Plano B)

**Data:** 2026-04-19 (drafted na iter 81 V2-L7 com verdict Phase 3.5a-V2 WINNER FOUND)
**Branch prevista:** `phase4/dual-path-paper-trading` (criar quando iniciar execução)
**Orçamento:** **3 meses calendário de paper trading** (não iters de loop autônomo)
**Path tag:** `[PAPER]` (combina `[SHORT-HOLD CFD]` Plano A + `[SWING BROKER]` Plano B)
**Pre-req:** Phase 3.5a-V2 encerrada com ≥ 1 Plano A winner. ✅ Satisfeito (2026-04-19).

---

## 0. Objetivo

Validar **na prática**, com capital zero de mercado real, que os 2 winners produtivos
das Phase 3.5a-V2 (Plano A) e Phase 3.5b (Plano B) executam fielmente ao backtest
quando sujeitos a:

- Ordens reais (paper) em horário real de mercado.
- Cost model empírico (spread medido, commission real, slippage observado, swap
  aplicado nas posições overnight/weekend).
- Dados ao vivo (não backfill retrofitted).
- Operador humano emitindo as ordens ou supervisionando o bot.

**Não é** objetivo desta fase: otimizar parâmetros, refitar WF, expandir universe,
ou adicionar features. Phase 4 é **teste de fidelidade**; a otimização vai para
Phase 5.

---

## 1. Winners a paper-tradear

### Plano A — `gayed_ema100_L2_off_gld` (Phase 3.5a-V2 L2 winner)

- **Strategy:** Gayed regime rotation `[leverage_for_the_long_run, p.11-21]`.
- **Sinais:** EMA-100 close(SPY). Se close > EMA100 → risk-on. Caso contrário → risk-off.
- **Portfolio risk-on:** 50% SPY + 50% QQQ em CFD Pepperstone, leverage 2×.
- **Portfolio risk-off:** 100% GLD CFD (sem alavancagem, posição spot em GLD CFD).
- **Rebalance cadence:** daily close (decisão no close US).
- **Broker:** Pepperstone cTrader Open API (Razor tier).
- **Cost model:** spread 2-5 bps half ×2 + commission $3.50/side + slippage 1-3 bps + swap 0.005-0.02%/day.
- **Sizing inicial:** paper USD equivalent 10k (escala arbitrária para simular frictions reais; sizing real quando Phase 5).

### Plano B — Portfolio 3-leg EW (V4, Phase 3.5b-addendum winner)

- **Strategy:** 3 LETFs independentes com sinais nos 1× índices.
  - Leg 1: SPY EMA-100 regime → execução em **SSO** (LETF 2× S&P).
  - Leg 2: QQQ Donchian 20/10 breakout → execução em **QLD** (LETF 2× NASDAQ-100).
  - Leg 3: GLD Donchian 40/20 breakout → execução em **UGL** (LETF 2× Gold).
- **Target weights:** 1/3 cada.
- **Rebalance mode:** threshold **10pp** (cash drifts dentro da banda, só rebal cross-leg quando alguma perna diverge > 10pp).
- **Broker:** Banco Inter Global (FINRA + Apex Clearing).
- **Cost model:** IR 15% BR por venda lucrativa (DARF 6015), zero corretagem, spread FX ~1.50% na remessa.
- **Sizing inicial:** paper BRL equivalente R$ 20k convertido para USD via PTAX simulado.

---

## 2. Tarefas Phase 4 (high-level roadmap, sem sub-iters de loop)

### T1 — Pepperstone cTrader Open API adapter (Plano A)

**Status:** new build.

Construir `src/ai_trade/brokers/ctrader_adapter.py` com:

- OAuth2 flow (usuário obtém refresh token via cTrader ID).
- Market data subscribe: SPY, QQQ, GLD (bars 1m/1h/1d).
- Order management: submit MKT/LIMIT buy/sell com leverage notional.
- Position query / account balance / swap debit visibility.
- Error handling: reconnect, rate limit, session drop.

Tests: mock server retorna fills simulados; live paper test contra cTrader Demo.

**Citation:** `[ctrader_open_api_spec, v4.x]` (docs oficiais cTrader).
Referência existente: `docs/reference/broker_dev_notes.md` (se existir).

### T2 — Plano A regime-signal service (diário)

Construir `src/ai_trade/live/gayed_regime_service.py`:

- Input: daily close SPY + EMA-100 (computed no close US, ~16:00 ET).
- Output: `RiskOn` / `RiskOff` signal + target allocation dict.
- Idempotent: executar múltiplas vezes no mesmo dia retorna mesmo signal.
- Logs: todas decisões em `logs/live_plano_a.log` (unified log pattern, ver
  memória do usuário `feedback_unified_log.md`).

Tests: dado histórico Tiingo, regime-service replica exactly o verdict backtest.

**Citation:** `[leverage_for_the_long_run, p.11-14]` (EMA-100 operacional).

### T3 — Plano A paper execution daily job

`scripts/live_plano_a_paper_daily.py` (daily cron):

1. Pull daily close SPY/QQQ/GLD.
2. Run `gayed_regime_service`.
3. Query current positions from cTrader Demo.
4. Compute delta → submit orders.
5. Log realized fills, slippage observed, swap debited.
6. Write daily paper P&L to `reports/phase4_paper/plano_a/<YYYY-MM-DD>.json`.

### T4 — Banco Inter Global account setup (Plano B)

**Status:** operational (not code).

- Usuário abre conta Global pela app Inter.
- Remete capital inicial: R$ 20k paper (ou equiv USD ~$4k).
- Valida catálogo SSO+QLD+UGL disponíveis (✅ confirmado 2026-04-18 per mandate §4.6.3).
- Configura planilha cost-basis em USD+PTAX.
- Runbook: `reports/phase3_5b/PRODUCTION.md` (já existe).

### T5 — Plano B paper execution (manual + planilha)

Por enquanto Plano B é **execução humana** (Inter Global não tem API programática).

1. Operador recebe daily signal do Plano B via `scripts/plano_b_daily_signal.py`.
2. Planilha calcula target weights + threshold 10pp.
3. Operador executa ordens na app Inter se rebal dispara.
4. Log manual em `reports/phase4_paper/plano_b/operator_log.md`.

Inter integrations são out-of-scope para Phase 4 (não há API oficial).

### T6 — Post-paper gate (end of month 3)

Ao fim dos 3 meses:

1. Consolidar realized vs backtest Sharpe/CAGR/MDD/median hold (para cada path).
2. Re-computar custos realizados vs modelados. Se real > modelo × 1.3 → re-calibrar.
3. Medir ρ(returns A, returns B) em daily. Se ρ > 0.7 → dual-path benefit em
   questão; re-ponderar.
4. Decisão: avançar para Phase 5 (live com capital mínimo), ou iterar Phase 4
   com adjustments.

Jornada final: `jornada/<date>-phase4-paper-verdict-<GO|NOGO>.md`.

---

## 3. Gates Phase 4 (paper → live)

Para avançar para Phase 5 (live) em **cada path**:

| Gate | Threshold paper vs backtest | Razão |
|---|---|---|
| Realized Sharpe | ≥ 0.7 × backtest Sharpe | tolerância de fidelidade |
| Realized CAGR (annualized do 3mo) | ≥ 0.5 × backtest CAGR | 3mo amostra curta, exige 50% |
| Realized MaxDD | ≤ 1.5 × backtest MaxDD | tolera piora até 1.5× |
| Slippage observado | ≤ 30 bps/trade | Pepperstone Razor target |
| Signal → fill latency | ≤ 5 min end-to-end | operacional |
| Zero discrepâncias código vs execução (bugs) | 0 | go/no-go absoluto |

Se **todos** gates pass em 3mo paper → avançar para Phase 5 live.
Se algum falha → diagnosticar (bug? cost mis-calibrado? signal mis-timed?) e
iterar Phase 4 com adjustment. Não avançar para live sem gate-passing.

---

## 4. Não-objetivos (fora de escopo Phase 4)

Coisas que **não são** Phase 4. Deixar para Phase 5 ou posterior:

1. **Otimização de parâmetros:** não tocar EMA-100, leverage 2×, Donchian 20/10, threshold 10pp. Phase 4 valida winners fixos.
2. **Universe expansion:** não adicionar novos tickers. Phase 4 usa SPY/QQQ/GLD/SSO/QLD/UGL apenas.
3. **GARCH vol-sizing variant:** Phase B lead, defer to Phase 5.
4. **Cost sensitivity sweeps:** defer to Phase 5.
5. **Multi-asset transport (Plano A on IWM/XLK/FX):** defer to Phase 5.
6. **Cross-strategy correlation analysis além do ρ(A,B) simples:** defer.
7. **V3 de Plano A:** PROIBIDO por contrato V2 (`project_plano_a_v2_last_attempt.md`). Se Plano A falhar gates Phase 4, investigar bug/cost/latency — não re-abrir search de família.

---

## 5. Orçamento e timeline

| Semana | Atividade |
|---|---|
| Semana 1 | T1 cTrader adapter + T4 Inter Global account setup |
| Semana 2 | T2 regime-signal service + T5 Plano B manual flow |
| Semana 3 | T3 Plano A daily job running paper |
| Semanas 4-15 | 3 meses paper trading (cada path) |
| Semana 16 | T6 post-paper gate + jornada verdict |

ETA total: **~4 meses calendário** (1 mês build + 3 meses observation).

---

## 6. Infraestrutura

### Novos arquivos

- `src/ai_trade/brokers/ctrader_adapter.py` + tests
- `src/ai_trade/live/gayed_regime_service.py` + tests
- `src/ai_trade/live/plano_b_signal.py` + tests (reusa código Phase 3.5b)
- `scripts/live_plano_a_paper_daily.py`
- `scripts/plano_b_daily_signal.py`
- `reports/phase4_paper/plano_a/README.md`
- `reports/phase4_paper/plano_b/README.md`
- `docs/live_trading_runbook.md` (combined operator manual)
- `logs/live_plano_a.log`, `logs/live_plano_b.log` (unified logs)

### Arquivos intocados (IMUTÁVEIS)

- Todo código Plano B em `src/ai_trade/backtest/strategies/` (letf_rotation, tsmom, portfolio_3leg).
- Todo código Plano A backtest em `src/ai_trade/backtest/strategies/bollinger_mr.py` (seed histórica — V2 winner não tem código próprio, é spec-only rotation).
- Todos specs Phase 3.x (phase_2, phase_2_5, phase_3_5a, phase_3_5a_v2, phase_3_5b*).
- Todos winners jornadas já escritas.

### Testes

- Manter pytest ≥ 783 passed.
- Adicionar ≥ 30 novos tests (10 cTrader adapter + 10 regime-service + 10 signal-service).
- Live paper tests com cTrader Demo: `tests/live/test_ctrader_demo_roundtrip.py` (não em CI default, flag `LIVE_TESTS=1`).

---

## 7. Risks e mitigations

| Risk | Mitigation |
|---|---|
| cTrader Open API rate-limit ou desconexão | Reconnect exponential backoff, heartbeat, fallback to REST polling 30s |
| Signal-to-fill latency > 5 min | Monitorar latência, alertar se > 2 min (pre-gate) |
| Slippage realizado > modelo | Medir primeiras 20 trades; se > modelo × 1.5, re-calibrar L=2 para L=1.5 proativo |
| Inter API futuras mudanças de catálogo (SSO/QLD/UGL delist) | Monitor `reports/phase3_5b/PRODUCTION.md` catalog check quarterly |
| ρ(A, B) > 0.7 em paper (dual-path diversification falha) | Re-ponderar 30/70 B/A em vez de 50/50; documentar em Phase 5 spec |
| User human error em execução manual Inter (Plano B) | Checklist por rebal, double-check trade log com signal antes de enviar |
| Bug de descompass entre backtest simulação e live | Testes de reconciliação daily: backtest(close_realizado) vs paper P&L, delta ≤ 0.1pp |

---

## 8. Pre-launch checklist

Antes de mergear esta spec em main e abrir branch `phase4/dual-path-paper-trading`:

- [ ] Validar `reports/phase3_5a_v2/AGGREGATE.md` está escrito com verdict PASS (✅ feito na iter 81).
- [ ] Validar `docs/investment-mandate.md §7` tem entry V2 verdict (✅ feito na iter 81).
- [ ] Validar `jornada/2026-04-19-0510-phase3.5a-v2-summary-WINNER-FOUND.md` existe (✅ feito na iter 81).
- [ ] Memory.md `status: done` (✅ feito na iter 81 V2-L7).
- [ ] ROADMAP.md atualizado para indicar Phase 3.5a-V2 encerrada + Phase 4 next (TODO user).
- [ ] Usuário confirma autorização de gastar 4 meses calendário nesta fase antes de launch.
- [ ] Usuário confirma abertura de conta Pepperstone live (não-Demo) planejada para Phase 5.

---

## 9. Citações

- Gayed regime rotation operacional: `[leverage_for_the_long_run, p.11-14, p.16-17]`.
- Pepperstone Razor cost model: `docs/investment-mandate.md §3` + `specs/phase_3_5a_v2.md §3`.
- cTrader Open API: `[ctrader_open_api_spec, v4.x]` (docs oficiais — URL quando disponível, não buscar especulativamente).
- Banco Inter Global broker stack: `docs/investment-mandate.md §4.6`.
- Threshold 10pp rebalance (Plano B V4 production default): `reports/phase3_5b/PRODUCTION.md §6` + jornada `2026-04-17-2315-phase3.5b-C4-threshold-sweep-V4.md`.
- Paper-to-live gate thresholds (0.7× Sharpe, 1.5× MDD tolerância): `[systematic_trading, ch.14-15]` (Carver live-trading discipline).

---

## 10. Stop rule Phase 4

Se após **3 meses paper** Plano A **falhar** os gates (realized Sharpe < 0.7 × 2.285
= 1.6, ou MDD realizado > 1.5 × 21% = 31.5%, ou slippage > 30 bps/trade):

1. **NÃO** re-abrir V3 do Plano A. Proibido pelo contrato V2.
2. **Diagnosticar** root cause: signal lag, cost calibração, data feed integridade.
3. **Iterar Phase 4** com fix específico (máx 1 month re-paper).
4. **Se fix não passa 2ª rodada** → pivotar para Plano B puro (mandate §4.7 re-alocação 5pp A→B).

Se Plano B falhar gates Phase 4 (realized Sharpe < 0.7 × 2.251 = 1.6, MDD > 1.5 ×
10.86% = 16.3%, ou operational errors) → iterar Phase 4 com ajuste manual de
signal cadence ou threshold. Plano B tem ceiling empírico conhecido (2.609 V4) →
erosão paper ≤ 30% é recuperável.

**Stop rule NÃO dispara extinção do projeto.** Phase 4 é validação, não selection.

---

**Fim do spec Phase 4.**

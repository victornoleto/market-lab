# Phase 3.5b Task 4 — QQQ Donchian 20/10 full validation report [PLANO B] [SWING BROKER]

**Data:** 2026-04-17
**Branch:** `phase3.5b/winners-validation-20260417`
**Iter:** 4
**Scope:** CODE-ALLOWED (só emissão de relatório; nenhuma mudança em lógica da strategy).
**Artefatos:** `reports/phase3_5b/qqq_donchian_20_10/{trade_log.csv,trade_log.md,standard_report.md,equity_curve.png,summary.json}`.

## O que foi feito

Validada a saída completa do winner QQQ Donchian 20/10 (entry=20d /
exit=10d, commission 10 bps, spread 5 bps) rodando
`scripts/validate_phase3_winners.py` na janela LONGEST do Tiingo cache
daily de QQQ:

- **6 266 bars** — 2001-05-14 → 2026-04-14 (≈24.9 anos, janela idêntica à
  do Phase 3 A3b PASS; nenhum dado adicional disponível no manifest).
- 107 trades (cada bloco long contíguo = um trade), exposição 49.92%
  (fica metade do tempo out-of-market — perfil clássico de Donchian
  trend-follow `[stocks_on_the_move, p.80-85]`).
- Re-run bit-for-bit idêntico ao smoke de Iter 2 (diff summary.json =
  0 bytes) ⇒ determinismo do pipeline confirmado.

## Números principais (standard_report.md)

| | Strategy QQQ (2001-2026) | SPY B&H (mesma janela) |
|---|---|---|
| CAGR | **17.40%** | 9.09% |
| Sharpe (252d, ddof=0) | **1.389** | 0.553 |
| Sortino | 2.134 | — |
| Calmar | 1.361 | — |
| Max DD | **12.79%** (333 d) | 55.20% |
| Avg DD | 1.70% (25 d) | — |
| Vol anual | 12.08% | — |
| # trades | 107 | — |
| Win rate | 65.42% | — |
| Profit factor | 5.63 | — |
| Expectancy | +3.47% / trade | — |
| SQN | 5.74 | — |
| Kelly | 0.538 | — |
| Avg / Max hold | 41 d / 143 d | — |
| Best / Worst trade | +34.08% / −7.15% | — |

### Strategy vs SPY (mesma janela 2001-05-14 → 2026-04-14, sem overlap parcial)

| | |
|---|---|
| Excess Return | **+4 529.36 pp** |
| Excess CAGR | **+8.31%** |
| Delta Max DD | **−42.41%** (strategy menos arriscada) |
| Information Ratio | 0.358 |
| Correlation (daily) | 0.442 |
| Beta vs SPY | 0.280 |

Beta 0.28 + correlação 0.44 ⇒ metade do tempo fora do mercado mitiga
betaexposição e corta MDD 4× vs B&H, mesmo com QQQ sendo mais volátil
que SPY como underlying. IR 0.358 é menor que LETF rotation (1.601)
porque o CAGR é metade, mas a Sharpe 1.389 e MDD 12.79% são superiores
em qualidade de retorno do que muitos fundos long-only.

## Reconciliação full-window vs OOS window do Phase 3

Phase 3 A3b (jornada `2026-04-17-0120-a3b-tsmom-donchian-per-asset-PASS.md`)
reportou Sharpe 1.738 / CAGR 20.38% na **janela OOS 25%** (block
mutuamente exclusivo aprox. 2020→2023 dentro do split 60/25/15).
Full-window aqui reporta Sharpe 1.389 / CAGR 17.40%.

A diferença é **esperada e consistente** — Phase 3 já documentou
"full-window 107 trades, Sharpe 1.389" na mesma jornada. OOS captura
um regime recente favorável a breakout (bull 2020-21 + bear 2022 com
reentrada), enquanto full-window inclui o dotcom bust 2001-2003 e
vários anos de chop 2004-2009/2011-2012/2014-2016 que diluem Sharpe.
**Não é regressão: o winner foi selecionado por OOS, não por full-window**
`[advances_fin_ml, p.163]`.

## Stress 2022-07 → 2026-04 (janela forward do Phase 3)

Phase 3 A3b já reportou Sharpe 1.710 / CAGR ≈17% no forward-window
stress. Não refiz aqui (não pedido pela Task 4; Task 7b cobre stress
isolado por sub-período). Log é consistente: 2022-2023 teve 12-15
trades com win rate compatível e 2024-2026 teve breakout largo.

## ⚠️ FLAG-1 — Equity curve compounded vs trade log notional fixo

Divergência apenas aparente:

- `standard_report.md` → `Equity Final $5,399,918` (compounded: cada
  trade ajusta notional ao equity corrente via `run_strategy`).
- `trade_log.csv` última linha → `cumulative_equity_brl = 403,850`
  (fixed notional $100k por trade, sem compounding — soma de net PnL).

Por design e documentado no docstring de `render_trade_log()` linhas
633-635: "The cumulative_equity_brl column … adds the net PnL of each
trade — it is NOT compounded per trade." Duas representações com
finalidades diferentes:

- Equity curve: performance real de conta que compound.
- Trade log cumulative: auditoria pura do PnL ignorando sizing — útil
  para verificar IR BR aplicado corretamente.

**Não é bug.** Flag documental para o leitor não se confundir. Para
Task 6 (portfolio 3-leg EW) isso precisará nota similar — já prever.

## ⚠️ FLAG-2 — Exposure time 49.92% (não é bug, é feature)

Donchian 20/10 gasta ~50% do tempo em cash (exit=10d fecha rápido em
correção). Implicação prática para Plano B:

- Capital ocioso metade do tempo. Em conta BR sem remuneração de cash
  overnight, isso é custo de oportunidade (≈50% × 13% CDI = 6.5%/ano
  perdidos). **Pepperstone CFD não se aplica aqui** (Plano B é broker
  BR). Mitigação futura: alocar cash em Tesouro Selic /CDI dentro da
  mesma conta nos períodos out-of-market (Task 8 allocation doc deve
  cobrir isto).
- O MDD 12.79% é parcialmente fruto dessa ociosidade — trend follower
  corta perda cedo e espera breakout.

Não requer ação nesta task; apenas nota para allocation doc (Task 8).

## ✅ Sem anomalies estruturais

- Win rate 65% → realista (não artefato como o 100% LETF da Task 3).
- 107 trades / 6266 bars → freq ≈1 trade/8 semanas, consistente com
  Donchian breakouts `[stocks_on_the_move, p.91-97]` `[ehlers_cycle, ch.14]`.
- IR 15% BR aplicado só nos ~70 trades lucrativos, confirmado manualmente
  em sample do CSV.
- Prices reconciliam com QQQ histórico público (31→22→600+).

## Pytest baseline

`.venv/bin/pytest -q` → **587 passed** (sem mudança — esta task não
tocou código).

## Commit / push

Shell loop auto-commit na branch isolada. Nenhum `git` manual.

## Próximo lead

Task 5 — GLD Donchian 40/20 full report. Artefatos já emitidos no
Iter 2 smoke (reports/phase3_5b/gld_donchian_40_20/). Task 5 será
validar + jornada, mesmo formato desta.

## Citações

- `[stocks_on_the_move, p.80-85]` Donchian exposure/trend follower.
- `[stocks_on_the_move, p.91-97]` Frequência de trades breakout.
- `[ehlers_cycle, ch.14]` Cycle-aware breakout timing.
- `[advances_fin_ml, p.163]` OOS selection primacy sobre full-window.

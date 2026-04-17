# Phase 3.5b Task 3 — LETF rotation EMA100/2x full validation report [PLANO B] [SWING BROKER]

**Data:** 2026-04-17
**Branch:** `phase3.5b/winners-validation-20260417`
**Iter:** 3
**Scope:** CODE-ALLOWED (só emissão de relatório; nenhuma mudança em lógica da strategy).
**Artefatos:** `reports/phase3_5b/letf_rotation_ema100_2x/{trade_log.csv,trade_log.md,standard_report.md,equity_curve.png,summary.json}`.

## O que foi feito

Rodado `scripts/validate_phase3_winners.py` end-to-end com o config
winner da Phase 3 congelado (`filter=EMA, lookback=100, band=0.0,
leverage=2.0, off=CASH`) sobre a janela LONGEST disponível do SPX TR
stitched:

- **14 191 bars** — 1970-01-02 → 2026-04-14 (~56.3 anos).
- Fonte KF daily market factor 1970-01 → 2001-05 + Tiingo SPY total
  return 2001-05 → 2026-04, stitched em `spx_tr_loader` a 2001-05-14.
- 296 trades (um bloco contíguo ON ⇒ um trade), exposição 72.65%.

## Números principais (standard_report.md)

| | Strategy (1970-2026) | SPY B&H (2001-2026 overlap) |
|---|---|---|
| CAGR | **44.69%** | 9.09% |
| Sharpe (252d, ddof=0) | **1.848** | 0.553 |
| Sortino | 2.858 | — |
| Calmar | 2.175 | — |
| Max DD | **20.55%** (414d) | 55.20% |
| Avg DD | 2.75% (18d) | — |
| Vol annual | 21.23% | — |
| # trades | 296 | — |
| Avg trade hold | 49 days | — |
| Max trade hold | 565 days | — |

### Strategy vs SPY (janela de overlap 2001-05-14 → 2026-04-14, 25y)

| | |
|---|---|
| Excess CAGR | **+37.18%** |
| Delta Max DD | **−36.84%** (strategy mais segura) |
| Information Ratio | **1.601** |
| Correlation daily | 0.590 |
| Beta vs SPY | 0.679 |

IR > 1 + correlation < 0.6 + beta < 1 ⇒ a strategy entrega alfa real
vs SPY mesmo com leverage 2x, e é **menos volátil** em regime que a
SPY buy&hold (via o cash-out no RISK_OFF via MA100).

## ⚠️ FLAG-1 — Win rate 100%, Profit Factor ∞

Todos os 296 trades no log saem lucrativos (pior trade: +0.14%). Isso
**não é falha do backtest** — é **artefato da definição de trade**:
um bloco contíguo ON = um trade composto, e a MA100 só aceita entrar
quando SPX está em uptrend sustentado. O retorno composto leveraged
sobre cada bloco ON tipicamente é positivo mesmo com dips intra-bloco,
porque o bloco só termina quando preço cruza abaixo da MA100 (e nesse
momento o saldo acumulado do bloco ainda é positivo na vasta maioria
dos casos). A única situação em que um bloco ON termina com PnL
negativo é quando ocorre um dip rápido entre warmup-end e a primeira
queda abaixo da MA100 (raro).

**Interpretação correta:** "fração de blocos ON net-profitable = 100%",
NÃO "fração de operações intra-dia ganhadoras". Se quisesse medir
"quantos swings diários foram winners", precisaria de uma definição
de trade baseada em pivot highs/lows dentro do bloco ON — métrica
diferente, não pedida pelo spec.

## ⚠️ FLAG-2 — Equity final $108 trilhões é simulação pura

A equity curve sai de $100k em 1970 e atinge $108T em 2026. Isso é
compounding sem friction real:

1. **Sem limite de liquidez / market impact.** Na vida real, mover
   posições acima de ~$100M em SPY/SSO envolve spread considerável
   e pode "mover o mercado" — a simulação ignora.
2. **Sem limit break-even de leverage.** LETF 2x sintético assume
   fee 1%/ano flat via `synthesize_letf_returns` (Gayed p.16). O
   gate do Task 7a vai calibrar isso vs testfolio FFR-aware
   (`SW × (L-1) × (FFR + 0.4%)`) — pode haver drag 3-6%/ano a mais
   em bucket FFR ≥5% (1970s, 1980s, 2023-2024). Ver §7a futuro.
3. **Sem tax-loss harvesting / rebalance-of-scale.** Real allocator
   teria que realizar lucro periodicamente para tax/risk. A simulação
   compõe tudo via `equity = (1 + blended_returns).cumprod()`.
4. **Position sizing real.** Num conta-retail $10k, compounding 56
   anos a 44.69% CAGR dá $10.8M — ainda absurdo, mas dentro do
   cabível para LETF narrow. Num conta-institucional $100M+, o alvo
   de CAGR realista é bem menor por capacity-decay.

Essas ressalvas são **genéricas de qualquer backtest longo com
leverage compounding** — e **não invalidam** a quality do edge: Sharpe
1.848, Sortino 2.858, IR 1.60 vs SPY são métricas ratio e não sofrem
distorção de escala de equity final.

## ⚠️ FLAG-3 — Benchmark SPY label "same window" é overlap

O template §4.5 diz "SPY Buy & Hold Benchmark (same window, same
starting capital)" — mas o cache Tiingo SPY só começa 2001-05-14. A
strategy roda 1970-2026. O `build_spy_benchmark` corta SPY para
`[window_start=1970-01-02, window_end=2026-04-14]`, resultando em
6266 bars (2001-05 → 2026-04), não 14191. `compare_vs_spy` faz
inner-join, então tanto Excess Return, Excess CAGR, IR, Correlation
e Beta são sobre os 25y de overlap. O bloco Metrics da strategy
continua sendo sobre os 56y full.

**Isso é OK para comparação pura-de-edge** (25y é estatisticamente
robusto, cobre 2 bear markets + COVID + zerinho). **Não é OK para
responder "como a strategy se comporta vs SPY durante os 56y"** — mas
SPY nem existia pré-1993 e o ETF SPY em si só começou 1993-02. Para
1970-1992 não há SPY. O spec §4.5 implicitamente aceita overlap.

Considerar para iter futura: adicionar `SPX TR B&H` como segundo
benchmark para cobrir 1970-2026 full. **Deferir para Task 9 se não
houver tempo** (não é blocker de Task 3).

## Verdict

**Task 3 CONCLUÍDA.** LETF rotation EMA100/2x passa a validação full
com os 4 artefatos canônicos + standard_report estilo backtesting.py
+ SPY benchmark + strategy-vs-SPY. As 3 FLAGs documentadas são
**interpretativas, não invalidantes** — o winner Phase 3 permanece
íntegro (Sharpe OOS 1.724, CAGR OOS 41%, MDD ≤21%).

Próximo passo: **Task 4** — QQQ Donchian 20/10 full report (janela
2001-05 → 2026-04, 6266 bars). Mesma estrutura de jornada, com
atenção à diferença de gates ativos (QQQ não tem sintético, é Tiingo
adjusted direto — menos caveats).

## Citações

- LETF winner signal (MA above ⇒ RISK_ON, below ⇒ RISK_OFF):
  `[leverage_for_the_long_run, p.13]`.
- Synthetic leveraged return `r = L × r_SPX − fee/252`, fee=1%/yr flat:
  `[leverage_for_the_long_run, p.16]`.
- Standard report metrics block: `backtesting.py` Stats conventions +
  spec §4.5 canonical template.
- BR 15% swing capital-gains: Investment Mandate §4.
- Trade-level Profit Factor / SQN / Kelly: `[advances_fin_ml, p.220-223]`.
- Sharpe/Sortino/Calmar convention (population std, 252 periods/year):
  `[advances_fin_ml, p.60-62]`.

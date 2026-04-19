# Lead T2 — Donchian/ATR-Chandelier breakout 1h FX + metais (aggregate)

**Phase:** phase3_5a | **Lead:** T2 | **Status:** DEAD END (0/12 PASS)
**Period:** 2020-01-06 → 2026-04-14 (~6.3y, Tiingo IEX 1h cache)
**Tested:** 12 tickers × 3 configs = 36 runs (long-only, time_stop=120 bars)
**Aggregation iter:** 16
**Registry:** `reports/phase3_5a/t2_donchian_breakout/registry.json`

## Summary

Lead T2 testou 3 famílias long-only de breakout clássico — Donchian 10/5,
Donchian 20/10 e ATR-Chandelier exit (20 entry + 3.0×ATR trailing) — em
todo o universo FX/metal disponível em Tiingo 1h (10 majors + XAUUSD +
XAGUSD). Janela 2020-01-06 → 2026-04-14 (longest cache), custos
Pepperstone Razor (half_spread 2 bps FX / 5 bps metal + swap 0.005%/d).
**Zero ticker passa o 5-gate framework** (PBO<0.5 + DSR p<0.05 + WF≥6/8
+ OOS>0 + FWD>0).

Padrão fundamental detectado: **FX majors 10/10 negativos** em OOS
Sharpe (best -2.08 USDJPY donchian_20_10_long), médias -3 a -5 em casos
piores (USDCAD -5.28, EURGBP -4.88). Donchian_10_5 é o pior de todos
(full MDD -60% a -80% em 900-1100 trades) — noise amplifier em 1h FX
com custos de varejo. ATR-Chandelier (exit mais solto) reduz trades 80%
e sobe Sharpe ~1.5 pontos mas não chega a positivo em FX.

**Metais (XAG/XAU) destoam**: os 2/2 tickers produzem OOS Sharpe
**positivo** em atr_chandelier_long (XAGUSD +0.57 CAGR +9.4%, XAUUSD
+0.31 CAGR +2.7%), com FWD stress também positivo. Porém falham gates
secundários: XAGUSD passa PBO (0.44) mas DSR p=0.479 / WF 3/8; XAUUSD
falha PBO (0.65 — os 3 configs convergem para perda) e DSR 0.67. Edge
existe em metais mas não tem consistência suficiente pra ser winner
Plano A.

Implicação: **breakout long puro 1h é structurally unfit pra FX majors
com custos de varejo**. A estrutura de FX (mean-reverting em intraday,
random walk no agregado, spreads 2-4 bps + commission 3.5 bps ≈ 5-7 bps
por trade) consome o edge — o ganho médio por trade precisaria ser
≥ 7 bps e consistentemente é sub-7. Em metais o sinal aparece porque
trending vol é mais pronunciado (XAU/XAG têm regimes de tendência forte
2020-2022 e 2024-2026) mas o sample de 2 ativos não satisfaz
multi-asset mandate §3 nem supera o gate de robustez PBO/DSR.

## Cross-ticker table (best config por ticker)

| Ticker | Freq | Best config | Sharpe OOS | CAGR OOS % | MDD OOS % | Hold (d) | Trades OOS | PBO | PASS |
|--------|------|-------------|-----------:|-----------:|----------:|---------:|-----------:|----:|:----:|
| AUDUSD | 1h | atr_chandelier_long | -3.13 | -16.03 | -31.09 | 1.00 | 186 | — | ✗ |
| EURGBP | 1h | atr_chandelier_long | -4.88 | -12.82 | -24.59 | 0.96 | 177 | — | ✗ |
| EURJPY | 1h | donchian_20_10_long | -2.44 | -12.27 | -25.31 | 0.96 | 229 | — | ✗ |
| EURUSD | 1h | donchian_20_10_long | -2.90 | -10.89 | -21.18 | 0.73 | 227 | — | ✗ |
| GBPJPY | 1h | donchian_20_10_long | -2.56 | -12.92 | -26.38 | 1.00 | 211 | — | ✗ |
| GBPUSD | 1h | atr_chandelier_long | -3.41 | -13.42 | -25.89 | 1.00 | 156 | — | ✗ |
| NZDUSD | 1h | atr_chandelier_long | -3.06 | -15.82 | -30.35 | 0.90 | 178 | — | ✗ |
| USDCAD | 1h | atr_chandelier_long | -5.28 | -16.11 | -30.69 | 0.88 | 188 | 0.34 | ✗ |
| USDCHF | 1h | atr_chandelier_long | -3.19 | -13.95 | -27.29 | 1.08 | 155 | 0.94 | ✗ |
| USDJPY | 1h | donchian_20_10_long | -2.08 | -11.23 | -23.76 | 0.90 | 204 | 0.55 | ✗ |
| XAGUSD | 1h | atr_chandelier_long | **+0.57** | **+9.40** | -25.04 | 1.12 | 172 | 0.44 | ✗ |
| XAUUSD | 1h | atr_chandelier_long | **+0.31** | **+2.66** | -13.94 | 1.04 | 171 | 0.65 | ✗ |

Legend: PASS requires PBO<0.5 AND DSR p<0.05 AND WF≥6/8 AND OOS Sharpe>0 AND FWD Sharpe>0 AND median hold≤5d.

## Por-config aggregate (média simples 12 tickers)

| Config | Avg OOS Sharpe | Avg OOS CAGR % | Avg OOS MDD % | Avg trades OOS |
|--------|---------------:|---------------:|--------------:|---------------:|
| donchian_10_5_long   | -5.04 | -17.73 | -39.26 | ~350 |
| donchian_20_10_long  | -2.36 |  -9.14 | -21.24 | ~210 |
| atr_chandelier_long  | -2.88 |  -9.95 | -23.56 | ~170 |

Donchian_10_5 é universalmente o pior (entrada/saída curtas demais →
torrent de trades ruim que consome custo). Donchian_20_10 menos ruim
mas ainda negativo. ATR-Chandelier empata com donch_20_10 no agregado
mas é o único config que captura os 2 metais em território positivo.

## Citations

- `[trading_systems_methods, p.353]` — Donchian channel (Richard Donchian, *Futures*
  1950s; Turtle Traders 1983 aplicação clássica).
- `[volatility_trading]` — ATR-based Chandelier stop (Chuck LeBeau, *Volatility Based Money Management*).
- `[advances_fin_ml, ch.7]` — CPCV com embargo pra evitar leakage temporal em PBO.
- `[systematic_trading, p.185-188]` — hold-time discipline (median ≤ 5d gate inflexível;
  todos os configs cumprem: hold 0.73-1.13 dias, bem dentro do limite).

## Implicação pra Phase 3.5a

1. **Breakout intraday long-only 1h em FX majors é DEAD END** com custos
   de varejo. O gap estrutural (5-7 bps custo vs edge sub-7 bps) é
   idêntico ao T1 (BollingerMR MR): a frequência 1h em FX é cara demais
   pra ambas as famílias clássicas de trend e reversion.

2. **Metais têm edge parcial**, mas: (a) só 2 ativos, (b) falham PBO/DSR,
   (c) MaxDD 25% é incompatível com alavancagem Plano A sem risk management
   ativo. Metais isolados não podem ser winner Plano A; exigiriam ≥5 assets
   com edge replicável (mandate §3).

3. **Curto prazo**: nenhum patch salvará T2 — Donchian/ATR long são
   canônicos, sem hiperparametros escondidos. Pular pra T3
   (pairs/stat-arb intraday) onde hipótese é estruturalmente diferente
   (não depende de trend/reversion unidirecional, explora co-movimento).

4. **Médio prazo**: T5 (regime filter hybrid) pode voltar a MR/breakout
   em metais com filtro DXY/vol regime — mas só se T3/T4 também falharem.

## Next lead

**Lead T3 — Intraday pairs / stat-arb.** Cointegração ADF + Engle-Granger
em pares óbvios (EURUSD/GBPUSD, USDJPY/USDCHF). Se cointegrados → Kalman
pair-trade 1h. Citar `[machine_trading_chan]` (Kalman filter) +
`[advances_fin_ml, ch.7]` (CPCV).

## Links

- Per-ticker reports: `reports/phase3_5a/t2_donchian_breakout/*.md`
- Per-ticker JSON: `reports/phase3_5a/t2_donchian_breakout/*.json`
- Registry: `reports/phase3_5a/t2_donchian_breakout/registry.json`
- Jornada: `jornada/2026-04-18-1500-phase3.5a-T2-donchian-breakout-DEAD.md`

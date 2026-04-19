# [SHORT-HOLD CFD] Phase 3.5a — Lead T2: Donchian/ATR breakout 1h FX+metais = DEAD END

**Iteração:** 16 do loop Phase 3.5a (aggregator iter após 12 ticker sweeps)
**Lead:** T2 (segundo da lista ativa)
**Veredito:** **DEAD END** — 0/12 tickers passam 5-gate
**Próximo:** Lead T3 (Intraday pairs / stat-arb — cointegração + Kalman)

---

## O que foi testado

Breakout long-only clássico em 1h, 3 famílias:
- **Donchian 10/5** — entry no rompimento de 10 barras, exit no retorno
  a 5 barras `[trading_systems_methods, p.353]`.
- **Donchian 20/10** — versão Turtle Traders mais lenta.
- **ATR-Chandelier** — entrada em 20-bar high, trailing stop 3.0×ATR(14),
  time_stop 120 barras `[volatility_trading]`.

**Universo:** os 12 tickers Tiingo 1h da iter 1 — 10 FX majors
(AUD/EUR/GBP/JPY/CAD/CHF/NZD/US pares) + XAUUSD + XAGUSD. Janela
completa **2020-01-06 → 2026-04-14** (longest cache permite).

**Custos Pepperstone modelados:**
- FX: `half_spread` = 2 bps (Razor + commission $3.50/side)
- Metais: `half_spread` = 5 bps
- Swap: 0.005%/dia (~1.8%/ano)

**Splits:** IS 2020-2023 (4y) / OOS 2024-2025 (2y) / FWD 2026-Q1 stress.

**Execução:** 12 iters de sweep (iters 4-15), 1 ticker por iter via
fan-out protocol (SWEEP_MODE=fanout), per-ticker reports atômicos,
registry `reports/phase3_5a/t2_donchian_breakout/registry.json` como
ponto de continuidade entre iters.

---

## Resultado

**0/12 tickers PASS 5-gate.**

### FX majors — 10/10 DEAD

| Ticker | Best config | OOS Sharpe | OOS CAGR% | OOS MDD% | Hold (d) |
|---|---|---:|---:|---:|---:|
| audusd | atr_chandelier_long | -3.13 | -16.03 | -31.09 | 1.00 |
| eurgbp | atr_chandelier_long | -4.88 | -12.82 | -24.59 | 0.96 |
| eurjpy | donchian_20_10_long | -2.44 | -12.27 | -25.31 | 0.96 |
| eurusd | donchian_20_10_long | -2.90 | -10.89 | -21.18 | 0.73 |
| gbpjpy | donchian_20_10_long | -2.56 | -12.92 | -26.38 | 1.00 |
| gbpusd | atr_chandelier_long | -3.41 | -13.42 | -25.89 | 1.00 |
| nzdusd | atr_chandelier_long | -3.06 | -15.82 | -30.35 | 0.90 |
| usdcad | atr_chandelier_long | -5.28 | -16.11 | -30.69 | 0.88 |
| usdchf | atr_chandelier_long | -3.19 | -13.95 | -27.29 | 1.08 |
| usdjpy | donchian_20_10_long | -2.08 | -11.23 | -23.76 | 0.90 |

Todos os 10 FX majors produzem OOS Sharpe negativo, em todas as 3
configs. Best (USDJPY donchian_20_10_long) -2.08 é inferior ao pior
FX do T1 (-2.58 EURGBP short). Donchian_10_5 é sistematicamente
catastrófico (MDD -60% a -80% em 900-1100 trades).

### Metais — 2/2 positivos mas fail PBO/DSR/WF

| Ticker | Best config | OOS Sharpe | OOS CAGR% | OOS MDD% | Hold (d) | PBO | DSR p | WF | FWD Sharpe |
|---|---|---:|---:|---:|---:|---:|---:|:---:|---:|
| XAGUSD | atr_chandelier_long | **+0.57** | **+9.40** | -25.04 | 1.12 | 0.44 ✓ | 0.48 ✗ | 3/8 ✗ | +0.55 |
| XAUUSD | atr_chandelier_long | **+0.31** | **+2.66** | -13.94 | 1.04 | 0.65 ✗ | 0.67 ✗ | 2-3/8 ✗ | +1.57 |

XAGUSD é o mais próximo de PASS: PBO passa (0.44), FWD positivo (+0.55,
CAGR +16%), hold OK. Mas DSR p=0.48 e WF 3/8 bloqueiam. XAUUSD tem
convergência cross-config (PBO 0.65 — os 3 configs perdem similar)
indicando falta de robustez paramétrica.

### Cross-config aggregate (média 12 tickers)

| Config | Avg OOS Sharpe | Avg OOS CAGR% | Avg OOS MDD% |
|---|---:|---:|---:|
| donchian_10_5_long   | -5.04 | -17.73 | -39.26 |
| donchian_20_10_long  | -2.36 |  -9.14 | -21.24 |
| atr_chandelier_long  | -2.88 |  -9.95 | -23.56 |

---

## Por que falha

**FX majors 1h:**
- Spread+commission = 5-7 bps total por trade. Breakout long captura
  continuação de trend curtíssimo; em FX intraday, **muitos breakouts
  revertem ao range** (FX é mean-reverting em baixa frequência).
- Donchian_10_5 gera 900-1100 trades em 6.3 anos (×5-7 bps = ~50% do
  capital consumido em custo) — todos os configs perdem mesmo com
  edge zero no ativo.
- Donchian_20_10 e ATR-Chandelier têm menos trades mas a distribuição
  dos wins/losses é simétrica demais, e o custo de retrigger após
  whipsaw é linear.

**Metais funcionam parcialmente porque:**
- XAU/XAG tem regimes de trending forte (2020-2022 QE era, 2024-2026
  geopolítica) onde breakout captura alpha real.
- ATR-Chandelier (trailing solto) permite capturar move inteiro sem
  whipsaw.
- Mas: só 2 ativos no universo, falta amostra pra satisfazer
  multi-asset mandate §3; e os gates de robustez (PBO/DSR/WF) exigem
  regime-stable que metais não oferecem (2023 foi flat → WF degrada).

**Implicação estrutural confirmada (T1 + T2):**

Ambas as famílias clássicas canônicas — **mean-reversion (Bollinger)
e trend-following (Donchian/ATR)** — falham em FX 1h com custos de
varejo. O edge da estrutura intraday FX é pequeno demais pra
sobreviver 5-7 bps round-trip. Pra ressuscitar seria necessário:
- Mudar frequência pra 15m (não disponível Tiingo whitelist v1)
- Usar múltiplos sinais combinados (não canônico, alto risco overfit)
- Explorar estrutura cross-asset (cointegração → Lead T3)

---

## Verdict

**Lead T2 = DEAD END**. 0/12 PASS 5-gate. FX majors 10/10 catastroficamente
negativos; metais 2/2 positivos mas falham robustez.

Adicionado a `dead_ends` da memory.md: Donchian 10/5, 20/10 e
ATR-Chandelier long em 12 FX/metais 1h — **NÃO retestar long-only
breakout clássico nessa janela/frequência**.

---

## Próximo

**Lead T3 — Intraday pairs / stat-arb.**

Hipótese: cointegração estrutural entre pares FX (EURUSD/GBPUSD,
USDJPY/USDCHF) ou índices CFD (SPX500/NAS100 — indisponível Tiingo)
pode oferecer edge que sobrevive custos porque:
1. Entrada quando spread diverge > 2σ (não depende de direção
   absoluta do ativo)
2. Kalman filter adapta hedge ratio dinamicamente
3. Reversão ao equilíbrio é estatisticamente robusta (ADF/Engle-Granger
   confirma coerência)

Citação obrigatória: `[machine_trading_chan]` (Kalman pair-trade),
`[advances_fin_ml, ch.7]` (CPCV com embargo).

Se T3 também falhar → T4 (session-based FX) → T5 (regime filter hybrid)
→ T6 (rebalance meta mandate — "Plano A não suporta retorno > B,
pivot") → T7 (summary).

---

## Artefatos produzidos

- 12 per-ticker reports: `reports/phase3_5a/t2_donchian_breakout/{audusd,eurgbp,eurjpy,eurusd,gbpjpy,gbpusd,nzdusd,usdcad,usdchf,usdjpy,xagusd,xauusd}.{json,md}`
- Cross-ticker aggregate: `reports/phase3_5a/t2_donchian_breakout/AGGREGATE.md`
- Registry (state machine): `reports/phase3_5a/t2_donchian_breakout/registry.json` (status=done)
- Zero código modificado (strategy engine reusa `src/ai_trade/backtest/strategies/donchian_breakout.py` existente)
- Pytest baseline: ≥709 passed (não tocado)

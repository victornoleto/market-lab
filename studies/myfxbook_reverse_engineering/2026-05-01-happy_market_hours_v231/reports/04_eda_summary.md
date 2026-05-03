# EDA summary — Happy Market Hours v2.3.1 (MyFxBook id 1407880)

**Data:** 2026-05-01
**Período coberto:** 2013-09-02 → 2021-06-16 (7,8 anos)
**Sample:** 3 305 trades + 95 depósitos (3 400 raw rows scrapeadas em 170 páginas)
**Conta:** Demo, leverage 1:500, MetaTrader 4

## Resumo executivo

Strategy fingerprint reverse-engineerable com alta confiança nos eixos
**tempo, exit, sizing, universe.** Direction signal não-determinado sem
1m OHLC.

**Edge real existe:** full-sample annualized Sharpe **2.51** sobre net pips
após cost model Pepperstone Razor 2025 (spread + $7 commission).
Walk-forward 7/8 janelas positivas. DSR p-value < 0.0001.

**Edge tem variação grande de regime:** WF window 7 (2019-10 → 2020-08,
inclui COVID) Sharpe **−1.08**, todas demais janelas Sharpe entre +1.31
e +5.39. Recovery em window 8 (2020-08 → 2021-06) Sharpe +1.73.

**Gate §2.4 binding constraint:** single-block OOS bootstrap 99.9% CI low
**negativo** (-1.67) — não pelo Sharpe (1.89, alto) mas pela amostra OOS
de 192 dias ser pequena pro nível 99.9% conservador do mandate.

**Limitação crítica:** sem dados pós 2021-06-16. Vendor catalogou o sistema
como "OLD" e atribuiu URL `/old-happy-market-hours-v231/`, sugerindo
substituição interna pré-2021. **Edge persistente em 2026 não pode ser
verificado dessa amostra.**

## Strategy fingerprint (alta confiança)

### Entry timing
- Concentração brutal em **23:00-01:00 UTC** (3 304 / 3 305 = 99,97% das
  entradas).
- Pico em 23:55-00:05 UTC (rollover de dia broker).
- Day-of-week: Monday 1 130 (34%), Tuesday 640, Wed 543, Thu 610, Friday 318,
  Sun 64. Sábado zero. Concentração Mon+Sun-late = 36%.
- Janela horária = abertura da sessão asiática (Tokyo 08:00-10:00 JST) +
  pós-fechamento NY (17:00-19:00 ET).

**Hipótese:** strategy explora liquidez de transição NY-close → Tokyo-open,
quando ranges contraem e reversões intra-asiáticas têm payoff. Suporte
teórico: `[evidence_based_ta, Aronson, p.367-380]` para hour-of-day FX
effects.

### Universe
6 pares FX (sem JPY/AUD/NZD): GBPUSD (898), USDCAD (808), EURUSD (703),
EURCHF (370), USDCHF (287), EURGBP (239). Todos EUR/USD/GBP/CHF/CAD-cross.

Por sessão: median 2 trades, P95 6, max 14. Pairs/sessão distrib:
1=476, 2=387, 3=248, 4=86, 5=47, 6=18 — strategy diversifica entre 1-6
pares simultâneos, depende do que dispara naquela noite.

### Direction signal — não-determinístico em features observadas
| Eixo | Buy% | Spread |
|---|---:|---|
| Per pair | 39-53% | balanceado, sem pair-fixo |
| Per hour | 29-51% | 01:00 UTC tem 71% Sell (mas só 248 trades) |
| Per DOW | 46-50% | sem DOW-fixo (Sun 66% Buy mas n=64) |

Direction varia per-pair-per-evening; não é random (signal-driven) mas
o signal exige OHLC 1m que não temos pra reverse-engineer formalmente.

**Hipótese candidata** (não testada): direction segue o close 23:00 UTC
em relação a uma média móvel (e.g., breakout ou MR vs EMA(50) H1).
Suporte: pairs trading literature (`[carver_systematic_trading]`).

### Exit mechanism — time-based, não TP/SL
- Distribuição: **94,1% manual_or_time**, 5,8% near-SL, **0,1% near-TP**.
- TP **never hit at +100 pips em 8 anos** (zero TPs reais).
- Hold time: P50 = 1,02h, P95 = 3,20h, P99 = 4,80h, max = 8,60h. Todos
  intraday, fechados na mesma sessão asiática.
- Saída provável: timer de 60-90 min OU close at session-end (~04:00 UTC
  quando Tokyo bate London).

### Lot sizing — proportional ao equity, NÃO martingale
| Year | Lot median |
|---|---:|
| 2013 | 0,25 |
| 2017 | 3,11 |
| 2019 | 9,93 |
| 2021 | 15,92 |

- Per-month max/median ratio: P95 = **1,06** (lots dentro do mês idênticos).
- Doubling-after-loss test: **0 trades** com lot >= 1,7× anterior em janela
  < 24h.
- Crescimento monotônico ano-a-ano = % risk sizing puro acompanhando
  equity 0,25 → 17 (≈ 68× crescimento, consistente com +4 550% gain).

K1 (martingale) **não triggered** após análise robusta. Critério inicial
P95/P50 = 4,03 era falso positivo (refletia equity-scaling de 8 anos).

### SL/TP setting evolution
| Period | SL pips | TP pips |
|---|---:|---:|
| 2013-2018 | -40 | +60 |
| 2019 | -40 (P95 = +2 = SL solto?) | +60 |
| 2020+ | -80 | +120 |

Razão risco:reward sempre **1:1.5**. Em 2020 o vendor dobrou as bandas,
provavelmente em resposta à expansão de volatilidade COVID.

## Análise PnL e edge decay

### PnL gross + net (Pepperstone Razor 2025)
| Year | n | Win% | gross avg pips | net avg pips | sharpe net |
|---|---:|---:|---:|---:|---:|
| 2013 | 68 | 51% | 1,07 | **−0,25** | −0,03 |
| 2014 | 167 | 66% | 1,87 | 0,59 | 0,06 |
| 2015 | 484 | 69% | 2,45 | 1,08 | 0,09 |
| 2016 | 641 | 75% | 4,03 | **2,64** | **0,25** ← peak |
| 2017 | 394 | 75% | 3,46 | 2,07 | 0,20 |
| 2018 | 337 | 70% | 3,11 | 1,69 | 0,19 |
| 2019 | 497 | 70% | 1,43 | 0,26 | 0,04 |
| 2020 | 541 | 71% | 1,20 | **0,04** | **0,00** |
| 2021 | 176 | 74% | 1,38 | 0,25 | 0,04 |

**Pico de edge em 2016-2018, decay severo a partir de 2019.** O vendor
optou por "OLD" precisamente nessa fase — provavelmente substituiu por
v2.4+ ou outros EAs que não temos histórico.

### Net PnL por par (full sample)
| Symbol | n | gross avg | cost | **net avg** | Win% net |
|---|---:|---:|---:|---:|---:|
| USDCHF | 287 | 4,50 | 1,45 | **+3,05** | 71% |
| EURCHF | 370 | 4,83 | 1,90 | **+2,93** | 78% |
| GBPUSD | 898 | 2,95 | 1,20 | **+1,75** | 69% |
| EURGBP | 239 | 2,00 | 1,45 | +0,55 | 58% |
| EURUSD | 703 | 1,26 | 0,83 | +0,43 | 67% |
| USDCAD | 808 | 1,34 | 1,44 | **−0,10** | 57% |

**USDCAD perde dinheiro em Pepperstone** (cost > gross). Os 808 trades
foram net-negativos no cost model proposto — viés de pares com spread
mais alto. Strategy tem que filtrar USDCAD ou aceitar que essa fração
do volume é dilutiva.

## Gates §2.4 verdict

Aplicados sobre PnL diário observado − cost model Pepperstone Razor 2025.

| Gate | Critério | Resultado | Verdict |
|---|---|---:|---|
| 2 (DSR p < 0.05) | full sample | p = 0,0000 | ✅ PASS |
| 3 (WF ≥ 6/8) | 8 windows of full sample | 7/8 positivas | ✅ PASS |
| 4 (Single-block OOS) | last 12mo Sharpe + bootstrap 99.9% CI > 0 | Sharpe 1.89, **CI low −1.67** | ❌ FAIL |
| 6 (Full bootstrap CI) | 99.9% CI low > 0 | CI [1.075, 4.013] | ✅ PASS |

Skip: Gate 1 (PBO — sem grid de busca), Gate 5 (FWD 3mo stress —
seria 2021-03 a 2021-06, não testado isoladamente), Gate 7 (cross-lib
— numpy reference apenas).

**Gate 4 FAIL é estatístico, não estrutural.** OOS Sharpe 1,89 seria
robusto a qualquer nível de confiança ≤ 99%. O nível 99.9% do mandate
exige amostra muito maior pra estabilizar (192 dias vs ~500+ ideais).

### Walk-forward windows
```
window  start       end         n_days  sharpe   mean_net_pips
1       2013-09-02  2015-05-12  162     1.475    +2.21
2       2015-05-15  2016-04-12  161     3.283    +5.25
3       2016-04-13  2017-01-30  161     5.389    +7.91
4       2017-02-03  2018-01-08  161     3.917    +4.19
5       2018-01-09  2018-12-13  161     3.454    +3.43
6       2018-12-14  2019-10-29  161     1.306    +0.94
7       2019-10-30  2020-08-06  161    -1.077    -1.17  ← COVID
8       2020-08-07  2021-06-16  161     1.727    +1.31
```

Pattern claro: edge era 3-5× Sharpe em 2015-2018, decayou pra 1,3 em
2019, virou negativo durante COVID 2019-10/2020-08, recuperou em window
8 (mas amostra só 161 dias).

## Mandate alignment — Plano A reactivation criteria

| Cláusula | Status |
|---|---|
| §3.1 Multi-asset | **Parcial.** Strategy já cobre 6 FX majors/crosses (GBPUSD/EURUSD listados em §3.1; EURGBP/EURCHF/USDCHF/USDCAD não). Falta Index (SPX500/NAS100), Gold (XAUUSD), Crypto (BTCUSD/ETHUSD), JPY/AUD majors. Transferência precisa de OHLC + replicator. |
| §3.3 Sweep leverage 1:1→1:200 | Untested (precisa do replicator). |
| §3.5 Dynamic sizing | Strategy tem proportional sizing nativo; precisaria adaptar regime "preservação" pós 2× equity. |
| §3.6 Capital mínimo $5k Pepperstone Index CFD | Strategy é FX, não Index — capital mínimo distinto, precisa lot-granularity test. |
| §2.4 Gates hard-block | **3/4 PASS, 1/4 FAIL.** Gate 4 OOS bootstrap CI low <0 é hard-block. |

**Fundamental:** sem dados 2021-07 → 2026-05 (5 anos), não há como verificar
se o edge persiste em 2026. WF window 8 (2020-08 → 2021-06) sugere recovery,
mas é stale evidence.

## Hipótese formal de regra (para futuro replicador, se executado)

```
DENOMINATION: Asian Session Multi-Pair Reversion (AS-MPR)
TIMING: 23:00-01:00 UTC (peak 23:55-00:05)
DOW FILTER: weekday + Sunday-late (Tokyo Mon open). Skip Saturday.
UNIVERSE: 6 FX majors/crosses {GBPUSD, EURUSD, USDCAD, EURCHF, USDCHF, EURGBP}
ENTRY:
  - At session-rollover bar, evaluate signal per pair (TBD without OHLC).
  - Open 1-6 simultaneous positions.
  - Position size: % of equity (proportional, ~constant lot/equity ratio).
EXIT:
  - Time-based: max 1-3 hours hold; close end-of-asian-session (~04:00 UTC).
  - SL: -40 pips (era 2013-2019), -80 pips (era 2020+). Rarely hit (5.8%).
  - TP: +60 pips (-2019), +120 pips (2020+). Almost never hit (0.1%).
COST MODEL (forward Pepperstone Razor 2025): 0.83-1.90 pips/trade RT.
```

## Caveats e known unknowns

1. **Direction signal não-identificado** — sem 1m OHLC dos 6 pares no
   período, não dá pra reverse-engineer o que dispara Buy vs Sell. Hipóteses
   candidatas: prior-bar continuation, breakout vs EMA(N) on H1, news-flow
   filter.

2. **5 anos de blackout** (2021-07 → 2026-05). Strategy classificada "OLD"
   pelo vendor — provavelmente substituída em vendor's catalog porque
   stopped working. Sem validação direta.

3. **Demo account** — sem swap, slippage, requote, rejection real. Cost
   model adicional aplicado é forward-Pepperstone, mas o vendor's account
   broker (Roboforex 1:500) tem perfil de execução diferente. Slippage
   real pode ser maior em real money.

4. **Vendor business model** — `www.happyforex.de` vende EAs como produto.
   Track record é marketing. Survivorship bias (winners shown, losers
   removed) é estrutural ao perfil — outras versões do mesmo EA
   provavelmente blow-upped silently.

5. **USDCAD net-negativo** em Pepperstone (cost > gross): sugere que se
   replicar live, pair-filter é mandatório. EUR-cross pairs (EURCHF,
   USDCHF) têm o melhor net — mas com spread Pepperstone alto (1,2-1,5
   pips), mesmo eles têm cost > 50% do gross.

## Citações

- `[evidence_based_ta, Aronson, p.367-380]` — hour-of-day e session-effects em FX
- `[advances_fin_ml, p.196-202]` — Deflated Sharpe Ratio (DSR)
- `[advances_fin_ml, p.208-211]` — Probability of Backtest Overfitting (PBO)
- `[fooled_by_randomness, Taleb]` — vendor track-record bias e survivorship
- `[systematic_trading, Carver, p.185-188]` — fixed commission dominates at retail
- `[carver_systematic_trading]` — direction signal hypothesis (breakout/MR)

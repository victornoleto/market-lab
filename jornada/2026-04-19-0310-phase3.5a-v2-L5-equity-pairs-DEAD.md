# [SHORT-HOLD CFD] V2-L5 — Equity pairs cointegração DEAD: 0/6 pares, arbitragem institucional apaga edge

**Data:** 2026-04-19 03:10 (iter 66, loop `phase3.5a-v2/plano-a-last-attempt-20260418`)
**Lead:** V2-L5 (sweep-tickers, aggregator) — pairs-trading market-neutral com cointegração EG + Kalman β + 2σ/0σ/4σ.
**Verdict:** ❌ DEAD END (0/6 pares cointegrados; nenhum trade gerado em nenhum par).

---

## O que fizemos

V2-L5 tentou o arquétipo clássico de pairs-trading de Chan (`[algo_trading_chan, p.42-54]`,
`[machine_trading_chan, ch.3]`) em 6 pares de ETFs líquidos US — selecionados por
relação econômica forte a priori — para ver se algum ainda carrega
spread mean-reverting utilizável como edge Plano A short-hold CFD:

- **GLD_SLV** — ouro vs. prata (metais preciosos).
- **QQQ_XLK** — Nasdaq-100 vs. tech sector.
- **SPY_IWM** — large-cap vs. small-cap.
- **TLT_IEF** — long-duration vs. intermediate-duration Treasuries.
- **XLE_USO** — energy sector vs. oil futures.
- **XLF_HYG** — financial sector vs. high-yield bonds.

Per-ticker pipeline (iter 60-65, um par por iter via fan-out protocol):
1. OLS Engle-Granger → resíduo `u_t = log(y) - α - β·log(x)`.
2. ADF sobre `u_t` → pass se `p ≤ 0.05`.
3. Se pass: Kalman filter para β dinâmico, z-score sobre janela 60d, entry ±2σ, exit 0σ, stop ±4σ, hold cap 30d, custos Pepperstone Razor (spread 2bps half + commission $3.50/side + slippage 1-3bps + swap 0.005%/dia cada perna).
4. Métricas IS/OOS/FWD + walk-forward 8 janelas + 5-gate framework V2 + 7 subset gates.

## O que encontramos

| Pair    | Window (y) | Bars | ADF stat | ADF p  | OLS β   | Kalman β | Cointegrado | Trades | PASS |
|---------|------------|------|----------|--------|---------|----------|-------------|--------|------|
| GLD_SLV | 20.0       | 5021 | -2.239   | 0.192  | 0.898   | 0.485    | NO          | 0      | NO   |
| QQQ_XLK | 22.6       | 5698 | -1.237   | 0.658  | 1.014   | 0.945    | NO          | 0      | NO   |
| SPY_IWM | 24.9       | 6266 | -2.504   | 0.115  | 1.121   | 0.802    | NO          | 0      | NO   |
| TLT_IEF | 12.3       | 3088 | +0.819   | 0.992  | 1.675   | 1.671    | NO          | 0      | NO   |
| XLE_USO | 20.0       | 5034 | -1.546   | 0.511  | -0.137  | 0.536    | NO          | 0      | NO   |
| XLF_HYG | 12.3       | 3088 | -2.697   | **0.0746** | 2.666 | 1.563 | NO (closest) | 0    | NO   |

**Zero trades em todos os 6 pares** (nenhum cointegrado ⇒ o filtro
ADF nunca deixa entrar posição). Subset gates: 1/7 cada (só
`oos_maxdd_le_25pct` passa trivialmente porque não há equity
drawdown).

## Por que falha (diagnóstico econômico)

**A hipótese que V2-L5 testou é ingênua para ETFs líquidos US em
2026.** Nos anos 1990-2005 Chan mostrou pair-trading profitable em
equities individuais e alguns ETFs nascentes (`[algo_trading_chan, p.42]`).
Em 2026, esses spreads são visibilíssimos e arbitrados por HFT /
quant funds em timeframes de segundos-minutos; o que resta em daily
é ruído correlacionado, não mean-reversion estrutural. A ADF
reflete isso:

- **SPY/IWM** (small vs. large): descolado pós-2021 por rate
  sensitivity (small-cap unprofitability) e MAG7 dominance.
- **QQQ/XLK**: XLK virou ~25% do QQQ pré-MAG7, mas MAG7
  concentração pós-2021 (NVDA, MSFT, AAPL, GOOG, META, AMZN, TSLA)
  quebra a paridade.
- **TLT/IEF** (p=0.992 — o mais refutado): rates zero-bound
  2014-2021 + hikes 2022-2024 + cuts 2024 injetam non-stationarity
  estrutural — o spread β≈1.67 é consistente com duration mas não
  é estacionário em ciclo completo.
- **XLE/USO**: β OLS **−0.137** é economicamente absurdo (energy
  equity deveria seguir oil positivamente). USO sofre contango
  drag (roll perdido) enquanto XLE reflete spot+upstream equity —
  **decoupling estrutural**, não pair-trade recuperável.
- **GLD/SLV**: silver carrega componente industrial (eletrônicos,
  solar, baterias) que rompe paridade em ciclos de manufacturing;
  correlação alta, mas spread integrado.
- **XLF/HYG (p=0.0746, closest):** credit-spread sensitivity
  compartilhada teoricamente, mas em 2022-2024 **Fed hikes atingem
  HYG por duration (price ↓) e beneficiam XLF por NIM expansion
  (price ↑)** — drivers parcialmente anuláveis quebram
  cointegração. β OLS 2.67 é anômalo: um ETF setorial não "segue"
  bonds com duplo de sensibilidade — provavelmente Engle-Granger
  capturou regressão espúria `[advances_fin_ml, ch.7]`.

O universo Pepperstone CFD (blue-chip global: SPY, QQQ, GLD, SLV,
BTC, ETH, majors FX) **não contém** os instrumentos onde pair-trading
retém edge em 2026 (micro-cap equities, specific corporate bond
pairs, cross-listed ADRs) — portanto V2-L5 é estruturalmente
incapaz de produzir winner para Plano A.

## O que isso informa para Plano A

- **V2-L5 para `## Dead ends`** em `docs/self_improvement/memory.md`.
- Winner Plano A permanece `gayed_ema100_L2_off_gld` standalone
  (Sharpe OOS 2.285, CAGR 79.14%, MDD -21.02%, hold 6d — iter 43).
- `winners_short_hold:` intacto (2 entradas).
- **Stop rule V2 não dispara** — já há 1 PASS em
  `winners_short_hold`; restam L6 (vol breakout multi-asset) + L7
  (verdict final).
- Confirma V1-T3 (Kalman pair-trade FX 1h) e V1-T4 (session-based
  FX 1h): pair-based e session-based são classes refutadas para
  Plano A em ETF/CFD líquido. Edge Plano A é **momentum/rotação
  leveraged** (Gayed-class), não relative-value.

## Próximos passos

**Iter 67 = V2-L6 bootstrap** (fan-out mode, sweep-configs, 12
configs × índices+commodities+FI, vol breakout sobre ATR+Donchian):

- lookback ∈ {20, 50, 100}d
- exit ∈ {trailing ATR 3×, opposite channel}
- direction ∈ {long-only, long/short}
- Citação: `[trading_systems_methods, p.353]`, `[volatility_trading]`,
  `[trend_following_covel, ch.5]`.

Iter budget remanescente: L6 (~14 iters) + L7 (1 iter atomic) = 15
iters para fechar V2.

## Citações

- `[algo_trading_chan, p.42-54]` — pair-trading: edge extinto em ETFs líquidos por arbitragem institucional.
- `[machine_trading_chan, ch.3]` — Kalman β dinâmico; casos negativos comuns em ETFs maduros.
- `[advances_fin_ml, ch.7]` — non-stationarity em séries financeiras; ADF requer estacionariedade estrutural.
- `[systematic_trading, p.185-188]` — retail CFD: spread+commission dominantes, trades infrequentes inviáveis sem edge claro.

## Artifacts

- AGGREGATE: [`reports/phase3_5a_v2/v2_l5_equity_pairs/AGGREGATE.md`](../reports/phase3_5a_v2/v2_l5_equity_pairs/AGGREGATE.md)
- Per-pair: `reports/phase3_5a_v2/v2_l5_equity_pairs/{GLD_SLV,QQQ_XLK,SPY_IWM,TLT_IEF,XLE_USO,XLF_HYG}.md`
- Registry: `reports/phase3_5a_v2/v2_l5_equity_pairs/registry.json` (status=done)

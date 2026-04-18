# Lead T3 — Intraday pairs / stat-arb (cointegração + Kalman pair-trade 1h) — aggregate

**Phase:** phase3_5a | **Lead:** T3 | **Status:** DEAD END (0/6 PASS)
**Period:** 2020-01-06 → 2026-04-14 (~6.3y, Tiingo IEX 1h cache)
**Tested:** 6 pairs × 3 configs = 18 runs
**Aggregation iter:** 24
**Registry:** `reports/phase3_5a/t3_intraday_pairs_statarb/registry.json`

## Summary

Lead T3 testou 3 famílias de pair-trading — **OLS-rolling hedge** (Bollinger
z>2 entry / z>0 exit) e dois **Kalman δ=1e-4 Ve=1e-3** (exits z=0 e z=0.5)
— em 6 pares canônicos: 3 FX (audusd/nzdusd, eurusd/eurgbp, eurusd/gbpusd),
1 JPY/CHF pair (usdjpy/usdchf), 1 equity (spy/qqq), 1 metal (xauusd/xagusd).
Janela 2020-01-06 → 2026-04-14 (longest cache 1h). Custos Pepperstone Razor
modelados `[systematic_trading, p.185-188]`: half_spread 2-10 bps/leg +
commission $3.50/side + swap 0.005%/dia (~1.8%/yr) **em cada uma das 2
pernas**. **Zero pares passam 5-gate.**

**Cointegração IS é condição necessária mas insuficiente.** Apenas 2/6
pares cointegraram @ 5% (audusd_nzdusd EG p=0.0019, eurusd_gbpusd
p=0.0122) `[algo_trading_chan, p.42-54, ch.2]`; ambos perdem OOS
(Sharpe -1.70 e -1.95 respectivamente). Os 4 pares NÃO cointegrados
também perdem (ou marginalmente ganham mas violam outros gates). O
único config com OOS Sharpe **positivo** foi spy_qqq kalman_z2_exit0
(+0.13, CAGR +0.65%), mas:

1. Par NÃO cointegrado IS (p=0.0706 > 5%).
2. **Median hold 9.04 dias OOS (12-23d em FWD)** — viola gate inflexível
   `median_hold ≤ 5d` `[systematic_trading, p.185-188]`. Equity CFD tem
   swap ~0.005%/dia cumulativo em hold longo — mesmo com Sharpe positivo,
   o P&L real em hold de 23 dias seria catastroficamente erodido.
3. DSR p=0.764 (muito longe de <0.05), WF 3/8 (precisa ≥6/8).

**Único ticker que passou PBO** (0.3571, primeiro T3-pass): spy_qqq —
ironicamente o NÃO cointegrado. Indica que PBO mede dispersão de
performance cross-config, não edge absoluto; os outros 5 pares convergem
todos pra negativo (PBO 0.53-0.99).

## Cross-ticker table (best config por par)

| Pair | Freq | Best config | Sharpe OOS | CAGR OOS % | MDD OOS % | Hold (d) | Trades OOS | PBO | Coint IS | 5-gate PASS |
|------|------|-------------|-----------:|-----------:|----------:|---------:|-----------:|----:|:--------:|:-----------:|
| AUDUSD/NZDUSD | 1h | `ols_z2_exit0`     | -1.70 |  -4.01 |  -8.28 | 0.31 | 282 | 0.8016 ✗ | ✓ p=0.0019 | ✗ |
| EURUSD/EURGBP | 1h | `ols_z2_exit0`     | -1.55 |  -4.44 | -10.40 | 2.42 | 134 | 0.6905 ✗ | ✗ p=0.1253 | ✗ |
| EURUSD/GBPUSD | 1h | `ols_z2_exit0`     | -1.95 |  -3.76 |  -7.81 | 1.29 | 176 | 0.9048 ✗ | ✓ p=0.0122 | ✗ |
| SPY/QQQ       | 1h | `kalman_z2_exit0`  | **+0.13** | **+0.65** | -3.93  | **9.04** | 36 | 0.3571 ✓ | ✗ p=0.0706 | ✗ (hold) |
| USDJPY/USDCHF | 1h | `kalman_z2_exit0`  | -1.10 |  -6.20 | -15.56 | 1.13 | 137 | 0.5317 ✗ | ✗ p=0.4387 | ✗ |
| XAUUSD/XAGUSD | 1h | `ols_z2_exit0`     | -0.88 | -17.24 | -40.26 | 0.08 | 202 | 0.9921 ✗ | ✗ p=0.1275 | ✗ |

Legend: PASS requires PBO<0.5 AND DSR p<0.05 AND WF≥6/8 AND OOS Sharpe>0
AND FWD Sharpe>0 AND cointegrated IS AND median hold ≤ 5d. Costs:
half_spread 2bps (FX) / 10bps (equity) / 5bps (metal) per leg +
commission $3.5/side + swap 0.005%/d.

## Por-config aggregate (média 6 pares)

| Config | Avg OOS Sharpe | Avg OOS CAGR % | Avg OOS MDD % | Comment |
|--------|---------------:|---------------:|--------------:|---------|
| ols_z2_exit0       | -1.28 |  -6.01 | -13.05 | Melhor em média, mas ainda todos negativos exceto 0 hits |
| kalman_z2_exit0    | -1.66 |  -9.05 | -18.52 | State-space overfit: IS ajusta bem, OOS degrada mais |
| kalman_z2_exit0p5  | -1.84 |  -9.80 | -19.32 | Exit apertado (z=0.5) reduz captura do profit taking |

**Padrão:** Kalman configs degradam mais do que OLS rolling em todos os
pares — confirma overfit warning `[machine_trading, p.76-79, ch.3]`
(EWA-EWC SSM Kalman).

## Por que falha

**1. Custos dobrados (pair = 2 legs).** Em FX: 4 bps round-trip (spread)
+ $7 commission por round-trip + 0.01%/dia swap (2 legs). Em equity CFD
(SPY/QQQ) dobra: 20 bps round-trip + commission + 0.01%/d. Um trade
médio precisa de +25-30 bps só pra cobrir custos; z-score mean-reversion
em 1h captura ~10-15 bps por convergência típica. Negative-sum game
estrutural.

**2. Cointegração IS decai OOS.** Pares que cointegram IS (audusd_nzdusd
p=0.002, eurusd_gbpusd p=0.012) têm relação instável: a relação EG IS
não persiste na janela OOS (ambos os pairs cointegrados perdem mais
que os não-cointegrados). Confirma `[machine_trading, p.76-79, ch.3]`
— state-space overfit em estatísticas cross-sectional.

**3. Hold-time trade-off irresolvível.** Kalman com exit z=0 gera hold
~9 dias em SPY/QQQ (marginalmente rentável mas viola gate); exit z=0.5
reduz hold mas mata captura. Não há janela paramétrica em que o edge
sobrevive custos E respeita hold ≤ 5d.

**4. Metal (XAU/XAG) pair-trade catastrófico.** XAUUSD-XAGUSD **não
cointegrou** (p=0.127) e PBO 0.99 (os 3 configs convergem para perda
similar). Embora individualmente XAU/XAG mostrem edge em T2 (ATR
breakout), a **razão** entre eles é dominada por regime (gold-silver
ratio), não por reversão estatística. 202 trades, CAGR -17%, MDD -40%.

## Implicação estrutural

Lead T1 (BollingerMR 0/36) + Lead T2 (Donchian/ATR breakout 0/12) + Lead
T3 (Pair-trade 0/6) = **54 runs em 1h com custos Pepperstone retail, 0
winner**. As 3 famílias clássicas canônicas (mean-reversion single-asset,
trend-following, statistical-arbitrage cross-asset) **não sobrevivem**
custos 1h retail. Essa é uma descoberta estrutural de mandate, não
falha de execução.

**Próximos candidatos:**
- Lead T4 (session-based FX) — explora estrutura temporal intraday
  (Asia range/London open/NY close) com custos localizados em poucos
  bars/dia.
- Lead T5 (regime filter + BollingerMR GARCH) — retrofit filtro sobre
  baseline já validado (BollingerMR GARCH SPY 1h L=2 PARTIAL-GO), não
  strategy nova.
- Lead T6 (rebalance mandate meta) — se T4+T5 ambos DEAD, documentar
  honestamente que **Plano A short-hold CFD não suporta retorno > Plano
  B (~29%/yr)** e pivot mandate §3.

## Citations

- Engle-Granger cointegration (ADF on OLS residuals): `[algo_trading_chan, p.42-54, ch.2]`
- Bollinger-band pair-trade entry/exit z-score: `[algo_trading_chan, p.71-73, ch.3]`
- Kalman dynamic hedge-ratio δ=1e-4, Ve=1e-3: `[algo_trading_chan, p.75-80, ch.3]`
- Kalman/SSM overfit warning (EWA-EWC): `[machine_trading, p.76-79, ch.3]`
- 5-gate framework (PBO/DSR/WF/CPCV): `[advances_fin_ml, ch.7, p.208-211]`
- Hold ≤ 5d swap-kill para short-hold CFD: `[systematic_trading, p.185-188]`

## Links

- Per-pair reports: `reports/phase3_5a/t3_intraday_pairs_statarb/{audusd_nzdusd,eurusd_eurgbp,eurusd_gbpusd,spy_qqq,usdjpy_usdchf,xauusd_xagusd}.{json,md}`
- Registry: `reports/phase3_5a/t3_intraday_pairs_statarb/registry.json`
- Jornada: `jornada/2026-04-18-1420-phase3.5a-T3-pairs-statarb-DEAD.md`

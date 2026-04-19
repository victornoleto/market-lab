# [SHORT-HOLD CFD] T2 sweep — USDCAD FAIL (8/12)

**Phase 3.5a · iter 11 · Lead T2 (Donchian/ATR breakout long) · ticker 8 of 12**

## Verdict

**NO-GO.** Todas as 3 configs falham 5-gate em USDCAD 1h 2020-01-06 →
2026-04-14 (pending: 4 tickers — usdchf/usdjpy/xagusd/xauusd).

| Config | OOS Sharpe | OOS CAGR% | OOS MDD% | Trades | Hold(d) | DSR p | WF k/N | 5-gate |
|---|---:|---:|---:|---:|---:|---:|---:|:---:|
| `donchian_10_5_long`    | **-6.48** | -18.86 | -35.29 | 370 | 0.44 | 1.000 | 0/8 | ✗ |
| `donchian_20_10_long`   | **-5.52** | -15.69 | -29.98 | 216 | 0.75 | 1.000 | 0/8 | ✗ |
| `atr_chandelier_long`   | **-5.28** | -16.11 | -30.69 | 188 | 0.88 | 1.000 | 0/8 | ✗ |

**PBO cross-config:** 0.3413 (pass — configs não permutam muito IS→OOS,
mas isso não salva — todas negativas em absoluto).

## O que isso diz

1. **USDCAD é pior ticker da sweep até agora.** OOS Sharpe -6.48 em
   donchian_10_5 bate eurgbp (-5.93) e gbpjpy (-2.56). MaxDD FULL
   -70.77% em donchian_10_5_long é catastrófico (1108 trades sangrando
   em custos).
2. **Hold 0.44-0.88d** — mesmo pattern over-trigger dos 7 anteriores.
   Custos fixos (5 bps half-spread + $3.50×2 comm em >370 trades OOS)
   consomem qualquer edge residual de breakout.
3. **FWD 2026Q1** negativo nos 3 (-4.83/-3.71/-4.38) — regime 2026
   desfavorece breakout long em FX majors.
4. **Benchmark SPY dura** — SPY mesma janela 2020-2026 CAGR +14.64%
   Sharpe 0.77; strategy IR -1.66 vs SPY. Excess CAGR -32.53%. Beta
   -0.053 (descorrelacionado de SPY, mas ruim absoluto).

## Padrão após 8 tickers FX/majors

| Ticker | Best config | Best OOS Sharpe | Best OOS CAGR% | PBO |
|---|---|---:|---:|---:|
| audusd | atr_chandelier_long | -3.13 | -16.03 | 0.78 |
| eurgbp | atr_chandelier_long | -4.88 | -12.82 | 0.73 |
| eurjpy | donchian_20_10_long | -2.44 | -12.27 | 0.32 |
| eurusd | donchian_20_10_long | -2.90 | -10.88 | ? |
| gbpjpy | donchian_20_10_long | -2.56 | -12.91 | ? |
| gbpusd | atr_chandelier_long | -3.41 | -13.42 | ? |
| nzdusd | atr_chandelier_long | -3.06 | -15.82 | ? |
| usdcad | atr_chandelier_long | **-5.28** | -16.11 | 0.34 |

**0/8 PASS.** Zero sinal de que FX majors 1h aceitam breakout long.
Próximo: usdchf/usdjpy/xagusd/xauusd (4 restantes) — só metais (XAG/XAU)
têm chance realista de salvar a sweep por serem trending assets, mas
histórico de commodities 1h suggests edge também small.

## Citações

- Donchian 10/5 & 20/10 `[trading_systems_methods, p.353]`
- Chandelier trailing ATR `[volatility_trading]`
- 5-gate (PBO/DSR/WF) `[advances_fin_ml, ch.7, p.208-211]`
- Hold ≤ 5d swap-kill `[systematic_trading, p.185-188]`
- Custos Pepperstone Razor (`docs/investment-mandate.md §3`)

## Próximo

Ticker 9/12 = `usdchf` (head-of-queue). Continua T2 sweep 1 ticker/iter
até aggregator iter (após 12/12 done).

## Arquivos

- `reports/phase3_5a/t2_donchian_breakout/usdcad.json`
- `reports/phase3_5a/t2_donchian_breakout/usdcad.md`
- `reports/phase3_5a/t2_donchian_breakout/registry.json` (status=sweeping, pending=4, done=8)

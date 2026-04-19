# [SHORT-HOLD CFD] T2 sweep — EURGBP FAIL (2/12)

**Phase 3.5a · iter 5 · Lead T2 (Donchian/ATR breakout long) · ticker 2 of 12**

## Verdict

**NO-GO.** Todas as 3 configs falham 5-gate em EURGBP 1h 2020-01-06 →
2026-04-14 (pending: 10 tickers FX/metal).

| Config | OOS Sharpe | OOS CAGR% | OOS MDD% | DSR p | WF k/N | 5-gate |
|---|---:|---:|---:|---:|---:|:---:|
| `donchian_10_5_long`    | **-5.93** | -16.00 | -30.15 | 1.000 | 0/8 | ✗ |
| `donchian_20_10_long`   | **-5.10** | -12.65 | -24.29 | 1.000 | 0/8 | ✗ |
| `atr_chandelier_long`   | **-4.88** | -12.82 | -24.59 | 1.000 | 0/8 | ✗ |

**PBO cross-config:** 0.7302 (fail — configs sobrefitam IS, permutam
em OOS; `[advances_fin_ml, p.208-211]`).

## O que isso diz

1. **EURGBP é range-bound mesmo em 1h.** Par cross eur/gbp tem
   vol-of-vol menor que majors USD-quoted; breakouts long saem em
   swing-high e retornam à média. Signal-noise ratio < 1.
2. **Hold 0.42-0.96d** (10/5-27 bars) — igual audusd. Chandelier
   amplia hold ~2× (donchian_10_5) mas edge continua negativo.
3. **FWD window (2026 Q1) ainda pior** (Sharpe -7.25/-5.82/-8.98) —
   2026 market regime mata o que pouco IS edge existia. Custos fixos
   (5 bps half-spread + $3.50×2 comm × ~338 trades OOS) dominam.
4. Confirma hipótese T1: **MR/range pairs não aceitam breakout long
   sem filtro regime/vol.**

## Citações

- Donchian 10/5 & 20/10 `[trading_systems_methods, p.353]`
- Chandelier trailing ATR `[volatility_trading]`
- 5-gate (PBO/DSR/WF) `[advances_fin_ml, ch.7, p.208-211]`
- Hold ≤ 5d swap-kill `[systematic_trading, p.185-188]`
- Custos Pepperstone Razor (`docs/investment-mandate.md §3`)

## Próximo

Ticker 3/12 = `eurjpy` (head-of-queue). Continua T2 sweep 1
ticker/iter até aggregator iter (após 12/12 done).

## Arquivos

- `reports/phase3_5a/t2_donchian_breakout/eurgbp.json`
- `reports/phase3_5a/t2_donchian_breakout/eurgbp.md`
- `reports/phase3_5a/t2_donchian_breakout/registry.json` (status=sweeping, 10 pending)

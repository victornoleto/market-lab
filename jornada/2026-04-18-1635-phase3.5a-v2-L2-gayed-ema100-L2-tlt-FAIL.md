# 2026-04-18 16:35 — Phase 3.5a-V2 Lead V2-L2 [SHORT-HOLD CFD] (sweep-configs, iter 26) — `gayed_ema100_L2_off_tlt` FAIL (2 gates)

**Path tag:** [SHORT-HOLD CFD]
**Status:** ❌ FAIL (2 subset gates: `wf_pass`, `oos_maxdd_le_25pct`)
**Position na sweep:** 11/27 configs (10 SMA200+1 EMA100 done, 17 pending)

## Config

- Regime signal: **EMA100** (faster-adapting MA vs SMA200)
- Leverage: **2×**
- Off-regime asset: **TLT** (long-duration Treasury — rising-rates-toxic 2022)
- Risk-on universe: {SPY, QQQ} daily close
- Cost model: Pepperstone Razor CFD (spread 4bps RT + commission 6.6bps RT + slippage 3bps RT + swap −0.005%/d levered)
- Window: 2001-05-14 → 2026-04-14 (25y, 6266 bars, **616 regime switches** — idêntico a EMA100_L2_cash, 2× SMA200)

## Resultado

| Split | Sharpe | CAGR | MaxDD | Final eq |
|-------|-------:|-----:|------:|---------:|
| IS  | **2.254** | 64.13% | −17.75% | 3 747.5 |
| OOS | **2.017** |  68.93% | **−27.69%** | 23.1 |
| FWD | **1.830** | 55.93% | −14.72% | 2.74 |

WF 8/8 profitable mas **max window drawdown 27.7% > 25% cap** → WF=FAIL.
MedHold 6.0d (≥3d ✓). Cost drag 125.8% tx + −44.9% swap (invariante entre off_cash e off_tlt).

## Subset gates 5/7 pass

| Gate | Valor | Pass |
|------|------:|:----:|
| oos_sharpe_gt_0 | 2.017 | ✅ |
| fwd_sharpe_gt_0 | 1.830 | ✅ |
| wf_pass | 27.7% > 25% | ❌ |
| median_hold_ge_3d | 6.0d | ✅ |
| oos_cagr_ge_30pct | 68.9% | ✅ |
| oos_sharpe_ge_2 | **2.017 ≥ 2.0** | ✅ |
| oos_maxdd_le_25pct | −27.7% > 25% | ❌ |

**Failed:** wf_pass, oos_maxdd_le_25pct.

## Comparação vs SMA200 L2 off_tlt (iter 17)

| Métrica | SMA200_L2_tlt | EMA100_L2_tlt | Δ |
|---------|--------------:|--------------:|---:|
| Switches | 310 | 616 | +99% |
| IS Sharpe | 1.508 | 2.254 | +49% |
| OOS Sharpe | 1.467 | **2.017** | **+37.5%** |
| OOS MDD | −36.55% | −27.69% | **+8.86 pp** |
| FWD Sharpe | 1.291 | 1.830 | +42% |

**EMA100 > SMA200 confirmado segunda vez** (primeira foi EMA100_L2_cash iter 25):
sinal mais adaptativo produz Sharpe estruturalmente mais alto em todo off-regime `[leverage_for_the_long_run, p.11, p.14]` — gap de ~35-40% em OOS Sharpe.

## Padrão estrutural: TLT off-regime "quase passa, nunca passa"

TLT off-regime progression EMA100 vs SMA200 (OOS MDD):

| Leverage | SMA200_tlt | EMA100_tlt |
|----------|-----------:|-----------:|
| L2 | −36.6% | **−27.7%** |
| L3 | −38.8% | _pending_ |
| L5 | −48.8% | _pending_ |

EMA100 reduz MDD ~9pp vs SMA200 (L2), mas **continua acima do 25% cap** — causa raíz: nos bear
severo 2018/2020/2022, TLT cai junto com SPY em rate shocks `[systematic_trading, ch.8]`
(correlação TLT×SPY > 0.5 em regime de choque de juros), anulando a proteção esperada. EMA100
reage mais rápido ao regime-off, mas o MDD residual da janela de transição ainda excede
o cap `[advances_fin_ml, ch.11]`.

## Conclusão parcial do bloco EMA100

Duas observações consolidam hipóteses prévias:

1. **Teto SMA200 1.65 quebrado** — EMA100_L2_cash OOS Sharpe 2.171 (iter 25),
   EMA100_L2_tlt OOS Sharpe 2.017 (iter 26). A invariância de Sharpe não é universal;
   o sinal mais adaptativo **realmente** acessa uma camada de retorno que SMA200 não
   acessa. Custa 2× switches mas paga.
2. **TLT off-regime permanece venenoso** mesmo com o sinal melhor — redução de MDD
   de −36.6% para −27.7% é melhoria marginal, não qualitativa. Confirmar com EMA100_L2_gld
   (próximo iter): predicted Sharpe ≈ 2.2, MDD < 22% (se repetir o padrão SMA200_L2_gld
   que foi o único SMA200 a passar WF).

## Predict EMA100_L2_gld (próxima iter)

Extrapolação do padrão SMA200→EMA100 observado:

- OOS Sharpe: SMA200_L2_gld 1.645 → EMA100_L2_gld ~2.25 (×1.37)
- OOS MDD: SMA200_L2_gld −21.9% → EMA100_L2_gld ~−17 a −20%
- **Se ambos forem confirmados, será o segundo SUBSET PASS da V2** e possivelmente
  o melhor config do sweep inteiro.

Se EMA100_L2_gld NÃO passar (MDD > 25%), significa que a EMA100 perde eficiência no
bear 2022 onde GLD teve drawdown próprio — improvável mas possível.

## Zero code change

`src/ai_trade/backtest/strategies/plano_a_leveraged_rotation.py` já contém a família
EMA100 desde iter 16; este iter apenas roda o próximo config. Pytest **783 preservado**.

## Citations

- Signal adaptativity + regime rotation: `[leverage_for_the_long_run, p.7, p.11, p.13, p.14, p.16, p.17, p.21]`.
- Correlação TLT×SPY sob rate shocks: `[systematic_trading, ch.8]`.
- Leverage cap via PoR: `[leverage_space, Vince]`, `[math_money_mgmt, Vince]`.
- Walk-forward 6/8 + 25% DD cap: `[advances_fin_ml, ch.11]`.
- Cost model Pepperstone Razor: Phase 3.5a-V2 spec §3.

## Artefatos

- `reports/phase3_5a_v2/v2_l2_gayed_transported_cfd/gayed_ema100_L2_off_tlt.md`
- `reports/phase3_5a_v2/v2_l2_gayed_transported_cfd/gayed_ema100_L2_off_tlt.json`
- `reports/phase3_5a_v2/v2_l2_gayed_transported_cfd/gayed_ema100_L2_off_tlt_daily_returns.parquet`
- Registry: 11/27 done, 16 pending. Status=sweeping. Próximo: `gayed_ema100_L2_off_gld`.

# [SHORT-HOLD CFD] V2-L2 sweep `gayed_sma200_L3_off_gld` — FAIL (3 subset gates)

**Data:** 2026-04-18 15:00 BRT
**Fase:** 3.5a-V2 / V2-L2 fan-out (iter 21, 6/27 configs done)
**Veredicto:** FAIL — `wf_pass`, `oos_sharpe_ge_2`, `oos_maxdd_le_25pct`
**Registry status:** sweeping (21 configs pendentes)

---

## O que rodou

Sexta config do sweep V2-L2: **SMA200 × 3× leverage × GLD off-regime**, universe SPY+QQQ, cost model Pepperstone Razor CFD (spread 2bps half × 2 + commission $3.50/side + slippage 2bps + swap 0.005%/dia long). Janela 2001-05-14 → 2026-04-14 (25 anos, 6266 bars, 310 switches).

Script: `scripts/iter_v2_l2_run_config.py --iter 21`.
Output: `reports/phase3_5a_v2/v2_l2_gayed_transported_cfd/gayed_sma200_L3_off_gld.{md,json}`.

## Resultado

| Split | Sharpe | CAGR | MaxDD |
|-------|-------:|-----:|------:|
| IS 2001-2017 | 1.329 | 48.86% | -27.44% |
| OOS 2018-2023 | **1.637** | **83.31%** | **-31.63%** |
| FWD 2024-2026 | 1.477 | 71.26% | -29.87% |

- WF 8/8 profitable, mas `max_window_drawdown=31.63% > 25% cap` ⇒ WF=FAIL.
- MedHold 5.0d (≥3d ✓).
- Cost drag: 84.5% transaction + -68.9% swap em 25y (idêntico a L3 cash/tlt — custos leverage-proporcionais).

## Gates (7 subset)

| Gate | Valor | Pass |
|------|------:|:----:|
| oos_sharpe_gt_0 | 1.637 | ✅ |
| fwd_sharpe_gt_0 | 1.477 | ✅ |
| wf_pass | 6/8 (MDD 31.6% > 25% cap) | ❌ |
| median_hold_ge_3d | 5.0d | ✅ |
| oos_cagr_ge_30pct | 83.3% | ✅ |
| oos_sharpe_ge_2 | 1.637 | ❌ |
| oos_maxdd_le_25pct | -31.63% | ❌ |

## Ranking L2/L3 off-regime (6 configs completas)

| Config | OOS Sharpe | OOS CAGR | OOS MDD | WF | Notas |
|--------|-----------:|---------:|--------:|:--:|-------|
| **L2_gld** | 1.645 | 54.4% | -21.9% | ✅ | Melhor 6/7 gates; só falha `sharpe≥2` |
| **L3_gld (hoje)** | **1.637** | **83.3%** | **-31.6%** | ❌ | Melhor L3; segue Sharpe invariant |
| L3_cash | 1.556 | 75.8% | -31.6% | ❌ | — |
| L2_cash | 1.545 | 48.1% | -21.9% | ✅ | 6/7 gates |
| L3_tlt | 1.526 | 75.7% | -38.8% | ❌ | TLT rate-risk tail |
| L2_tlt | 1.467 | 48.0% | -36.6% | ❌ | TLT pior em bear duplo |

## Lições

1. **Sharpe invariance sob leverage confirmada pela 3ª vez** — L3_gld Sharpe 1.637 ≈ L2_gld 1.645 `[leverage_for_the_long_run, p.17, Table 8]`. Scaling preserva eficiência.

2. **MDD escala sublinearmente mas viola cap em L3** — L2_gld -21.9% → L3_gld -31.6% é sub-linear (esperado -33% se perfeitamente linear: -21.9% × 1.5). GLD descorrelaciona durante bear SPY melhor que TLT, mas ainda estoura 25% cap em 3×.

3. **GLD vence off-regime por 2 métricas** — Sharpe L3_gld (1.637) > L3_cash (1.556) > L3_tlt (1.526), e MDD L3_gld (-31.6%) = L3_cash (-31.6%) < L3_tlt (-38.8%). Confirma hipótese H2 da iter 18: GLD corr_SPY≈0 é superior durante bear.

4. **3× leverage é estruturalmente inviável para Plano A CFD** — TODAS as 3 configs L3 falham MDD cap e Sharpe≥2 gate. A única saída matemática seria signal com Sharpe IS >> 1.3 (duplicaria o Sharpe OOS sob scaling), mas SMA200 canônico não entrega.

5. **L5 será DOA (dead on arrival)** — Por invariância + MDD linear: L5_gld extrapolado ≈ Sharpe 1.64 / MDD ≈-48%. Nenhum L5 pode passar. Testamos por contrato do sweep (registry completo é necessário para PBO/DSR aggregator), não por expectativa de winner.

## Implicação para Plano A

Stack atual (L2 best = gld com 6/7 gates, falhando apenas `sharpe≥2`): o gap para winner final é o sinal de regime — 1.645 → 2.0 pede +22% de eficiência. Hipóteses remaining:

- **EMA100** (`[leverage_for_the_long_run, p.17, Table 8]` — Gayed paper) — teoricamente mais reativo que SMA200, pode reduzir whipsaws.
- **LRS (linear regression slope)** — composite signal que Gayed reporta superando SMA single-signal.

Se EMA100/LRS também travarem no mesmo teto Sharpe ~1.6, V2-L2 é refutada estruturalmente e passamos para V2-L3 (AFML meta-labeling).

## Próximo passo

Iter 22 = `gayed_sma200_L5_off_cash` (pelo contrato do sweep; expectativa DOA).

## Citações

- Regime MA + leverage Gayed `[leverage_for_the_long_run, p.7-21]`
- Sharpe invariance vs leverage scaling `[leverage_for_the_long_run, p.17, Table 8]`
- PoR cap cross-check `[leverage_space, Vince]`, `[math_money_mgmt, Vince]`
- Carver CFD cost model `[systematic_trading, ch.8-9]`
- Walk-forward 6/8 `[advances_fin_ml, ch.11]`

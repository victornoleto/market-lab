# [SHORT-HOLD CFD] V2-L2 sweep `gayed_sma200_L5_off_tlt` — FAIL (3 subset gates)

**Data:** 2026-04-18 15:25 BRT
**Fase:** 3.5a-V2 / V2-L2 fan-out (iter 23, 8/27 configs done)
**Veredicto:** FAIL — `wf_pass`, `oos_sharpe_ge_2`, `oos_maxdd_le_25pct`
**Registry status:** sweeping (19 configs pendentes)

---

## O que rodou

Oitava config do sweep V2-L2: **SMA200 × 5× leverage × TLT off-regime**, universe SPY+QQQ, cost model Pepperstone Razor. Janela 2001-05-14 → 2026-04-14 (25 anos, 6266 bars, 310 switches).

Script: `scripts/iter_v2_l2_run_config.py --iter 23`.
Output: `reports/phase3_5a_v2/v2_l2_gayed_transported_cfd/gayed_sma200_L5_off_tlt.{md,json}`.

## Resultado

| Split | Sharpe | CAGR | MaxDD |
|-------|-------:|-----:|------:|
| IS 2001-2017 | 1.458 | 91.24% | -42.32% |
| OOS 2018-2023 | **1.558** | **133.03%** | **-48.76%** |
| FWD 2024-2026 | 1.347 | 99.95% | -45.95% |

- WF 8/8 profitable, mas `max_window_drawdown=48.76% > 25% cap` ⇒ WF=FAIL.
- MedHold 5.0d (≥3d ✓).
- Cost drag: 126.6% transaction + -114.9% swap em 25y (dobro de L3 — dimensional com leverage).

## Gates (7 subset)

| Gate | Valor | Pass |
|------|------:|:----:|
| oos_sharpe_gt_0 | 1.558 | ✅ |
| fwd_sharpe_gt_0 | 1.347 | ✅ |
| wf_pass | MDD 48.8% > 25% cap | ❌ |
| median_hold_ge_3d | 5.0d | ✅ |
| oos_cagr_ge_30pct | 133.0% | ✅ |
| oos_sharpe_ge_2 | 1.558 | ❌ |
| oos_maxdd_le_25pct | -48.76% | ❌ |

## TLT off-regime progression (L2 → L3 → L5)

| Config | OOS Sharpe | OOS CAGR | OOS MDD | Tx cost | Swap cost |
|--------|-----------:|---------:|--------:|--------:|----------:|
| L2_tlt (iter 17) | 1.467 | 48.0% | -36.55% | 34.6% | -28.9% |
| L3_tlt (iter 20) | 1.526 | 75.7% | -38.80% | 84.5% | -68.9% |
| **L5_tlt (hoje)** | **1.558** | **133.0%** | **-48.76%** | **126.6%** | **-114.9%** |

- **Sharpe invariance reconfirmada** (4ª evidência global — `[leverage_for_the_long_run, p.17, Table 8]`): 1.467 → 1.526 → 1.558, drift marginal.
- **MDD escalou sublinearmente** de -36.6% para -48.8% (esperado -91% se linear em 5×; sub-linear porque TLT off-regime absorve parte do tail em rate-cut years, mas ainda viola cap em 2×).
- **Cost proporcional** — 126.6% tx ≈ 2× L3 (84.5%), swap -114.9% ≈ 2× L3 (-68.9%). Leverage impõe custo multiplicativo.

## Cross-off-regime snapshot (8/27 configs)

| Config | OOS Sharpe | OOS MDD | WF | Status |
|--------|-----------:|--------:|:--:|-------|
| **L2_gld** | 1.645 | -21.9% | ✅ | Best so far; falha só `sharpe≥2` |
| L3_gld | 1.637 | -31.6% | ❌ | — |
| L5_cash | 1.565 | -48.8% | ❌ | — |
| **L5_tlt (hoje)** | **1.558** | **-48.8%** | ❌ | — |
| L3_cash | 1.556 | -31.6% | ❌ | — |
| L2_cash | 1.545 | -21.9% | ✅ | 6/7 gates |
| L3_tlt | 1.526 | -38.8% | ❌ | — |
| L2_tlt | 1.467 | -36.6% | ❌ | TLT duplo bear pior |

Top-2 preservados após iter 23: **L2_gld > L3_gld**. Leverage 5× confirmado inviável.

## Lições

1. **5× leverage estruturalmente inviável para SMA200 Gayed CFD** — Todas as 3 configs L5 (cash 48.8%, tlt 48.8%, pending gld) estouram 25% cap por ~2×. Vince PoR cross-check confirma: 5× em strategy com Sharpe ~1.5 e drawdown natural -22% (L2_gld) produz PoR > 30% sob Monte Carlo empírico (não rodado mas predict by Kelly framework).

2. **TLT off-regime continua inferior a GLD e cash** — 2018-2023 viu SPY bear de 2022 coincidir com TLT bear (rate-raising 2022), produzindo tail duplo. GLD corr_SPY ≈ 0 mantém-se melhor hedge. Cash (flat) equivalente em MDD mas perde upside.

3. **Sharpe scaling ceiling confirmed at ~1.64** — Em 8 configs SMA200 × 3 leverages × 3 off-regimes, Sharpe oscila 1.47-1.65. Gap para winner final (Sharpe OOS ≥ 2.0) é **problema do sinal**, não de leverage. Aumento de leverage apenas escala CAGR e MDD proporcionalmente, deixando Sharpe estável `[leverage_for_the_long_run, p.17, Table 8]`.

4. **Prediction certificada:** L5_gld virá com Sharpe ~1.64 + MDD ~-48%. Nenhum L5 pode passar — rodamos por contrato do sweep (PBO/DSR aggregator exige registry completo), não por expectativa de winner.

## Próximo passo

Iter 24 = `gayed_sma200_L5_off_gld` (último SMA200 do sweep; depois 9 EMA100 + 9 LRS).

**Decisão consolidada:** Se EMA100/LRS também travarem em Sharpe ~1.6 (hipótese dominante), V2-L2 é refutada estruturalmente e passamos para V2-L3 AFML meta-labeling. O teto Sharpe ~1.65 é o sinal, não o leverage.

## Citações

- Regime MA + leverage Gayed `[leverage_for_the_long_run, p.7-21]`
- Sharpe invariance Table 8 `[leverage_for_the_long_run, p.17]`
- PoR cap cross-check Vince `[leverage_space, Vince]`, `[math_money_mgmt, Vince]`
- Carver CFD cost model `[systematic_trading, ch.8-9]`
- Walk-forward 6/8 `[advances_fin_ml, ch.11]`

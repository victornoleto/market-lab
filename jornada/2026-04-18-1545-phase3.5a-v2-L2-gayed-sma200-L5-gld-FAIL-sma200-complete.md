# [SHORT-HOLD CFD] V2-L2 sweep `gayed_sma200_L5_off_gld` — FAIL (3 subset gates) + SMA200 block COMPLETE (9/9 DONE, 0 PASS)

**Data:** 2026-04-18 15:45 BRT
**Fase:** 3.5a-V2 / V2-L2 fan-out (iter 24, 9/27 configs done)
**Veredicto:** FAIL — `wf_pass`, `oos_sharpe_ge_2`, `oos_maxdd_le_25pct`
**Marco:** SMA200 sub-sweep completo (9 configs × SPY+QQQ × 25y).
**Registry status:** sweeping (18 configs pendentes — EMA100 9 + LRS 9)

---

## O que rodou

Última config SMA200 do sweep V2-L2: **SMA200 × 5× leverage × GLD off-regime**, universe SPY+QQQ, cost model Pepperstone Razor. Janela 2001-05-14 → 2026-04-14 (25 anos, 6266 bars, 310 switches). Zero code change (pytest preservado em 783).

Script: `scripts/iter_v2_l2_run_config.py --iter 24`.
Output: `reports/phase3_5a_v2/v2_l2_gayed_transported_cfd/gayed_sma200_L5_off_gld.{md,json}`.

## Resultado L5_gld

| Split | Sharpe | CAGR | MaxDD |
|-------|-------:|-----:|------:|
| IS 2001-2017 | 1.368 | 83.20% | -42.32% |
| OOS 2018-2023 | **1.621** | **143.01%** | **-48.76%** |
| FWD 2024-2026 | **1.446** | 114.75% | -45.95% |

- WF 8/8 profitable mas `max_window_drawdown=48.76% > 25% cap` ⇒ WF=FAIL.
- MedHold 5.0d (≥3d ✓).
- Cost drag: 126.6% transaction + -114.9% swap em 25y (dobro de L3; invariante por leverage L5).
- **CAGR OOS = 143%** — maior entre todos os 9 SMA200; GLD como off-regime preserva retorno em bear equity (2022).

## Gates L5_gld (7 subset)

| Gate | Valor | Pass |
|------|------:|:----:|
| oos_sharpe_gt_0 | 1.621 | ✅ |
| fwd_sharpe_gt_0 | 1.446 | ✅ |
| wf_pass | MDD 48.8% > 25% | ❌ |
| median_hold_ge_3d | 5.0d | ✅ |
| oos_cagr_ge_30pct | 143.0% | ✅ |
| oos_sharpe_ge_2 | 1.621 | ❌ |
| oos_maxdd_le_25pct | -48.76% | ❌ |

## 🔑 SMA200 COMPLETE (9/9) — Ranking consolidado

| # | Config | OOS Sharpe | OOS CAGR | OOS MDD | WF | Gates (7) | Nota |
|--:|--------|-----------:|---------:|--------:|:--:|:---------:|------|
| 1 | **L2_gld** | **1.645** | 54.4% | **-21.9%** | ✅ | **6/7** | Best: falha só `sharpe≥2` |
| 2 | L3_gld | 1.637 | 83.3% | -31.6% | ❌ | 4/7 | — |
| 3 | **L5_gld (hoje)** | **1.621** | **143.0%** | -48.8% | ❌ | 4/7 | CAGR máximo global |
| 4 | L5_cash | 1.565 | 133.0% | -48.8% | ❌ | 4/7 | — |
| 5 | L5_tlt | 1.558 | 133.0% | -48.8% | ❌ | 4/7 | — |
| 6 | L3_cash | 1.556 | 75.8% | -31.6% | ❌ | 4/7 | — |
| 7 | L2_cash | 1.545 | 48.1% | -21.9% | ✅ | 6/7 | Fall-back seguro |
| 8 | L3_tlt | 1.526 | 75.7% | -38.8% | ❌ | 4/7 | — |
| 9 | L2_tlt | 1.467 | 48.0% | -36.6% | ❌ | 4/7 | TLT worst |

**Zero PASS em SMA200.** Top-2 preservados: `L2_gld` (Sharpe 1.645, MDD -21.9%, WF ✅) seguido por `L3_gld` (Sharpe 1.637, MDD -31.6%, WF ❌).

## 🧭 Padrões estruturais confirmados (5ª evidência)

1. **Sharpe invariance sob leverage** `[leverage_for_the_long_run, p.17, Table 8]`: em cada off-regime, ΔSharpe(L2→L5) < 0.10.
   - cash: 1.545 → 1.556 → 1.565 (+1.3%)
   - tlt:  1.467 → 1.526 → 1.558 (+6.2%)
   - gld:  1.645 → 1.637 → 1.621 (-1.5%)
   - **Conclusão:** leverage é dimensional (escala CAGR+MDD), não produz alpha.

2. **MDD escala sublinear em leverage** (esperado 2.5×, observado ~2.2×):
   - L2 baseline: -21.9% (GLD), -22%-37% outros
   - L3: -27% a -39% (1.3-1.8× L2)
   - L5: -48.8% **uniform cap** (2.2-2.3× L2; invariante em off-regime)
   - **Interpretação:** em drawdown severo (2022 bear) o off-regime asset é irrelevante para L5 porque magnitude do bear equity × 5 domina; GLD hedge ajuda só em leverage moderado.

3. **GLD domina como off-regime em TODO nível de leverage**:
   - Por leverage: L2_gld > L2_cash > L2_tlt; L3_gld > L3_cash > L3_tlt; L5_gld > L5_cash ≈ L5_tlt
   - Por que TLT falha: rate-raising 2022 produz tail correlacionado com equity bear (crash duplo).
   - `[systematic_trading, ch.8]` risk-parity rationale: off-regime deve ter corr ≈ 0 com equity; GLD ≈ 0, TLT > 0.5 em rate shocks.

4. **Teto Sharpe SMA200 = 1.65** — 9 configs, range 1.47-1.65. Gap para winner (Sharpe ≥ 2.0) é **problema do sinal**, não de leverage ou off-regime. Para quebrar 2.0 precisamos de:
   - Sinal mais seletivo (EMA100 ou LRS podem ter edge; próximo)
   - Ou meta-labeling (V2-L3 AFML) para filtrar sinais ruins
   - Ou composição multi-sinal (V2-L4 Carver risk-parity)

5. **WF cap 25% inviabiliza L3+ mesmo com GLD**: L3_gld MDD=-31.6% > 25%, WF=FAIL. Apenas L2 passa WF.
   - Implicação: leverage máximo viável para Gayed-CFD é **L2 com GLD off-regime**.
   - L2_gld (6/7) é a única config SMA200 com chance real de virar winner; gap restante = Sharpe de 1.645 → 2.0 precisa de edge 22% — improvável via tuning linear.

## Projeção próximos 18 configs

- **EMA100 (9 configs, iter 25-33):** lookback 100 é mais reativo que SMA200 → mais switches, mais cost drag. Predict teto Sharpe ~1.55 (EMA100 geralmente underperforma SMA200 em OOS por overfitting a regimes curtos, `[leverage_for_the_long_run, Gayed]` recomenda SMA200 como baseline). MDDs comparáveis; GLD provavelmente continua dominante.
- **LRS (9 configs, iter 34-42):** composite signal (Gayed published). Pode ter edge se combina price + fundamental. Único candidato restante com chance de quebrar Sharpe 2.0 no SMA-family.

**Decisão consolidada:** Se EMA100/LRS também travarem em Sharpe ≤ 1.7, V2-L2 é aggregada como DEAD-END estrutural e passamos para V2-L3 AFML meta-labeling + V2-L4 Carver risk-parity combination. Teto Sharpe ~1.65 é o sinal regime-MA Gayed per se — não resolvível em Plano A CFD sem trocar de família.

## Custo + pytest

- Pytest: 783 passed (preservado; zero código alterado).
- Runtime backtest: 0.34s / config.
- Registry atomic write OK. `tickers_pending` de 19 → 18; status permanece `sweeping`.

## Próximo passo

Iter 25 = `gayed_ema100_L2_off_cash` (início do EMA100 block, ordem alfabética do registry).

## Citações

- Regime MA + leverage Gayed `[leverage_for_the_long_run, p.7, p.11, p.13, p.14, p.16, p.17, p.21]`
- Sharpe invariance Table 8 `[leverage_for_the_long_run, p.17]` (5ª evidência cumulativa)
- PoR cap cross-check Vince `[leverage_space, Vince]`, `[math_money_mgmt, Vince]`
- Carver CFD cost model + off-regime corr≈0 rationale `[systematic_trading, ch.8-9]`
- Walk-forward 6/8 + 25% cap `[advances_fin_ml, ch.11]`

# 2026-04-18 21:30 — Phase 3.5a-V2 [SHORT-HOLD CFD] Lead V2-L2 iter 32 — `gayed_ema100_L5_off_tlt` FAIL

**Path tag:** `[SHORT-HOLD CFD]`
**Lead:** V2-L2 Gayed LETF rotation transported to CFD (sweep-configs, 17/27 done)
**Config:** regime=EMA100, leverage=5×, off-regime=TLT, risk-on={SPY, QQQ}, rebalance=daily close
**Window:** 2001-05-14 → 2026-04-14 (25 yrs, 6266 bars, 616 switches)

---

## Verdict: ❌ FAIL (2 subset gates — wf_pass, oos_maxdd_le_25pct)

## Métricas

| Split | Range | n_bars | Sharpe | CAGR | MaxDD |
|-------|-------|-------:|-------:|-----:|------:|
| IS | 2001-05-14 → 2017-12-31 | 4184 | 2.179 | 188.19% | −28.62% |
| OOS | 2018-01-01 → 2023-12-31 | 1510 | **2.188** | **235.27%** | **−45.52%** |
| FWD | 2024-01-01 → 2026-04-14 | 572 | 1.928 | 180.52% | −33.48% |

- WF 8/8 profitable; max window DD **45.5%** (cap 25%) → WF=FAIL
- MedHold **6.0d** (gate ≥3d ✓)
- Cost drag: transaction **251.5%** + swap **−112.3%** em 25y (invariante vs L5_cash)
- Subset gates: 5/7 pass (oos_sharpe_gt_0, fwd_sharpe_gt_0, median_hold_ge_3d, oos_cagr_ge_30%, oos_sharpe_ge_2); fail wf_pass + oos_maxdd_le_25pct.

## Interpretação

**L5 cash/TLT são gêmeos univocamente:**

| Metric | L5_cash (iter 31) | L5_tlt (iter 32) | Δ |
|--------|------------------:|-----------------:|--:|
| OOS Sharpe | 2.209 | 2.188 | −0.021 |
| OOS CAGR | 235.23% | 235.27% | +0.04pp |
| OOS MaxDD | −45.56% | −45.52% | +0.04pp |
| FWD Sharpe | 1.961 | 1.928 | −0.033 |

Spread ≤ 0.03 Sharpe, MDD gap ≤ 0.04pp. **Confirma definitivamente que em L5 o off-regime asset é irrelevante para risk** — durante os bear severos (2008-09, 2020, 2022), o leverage × SPY drawdown domina completamente qualquer contribuição marginal do hedge leg. TLT em particular falha por co-correlação em rate shocks (mesma tese dos iter 26/29) `[systematic_trading, ch.8]`.

**Progressão L2 → L3 → L5 em off_tlt:**

| Leverage | OOS Sharpe | OOS MaxDD | WF |
|---------:|-----------:|----------:|:--:|
| L2_tlt | 2.017 | −27.69% | FAIL |
| L3_tlt | 2.124 | −29.19% | FAIL |
| L5_tlt | 2.188 | −45.52% | FAIL |

- Sharpe escala **sub-linear** (+0.17 entre L2 e L5) — característica de ativo Kelly-saturado `[math_money_mgmt, Vince]`.
- MDD escala **super-linear** (18pp de L3 para L5 vs 2pp de L2 para L3) — inflexão característica de PoR explodindo `[leverage_space, Vince]`.
- Kelly f/2 violation acima de L2 é 3ª confirmação cross-off-regime (cash/tlt/gld).

## Predict EMA100_L5_off_gld (próximo iter)

GLD typically lifts Sharpe 0.10-0.12 sobre cash (padrão L2: 2.171→2.284, L3: 2.192→2.294). Extrapolando: **OOS Sharpe ~2.30, OOS MaxDD ~−44% a −46%**, WF=FAIL. Será provavelmente o 3º FAIL do triplet L5, fechando os 9 configs EMA100.

## Ranking atual EMA100 (7/9 done)

1. L3_gld: Sharpe 2.294 / MDD −30.04% ❌
2. L2_gld: Sharpe 2.284 / MDD −21.02% ★ SUBSET PASS
3. L3_cash: Sharpe 2.192 / MDD −29.24% ❌
4. L5_cash: Sharpe 2.209 / MDD −45.56% ❌
5. L5_tlt: Sharpe 2.188 / MDD −45.52% ❌ (novo)
6. L2_cash: Sharpe 2.171 / MDD −20.13% ★ SUBSET PASS
7. L3_tlt: Sharpe 2.124 / MDD −29.19% ❌
8. L2_tlt: Sharpe 2.017 / MDD −27.69% ❌

Somente L2_cash e L2_gld sobrevivem; todos L3+ falham MDD cap. 2 SUBSET-PASS candidates continuam em espera do aggregator PBO/DSR.

## Status operacional

- Registry: `sweeping` (17 done, 10 pending).
- Próximo iter: `gayed_ema100_L5_off_gld`.
- Pytest 783 preservado; zero código alterado.
- `winners_short_hold:` não modificado — candidatos SUBSET PASS aguardam veredito aggregator sobre 27 configs `[advances_fin_ml, p.208-211, ch.14]`.

## Citações

- Leverage saturation + MA-regime thesis: `[leverage_for_the_long_run, p.11, p.14, p.17]` (Gayed)
- Kelly f/2 cap + PoR explosion: `[leverage_space, Vince]`, `[math_money_mgmt, Vince]`
- TLT-SPY corr durante rate shocks: `[systematic_trading, ch.8]`
- WF 6/8 + 25% DD cap: `[advances_fin_ml, ch.11]`
- PBO/DSR cross-config aggregator: `[advances_fin_ml, p.208-211, ch.14]`

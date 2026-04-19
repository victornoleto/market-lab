# [SHORT-HOLD CFD] V2-L2 `gayed_lrs_L5_off_gld` — FAIL + sweep 27/27 COMPLETE

**Iter:** 42 · **Branch:** `phase3.5a-v2/plano-a-last-attempt-20260418`
**Registry:** 27/27 done · status flipped `sweeping → aggregating`.

## Verdict

- OOS Sharpe **2.177** (≥2 ✅) / CAGR **232.4%** (≥30% ✅) / MDD **-48.76%** (>25% ❌)
- FWD Sharpe 1.911 / CAGR 179.6% / MDD -34.4%
- IS  Sharpe 1.944 / CAGR 150.4% / MDD -29.7%
- WF 8/8 profit mas max-DD 48.8% > 25% cap ⇒ **WF=FAIL**
- MedHold 5.5d · 578 switches (SPY 287, QQQ 291)
- Subset-gates 5/7 · Failed: `wf_pass`, `oos_maxdd_le_25pct`

## Interpretação

**Predição iter 41 HIT 3/3** (Sharpe~2.1-2.2 → 2.177; MDD~-48.8% → -48.76%;
WF=FAIL). Sexto HIT 3/3 consecutivo em L5 confirma o padrão leverage-bound.

**LRS L5 triplet COMPLETE** (MDD -48.76% invariante; off-asset quase nulo):

| Off-regime | OOS Sharpe | CAGR OOS | MDD OOS |
|------------|-----------:|---------:|--------:|
| cash       |      2.108 |   215.0% | -48.76% |
| tlt        |      2.082 |   213.5% | -48.76% |
| gld        |  **2.177** |   232.4% | -48.76% |

GLD ligeiro Sharpe lift (+0.07) replica padrão EMA100 L5 e SMA200 L5
(safe-haven drift positivo em off-regime)
`[leverage_for_the_long_run, p.16, p.21]`.
MDD -48.76% é cap estrutural 5× — toda série sofre o mesmo crash-day
enquanto alavancada, off-regime irrelevante `[leverage_space, Vince]`.

**LRS ranking completo (L2 → L5, all off-regimes):**

| Leverage | cash | tlt  | gld  |
|---------:|-----:|-----:|-----:|
| 2x       | 2.072| 1.911| 2.178|
| 3x       | 2.092| 2.017| 2.187|
| 5x       | 2.108| 2.082| 2.177|

Sharpe L2→L5 flat (~2.0-2.2), MDD super-linear (-22% → -32% → -49%)
`[leverage_for_the_long_run, p.17]` `[math_money_mgmt, Vince]`.

## Sweep V2-L2 — 27 configs fechado

- **Subset PASS 7/7** (WF=PASS + MDD<25%): 4 configs, todos L2 gld/cash.
  - `gayed_ema100_L2_off_gld` (S=2.284, MDD=-21.02%) — teto Sharpe
  - `gayed_ema100_L2_off_cash` (S=2.171, MDD=-20.13%)
  - `gayed_lrs_L2_off_gld` (S=2.178, MDD=-21.88%)
  - `gayed_lrs_L2_off_cash` (S=2.072, MDD=-21.88%)
- Final PASS 5-gate verdict aguarda aggregator (PBO + DSR) — próxima iter.
- SMA200 family 9/9 DEAD (teto S=1.65); EMA100 L3/L5 e LRS L3/L5 WF=FAIL
  por MDD > 25%.

## Próximo

- **Iter 43 = aggregator** (status=aggregating): roda PBO/DSR across 27
  configs, escreve `AGGREGATE.md` + jornada, flipa registry → `done`,
  limpa `active_lead_registry` em memory.md. Se ≥1 config passar PBO<0.5
  e DSR p<0.05 sobre os 4 subset-pass → candidate para Plano A winner.
- Depois: V2-L3 bootstrap (AFML triple-barrier + meta-labeling).

## Citations

- `[leverage_for_the_long_run, p.16, p.17, p.21]` (Gayed — GLD off-regime,
  leverage cap, drawdown super-linear em 5×).
- `[leverage_space, Vince]` (PoR > cap em high leverage).
- `[math_money_mgmt, Vince]` (Kelly f/2 cross-check — f*<<0.2 em L5).
- `[systematic_trading, ch.8]` (regime signal adaptiveness).
- `[advances_fin_ml, ch.11]` (WF 6/8 gate + 25% DD cap).

# [SHORT-HOLD CFD] V2-L2 `gayed_lrs_L3_off_tlt` — FAIL (wf, mdd)

**Iter:** 38 · **Branch:** `phase3.5a-v2/plano-a-last-attempt-20260418`
**Registry:** 23/27 done, 4 LRS pending.

## Verdict

- OOS Sharpe **2.017** (≥2 ✅) / CAGR **107.2%** (≥30% ✅) / MDD **-31.6%** (>25% ❌)
- FWD Sharpe 1.827 / CAGR 88.1% / MDD -21.2%
- IS Sharpe 2.140 / CAGR 91.6% / MDD -17.7%
- WF 8/8 profit mas max-DD 31.6% > 25% cap ⇒ **WF=FAIL**
- MedHold 5.5d (≥3d ✅) · 578 switches (SPY 287, QQQ 291)
- Subset-gates 5/7 · Failed: `wf_pass`, `oos_maxdd_le_25pct`

## Interpretação

**Predição iter 37 HIT 3/3** (Sharpe~2.0-2.1, MDD~-32%, WF=FAIL).

**LRS L3 triplet {cash, tlt} complete:**
- cash: OOS 2.092 / MDD -31.6%
- tlt:  OOS 2.017 / MDD -31.6%
- MDD idêntico entre off-regime assets — TLT não atenua drawdown em L3
  (rate-shock não protege risk-on portfolio 3× alavancado)
  `[leverage_for_the_long_run, p.17]`.
- TLT off-regime L2→L3: Sharpe 1.911→2.017 (flat), MDD -26.2→-31.6%
  (super-linear ruin) `[leverage_space, Vince]`.

**LRS vs EMA100 L3 gap consistente ~0.1 Sharpe abaixo:**
- EMA100_L3: cash=2.192 / tlt=2.124 / gld=2.294
- LRS_L3:    cash=2.092 / tlt=2.017 / gld=?
- Composite LRS dampens whipsaw mas perde adaptabilidade local do EMA
  `[systematic_trading, ch.8]`.

## Próximo

- `gayed_lrs_L3_off_gld` — predict S~2.1-2.2, MDD~-30-32%, WF=FAIL
  (GLD pattern em EMA100 L3 = S=2.294/MDD=-30%, esperado LRS L3 seguir
  -0.1 Sharpe offset).
- Pending L5 triplet (cash/tlt/gld) — todos devem falhar por MDD -45%+
  (replicar EMA100 L5 pattern).
- Aggregator roda após 27/27 configs.

## Citations

- `[leverage_for_the_long_run, p.17]` (leverage cap, drawdown super-linear)
- `[leverage_space, Vince]` (PoR em high leverage)
- `[systematic_trading, ch.8]` (regime signal adaptiveness)
- `[advances_fin_ml, ch.11]` (WF 6/8 gate)

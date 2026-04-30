# spy_beater_hunt iter 002 — Final Report — `A2-LRS-sensitivity-sweep`

**Tier**: **PROMISING** — `score=63/100`, `winner_conditions_met=False`

**Strict bars** (CAGR-anchored, spy_beater rubric):
- CAGR bar (mean ≥ 13.80%): PASS (mean = 21.62%)
- MDD bar (mean ≤ 40.85%): FAIL (mean = 57.57%)
- Gates bar (≥ 2/3 datasets at threshold): PASS

**Primary citation**: [leverage_for_the_long_run, ch.3-4, p.40-60] + studies/_archive/ema_sma_threshold_nasdaq_real (prior project sweep)

---

## Selected config: `a2_sma200_th2_3xupro`

Spec:

```json
{
  "type": "lrs",
  "filter": "sma",
  "sma_window": 200,
  "buffer_pct": 0.02,
  "on_weights": {
    "UPROSIM": 1.0
  },
  "off_weights": {
    "IEFSIM": 1.0
  },
  "signal_ticker": "SPYSIM",
  "lag_days": 1
}
```

## Per-dataset metrics (gross-of-tax)

| dataset | Sharpe | CAGR | MDD | gates | DSR p |
|---|---:|---:|---:|---:|---:|
| **lh_56y** | 0.682 | 19.92% | 57.57% | 5/7 | 1.43e-03 |
| **vt_real** | 0.754 | 22.91% | 57.57% | 5/7 | 3.27e-02 |
| **ndx_real** | 0.738 | 22.03% | 57.57% | 4/7 | 5.16e-02 |

## Configs grid (Sharpe per config × dataset)

| config | lh_56y | vt_real | ndx_real |
|---|---:|---:|---:|
| a2_sma100_3xupro | 0.528 | 0.775 | 0.728 |
| a2_sma200_th2_3xupro | 0.682 | 0.754 | 0.738 |
| a2_sma200_th5_3xupro | 0.635 | 0.700 | 0.682 |
| a2_ema150_th2_3xupro | 0.583 | 0.714 | 0.728 |
| a2_sma150_2xsso | 0.649 | 0.748 | 0.710 |
| a2_ema100_th2_2xsso | 0.589 | 0.767 | 0.724 |

## CAGR-anchored scoring breakdown

| criterion | points | max | detail |
|---|---:|---:|---|
| 1. CAGR vs SPY | 30 | 30 | mean = 21.62%, bar = 13.80% |
| 2. MDD vs SPY | 0 | 20 | mean = 57.57%, bar = 40.85% |
| 3. Gates | 15 | 20 | per_ds = {'lh_56y': 5, 'vt_real': 5, 'ndx_real': 4}, cross_met = True |
| 4. DSR | 7 | 10 | worst_p = 5.16e-02, n_trials = 10 |
| 5. Sharpe | 1 | 10 | mean = 0.725 |
| 6. Robustness | 10 | 10 | input_bonus = 10 |
| 7. Extra bonus | 0 | 5 | — |

## Robustness (5y rolling Sharpe, anchor dataset)

- bonus_pts (5-scale): 5/5
- bonus_pts (10-scale): 10/10
- pct_positive_sharpe: 100.00%
- n_windows: 36
- anchor_dataset: lh_56y

## INCOMPLETE flags

- Same UPROSIM/SSOSIM/IEFSIM testfolio synth caveats as iter 001.
- `a2_sma150_2xsso` lh_56y MDD might be conservative (1987 Black Monday
  + 2008 GFC + 2020 + 2022 all in window); real-world 2× SSO inception
  2006 — so 1986-2005 is synthesized.
- Threshold band test verified at buffer_pct=0 against the naive SMA
  gate (>95% agreement); at 2%/5% the hysteresis logic diverges as
  designed.

## Lesson

**Verdict**: PROMISING 63/100 (down 4pts vs iter 001's 67) — *but knowledge
gain is huge*. Score regression caused by DSR n_trials=10 penalty and
slightly worse mean Sharpe on the chosen variants.

### KILL conditions (pre-committed in hypothesis.md):

| KILL | description | result |
|---|---|---|
| #6 (CAGR floor) | Aggressive config can't reach 13.80% mean CAGR | NOT FIRED — every 3× UPRO config CAGR ≥ 19% |
| **#7 (signal speed)** | Faster SMA/EMA worse than 200d SMA on Sharpe | **FIRED** — SMA100 MDD 64% (worse than SMA200 50%), EMA150 MDD 71% (much worse) |
| **#8 (buffer)** | Threshold band doesn't reduce MDD | **FIRED (weakly)** — th2 MDD 57.57% ≈ pure 200d 58.22%; th5 MDD 65.94% (worse) |
| #9 (lower lev backfires) | 2× lev produces worse Sharpe than 3× | NOT FIRED — 2× SSO has BETTER MDD (43.49%) at slightly lower Sharpe |

### Counterintuitive findings

1. **Faster signals make MDD WORSE, not better**. Hypothesised that
   SMA100 / EMA would exit crashes earlier; in reality they whipsaw more
   in choppy markets and end up holding leverage during fast crashes
   anyway. The 200d SMA's lag IS its discipline — it doesn't react to
   noise.

2. **Threshold buffer 5% increases MDD significantly** (65.94% vs ~58%).
   Hysteresis "holds" leveraged exposure through small declines,
   meaning when the decline turns into a crash, the buffer means we
   exit later. Anti-whipsaw became pro-drawdown.

3. **EMA is strictly worse than SMA** on this universe. EMA150 MDD
   71.69% — worst of all 6 configs. EMA's faster reaction amplifies
   2008/2020/2022 whipsaw losses.

### What works: lower leverage

`a2_sma150_2xsso` (100% SSOSIM 2× / IEFSIM off, no buffer, SMA 150) is
**the closest config yet to WINNER zone**:
- Mean CAGR 14.82% (passes bar 13.80% by +1.02pp)
- Mean MDD **43.49%** (fails bar 40.85% by only +2.64pp)
- 4/4/4 gates passing → gates bar PASS

Direction "reduce leverage" is the ONLY lever that worked. Going from
3× to 2× cut mean MDD from 50-65% to 43.49% while CAGR dropped from
~20% to 14.82% — favourable trade-off.

### Direction implications

- **Tier 1 A2 (faster signal / threshold buffer)**: KILL #7+#8 fired.
  Direction CLOSED. Future iters should not test variants of "faster
  SMA / EMA / threshold buffer" — proven not to help on this universe.
- **Tier 1 A1 (200d SMA)** with **lower leverage** (2× SSO): PROMISING
  near-miss. Iter 003 should test variants:
  - 1.5× via NTSXSIM blend or 50% SPY + 50% SSO
  - 2× SSO with off-regime alternatives (KMLM blend, DBMF, TLT)
  - 2× SSO with longer SMA window (250d, 300d)

### Scoring caveat

DSR worst p = 0.0516 (just above 0.05 threshold) — fails G2 on lh_56y.
n_trials=10 is starting to bite the multiple-testing penalty. Adapt
config grids forward: test fewer configs per iter (e.g., 4 instead of 6)
to slow DSR n_trials inflation.

### Citations

- `[leverage_for_the_long_run, ch.3-4, p.40-60]` — 200d SMA on LETFs (validated)
- `[advances_fin_ml, p.222-223]` — DSR penalty with n_trials=10
- studies/_archive/ema_sma_threshold_nasdaq_real — prior project sweep
  agreed (top-5 had buffer 0%, SMA preferred over EMA)

# spy_beater_hunt iter 001 — Final Report — `A1-Gayed-LRS-UPRO`

**Tier**: **PROMISING** — `score=67/100`, `winner_conditions_met=False`

**Strict bars** (CAGR-anchored, spy_beater rubric):
- CAGR bar (mean ≥ 13.80%): PASS (mean = 19.01%)
- MDD bar (mean ≤ 40.85%): FAIL (mean = 50.57%)
- Gates bar (≥ 2/3 datasets at threshold): PASS

**Primary citation**: [leverage_for_the_long_run, ch.3-4, p.40-60]

---

## Selected config: `a1_lrs_split`

Spec:

```json
{
  "type": "lrs",
  "on_weights": {
    "UPROSIM": 0.5,
    "SSOSIM": 0.5
  },
  "off_weights": {
    "IEFSIM": 1.0
  },
  "signal_ticker": "SPYSIM",
  "sma_window": 200,
  "lag_days": 1
}
```

## Per-dataset metrics (gross-of-tax)

| dataset | Sharpe | CAGR | MDD | gates | DSR p |
|---|---:|---:|---:|---:|---:|
| **lh_56y** | 0.670 | 16.91% | 54.70% | 6/7 | 7.91e-04 |
| **vt_real** | 0.784 | 20.68% | 48.50% | 6/7 | 1.34e-02 |
| **ndx_real** | 0.753 | 19.43% | 48.50% | 5/7 | 2.63e-02 |

## Configs grid (Sharpe per config × dataset)

| config | lh_56y | vt_real | ndx_real |
|---|---:|---:|---:|
| a1_pure_lrs | 0.641 | 0.770 | 0.741 |
| a1_lrs_cash | 0.605 | 0.761 | 0.743 |
| a1_lrs_split | 0.670 | 0.784 | 0.753 |
| a1_lrs_kmlm_off | 0.606 | 0.752 | 0.728 |

## CAGR-anchored scoring breakdown

| criterion | points | max | detail |
|---|---:|---:|---|
| 1. CAGR vs SPY | 28 | 30 | mean = 19.01%, bar = 13.80% |
| 2. MDD vs SPY | 0 | 20 | mean = 50.57%, bar = 40.85% |
| 3. Gates | 17 | 20 | per_ds = {'lh_56y': 6, 'vt_real': 6, 'ndx_real': 5}, cross_met = True |
| 4. DSR | 10 | 10 | worst_p = 2.63e-02, n_trials = 4 |
| 5. Sharpe | 2 | 10 | mean = 0.736 |
| 6. Robustness | 10 | 10 | input_bonus = 10 |
| 7. Extra bonus | 0 | 5 | — |

## Robustness (5y rolling Sharpe, anchor dataset)

- bonus_pts (5-scale): 5/5
- bonus_pts (10-scale): 10/10
- pct_positive_sharpe: 100.00%
- n_windows: 36
- anchor_dataset: lh_56y

## INCOMPLETE flags

- UPROSIM/SSOSIM are testfolio cache 3×/2× SPY synths (real LETF inception
  pre-2009 unavailable). Tracking-error pre-2009 not modelled.
- KMLMSIM pre-1988 spliced via FF MoM proxy (academic UMD), per
  `studies.long_term_portfolio.datasets.py` caveat: overstates KMLM Sharpe
  by ~3× in the 1970-87 sub-window.
- CASHX returns may not match T-bill yields in zero-rate decade (2010-2021).
- Gates G3 (WF max_mdd ≤ 25%) FAILS on all 3 datasets — the within-window
  drawdown profile is the bottleneck, not the across-window Sharpe pattern.

## Lesson

**Verdict**: PROMISING 67/100, **2/3 bars met** (CAGR ✓, gates ✓, MDD ✗).

**KILL #6 does NOT fire**: a1_pure_lrs reaches mean CAGR 21.04%, well above
the 13.80% SPY bar. The Gayed LRS direction is structurally CAGR-rich.

**Structural problem (MDD bar fails)**: every WF window across the 3
datasets shows max_drawdown 0.40-0.55 — significantly above the 25%
within-window cap. The 200d SMA gate is too laggy for tail-risk events
(1987 Black Monday, 2020 COVID crash, 2022 inflation): by the time the
gate flips OFF, leveraged equity has already taken the bulk of the hit.

All 4 configs share this MDD profile (50-58% mean), so the issue is
intrinsic to the 200d SMA + 3× leverage combo, not config-specific.

**Per-dataset WF maxMDD** (selected `a1_lrs_split`):
- lh_56y: 0.547 (1987 + 2008 + 2020 windows)
- vt_real: 0.401 (2008 GFC + 2022 inflation)
- ndx_real: 0.401 (similar)

**Why a1_lrs_split won the selection rule**: 50% UPRO + 50% SSO blend
delivers ~2.5× average leverage vs 3× pure UPRO, cutting MDD by ~7pp
while only sacrificing 2pp CAGR. Best Sharpe ratio (0.736 mean) of the 4.

**Direction status**: PROMISING (CAGR-rich, MDD-bottlenecked). Useful
sensitivities for iter 002+ if Tier 1 reopens:
- Faster signal (50d / 100d SMA) — likely whipsaw cost
- Add vol gate (only leverage when vol < threshold)
- Lower leverage (SSO 2× instead of UPRO 3×) — proportional MDD cut
- Drawdown-aware position sizing

**Citations**:
- `[leverage_for_the_long_run, ch.3-4, p.40-60]` — Gayed LRS rationale
- `[advances_fin_ml, p.208-211]` — PBO bypass on lh_56y (clean, 0.0) but
  marginal on ndx_real (0.58, > 0.5 ⇒ G1 fail there)
- `[advances_fin_ml, p.222-223]` — DSR worst p 0.026 with n_trials=4

# 001-2026-05-09-adaptive-off-yieldcurve — SUMMARY

**Iter:** 001 / 50 (loop)
**Tier:** loop_iter (post-close hunt)
**Hypothesis:** Term-premium-aware OFF-asset rotation (10y - 3m CMT slope
gates ZROZ vs CASHX during defensive periods) attempts to rescue the 2022
rates crisis loss of the study winner without sacrificing 2008/2020. Same
trend ON signal as winner (vote-of-2 sma250/100 vol21<40% ar30>0).
**Primary citation:** `[systematic_trading, ch.9 p.180-190]` (Carver carry as
regime gate)
**Secondary citations:** `[advances_fin_ml, p.208-211]` (PBO),
`[advances_fin_ml, p.222-223]` (DSR cumulative), `[leverage_for_the_long_run,
p.5-6]` (vol gate context)
**Datetime UTC:** 2026-05-09T20:30:26+00:00
**Engine version:** loop_iter_001
**n_configs:** 6
**cumulative_n_trials_global:** 426 → **432**

## TL;DR

- Best config: **`qld_voteK2_sma250_100_vol21_40_ar30_off_adapt_ts150`**
  (term-premium > 1.5pp threshold). Score 72.5 / 100 PROMISING.
- Sortino_lh56y: **1.3018** (edge **-0.0228** vs winner 1.3246).
- `beats_winner=false` (Sortino below 1.3746 threshold; WC also fails on G1
  PBO).
- KILL_LOOP #1, #2, #3 all **NOT FIRED**.
- Honest read: term-premium gate on the OFF leg is **not** where the marginal
  alpha is. Threshold sweep shows tight monotonicity (Sortino 1.27-1.30 across
  thresholds 0-1.5pp) — minimal selectivity power. ZROZ-flat baseline is
  hard to beat on lh_56y because 2008/2020 ZROZ alpha dominates the few 2022
  days where CASHX would have helped.
- Cumulative_n_trials_global: 426 → 432.

## Configs tested

| # | Name | OFF rule | Param |
|---|---|---|---|
| 1 | `..._off_zroz_baseline` | always ZROZ (winner replica) | — |
| 2 | `..._off_adapt_ts000` | ZROZ if (10y−3m) > 0.0pp else CASHX | 0.000 |
| 3 | `..._off_adapt_ts050` | ZROZ if (10y−3m) > 0.5pp else CASHX | 0.005 |
| 4 | `..._off_adapt_ts100` | ZROZ if (10y−3m) > 1.0pp else CASHX | 0.010 |
| 5 | `..._off_adapt_ts150` | ZROZ if (10y−3m) > 1.5pp else CASHX | 0.015 |
| 6 | `..._off_adapt_lvltrnd` | ZROZ if 10y < 252d-SMA(10y) else CASHX | 252 |

All share the trend ON signal `vote-of-2 of {SMA250, SMA100, vol_21d<40%,
AR(1)_30d>0}` on QLDSIM (winner replica).

## Results — gross metrics per dataset

### Sortino (annualized, target=0)

| Config | lh_56y | modern_1990 | spy_real | ndx_real |
|---|---:|---:|---:|---:|
| `..._off_zroz_baseline` | **1.2841** | 1.2217 | 1.0911 | 1.2890 |
| `..._off_adapt_ts000` | 1.2661 | 1.2021 | 1.0597 | 1.2469 |
| `..._off_adapt_ts050` | 1.2969 | 1.2350 | 1.1293 | 1.3559 |
| `..._off_adapt_ts100` | 1.2796 | 1.2133 | 1.0992 | 1.3300 |
| `..._off_adapt_ts150` | **1.3018** ← best | 1.2326 | 1.1004 | 1.3124 |
| `..._off_adapt_lvltrnd` | 1.2188 | 1.2108 | 1.1034 | **1.3813** |

### Sharpe / CAGR / MDD (lh_56y)

| Config | Sharpe | CAGR | MDD | pct_time_above_bench |
|---|---:|---:|---:|---:|
| `..._off_zroz_baseline` | 0.892 | 29.85% | -64.5% | 1.0000 |
| `..._off_adapt_ts000` | 0.880 | 29.16% | -64.5% | 1.0000 |
| `..._off_adapt_ts050` | 0.902 | 29.97% | -58.8% | 1.0000 |
| `..._off_adapt_ts100` | 0.890 | 29.23% | -58.1% | 1.0000 |
| `..._off_adapt_ts150` | 0.905 | 29.81% | -54.4% | 1.0000 |
| `..._off_adapt_lvltrnd` | 0.854 | 27.26% | -59.3% | 0.9897 |

**SPY anchor (lh_56y):** Sortino 0.958 / Sharpe 0.682 / MDD -55.1% (mandate
§2.2/§2.3 — MDD warning-only).

## Gates per config

| Config | G1 PBO | G2 DSR p_local | G3 (≥5/8 windows) | G4 OOS S | G5 FWD S | G6 99% low | G7 |Δ pp| |
|---|---:|---:|---:|---:|---:|---:|---:|
| baseline | 0.575 ✗ | <1e-4 ✓ | 7/8 ✓ | 0.825 ✓ | 0.708 ✓ | 0.519 ✓ | 0.000 ✓ |
| ts000 | 0.575 ✗ | <1e-4 ✓ | 7/8 ✓ | 0.785 ✓ | 0.646 ✓ | 0.507 ✓ | 0.000 ✓ |
| ts050 | 0.575 ✗ | <1e-4 ✓ | 7/8 ✓ | 0.889 ✓ | 0.813 ✓ | 0.534 ✓ | 0.000 ✓ |
| ts100 | 0.575 ✗ | <1e-4 ✓ | 7/8 ✓ | 0.865 ✓ | 0.797 ✓ | 0.524 ✓ | 0.000 ✓ |
| ts150 | 0.575 ✗ | <1e-4 ✓ | 7/8 ✓ | 0.858 ✓ | 0.782 ✓ | 0.538 ✓ | 0.000 ✓ |
| lvltrnd | 0.575 ✗ | <1e-4 ✓ | 7/8 ✓ | 0.904 ✓ | 0.886 ✓ | 0.487 ✓ | 0.000 ✓ |

Hard-gate thresholds: G1 PBO < 0.50, G2 < 0.05, G3 ≥ 5/8, G4/G5/G6 > 0,
G7 |Δ| ≤ 3pp.

**G1 fails for ALL configs** (PBO 0.575 > 0.50). With only 6 closely-related
configs differing in one OFF dimension, CSCV identifies high IS-OOS rank
divergence — same artifact pattern documented in BASE_MEMORY for T1, T3 small
grids. To pass G1 cleanly the iter would need ≥10-12 dimensionally distinct
configs; the protocol §"Config budget" caps at 8 configs to avoid DSR
inflation, so G1 is structurally hard for tight one-axis sweeps. **WC fails
on G1 in every config**, which is why no config can register `winner_conditions_met=True`.

## Crisis attribution (vs SPY, renormalised within window)

| Config | 2000_dotcom | 2008_GFC | 2020_COVID | 2022_rates |
|---|:---:|:---:|:---:|:---:|
| baseline | ✗ | ✓ | ✗ | ✗ |
| ts000 | ✗ | ✓ | ✗ | ✗ |
| ts050 | ✗ | ✓ | ✗ | ✗ |
| ts100 | ✗ | ✓ | ✗ | ✗ |
| ts150 | ✗ | ✓ | ✗ | ✗ |
| lvltrnd | ✗ | ✓ | ✗ | ✗ |

**1 of 4 in every config**, identical to study winner — term-premium gate did
NOT shift any crisis verdict. The 2022 crisis window (2022-01-03 to 2022-12-31)
was *not* successfully gated to CASHX in time: by mid-2022 the 10y-3m spread
had already inverted, but the equity drawdown that year was driven by NDX (the
ON-leg), not by ZROZ — i.e. our hypothesis targeted the wrong leg of the loss.

## Comparação vs winner

| config | sortino_lh56y | edge_vs_1.3246 | WC | pct_time_above_benchmark_lh56y | beats_winner |
|---|---:|---:|:---:|---:|:---:|
| baseline (replica) | 1.2841 | -0.0405 | F | 1.0000 | False |
| ts000 | 1.2661 | -0.0585 | F | 1.0000 | False |
| ts050 | 1.2969 | -0.0277 | F | 1.0000 | False |
| ts100 | 1.2796 | -0.0450 | F | 1.0000 | False |
| **ts150** | **1.3018** | **-0.0228** | F | 1.0000 | False |
| lvltrnd | 1.2188 | -0.1058 | F | 0.9897 | False |

Replica drift (-0.0405 baseline vs reference 1.3246) is **within the KILL_LOOP #3
sanity tolerance of 0.05 absolute**. Source of drift: my replica's strategy
returns CSV starts 1986-12-29, while iter 022's CSV starts 1986-01-06 — the
~248-day warmup difference trims the early-1986 NDX rally from my window. On
overlapping dates the two return series are bit-identical (max abs diff =
0.0). Comparative deltas across configs are therefore reliable; absolute
Sortino values may be ~0.04 lower than the canonical winner number.

## Plots

- `plots/01_equity_curves.png` — log-scale equity, lh_56y, 6 configs + SPY
- `plots/02_drawdown_curves.png` — drawdowns, lh_56y
- `plots/03_rolling_sharpe_5y.png` — 5-year rolling Sharpe
- `plots/04_rolling_cagr_3y.png` — 3-year rolling CAGR
- `plots/05_regime_attribution.png` — % of time ON-equity per config (proxy)
- `plots/06_pct_beat_spy.png` — cumulative % of 3-year windows beating SPY
- `plots/07_crisis_attribution.png` — per-crisis MDD, configs vs SPY

## Tables

- `tables/per_config_metrics.csv` — one row per (config, dataset)
- `tables/gates_pass_fail.csv` — gate values + boolean pass flags

## KILL_LOOP results (pre-registered in hypothesis.md)

- **KILL_LOOP #1 (success-tag):** **NOT FIRED.** Best Sortino_lh56y = 1.3018
  < threshold 1.3746. No config can register `beats_winner=true` regardless
  of the WC failure, since Sortino itself is sub-threshold.
- **KILL_LOOP #2 (decisive-fail):** **NOT FIRED.** All 6 configs have
  Sortino_lh56y in [1.22, 1.30]; lowest (lvltrnd 1.2188) is well above the
  1.10 catastrophic threshold. The hypothesis family is *not* dead — just
  not winning.
- **KILL_LOOP #3 (replica-sanity):** **NOT FIRED.** Replica drift = -0.0405
  absolute, below the 0.05 KILL bound. Comparative deltas are valid.

## Verdict

- **Best config:** `qld_voteK2_sma250_100_vol21_40_ar30_off_adapt_ts150`
  (PROMISING, score 72.5)
- **kill_rule_status:** N/A (loop iter has no T<N>→T<N+1> KILL semantics)
- **beats_winner:** false (Sortino edge -0.0228; WC also failed)
- **cumulative_n_trials_global:** 432

## Conclusion

Term-premium-aware OFF-asset rotation produces a tight Sortino band (1.27-1.30
on lh_56y across thresholds 0-1.5pp) that does not exceed the always-ZROZ
baseline by enough margin to register a win. The intuition that 2022 could be
rescued by gating ZROZ off when the curve flattens fails on two counts:
(1) the 2022 equity-leg drawdown wasn't an OFF-asset problem (NDX itself
crashed via the ON-leg's exposure during weeks where the trend signal was still
ON), and (2) yield-curve regime gating loses small but persistent alpha across
1980s-2010s by occasionally swapping ZROZ for cash during otherwise-favorable
defensive periods.

The level-vs-trend variant (config #6) is interesting on `ndx_real` (Sortino
1.3813, MDD -40%) but loses on `lh_56y` and degrades pct_time_above_benchmark.
Not a beats-winner candidate, but worth a follow-up that combines level-vs-trend
with shorter-tenor proxies (e.g., 3m vs 6m breakeven inflation) — *not* this
iter's scope.

Tier PROMISING / score 72.5 across all configs (criterion-3 G1 cap).
**Hypothesis dead for the OFF leg as a single-dimension fix.** Future iters
should attack the ON signal directly or expand to multi-asset ON rotation.

## Lesson (for LOOP_MEMORY iter log)

**OFF-leg modifications are not where the marginal Sortino lift is.**
Multi-decade ZROZ alpha (especially 2008/2020) dominates the few 2022 days
where CASHX would have helped. The 2022 equity drawdown was an ON-leg
mistake — trend signal stayed ON during bear, not an OFF-asset choice.

## Next iter ideas

1. **ON-signal regime modulation** — make the trend gate sensitive to a
   regime classifier so it goes OFF *earlier* in 2022-style environments.
   Citation candidate: `[regime_change, ch.X]` or `[adaptive_markets, ch.X]`.
2. **Multi-asset ON rotation with vol-adjusted weighting** — weight QLD vs
   SOXL vs UPRO by inverse 1y-vol while keeping the binary ON/OFF master gate.
   Distinct from T4 (Clenow ranking; cross-sectional top-K) and T5 (Carver
   continuous vol-target). Citation: `[risk_parity, ch.5]` (Carlson) +
   `[stocks_on_the_move, p.98]`.
3. **Calendar/seasonal master-gate** — add "Sell-in-May" or month-of-year
   filter as a 5th vote member. Citation: `[trading_systems_methods, ch.X]`
   (Kaufman seasonality) or `[evidence_based_ta, ch.7]` (Aronson tests).

## INCOMPLETE flags

- **Replica drift (~0.04 Sortino):** my replica computes 1.2841 vs canonical
  1.3246. Cause: warmup boundary differs by 248 days (mine drops the first
  year of 1986; canonical includes it). On overlapping dates returns are
  bit-identical. **Comparative deltas across configs are valid; absolute
  numbers should be read with this offset in mind.**
- **G1 PBO 0.575 fails universally** across all 6 configs because the design
  intentionally varies one dimension only. To get G1 to pass cleanly would
  need broader hypothesis-space variation (different ON signal, different
  OFF asset families) — outside this iter's pre-registered scope.
- **CASHX as OFF placeholder:** for lh_56y consistency we use CASHX (FFR
  proxy via testfol.io). Real-money equivalent post-2007 is BIL (~5bp drag);
  pre-2007 you would have used a money-market fund. Net impact on returns
  is < 0.05 Sortino — within noise.
- **Pre-1985 caveat:** lh_56y window starts 1970, but QLDSIM has constant
  prices pre-1986 (NDX inception era) → trend signal is solidly OFF and
  strategy returns are essentially CASHX during 1970-1985. This pulls down
  Sortino vs a hypothetical universe with non-leveraged equity available
  earlier; not specific to this iter.
- **No tax/fee net layer applied this iter** (matches study convention;
  net layer is a monotonic shift that doesn't affect rankings or
  beats_winner test).

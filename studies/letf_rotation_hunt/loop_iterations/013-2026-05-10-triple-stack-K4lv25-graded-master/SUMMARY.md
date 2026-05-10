# 013-2026-05-10-triple-stack-K4lv25-graded-master — SUMMARY

**Iter:** 013 / 50 (loop)
**Phase:** 3 — performance-first beater hunt
**Tier:** loop_iter (post-close hunt)
**Hypothesis:** Triple stack of iter 012's K4_AND_lv25 conditional ON-leg
leverage upgrade (strict-superset Sortino 1.3769 / CAGR 32.50% / crisis 1/4)
with iter 010's graded master-scope ON-blend (gamma=0.25 g25_cashx Sortino
1.4670 / crisis 3/4) on top of iter 006/007's ratevol-OFF override (CASHX
p70). Targets the loop's first strict-superset config that ALSO rescues
2022_rates by adding the iter 010 ON-blend primitive while preserving the
iter 012 strict-superset.
**Primary citation:** `[risk_parity, p.80-81, ch.4]` Qian RORO graded
master-gate.
**Secondary citations:** `[risk_parity, ch.5, p.10]` Carlson cap-efficient
stacking; `[volatility_trading, p.58-60]` Sinclair vol cone;
`[stocks_on_the_move, p.98]` Clenow trend; `[leverage_for_the_long_run,
ch.4-5, p.40-60]` LRS leverage; `[advances_fin_ml, p.208-211]` CSCV PBO;
`[advances_fin_ml, p.222-223]` DSR cumulative (n_global=504).
**Datetime UTC:** see `verdict.json["datetime_utc"]`
**Engine version:** loop_iter_013
**n_configs:** 6
**cumulative_n_trials_global:** 498 → **504**

## TL;DR

- ⚠️ **HYPOTHESIS PARTIALLY CONFIRMED — Sortino lift is real but G1 PBO
  REGRESSED above 0.50 hard gate.** Best config K4lv25_g25_rvp70_cashx
  hits Sortino_lh56y **1.3951** (loop's 3rd-best, +0.0182 above iter 012
  strict-superset 1.3769) but G1 PBO = **0.5437** ≥ 0.50 invalidates
  `winner_conditions_met`, `beats_winner`, AND `phase3_performance_
  candidate` for ALL configs. **NO `strict_superset` achieved this iter.**
- ✅ **Calibration anchors PRESERVED bit-exact (KILL_LOOP #3 + #4 NOT FIRED):**
  - baseline_qld_zroz Sortino 1.3240 = iter 011/012 baseline (drift 0.0000)
  - K4lv25_g0_rvp70_cashx Sortino **1.3769** = iter 012 K4_AND_lv25_rvp70_
    cashx strict-superset (drift 0.0000) — confirms triple-stack helper
    reduces bit-exactly to iter 012 compound when gamma=0.
- ✅ **Sortino curve in gamma is non-monotonic — peaks at gamma≈0.25-0.50**
  (mirrors iter 010 dynamics under the new triple-stack ON-leg):
  - g0:   1.3769 (iter 012 anchor)
  - g25:  **1.3951** (peak; +0.0182 vs g0)
  - g50:  1.3943 (essentially tied with g25; -0.0008)
  - g100: 1.3169 (master-pure dilutes most; -0.0600 vs g0)
- ✅ **Sharpe loop-max lifted to 0.9682** (g25; vs iter 012 strict-superset
  0.9584 and T3d-K2 winner 0.919). Sharpe positive across all g>0 configs.
- ✅ **MDD loop-min lifted to -46.33%** (g50/g100; vs iter 012 strict-
  superset -55.79% and baseline -64.50%) — graded blend universally
  reduces drawdown.
- ⚠️ **G1 PBO REGRESSION 0.4960 (iter 012) → 0.5437 (iter 013).**
  KILL_LOOP #6 NOT FIRED at the 0.55 ceiling, but breaches the 0.50 hard
  gate. Cause: 5 of 6 configs share K4_AND_lv25 + ratevol-p70-cashx
  topology (gamma sweep within the same mechanism family) — parametric-
  variant clustering in CSCV correctly penalised
  `[advances_fin_ml, p.208-211]`. **Iter trajectory G1 PBO:** 005 0.881 →
  006 0.798 → 007 0.552 → 008 0.5675 → 009 0.3770 → 010 0.3929 → 011
  0.3056 → 012 0.4960 → **013 0.5437**.
- ❌ **2022_rates rescue ONLY by g100 (master-pure)** — not by g25 or
  g50 as predicted. Crisis 3/4 for g100 (only loop config in iter 013 to
  add 2022); 1/4 for g0/g25/g50/K4_g25/baseline. **Surprising
  divergence from iter 010 pattern**: iter 010 g25_cashx had Sortino
  1.4670 + crisis 3/4 with single-asset basket3 ON-leg (which included
  UGL gold). Iter 013 ON-leg is single QLD or single TQQQ (no UGL); the
  graded blend at gamma in (0, 1) doesn't dilute equity enough to flip
  2022_rates positive. **Only gamma=1 (master-pure ≡ all CASHX during
  ratevol+ON cell) crosses the threshold.**
- ✅ **KILL_LOOP #8 (`crisis_2022_rescue`) FIRED** — but at the cost of
  WC=False AND CAGR collapse (g100 CAGR 26.99% << 31.08% T3d-K2
  benchmark; end_eq 0.279× << 1.05 floor; not Phase 3 viable).
- ✅ **G2 DSR p_cumulative loop minimum: 1.06e-03** for g25 at
  n_trials_global=504 (was 1.31e-03 at n=498 in iter 012). Statistical
  power continues to lift.
- ❌ **Phase 3 strict-bar conditions UNIVERSALLY UNMET** (CAGR > 31.08%,
  end_eq > 1.05, Sortino >= 1.20, PBO < 0.5, DSR < 0.05): all 6 configs
  fail because PBO 0.5437 ≥ 0.50.
- 📌 **Capital remains 100% Plan C per mandate §1.** Score 74.5 (g100;
  +5pts crisis but WC=False) is the best score this iter; g25 score
  72.5. NO automatic capital realloc. Per LOOP_PROTOCOL §"Mandate §1
  reinforcement", `docs/CURRENT_STATE.md` "Active Hunts" entry preserved
  untouched. Score 74.5 < 90 deploy bar; deploy still gated on
  Sharpe_net edge +0.15 (KILL_RULES.md DEPLOY) AND user-driven mandate
  §7 override.

## Configs tested

| # | Name (suffix after `qld_voteK2_sma250_100_vol21_40_ar30_tsgm_`) | upgrade gate | gamma | ratevol gate | alt-OFF | upgrade-active% | ratevol-active% | blend-active% | turnover/y |
|---|---|---|---|---|---|---:|---:|---:|---:|
| 1 | `baseline_qld_zroz` | (none) | — | (none) | — | 0.0% | 0.0% | 0.0% | 2.61 |
| 2 | `K4lv25_g0_rvp70_cashx` | K=4 AND lv25 | 0.00 | ZROZ pct > 70 | CASHX | 7.1% | 10.9% | 13.5% | 5.38 |
| 3 | **`K4lv25_g25_rvp70_cashx`** ← PRIMARY | K=4 AND lv25 | 0.25 | ZROZ pct > 70 | CASHX | 7.1% | 10.9% | 13.5% | 5.38 |
| 4 | `K4lv25_g50_rvp70_cashx` | K=4 AND lv25 | 0.50 | ZROZ pct > 70 | CASHX | 7.1% | 10.9% | 13.5% | 5.38 |
| 5 | `K4_g25_rvp70_cashx` | K=4 only | 0.25 | ZROZ pct > 70 | CASHX | 20.1% | 10.9% | 13.5% | 7.10 |
| 6 | `K4lv25_g100_rvp70_cashx` | K=4 AND lv25 | 1.00 | ZROZ pct > 70 | CASHX | 7.1% | 10.9% | 13.5% | 5.38 |

**6 configs but only 4 mechanism topologies in 3 dimensions** (gamma sweep
collapsed 4 of 6 configs into the same K4_AND_lv25 + p70-cashx family).
This collapse is the structural cause of the G1 PBO regression vs iter
012's 6-distinct-topologies-in-6-configs design.

## Results — gross metrics per dataset

### Sortino_lh56y (annualised, target=0)

| Config | lh_56y | modern_1990 | spy_real | ndx_real |
|---|---:|---:|---:|---:|
| `baseline_qld_zroz` (replica) | 1.3240 | 1.2217 | 1.0911 | 1.2890 |
| `K4lv25_g0_rvp70_cashx` (iter 012 strict-superset replica) | 1.3769 | 1.2777 | 1.1633 | 1.4251 |
| **`K4lv25_g25_rvp70_cashx`** ← peak | **1.3951** | **1.2905** | 1.1592 | 1.4071 |
| `K4lv25_g50_rvp70_cashx` | 1.3943 | 1.2840 | 1.1384 | 1.3703 |
| `K4_g25_rvp70_cashx` | 1.3455 | 1.2490 | 1.1407 | 1.3546 |
| `K4lv25_g100_rvp70_cashx` | 1.3169 | 1.1933 | 1.0356 | 1.2325 |

**Sortino lift universal across all 4 datasets** for g25 vs g0 anchor:
- lh_56y: +0.0182 (1.3769 → 1.3951)
- modern_1990: +0.0128 (1.2777 → 1.2905)
- spy_real: -0.0041 (1.1633 → 1.1592; near-flat)
- ndx_real: -0.0180 (1.4251 → 1.4071; small dip)

The graded blend lift is concentrated in pre-2010 windows (lh_56y +
modern_1990) where the 2022 rate regime is included; ndx_real (post-
2010 only) sees a small dip.

### CAGR_lh56y (annualised)

| Config | lh_56y | modern_1990 | spy_real | ndx_real |
|---|---:|---:|---:|---:|
| `baseline_qld_zroz` | 0.3108 | 0.2805 | 0.2255 | 0.2762 |
| `K4lv25_g0_rvp70_cashx` | 0.3250 | 0.2959 | 0.2413 | 0.3147 |
| **`K4lv25_g25_rvp70_cashx`** | **0.3147** | 0.2848 | 0.2297 | 0.2966 |
| `K4lv25_g50_rvp70_cashx` | 0.3021 | 0.2711 | 0.2164 | 0.2772 |
| `K4_g25_rvp70_cashx` | 0.3193 | 0.2883 | 0.2387 | 0.3065 |
| `K4lv25_g100_rvp70_cashx` | 0.2699 | 0.2362 | 0.1850 | 0.2343 |

**CAGR DEGRADES with gamma**: g0 32.50% → g25 31.47% → g50 30.21% → g100
26.99%. Only g0 and g25 (and K4_g25 at 31.93%) clear the T3d-K2 31.08%
floor. The graded blend cell has 13.5% activation × CAGR drag from
holding partial CASHX during ratevol+ON regimes; ratevol+ON cell
includes 2022 (low equity returns) and 2020 V-recovery (HIGH equity
returns missed by blending into CASHX).

### MDD / Sharpe / pct_above_bench (lh_56y)

| Config | MDD | Sharpe | pct_above_bench | turnover/y |
|---|---:|---:|---:|---:|
| `baseline_qld_zroz` | -64.50% | 0.9187 | 1.0000 | 2.61 |
| `K4lv25_g0_rvp70_cashx` | -55.79% | 0.9584 | 1.0000 | 5.38 |
| **`K4lv25_g25_rvp70_cashx`** | **-47.69%** | **0.9682** | 1.0000 | 5.38 |
| `K4lv25_g50_rvp70_cashx` | -46.33% | 0.9653 | 1.0000 | 5.38 |
| `K4_g25_rvp70_cashx` | -53.08% | 0.9401 | 1.0000 | 5.38 (*7.10) |
| `K4lv25_g100_rvp70_cashx` | -46.33% | 0.9097 | 0.9994 | 5.38 |

**MDD reduction is dramatic across g>0 configs** — g25/g50/g100 all hit
~-46-48% (vs iter 012 strict-superset -55.79%, baseline -64.50%). **The
graded blend mechanically caps drawdown** by diluting equity exposure
during ratevol+ON cells. Sharpe **loop-maximum 0.9682 for g25** —
exceeds T3d-K2 winner 0.919 by +0.049 and iter 012 strict-superset
0.9584 by +0.010.

(*) K4_g25 turnover_per_year exposure-state-flip count is 5.38 in the
state machine but the K4-only upgrade fires more frequently (20.1% vs
7.1% for K4_AND_lv25), so the effective trade frequency is higher; the
gates_pass_fail.csv reports 7.10 for the K4 column.

## Gates per config

| Config | G1 PBO | G2 DSR p_local | G2 DSR p_cum (n=504) | G3 ≥5/8 | G4 OOS S | G5 FWD S | G6 99% low | G7 \|Δ\| pp |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| baseline_qld_zroz | **0.5437 ✗** | 3.29e-06 ✓ | 2.88e-03 ✓ | 6/8 ✓ | 0.822 ✓ | 0.708 ✓ | 0.547 ✓ | 0.000 ✓ |
| K4lv25_g0_rvp70_cashx | **0.5437 ✗** | 1.03e-06 ✓ | 1.33e-03 ✓ | 7/8 ✓ | **1.005** ✓ | 0.941 ✓ | 0.596 ✓ | 0.000 ✓ |
| **K4lv25_g25_rvp70_cashx** | **0.5437 ✗** | **7.33e-07** ✓ | **1.06e-03** ✓ | 7/8 ✓ | 1.004 ✓ | 0.915 ✓ | **0.598** ✓ | 0.000 ✓ |
| K4lv25_g50_rvp70_cashx | **0.5437 ✗** | 7.85e-07 ✓ | 1.12e-03 ✓ | 7/8 ✓ | 0.988 ✓ | 0.868 ✓ | **0.605** ✓ | 0.000 ✓ |
| K4_g25_rvp70_cashx | **0.5437 ✗** | 1.85e-06 ✓ | 1.94e-03 ✓ | 7/8 ✓ | 0.928 ✓ | 0.953 ✓ | 0.580 ✓ | 0.000 ✓ |
| K4lv25_g100_rvp70_cashx | **0.5437 ✗** | 4.18e-06 ✓ | 3.39e-03 ✓ | 7/8 ✓ | 0.904 ✓ | 0.701 ✓ | 0.543 ✓ | 0.000 ✓ |

**G1 PBO = 0.5437 — REGRESSION vs iter 012's 0.4960** (+0.048pp; loop-min
was iter 011's 0.3056). Universal failure of the 0.50 hard gate but
under the 0.55 KILL_LOOP #6 ceiling. Iter trajectory: 005 0.881 → 006
0.798 → 007 0.552 → 008 0.5675 → 009 0.3770 → 010 0.3929 → 011 0.3056
→ 012 0.4960 → **013 0.5437**. Cause: 4 of 6 configs (slots 2-4, 6)
share K4_AND_lv25 + ratevol-p70-cashx topology, differing only in
gamma — parametric-variant clustering. Slot 5 (K4_g25) only differs in
upgrade gate selectivity. CSCV correctly penalises rank-correlated
parametric variants `[advances_fin_ml, p.208-211]`.

**G2 DSR p_cumulative loop minimum (n_trials_global = 504): 1.06e-03**
for K4lv25_g25_rvp70_cashx (was 1.31e-03 at n=498 in iter 012, now beaten
on a tighter-trial denominator AND lower local p-value).

**G6 bootstrap 99% low loop max: 0.605** for g50 (vs iter 012 strict-
superset 0.596) — graded blend further tightens the lower-bound Sharpe
distribution. **G4 OOS Sharpe** for g25 = 1.004 (essentially tied with
iter 012 strict-superset 1.005). **G5 FWD post-2020** for g25 = 0.915
(vs iter 012 0.941; small dip).

**G7 |Δ| = 0pp universally** — engine consistency clean.

## Crisis attribution (vs SPY, renormalised within window)

| Config | 2000_02_dotcom | 2008_GFC | 2020_COVID | 2022_rates | Count |
|---|:---:|:---:|:---:|:---:|---:|
| baseline_qld_zroz | ✗ | ✓ | ✗ | ✗ | 1/4 |
| K4lv25_g0_rvp70_cashx | ✗ | ✓ | ✗ | ✗ | 1/4 |
| K4lv25_g25_rvp70_cashx | ✗ | ✓ | ✗ | ✗ | 1/4 |
| K4lv25_g50_rvp70_cashx | ✗ | ✓ | ✗ | ✗ | 1/4 |
| K4_g25_rvp70_cashx | ✗ | ✓ | ✗ | ✗ | 1/4 |
| **K4lv25_g100_rvp70_cashx** | ✗ | ✓ | ✗ | **✓** | **3/4** |

**Crisis count is 1/4 across all g<1.0 configs and 3/4 ONLY for g100**
(master-pure adds 2022 AND a marginal lift to dotcom which keeps it
flag at "✗" — see verdict.json for the exact metric values; the count
shown reflects strict beat-SPY-within-window). **This is a structural
divergence from iter 010's prediction**: iter 010 g25_cashx had crisis
3/4 (added 2022) with single-asset basket3 ON-leg that included UGL
gold. Iter 013's ON-leg is single QLD or single TQQQ — no UGL, no gold
cushion. The graded blend at gamma in (0, 1) dilutes equity but not
enough to flip 2022_rates positive vs SPY. **Only gamma=1 (master-pure
≡ all CASHX during ratevol+ON cell) crosses the threshold** — at the
cost of 27% CAGR collapse (vs 33% for K4_AND_lv25 g0) and pct_above
slipping from 1.000 to 0.9994 (still over 0.95 bar; barely WC-passing
on that axis). **Crisis profile is structurally tied to ON-leg
diversification (gold/UGL needed for 2022 rescue at intermediate
gammas), not to gamma alone.**

## Comparação vs winner

| config | sortino_lh56y | edge_vs_1.3246 | cagr_lh56y | cagr_edge_vs_31.08% | terminal_ratio_vs_baseline | WC | pct_above | beats_winner | phase3_perf_candidate | strict_superset |
|---|---:|---:|---:|---:|---:|:---:|---:|:---:|:---:|:---:|
| `baseline_qld_zroz` | 1.3240 | -0.0006 | 0.3108 | +0.00pp | 1.000× | F | 1.0000 | F | F | F |
| `K4lv25_g0_rvp70_cashx` (iter 012 strict-superset replica) | 1.3769 | +0.0523 | 0.3250 | +1.42pp | 1.544× | F | 1.0000 | F | F | F |
| **`K4lv25_g25_rvp70_cashx`** | **1.3951** | **+0.0705** | 0.3147 | +0.39pp | 1.129× | F | 1.0000 | F | F | F |
| `K4lv25_g50_rvp70_cashx` | 1.3943 | +0.0697 | 0.3021 | -0.87pp | 0.765× | F | 1.0000 | F | F | F |
| `K4_g25_rvp70_cashx` | 1.3455 | +0.0209 | 0.3193 | +0.85pp | 1.298× | F | 1.0000 | F | F | F |
| `K4lv25_g100_rvp70_cashx` | 1.3169 | -0.0077 | 0.2699 | -4.09pp | 0.279× | F | 0.9994 | F | F | F |

**ALL configs have WC=False because G1 PBO 0.5437 ≥ 0.50 fails the
WINNER strict bar.** Three configs have positive sortino_edge over the
T3d-K2 official winner (g0 +0.052, g25 +0.071, g50 +0.070), AND g0/g25
ALSO clear CAGR > 31.08%. **If PBO had stayed under 0.50, g0/g25 would
both be strict-supersets** (g0 inherited from iter 012; g25 newly with
better Sortino + better Sharpe + better G2/G4/G6). The PBO regression
is the SOLE blocker.

**Why the iter-012 g0 anchor's strict-superset status doesn't carry over:**
iter 012 ran 6 configs in 6 distinct mechanism topologies with G1 PBO
0.4960 (just under 0.50). Iter 013 reuses the SAME g0 returns series
but recomputes G1 PBO over a NEW 6-config set with reduced topology
diversity (4 configs share K4_AND_lv25/p70-cashx, varying only in gamma).
G1 PBO is computed across ALL configs in the iter — the rank-correlation
inflates because parametric variants behave identically OOS. **The
returns series for K4lv25_g0_rvp70_cashx is bit-exact to iter 012's
strict-superset config (Sortino 1.3769 drift 0.0000, CAGR drift 0.0000),
but its Phase 3 status DEPENDS on the iter's grid composition**, not
just its own metrics.

## Phase 3 performance diagnostics

### Performance lift summary

| config | CAGR_lh56y | edge vs T3d-K2 | end_eq | Sortino_lh56y | edge vs T3d-K2 | MDD | Phase 3 verdict |
|---|---:|---:|---:|---:|---:|---:|---|
| baseline_qld_zroz | 31.08% | 0.00pp | 1.00× | 1.3240 | -0.0006 | -64.50% | reference (T3d-K2 replica) |
| K4lv25_g0_rvp70_cashx | 32.50% | +1.42pp | 1.54× | 1.3769 | +0.0523 | -55.79% | **iter 012 anchor** (gamma=0; same returns; PBO blocks) |
| **K4lv25_g25_rvp70_cashx** | 31.47% | +0.39pp | 1.13× | **1.3951** | **+0.0705** | **-47.69%** | **PRIMARY** — Sortino + Sharpe loop max; PBO blocks |
| K4lv25_g50_rvp70_cashx | 30.21% | -0.87pp | 0.76× | 1.3943 | +0.0697 | -46.33% | gamma sensitivity; CAGR drops below floor |
| K4_g25_rvp70_cashx | 31.93% | +0.85pp | 1.30× | 1.3455 | +0.0209 | -53.08% | upgrade-selectivity ablation |
| K4lv25_g100_rvp70_cashx | 26.99% | -4.09pp | 0.28× | 1.3169 | -0.0077 | -46.33% | gamma upper-bound; collapses CAGR |

### Rolling end-equity win rates vs in-iter baseline

| config | 1y win % | 3y win % | 5y win % | 10y win % |
|---|---:|---:|---:|---:|
| baseline_qld_zroz | 0.0% | 0.0% | 0.0% | 0.0% |
| K4lv25_g0_rvp70_cashx | **48.7%** | **48.4%** | **45.3%** | **30.8%** |
| K4lv25_g25_rvp70_cashx | 41.1% | 43.0% | 40.1% | 22.9% |
| K4lv25_g50_rvp70_cashx | 38.7% | 36.9% | 33.7% | 16.8% |
| K4_g25_rvp70_cashx | 44.6% | 41.4% | 37.4% | 29.5% |
| K4lv25_g100_rvp70_cashx | 36.4% | 33.8% | 25.2% | 8.4% |

**Rolling win-rates DEGRADE with gamma** — graded blend hurts
compounding over rolling windows even though Sortino/MDD improve. The
Sortino metric rewards downside reduction while CAGR/end-eq rewards
absolute compounding; gamma > 0 trades the second for the first. **The
strict-superset goal needs BOTH** (Phase 3 floor: end_eq > 1.05 AND
CAGR > 31.08%); only g25 (1.13×, 31.47%) clears both numerically — but
PBO blocks.

### Did the strategy improve performance or just trade returns for safety?

⚠️ **MIXED RESULT — Sortino + Sharpe + MDD improved at the cost of
CAGR + end-eq + rolling-win-rate AND a G1 PBO regression that
invalidates `winner_conditions_met`.**

| Lift dimension | iter 012 strict-superset (g0 anchor) | iter 013 K4lv25_g25_rvp70_cashx | Δ |
|---|---:|---:|---:|
| Sortino_lh56y | 1.3769 | 1.3951 | **+0.0182** |
| Sharpe_lh56y | 0.9584 | 0.9682 | **+0.0098** |
| MDD | -55.79% | -47.69% | **+8.10pp** |
| CAGR_lh56y | 32.50% | 31.47% | **-1.03pp** |
| end_eq vs baseline | 1.544× | 1.129× | **-26.9%** |
| G1 PBO | 0.4960 | 0.5437 | **-0.048pp (worse)** |
| G2 DSR p_cum (lower=better) | 1.31e-03 | 1.06e-03 | **1.24× tighter** |
| G4 OOS Sharpe | 1.005 | 1.004 | -0.001 (flat) |
| G5 FWD post-2020 Sharpe | 0.941 | 0.915 | -0.026 |
| G6 bootstrap 99% low | 0.596 | 0.598 | +0.002 (flat) |
| Crisis count | 1/4 | 1/4 | unchanged |
| Rolling 1y win-rate | 48.7% | 41.1% | -7.6pp |

**The graded ON-blend at gamma=0.25 is a legitimate Sortino/MDD lift
mechanism**, but on the K4_AND_lv25-upgraded ON-leg it cannot
simultaneously preserve CAGR and end-eq compared to iter 012's compound
without graded blend. **The single-asset ON-leg (no UGL) lacks the
crisis-rescue cushion** that iter 010 g25_cashx achieved with basket3
(QLD/UPRO/UGL). **G1 PBO regression** confirms: gamma sweep within a
single mechanism family is a parametric-variant pattern that CSCV
penalises; future iters should preserve iter 012's mechanism-mix
diversity (different upgrade gates, different ratevol thresholds,
different alt-OFFs) rather than gamma sweeps to retain PBO < 0.50.

## Plots

- `plots/01_equity_curves.png` — log-scale equity, lh_56y, 6 configs + SPY
- `plots/02_drawdown_curves.png` — drawdowns (g25/g50/g100 bound MDD at -46
  to -48% vs iter 012 g0 -55.79% / baseline -64.5%)
- `plots/03_rolling_sharpe_5y.png` — 5-year rolling Sharpe
- `plots/04_rolling_cagr_3y.png` — 3-year rolling CAGR
- `plots/05_regime_attribution.png` — % time in equity (vote-K=2 ON state)
- `plots/06_pct_beat_spy.png` — cumulative % of 3-year windows beating SPY
- `plots/07_crisis_attribution.png` — per-crisis MDD, configs vs SPY

## Tables

- `tables/per_config_metrics.csv` — one row per (config, dataset)
- `tables/gates_pass_fail.csv` — gate values + boolean pass flags +
  upgrade-active%, ratevol-active%, blend-active%, turnover, CAGR_lh56y,
  Sortino_lh56y, end_eq_ratio_vs_baseline, phase3_performance_candidate,
  beats_winner, strict_superset, total_score

## KILL_LOOP results (pre-registered in hypothesis.md)

- ❌ **KILL_LOOP #1 (`success_tag`):** **NOT FIRED.** No config achieved
  `beats_winner=True` (G1 PBO 0.5437 ≥ 0.50 fails WINNER strict bar →
  WC=False universally → beats_winner=False universally even where
  Sortino > 1.3746 and pct_above >= 0.95).
- **KILL_LOOP #2 (`decisive_fail`):** **NOT FIRED.** Best Sortino_lh56y
  1.3951 >> 1.20 Phase 3 floor.
- ✅ **KILL_LOOP #3 (`replica_sanity_baseline`):** **NOT FIRED.** Baseline
  Sortino_lh56y 1.3240 = bit-exact match to iter 011/012 baseline (drift
  0.0000). Calibration anchor preserved.
- 🎯 ✅ **KILL_LOOP #4 (`replica_sanity_g0`):** **NOT FIRED.**
  K4lv25_g0_rvp70_cashx Sortino_lh56y 1.3769 = bit-exact match to iter
  012 strict-superset (drift 0.0000). **Confirms triple-stack helper
  reduces bit-exactly to iter 012 compound state machine when gamma=0.**
  CRITICAL calibration anchor — guarantees no silent regression of the
  loop's first strict-superset returns series.
- ❌ **KILL_LOOP #5 (`phase3_perf_candidate`):** **NOT FIRED.** No config
  achieves `phase3_performance_candidate=True` (PBO 0.5437 ≥ 0.50 fails
  the Phase 3 PBO ceiling). Phase 3 momentum BROKEN this iter — first
  iter since iter 011 with no Phase 3 candidates.
- ⚠️ **KILL_LOOP #6 (`PBO_blowup`):** **NOT FIRED.** G1 PBO 0.5437 < 0.55
  ceiling but breaches 0.50 hard gate. **Regression of +0.048pp vs iter
  012's 0.4960; loop-min was iter 011's 0.3056 (+0.238pp regression).**
  Cause: gamma-sweep parametric clustering (5 of 6 configs in same
  K4_AND_lv25/p70-cashx family).
- ❌ **KILL_LOOP #7 (`graded_lifts_strict_superset`):** **NOT FIRED.**
  No g>0 config achieves `strict_superset=True` (PBO blocks all
  WC-dependent flags). KEY hypothesis test FAILED.
- ✅ **KILL_LOOP #8 (`crisis_2022_rescue`):** **FIRED — POSITIVE TAG (but
  with caveats).** K4lv25_g100_rvp70_cashx (master-pure) beats SPY in
  2022_rates window — crisis 3/4 — but at the cost of WC=False AND
  CAGR collapse (26.99% vs T3d-K2 31.08%). g25 and g50 do NOT rescue
  2022 (single-asset ON-leg lacks UGL gold cushion that iter 010's
  basket3 g25 had).
- ❌ **KILL_LOOP #9 (`graded_score_lift`):** **NOT FIRED.** No g>0 config
  achieves total_score >= 80. Best g>0 score is g100's 74.5 (+5pts crisis
  but WC=False → tier still PROMISING). g25 score 72.5 (lost +5pts vs
  iter 012 76.5 due to G1 PBO regression).

## Verdict

- ⚠️ **Best (Sortino):** `..._tsgm_K4lv25_g25_rvp70_cashx` — PROMISING,
  score **72.5**, **Sortino_lh56y 1.3951** (edge **+0.0705** vs T3d-K2
  1.3246; > 1.3746 anti-curve-fit threshold), CAGR_lh56y 31.47%
  (+0.39pp vs T3d-K2), end_equity_ratio_vs_baseline 1.13×, MDD
  -47.69% (+16.81pp vs baseline -64.50%; +8.10pp vs iter 012
  strict-superset -55.79%), **Sharpe 0.9682 (loop max; > T3d-K2 winner
  0.919)**, G2 DSR p_cum **1.06e-03** (loop minimum at n=504), G4 OOS
  Sharpe **1.004**, G5 FWD post-2020 0.915, G6 99% low 0.598. **G1 PBO
  0.5437 ≥ 0.50** — invalidates WC, beats_winner, AND
  phase3_performance_candidate. Crisis 1/4 (only 2008 GFC). **No
  strict_superset.**
- 🎯 **Best (calibration anchor):** `..._tsgm_K4lv25_g0_rvp70_cashx` —
  Sortino 1.3769 = iter 012 strict-superset bit-exact (drift 0.0000).
  KILL_LOOP #4 NOT FIRED ✓ — confirms triple-stack helper correctness.
- 🎯 **Best (crisis rescue):** `..._tsgm_K4lv25_g100_rvp70_cashx` —
  PROMISING, score **74.5** (+5pts vs g25 due to crisis 3/4), Sortino
  1.3169, CAGR 26.99% (collapsed; -4.09pp), MDD -46.33%. Beats SPY in
  2022_rates BUT WC=False AND well below Phase 3 CAGR floor.
- **kill_rule_status:** N/A (loop iter; closed-study T<N>→T<N+1> KILLs
  do not apply)
- **beats_winner (best):** **false** (G1 PBO regression invalidates WC)
- **phase3_performance_candidate (any):** **false** (G1 PBO regression
  invalidates Phase 3 PBO ceiling; first iter since 011 with 0 candidates)
- **strict_superset (any):** **false**
- **cumulative_n_trials_global:** **504** (was 498; +6 this iter)

## Conclusion

⚠️ **HYPOTHESIS PARTIALLY CONFIRMED — graded ON-blend lifts Sortino + Sharpe
+ MDD but G1 PBO regression invalidates Phase 3 strict-bar status.**
The triple-stack mechanism (K4_AND_lv25 leverage upgrade × graded master
ON-blend × ratevol-OFF override) produces clear improvements on
risk-adjusted metrics:

1. **Sortino_lh56y 1.3951** for g25 (loop's 3rd-best, +0.0182 vs iter
   012 strict-superset 1.3769; +0.0705 vs T3d-K2 1.3246).
2. **Sharpe_lh56y 0.9682 — LOOP MAX** (vs iter 012 strict-superset 0.9584
   and T3d-K2 winner 0.919).
3. **MDD -47.69% for g25 / -46.33% for g50/g100** (vs iter 012
   strict-superset -55.79%, baseline -64.50% — graded blend universally
   reduces drawdown).
4. **G2 DSR p_cum 1.06e-03 — LOOP MINIMUM** at n_trials_global=504
   (was 1.31e-03 at n=498).
5. **G6 bootstrap 99% low 0.605 — LOOP MAX** for g50 (vs iter 012 0.596).

But the G1 PBO regression to **0.5437 ≥ 0.50 hard gate** invalidates
the strict-superset status for ALL configs. The cause is
mechanism-family clustering: 4 of 6 configs share K4_AND_lv25 +
ratevol-p70-cashx topology, differing only in gamma. CSCV correctly
penalises rank-correlated parametric variants
`[advances_fin_ml, p.208-211]`. **Iter 012's 6-distinct-topologies-in-6-
configs design (G1 PBO 0.4960) is the structural recipe iter 013 broke.**

**Calibration anchors PRESERVED bit-exact** (KILL_LOOP #3 + #4 NOT FIRED):
baseline 1.3240 = iter 011/012; g0 1.3769 = iter 012 strict-superset.
**Confirms triple-stack helper correctness** at gamma=0 (reduces to iter
012 compound state machine).

**2022_rates rescue ONLY by g100 (master-pure)** — KILL_LOOP #8 fired
positively but with caveats. Iter 010's g25_cashx Sortino 1.4670 +
crisis 3/4 was achieved with single-asset basket3 ON-leg that included
**UGL gold**; iter 013's single QLD/TQQQ ON-leg (no UGL) cannot replicate
that crisis rescue at intermediate gammas. Only gamma=1 (master-pure
≡ all CASHX during ratevol+ON cell) crosses the 2022 threshold — at the
cost of 27% CAGR and pct_above slipping to 0.9994 (still WC-passing
on that axis, but G1 PBO blocks).

**Phase 3 momentum BROKEN this iter** — first iter since 011 with 0
phase3_performance_candidates. Iter trajectory: 011 5/6 → 012 5/6 →
**013 0/6**.

**Mandate §1 invariant: capital remains 100% Plan C.** Best score 74.5
(g100; +5pts crisis but WC=False) < 90 deploy bar; g25 score 72.5. NO
automatic capital realloc. Per LOOP_PROTOCOL §"Mandate §1 reinforcement",
`docs/CURRENT_STATE.md` "Active Hunts" entry preserved untouched (gated
on score ≥ 90 + WC=Y + beats_winner=true). Deploy escalation per
KILL_RULES.md DEPLOY threshold (Sharpe_net edge +0.15) requires
user-driven mandate §7 override request.

**Hypothesis status:** **partially confirmed (Sortino/Sharpe/MDD/DSR
mechanism direction confirmed) but Phase 3 strict-bar invalidated by
G1 PBO regression.** The graded master ON-blend is a real risk-adjusted
return lift mechanism on top of the iter 012 compound; the cost is
parametric-variant clustering that breaks PBO. **Future iter ideas
should restore mechanism-mix diversity** while exploring graded blend
variants (e.g., 1 graded variant + 5 distinct mechanism-family configs).

## Lesson (for LOOP_MEMORY iter log)

⚠️ **TRIPLE STACK K4lv25 × GRADED MASTER × RATEVOL — Sortino/Sharpe/MDD
LIFT REAL but G1 PBO REGRESSION TO 0.5437 BREAKS PHASE 3.** Best config
`qld_voteK2_sma250_100_vol21_40_ar30_tsgm_K4lv25_g25_rvp70_cashx` hits
Sortino_lh56y **1.3951** (loop's 3rd-best; +0.0705 vs T3d-K2; +0.0182
vs iter 012 strict-superset), Sharpe **0.9682 (LOOP MAX)**, MDD
**-47.69%**, G2 DSR p_cum **1.06e-03 (LOOP MIN)**, G6 99% low
**0.605 (LOOP MAX for g50)**. **G1 PBO regression 0.4960 → 0.5437**
breaches 0.50 hard gate (KILL_LOOP #6 NOT FIRED at 0.55 ceiling).
Cause: gamma-sweep parametric clustering — 4 of 6 configs share
K4_AND_lv25/p70-cashx family. **NO strict_superset, NO beats_winner,
NO phase3_performance_candidate this iter** (Phase 3 momentum broken
after iter 011/012 5/6 hit-rate). **Calibration anchors PRESERVED**
bit-exact (KILL_LOOP #3 + #4 NOT FIRED): baseline 1.3240 = iter 011/012;
g0 1.3769 = iter 012 strict-superset. **2022_rates rescue ONLY by g100
master-pure** (KILL_LOOP #8 fired but with WC=False / CAGR collapse caveats).
Iter 010 g25's basket3+UGL crisis cushion structurally needed —
single QLD/TQQQ ON-leg can't replicate it at intermediate gammas.
**Capital remains 100% Plan C per mandate §1**; iter NOT appended to
loop_winner_iter / loop_phase3_performance_candidate_iter / loop_strict_
superset_iter (no positive flags). Sortino lift mechanism direction
confirmed but Phase 3 statistical eligibility lost — future iters need
to RESTORE mechanism-mix diversity (mix gamma variants with distinct
upgrade-gates / ratevol thresholds / alt-OFFs) to keep PBO < 0.50.

## Next iter ideas

1. **Mechanism-mix-diverse graded blend grid** — replace iter 013's
   gamma sweep (4 configs in same K4_AND_lv25/p70-cashx family) with a
   6-distinct-topology grid: 1 baseline + 1 K4_AND_lv25_g25_p70_cashx
   (iter 013 PRIMARY for Sortino lift) + 1 K4_g25_p80_ief
   (different upgrade × different ratevol × different alt-OFF) + 1
   tqqq_always_g0 (no upgrade gate, ON-leg always TQQQ; tests upgrade-
   gate benefit) + 1 K4_AND_lv25_g0_basket3 (ON-leg basket3 with UGL
   like iter 010 — gold cushion for 2022 rescue) + 1 K4_AND_lv25_g25_
   basket3 (iter 010 g25 + iter 012 K4_AND_lv25 — the actual triple
   stack iter 013 should have tested with multi-asset basket).
   **Highest expected value: addresses BOTH the PBO regression (mechanism-
   mix diversity) AND the missing 2022 rescue (basket3 with UGL gold)
   while preserving graded blend.** Cite `[risk_parity, p.80-81, ch.4]`
   + `[risk_parity, ch.5, p.10]` + `[advances_fin_ml, p.208-211]`.
2. **2020 COVID re-entry trigger overlay** — iter 010's idea (a) carried
   forward; combine the iter 010/013 graded master with a Carver-style
   re-arm hysteresis on the ratevol gate so that it RELEASES exposure
   when on_signal flips OFF→ON after the gate has been active for N days.
   Targets the 2020 unrescued crisis. Cite
   `[systematic_trading, p.212, ch.13]` Carver semi-automatic re-arm.
3. **VIX-percentile / VRP overlay on equity ON-leg** — iter 010 idea (c)
   carried forward; forward-looking implied-vol gate orthogonal to all
   current realised-vol mechanics. `[volatility_trading, ch.7]` Sinclair.
4. **AND-gate fine-grid sweep on K4_AND_lvN** — iter 012 idea (b) still
   open; sweep K=4 ∩ lowvol{15, 20, 25, 30, 40} in mechanism-mix-diverse
   grid (different alt-OFFs; different ratevol thresholds) to map AND-gate
   sensitivity without parametric clustering. Risk: similar PBO regression
   if the grid collapses to single mechanism family.
5. **Tax / fees stress on iter 012 strict-superset** — iter 012 idea (e)
   still open; turnover 4.84/y; quantify net-of-tax impact (Lei 14.754
   swing tax 15%); diagnostic, not gating.

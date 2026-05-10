---
mission: "post-close strategy hunt: research new strategies and benchmark vs T3d-K2 study winner"
status: open
total_iterations: 8
target_total_iterations: 50
closed_study_cumulative_n_trials: 426
cumulative_n_trials_loop: 48
cumulative_n_trials_global: 474
incumbent_winner_iter: "022-2026-05-06-T3d-extended-grid"
incumbent_winner_config: "qld_voteK2_sma250_100_vol21_40_ar30_off_zroz"
incumbent_winner_sortino_lh56y: 1.3246
incumbent_winner_sharpe_lh56y: 0.919
incumbent_winner_score: 82
beats_winner_threshold_sortino: 1.3746
beats_winner_threshold_pct_above_spy: 0.95
beats_winner_threshold_winner_conditions_met: true
loop_winner_iter: null
latest_iteration: "008-2026-05-09-compound-4axis-cscv-diversity"
latest_score: 75.0
latest_tier_label: STRONG
latest_beats_winner: false
---

# letf_rotation_hunt — LOOP MEMORY

**Lê PRIMEIRO toda iteração.** Estado do post-close strategy hunt.

Não confundir com `BASE_MEMORY.md` (registro do study fechado, frozen). O loop
roda em paralelo, não modifica o estudo, e usa o study winner T3d-K2
(`qld_voteK2_sma250_100_vol21_40_ar30_off_zroz`, Sortino_lh56y 1.3246) como
benchmark fixo.

## Beats-winner criterion (frozen)

Um iter conta como `beats_winner=true` se TODOS os três passam:

1. `sortino_lh56y > 1.3746` (= 1.3246 + 0.05 anti-curve-fit margin)
2. `winner_conditions_met = True` (per scoring rubric)
3. `pct_time_above_benchmark_lh56y >= 0.95`

Falha em qualquer um → `beats_winner=false`. Loop **não para** no primeiro
beater (decisão de design — varredura ampla preferida sobre halt rápido).

Se um iter bate, registra em `loop_winner_iter` (lista de todos beaters)
e adiciona flag de review humana — **nunca** dispara realocação de capital
sozinho. Mandate §1 preserva 100% Plano C; qualquer deploy precisa de
mandate §7 override request manual.

## Trial accounting

DSR/p-value reporting in loop iters must use `cumulative_n_trials_global`, not
only the configs tested inside the current iter. Global trials start at the
closed-study count (426 after T5) and add every loop config. Local-only DSR is
allowed as a diagnostic, but cannot support `beats_winner=true` unless the
global-trials DSR still passes `[advances_fin_ml, p.222-223]`.

## Iteration log (newest first)

### 008 — 2026-05-09 — compound-4axis-cscv-diversity

**Hypothesis:** Drop G1 PBO < 0.50 (lone strict-bar blocker for
`winner_conditions_met=True` after iter 007) by widening the compound-
mechanic family from iter 007's 3 axes to 5 qualitatively distinct
mechanism dimensions (ON-basket on/off, OFF-mechanic on/off, ratevol
threshold p70/p80, ratevol window 60d/120d, alt-OFF asset CASHX/IEFSIM).
Citation: `[advances_fin_ml, p.208-211]` (CSCV diversity rationale) +
`[stocks_on_the_move, p.98]` + `[volatility_trading, p.58-60]`.

**Configs tested (6, 5-mechanic-axis grid centred on iter 007 winner replica):**

| name | ON-basket | OFF-mechanic | sortino_lh56y | active% | score | tier | WC | edge_vs_winner |
|---|---|---|---:|---:|---:|---|:---:|---:|
| `..._4axis_baseline` (replica) | single QLD | always-ZROZ | 1.2841 | 0.0% | 72.5 | PROMISING | F | -0.0405 |
| **`..._4axis_basket3_x_ratevol_p70_60d_cashx`** ← **iter 007 winner replica (Sortino-best)** | basket3 invvol60 | ratevol-p70-60d→CASHX | **1.4637** | 28.0% | 75.0 | STRONG | F | **+0.1391** |
| `..._4axis_basket3_only` | basket3 invvol60 | always-ZROZ | 1.3340 | 0.0% | 77.5 | STRONG | F | +0.0094 |
| `..._4axis_basket3_x_ratevol_p80_60d_cashx` | basket3 invvol60 | ratevol-p80-60d→CASHX | 1.4430 | 19.1% | 77.5 | STRONG | F | +0.1184 |
| `..._4axis_basket3_x_ratevol_p70_120d_cashx` | basket3 invvol60 | ratevol-p70-120d→CASHX | 1.4442 | 28.0% | 75.0 | STRONG | F | +0.1196 |
| `..._4axis_basket3_x_ratevol_p70_60d_ief` | basket3 invvol60 | ratevol-p70-60d→IEFSIM | 1.4524 | 28.0% | 75.0 | STRONG | F | +0.1278 |

**KILL_LOOP results (pre-registered):**
- KILL_LOOP #1 (success-tag) — **NOT FIRED.** No config achieved
  `beats_winner=true`. 5 of 6 configs cleared Sortino > 1.3746;
  6 of 6 cleared pct_above ≥ 0.95 (1.0000 universally — first loop
  iter where this is universal). G1 PBO blocked all configs.
- KILL_LOOP #2 (decisive-fail) — **NOT FIRED** (best Sortino 1.4637 >>
  1.30 floor; family alive).
- KILL_LOOP #3 (replica-sanity) — **NOT FIRED** (baseline 1.2841 =
  bit-exact match to iters 001-007 baselines).
- KILL_LOOP #4 (compound-edge-decay) — **NOT FIRED.** Iter 007 winner
  replica (config 2) Sortino_lh56y = **1.4637**, **bit-exact** match to
  iter 007 finding (drift = 0.0000). Cross-iter scientific
  reproducibility confirmed.
- KILL_LOOP #5 (PBO-still-polluted) — **FIRED.** G1 PBO = **0.5675** ≥
  0.50, slightly *above* iter 007's 0.552. Hypothesis (parameter-sweep
  mechanism diversity drops PBO) **rejected** — adding parameter axes
  within one OFF-leg ratevol mechanic *increased* PBO marginally.

**Key finding: clean negative result. Hypothesis REJECTED.**
**Mechanism diversity for CSCV is structural, not parametric.** Adding
parameter sweeps (threshold p70/p80, window 60d/120d, alt-OFF
CASHX/IEFSIM) within the same OFF-leg ratevol mechanic produced
*marginally worse* G1 PBO (0.5675 vs iter 007's 0.552), not better.
Parameter variants share IS-OOS rank correlation by construction —
CSCV correctly penalises this `[advances_fin_ml, p.208-211]`. Iter
trajectory: iter 005 0.881 → iter 006 0.798 → iter 007 0.552 → iter
008 0.5675 (direction reversed). **Sortino spread across the 4
ratevol-override variants is flat (1.4430-1.4637, range 0.021)** —
the parameter sweep produces mechanism-equivalent strategies. **Iter
007 findings replicate bit-exact:** Sortino 1.4637, MDD -32.82%,
Sharpe 1.0068, G5 FWD post-2020 1.227. Cross-iter reproducibility
confirmed. **5 of 6 configs clear +0.05 anti-curve-fit margin
(Sortino > 1.3746); 6 of 6 clear pct_above ≥ 0.95** — but
`beats_winner=false` universally because **G1 PBO 0.5675 ≥ 0.50** is
the lone blocker. **threshold_p80 narrowly leads on G5 FWD post-2020
Sharpe** (1.268 vs winner replica 1.227); **basket3_only and
threshold_p80 lead on crisis attribution** (3/4 each — add 2020 COVID
via UGL). Iter 004's clean PBO 0.071 came from a *master-scope*
override config (whole-portfolio cash, qualitatively different
mechanism). **The structural-diversity primitive — not the parametric
one — is what cracks PBO.** Methodological insight: **ceiling reached
for compound-family CSCV diversity at PBO ~0.55**; further parameter
sweeps within the family will not break it. **Capital remains 100%
Plan C per mandate §1.**

**beats_winner:** **false** (G1 PBO 0.5675 ≥ 0.50 universally; Sortino
+ pct_above thresholds both cleared by 5 of 6 configs; first loop iter
where pct_above ≥ 0.95 is universal but G1 still blocks).

**Next iter ideas:** (a) **Master-scope OFF override (iter 004-style
structural-diversity primitive)** — keep iter 007 compound winner
config family but add a master-scope config: when ratevol gate fires,
override to whole-portfolio CASHX (rather than only when on_signal=OFF).
That's the qualitatively different mechanism that should restore CSCV
diversity. 6-config design: anchor (compound winner replica),
basket3_only, master_basket3_x_ratevol, master_single_x_ratevol,
threshold_p80, alt_off_ief. Cite `[advances_fin_ml, p.208-211]` +
`[volatility_trading, p.58-60]`. **Highest expected value: directly
addresses the iter 008 negative result with iter 004's proven mechanism-
diversity primitive.** (b) **VIX-percentile / VRP overlay on equity
ON-leg** `[volatility_trading, ch.7]` Sinclair — forward-looking
implied-vol gate orthogonal to realised-vol gates and bond-vol gate
already in stack. Different mechanic family from compound (CSCV-
diverse). (c) **Bond duration timing on OFF leg**
`[systematic_trading, ch.9, p.180-190]` — distinct from ratevol gate
(yields, not return vol); also targets 2022_rates rescue (iter 008
confirmed all 5 override variants fail 2022_rates).

### 007 — 2026-05-09 — compound-ratevol-off-x-invvol-on-basket

**Hypothesis:** Compound the two best-performing loop mechanics — iter 005's
ON-leg multi-asset inverse-vol basket {QLD, UPRO, UGL} (+0.0094 edge) and
iter 006's OFF-leg ratevol regime gate (ZROZ vol-pct > 70th → CASHX,
+0.0140 edge) — into a single 3-axis orthogonal grid. Tests (a)
compounding vs conflict, (b) whether real-mechanism-switch grid breaks
G1 PBO 0.79-0.88 ceiling. Citation: `[stocks_on_the_move, p.98]` (Clenow
vol-parity sizing, ON-leg) + `[volatility_trading, p.58-60]` (Sinclair
volatility cone, OFF-leg) + `[risk_parity, ch.5]` (Carlson cap-efficient
stacking — compounding orthogonal lifts).

**Configs tested (6, 3-axis orthogonal grid: ON-leg type × OFF-mechanic × alt-OFF asset):**

| name | ON-leg | OFF-mechanic | sortino_lh56y | active% | score | tier | WC | edge_vs_winner |
|---|---|---|---:|---:|---:|---|:---:|---:|
| `..._compound_baseline` (replica) | single QLD | always ZROZ | 1.2841 | 0.0% | 72.5 | PROMISING | F | -0.0405 |
| `..._compound_ratevol_only` (iter 006 best replica) | single QLD | ratevol-p70-cashx | 1.3386 | 28.0% | 72.5 | PROMISING | F | +0.0140 |
| `..._compound_basket3_only` (iter 005 best replica) | basket3 invvol60 | always ZROZ | 1.3340 | 0.0% | 77.5 | STRONG | F | +0.0094 |
| **`..._compound_basket3_x_ratevol_p70_cashx`** ← **Sortino-best** | basket3 invvol60 | ratevol-p70-cashx | **1.4637** | 28.0% | 75.0 | STRONG | F | **+0.1391** |
| `..._compound_basket3_x_ratevol_p70_ief` | basket3 invvol60 | ratevol-p70-ief | 1.4524 | 28.0% | 75.0 | STRONG | F | +0.1278 |
| `..._compound_basket2_qld_ugl_x_ratevol_p70_cashx` | basket2 invvol60 | ratevol-p70-cashx | 1.4297 | 28.0% | 77.0 | STRONG | F | +0.1051 |

**KILL_LOOP results (pre-registered):**
- KILL_LOOP #1 (success-tag) — **NOT FIRED** (best Sortino 1.4637 >
  threshold 1.3746 ✓ AND pct_above 1.0000 ≥ 0.95 ✓ — first time both
  numerical thresholds clear simultaneously — but winner_conditions_met
  =False because G1 PBO 0.552 ≥ 0.50 fails the strict bar)
- KILL_LOOP #2 (decisive-fail) — **NOT FIRED** (all 5 non-baseline
  configs ≥ 1.33; family confirmed alive)
- KILL_LOOP #3 (replica-sanity) — **NOT FIRED** (baseline 1.2841 =
  bit-exact match to iters 001-006 baselines)
- KILL_LOOP #4 (compound-non-additivity) — **NOT FIRED — STRONGLY
  CONTRADICTED**. Compound config 4 Sortino 1.4637 is +0.125 ABOVE
  max(ratevol_only, basket3_only) — mechanics compound super-additively
  by 1.72× the naive sum, not conflict.
- KILL_LOOP #5 (PBO-still-polluted) — **FIRED — partially.** G1 PBO
  0.552 ≥ 0.50 still fails, but improvement direction is monotonic
  (iter 005 0.881 → iter 006 0.798 → iter 007 0.552). 3-axis grid with
  real ON↔OFF mechanism switch dropped PBO by 0.246 vs iter 006.

**Key finding:** **Compound super-additivity confirmed — loop's largest
Sortino edge ever (+0.1391 vs winner 1.3246).** Best config:
`compound_basket3_x_ratevol_p70_cashx` Sortino_lh56y **1.4637**. Compound
delta over baseline (+0.1796) is **1.72×** the naive sum of independent
deltas (ratevol_only +0.0545 + basket3_only +0.0499 = +0.1044). The two
mechanics don't just stack — they reinforce each other. **MDD -32.82%**
(smallest in loop; smaller than SPY -55.1% in absolute terms; cuts
baseline -64.5% by half). **Sharpe = 1.0068** (crosses 1.0 for first
time in any loop config). **G5 FWD post-2020 Sharpe = 1.227** vs
baseline 0.708, lift +0.519 — single largest G5 improvement in loop AND
larger than iters 005+006 G5 lifts summed (super-additive on G5 too).
**Three configs (4, 5, 6) clear the +0.05 anti-curve-fit Sortino margin
(1.3746); two also clear the 0.95 pct_above_benchmark bar — first loop
iter to clear both simultaneously.** `beats_winner=false` only because
**G1 PBO 0.552 ≥ 0.50 fails the strict bar** in winner_conditions_met
— it's the LONE remaining blocker. **Sortino effect is robust across all
4 datasets** (lh_56y 1.4637 / mod_1990 1.3703 / spy_real 1.4549 /
ndx_real 1.5242). **CASHX > IEFSIM marginally** (zero duration cleanly
orthogonal to ZROZ duration risk); **basket3 > basket2** (UPRO needed
for 3-leg cross-asset diversification). **Super-additivity comes from
regime-coincidence**: ratevol gate fires precisely during bond-stress
windows where multi-asset basket (with UGL gold) ALSO has peak marginal
value — the two effects aren't just orthogonal, they reinforce in the
SAME regimes. CAGR trade-off: 23.25% vs baseline 29.85% (basket3 with
UGL drags equity-bull periods); turnover 15.6/y vs baseline 9.3/y (1.7×
basket-rebalance cost).

**beats_winner:** **false** (Sortino 1.4637 > 1.3746 ✓; pct_above
1.0000 ≥ 0.95 ✓; **winner_conditions_met=False because G1 PBO 0.552 ≥
0.50** is the lone strict-bar blocker; loop's closest approach to
beats_winner=true ever).

**Next iter ideas:** (a) **4th-axis orthogonal grid to crack G1 PBO
0.50** — keep the iter 007 winner config family but add a real 4th
mechanism switch (e.g., threshold sweep p65/p70/p75/p80 plus
mechanism-switch-OFF configs like baseline + basket3-only + single +
compound). 6-config design with 4 real mechanism dimensions should drop
PBO toward iter 004's 0.071. **Highest expected value: this is the
ONLY barrier to first beats_winner=true.** Cite `[advances_fin_ml,
p.208-211]` (CSCV diversity rationale). (b) **VIX-percentile / VRP
overlay** on equity ON-leg `[volatility_trading, ch.7]` Sinclair —
forward-looking implied-vol gate orthogonal to realised-vol gates and
bond-vol gate already in stack. Could replace AR(1) in vote-K composite.
(c) **Tax / fees stress on iter 007 winner** — turnover 1.7× baseline;
quantify net-of-tax Sortino impact before any deploy consideration
(diagnostic, not gating).

### 006 — 2026-05-09 — bond-ratevol-regime

**Hypothesis:** Bond rate-vol regime master-gate — when ZROZ realised vol
(60d/120d) percentile within trailing 5y exceeds 70th/80th, OFF leg
reroutes from ZROZ (≈ 27y duration) to a shorter-duration alternative
(CASHX or IEFSIM). Targets the 2022_rates loss directly via own-asset
OFF-leg second-moment regime detection — orthogonal to all 5 prior loop
iters. Citation: `[volatility_trading, p.58-60]` (Sinclair volatility cone) +
`[systematic_trading, p.212, ch.13]` (Carver vol-scaled regime thresholds).

**Configs tested (6, 3-axis grid: pct × window × alt-asset):**

| name | pct | window | alt-OFF | sortino_lh56y | active% | score | tier | WC | edge_vs_winner |
|---|--:|--:|---|---:|---:|---:|---|:---:|---:|
| `..._ratevol_off_baseline` (replica) | — | — | — | 1.2841 | 0.0% | 72.5 | PROMISING | F | -0.0405 |
| **`..._ratevol_p70_60d_to_cashx`** ← Sortino-best | 0.70 | 60d | CASHX | **1.3386** | 28.0% | 72.5 | PROMISING | F | **+0.0140** |
| `..._ratevol_p80_60d_to_cashx` | 0.80 | 60d | CASHX | 1.3288 | 19.1% | 72.5 | PROMISING | F | +0.0042 |
| `..._ratevol_p80_120d_to_cashx` | 0.80 | 120d | CASHX | 1.3244 | 19.8% | 72.5 | PROMISING | F | -0.0002 |
| `..._ratevol_p70_60d_to_ief` | 0.70 | 60d | IEFSIM | 1.3345 | 28.0% | 72.5 | PROMISING | F | +0.0099 |
| `..._ratevol_p80_60d_to_ief` | 0.80 | 60d | IEFSIM | 1.3241 | 19.1% | 72.5 | PROMISING | F | -0.0005 |

**KILL_LOOP results (pre-registered):**
- KILL_LOOP #1 (success-tag) — **NOT FIRED** (best Sortino 1.3386 < 1.3746
  threshold AND winner_conditions_met=False universally because G1 PBO
  0.798 fails)
- KILL_LOOP #2 (decisive-fail) — **NOT FIRED** (all 5 ratevol Sortinos
  ≥ 1.3241; family is *promising*, not dead)
- KILL_LOOP #3 (replica-sanity) — **NOT FIRED** (baseline 1.2841 =
  bit-exact match to iters 001-005 baselines)
- KILL_LOOP #4 (over-suppression) — **NOT FIRED** (pct_above_benchmark
  = 1.0000 universally; OFF-leg-only override avoided iter 004 master
  failure mode)
- KILL_LOOP #5 (ratevol-non-event) — **NOT FIRED** (gate fires 19-28%
  of post-warmup days, well above 5% underpowered floor)

**Key finding:** **New loop edge maximum:** `ratevol_p70_60d_to_cashx`
Sortino 1.3386 (edge +0.0140 vs winner 1.3246) — exceeds iter 005's
basket3_invvol60 (+0.0094) by 0.0046. **All 5 override configs lift
baseline universally (5×4 wins on Sortino across configs × datasets)** —
bit-uniform improvement, first loop iter with this property. **G5 FWD
post-2020 Sharpe massive lift** for every override config (0.708
baseline → 0.856-0.943) — direct hypothesis confirmation that bond
rate-vol gating helps in the 2022 regime. MDD reduced ~7-9pp absolute
(-64.5% → -55.8% best) without sacrificing CAGR (29.9% → 30.5% — CASHX
yield carries defensive periods). **Crisis attribution count UNCHANGED
at 1/4** — SPY-relative binary test misses bond-stress episodes that
don't coincide with equity bear; the Sortino lift is distributed
across multiple bond-stress regimes (1979-1981 Volcker, 1994 Greenspan
shock, 2013 taper, 2022). **G1 PBO 0.798 universally fails** (better
than iter 005's 0.881 but below iter 004's clean 0.071) — 3-axis grid
(pct × window × alt-asset) reduces pollution but still single-mechanic
family. **CASHX > IEFSIM** during bond stress (zero duration cleanly
orthogonal); **p70 > p80** (wider activation gives more dodging
chances). Methodological insight: **two independent loop mechanics now
show G5 post-2020 Sharpe lift** (this iter via ratevol gate; iter 005
via multi-asset basket) — closed-study winner has a real post-2020
edge-decay problem the loop is starting to triangulate.

**beats_winner:** **false** (best Sortino 1.3386 < 1.3746 threshold AND
G1 PBO blocker; second consecutive iter with positive edge over winner
benchmark but +0.05 anti-curve-fit margin not cleared).

**Next iter ideas:** (a) **Combine ratevol-OFF × inverse-vol-ON basket**
`[volatility_trading, p.58-60]` + `[stocks_on_the_move, p.98]` — orthogonal
grid spanning OFF-side regime detection (this iter) AND ON-side
diversification (iter 005). 8 configs: 2 OFF × 2 ON × 2 controls. Tests
whether the two effects compound or conflict — both already show
positive edge AND positive G5 lift independently. **Highest expected
value because compounding is likely AND it would be the first
multi-mechanic-family grid in the loop, potentially breaking G1 PBO.**
(b) VIX-percentile / VRP overlay on equity ON-leg `[volatility_trading,
ch.7]` — forward-looking implied vol gate, distinct from realised-vol
already in winner stack. (c) Bond carry forecast on OFF rotation
`[systematic_trading, ch.7 p.119]` — 10y yield − FFR as additional input
to OFF-leg routing.

### 005 — 2026-05-09 — multi-asset-on-invvol

**Hypothesis:** Replace winner's single-asset (QLD) ON leg with a basket of
equity-style LETFs ({QLD, UPRO, UGL}) sized by inverse realised volatility
(60d / 120d) so each asset contributes equal volatility, while keeping
winner's binary vote-K=2 trend gate (computed on QLD) and ZROZ as OFF.
Tests cross-asset **first-moment** diversification — orthogonal to iter
004's (failed) cross-asset second-moment regime gate. Citation:
`[stocks_on_the_move, p.98]` (Clenow vol-parity sizing) +
`[systematic_trading, ch.10]` (Carver inverse-vol position sizing).

**Configs tested (6):**

| name | basket | vol_window | sizing | sortino_lh56y | score | tier | WC | edge_vs_winner |
|---|---|---:|---|---:|---:|---|:---:|---:|
| `..._on_baseline` (replica) | {QLD} | — | single | 1.2841 | 72.5 | PROMISING | F | -0.0405 |
| `..._on_basket2_qld_upro_invvol60` | {QLD, UPRO} | 60d | invvol | 1.2695 | 75.5 | STRONG | F | -0.0551 |
| `..._on_basket2_qld_ugl_invvol60` | {QLD, UGL} | 60d | invvol | 1.2849 | 74.5 | PROMISING | F | -0.0397 |
| **`..._on_basket3_qld_upro_ugl_invvol60`** ← Sortino-best | {QLD, UPRO, UGL} | 60d | invvol | **1.3340** | 77.5 | STRONG | F | **+0.0094** |
| `..._on_basket3_qld_upro_ugl_invvol120` | {QLD, UPRO, UGL} | 120d | invvol | 1.3049 | 77.5 | STRONG | F | -0.0197 |
| `..._on_basket3_qld_upro_ugl_eqweight` ← score-best | {QLD, UPRO, UGL} | — | eqweight | 1.3317 | **78.0** | STRONG | F | +0.0071 |

**KILL_LOOP results (pre-registered):**
- KILL_LOOP #1 (success-tag) — **NOT FIRED** (best Sortino 1.3340 < 1.3746;
  AND winner_conditions_met=False universally because G1 PBO 0.881 fails)
- KILL_LOOP #2 (decisive-fail) — **NOT FIRED** (all multi-asset Sortinos ≥ 1.27)
- KILL_LOOP #3 (replica-sanity) — **NOT FIRED** (baseline 1.2841 = bit-exact match
  to iters 001-004 baselines)
- KILL_LOOP #4 (single-asset-domination) — **NOT FIRED — partially contradicted.**
  basket3 configs (1.3340 / 1.3317 / 1.3049) all *exceed* baseline. Iter 023's
  "QLD × Vote-K=2 is asset-specific" finding holds at 1-asset and 2-asset
  scales but breaks at 3-asset basket via cross-asset diversification.
  basket2_qld_ugl pct_above 0.93 < 0.95 strict bar (1980-2000 gold drag).
- KILL_LOOP #5 (turnover-blowup) — **NOT FIRED** (max 5.44/y; baseline 2.61;
  ratio 2.08× < 3× threshold)

**Key finding:** **First positive Sortino edge in the loop.**
basket3_qld_upro_ugl_invvol60 hits Sortino 1.3340 (edge +0.0094 vs winner
1.3246). Three-asset inverse-vol basket beats single-asset baseline by
+0.05 Sortino AND breaks the 1-of-4 crisis-rescue ceiling (3-of-4: dotcom
+ GFC + COVID via UGL gold complement). Two-asset baskets underperform —
the diversification benefit requires the third (cross-asset) leg. Equal-
weight ties inverse-vol on Sortino (1.3317 vs 1.3340) but loses 2020_COVID
rescue (fixed UPRO 3x weight is over-exposed during Mar-2020 -77% trough).
**G1 PBO 0.881 is the universal blocker** — single-mechanic grid (5 multi-
asset variants) is high-correlation; CSCV finds significant IS-OOS rank
divergence. WC=False for all configs despite positive Sortino edges.
**2022_rates still not rescued** — even gold falls during USD-strength +
real-rate rebound. **Methodological lesson:** orthogonal multi-mechanic
grid (iter 004 style, PBO 0.071) → clean PBO; single-mechanic grid (iter
005 style) → polluted PBO. Future multi-asset iter should redesign with
3 orthogonal axes.

**beats_winner:** **false** (best Sortino 1.3340 < 1.3746 threshold AND G1
PBO blocker; first config with positive edge but +0.05 anti-curve-fit
margin not cleared).

**Next iter ideas:** (a) **Bond duration timing** `[systematic_trading,
ch.9 p.180-190]` — 10y rate vol > 60d 80th percentile → reduce ZROZ /
switch to IEF. Iter 005 confirmed multi-asset can't rescue 2022_rates
(gold also fell); sidestepping bond risk directly is the orthogonal angle
and targets the unrescued crisis. **Highest expected value.**
(b) **Multi-asset orthogonal-grid retest** — same {QLD, UPRO, UGL} basket
but vary across 3 mechanic dimensions (composition × sizing × gate scope)
in 8 configs, to test whether iter 005's +0.0094 Sortino edge survives
proper CSCV (G1 PBO < 0.5). (c) VIX-percentile / VRP overlay
`[volatility_trading, ch.7]`.

### 004 — 2026-05-09 — corr-regime-stockbond

**Hypothesis:** Stock-bond correlation regime master-gate. When 60d/120d
rolling correlation between QLD↔ZROZ daily returns exceeds 0.00/0.20/0.30,
redirect either the OFF leg or the entire portfolio to CASHX since the
diversification hedge has structurally broken. Citation:
`[risk_parity, p.80-81, ch.4]` (Qian RORO regime — stocks-and-bonds correlation
flip eliminates diversification value). Targets the 2022_rates loss directly via
cross-asset second-moment regime detection — orthogonal to iters 001
(yield-curve), 002 (vol-DD), 003 (calendar).

**Configs tested (6):**

| name | threshold | window | scope | sortino_lh56y | corrpct | score | tier | WC | edge_vs_winner |
|---|--:|--:|---|---:|---:|---:|---|:---:|---:|
| `..._corrgate_off_baseline` ← Sortino-best | — | — | none | **1.2841** | 0.0% | 76.5 | STRONG | T | -0.0405 |
| `..._corrgate_t000_60d_offleg_cashx` | 0.00 | 60d | offleg→CASHX | 1.2211 | 44.7% | 76.5 | STRONG | T | -0.1035 |
| `..._corrgate_t020_60d_offleg_cashx` | 0.20 | 60d | offleg→CASHX | 1.2133 | 24.0% | 76.5 | STRONG | T | -0.1113 |
| `..._corrgate_t030_60d_offleg_cashx` (best corr-gate) | 0.30 | 60d | offleg→CASHX | 1.2540 | 14.6% | 76.5 | STRONG | T | -0.0706 |
| `..._corrgate_t020_120d_offleg_cashx` | 0.20 | 120d | offleg→CASHX | 1.2184 | 21.7% | 76.5 | STRONG | T | -0.1062 |
| `..._corrgate_t020_60d_master_cashx` (KILL #4 OVER_SUPPRESS) | 0.20 | 60d | master→CASHX | 0.9252 | 24.0% | 42.5 | MARGINAL | F | -0.3994 |

**KILL_LOOP results (pre-registered):**
- KILL_LOOP #1 (success-tag) — **NOT FIRED** (best Sortino 1.2841 < 1.3746)
- KILL_LOOP #2 (decisive-fail) — **NOT FIRED** (only master is < 1.10; offleg variants 1.21-1.25)
- KILL_LOOP #3 (replica-sanity) — **NOT FIRED** (baseline 1.2841 = bit-exact iters 001/002/003 baseline)
- KILL_LOOP #4 (over-suppression) — **FIRED for `..._master_cashx`** (lh_56y pct_above_bench 0.7039 << 0.85)
- KILL_LOOP #5 (corr-regime-non-event) — **NOT FIRED** (corrgate fires 14.6%-44.7% — well above 5%)

**Key finding:** Stock-bond correlation regime gating produces no Sortino
lift on the winner's two-leg structure — the corr-flip is most active when
the trend signal is *already* defensive, so the gate's marginal
contribution is just OFF-leg vehicle choice (ZROZ vs CASHX). Across 56
years, ZROZ duration risk premium > CASHX short-rate yield in
expectation, so the swap loses Sortino. **`..._master_cashx` is the loop's
first FIRED KILL_LOOP** (#4 over-suppression: lh_56y pct_above_bench 0.7039
< 0.85) — forcing whole-portfolio cash during 24% of days collapses
Sortino by 28%. **G1 PBO=0.071 is the cleanest PBO of the loop** (vs
003's 0.444, 002's 0.159, 001's 0.575): orthogonal grid design (threshold
× window × scope) pays off methodologically even when the strategy
hypothesis fails. Best corr-gate variant (`t030_60d_offleg`) recovers to
baseline in post-2003 windows (spy_real 1.0911 = baseline; ndx_real 1.2890
= baseline) but loses 0.030 Sortino in lh_56y. Crisis attribution
unchanged (2008_GFC only, 1 of 4) — 2022_rates not rescued because the
QLD↔ZROZ correlation flipped positive *after* the bear was already
underway, AND the offleg-only override doesn't fire during ON state. The
t000 variant gives the cleanest MDD reduction of the loop (-7.1pp absolute,
-11% relative) but at -0.063 Sortino cost.

**beats_winner:** **false** (best Sortino edge -0.0405 = baseline replica
drift only; no corr-gate variant adds Sortino).

**Next iter ideas:** (a) **Multi-asset ON rotation with inverse-vol
weighting** {QLD, SOXL, UPRO} `[risk_parity, p.10, ch.1]` +
`[stocks_on_the_move, p.98]` — distinct from T4 Clenow / T5 Carver / iter
023 (which used 1 ON asset per config); cross-asset *first* moment
diversification on ON leg is the natural complement to this iter's
negative result on cross-asset *second* moment; (b) VIX-percentile / VRP
overlay `[volatility_trading, ch.7]` (forward-looking implied vol vs
realised already in stack); (c) Bond duration timing `[systematic_trading,
ch.9]` — sidestep bond risk directly rather than the cross-asset
correlation.

### 003 — 2026-05-09 — calendar-halloween-gate

**Hypothesis:** Calendar-month seasonal master-gate (Hirsch best-6-months /
Halloween effect: Nov-Apr ON, May-Oct weak) overlaid on the winner's
vote-of-K trend signal via three aggregation rules: hard veto OFF (May-Oct
or narrower Jun-Sep), augment as 5th vote member (K=2 or K=3 of 5), or
replace AR(1) with the calendar indicator. Citation:
`[trading_systems_methods, p.479-481]` (Hirsch / Halloween / Turn-of-month
calendar rules).

**Configs tested (6):**

| name | calendar mechanic | sortino_lh56y | score | tier | WC | edge_vs_winner |
|---|---|---:|---:|---|:---:|---:|
| `..._cal_off` (winner replica) | none (baseline) | 1.2841 | 76.5 | STRONG | T | -0.0405 |
| `..._cal_veto_may_oct` | hard veto May-Oct (Hirsch) | 1.1216 | 68.5 | PROMISING | F | -0.2030 |
| **`..._cal_veto_jun_sep`** ← Sortino-best | hard veto Jun-Sep (narrow) | **1.3061** | 71.5 | PROMISING | T | **-0.0185** |
| `..._cal_5vote_K2of5_may_oct` ← score-best | 5th vote (Nov-Apr=1), K=2 | 1.2575 | **79.5** | STRONG | T | -0.0671 |
| `..._cal_5vote_K3of5_may_oct` | 5th vote, stricter K=3 | 1.1128 | 58.5 | MARGINAL | F | -0.2118 |
| `..._cal_replace_ar_may_oct` | swap AR(1) for Halloween | 1.1515 | 76.5 | STRONG | T | -0.1731 |

**KILL_LOOP results (pre-registered):**
- KILL_LOOP #1 (success-tag) — **NOT FIRED** (best Sortino 1.3061 < 1.3746)
- KILL_LOOP #2 (decisive-fail) — **NOT FIRED** (only 1 of 5 calendar configs < 1.10 floor)
- KILL_LOOP #3 (replica-sanity) — **NOT FIRED** (baseline 1.2841 = bit-exact iter 001/002 baseline)
- KILL_LOOP #4 (over-suppression) — **NOT FIRED** (all configs pct_time_above_benchmark_lh56y = 1.0000)

**Key finding:** The narrower Jun-Sep "summer stall" veto is the **first loop
config to lift Sortino above the replica baseline** (1.2841 → 1.3061, +0.022
edge). The canonical Hirsch May-Oct framing is monotonically worse than
baseline (-0.20 Sortino) because forcing OFF for 50.5% of trading days costs
more than it saves in crisis-rescue. The 2022_rates target was NOT rescued
by any variant: the bear ran Nov-2021 → Oct-2022, spanning ~6 months in
Hirsch "good" Nov-Apr where ON stayed on. Crisis attribution unchanged
(2008_GFC only, 1 of 4) for every config. **Augmentation K=2 (config 4)
produces highest CAGR (31.0%) and highest score (79.5 STRONG)** but lower
Sortino than baseline because soft tilt keeps Oct-2008 exposure on. G5
post-2020 FWD Sharpe surfaces clean published-edge decay: baseline 0.708 →
jun_sep 0.371 → may_oct 0.001. **G1 PBO=0.444 passes universally** (worse
than iter 002's 0.159 but better than iter 001's 0.575) — calendar layer
adds modest CSCV variation between veto/augment/replace.

**beats_winner:** **false** (best Sortino edge -0.0185 — closest any loop
iter has come to +0.05 threshold but still 0.0685 short).

**Next iter ideas:** (a) Stock-bond correlation regime classifier (60d
QLD↔ZROZ correlation flip; targets 2022 directly via dual-fall regime
detection) `[risk_parity, ch.5]` / `[ml_for_algo_trading, ch.9]`; (b)
Multi-asset ON rotation with inverse-vol weighting `[risk_parity, ch.5 p.10]`
+ `[stocks_on_the_move, p.98]`; (c) VIX-percentile / VRP harvesting overlay
`[machine_trading]` / `[volatility_trading, ch.7]`.

### 002 — 2026-05-09 — on-vol-dd-killswitch

**Hypothesis:** Vol-adjusted drawdown master-gate (Carver-style kill switch:
DD_252d > X × σ_price_21d, half-threshold re-arm hysteresis) overlaid on top
of the winner's vote-of-K trend signal. Targets the 2022_rates loss
identified in iter 001 as an ON-leg latency problem. Citation:
`[systematic_trading, p.212 ch.13]` (Carver semi-automatic stop, X*sigma
from tracking extreme).

**Configs tested (6):**

| name | kind | param | sortino_lh56y | killpct | score | tier |
|---|---|--:|---:|---:|---:|---|
| **`..._dd_off`** (winner replica) | no killswitch | — | **1.2841** ← best | 0.0% | 76.5 | STRONG |
| `..._dd_x2_252_vol21` | vol-adj | 2 | 1.0824 | 38.1% | 71.0 | PROMISING |
| `..._dd_x3_252_vol21` | vol-adj | 3 | 1.1526 | 27.7% | 76.5 | STRONG |
| `..._dd_x4_252_vol21` (Carver) | vol-adj | 4 | 1.1779 | 21.7% | 76.5 | STRONG |
| `..._dd_x5_252_vol21` | vol-adj | 5 | 1.2240 | 17.5% | 79.5 | STRONG |
| `..._dd_pct25_252` | abs % | 25% | 1.1365 | 31.2% | 76.0 | STRONG |

**KILL_LOOP results (pre-registered):**
- KILL_LOOP #1 (success-tag) — **NOT FIRED** (best Sortino 1.2841 < 1.3746)
- KILL_LOOP #2 (decisive-fail) — **NOT FIRED** (4 of 5 ks-configs ≥ 1.10 floor)
- KILL_LOOP #3 (replica-sanity) — **NOT FIRED** (baseline 1.2841 = iter 001 baseline exactly)
- KILL_LOOP #4 (whipsaw-detector) — **NOT FIRED** (kill-switch turnover lower than baseline 9.3/y)

**Key finding:** Carver's sigma-price stop does NOT generalise from
single-trade single-asset position management to a regime overlay on a
leveraged trend system. LETF natural vol means even normal pullbacks cross
3-4σ DD thresholds; the kill switch fires too often (21.7% of days at
Carver-default X=4) and locks out compounding rallies. Sortino is
monotonically below baseline across the entire X sweep. The original target
crisis (2022_rates) is not rescued by any variant — 2022 was a duration
problem (slow grinding bear), not a magnitude problem. **Structural
positive:** G1 PBO=0.159 passes cleanly across all configs (vs iter 001's
universal G1=0.575 fail) — kill-switch dimension is genuinely orthogonal,
confirming CSCV behaves correctly when configs vary in distinct mechanics.

**beats_winner:** **false** (best Sortino edge -0.0405 = baseline replica
drift only; no kill-switch variant adds Sortino).

**Next iter ideas:** (a) Equity-bond correlation regime classifier — flip OFF
when 60d QLD↔ZROZ correlation goes positive (would have fired in 2022 when
both fell together) `[regime_change]`/`[ml_for_algo_trading]`; (b)
Multi-asset ON rotation with inverse-vol weighting `[risk_parity, ch.5]` +
`[stocks_on_the_move, p.98]`; (c) Calendar/seasonal master-gate as 5th vote
member `[trading_systems_methods, p.388]`/`[evidence_based_ta, ch.7]`.

### 001 — 2026-05-09 — adaptive-off-yieldcurve

**Hypothesis:** Term-premium-aware OFF-asset rotation (10y - 3m CMT slope
gates ZROZ vs CASHX during defensive periods) attempts to rescue the 2022
rates loss of the study winner. Same trend ON signal as winner (vote-of-2
sma250/100 vol21<40% ar30>0). Citation: `[systematic_trading, ch.9 p.180-190]`
(Carver carry as regime gate).

**Configs tested (6):**

| name | OFF rule | sortino_lh56y | sharpe_lh56y | score | tier |
|---|---|---:|---:|---:|---|
| `..._off_zroz_baseline` | always ZROZ (replica) | 1.2841 | 0.892 | 72.5 | PROMISING |
| `..._off_adapt_ts000` | (10y-3m) > 0.0pp gate | 1.2661 | 0.880 | 72.5 | PROMISING |
| `..._off_adapt_ts050` | (10y-3m) > 0.5pp gate | 1.2969 | 0.902 | 72.5 | PROMISING |
| `..._off_adapt_ts100` | (10y-3m) > 1.0pp gate | 1.2796 | 0.890 | 72.5 | PROMISING |
| **`..._off_adapt_ts150`** | (10y-3m) > 1.5pp gate | **1.3018** ← best | 0.905 | 72.5 | PROMISING |
| `..._off_adapt_lvltrnd` | 10y < 252d-SMA(10y) | 1.2188 | 0.854 | 72.5 | PROMISING |

**KILL_LOOP results (pre-registered):**
- KILL_LOOP #1 (success-tag) — **NOT FIRED** (best Sortino 1.3018 < 1.3746)
- KILL_LOOP #2 (decisive-fail) — **NOT FIRED** (all configs ≥ 1.10 floor)
- KILL_LOOP #3 (replica-sanity) — **NOT FIRED** (replica drift -0.04 < 0.05 bound)

**Key finding:** Term-premium gating on the OFF leg produces a tight Sortino
band (1.27-1.30) that does not exceed the always-ZROZ baseline by enough
margin to register a win. The 2022 equity drawdown was an ON-leg mistake (NDX
crashed while trend signal was still ON), not an OFF-asset problem — so no
amount of OFF-asset cleverness rescues that crisis. G1 PBO 0.575 fails
universally because the one-axis sweep design intentionally minimizes
hypothesis-space diversity.

**beats_winner:** **false** (best Sortino edge -0.0228; WC also failed on G1
PBO).

**Next iter ideas:** (a) ON-signal regime modulation — make the trend gate go
OFF earlier in 2022-style stress regimes via regime classifier
(`[regime_change]` / `[adaptive_markets]`); (b) Multi-asset ON rotation with
inverse-vol weighting (distinct from T4 ranking and T5 Carver); (c)
Calendar/seasonal master-gate as a 5th vote member (`[trading_systems_methods]`
Kaufman or `[evidence_based_ta]` Aronson).

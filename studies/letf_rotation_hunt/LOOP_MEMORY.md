---
mission: "post-close strategy hunt: research new strategies and benchmark vs T3d-K2 study winner"
status: open
total_iterations: 5
target_total_iterations: 50
closed_study_cumulative_n_trials: 426
cumulative_n_trials_loop: 30
cumulative_n_trials_global: 456
incumbent_winner_iter: "022-2026-05-06-T3d-extended-grid"
incumbent_winner_config: "qld_voteK2_sma250_100_vol21_40_ar30_off_zroz"
incumbent_winner_sortino_lh56y: 1.3246
incumbent_winner_sharpe_lh56y: 0.919
incumbent_winner_score: 82
beats_winner_threshold_sortino: 1.3746
beats_winner_threshold_pct_above_spy: 0.95
beats_winner_threshold_winner_conditions_met: true
loop_winner_iter: null
latest_iteration: "005-2026-05-09-multi-asset-on-invvol"
latest_score: 77.5
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

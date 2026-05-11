# Iter 010 — graded-master-bridge — HYPOTHESIS (pre-commit)

**Slug:** `010-2026-05-09-graded-master-bridge`
**n_configs:** 6
**cumulative_n_trials_global before / after:** 480 → **486**
**Datetime UTC (start):** 2026-05-09 (continues iter 009 same-day work)

## 1 Hypothesis

Iter 009 surfaced an explicit **operative trade-off**:

- **offleg-pure** override (basket3 × ratevol→CASHX, only when on_signal=OFF):
  Sortino 1.4637, beats_winner=**True**, but **fails 2022_rates rescue** (crisis count 2/4).
  Preserves equity-bull compounding because override never fires while on_signal=ON.
- **master-pure** override (whole-portfolio CASHX whenever ratevol fires, regardless
  of on_signal): Sortino 1.3686, edge +0.044 (below +0.05 threshold), WC=**False**
  (cross-dataset mean pct_above ~0.93 < 0.95), but **rescues 2022_rates** (crisis
  count 3/4). Cash drag during ratevol+ON regimes costs both pct_above and Sortino.

Hypothesis: a **graded** master-scope — interpolating with coefficient `gamma ∈ (0, 1)`
between offleg-pure (gamma=0, no override during ON) and master-pure (gamma=1, full
override during ON) — has a **sweet spot at gamma ∈ {0.25, 0.50}** that simultaneously:
1. Retains `beats_winner=True` (Sortino > 1.3746 AND winner_conditions_met=True
   AND pct_above_lh56y ≥ 0.95).
2. Adds the 2022_rates crisis rescue (crisis count ≥ 3/4).

If the hypothesis holds, this would be the **first config in the loop to clear all
three of**: beats_winner=True, score ≥ 80, AND 3/4 crises beaten — closer (though not
yet at) the score-90 deploy bar of LOOP_PROTOCOL §"Mandate §1 reinforcement".

## 2 Mechanic specification

Graded master-scope strategy (NEW helper: `graded_master_strategy.py`):

| ratevol | on_signal | offleg-pure (gamma=0) | graded (0<gamma<1) | master-pure (gamma=1) |
|--:|--:|---|---|---|
| 0 | ON  | on_basket | on_basket | on_basket |
| 0 | OFF | off_zroz  | off_zroz  | off_zroz  |
| 1 | ON  | on_basket | gamma*alt_off + (1-gamma)*on_basket | alt_off |
| 1 | OFF | alt_off   | alt_off   | alt_off   |

Only the `(ratevol=1, on_signal=ON)` cell varies with gamma — exactly the regime
where iter 009 identified the offleg/master semantic difference. All other regimes
are identical between offleg, graded, and master. This keeps the mechanic
**structurally adjacent** to iter 009 but parametrically distinct.

## 3 Configs (6, mechanism-mix structural-diversity grid)

| # | name | topology | gamma | basket | scope helper |
|--:|---|---|--:|---|---|
| 1 | `..._gmaster_baseline` | none-single | — | {QLDSIM} | (no helper; trend only) |
| 2 | `..._gmaster_basket3_only` | none-basket | — | {QLDSIM, UPROSIM, UGLSIM} (invvol60) | (no helper; trend only) |
| 3 | **`..._gmaster_offleg_pure`** ← iter 009 winner replica | offleg | 0.00 | basket3 invvol60 | iter 007 `build_compound_strategy_returns` |
| 4 | `..._gmaster_g25_cashx` | **graded** | 0.25 | basket3 invvol60 | NEW `build_graded_master_strategy_returns` |
| 5 | `..._gmaster_g50_cashx` | **graded** | 0.50 | basket3 invvol60 | NEW `build_graded_master_strategy_returns` |
| 6 | `..._gmaster_master_pure` ← iter 009 master_basket3 replica | master | 1.00 | basket3 invvol60 | iter 009 `build_master_scope_strategy_returns` |

Trend ON signal is `vote-of-2 of {SMA250, SMA100, vol_21d<40%, AR(1)_30d>0}` on
QLDSIM (winner replica gate; iter 007 helper unchanged). ratevol gate is
ZROZSIM realised-vol percentile within trailing 5y, threshold p70, window 60d
(iter 006 helper unchanged). alt_off = CASHX (testfolio synthetic FFR proxy).

**4 distinct mechanism topologies** (none-single, none-basket, offleg,
graded, master) — preserves the structural-diversity primitive iter 009
established as PBO-cracking (vs iter 008's 5 parametric variants of one
mechanism, which yielded PBO 0.5675).

## 4 Datasets

Same as iter 005-009 study window stack (mandate §1 reproducibility):

| Dataset | Window | Bottleneck |
|---|---|---|
| `lh_56y` | 1970-01-01..2026-04-30 | SPYSIM |
| `modern_1990` | 1990-01-01..2026-04-30 | SPYSIM (post-Halloween-effect-canonical) |
| `spy_real` | 2003-01-01..2026-04-30 | Tiingo SPY |
| `ndx_real` | 2010-02-01..2026-04-30 | Tiingo QQQ |

## 5 Pre-registered KILL_LOOP rules

1. **KILL_LOOP #1 (`success_tag`):** ANY config has `beats_winner=True` (positive
   tag — the iter found at least one beater of the frozen winner).
2. **KILL_LOOP #2 (`decisive_fail`):** best Sortino_lh56y < 1.30 — graded mechanic
   destroyed the compound lift entirely.
3. **KILL_LOOP #3 (`replica_sanity_baseline`):** baseline Sortino_lh56y deviates
   from 1.2841 by > 0.005 (cross-iter reproducibility check).
4. **KILL_LOOP #4 (`replica_sanity_offleg_pure`):** offleg_pure Sortino_lh56y
   deviates from 1.4637 by > 0.005 (iter 007/008/009 winner replica anchor; 4th
   generation reproducibility test).
5. **KILL_LOOP #5 (`PBO_held`):** G1 PBO < 0.50 (mechanism diversity preserved
   from iter 009's 0.377; positive tag if held). FIRES if PBO regresses ≥ 0.50
   like iter 008.
6. **KILL_LOOP #6 (`graded_2022_rescue`):** at least one **graded** config
   (#4 or #5) has `beats_winner=True` AND beats SPY in 2022_rates window.
   This is the **directional hypothesis test** — graded mechanic finds a
   sweet spot that the binary offleg/master mechanics couldn't.

## 6 Expected outcomes (per config)

| # | name | Expected Sortino_lh56y range | Expected beats_winner | Expected 2022_rescue |
|--:|---|---:|:---:|:---:|
| 1 | baseline | 1.275-1.290 (replica band) | F | F |
| 2 | basket3_only | 1.325-1.345 (replica band) | F | F |
| 3 | offleg_pure | 1.460-1.467 (replica band) | T | F |
| 4 | graded_g25 | 1.43-1.46 (light-touch master, mostly retains offleg behaviour) | T (most likely) | T (possibly — depends on whether 25% during ratevol+ON catches enough of 2022) |
| 5 | graded_g50 | 1.40-1.45 (interpolated) | T (less certain than #4) | T (more likely — half-cash during ratevol+ON catches 2022 better) |
| 6 | master_pure | 1.365-1.371 (replica band) | F (WC fails on cross-dataset pct_above) | T |

**Hypothesis confirmed if:** at least one of #4 or #5 has `beats_winner=True`
AND `2022_rates_beat=True` simultaneously.

**Hypothesis rejected if:** both #4 and #5 either lose beats_winner (Sortino
or pct_above drops below threshold) OR fail 2022_rates rescue. Then graded
mechanic offers no clean trade-off resolution — would suggest pursuing
orthogonal mechanic family (e.g., VIX-percentile gate, iter 009 idea #3)
in iter 011.

## 7 Comparação plan vs winner (per beats-winner test)

For each config, compute:
- `sortino_edge_vs_winner = sortino_lh56y - 1.3246`
- `beats_winner = (sortino_lh56y > 1.3746) AND winner_conditions_met AND (pct_above_lh56y >= 0.95)`

Best-config selection rule (same as iter 009): primary key = `sortino_lh56y`
(descending), tiebreaker = `score_breakdown.total` (descending).

## 8 Citations

- **Primary:** `[risk_parity, p.80-81, ch.4]` — Qian RORO graded master-gate
  (the canonical reference for graded weights between full-on and full-off
  regime classification).
- `[advances_fin_ml, p.208-211]` — CSCV / PBO via combinatorial 50/50 splits;
  structural mechanism diversity preservation rule (iter 008 → iter 009 → iter 010).
- `[advances_fin_ml, p.222-223]` — DSR with cumulative n_trials denominator
  (G2 global trial count = 486 for this iter).
- `[volatility_trading, p.58-60]` — Sinclair volatility cone (ratevol gate
  module re-imported from iter 006).
- `[stocks_on_the_move, p.98]` — Clenow vol-parity sizing (basket3 invvol60
  module re-imported from iter 005).
- `[risk_parity, ch.5, p.10]` — Carlson cap-efficient stacking (compound
  super-additivity, iter 007 finding; preserved at gamma=0).

## 9 Scope limits (LOOP_PROTOCOL §"Scope limits")

- New helper this iter: `graded_master_strategy.py`
  (`build_graded_master_strategy_returns` + `graded_master_turnover`).
  Self-contained inside iter dir per LOOP_PROTOCOL.
- Iter 005/006/007/009 helpers re-imported READ-ONLY (no mutation).
- gates.py / scoring.py / plot_helper.py / data_loader.py / signals.py /
  signals_carry.py / synths.py / tax_layer.py / kill_rules.py /
  verdict_schema.json / loop_verdict_schema.json — UNTOUCHED (study modules).
- iterations/ / configs/ / run_iter*.py / BASE_MEMORY.md — UNTOUCHED
  (closed study).
- TDD baseline ≥ 813 tests must not regress (currently 1055 collected;
  new test file `tests/test_letf_rotation_hunt_loop_010.py` for graded
  helper unit tests).

## 10 Mandate §1 invariant

- Capital remains 100% Plan C regardless of outcome.
- `beats_winner=True` is a research signal, not a deploy signal.
- Score ≥ 90 + WC=Y + beats_winner=True is the LOOP_PROTOCOL threshold for
  the `docs/CURRENT_STATE.md` "Active Hunts" entry; per orchestrator
  conservative guardrails, public docs preserved untouched unless that bar
  clears AND user-driven mandate §7 override is explicitly granted.
- This iter records to `loop_winner_iter` list in `LOOP_MEMORY.md` frontmatter
  ONLY if any config has `beats_winner=True`.

## 11 INCOMPLETE flags (pre-registered)

- **Replica drift baseline (~0.04 Sortino):** baseline Sortino_lh56y target
  1.2841 vs canonical iter 022 winner 1.3246. Loop's relative deltas are
  bit-exact valid; absolute level differs from canonical due to different
  signal periods (sma200/50 canonical vs sma250/100 loop family).
- **Synth caveats (pre-1985):** ZROZSIM, IEFSIM, CASHX, UGLSIM are testfolio
  synthetic proxies. Same caveat as iters 005-009; primitives (basket-invvol,
  ratevol percentile, graded master coefficient) robust to absolute-level
  miscalibration via rolling rank / rolling sigma / categorical state machine
  with linear interpolation.
- **5y warmup falls back to baseline routing** during 1970-1975 (~9% of
  lh_56y span) for the ratevol gate. Graded master inherits warmup behaviour
  (when ratevol NaN, no graded fires; baseline routing applies).
- **DSR p_value reported is local (n=6) per protocol.** Cumulative DSR
  (n_trials_global = 486) is the canonical denominator for `beats_winner`
  promotional claims per `[advances_fin_ml, p.222-223]`. Both are computed.
- **Linear interpolation only:** graded coefficient applies linearly; this
  iter does NOT test non-linear graded forms (e.g., concave/convex curves
  in gamma vs ratevol intensity). Linearity is the simplest hypothesis;
  if confirmed, iter 011 could test concavity. If rejected, iter 011 should
  pivot to orthogonal mechanism family (e.g., VIX-percentile).

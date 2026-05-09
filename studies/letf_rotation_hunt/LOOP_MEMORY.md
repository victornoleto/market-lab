---
mission: "post-close strategy hunt: research new strategies and benchmark vs T3d-K2 study winner"
status: open
total_iterations: 1
target_total_iterations: 50
closed_study_cumulative_n_trials: 426
cumulative_n_trials_loop: 6
cumulative_n_trials_global: 432
incumbent_winner_iter: "022-2026-05-06-T3d-extended-grid"
incumbent_winner_config: "qld_voteK2_sma250_100_vol21_40_ar30_off_zroz"
incumbent_winner_sortino_lh56y: 1.3246
incumbent_winner_sharpe_lh56y: 0.919
incumbent_winner_score: 82
beats_winner_threshold_sortino: 1.3746
beats_winner_threshold_pct_above_spy: 0.95
beats_winner_threshold_winner_conditions_met: true
loop_winner_iter: null
latest_iteration: "001-2026-05-09-adaptive-off-yieldcurve"
latest_score: 72.5
latest_tier_label: PROMISING
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

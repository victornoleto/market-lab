---
mission: "post-close strategy hunt: research new strategies and benchmark vs T3d-K2 study winner"
status: open
total_iterations: 0
target_total_iterations: 50
closed_study_cumulative_n_trials: 426
cumulative_n_trials_loop: 0
cumulative_n_trials_global: 426
incumbent_winner_iter: "022-2026-05-06-T3d-extended-grid"
incumbent_winner_config: "qld_voteK2_sma250_100_vol21_40_ar30_off_zroz"
incumbent_winner_sortino_lh56y: 1.3246
incumbent_winner_sharpe_lh56y: 0.919
incumbent_winner_score: 82
beats_winner_threshold_sortino: 1.3746
beats_winner_threshold_pct_above_spy: 0.95
beats_winner_threshold_winner_conditions_met: true
loop_winner_iter: null
latest_iteration: null
latest_score: null
latest_tier_label: null
latest_beats_winner: null
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

(empty — primeiro iter populates this section conforme PROMPT step 7)

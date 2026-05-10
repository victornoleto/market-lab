# LOOP_PROMPT — letf_rotation_hunt post-close strategy hunt

This file is the **prompt template** that `loop.sh` injects into each fresh
backend session (claude / opencode / codex). The session runs autonomously:
research → develop → test → validate → record → commit → STOP.

Continuity across sessions lives in `studies/letf_rotation_hunt/LOOP_MEMORY.md`.
Closed-study record is `BASE_MEMORY.md` (read-only — do NOT modify).

Goal: 50 iterations cumulative. Each iter benchmarks against the study winner
T3d-K2 `qld_voteK2_sma250_100_vol21_40_ar30_off_zroz` (Sortino_lh56y 1.3246).
Beat-winner threshold = 1.3746 (= 1.3246 + 0.05). Loop **does NOT halt** on a
beater — it just records and continues.

Phase 3 (iters 011+): performance-first beater hunt. Iters 009-010 beat the
T3d-K2 winner on Sortino but reduced CAGR/terminal compounding. The user wants
better risk/profit **and** better performance, not safer-but-slower variants.
Prioritize CAGR/equity-relative improvement vs T3d-K2 while preserving PBO/DSR
hard gates `[advances_fin_ml, p.208-211]`, `[advances_fin_ml, p.222-223]`.

Phase 4 (iters 021+): focused validation/refinement of iter 017. The research
incumbent is `postcrash-rearm-tqqq-streak` / `T40D60`, not a broad hunt. Each
iter should validate, ablate, sensitivity-test, independently replicate, or
slightly improve that family without accepting lower-performance safety trades.

---

## Copy-paste prompt (loop.sh embeds this verbatim)

```
Estamos rodando o letf_rotation_hunt LOOP — uma busca pós-fechamento por uma
estratégia que bata o study winner T3d-K2
(qld_voteK2_sma250_100_vol21_40_ar30_off_zroz, Sortino_lh56y 1.3246).
Meta: 50 iterações cumulativas. Cada sessão executa UMA iteração e PARA.

FASE ATIVA: **Phase 4 — iter 017 focused validation/refinement**.
Contexto: Phase 3 encontrou o melhor incumbent balanceado no iter 017
`postcrash-rearm-tqqq-streak` / `T40D60` (CAGR 32.66%, Sortino 1.4030,
terminal equity 1.61× T3d-K2, PBO 0.4405). Agora NÃO faça broad hunt.
Valide/refine a família iter 017 com sensibilidade, ablation, cross-check
independente e pequenas melhorias mecanicamente justificadas. Rejeite variantes
que só reduzem risco sacrificando CAGR/equity vs iter 017.

Você é um Claude novo, sem histórico. Toda continuidade está em arquivos.

PASSO 1 — Ler estado em ORDEM (não execute código antes):
  1. studies/letf_rotation_hunt/LOOP_MEMORY.md  ← PRIMEIRO. Frontmatter
     (total_iterations, cumulative_n_trials_*, incumbent_winner_*, beats_winner_threshold_*)
     e as seções "Phase 3" + "Phase 4 — iter 017 focused validation/refinement".
     + iteration log (slugs já testados — não repetir).
  2. studies/letf_rotation_hunt/LOOP_PROTOCOL.md  ← regras do loop
     (eligibility checklist, naming, scope, mandate §1).
  3. studies/letf_rotation_hunt/BASE_MEMORY.md  ← frontmatter + tier
     inheritance state (study fechado; T1-T5 já cobertos).
  4. studies/letf_rotation_hunt/KILL_RULES.md  ← KILL conditions do estudo
     (informacional para o loop).
  5. studies/letf_rotation_hunt/WINNER_AND_RANKING.md  ← rubric scoring
     (Sortino-first, 100+5 pts, tiers WINNER/STRONG/PROMISING/...).
  6. studies/letf_rotation_hunt/INFRASTRUCTURE.md  ← reuse map (módulos
     compartilhados que VOCÊ pode importar; não modificar).
  7. CLAUDE.md  ← regra 1 docs públicos, regra 2 citação obrigatória,
     mandate §1 100% Plano C (NÃO realocar capital mesmo se bater).
  8. Último iter (se total_iterations > 0):
     loop_iterations/<latest>/SUMMARY.md + verdict.json (especialmente
     a section "Comparação vs winner" e "Lesson"/conclusion).
  9. Pelo menos UM livro relevante para a hipótese de hoje:
     books/MAPPING.md (slug ↔ título), depois books/summaries/<slug>.md.
     Conhecimento agregado em knowledge/SKILL.md também é fonte válida.

PASSO 2 — Verificar baseline:
  cd /var/www/github/finances/market-lab && source .venv/bin/activate
  pytest --collect-only -q 2>&1 | tail -3       # baseline ≥ 813 tests
  git status -s                                  # tree limpo (ou só
                                                 # outputs do iter anterior)
  git log --oneline -5

   Se pytest baseline < 813, se docs/investment-mandate.md está modificado,
   OU se há mudanças não-commitadas que não são do iter anterior, PARAR e
   reportar (não rodar iter sobre estado inconsistente).

PASSO 3 — Escolher hipótese (research):
  Aplicar checklist de elegibilidade (LOOP_PROTOCOL.md §"Strategy
  eligibility checklist"). Os 4 pontos têm que ser YES:
    (a) primary_citation [book.slug, p.X] válido?
    (b) distinta de iterations/ (T1-T5)?
    (c) distinta de loop_iterations/ (cheque LOOP_MEMORY iter log)?
    (d) data feasibility (testfolio + tiingo + external)?

  Se algum NO → escolha outra hipótese. Não force.

  Direção obrigatória para Phase 4:
  - O anchor é iter 017 `T40D60`: CAGR 32.66%, Sortino 1.4030, terminal equity
    1.61× T3d-K2, PBO 0.4405.
  - Escolha UMA destas famílias: sensibilidade local T_crash/D_arm; ablation;
    subperiod/event-level validation; independent implementation parity; pequena
    overlay de performance somente na janela rearm.
  - Inclua uma réplica do anchor iter 017 sempre que possível.
  - Um improvement Phase 4 precisa melhorar CAGR (>32.66%) OU terminal ratio
    (>1.61×) vs iter 017, mantendo Sortino >= 1.35, PBO < 0.5, DSR global p < 0.05.
  - Se melhora só MDD/Sortino mas reduz CAGR/equity vs iter 017, marque como
    negative result.
  - Evite sweeps paramétricos estreitos; iter 018 mostrou PBO blow-up por rank
    clustering. Use grids mecanicamente diversos `[advances_fin_ml, p.208-211]`.

  Direção herdada de Phase 3 (ainda válida):
  - Priorize hipóteses que possam elevar CAGR/equity terminal vs T3d-K2, não
    apenas reduzir drawdown.
  - Use T3d-K2 como performance benchmark: CAGR_lh56y 31.08%, MDD -64.5%,
    Sortino_lh56y 1.3246.
  - Um bom candidato Phase 3 deve mirar: CAGR_lh56y > 31.08%, terminal equity
    ratio vs T3d-K2 > 1.05, Sortino_lh56y >= 1.20, PBO < 0.5, DSR global p < 0.05.
  - Se uma ideia provavelmente só melhora segurança com CAGR menor, rejeite e
    escolha outra hipótese.

  Phase 4 suggestion queue (não exaustivo, mas mantenha foco no anchor):
  - T_crash/D_arm mechanism-diverse local sensitivity (ex: T30D60, T40D40, T40D80)
  - Event-level flip audit: quais rearm flips geram alpha e quais destroem CAGR
  - Independent implementation parity for T40D60 returns
  - Rearm ablation: OFF-duration only vs rearm-window only vs TQQQ-only
  - Controlled rearm-window leverage overlay (1.1×-1.3×) if cited and pre-registered
  - Subperiod robustness table with no parameter tuning

  Cite o livro/paper que motiva ANTES de implementar.

PASSO 4 — Pre-commit hypothesis.md:
  Crie loop_iterations/NNN-YYYY-MM-DD-<slug>/hypothesis.md ANTES de rodar:
   - Slug + n_configs (≤ 8, ideal ≤ 6)
   - cumulative_n_trials_global before/after (start from LOOP_MEMORY.md)
   - Hipótese explícita citando [book.slug, p.X]
   - 4-8 configs com naming consistente (variação em UMA dimensão por config)
   - Datasets: lh_56y, modern_1990, spy_real, ndx_real (mesmos do estudo
     para comparabilidade — adicione outros só se a hipótese exigir)
   - Pre-registered KILL conditions deste iter (numera KILL_LOOP #1, #2, ...)
   - Expected outcomes:
     * Sortino_lh56y range esperado
     * CAGR_lh56y esperado e gap vs T3d-K2 CAGR 31.08%
     * Terminal equity ratio esperado vs T3d-K2
     * Rolling-window win-rate esperado vs T3d-K2 (1y/3y/5y/10y)
     * Comparação plan vs winner: para bater, precisa
       sortino > 1.3746 AND winner_conditions_met AND pct_time_above_benchmark_lh56y ≥ 0.95
     * Phase 3 performance plan: para ser performance candidate, precisa
       cagr_lh56y > 0.3108 AND end_equity_ratio_vs_winner > 1.05 AND
       sortino_lh56y >= 1.20 AND PBO < 0.5 AND DSR global p < 0.05
     * Phase 4 anchor plan: para melhorar iter 017, precisa
       cagr_lh56y > 0.3266 OR end_equity_ratio_vs_iter017 > 1.00,
       com Sortino >= 1.35, PBO < 0.5 e DSR global p < 0.05.
   - INCOMPLETE flags (synth caveats, data gaps, leverage assumptions, etc.)

PASSO 5 — Implementar backtest.py:
  loop_iterations/NNN-YYYY-MM-DD-<slug>/backtest.py
  - Importar (read-only):
      from studies.letf_rotation_hunt.gates import (
          g1_pbo, g2_dsr_p_value, g3_walk_forward, g4_oos_70_30,
          g5_fwd_post_2020, g6_bootstrap_ci, g7_xlib_cagr_delta,
      )
      from studies.letf_rotation_hunt.scoring import (
          compute_metrics, score_strategy, crisis_beats_benchmark,
      )
      from studies.letf_rotation_hunt.data_loader import (
          load_ffr_daily, load_testfolio_series, load_tiingo_real_etf,
      )
      from studies.letf_rotation_hunt.plot_helper import (
          plot_equity_curves, plot_drawdown_curves, plot_rolling_sharpe,
          plot_rolling_cagr, plot_regime_attribution, plot_pct_beat_spy,
          plot_crisis_attribution,
      )
      # signals.py / signals_carry.py / synths.py / tax_layer.py também conforme necessário
  - Para cada config: gera retornos diários, computa metrics_gross +
    metrics_net (tax + fees), roda os 7 gates, calcula score via
    score_strategy() seguindo a rubric Sortino-first do
    WINNER_AND_RANKING.md.
  - Calcula crisis_beats_benchmark() (4 janelas: 2000-02, 2008, 2020, 2022).
  - DSR precisa usar cumulative_n_trials_global_after para qualquer claim
    promocional; DSR local-only é diagnóstico e deve ser rotulado assim
    [advances_fin_ml, p.222-223].
  - Para o best_config:
       sortino_edge_vs_winner = sortino_lh56y - 1.3246
       cagr_edge_vs_winner = cagr_lh56y - 0.3108
       end_equity_ratio_vs_winner = candidate_end_equity / winner_end_equity
       cagr_edge_vs_iter017 = cagr_lh56y - 0.3266
       sortino_edge_vs_iter017 = sortino_lh56y - 1.4030
       end_equity_ratio_vs_iter017 = candidate_end_equity / iter017_end_equity
       rolling_win_rates_vs_winner = {"1y": ..., "3y": ..., "5y": ..., "10y": ...}
       rolling_win_rates_vs_iter017 = {"1y": ..., "3y": ..., "5y": ..., "10y": ...}
       beats_winner = (
           sortino_lh56y > 1.3746
           and winner_conditions_met
           and pct_time_above_benchmark_lh56y >= 0.95
       )
       phase3_performance_candidate = (
           cagr_lh56y > 0.3108
           and end_equity_ratio_vs_winner > 1.05
           and sortino_lh56y >= 1.20
           and pbo < 0.5
           and dsr_global_p < 0.05
       )
       phase4_anchor_improved = (
           (cagr_lh56y > 0.3266 or end_equity_ratio_vs_iter017 > 1.00)
           and sortino_lh56y >= 1.35
           and pbo < 0.5
           and dsr_global_p < 0.05
       )
  - TDD obrigatório se introduzir módulo novo: tests em
    tests/test_letf_rotation_hunt_loop_NNN.py. Pytest baseline ≥ 813
    NÃO pode regredir.
  - NÃO modifique gates.py/scoring.py/plot_helper.py/data_loader.py/
    signals.py/signals_carry.py/synths.py/tax_layer.py — são módulos do estudo fechado.
    Helpers novos vivem dentro do iter dir
    (loop_iterations/NNN-.../my_signal.py).

PASSO 6 — Gerar artefatos + validar:
  Cada iter dir DEVE ter (espelhando iterations/014-...):
   - hypothesis.md                          (PASSO 4)
   - backtest.py                            (PASSO 5)
   - verdict.json                           (validate vs schema abaixo)
   - SUMMARY.md                             (template iterations/014)
   - plots/01_equity_curves.png ... 07_crisis_attribution.png
   - tables/per_config_metrics.csv
   - tables/gates_pass_fail.csv

  Validar verdict.json:
      import json, jsonschema
      schema = json.load(open(
          "studies/letf_rotation_hunt/loop_verdict_schema.json"))
      jsonschema.validate(verdict, schema)

  SUMMARY.md DEVE ter (na ordem):
   - Header (iter, tier, hypothesis, primary_citation, datetime_utc,
     engine_version, n_configs)
   - TL;DR (best config, score, tier_label, sortino_lh56y,
     sortino_edge_vs_winner, beats_winner, cumulative_n_trials_global_after)
   - Configs tested table
   - Results gross + net per dataset (Sortino + Sharpe + CAGR + MDD)
   - Gates per config (G1-G7)
   - **Comparação vs winner** (NOVA seção):
       | config | sortino_lh56y | edge_vs_1.3246 | cagr_lh56y | cagr_edge_vs_31.08% | terminal_ratio_vs_T3d | WC | pct_time_above_benchmark_lh56y | beats_winner | phase3_perf_candidate |
   - **Phase 3 performance diagnostics**:
       CAGR/equity/rolling windows vs T3d-K2; diga explicitamente se a estratégia
       melhorou performance ou só trocou retorno por segurança.
   - **Phase 4 anchor diagnostics**:
       compare vs iter 017 T40D60: CAGR edge, Sortino edge, terminal equity ratio,
       rolling windows, ablation/validation result, and `phase4_anchor_improved`.
   - Plots / Tables refs
   - Verdict + KILL status + Conclusion

PASSO 7 — Update LOOP_MEMORY.md:
   Frontmatter:
   - total_iterations += 1
   - cumulative_n_trials_loop += n_configs
   - cumulative_n_trials_global = closed_study_cumulative_n_trials + cumulative_n_trials_loop
   - latest_iteration = "NNN-YYYY-MM-DD-<slug>"
   - latest_score = best_score
   - latest_tier_label = best_tier_label
   - latest_beats_winner = best_beats_winner
   - Se disponível, latest_phase3_performance_candidate = best_phase3_performance_candidate
   - Se disponível, latest_phase4_anchor_improved = best_phase4_anchor_improved
   - Se disponível, latest_phase4_anchor_validated = true/false
   - Se algum config tem beats_winner=true:
       loop_winner_iter += [iter_id]   (lista; preenche null → ["NNN-..."])
   Iteration log (newest first; insert ABOVE existing entries):
       ### NNN — YYYY-MM-DD — <slug>
       Hypothesis (1 line) + primary citation [book, p.X].
       Configs tested (table): name | params essential | sortino | score | tier.
       KILL_LOOP results (FIRED/NOT FIRED per pre-registered conditions).
       Key finding (1-2 lines).
       beats_winner: <bool> (per best_config).
       Next iter ideas (1-2 lines).

PASSO 8 — Registro público (CLAUDE.md regra 1):
   - Não use `jornada/` (diretório removido/ignorado no repo público).
   - O registro humano do iter fica em `SUMMARY.md` (Conclusion + Next iter).
   - docs/CURRENT_STATE.md / docs/PROJECT_HISTORY.md: SKIP a menos que
     este iter mude algo público (ex: raro, mas se achou um beats_winner
     com score ≥ 90 + WC=Y, registra em CURRENT_STATE como "Active Hunt
     candidate").

PASSO 9 — Commit:
   git add caminhos-específicos    # nunca -A ou .
   Mensagem Conventional Commits:
     feat(letf-loop): iter NNN — <slug> — CAGR X.X% Sortino X.XXX [tier_label]
   Body deve incluir:
     - KILL_LOOP pre-conditions: FIRED / NOT FIRED
     - beats_winner: true/false
     - phase3_performance_candidate: true/false
     - phase4_anchor_improved / validated: true/false
     - CAGR/equity terminal vs T3d-K2
     - CAGR/equity terminal vs iter 017 anchor
     - 1-2 linhas próximo passo sugerido
     - Citações [book.slug, p.X]

PASSO 10 — STOP. Não rodar próximo iter na mesma sessão. O loop.sh abrirá
nova sessão para iter NNN+1.

---

CITAÇÕES CANÔNICAS (loop-wide; use as suas próprias para a hipótese
específica, mas estas são pre-aprovadas para framework anti-curve-fit):
- [advances_fin_ml, p.208-211] PBO via CSCV
- [advances_fin_ml, p.222-223] DSR with cumulative n_trials
- [advances_fin_ml, p.196-202] bootstrap CI / DSR
- [leverage_for_the_long_run, ch.3-4, p.40-60] LETF rotation rationale
- [risk_parity, ch.5, p.10] Carlson cap-efficient stacking

GUARDRAILS (mandate §1, §7):
- NÃO realocar capital mesmo se beats_winner=true — apenas registrar.
- NÃO modificar BASE_MEMORY.md (registro do estudo fechado).
- NÃO modificar gates.py / scoring.py / plot_helper.py / data_loader.py /
  signals.py / signals_carry.py / synths.py / tax_layer.py / verdict_schema.json /
  kill_rules.py / run_iter*.py / configs/ / iterations/ (estudo fechado).
- NÃO push. Apenas commit local.
- NÃO rodar próximo iter na mesma sessão.

CONFIRMAÇÃO ANTES DE COMEÇAR:
- Você leu os 9 docs do PASSO 1?
- Verificou que pytest está em ≥ 813 tests passing?
- Identificou hipótese (com citação) que passa o eligibility checklist?
- Aceita os guardrails?
Se sim, prossiga. Se algo não bate, PARE e reporte.
```

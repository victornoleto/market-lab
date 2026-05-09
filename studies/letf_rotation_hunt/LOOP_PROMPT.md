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

---

## Copy-paste prompt (loop.sh embeds this verbatim)

```
Estamos rodando o letf_rotation_hunt LOOP — uma busca pós-fechamento por uma
estratégia que bata o study winner T3d-K2
(qld_voteK2_sma250_100_vol21_40_ar30_off_zroz, Sortino_lh56y 1.3246).
Meta: 50 iterações cumulativas. Cada sessão executa UMA iteração e PARA.

Você é um Claude novo, sem histórico. Toda continuidade está em arquivos.

PASSO 1 — Ler estado em ORDEM (não execute código antes):
  1. studies/letf_rotation_hunt/LOOP_MEMORY.md  ← PRIMEIRO. Frontmatter
     (total_iterations, cumulative_n_trials_*, incumbent_winner_*, beats_winner_threshold_*)
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

  Famílias de estratégia ainda não exploradas (sugestões — não exaustivo):
  - Cross-asset trend / risk parity rebalancing (Carlson, Asness)
  - VIX percentile / VRP harvesting (Bozovic, Israelov)
  - Calendar / seasonality (Bouchard, Heston-Sadka)
  - Currency carry baskets (Burnside, Lustig)
  - Gold momentum / commodity momentum (Erb-Harvey)
  - Bond duration timing (Ilmanen)
  - Equity factor tilts: low-vol, profitability, investment (Asness, Frazzini)
  - Volatility-of-volatility / VVIX-driven (Cont, Bardgett)

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
     * Comparação plan vs winner: para bater, precisa
       sortino > 1.3746 AND winner_conditions_met AND pct_time_above_benchmark_lh56y ≥ 0.95
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
       beats_winner = (
           sortino_lh56y > 1.3746
           and winner_conditions_met
           and pct_time_above_benchmark_lh56y >= 0.95
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
       | config | sortino_lh56y | edge_vs_1.3246 | WC | pct_time_above_benchmark_lh56y | beats_winner |
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
     feat(letf-loop): iter NNN — <slug> — Sortino X.XXX (edge ±YY) [tier_label]
   Body deve incluir:
     - KILL_LOOP pre-conditions: FIRED / NOT FIRED
     - beats_winner: true/false
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

# spy_beater_hunt — per-session prompt (50-iter loop)

This file is the **prompt template** the user pastes into each fresh Claude
Code session to drive ONE iteration of the hunt forward. The session
runs autonomously: research → develop → test → validate → record → commit
→ stop. Continuity across sessions lives in
`studies/spy_beater_hunt/BASE_MEMORY.md`.

Goal: 50 iterations cumulative. Stop early if any iter produces a WINNER
(all 3 strict bars met AND score ≥ 90).

**CURRENT STATE (2026-04-29 post-refactor)**:
- Datasets: `(lh_56y, spy_real)` — 1986+ synth + Tiingo SPY 2003+ real
- Bars: CAGR ≥ **11.21%**, MDD ≤ **55.17%**, gates ≥ 5/7 on each dataset
- Anchor ranges: CAGR 5%-20%, MDD 15%-70%, Sharpe 0.5-2.0
- Scoring criterion 6 = multi-horizon CAGR pass-rate vs SPY (5y/10y/15y/20y, 3+3+2+2pts)
- Iter 001 a1_lrs_split passed ALL 3 BARS (winner_conditions_met=True),
  PROMISING 60/100 — needs higher score for tier WINNER (≥90)
- Direction A2 faster-signal/buffer CLOSED via KILL #7/#8
- Direction A2 lower-leverage (2× SSO) is ACTIVE — closest to score 90+ frontier

---

## Copy-paste prompt for next session

```
Estamos rodando o spy_beater_hunt — uma vertente que tenta achar UMA estratégia
de longo prazo que bata o SPY EM CAGR (≥ 13.80% mean) E em MDD (≤ 40.85% mean)
E sobreviva ao 7-gate battery em ≥ 2/3 datasets. Meta: 50 iterações cumulativas
ou WINNER mais cedo. Cada sessão executa UMA iteração e para.

Você é um Claude novo, sem histórico — toda continuidade está em arquivos.

PASSO 1 — Ler estado em ORDEM (não execute nada antes):
  1. studies/spy_beater_hunt/BASE_MEMORY.md  ← PRIMEIRO. Estado do loop.
     Veja: total_iterations, latest_*, direction_status, closest_to_winner.
  2. studies/spy_beater_hunt/SPEC.md  ← bar conditions + gates + KILL conditions
  3. studies/spy_beater_hunt/PROMISING_DIRECTIONS.md  ← ranking de hipóteses
  4. studies/spy_beater_hunt/WINNER_AND_RANKING.md  ← scoring rubric
  5. studies/spy_beater_hunt/INFRASTRUCTURE.md  ← reuso da long_term_portfolio
  6. CLAUDE.md  ← regra 1 (jornada), regra 2 (citação obrigatória)
  7. Último iter: studies/spy_beater_hunt/iterations/<latest>/final_report.md
     (especialmente a section "Lesson")

PASSO 2 — Verificar baseline:
  cd /var/www/pessoal/ai-trade && source .venv/bin/activate
  pytest --collect-only -q 2>&1 | tail -3
  git log --oneline -5

PASSO 3 — Escolher próxima hipótese:
  Critérios de escolha (em ordem):
  (a) Se BASE_MEMORY.direction_status indica uma direção PROMISING não
      esgotada com lesson aplicável, esse é o próximo iter (variantes do
      closest_to_winner).
  (b) Senão, próxima Tier 1/2 não-fechada de PROMISING_DIRECTIONS.md.
  (c) Senão, exploração nova baseada em livros (cite [book.slug, p.X]).

  ATENÇÃO: respeite os KILL conditions já disparados. Se KILL #7+#8
  (faster signal/threshold) já fecharam, NÃO crie variantes desse tipo.

PASSO 4 — Pre-commit hypothesis (em iterations/NNN-YYYY-MM-DD-slug/):
  Crie hypothesis.md ANTES de rodar com:
   - Slug + cumulative n_trials antes/depois
   - Hipótese explícita citando livro
   - 4-6 configs com naming consistente (não inflar n_trials)
   - KILL conditions pré-comitadas (numere após o último usado:
     KILL #6, #7, #8, #9 já existem; novos seguem #10+)
   - Expected outcomes
   - INCOMPLETE flags (synth caveats etc.)

PASSO 5 — Implementação:
  - Se requer NEW módulo (e.g., novo synth, novo gate): TDD primeiro
    em tests/test_studies_spy_beater_hunt.py + impl no módulo
    apropriado. NUNCA quebrar 730+ tests baseline.
  - Se requer só novo backtest.py com configs existentes: skip TDD, vai
    direto pro driver.
  - Use studies.spy_beater_hunt.run_iter.run_iter_spy_beater(...) — ele
    já faz scoring + gates + plots. Não duplique.

PASSO 6 — Run + verify:
  PYTHONPATH=. python studies/spy_beater_hunt/iterations/NNN-.../backtest.py
  Resultados terminam impressos (Tier, Score, Bars, Per-dataset, All-configs).

PASSO 7 — Validar e escrever lesson:
  Edite manualmente final_report.md (gerado pelo run) substituindo a
  section "Lesson" "(Append after manual review.)" pelo seu diagnóstico:
   - Cada KILL listada em hypothesis.md → resultado (FIRED / NOT FIRED)
   - Closest-to-winner: qual config + gap em pp por bar
   - Direction implications (closed / promising / next iter ideas)
   - Citações [book.slug, p.X] em toda decisão

PASSO 8 — Update BASE_MEMORY.md:
   - Frontmatter: total_iterations++, cumulative_n_trials += N_CONFIGS,
     latest_iteration, latest_score, latest_tier, direction_status
     update conforme KILLs disparados, closest_to_winner se mudou.
   - Iteration log (newest first): bloco completo com config table,
     KILLs, key finding, citations.

PASSO 9 — Jornada (CLAUDE.md regra 1):
   - Crie jornada/YYYY-MM-DD-HHmm-spy-beater-iterNNN-<one-line>.md
     em linguagem humana (~200 palavras).
   - Adicione bullet em jornada/README.md sob "### 2026-04-29" (ou data
     apropriada) — newest first.

PASSO 10 — Commit:
  git add ...
  git commit -m "feat(spy_beater_hunt): iter NNN — <slug> <TIER> <score>/100 (<bars> bars)"
  Mensagem deve incluir: KILLs disparados, closest config, próximo passo
  sugerido. Conventional Commits style.

PASSO 11 — STOP. Não rodar próximo iter na mesma sessão. O usuário
abrirá nova sessão para iter NNN+1.

NOTA SOBRE COMPLEXIDADE:
- DSR n_trials inflaciona com cada iter (penalty cresce). Se DSR worst p
  > 0.05, considere 3-4 configs por iter ao invés de 6+ para slow down.
- Plots são gerados automaticamente pelo run_iter (5 PNGs: 3 overlays +
  scatter + heatmap). Se quiser plot custom, adicione ao plot_helper.py.

NOTA SOBRE TARGET 50 ITERS:
- BASE_MEMORY.target_total_iterations = 50.
- Se total_iterations atinge 50 sem WINNER: declarar
  IMPOSSIBILITY_RESULT, escrever FINAL_REPORT_spy_beater_failed.md,
  F1+SPLIT confirmado deploy. Mandate §1 unchanged.
- Se WINNER aparece antes: declarar winner em BASE_MEMORY.status,
  escrever FINAL_REPORT_spy_beater_winner.md, comparar vs F1+SPLIT,
  preparar mandate §7 override request.

CONFIRMAÇÃO ANTES DE COMEÇAR:
- Você leu os 6+ docs do PASSO 1?
- Verificou que pytest está em 730+ tests passing?
- Identificou que direção / configs vai testar?
Se sim, prossiga. Se algo não bate (KILL fired mas você quer testar
mesmo assim, ou pytest está vermelho), pare e reporte ao usuário.
```

---

## Notas operacionais

### Naming conventions

- Iter dir: `iterations/NNN-YYYY-MM-DD-<slug-with-dashes>/`
  (NNN é zero-padded 3 dígitos: 001, 002, ...)
- Config name: `<iter-letter><iter-num>_<feature-list>` (ex: `a3_2xsso_kmlm_off`)
- Iter-letter mapping: A1/A2/A3 = LRS family; B1/B2 = HFEA; C1/C2 = vol-target;
  D1/D2 = concentrated growth.

### When to KILL the entire hunt early

Halt before iter 50 if:
- 5 consecutive iters all FAIL (score < 40) — vertente exhausted
- 10 consecutive iters all PROMISING but no improvement on closest-to-winner
- KILL #6 fires globally (CAGR bar unreachable even at extreme leverage)

### When to extend past 50

If iter 48-50 shows steep improvement curve (closest-to-winner gap
shrinking <1pp per iter), bump target_total_iterations to 60.

### Mandate compliance

This hunt operates under mandate §1 MAINTENANCE MODE (2026-04-23). Any
WINNER candidate triggers a mandate §7 override request — same as
F1+SPLIT (which remains deploy fallback). Do NOT deploy mid-hunt.

### Citations canonical (loop-wide)

- `[leverage_for_the_long_run, ch.3-4, p.40-60]` Gayed LRS rationale
- `[risk_parity, ch.5, p.10]` Carlson cap-efficient stacking
- `[advances_fin_ml, p.208-211]` PBO via CSCV
- `[advances_fin_ml, p.222-223]` DSR with cumulative n_trials
- `[advances_fin_ml, p.196-202]` bootstrap CI
- `[advances_fin_ml, p.31-34]` cross-lib + factor framework
- HFEA Bogleheads 2019 (leveraged barbell)
- studies/_archive/ema_sma_threshold_nasdaq_real (prior project sweep)

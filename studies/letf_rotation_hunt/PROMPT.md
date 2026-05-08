# PROMPT — letf_rotation_hunt iteration protocol

## Per-iter steps

1. **Read** `BASE_MEMORY.md` (state-of-now), latest iter `verdict.json`, `KILL_RULES.md`, `WINNER_AND_RANKING.md`.
2. **Identify next iter** from BASE_MEMORY tier inheritance state. Determine sub-fase (T1a/T1b/.../T5d).
3. **Write** `iterations/NNN-YYYY-MM-DD-T<X><letter>-<slug>/config.yaml` with:
   - Inherited config from previous tier (or seed config if T1a)
   - Sub-fase configs to test
   - Datasets, signal params, OFF asset, decision freq
4. **Run** `python -m studies.letf_rotation_hunt.run_iter --iter NNN --config <path>`
   - Generates `verdict.json`, `SUMMARY.md`, plots, tables
   - Updates BASE_MEMORY.md
5. **Validate** `verdict.json` against schema (auto in run_iter).
6. **Update public docs** if verdict changes project state: `docs/CURRENT_STATE.md` and, for historical narrative, `docs/PROJECT_HISTORY.md`.
7. **Commit** with message `feat(letf-hunt): iter NNN - T<X><letter> <slug> - <verdict_summary>`.

## Inheritance rules

- Each tier reads tier_inheritance from BASE_MEMORY
- If prev tier KILL fired → use last valid winner (skip killed tier)
- Inheritance details captured in `verdict.json:tier_inheritance` field

## Pause/resume

Study pausável a qualquer ponto. Reabrir = ler BASE_MEMORY → próxima iter inferida pelo iter log + tier inheritance state.

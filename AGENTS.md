# Project instructions for Codex

Read `CLAUDE.md` (this directory) before taking any action. It contains
mandatory rules: citation policy (Regra 2), jornada/ update rule (Regra 1),
investment mandate summary, and coding conventions.

Key reminders:
- Working dir: `/var/www/pessoal/ai-trade`
- Python: `uv run python` (never bare `python`)
- Tests: `uv run pytest`
- NEVER `git commit` inside an agent — the loop orchestrator handles commits
- NEVER modify `docs/investment-mandate.md` inside an agent
- Tax model: `AnnualDarfEngine` from `studies/global_factor_tilt_loop/tax_engine_v2.py`

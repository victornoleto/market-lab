# Phase 3.5b — DO NOT CLEANUP

**Marcador de proteção contra o cleanup geral pós-Phase 3.5a-V2.**

---

## Status (2026-04-18)

Phase 3.5b está **finalizada e consolidada**. Toda a estrutura abaixo
foi revisada pelo usuário e está no estado definitivo:

- `PRODUCTION.md` — runbook operacional canônico (default threshold
  revisto de 5pp → 10pp em 2026-04-18; §10 extended-window 1986-2026;
  §11 rejected alternatives).
- `README.md` — index técnico atualizado com link para §10 e §11.
- `letf_rotation_ema100_2x/`, `qqq_donchian_20_10/`,
  `gld_donchian_40_20/`, `portfolio_3leg_ew/` — sleeves canônicos;
  imutáveis.
- `robustness/` — Tasks 7a-7f; imutáveis.
- `variants/` — Phase 3.5b-addendum (A/B/C); imutáveis.
- `extended_window_1986_2026/` — §10 headline finding; preservar.
- `threshold_sweep_full/` — §2 sweep 5/10/15/25/100pp; preservar.
- `rejected_alternatives/static_sso_zroz_gld/` — §11 decisão negativa;
  preservar como evidência documentada.
- `variants_letf_execution/` — ★★ §12 V4 promoted 2026-04-18 (gate
  verdict formal); README + gates_verdict.md + gates_verdict.json +
  equity/drawdown charts + summary.json.
- `summary.json` — consolidated metrics; imutável.

## Instruções para cleanup pós-V2

Quando o cleanup geral rodar após Phase 3.5a-V2:

1. **Não mexer em nada sob `reports/phase3_5b/`.**
2. **Não deletar scripts `run_phase3_5b_*.py`, `run_plano_b_*.py`,
   `run_static_sso_zroz_gld.py`, `run_a3d_3leg_portfolio.py`,
   `validate_phase3_winners.py`, `extract_testfolio_json.py`,
   `run_plano_b_variants_letf_execution.py`,
   `run_plano_b_variants_gates.py`.**
   Todos são reproducíveis para os artefatos acima.
3. **Não mexer em `src/market_lab/backtest/data/testfolio_loader.py`.**
4. **Não mexer em `data/testfolio/`** (raw JSON + cache parquet).
5. **Não mexer em jornadas `phase3.5b-*`** (history record).

## Jornadas relacionadas (imutáveis)

- `jornada/2026-04-17/24-phase3.5b-full-validation-summary.md`
- `jornada/2026-04-17/32-phase3.5b-addendum-summary.md`
- `jornada/2026-04-17/33-phase3.5b-addendum-task-c4-threshold-rebalance.md`
- `jornada/2026-04-18/04-phase3.5b-extended-window-PASS.md`
- `jornada/2026-04-18/05-phase3.5b-rejected-sso-zroz-gld.md`
- `jornada/2026-04-18/08-phase3.5b-V4-promoted-gate-verdict.md`
- `jornada/2026-04-18/16-phase3.5b-3x-variants-V5-V8-tested.md`

## Se precisar mexer (excepcionalmente)

Só modificar Phase 3.5b se:

1. **Bug genuíno** em um dos sleeves (improvável — 7 gates passados +
   extended window + supplementary rejection evidence).
2. **Mudança de broker** (Inter Global) impactando SSO/QQQ/GLD.
3. **Nova evidência empírica** (ex: ETF SSO delisted) que invalide
   um dos legs — aí documenta em novo jornada e atualiza
   `PRODUCTION.md` §6 FLAGs.

Em qualquer outro caso: **não tocar**.

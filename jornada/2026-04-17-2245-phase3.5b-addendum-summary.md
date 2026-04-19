# 2026-04-17 2245 — ★★ Phase 3.5b-addendum SUMMARY [PLANO B] [SWING BROKER] (Task D)

## Verdict

**PASS — addendum operacional CLOSED.** 3 investigações respondidas,
winner **inalterado**, indices criados. Loop `status: done`.

## O que o usuário perguntou (iter 15 → iter 23)

Phase 3.5b main fechou em `2026-04-17 10:58` (commit 4a732ce, iter 15)
com 4 winners PASS + robustness battery 7 tasks PASS. O usuário abriu
3 dúvidas operacionais pós-fechamento, todas respondíveis sem quebrar
o winner:

1. **E se eu dropar GLD e rodar só LETF+QQQ?** (2-leg EW)
2. **E se eu subir a alavancagem do LETF para 2.5× ou 3×?**
3. **E se eu rebalancear mensal (via venda ou via aporte) em vez de
   diário?**

Regra do addendum: **show all, flag failures** — nenhum gate bloqueia
report, tudo roda end-to-end, gates viram ⚠️ FLAGs em `flags.md`. Decisão
final fica com o usuário via tabela comparativa.

## O que saiu

### Task A — 2-leg LETF+QQQ EW (iter 16)

- Janela longest 2001-05-14 → 2026-04-14 (6266 bars, 24.87 anos).
- Sharpe **1.888**, CAGR 31.59%, MaxDD 14.41%, IR vs SPY 1.158.
- ⚠️ **DR 1.121 < 1.20** — doubling-down (ρ(LETF, QQQ) = 0.555, ambas
  long US equity). Blend beat LETF-alone em +0.11 Sharpe mas sem
  factor diversification — só deploy se broker bloquear GLD.
- Report: `reports/phase3_5b/variants/letf_qqq_2leg_ew/` (5 artefatos
  + `flags.md` explicando DR).
- Jornada: `2026-04-17-2100-phase3.5b-addendum-task-a-2leg-letf-qqq.md`.

### Task B — LETF leverage sweep 2× / 2.5× / 3× (iters 17-19)

| Leverage | CAGR   | Sharpe | MaxDD   | WF MaxDD gate | ETF real?      | Verdict          |
|----------|-------:|-------:|--------:|:-------------:|:--------------:|:----------------|
| **2×**   | 44.69% | 1.848  | 20.55%  | ✅ 8/8        | ✅ SSO (2006+) | ✅ prod default |
| 2.5×     | 58.89% | 1.882  | 24.65%  | ✅ 8/8 (0.35 pp WF1) | ❌ none   | ⚠️ theory-only  |
| 3×       | 74.17% | 1.910  | 28.45%  | ❌ 5/8 (WF1/2/7) | ✅ UPRO (2009+) | ⚠️ FAIL gate |

Sharpe praticamente flat (+0.062 span); CAGR escala linear (+15 pp por
+0.5×), MaxDD idem (+4 pp por +0.5×). O CAGR extra é **prêmio de risco
puro** — nada mudou risk-adjusted. Sub-index
`reports/phase3_5b/variants/letf_leverage_comparison/README.md` tem
tabela WF MaxDD × leverage × window.

- Script reusável: `scripts/run_phase3_5b_letf_leverage_variant.py
  --leverage {2.5,3.0}` (B1 é symlink reuse do winner).
- Jornadas: `2026-04-17-2115-task-b1-letf-2x-reuse.md`,
  `-2130-task-b2-letf-2_5x-synthetic.md`,
  `-2145-task-b3-letf-3x.md`.

### Task C — Rebalance modes (iters 20-22)

Módulo novo
[`src/ai_trade/backtest/metrics/rebalance_modes.py`](../src/ai_trade/backtest/metrics/rebalance_modes.py)
(~320 loc, 3 funções puras — `apply_daily_rebalance`,
`apply_monthly_sell_rebalance`, `apply_monthly_cashflow_rebalance`) +
28 testes unitários. Pytest **670 → 698** (+28), zero regressão.

3-leg EW {LETF+QQQ+GLD} (janela 2004-11-18 → 2026-04-14, 21.36 yrs):

| Mode             | Sharpe | MaxDD   | Events/yr | IR/yr    |
|------------------|-------:|--------:|----------:|---------:|
| daily (winner)   | **2.108** | **10.86%** | 0.0       | $0       |
| monthly_sell     | 1.964  | 10.94%  | 17.9      | $30 740  |
| monthly_cashflow | 1.944  | 17.78%  | 0.0       | $0 (dep) |

2-leg EW {LETF+QQQ} (janela 2001-05-14 → 2026-04-14, 24.87 yrs):

| Mode             | Sharpe | MaxDD   | Events/yr | IR/yr     |
|------------------|-------:|--------:|----------:|----------:|
| daily (Task A)   | **1.888** | **14.41%** | 0.0   | $0        |
| monthly_sell     | 1.800  | 14.46%  | 12.1      | $144 794  |
| monthly_cashflow | 1.881  | 18.15%  | 0.0       | $0 (dep)  |

**Achados-chave:**

- `daily > sell > cashflow` no 3-leg em Sharpe, mas `daily ≈ cashflow
  > sell` no 2-leg — com ρ=0.555 as duas pernas co-movem e o drift
  típico cai (mean_sell 0.60% vs 0.82% no 3-leg).
- **Paradoxo 4.7× IR:** monthly_sell no 2-leg paga $144 k/yr vs $30 k/yr
  no 3-leg. Três drivers: (a) notional maior por perna (50% vs 33%),
  (b) janela mais longa com ganhos acumulados maiores, (c) sem GLD
  "drenando ganhos". Sell é dominado por daily em todos os cenários.
- **Cashflow não é upgrade — é fallback ergonômico.** Só o 2-leg
  preserva Sharpe; 3-leg cai −0.164 e MaxDD explode +6.92 pp porque
  $500/mo é insignificante vs equity ao longo do tempo.

Sub-index: `reports/phase3_5b/variants/rebalance_modes/README.md`
(inclui hipótese C3 confirmação parcial) +
`implementation_notes.md` (cost basis, month-end detection, deposit
allocation).

- Jornadas: `2026-04-17-2200-task-c1-rebalance-modes-module.md`,
  `-2215-task-c2-rebalance-3leg.md`,
  `-2230-task-c3-rebalance-2leg.md`.

### Task D (este doc) — indices + summary (iter 23)

- Criado `reports/phase3_5b/README.md` (main index) com TL;DR,
  winners table, 7 tasks robustness, addendum variants table, directory
  map.
- Criado `reports/phase3_5b/variants/README.md` (sub-index) com tabela
  all-in 9 rows (winner + 8 variants), explainer inline do DR, production
  recommendation.
- Atualizado `jornada/2026-04-17-2045-phase3.5b-full-validation-summary.md`
  com seção "Operational variants (addendum 2026-04-17)" no fim
  (tabela consolidada + decisão final + links).
- Zero código tocado nesta iteração; pytest **698** mantido.

## Decisão final (consolidada)

**Production default permanece 3-leg EW daily**, Sharpe 2.108, MaxDD
10.86%, CAGR 25.56% na janela 2004-11-18 → 2026-04-14 (21.36 yrs).

**Variantes que sobrevivem como alternativa condicional:**

- **C₃ (2-leg + monthly_cashflow $500/mo)** — fallback ergonômico para
  usuário com broker sem GLD e preferência DCA. Sharpe 1.881
  (~0.27 abaixo do winner), tax-free no rebal layer, MaxDD 18.15%
  (+7.29 pp vs winner).
- **B₃ (LETF 3×)** — escalation lever *opt-in* só com overlay manual
  (Kelly < 0.5× ou regime-conditional). Não promover à prod.

**Variantes rejeitadas:**

- A (2-leg daily) dominada por W em Sharpe e MaxDD (mesmo sem DR).
- B₂ (2.5× sintético) não existe como ETF BR → impossível deploy.
- C₁/C₂/C₄ (monthly_sell e cashflow-3leg) dominadas por daily.

## Cumprimento do spec

`specs/phase_3_5b_addendum_operational.md` Task D checklist:

- [x] `reports/phase3_5b/README.md` com TL;DR + winners table + links +
      seção "Operational variants (addendum)".
- [x] `reports/phase3_5b/variants/README.md` com tabela all-in e
      explainer do DR (Choueifaty-Coignard).
- [x] Seção "Operational variants (addendum 2026-04-17)" adicionada ao
      `jornada/2026-04-17-2045-phase3.5b-full-validation-summary.md`.
- [x] Jornada dedicada (este doc).
- [x] `memory.md` `status: done` (iter 23).

## Pytest baseline

670 (iter 15, Phase 3.5b main close) → **698** (iter 20, Task C1) →
**698** (iter 23, este doc, zero código). Zero regressão, zero
flakiness, winners imutáveis preservados durante todas as 8 iterações do
addendum.

## Citações

- Naive EW robustness: `[advances_fin_ml, p.298-299]`.
- DR (Choueifaty-Coignard 2008): `[advances_fin_ml, p.310]`.
- LETF synthetic formula e grid: `[leverage_for_the_long_run, p.16-17, Table 8]`.
- Vol-drag com L²: `[leverage_for_the_long_run, p.7-9]`.
- BR 15% IR realized gains: `docs/investment-mandate.md` §4.
- WF MaxDD ≤ 25% gate: `docs/investment-mandate.md` §5.

## Próximo passo

Loop Phase 3.5b-addendum FECHADO. Handoff para:

- **Phase 3.5a** (branch paralela) — busca de Strategy A short-hold
  CFD para Plano A Pepperstone.
- **Phase 4 paper trading Plano B** — deploy do 3-leg EW daily em
  conta broker BR ($10k equivalente, monitor ρ 252d ≥ 0.70 × 3 por
  ≥ 10 barras como alerta — evento inédito em 21 anos).

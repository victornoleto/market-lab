# Spec — Phase 3.5b Addendum: Operational Variants

Addendum ao `specs/phase_3_5b_winners_validation.md` focado em **variantes
operacionais** para responder 3 dúvidas do usuário pós-conclusão da Phase 3.5b
principal:

1. **Rebalance mensal via aportes (cashflow-based)** é viável? Quão pior fica
   vs daily? Quantos eventos tributários evita?
2. **2-leg portfolio (LETF+QQQ, sem GLD)** — quais métricas completas, mesmo
   sabendo que falhou DR no Phase 3?
3. **LETF em 2x/2.5x/3x** (não só 2x) — métricas completas, mesmo quando
   falham gates (MaxDD, DR). Regra: **show all, flag failures**.

**Branch:** continua em `phase3.5b/winners-validation-20260417` (mesma branch).

**Execução:** loop autônomo `scripts/self_improve_loop.sh
CLAUDE_MODEL=claude-opus-4-7 MAX_ITER=10 SCOPE=code`.

---

## 0. Regras invioláveis deste addendum

- **Nenhum gate bloqueia report.** Toda config roda end-to-end, gera
  `standard_report.md` + `trade_log.{csv,md}` + `equity_curve.png` +
  `summary.json` + `flags.md` listando quais gates falharam e por quê.
- **SPY benchmark obrigatório** em todo report (mesma regra Phase 3.5b).
- **Winners imutáveis** — o 3-leg EW com 2x LETF + daily rebalance continua
  sendo o production default. Addendum produz **alternativas informadas**, não
  substitutos.
- **NÃO modificar LÓGICA** das strategies ou do `portfolio_3leg.py` — só
  adicionar módulo novo `rebalance_modes.py` + scripts de execução.
- Citação `[book.slug, p.X]` obrigatória.
- Tag `[PLANO B]` / `[SWING BROKER]` em jornada headers.

---

## 1. Report structure (obrigatória)

```
reports/phase3_5b/
├── README.md                             # ★ NEW — main index + TL;DR + links
├── summary.json                          # existente (mantido)
├── letf_rotation_ema100_2x/              # existente
├── qqq_donchian_20_10/                   # existente
├── gld_donchian_40_20/                   # existente
├── portfolio_3leg_ew/                    # existente
├── robustness/                           # existente
└── variants/                             # ★ NEW
    ├── README.md                         # ★ sub-index comparativo
    ├── letf_qqq_2leg_ew/                 # Task A
    │   ├── standard_report.md
    │   ├── trade_log.csv
    │   ├── trade_log.md
    │   ├── summary.json
    │   ├── equity_curve.png
    │   └── flags.md                      # DR 1.124 < 1.2 explained
    ├── letf_leverage_comparison/         # Tasks B1/B2/B3 consolidados
    │   ├── README.md                     # tabela 2x vs 2.5x vs 3x
    │   ├── letf_ema100_2x/               # symlink ou reuso de letf_rotation_ema100_2x
    │   ├── letf_ema100_2_5x/             # ★ sintético-only flag
    │   └── letf_ema100_3x/               # ★ MaxDD flag
    └── rebalance_modes/                  # Tasks C1/C2/C3
        ├── README.md                     # tabela comparativa drift × tax × perf
        ├── comparison_3leg.md            # 3 modes × 3-leg portfolio
        ├── comparison_2leg.md            # 3 modes × 2-leg portfolio
        └── implementation_notes.md       # detalhes do algoritmo cashflow
```

---

## 2. Tasks

### Task A — 2-leg LETF+QQQ EW full report

- [ ] Rodar `validate_phase3_winners.py` (ou extensão) com config 2-leg EW no
      `portfolio_combiner.py` (Phase 3 A3c). Janela longest 2001-05-14 →
      2026-04-14 (6266 bars, QQQ-limited).
- [ ] Gerar `reports/phase3_5b/variants/letf_qqq_2leg_ew/`:
      `standard_report.md`, `trade_log.{csv,md}`, `summary.json`,
      `equity_curve.png`, **`flags.md`** explicando:
      - DR = 1.124 (medido) vs threshold 1.2 → ⚠️ FAIL
      - Por quê: ρ(LETF,QQQ) = 0.555, ambos equity US → doubling-down, não
        diversificação genuína.
      - OOS Sharpe 2.098 > baseline LETF-only 1.990 (+0.108) — edge adicional
        existe mas marginal.
      - Comparar side-by-side com 3-leg EW: Sharpe 2.108 (3-leg) vs 2.098
        (2-leg) → 3-leg ganha principalmente em MaxDD (menor) e DR.
- [ ] Jornada `<date>-phase3.5b-addendum-task-a-2leg-letf-qqq.md` [PLANO B].
- **Conclusion:** _(preencher)_

### Task B — LETF 2x / 2.5x / 3x comparison

- [ ] B1 (2x baseline) — reusar métricas já produzidas em
      `reports/phase3_5b/letf_rotation_ema100_2x/`. **Não re-rodar.** Apenas
      copiar/linkar no sub-index.
- [ ] B2 (2.5x sintético) — `synthesize_letf_returns(spx_tr, L=2.5, fee=0.01)`.
      Rodar `letf_rotation` EMA100 band=0% lev=2.5x. Gerar report completo em
      `reports/phase3_5b/variants/letf_leverage_comparison/letf_ema100_2_5x/`.
      **Flag em `flags.md`:** "Não existe ETF 2.5x real. Sintético apenas —
      impossível deploy em Plano B swing broker BR. Valor: só para gradient
      entre 2x e 3x."
- [ ] B3 (3x) — rodar EMA100 band=0% lev=3x, janela SPX TR 1970-2026. Gerar
      report completo. **Flag em `flags.md`:**
      - MaxDD full-window (medir).
      - MaxDD por janela WF: se > 25% em qualquer janela, listar quais e
        valores. Gate Phase 3 B1c rejeitou 3x por este motivo.
      - OOS Sharpe esperado ~1.781 (B1c iter 32 mediu este valor antes da
        rejeição por MaxDD).
      - ETF real: UPRO (ProShares) pós-2009-06; SPXU pré-2009 só sintético.
- [ ] **Sub-index `reports/phase3_5b/variants/letf_leverage_comparison/README.md`:**
      tabela side-by-side 2x/2.5x/3x com colunas: CAGR, Sharpe, MaxDD,
      MaxDD WF (max janela), Gates passed, Availability (real ETF?), FLAGs.
- [ ] Jornada `<date>-phase3.5b-addendum-task-b-letf-leverage-variants.md`
      [PLANO B].
- **Conclusion:** _(preencher)_

### Task C — Rebalance modes (daily vs monthly-sell vs monthly-cashflow)

- [ ] **C1 — Implementar `src/ai_trade/backtest/metrics/rebalance_modes.py`**
      com 3 funções puras de retorno-série que tomam o equity curve e weights
      target e aplicam o rebalance:
      - `apply_daily_rebalance(returns_df, weights)` — reuso do atual (EW
        recalc a cada bar close).
      - `apply_monthly_sell_rebalance(returns_df, weights, freq='M')` — no
        último dia útil de cada mês: vender excess, comprar deficit, pagar 15%
        IR BR sobre ganhos realizados nas vendas.
      - `apply_monthly_cashflow_rebalance(returns_df, weights, monthly_deposit,
        freq='M')` — a cada mês, depositar `monthly_deposit` e **alocar
        100% do depósito para a perna mais subponderada** (no-sell).
        Parametrizar `monthly_deposit` (default 0.5% do capital inicial, ~$50
        para $10k).
      - Cada função retorna: daily equity curve, daily weights, list of
        taxable events (for sell-based modes), drift series (daily |actual_w
        − target_w| por perna).
- [ ] **C1 — Testes unitários** em `tests/test_rebalance_modes.py`: mínimo 15
      testes cobrindo (a) daily == baseline exato; (b) monthly-sell sem
      aportes mantém drift pequeno + eventos tributários = rebalance dates;
      (c) monthly-cashflow com drift inicial converge target; (d) edge cases
      (zero deposit, negative returns, all-equal weights).
- [ ] **C2 — Comparação 3-leg EW** em
      `reports/phase3_5b/variants/rebalance_modes/comparison_3leg.md`:
      - Tabela 3×N: modes vs {CAGR, Sharpe, MaxDD, Max drift %, # taxable
        events/ano, IR paid/ano}.
      - Plot: evolução drift-per-leg ao longo de 21 anos.
      - Conclusão: qual mode é "good enough" vs daily ideal?
- [ ] **C3 — Comparação 2-leg EW** (LETF+QQQ): repetir C2 em
      `comparison_2leg.md`. Hipótese: 2-leg menos sensível a drift porque
      correlação alta = pernas movem juntas.
- [ ] Jornada `<date>-phase3.5b-addendum-task-c-rebalance-modes.md` [PLANO B].
- **Conclusion:** _(preencher)_

### Task D — Main index `reports/phase3_5b/README.md` + summary jornada update

- [ ] Criar `reports/phase3_5b/README.md` como **main index** com:
      - TL;DR 1 parágrafo do Phase 3.5b principal.
      - Tabela "winners oficiais" (4 sleeves + portfolio).
      - Link para cada sub-diretório com 1-line summary.
      - Seção **"Operational variants (addendum)"**: tabela comparativa e
        link para `variants/README.md`.
- [ ] Criar `reports/phase3_5b/variants/README.md` com:
      - Tabela all-in: {2-leg LETF+QQQ, 3-leg default, LETF 2x/2.5x/3x,
        rebalance modes 3×2} × {CAGR, Sharpe, MaxDD, gates passed/failed,
        availability, recommended?}.
      - Explicação inline do DR (Choueifaty-Coignard) pro usuário.
- [ ] Atualizar
      `jornada/2026-04-17-2045-phase3.5b-full-validation-summary.md`:
      adicionar seção **"Operational variants (addendum 2026-04-17)"** no
      fim com:
      - Links para os 3 novos sub-reports.
      - Tabela resumida.
      - Decisão final: qual variant é "safe to deploy" ou "only theoretical".
- [ ] Jornada `<date>-phase3.5b-addendum-summary.md` [PLANO B] consolidando
      findings.
- [ ] Flip memory.md `status: done` (novamente).
- **Conclusion:** _(preencher)_

---

## 3. Gates e regras invioláveis (mesmas do principal)

- Pytest baseline 670 passed. Não pode quebrar. Novos testes bem-vindos.
- NÃO modificar lógica strategies — só adicionar módulos novos.
- SPY benchmark obrigatório em todo report.
- IR 15% BR por venda lucrativa.
- Swap = 0 (Plano B).
- Citação obrigatória.

---

## 4. Budget & ETA

- **Iter budget:** 10 iters cap.
- **Tempo estimado:** ~1h20 com Opus 4.7.
- **Tasks críticas (code-heavy):** C1 (módulo rebalance) + D (sumários).
- **Tasks leves (só run + writeup):** A, B1, B2, B3, C2, C3.

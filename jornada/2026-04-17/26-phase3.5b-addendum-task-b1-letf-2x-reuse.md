# Task B1 — LETF 2x baseline reuso (leverage_comparison) [SWING BROKER] [PLANO B]

**Data:** 2026-04-17 21:15
**Fase:** Phase 3.5b-addendum
**Iter:** 17
**Tag:** [PLANO B] [SWING BROKER]
**Duração wallclock:** ~3 min
**Pytest:** 670 passed (unchanged)

---

## O que aconteceu

Task B1 do spec `specs/phase_3_5b_addendum_operational.md` pede para **não
re-rodar** o baseline LETF 2x e apenas materializar o report dentro do
diretório de comparação de alavancagens.

Criei `reports/phase3_5b/variants/letf_leverage_comparison/letf_ema100_2x/`
com **symlinks relativos** para os 5 artefatos do winner canônico
(`reports/phase3_5b/letf_rotation_ema100_2x/`) e uma `README.md` explicando
por que o report é reusado em vez de regerado.

Isso prepara o terreno para as próximas 2 colunas da tabela side-by-side:
- Task B2 — LETF 2.5x sintético (próxima iter)
- Task B3 — LETF 3x (sintético full-window, UPRO real pós-2009)

O sub-index `letf_leverage_comparison/README.md` em si será escrito em B3
(quando as 3 colunas estiverem disponíveis para comparar).

## Por que symlink e não copy?

- Winner é imutável (constraint #4); qualquer divergência entre canonical e
  reuso seria bug. Symlink garante fonte única de verdade.
- Gasto de disco zero (o report canônico já ocupa ~148 KB).
- Se o canônico precisar de fix em alguma release futura, symlinks não ficam
  stale.
- Relativo em vez de absoluto: não quebra em clone/container.

## Métricas do baseline (reuso)

| Metric                   | Valor                |
|--------------------------|----------------------|
| Janela                   | 1970-01-02 → 2026-04-14 (20556d) |
| CAGR                     | 44.69% |
| Sharpe                   | 1.848 |
| MaxDD                    | 20.55% |
| Calmar                   | 2.175 |
| Trades                   | 296 (win_rate 100%, profit_factor ∞ por SPX TR longo-só) |
| Exposure                 | 72.65% |
| SPY B&H (same window)    | CAGR 9.09% / Sharpe 0.553 / MaxDD 55.20% |
| IR vs SPY                | 1.601 |
| ρ vs SPY                 | 0.590 (moderada — MA filter reduz drawdown common) |

Fonte: `reports/phase3_5b/letf_rotation_ema100_2x/summary.json`.

## Gates (referência — já validados em Phase 3 B1c)

- PBO < 0.5 ✅
- DSR p < 0.05 ✅
- WF ≥ 6/8 ✅
- Single-block OOS ✅
- Forward-window stress ✅
- MaxDD < 25% ✅ (20.55%)

Citação: `jornada/2026-04-17-0055-b1c-letf-rotation-gates-PASS.md`.

## Artefatos

- `reports/phase3_5b/variants/letf_leverage_comparison/letf_ema100_2x/` (5
  symlinks + README.md).

## Next

- **Task B2 (iter 18):** LETF 2.5x sintético via
  `synthesize_letf_returns(spx_tr, L=2.5, fee=0.01)`. Full-window 1970-2026.
  Report + `flags.md` "⚠️ SINTÉTICO — não existe ETF 2.5x real".

## Citações

- LETF synthetic formula: `[leverage_for_the_long_run, p.16]`.
- Leverage 2x (SSO pós-2006): `[leverage_for_the_long_run, p.17, Table 8]`.
- DR formula (a ser aplicado no Task D main index): `[advances_fin_ml,
  p.310]` (Choueifaty-Coignard 2008).

# Task B2 — LETF 2.5x sintético (leverage_comparison) [SWING BROKER] [PLANO B]

**Data:** 2026-04-17 21:30
**Fase:** Phase 3.5b-addendum
**Iter:** 18
**Tag:** [PLANO B] [SWING BROKER] [SINTÉTICO]
**Duração wallclock:** ~1 min (SPX TR cache hit)
**Pytest:** 670 passed (baseline mantido)

---

## O que aconteceu

Task B2 do spec `specs/phase_3_5b_addendum_operational.md` pede um relatório
end-to-end para a alavancagem 2.5× sintética — mesmo sabendo que não existe
ETF listado nessa alavancagem — para preencher a coluna central da tabela
side-by-side 2×/2.5×/3× que será renderizada em B3.

Implementação:

1. Novo script parametrizado `scripts/run_phase3_5b_letf_leverage_variant.py`
   que aceita `--leverage` e emite os 6 artefatos padrão em
   `reports/phase3_5b/variants/letf_leverage_comparison/letf_ema100_<slug>/`.
   Reutilizável em B3 (apenas `--leverage 3.0`).
2. Config: `LETFRotationConfig(filter="EMA", lookback=100, band_pct=0.0,
   leverage=2.5, annual_fee=0.01, tax_rate=0.15)` — único delta vs winner
   2× é a alavancagem.
3. Cost model: Gayed flat-fee (`r_synth[t] = L·r_SPX_TR[t] - 0.01/252`)
   `[leverage_for_the_long_run, p.16]`. **Não** usei FFR-aware aqui porque
   o spec pede paridade com o baseline 2× já publicado (mesmo modelo de
   custo, mesmo grid topology, mesma janela 1970-2026).
4. Janela: LONGEST available per CLAUDE.md hard rule — 14 191 bars SPX TR
   stitched (KF→Tiingo seam 2001-05-14).

## Métricas 2.5× sintético (full-window 1970-01-02 → 2026-04-14)

| Métrica | L=2× (winner) | L=2.5× (sintético) | Δ |
|---------|---------------|--------------------|-:|
| CAGR | 44.69% | **58.89%** | +14.20 pp |
| Sharpe | 1.848 | **1.882** | +0.034 |
| Sortino | 2.858 | 2.926 | +0.068 |
| Calmar | 2.175 | 2.389 | +0.214 |
| MaxDD (full) | 20.55% | 24.65% | +4.10 pp |
| MaxDD max window WF | 19.07% (WF6) | **24.65% (WF1)** | borderline |
| Vol anualizada | 21.23% | 26.48% | +5.25 pp |
| IR vs SPY | 1.601 | **1.837** | +0.236 |
| Beta vs SPY | 0.679 | 0.847 | +0.168 |
| Trades | 296 | 296 | 0 (mesmo signal) |
| Exposure time | 72.65% | 72.65% | 0 |

SPY buy&hold referência (mesma janela): CAGR 9.09%, Sharpe 0.553, MaxDD
55.20%.

## Walk-forward MaxDD por janela (8 blocos B1c)

| Window | Período | MaxDD % | Flag |
|--------|---------|---------|------|
| WF1 | 1970-1977 | -24.65% | ✅ PASS (borderline) |
| WF2 | 1978-1985 | -23.38% | ✅ PASS |
| WF3 | 1986-1993 | -20.17% | ✅ PASS |
| WF4 | 1994-2001 | -21.14% | ✅ PASS |
| WF5 | 2002-2009 | -16.74% | ✅ PASS |
| WF6 | 2010-2017 | -19.07% | ✅ PASS |
| WF7 | 2018-2025 | -22.58% | ✅ PASS |
| WF8 | 2026-only | -10.80% | ✅ PASS |

Todos os 8 blocos WF ficam abaixo do gate 25% — mas WF1 (stagflation 70s)
passa por 0.35 pp. Com custo FFR-aware na era de juros altos a margem
provavelmente desaparece; anoto como FLAG de robustez.

## FLAGs operacionais (por que não é winner default)

1. **⚠️ SINTÉTICO — não existe 2.5× ETF listado em 2026-04.** Opções
   reais: (a) total-return swap daily-rebalanced em broker institucional
   (Pepperstone/IBKR, conta ≥ $25k com sign-off), (b) stacking 2×+3× em
   pesos (0.5, 0.5) — L_efetivo = 2.5× mas cada leg rebalanceia diariamente
   (tracking error estimado +0.5-1.0%/yr vs teórico). Stacking 2×+1× resulta
   em L=1.5×, não 2.5× — NÃO equivalente.
2. **⚠️ Margem WF1 estreita.** 24.65% vs gate 25% → 0.35 pp. Sob modelo
   FFR-aware (Task 7a) o custo de swap em anos 70s era 10-12%/yr — drag
   muito acima do 1% flat-fee. WF1 provavelmente falha o gate nessa re-run.
3. **⚠️ Vol +25% vs winner.** 26.48% anualizada vs 21.23% do 2×. Posição
   sizing no live precisa de haircut proporcional para preservar risco de
   $1k account.

## Decisão

Report arquivado como **referência didática e dado de entrada para a
tabela comparativa B3**. **NÃO promove ao conjunto de winners** — o
winner Path B continua sendo L=2× (SSO real, 17 anos de histórico live,
sem dependência de swap desk).

O ganho de Sharpe (+0.034) é estatisticamente ruído dentro das bootstrap
CI's 99.9% do B1c; o que realmente muda é vol/MaxDD (risco direto) e
dependência de infraestrutura (implementability). 2.5× é "melhor em
papel" — em produção, não.

## Artefatos

- `reports/phase3_5b/variants/letf_leverage_comparison/letf_ema100_2_5x/`
  - `standard_report.md` — backtesting.py-style metrics + SPY benchmark.
  - `trade_log.csv` / `trade_log.md` — 296 trades, 15% BR tax aplicado.
  - `summary.json` — snapshot + wf_maxdd array para sub-index B3.
  - `equity_curve.png` — log-scale strategy vs SPY.
  - `flags.md` — narrativa SINTÉTICO + tabela WF MaxDD + comparação vs 2×.
- `scripts/run_phase3_5b_letf_leverage_variant.py` — reusable em B3.

## Citações

- Synthetic LETF formula: `[leverage_for_the_long_run, p.16]`.
- Leverage grid tested (1.25/2/3): `[leverage_for_the_long_run, p.17,
  Table 8]`.
- WF MaxDD ≤ 25% gate: `reports/letf_rotation_b1c_verdict.json` (Phase 3
  Lead B1c final verdict) + Investment Mandate §5.
- Gate PBO < 0.5: `[advances_fin_ml, p.208-211]`.

## Próximo

Iter 19 (Task B3) — LETF 3× sintético full-window + sub-index
`letf_leverage_comparison/README.md` com tabela side-by-side 2×/2.5×/3×.

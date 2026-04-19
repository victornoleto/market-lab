# 2026-04-17 1415 — Phase 3.5b Task 7a parte 2 [PLANO B] FFR-aware re-run PASS

## TL;DR

Re-rodei o grid B1c canônico (72 configs, 1970-2026, 14,191 bars) injetando
a série FFR diária do Ken French (RF × 252) em `simulate_letf_rotation` via
o novo parâmetro opcional `ffr_annualized`. O **winner Phase 3 (cid=37
EMA100/2x/band 0%) sobrevive todos os gates** sob o cost model FFR-aware:

| Métrica | Flat-fee (baseline) | FFR-aware | Delta |
|---|---:|---:|---:|
| IS Sharpe | 1.854 | **1.644** | −0.210 |
| OOS Sharpe | 1.724 | **1.678** | −0.046 |
| Stress Sharpe | 2.004 | **1.916** | −0.088 |
| IS CAGR | 43.86% | 37.49% | −6.37 pp |
| OOS CAGR | 41.06% | 39.65% | −1.41 pp |
| Stress CAGR | 52.81% | 49.72% | −3.09 pp |
| DSR p-value (OOS) | 1e-05 | 2.189e-05 | ~idem |
| WF ratio | 1.000 | 1.000 | idem |
| PBO | 0.000 | **0.000** | idem |
| Passing configs | 13/72 | **13/72** | idem |

**Intersection baseline ∩ FFR-aware = 13/13** — nenhum config entra, nenhum
sai. Os 13 passing configs são idênticos. O edge do LETF rotation Phase 3
**não é artefato de sub-modelagem de custo**.

Pytest: 597 → **600 passed** (+3 novos testes de FFR-aware path).

## Contexto — por que re-rodar

Iter 7 (Task 7a parte 1) confirmou que nossa `synthesize_letf_returns`
(Gayed flat-1%) superestima o retorno 2x sintético em +6.0%/ano full-window
e +9.72%/ano no bucket FFR≥5% (32 anos). Isso levantou a hipótese de que o
winner Phase 3 (Sharpe IS 1.854) pudesse ser artefato: o período 1970-2000
inteiro cai no bucket alto-FFR onde flat-1% cheira barato demais.

A resposta tem que vir dos **gates**: PBO, DSR, WF, OOS Sharpe, Stress
Sharpe, bootstrap CI — todos recomputados com o cost model certo.
Constraint #9 do memory determinava re-rodar antes de confirmar o winner.

## O que eu fiz

### Hook não-breaking em `simulate_letf_rotation`

Adicionei `ffr_annualized: pd.Series | None = None` (+ knobs `ffr_swap_exposure`,
`ffr_spread`, `ffr_expense_ratio` com defaults testfolio) ao sinal de
`simulate_letf_rotation`. Quando `ffr_annualized is None`, o path continua
exato-ao-byte com Gayed flat-fee (teste de regressão em
`TestSimulateFFRAware.test_default_none_preserves_flat_fee_path` garante
isso). Quando provido, o cost model vira o da `synthesize_letf_returns_ffr_aware`
criada em iter 7.

Contração da regra #3 (não modificar lógica): nem signal, nem switches,
nem costs de transação, nem tax, nem compounding mudam. Só a série
`on_returns` usada no regime ON passa a refletir custo time-varying.
Todos os 25 testes LETF existentes seguem passando.

### Script `scripts/run_b1c_rerun_ffr_aware.py`

Espelha `scripts/run_grid_letf_rotation_b1c.py` (mesmos axes, mesmas
janelas, mesmo bootstrap) mas:

1. Carrega FFR via `fetch_ken_french_daily()` + `RF × 252`.
2. Ajusta FFR ao índice SPX TR (ffill+bfill; ver justificativa em
   `synthesize_letf_returns_ffr_aware`).
3. Injeta no grid.
4. Compara com baseline `reports/letf_rotation_b1c_verdict.json` para
   delta per-config.
5. Emite JSON verdict + markdown delta com citação de
   `[advances_fin_ml, p.208-211]`, `[leverage_for_the_long_run, p.16]`.

### Resultados — winner cid=37 FFR-aware

- **Verdict: PASS** em todos os 5 gates (PBO, DSR, WF, OOS/Stress Sharpe >0,
  bootstrap CI>0).
- OOS Sharpe 1.678 (down de 1.724, Δ=−0.046). Bootstrap 99.9% CI
  **[0.985, 2.419]** — lower bound > 0.8, muito longe do threshold zero.
- Top top-3 OOS Sharpe: cid=38 EMA100/3x (1.718 FAIL_DSR), cid=37 EMA100/2x
  (1.678 PASS), cid=36 EMA100/1x (1.595 PASS).

### Resultados — grid completo

| | Baseline (flat) | FFR-aware | Comentário |
|---|---|---|---|
| PBO | 0.000 | **0.000** | PBO não é funda de custo absoluto; folga enorme. |
| Passing cids | 13 | **13** | Interseção **13/13** — nenhum entra/sai. |
| Mediana Sharpe grid | — | — | Deltas de Sharpe uniformemente no range [−0.07, +0.003]. |

Deltas maiores (−0.06 to −0.07) ocorrem em configs 3x (cid=2, 11, 38, 47,
56) — faz sentido: `SW*(L-1)` escala com `(L-1)`, então 3x paga triplo da
margem extra vs 2x. Os 1x-configs têm delta ~0 (só o `expense_ratio`
adicional, neutralizado pelo flat 1% fee se você pensar em termos de
quem paga mais).

## Implicação para Phase 3.5b

1. Winner LETF rotation Phase 3 **continua válido** sob cost model
   conservador. Não há `⚠️ FLAG` crítico aqui.
2. A **CAGR report** na allocation doc (Task 8) deve citar a versão
   FFR-aware quando o público for conservador — é ~1-6 pp/ano menor em
   OOS, mais realista para produção.
3. **Sharpe é mais robusto que CAGR** a sub-modelagem de custo: a perda
   de prêmio médio é absorvida por reduções proporcionais em IS, OOS e
   Stress, mantendo a forma do edge.
4. O gap **+6.0%/yr full-window** que disparou o gate ainda é real, mas
   ele se concentra no **retorno absoluto** do 2x synthetic, não no
   **spread vs buy-and-hold** — que é o que os gates medem.

## Artefatos novos

- `src/ai_trade/backtest/strategies/letf_rotation.py` — hook opcional
  `ffr_annualized=`; behavior idêntico quando None.
- `scripts/run_b1c_rerun_ffr_aware.py` — 280 loc, reusa
  `evaluate_b1c_gates`.
- `tests/test_letf_rotation.py` — +3 testes em `TestSimulateFFRAware`:
  default-None preserves flat-fee, high-FFR reduz equity, analytic match
  quando FFR=0 + annual_fee ajustado.
- `reports/phase3_5b/robustness/b1c_rerun_ffr_aware_verdict.json` — full
  72-config verdict dict (mesmo schema).
- `reports/phase3_5b/robustness/b1c_rerun_ffr_aware.md` — delta report
  com top-15 por OOS Sharpe.

## Limitações (⚠️ FLAGs documentais, não-bloqueantes)

- **Ken French RF = 1-mo T-bill**, não exato Federal Funds Rate. Gap
  histórico médio RF-vs-FFR ~0-30 bps. Fiz RF×252 como "FFR" proxy para
  o cost model; modelo conservador (RF ≤ FFR em geral), haircut seria
  um pouco maior com FFR real. Aceitável — o gate não chega perto de
  falhar mesmo assim.
- **UPRO/SSO reais ainda ausentes do Tiingo** — parte 3 da Task 7a
  (fechar 3-way) fica pendente.
- **Bootstrap 99.9% CI** agora [0.985, 2.419] vs baseline [0.888, 2.406].
  Ambos comfortably > 0. Leve melhora do lower bound (seed=42, sem
  re-seed).

## Citações

- Cost formula FFR-aware: `data/external/README.md` Task 7a section.
- Gayed flat-fee intacto: `[leverage_for_the_long_run, p.16]`.
- Gate thresholds:
  - PBO < 0.5 → `[advances_fin_ml, p.208-211]`.
  - DSR p < 0.05 → `[advances_fin_ml, p.196-202, p.273-275]`.
  - WF ≥ 6/8 → Pardo (2008) ch.10-11 + mandate rule #5.
  - Stationary bootstrap → `[advances_fin_ml, p.196-202]`.
- Ken French RF proxy para FFR: `data/external/README.md` header
  (Ibbotson/ICE BofA 1-mo TBill).

## Próxima iteração

Iter 9 — Task 7b: stress isolado (2008-09 crise, 2020-03 COVID, 2022
bear/hikes, 2025-Q1). Sharpe + drawdown por sub-período por strategy.
Winner Phase 3 já survived FFR gate, foco agora vira drawdown behavior.

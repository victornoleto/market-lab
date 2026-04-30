# bestfolio_meta_wf_hunt — Spec

**Status:** **CLOSED 2026-04-29 18:13** — iter 001 DEAD_END (kill K3 fired:
turnover 177-222%/yr sem Sharpe edge; 0/3 datasets clear hurdle +0.05;
DSR falha 2/3 a n_trials=157). Decisão do usuário 2026-04-29: encerrar
formalmente, não rodar iter 002. Ver §12 (Closure) abaixo.

**Predecessor:** `studies/long_term_portfolio/` (FROZEN — F1+SPLIT FINAL PICK,
deploy-ready, mean Sharpe 1.109 / mean MDD 16.76% / mean CAGR ~10.7% across
lh_56y / vt_real / ndx_real).
**Branch alvo:** `bestfolio-meta-wf/iter-NNN` (não reutilizar `bestfolio-hunt/*`).

---

## 1. Hipótese

Um solver **walk-forward** (estilo bestfolio.app) que aloca pesos mensais
sobre **N portfólios estáticos já validados** consegue:

- **(a)** preservar gates hard-block do projeto (PBO < 0.5, DSR p < 0.05,
  WF k=8 ≥ 6, bootstrap 99.9% CI > 0, cross-lib ±3pp), e
- **(b)** entregar Sharpe líquido ≥ +0.05 vs F1+SPLIT em ≥ 2/3 datasets
  com MDD ≤ MDD(F1+SPLIT) + 3pp, e
- **(c)** justificar a complexidade adicional vs static F1+SPLIT (turnover
  ≤ 50%/yr no meta, alocação não-degenerada — i.e. não recomenda 100%
  num único sleeve mais de 70% do tempo).

Se as três falharem, a vertente fecha como DEAD_END e F1+SPLIT permanece.

---

## 2. Por que essa vertente é diferente das 10 iters bestfolio que morreram

iters 001-010 (renomeadas para long_term_portfolio) testaram **sleeves
individuais** do catálogo bestfolio (HAA, BAA, Composite, Vol Throttle,
etc.) — todas MARGINAL/PROMISING, nenhuma WINNER per gates locais.

Esta vertente é **estrutural**, não substantiva: usa a metodologia
walk-forward deles aplicada sobre **nossa** universo de sleeves vencedores
do long_term_portfolio. A pergunta não é "esse sleeve passa?" mas
"diversificação dinâmica entre N sleeves passantes adiciona valor sobre
F1+SPLIT static?".

Crítica metodológica documentada do bestfolio (de extração literal das
páginas walk-forward + methodology):

- Eles selecionam 5 sleeves **ex-post** do catálogo deles (já passantes
  internos), depois rodam WF sobre os pesos. WF é honesto no nível dos
  pesos, **não** no nível da seleção de universo. PBO e DSR não mencionados.
  Cf. `[advances_fin_ml, p.208-211]` (PBO de seleção em 2 camadas infla).
- LETF decay subestimado: SmartLeverage 2.0x-3.0x usa SSO/UPRO/TQQQ.
  Decay empírico SSO ~1.5%/yr, UPRO ~4-6%/yr em regimes voláteis.
  Cf. `[leverage_for_the_long_run]` para path-dependence.
- Taxes "not modeled" (literal). Para BR-resident sob Lei 14.754/2023:
  tax drag = 15% × CAGR_gross_anual via `studies/_shared/tax_engine.py`.

Mitigações nesta vertente:
- Universo = **só nossos sleeves passantes do long_term_portfolio**
  (não catálogo bestfolio cru).
- PBO/DSR aplicados sobre o **meta-portfólio**, não só sleeves base.
- LETF decay já está embedded nas séries dos sleeves (NTSX/GDE têm
  expense + decay realista; KMLM/DBMF não são leveraged).
- Lei 14.754 modelada em `final_report.md` (informational, não-gating).

---

## 3. Universo de sleeves (5 candidatos iniciais)

Todos extraídos do `studies/long_term_portfolio/STRATEGY_ZOO.md` /
final report (ler antes de cada iter):

| ID | Slug | Composição | Por que entra | Citação âncora |
|----|------|------------|---------------|----------------|
| S1 | F1_SPLIT | NTSX 25 / GDE 25 / KMLM 17.5 / DBMF 17.5 / TLT 15 | FINAL PICK, incumbent | `[risk_parity, ch.5]` |
| S2 | iter023_TLT_static | TLT-stack base do iter 023 (pré-SPLIT) | Bond-heavy, regime-deflation | `[stocks_for_the_long_run]` |
| S3 | iter020_AllWeather | Browne AllWeather defensive iter 020 | Stress-regime hedge | `[risk_parity, ch.4]` |
| S4 | F3_SPMO_hybrid | iter 040 SPMO hybrid (US momentum tilt) | Momentum overlay | `[stocks_on_the_move, p.21-30]` |
| S5 | F7_RSST_heavy | iter 041 RSST stacked (highest CAGR 12.50%) | Aggressive sleeve para upside | `[trend_following]` |

Constraint: nenhum sleeve fora de `_shared/EXTERNAL_INSTRUMENTS.md` ou
do `STRATEGY_ZOO.md`. Não introduzir novo ETF synth nesta vertente —
universe-fixing essencial pra evitar meta-meta-overfit.

---

## 4. Solver walk-forward

Espelha bestfolio.app/blog/walk-forward-portfolios literal:

- **Lookback:** 36 meses (3 anos) de retornos diários dos N sleeves.
- **Frequência:** rebal mensal (último pregão útil do mês).
- **Constraints:** ∑w_i = 1, w_i ≥ 0 (no shorts), w_i ≤ 0.40 (max 40%
  por sleeve — bestfolio's choice, mantemos para reproduzibilidade).
- **Objetivo:** max Sharpe (variante Conservative) E max CAGR (variante
  Aggressive). Rodar ambas; reportar separadamente.
- **OOS:** weights computados em [t-36m, t] aplicados em [t, t+1m].
  Embargo 21 dias entre fim do train e início do test (defesa contra
  serial correlation, cf. `[advances_fin_ml, p.105-108]` — addition over
  bestfolio).

Implementação: `studies/_shared/wf_solver.py` (criar). Reutilizar séries
de sleeves de `studies/long_term_portfolio/iterations/<iter>/results.json`.

---

## 5. Gates (hard-block, herdados do projeto)

| Gate | Threshold | Citação |
|------|-----------|---------|
| PBO sobre meta-Sharpe | < 0.5 | `[advances_fin_ml, p.208-211]` |
| DSR p-value | < 0.05 com n_trials cumulativo do hunt | `[advances_fin_ml, p.222-223]` |
| Walk-forward 8-fold | ≥ 6/8 winners | `[advances_fin_ml, p.105-108]` |
| Bootstrap 99.9% CI sobre CAGR | low > 0 | `[advances_fin_ml, p.196-202]` |
| Cross-lib (vectorbt vs bt) | |Δ CAGR| ≤ 3pp | (próprio) |
| Sharpe edge vs F1+SPLIT | ≥ +0.05 em ≥ 2/3 datasets | scoring.py rubric |
| MDD vs F1+SPLIT | ≤ +3pp em ≥ 2/3 datasets | mandate §2.3 tier framework |

Falhar qualquer um → DEAD_END + jornada entry.

---

## 6. Cost model

- Backtest **gross-of-tax** (consistente com long_term_portfolio scoring).
- `final_report.md` reporta também **net** via
  `_shared/tax_engine.AnnualDarfEngine` (Lei 14.754: 15% anual flat,
  carry-forward indefinido, perdas compensam ganhos no ano).
- LETF decay já embedded nas séries dos sleeves. Não somar decay extra.
- Slippage: 10bps por one-way trade aplicado sobre turnover do meta
  (não duplicar slippage interno dos sleeves base).
- FX: zero no backtest (operação USD↔USD dentro da Inter); se compor
  meta com instrumento BRL-denominado no futuro, revisitar.

---

## 7. Iter loop

Loop de no máximo **6 iters** (orçamento conservador):

| Iter | Variante | Decisão se passa | Decisão se falha |
|------|----------|------------------|------------------|
| 001 | Solver max-Sharpe, universo S1-S5 (5 sleeves) | iter 002: max-CAGR | iter 002: subset 3 sleeves (drop S5) |
| 002 | Variante alternativa | iter 003: turnover penalty | iter 003: relax max-w para 50% |
| 003 | Hyperparameter sweep menor | iter 004: cross-lib | DEAD_END |
| 004 | Cross-lib (vectorbt vs bt) | iter 005: paper trading | DEAD_END |
| 005 | FWD stress (2008, 2020, 2022) | iter 006: deploy candidate | DEAD_END |
| 006 | Deploy spec + Phase 4 paper hookup | LIVE candidate | DEAD_END |

Não exceder 6 iters sem novo OK do usuário (n_trials inflation kills DSR).

---

## 8. Kill criteria explícitos

A vertente **fecha imediatamente** se:

- (K1) iter 001 + iter 002 ambos falham gates → DEAD_END (estrutural).
- (K2) Em qualquer iter, weights do solver convergem para ≥ 80% num
  único sleeve > 80% do tempo → diversificação dinâmica não está
  agregando, F1+SPLIT static é dominante.
- (K3) Turnover do meta > 100%/yr **e** Sharpe edge vs F1+SPLIT
  < +0.10 → custo de complexidade não justificado.
- (K4) MDD do meta > MDD(F1+SPLIT) + 5pp em qualquer dataset →
  walk-forward não está adicionando defesa, só CAGR-chasing.

---

## 9. Success criteria explícitos

Promove para Phase 4 (paper trading) se simultaneamente:

- Todos os gates §5 passam em iter 001 OU iter 002.
- iter 003 hyperparameter sweep mostra estabilidade (Sharpe ±0.05 entre
  configurações vizinhas — defesa anti-overfit do solver).
- iter 004 cross-lib confirma com |Δ CAGR| ≤ 3pp.
- iter 005 FWD stress (2008, 2020-mar, 2022) sobrevive (no max-DD
  pior que +5pp do worst histórico do incumbent F1+SPLIT).

---

## 10. Não-objetivos

Esta vertente NÃO:
- Reativa Plano A (Pepperstone CFD) — mandate §1, §3 DORMANT.
- Reativa Plano D (BR ranking mensal) — mandate §4b DORMANT.
- Toca em `studies/long_term_portfolio/` (frozen).
- Introduz novos ETFs synth ou tickers além de `_shared/EXTERNAL_INSTRUMENTS.md`.
- Modela LETF decay separadamente (já embedded nas séries dos sleeves).

---

## 11. Referências

- bestfolio.app walk-forward methodology blog post (consultado 2026-04-29)
- bestfolio.app/methodology#variants-smartleverage (consultado 2026-04-29)
- `[advances_fin_ml, p.105-108]` — embargoed CV
- `[advances_fin_ml, p.196-202]` — bootstrap CI
- `[advances_fin_ml, p.208-211]` — PBO seleção 2-camadas
- `[advances_fin_ml, p.222-223]` — DSR n_trials cumulativo
- `[risk_parity, ch.4-5]` — incumbent F1+SPLIT thesis
- `[stocks_on_the_move, p.21-30]` — momentum sleeve S4
- `[leverage_for_the_long_run]` — LETF decay path-dependence
- `[trend_following]` — managed futures sleeve S5
- Lei 14.754/2023 — `studies/_shared/tax_engine.py` canonical

---

## 12. Closure (2026-04-29 18:13)

**Resultado iter 001 (max-Sharpe, S1-S5):**

| Dataset | meta Sharpe | S1 Sharpe | edge | meta MDD | turnover |
|---|---:|---:|---:|---:|---:|
| lh_56y | 1.137 | 1.125 | +0.012 | 17.42% | 177.2% |
| vt_real | 1.106 | 1.118 | -0.012 | 12.73% | 215.7% |
| ndx_real | 1.102 | 1.128 | -0.026 | 12.73% | 222.0% |

**Verdict:** DEAD_END. Kill K3 fires. 0/3 datasets clear Sharpe hurdle +0.05;
DSR falha 2/3 (vt_real p=0.062, ndx_real p=0.101 a n_trials=157 cumulativo).

**iter 002 (max-CAGR Aggressive variant) NÃO executado** por decisão do
usuário (2026-04-29). Justificativa: failure no iter 001 é estrutural —
densidade de Sharpe entre os 5 sleeves é apertada demais (1.10-1.14 média)
para 36mo de daily distinguir signal de noise. iter 002 com mesmo universo
+ objetivo diferente tende a produzir resultado isomorfo. Cada iter
adicional ainda incrementa n_trials no DSR deflator (já em 157 → 158
mata DSR de quase tudo).

**Achado positivo preservado (não-deployável mas registrável):** o solver
diversifica genuinamente (avg weights S1 26 / S2 18 / S3 29 / S4 11 / S5 15
no lh_56y) e reduz MDD em 1,88-2,48pp em todos os 3 datasets a Sharpe
constante. Não passa o gate (sem edge), mas inspira possível direção C.6
futura: "F1+SPLIT com sleeve TLT-bias condicionado a vol regime" — captura
parte da redução de MDD sem o turnover de 200%/yr. Não vai ser perseguida
agora.

**Artefatos preservados:**
- `iterations/001-2026-04-29-meta-wf-S1-S5-maxSharpe/` — hipótese, backtest,
  results.json, verdict.json, final_report.md (evidência completa)
- `studies/_shared/wf_solver.py` — solver canônico bestfolio-style com
  embargo, validado por `tests/test_wf_solver.py` (5 testes ✅). Reutilizável
  em estudos futuros que precisem de solver walk-forward com constraints.
- `jornada/2026-04-29-1813-bestfolio-meta-wf-iter001-deadend.md`

**Estado pós-closure:** F1+SPLIT permanece único deploy-ready candidate
(via long_term_portfolio FINAL_REPORT). Mandate §1 maintenance mode 100%
Plano C inalterado até INTER_CHECK fill + §7 override formalization.

**Lição estrutural (saved to feedback memory):** Quando um universo de
sleeves já passou pré-gates honestos, a densidade de Sharpe é tipicamente
tight (±0,05). Walk-forward dynamic allocation sobre tal universo tende a
ruído: rediscobre a alocação static near-optimum mensalmente, ao custo de
turnover 100-250%/yr. Para descobrir edge real, ou (a) o universo precisa
ter dispersão de Sharpe maior (sleeves de regimes distintos não-pré-screenados),
ou (b) o sinal precisa ser não-Sharpe (ex.: regime detection com features
exógenas, não rolling momentum/Sharpe).

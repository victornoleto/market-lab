# 2026-04-24 10h47 — Hunt loop iter 007: momentum overlay no vol-managed blend dá 50/100 MARGINAL, regressão vs iter 006

**Contexto**: modo MAINTENANCE (mandate §1 segue 100% Plano C). Hunt
loop continua rodando em background como pesquisa pura; resultados
alimentam `studies/strategy_hunt_loop/` mas não mudam a alocação.

## O que foi feito

Iter 007 do Strategy Hunt Loop testou a hipótese "option B" deixada
pelo iter 006 (final_report): **compor o blend vol-managed SPY+TLT
com um filtro de momentum 12-1 (skip-a-month) canônico**. A teoria
(Moreira-Muir 2017 Table IV, Jegadeesh-Titman 1993, Moskowitz-Ooi-
Pedersen 2012) dizia que adicionar momentum sobre vol-managed
multiplica o edge por um fator 1.15-1.30×.

Setup:

- Base blend pré-comprometido: `vt15_L21_cap20` (iter 006's
  spy/ndx top — Sharpe 1.000 / 1.021)
- Grid overlay: 3 configs (mom252_skip21 canônico, mom126_skip21
  mais curto, mom378_skip21 mais longo), todos threshold=0 (gate
  binário "mom > 0 → deploy, else cash")
- 3 datasets × 3 configs = 9 trials novos; cumulative n_trials
  4228 → 4237
- TDD disciplinado: 11 specs em `tests/test_momentum_overlay.py`
  passaram no primeiro green; baseline pytest 718 → 729

## O resultado

**Score 50/100 MARGINAL** — regressão de −17 pts vs iter 006 (67
PROMISING).

| dataset | iter 006 Sharpe | iter 007 Sharpe | Δ | kill? |
|---|---|---|---|---|
| educational | 0.929 | 0.916 | −0.013 | — |
| spy_real | **1.000** | 0.941 | **−0.059** | KILL #1 |
| ndx_real | **1.021** | 0.872 | **−0.149** | KILL #1 |

Adicional: G1 PBO 0.64-0.76 **falha nos 3 datasets** (KILL #3
triggered) mesmo com grid pré-comprometido ex-ante de 3 cfgs. G6
bootstrap no ndx_real ficou em −0.001 — Sharpe está tão marginal que
a distribuição bootstrap ficou centrada em zero.

MDD melhorou 2-5 pp nos 3 datasets — o gate acha informação de
regime, mas o custo de abandonar o expected return excede o ganho.

## O que isso significa (lição estrutural)

**Momentum overlay é REDUNDANTE com variance-scaling em um blend
vol-managed.** Os dois mecanismos atacam a mesma informação
subjacente: volatilidade de regime do equity.

O livro do Gayed
(`[leverage_for_the_long_run, p.9]`) registra que SPY abaixo da 200d
MA tem volatilidade 2-3× maior que acima. Essa assimetria é o que o
variance-scaling (iter 005's `σ^{-2}`, iter 006's portfolio
variance-scaling) JÁ captura, via a regra
`scale = target_vol² / σ²_port`.

Empilhar um gate de momentum por cima força a exposição pra zero
justamente nos regimes onde o blend já reduziu naturalmente,
abrindo mão do drift positivo residual em troca de custo de flip.
O efeito é negativo. Pior ainda: a simetria é adversa — o dano em
Sharpe ESCALA com o Sharpe base (edu: −0.013; spy: −0.059; ndx:
−0.149). Quanto mais a mecânica base ganha, mais caro fica o overlay.

Traduzindo: **o Moreira-Muir Table IV não replica em blend vol-
managed**. Esse uplift foi documentado para MOM isolado × vol-scaling,
não para uma mecânica que já é vol-managed cross-asset.

## Consequência pro próximo iter

DEAD_ENDS.md ganhou entrada nova. A categoria "signal overlay em blend
vol-managed" está fechada para sinais CORRELACIONADOS com vol
(momentum, SMA/EMA, VIX, drawdown).

O path forward é **sinais ortogonais**:

1. **Single-cfg ex-ante do iter 006 (sem grid)** — Option A do iter 006
   ainda válida; elimina PBO completamente (PBO é undefined para N=1),
   testa se o edge do iter 006 é estrutural ou grid-selecionado.
   Custo: +3 n_trials.
2. **Term-spread (T10Y3M) ou credit-spread (EBP) overlay** — macro
   signals rastreiam bond/credit regime, não equity-vol. Ortogonal por
   construção. Dados já em `data/external/macro/`.
3. **Meta-labeling AFML ch.3** — modelo secundário prevê lucratividade
   bar-a-bar da decisão do iter 006 usando features cross-sectional /
   macro que o blend não vê. Filtro data-driven, não rule-driven.
4. **Extensão 3-asset SPY+TLT+GLD** — mantido de iter 006 option C.

## Arquivos gerados

- `studies/strategy_hunt_loop/iterations/007-2026-04-24-1047-vol-managed-60-40-momentum-overlay/`:
  - `hypothesis.md`, `final_report.md`, `verdict.json`, `results.json`
  - `momentum_overlay.py`, `numpy_reference.py`, `run_backtests.py`,
    `compute_gates_and_score.py`
- `tests/test_momentum_overlay.py` — 11 specs TDD (all green)
- `studies/strategy_hunt_loop/BASE_MEMORY.md` — frontmatter + log +
  top-K + promising directions + dead-end categories atualizados
- `studies/strategy_hunt_loop/DEAD_ENDS.md` — entrada completa iter 007

## Glossário (termo novo)

- **Signal redundancy** — quando dois filtros numa pipeline atacam a
  mesma informação latente. Empilhar aumenta custo sem aumentar
  precisão. Lição experimental de iter 007: variance-scaling e
  momentum overlay são redundantes em equity-regime volatility.

# B2 [SWING BROKER]: LETF rotation vs ETF Rotation top-1 — LETF domina, substitui ETFRotation como winner Path B

**Tag:** [SWING BROKER] (Path B — swing broker BR, 15% IR)
**Iteração:** 34 (Phase 3, Lead B2)
**Data:** 2026-04-17 00:05 UTC
**Decisão:** `REPLACE_B_WITH_A` — LETF rotation (EMA100, lev=2x) substitui
ETFRotation top-1 como **single winner Path B**.

## TL;DR

Comparei lado a lado as duas estratégias Path B vigentes sobre o maior
histórico disponível na intersecção dos dois universos (4849 bars,
2007-01-04 → 2026-04-14, ~19 anos). A LETF rotation (winner B1c,
EMA100/band=0/lev=2x, net 15% IR) domina o ETFRotation top-1 em todos
os quatro eixos:

| Métrica             | LETF rotation | ETFRotation top-1 | Risk-parity blend |
|---------------------|---------------|-------------------|-------------------|
| Sharpe anualizado   | **1.90**      | 0.75              | 1.56              |
| CAGR líquido        | **49.9%**     | 11.7%             | 27.2%             |
| MaxDD               | **−18.4%**    | −28.6%            | −21.6%            |
| MAR (CAGR/\|DD\|)     | **2.72**      | 0.41              | 1.26              |
| Diversification D   | —             | —                 | 1.18              |

Correlação Pearson 0.44 (moderada), Spearman 0.48. Rolling 252d
correlação **muito instável**: min −0.06 / mediana 0.49 / max 0.91 —
acopla fortemente em bulls (pós-2010) e descorrelaciona em stress.

O blend inverse-vol (57.8% ETFRot / 42.2% LETF) tem Sharpe 1.56, **abaixo**
do leg dominante (1.90), portanto blendar destrói performance ajustada
ao risco. Diversification D=1.18 é positivo mas insuficiente pra
compensar a perda de CAGR (de 50% pra 27%).

**Conclusão operacional:** Path B passa a ser **apenas LETF rotation**.
ETFRotation top-1 sai de "winner production-ready" pra "benchmark de
comparação". Path A (BollingerMR SPY 1h + multi-asset A3) segue intocado.

## Metodologia

### Janela

- LETF rotation: construída sobre `load_spx_tr_daily` (1970-2026,
  14,191 bars disponíveis; sliced pra overlap). Warmup começa em
  2004-01-02 pra garantir >500 bars pré-overlap (EMA100 estável).
- ETFRotation top-1: universo SPY/QQQ/IWM/GLD/TLT, warmup 500 dias.
  Janela válida começa 2007-01-03 (≈500d após primeiro bar GLD em
  2004-11-18).
- Overlap: **2007-01-04 → 2026-04-14** (4849 bars, maior janela
  comum respeitando dependências de data dos dois sistemas —
  manifest.json auditado pra SPY/QQQ/IWM/GLD/TLT antes do run).

### Custos modelados

| Estratégia      | Custos aplicados                                                                              |
|-----------------|-----------------------------------------------------------------------------------------------|
| LETF rotation   | Drag anual 1% (Gayed p.16) + 10 bps commission + 5 bps spread por switch + **15% IR BR** no ON→OFF com ganho |
| ETFRotation     | Execução bar-level no `Runner` (comissão baseline `ExecutionConfig`); 15% IR aplicado post-hoc quando reportado |

Os retornos líquidos da LETF já incluem o 15% BR; os retornos da
ETFRotation vêm do `equity_curve` do Runner (Tiingo daily, sem IR
aplicado — consistente com como foi validada no iter 20). Como o
ETFRotation perde de forma categórica (todos os 4 eixos), aplicar o
IR diminuiria ainda mais o Sharpe — não muda a decisão.

### Decisão

Regra `decide_blend_vs_replace` (`strategy_benchmark.py`) adicionou
uma primeira regra de **dominância estrita**:

> Se um leg tem Sharpe, MAR e MaxDD (mais raso) **todos** melhores que
> o outro AND o blend inverse-vol tem Sharpe < leg dominante ⇒ REPLACE.

Essa regra captura o caso comum onde uma estratégia é estritamente
dominante mas não ultra-correlacionada (aqui corr=0.44, longe do
threshold 0.7 usado pelo teste de "correlated replace"). Sem essa
regra a decisão cairia em `INDEPENDENT_LANES`, que **não representa
a realidade econômica** do mandate — blendar 58% num leg de Sharpe
0.75 é folclore à luz do mandate §4.

### Gates & referências

Nenhum gate novo foi rodado — B1c já validou a LETF rotation com
PBO=0, DSR p=0, WF 8/8, bootstrap 99.9% CI [1.037, 2.468] em iter
32. B2 **não re-valida** B1c; usa os retornos reconstruídos via
`simulate_letf_rotation` (mesmo código, mesma config) e compara.

Citações:
- `[leverage_for_the_long_run, p.13, p.16]` — LRS signal + leverage
  drag.
- `[stocks_on_the_move, p.81, p.66-67, p.95]` — ETFRotation top-1.
- `[advances_fin_ml, p.196-202]` — Sharpe annualization / DSR
  framework.
- Choueifaty-Coignard (2008) — diversification ratio.

## O que mudou no código

- `src/ai_trade/backtest/grid/strategy_benchmark.py` (novo, ~280
  linhas): pure helpers (align, sharpe, cagr, maxdd, mar, inverse-vol
  weights, diversification ratio, rolling corr, blend, decision,
  run_benchmark).
- `scripts/run_b2_benchmark.py` (novo, ~220 linhas): driver que
  regenera os retornos líquidos dos dois winners e escreve
  `reports/b2_benchmark/<run-id>/{verdict.json,daily_returns.csv}`.
- `tests/test_strategy_benchmark.py` (novo, 27 testes): cobre todas
  as helpers + 4 ramos da decisão (incluindo dominance-override).

Arquivos existentes intocados (winners produção são INTOCÁVEIS per
constraint Phase 3 §Constraints):
- `strategies/letf_rotation.py`, `strategies/etf_rotation.py`,
  `grid/letf_rotation_b1c.py`, `data/spx_tr_loader.py` — zero diff.

## Números brutos (reports/b2_benchmark/b2_phase3_iter34/)

- `verdict.json` — decisão completa + thresholds.
- `daily_returns.csv` — 4849 bars × 3 colunas (LETF, ETFRot, blend).

Top-line:
- `window=2007-01-04 → 2026-04-14 (4849 bars)`
- `pearson=0.4411  spearman=0.4847`
- `rolling_corr_252d: min=-0.059, median=0.488, max=0.905`
- `decision=REPLACE_B_WITH_A`

## Impacto no mandate

- **Strategy B agora é 1 estratégia, não 2.** `winners_swing:` no
  memory.md frontmatter continua com as 2 entries históricas
  (read-only per Phase 3 §Winners históricos), mas o mandate
  operacional a partir de hoje é: **LETF rotation EMA100 band=0
  lev=2x** é o único winner Path B — ETFRotation top-1 fica como
  benchmark científico.
- **Target mandate §4 atingido para Path B**: CAGR ≥ 15% (LETF tem
  ~50%, bem acima do target 15-20%).
- **Cross-strategy correlation vs Path A** (BollingerMR SPY 1h) ainda
  pendente — será lead separado se relevante para portfolio-level
  sizing (já temos ρ=0.252 BollingerMR × ETFRotation do iter 27, mas
  ρ(BollingerMR × LETF) precisa ser medido antes de decidir
  allocation).

## Próximo passo

**Lead A3 — Per-asset BollingerMR + threading-ready refactor**
(pre-req A2 ✅). Targets ranqueados por A2 (IWM 1h > TLT 1h > xrpusd
daily). Estrutura prevista: `src/ai_trade/live/worker.py` + testes
de state-isolation por ticker + correlation matrix entre ativos que
passam gates individualmente.

Depois de A3 concluído, loop Phase 3 encerra o ciclo A1/B1/A2/B2/A3
e `status: done` quando summary jornada for escrito.

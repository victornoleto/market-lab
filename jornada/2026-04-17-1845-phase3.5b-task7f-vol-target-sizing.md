# 2026-04-17 1845 — Phase 3.5b Task 7f [PLANO B] [SWING BROKER]: Vol-target 10% sizing → baseline EW kept

## Verdict

**Production default sizing permanece `baseline_ew` (1/3/1/3/1/3, sem rescaling).**

Vol-target 10% **não é promovido** pela regra dupla-margem (ΔOOS
Sharpe ≥ +0.05 AND ΔOOS CAGR ≥ +1.0 pp). Dos 9 configs testados
(`{63, 126, 252}d × {1.5, 2.0, 3.0}× cap`), **nenhum** atende a
margem de CAGR — o 3-leg EW já opera naturalmente próximo do target
(vol realizada full ~11%, OOS scale médio 0.96-1.05), então o
rescaling é um ajuste cosmético em retorno, não um upgrade
material.

**Observação não-promocional (mas digna de registro para o allocation
doc):** o melhor challenger (`vt_target=0.10_L63_cap3.0`) cortaria o
MaxDD full de **10.86% → 7.39%** (−3.47 pp) e subiria OOS Sharpe de
2.30 → 2.48 (+0.18) com OOS CAGR ligeiramente melhor (30.54% →
30.80%, +0.26 pp). A falha do gate é **apenas o +1.0 pp em CAGR**,
não performance geral. Task 8 vai citar isso como "variante defensiva
opcional" — não winner promovido mas disponível para users que
queiram menor DD sem sacrificar CAGR.

## Contexto / porquê

Task 7f do spec `phase_3_5b_winners_validation.md` pede testar
vol-target 10% no nível do portfolio como alternativa de sizing ao
EW estático — validar se uma camada de ex-ante scaling melhora o
retorno risk-adjusted. Referência canônica: standardização de vol
em CTA systematic — `[systematic_trading_carver, p.107-111]` — e
bet-sizing a partir de target de vol em `[advances_fin_ml,
p.162-164]`.

A regra dupla-margem segue o mesmo padrão conservador de Task 7d
(allocation): `[advances_fin_ml, p.298-299]` — naive 1/n é o prior
Bayesiano correto absent evidência forte, então exigimos margem
material em BOTH Sharpe AND CAGR para promover um challenger.

## Desenho

- Input: EW 3-leg blended daily returns (post-tax/post-cost),
  common window 2004-11-18 → 2026-04-14 (5383 bars, GLD-limited).
- Scale factor na barra `t`: `s_t = clip(target_vol /
  σ̂_{t-1}, 0, max_leverage)` onde `σ̂_{t-1}` é a rolling std
  anualizada sobre `[t-L, t-1]` — **shift(1) garante zero
  look-ahead**.
- Configs: cartesian `{63, 126, 252}d × {1.5, 2.0, 3.0}× cap`
  (9 configs) + baseline_ew.
- Split IS/OOS: 60/40, `is_end=2017-09-21` — mesmo split usado em
  Task 7d (allocation).
- Regra de promoção: `select_default_sizing` exige
  ΔOOS Sharpe ≥ +0.05 AND ΔOOS CAGR ≥ +1.0 pp.

## Resultados (sweep completo)

| Config | Scale mean | cap_hit% | Sharpe full | MaxDD full | Sharpe OOS | CAGR OOS |
|---|---|---|---|---|---|---|
| baseline_ew | 1.00 | 0.0% | 2.11 | **10.86%** | 2.30 | **30.54%** |
| vt_L63_cap1.5 | 1.02 | 10.3% | 2.19 | 7.39% | 2.46 | 29.41% |
| vt_L63_cap2.0 | 1.04 | 2.2% | 2.20 | 7.39% | 2.48 | 30.34% |
| vt_L63_cap3.0 | 1.05 | 1.1% | **2.20** | **7.39%** | **2.48** | **30.80%** |
| vt_L126_cap1.5 | 0.99 | 6.5% | 2.16 | 8.43% | 2.38 | 28.29% |
| vt_L126_cap2.0 | 1.00 | 0.5% | 2.16 | 8.43% | 2.40 | 28.73% |
| vt_L126_cap3.0 | 1.01 | 0.0% | 2.16 | 8.43% | 2.40 | 28.73% |
| vt_L252_cap1.5 | 0.96 | 1.9% | 2.17 | 9.24% | 2.34 | 28.03% |
| vt_L252_cap2.0 | 0.97 | 0.0% | 2.17 | 9.28% | 2.35 | 28.29% |
| vt_L252_cap3.0 | 0.97 | 0.0% | 2.17 | 9.28% | 2.35 | 28.29% |

**Padrão**: scale médio de 0.96 a 1.05 confirma que o portfolio já
opera perto dos 10% target — o maior ganho é **suavização** (MaxDD
de 10.86% → 7.39% no L63), não amplificação. O cap de 3.0 foi
acionado em apenas 1.1% dos bars no L63 (ativado em clusters de
baixa vol — 2005-2006, 2017, 2019 — onde o portfolio teria podido
escalar até 3x).

## Interpretação

1. **A vol natural do 3-leg EW já é ~10%**, então a promessa teórica
   do vol-target (estabilizar σ) se traduz em ganho marginal — a
   construção diversificada das 3 pernas (Task 7e ρ<0.7 em todas as
   janelas) já entrega boa parte do benefício.
2. **L63 > L126 > L252 em Sharpe OOS** — lookback curto responde mais
   rápido a regime shifts (COVID spike, 2022 bear). Consistente com
   `[systematic_trading_carver, p.110]` que recomenda L≈25-36 para
   intraday e L≈100-250 para swing (nosso 63 está entre — equilíbrio
   correto).
3. **Cap raramente atua** (1-10% dos bars) — a 3-leg naturalmente
   exibe vol estável. Em um portfolio de edge único, o cap seria muito
   mais ativo.
4. **MaxDD improvement de 32%** (10.86 → 7.39) é real e grande —
   **defensivamente atrativo**, especialmente para users sensíveis
   a DD. Fica registrado como variante opcional no allocation doc
   (Task 8).
5. **Custos de rebalance não modelados** — a implementação assume
   daily rebalance sem custo adicional. Task 7c sensitivity já
   confirmou que o portfolio 3-leg sobrevive até 10 bps/switch com
   Sharpe 2.141 — o vol-target adicionaria ~N bps/dia × scale
   diff, ordem de grandeza desprezível a bp-sweep atual.

## Decisão

- **Produção = `baseline_ew`** (sem rescaling, EW 1/3 cada perna).
  É o default conservador + robusto + equivalente em performance
  real.
- **Variante defensiva opcional = `vt_target=0.10_L63_cap3.0`** —
  documentada no allocation doc (Task 8) para users que priorizam
  MaxDD. Não é winner promovido (regra dupla-margem), mas é uma
  curva Pareto-ótima disponível.
- Winners imutáveis preservados (memory.md frontmatter intocado —
  `status: in_progress`, contexto histórico apenas).

## Artefatos

- `src/ai_trade/backtest/metrics/vol_target.py` (~500 loc).
  Funções `apply_vol_target`, `compare_vol_target_configs`,
  `select_default_sizing`, `render_vol_target_markdown`; dataclasses
  `VolTargetConfig`, `VolTargetRow`, `VolTargetComparison`.
- `scripts/run_vol_target_sizing.py` (+ reuse dos helpers Phase 3.5b).
- `tests/test_vol_target.py` (+21 tests: knobs canônicos, error
  paths, sem look-ahead, convergência estocástica, dual-margin
  regra, render).
- `reports/phase3_5b/robustness/vol_target_sizing.{md,json}`.
- Pytest 649 → **670 passed** (+21 novos). Baseline mantido.

## Próximo

Task 7f completa. Restantes: **Task 8** (`docs/phase3_winners_allocation.md`)
e **Task 9** (summary + `status: done`). Opcional:
Task 7a parte 3 (UPRO/SSO cache do Tiingo) se priorizado antes de
Task 8.

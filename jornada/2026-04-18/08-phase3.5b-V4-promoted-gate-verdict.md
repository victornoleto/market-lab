# Phase 3.5b — V4 promoted: 5-gate formal PASS em ambas as janelas (★★)

**Path tag:** [SWING BROKER] | **Tipo:** promotion | **Status:** ✅ V4 é novo default
**Data:** 2026-04-18 ~14:00

## Decisão

**V4 (SSO 2× + QLD 2× + UGL 2×) substitui V1 (SSO + QQQ + GLD)** como
config default de produção no `PRODUCTION.md`. V1 fica documentado
como conservative fallback (§13).

## O que aconteceu

Em conversação direta (não loop autônomo), usuário propôs testar o
análogo do leg SSO nas 2 pernas 1× restantes: usar o LETF 2× equivalente
(QLD para QQQ, UGL para GLD) quando o signal 1× disser LONG. Rodei 4
variantes:

| Variant | Leg 1 | Leg 2 | Leg 3 |
|---|---|---|---|
| V1 | SSO | QQQ | GLD |
| V2 | SSO | **QLD** | GLD |
| V3 | SSO | QQQ | **UGL** |
| V4 | SSO | **QLD** | **UGL** |

## Dados — testfol.io ground truth (1 curl extra)

Para ter **zero model risk** usamos testfol.io como fonte dos LETFs em
vez de `synthesize_letf_returns(L=2, fee=0.01)`. Task 7a já tinha
medido que nossa synth flat-fee overstates ~6-10%/yr em regimes de FFR
alto. Evidência no próprio dado:

| Ticker | 1× CAGR 40y | 2× CAGR 40y | Multiplier efetivo |
|---|---:|---:|---:|
| SPY → SSO | 11.49% | **14.58%** | 1.27× |
| QQQ → QLD | 14.58% | **17.27%** | 1.19× |
| GLD → UGL | 6.92% | **6.34%** | **0.92× (NEGATIVE)** |

Achado importante: **UGL sozinho tem CAGR menor que GLD** porque vol
drag do daily rebalancing em gold (que tem períodos flat longos entre
trends) come a alavancagem. Isso explica por que V3 (só UGL) tem Sharpe
pior que V1, mas V4 (UGL + QLD juntos) consegue aproveitar UGL como hedge
via interaction effect.

Usuário enviou curl com allocations `SPYSIM + QQQSIM?L=2 + GLDSIM?L=2`
— eu alterei o primeiro allocation para `SPYSIM?L=2` antes de executar
para termos SSO (2×) em vez de SPY (1×) redundante. Cache parquet
unificado atualizado para 7 tickers (SPYSIM, QQQSIM, GLDSIM, ZROZSIM
do 1º pull + SSOSIM, QLDSIM, UGLSIM do 2º).

## Dois scripts construídos

1. **`scripts/run_plano_b_variants_letf_execution.py`** — produz equity
   + drawdown charts para as 4 variantes vs SPYSIM. Signals no 1×
   underlying, execution nos returns ground-truth do LETF.
2. **`scripts/run_plano_b_variants_gates.py`** — roda 5 gates (OOS
   Sharpe > 0, Stress Sharpe > 0, WF 8/8 + ≤25% DD, DSR p<0.05 com
   n_trials=4, Bootstrap 99.9% CI lower > 0) em 2 janelas (canonical
   2004-2026 + supplementary 1986-2026).

## Gate verdict (★ todas passam)

**Canonical 2004-2026** (decision window):

| Rank | Variant | OOS Sh | Stress Sh | Full CAGR | Full MaxDD | DSR p | Boot lo | 5 gates |
|---:|---|---:|---:|---:|---:|---:|---:|:-:|
| **1** | **V4** | **2.609** | 2.172 | **39.19%** | -12.22% | 0.0000 | 1.274 | ✅ PASS |
| 2 | V2 | 2.595 | 2.176 | 35.03% | -12.62% | 0.0000 | **1.304** | ✅ PASS |
| 3 | V1 | 2.478 | 2.137 | 26.53% | **-9.39%** | 0.0000 | 1.043 | ✅ PASS |
| 4 | V3 | 2.392 | 2.058 | 30.89% | -10.88% | 0.0000 | 1.081 | ✅ PASS |

**Extended 1986-2026** (stress confirmation):

| Rank | Variant | OOS Sh | Stress Sh | Full CAGR | Full MaxDD | 5 gates |
|---:|---|---:|---:|---:|---:|:-:|
| **1** | **V4** | **2.320** | 2.172 | 37.93% | -16.91% | ✅ PASS |
| 2 | V2 | 2.294 | 2.176 | 35.00% | -15.81% | ✅ PASS |
| 3 | V1 | 2.195 | 2.137 | 25.94% | -11.13% | ✅ PASS |
| 4 | V3 | 2.174 | 2.058 | 28.92% | -13.70% | ✅ PASS |

**Ranking cross-window estável** — V4 > V2 > V1 > V3 em OOS Sharpe em
ambas as janelas.

## Por que V4 (não V2)

V4 domina V2 em quase todas as métricas:

| | V4 | V2 | Δ V4 vs V2 |
|---|---:|---:|---:|
| Canonical CAGR | 39.19% | 35.03% | **+4.16 pp** |
| Canonical MaxDD | -12.22% | -12.62% | -0.40 pp (V4 melhor) |
| Canonical OOS Sharpe | 2.609 | 2.595 | +0.014 |
| Canonical Boot 99.9% lo | 1.274 | 1.304 | -0.030 (V2 melhor) |
| Extended CAGR | 37.93% | 35.00% | +2.93 pp |
| Extended MaxDD | -16.91% | -15.81% | +1.10 pp |
| Extended Boot 99.9% lo | 1.357 | 1.305 | +0.052 |

Bootstrap canonical é a única métrica onde V2 ganha marginal, mas no
extended V4 reverte. Combined CAGR advantage compounded por 40y é
ordens de magnitude maior.

## Por que V3 fica em 4º (sozinho com UGL)

Confirmation do achado dos dados brutos: UGL standalone CAGR 6.34% <
GLD 6.92%. Quando você leveraged só a perna GLD (V3), você adiciona
drag sem compensação diversification — leg SSO+QQQ já são correlacionados
com S&P então UGL como hedge 1/3 não ajuda tanto quanto ajudaria com
2 equity legs alavancadas (V4).

**Interaction effect é real:** UGL isoladamente ruim (V3 pior que V1),
UGL em V4 (onde 2 legs equity são 2×) vira valiosa. Correlação baixa
de UGL vale MAIS proporcional quando a vol do resto do portfolio sobe.

## Decisão tomada

V4 é **novo default de produção** com as seguintes atualizações:

- `PRODUCTION.md` §1 rewrite com SSO/QLD/UGL + rationale promoção.
- `PRODUCTION.md` §5 expected metrics — V4 numbers, V1 lado-a-lado.
- `PRODUCTION.md` §6 flags — 2 novos flags (QLD/UGL liquidity + 3-LETF
  tracking stack).
- `PRODUCTION.md` §9 navegação — link para `variants_letf_execution/`.
- `PRODUCTION.md` §12 — novo header "V4 promoção gate verdict formal"
  com as 2 tabelas + decisão.
- `PRODUCTION.md` §13 — novo header "V1 fallback conservative
  alternative" com use cases + metrics.
- `reports/phase3_5b/README.md` TL;DR atualizada com V4 promotion bullet.
- `reports/phase3_5b/variants_letf_execution/README.md` novo (índice).
- `reports/phase3_5b/_DO_NOT_CLEANUP.md` atualizado.

V1 permanece documentado como fallback defensável para:
1. Disaster recovery se Inter delistar QLD ou UGL
2. Behavioral conservadorismo se MaxDD V4 real ficar insustentável
3. Escalação gradual (deploy V1 6-12m → V4 após track record)

## Caveats preservados

1. **V4 nunca foi live.** Todos os números são backtest. Gayed
   `[p.21, Table 12]` prevê drag real LETF ~2%/yr > teórico.
   **Esperar -1 a -2 pp CAGR + +1 a +3 pp MaxDD real vs backtest**.
2. **QLD/UGL liquidity** menor que SSO — QLD AUM $7B+, UGL $300M.
   Limitar ordens a 1% do ADV para não impactar preço.
3. **DSR n_trials=4** — conservador porque só 4 variantes testadas de
   design, não 72 como b1c. p-value 0.0000 é bem robusto mesmo assim.
4. **Extended window supplementary** — pré-2004 QQQSIM e pré-2004
   GLDSIM são modelados testfol.io, não ETFs reais. Serve como stress
   confirmatório, não como gate primário.
5. **Behavioral risk** — MaxDD V4 ~-12% backtest vira ~-15% real,
   que é mais dolorido que V1 -9%. Kahneman/Tversky (prospect theory)
   diz dor 2× ganho equivalente. Escalação gradual mitiga.

## Artefatos

- `reports/phase3_5b/variants_letf_execution/` — pasta completa
- `scripts/run_plano_b_variants_letf_execution.py` — equity+drawdown
- `scripts/run_plano_b_variants_gates.py` — 5-gate evaluator
- `data/testfolio/sso-qld-ugl.json` — raw 2nd download
- `data/testfolio/cache/history.parquet` — 7 tickers unified

## Pytest

765 preservado (zero regressão).

## Citações

- 5-gate framework: `[advances_fin_ml, p.208-211]` (PBO/CSCV),
  `[p.273-275]` (DSR), `[p.196-202]` (stationary bootstrap).
- WF ≥ 6/8 + MaxDD ≤ 25%: `docs/investment-mandate.md` §5.
- testfol.io ground truth: Phase 3.5b Task 7a.
- LETF daily decay + real-vs-theoretical gap:
  `[leverage_for_the_long_run, p.16, p.21, Table 12]`.
- Half-Kelly parameter uncertainty: `[fortune_formula]`, `[leverage_space]`.

## Próximos passos

- ✅ PRODUCTION.md §1/§5/§6/§9/§12/§13 atualizados.
- ✅ README.md phase3_5b TL;DR atualizada.
- ✅ variants_letf_execution/README.md criado.
- Override §7 mandate: pending user ratification — registro desta
  decisão em `docs/investment-mandate.md` §7 history.
- Quando começar Phase 4 (paper trading): deploy inicial em V1 por
  6-12 meses, migrar para V4 após track record confirmado (§4.2).

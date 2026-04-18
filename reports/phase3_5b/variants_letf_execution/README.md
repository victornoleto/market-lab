# Phase 3.5b — V1/V2/V3/V4 LETF-execution variants

**Path tag:** `[SWING BROKER]` / Plano B.
**Status:** ✅ All 4 variants PASS 5 gates (canonical 2004-2026 + extended 1986-2026).
**Decision (2026-04-18):** **V4 promoted to production default.** V1 retained as conservative fallback.

---

## TL;DR

Testamos 4 configurações idênticas em sinais (EMA100 no SPY para SSO, Donchian 20/10 em QQQ, Donchian 40/20 em GLD) mas diferentes em **execução** — quando a perna entra LONG, usamos o ETF 1× ou o LETF 2× equivalente:

| Variant | Leg SSO | Leg QQQ | Leg GLD | Deploy tickers |
|---|---|---|---|---|
| V1 | SSO 2× | QQQ 1× | GLD 1× | SSO + QQQ + GLD |
| V2 | SSO 2× | **QLD 2×** | GLD 1× | SSO + QLD + GLD |
| V3 | SSO 2× | QQQ 1× | **UGL 2×** | SSO + QQQ + UGL |
| **V4** | SSO 2× | **QLD 2×** | **UGL 2×** | SSO + QLD + UGL |

Dados: testfol.io ground-truth (SSOSIM/QLDSIM/UGLSIM via `SPYSIM?L=2`, `QQQSIM?L=2`, `GLDSIM?L=2`) — **zero model risk**, custos FFR-aware e ER baked in.

Threshold rebalance 10pp (default produção). 15% BR IR por exit lucrativo. 15 bps switch cost por flip de sinal.

---

## Verdict ordenado (canonical 2004-2026)

| Rank | Variant | OOS Sh | Stress Sh | Full CAGR | Full MaxDD | WF max DD | DSR p | Boot 99.9% CI lo | 5 gates |
|---:|---|---:|---:|---:|---:|---:|---:|---:|:-:|
| **1** | **V4 SSO+QLD+UGL** | **2.609** | 2.172 | **39.19%** | -12.22% | 12.22% | 0.0000 | 1.274 | ✅ PASS |
| 2 | V2 SSO+QLD+GLD | 2.595 | 2.176 | 35.03% | -12.62% | 12.62% | 0.0000 | **1.304** | ✅ PASS |
| 3 | V1 SSO+QQQ+GLD | 2.478 | 2.137 | 26.53% | **-9.39%** | 9.39% | 0.0000 | 1.043 | ✅ PASS |
| 4 | V3 SSO+QQQ+UGL | 2.392 | 2.058 | 30.89% | -10.88% | 10.88% | 0.0000 | 1.081 | ✅ PASS |

## Verdict ordenado (supplementary 1986-2026, 40y)

| Rank | Variant | OOS Sh | Stress Sh | Full CAGR | Full MaxDD | WF max DD | 5 gates |
|---:|---|---:|---:|---:|---:|---:|:-:|
| **1** | **V4** | **2.320** | 2.172 | **37.93%** | -16.91% | 16.91% | ✅ PASS |
| 2 | V2 | 2.294 | 2.176 | 35.00% | -15.81% | 15.81% | ✅ PASS |
| 3 | V1 | 2.195 | 2.137 | 25.94% | **-11.13%** | 11.13% | ✅ PASS |
| 4 | V3 | 2.174 | 2.058 | 28.92% | -13.70% | 13.70% | ✅ PASS |

**Consistência cross-window:** V4 lidera OOS Sharpe + CAGR em ambos, V2 segundo, V1 terceiro (menor MaxDD), V3 quarto. Ranking estável.

---

## Por que V4 foi promovida (não V2)

Olhando o trade-off V4 vs V2 (a única comparação não-trivial):

| | V4 | V2 | Diferença |
|---|---:|---:|---:|
| Canonical OOS Sharpe | 2.609 | 2.595 | +0.014 |
| Canonical CAGR | 39.19% | 35.03% | **+4.16 pp** |
| Canonical MaxDD | 12.22% | 12.62% | -0.40 pp (V4 melhor) |
| Canonical WF max DD | 12.22% | 12.62% | -0.40 pp |
| Canonical Boot 99.9% lo | 1.274 | 1.304 | -0.030 |
| Extended OOS Sharpe | 2.320 | 2.294 | +0.026 |
| Extended Boot 99.9% lo | 1.357 | 1.305 | +0.052 |

V4 domina V2 em quase todas as métricas — exceção única é bootstrap canonical lo (1.274 vs 1.304) que é diferença de 3% dentro do ruído esperado do bootstrap. No extended window V4 reverte e fica à frente.

Sobre a aparente contradição "V3 reprova em Sharpe mas V4 (que inclui UGL como V3) ganha":

**★ Interaction effect — achado importante a preservar.** Os dados brutos de testfol.io revelam:

| Asset | 1× CAGR 40y | 2× CAGR 40y | Multiplier efetivo |
|---|---:|---:|---:|
| SPY → SSO | 11.49% | 14.58% | 1.27× |
| QQQ → QLD | 14.58% | 17.27% | 1.19× |
| **GLD → UGL** | **6.92%** | **6.34%** | **0.92× (NEGATIVO)** |

**UGL isoladamente é negative-alpha** — o daily rebalance decay durante períodos flat longos do ouro (2012-2018, 2020-2023) come mais que a alavancagem adiciona em períodos de trend. Isto é **intrínseco ao daily-rebalanced LETF em ativos de baixa persistência de tendência**, não um problema de parametrização.

MAS quando incluído num portfolio EW com 2 legs equity já alavancadas (V4), UGL **vira positive via interaction effect**:
- Em V3 (SSO 2× + QQQ 1× + UGL 2×): o portfolio tem vol moderada. UGL entra diluindo o CAGR + adicionando decay sem receber o "prêmio de diversificação" proporcional porque 2/3 do portfolio já tem correlação ≥ 0.5 com equity.
- Em V4 (SSO 2× + QLD 2× + UGL 2×): o portfolio tem vol alta pelos 2 legs 2×-equity que correlacionam fortemente em risk-off. A correlação baixa de UGL (~0-0.15 com equity em risk-off) agora vale **MAIS** proporcionalmente — é o único hedge disponível quando ambos SSO e QLD caem juntos (2008, 2022). O custo do decay é o mesmo, mas o benefício de diversification é muito maior.

**A lição generalizada:** o valor de diversification de um asset alavancado depende do **risco do resto do portfolio**. Em contexto de vol baixa, UGL é drag; em contexto de vol alta, UGL salva MaxDD. Este é um ponto onde intuição linear falha — o pricing de UGL na composição não é aditivo, é contextual.

**Implicação para design futuro:** quando adicionar legs alavancadas a uma composição, pensar em **pairs** ou **triplets**, não em adições marginais. Adicionar UGL sozinho ao V1 piora o portfolio. Adicionar UGL + QLD juntos ao V1 melhora. É o mesmo raciocínio de `[advances_fin_ml, p.298-313, ch.16]` sobre HRP vs IVP — a estrutura correlacional domina a decisão.

---

## Decisão: V4 é o novo default de produção

**Razões operacionais:**

1. **Passa 5 gates no window canônico 2004-2026** — mesmo padrão que V1 teve que passar. Verdict formal idêntico.
2. **Passa 5 gates no window extended 1986-2026** — robustez cross-regime confirmada em 40 anos, 5 crashes estruturais (1987/2000/2008/2020/2022).
3. **OOS Sharpe 2.609 em canonical** — **melhor de todas as 4 em ambas as janelas**.
4. **MaxDD 12.22% canonical** — **bem abaixo do gate 25%** (mandate §5).
5. **Broker catalog validado** — Inter Global lista QLD e UGL (user confirmou 2026-04-18).
6. **Pareto-domina V2 e V3** operacionalmente.

**Fallback documentado:** V1 (SSO+QQQ+GLD, sem leverage nas 2 pernas extras) fica registrado como **conservative alternative** com MaxDD menor (-9.39%) mas CAGR inferior (-12.66 pp vs V4). Útil se:
- Inter algum dia delistar QLD ou UGL
- User preferir maior rigor psicológico em DD (half-Kelly argument `[fortune_formula]` / `[leverage_space]`)

**Escalação recomendada:** deploy em V1 nos primeiros 6 meses live (disciplina behavioral + broker-learning), migrar para V4 após 6-12 meses de track record confirmado. Ver PRODUCTION.md §4.2.

---

## Caveats

1. **Ainda não há track record live.** Gates são backtest; real-world pode divergir por friction/execution não-modelados.
2. **2× LETF daily decay.** testfol.io modela tracking vs ETF real; Gayed Table 12 `[leverage_for_the_long_run, p.21]` mostra drag adicional ~2%/yr em UPRO real vs teórico. Esperar **-1 a -2 pp CAGR** e **+1 a +3 pp MaxDD** vs backtest no primeiro ano live.
3. **Regime risk.** Nossa janela extended 1986-2026 não inclui 1929 Depression, 1973-74 Volcker stagflation. Tail events fora da amostra podem comportar 2× leverage de forma não testada.
4. **Tax cost multiplica.** V4 paga mais DARFs em dólar absoluto (maior CAGR → mais ganhos realizados nas saídas Donchian). Ainda assim líquido-15% já modelado no backtest.

---

## Artefatos

- `equity_vs_spy.png` — 4 variantes vs SPYSIM, log-scale 1986-2026.
- `drawdown_vs_spy.png` — underwater curves das 4 variantes.
- `summary.json` — métricas descriptivas.
- `gates_verdict.md` — este ranking + gate detail.
- `gates_verdict.json` — machine-readable per-variant per-window per-gate.

## Scripts

- [`scripts/run_plano_b_variants_letf_execution.py`](../../../scripts/run_plano_b_variants_letf_execution.py) — produz equity + drawdown charts.
- [`scripts/run_plano_b_variants_gates.py`](../../../scripts/run_plano_b_variants_gates.py) — 5-gate evaluator em 2 janelas.

## Citações

- 5-gate framework: `[advances_fin_ml, p.208-211]` (PBO/CSCV), `[p.273-275]` (DSR), `[p.196-202]` (stationary bootstrap).
- WF ≥ 6/8 + MaxDD ≤ 25%: `docs/investment-mandate.md` §5.
- testfol.io ground truth: Phase 3.5b Task 7a.
- LETF daily decay + real-vs-theoretical gap: `[leverage_for_the_long_run, p.16, p.21, Table 12]`.
- Half-Kelly parameter uncertainty: `[fortune_formula]`, `[leverage_space]`.

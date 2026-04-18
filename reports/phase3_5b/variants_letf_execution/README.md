# Phase 3.5b — V1–V8 LETF-execution variants

**Path tag:** `[SWING BROKER]` / Plano B.
**Status:** ✅ All 8 variants PASS 5 gates (canonical 2004-2026 + extended 1986-2026).
**Default promoted (2026-04-18):** **V4 (SSO + QLD + UGL)** — best risk-adjusted with safe MaxDD margin.
**Ultra-aggressive alternative (2026-04-18):** **V8 (UPRO + TQQQ + UGL)** — highest CAGR, gate-passing but tight MaxDD margin to 25% cap.

---

## TL;DR

Testamos 8 configurações idênticas em **sinais** (EMA100 no SPY para SSO, Donchian 20/10 em QQQ, Donchian 40/20 em GLD) mas diferentes em **execução** — quando uma perna entra LONG, usamos o ETF 1×, 2×, ou 3× equivalente:

| Variant | Leg 1 (S&P) | Leg 2 (NDX) | Leg 3 (Gold) | Família |
|---|---|---|---|---|
| V1 | SSO **2×** | QQQ 1× | GLD 1× | 2× baseline |
| V2 | SSO **2×** | **QLD 2×** | GLD 1× | 2× NDX added |
| V3 | SSO **2×** | QQQ 1× | **UGL 2×** | 2× gold added |
| **V4** | SSO **2×** | **QLD 2×** | **UGL 2×** | **2× all (default)** |
| V5 | **UPRO 3×** | QQQ 1× | GLD 1× | 3× S&P only |
| V6 | **UPRO 3×** | **TQQQ 3×** | GLD 1× | 3× equity + 1× gold |
| V7 | **UPRO 3×** | QQQ 1× | **UGL 2×** | 3× S&P + 2× gold |
| **V8** | **UPRO 3×** | **TQQQ 3×** | **UGL 2×** | **Max leverage** |

**Nota:** não existe ETF 3× para ouro no mercado US (DGP foi 2× e descontinuado). V7/V8 usam UGL 2× por essa razão estrutural.

Dados: testfol.io ground-truth via `?L=N` (SSOSIM/QLDSIM/UGLSIM/UPROSIM/TQQQSIM) — **zero model risk**, custos FFR-aware e ER baked in para todos os LETFs.

Threshold rebalance 10pp (default produção). 15% BR IR por exit lucrativo. 15 bps switch cost por flip de sinal. DSR n_trials=8.

---

## Verdict ordenado (canonical 2004-2026 — authoritative)

| Rank | Variant | OOS Sh | Stress Sh | Full CAGR | Full MaxDD | WF max DD | DSR p | Boot 99.9% lo | 5 gates |
|---:|---|---:|---:|---:|---:|---:|---:|---:|:-:|
| 1 | **V8 UPRO+TQQQ+UGL** | **2.622** | 2.203 | **58.17%** | -17.14% | 17.14% | 0.0000 | 1.309 | ✅ PASS |
| 2 | **V4 SSO+QLD+UGL** ⭐ | 2.609 | 2.172 | 39.19% | -12.22% | 12.22% | 0.0000 | 1.274 | ✅ PASS |
| 3 | V2 SSO+QLD+GLD | 2.595 | 2.176 | 35.03% | -12.62% | 12.62% | 0.0000 | **1.304** | ✅ PASS |
| 4 | V6 UPRO+TQQQ+GLD | 2.573 | 2.129 | 53.02% | -17.05% | 17.05% | 0.0000 | 1.325 | ✅ PASS |
| 5 | V1 SSO+QQQ+GLD | 2.478 | 2.137 | 26.53% | **-9.39%** | 9.39% | 0.0000 | 1.043 | ✅ PASS |
| 6 | V7 UPRO+QQQ+UGL | 2.428 | 2.053 | 38.98% | -12.38% | 12.38% | 0.0000 | 1.176 | ✅ PASS |
| 7 | V3 SSO+QQQ+UGL | 2.392 | 2.058 | 30.89% | -10.88% | 10.88% | 0.0000 | 1.081 | ✅ PASS |
| 8 | V5 UPRO+QQQ+GLD | 2.354 | 2.022 | 34.46% | -14.06% | 14.06% | 0.0000 | 1.024 | ✅ PASS |

## Verdict ordenado (supplementary 1986-2026, 40y)

| Rank | Variant | OOS Sh | Stress Sh | Full CAGR | Full MaxDD | WF max DD | 5 gates |
|---:|---|---:|---:|---:|---:|---:|:-:|
| 1 | **V8 UPRO+TQQQ+UGL** | **2.348** | 2.203 | **56.39%** | -22.84% | 22.84% | ✅ PASS |
| 2 | **V4 SSO+QLD+UGL** ⭐ | 2.320 | 2.172 | 37.93% | -16.91% | 16.91% | ✅ PASS |
| 3 | V2 SSO+QLD+GLD | 2.294 | 2.176 | 35.00% | -15.81% | 15.81% | ✅ PASS |
| 4 | V6 UPRO+TQQQ+GLD | 2.272 | 2.129 | 52.88% | -20.21% | 20.21% | ✅ PASS |
| 5 | V1 SSO+QQQ+GLD | 2.195 | 2.137 | 25.94% | **-11.13%** | 11.13% | ✅ PASS |
| 6 | V3 SSO+QQQ+UGL | 2.174 | 2.058 | 28.92% | -13.70% | 13.70% | ✅ PASS |
| 7 | V7 UPRO+QQQ+UGL | 2.140 | 2.053 | 36.43% | -13.89% | 13.89% | ✅ PASS |
| 8 | V5 UPRO+QQQ+GLD | 2.085 | 2.022 | 33.32% | -14.06% | 14.06% | ✅ PASS |

**Consistência cross-window:** ranking de OOS Sharpe é **idêntico** entre canonical e extended para as primeiras 4 posições (V8 > V4 > V2 > V6). Algumas posições embaixo trocam mas a separação top-4 vs bottom-4 é estável.

---

## ★ Por que V4 permanece default, não V8 (apesar do V8 ter maior Sharpe)

V8 tem **melhor OOS Sharpe** em ambas janelas (2.622 vs 2.609 canonical, 2.348 vs 2.320 extended). CAGR **dramaticamente superior** (+18.98pp canonical). Mas V4 permanece default por **3 razões operacionais concretas**:

### 1. Margem de segurança ao gate MaxDD 25% (`[mandate §5]`)

| | V4 (default) | V8 (alternative) | Margem do gate 25% |
|---|---:|---:|---|
| Canonical MaxDD | **-12.22%** | -17.14% | V4: 12.78pp / V8: 7.86pp |
| Extended MaxDD | **-16.91%** | -22.84% | V4: 8.09pp / V8: **2.16pp** |

V8 extended MaxDD 22.84% está a **apenas 2.16 pp do gate 25%**. Uma janela de stress pior que 2008/2022 (e.g. stagflação 1973-74 fora da amostra) poderia levar V8 a violar o gate. V4 tem margem muito maior.

### 2. Gayed drag real LETF ~2%/yr vs teórico `[leverage_for_the_long_run, p.21, Table 12]`

testfol.io embute FFR-aware cost mas **não** embute tracking error intra-diário real. Para LETF 3× o drag real é tipicamente 2-3×/yr pior que 2× (compound daily). Aplicando drag esperado:

| | V4 MaxDD backtest | V4 MaxDD real esperado | V8 MaxDD backtest | V8 MaxDD real esperado |
|---|---:|---:|---:|---:|
| Canonical | -12.22% | ~-14-15% | -17.14% | **~-21-24%** |
| Extended | -16.91% | ~-18-20% | -22.84% | **~-27-30%** |

**V8 real (extended) provavelmente VIOLA o gate 25% em produção.** V4 mantém margem segura.

### 3. OOS Sharpe advantage é dentro do ruído bootstrap

V8 OOS Sharpe 2.622 vs V4 2.609 = Δ +0.013. Bootstrap CI lower: V8 1.309 vs V4 1.274 = Δ +0.035. Ambos estão dentro da banda de incerteza paramétrica estimada (half-Kelly argument `[fortune_formula]`, `[leverage_space]`: quando Sharpe é estimado com T=5000+ observações, std(Sharpe) ≈ 1/√T ≈ 0.014). **V8 não é estatisticamente superior a V4 — é marginal.**

### Conclusão operacional

- **V4 é o default** porque o CAGR -19pp menor é compensado pela ordem de magnitude maior de margem ao MaxDD gate.
- **V8 é a ultra-aggressive** documentada — para quem está disposto a aceitar risco de gate-violation em stress events futuros em troca de CAGR ~50% em vez de ~39%.

---

## ★ Interaction effect — achado importante a preservar (UGL sozinho vs UGL com QLD)

Os dados brutos de testfol.io revelaram três LETFs com comportamentos standalone distintos:

| Asset | 1× CAGR 40y | 2× CAGR 40y | 3× CAGR 40y | Multiplier efetivo (3× vs 1×) |
|---|---:|---:|---:|---:|
| SPY → SSO → UPRO | 11.49% | 14.58% | 13.51% | 1.18× |
| QQQ → QLD → TQQQ | 14.58% | 17.27% | **12.16%** | **0.84× (NEGATIVE)** |
| GLD → UGL → — | 6.92% | **6.34%** | N/A | **0.92× (NEGATIVE)** |

**Duas observações estruturais:**

1. **UGL é negative-alpha isolado.** O daily rebalance decay durante períodos flat longos do ouro (2012-2018, 2020-2023) come mais que a alavancagem adiciona em períodos de trend. Intrínseco ao daily-rebalanced LETF em ativos de baixa persistência de tendência.

2. **TQQQ também é negative-alpha isolado em 40y** — mesma lógica que UGL, mas para NDX 3×. Buy-and-hold TQQQ desde 1986 teria CAGR menor que QQQ 1×. Só vale se filtrado por Donchian (segura apenas durante trend LONG).

### Mas ambos viram positive quando colocados em blend EW apropriado

- **V3 (SSO+QQQ+UGL)** — UGL sozinho: Sharpe **2.392** < V1 2.478. UGL **piora** o portfolio.
- **V4 (SSO+QLD+UGL)** — UGL com QLD: Sharpe **2.609** > V1 2.478. UGL **melhora** o portfolio.
- **V5 (UPRO+QQQ+GLD)** — UPRO só: Sharpe **2.354** < V1 2.478. UPRO sozinho **piora**.
- **V8 (UPRO+TQQQ+UGL)** — UPRO + TQQQ + UGL juntos: Sharpe **2.622** > V1. Triplet **melhora**.

### Lição generalizada

**O valor de diversification de um asset alavancado depende do risco do resto do portfolio.** Em contexto de vol baixa, LETFs "extras" são drag; em contexto de vol alta já existente, LETFs adicionais viram hedge proporcional mais valioso. Este é um ponto onde intuição linear falha — o pricing de cada asset na composição **não é aditivo, é contextual**.

Matematicamente: o Sharpe ratio de uma carteira depende de `(weighted_mean_return) / sqrt(weights' @ Cov @ weights)`. Adicionar um asset com:
- Mean negative (UGL, TQQQ standalone) → reduz numerator
- Correlação baixa com resto (UGL vs equity ~0-0.15, TQQQ vs equity varia com vol regime) → reduz denominator

Em portfolio de **baixa vol** (numerador domina), adicionar reduz Sharpe. Em portfolio de **alta vol** (denominador domina), adicionar aumenta Sharpe. O **ponto de transição** depende dos parâmetros específicos — daí a importância de testar cada composição empiricamente em vez de assumir aditividade.

**Implicação para design futuro:** quando considerar expansão do portfolio (nova leg), pensar em **pairs** ou **triplets**, não em adições marginais. Adicionar UGL sozinho ao V1 piora. Adicionar UGL + QLD juntos ao V1 melhora. Adicionar UGL + QLD + UPRO (V8) melhora mais. É o mesmo raciocínio de `[advances_fin_ml, p.298-313, ch.16]` sobre HRP vs IVP — a estrutura correlacional domina a decisão, não os means isolados.

---

## Deploy recommendation por perfil de risco

| Perfil | Variant | CAGR canonical | MaxDD canonical | Quando usar |
|---|---|---:|---:|---|
| Conservador | V1 | 26.53% | -9.39% | Primeiros 6-12m live, behavioral accommodation, disaster recovery (§13 PRODUCTION.md) |
| **Standard** ⭐ | **V4** | **39.19%** | **-12.22%** | **Default produção. Margem sólida ao gate 25%. Promoted 2026-04-18.** |
| Aggressive | V6 | 53.02% | -17.05% | 3× equity sem UGL. Similar ao V8 em risco, menor CAGR — sem vantagem clara sobre V8. |
| Ultra-aggressive | V8 | 58.17% | -17.14% | Para quem aceita risco de gate-violation em stress futuro. **Não recomendado antes de 12-24m track record V4 live.** |

**Escalação recomendada:**

1. Fase 1 (0-6 meses live) — V1 para aclimatar operação + broker + planilha DARF
2. Fase 2 (6-12 meses) — migrar para V4 se V1 performou dentro do esperado (±30% do backtest)
3. Fase 3 (12-24 meses) — reavaliar subir para V6 ou V8 se V4 acumulou cushion equity suficiente para absorver MaxDD maior sem violar psyche

Nunca pular direto de V1 para V8 — o salto de MaxDD -9% para -17% é psicologicamente brutal e aumenta probabilidade de abandono da estratégia no pior momento (`[p.19-20] leverage_for_the_long_run` — "risk of ruin = abandonment").

---

## Caveats

1. **Ainda não há track record live.** Gates são backtest; real-world pode divergir por friction/execution não-modelados.
2. **2× e 3× LETF daily decay.** testfol.io modela FFR-aware mas não tracking error intra-diário real. Gayed Table 12 `[p.21]` mostra drag adicional ~2%/yr em UPRO real vs teórico — proporcionalmente maior em V6/V7/V8. **Esperar -1 a -3 pp CAGR** e **+2 a +5 pp MaxDD** vs backtest no primeiro ano live, especialmente em 3× configs.
3. **Regime risk.** Nossa janela extended 1986-2026 não inclui 1929 Depression, 1973-74 Volcker stagflation. Tail events fora da amostra podem comportar 3× de forma que viola o gate 25%.
4. **Broker liquidity.** QLD AUM $7B (OK), UGL AUM $300M (menor mas líquido), UPRO AUM $3B (OK), TQQQ AUM $20B+ (muito líquido). Limitar orders a 1% ADV para todos LETFs.
5. **Tax cost multiplica.** V8 paga ~200× mais tax em dólar absoluto que V1 em backtest (rebals + Donchian exits × maior equity compondo). Ainda líquido-15% no resultado reportado.
6. **n_trials=8 na DSR.** V1-V4 em sessão anterior usou n_trials=4. Esta bateria expandida usa n_trials=8 (mais conservador). Todas ainda passam com p<0.0001.

---

## Artefatos

- `equity_vs_spy.png` — 8 variantes vs SPYSIM, log-scale 1986-2026.
- `drawdown_vs_spy.png` — underwater curves das 8 variantes.
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
- Risk-of-ruin as abandonment: `[leverage_for_the_long_run, p.19-20]`.
- Correlation-structure decisions (HRP vs IVP): `[advances_fin_ml, p.298-313, ch.16]`.

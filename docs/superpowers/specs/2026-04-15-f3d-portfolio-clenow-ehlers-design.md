# F3.D — Portfolio Combinado Clenow + Ehlers BP Swing

**Data:** 2026-04-15
**Fase:** 2.5 Run 4 Step 2 (F3.D no plano)
**Autor:** Claude Code (brainstorming guiado)
**Status:** design aprovado, aguardando plan de implementação
**Skill usada:** `superpowers:brainstorming`

---

## 1. Contexto

### 1.1 Por que F3.D agora

Os dois primeiros passos do Run 4 falharam ambos os gates anti-overfit do
framework de Phase 3 (CPCV / PBO / DSR / walk-forward):

- **Run 4 Step 1 — AFML meta-labeling simples sobre Ehlers SPY (2026-04-15):**
  PBO 0.647 (piorou vs 0.496 baseline), DSR 0/48 configs pass, WF 0/48 pass,
  best Sharpe 0.575 (abaixo da baseline 0.806). Postmortem: filtro ingênuo
  (split temporal 50/50, RandomForest em ~80 eventos) cortou sinal bom
  junto com ruído e ainda inflacionou N_trials de 24 → 48, piorando a
  deflação do DSR.
- **F3.C — Long-history Ehlers SPY 2005-2023 (2026-04-15):** PBO 0.405 ✅
  (melhorou), DSR best p-value 0.213 (melhorou mas ainda fail), WF 0/24
  pass (piorou — crises 2008/2011/2015/2020/2022 em 8 janelas quebram a
  consistência). Best config (hp=48, lp=20, pct=0.80, stop=0.02): 6/8
  janelas lucrativas, DD máximo 29.44% (gate 25% — **quase passou**).

Padrão observado nas duas rodadas: **edge real mas frágil**. Janela curta
tem Sharpe bruto decente mas falha DSR por amostra pequena. Janela longa
melhora DSR/PBO mas quebra WF em crises específicas. Nem janela isolada
resolve.

### 1.2 Fato estatístico que motiva F3.D

Do Run 2 verdict, `specs/backtest_phase2_5_ehlers.md §"Run — results and
fork"`: correlação entre best equity curves de Clenow e Ehlers BP Swing ≈
**−0.0108** (praticamente ortogonais).

A matemática da diversificação é bem-estabelecida
`[risk_parity, Qian — risk-parity math]`
`[systematic_trading, Carver — diversification multiplier ch.5]`:

- Com ρ ≈ 0 e blend 50/50 **vol-scaled** (vols componentes iguais): σ_portfolio ≈ σ̄ / √2.
- Sharpe esperado do portfolio ≈ 1.41 × média dos Sharpes componentes.
- Com Ehlers 0.806 + Clenow 0.618 → Sharpe esperado ~1.0 **no caso ideal**.
- **1.0 é exatamente o threshold do ROADMAP §Phase 5** ("If DSR < 1.0 → discard").

**⚠️ Caveat crítico:** o cálculo acima assume **vols aproximadamente
iguais** entre os dois componentes. Na v1 (sem vol-scaling) o ganho
real depende do ratio σ_Clenow / σ_Ehlers observado. Se ratio for 2:1, o
Sharpe esperado do portfolio cai pra ~0.83 (componente mais volátil
domina o risco). Ver §5 "Vol mismatch" para mitigação.

### 1.3 Hipótese testável

**H1:** Um portfolio "dois livros separados" com Ehlers BP Swing + Clenow
Momentum (configs fixas nas top-3 dos runs anteriores, blend 50/50,
rebalance ausente na v1) tem Sharpe efetivo ≥ 1.0 e passa PBO + DSR + WF
em:
- 2015-2023 (baseline limpo, sem crise grave)
- 2005-2023 (stress test, inclui 2008/2011/2015/2020/2022)

**Se H1 falhar**, o próximo passo é AFML sofisticado com walk-forward CV
+ features ricas (caminho B, diferido).

---

## 2. Arquitetura

### 2.1 Componentes

```
PortfolioCombined (offline merge, sem mudança no engine)
├── Clenow Momentum (config fixa — top-3 do Run 3 Tiingo)
│   └── universo: SPX 506 Tiingo survivorship-free
├── Ehlers BP Swing (config fixa — top-3 do long-history run)
│   └── universo: SPY Tiingo
└── Combinador
    ├── weights: [0.5, 0.5] fixo
    ├── rebalance: ausente na v1
    └── merge: retornos ponderados → equity curve unificada
```

### 2.2 Decisão de alocação: "dois livros separados" (offline merge)

| Abordagem | Descrição | Pró | Contra | Decisão |
|---|---|---|---|---|
| **Dois livros offline (escolhida)** | Rodar sub-backtests independentes, combinar equity curves offline via retornos ponderados | Zero mudança no engine; reusa 90% do código; defensável com zero parâmetros novos | Pesos divergem dentro do ano se uma sub-estratégia outperformar | ✅ v1 |
| Dois livros com rebalance anual | Mesmo + reset de pesos pra 50/50 todo 1º de janeiro | Mantém diversificação estrita | Requer operação de "transfer de cash entre livros" (complica) | Ablation pós-v1 se v1 passar |
| Vol-scaling contínuo risk-parity | A cada bar, inverso à vol realizada de cada estratégia | Risk-parity formal `[risk_parity, Qian]` | Introduz parâmetro (vol lookback); precisa alavancagem | Considerar se v1 + ablation falharem |

**Justificativa da escolha:** Clenow defende explicitamente "let winners
run" sem rebalance frequente `[stocks_on_the_move]`. Carver reconhece que
rebalance tem custo de turnover `[systematic_trading]`. Em janela de 9-19
anos, sem rebalance, pesos podem divergir mas a ortogonalidade preserva
o efeito de diversificação de longo prazo. **Vale começar simples e
adicionar rebalance como ablation só se v1 passar.**

---

## 3. Grid de Parâmetros + Gates Estatísticos

### 3.1 Grid

Zero parâmetros novos no blend. Única fonte de N_trials é a escolha de
config das sub-estratégias.

| Componente | Configs testadas | Fonte |
|---|---|---|
| Clenow | 3 configs (best + 2 próximas do Run 3 Tiingo por Sharpe) | `reports/grid_clenow_tiingo_postfix_20260415-1005/diagnostic.md` |
| Ehlers BP Swing | 3 configs (best + 2 próximas do long-history run por Sharpe) | `reports/grid_ehlers_20260415-1353/diagnostic.md` |
| Blend | 50/50 fixo | — |

**N_trials = 9 portfolios** (3 × 3). A deflação do DSR escala com
√log(N); vs N_trials = 48 do Run 4 Step 1, √log(9)/√log(48) ≈ 0.77, ou
seja deflação ~23% mais branda.

**Por que não testar só a "melhor" de cada (N = 1):** escolher a melhor
config de cada sub-estratégia *depois* de ver os resultados é overfitting
retroativo `[advances_fin_ml, López de Prado ch.11 — "backtest overfitting"]`.
N = 9 honesto reflete incerteza genuína de qual config individual usar;
não elimina o viés de seleção mas o mitiga.

### 3.2 Gates

Inalterados vs framework Phase 3:

| Gate | Limite | Fonte |
|---|---|---|
| **PBO** | < 0.5 | `[advances_fin_ml, ch.11]` |
| **DSR** best p-value | < 0.05 | `[advances_fin_ml, ch.14]` |
| **Walk-forward** | ≥ 6/8 janelas lucrativas + DD ≤ 25% em cada | `[trading_systems_methods, Kaufman]` |
| **CPCV** distribuição | PSR (Probabilistic Sharpe Ratio) > 0.95 sobre a distribuição combinada | `[advances_fin_ml, ch.12]` |

### 3.3 Janelas de teste

1. **2015-2023 (baseline limpo)** — valida hipótese base "ortogonalidade
   eleva Sharpe o suficiente pra passar DSR". É a janela onde Ehlers teve
   Sharpe 0.806 e Clenow teve Sharpe ~0.618 isoladamente.
2. **2005-2023 (stress test)** — testa se o Clenow-regime-flat durante
   crises (regime filter SPX < SMA200) realmente subsidia o DD do Ehlers
   em 2008/2011/2015/2020/2022. Validação da premissa-core de F3.D.

Executar **2015-2023 primeiro**. Se PASS → 2005-2023. Se FAIL → postmortem
e pular pra AFML sofisticado.

---

## 4. Arquivos + Código

### 4.1 Estratégia de implementação

Merge **offline** das equity curves. Zero mudança no engine
(`src/ai_trade/backtest/engine/`). Cada sub-estratégia roda via
`GridRunner` existente; combinamos as curvas depois com utilitário novo.

### 4.2 Arquivos novos

| Path | Responsabilidade | Linhas est. |
|---|---|---|
| `src/ai_trade/backtest/portfolio/__init__.py` | Export do pacote | ~5 |
| `src/ai_trade/backtest/portfolio/combined.py` | `combine_equity_curves(curves, weights, initial_capital)` + `compute_portfolio_metrics(portfolio_curve)` | ~100 |
| `scripts/run_portfolio_combined.py` | CLI: roda sub-grids (3 Clenow + 3 Ehlers), gera 9 portfolios, valida gates, gera report | ~150 |
| `tests/test_portfolio_combined.py` | Testes unitários do merge + metrics + integração | ~100 |

### 4.3 Arquivos modificados

| Path | Mudança |
|---|---|
| `src/ai_trade/backtest/validation/` | Nenhuma — CPCV/PBO/DSR/WF já operam sobre equity curves genéricas (validado no Run 3) |
| `src/ai_trade/backtest/grid/__init__.py` | Possível export de `PortfolioConfig` dataclass se necessário |
| `pyproject.toml` | **Nenhuma** — sem novas dependências (reusa pandas/numpy/sklearn/matplotlib já presentes) |
| `ROADMAP.md` §"Current status" | Atualização pós-run com verdict |
| `JORNADA.md` | Entrada datada no changelog pós-run |

### 4.4 Fluxo do script CLI

```
scripts/run_portfolio_combined.py:
  1. Parse args: --start, --end, --out (output dir)
  2. load_tiingo_data(SPX_506 + SPY, start, end)
  3. run_clenow_grid(3 configs hard-coded) → 3 equity curves
  4. run_ehlers_grid(3 configs hard-coded) → 3 equity curves
  5. for (c, e) in product(clenow_curves, ehlers_curves):  # 9 portfolios
       combined = combine_equity_curves([c, e], [0.5, 0.5], initial_capital=10_000)
  6. run_cpcv(9 portfolios) → Sharpe distribution
  7. run_pbo(9 portfolios) → PBO score
  8. run_dsr(9 portfolios) → deflated Sharpe + p-values
  9. run_walk_forward(9 portfolios) → 8 windows each
  10. generate_diagnostic.md report + equity PNGs + summary JSON
```

### 4.5 Interface do utilitário core

```python
def combine_equity_curves(
    curves: list[pd.Series],      # equity curves de cada sub-estratégia
    weights: list[float],          # pesos (somam 1.0)
    initial_capital: float,        # capital inicial do portfolio
) -> pd.Series:
    """
    Combina N equity curves via retornos ponderados.

    Steps:
    1. Align temporally via inner join (trunca pro overlap).
    2. Compute retornos pct_change de cada curve.
    3. Portfolio return = sum(weights[i] * returns[i]).
    4. Rebuild equity curve from initial_capital * cumprod(1 + port_ret).

    Citação: `[systematic_trading, Carver — capital allocation]`.
    """
```

### 4.6 Riscos técnicos conhecidos

1. **Equity curves em escalas diferentes** (Clenow pode usar capital
   inicial arbitrário do Ehlers) → resolvido normalizando pra retornos
   antes de combinar.
2. **Alinhamento temporal** (Clenow tem warmup de 90d; Ehlers ~100 bars)
   → `pd.DataFrame.align(method='inner')` e truncar pro overlap.
3. **NaN handling** durante warmup → skipna no pct_change, zero antes do
   primeiro retorno válido.

---

## 5. Caveats Estatísticos

| Caveat | Descrição | Mitigação |
|---|---|---|
| **Crash correlation** | ρ ≈ 0 observado em 2015-2023 (sem crise grave). Em crashes, correlações tendem a 1 `[volatility_trading, Sinclair — "correlation goes to 1 in crashes"]` | Teste 2005-2023 (inclui 2008/2020) valida ou refuta empiricamente |
| **Best-config selection bias** | Escolher top-3 de runs anteriores é overfit implícito | N = 9 (3 × 3) em vez de N = 1 reflete incerteza de escolha; não elimina, mitiga |
| **Period mismatch** | Clenow "best" veio de Tiingo 2015-2023; Ehlers "best" de 2005-2023. Configs podem não co-existir otimamente | Re-rodar grid Clenow em 2005-2023 **antes** do teste long-history |
| **Rebalance ausente** | Dois livros divergem ao longo do tempo. Em 19a, se um componente outperformar 5 ×, pesos podem ir pra ~83/17 | v1: aceitar (Clenow-style). v2: rebalance anual como ablation se v1 passar |
| **Tiingo survivorship em SPX** | Run 3 confirmou que universo survivorship-honest é mais estrito que yfinance, e Clenow piorou (PBO 0.524 → 0.603). Não é bug, é honestidade | Aceitar; portfolio pode compensar via diversificação com Ehlers (que não sofre desse problema em SPY single-asset) |
| **Vol mismatch entre componentes** | v1 usa blend 50/50 sem vol-scaling. Se σ_Clenow ≠ σ_Ehlers, o componente mais volátil domina o risco e o Sharpe real do portfolio fica abaixo do ideal de 1.41× a média | (a) Reportar σ de cada sub-estratégia no diagnostic.md pra checar premissa. (b) Se ratio > 1.5, v2 com vol-scaling contínuo entra no menu (ver §8 "Fora de escopo"). |

---

## 6. Plano de Execução

### 6.1 Ordem dos passos

1. **TDD (Test-Driven Development) primeiro** — escrever `tests/test_portfolio_combined.py` antes de `combined.py`:
   - `test_combine_returns_correctly_weighted` — 2 curves sintéticas com retornos conhecidos
   - `test_combine_aligns_temporally` — curves com períodos overlappantes diferentes
   - `test_combine_preserves_initial_capital` — final equity ≠ 0
   - `test_weights_must_sum_to_one` — validação de input
2. **Implementar `combined.py`** — passar os testes acima (~100 linhas).
3. **Testes de integração** — mockar sub-estratégias, rodar pipeline end-to-end.
4. **Implementar `scripts/run_portfolio_combined.py`** (~150 linhas).
5. **Run v1: 2015-2023** — gates.
6. **Decisão sobre v2:** se v1 PASS → re-rodar grid Clenow em 2005-2023 → rodar portfolio v2 em 2005-2023. Se v1 FAIL → postmortem e ir pra caminho B.
7. **Report final** — diagnostic.md + entrada em `JORNADA.md` + update em `ROADMAP.md §"Current status"`.

### 6.2 Critério go/no-go

| Outcome v1 | Outcome v2 | Ação |
|---|---|---|
| PASS | PASS | F3.D sucesso → avançar pra Phase 3 (Universe Selector ou Phase 4 prep) |
| PASS | FAIL | Portfolio aguenta períodos normais mas não crises → adicionar regime filter no Ehlers, ou ir pra AFML sofisticado |
| FAIL | — (não roda) | Ortogonalidade não salva → caminho B (AFML sofisticado com walk-forward CV + features) |

### 6.3 Tempo estimado

- Implementação + testes: ~3-4h.
- Runs: < 10min wallclock cada (grid framework já validado).
- Análise + docs: ~1h.
- **Total: ~5-6h de sessão.**

### 6.4 Baseline de testes

362/362 verdes atualmente (incluindo 10 do `ehlers_meta` do Run 4 Step 1).
Após F3.D: meta +9 testes novos → **371 testes, 100% verdes**. Não quebrar
baseline `[.claude/CLAUDE.md "Convenções de código"]`.

### 6.5 Próximos passos pós-run (independente do verdict)

1. Verdict documentado em `JORNADA.md` changelog (linguagem humana, regra
   inviolável do projeto).
2. `ROADMAP.md §"Current status"` atualizado.
3. Se v1+v2 PASS: Phase 3 sub-universo Pepperstone ou Phase 4 paper
   trading prep entra em discussão.
4. Se FAIL: ROADMAP atualiza "caminho B" (AFML sofisticado) como próximo
   ciclo, com roteiro claro:
   - `scikit-learn` walk-forward CV com embargo (López de Prado `[advances_fin_ml, ch.7]`).
   - Features estendidas: `[osc, dcp, hp, ss_trend, atr20, regime_flag, vix_proxy, volume_z]`.
   - Triple-barrier labeling mais agressivo (TP/SL assimétricos).
   - Universo de treino: long-history 1993-2026 (Tiingo widest bulk).

---

## 7. Referências

### 7.1 Livros citados

| Slug | Tópico usado |
|---|---|
| `advances_fin_ml` (López de Prado) | PBO ch.11, DSR ch.14, CPCV ch.12, walk-forward CV ch.7 |
| `stocks_on_the_move` (Clenow) | Regime filter SMA200, "let winners run" (no rebalance frequente) |
| `systematic_trading` (Carver) | Diversification multiplier ch.5, capital allocation |
| `risk_parity` (Qian) | Risk-parity math (σ_port com ρ ≈ 0) |
| `volatility_trading` (Sinclair) | Crash correlation ("correlation goes to 1 in crashes") |
| `trading_systems_methods` (Kaufman) | Walk-forward gate (≥ 6/8 + DD ≤ 25%) |

### 7.2 Artefatos do projeto

| Path | Uso |
|---|---|
| `reports/grid_clenow_tiingo_postfix_20260415-1005/diagnostic.md` | Fonte das top-3 configs Clenow |
| `reports/grid_ehlers_20260415-1353/diagnostic.md` | Fonte das top-3 configs Ehlers long-history |
| `specs/backtest_phase2_5_ehlers.md §"Run — results and fork"` | Verdict ρ = −0.0108 entre Clenow × Ehlers |
| `src/ai_trade/backtest/validation/` | CPCV/PBO/DSR/WF reutilizados |
| `src/ai_trade/backtest/grid/` | GridRunner genérico reutilizado |
| `src/ai_trade/backtest/strategies/{clenow,ehlers_bp_swing}.py` | Sub-estratégias reutilizadas |
| `logs/f3d.log` | Log unificado de progresso desta sessão |

---

## 8. Fora de Escopo (Explícito)

Itens **intencionalmente** não incluídos em F3.D v1, deferidos:

- **Rebalance anual** — ablation pós-v1 se v1 passar.
- **Vol-scaling contínuo** — ablation pós-v1 se rebalance não for suficiente.
- **AFML sofisticado** — caminho B, entra em próximo ciclo se F3.D falhar.
- **Regime filter no Ehlers** — entra se v1 PASS + v2 FAIL.
- **Multi-asset Ehlers** (não-SPY) — Run 3 já testou e falhou; não repetir.
- **Carver multi-asset trend** / **Chan cointegration** — caminho D, só
  após F3.D + AFML sofisticado esgotados.
- **Phase 3 (sub-universo Pepperstone)** — só entra se F3.D passar os dois
  testes (2015-2023 + 2005-2023).

---

**Design aprovado em 2026-04-15 pelo usuário (seções 1-4 revisadas em
chat). Próximo passo: invocar `superpowers:writing-plans` para produzir
plan de implementação detalhado.**

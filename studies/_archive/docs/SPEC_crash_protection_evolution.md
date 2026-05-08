# SPEC — Evolução da estratégia EMA/SMA threshold com proteção de crash

> **Propósito deste documento**: servir de contexto/instruções para uma
> próxima sessão que vai evoluir a estratégia educacional `EMA/SMA
> threshold crossover` com dois mecanismos novos: (A) sinais preditivos
> de crash da literatura e (B) stop-loss configurável. Quando abrir a
> próxima sessão, cole este arquivo e peça pra começar.

---

## 0. TL;DR (o que fazer)

Estender os 3 estudos existentes (`ema_sma_threshold_educational`,
`ema_sma_threshold_spy_real`, `ema_sma_threshold_nasdaq_real`) com:

1. **Stop-loss por drawdown-from-peak** — novo eixo de grid: `stop_loss_pct
   ∈ {None, 15%, 20%, 25%, 30%, 35%, 40%}`. Testar **3 modos de re-entry**
   diferentes.
2. **Sinais preditivos de crash** (CAPE, EBP, yield curve, VIX term, LPPLS)
   como **de-leveraging signal** — reduzir buy_leverage dinamicamente
   quando risco sistêmico sobe, em vez de zerar posição.
3. **Composite risk score** combinando múltiplos indicadores.
4. Rodar sweep completo + todas as analyses (including rolling windows +
   worst-case + 50/50 portfolio impact).

**Meta principal**: reduzir MDD de 54% (top config `EMA_N150_th5_bL3_sL0`)
para algo entre 25-40% sem sacrificar mais que 3-5pp de CAGR.

**Meta de validação**: top configs precisam passar ≥ 5/7 gates no 40y
synth E ≥ 4/7 gates no SPY real/NDX real. Não aceitar gate-waiving só
porque adicionamos parâmetros.

---

## 1. Contexto (o que já foi construído)

### 1.1 Estudos existentes

| Estudo | Dataset | Janela | Top-1 config | CAGR | MDD |
|---|---|---|---|---|---|
| `ema_sma_threshold_educational` | SPYSIM synth testfolio | 1986-2026 (40y) | `EMA_N150_th5_bL3_sL0` | 27.67% | 54% |
| `ema_sma_threshold_spy_real` | Tiingo SPY/SSO/UPRO | 2009-2026 (17y) | `EMA_N150_th5_bL2_sL0` | 15.10% | 39% |
| `ema_sma_threshold_nasdaq_real` | Tiingo QQQ/QLD/TQQQ | 2010-2026 (16y) | `SMA_N150_th0_bL2_sL0` | 25.32% | 41% |

Todos os três:
- `configs/NN_<cfg_id>/` subpastas com `summary.md`, `equity.png`, `trades.csv`
  para top-20.
- `FINAL.md` com ranking pure + tax15.
- `analyses/` com rolling windows, equity-vs-benchmark, worst-case,
  portfolio 50/50.

### 1.2 Código reusável (não reinventar)

- **Simulator core**: `src/market_lab/backtest/strategies/ema_sma_threshold_educational.py`
  - `EMASMAThresholdConfig` (filter, lookback, threshold_pct, buy_leverage, sell_leverage, tax_rate, fee, switch_cost_bps)
  - `simulate_ema_sma_threshold(prices, returns, cfg)` — synth path
  - `simulate_regime_threshold_with_legs(signal_prices, buy_leg, sell_leg, cfg)` — real path
  - `compute_threshold_regime(prices, cfg)` — histerese band signal
  - `Trade` dataclass e `ThresholdResult` com trade ledger
- **Grid orchestrator**: `src/market_lab/backtest/grid/ema_sma_threshold_grid.py`
  - `EMASMAThresholdAxes` (cartesian)
  - `compute_config_metrics`, `compute_composite_scores`, `evaluate_gates`
- **Real ETF runner**: `src/market_lab/backtest/grid/real_etf_regime_runner.py`
  - `RealETFMarket` (SPY_MARKET, NDX_MARKET)
  - `build_data_bundle`, `simulate_config_with_real_legs`
- **Report helpers**: `src/market_lab/backtest/grid/real_etf_report_helpers.py`
  - `emit_all_artifacts` — gera FINAL.md + configs.csv + per-config subfolders
- **Analyses**: `src/market_lab/backtest/grid/real_etf_analyses.py`
  - `run_rolling_windows_analysis` — rolling 3/5/7/10y
- **Validation gates** (todos ativos): `src/market_lab/backtest/validation/`
  - `pbo.py`, `dsr.py`, `walk_forward.py`, `bootstrap.py`, `cpcv.py`

### 1.3 Descobertas-chave das análises

1. **Gayed p.21 Table 12 confirmado**: synth 3x UPRO supera real em 2-3pp/ano.
2. **Look-ahead bug descoberto e fixado** em `plano_a_leveraged_rotation.py`
   commit `7b90a8f`. Mesmo pattern existia no `letf_rotation.py` (nunca
   patchado) e no meu simulator inicial (patchado + regression test).
3. **G3 Walk-Forward é o gate mais duro**: 0/384 passam pelo limite MDD<25%
   por janela. Signal é robusto (top passes 6/7) mas drawdown discipline não.
4. **Rolling windows 40y synth**: top-1 bate SPY em 100% das janelas 5/10/15/20y.
5. **Real data (SPY 17y)**: edge cai para 0.10pp no top-1, Sharpe pior que
   B&H (0.71 vs 0.90). Strategy é basicamente equivalente a SPY após custos.
6. **NDX real**: edge se mantém, top-1 com +6pp CAGR e Sharpe equivalente.
7. **Forecasts institucionais 2026-04** (Goldman 7.7%, Vanguard 4.5%,
   Research Affiliates 3.1%, Shiller 1.3%, Buffett Ind -0.7%):
   expected 50/50 blend é **6-12%**, não 20%.
8. **Usuário declarou compromisso** com a estratégia para live com staging
   e stop pré-comprometido.

### 1.4 Documento de referência existente

O arquivo `studies/crashes_sp500_e_indicadores_preditivos.md` já
consolidou papers/indicadores de previsão de crash. **Este spec usa
aquele doc como base** — a próxima sessão NÃO precisa re-pesquisar a
literatura, só escolher quais indicadores implementar.

Resumo do que já está lá:
- **Valuation**: Campbell-Shiller CAPE, Excess CAPE Yield, P-CAPE (Haghani 2024)
- **Macro**: Yield curve (Estrella-Mishkin probit), NY Fed recession probability
- **Crédito**: Excess Bond Premium (Gilchrist-Zakrajšek 2012) — paper mais forte
- **Vol**: VIX > 30, VIX term backwardation, SKEW
- **Preço**: LPPLS Confidence (Sornette) — biblioteca `lppls` PyPI
- **Rede**: Multiplex Recurrence Networks (Guo 2024) — avançado
- **ML**: Chatzis 2018, Shankar 2025 — secundário
- **Framework composto**: `Risk_t = Σ w_i · z(indicator_i)`

---

## 2. Motivação (por que evoluir agora)

O usuário está disposto a ir live com staging, mas o principal risco é o
**54% MDD do top config 3x UPRO cash**. Três observações:

1. **Quando SPY cai, UPRO cai 3× mais rápido**. O EMA-150 ±5% leva
   20-40 bars pra flipar. Em crash rápido (março 2020: SPY -34% em 22d),
   o UPRO já perdeu 60-70% antes do signal ejetar.
2. **Existem sinais na literatura** que antecipam crashes em semanas-meses,
   não dias. CAPE, EBP, yield curve dão leads de 6-24 meses. LPPLS dá
   leads de dias-semanas. Usando esses sinais, podemos **de-leverage antes
   do crash**, não durante.
3. **Stop-loss por DD é o mecanismo mais simples** — se o portfolio cair
   X%, sair temporariamente. Não é ótimo (pode perder whipsaw recovery),
   mas é **validável empiricamente** e tem implementação trivial.

### Pergunta central

> **Podemos reduzir o MDD do top config de 54% para 25-40% sem sacrificar
> mais que 3-5pp de CAGR, usando stop-loss e/ou sinais preditivos
> validados na literatura?**

---

## 3. Escopo da próxima sessão

### 3.1 Dois mecanismos novos

#### A. Stop-loss por drawdown-from-peak

**Sinal de exit** além do regime normal:
```
current_dd = equity / running_peak - 1
if current_dd <= -stop_loss_pct:
    regime = -1 forced (cash)  # stop triggered
```

**Eixo de grid**:
- `stop_loss_pct ∈ {None, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40}` (7 valores)

**Re-entry: 3 modos a testar**:

1. **`next_signal`** — esperar o próximo cross-up normal (price > MA +
   threshold). Mais conservador. Perde recovery rápido.
2. **`time_cooldown`** — esperar N dias após stop, depois respeitar
   signal normal. Sweep N ∈ {21, 63, 126} (1m / 3m / 6m).
3. **`recovery_trigger`** — re-entrar quando price subiu X% do local
   bottom pós-stop. Sweep X ∈ {0.05, 0.10, 0.15}. Captura recovery
   mais cedo.

**Novo config field**:
```python
stop_loss_pct: float | None = None
reentry_mode: Literal["next_signal", "time_cooldown", "recovery_trigger"] = "next_signal"
reentry_param: float | int | None = None  # cooldown days or recovery %
```

#### B. Crash predictor como de-leveraging signal

Em vez de zerar quando risco sobe, **reduzir leverage gradualmente**:
```
base_leverage = cfg.buy_leverage  # e.g., 3.0
risk_score = compute_risk_score(t)  # 0..1
effective_leverage = base_leverage * (1 - λ * risk_score)
# λ ∈ {0.3, 0.5, 0.7} — quanto reduz por unidade de risco
```

**Indicadores a testar** (ordem de prioridade):

1. **Excess Bond Premium (EBP)** — Gilchrist-Zakrajšek 2012. Fed publica
   CSV em `federalreserve.gov/econres/notes/feds-notes/ebp_csv.csv`.
   Série mensal desde 1973. **Mais forte preditor de recessão na
   literatura pós-2012**. Z-score rolling 60 meses.

2. **Term Spread (yield curve)** — T10Y3M da FRED via `pandas_datareader`.
   Z-score rolling 60 meses. Inversão (spread < 0) = sinal histórico.

3. **CAPE ratio** — Shiller database (multpl.com/shiller-pe scrape OU
   arquivo CSV do site de Shiller). Z-score rolling 10 anos.

4. **VIX term backwardation** — VIXCLS (FRED) + VX1/VX2 de futuros.
   Pode usar só VIX > 30 como proxy simples se VX term não estiver
   acessível.

5. **LPPLS Confidence** — biblioteca `lppls` no PyPI. Custo computacional
   alto; rodar semanal, não diário.

**Composite risk score**:
```
risk_t = Σ w_i · sigmoid(z_i_t)
```
com `w_i = 1/n` (equal-weight inicial, para evitar fit).

### 3.2 Novo eixo de grid — **total: ~7680 configs** (enorme)

Ou seja: base axes (384) × stop_loss variants (7) × risk-signal variants
(5+) = muito grande. **Não rodar full grid** — usar estratégia faseada:

**Fase 1 — Stop-loss isolado (no risk signal)**:
- 20 top configs existentes × 7 stop-loss × 3 re-entry modes × 3 reentry_param
- = 20 × 63 = 1260 configs
- Roda rápido (~30 min com gates)

**Fase 2 — Risk signal isolado (no stop-loss)**:
- 20 top configs × 5 indicators × 3 λ values
- = 20 × 15 = 300 configs

**Fase 3 — Combinação best-of-fase-1 + best-of-fase-2**:
- Top 10 da Fase 1 × top 5 da Fase 2 = 50 configs
- Full gates + rolling windows

**Fase 4 — Validação em real data (SPY e NDX)**:
- Top 5 de Fase 3 em SPY real + NDX real
- Aplicar todas as analyses existentes + nova "crash comparison"

---

## 4. Implementação sugerida

### 4.1 Novo módulo: `stop_loss_and_risk_signals.py`

Localização: `src/market_lab/backtest/strategies/stop_loss_and_risk_signals.py`

**Contém**:
- `StopLossConfig` dataclass (`stop_loss_pct`, `reentry_mode`, `reentry_param`)
- `RiskSignalConfig` dataclass (`indicator_type`, `lookback`, `lambda_de_lever`)
- `simulate_with_stop_loss(signal_prices, buy_leg, sell_leg, cfg, stop_cfg)` — variante que incorpora stop + re-entry
- `simulate_with_risk_signal(signal_prices, buy_leg, sell_leg, cfg, risk_series)` — variante que usa `risk_series` pré-computada para ajustar leverage
- `simulate_with_both(...)` — versão final combinada

### 4.2 Loader de dados macro: `macro_data_loader.py`

Localização: `src/market_lab/backtest/data/macro_data_loader.py`

**Funções**:
- `load_ebp(vintage_date=None) -> pd.Series` — EBP mensal do Fed, com
  opção de usar vintage histórico (ALFRED) para honest backtest.
- `load_term_spread(series="T10Y3M") -> pd.Series` — via pandas-datareader FRED.
- `load_cape() -> pd.Series` — Shiller CSV.
- `load_vix() -> pd.Series` — VIXCLS da FRED.
- `load_nyfed_recession_prob() -> pd.Series` — opcional.

**Honest backtest**:
- Todas as séries precisam ser **alinhadas com lag** (publish date ≠ ref date).
- EBP: publicado ~30 dias após fim do mês. Usar `series.shift(21)` (21 trading days).
- CAPE: usar earnings reported (~45 dias de lag). `series.shift(32)`.
- Term spread: disponível t+1. `series.shift(1)`.

### 4.3 Indicador LPPLS — módulo separado

Localização: `src/market_lab/backtest/signals/lppls_confidence.py`

Wrapper fino sobre biblioteca `lppls` do PyPI. Custo alto → rodar uma vez
offline, salvar `pd.Series` em parquet, carregar no sweep.

```bash
uv pip install lppls
```

### 4.4 Grid orchestrator

Estender `EMASMAThresholdAxes` ou criar novo `EnhancedAxes`:
```python
@dataclass(frozen=True)
class EnhancedThresholdAxes(EMASMAThresholdAxes):
    stop_loss_pcts: tuple[float | None, ...] = (None, 0.25, 0.30, 0.35)
    reentry_modes: tuple[str, ...] = ("next_signal", "time_cooldown", "recovery_trigger")
    cooldown_days_options: tuple[int, ...] = (21, 63, 126)
    recovery_trigger_pcts: tuple[float, ...] = (0.05, 0.10, 0.15)
    risk_indicators: tuple[str, ...] = (None, "ebp", "term_spread", "cape", "vix", "composite")
    lambda_de_levers: tuple[float, ...] = (0.0, 0.3, 0.5, 0.7)
```

### 4.5 Estrutura de saída

```
studies/ema_sma_threshold_crash_protected/
├── SPEC.md                              # copy of this file
├── README.md
├── run_sweep.py                         # main CLI
├── FINAL.md                             # best configs com crash protection
├── configs.csv
├── summary.json
├── configs/                             # top-30 per-config detail
│   ├── 01_<cfg_id>_sl25_cooldown63/
│   │   ├── summary.md
│   │   ├── equity.png                   # strategy + stop-loss triggers
│   │   ├── trades.csv
│   │   └── stops_triggered.csv          # data, dd%, re-entry date
│   └── ...
├── analyses/
│   ├── 01_stop_loss_sweep.md            # Fase 1 results
│   ├── 02_risk_signal_comparison.md     # Fase 2 per-indicator
│   ├── 03_combined_crash_protection.md  # Fase 3 top combinations
│   ├── 04_mdd_reduction_effectiveness.md# quanto cada mecanismo salva
│   ├── 05_specific_crashes/             # behavior during 2000, 2008, 2020, 2022
│   │   ├── 2000_dotcom.md + .png
│   │   ├── 2008_gfc.md + .png
│   │   ├── 2020_covid.md + .png
│   │   └── 2022_bear.md + .png
│   └── 06_rolling_windows_protected.md  # rolling stability
```

---

## 5. Experimentos específicos

### 5.1 Fase 1 — Stop-loss isolado

Pra cada top-20 config dos 3 estudos existentes, variar
`stop_loss_pct ∈ {0.15, 0.20, 0.25, 0.30, 0.35, 0.40}` × 3 re-entry modes.

**Métricas a reportar por config**:
- CAGR, Sharpe, MDD (mesmo de sempre)
- **Novas**: `n_stops_triggered`, `avg_days_from_stop_to_reentry`,
  `cagr_saved_vs_baseline` (positive = stop helped), `mdd_reduced_vs_baseline`
- **Per-crash analysis**: em cada crash histórico (2000, 2008, 2020),
  o stop disparou? Em que data? Qual o DD no ponto do stop? Qual foi o
  DD que a strategy teria tido sem stop?

**Pergunta específica a responder**:
> "Se colocar stop-loss em 25%, quantos falsos positivos (stops em
> drawdowns que iam recuperar sem catastrofia) vs verdadeiros positivos
> (stops em 2008 que salvaram de MDD 60%+)?"

### 5.2 Fase 2 — Risk signal de-leveraging

Pra cada top-5 config dos 3 estudos, testar cada indicador individualmente.

**Lambda sweep**:
- `λ=0.0` (baseline, sem de-leveraging)
- `λ=0.3` (30% de redução no pico do risco)
- `λ=0.5` (50% de redução no pico)
- `λ=0.7` (reduz drasticamente até quase cash)

**Pergunta específica**:
> "Qual indicador (EBP / term spread / CAPE / VIX / LPPLS) produz o
> melhor ratio Δmdd/ΔCAGR? Qual tem menos whipsaw?"

### 5.3 Fase 3 — Combinação

Top 10 stop-loss configs × top 5 risk signal configs = 50 configs finais
com gates + rolling windows + worst-case.

### 5.4 Fase 4 — Real-data validation

Levar os 3-5 melhores de Fase 3 para `spy_real` e `ndx_real`.
Métricas-chave:
- Δmdd vs baseline (quanto reduziu)
- ΔCAGR vs baseline (custo do seguro)
- Effectiveness ratio = Δmdd / ΔCAGR (quanto de MDD saved por pp de CAGR perdido)

### 5.5 Crash-specific analyses

Para cada crash histórico (2000 dot-com, 2008 GFC, 2020 COVID, 2022
bear), produzir um mini-report:
- Timeline day-by-day do strategy equity
- Data do stop trigger (se houver)
- Data do re-entry
- DD evitado vs DD realizado
- Comparação com buy-hold SPY no mesmo período
- Equity curve plot zoom nesse crash

---

## 6. Constraints de validação

### 6.1 Gates honestos (inviolável)

Todos os configs finais passam pelos 7 gates existentes:
- G1 PBO < 0.5 `[advances_fin_ml, p.208-211]`
- G2 DSR p < 0.05 `[advances_fin_ml, p.222-223]`
- G3 Walk-Forward 6/8 + MDD<25% por janela `[advances_fin_ml, ch.12]`
- G4 OOS 70/30 Sharpe > 0
- G5 FWD post-2020 Sharpe > 0
- G6 Bootstrap 99.9% CI low > 0 `[advances_fin_ml, p.196-202]`
- G7 Cross-lib ±3pp CAGR `[advances_fin_ml, p.31-34]`

**Novo gate opcional G8** pra este estudo:
- G8 "MDD reduction effective" — config com stop precisa reduzir MDD em
  ≥ 5pp vs baseline sem stop. Se não reduzir, o stop não está fazendo
  nada útil.

### 6.2 DSR com n_trials correto

**Importante**: ao expandir grid de 384 → ~1260 (Fase 1) ou mais, o DSR
penalty aumenta porque `n_trials = new_grid_size`. Precisa reportar DSR
com n_trials do grid combinado, não só do subset.

`[advances_fin_ml, p.222-223]`: E[SR_max] sob null ∝ √(ln N_trials).
Ir de 384 → 1260 aumenta benchmark_sharpe em ~12%. Não é catastrófico
mas aumenta a barra.

### 6.3 Small-sample warning

O doc de referência (`crashes_sp500_e_indicadores_preditivos.md`) alerta:
> "5-8 crashes genuínos em 90+ anos. Qualquer hyperparameter tuning
> destrói o sinal. Grid mínimo."

Implicação: **não expandir grid de risk signals arbitrariamente**. Testar
cada indicador com 1-2 parâmetros fixos dos papers originais, não varrer
lookbacks/thresholds livremente. Justificativas por citação
`[book.slug, p.X]`.

### 6.4 Respeitar mandate

Mandate §1: projeto em MAINTENANCE, 100% Plano C. Este estudo continua
**educacional/experimental**. Não propõe reativar slot A/B/D ativo.

Se descobrirmos config robusto (MDD 25-35% + CAGR 15-20% líquido +
passa 6/7 gates em todos os 3 datasets), isso pode virar **material pra
uma futura reativação proposta de slot B**, mas não automaticamente.

### 6.5 Honest data handling

- **EBP e CAPE**: usar vintages do ALFRED, não latest-revised. Senão
  look-ahead bias.
- **CAPE tem lag de ~45 dias**. `series.shift(32)` no daily.
- **LPPLS rodado offline** com data disponível no momento t (não
  futuro). Salvar parquet vintage.

### 6.6 Cross-lib (G7) ainda aplicável

Cada nova variante precisa ter hand-rolled (numpy puro, sem pandas)
implementada e bater dentro de ±3pp CAGR da vectorized. Pattern já
existe em `ema_sma_threshold_grid.py:_evaluate_g7_cross_lib`.

---

## 7. Deliverables da próxima sessão

1. **Código**:
   - `src/market_lab/backtest/strategies/stop_loss_and_risk_signals.py`
   - `src/market_lab/backtest/data/macro_data_loader.py`
   - `src/market_lab/backtest/signals/lppls_confidence.py`
   - `src/market_lab/backtest/grid/crash_protected_grid.py` (extensão)
   - Testes unitários: `tests/test_stop_loss.py`, `tests/test_risk_signals.py`,
     `tests/test_macro_loader.py` (mock dados Fed/FRED)
   - Baseline pytest não quebra (hoje 1097 passed).

2. **Estudo novo**: `studies/ema_sma_threshold_crash_protected/`
   - Estrutura descrita em §4.5
   - README + FINAL + per-config subfolders + analyses subfolders

3. **Documentos de decisão**:
   - `studies/ema_sma_threshold_crash_protected/DECISION_LOG.md` — por que
     escolhemos cada indicador, cada parâmetro, cada λ
   - `studies/ema_sma_threshold_crash_protected/DATA_PROVENANCE.md` —
     fonte e vintage de cada série usada

4. **Jornada entry**:
   - `jornada/YYYY-MM-DD-HHmm-crash-protection-study.md`
   - Atualizar `jornada/README.md` com entrada no topo

5. **Update portfolio analysis**:
   - Re-rodar `run_portfolio_5050.py` substituindo o top config
     atual pelo melhor crash-protected config.
   - Novo MDD blend 50/50 esperado: 25-35%.

---

## 8. Pontos de atenção específicos

### 8.1 Sobre o "quando volto depois do stop"

O usuário sinalizou a tensão: "o preço cai pra -26% (stop em -25%), rebounda
e sobe muito — eu perco isso". Três pontos:

1. **Esse é o preço do seguro**. Stop-loss é fundamentalmente trade-off
   de crash protection vs whipsaw cost. Precisa medir empiricamente.
2. **Re-entry `recovery_trigger`** é desenhado exatamente pra isso — volta
   quando preço sobe 5-10% do local bottom pós-stop. Captura recovery
   rápido, mas introduz novo parâmetro (whipsaw risk em chop).
3. **Re-entry `time_cooldown`** simplifica: aguenta N dias (21/63/126),
   depois respeita signal normal. Menos parâmetros, mais robusto.

**Minha recomendação**: testar todos os 3 re-entry modes na Fase 1 com
**mesmo set de stop_loss_pct**. Escolher baseado em:
- CAGR final (não só MDD)
- % de stops falsos-positivos (stops em drawdowns que iam recuperar
  dentro de 6 meses)
- Sensibilidade ao threshold (se muda muito com parametro, é overfit)

### 8.2 Sobre o "quando rebounda e fica muito tempo underwater"

Outro caso real: stop dispara em -25%, preço fica 2 anos entre -30 e -20%,
depois dispara. O `next_signal` modo só reentra quando price cruza MA
+ threshold, que pode demorar mais que esses 2 anos. **Você perde toda
a recuperação base**.

Analise per-crash específica deve cobrir isso:
- 2000-2002: SPY perdeu 49%. Em que data stop disparava? Quanto tempo
  ficou fora? Quanto perdeu ao não capturar o 2003 rally?
- 2008-2009: SPY perdeu 57%. Idem.
- 2020: COVID crash foi 34% em 32 dias. Stop provavelmente disparou. Que
  re-entry mode pegou melhor o rally subsequente (mar-ago 2020)?

### 8.3 Sobre indicadores de crash serem "ineficazes em Trump-era"

O doc de referência menciona: yield curve inverteu 2022-2024 sem produzir
recessão clássica. CAPE > 30 por quase toda década 2010s sem crash.

**Implicação prática**: um de-leveraging signal que reduz leverage por 5-7
anos (toda a década de 2010) destrói a CAGR. Precisa de:
- **Sigmoide** em vez de linear (só de-levera acima de threshold alto)
- **Time-decay** se condição persiste sem crash
- **Composite** com confirmação múltipla (exige ≥ 2 indicadores em stress
  simultaneamente antes de de-leveragear)

### 8.4 Sobre comportamento durante circuit breakers

Crash 2020: SPY caiu 12% em 1 dia (16 de março). Circuit breakers param
negociação 3 vezes em uma semana. **Stop-loss que dispara intraday pode
não conseguir executar se mercado está parado**. Modelo realista: stop
dispara no close (não intraday). Isso é pior que ideal mas honest.

### 8.5 Sobre alavancagem dinâmica (continuous vs discrete)

Opção A — continuous: `effective_leverage = 3 × (1 - λ · risk_score)`.
Ex: com λ=0.5 e risk=0.5, leverage cai pra 2.25.

Opção B — discrete: steps {3x, 2x, 1x, 0x} conforme bands do risk_score.
Mais tratável operacionalmente (menos rebalancing), mais jumpy.

Testar **ambas**. Minha expectativa: continuous é melhor em backtest mas
discrete é mais executável em live. Reportar ambos.

---

## 9. Referências

### 9.1 Papers (todos já resumidos em `crashes_sp500_e_indicadores_preditivos.md`)

- Campbell & Shiller (1988) — CAPE
- Shiller & Jivraj (2017) — Excess CAPE Yield
- Gilchrist & Zakrajšek (2012) — EBP, AER 102(4)
- Estrella & Mishkin (1998) — yield curve probit
- Filimonov & Sornette (2013) — LPPLS calibration, Physica A
- Scheffer et al. (2009) — Early Warning Signals, Nature
- López de Prado (2018) `[advances_fin_ml]` — ch.7, 11, 12, 14
- Bailey-Borwein-López de Prado-Zhu (2014) — PBO paper

### 9.2 Books no projeto (em `books/summaries/`)

- `[advances_fin_ml]` López de Prado — gates PBO/DSR/CPCV
- `[leverage_for_the_long_run]` Gayed — synth LETF formula e limitations
- `[systematic_trading]` Carver — portfolio construction e Kelly
- `[adaptive_markets]` Lo — regime shift e drawdown psychology
- `[risk_parity]` — hedge via bonds
- `[fin_time_series_tsay]` — time series econometrics base

### 9.3 Dados

| Indicador | Fonte | URL |
|---|---|---|
| EBP | Fed | `federalreserve.gov/econres/notes/feds-notes/ebp_csv.csv` |
| Yield curve T10Y3M | FRED | `fred.stlouisfed.org` |
| CAPE | Multpl/Shiller | `multpl.com/shiller-pe` ou `shillerdata.com` |
| VIX | FRED | série `VIXCLS` |
| NY Fed recession prob | NY Fed | `newyorkfed.org/research/capital_markets/ycfaq` |
| Vintages | ALFRED | `alfred.stlouisfed.org` |

### 9.4 Bibliotecas

- `lppls` (PyPI) — LPPLS Confidence
- `arch` — GARCH para VIX synthesis se necessário
- `statsmodels` — probit para yield curve benchmark
- `pandas-datareader` — FRED ETL

---

## 10. Como usar este spec

**Quando abrir a próxima sessão**:

1. Leia `jornada/README.md` (estado geral).
2. Leia este spec inteiro.
3. Leia `studies/crashes_sp500_e_indicadores_preditivos.md` (literatura).
4. Leia `studies/ema_sma_threshold_educational/FINAL.md` (onde está o baseline).
5. Leia `studies/ema_sma_threshold_spy_real/FINAL.md` e `.../nasdaq_real/FINAL.md`
   (para entender o delta synth-vs-real).
6. Leia `studies/ema_sma_threshold_spy_real/analyses/04_worst_case_ema150_th5_3x.md`
   (entendendo o risco que queremos reduzir).

**Comando de abertura sugerido**:

> "Estou continuando o estudo `ema_sma_threshold`. Leia
> `studies/SPEC_crash_protection_evolution.md` como contexto, depois
> comece pela Fase 1 (stop-loss sweep isolado nos top-20 configs dos 3
> datasets). Quando Fase 1 estiver pronta, pare e me mostre os resultados
> antes de partir para Fase 2."

### Critério de sucesso da próxima sessão

**Deliverable mínimo aceitável**:
- Fase 1 + Fase 2 rodadas em SPYSIM synth 40y
- `FINAL.md` mostrando se algum combo stop+signal reduz MDD de 54% para
  ≤ 40% sem perder > 5pp CAGR
- Pelo menos 5/7 gates passando no best config crash-protected

**Deliverable ideal**:
- Fases 1-4 completas
- Real data validation em SPY e NDX
- Análise per-crash
- 50/50 portfolio revisitado com crash-protected config
- Recomendação explícita: este config é materialmente melhor que o
  baseline pra staging live?

---

## 11. Filosofia geral

- **Honest gates > nice numbers**. Se protection mechanism não passa os
  gates, não é winner.
- **Parcimônia de parâmetros**. Mandate Rule #2: max 4 parâmetros per
  strategy, cada extra cita justificativa.
- **Cross-dataset robustness**. Config precisa funcionar em synth 40y E
  real SPY E real NDX — não é suficiente funcionar em um só.
- **Small-sample skepticism**. 5-8 crashes em 90 anos. Qualquer fit fino
  a esses eventos = overfit.
- **Educacional, não production**. Mandate §1 segue, este estudo não
  automaticamente reativa Plano A/B/D.
- **Citação obrigatória** (Regra #2 do `CLAUDE.md`): toda decisão técnica
  cita um livro específico.
- **Jornada atualizada** (Regra #1): progresso relevante vai pra
  `jornada/YYYY-MM-DD-HHmm-slug.md` + update de `jornada/README.md`.

---

*Fim do spec. Próxima sessão usa isto como contexto completo.*

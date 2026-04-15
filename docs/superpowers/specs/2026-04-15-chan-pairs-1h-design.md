# Chan Bollinger Pairs em 1h — GLD-SLV (Primeira Estratégia Intraday Pós-Pivô)

**Data:** 2026-04-15
**Fase:** Phase 2.5 — catálogo intraday, entrada #1 pós-pivô
**Autor:** Claude Code (brainstorming guiado)
**Status:** design aprovado, aguardando plan de implementação
**Skill usada:** `superpowers:brainstorming`
**Dependências:** `tiingo_service` lazy-cache (✅ entregue 2026-04-15 noite, spec `2026-04-15-tiingo-service-lazy-cache-design.md`)

---

## 1. Contexto

### 1.1 Gatilho

Após `tiingo_service` destravar intraday 1h (IEX equity + crypto + forex com
split-adjust), o `ROADMAP §Next steps (post-pivot)` item 2 pede "catálogo de
estratégias intraday short-hold começando em 1h". A linha mestre desse catálogo
cita três famílias candidatas; Chan mean-reversion pairs é a primeira entrada,
escolhida porque:

1. **Holding natural casado com §1.4** — pairs trading canônico tem duração de
   algumas horas a poucos dias, alinhado com `median_hold_hours ≤ 48h` sem
   precisar mutilar sinal.
2. **Mais citável** — `[algo_trading_chan, ch.3, p.71-73]` é a referência
   canônica sem ambiguidade. Volatility breakouts Sinclair tem múltiplas
   formulações; Ehlers BP Swing em 1h seria re-calibração de estratégia já
   testada (valor informacional menor).
3. **Orthogonal às 5 anteriores** — nenhum dos 5 runs Phase 2.5 explorou
   cointegração. Novidade genuína no catálogo.

### 1.2 Escopo v1 — 1 pair canônico fixo

`GLD-SLV` como único pair. Fundamentação:

- **Link econômico sólido**: ambos ETFs spot-backed (`collateralized` por metal
  físico, sem contango) → sem o `roll return` pitfall que Chan
  `[p.118-119, ch.5]` admite ter custado $100k em 2006. O exemplo canônico do
  próprio Chan `[p.71-73, ch.3]` usa GLD-USO; USO é futures-backed e entra
  exatamente no pitfall que ele avisa. GLD-SLV é o análogo **mais fiel ao canon
  sem herdar o bug do exemplo**.
- **Liquidez verificada no universo Tiingo bulk** (MAPPING inclui GLD e SLV em
  `data/tiingo/`).
- **Retention Tiingo 1h IEX**: Smoke #1 validou SPY 5y em 1h; ETFs de
  commodities têm retention similar esperada (probe antes do implementar
  está no plan — §5 abaixo).

Descartados nesta iteração:
- **QQQ-SPY**: correlação ~0.95 absoluta (QQQ é subset de SPY); signal
  provavelmente fraco; gate rejeitaria por Sharpe baixo sem distinguir método
  de pair.
- **XLE-XOP**: atrativo mas menos citável (literatura pairs ETF setor é mais
  rarefeita que precious metals).
- **Basket multi-pair**: reduzir escopo preserva parsimônia; 5 runs daily
  falharam DSR em parte porque N_trials era alto; 1 pair × 4 configs = N=4
  é deliberadamente enxuto.
- **Cointegration-driven universe selector**: ROADMAP §3 avisa "Universe
  Selector é ele próprio uma estratégia — precisa passar o mesmo gate"; gera
  layer extra de overfit. Reserva pra v3+ se v1-v2 pass.

### 1.3 Hipótese de sucesso v1

Spec é executável em v1 se:
- `GLD` e `SLV` em `data/tiingo/1hour/` cobrirem ≥ 3 anos de história (Smoke
  #2 probe antes do impl — §5.1 do plan abaixo). Entre 3 e 5 anos é OK; < 3
  anos aborta CPCV N=6 por fold magro.
- OU regression no training split (~9 meses = 1250 bars) passa `t_stat(λ) <
  -2.0` (cointegração estatisticamente confirmável). Se não passa, pair é
  inválido **antes de qualquer backtest** — RuntimeError claro.
- `half_life_bars ∈ [4, 60]` no training. Fora desse range, pair não
  mean-reverte no timeframe 1h (clamp defensivo).

Assumindo hipótese OK, o trabalho está entregue quando:

- `ChanBollingerPairsStrategy(long_symbol="GLD", short_symbol="SLV",
  ...).on_bar(...)` emite ordens consistentes com a lógica canônica Chan
  `[p.71-73]`.
- 405 testes atuais permanecem verdes + ~20 novos testes cobrindo fit OU,
  entry/exit, session gates, §1.4 hard cap, spread stop, hedge ordering.
- `scripts/run_grid_chan_pairs.py` roda 4 configs em < 30s wallclock (n_jobs=4).
- Diagnostic report inclui `median_hold_hours`, `max_hold_hours`,
  `pct_trades_overnight`, `pct_time_stop_exits`, `pct_spread_stop_exits`,
  `beta_train`, `half_life_train`, `t_stat_OU` (requisito §1.4 do
  `tiingo_service` spec).
- Veredito de gate explícito (PASS/FAIL por CPCV+PBO+DSR+WF+MCPT) com
  racional citado na diagnóstico + hook pra v2 (§7 abaixo).

### 1.4 Compliance com §1.4 do `tiingo_service` spec

O spec pai `2026-04-15-tiingo-service-lazy-cache-design.md §1.4` estabelece:
- `median_hold_hours ≤ 48` é gate de catálogo.
- `median_hold > 72h` em 1h bars = descarte antes de DSR/PBO.
- Base econômica: `[systematic_trading, Carver, p.185-188, ch.12]` —
  annualized cost ≤ 0.13 SR/year.

Esta estratégia enforça isso via **três camadas**:
1. **Hard cap wall-clock** 48h no exit logic (§3 abaixo). Dispara
   independentemente de z-score.
2. **Friday weekend-flat** previne swap 3x do fim de semana.
3. **Time-stop em trading bars** = `min(3 × half_life, 24)`. Se half-life é
   ~15 bars, time-stop é 45 bars (~7 trading days), clampeado a 24 bars (1
   trading day). Empurra a duração típica pra 1-3 dias.

Alerta no diagnostic: se `pct_trades_exited_by_hard_cap > 20%`, **spec falhou
na sua premissa** — o sinal não é fundamentalmente curto no timeframe, violação
do pivô. Retorna ao brainstorm.

---

## 2. Arquitetura

### 2.1 Localização no repo

Novo módulo único:

```
src/ai_trade/backtest/strategies/chan_bollinger_pairs.py
```

Pattern: `@dataclass ChanBollingerPairsStrategy` implementando o `Strategy`
Protocol (`on_bar(bars, portfolio, context) → list[Order]`), seguindo o
template de `ehlers_bp_swing.py`. `StrategyBase` (ABC rebalance-day) não se
aplica — pairs dispara em qualquer bar.

Nenhum indicator novo em `backtest/indicators/` — Bollinger z-score é
`rolling().mean()/.std()` direto; OU regression é `numpy.polyfit`. Se v2
precisar Johansen/CADF multi-asset, aí vira módulo próprio
`backtest/indicators/cointegration.py`.

### 2.2 Assinatura pública

```python
@dataclass
class ChanBollingerPairsStrategy:
    data: dict[str, pd.DataFrame]    # keys: long_symbol, short_symbol
    long_symbol: str = "GLD"
    short_symbol: str = "SLV"

    # Grid knobs (2×2 = 4 configs)
    lookback_multiplier: int = 2      # {1, 2}
    entry_z: float = 1.0               # {1.0, 1.5}

    # Constants (não grid, cada um citado):
    exit_z: float = 0.0                # [p.71-72, ch.3]
    spread_stop_z: float = 3.0         # [p.293-294, ch.8]
    train_bars: int = 1250             # ~9 meses 1h; fit de β + OU
    half_life_clamp: tuple[int,int] = (4, 60)
    risk_pct_of_equity: float = 0.95   # precedente ehlers_bp_swing.py:108
    max_hold_hours: float = 48.0       # spec §1.4
    entry_hour_cutoff: int = 14        # ET local (deixa ≥ 2h antes close)
    friday_flat_hour: int = 15         # sex ≥ 15:00 ET força exit
    friday_no_entry_hour: int = 13     # sex ≥ 13:00 ET proíbe entrada

    # Computed em __post_init__ (read-only depois):
    _beta: float
    _half_life_bars: int
    _lookback_bars: int
    _time_stop_bars: int
    _t_stat_ou: float
    _indicators: pd.DataFrame          # cols: spread, spread_ma, spread_std, zscore
```

### 2.3 Protocolo de fit (único, em `__post_init__`)

1. **`adjust_ohlc`** em ambas as pernas (crítico, regression do bug commit
   `5ca9410`). Reusa `backtest/data/adjust.py`.
2. **Sync de timestamps**: `data[long].index == data[short].index`; se não,
   raise `ValueError` claro. Mean-reversion on bars não-alinhados é bug, não
   feature.
3. **Split**: `train_slice = data[:train_bars]`; `oos_slice = data[train_bars:]`.
   Todo fit vive no train; todo reporting vive no oos.
4. **Fit β**:
   - OLS 1: `price_long = α₁ + β₁ · price_short + ε₁` → extrai `β₁`, `t_stat_β₁`.
   - OLS 2 (Chan `[p.54, ch.2]` "tente os dois orderings"):
     `price_short = α₂ + β₂ · price_long + ε₂` → extrai `1/β₂`, `t_stat_β₂`.
   - Pick o ordering com `t_stat_β` mais negativa no teste OU subsequente
     (passo 5). Log ambos no diagnostic.
5. **Fit OU** sobre `spread_train = price_long - β · price_short`:
   - Regression `Δspread_train ~ λ · spread_train_lag` via `numpy.polyfit(deg=1)`.
   - `half_life_bars = round(-log(2) / λ)`.
   - Valida: `λ < 0` AND `t_stat(λ) < -2.0` AND `half_life_bars ∈ [4, 60]`.
     Qualquer violação → `RuntimeError` com mensagem autodiagnóstica.
6. **Derivados**:
   - `lookback_bars = lookback_multiplier × half_life_bars`
   - `time_stop_bars = min(3 × half_life_bars, 24)`
7. **Pré-computa indicadores sobre série inteira** (train + oos):
   - `spread[t] = price_long[t] - β · price_short[t]`
   - `spread_ma[t] = spread[t-lookback+1 : t+1].mean()`
   - `spread_std[t] = spread[t-lookback+1 : t+1].std()`
   - `zscore[t] = (spread[t] - spread_ma[t]) / spread_std[t]`

   Importante: rolling sobre série inteira é **OK** porque `on_bar` só consome
   bars do oos_slice (engine passa bar-a-bar). Train_slice não gera sinal,
   só serve pra estimar parâmetros.

---

## 3. Lógica de entrada e saída

### 3.1 Helpers por bar

```
current_z    = zscore[t]
prev_z       = zscore[t-1]
bars_held    = t - entry_idx                              (se em posição)
wall_clock_h = (bar.ts - entry_wall_clock_ts).seconds/3600 (se em posição)
hour_of_day  = bar.timestamp.hour                         (ET, instrument local)
weekday      = bar.timestamp.weekday()                    (Mon=0, Fri=4)
pos_long  = portfolio.positions.get(long_symbol)
pos_short = portfolio.positions.get(short_symbol)
in_position = (pos_long is not None AND pos_short is not None)
```

### 3.2 Entry logic (quando `not in_position`)

Ordem de checagem:

1. **Session gate**: se `hour_of_day > entry_hour_cutoff` (14) OR (`weekday ==
   4 AND hour_of_day >= friday_no_entry_hour` (13)) → skip. Racional: deixa ≥
   2h de trading bars pra posição respirar antes do close; sex a tarde evita
   abrir trade que cairia no swap 3x do fim-de-semana.
2. **Long spread entry**: `prev_z > -entry_z AND current_z <= -entry_z` →
   emite:
   - `Order(long_symbol, side="buy",  volume=long_leg_shares)`
   - `Order(short_symbol, side="sell", volume=short_leg_shares)`

   onde o sizing é:
   ```
   total_notional  = equity × risk_pct_of_equity
   long_leg_shares  = total_notional / (price_long + β × price_short)
   short_leg_shares = β × long_leg_shares
   ```

   Grava em `context[f"chan_pairs_state_{long}_{short}"]`:
   ```python
   {"entry_idx": t, "entry_z": current_z, "entry_wall_clock_ts": bar.ts,
    "side": "long_spread", "beta_at_entry": self._beta}
   ```
3. **Short spread entry**: `prev_z < +entry_z AND current_z >= +entry_z` →
   simétrico (sell long, buy short).

Cita: `[algo_trading_chan, p.71-72, ch.3]` — regra canônica de crossing.

### 3.3 Exit logic (quando `in_position`), ordem de precedência

Primeira que dispara vence.

1. **Spread blow-out stop** `[p.293-294, ch.8]`: se posição é long spread AND
   `current_z <= -spread_stop_z`, OU short spread AND `current_z >=
   spread_stop_z` → fecha ambas as pernas. **Proteção de capital contra
   regime shift**; não dispara em reversão saudável.
2. **Friday weekend-flat**: se `weekday == 4 AND hour_of_day >=
   friday_flat_hour` (15) → fecha ambas. Evita swap 3x do fim-de-semana CFD.
3. **Wall-clock hard cap §1.4**: se `wall_clock_h >= max_hold_hours` (48) →
   fecha ambas. Gate literal do spec `tiingo_service §1.4`.
4. **Time-stop trading bars** `[p.47, ch.2]`: se `bars_held >= time_stop_bars`
   → fecha ambas. Protege contra half-life mal estimado.
5. **Mean-reversion exit** `[p.71-72, ch.3]`: se long spread AND `current_z
   >= exit_z` (0), OU short spread AND `current_z <= -exit_z` (0) → fecha
   ambas. **Exit esperado do Chan canon — a maioria dos trades sai aqui**.

Qualquer exit emite **dois orders síncronos no mesmo bar** (fecha long leg,
fecha short leg); engine `Portfolio` aplica ambos simultaneamente.

State cleanup: `context[f"chan_pairs_state_{long}_{short}"].clear()` logo
após exit.

**Adaptações não-Chan documentadas**: regras 2-3 (session gate Friday-flat +
wall-clock) são enxertos Pepperstone-CFD; não estão em `algo_trading_chan`.
Docstring do módulo marca: `[spec_adaptation: spec_tiingo_service §1.4 +
systematic_trading Carver p.185-188 ch.12]`.

Precedência (stop → session → hard cap → time-stop → mean-revert) é minha
proposta. Racional: capital preservation > compliance §1.4 > parsimônia de
tempo > signal natural.

---

## 4. Pipeline de dados

### 4.1 Fonte

`TiingoSource(frequency="1hour")` — infra pai, ✅ entregue 2026-04-15 noite.
Args do fetch:

```python
df_gld = tiingo_source.fetch("GLD", start=..., end=..., frequency="1hour")
df_slv = tiingo_source.fetch("SLV", start=..., end=..., frequency="1hour")
```

Split/dividend adjust já aplicado internamente pelo `TiingoSource` (via daily
cache, lógica do `adjust.py`). Não precisa re-aplicar.

### 4.2 Janela

- Smoke #2 probe (§5.1 do plan) mede retention real GLD/SLV 1h.
- Estimativa esperada: ~5y (análogo ao SPY Smoke).
- Janela alvo: `start=2021-04-15, end=2026-04-15` = ~5 anos = ~8190 bars por
  ticker.
- Se retention < 3 anos: spec ainda executável mas CPCV N=6 fica apertado
  (≥ 1000 bars por fold) → escalar decisão ao usuário.

### 4.3 Partição pra fit vs. avaliação

- `train_bars = 1250` (~9 meses de 1h bars, conservadoramente < 15% do
  total). Único uso: estimar `β`, `half_life`, `t_stat_OU`. Nunca entra em
  stats OOS.
- `oos_slice` = resto (~6900 bars = ~3.4 anos efetivos).
- CPCV, WF, PBO, DSR, MCPT operam **exclusivamente sobre oos_slice**.

### 4.4 Walk-forward: fit refeito a cada janela

Diferente do training/oos fixo do grid, o walk-forward honesto **re-fita `β` e
`half_life` no início de cada janela WF**. Garante que não há congelamento de
parâmetros que só fazia sentido em 2021. 8 janelas × ~6 meses cada → 8 fits
separados → 8 performances OOS independentes. Isso é o que Chan `[p.8, ch.1]`
chama de "true out-of-sample".

### 4.5 Embargo CPCV

`embargo = max(lookback_bars, 3 × half_life_bars)` bars em cada fronteira de
fold. Previne leakage via rolling window. Referência: `[advances_fin_ml, ch.7]`
purge+embargo.

---

## 5. Gate de anti-overfit

Mesma bateria dos 5 runs Phase 2.5 anteriores, aplicada só sobre `oos_slice`:

### 5.1 Grid

2×2 = **4 configs**:

| config | lookback_multiplier | entry_z |
|---|---|---|
| #1 | 1 | 1.0 |
| #2 | 1 | 1.5 |
| #3 | 2 | 1.0 |
| #4 | 2 | 1.5 |

N_trials = 4. Deliberadamente enxuto pro DSR respirar (Runs anteriores: N=24
Ehlers, N=30 Clenow).

### 5.2 Battery

| Gate | Ref | Config | Pass criterion |
|---|---|---|---|
| **CPCV** | `[advances_fin_ml, ch.7]` | 6 folds, embargo conforme §4.5 | Gera distribuição de Sharpes |
| **PBO** | `[advances_fin_ml, p.208-211]` | Sobre Sharpes do CPCV | `< 0.5` |
| **DSR** | `[advances_fin_ml]` | `N_trials=4` | `p < 0.05` |
| **Walk-forward** | `[kaufman]`, ROADMAP §3.5 | 8 janelas × ~6 meses, fit refeito por janela | ≥ 6 profitable, DD ≤ 25% em cada |
| **MCPT** | `[masters_permutation_tests]` | 500 shuffles dos returns de `short_symbol` (mantém long intacto) | `p < 0.05` |

### 5.3 Veredito final

**PASS** iff: `PBO < 0.5` AND `DSR p < 0.05` AND `WF ≥ 6/8` AND `MCPT p < 0.05`.

Qualquer falha = FAIL. Diagnóstico precisa explicitar:
- Qual gate falhou, com magnitude.
- Hipótese econômica da causa (pair não cointegrado? regime-sensitive?
  half-life instável entre janelas WF?).
- Recomendação de próximo passo (§7).

---

## 6. Cobertura de testes

Arquivo: `tests/test_chan_bollinger_pairs.py`. Baseline 405 → target 425+.

| # | Teste | Cobre |
|---|---|---|
| 1 | fit_beta_synthetic | OLS recupera β=2.5 em `y = 2.5x + noise` |
| 2 | fit_half_life_ou | OU synth com λ conhecido → half_life ± 1 bar |
| 3 | ou_rejects_random_walk | Série RW → RuntimeError (t_stat não-significativo) |
| 4 | half_life_clamp_out_of_range | HL sintético = 100 → RuntimeError (fora [4,60]) |
| 5 | entry_long_spread_on_crossing | z cruza −1.0 → 2 orders (buy long, sell short) com razão β |
| 6 | entry_short_spread_on_crossing | Simétrico |
| 7 | entry_ignored_after_cutoff | Bar 15:00 com z=−1.5 → sem ordem |
| 8 | entry_ignored_friday_afternoon | Bar sex 13:30 com z=−1.5 → sem ordem |
| 9 | friday_weekend_flat_exit | Pos aberta, bar sex 15:00 → 2 exit orders |
| 10 | wall_clock_48h_cap | Entry seg 10:00, bar qua 10:00 → 2 exit orders (mesmo com z favorável) |
| 11 | mean_revert_exit_long | Long spread, z cruza 0 → 2 exit orders |
| 12 | mean_revert_exit_short | Simétrico |
| 13 | spread_stop_long | Long spread, z <= −3 → 2 exit orders |
| 14 | spread_stop_short | Simétrico |
| 15 | time_stop_in_trading_bars | bars_held == time_stop_bars → 2 exit orders |
| 16 | hedge_ratio_ordering_picks_best | Testa ambos OLS orderings, escolhe t_stat mais neg |
| 17 | adjust_ohlc_applied | Regression bug `5ca9410` — ambos símbolos ajustados |
| 18 | diagnostic_fields_present | Run completo emite todos os campos obrigatórios |
| 19 | misaligned_timestamps_raises | data[long].index != data[short].index → ValueError |
| 20 | insufficient_equity_emits_no_orders | equity ≤ 0 → lista vazia |

### 6.1 Runner CLI

`scripts/run_grid_chan_pairs.py` seguindo exatamente o padrão de
`scripts/run_grid_ehlers_meta.py` + `run_grid_ehlers.py`. Reusa
`backtest/grid/GridRunner[ConfigT]` genérico (já está generalizado desde Run
2 via TypeVar). Novo arquivo `src/ai_trade/backtest/grid/chan_pairs_config.py`
com dataclass `ChanPairsConfig`.

Target wallclock: < 30s em n_jobs=4 pra 4 configs sobre 5y de GLD+SLV 1h
(precedente: Run 2 Ehlers 24 configs em ~3s; Chan pairs tem mesma
complexidade por-config, 6× menos configs → muito dentro do budget).

### 6.2 Report + diagnostic

Usa `backtest/metrics/report.py` existente + extensão do `diagnostic.md` com
seção "Pair Fit Diagnostics":

```markdown
## Pair Fit Diagnostics (train split)

- long_symbol: GLD
- short_symbol: SLV
- train_bars: 1250 (~9 months)
- beta (GLD ~ SLV): 2.58 (t-stat: -3.41)
- beta (SLV ~ GLD, inverted): 2.46 (t-stat: -2.89)
- winner: GLD ~ SLV ordering
- half_life_bars: 17
- t_stat_OU: -2.94  ✅ significant
- lookback_bars used (multiplier=2): 34
- time_stop_bars: 24 (capped from 3×17=51)

## Hold Time Distribution (OOS)

- median_hold_hours: 12.3
- max_hold_hours: 48.0 (hit hard cap 8 times, 4.2%)
- pct_trades_overnight: 67%
- pct_exited_by: {spread_stop: 3%, friday_flat: 11%, hard_cap: 4%,
                  time_stop: 18%, mean_revert: 64%}
```

---

## 7. Critérios de sucesso e hook downstream

### 7.1 PASS v1

Se todos os 4 gates passam:

- Promove `ChanBollingerPairsStrategy` como primeira entrada validada do
  catálogo intraday.
- **Próximo passo (v2)**: testa `rolling β` (opção b da discussão de hedge
  ratio) como 1 trial adicional. Se melhora significativamente no DSR
  re-rodado com N=5: promove. Se não: congela v1 inalterada.
- Entrada em JORNADA.md: "Primeira estratégia intraday shippada pós-pivô,
  Sharpe X, CAGR Y, median_hold Zh".

### 7.2 FAIL v1 por DSR (p ∈ [0.05, 0.10])

Sinal real mas amostra estatisticamente curta.
- Amplia universo pra batch de 3 pares (GLD-SLV + XLE-XOP + SPY-IWM), cada
  um rodado independente.
- Combina p-values via Fisher's method `[masters_permutation_tests]`.
- Se p-combinado < 0.05: pair family tem edge, mas pair individual não
  atinge significância.

### 7.3 FAIL v1 por PBO > 0.5

Uniformidade do paradigma (análogo ao F3.D Portfolio Run 4 Step 2).
- Diagnóstico: provavelmente pares ETFs macro-driven demandam regime filter
  overlay.
- Próximo passo: Chen `regime_change` pre-filter antes de activar a
  estratégia.

### 7.4 FAIL v1 por WF < 6/8

Regime sensitivity.
- Diagnóstico: cointegração tem half-life não-estacionário; rolling β pode
  ajudar (promove v2 mesmo sem v1 passar).
- Segundo tentativa: adiciona regime filter como em §7.3.

### 7.5 FAIL v1 por MCPT

Não há cointegração genuína em 1h.
- Chan `[p.88-89, ch.4]` estava certo pra ETFs também (e não só stocks).
- Pivotamos pro segundo item do catálogo intraday: volatility breakouts
  Sinclair `[volatility_trading]`.

### 7.6 FAIL catastrófico — hard_cap > 20% dos trades

Sinal fundamentalmente não é short-hold em 1h. Viola o pivô.
- Retorna ao brainstorm. Provavelmente timeframe errado (5m? 15m?) ou pair
  errado.

---

## 8. Fora do escopo (YAGNI explícito)

- **Rolling β ou Kalman filter dinâmico**: diferido pra v2. Chan admite
  Kalman params tuned in-sample; não vale adicionar complexidade sem v1
  passar primeiro.
- **Cointegration-driven universe selector**: só se v1-v2 pass + houver
  interesse em multi-pair.
- **Johansen test multi-asset**: só se formos pra 3+ instrumentos num
  portfolio cointegrado. Para 1 pair, CADF via OLS + OU regression é
  suficiente.
- **Adaptive z thresholds** (Chan `[p.77, ch.3]` variação): over-engineering
  pro v1.
- **Portfolio de pairs (wrapper sobre múltiplas instâncias)**: usa a infra
  `src/ai_trade/backtest/portfolio/` que já é timeframe-agnostic (Run F3.D
  legacy); acende quando tivermos 2+ estratégias intraday validadas.
- **Transaction costs / spreads / swap** no backtest: deferred por
  consistência com runs anteriores (Phase 3 re-aplica custos via calibration
  pre-Phase 4). Diagnostic só reporta `pct_trades_overnight` como proxy do
  swap que será aplicado depois.

---

## 9. Dependências e pré-requisitos

- ✅ `tiingo_service` lazy-cache 1h (spec pai, entregue 2026-04-15 noite).
- ✅ `backtest/engine/` (Portfolio + Runner + Execution, 405 testes verdes).
- ✅ `backtest/validation/` (CPCV + PBO + DSR + WF + MCPT, Phase 2 delivered).
- ✅ `backtest/data/adjust.py` (bug `5ca9410` fix).
- ✅ `backtest/grid/GridRunner[ConfigT]` genérico (Run 2 Ehlers generalization).
- ✅ `backtest/metrics/report.py` (diagnostic markdown).

Nada a construir como pré-requisito. Spec é drop-in sobre a infra existente.

---

## 10. Citações consolidadas

Toda decisão do spec cita explicitamente:

- **Pair canônico Bollinger z-score**: `[algo_trading_chan, p.71-73, ch.3]`
- **Lookback = múltiplo de half-life**: `[algo_trading_chan, p.47, ch.2]`
- **OU regression half-life**: `[algo_trading_chan, p.47-48, ch.2]`
- **Ambos orderings OLS**: `[algo_trading_chan, p.54, ch.2]`
- **Stop-loss em mean-reversion não disparado em backtest**:
  `[algo_trading_chan, p.293-294, ch.8]`
- **Evitar roll-return pitfall (motivo pra SLV, não USO)**:
  `[algo_trading_chan, p.118-119, ch.5]`
- **Warning contra stock pairs**: `[algo_trading_chan, p.88-89, ch.4]`
- **True OOS via walk-forward**: `[algo_trading_chan, p.3, p.8, ch.1]`
- **Cost gate 0.13 SR/year (§1.4 hard cap)**: `[systematic_trading, Carver,
  p.185-188, ch.12]`
- **CPCV + purge/embargo**: `[advances_fin_ml, ch.7]`
- **PBO threshold**: `[advances_fin_ml, p.208-211]`
- **DSR**: `[advances_fin_ml]`
- **MCPT**: `[masters_permutation_tests]`
- **WF 8+ windows**: `[kaufman]`, ROADMAP §3.5

Adaptações documentadas como **não-Chan**:
- Session gate (entry cutoff 14:00, friday_no_entry 13:00, friday_flat 15:00)
  — enxertos Pepperstone-CFD derivados de §1.4 + Carver ch.12.
- Wall-clock hard cap 48h — gate literal do spec pai.
- Ordem de precedência dos exits — proposta interna.

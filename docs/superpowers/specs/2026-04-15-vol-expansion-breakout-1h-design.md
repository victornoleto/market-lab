# Volatility Expansion Breakout em 1h — SPY + XAU/USD + EUR/USD (Segunda Estratégia Intraday Pós-Pivô)

**Data:** 2026-04-15
**Fase:** Phase 2.5 — catálogo intraday, entrada #2 pós-pivô
**Autor:** Claude Code (brainstorming guiado, skill `superpowers:brainstorming`)
**Status:** design aprovado, aguardando plan de implementação
**Dependências:** `tiingo_service` lazy-cache (✅ entregue 2026-04-15 noite, spec `2026-04-15-tiingo-service-lazy-cache-design.md`), `DiagnosticAnalyzer` GATE_UPSTREAM_FAIL (✅ commit `8f51a0a`)
**Antecede:** Chan Bollinger Pairs 1h (entrada #1 do catálogo, FAIL CADF, spec `2026-04-15-chan-pairs-1h-design.md`)

---

## 1. Contexto

### 1.1 Gatilho

Per `ROADMAP §Next steps (post-pivot)` item 2 e `JORNADA §Onde estamos hoje`, o catálogo intraday 1h pivota pra Sinclair `[volatility_trading]` após Chan Bollinger Pairs GLD-SLV falhar CADF (`t_stat_OU = -2.956 > -3.4`, `reports/grid_chan_pairs_20260415-2109/diagnostic.md`). Esta é a entrada #2 do catálogo.

**Discrepância de framing resolvida durante brainstorm:** o rótulo "volatility breakouts Sinclair" é parcialmente impróprio — `volatility_trading.md` (298p) trata exclusivamente de **opções e implied-vs-realized vol** (selling straddles `[p.217]`, VIX basis `[p.226]`, VXX/VXZ IVTS `[p.228-229]`, dispersion `[p.219]`, delta-hedge `[p.102]`). Sinclair não escreve sobre price-breakouts em ativos spot. Nossa infra (Tiingo IEX 1h equity + Tiingo FX 1h) não suporta options chains nem VIX intraday. Portanto, esta estratégia é um **híbrido honesto**:

- **Mecânica do breakout** vem de Kaufman `[trading_systems_methods, p.353]` (Donchian 20/40 = base do método Turtles, citado como "basis of the Turtle method" pelo próprio Kaufman).
- **Filtro de regime** vem de Sinclair `[volatility_trading, p.20-23, p.58-60]` (Yang-Zhang em volatility cone).
- **Sizing** vem de Carver `[systematic_trading, p.144, p.159, ch.9-10]` (volatility-targeting via Half-Kelly).
- Sinclair fica em papel honesto: **provedor do estimador de vol e do filtro de regime**, não de lógica de entrada.

### 1.2 Escopo v1 — 3 ativos × 4 configs (Bundle β)

**Universo:**
- `SPY` (Tiingo IEX 1h, sessão US equity 9:30-16:00 ET, ~7 bars/dia)
- `XAU/USD` (Tiingo FX 1h, sessão 24h Dom-Sex, ~120 bars/semana) — spot gold
- `EUR/USD` (Tiingo FX 1h, sessão 24h Dom-Sex)

**Justificativa do Bundle β:**
1. **Multi-asset class diversifica teste de robustez** — equity-beta (SPY) + commodity/inflation-hedge (XAU) + G7 rate differential (EUR/USD). 3 drivers econômicos distintos. Edge que pega nos 3 é evidência forte do mecanismo, não tailoring.
2. **Spot gold > GLD pra breakouts** — GLD tem overnight gaps artificiais por London fix; XAU/USD tem range contínuo. Yang-Zhang `[p.22, Eq.2.17a]` foi derivado pra "lidar com opening jumps" — XAU se beneficia diretamente.
3. **EUR/USD é a FX mais citável** e menos regime-dependente; torna PROCEED/BLOCK do diagnostic mais defensável.
4. **Sessions semi-coerentes** — 1 equity + 2 FX. Dois bar-handlers ao invés de 3.

**Fallback Bundle α:** se Tiingo FX 1h retention < 3y para `XAU/USD` ou `EURUSD` (Smoke #2 do plan), substitui por `GLD` (mesma sessão IEX que SPY) e mantém EUR/USD. Documentado no plan §5.1.

**Descartados nesta iteração:**
- **Sector SPDR basket (XLE/XLF/XLK...)** — alta correlação intra-equity (todos equity-beta dependent), reproduz o problema de uniformidade que matou F3.D v1 (PBO 0.849).
- **AUD/USD como FX** — commodity-FX, correlacionado com gold, rompe ortogonalidade econômica.
- **USD/JPY** — BoJ interventions são outliers que distorcem o filtro YZ-cone (`[p.52]` adverte sobre handling de outliers).
- **GBP/USD** — Brexit-era é regime mudado pós-2020; sample limpo é mais curto.
- **Pyramiding** — Turtles permite até 4 unidades `[trading_systems_methods, p.353]`; v1 fica em 1 unidade pra parsimônia.

### 1.3 Hipótese de sucesso v1

Spec é executável em v1 se:

1. **Retention Tiingo FX 1h** confirmada via Smoke #2 (probe no plan §5.1):
   - `XAU/USD` ≥ 3y de bars (necessário pra CPCV N=6 viável)
   - `EURUSD` ≥ 3y de bars
   - Se qualquer um < 3y → fallback automático Bundle α (XAU→GLD), log warning, prossegue
2. **Cone warmup** ≥ 1y (≈1700 FX bars / ≈1690 SPY bars) por símbolo antes do filtro retornar `True`. Período de warmup gera zero trades (não erro).
3. **Sample size pós-backtest** ≥ 30 trades por símbolo. Se algum símbolo tem `n_trades < 30` ⇒ DSR insignificante por baixa amostragem; **única retentativa documentada com K=50th** (decisão pré-registrada, não grid disfarçado).

Assumindo hipótese OK, o trabalho está entregue quando:

- `VolExpansionBreakoutStrategy(...).on_bar(...)` emite ordens consistentes com a lógica Donchian + filtro YZ-cone descrita em §3.
- 432 testes atuais permanecem verdes (baseline pós-Chan pair) + ~27 novos testes cobrindo cada componente isolado (RegimeFilter, BreakoutSignal, VolTargetSizer, ExitManager) + integração.
- `scripts/run_grid_vol_expansion.py` roda 12 trials (4 configs × 3 ativos) em < 60s wallclock (n_jobs=4). Sem GARCH/MLE — operação trivial.
- Diagnostic report inclui métricas obrigatórias (§5.2): `median_hold_hours`, `max_hold_hours`, `pct_trades_overnight`, `pct_time_stop_exits`, `pct_disaster_stop_exits`, `n_trades_per_symbol`, `pct_filter_active`, `yz_pct_at_entry_avg`, `breakout_strength_avg`.
- Veredito de gate explícito (PASS/FAIL por CPCV+PBO+DSR+WF+MCPT) com racional citado na diagnóstico + hooks documentados pra v2 (§7).

### 1.4 Compliance com §1.4 do `tiingo_service` spec

O spec pai `2026-04-15-tiingo-service-lazy-cache-design.md §1.4` estabelece:
- `median_hold_hours ≤ 48` é gate de catálogo.
- `median_hold > 72h` em 1h bars = descarte antes de DSR/PBO.
- Base econômica: `[systematic_trading, Carver, p.185-188, ch.12]` — annualized cost ≤ 0.13 SR/year.

Esta estratégia enforça via **três camadas de exit (§3.3)**:
1. **Donchian opposite-channel** (N_exit ∈ {10, 20}) — saída esperada típica em horas a poucos dias.
2. **Hard cap wall-clock 48h** — dispara independente de preço/canal.
3. **Disaster stop 4σ** — Carver `[systematic_trading, p.212, ch.13]`; protege contra gap notícia em fake breakout.

**Friday weekend-flat não está em v1** para nenhum dos 3 ativos. FX 24h fecha sozinho Sex 17 ET (sem exposure weekend material). SPY: trade aberto Sex tarde com 48h hard cap fecha Dom à noite (mercado closed) → ordem executa Seg open com slippage de gap. O hard cap §1.4 cobre o weekend exposure sem precisar de Friday flat dedicado. Hook v2 #7 avalia se `pct_trades_overnight_SPY` no diagnostic justifica adicionar Friday flat dedicado.

Alerta no diagnostic: se `pct_trades_exited_by_hard_cap > 20%` em qualquer símbolo, **spec falhou na sua premissa intraday-short-hold** — sinal não é fundamentalmente curto no timeframe, violação do pivô. Retorna ao brainstorm. Idêntico ao gate Chan pair `[chan-pairs-1h-design §1.4]`.

---

## 2. Arquitetura

### 2.1 Localização no repo

Novo módulo único:

```
src/ai_trade/backtest/strategies/
├── base.py                       (já existe)
├── chan_bollinger_pairs.py       (já existe, entrada #1 catálogo)
├── ehlers_bp_swing.py            (já existe, template estilístico)
└── vol_expansion_breakout.py     (NOVO — esta estratégia)

src/ai_trade/backtest/strategies/vol_expansion_breakout/  (sub-módulos)
├── __init__.py
├── regime_filter.py              (Yang-Zhang + cone)
├── breakout_signal.py            (Donchian channel)
├── vol_target_sizer.py           (Carver volatility scalar)
└── exit_manager.py               (3 condições primeiro-disparo)

scripts/
└── run_grid_vol_expansion.py     (NOVO — análogo a run_grid_chan_pairs.py)

tests/backtest/strategies/
├── test_vol_expansion_regime_filter.py
├── test_vol_expansion_breakout_signal.py
├── test_vol_expansion_sizer.py
├── test_vol_expansion_exit_manager.py
└── test_vol_expansion_strategy_integration.py
```

Cada componente é classe própria, testável em isolamento. `VolExpansionBreakoutStrategy` é orchestrator — chama os 4 componentes em `on_bar`.

### 2.2 Componentes (4 classes desacopladas)

```
┌──────────────────────────────────────────────────────────┐
│ VolExpansionBreakoutStrategy(StrategyBase)               │
│                                                          │
│   def on_bar(symbol, bar_t):                             │
│       buffer[symbol].append(bar_t)                       │
│                                                          │
│       if not has_position(symbol):                       │
│           if RegimeFilter.is_quiet(buffer[symbol]):      │
│               direction = BreakoutSignal.fire(           │
│                   buffer[symbol], N_entry                │
│               )                                          │
│               if direction:                              │
│                   units = VolTargetSizer.units(          │
│                       symbol, σ_yz, equity, target_vol   │
│                   )                                      │
│                   emit Order(symbol, direction, units)   │
│       else:                                              │
│           reason = ExitManager.should_exit(              │
│               buffer[symbol], position[symbol], bar_t    │
│           )                                              │
│           if reason:                                     │
│               emit Order.close(symbol, reason)           │
└──────────────────────────────────────────────────────────┘
```

### 2.3 Estado interno por símbolo

```python
@dataclass
class SymbolState:
    ohlc_buffer: collections.deque[OHLCBar]   # rolling, maxlen = max(N_entry, cone_lookback) + buffer
    yz_history: collections.deque[float]      # rolling YZ values pra cone, maxlen = cone_lookback
    cone_percentiles_cache: tuple[float,...]  # invalidated quando yz_history muda
    open_position: Position | None
    entry_bar_index: int                       # pra time-stop wall-clock
```

**Cone percentile recompute**: incremental (insert + sort numpy), amortizado O(log N) por bar; rebuild full a cada N=100 bars pra prevenir drift. Decisão de implementação não-estratégica.

---

## 3. Lógica de entrada/saída

### 3.1 RegimeFilter (Yang-Zhang em cone)

**Yang-Zhang volatility estimator** `[volatility_trading, p.22-23, Eq. 2.17a]`:

$$\sigma_{YZ} = \sqrt{\sigma_o^2 + k\sigma_c^2 + (1-k)\sigma_{rs}^2}$$

onde:
- $\sigma_o^2$ = overnight close-to-open variance
- $\sigma_c^2$ = close-to-close variance
- $\sigma_{rs}^2$ = Rogers-Satchell-Yoon variance `[p.22, Eq. 2.16]` (lida com drift)
- $k = 0.34 / (1.34 + (N+1)/(N-1))$ `[p.23]`
- N = 20 bars (janela rolling)

**Por que Yang-Zhang**: Sinclair `[p.22]` justifica explicitamente — "weighted average of the Rogers, Satchell, and Yoon estimator, the close-to-open volatility and the open-to-close volatility... allows for opening jumps". Cobre os 3 ativos: SPY tem opening gaps overnight (US→US), XAU/USD tem weekly close→open (Sex 17 → Dom 17), EUR/USD idem.

**Cone**: histórico das últimas `cone_lookback = 1700` bars de `σ_YZ(20)` rolling. Computa percentil de `σ_YZ_atual` neste histórico. Sinclair `[p.58-60]` descreve a primitiva exata.

**Filtro**: `is_quiet(symbol) = (percentil ≤ K_filter)` onde **`K_filter = 33`** (fixo, não gridado).

**Output API do RegimeFilter** (consumido por sizer §3.3 e disaster stop §3.4):
```python
@dataclass
class RegimeReading:
    is_quiet: bool                 # percentil ≤ K_filter
    sigma_yz_annual: float         # raw × sqrt(bars_per_year), pronto pra consumo
    sigma_yz_percentile: float     # 0-100, pra diagnostic e debug
    bars_in_history: int           # pra warmup detection
```

`bars_per_year` é configurado por símbolo na construção (1638 SPY/GLD, 6240 FX). A anualização acontece **uma única vez no filtro**; ninguém downstream re-escaleia.

**Por que K=33 fixo, não tunável**:
- Sinclair não fornece número canônico pro lado baixo do cone (só 90th pra venda de vol, `p.60`).
- Gridar K transforma filtro de **classificador binário de regime** em **target de otimização** → curve-fit. Sinclair `[p.218]` adverte explicitamente sobre curve-fit em filtros baseados em vol smoothing.
- "Bottom third" tem justificativa econômica a priori: divide histórico em terços (low/mid/high vol regime); filtro ativo ~33% do tempo ⇒ sample meaningful sem ser permissivo.
- Mantém grid em 12 trials totais (não infla pra 24+) → DSR threshold tratável.

**Warmup**: durante as primeiras 1700 bars por símbolo, `is_quiet` retorna `False` (não trade). Sem erro; só observabilidade no diagnostic (`bars_in_warmup`).

### 3.2 BreakoutSignal (Donchian channel)

Per Kaufman `[trading_systems_methods, p.353, RULE]`: "Buy when high > max high 40 days; exit long when low < min low 20 days" (Donchian 20/40, base do método Turtles).

**Adaptação 1h**: parâmetros gridados em `N_entry ∈ {20, 55}` bars (ver §3.5 grid).

**Lógica de fire**:
```python
def fire(buffer, N_entry) -> Direction | None:
    last_close = buffer[-1].close
    high_window = max(b.high for b in buffer[-N_entry-1:-1])  # exclui bar atual
    low_window  = min(b.low  for b in buffer[-N_entry-1:-1])
    if last_close > high_window:
        return Direction.LONG
    if last_close < low_window:
        return Direction.SHORT
    return None
```

**Bidirecional simétrico** em todos os 3 ativos. Justificativa: hipótese é direction-agnostic ("low vol → próximo movimento carrega informação"). FX (XAU, EUR) sem drift estrutural; SPY captura edge real em rompimentos de baixa em regimes de stress (2008, 2020). Turtles canon `[trading_systems_methods, p.353]` é bidirecional.

**Gate combinado**: trade só dispara se `RegimeFilter.is_quiet ∧ BreakoutSignal.fire ≠ None`. As duas condições são **independentes** (filtro = vol-based, signal = price-based) → não há double-counting.

### 3.3 VolTargetSizer (Carver volatility-targeting)

Per Carver `[systematic_trading, p.144, p.159, ch.9-10]`:

$$\text{position\_size} = \frac{\text{target\_vol\_annual} \times \text{equity}}{\sigma_{YZ}^{\text{annual}}}$$

**Convenção de unidades (única, válida em todo o spec)**: σ_YZ é sempre **fração anualizada**. Sinclair `[p.14]` define o estimador raw como per-bar variance — convertemos pra anualizado via `σ_YZ_annual = σ_YZ_raw × √bars_per_year` no momento da emissão. Todo uso downstream (sizer §3.3, disaster stop §3.4, métricas diagnostic §5.3) consome σ_YZ já anualizado.

Onde:
- `target_vol_annual = 0.10` (10%, fixo, não gridado)
- `σ_YZ_annual` = output canônico do RegimeFilter (re-uso) — magnitude anualizada, não percentil
- `bars_per_year` (usado pra anualizar σ raw e na conversão price-points em §3.4):
  - SPY: 6.5h × 252d = 1638 bars
  - GLD (fallback): idem 1638
  - XAU/USD, EUR/USD: 24h × 5d × 52w = 6240 bars (FX trading week)

**Por que vol-targeting > Kelly contínuo de Sinclair `[volatility_trading, p.138, Eq. 8.14]`**:

Sinclair: `f = r/σ²`. Requer estimar `r` (expected return) por ativo → 3 estimativas frágeis → contribui pra overfit. O próprio Sinclair `[p.139]` admite: *"There is no compelling theoretical reason for sizing trades according to the fractional Kelly idea. Fractional Kelly doesn't correspond to maximizing any utility function."* Ele dilui pra fractional por razões práticas (drawdown control), não teóricas.

Carver vol-targeting é Kelly degenerado quando `r ∝ σ` (vol risk premium); matematicamente parente, praticamente robusto pra multi-asset. **Citação principal limpa** = Carver; Sinclair entra como provedor do `σ_YZ`.

**Por que 10% (não 25% Carver max)**:
- Carver `[p.146, ch.9]`: vol-target ≤ SR_realistic / 2 (Half-Kelly). Para semi-auto staunch: SR ≤ 0.5 ⇒ vol-target ≤ 25%.
- Escolho 10% (≡ SR_realistic ≈ 0.2) porque (i) v1 prova edge antes de leverage; (ii) 3 ativos somam vol agregado mesmo com correlação baixa; (iii) Carver `[p.143]` exemplo CHF 2015 mostra que 50% vol-target em FX requer 50× leverage — catastrófico em jumps. 10% deixa headroom.

**Sem pyramiding**: 1 unidade por sinal. Turtles permite até 4 `[trading_systems_methods, p.353]` — hook v2 (§7).

**σ floor (zero-vol guard)**: se `σ_YZ < 1e-6`, sizer retorna 0 e loga warning. Previne division-by-zero em períodos degenerate (gap, halt).

### 3.4 ExitManager (3 condições, primeiro-disparo)

Em cada bar com posição aberta, testa as 3 em ordem; primeira que dispara fecha:

**1. Donchian opposite channel** `[trading_systems_methods, p.353]`

```python
def opposite_channel_exit(position, buffer, N_exit) -> bool:
    if position.direction == LONG:
        return buffer[-1].close < min(b.low for b in buffer[-N_exit-1:-1])
    else:  # SHORT
        return buffer[-1].close > max(b.high for b in buffer[-N_exit-1:-1])
```

Saída esperada típica em horas-a-dias.

**2. Hard cap wall-clock 48h** (compliance §1.4)

```python
def time_stop_exit(position, bar_t) -> bool:
    return (bar_t.timestamp - position.entry_timestamp) >= timedelta(hours=48)
```

Independente de preço/canal. Igual gate Chan pair §1.4.

**3. Disaster stop 4σ** `[systematic_trading, p.212, ch.13]`

Conversão explícita de σ_YZ (fração anualizada) pra **price points** sobre um horizonte de referência:

```python
# Computed once at entry, frozen for life of position
sigma_pp_per_bar = entry_price * sigma_yz_at_entry / sqrt(bars_per_year)
sigma_pp_ref = sigma_pp_per_bar * sqrt(REF_HOLD_BARS)   # REF_HOLD_BARS = 24
disaster_threshold = 4 * sigma_pp_ref

def disaster_stop_exit(position, bar_t) -> bool:
    if position.direction == LONG:
        return (position.entry_price - bar_t.close) >= position.disaster_threshold
    else:
        return (bar_t.close - position.entry_price) >= position.disaster_threshold
```

**Convenção de unidades**: σ_YZ é fração anualizada (ex: 0.20 = 20%/y). `bars_per_year` é o mesmo do sizer (§3.3) — 1638 SPY/GLD, 6240 FX. `REF_HOLD_BARS = 24` (≈1 dia trading SPY ou ≈1 dia FX) é a escala de hold esperada — fixa, não tunável. Resultado: `disaster_threshold` em dólares, comparável diretamente com `(entry - close)`.

Carver `[p.212]` usa "X = 4 sigma_price_points from tracking extreme" — adaptamos pra "4σ from entry price" (disaster guard, não trailing). Tracking extreme é hook v2 #4. σ_YZ + threshold congelados no entry pra evitar stop "se mexer" com vol intra-trade.

**Sanity numérico** (SPY): entry=$500, σ_YZ=0.20, bars_per_year=1638, REF_HOLD=24 → σ_pp_per_bar ≈ $2.47, σ_pp_ref ≈ $12.10, disaster ≈ $48.40 (~9.7% below entry). Wide o suficiente pra não ser trailing disfarçado, apertado o suficiente pra capear gap notícia.

**Por que 4σ não-gridado**: mesmo argumento de K_filter — disaster stop é safety net, não target de otimização.

**Não-incluso v1 (hooks v2 §7)**:
- Vol-contraction regime-shift exit (sair quando YZ percentil sobe acima de threshold)
- Trailing stop / break-even shift
- Friday flat pra SPY (avaliar necessidade no diagnostic)

### 3.5 Grid v1 final

| Param | Valores | Tipo | Justificativa |
|---|---|---|---|
| `N_entry` | 20, 55 | gridado | Turtles canônico vs Donchian original `[p.353]` |
| `N_exit` | 10, 20 | gridado | Turtles canônico (5/20) vs simétrico c/ entry |
| `K_filter` | 33 | **fixo** | Filtro = classificador, não target (§3.1) |
| `target_vol` | 0.10 | **fixo** | Carver Half-Kelly conservador (§3.3) |
| `disaster_stop_n_sigma` | 4 | **fixo** | Carver semi-auto stop `[p.212]` (§3.4) |
| `ref_hold_bars` | 24 | **fixo** | Horizonte de referência pra disaster stop in price points (§3.4) |
| `cone_lookback` | 1700 | **fixo** | ≈1y; Sinclair "two-to-four years" `[p.58]` adaptado |
| `yz_window` | 20 | **fixo** | Sinclair janela curta canônica `[p.20-23]` |

**Combinatorial**: 2 × 2 = **4 configs × 3 ativos = 12 trials totais**.

DSR threshold approx: `E[max] ≈ √(2 ln 12) ≈ 2.23`. Mais alto que Chan pair (4 trials, 1.67) mas dentro do orçamento de catálogo.

**Anti-grid hidden parameter**: 5 dos 7 parâmetros são fixos a priori. Apenas `N_entry` e `N_exit` são gridados — ambos canon Turtles direto de Kaufman. Esta parsimônia é requisito explícito do pivô `[ROADMAP §Next steps]` e da lição PBO=0.849 do F3.D v1.

---

## 4. Dados

### 4.1 Símbolos e endpoints

| Símbolo | Endpoint Tiingo | Sessão | Bars/dia esperados |
|---|---|---|---|
| `SPY` | IEX 1h | 9:30-16:00 ET, ~252 d/y | ~7 |
| `XAU/USD` | FX 1h | Dom 17 ET → Sex 17 ET, ~5 d/wk | ~24 |
| `EURUSD` | FX 1h | Dom 17 ET → Sex 17 ET, ~5 d/wk | ~24 |

Lazy-cache via `tiingo_service` (spec pai). Probe inicial no plan §5.1.

### 4.2 Período de backtest

- **Train+Test combinado**: últimas 4 anos disponíveis por símbolo (corte em Tiingo retention real).
- **CPCV N=6** (mesmo do projeto-wide).
- **Warmup zero-trade**: primeiros 1700 bars excluídos do scoring (warmup do cone).

### 4.3 Calendar / timezone

- Todos os bars normalizados pra UTC no buffer interno.
- SPY: `pandas_market_calendars.get_calendar("NYSE")` filtra holidays + sessões parciais.
- FX: 24h Dom-Sex, ignora holidays (mercado FX não fecha por feriados domésticos isolados; respeita Christmas/New Year via filtros do Tiingo).

### 4.4 Fallback Bundle α

Se Smoke #2 detecta `XAU/USD` 1h retention < 3y:
1. Log warning estruturado em `logs/grid.log`.
2. Substitui símbolo no config: `XAU/USD` → `GLD` (Tiingo IEX 1h, mesma sessão SPY).
3. Atualiza `bars_per_year` no sizer: GLD usa 1638 (idem SPY).
4. Diagnostic report inclui flag `bundle_used: alpha` em vez de `beta`.

EUR/USD não tem fallback — é mais comum em planos Tiingo. Se ele falhar retention, **aborta o spec** e volta ao brainstorm pra reconsiderar premissa multi-asset.

---

## 5. Gates e diagnostic

### 5.1 Pre-gates (RuntimeError ou skip antes de qualquer trade)

1. **Tiingo retention**: § 4.4 acima. Probe no plan §5.1, antes de implementar a estratégia.
2. **Cone warmup**: < 1700 bars ⇒ `is_quiet = False`. Sem erro.
3. **σ_YZ degenerate**: `σ_YZ < 1e-6` ⇒ sizer retorna 0 + warning. Sem erro.
4. **Sample size pós-backtest**: `n_trades < 30` por símbolo ⇒ retentativa única documentada com `K_filter = 50` (não grid). Se ainda < 30 ⇒ FAIL com diagnostic claro.

### 5.2 Anti-overfit gates (mesmo battery do projeto)

- **CPCV** `[advances_fin_ml, p.156-160, ch.7]` — N=6 folds.
- **PBO** `[p.208-211]` — descarta se PBO > 0.5.
- **DSR** `[p.205-207]` — threshold = `√(2 ln N_trials) ≈ 2.23` para N=12.
- **WF (Walk-Forward)** — anchored, mínimo 3 segmentos.
- **MCPT (Monte Carlo Permutation Test)** — 1000 permutations.

PROCEED requer: `PBO ≤ 0.5 ∧ DSR p ≤ 0.05 ∧ WF positivo ∧ MCPT p ≤ 0.05`.

### 5.3 Diagnostic métricas obrigatórias

Em `reports/grid_vol_expansion_<timestamp>/diagnostic.md`:

**Gate-related:**
- `cpcv_sharpe_per_fold`, `pbo`, `dsr_p`, `wf_segments`, `mcpt_p`
- `verdict`: PROCEED / PROCEED-WITH-CHANGES / BLOCK
- `n_trials_total`, `best_config_per_symbol`

**§1.4 compliance:**
- `median_hold_hours_per_symbol`, `max_hold_hours_per_symbol`
- `pct_trades_overnight_per_symbol`
- `pct_time_stop_exits` (alerta se > 20%)
- `pct_disaster_stop_exits` (alerta se > 30% — sinal de stop muito apertado)
- `pct_opposite_channel_exits` (esperado dominante)

**Filter health:**
- `bars_in_warmup_per_symbol`
- `pct_filter_active` (deve ser ~33% pós-warmup)
- `yz_pct_at_entry_avg` (deve ser < 33)
- `n_trades_per_symbol` (gate ≥ 30)

**Signal quality:**
- `breakout_strength_avg` (quanto o close excedeu o canal, em σ_YZ units)
- `win_rate_per_symbol`, `avg_win_per_symbol`, `avg_loss_per_symbol`
- `sharpe_per_symbol`, `max_dd_per_symbol`

**Bundle confirmation:**
- `bundle_used` (α ou β)
- `tiingo_retention_per_symbol` (anos disponíveis)

### 5.4 Fallback config K=50 (única retentativa)

Se diagnostic detecta `n_trades < 30` em qualquer símbolo, runner re-executa **uma vez** com `K_filter = 50` (50th percentile, filtro ativo ~50% do tempo). Resultados desta retentativa são **anexados** ao mesmo diagnostic com seção separada `Retry K=50`. Não é grid disfarçado — é decisão pré-registrada documentada aqui em §1.3 e §5.4.

Se K=50 ainda dá `n_trades < 30` ⇒ FAIL definitivo. Significa que no período histórico não há sinal suficiente; estratégia descartada do catálogo (ou retorna ao brainstorm pra reconsiderar lookback / símbolos).

---

## 6. Testes

### 6.1 Inventário (target ~25 novos, baseline 405 verde)

**`test_vol_expansion_regime_filter.py`** (~8 testes)
- YZ formula vs canonical Sinclair `[p.22, Eq.2.17a]` (synth OHLC, valor esperado calculado à mão)
- k weighting factor `[p.23]`: N=20 → k esperado
- Cone percentile incremental matches scratch numpy version
- Warmup: < 1700 bars retorna `is_quiet=False` sempre
- σ_YZ degenerate (constant prices): `is_quiet=False` (não NaN), `sigma_yz_annual=0`
- Opening jump: YZ > close-to-close (validação Sinclair `[p.22]`)
- Multiple horizons consistency (sanity: maior janela → menor variação)
- **Annualization output**: σ_YZ_raw=0.01/bar com bars_per_year=1638 → σ_yz_annual ≈ 0.405 (= 0.01 × √1638). FX 6240 → ≈ 0.79

**`test_vol_expansion_breakout_signal.py`** (~5 testes)
- Long fire: synth com close > max(N) histórico
- Short fire: synth com close < min(N)
- No fire: close dentro do canal
- Boundary: close == max(N) → no fire (estritamente >)
- N_entry=55 vs N_entry=20 com mesmo dataset (sanity)

**`test_vol_expansion_sizer.py`** (~5 testes)
- Vol target formula: σ_YZ_annual=0.20, target=0.10, equity=$100k → notional=$50k; shares = $50k / entry_price
- σ floor: σ_YZ_annual < 1e-6 → notional=0 + warning logged
- Convenção anualizada: input já anualizado, sizer não re-scaleia (consome direto)
- Equity scaling: dobrar equity dobra notional
- σ scaling: dobrar σ_YZ metade notional

**`test_vol_expansion_exit_manager.py`** (~6 testes)
- Opposite channel exit long: close < min(N_exit)
- Opposite channel exit short: close > max(N_exit)
- Time-stop hard cap: 48h exato
- Disaster stop long: `(entry - close) >= disaster_threshold` (com unit conversion §3.4: σ_YZ → price points sobre REF_HOLD_BARS)
- Disaster stop short: `(close - entry) >= disaster_threshold` (idem)
- Disaster stop unit conversion: σ_YZ=0.20 + entry=$500 + bars_per_year=1638 + REF=24 → threshold ≈ $48.40 (sanity §3.4)
- Race condition: as 3 condições disparam mesmo bar → primeira na ordem ganha

**`test_vol_expansion_strategy_integration.py`** (~3 testes)
- Cenário 1: synth 1y de bars com regime quiet + breakout long no bar 100 → ordem long emitida; exit no opposite channel → flat
- Cenário 2: synth com regime ruidoso (σ alta) sempre → zero trades
- Cenário 3: 3 símbolos sintéticos paralelos, um com sinal um sem → posições corretas por símbolo

### 6.2 Não-incluso v1

- Property tests (Hypothesis) — hook v2
- Performance benchmarks (cone rebuild < X ms) — hook v2
- Stress tests com tick data — não temos infra

---

## 7. Hooks v2 (deferred)

Documentados aqui pra ressuscitar se v1 PASS:

1. **Multi-horizon cone**: YZ em 20 + 60 bars, exigir percentil baixo nos dois (Sinclair `[p.58-59]` faz cone multi-horizonte).
2. **Pyramiding**: até 4 unidades estilo Turtles `[trading_systems_methods, p.353]`. Adiciona unidade a cada novo high (long) ou low (short) por X% do range.
3. **Vol-contraction regime-shift exit**: sair quando YZ percentil sobe acima de threshold (filtro vira "saímos do regime de baixa vol"). Adiciona 4ª condição ao ExitManager.
4. **Trailing disaster stop**: usar Carver tracking extreme `[p.212]` em vez de entry price congelado.
5. **Universo expandido**: + GBP/USD, + GLD em paralelo (não substituto). Re-roda DSR com N_trials maior.
6. **Meta-label AFML over este sinal**: item 3 do ROADMAP next steps post-pivot. Triple-barrier sobre as entradas Donchian filtradas, walk-forward CV com purge/embargo `[advances_fin_ml, ch.7]`.
7. **Friday flat pra SPY**: avaliar se `pct_trades_overnight_SPY > X%` e DD overnight é material.
8. **Asymmetric direction bias**: testar long-only em SPY (equity drift) vs bidirecional FX. Hipótese alternativa não-canônica.

---

## 8. YAGNI explícito (NÃO está no v1)

- ❌ **Pyramiding** (Turtles 4 unidades) → hook v2 #2
- ❌ **GARCH(1,1)** filter — Sinclair `[p.57]` adverte instabilidade de params em re-fit
- ❌ **EWMA λ filter** `[p.218]` — Sinclair próprio adverte curve-fit explícito
- ❌ **Multi-horizon cone** → hook v2 #1
- ❌ **Pair logic / cointegration** — esse é Chan, não Sinclair
- ❌ **K_filter como parâmetro tunável** — fixo a priori (§3.1)
- ❌ **target_vol como parâmetro tunável** — fixo 10% (§3.3)
- ❌ **disaster_stop_n_sigma como parâmetro tunável** — fixo 4 (§3.4)
- ❌ **Universe selector dinâmico** — ROADMAP §3 adverte ("Universe Selector é estratégia, precisa passar gate")
- ❌ **Options chain** — não temos infra (Sinclair-puro requeriria)
- ❌ **VIX feed** — não temos endpoint Tiingo
- ❌ **Trailing stop** → hook v2 #4
- ❌ **Friday flat SPY** → hook v2 #7
- ❌ **Asymmetric direction** → hook v2 #8

---

## 9. Dependências

### 9.1 Diretas

- ✅ `tiingo_service` lazy-cache (spec `2026-04-15-tiingo-service-lazy-cache-design.md`, entregue 2026-04-15)
- ✅ `DiagnosticAnalyzer` GATE_UPSTREAM_FAIL handling (commit `8f51a0a`)
- ✅ `StrategyBase` (`backtest/strategies/base.py`)
- ✅ Gate battery CPCV/PBO/DSR/WF/MCPT (`backtest/gates/`)
- ✅ `pandas_market_calendars` (já no `pyproject.toml`)

### 9.2 Indiretas (validação)

- `Chan pairs §7.5 hook` — esta entrada satisfaz "próximo item do catálogo"
- `JORNADA §"O que vem a seguir"` — atualizar pós-implementação com verdict do run
- `ROADMAP §Next steps item 2` — esta é a 2ª das 3 famílias citadas (Chan ✗, Sinclair ←, Ehlers ⏳)

### 9.3 Bloqueia

Nada bloqueia downstream em v1. Se PASS, hook v2 #6 (AFML meta-label) é o próximo natural per ROADMAP item 3.

---

## 10. Citações consolidadas

| Decisão | Citação |
|---|---|
| Yang-Zhang volatility estimator | `[volatility_trading, p.22-23, Eq. 2.17a]` |
| Volatility cone | `[volatility_trading, p.58-60]` |
| Filtro vol baixa "bottom third" como classificador (não target) | Adaptação a priori; Sinclair `[p.218]` adverte sobre curve-fit em filtros vol-tunáveis |
| Donchian 20/40 channel breakout (base Turtles) | `[trading_systems_methods, p.353]` |
| Bidirecional simétrico | `[trading_systems_methods, p.353, RULE]` |
| Volatility-targeting (vol scalar) | `[systematic_trading, p.144, p.159, ch.9-10]` |
| Half-Kelly cap (target ≤ SR/2) | `[systematic_trading, p.144, p.146, ch.9]` |
| Vol target 10% (≡ SR ≈ 0.2, conservador) | `[systematic_trading, p.143, p.146]` (CHF 2015 cautionary tale) |
| Disaster stop 4σ | `[systematic_trading, p.212, ch.13]` |
| Hard cap 48h compliance | `[chan-pairs-1h-design §1.4]` + `[tiingo-service-lazy-cache-design §1.4]` + `[systematic_trading, p.185-188, ch.12]` (cost ≤ 0.13 SR/y) |
| CPCV / PBO / DSR | `[advances_fin_ml, ch.7, p.156-160, p.205-211]` |
| Sinclair non-applicability de variance premium em equities individuais | `[volatility_trading, p.219, p.222]` (justifica index-only em SPY, não single-stocks) |
| Sizing único (sem pyramiding v1) | Parsimônia; hook v2 #2 referencia `[trading_systems_methods, p.353]` |

---

## 11. Risco e premissas explícitas

### 11.1 Risco principal

**O filtro YZ-cone pode ser muito eficaz** e reduzir trades a um número onde DSR fica insignificante. K=33 mantém filtro ativo ~33% do tempo *em distribuição estacionária*, mas em regimes prolongados de alta vol (ex: 2020 crisis) o filtro pode ficar inativo por meses. Mitigado por:
- Pre-gate `n_trades ≥ 30` por símbolo
- Retentativa documentada com K=50
- Período de backtest 4y (cobre regimes diversos)

### 11.2 Premissa não testável em v1

**Sinclair `[p.219, p.222]`** documenta que variance premium não é persistente em single equities — é index-effect. SPY (S&P 500 ETF) é index-proxy ⇒ premissa OK. **Mas o mecanismo desta estratégia (vol-expansion breakout) não depende de variance premium** — depende de informação carregada por movimento pós-quiescência. Premissa fica honesta: usamos Sinclair pra ferramenta (YZ + cone), não pra hipótese econômica (vol risk premium).

### 11.3 Premissa testável em v1 (gate explícito)

Mecanismo de **breakout de baixa vol carregar informação** é a hipótese central. Falha se:
- Breakouts low-vol não geram retornos diferenciados de breakouts high-vol → `breakout_strength_avg` low + Sharpe baixo
- Filtro YZ-cone não diferencia regimes (sample percentil é uniformemente distribuído entre bins de retorno) → `yz_pct_at_entry_avg ≈ 50` em vez de < 33
- Edge esmaga em FX (24h vs 6.5h sessions) → Sharpe SPY OK mas FX fail

Cada um destes é diagnosticado explicitamente em §5.3.

---

**Spec status:** design completo e citado, aguardando aprovação do Victor antes do plan de implementação.

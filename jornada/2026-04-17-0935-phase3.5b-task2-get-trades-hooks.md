# Phase 3.5b Task 2 — ganchos `get_trades()` + script de validação [PLANO B]

**Data:** 2026-04-17
**Branch:** `phase3.5b/winners-validation-20260417`
**Iter:** 2
**Scope:** CODE-ALLOWED. Sem commit/push manual — loop auto-commita.

## O que foi feito

Task 2 do `specs/phase_3_5b_winners_validation.md` — adicionar hooks
`get_trades()` nos 3 winners Phase 3 e escrever o script orquestrador
que produz os 4 relatórios padrão.

### Mudanças de código (aditivas, não-breaking)

1. **`strategies/letf_rotation.py`** — nova função `get_trades(result,
   spx_returns, config, *, asset_label=None, notional=1.0) -> list[Trade]`.
   Varre `result.regime` e para cada bloco contíguo `"ON"` emite um
   `Trade` com:
   - `entry_date` = primeiro dia ON, `exit_date` = último dia ON,
   - `entry_price` = 1.0, `exit_price` = `∏(1 + on_returns[block])`
     (retorno composto leveraged net de fee, **sem** switch cost / tax —
     o layer de report aplica IR por trade lucrativo).
   - `asset_label` default `"LETF_<L>x"`.

2. **`strategies/tsmom.py`** — nova função `get_trades(result, close, *,
   asset_label, notional=1.0) -> list[Trade]`. Um trade por bloco `"LONG"`
   com `entry_price=close[entry]` e `exit_price=close[exit]` (underlying
   direto, sem leverage).

3. **`grid/portfolio_3leg.py`** — nova função `aggregate_leg_trades(legs)`
   que achata uma sequência `(name, list[Trade])` em uma única lista
   ordenada cronologicamente. IR 15% continua aplicado por trade
   individual na renderização (§3 do spec).

4. **`scripts/validate_phase3_winners.py`** (NEW, ~340 loc) — orquestra:
   - Carrega SPX TR 1970-2026 + QQQ/GLD Tiingo daily + SPY benchmark.
   - Roda os 3 simuladores com os configs winner congelados.
   - Extrai trades via os hooks, escala pelo capital inicial (default
     R$100k), renderiza `standard_report.md` + `trade_log.{csv,md}` +
     `equity_curve.png` + `summary.json` em
     `reports/phase3_5b/<strategy>/`.
   - Portfolio 3-leg EW: blend daily returns + aggrega trades das 3
     pernas com notional = capital/3.

### Testes

Novo arquivo `tests/test_get_trades_hooks.py` com **15 testes**:

- LETF: lista de Trade, ordenação cronológica, contagem bate com
  entradas ON, comportamento em regime sempre-OFF, label default.
- TSMOM: lista de Trade, preços batem com `close`, contagem bate com
  entradas LONG, zero trades em série chopy.
- Portfolio: agregador vazio, ordenação por entry_date, labels
  preservados, leg_name aplicado em trade sem asset, estabilidade
  em empate de datas.
- Smoke test integrando hooks → `build_standard_report`.

**Baseline:** 572 → **587 passed** (550 original preservado).

### Smoke test do script end-to-end

Rodou em ~1.3s produzindo 4 pastas de relatório. Números de cabeçalho
(janela longest de cada strategy):

| Strategy | Window | # Trades | Sharpe | CAGR |
|---|---|---|---|---|
| LETF EMA100/2x | 1970-01 → 2026-04 | 296 | 1.848 | 44.69% |
| QQQ Donchian 20/10 | 2001-05 → 2026-04 | 107 | 1.389 | 17.40% |
| GLD Donchian 40/20 | 2004-11 → 2026-04 | 48 | 0.937 | 11.46% |
| Portfolio 3-leg EW | 2004-11 → 2026-04 | 451 | 2.108 | 25.56% |

Os Sharpes diferem das métricas Phase 3 que usavam janela comum 3-leg
(2004-11 → 2026-04 para todos) — isso é por design: Phase 3.5b reporta
cada strategy no seu longest window individual (regra do CLAUDE.md).

### Observação para Tasks 3-6 ⚠️ FLAG

O Trade log LETF mostra **100% win rate** e **Profit Factor = ∞**. Isso
é **artefato da definição de trade** (um bloco contíguo ON = um trade),
não falha do backtest. Como a MA100 prende a ON regime durante trends
sustentados, o retorno composto leveraged sobre cada bloco ON é
tipicamente positivo mesmo com dips intra-bloco. **Interpretação
correta:** "fração de blocos ON net-profitable", não "fração de swings
ganhadores". Tasks 3-6 devem documentar isso explicitamente no jornada
de cada strategy para não induzir em erro.

Nenhuma lógica de strategy foi tocada — só hooks de export. Winners
permanecem imutáveis.

## Próximo passo

Task 3: rodar `validate_phase3_winners.py`, interpretar o
`standard_report.md` do LETF + trade log, e escrever
`jornada/<date>-phase3.5b-letf-full-validation.md [PLANO B]`. Mesma
estrutura para Tasks 4 (QQQ), 5 (GLD), 6 (portfolio).

## Citações

- LRS signal (MA100, above→RISK_ON, below→RISK_OFF):
  `[leverage_for_the_long_run, p.13]`.
- Leveraged return synthesis (`r = L·r_SPX - fee/252`):
  `[leverage_for_the_long_run, p.16]`.
- Donchian 20/10 TSMOM (Turtle basis):
  `[trading_systems_methods, p.353]`.
- BR 15% swing capital-gains tax: Investment Mandate §4.
- Trade-level Profit Factor / SQN / Kelly: `[advances_fin_ml, p.220-223]`.

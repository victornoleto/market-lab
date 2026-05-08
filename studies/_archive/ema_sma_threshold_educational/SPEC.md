# Spec — EMA/SMA Threshold Crossover on SPY with Leveraged ETFs (Educacional)

**Status**: educational / experimental — **não reivindica PASS no mandate**.
Projeto está em MAINTENANCE mode (§1 — 100% Plano C). Este sweep existe
para estudo de trend-following clássico com LETFs, sem modificar
portfolio de produção.

## Objetivo

Testar uma estratégia de trend-following em SPY:
- **Buy signal**: `P(SPY) > MA(N) × (1 + threshold)` → comprar leg alavancado
  long (1x / 2x / 3x SPY).
- **Sell signal**: `P(SPY) < MA(N) × (1 − threshold)` → trocar por leg
  alavancado short (0x cash, −1x, −2x, −3x).
- **Dentro da banda** (`MA × (1 ± threshold)`): mantém posição anterior
  (histerese anti-whipsaw).

Rankear 384 combinações `(MA type, lookback, threshold, buy leg, sell leg)`
por composite score CAGR/Sharpe/MDD e reportar "X/7 gates passed" como
informação adicional (gates informacionais, não-bloqueantes).

## Fonte de dados

`data/testfolio/cache/history.parquet` → ticker `SPYSIM` (S&P 500 TR,
1986-01-02 → 2026-04-17, 10151 dias, ~40 anos cobrindo 2000/2008/2020).

Returns derivados: `r_SPX(t) = pct_change(P_SPX(t))`.

Leveraged legs sintetizados via fórmula Gayed
[`leverage_for_the_long_run`, p.16]:

```
r_synth(t) = L · r_SPX(t) − fee/252
```

Onde `L ∈ {+1, +2, +3, 0, −1, −2, −3}` e fee = 0.95% aa (UPRO pós-2021
real, citado em `[leverage_for_the_long_run, p.16, footnote 23]`).
`L = 0` representa cash (return diário fixo do rate passado, default 0.0).

## Regras de sinal

Para cada dia `t` após warmup (`t ≥ lookback`):

```
MA(t)      = SMA(P_SPX, lookback)(t) ou EMA(P_SPX, span=lookback)(t)
upper(t)   = MA(t) · (1 + threshold)
lower(t)   = MA(t) · (1 − threshold)

regime(t) = +1  se  P_SPX(t) > upper(t)        (BUY — long leverage)
regime(t) = −1  se  P_SPX(t) < lower(t)        (SELL — short/cash)
regime(t) =  regime(t−1) caso contrário        (HOLD — histerese)
```

Primeiro dia pós-warmup sem regime prévio → default `-1` (conservador).

Cita `[leverage_for_the_long_run, p.8]` (SMA canônico), `[p.11]` (band
anti-whipsaw, Reddit study 5%) e `[p.13]` (regime de volatilidade).

## Grid parameters

| Eixo | Valores default (384 configs) | Full (`--full`, 1512 configs) |
|---|---|---|
| `filter` | SMA, EMA | SMA, EMA |
| `lookback` | 50, 100, 150, 200 | 20, 50, 75, 100, 125, 150, 175, 200, 250 |
| `threshold_pct` | 0.00, 0.02, 0.05, 0.10 | 0.00, 0.01, 0.02, 0.03, 0.05, 0.07, 0.10 |
| `buy_leverage` | 1.0, 2.0, 3.0 | 1.0, 2.0, 3.0 |
| `sell_leverage` | 0.0, −1.0, −2.0, −3.0 | 0.0, −1.0, −2.0, −3.0 |

Cartesian product. Lookbacks e thresholds sempre se referem ao SPY TR
(SPYSIM), não ao leg alavancado.

Mandate Rule #2 limita a 4 parâmetros; aqui são 5 mas cada um tem
justificativa econômica:

1. `filter` testado em Gayed [p.14, Table 6].
2. `lookback` testado em Gayed [p.14, Table 6, 10-200].
3. `threshold_pct` é banda de histerese, citado em Reddit study 5%
   `[p.11]`.
4. `buy_leverage` testado em Gayed [p.17, Table 8].
5. `sell_leverage` — contribuição deste estudo (Gayed usa só cash
   como off-asset `[p.21]`); justificativa: o usuário pediu varrer
   `{cash, short1x, short2x, short3x}` para entender como short alavancado
   se compara ao cash clássico na queda.

## Custo / fees (simplificado)

- **Fee drag leveraged**: 0.95% aa aplicado diariamente
  (`[leverage_for_the_long_run, p.16]`). Mesma fee para long e short legs
  (synth limitation — short ETFs reais têm borrow cost extra, não
  modelado aqui).
- **Switch cost**: 10bp commission + 5bp spread = 0.15% por transição
  de regime (mesmo padrão de `letf_rotation.py`).
- **Tax**: não modela DARF 15% aqui (educacional; real-portfolio decisions
  em `portfolio-aposentadoria.md` não dependem disso). Flag `--tax` no CLI
  ativa se necessário.

## Métricas computadas (por config)

Via `market_lab.backtest.metrics.performance`:

- `cagr(equity, 252)` — CAGR anualizado.
- `sharpe(returns, 252)` — Sharpe anualizado, ddof=0.
- `max_drawdown(equity)` — magnitude positiva em [0, 1].
- `calmar(equity)` — CAGR / |MDD|.
- `sortino(returns, 252)` — downside deviation.
- `volatility(returns, 252)` — σ · √252.
- `n_switches` — contagem de transições de regime.

## Composite score (ranking)

Decisão do usuário (não cita livro — ranking educacional):

```python
rank_cagr   = rankdata(cagrs) / N         # alto = bom
rank_sharpe = rankdata(sharpes) / N       # alto = bom
rank_mdd    = rankdata(-abs(mdds)) / N    # alto = bom (menor MDD)
composite   = 0.4 · rank_cagr + 0.4 · rank_sharpe + 0.2 · rank_mdd
```

Percentile-based normalization é robusto a outliers (configs
catastróficos com CAGR=-100% não distorcem a escala).

## Gates (7, informacionais — não-bloqueantes)

| # | Gate | Threshold | Citação |
|---|---|---|---|
| G1 | PBO (CSCV) | < 0.5 | `[advances_fin_ml, p.208-211]` |
| G2 | DSR p-value | < 0.05 | `[advances_fin_ml, p.222-223]` |
| G3 | Walk-Forward ≥ 6/8 windows + MDD<25% | pass | `[advances_fin_ml, ch.12]` |
| G4 | Single-block OOS Sharpe > 0 (split 70/30) | > 0 | mandate §5 |
| G5 | FWD stress post-2020 Sharpe > 0 | > 0 | mandate §5 |
| G6 | Bootstrap 99.9% CI low > 0 | > 0 | `[advances_fin_ml, p.196-202]` |
| G7 | Cross-lib ±3pp CAGR (hand-rolled vs rolling) | ≤ 3pp | `[advances_fin_ml, p.31-34]` |

Cada config recebe `gates_passed ∈ [0, 7]`. Reportado na tabela de top-20
como coluna informativa.

## Benchmark

SPY buy-and-hold (SPYSIM full range 1986-2026) sempre listado no topo
da tabela como linha "benchmark". Métricas esperadas: CAGR ~10-12%,
Sharpe ~0.5, MDD ~-55% (crash 2008).

## Outputs

```
reports/educational/ema_sma_threshold/
├── report.md                        # top-20 ranked + gates summary + archetypes
├── configs.csv                      # todos 384 configs + métricas + gates
├── summary.json                     # machine-readable (axes, top-K, benchmark)
└── equity/
    ├── 01_<cfg_id>.parquet          # top-10 equity curves
    ├── 02_<cfg_id>.parquet
    └── ...
```

`report.md` inclui:

1. **Benchmark row** — SPY buy-hold métricas.
2. **Top-20 table** — colunas `rank | cfg_id | filter | N | thr | buy_L |
   sell_L | CAGR | Sharpe | MDD | Calmar | composite | gates_passed`.
3. **Gates summary** — quantos configs passaram cada gate individualmente.
4. **Config archetypes** — agrupamento do top-20 por `(filter, buy_L)` para
   identificar padrões dominantes.
5. **Disclaimer** — "Educacional. Não reivindica PASS no mandate."

## Verificação

```bash
# Smoke (8 configs, ~5s)
.venv/bin/python scripts/run_ema_sma_threshold_sweep.py --smoke

# Default (384 configs, ~30-60s)
.venv/bin/python scripts/run_ema_sma_threshold_sweep.py

# Full (1512 configs, ~3-5min)
.venv/bin/python scripts/run_ema_sma_threshold_sweep.py --full

# Unit tests (8 novos, baseline 461 → 469)
.venv/bin/pytest tests/test_ema_sma_threshold_educational.py -v
```

## Citações consolidadas

- Synth LETF formula `r = L·r_SPX − fee/252`: `[leverage_for_the_long_run, p.16]`
- SMA 200 canônico: `[leverage_for_the_long_run, p.8, p.13]`
- MA periods 10-200 todos positivos: `[leverage_for_the_long_run, p.14, Table 6]`
- Leverage 1.25/2/3 testados: `[leverage_for_the_long_run, p.17, Table 8]`
- Band hysteresis 5%: `[leverage_for_the_long_run, p.11]` (Reddit study reference)
- Fee 0.95%: `[leverage_for_the_long_run, p.16, footnote 23]`
- PBO CSCV: `[advances_fin_ml, p.208-211]`
- DSR: `[advances_fin_ml, p.222-223]`
- Bootstrap: `[advances_fin_ml, p.196-202]`
- CPCV/purged K-fold: `[advances_fin_ml, ch.12]`
- Cross-lib tolerance: `[advances_fin_ml, p.31-34]`
- Max 4 params rule: `[systematic_trading]` (este spec usa 5 com justificativa).

# Momentum Study

Fork research-only de `studies/momentum_13612_universes/`, agora usando a base
local `yf_tickers`/`yf_daily_prices` em Postgres como fonte de preços. O objetivo
é testar famílias de momentum de longo prazo com grids amplos, mas com filtros,
trial accounting e validações explícitos.

## Uso

Auditar cobertura e filtros sem rodar o grid:

```bash
uv run python studies/momentum/run.py --config studies/momentum/config/default.yaml --audit-only
```

Rodar uma bateria ampla:

```bash
uv run python studies/momentum/run.py --config studies/momentum/config/default.yaml --phase broad
```

Rodar apenas US stocks:

```bash
uv run python studies/momentum/run.py --config studies/momentum/config/us_stocks.yaml --phase broad --cache-panels --progress-every 50
```

`broad` é um screen rápido: usa retornos pré-computados, pula bootstrap/cross-check
por configuração e limita o PBO por amostragem determinística (`broad_pbo_max_configs`)
para manter o grid manejável. Use `--phase validate` nos finalistas para rodar a
validação pesada completa `[advances_fin_ml, p.208-211]`,
`[advances_fin_ml, p.273-275]`.

Rodar um smoke pequeno:

```bash
uv run python studies/momentum/run.py --config studies/momentum/config/default.yaml --phase broad --limit-configs 20 --max-symbols 80
```

Por padrão o run grava PNGs em `studies/momentum/plots/` e um manifesto em
`studies/momentum/results/plot_manifest.json`. Use `--no-plots` para rodar só
os artefatos tabulares/JSON.

## Configuração

Filtros, universos, top-N, rebalance, score modes e weight modes ficam em
`config/default.yaml`. Ajuste ali antes de rodar novas baterias.

## Data Policy

- Fonte principal: Postgres local criado por `data/yfinance/sync.py`.
- Coluna de preço padrão: `adj_close`.
- `country` é mercado/listagem (`us`, `br`, `global`), não domicílio jurídico.
- Como o universo vem de yfinance/current lists, resultados continuam
  `promotion_eligible=false` até existir auditoria PIT/delisted/corporate actions
  `[advances_fin_ml, p.208-211]`.

## Estratégias

- `raw_13612`: média 1/3/6/12 meses `[stocks_on_the_move, p.60]`.
- `mom_12_1`: 12 meses excluindo o último mês, para reduzir reversal curto.
- `mom_3_6_12`: lookbacks intermediários.
- `clenow_trend`: slope log-preço anualizado × R² `[stocks_on_the_move, p.70-77, p.98]`.
- `vol_adjusted`: momentum dividido por volatilidade `[systematic_trading, p.137-148]`.
- `mom_lowvol_composite`: blend rank momentum + low-vol.
- Pesos: equal, inverse-vol e capped inverse-vol.
- Rebalance: offsets explícitos ou `staggered_offsets=true` para reduzir timing luck
  `[advances_fin_ml, p.273-275]`.

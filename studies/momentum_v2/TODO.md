# TODO — momentum_v2

O que falta testar/validar neste estudo. Tudo **research-only**; nada aqui muda o
mandate §1. Veredito atual e o que já foi validado: ver `README.md`.

## Já validado (recap)

- **us_stocks** — funil broad→evolution→validate, janelas 1990 + 2000: PASS em todos
  os gates honestos (PBO/DSR/WF/bootstrap/cross-lib), mas `promotion_eligible=false`
  por survivorship.
- Recorte **top_n 3-10** (executável na mão) + **sweep de drawdown** (vol-targeting
  corta o MDD full mantendo Sharpe/Calmar; SPY SMA200 = proteção de crise).

---

## 1. Outros universos US — `us_etfs` e `us_mixed`

Sem código novo — o funil já suporta via `--universe` (chaves em `UNIVERSE_SQL`).

```bash
for u in us_etfs us_mixed; do
  for s in 1990-01-01 2000-01-01; do
    uv run python studies/momentum_v2/run.py --universe $u --phase broad     --start $s --cache-panels
    uv run python studies/momentum_v2/run.py --universe $u --phase evolution --start $s --cache-panels
    uv run python studies/momentum_v2/run.py --universe $u --phase validate  --start $s --cache-panels
  done
done
```

- Benchmark já = SPY (config). Cobertura no DB (audit 2026-06-16): ~5.3k US ETFs;
  `us_mixed` = stocks + ETFs juntos.
- **Hipótese a testar:** ETFs têm menos "nomes puros de momentum" e mais sobreposição
  (setoriais/alavancados/inversos) — o edge pode enfraquecer ou virar ruído. Conferir
  se top-N de ETFs não vira concentração em LETFs (3x) — talvez precise de filtro de
  exclusão por nome/alavancagem.
- Rodar `topn_view.py` e `drawdown_sweep.py` nas mesmas janelas para comparar com us_stocks.

## 2. Universo BR — `br_stocks`

```bash
uv run python studies/momentum_v2/run.py --universe br_stocks --phase broad --start 2000-01-01 --cache-panels
# (+ evolution/validate; e talvez --start 2010-01-01)
```

- Benchmark já = `BOVA11.SA` (config); filtros via chave `br_stock`. Tax model BR já é o default.
- **Janela 1990 não se aplica** (cobertura BR começa ~2000; BOVA11 desde 2008). Usar 2000+ / 2010+.
- Cobertura: ~279 BR stocks no DB — universo pequeno; revisar `min_median_dollar_volume`
  e `min_price` para a realidade da B3 (liquidez/ticks menores) antes de concluir.
- **Survivorship é ainda pior no BR** (cobertura yfinance limitada + poucos delisted) —
  tratar como diagnóstico, não esperar promoção.

## 3. Resolver o survivorship bias (o teto real)

É o **único bloqueador** que sobrou: o feed yfinance/current-universe não tem as
empresas que faliram/saíram, então os CAGRs estão inflados e nada é promovível
`[advances_fin_ml, p.208-211]`. Resolver exige **duas** coisas:

1. **Preços de tickers delisted/mortos** (retornos até o delisting, ajustados).
2. **Membership point-in-time do índice** (quais tickers eram negociáveis/no índice
   em cada data de rebalance) — hoje só temos a tentativa Wikipedia-PIT do estudo antigo.

### Providers candidatos (verificar preço/cobertura atuais antes de assinar)

| Provider | Resolve | Custo aprox. | Acesso | Nota |
|---|---|---|---|---|
| **Norgate Data** | delisted US + **membership PIT** (S&P 500/400/600 histórico) | ~US$30–80/mês | app local + `norgatedata` (Python) | Melhor encaixe retail p/ PIT membership; foco US + futuros; não é REST. |
| **Sharadar SEP/SF1** (Nasdaq Data Link) | delisted (survivorship-free) + fundamentos PIT | ~US$50–150/mês | REST/Quandl API | Ótimo custo-benefício; fácil em Python; membership via tabelas de actions. |
| **EOD Historical Data** (eodhd.com) | delisted + flag survivorship-free; constituents de índices | ~US$20–100/mês | REST API | Mais barato; cobertura global ampla; bom p/ começar. |
| **Polygon.io** | tickers delisted + corporate actions | ~US$30–200/mês | REST API | Cobertura boa; PIT membership não é produto central. |
| **CRSP** (via WRDS) | gold standard: delisting returns + membership histórico | institucional (caro) | acadêmico/WRDS | Melhor qualidade, pior preço; via universidade. |
| **Tiingo** | já temos infra de storage; algum delisted | barato | REST API | Parcial — não cobre PIT membership completo. |

### Recomendação (a decidir)

- Se o objetivo é **fechar o survivorship de US stocks com PIT membership**: **Norgate**
  é o caminho mais direto (delisted + constituintes históricos num lugar só).
- Se preferir **API barata** e tratar membership separadamente: **EODHD** ou **Sharadar**
  para os preços de delisted, reconstruindo membership do S&P via constituents deles.
- Reaproveitar a infra: já existe `TiingoSource`/`TiingoStorage` e o padrão `PostgresSource`;
  um novo provider entraria como mais um data source + um ingest para `yf_*`-style tables
  (ou tabelas novas `pit_membership` / `delisted_prices`).

### Passos quando houver dados PIT/delisted

1. Ingerir preços delisted + tabela de membership PIT no Postgres.
2. Passar `eligible_by_date` (já suportado em `core.py`/`overlays.py`) ao funil para
   mascarar o ranking pelos constituintes de cada data.
3. Re-rodar us_stocks e comparar CAGR/MDD vs o screen survivorship-biased — só então
   um PASS de gate pode virar `promotion_eligible`.

---

## Outros (menor prioridade)

- **Combo de overlays não medido:** vol-target **+** SPY SMA200 (de-risk geral + proteção
  de crise) — o `drawdown_sweep.py` testou cada um isolado, não combinados.
- **Janelas adicionais** de robustez (ex.: 2010+) e/ou walk-forward de regime.
- **Dep nota:** o uso contra o DB real precisa de `psycopg` declarado em `pyproject.toml`
  (entra junto da infra de dados Postgres, fora deste commit). Os testes não precisam
  (usam conn fake / `_load_panel` stubbado).

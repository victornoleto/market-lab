# MyFxBook Strategy Reverse-Engineering Study

> **Estudo isolado.** Vive em `studies/myfxbook_reverse_engineering/`,
> não toca `backtest/strategies/`, `live/` nem nenhuma rota de produção.
> Pode importar de `backtest/data/`, `backtest/validation/` e outras
> infra-shared do projeto.
>
> **Mandate alignment:** trabalho sob **maintenance mode** (mandate §1).
> Capital permanece 100% Plano C. Plano A continua DORMANT até que algum
> system identificado aqui passe gates §2.4 hard-block + paper-trading
> 90d demo Pepperstone. Reativação requer sign-off explícito do usuário.

## Objetivo

Reverse-engineer todas as strategies publicamente acessíveis no perfil
MyFxBook **HappyForex** (vendor de Expert Advisors `happyforex.de`),
identificar o **direction signal** de cada uma, e rankear as melhores
candidatas para reativação eventual de Plano A.

## Por que esse vendor

Após sweep inicial em 2026-05-01 (`2026-05-01-happy_market_hours_v231/`),
foi identificado que **o sistema `OLD Happy Market Hours v2.3.1`
(id 1407880) tem edge real estatisticamente** (Sharpe 2,51 full-sample,
DSR p<0,0001, WF 7/8) — mas com 5 anos de blackout (2021-07 → 2026-05)
e direction signal não-determinado sem 1m OHLC.

Como o vendor publica **~60 systems**, há possibilidade real de outros
candidatos com:
- Edge persistente até hoje (não-OLD, em produção atual)
- DD reduzido (< 30%)
- Universe diversificado (Index, Gold, Crypto além dos FX)

Justifica catalog-wide sweep antes de investir em paper-trading 90d num
system específico.

## Estrutura

```
studies/myfxbook_reverse_engineering/
├── README.md                            ← este arquivo
├── ROADMAP.md                           ← phases + tasks check-off
├── .env                                 ← cookies MyFxBook (gitignored)
├── shared/                              ← scripts reusáveis para qualquer system_id
│   ├── config.py                        ← paths, cost models, constants
│   ├── fetcher.py                       ← scrape paginado de trade history
│   ├── parser.py                        ← HTML → parquet
│   ├── catalog.py                       ← scrape lista de systems do vendor
│   ├── sanity.py                        ← K1 (martingale) + checks
│   ├── eda.py                           ← timing/exit/sizing/decay
│   ├── direction_dukascopy.py           ← OHLC-based signal extraction
│   └── gates.py                         ← §2.4 application
├── data/
│   ├── catalog/                         ← lista de todos systems
│   ├── ohlc/                            ← Dukascopy 1m bars cache (per pair+month)
│   └── trades/                          ← per-system parquets
├── systems/<system_id>/                 ← per-system reports
│   ├── sanity.md
│   ├── eda.md
│   ├── signal_rule.md
│   └── decision_memo.md
├── ranking/                             ← cross-system comparison
│   └── TOP_SYSTEMS.md (output final)
├── _archive/                            ← Folclore-classified systems
└── 2026-05-01-happy_market_hours_v231/  ← exemplar prototype (id 1407880)
```

## Convenções

- Citação obrigatória (`CLAUDE.md` Regra 2) em todo decision memo.
- Cookies `.env` no nível do estudo (não per-system).
- Logs unificados em `logs/myfxbook_reverse_engineering.log` (per memory feedback).
- Rate limit scrape: 1 req / 400ms (default Playwright session).
- Cost model forward Pepperstone Razor 2025 padrão (override per-pair).

## Citações principais

- `[evidence_based_ta, Aronson, p.367-380]` — session/hour-of-day FX effects
- `[advances_fin_ml, p.196-211]` — DSR + PBO gates
- `[advances_fin_ml, ch.7-8]` — Triple-barrier + meta-labeling para direction
- `[fooled_by_randomness, Taleb]` — vendor track-record bias
- `[systematic_trading, Carver]` — cost model retail + sizing
- `[testing_tuning]` — walk-forward methodology

## Estado atual

Veja `ROADMAP.md` para phases ativas e próximos passos.

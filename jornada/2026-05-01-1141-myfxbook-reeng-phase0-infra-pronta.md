# Phase 0 do estudo MyFxBook Reverse-Engineering pronta — infra para escalar pra ~60 systems

**Data:** 2026-05-01

**Contexto:** o probe de 2026-05-01 sobre o sistema HappyForex/Happy Market Hours v2.3.1
(id 1407880) terminou com verdict "edge real existe mas blackout de 5 anos impede
verificar persistência" e 1/4 hard-blocks falhando (gate OOS bootstrap CI low).
Em vez de ir direto pra paper-trading só desse system, o ROADMAP definiu 8 fases —
catalog sweep do vendor inteiro (~60 systems), per-system sanity/EDA cheap, OHLC
1m, direction extraction, gates §2.4, ranking, paper-trading top-1.

Phase 0 era a fundação: transformar os scripts hardcoded do prototype em módulos
parametrizados por `system_id` em `studies/myfxbook_reverse_engineering/shared/`,
e provar que a generalização não introduziu bug aritmético.

## O que foi feito

Sete módulos em `shared/` cobrindo o pipeline inteiro até gates:

- `config.py` — paths, cost model Pepperstone Razor 2025, loader de cookies `.env`
- `fetcher.py` — scrape paginado da trade-history endpoint (cookies + rate limit 400ms)
- `parser.py` — JSON batches → parquet tipado (lots, pips, durations coerced)
- `catalog.py` — scrape da paginação do vendor + classifier de tier 1/2/3/folclore
- `sanity.py` — K1 (martingale) merged com lot dynamics — single dataclass `SanityStats`
- `eda.py` — timing/exit/sizing/decay/direction/evening merged — single `EDAStats`
- `gates.py` — full + OOS Sharpe, DSR p, bootstrap 99.9% CI seed=7, WF 8 windows

Mais um smoke test (`_smoke_test.py`) que carrega o parquet do prototype e roda
todo o pipeline, asseverando 109 números-chave a 3 decimais contra os relatórios
existentes (`reports/03_sanity_report.md`, `04b_direction_decay.txt`,
`06_gates_observed.md`).

## O que isso significa em prático

109/109 checks ✅ — sharpe full 2.507, OOS 1.894, bootstrap CI low full 1.075 e
OOS −1.668, walk-forward 7/8 windows positivas, todos os net-pips por par,
distribuição entry-hour/DOW/per-pair-peak — tudo bate com o prototype original.

Significa que dá pra rodar `compute_sanity(trades_df, system_id=NOVO)` em qualquer
system futuro do catálogo HappyForex e ter confiança que a aritmética é a mesma
que validamos no Happy Market Hours v2.3.1. Não introduzi bug ao generalizar.

A separação `compute_*` puro (retorna dataclass) + `format_*_report` markdown
+ `write_*_report` torna possível: (a) testar números sem ler arquivo, (b)
trocar o template do report sem mexer na lógica, (c) plugar nos próximos
módulos do ROADMAP (Phase 3 vai chamar `compute_sanity` e `compute_eda` em
loop sobre 60 systems).

Pytest continua rodando 771 testes (baseline preservado — nenhum test_*.py
em `studies/` então pytest não pega nada de novo).

## Onde a barra está agora

Phase 0 ✅. Próxima é Phase 1 — scrape do catálogo do vendor HappyForex (~60
systems) via `shared/catalog.py`, com gate "≥ 5 systems Tier 1+2 ou encerra
o estudo como Folclore puro". Vai exigir cookies frescos (Cloudflare expira),
então a primeira ação é confirmar que a `.env` ainda funciona ou re-export
do navegador.

Custo bounded ainda é ~11d ativos pra todo o pipeline. Probabilidade calibrada
de end-to-end success (algum system passar paper-trading 90d) continua 10-20%.

Capital permanece 100% Plano C durante todo o estudo (mandate §1, maintenance
mode). Plano A continua DORMANT até paper-trading PASS + sign-off explícito.

## Citações

- `[advances_fin_ml, p.196-211]` — DSR + PBO (gates 2 e 1)
- `[advances_fin_ml, ch.7]` — purged k-fold (próximas fases de direction extraction)
- `[evidence_based_ta, Aronson, p.367-380]` — hour-of-day FX session effects
- `[fooled_by_randomness, Taleb]` — vendor track-record bias / survivorship
- `[carver_systematic_trading, p.185-188]` — fixed commission domina cost model retail

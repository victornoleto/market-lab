# Winners Deep Dive — Structure

Cada relatório desta pasta deve ser gerado por `studies/letf_rotation_hunt/scripts/generate_winners_deep_dive.py` e seguir esta ordem:

1. `Resumo Executivo`
2. `Definicao Operacional`
3. `Benchmark Set`
4. `Metricas Principais`
5. `Equity E Relativo Aos Benchmarks`
6. `Rolling Windows`
7. `Entry-Date Analysis`
8. `Crises E Regimes`
9. `Comportamento ON/OFF`
10. `Limitacoes E Veredito`
11. `Artefatos Gerados`

Benchmarks obrigatorios:

- SPY buy-and-hold via `SPYSIM`.
- Plano C B4 original: `25% NTSXSIM / 25% GDESIM / 25% RSSTSIM / 25% ZROZSIM`.

Padrao de janela:

- Comparacao principal sempre usa a intersecao diaria entre estrategia, SPY e B4.
- Se a estrategia tiver historico maior que B4, mencionar como limitacao em vez de misturar janelas.

Metricas obrigatorias:

- CAGR, MDD, Sharpe, Sortino, Calmar, vol anualizada, skew, kurtosis, equity final.
- Rolling 3y/5y/10y/15y, com win-rate contra SPY e B4.
- Rolling relative equity 3y/5y/10y/15y por start date: equity da estrategia / equity do benchmark, percentual de dias acima, minimo relativo e maior sequencia abaixo do benchmark.
- Forward returns por data de entrada 1y/3y/5y/10y.
- Crises: dotcom, GFC, COVID, rates 2022.

Toda decisao de indicador, parametro, gate ou benchmark deve citar fonte no formato do projeto, quando aplicavel.

# MyFxBook Single-System Workbench

Ferramenta research-only para rodar um system MyFxBook por `accountOid`.

Ela organiza quatro etapas:

1. baixar `system_info` e histórico de trades, se `--download` for usado;
2. parsear/cachear `data/trades/<accountOid>/trades.parquet`;
3. minerar padrões de entrada com o Stage 1 existente;
4. criar uma regra candidata efêmera, fazer backtest sintético e gerar duas notas.

## Uso

Com dados já baixados:

```bash
uv run python -m studies.myfxbook_reverse_engineering.workbench.pipeline --account-oid 1407880
```

Baixando antes de analisar:

```bash
uv run python -m studies.myfxbook_reverse_engineering.workbench.pipeline \
  --account-oid 1152318 \
  --url "https://www.myfxbook.com/members/HappyForex/old-happy-forex-v241-real/1152318" \
  --download
```

O download via Playwright depende de sessão/cookies válidos conforme o estudo em `DOWNLOAD-DATA.md`.

## Saídas

Arquivos em `systems/<accountOid>/workbench/`:

- `pipeline_summary.json` — JSON parseável com scores e métricas.
- `pipeline_report.md` — leitura curta em Markdown.
- `candidate_window.parquet` — janelas candidatas usadas no backtest.
- `synthetic_trades.parquet` — trades sintéticos, se a regra disparar.

## Scores

`fidelity_score` mede quão bem a regra reproduz o system real: timing, direção, contagem, hold, correlação e lift contra baselines. É a nota A.

`efficacy_score` mede se os trades sintéticos da regra decodificada parecem economicamente úteis após custos simples: Sharpe, bootstrap, OOS, profit factor e walk-forward. É a nota B.

## Guardrails

- Não modifica `frozen_rules/`.
- Não faz paper/live.
- Não declara winner.
- A regra automática é candidata efêmera, útil para triagem.
- Qualquer promoção para estratégia exige validação separada com gates do mandate.

Citações metodológicas: candidate mining/no-lookahead `[advances_fin_ml, ch.5, ch.7]`; controles contra data mining `[evidence_based_ta, p.247-260]`; custos `[systematic_trading, p.182-197]`; bootstrap/DSR `[advances_fin_ml, p.196-211]`.

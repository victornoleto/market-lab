# Pivot de fonte de dados — Tiingo vira primary, yfinance vira fallback

**Data:** 2026-04-21 14h  
**Status:** fix aplicado, pytest green (914), loop 3.5e em pausa para decisão
de re-run.

---

## O que aconteceu

Durante a sessão de iters 15-23 do Phase 3.5e (grid honesto, Plano B LETF
rotation), o loop começou a reportar **"Stage-2 yfinance divergence"** em
pontos cada vez mais preocupantes:

| Iter | Ticker | Config | ΔCAGR Stage-2 | Gate (3pp) |
|---|---|---|---|---|
| 15 | QLD | c01 sma200 × 3 off-legs | 5-7pp | ❌ fora |
| 21 | QLD | c02 sma150+cash | **8.21pp** | ❌ fora |
| 23 | TQQQ | c02 sma150+cash | **15.16pp** | ❌ muito fora |

Em todas as iterações, o agente rotulou como "artefato de reconstrução
sintética do LETF vs yfinance" e seguiu em frente. O usuário parou o loop
e perguntou: **"O yfinance precisa ser a menos confiável. Foque em Tiingo
(pago) e testfol.io (base sólida). Não estou entendendo porque está dando
essa divergência."**

---

## Diagnóstico

O código em `reports/phase_3_5c/cross_lib/data/reference_prices.py` fazia:

- **Stage 1 (fonte de verdade)**: Tiingo para SPY/QQQ/GLD/TLT (underlyings),
  mas **yfinance para SSO/QLD/UPRO/TQQQ** (LETFs pós-inception). Motivo:
  Tiingo bulk cache não tinha as LETFs.
- **Stage 2 (validação independente)**: `yf.download()` re-fetch ao vivo
  dos mesmos LETFs.

Resultado: **yfinance vs yfinance** — dois snapshots da mesma fonte tirados
em momentos diferentes. yfinance ajusta retroativamente `adjusted-close` a
cada split/dividend, então cache parquet e fetch live divergem. Para
QQQ-based LETFs (QLD/TQQQ) o drift é muito maior (mais splits históricos),
chegando a 15pp de ΔCAGR. Nunca foi "artefato sintético". Sempre foi
yfinance consigo mesmo.

Tiingo tem `adj_close` point-in-time estável — nunca muda após o fechamento
da data. Testfol.io entrega equity curves simuladas (SPY 1x/2x/3x desde
1885) com metodologia documentada. Ambos são fontes pagas e confiáveis. O
pipeline estava deixando ambos de lado em favor da fonte grátis e instável.

---

## Correção aplicada (opção C, aprovada pelo usuário)

### C1 — LETFs entram no Tiingo

`scripts/tiingo_bulk_download.py`: adicionado SSO, QLD, UPRO, TQQQ ao
`ETF_TICKERS` + SHV (off-leg T-bills usado por c04). Re-run do `--bucket
etf` fetchou 5 missing + atualizou 30 existentes. Manifest agora cobre
desde a inception real de cada LETF até 2026-04-20.

### C2 — `reference_prices.py` vira Tiingo-first

`_real_post_inception(ticker, end_date)` agora tenta `TiingoStorage.read()`
primeiro; só cai em yfinance se `KeyError` (ticker fora do Tiingo — restam
UGL/SPXL/TMF que não entraram nesse batch mas não são usados em Phase
3.5e). A `adj_close` do Tiingo é usada como close canônico; OHL são
escalados pelo mesmo fator para preservar ranges intraday. Parquet
reconstruído: 78.231 linhas, cobertura SSO/QLD 2006-06-21+, UPRO
2009-06-25+, TQQQ 2010-02-11+.

### C3 — Stage-2 helper dedicado

Novo módulo `reports/phase_3_5c/cross_lib/stage2_validation.py`:

```python
run_stage2(ticker, cagr_stage1, strategy_cagr_fn=..., ...) -> Stage2Result
```

- SSO → `spy_2x_equity` do testfol.io
- UPRO/SPXL → `spy_3x_equity` do testfol.io
- QLD/TQQQ/UGL/TMF → `status="na"` com razão explícita ("sem QQQSIM/GLDSIM/
  TLTSIM payload; future work")

Zero yfinance no caminho. Tests novos em `tests/cross_lib/test_stage2_validation.py`
(6 testes, todos passando).

Spec `specs/phase_3_5e_plano_b_leverage_comparison.md §3.1` atualizado
para instruir futuras iters a usar o helper — chamadas diretas a yfinance
em sweep scripts ficam **proibidas**.

---

## Impacto nos resultados prévios

Os 12 trials do c01 AGGREGATE (DEAD, 0/12 gate pass) e os 3 trials parciais
de c02 (QLD/SSO/TQQQ, todos FAIL) **foram computados sobre yfinance pós-
inception**. Os verdicts finais (Calmar <0.5, Sharpe_net <0.8, FWD tariff
shock kill) não dependem de pequenos ajustes em `adj_close` — mas os
números exatos (Sharpe=0.660 para QLD+GLD, etc.) podem mudar ±0.05-0.15 com
Tiingo.

Risco: um config que estava **borderline fail** no yfinance poderia virar
**borderline pass** no Tiingo (ou vice-versa). Nenhum dos 15 trials até
agora estava borderline — todos bem longe dos gates. Mas para integridade
científica, idealmente c01/c02 re-rodam sobre o novo parquet.

**Decisão pendente:** re-run completo (opção a) ou aceitar resultados
prévios + seguir daqui com dados corretos (opção b).

---

## Próximo passo

Aguardar decisão do usuário sobre re-run. Independente:

- Se re-run: reset de trial_count.json + registry c01/c02, relançar loop.
- Se seguir: resumir loop, iter 24 faz UPRO c02 sobre novo parquet, depois
  aggregator c02.

Em ambos os casos, próximas iters usarão Tiingo (Stage-1) + testfol.io
(Stage-2 SSO/UPRO) + N/A explícito (Stage-2 QLD/TQQQ).

---

## Citações usadas

- Synthetic formula preservada: `[leverage_for_the_long_run, p.16]`
- Two-stage isolation rationale: `[advances_fin_ml, p.31-34]`
- Tolerance 3pp: spec §6.3 do 3.5c cross-lib design

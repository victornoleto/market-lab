# Iter 026 — MTUM real: DATA-LIMITED dead-end (subscription gone)

**Data**: 2026-04-29 (UTC, 02:30)
**Iter**: 026, slug `iter011-MTUM-real-data-limited-deadend`
**Status**: data_limited — backtest não rodou

## TL;DR

Plano era testar MTUM/SPMO/IDMO live (factor ETFs investíveis) como
substituto deployable do UMD academic da iter 016 (que mostrou +0.088 lh_56y
edge). Pre-run inventory:

- **MTUM** (iShares MSCI USA Momentum, live 2013-04+): ❌ Tiingo cache +
  ❌ testfolio synth
- **SPMO** (Invesco S&P 500 Momentum, live 2015-10+): ❌ ❌
- **IDMO** (Invesco S&P Intl Momentum, live 2015-08+): ❌ ❌
- **MTUMSIM** (potencial testfolio synth): n/a — não existe no testfolio cache

Tiingo subscription cancelled (`TIINGO_API_KEY` vazio) — sem on-demand pull.
Tiingo bulk script tem 32 ETFs (broad/sector/bond/commodity/leveraged) mas
zero factor ETFs.

## Decisão

Iter 026 declarado **DATA-LIMITED DEAD-END** (similar a iter 021 sector
rotation 4-asset, que também ficou inconclusivo por janelas de dados).

Sem verdict.json (build_zoo_plot pula iters sem verdict). Documentação fica
em `hypothesis.md` + `final_report.md` pra rastreabilidade.

## Implicações

1. **iter 016 UMD academic permanece a referência standing de momentum** —
   +0.088 lh_56y strict, +0.047 ndx_real, −0.016 vt_real. Best info disponível.

2. **B.5 direction paused, NOT closed** — MTUM real test estimaria edge
   ~+0.05 lh_56y (UMD academic × ~60% capture rate per Frazzini-Israel-
   Moskowitz 2018, que quantifica long-only constraint + turnover gap).
   Reativação dependente de:
   (a) Tiingo subscription resumption, ou
   (b) MTUMSIM testfolio synth construído a partir de prospectus iShares +
       MSCI Momentum Index history.

3. **Top-K do batch atual unchanged**: iter 011 substantive incumbent;
   iter 023 TLT-static é o forte candidate sub-iter (NEW STRONG 86,
   LEGACY WINNER 91, substantive +signal 3/3 datasets vs iter 011).

## Citações

- iter 016 (UMD academic) — proxy result
- `[stocks_on_the_move, p.21-30]` Clenow
- Frazzini-Israel-Moskowitz 2018 — Trading Costs of Asset Pricing Anomalies

## O que vem a seguir

Sintetizar batch 023-026 + atualizar STRATEGY_ZOO + plot zoo + decisão final
ao usuário.

# [SHORT-HOLD CFD] V2-L0 — Universe screener (PASS gate)

**Data:** 2026-04-18 | **Fase:** 3.5a-V2 | **Lead:** V2-L0 [atomic]
**Verdict:** ✅ PASS (39 ≥ 30 threshold)
**Branch:** `phase3.5a-v2/plano-a-last-attempt-20260418`

---

## O que foi feito

Primeira iter da V2 (last attempt Plano A). Construí o universo
multi-asset CFD que os próximos 7 leads vão testar. A meta era ter
≥30 instrumentos com cache Tiingo daily válido e medir 3 coisas por
instrumento: volatilidade anualizada 252d, Hurst exponent 100d
(proxy trend vs MR tendency) e correlação vs SPY 252d.

Tudo saiu do cache parquet já existente em `data/tiingo/daily/prices/`
— não foi preciso puxar nada novo da API. O FX/metais daily (12
pares) havia sido pullado em 2026-04-18 00:51 (ver
`data/tiingo/bulk_summary_bulk_forex_daily_20260418-0051.json`).

## Cobertura — 39 instrumentos em 3 classes

| Classe | N | Média n_bars | Média vol_252 | Média Hurst100 | Média corr_SPY |
|--------|--:|------------:|--------------:|---------------:|---------------:|
| ETF (equity/sector/commodity/FI) | 26 | 4391 | 0.260 | 0.452 | 0.412 |
| Forex (majors + metals) | 12 | 1913 | 0.125 | 0.414 | 0.133 |
| Crypto (BTC) | 1 | 4483 | 0.468 | 0.533 | 0.528 |

**Janelas:**
- SPY/QQQ/IWM voltam a 2001-05-14 (25 anos).
- Sector ETFs grandes (XLK/XLF/XLE/XLU) voltam a 2003-08-20 (23 anos).
- FX + metais daily têm apenas 2020-01-01 → 2026-04-17 (6.3 anos) —
  limitação Tiingo forex endpoint.
- BTCUSD volta a 2014-01-01 (12.3 anos).

## Flags de integridade

- **Stale (last_dt > 60d atrás):** DBA (2023-12-29). Será depriorizado
  em V2-L1/L2/L6. V2-L3 meta-label CPCV pode usar se útil.
- **Short window (< 1500 bars):** 0 instrumentos.
- **Low ADV USD (< $10M):** todos os 12 pares forex — Tiingo forex
  endpoint não reporta volume (é notional), não indica liquidez
  real. Ignorar esse flag para forex.
- **Errors:** 0.

## Observações relevantes para próximos leads

1. **Descasamento de janela forex vs equity.** Equity/ETF têm 25y,
   forex daily 6y. Para L1 TSMOM, IS/OOS partitions precisam respeitar
   isso — mínimo 2022-01-01 como corte se forex entrar no mesmo grid.
2. **Hurst médio em 0.45-0.54.** Maioria próxima de random walk (H=0.5).
   Outliers: TLT (0.32), IEF (0.31), XLRE (0.26) — signal de mean
   reversion; USO (0.57), XLK (0.54), XLU (0.54) — signal de trend.
   Isso informa **qual família funciona em qual ativo**
   `[algo_trading_chan, p.44-46]`.
3. **Corr vs SPY dispersa.** GLD (0.003), USO (-0.24), UNG (-0.13),
   XLE (0.04), TLT (0.14) — boa diversificação fora do core beta.
   Isso ajuda V2-L4 Carver risk-parity achar pesos não triviais.

## Artefatos produzidos

- `data/universe_plano_a_v2.json` — manifest machine-readable (39 rows).
- `reports/phase3_5a_v2/L0_universe_screener.md` — tabela + flags + verdict.
- `scripts/build_universe_plano_a_v2.py` — script reutilizável (idempotente).

## Citations

- `[advances_fin_ml, ch.2]` — data integrity pre-screen.
- `[systematic_trading, p.~90-100]` — universe breadth por Carver.
- `[algo_trading_chan, p.44-46, ch.2]` — Hurst via structure function.

## Próximo lead

**V2-L1 — TSMOM multi-asset daily [sweep-configs]** (~14 iters).
Bootstrap do registry popula `configs` (4 lookbacks × 3 vol-targets =
12) e `tickers_pending` vem deste universo. Próxima iter = apenas
bootstrap (atomic commit isolado pelo protocolo fan-out §2).

---

**Pytest:** 765 passed (baseline preservada).

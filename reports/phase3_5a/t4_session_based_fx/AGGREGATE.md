# Lead T4 — Session-based FX strategies (aggregate)

**Phase:** 3.5a | **Lead:** T4 | **Status:** DEAD END (0/6 PASS)
**Period:** 2020-01-06 → 2026-04-14 (~6.3 y, Tiingo IEX 1h FX cache)
**Tested:** 6 FX tickers × 3 configs = 18 runs
**Aggregation iter:** 32

## Summary

T4 reprised three canonical FX session plays on the six most liquid
FX pairs (EURUSD, GBPUSD, EURGBP, USDCAD, USDJPY, AUDUSD) 1h:
London-open breakout off the Asian range, NY-close mean reversion,
and Asian-range fade against the prior NY range. After modelling the
full Pepperstone Razor cost stack (2 bps half-spread + $3.50/side +
daily swap) and the 5-gate framework, **0/6 tickers pass**. The
sweep is a clean DEAD END — every configuration either fee-drags
itself to ruin (ORB / range-fade) or degenerates into a
near-zero-trade regime that the Sharpe can't support (NY-close MR).

Pattern by family:

- **london_orb_asian_range** (breakout): catastrophic and uniform.
  OOS Sharpe spans −3.13 (USDJPY) to −9.31 (EURGBP), CAGR −21% to
  −31%, MaxDD −40% to −54%, 470–575 trades/yr. Median hold 1.0 d so
  the trade COUNT — not the hold time — is what kills it: each
  round-trip burns ≥5–7 bps on spread + commission + adverse fill and
  the alpha is below that threshold. Confirms prior T2
  breakout-on-FX-1h finding: Donchian/ATR families don't carry
  transaction costs on FX 1h (`[quant_trading_chan, ch.3]`).
- **ny_close_mr_1h** (mean reversion): degenerate-by-design. Band at
  0.2 × 24-bar range is so tight it fires 0–9 trades over 2 years of
  OOS (eurgbp → 0, gbpusd/eurusd → 2, usdjpy → 3, audusd → 1,
  usdcad → 9). The two "positive" OOS Sharpes — audusd +0.75 (1
  trade) and usdjpy +0.27 (3 trades) — are pure noise: DSR p-values
  collapse once sample size is this small, WF can't decide, and FWD
  window gives 0 trades on both. Widening the band would pull the
  family back into ORB-like trade-spam territory.
- **asian_range_fade_ny_range** (fade): universally negative. OOS
  Sharpe −2.93 to −4.95, CAGR −5% to −13%, 210–405 trades. Short
  median hold (0.29 d) means the cost-per-trade ratio is even worse
  than ORB in percentage terms.

Cross-ticker PBO = 0.0 (ties-aware — almost every config is a
net-loser everywhere, so rank stability is meaningless here). DSR
and WF fail for every passable-looking candidate due to
sample-size collapse.

**Diagnosis:** session rotation on FX majors at 1h, at Pepperstone
Razor costs, is DOA. The alpha hypothesis — that sessions produce
exploitable intraday skew — is visible in the raw returns but the
gross edge per trade (~3–8 bps) sits under the ~5–10 bps round-trip
friction. T4 joins T1 (BollingerMR 0/36), T2 (Donchian 0/12), T3
(pairs 0/6) as a cost-eaten DEAD END. Recurring lesson after 72
runs across 4 leads: **FX 1h with Razor-tier cost is not where
Plano A edge lives.** Next lead (T5) moves to regime filtering —
the hope is a selective filter reduces trade count without touching
the per-trade hit rate.

## Cross-ticker table

| Ticker | Best config       | Sharpe OOS | CAGR OOS % | MaxDD OOS % | Trades OOS | Median hold (d) | PASS |
|--------|-------------------|-----------:|-----------:|------------:|-----------:|----------------:|:----:|
| AUDUSD | ny_close_mr_1h    |      +0.75 |      +0.21 |       −0.13 |          1 |            0.46 |   ✗  |
| USDJPY | ny_close_mr_1h    |      +0.27 |      +0.18 |       −0.75 |          3 |            0.46 |   ✗  |
| EURGBP | ny_close_mr_1h    |       0.00 |       0.00 |        0.00 |          0 |            0.00 |   ✗  |
| USDCAD | ny_close_mr_1h    |      −0.50 |      −0.28 |       −0.98 |          9 |            0.46 |   ✗  |
| GBPUSD | ny_close_mr_1h    |      −0.74 |      −0.18 |       −0.50 |          2 |            0.33 |   ✗  |
| EURUSD | ny_close_mr_1h    |      −0.83 |      −0.10 |       −0.24 |          2 |            0.46 |   ✗  |

All 6 tickers fail the same way: DSR sample-size collapse on the
MR family + catastrophic fee-drag on the two other families.

**Family-level worst cases (OOS):**

| Ticker | london_orb Sharpe | london_orb Trades | asian_fade Sharpe |
|--------|------------------:|------------------:|------------------:|
| EURGBP |             −9.31 |               575 |             −3.22 |
| USDCAD |             −6.98 |               573 |             −4.95 |
| EURUSD |             −6.24 |               558 |             −3.32 |
| GBPUSD |             −5.94 |               552 |             −3.67 |
| AUDUSD |             −4.62 |               487 |             −2.93 |
| USDJPY |             −3.13 |               470 |             −3.11 |

## Citations

- `[quant_trading_chan, p.43-53, ch.2-3]` — FX intraday parsimony
  (≤ 5 params) and Sharpe annualization; bound on how thin a session
  band can be before the Sharpe stops meaning anything.
- `[trading_systems_methods, p.353]` — Donchian/breakout foundations
  (base template for `london_orb_asian_range`).
- `[trading_systems_methods, p.326-329]` — range-fade / false-breakout
  mechanics (base template for `asian_range_fade_ny_range`).
- `[volatility_trading]` — ATR filter + Chandelier exit (stop-loss
  layer across the three families).
- `[systematic_trading, p.185-188]` — hold-time discipline; T4
  respects the ≤ 24 h intra-session ceiling even on breakout.
- `[advances_fin_ml, ch.7]` — CPCV / PBO gate framework used to
  compute cross-config PBO per ticker.

## Links

- Per-ticker reports: `reports/phase3_5a/t4_session_based_fx/*.md`
- Registry: `reports/phase3_5a/t4_session_based_fx/registry.json`
- Jornada: `jornada/2026-04-18-1545-phase3.5a-T4-session-based-fx-DEAD.md`
- Next lead: **T5** — Regime-filter hybrid over BollingerMR SPY baseline
  (`specs/phase_3_5a_plano_a_investigation.md` §T5).

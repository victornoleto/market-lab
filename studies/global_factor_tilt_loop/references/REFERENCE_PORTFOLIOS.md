# Reference Portfolios — bestfolio.app top-Sharpe leaderboard 2026-04-27

External benchmarks the loop should beat (or aspire to). Compiled
2026-04-27 from `bestfolio_leaderboard_2026-04-27.json` (raw API
response). All metrics are bestfolio's own backtest engine output —
not independently verified.

## Top 10 by Sharpe (full-period)

| # | strategy | author | yrs | CAGR | MDD | Sharpe | risk | type |
|---|---|---|---|---|---|---|---|---|
| 1 | VAA-G4 SmartStack (Gold+MF) | Keller & Keuning | 33.4 | 19.6% | -17.6% | 1.18 | aggressive | TAA |
| 2 | HAA SmartStack (Gold+MF) | Keller | 28.8 | 17.5% | -15.9% | 1.18 | moderate | TAA |
| 3 | Tactical Permanent Standard | Adam Butler (ReSolve) | 38.8 | 7.1% | -7.5% | 1.18 | conservative | TAA |
| 4 | HAA Standard (with QQQ) | Keller | 33.4 | 14.4% | -16.8% | 1.17 | moderate | TAA |
| 5 | Composite Momentum Standard | BestFolio | 28.8 | 12.6% | -19.4% | 1.17 | moderate | TAA |
| 6 | RP Gold+SCV No Filter | Schwoerer | 24.8 | 7.5% | -15.6% | 1.17 | moderate | risk-parity |
| 7 | HAA without QQQ | Keller | 33.4 | 12.4% | -12.4% | 1.15 | moderate | TAA |
| 8 | Golden Ratio | Bogleheads | 33.1 | 10.8% | -19.4% | 1.15 | moderate | static |
| 9 | BAA-G12 Balanced | Keller | 29.0 | 11.3% | -11.0% | 1.13 | moderate | TAA |
| 10 | Permanent Portfolio Tactical | Browne | 38.8 | 6.7% | -7.5% | 1.13 | conservative | TAA |

## Loop iters comparison

| iter | Sharpe (long-window) | CAGR | MDD | gap to bestfolio #1 |
|---|---|---|---|---|
| 002 (winner) | 1.00 (32y) | 13.2% | 21.2% | -0.18 / -6.4pp / -3.6pp better MDD |
| 003 (user portfolio) | 0.77 (31y) | 11.65% | 44.5% | -0.41 / -8.0pp / +27pp worse |
| 004 (winner) | 0.89 (38y) | 9.5% | 20.8% | -0.29 / -10.1pp / -3.2pp better MDD |
| **VAA SmartStack** | **1.18 (33.4y)** | **19.6%** | **17.6%** | reference |

The loop's iter 002 is competitive with bestfolio's TAA family at the
**unstacked** Sharpe level (~1.0) but loses ~0.18 Sharpe vs the
SmartStack overlay. The SmartStack overlay is exactly the gold + MF
sleeve approach from iter 004 — but applied on top of a more
sophisticated momentum core (HAA dual+canary vs iter 002's K=2 fixed).

## Keller TAA family — academic references

### VAA (Vigilant Asset Allocation) — Keller & Keuning 2017

- SSRN: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3002624
- Title: "Breadth Momentum and Vigilant Asset Allocation (VAA): Winning More by Losing Less"
- Mechanism: Offensive universe {SPY, EFA, EEM, AGG} + Defensive {LQD, IEF, SHY}
- Breadth signal: if ANY offensive asset has 13612W momentum < 0 → switch B fraction to defensive
- T1/B1 = top-1 offensive when bullish, switch entirely to top-1 defensive when bearish
- VAA-G4: G=4 (4 offensive assets); recommended config in original paper

### HAA (Hybrid Asset Allocation) — Keller & Keuning 2023

- SSRN: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4346906
- Title: "Dual and Canary Momentum with Rising Yields/Inflation: Hybrid Asset Allocation (HAA)"
- Mechanism: Dual momentum (absolute + relative) + single "canary" asset
- Canary signals risk-on/risk-off for whole portfolio
- Simpler than VAA, designed for retail; updated post-2022 inflation regime
- Stronger empirical Sharpe in modern regime (post-2022 rising yields)

### Other Keller papers

- BAA (Bold Asset Allocation): https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4166845
- DAA (Defensive Asset Allocation): SSRN 3212862
- LAA (Lethargic Asset Allocation): mostly static + simple regime filter

## SmartStack overlay (bestfolio convention)

"SmartStack (Gold+MF)" appears to mean: the base TAA strategy decides
the dynamic equity/bond allocation per month, and a fixed sleeve of
~10-15% gold + ~10% managed futures is added stacked (capital-efficient
allocation, not separately funded). Total notional ~1.2-1.4×.

Closest analog in our loop: iter 004 (momentum K=2/lb=6 + 10% KMLM).
The gap (Sharpe 0.89 → 1.18) likely comes from:
1. HAA's superior momentum core (dual+canary vs raw top-K)
2. Gold sleeve added (we only have MF in iter 004)
3. Possibly different rebalance frequency (HAA monthly vs our monthly — same)

## Citations to anchor iter 005+ proposals

- VAA paper SSRN 3002624 — direct citation for breadth momentum
- HAA paper SSRN 4346906 — direct citation for dual+canary
- `[stocks_on_the_move, ch.6]` — Clenow on dynamic vs static (in cache)
- `[advances_fin_ml, ch.10]` — factor mining methodology (in cache)

NOTE: These are external references; primary book citations from
`books/summaries/` remain mandatory per CLAUDE.md Regra 2. Use SSRN
papers as supplementary.

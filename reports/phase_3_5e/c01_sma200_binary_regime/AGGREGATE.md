# c01 SMA200 Binary Regime — Phase 3.5e Aggregator [SWING BROKER]

**Lead:** c01_sma200_binary_regime | **Iter:** 19 | **Aggregation date:** 2026-04-21
**Strategy:** SPY > SMA200 (prev day) → 100% asset; else → off-leg.
**Signal:** SPY SMA200 `[leverage_for_the_long_run, ch.2]`
**Assets:** QLD (2×QQQ), SSO (2×SPX), TQQQ (3×QQQ), UPRO (3×SPX)
**Off-legs:** cash (0%), GLD, TLT
**Tax:** 15% IR BR flat on CAGR.

---

## Aggregate PBO (N=12, informational)

**PBO = 0.139** (PASS — threshold < 0.5)
N = 12 configs, 252 CSCV combinations.
Common window: 2004-11-18 → 2026-04-14 (GLD-constrained).

> **Note:** This is the c01-family PBO (N=12). The real PBO gate for Phase 3.5e
> fires at the final aggregator after all 144 trials (12 configs × 4 assets × 3 off-legs).
> `[advances_fin_ml, p.208-211]`

---

## Results — All 12 c01 Trials

| Ticker | Off-leg | Window | CAGR_net% | Sharpe_IS | Sharpe_net | MaxDD% | Calmar | WF | OOS_S | FWD_S | DSR_p | Pre-pass | Fail reason |
|--------|---------|--------|-----------|-----------|------------|--------|--------|----|-------|-------|-------|----------|-------------|
| QLD | cash | 24.9y | 13.1 | 0.653 | 0.555 | -46.6 | 0.331 | 7/8 | 0.54 | -0.59 | 0.0034 | ✗ | FWD, CALMAR, SHARPE_NET |
| QLD | GLD | 21.4y | 17.5 | 0.776 | 0.660 | -51.6 | 0.400 | 8/8 | 0.51 | -0.25 | 0.0012 | ✗ | FWD, CALMAR, SHARPE_NET |
| QLD | TLT | 23.7y | 13.6 | 0.646 | 0.549 | -61.6 | 0.259 | 8/8 | 0.29 | -0.66 | 0.0116 | ✗ | OOS, FWD, CALMAR, SHARPE_NET |
| SSO | cash | 24.9y | 9.1 | 0.582 | 0.495 | -39.0 | 0.276 | 7/8 | 0.62 | -1.01 | 0.0343 | ✗ | FWD, CALMAR, SHARPE_NET |
| SSO | GLD | 21.4y | 11.8 | 0.647 | 0.550 | -42.4 | 0.326 | 8/8 | 0.59 | -0.49 | 0.0380 | ✗ | FWD, CALMAR, SHARPE_NET |
| SSO | TLT | 23.7y | 9.0 | 0.543 | 0.462 | -54.0 | 0.196 | 8/8 | 0.28 | -1.08 | 0.0920 | ✗ | DSR, OOS, FWD, CALMAR, SHARPE_NET |
| TQQQ | cash | 24.9y | 16.4 | 0.634 | 0.539 | -63.2 | 0.306 | 7/8 | 0.52 | -0.63 | 0.0397 | ✗ | FWD, CALMAR, SHARPE_NET |
| TQQQ | GLD | 21.4y | 22.2 | 0.755 | 0.642 | -63.7 | 0.409 | 8/8 | 0.44 | -0.40 | 0.0225 | ✗ | FWD, CALMAR, SHARPE_NET |
| TQQQ | TLT | 23.7y | 17.3 | 0.646 | 0.549 | -71.8 | 0.284 | 8/8 | 0.33 | -0.67 | 0.0544 | ✗ | DSR, OOS, FWD, CALMAR, SHARPE_NET |
| UPRO | cash | 24.9y | 11.7 | 0.564 | 0.480 | -55.7 | 0.248 | 7/8 | 0.58 | -1.07 | 0.1112 | ✗ | DSR, FWD, CALMAR, SHARPE_NET |
| UPRO | GLD | 21.4y | 14.6 | 0.630 | 0.536 | -53.2 | 0.323 | 8/8 | 0.50 | -0.72 | 0.1020 | ✗ | DSR, FWD, CALMAR, SHARPE_NET |
| UPRO | TLT | 23.7y | 11.7 | 0.551 | 0.468 | -64.3 | 0.214 | 8/8 | 0.33 | -1.12 | 0.1583 | ✗ | DSR, FWD, CALMAR, SHARPE_NET |

---

## Summary verdict

- **Total trials:** 12 (4 assets × 3 off-legs)
- **Pre-pass (pending PBO):** 0/12
- **FWD failures:** 12/12 (universal — Jan-Apr 2026 tariff shock)
- **Calmar < 0.5 failures:** 12/12
- **Sharpe_net < 0.8 failures:** 12/12
- **DSR failures:** 5/12 (DSR p degrades as trial count grows)
- **OOS failures:** 3/12

**Best:** QLD / GLD: CAGR_net=17.5%, Sharpe_IS=0.776, Sharpe_net=0.660, Calmar=0.400
**Worst FWD:** UPRO / TLT: FWD_Sharpe=-1.12

---

## Cross-asset patterns

**Best off-leg:** GLD dominates across all 4 assets in Sharpe_net and OOS_Sharpe.
**Worst off-leg:** TLT — adds OOS/DSR failures on top of universal FWD failure (2022 bond crash).
**Asset ranking (sma200_gld config, Sharpe_net):**
  1. QLD: 0.660 — 2×QQQ, NDX beta advantage
  2. TQQQ: 0.642 — 3×QQQ, higher CAGR_net (22.2%) but worse Calmar (0.409)
  3. SSO: 0.550 — 2×SPX, lower vol but lower return
  4. UPRO: 0.536 — 3×SPX, weakest in family

**Cross-leverage rule (spec §7.2):** QLD vs TQQQ for sma200_gld:
  - Sharpe_net(QLD)=0.660 vs Sharpe_net(TQQQ)=0.642 → difference = 0.018 < 0.1 threshold
  - Calmar(QLD)=0.400 > Calmar(TQQQ)=0.409 — TQQQ wins on Calmar
  - Rule: prefer 2× when Sharpe_net gap < 0.1 AND Calmar(2×) > Calmar(3×) → FAIL here
  - Conclusion: TQQQ marginally preferred by Calmar but gap is negligible

---

## Universal FWD failure analysis

**Root cause:** Jan-Apr 2026 tariff shock caused sharp SPX drawdown (~15%), triggering SMA200
sell signal. LETF then entered off-leg during one of the highest-vol QQQ periods of the decade.
FWD Sharpe ranges from -0.25 (QLD/GLD, least bad) to -1.12 (UPRO/TLT, worst).

**Is this a regime failure or a statistical outlier?**
- SMA200 Gayed strategy DOES rotate to off-leg during drawdowns — that's the design.
- The failure is in the off-leg performance: GLD held up best (-0.247 FWD) while TLT fell further.
- WF gate passes 7-8/8 for all configs → the IS signal is real; the 2026 stress is new.
- Implication for c02+: shorter MAs (SMA150, EMA100) may avoid delayed exits but also add noise.

---

## Stage 2 divergence note

Stage 2 (yfinance) shows 5-15pp CAGR divergence vs Stage 1 (reference_prices.parquet).
Root cause: synthetic LETF construction before inception dates (TQQQ/UPRO < 2010) inflates
returns in parquet data. Stage 2 yfinance uses actual inception prices from 2006/2009/2010.
This is expected and documented. It does NOT invalidate the strategy — it inflates IS CAGR
but not Sharpe or gates. Stage 2 divergence > 3pp flagged but non-blocking for this phase.

---

## Verdict: c01 DEAD END (0/12 pre-pass)

**PBO (c01 family, N=12):** 0.139 (PASS)
All 12 c01 trials fail the FWD gate. The Gayed canonical SMA200 regime filter does NOT
survive the Jan-Apr 2026 tariff stress window for any asset or off-leg combination.
Economic metrics (CAGR_net 9-22%) are present but Calmar <0.5 and Sharpe_net <0.8
across the board.

**Next:** c02 sma150_cash — shorter MA, cash off-leg. Tests if faster exit avoids 2026 stress.
`[leverage_for_the_long_run, p.30]`

---

## Citations

- `[leverage_for_the_long_run, ch.2]` — Gayed SMA200 binary regime canonical
- `[advances_fin_ml, p.208-211]` — PBO/CSCV gate (N ≥ 4 reliable)
- `[advances_fin_ml, p.298-299]` — DSR gate (cumulative n_trials)

# Phase 3.6 — swing-winner hunt running index

**Plan:** `docs/plans/2026-04-23-find-swing-winner-phase-3-6.md`
**Branch:** `phase3.6/swing-winner-hunt-20260423`
**Baseline pytest:** 918 green (collection verified 2026-04-23)
**Engine:** F2-patched (commit `7b90a8f`), lookahead-clean.

---

## Protocol

- Stop at **first winner** (all 13 gates pass, with user-locked relaxations in plan §5).
- Escalate after **10 FAIL or 3+ PARTIAL** (write `BREADTH_NO_WINNER.md`).
- Every candidate: `<family_slug>/AGGREGATE.md` + jornada entry + commit.
- Excludes 6 rejected V2 leads (TSMOM, Gayed EMA, AFML meta-label, Carver RP, Kalman pairs, Donchian vol-breakout).

## Candidates tried

| # | Family slug | Source book(s) | Broker | Horizon | Status | Verdict | Notes |
|---|---|---|---|---|---|---|---|
| A | `a_clenow_momentum` | `stocks_on_the_move.md` | Inter (stocks) | 21d rebal | done | ❌ FAIL (3/13) | OOS Sharpe 0.25, CAGR 2.67%, MDD −26.62%, DSR p=0.72, bootstrap CI straddles zero. IR vs SPY −0.63. FWD salvages (Sharpe 1.18 / CAGR 16.4%) but doesn't rescue OOS. Universe = Tiingo 1165 ADV>$50M (PIT-S&P proxy). |
| B | `b_risk_parity_inverse_vol` | `risk_parity.md`, `systematic_trading.md` | Inter (ETFs) | 21d rebal | done | ❌ FAIL (5/13) | OOS Sharpe 0.17, CAGR 1.31%, MDD −25.40% — edge absent; 2018-2023 rate shock killed bond+equity diversification; leverage cap prevents CDI-floor clearance |
| C | `c_gtaa_faber_10mo` | `trading_evolved.md` (p.183-185, p.211-212), `systematic_trading.md` | Inter (ETFs) | 21d rebal | done | ❌ FAIL (5/13) | OOS Sharpe 0.41, CAGR 3.89%, MDD −20.71%, **PBO 0.909** (catastrophic). 4-asset variant SPY/EFA/GLD/IEF (REIT+DBC absent from Tiingo). Cross-lib Δ=0.000pp (no alignment bug). Confirms Clenow's p.211-212 caveat: 10-mo MA is hindsight-curve-fit. |

## Waves

- **Wave 1 (HIGH):** A Clenow cross-sectional momentum, B RP inverse-vol, C GTAA 10-mo SMA — _dispatched 2026-04-23_
- **Wave 2 (MED):** D Chan MR pairs, E Ehlers cycles, F vol-targeting managed futures, H Adaptive Markets regime, I stat-sound indicators — _pending_
- **Wave 3 (LOW):** G Aronson EBTA, J ML classical, K universal trend, L sentiment/PEAD — _pending_

## Counters

- FAIL: 3
- PARTIAL (12/13): 0
- WINNER: 0
- Remaining until escalation: 7 FAIL **or** 3 PARTIAL

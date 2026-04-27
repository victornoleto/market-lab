# External Instruments — Capital-Efficient / Return-Stacking ETFs

Reference list of capital-efficient / return-stacking ETFs the user
flagged as relevant building blocks. Iters can reference these by name
when proposing portfolios; synth paths documented inline.

Maintained outside `BASE_MEMORY.md` to avoid bloat (BASE_MEMORY auto-
prunes at 18KB).

---

## WisdomTree Efficient ("NTS-") family

| Ticker | Product | Stack | Cache | Notes |
|---|---|---|---|---|
| **NTSX** | US 90/60 | 90% S&P 500 + 60% Treasury futures | check `NTSXSIM` | Cornerstone of WT Efficient line |
| **NTSI** | Intl Dev 90/60 | 90% MSCI EAFE + 60% Treasury futures | likely missing | ex-US developed pair to NTSX |
| **NTSE** | EM 90/60 | 90% MSCI EM + 60% Treasury futures | likely missing | EM pair |
| **GDE** | S&P + Gold | 90% S&P 500 + 90% gold via futures | `GDESIM` ✅ | Inflation-hedge stack |
| **NTSD** | US + Intl Equity | US large-cap holdings + intl equity index futures (actively managed) | missing — synth needed | **Added 2026-04-27** by user. Newer ETF. Stacks intl equity instead of bonds. |

NTSD synth path:
- Lower bound proxy: `SPYSIM × 1.0 + VEASIM × 0.9` (or `VXUSSIM × 0.9`
  for broader ex-US).
- Subtract ~50-100 bps/y financing for the futures overlay.
- Active management adds unmodeled tracking error — flag as INCOMPLETE
  if iter relies on tight tracking.

NTSD primary citation: `[risk_parity, ch.5]` (Bridgewater capital
efficiency rationale) + product prospectus (web fetch required when
online).

---

## Newfound/ReSolve Return Stacked ("RSS-") family

| Ticker | Product | Stack | Cache | Notes |
|---|---|---|---|---|
| **RSSB** | Global Stocks + Bonds | 100% VT-equiv + 100% IEF | `RSSBSIM` ✅ | Already in user portfolio (25%) |
| **RSST** | US Stocks + MF | 100% S&P + 100% managed futures | missing — synth as `SPYSIM + KMLMSIM` | In user portfolio (15%) |
| **RSBT** | Bonds + MF | 100% IEF + 100% MF | missing | Bond-replacement variant |
| **RSSY** | Stocks + Carry | 100% S&P + carry strategies | missing | Less validated |

---

## Standalone diversifiers (not stacked)

| Ticker | Product | Cache | Notes |
|---|---|---|---|
| **KMLM** | KFA Mount Lucas Managed Futures | `KMLMSIM` ✅ | In user portfolio (8%) |
| **DBMF** | iMGP DBi Managed Futures | `DBMFSIM` ✅ | Alternative MF sleeve |

---

## Avantis factor-tilt ETFs

| Ticker | Product | Cache | Synth path |
|---|---|---|---|
| **AVUV** | US small cap value | missing | Proxy: `VBRSIM` (Russell 2000 Value) |
| **AVDV** | Dev ex-US small cap value | missing | Proxy: `VSSSIM` or `EFVSIM` with size tilt |
| **AVEM** | EM with Avantis tilts | missing | Proxy: `VWOSIM` baseline |

Avantis tilt premium estimate: ~0.3-0.5%/y vs vanilla benchmark.
Document explicitly when synthing (Fama-French SCV / MOM premia).

---

## Momentum factor ETFs

| Ticker | Product | Cache | Synth path |
|---|---|---|---|
| **SPMO** | Invesco S&P 500 Momentum | missing | Synth from `SPYSIM` + cross-sectional MOM overlay |
| **IDMO** | Invesco Intl Dev Momentum | missing | Synth from `VEASIM` + MOM overlay |

Citation: `[stocks_on_the_move, p.21-30]` (Clenow), Jegadeesh-Titman
1993, AQR factor docs.

---

## Leveraged ETF (LETF) — daily-reset

| Ticker | Product | Cache | Notes |
|---|---|---|---|
| **WLDU** | iShares Edge MSCI World 2x | missing — synth via testfol.io `VTSIM?L=2` with 0.75% drag | **Added 2026-04-27** by user. Daily-reset 2× global equity. LETF decay literature: `[leverage_for_the_long_run, p.40-60]` — daily decay can be substantial in choppy markets but mild in strong trending markets. |

WLDU vs stacked alternatives (RSSB+NTSD+GDE):
- **WLDU pro**: single instrument; 2× notional global equity in one ticker
- **WLDU con**: 0.75% expense + ~SOFR financing + daily-reset decay
- **Stacked pro**: futures-based overlay has lower decay, can pair with bonds/MF/gold for diversification
- **Stacked con**: more tickers to rebalance, more counterparty surface

Primary citation for LETF caveat: `[leverage_for_the_long_run, p.40-60,
ch.3-4]` — Gayed's 200-day SMA gate dramatically reduces LETF decay
risk by avoiding choppy/bearish regimes. A WLDU-with-SMA strategy
deserves its own iter slot (Tier 1 reactivation candidate).

---

## Update protocol

When user flags a new instrument:
1. Add row to relevant table here.
2. Document synth path or note "synth missing".
3. If important enough to actively test, append to `BASE_MEMORY.md`
   `## Promising unexplored directions` between iters (NEVER mid-iter
   to avoid Stage 5 race condition).

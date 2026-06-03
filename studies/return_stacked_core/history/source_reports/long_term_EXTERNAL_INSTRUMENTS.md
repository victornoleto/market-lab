# External Instruments — Capital-Efficient / Return-Stacking ETFs

Reference list of capital-efficient / return-stacking ETFs the user
flagged as relevant building blocks. Iters can reference these by name
when proposing portfolios; synth paths documented inline.

Maintained outside `BASE_MEMORY.md` to avoid bloat (BASE_MEMORY auto-
prunes at 18KB).

Mirrored from `studies/global_factor_tilt_loop/EXTERNAL_INSTRUMENTS.md`
(same universe; RSIT row added 2026-04-27).

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
| **RSIT** | Intl Stocks + MF | ~100% MSCI EAFE/ACWI ex-US + 100% MF | pending launch | **Added 2026-04-27**. SEC 485APOS filed 2026-02-18 (Tidal Trust II). Launch ~mai/2026. Synth: `VEASIM×1.0 + KMLMSIM×1.0 − 50bps/y`. Mirror internacional do RSST. |

---

## Standalone diversifiers (not stacked)

| Ticker | Product | Cache | Notes |
|---|---|---|---|
| **KMLM** | KFA Mount Lucas Managed Futures | `KMLMSIM` ✅ | In user portfolio (8%) |
| **DBMF** | iMGP DBi Managed Futures | `DBMFSIM` ✅ | Alternative MF sleeve |
| **CTA** | Simplify Managed Futures Strategy ETF | missing | Active CTA ETF; proxy with `KMLMSIM`/`DBMFSIM` only with caveat |

KMLM vs CTA: both are managed-futures/CTA exposures, but they are not the
same instrument. `KMLM` tracks the KFA MLM Index style: rules-based trend
following over futures markets, with transparent index exposure and long
synthetic history in testfolio. `CTA` is an active ETF wrapper around a CTA
program; it can vary exposures/implementation and has shorter live history.
For backtests, `KMLMSIM` is the better long-window proxy; using it for `CTA`
tests the managed-futures sleeve concept, not CTA ETF tracking accuracy.
Managed futures are treated as a crisis/convexity diversifier per
`[ilmanen_expected_returns, ch.19]` and trend-following/momentum per
`[stocks_on_the_move, p.21-30]`.

---

## Avantis factor-tilt ETFs

| Ticker | Product | Cache | Synth path | Synth in `synths.py` |
|---|---|---|---|---|
| **AVUV** | US small cap value | missing | `VBRSIM + 75bps tilt` | `avuv_synth_returns_from_cache()` ✅ |
| **AVDV** | Dev ex-US small cap value | missing | `VSSSIM + 100bps tilt` | `avdv_synth_returns_from_cache()` ✅ |
| **AVEM** | EM with Avantis tilts | missing | `VWOSIM + 125bps tilt` | `avem_synth_returns_from_cache()` ✅ |
| **AVNM** | All-Intl (Dev + EM blend) | missing | `~78% VEASIM + ~22% VWOSIM + 60bps blended tilt` | `avnm_synth_returns_from_cache()` ✅ (added 2026-05-05 iter 057) |
| **AVDE** | Dev ex-US core (Avantis multi-factor) | missing | `VEASIM + 55bps blended tilt` | `avde_synth_returns_from_cache()` ✅ (added 2026-05-05 iter 057) |

Avantis tilt premium estimate: ~0.3-0.5%/y vs vanilla benchmark.
Document explicitly when synthing (Fama-French SCV / MOM premia).
INCOMPLETE: AVNM/AVDE static premiums are conservative literature midpoints
between Fama-French intl SCV (75-100bps) and US-LARGE-VALUE (50bps); real
Avantis multi-factor screens are proprietary.

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

## User-expanded stacking watchlist (2026-04-28)

These are user-provided building blocks for future iterations. Only the rows
with clear synth/cache support should be used in immediate tests; the others
need real ETF data or explicit synthetic assumptions.

### High-priority synthable now

| Theme | Tickers | Stack | Immediate synth path |
|---|---|---|---|
| Global stock + bonds | RSSB, NTSG | VT + GOVT/Treasury overlay | `RSSBSIM` ✅; NTSG proxy `0.9*VTSIM + 0.6*IEFSIM - 0.5*CASHX` |
| US stock + MF/CTA | RSST, CTAP, HOLD, MATE, JPM/Direxion upcoming | SPY + managed futures | proxy `SPYSIM + KMLMSIM - financing`; flag as RSST/CTAP concept |
| Intl stock + MF/CTA | RSIT/Tidal upcoming | VXUS/VEA + managed futures | proxy `VEASIM + KMLMSIM - financing`; incomplete until ETF launches |
| Stock + gold | GDE, ISSG | SPY + gold | `GDESIM` ✅ or proxy `SPYSIM + GLDSIM - financing` |
| Global/factor tilt | AVUV/AVDV/AVEM sleeves | SCV/value/factor exposure | `VBRSIM`, `VSSSIM`, `EFVSIM`, `VWOSIM` proxies |
| Classic NTS family | NTSX/NTSI/NTSE/NTSD | equity + Treasury or intl overlay | `NTSXSIM`; NTSI/NTSE synth from VEA/VWO + IEFSIM |

### Interesting but blocked or high-caveat

| Theme | Tickers | Blocker/caveat |
|---|---|---|
| Crypto stack | BTGD, RSSX, OOSB, OOQB, BEGS, ISBG, ISSB, ISBT | BTC/ETH synth and regime handling needed; high volatility may dominate gates. 2026-05-05 old-B4 deep dive preserved in `studies/b4-v2/LEGACY_B4_DEEP_DIVE.md`: BTGD proxy was `50% BTCSIM + 50% GLDSIM - 0.55%/yr ER`; corrected RSSX proxy was `100% SPYSIM + 65% GLDSIM + 35% BTCSIM - borrow`. Caveats remain: BTGD spot proxies skip futures roll cost, RSSX inverse-vol weights drift through time, and the discarded RSSX v1 proxy (`100% SPY + 100% BTC`) overstated BTC roughly 3x. |
| Income-option wrappers | ISTG, ISSG, ISST, ISBG, ISSB, ISBT | Option-income path dependency not representable by simple total-return stack |
| Gold/miners stack | GDMN | Gold miners proxy/data needed; miner beta differs from gold |
| Macro/carry/MNA | ASGM, RSBY, RSSY, RSBA | Need carry/MNA/AHLT/long-short proxy; avoid fake precision |
| Commodity/broad inflation | ALLW, RPAR, UPAR, WTIP, WTLS | DBC/LTPZ/long-short/oil/BTC components need cache/proxy decisions |

Immediate research implication: next tests should favor **global equity +
factor tilt + managed futures/CTA + gold/bonds** with low turnover, because
iters 001-002 failed mainly from defensive rotation and tax drag. `[risk_parity,
ch.5]`, `[ilmanen_expected_returns, ch.19]`, `[stocks_on_the_move, p.21-30]`.

---

## Update protocol

When user flags a new instrument:
1. Add row to relevant table here.
2. Document synth path or note "synth missing".
3. If important enough to actively test, append to `BASE_MEMORY.md`
   `## Promising unexplored directions` between iters (NEVER mid-iter
   to avoid Stage 5 race condition).

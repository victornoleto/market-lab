# Global Factor-Tilt Loop — STUDY PREPARATION

**Status**: PREPARATION + REFINED 2026-04-26. Ready to activate after
strategy_hunt_loop deploy_studies session closes.

**Mission**: Find ONE globally-diversified strategy that beats both:
1. **VT 1x buy-and-hold** (cap-weighted global passive baseline)
2. **Plano C V3_1 v3.5** (current factor + global with 25% GDE + 12% AVUS
   + 20% AVDE + 13% AVEM + factor tilts + BTGD)
3. **V_HYBRID + 10% MF** (the deploy_studies WINNER: V3_1 with NTSX
   replacing AVUS + 10% managed futures sleeve — Sharpe 0.743, MDD 44.7%,
   P(rolling 10y < 5%) = 0.6%)

The bar is **higher than VT-only** because deploy_studies already
identified strong factor + global + capital-efficiency combinations.
This loop must find something **structurally novel** vs those.

This is a **bifurcation** of `studies/strategy_hunt_loop/` — the
hypothesis-search infrastructure is reusable, only the universe and
benchmark change.

## Multi-stacking thesis (NEW — primary research direction)

**User's intuition (2026-04-26)**: "seria muito interessante ter alguma
forma de implementar multistacking como temos para etfs US."

Why this matters: deploy_studies showed that NTSX (US 90/60 stack) +
GDE (US 90/90 with gold) gives massive capital efficiency benefit. If we
can replicate this at the **global** level — i.e., return-stacked
INTERNATIONAL equity + bonds, or return-stacked GLOBAL equity + alts —
we may get the "best of both worlds" (capital efficiency + global
diversification).

Real-world ETFs to investigate:
- **NTSI** / **NTSE** — WisdomTree intl + EM versions of NTSX (REJECTED
  by Plano C V3.5 based on real 2021-2026 data showing 2022 rate-shock
  damage; revisit on 32y synth)
- **RSST** / **RSBT** / **RSSY** — Newfound/ReSolve "Return Stacked"
  family (US stocks + managed futures, bonds + MF, etc); inception
  2023+, only synth backfill via testfolio
- **RSSB** — Return Stacked Global Stocks & Bonds (100% world equity +
  100% Treasury bonds via futures; PULLED 2026-04-26, 56y synth available)
- **RSSX** — 100% S&P + 100% gold/BTC; inception May 2025, no synth
- **GDE** — already core of Plano C, 90% S&P + 90% gold

Open question: is there a path to a **global return-stacked all-weather**
portfolio? E.g., 60% RSSB (global eq + Treasury) + 30% GDE (S&P + gold)
+ 10% KMLM (managed futures) = 200%+ notional with full geographic
coverage + factor tilts + tail-risk hedge.

This is what the loop should explore systematically.

---

## Why a separate study (vs continuing strategy_hunt_loop)?

`strategy_hunt_loop` tested edge against SPY (US-only) and QQQ
(US-tech). Most winners (iter 035, 016, 006, 074, 079) **dominate SPY
because they add asset diversification on top of US equity** — bonds,
gold, vol-target overlay. They are not "edge over global equity";
they're "edge over US-only".

A US-resident investor going *globally diversified* would naturally use
**VT** (Vanguard Total World) or equivalent as the passive baseline.
That bench is harder to beat because:

1. VT is already 60% US + 40% international — the gain from adding
   ex-US is gone.
2. VT's natural Sharpe is *lower* than SPY (~0.55 vs 0.90 in 17y) but
   so is its CAGR — the bar shifts proportionally.
3. The candidate strategies need a DIFFERENT kind of edge: factor
   tilts, regional rotation, currency hedge, etc.

So: separate loop, separate winner conditions, separate dead-ends.

---

## Benchmarks (UPDATED 2026-04-26 — VTSIM now in cache)

| dataset | benchmark | window available | source |
|---|---|---|---|
| **vt_real** | VT 1x b&h | 2008-06 → present (~17y) | Tiingo VT.parquet (need to confirm pull) |
| **educational** | **VTSIM 1x b&h** | **1970-01 → 2026-04 (56y)** | testfolio cache (pulled) |
| ndx_real (carryover) | QQQ 1x b&h | 16y | Tiingo (existing) |

**EFASIM was previous candidate but is NOT what we want.** EFASIM is
MSCI EAFE (developed only, no EM, no small). VTSIM is the proper VT
analog (Total World — US + dev + EM + small-mid).

VTSIM gives us **56 years** of global equity benchmark history.
Includes: 1973-74 oil crisis bear, 1987 crash, 1990 recession, 2000
dot-com (US + intl), 2008 GFC, 2020 COVID, 2022 rate hikes, 2024-25.

---

## Candidate universe (Avantis-tilted, factor-aware) — CORRECTED

User clarified: **AVUS** is the broad US factor fund (not AVUV — that
is small-cap value only). Updated table:

### Avantis core (broad with multi-factor tilts)

| ticker | role | inception | live history |
|---|---|---|---|
| **AVUS** | US broad equity (size + value + profitability tilts) | 2019-09 | 6.5y |
| **AVDE** | International developed broad | 2019-09 | 6.5y |
| **AVEM** | Emerging markets broad | 2019-09 | 6.5y |
| **AVNM** | All Intl Markets (dev + EM combined) — newer convenience | 2024-01 | ~2.3y |

### Avantis sleeves (deeper factor tilts)

| ticker | role |
|---|---|
| **AVUV** | US Small-Cap Value (deeper SCV) |
| **AVDV** | Intl Developed Small-Cap Value |
| **AVES** | Emerging Markets Value |

### Vanguard equivalents (longer history, cap-weighted, NO factor tilt)

| ticker | role | testfolio synth | inception |
|---|---|---|---|
| **VT** | Total World (US + intl) | **VTSIM** | 1970+ in synth, 2008 live |
| **VTI** | US Total Market | **VTISIM** (need to pull) | 1926+ synth |
| **VXUS** | Total Intl ex-US | **VXUSSIM** | 1970+ synth, 2011 live |
| **VEA** | Intl Developed | **VEASIM** | 1970+ synth |
| **VWO** | Emerging Markets | **VWOSIM** | 1994+ synth |
| **VBR** | US Small-Cap Value (proxy for AVUV) | **VBRSIM** | **1926+ synth (99.8y)** |
| **VSS** | Intl Developed Small-Cap | VSSSIM (need to pull) | TBD |

### Long-window strategy: use Vanguard synth, deploy with Avantis

Because AVNM (2.3y) and AVUS/AVDE/AVEM (6.5y) have insufficient history
for robust 40+ year backtest:

* **Backtest** on VTSIM/VTISIM/VXUSSIM/VBRSIM (cap-weighted, 50-100y)
* **Design strategy logic** to be ticker-agnostic (just "US sleeve",
  "intl developed sleeve", "EM sleeve", "small-value sleeve")
* **Deploy** with Avantis tickers (AVUS, AVDE, AVEM, AVUV, AVDV, AVES)
  for the factor tilt premium
* **Assumption**: Avantis adds ~1-2pp/yr over Vanguard cap-weighted
  via factor tilts (Fama-French 1993 + Asness 1997+ via AQR + Avantis
  6.5y live track record)

This assumption needs to be flagged as a calibrated guess until AVNM
has 10+ years of live data.

### Bonds + alternatives (already in cache)

| ticker | role | testfolio synth |
|---|---|---|
| TLT | 20+y Treasury | TLTSIM (need to pull) |
| IEF | 7-10y Treasury | **IEFSIM** ✅ pulled (1962+) |
| BND | Aggregate Bond | **BNDSIM** ✅ pulled (1986+) |
| ZROZ | 25y Zero-coupon | **ZROZSIM** ✅ existing |
| GLD | Gold | **GLDSIM** ✅ existing |

---

## Hypothesis menu (curated, based on academic literature)

These are STARTING points for the loop's Stage 1 hypothesis selection.
The loop may invent variants or find new directions.

### Tier 1: established factor literature

1. **Static return-stack: VTI + VBR + VEA + VWO + bonds + gold**.
   `[risk_parity, ch.5]` extended globally. Direct port of
   `strategy_hunt_loop` iter 035 to global universe.
   Long-window backtest on Vanguard synth (1970+); deploy as
   AVUS + AVUV + AVDE + AVEM + IEF/BND + GLD.

2. **Vol-managed VT + bonds/gold mix**. Direct port of iter 016
   (vol-target overlay) to global universe. `[systematic_trading,
   ch.11]` + Moreira-Muir 2017.

3. **VT vs `VTI+VXUS 60/40` rotation**. When US outperforms by N pp
   on rolling 12m → tilt to VTI; when ex-US outperforms → tilt to
   VXUS. Cross-region momentum. `[stocks_on_the_move, p.21-30]`.

4. **Multi-asset top-K momentum** (port of iter 079 to global).
   Universe: VTI + VEA + VWO + IEF + GLD with BND fallback.
   Deploy: AVUS + AVDE + AVEM + IEF + GLD with BND fallback.

### Tier 2: regional + style rotation

5. **Top-K country rotation** (Faber 2007 style on country ETFs).
   Universe: SPY, EWJ (Japan), EWG (Germany), EZU (Eurozone),
   EWU (UK), MCHI (China), EWZ (Brazil), INDA (India). Pick top-K
   by 12m momentum. (No synth analogs in testfolio — 17y window only.)

6. **Factor sleeve rotation**: rotate across US-large + US-SCV +
   intl-large + intl-SCV by relative momentum. Long-window via
   VVSIM/VBRSIM/VEASIM/VSSSIM.

### Tier 3: explicit currency / hedge layer

7. **VT + currency hedge overlay**. Hedge USD/EUR/JPY exposure when
   carry signal flips. `[risk_parity, ch.5]`.

8. **VT + EM commodity exposure** (DBA, DBC, GLD). Adds inflation
   hedge orthogonal to equity beta.

### Tier 4: multi-stacking (priority, deploy_studies follow-up)

9. **Global return-stacked all-weather**: e.g., 60% RSSB (global eq +
   Treasury via futures, 200% notional) + 30% GDE (S&P + gold) + 10%
   KMLM (managed futures). Total notional ~270% via futures stacking,
   zero margin loan. Tests: does this dominate V_HYBRID+MF in long-window
   Sharpe + MDD?

10. **Synthetic NTSI/NTSE re-evaluation**: Plano C V3.5 rejected based
    on real 2021-2026 data only. Loop should re-test with 32-56y synth.
    Hypothesis: NTSI/NTSE adds value in lost-decade scenarios but loses
    in rate-cycle shocks (2022). If true, **conditional** allocation
    (e.g., NTSI active only when bond term spread > X) may capture
    upside without 2022-style downside.

11. **Custom return-stacked synthesis**: leverage the testfolio-validated
    formula `eq_w × eq + bond_w × bond - cash_w × CASHX` to construct
    arbitrary stacks. E.g., "global 90/60 stack" = 0.90 VTSIM + 0.60
    IEFSIM - 0.50 CASHX (a synth NTSG that doesn't exist as real ETF).
    Test these as sleeves in larger portfolios.

12. **MF + global combination**: deploy_studies showed MF (KMLM/DBMF) is
    "free lunch" for V_HYBRID. Loop should test MF integration in
    global-only portfolios — does adding MF to VT improve Sharpe/MDD as
    much as it did to V_HYBRID?

---

## What's reusable from `strategy_hunt_loop` (CONFIRMED, ready to copy)

**Reuse VERBATIM** (no edits):
- `cross_lib_validator.py` — light cross-lib metric validation
- `rescore_v2.py` — relaxed DSR convention
- `run_loop.sh` — shell orchestrator (only `LOOP_DIR` changes)

**Reuse with MINOR substitution** (parameterize):
- `scoring.py` — swap `BENCHMARKS` dict (VT-based numbers)
- `plot_helper.py` — swap `BENCH_PARQUETS` (add `vt_real` mapping)
- `WINNER_AND_RANKING.md` — swap benchmark table only
- `PROMPT.md` — swap dataset slugs (`spy_real`→`vt_real`, etc.)
- `long_window_validator.py` — copy the unified driver pattern, add
  global strategies

**New for this loop**:
- `BASE_MEMORY.md` — fresh frontmatter, empty iteration log
- `DEAD_ENDS.md` — empty (different mechanism family from US-only)
- `INFRASTRUCTURE.md` — augmented ticker list (Avantis + Vanguard)

---

## Pre-launch checklist (do these before activating loop)

- [x] **Pull VTSIM, VXUSSIM, VEASIM, VWOSIM, VBRSIM, BNDSIM, IEFSIM**
      → done 2026-04-26 (in cache)
- [x] **Pull GDESIM, RSSBSIM, CASHX, KMLMSIM, DBMFSIM**
      → done 2026-04-26 deploy_studies session (in cache)
- [ ] **Pull VTISIM, VSSSIM, EFVSIM, TLTSIM** for completeness
      (`uv run python scripts/testfolio_pull.py VTISIM VSSSIM EFVSIM TLTSIM --refresh-cache`)
- [ ] **Try pulling NTSXSIM, NTSISIM, NTSESIM, RSSTSIM, AVNMSIM, AVESSIM**
      again (failed in 2026-04-26 session — testfolio may add them later;
      meanwhile use synth via formula)
- [ ] **Confirm tickers at Inter Internacional**: user already
      confirmed Inter has all needed tickers (AVUS/AVDE/AVEM/AVUV/AVDV/
      AVES/AVNM/VT/VTI/VXUS/VWO/VEA/VBR/VSS/IEF/BND/TLT/GLD).
- [ ] **Cache live prices via Tiingo** for VT/VTI/VXUS/VEA/VWO/AVUS/
      AVDE/AVEM/AVNM/AVUV/AVDV/AVES (some Avantis tickers may be too
      young for meaningful live history; check inception per ticker).
- [ ] **Compute VT real benchmark numbers** for `scoring.BENCHMARKS_GLOBAL`:
      VT Sharpe / CAGR / MDD on 17y window (2008-06 → 2026-04).
- [ ] **Compute VTSIM bench numbers** for `educational` slot (56y).
- [ ] **Decide benchmark hierarchy**: only-VT, only-VTI+VXUS-blend, or
      both? Affects `winner_conditions_met` definition.
- [ ] **Update PROMPT.md** for this loop: replace "SPY 1x buy-hold"
      bench with "VT 1x buy-hold"; replace dataset slugs (`spy_real`,
      `ndx_real`, `educational`) with new global slugs.
- [ ] **Decide MAX_ITER + ITER_TIMEOUT** for the new run.

---

## Files to create when activating

```
studies/global_factor_tilt_loop/
├── README.md                        ← this file (already exists)
├── PROMPT.md                        ← copy + adapt from strategy_hunt_loop
├── BASE_MEMORY.md                   ← fresh, frontmatter only
├── DEAD_ENDS.md                     ← empty initially
├── WINNER_AND_RANKING.md            ← copy + adapt benchmark table
├── scoring.py                       ← copy + swap BENCHMARKS
├── plot_helper.py                   ← copy + swap BENCH_PARQUETS
├── cross_lib_validator.py           ← copy verbatim
├── long_window_validator.py         ← copy + new strategies
├── rescore_v2.py                    ← copy verbatim
├── run_loop.sh                      ← copy + change LOOP_DIR
├── INFRASTRUCTURE.md                ← copy + augment ticker list
└── iterations/                      ← empty
```

When activating, the first action is: **copy these files from
`studies/strategy_hunt_loop/`, run the pre-launch checklist, then
launch.**

---

## Branching strategy

Suggested: `global-factor-tilt/iter-NNN-NNN` branches off main, same
pattern as `strategy-hunt-relaxed/iter-075-100`. Keep this loop's work
isolated from gold_swing_loop and strategy_hunt_loop.

---

## Why "AVNM will beat VXUS" is a reasonable assumption (justification)

User's intuition: AVNM should beat VXUS over 10-30 years.

Backing literature:
- **Fama, Eugene F., and Kenneth R. French (1993)**, "Common risk
  factors in the returns on stocks and bonds." *Journal of Financial
  Economics* 33(1): 3-56. — small-value premium (~2-4%/yr historically).
- **Asness, Cliff (1997+)** via AQR — value premium ex-US is at least
  as strong as in US.
- **Avantis methodology** (Eduardo Repetto, ex-DFA, 2019) — multi-factor
  scoring across size + value + profitability, integrated daily
  (vs DFA's monthly cuts).

Empirical (2019-2026, 6.5y):
- AVUS vs VTI: AVUS +0.5-1pp/yr (broad with light tilts)
- AVUV vs VBR: AVUV +1-2pp/yr (deeper SCV concentration)
- AVDE vs VEA: AVDE ~+0.8pp/yr
- AVEM vs VWO: AVEM ~+1pp/yr

**Conclusion**: defensible to design strategy on Vanguard synth +
deploy on Avantis with expected +1-2pp/yr factor premium added.
NOT proven — needs 10+y of live AVNM data to confirm. Flagged as
"calibrated assumption" in any deploy doc.

---

*Created 2026-04-25, updated 2026-04-26 with VTSIM/VBRSIM/etc. cache
+ Avantis ticker corrections. Awaiting gold_swing_loop completion
before activation.*

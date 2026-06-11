# PLAN — evolution/: pre-registered hunt for a better RSC core

Date: 2026-06-11 (pre-registered BEFORE any grid run in this folder).
Status: **discovery-only research** (no deployment, no capital/mandate change;
maintenance mode per `docs/investment-mandate.md` §1).

## Charter (user goal, 2026-06-11)

Find a portfolio/adjustment to the current RSC-US core
(`35% GDE / 40% RSST / 25% ZROZ`) with **higher CAGR** while keeping
**MDD ≤ 30%** (daily close, simulated gross curves), and only call it better
if it is *definitively* better — i.e., it survives a pre-registered
robustness gauntlet, not just a full-sample argmax
`[advances_fin_ml, p.208-211]`, `[testing_tuning, p.327-335]`.

This is a user-directed reopening of allocation search. `EVOLUTION.md`
("What Not To Reopen") requires new work to be pre-registered and
mechanism-distinct — this document is that pre-registration. Weight-only
re-tuning of {GDE,RSST,ZROZ} is already known to be curve-fitting
(`discussion/REPORT.md` Q1: best in-cap node 45/25/30 gains only +0.3pp).

## Benchmark anchor (must reproduce before anything runs)

CORE `35/40/25` GDE/RSST/ZROZ, monthly rebalance, window
`2000-01-04..2026-05-21`, discussion engine conventions
(`discussion/engine.py`, rebalance at first trading day of month before that
day's return; metrics per `[systematic_trading, p.185-188]`):

```text
CAGR 12.5241% | MDD -30.7605% | Sharpe 0.84687   (ablations_primary.csv A0)
```

The anchor gate (`e00_anchor_gate.py`) aborts the study if these numbers do
not reproduce within 1e-6.

## Mechanisms under test (each cites its economic rationale)

| ID | Mechanism | Rationale | New sleeves |
|---|---|---|---|
| M1 | More stacked notional per dollar via additional return-stacked sleeves | Capital efficiency / stacking lowly-correlated streams is the documented source of the core's edge `[risk_parity, ch.5]`, `[leverage_for_the_long_run, p.13]` | `RSBTSIM` (bonds+trend, real ETF RSBT), `RSSBSIM` (stocks+bonds, real ETF RSSB) |
| M2 | Direct diversifier sizing (unbundled gold / trend) | Gold and trend are the two crisis sleeves with positive crisis capture (`discussion/tables/crisis_capture.csv`); sizing them independently of the equity wrapper is not expressible in the 3-asset simplex | `GLDSIM`, `KMLMSIM` |
| M3 | Growth-factor tilt | Distinct equity return stream; tested honestly across a window that includes the dot-com bust | `QQQSIM` |
| M4 | Rebalance frequency (same weights) | Sensitivity/robustness test; any gain must be consistent across period offsets or it is rebalance-timing luck (cf. HFEA quarterly +3.2pp read in `discussion/REPORT.md`) `[testing_tuning, p.327-335]` | none |

**Pre-registered exclusions:** BTC/RSSX sleeves (window starts 2010-07, not
comparable on the primary window + survivorship caveat; satellite question
already answered in `discussion/REPORT.md` Q3). RSSY/carry (monthly-native,
already rejected). External margin / negative cash (mandate-disallowed).
Timing/vol-targeting overlays (failed repo gates repeatedly; static only).

## Proxy formulas (financing convention identical to RSST tracking proxy)

```text
MFBLEND  = 0.70*DBMFSIM + 0.30*KMLMSIM
RSBTSIM  = IEFSIM + MFBLEND - (CASHX + 200bps/yr)     # RSBT: 100% core bonds + 100% MF
RSSBSIM  = SPYSIM + IEFSIM  - (CASHX + 200bps/yr)     # RSSB: 100% stocks + 100% bonds (US proxy)
```

Long-window (1988+) diagnostic variants use `KMLMSIM` alone as the MF sleeve
(`RSST88 = SPYSIM + KMLMSIM - (CASHX + 200bps/yr)`, same for `RSBT88`),
mirroring the repo's KMLM-only long-window lens.

## Search space (5% steps, monthly rebalance, primary window)

| Menu | Assets | Nodes |
|---|---|---:|
| A | GDE, RSST, ZROZ, RSBT | 1,771 |
| B | GDE, RSST, ZROZ, GLD | 1,771 |
| C | GDE, RSST, ZROZ, QQQ | 1,771 |
| D | GDE, RSST, ZROZ, KMLM | 1,771 |
| E | GDE, RSST, ZROZ, RSSB | 1,771 |
| F | GDE, RSST, ZROZ, RSBT, GLD | 10,626 |
| G | GDE, RSST, ZROZ, RSBT, QQQ | 10,626 |

n_trials ≈ 30,107 before dedup (3-asset subspace repeats across menus;
deduped by weight signature when aggregating). This count is reported in the
final REPORT — the verdict language must account for it
`[advances_fin_ml, p.208-211]`.

**Round 2 amendment (2026-06-11, pre-registered after Round 1 results, BEFORE
running):** Round 1 produced 0 gauntlet finalists and M4 failed the offset
consistency rule. To close the static space exhaustively (coverage, NOT
threshold adjustment — all criteria below unchanged):

| Menu | Assets | Step | Nodes |
|---|---|---|---:|
| H | GDE, RSST, ZROZ, GLD, KMLM | 5% | 10,626 |
| I | all 8 sleeves | 10% | 19,448 |

If Round 2 also yields no finalist, the verdict is a documented honest FAIL
of the static-allocation route within the MDD ≤ 30% cap.

**Round 3 amendment (2026-06-11, pre-registered after Round 2 = 0 finalists,
BEFORE running):** the one static corner not yet covered as a *grid* is a
leveraged-equity **carrier** (SSO 2x / UPRO 3x, leverage embedded in the
fund, no external margin `[leverage_for_the_long_run, p.13]`) delivering the
equity exposure in fewer dollars, with the freed budget buying *unbundled*
diversifier notional (GLD/KMLM/ZROZ/RSBT). The `discussion/` ablations only
tested 100% SSO/UPRO and ONE fixed DIY-SSO mix — never the simplex. This is
mechanism-distinct from Rounds 1-2 (equity decoupled from the diversifiers
attached inside GDE/RSST). HFEA's documented failure mode (one hedge, 3x)
does not apply a priori to a 4-diversifier ballast `[risk_parity, ch.5]`.

| Menu | Assets | Step | Nodes |
|---|---|---|---:|
| J | SSO, GDE, ZROZ, RSBT | 5% | 1,771 |
| K | SSO, GLD, KMLM, ZROZ | 5% | 1,771 |
| L | SSO, GDE, RSST, ZROZ, RSBT | 5% | 10,626 |
| M | SSO, GLD, KMLM, ZROZ, RSBT | 5% | 10,626 |
| O | UPRO, GLD, KMLM, ZROZ, RSBT | 5% | 10,626 |

QLD is skipped: menu C already showed the QQQ flavor fails the 2000-2008
starts and a 2x wrapper only amplifies that. All criteria, gates and
thresholds remain EXACTLY as pre-registered above. If Round 3 also yields
no finalist, every implementable static expression (1x sleeves, embedded-2x
stacks, 2x/3x LETF carriers) is exhausted and the honest-FAIL verdict is
final for the static route.

**Round 4 amendment (2026-06-11, pre-registered after Round 3 = 0 finalists,
BEFORE running):** last untested static mechanism = **threshold/tolerance-band
rebalancing** (also an explicit Open Blocker in the study `README.md`):
rebalance to target only when any sleeve's weight drifts beyond a relative
band of its target. Mechanism: harvests sleeve momentum/autocorrelation like
low-frequency rebalancing, but risk-triggered instead of calendar-triggered
`[systematic_trading, p.137-148]`. Bands swept: 10%, 15%, 20%, 25%, 33%, 50%
relative; portfolios: CORE, EW, 45/25/30, the two Round-1 near-miss
structures. Verdict rule (mirrors M4): a band only counts as an improvement
if CAGR > monthly AND MDD ≤ 30% AND the same holds for both neighboring band
values (parameter plateau, no band-luck) `[testing_tuning, p.327-335]`.
Also recorded: annual-rebalance variants on the 1988+ window (does the
annual MDD knob hold out-of-window?). If Round 4 yields no qualifying
improvement, the static route is closed with NO further amendments.

**Round 5 amendment (2026-06-11, pre-registered after Round 4 found a
band-mechanism parameter plateau and e06 left `45/25/30 b20` failing ONLY
the G2 weight-neighborhood — via the interpretable ZROZ < 30% boundary):**
sweep the FULL {GDE,RSST,ZROZ} simplex (231 nodes, 5% step) under
tolerance-band rebalancing, bands {15%, 20%, 25%}, through the complete
gauntlet. FINALIST rule (fixed before running): a node is definitively
better only if, at band 20%, it passes G1 (≥7/8 starts vs CORE-monthly),
G2 (all ±5pp neighbors at the SAME band: MDD ≥ −32%, mean CAGR >
CORE-monthly), G3 (n/a for pure-core sleeves; else +50bps), G4 (≥60%
rolling-5y) — AND passes C1∧C2' at bands 15% and 25% too (band plateau,
no band-luck). G5 (1988+) stays a recorded diagnostic. Tier-1 "definitive"
keeps the pre-registered CAGR ≥ CORE + 0.75pp; the honorable tier keeps
CAGR > CORE. Trial accounting continues (693 node-band configs + start
sub-sims). No further rounds after this one regardless of outcome.

## Success criteria (fixed now, before any run)

Screen (full primary window `2000-01-04..2026-05-21`):

- **C1 (hard):** MDD ≥ −30.00% (daily close, gross).
- **C2 (primary):** CAGR ≥ CORE + 0.75pp (≥ 13.27%).
- **C2' (secondary tier):** CAGR > CORE (12.52%).

Gauntlet (run on every node passing C1 ∧ C2'; PASS requires all of G1-G4;
G5 is a recorded diagnostic):

- **G1 start-date:** beats CORE CAGR (same start) in ≥ 7/8 starts
  (2000/2002/.../2014, same dates as `s04_simplex.py`).
- **G2 neighborhood (plateau, not peak):** all one-step (±5pp) neighbors have
  MDD ≥ −32% AND mean neighbor CAGR > CORE `[testing_tuning, p.327-335]`.
- **G3 drag stress:** +50bps/yr extra drag on every sleeve not in
  {GDE,RSST,ZROZ} → still CAGR > CORE.
- **G4 sub-period dominance:** rolling 5y windows (1y step, from the same
  full-sample equity curves): beats CORE rolling CAGR in ≥ 60% of windows.
- **G5 long-window diagnostic (1988+, KMLM-only MF):** record CAGR/MDD vs
  CORE-1988 equivalent; flag if candidate underperforms CORE-1988 CAGR or
  deepens MDD by > 2pp.

**"Definitively better" =** C1 ∧ C2 ∧ G1-G4 pass, with G5 not flagging a
contradiction. C1 ∧ C2' ∧ G1-G4 = "honorable mention" tier only.

M4 (rebalance frequency) verdict rule: a frequency change is only an
improvement if min-across-offsets CAGR still beats monthly AND MDD stays
≤ 30% for all offsets.

## Pipeline

```text
e00_anchor_gate.py   → tables/verification.csv (aborts on mismatch)
e01_grids.py         → tables/grid_<menu>.csv, tables/candidates.csv
e02_gauntlet.py      → tables/gauntlet.csv, tables/finalists.csv
e03_rebalance.py     → tables/rebalance_freq.csv
e04_longwindow.py    → tables/longwindow_1988.csv
REPORT.md            → consolidated verdict
```

Deterministic, no RNG. Reuses `discussion/engine.py` verbatim (import, no
copy); offset-aware rebalancing lives in `evo_engine.py`.

# REPORT — evolution/: can anything beat RSC-US with MDD ≤ 30%?

Date: 2026-06-11. Status: **discovery-only research** (no deployment, no
capital/mandate change; maintenance mode per `docs/investment-mandate.md` §1).
Pre-registration: `PLAN.md` (criteria fixed before any run). Rebuild:
`uv run python studies/return_stacked_core/evolution/make_all.py`.

Charter (user, 2026-06-11): find a portfolio/adjustment to RSC-US
`35% GDE / 40% RSST / 25% ZROZ` with **higher CAGR and MDD ≤ 30%**, calling
it better only if *definitively* better.

---

## Verdict — **honest FAIL: nothing in the static space is definitively better.**

Across **60,181 portfolio trials (46,673 unique)** over 8 implementable
sleeves (GDE, RSST, ZROZ + new RSBT, RSSB, GLD, KMLM, QQQ), plus a
rebalance-frequency study (M4) and a 1988+ long-window diagnostic (G5):

- **408 nodes** pass the screen (MDD ≥ −30%, CAGR > CORE 12.52%) on the
  primary window `2000-01-04..2026-05-21`.
- **Zero** reach the pre-registered "definitively better" bar
  (CAGR ≥ CORE + 0.75pp): the in-cap frontier tops out at **13.17%**
  (+0.65pp).
- **Zero of 408** survive the robustness gauntlet (G1 start-date 1/408,
  G2 neighborhood 190/408, G3 drag 210/408, G4 rolling-5y dominance 1/408 —
  no node passes all four).
- **M4 rebalance frequency:** quarterly/semiannual/annual lift mean CAGR
  +0.1-0.2pp and *reduce* worst MDD, but the minimum across period offsets
  never beats monthly → rebalance-timing luck, not mechanism
  `[testing_tuning, p.327-335]`.
- **G5 (1988+, KMLM-only MF):** every near-miss *loses* to CORE-1988 in CAGR
  (CORE 13.66% vs candidates 12.3-13.2%). The screen-window "gains" were the
  2000s gold decade, not a structural edge.

**Why it fails, structurally:** every in-cap CAGR gain available in this
universe is a gold/trend tilt (GDE 55-60%). Those tilts beat CORE only from
2000-2008 starts; from 2010/2012/2014 starts CORE compounds at 13.6-14.7%
and no in-cap static mix clears that bar 7/8 times (G1) or in ≥60% of
rolling 5y windows (G4). Selecting the full-window argmax anyway would be
textbook selection bias over ~47k trials `[advances_fin_ml, p.208-211]`.
This extends the `discussion/` plateau conclusion to the wider 8-sleeve
universe: **the edge is the stack of decorrelated streams, and the plateau
is already priced — there is no robust free CAGR left within the 30% cap**
`[risk_parity, ch.5]`, `[leverage_for_the_long_run, p.13]`.

---

## The kill matrix (best candidates by family)

Primary window, monthly rebalance, gross. CORE = 12.52% / −30.76% / 0.847.
Gauntlet: G1 = beats CORE CAGR in ≥7/8 starts; G2 = ±5pp neighborhood
plateau; G3 = CAGR > CORE with +50bps drag on non-core sleeves; G4 = beats
CORE in ≥60% of rolling 5y windows.

| Candidate | CAGR | MDD | G1 | G2 | G3 | G4 | Killed by |
|---|---:|---:|:--:|:--:|:--:|:--:|---|
| GDE60/RSST5/ZROZ20/KMLM15 (best in-cap) | 13.17% | −29.76% | 6/8 | ✗ | ✓ | 55% | start dates, rolling |
| GDE60/ZROZ20/RSBT20 | 13.12% | −29.52% | 4/8 | ✗ | ✓ | 50% | start dates, rolling |
| GDE55/RSST10/ZROZ15/KMLM20 (closest) | 12.83% | −28.42% | 6/8 | ✓ | ✓ | 59% | one start, one window |
| GDE60/RSST5/KMLM35 (only G1 pass) | 12.71% | −29.68% | **7/8** | ✗ | ✗ | 45% | no ZROZ ⇒ fragile, drag |
| GDE50/ZROZ20/RSBT15/QQQ15 (only G4 pass) | 12.72% | −29.99% | 6/8 | ✗ | ✓ | **64%** | neighbors breach cap |

All five also **lose to CORE-1988 in CAGR on the 1988+ window**
(`tables/longwindow_1988.csv`) — the G5 diagnostic flags every single one.

## What the hunt did establish (useful, honest residue)

1. **CORE itself violates the user's 30% cap** (−30.76% on 2000+; −32.4% on
   1988+). If MDD ≤ 30% is a *hard* constraint, the honest move is not "more
   CAGR" — it is accepting a small CAGR cost for a deeper-diversified plateau
   member. The cap-respecting plateau members on BOTH windows:

   | Portfolio | 2000+ CAGR/MDD | 1988+ CAGR/MDD | Read |
   |---|---|---|---|
   | CORE 35/40/25 | 12.52% / −30.76% | 13.66% / −32.36% | breaches cap in both |
   | EW 33/33/33 | 12.07% / −26.29% | 13.19% / −27.12% | in-cap both; −0.45pp CAGR |
   | 45/25/30 | 12.84% / −29.68% | 13.22% / −28.09% | in-cap both; CAGR mixed (+0.31pp / −0.44pp); argmax-flavored — treat as plateau member, not "optimum" `[advances_fin_ml, p.208-211]` |

   ZROZ sizing remains the CAGR↔MDD dial (`discussion/REPORT.md` fig 09).

2. **RSBT (bonds+trend, real ETF) is a legitimate implementation diversifier,
   not a CAGR play**: standalone 6.40% / −28.5% vs ZROZ 5.54% / −62.9%;
   swapping ZROZ→RSBT trades convexity for carry at similar portfolio-level
   metrics. Belongs with the CTAP/product-risk refinements in `README.md`,
   on the same evidence tier.

3. **Unbundled QQQ/GLD/KMLM/RSSB sleeves do not displace the stacked core**
   — same conclusion the lineage reached for factor sleeves
   (`EVOLUTION.md` Phase 4): nothing earns a slot the embedded stacks don't
   already provide more efficiently.

4. **Rebalance frequency is a free MDD knob, not a CAGR knob**: annual
   rebalancing keeps CORE-family MDD inside the cap at every offset (e.g.
   CORE worst-offset −29.79%, 45/25/30 worst-offset −28.92%) at
   approximately unchanged mean CAGR — but offset dispersion (±0.3pp) means
   any single-offset CAGR gain is luck `[testing_tuning, p.327-335]`.

## Multiple-testing accounting

| Item | Count |
|---|---:|
| Grid trials (raw / deduped) | 60,181 / 46,673 |
| Frequency-study rows | 65 |
| Long-window rows | 9 |
| Screen survivors (C1 ∧ C2') | 408 |
| Pre-registered "definitive" tier (C2) | 0 |
| Gauntlet finalists | **0** |

With ~47k trials and zero gauntlet survivors, any candidate promoted from
this study would be a selection-bias artifact by construction
`[advances_fin_ml, p.208-211]`, `[testing_tuning, p.327-335]`.

## Files

| File | Contents |
|---|---|
| `PLAN.md` | Pre-registration (mechanisms, menus, criteria, Round 2 amendment) |
| `evo_data.py` / `evo_engine.py` | Sleeve construction + offset-aware engine (reuses `discussion/engine.py`) |
| `e00..e04_*.py`, `make_all.py` | Deterministic pipeline |
| `tables/verification.csv` | Anchor gate (CORE + 45/25/30 reproduce to 1e-6) |
| `tables/grid_[A-I].csv` | Per-menu metrics (all nodes; gitignored ~11 MB, rebuild via `make_all.py --only e01`) |
| `tables/candidates.csv` / `gauntlet.csv` / `finalists.csv` | Screen → gauntlet (finalists is empty, by result) |
| `tables/rebalance_freq.csv` | M4 frequency × offset study |
| `tables/longwindow_1988.csv` | G5 diagnostic |
| `tables/n_trials.txt` | Trial accounting |

Proxy caveat (inherited, repeat in any external claim): MF-proxy sensitivity
is caveat #1 of the discussion package; RSBT/RSSB here are tracking proxies
with the repo's 200bps financing convention, not live-fund backfills.

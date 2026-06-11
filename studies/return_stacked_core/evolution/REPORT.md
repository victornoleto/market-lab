# REPORT — evolution/: can anything beat RSC-US with MDD ≤ 30%?

Date: 2026-06-11. Status: **discovery-only research** (no deployment, no
capital/mandate change; maintenance mode per `docs/investment-mandate.md` §1).
Pre-registration: `PLAN.md` (criteria fixed before any run; five rounds, each
amendment registered before running). Rebuild:
`uv run python studies/return_stacked_core/evolution/make_all.py`.

Charter (user, 2026-06-11): find a portfolio/adjustment to RSC-US
`35% GDE / 40% RSST / 25% ZROZ` (monthly rebalance; 12.52% CAGR / −30.76%
MDD / 0.847 Sharpe on `2000-01-04..2026-05-21`) with **higher CAGR and
MDD ≤ 30%**, calling it better only if *definitively* better.

---

## Verdict

**Under the pre-registered gates: 0 finalists in five mechanism rounds
(95,601 trials, 74,193 unique static portfolios + 723 band/frequency
configs).** Weight re-allocation, new stacked sleeves (RSBT/RSSB), unbundled
diversifiers (GLD/KMLM/QQQ), leveraged carriers (SSO/UPRO) and calendar
frequency all fail robustness — every static CAGR gain inside the cap is a
start-date artifact of the 2000s gold decade
`[advances_fin_ml, p.208-211]`, `[testing_tuning, p.327-335]`.

**The chartered question has exactly one defensible answer, and it is not a
new allocation — it is a rebalancing-rule change:**

### Best candidate found: `45/25/30 GDE/RSST/ZROZ + 20% tolerance bands` — 5 of 6 gates, NOT a validated winner

Rebalance to target only when a sleeve drifts beyond ±20% (relative) of its
target weight, checked daily — risk-triggered momentum harvesting instead of
calendar resets `[systematic_trading, p.137-148]`. Scorecard vs the current
portfolio (CORE 35/40/25 monthly):

| Lens | 45/25/30 b20 | CORE monthly | Δ |
|---|---|---|---|
| 2000+ CAGR | **13.39%** | 12.52% | **+0.87pp** (above the +0.75pp tier-1 bar) |
| 2000+ MDD | **−29.52%** | −30.76% | +1.24pp, **inside the cap** (CORE is not) |
| 2000+ Sharpe | 0.890 | 0.847 | +0.043 |
| 1988+ CAGR (KMLM-only lens) | 13.63% | 13.66% | −0.03pp ≈ tie |
| 1988+ MDD | **−29.16%** | −32.36% | +3.20pp, inside the cap |
| G1 start-dates beaten | **7/8** (2000-2014 biennial) | — | gate pass |
| G4 rolling-5y windows beaten | **73%** | — | gate pass |
| Band plateau (b15/b25 also in-cap & > CORE) | ✓ 13.13% / 13.13% | — | not band-luck |
| G3 drag stress | n/a (uses only the three core funds) | — | trivially pass |
| Turnover | **1.44 rebalances/yr** (38 in 26.4y) | 12/yr | gross comparison is conservative — fewer taxable events |
| **G2 weight-neighborhood** | **✗ FAIL** | — | see below |

**The one failed gate, exactly:** two of its six ±5pp weight neighbors —
`50/25/25` and `45/30/25`, i.e. the ZROZ ≤ 25% direction — breach the −32%
neighbor-MDD floor under bands (−33.6% / −33.0%). The boundary is
interpretable, consistent across bands 15/20/25, and operationally
meaningful: **under tolerance bands, ZROZ < 30% is cap-fragile.** Per the
pre-registered rule (no post-hoc threshold adjustment — same discipline that
re-closed `lrs/` Phase 8 at DSR p = 0.052), the candidate is **not** a
finalist. Anyone acting on it anyway must treat *ZROZ ≥ 30% at target* as a
hard operating rule and accept that the claim rests on a 26-year simulated
window with the study's proxy caveats.

No other (node, band) combination does better: the full 231-node simplex ×
bands {15, 20, 25} gauntlet (`tables/band_simplex.csv`) yields 6 screen
passes, of which only `40/25/35` and `45/20/35` have safe neighborhoods —
and those fail G1 (2/8, 4/8): deeper ZROZ buys neighborhood safety but gives
the CAGR edge back. The cap, the neighborhood floor and the start-date gate
form a three-way squeeze with exactly zero joint solutions.

---

## Round-by-round (all pre-registered in PLAN.md)

| Round | Mechanism | Trials | Result |
|---|---|---:|---|
| 1 | New stacked sleeves (RSBT/RSSB) + unbundled GLD/KMLM/QQQ, menus A-G | 30,107 | 271 screen / **0 gauntlet** |
| 2 | Coverage closure: GLD+KMLM menu, 8-asset 10%-step universe | +30,074 | 408 screen / **0 gauntlet** |
| 3 | Leveraged carriers SSO/UPRO + decoupled diversifiers, menus J-O | +35,420 | carriers **dominated** (best in-cap nodes are the SSO/UPRO=0 corners); 413 screen / **0 gauntlet** |
| 4 | Calendar frequency (M4) + tolerance bands (e05) | 95 configs | calendar = offset luck; **bands = real parameter plateau** (+0.2-0.7pp on 4 of 5 structures, 16/30 plateau improvements) |
| 5 | Full simplex × bands {15/20/25} gauntlet (e07) | 693 configs | 6 screen / **0 finalists**; `45/25/30 b20` fails only G2 |

Supporting facts preserved:

- **G1 bar (CORE-monthly CAGR per start):** 12.5% (2000) → 13.6% (2002-2006)
  → 14.7% (2010, 2014). The gold-tilt static candidates beat the early
  starts and lose the late ones; band candidates are the only family that
  cleared 7/8.
- **1988+ diagnostic:** every Round 1-3 near-miss loses to CORE-1988
  (13.66%) by 0.4-1.4pp. The band candidate ties it. `tables/longwindow_1988.csv`.
- **Annual rebalance = MDD knob, not CAGR knob:** CORE annual keeps MDD
  in-cap at all 12 offsets on 2000+ (worst −29.79%) but NOT on 1988+
  (worst −31.81%); min-across-offsets CAGR never beats monthly.
  `tables/rebalance_freq.csv`, `tables/annual_1988.csv`.
- **EW 33/33/33 under wide bands** is the defensive standout: b50 = 12.94% /
  −24.69% (2000+) and 14.24% / −24.73% (1988+!) — but G1 2/8 on 2000+
  (it loses the gold-decade starts to CORE). For a *drawdown-first* mandate
  it is the most interesting row in the study. `tables/bands.csv`.
- **RSBT (real ETF, bonds+trend)**: standalone 6.40% / −28.5% vs ZROZ
  5.54% / −62.9%; legit implementation diversifier (CTAP tier), not a CAGR
  play `[risk_parity, ch.5]`.

## Multiple-testing accounting

| Item | Count |
|---|---:|
| Static grid trials (raw / deduped) | 95,601 / 74,193 |
| Band + frequency configs (e03/e05/e06/e07) | 723 |
| Screen survivors (static C1 ∧ C2') | 413 |
| Pre-registered tier-1 (CAGR ≥ +0.75pp), static | 0 |
| Gauntlet finalists (all rounds) | **0** |
| Best candidate gate score | `45/25/30 b20`: 5/6 (G2 fail, G5 = 3bps tie diagnostic) |

The verdict language is calibrated to this count: with ~75k trials, only the
gauntlet separates signal from selection bias, and nothing passed it whole
`[advances_fin_ml, p.208-211]`.

## Files

| File | Contents |
|---|---|
| `PLAN.md` | Pre-registration, Rounds 1-5 amendments (each before running) |
| `evo_data.py` / `evo_engine.py` | Sleeve construction + offset/band engines (reuses `discussion/engine.py`) |
| `e00..e07_*.py`, `make_all.py` | Deterministic pipeline |
| `tables/verification.csv` | Anchor gate (CORE + 45/25/30 reproduce to 1e-6) |
| `tables/grid_[A-O].csv` | Per-menu static metrics (gitignored ~20 MB, rebuild via `make_all.py --only e01`) |
| `tables/candidates.csv` / `gauntlet.csv` / `finalists.csv` | Static screen → gauntlet (finalists empty) |
| `tables/rebalance_freq.csv` / `bands.csv` / `bands_verdicts.csv` / `annual_1988.csv` | Round 4 |
| `tables/band_gauntlet.csv` / `band_simplex.csv` | Round 5 (the headline tables) |
| `tables/longwindow_1988.csv` | G5 diagnostic |
| `tables/n_trials.txt` | Trial accounting |

Caveats (inherited, repeat in any external claim): MF-proxy sensitivity is
caveat #1 of the discussion package; RSBT/RSSB are tracking proxies with the
repo's 200bps financing convention; all numbers simulated, gross of
taxes/fees (the band candidate's 8× lower turnover makes the gross
comparison conservative in its favor); band triggers were evaluated daily
with the same reset-before-return convention as the calendar engine.

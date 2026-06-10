# Phase 7C — Macro Growth-Trend-Timing Gate (UNRATE) (PRE-REGISTRATION)

> Status: research-only / diagnostic. Nothing here authorizes deployment, paper
> trading or a mandate change. Mandate §1 (maintenance mode) unchanged.
> **Round order note:** Phase 7 round runs 7A → 7B → 7C → 7D → 7E → (7F) → 8.

## Citation EXCEPTION (user-approved 2026-06-09)

The specific rule below (`UNRATE > SMA12m(UNRATE)` as the recession-risk
regime) comes from the **Philosophical Economics "Growth-Trend Timing" essay
(blog, 2016)** — it has no source among the repository's 33 books. The user
explicitly approved running it as a documented exception to CLAUDE.md Rule 2.
The mechanism *family* (only pay the trend-timing cost when recession risk is
elevated) anchors on the paper's own regime evidence: the S&P 500 trades below
its 200-day MA **68.2% of the time during recessions vs 19.4% during
expansions** `[leverage_for_the_long_run, p.9]` — the contrapositive reading is
that outside recessions the MA gate mostly pays whipsaw/timing cost for
protection that is rarely needed.

## Question

Phase 6C showed 90.9% of the binding walk-forward failures happen in BULL
windows — the structural cost of timing. This phase tests the Growth-Trend
Timing composition: **apply the trend rule only when the macro regime says
recession risk; otherwise hold the target-leverage sleeve unconditionally.**
Hypothesis: removing the timing cost in expansions lifts walk-forward
consistency while keeping the deep-crisis protection (where the LRS edge is
100%, per 6C).

## Mechanism (one family — macro override of the regime gate)

- Macro state: `macro_risk_t = UNRATE_m > SMA12(UNRATE)_m`, computed on the
  monthly FRED series, aligned to trading days and lagged
  **25 trading days** from the first-of-month reference stamp (BLS publishes
  the Employment Situation on the first Friday of the FOLLOWING month ≈ 23 td
  after the stamp; +2 td buffer). NOTE: the round plan sketched 10 td; that
  would leak ~3 weeks of unpublished information, so the committed value is
  25 td — the more conservative, honest-alignment choice
  `[advances_fin_ml, p.31-34]` (loader: `macro_data_loader.UNRATE_LAG_TD`).
- Warmup / pre-1949 NaN → `macro_risk = True` (falls back to the full base
  rule, never to unconditional leverage).
- Two pre-registered override scopes:
  - **(a) trend_only:** `signal = macro_risk ? (SMA200 & vol_gate) : vol_gate`
    (the vol throttle never sleeps; only the trend gate does).
  - **(b) trend_and_vol:** `signal = macro_risk ? (SMA200 & vol_gate) : True`
    (full unconditional target leverage in expansions).
- Everything else verbatim from the Phase 2/4 bases: ladder weights, risk-off
  sleeves, weekly cadence, lag-through-CASHX, `AnnualDarfEngine`.
- Data: `data/external/macro/unrate_monthly.parquet`
  (`scripts/data_sprint/ingest_unrate_fred.py`, FRED no-auth CSV, 1948+).
  **Vintage limitation (recorded, not blocking):** FRED serves the latest
  revised series; a point-in-time ALFRED check is future work.

## Pre-registered grid — 72 rows (+72 to the n_trials ledger → 4149 + 72 = 4221)

| Axis | Values | Anchor |
|---|---|---|
| Bases | the 6 Phase 4 bases (3 SPY + 3 QQQ, geometry verbatim) | Phase 2/4 |
| Override scope | `trend_only`, `trend_and_vol` | the two readings of "turn timing off in expansions" |
| lag | `0..5` | restart convention |

Plus 6 non-trial baseline rows (binary bases at committed lags, recomputed).

**Built-in sanity (non-trial):** forcing `macro_risk = True` everywhere must
reproduce the binary base byte-for-byte (max abs diff reported).

## Pre-registered screen (per branch, on the best trial row by WF beats, tie-break Calmar)

1. WF beat count **strictly greater** than the best binary baseline of the
   branch (SPY > 12/17, QQQ > 7/11), on the exact Phase 4 splits.
2. After-tax CAGR ≥ branch headline − 1pp.
3. MDD ≥ −50% (round constraint). Known risk reported per window: non-recession
   crashes (1987-style) are held at full leverage under scope (b).

All three → diagnostic SUCCESS (feeds 7F). Any miss → honest FAIL. No
deployment, no paper-trade label, no mandate change `[advances_fin_ml,
p.208-211]`.

## Outputs

`lrs/results/phase07c_macro_gtt_gate.csv`, `REPORT.md`, plots (macro regime
shading + equity, equity/DD vs binary headline, WF beats comparison, frontier),
`tests/test_lrs_phase07c.py`.

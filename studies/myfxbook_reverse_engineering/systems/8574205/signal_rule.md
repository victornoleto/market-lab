---
system_id: 8574205
family: UNCATEGORIZED
confidence: 0.28
generated: 2026-05-02
rule:
  entry_window_utc: ["16:00", "20:00"]   # NY afternoon session — accounts for 54% of all entries
  pairs: [EURJPY, USDJPY, EURUSD, NZDUSD, AUDUSD]
  direction: |
    # CAUTION: direction edge is indistinguishable from noise.
    # Best univariate rule (rank 3, match_rate_cv=0.549) barely exceeds baseline (0.536).
    # Grid architecture implied by system name "MartiGrid" and fixed lot structure.
    # Price-grid systems place BUY and SELL orders at fixed price intervals
    # without conditioning on market direction — direction is determined by
    # grid level activation, not by a market signal.
    #
    # Best available approximation using candidates.json thresholds:
    BUY if bb_pos_20_2_H1 > -0.7377
    SELL otherwise
    # NOTE: this rule captures only 0.8 coverage and achieves match_rate_cv=0.549,
    # only 1.3pp above the 53.6% always-buy baseline. The replicator should treat
    # this as a near-random direction signal. Stage 3 must test against pure grid
    # (buy at even grid levels, sell at odd grid levels) as the true entry logic.
  exit:
    max_holding_hours: 1520   # p95 hold; p50=24h suggests bimodal distribution
    take_profit_pips: null    # no TP detected; exit is manual or time-based
    stop_loss_pips: null      # no SL detected; max hold 11880h=495 days observed
  sizing: fixed_lot_0.02     # p50=p95=p99=max=0.02 — perfectly fixed, no martingale scaling
citations:
  - "[advances_fin_ml, p.160-161] — MDI is 'in-bag feature importance measure based on weighted average impurity reduction across all splits; fast but biased toward high-cardinality features' — confirms ret_10_H4 and bb_pos_20_2_H4 at top of tree are MDI-style importances that may overstate true predictive value for this system."
  - "[algo_trading_chan, p.5-6, ch.1] — 'There is a general approach to trading strategy construction that can minimize data-snooping bias: make the model as simple as possible, with as few parameters as possible' — the grid architecture of MartiGrid is consistent with this principle; a fixed price-grid requires zero direction parameters, which also means conventional signal-rule mining cannot reconstruct it."
risk_flags:
  - "system name 'MartiGrid' explicitly signals grid+martingale hybrid despite k1_pass=PASS on lot-size check — grid entries at fixed intervals are indistinguishable from martingale by lot-step ratio alone"
  - "max_hold_hours=11880 (495 days) — open drawdown risk over multi-year horizon is not captured by any intraday session model"
  - "broker ForexMart is a small, poorly-regulated broker (not tier-1); confidence penalty applied (-0.10)"
  - "match_rate_cv of top candidate (0.549) is only 1.3pp above always-buy baseline (0.536) — direction has no statistically meaningful learnable structure; all direction rules should be treated as noise"
  - "NZDUSD buy_pct=72% suggests possible directional bias for that pair, but sample may be confounded by trend regime during 2021-2026"
  - "blackout 2021-2026 (5-year window) — track record starts 2021-09-03; edge persistence post-2026 unknown"
  - "p50 hold = 24h and p95 hold = 1520h are inconsistent with any session-based family — bimodal hold distribution suggests winners close quickly while losers are held indefinitely (grid behaviour)"
---

# Decoded signal — Happy MartiGrid (Multipairs) FM - REAL (id 8574205)

## Family rationale

After systematic review of all five classifiable families, this system does not fit any named
taxonomy entry with confidence sufficient to assign a family above UNCATEGORIZED.

The entry hour concentration at 16:00-19:00 UTC (NY afternoon, accounting for the top four
entry slots) is compatible with OVERLAP_NY_LONDON_RANGE (12-16 UTC) or NY_SESSION_REVERSAL
(12-16 UTC) on the timing dimension alone. However, two disqualifying factors prevent either
assignment:

First, the direction statistics. Direction by hour shows buy% of 50-56% across all hours —
essentially coin-flip. The best candidate rule (rank 3: `bb_pos_20_2_H1 > -0.7377 => Buy`,
match_rate_cv=0.549) barely exceeds the baseline always-buy rate of 53.6% (match_rate_cv=0.536).
For OVERLAP_NY_LONDON_RANGE or NY_SESSION_REVERSAL, we would expect a miner to find a rule
with match_rate_cv > 0.60 anchored to session position or Asian range sign. No such rule
exists in candidates.json. The RIPPER ruleset (rank 8) covers 100% of the data but achieves
match_rate_cv=0.479 — below random — with high fold variance (std=0.052). This is a textbook
sign of a system where direction is not determined by market condition features at all.

Second, the hold-time distribution. The p50 hold of 24 hours and p95 hold of 1520 hours
(63 days) are irreconcilable with any session-based model. All named session families in
the taxonomy require exits within 1-6 hours. A p95 of 1520 hours means 5% of trades are
held more than 63 days, and the observed maximum is 11880 hours (495 days). Session families
assume time-boxed exits by definition.

The system name "Happy MartiGrid" (Multipairs) makes the architecture explicit: this is a
price-grid system where BUY and SELL limit orders are placed at fixed price intervals around
a reference level, regardless of market direction. The k1_pass=PASS on the martingale lot-size
check is expected for grid systems because lot sizes remain constant per entry (0.02 throughout
the entire track record: p50=p95=p99=max=0.02). A grid strategy shows no lot escalation per
position; instead it accumulates multiple fixed-lot positions at different grid levels. This
is structurally undetectable by the Stage 1 martingale check, which only tests lot-step ratio.

The pair universe (EURJPY dominant at 38.8%, USDJPY 29.1%, EURUSD 13.9%, NZDUSD 9.2%,
AUDUSD 9.0%) is also atypical. JPY-crosses (67.9% of trades) are chosen for their high
intraday volatility and low spread relative to pip size — standard grid system pair selection
criteria. This pair universe does not match any named session family (LATE_NY_BREAKOUT uses
EUR/GBP/CHF majors; London families use GBPUSD-centric pairs).

Alternatives considered and rejected:
- `LATE_NY_BREAKOUT`: entry window 16-19 UTC partially overlaps but pairs universe incompatible
  and exit timing disqualifies (p50=24h vs required 1-3h).
- `OVERLAP_NY_LONDON_RANGE`: timing compatible but direction near-random and hold times too long.
- `NY_SESSION_REVERSAL`: timing adjacent but no reversal signal detectable and hold too long.
- `FACTOR_SCALPING`: p50=24h hold is far too long; scalping requires < 30 min.
- `MARTINGALE_GRID`: k1_pass=PASS disqualifies by Stage 1 sanity, but the name and grid
  structure are consistent with this family conceptually. The lot-step ratio check is
  insufficient to detect grid strategies where each grid level is a fresh fixed-lot entry.

## Rule derivation

The direction rule presented in the YAML uses the single highest-quality univariate candidate
from candidates.json: rank 3, `bb_pos_20_2_H1 > -0.7377 => Buy`, with match_rate_cv=0.549,
p_value_corrected=2.04e-07. The statistical significance (despite being corrected across 560
tests) must be interpreted cautiously. Aronson [evidence_based_ta, p.287-288] warns that "the
observed performance of the best of N rules systematically overestimates expected performance"
and that data-mining bias grows with the number of rules tested. With 560 tests and a tiny
effect size (1.3pp above baseline), this result could plausibly be a data-mining artifact.

The threshold -0.7377 for bb_pos_20_2_H1 (Bollinger Band position on H1 bars, 20-period,
2 std-dev) was taken verbatim from candidates.json rank 3. This threshold was NOT invented —
it is the exact value found by the univariate miner for the training set. Similarly, ema_dist_20_H1
threshold -1.738 (rank 4) and ret_10_H1 threshold -0.005032 (rank 5) all share the same
match_rate_cv (~0.547-0.549) and coverage (0.80), suggesting they are near-collinear measures
of the same underlying condition: "price is not too far below the mean" = broad buy bias.

The decision tree (rank 2, match_rate_cv=0.515, below the 0.536 baseline) uses ret_10_H4 as
primary split with importance 0.25, followed by bb_pos_20_2_H4 (0.24). The MDI-style importances
from the tree are influenced by correlation among features. As López de Prado [advances_fin_ml,
p.160-161] notes, MDI is "biased toward high-cardinality features" and trees can misallocate
importance when features are correlated. Since the tree performs below baseline (0.515 < 0.536),
its feature rankings should not be used to infer true predictive power.

The exit parameters are derived from the fingerprint hold-time percentiles. No TP or SL is
present (all exits are manual_or_time with no systematic TP/SL pattern). The max_holding_hours
was set to the p95 value (1520h) as a conservative approximation; the replicator should test
both the p50 (24h) and p95 (1520h) variants to identify whether the profitable trades close
early or late.

## Confidence breakdown

- Family identification: 0.35 — UNCATEGORIZED is highly likely given the grid name + fixed
  lot + near-random direction + long hold times. The 0.35 (not lower) reflects that entry
  timing at 16-19 UTC is real and not noise (top 4 hours account for 1154/3994 = 29% of trades,
  concentrated from a 24-hour uniform baseline of 4.2% per hour).
- Direction rule: 0.20 — match_rate_cv=0.549 only 1.3pp above always-buy baseline; likely
  a data-mining artifact from 560 tests. No rule in candidates.json is actionable with
  confidence for direction prediction in the replicator.
- Exit logic: 0.25 — p50=24h is observed but the bimodal distribution (winners close fast,
  losers held years) cannot be captured by a single max_holding_hours parameter.
- Overall: 0.28 = weighted mean (0.35×0.40 + 0.20×0.35 + 0.25×0.25)

## Open questions (for Stage 3 + posteriores)

- **Grid spacing recovery**: Stage 3 should test whether trades cluster at fixed pip intervals
  around a reference price (e.g., every 20/50/100 pips on EURJPY). If confirmed, the true
  entry logic is "place limit order at grid level N" rather than any market-condition feature.
- **Bimodal hold distribution**: Stage 3 should separate the p50=24h winners from the
  multi-day/week losers and analyze their direction separately — the strategy may have a
  quick-win/slow-loss asymmetry typical of grid systems.
- **NZDUSD directional bias**: buy_pct=72% on NZDUSD is an outlier vs. all other pairs
  (~48-56%). Stage 3 should test whether this is a systematic long bias or a regime artifact
  from the 2021-2024 NZDUSD depreciation trend that created persistent underwater grid buys.
- **ForexMart broker risk**: Execution quality and swap conditions at ForexMart may differ
  substantially from tier-1 brokers. Grid strategies are highly sensitive to swap costs on
  multi-day/week holds; Stage 3 should model swap costs explicitly.
- **k1_pass reliability for grids**: The Stage 1 martingale check tested lot-step ratio.
  A grid that adds positions at every N pips with fixed lots shows ratio=1.0 and passes.
  Stage 3 should add a secondary check: do entries cluster at fixed price intervals per pair?
- **Entry timing significance**: The 16-19 UTC concentration may reflect a scheduled EA
  run time (e.g., MT4 EA executes at London/NY session checks). Stage 3 should test whether
  the timing is truly predictive or simply reflects when the EA evaluates grid levels.
- **Pair universe rationale**: JPY-cross dominance (67.9% of trades) is atypical for session
  families. Stage 3 should test whether EURJPY/USDJPY volatility clustering at 16-19 UTC
  (US data releases at 12:30-14:00 UTC + Tokyo late-session) explains the entry timing.

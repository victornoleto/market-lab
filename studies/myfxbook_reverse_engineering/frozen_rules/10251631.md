---
system_id: 10251631
family: UNCATEGORIZED
confidence: 0.32
generated: 2026-05-02
reason_code: taxonomy_gap
candidate_new_family: ASIAN_PRELONDON_GOLD_MR_H4
prev_label: FACTOR_SCALPING
prev_source: signal_rule.md (Sonnet baseline 2026-05-02)
reclass: true
rule:
  entry_window_utc: ["01:00", "06:00"]    # 01-06 UTC = 333/461 trades (~84%); peak 03:00 (115)
  pairs: [XAUUSD]                          # gold-only — vendor name "Happy Gold FM"
  direction: |
    # Strict v3 rule. Direction signal is WEAK (tree CV=0.531 vs 0.503 baseline);
    # use only the rules with direct empirical support from candidates.json.
    #
    # Primary anchor (rank 8 univariate, the ONLY rule passing Bonferroni
    # correction over n_tests=516 with p_corr=4.77e-04, match_rate_cv=0.612,
    # coverage=0.538):
    #   close_vs_session_open_H4 > -1.0  =>  SELL
    #
    # Tree refinement (rank 1, max_depth=4, top feat importance
    # close_vs_session_open_H4=0.37 — same dominant feature as univariate):
    #   close_vs_session_open_H4 <= -0.50 AND bb_pos_20_2_M15 <= 0.05  =>  BUY
    #   close_vs_session_open_H4 <= -0.50 AND bb_pos_20_2_M15  > 0.05  =>  SELL
    #
    # Combined executable rule (replicator literal):
    BUY  if (close_vs_session_open_H4 <= -0.50) AND (bb_pos_20_2_M15 <= 0.05)
    SELL if (close_vs_session_open_H4 <= -0.50) AND (bb_pos_20_2_M15  > 0.05)
    SELL if (close_vs_session_open_H4 >  -0.50)
    NONE otherwise
    # Topology = H4 mean-reversion fade vs session open: when H4 close has NOT
    # collapsed >= 0.5 std below the session open => fade upward => SELL; when
    # H4 has dropped sharply (<= -0.50) AND M15 BB position is at/below the
    # midpoint => BUY (catch the rebound). This is a coherent MR signature
    # but does not match any closed-enum family (gold only, Asian-pre-London
    # window, H4-driven). See Family rationale.
  exit:
    max_holding_hours: 14                 # post-R4 fingerprint: hold p50=0.15h, p95=13.62h
    take_profit_pips: null                # exit_kind = manual_or_time (no discrete TP/SL)
    stop_loss_pips: null
  sizing: fixed_lot_X                     # lot p50=1929 oz, p95/p50=1.22, no martingale (steps=0)
citations:
  - "[evidence_based_ta, p.281] — 'NEVER use single-rule back test p-values to evaluate the best rule from a data-mining run. Only tests that incorporate data-mining bias are valid — WRC or MCP.' Only rank-8 close_vs_session_open_H4 survives Bonferroni (p_corr=0.000477 over 516 tests); other univariates have p_corr>=0.07 and are not statistically distinguishable from chance."
  - "[advances_fin_ml, ch.5] — feature importance interpretation (MDA): close_vs_session_open_H4 dominates the tree at importance 0.37 (more than 2x the next feature ret_10_M1=0.15), making it the unique anchor for the direction rule. The remaining features (bb_pos_20_2_H4=0.13, bb_pos_20_2_M15=0.13, atr_ratio_H4=0.12) are roughly co-equal — classic sign of a single weak signal padded by noise."
  - "[algo_trading_chan, p.5-6] — 'simple, linear models exploiting identifiable market inefficiencies are superior to complex nonlinear models, because complexity invites data-snooping bias while linearity yields parsimony and interpretability.' The depth-4 tree achieves only 0.531 CV accuracy vs 0.503 baseline — confirming Chan's warning that without an identifiable inefficiency the added depth captures noise. Used to justify low confidence rather than forcing a richer family."
  - "[algo_trading_chan, p.41-48, ch.2] — H4 mean-reversion topology: 'a price series whose variance grows slower than a geometric random walk... prerequisite for mean-reversion trading'. The tree's primary split (fade UP when H4 has not declined; BUY when H4 has dropped sharply) is the textbook structure of an Ornstein-Uhlenbeck-style fade vs session-anchored mean."
risk_flags:
  - "taxonomy_gap — coherent MR signature on XAUUSD in Asian/pre-London window does not map to any v3 enum family (LATE_NY_BREAKOUT/LONDON_*/NY_*/OVERLAP_* are FX-major-defined; H1_MOMENTUM_GOLD requires H1 momentum + tree dir_acc>0.7, NEITHER satisfied here). Proposed candidate_new_family=ASIAN_PRELONDON_GOLD_MR_H4."
  - "direction_signal_weak — best tree CV=0.531 (vs 0.503 baseline, std=0.056, fold range 0.424-0.576). Best univariate match_rate_cv=0.612 at coverage 0.538. System is near-random in direction; replicator backtest may diverge significantly from vendor track."
  - "h1_momentum_gold_REJECTED — explicitly considered. 6541963 (the H1_MOMENTUM_GOLD anchor) has tree dominant feature ret_10_H1=0.74, tree CV=0.844, NY-session entry (15-17 UTC), p50 hold=0.00h. This system has H4 close_vs_session_open dominant (0.37, NOT an H1 momentum feature), tree CV=0.531, Asian/pre-London entry (01-06 UTC), p50 hold=0.15h. Different topology, different timeframe, different session — NOT the same family."
  - "factor_scalping_REJECTED — Sonnet baseline label rejected per taxonomy review_gate (Family.FACTOR_SCALPING: '6/6 systems pré-Opus reclassificados'). FACTOR_SCALPING criteria require 'durations < 30min' — fingerprint p95=13.62h violates this. Single-instrument + intraday + flat-sizing alone is insufficient signature; without an identified factor edge (vol-targeting / pair-trading), the label is bucket-de-fuga per v3 contract."
  - "broker_forexmart_folklore — ForexMart is a Tier-3 offshore broker (CySEC IBC). Confidence reduced 0.05 per workflow rule; vendor selection bias plausible."
  - "drawdown_33_74pct — max DD on real account with 1:500 leverage and frequent withdrawals (-$11k of $14k deposits) is structurally inconsistent with the flat-lot sizing profile (p95/p50=1.22). Possible: variable sizing in periods not captured by p50/p95 ratio, or a single tail event during the active window 2022-03 to 2024-08."
  - "blackout_post_2024_08 — vendor stopped posting after 2024-08-07; edge persistence in 2024-2026 regime unknown."
---

# Decoded signal — Happy Gold FM - REAL (GN) (id 10251631)

## Family rationale

This system trades XAUUSD exclusively (461/461 trades) on a real ForexMart account at 1:500 leverage. The closed v3 enum offers no fitting family:

1. **All FX-session families excluded** (LATE_NY_BREAKOUT, LONDON_OPEN_MOMENTUM, LONDON_OPEN_MR, NY_SESSION_REVERSAL, OVERLAP_NY_LONDON_RANGE, OVERNIGHT_GAP_FADE) — these are defined for FX majors with USD/EUR pricing dynamics; gold has different liquidity windows (LBMA fix, COMEX RTH) and is driven by different macro flows. Mapping any of them onto XAUUSD would be a category error.

2. **MARTINGALE_GRID excluded** — sanity passes (steps=0, max_streak=0, lot p95/p50=1.22).

3. **FACTOR_SCALPING excluded** — explicitly per the v3 taxonomy `review_gate` ("6/6 systems pré-Opus reclassificados") and per its criteria ("durations < 30min"): post-R4 fingerprint shows hold p95=13.62h, well beyond a scalping window. The Sonnet baseline labelled this FACTOR_SCALPING, but that reads as a bucket-de-fuga (single-instrument + intraday + flat-sizing — which is true but does not constitute a *factor* edge). The tree CV of 0.531 vs 0.503 baseline confirms there is no identified factor edge to anchor the label.

4. **H1_MOMENTUM_GOLD (provisional) explicitly rejected.** This was the most tempting fit (gold + intraday). Side-by-side comparison with the H1_MOMENTUM_GOLD anchor system 6541963 (Happy Gold Tickmill M15):

   | Feature | 10251631 (this) | 6541963 (anchor) |
   |---|---|---|
   | Top tree feature | `close_vs_session_open_H4` (0.37) | `ret_10_H1` (0.74) |
   | Tree CV accuracy | 0.531 | 0.844 |
   | Entry concentration | 01-06 UTC (Asian/pre-London) | 15-17 UTC (NY) |
   | Hold p50 / p95 | 0.15h / 13.62h | 0.00h / 0.29h |
   | Direction balance (Buy %) | 50.3% (symmetric) | 52.1% (slight long bias) |
   | Univariate top | `close_vs_session_open_H4 > -1 ⇒ Sell` (MR) | `ret_10_H1 > -0.001 ⇒ Buy` (momentum) |

   The provisional `H1_MOMENTUM_GOLD` criteria ("Gold/XAU + entry-on-H1-momentum + tree balanced + dir_acc>0.7") fail on three of four conditions: the dominant feature is H4-not-H1; topology is mean-reversion-not-momentum; and direction accuracy 0.531 is far below the 0.7 threshold. Only "Gold/XAU" matches.

5. **No remaining provisional fits.** NEWS_RELEASE_MOMENTUM requires a name-flag NEWS/HF News and clock-anchored event windows — no evidence here. SWING_TREND_MOMENTUM requires median hold >72h and H4/D1 trend dominance — fails (p50=0.15h, top hour 03 UTC concentrates 25% of trades).

The empirical signature *is* coherent — H4 mean-reversion fade vs session open, Asian/pre-London window, gold only — but it is genuinely outside the closed enum. Per v3 contract: `family=UNCATEGORIZED + reason_code=taxonomy_gap + candidate_new_family=ASIAN_PRELONDON_GOLD_MR_H4`. If a 2nd system in 5R-1 (or later runs) carries the same signature, this candidate is upgrade-eligible.

## Rule derivation

**Entry window.** Direct read of fingerprint timing: hours 01-06 UTC = 115+80+52+50+36 = 333 trades = 72.2% of 461; if 02 and 06 are stretched the band covers ~84%. The 5-min resolution shows no single clock-on-the-hour spike (top 04:00=20, 01:00=19, 03:05=16, 03:00=15) — suggesting a condition-triggered entry, not a cron-anchored one.

**Direction signal.** Two corroborating sources both point at `close_vs_session_open_H4` as the dominant feature:

- **Univariate (rank 8, the ONLY survivor of Bonferroni n_tests=516):** `close_vs_session_open_H4 > -1.0 ⇒ Sell`, match_rate_cv=0.612, coverage=0.538, p_corr=4.77e-04.
- **Tree (rank 1):** feature importance 0.37 on `close_vs_session_open_H4`, more than 2x the next feature (`ret_10_M1`=0.15). Primary split at -0.50 produces an MR-fade topology: when H4 has not collapsed below session open, SELL; when H4 has collapsed AND M15 BB pos is at/below the midpoint, BUY (rebound).

**Composite rule.** I unified the rank-1 tree branches with the rank-8 anchor as follows:

```
BUY  if close_vs_session_open_H4 <= -0.50 AND bb_pos_20_2_M15 <= 0.05
SELL if close_vs_session_open_H4 <= -0.50 AND bb_pos_20_2_M15  > 0.05
SELL if close_vs_session_open_H4 >  -0.50
NONE otherwise
```

The `>=-0.50` SELL branch absorbs the rank-8 univariate's `>-1.0 SELL` (every >-0.50 trade also satisfies >-1.0); the `<=-0.50` branches add the BB-position discrimination from the tree.

**Thresholds — all literal from candidates.json (rank 1 tree splits):**
- `close_vs_session_open_H4 <= -0.50` (tree root split)
- `bb_pos_20_2_M15 <= 0.05` (tree depth-2 split)

I deliberately did NOT include the deeper tree branches (`bb_pos_20_2_H4`, `ret_10_M1`, `atr_ratio_M1/H4`) because:
- they collapse to the same class on both sides of their splits in the tree dump (line 76-78, 84-88), so they add no discrimination
- including features whose splits don't change the class label would mislead the replicator

**Exit logic.** Post-R4 fingerprint: `hold p50/p95/max = 0.15 / 13.62 / 160.87` hours. Set `max_holding_hours: 14` (rounded p95 — 95% of trades close inside this window). The 160.87h max is a long-tail outlier (likely weekend bridge or stop-out delay). `exit_kind=manual_or_time` (no discrete TP/SL detected by Stage 1).

**Sizing.** lot p50=1929 oz, p95=2358, p95/p50=1.22, steps=0. Flat-lot with mild variation (likely small equity-proportional adjustments). Conservative label `fixed_lot_X`.

## Confidence breakdown

- **Family identification: 0.40** — Decisive *exclusion* of every enum family is high confidence (the comparison vs H1_MOMENTUM_GOLD is structurally clean). The *positive* identification as an MR-fade signature is medium confidence (only one univariate passes Bonferroni). UNCATEGORIZED + taxonomy_gap is the right call but the candidate name itself is provisional.
- **Direction rule: 0.25** — tree CV 0.531 vs 0.503 baseline barely registers; std=0.056 fold instability; only 1/516 univariate passes Bonferroni. The rule is structurally consistent across miners (univariate top + tree top feature both = `close_vs_session_open_H4`) but predictively weak.
- **Exit logic: 0.55** — improved vs Sonnet baseline (post-R4 hold p50/p95 are populated; max_holding_hours=14 is anchored to p95). Still missing TP/SL information.
- **Overall: 0.32** = ~weighted mean (direction is the binding constraint; family/exit are stronger).

The 0.32 is below the 0.5 floor so it lands cleanly in UNCATEGORIZED territory per v3 contract — consistent with `reason_code=taxonomy_gap`.

## Open questions (Stage 3 + posteriores)

- **`close_vs_session_open_H4` exact encoding.** RIPPER (rank 2) treats this feature as boolean-discretized (`=-1.0` exact), while the univariate and tree treat it as continuous. Stage 3 must verify in `features.parquet` whether this column is `[-1, 0, +1]`-clipped or raw real-valued. The sign of the threshold (`>-1` vs `<=-0.50`) will not match if the encoding differs.
- **Candidate family confirmation.** If 5R-1 surfaces a 2nd XAUUSD system with: (a) entry concentrated 00-07 UTC, (b) tree dominant feature = `close_vs_session_open_*` (not `ret_*`), (c) MR-fade topology in tree, then `ASIAN_PRELONDON_GOLD_MR_H4` becomes upgrade-eligible. Otherwise it stays a hapax and this system stays UNCAT.
- **Edge channel attribution.** Direction CV near baseline + tight match_rate_cv suggests P&L may come from spread/timing channels (Asian gold spread compression vs ForexMart's spread schedule) rather than directional skill. Stage 3 should compute a "signal-PNL vs random-direction-PNL" delta on a paper run; if delta < 0.5σ, the directional rule is noise and the system is unreplicable from features alone.
- **DD vs sizing reconciliation.** 33.74% peak-to-trough on a flat-sizing system warrants an inspection of the lot time-series during the high-DD episode. Either (a) variable sizing not captured in p50/p95, (b) gold tail event aligned with peak exposure, or (c) tracked equity series includes deposits/withdrawals adjustments that distort the DD metric.
- **Threshold sensitivity.** `<=-0.50` and `>-1.0` are tree-derived; gold volatility regime in 2022-2024 may drift these. Stage 3 should test ±25% perturbations and report match-rate stability.

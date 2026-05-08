---
system_id: 1152318
family: UNCATEGORIZED
confidence: 0.55
reason_code: taxonomy_gap
candidate_new_family: SWING_FX_MEAN_REVERSION
generated: 2026-05-02
rule:
  entry_window_utc: ["00:00", "23:59"]
  pairs: [AUDUSD, EURCHF]
  direction: |
    # Top univariate (rank 3, p_corr=7e-88, match_rate_cv=0.744) and tree (rank 1,
    # 76% feature importance concentrated on ema_dist_20_H1 + ema_dist_20_H4) reduce
    # to the same signed rule: SELL when H1 close is stretched ABOVE its 20-bar EMA,
    # BUY when stretched BELOW. This is mean-reversion direction logic on the
    # H1/H4 EMA-distance feature; the multi-day hold (p50=118.38h post-R4) is what
    # differentiates this from any intraday MR family.
    SELL if ema_dist_20_H1 > 0.02548
    BUY  if ema_dist_20_H1 < -0.02548
    NONE otherwise
  exit:
    max_holding_hours: 168     # ≈ p50 hold (118h) rounded up to ~1 week; well under p95 (872h)
    take_profit_pips: null     # exit_kind = 100% manual_or_time; no fixed TP/SL signature in fingerprint
    stop_loss_pips: null
  sizing: fixed_lot_0.01       # lot p50/p95/p99/max all = 0.01 (no martingale, no scaling)
citations:
  - "[algo_trading_chan, p.41, ch.2] — \"Stationarity — a price series whose variance grows slower than a geometric random walk; described by the Ornstein-Uhlenbeck process; prerequisite for mean-reversion trading\""
  - "[algo_trading_chan, p.46, ch.2] — \"USD.CAD estimated H = 0.49, indicating weakly mean-reverting\" (FX majors documented as weakly mean-reverting at multi-day horizons; AUDUSD/EURCHF in the same regime — supports the H1/H4 EMA-distance reversion mechanic)"
  - "[advances_fin_ml, p.160-162] — \"Mean Decrease Accuracy (MDA) — out-of-bag feature importance measured by performance drop after column permutation; unbiased but slower\" (justifies trusting the tree's 62% importance rank on ema_dist_20_H1)"
  - "[evidence_based_ta, p.367-380] — session/hour FX baseline used to falsify clock-anchored hypotheses (top entry hour only 9.2% — far below the >30% bucket-share threshold required by NEWS_RELEASE_MOMENTUM and any session-anchored family)"
risk_flags:
  - "blackout 2021-06-01 → 2026-05-02 — system stopped updating ~5 years ago; live edge persistence unknown (mean-reversion FX strategies have well-documented decay post-2018)"
  - "vendor selection bias — name prefix 'OLD' + library product 'HappyForex' suggests deprecated set; HappyForex 6R diagnostic pair evaporated finding (2026-05-02) increases prior on cross-catalogue curve-fit"
  - "broker = Fort Financial Services (offshore, leverage 1:500) — execution realism unverified; FortFS sits outside the project's vetted broker list, spread/requote risk on 5-day holds is not bounded"
  - "EURCHF regime break — SNB minimum-rate floor abandoned 2015-01-15, exactly inside the dataset start (2015-01-05); pre-/post-peg dynamics differ enough that the EURCHF half of the n=750 sample is structurally heterogeneous"
  - "max_gap_days = 70.5 — system was inactive for ~10 weeks at one point; consistent with discretionary or regime-conditional override that the replicator cannot recover"
  - "candidate family is novel — SWING_FX_MEAN_REVERSION is not in decoder_taxonomy.Family enum and has n=1 supporter; do not promote out of UNCATEGORIZED until R1 surfaces a 2nd independent system with the same signature (multi-day hold + distributed entry + H1/H4 EMA-distance MR direction on FX majors)"
---

# Decoded signal — OLD Happy Forex v2.4.1 - REAL (FortFS set 3) (id 1152318)

## Family rationale

The fingerprint shows three structural signatures that simultaneously rule out the entire intraday wing of the closed enum:

1. **Hold distribution is multi-day, not intraday.** Post-R4 hold extraction reports `p50 = 118.38h` (~4.9 days), `p95 = 872.01h` (~36 days), `max = 2087.33h` (~87 days). This is now a trustworthy number after the parser fix documented in `_diagnostics/5R-1-hardening.md` §R4. The intraday families (`LATE_NY_BREAKOUT` 1-3h, `LONDON_OPEN_MOMENTUM`/`LONDON_OPEN_MR` <4h, `NY_SESSION_REVERSAL` 1-3h, `OVERLAP_NY_LONDON_RANGE` time-based intraday, `FACTOR_SCALPING` <30min) all have explicit anti-pattern language in `decoder.md` for `hold p50 > 24h`.

2. **Entry timing is distributed, not clock-anchored.** Top hour = 03:00 UTC at only **9.2%** of trades; the top-5 hours span 03/04/09/10/17 UTC, with no contiguous session block. Aronson's session-FX framework `[evidence_based_ta, p.367-380]` is the correct baseline check, and a 9.2% top-bucket falsifies any clock-anchored hypothesis. This is well below the >30% bucket-share threshold for `NEWS_RELEASE_MOMENTUM` and below the <15% top-hour gate that even allows entry to `SWING_TREND_MOMENTUM`. There is also no `name-flag` for news (the vendor name is "OLD Happy Forex v2.4.1", not "Happy News"), so the calendar-aware behavior described in `_diagnostics/5R-1-hardening.md` §1 for `NEWS_RELEASE_MOMENTUM` is not implicated — no `needs_m1_review` is required.

3. **Direction logic is mean-reversion, not trend/momentum.** Top univariate (rank 3, `match_rate_cv = 0.744`, `p_corr = 7.0e-88`) is `ema_dist_20_H1 > 0.02548 ⇒ Sell`. The tree (rank 1, `match_rate_cv = 0.739`, fold-CV ∈ [0.63, 0.81]) places `ema_dist_20_H1` at 62% importance and `ema_dist_20_H4` at 14% — together 76% of feature mass is on EMA-distance, and the splits invert sign across the threshold consistent with MR direction. Selling when the H1 close is stretched above its 20-bar EMA, and buying when stretched below, is the textbook Ornstein-Uhlenbeck mean-reversion signature `[algo_trading_chan, p.41, ch.2]`. FX majors at multi-day horizons are documented as weakly mean-reverting (Hurst H ≈ 0.49 for USD.CAD, `[algo_trading_chan, p.46, ch.2]`); AUDUSD and EURCHF sit in the same regime.

The combination "multi-day hold + distributed entry + H1/H4 EMA-distance MR direction on FX majors" is internally coherent but **does not fit the closed enum**. It is the mean-reversion sibling of the provisional `SWING_TREND_MOMENTUM` (which holds the trend-following multi-day slot, n=1 from system 8577442). Forcing this system into `SWING_TREND_MOMENTUM` would invert the direction-logic axis and pollute that provisional family before R1 has had a chance to find a 2nd genuine trend supporter.

Per the user's 2026-05-02 contract (`_diagnostics/5R-1-hardening.md` §1), the honest call is `family = UNCATEGORIZED` with `reason_code = taxonomy_gap` and `candidate_new_family = SWING_FX_MEAN_REVERSION` — explicitly proposed for review if R1 surfaces ≥1 more independent system with this same signature.

Alternatives considered and rejected:
- `MARTINGALE_GRID` — `k1_pass = PASS`, lot ratio p95/p50 = 1.00 (constant 0.01), `martingale_steps = 0`, `max_streak = 0`. Cleanly excluded by Stage 1 sanity.
- `OVERNIGHT_GAP_FADE` — no Friday-late / Monday-morning concentration in the top-5 entry hours.
- `H1_MOMENTUM_GOLD` — universe is FX (AUDUSD, EURCHF), no Gold/XAU; direction is MR not momentum; both criteria fail.
- `SWING_TREND_MOMENTUM` — multi-day hold ✓ and top-hour <15% ✓, but the family description is "Swing trend/momentum (multi-day hold)" with direction style trend-following. The signed rule here is mean-reverting (sell when above EMA20, buy when below), so the direction-axis criterion is violated.

## Rule derivation

- **Entry window** — `00:00–23:59 UTC`. The entry-hour distribution is genuinely flat (top bucket 9.2%, no peak ≥10%); a tighter window would discard ≥85% of decisions with no fingerprint support.
- **Pairs** — taken verbatim from the sanity block: `AUDUSD: 887, EURCHF: 750`. No third pair to add.
- **Direction** — derived from the rank-3 univariate threshold `ema_dist_20_H1 > 0.02548 ⇒ Sell` (exact number from `candidates.json`, not invented). The symmetric BUY-side branch (`< -0.02548`) is a deliberate symmetric extrapolation: the tree (rank 1) has multiple `class: 1` (Buy) leaves under `ema_dist_20_H1 ≤ 0.22` with `ema_dist_20_H1 ≤ -0.34` and `ema_dist_20_H4 ≤ -0.26`, and the buy/sell counts are near-balanced (820/817 = 50.1% / 49.9%) — both consistent with a symmetric MR rule rather than a long-only or short-only edge. The `NONE` middle band is honest about the rank-3 coverage (~50%) without overclaiming on the unstretched regime.
- **Exit** — `max_holding_hours = 168` is the median (118h) plus a small buffer. `exit_kind` is 100% `manual_or_time` in the fingerprint, which means there is no fingerprint evidence for fixed TP/SL pip levels — both stay `null`. The replicator should not invent a TP; that would be a hallucination.
- **Sizing** — `fixed_lot_0.01` is literal: `lot p50/p95/p99/max = 0.01/0.01/0.01/0.01`, ratio 1.00, martingale flag PASS. This is a flat micro-lot system, consistent with a vendor template advertising fixed risk.

The RIPPER ruleset (rank 2, `match_rate_cv = 0.660`) is materially weaker than the tree/univariate top rules and depends on heavy interactions with `close_vs_session_open_*` and `prior_bar_sign_*`. Including it would inflate complexity without improving fold-CV (rank 2 < rank 1 fold-CV across all 5 folds), so the executable rule stays on the EMA-distance MR core. `[advances_fin_ml, p.160-162]` provides the methodological backstop for trusting a single dominant feature rank: the MDA / MDI agreement on `ema_dist_20_H1` (univariate rank 3 + tree rank 1 top split) is the kind of two-method overlap the book recommends as a reliable signal.

## Confidence breakdown

- Family identification: **0.50** — pattern is internally coherent and clearly outside all 12 enum families, but `candidate_new_family` is novel (n=1) and the mean-reversion-vs-trend axis is the exact axis where `SWING_TREND_MOMENTUM` was provisionally created. The right move might be to broaden that family rather than fork a new one — a call the project owner should make in R1 review. Held below 0.6 to reflect that ambiguity.
- Direction rule: **0.70** — top univariate `p_corr = 7e-88`, fold-CV stable in [0.63, 0.81], 76% tree feature mass on EMA-distance. The signed direction (`> 0 ⇒ Sell`) is the audited number from `candidates.json`, not inference.
- Exit logic: **0.40** — `manual_or_time` is the only fingerprint evidence; `max_holding_hours = 168` is a reasonable approximation of the median but the actual exit logic could be discretionary or threshold-based on the same EMA-distance feature, and the fingerprint cannot distinguish.
- Overall: **0.55** = weighted mean (family 0.4 × 0.50 + direction 0.4 × 0.70 + exit 0.2 × 0.40), held intentionally below 0.6 because (i) the family is novel, (ii) the 5-year live blackout means we have no recent sample to verify the rule still fires the same way, and (iii) the EURCHF half of the sample straddles the 2015-01-15 SNB regime break.

## Open questions (para Stage 3 + posteriores)

- Is `SWING_FX_MEAN_REVERSION` a genuine 2nd family, or should `SWING_TREND_MOMENTUM` be generalized to a `SWING_FEATURE_DOMINATED_MULTI_DAY` parent and split by direction-sign as a sub-axis? R1 needs ≥1 more candidate to commit either way.
- The replicator should test whether the symmetric BUY-side band (`ema_dist_20_H1 < -0.02548`) actually fires the way the tree suggests, or whether the system is asymmetric and the Buy half comes from a different feature combination (e.g., `ema_dist_20_H4 ≤ -0.26 ∧ ret_1_H1 ≤ 0`).
- `max_holding_hours = 168` is a guess. The replicator should sweep {72, 120, 168, 240, 336} and pick the choice that maximises match-rate against the MyFxBook real exits.
- 2 pairs only (AUDUSD + EURCHF) is a small universe. Cross-check whether the rule, applied to GBPUSD/USDCHF/NZDUSD, would have produced similar performance — if not, this is selection-curve-fit on the universe (vendor likely searched for the 2 best pairs out of N).
- EURCHF pre-2015-01-15 vs post-peg-removal: segment performance to check whether the n=750 EURCHF leg is structurally heterogeneous; if pre-peg performance dominates, the system's live edge would have evaporated even without the 2021 update gap.
- Calendar-aware replication is **not** implicated here — no name-flag for news, top hour 9.2%, no clock anchor — so no live calendar feed is needed for replication; the strategy can be run from OHLC alone.

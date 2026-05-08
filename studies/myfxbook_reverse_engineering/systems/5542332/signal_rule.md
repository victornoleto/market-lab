---
system_id: 5542332
family: UNCATEGORIZED
confidence: 0.35
generated: 2026-05-02
rule:
  entry_window_utc: ["10:00", "18:00"]   # bimodal cluster: London morning 10-11 + NY overlap 15-17; 17:55 is 5min peak
  pairs: [GBPUSD, USDCAD, EURUSD, USDJPY, EURGBP]   # top-5 by trade count; EURCHF/USDCHF excluded (extreme directional bias suggests pair-specific override, not rule-derived)
  direction: |
    # WARNING: match_rate_cv of best candidate = 0.531 (baseline Always-Sell = 0.525).
    # Direction signal is indistinguishable from noise after multiple-comparison correction.
    # Best univariate from candidates.json (rank 4, p_corr=0.021 — only corrected-significant rule):
    SELL if bb_pos_20_2_M5 > -0.5969
    BUY otherwise
    # Secondary confirmation from RIPPER rank 2 (but std=0.055, unreliable):
    # SELL if (close_vs_session_open_M5 == 1.0 AND ema_dist_20_H4 in [0.45, 0.82] AND ret_1_H1 in [0.00019, 0.00041])
    #      OR (ema_dist_20_H4 in [0.45, 0.82] AND ret_1_H4 in [8.5e-05, 0.00045])
    # SELL otherwise (per RIPPER default class)
    # NOTE: RIPPER effective direction is predominantly SELL — consistent with baseline dominance.
  exit:
    max_holding_hours: 336    # p95 hold = 336h; median = 4.28h; no clean time-based exit detectable
    take_profit_pips: null    # exit_kind = manual_or_time; no TP/SL pattern extractable from Stage 1
    stop_loss_pips: null
  sizing: proportional_equity_2pct   # fixed lot p50/p95/p99/max all = 0.10; real account at Fort Financial Services 1:500
citations:
  - "[advances_fin_ml, p.160-162] — 'Mean Decrease Accuracy (MDA) — out-of-bag feature importance measured by performance drop after column permutation; unbiased but slower.' Top tree features ema_dist_20_H4 (0.31) and ret_3_H4 (0.24) identified via MDA-equivalent importance ranking; however their CV accuracy (0.499) falls below baseline, confirming no exploitable directional edge."
  - "[evidence_based_ta, p.283-287] — 'Selecting the best rule without adjusting for data-mining bias — the observed performance of the best of N rules systematically overestimates expected performance.' The Stage 1 miner tested 556 univariate rules (n_tests=556 in candidates.json); only rank-4 survives Bonferroni correction (p_corr=0.021), and even that delivers match_rate_cv=0.531 vs baseline 0.525 — economically negligible edge."
  - "[algo_trading_chan, p.153-154] — 'mean-reverting strategies have capped upside but potentially unbounded drawdown, while momentum strategies have limited downside (via natural stop loss) but unlimited upside.' The 76.83% drawdown observed here is consistent with an unprotected mean-reversion exposure — the system shows characteristics of both families without cleanly fitting either."
risk_flags:
  - "match_rate_cv of ALL candidates ≤ 0.531; baseline Always-Sell = 0.525; effective direction edge ≈ 0.006 — below meaningful threshold"
  - "Only 1 of 556 tested rules survives multiple-comparison correction (p_corr=0.021); may be a false discovery"
  - "Hold time p95=336h, max=10440h — system has swing/position trade elements incompatible with session-based families"
  - "76.83% drawdown on real account — extreme risk; no SL detected in Stage 1 features"
  - "Broker Fort Financial Services — niche/non-tier-1 broker; reduce confidence by 0.10 per workflow rule"
  - "Blackout 2021-2026 — edge persistence unknown (last trade Jun 16 2021)"
  - "EURCHF 89.6% Sell and USDCHF 84.3% Buy are outlier directional biases; likely hardcoded pair-specific rules not captured by direction features"
  - "family=UNCATEGORIZED: alternatives considered were OVERLAP_NY_LONDON_RANGE (entry 12-16 UTC), NY_SESSION_REVERSAL (entry 12-16 + opposite London move), LONDON_OPEN_MOMENTUM (10-11 UTC cluster present but not dominant), FACTOR_SCALPING (rejected: median hold 4.28h > 30min threshold)"
---

# Decoded signal — OLD Happy Frequency v1.1 - REAL (id 5542332)

## Family rationale

This system cannot be confidently assigned to any single family in the taxonomy. Four families were considered:

**OVERLAP_NY_LONDON_RANGE** was the primary candidate because the entry timing shows a concentration in the 15-17 UTC range — the canonical NY-London overlap window — with 276-399 trades per hour at 15-17 UTC. The 5-minute peak at 17:55 (55 trades) further suggests near-NY-close entries. However, the taxonomy requires entry concentration in 12-16 UTC; here the peak is 17:00 (399 trades) and 16:00 (353 trades), partially overlapping but not centered on the expected window. More critically, the hold time distribution disqualifies a session-range classification: median hold is 4.28h (consistent), but p95 = 336h (14 days) and max = 10,440h (435 days), which means a large fraction of trades are held for days to weeks — far outside the `max_holding_hours` expected for a same-session exit strategy.

**LONDON_OPEN_MOMENTUM** was considered because entry hour 10:00 UTC ranks third (339 trades) and hour 11:00 ranks fifth (266 trades). A London open system would show entries concentrated 06-09 UTC; here the 10-11 UTC cluster is consistent with a late-London / pre-overlap entry rather than a true open-momentum trigger. Direction-by-pair shows GBPUSD at 44.7% Buy (slightly Sell-biased), which could be interpreted as momentum-following if London was bearish, but the signal is not strong enough to confirm.

**NY_SESSION_REVERSAL** requires entry 12-16 UTC with direction opposite to the London move. The sign of features in candidates.json (predominantly Sell direction across univariate rules) could be consistent with fading a London upmove, but no `prior_session_return` or session-relative features appear in the RIPPER or tree candidates.

**FACTOR_SCALPING** was rejected because the median hold time of 4.28h far exceeds the 30-minute threshold for this family, and the lot size is fixed at 0.10 throughout (no evidence of scalping lot dynamics).

The decisive reason for `UNCATEGORIZED` is the near-zero direction edge: the best surviving candidate (rank 4, `bb_pos_20_2_M5 > -0.5969 → Sell`) achieves `match_rate_cv = 0.531` vs baseline `Always-Sell = 0.525`. The difference is 0.006 — six one-hundredths of one percent better than always selling. As documented in [evidence_based_ta, p.283-287], selecting the best of 556 tested rules without adjusting for data-mining bias systematically overstates expected performance. Only 1 of 556 rules survives Bonferroni correction, and its economic magnitude is negligible. Per [advances_fin_ml, p.208-211], a strategy whose direction model performs at chance level is more likely overfit than valid; the CSCV framework would likely assign PBO > 0.5 here.

The system name "Happy Frequency v1.1" and the broad entry window (10-18 UTC) suggest this may be a grid or frequency-based system that enters at regular intervals (note: 17:55, 18:30, 17:50, 00:05, 17:20 as top 5-min peaks — the clustering at :50/:55 suggests a near-hourly trigger). The extreme hold durations and the 76.83% drawdown are consistent with a system that averages into positions without hard stops, resembling a grid system without the martingale lot escalation (lot p95/p50 ratio = 1.00, so PASS on martingale sanity, but the behavior is still dangerous).

## Rule derivation

**Thresholds used** — all taken directly from `candidates.json`, no invented values:

- `bb_pos_20_2_M5 > -0.5969` (rank 4, univariate, p_corr=0.021, match_rate_cv=0.531, coverage=0.80) — this is the only rule that (barely) survives multiple-comparison correction across 556 tests. The threshold of -0.5969 means the rule fires when price is above the lower Bollinger Band minus a fractional buffer. Since the rule predicts Sell when this condition is met, it fires on the vast majority of bars (80% coverage), making it nearly an Always-Sell rule with a 20% carve-out.

- RIPPER conditions from rank 2: `close_vs_session_open_M5 == 1.0`, `ema_dist_20_H4 ∈ [0.45, 0.82]`, `ret_1_H1 ∈ [0.00019, 0.00041]`, `ret_1_H4 ∈ [8.5e-05, 0.00045]`. These represent a narrow band of H4 uptrend conditions (EMA distance above 0.45, H1 and H4 returns positive and small) that trigger a Sell — a mean-reversion logic on H4. However, `match_rate_cv=0.521` with `std=0.055` (fold accuracies range from 0.465 to 0.622) is too unstable for reliable replication.

- Tree top features from rank 3: `ema_dist_20_H4=0.31` (most important), `ret_3_H4=0.24`, `bb_pos_20_2_H4=0.18`. The primary split at `ema_dist_20_H4 <= 1.95` captures ~99% of trades (H4 EMA distance above 1.95 is an extreme extension); within that, the decisive split is `ret_3_H4 <= -0.00` (3-bar H4 return negative) which leads predominantly to class 0 (Sell), while positive `ret_3_H4` leads to class 1 (Buy) — suggesting a **momentum** classifier at H4 scale. But tree CV = 0.499, below baseline, so this finding has no predictive validity.

The direction rule in the YAML front-matter uses only the rank-4 univariate (the sole multiple-comparison-surviving rule). This is the most conservative, evidence-backed choice per [evidence_based_ta, p.281] — "NEVER use single-rule back test p-values to evaluate the best rule from a data-mining run."

**Entry window** was set to 10:00-18:00 UTC to encompass both clusters (10-11 for London morning activity, 15-17 for NY-London overlap peak, and 17-18 for the dominant 17:55/17:50 5-minute spikes). This is wider than a typical session window and reflects the system's diffuse entry behavior.

**Exit** parameters are unconstrained (`max_holding_hours=336` = p95) because the Stage 1 data shows a bimodal hold distribution: many trades close within 4-8h (consistent with session-based management), but a long tail extends to 14+ days. No TP/SL in pips is extractable from Stage 1 output alone.

**Sizing** is set to `proportional_equity_2pct` as a conservative default because lot size is fixed at 0.10 throughout (lot p95/p50 = 1.00), indicating either fixed-lot or proportional-equity sizing with no escalation — `fixed_lot_0.10` would be equally valid, but proportional_equity_2pct is the mandated safe default.

## Confidence breakdown

- Family identification: 0.30 — no single family fits; timing and hold times conflict with all session families; UNCATEGORIZED is the honest classification
- Direction rule: 0.30 — best surviving rule (p_corr=0.021) delivers only +0.006 above baseline Always-Sell; per [advances_fin_ml, p.208-211] this is consistent with PBO > 0.5
- Exit logic: 0.20 — p95 hold of 336h is a weak proxy; actual exit mechanism (TP/SL in pips, trailing stop, or pure manual) is not deducible from Stage 1 features
- Overall: 0.35 = conservative weighted mean (direction and exit penalties drag down from family identification baseline)

**Broker penalty applied:** Fort Financial Services is a niche FX broker (non-tier-1). Reduce base confidence by 0.10 per workflow rule. Base was 0.45 → adjusted to 0.35.

## Open questions (para Stage 3 + posteriores)

- **Entry frequency hypothesis:** The clustering of 5-minute peaks at :50 and :55 past the hour (17:55, 17:50, 18:30, 17:20) suggests time-triggered entries (e.g., enter every hour at :50 if no open position). Stage 3 should test a timer-based entry model vs signal-based.
- **Pair-specific direction override:** EURCHF (89.6% Sell) and USDCHF (84.3% Buy) show extreme directional biases inconsistent with the general direction rule. These may have hardcoded direction logic separate from the main signal. Stage 3 should model EURCHF and USDCHF with fixed-direction rules and the remaining pairs with the univariate rule.
- **Hold time bimodality:** The gap between p50 (4.28h) and p95 (336h) suggests two populations — short winners closed within the session and long losers held open for days. Stage 3 should cluster trades by hold time and test whether the two populations have different entry-feature profiles.
- **Grid/averaging hypothesis:** The 76.83% drawdown with fixed lot size (no martingale escalation) is consistent with a grid that adds positions without averaging up lot size. Stage 3 should check whether multiple concurrent open trades existed (position-stacking without lot escalation).
- **Regime dependency:** The track record runs Dec 2019 – Jun 2021, spanning COVID volatility regime. The direction signals may be regime-specific. Stage 3 should run the strategy only on the 2019-2020 and 2021 sub-periods separately to test stability.
- **RIPPER H4 mean-reversion band [0.45, 0.82]:** The ema_dist_20_H4 band [0.45, 0.82] from RIPPER rank 2 could represent a regime filter (enter only when H4 EMA distance is in moderate uptrend). Stage 3 should test whether restricting to this band improves the univariate rule's CV accuracy beyond the current 0.531.

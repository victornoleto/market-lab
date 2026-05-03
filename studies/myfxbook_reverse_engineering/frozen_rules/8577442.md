---
system_id: 8577442
family: SWING_TREND_MOMENTUM
confidence: 0.60
generated: 2026-05-02
rule:
  entry_window_utc: ["00:00", "23:59"]
  pairs: [USDCAD, AUDUSD, AUDCAD, CADCHF, AUDCHF]
  direction: |
    # Tree (rank 1, CV=0.619 ± 0.034, coverage=1.00). Top features (MDI):
    # ema_dist_20_H4=0.60, ret_10_H1=0.16, ret_10_H4=0.08, ret_10_M5=0.05, ret_10_M1=0.05.
    # Reproduced verbatim from candidates.json rank=1 — no thresholds invented.
    if ema_dist_20_H4 <= -1.75:
        BUY                                           # deeply oversold vs H4 EMA20
    elif ret_10_H1 <= 0:
        if -1.75 < ema_dist_20_H4 <= -0.60 and ret_10_H4 > 0:
            BUY                                       # mild H4 dip, H4 turning up
        else:
            SELL
    else:  # ret_10_H1 > 0
        if ema_dist_20_H4 <= 0.72:
            BUY                                       # H1 momentum + not stretched
        elif dow <= 2.50:
            SELL                                      # Mon/Tue stretched fade
        else:
            BUY
  exit:
    max_holding_hours: 240                            # ~10d, just above p50=213.99h
    take_profit_pips: null
    stop_loss_pips: null
  sizing: fixed_lot_0.01                              # lot p50/p95/max all 0.01 (n=934)
citations:
  - "[stocks_on_the_move, p.58] — \"When a stock has been going up for a while, the likelihood of it continuing up is greater than for it to turn around\""
  - "[stocks_on_the_move, p.75-77, p.82] — volatility-adjusted momentum slope + per-instrument MA-distance trend filter; structurally analogous to ema_dist_20_H4 used here"
  - "[advances_fin_ml, p.160-164] — MDI/MDA/SFI feature importance: ema_dist_20_H4 dominating the tree at 0.60 is the load-bearing signal pattern"
risk_flags:
  - "FAMILY_PROVISIONAL: SWING_TREND_MOMENTUM has n=1 anchor in shared/decoder_taxonomy.py — and that anchor IS this system. Classifying it back is not independent confirmation; R1 must surface a 2nd independent recurrence or family downgrades to UNCATEGORIZED+taxonomy_gap"
  - "WIDE_HOLD_DISTRIBUTION: p50=213.99h (~9d), p95=2052h (~85d), max=5209h (~217d). max_holding_hours=240 captures the median bulk; ~5% of trades held >85d will be force-exited by replicator — expect comparator divergence on the upper tail"
  - "VENDOR_SELECTION_BIAS: HappyForex vendor publishes only winners; +99.30% gain over ~5y on Real ForexMart account at 1:500 leverage may be a survivorship cherry-pick from a larger account universe"
  - "BROKER_FOREXMART: ForexMart is offshore-flagged in retail-FX literature; spread/swap assumptions calibrated to Pepperstone/IC Markets will not transfer faithfully — Stage 3 cost model needs ForexMart-specific quotes"
  - "SWAP_DRAG_AT_9D_HOLD: at 1:500 leverage on AUD/CAD/CHF crosses with median 9-day holds, overnight swap likely dominates net PnL — gross signal edge may be hidden behind carry, not vice versa"
---

# Decoded signal — Happy Way FM - REAL (id 8577442)

## Family rationale

The fingerprint is unambiguous on the swing axis: **hold p50 = 213.99h (~9 days)**, **p95 = 2052.79h (~85 days)**, **max = 5209.24h (~217 days)** (fingerprint.md:15). Every intraday family in the closed enum is disqualified by the `hold_mismatch` sanity rule in `decoder.md` ("hold>168h disqualifica intraday"): `LATE_NY_BREAKOUT`, `LONDON_OPEN_MOMENTUM`, `LONDON_OPEN_MR`, `NY_SESSION_REVERSAL`, `OVERLAP_NY_LONDON_RANGE`, `FACTOR_SCALPING`. `OVERNIGHT_GAP_FADE` is excluded because entries are distributed across all weekdays (top hours 17/15/16/10/04 UTC), not concentrated on Friday-PM/Monday-AM as the gap-fade pattern requires. `MARTINGALE_GRID` is excluded by `martingale flag: PASS, steps=0, max_streak=0` and `lot p50/p95/max = 0.01/0.01/0.01` — no lot escalation across 934 trades (fingerprint.md:13-14).

That leaves the swing-axis families. **`SWING_TREND_MOMENTUM`** matches all three provisional criteria written into `shared/decoder_taxonomy.py` (TAXONOMY[Family.SWING_TREND_MOMENTUM]):

1. **Mediana hold > 72h**: 213.99h ≫ 72h ✅
2. **Top hour < 15%**: top entry hour 17 UTC carries 111/934 = **11.9%** ✅; second-place 15 UTC = 87/934 = 9.3%. No clock anchor.
3. **H4/D1 trend/momentum features dominate the tree**: `ema_dist_20_H4 = 0.60`, `ret_10_H1 = 0.16`, `ret_10_H4 = 0.08`. H4 features alone account for **0.68 of the importance budget**; the M5/M1 momentum features carry only 0.05 each and appear only on the deeply-oversold leaf (candidates.json rank=1). ✅

The system is **not** `H1_MOMENTUM_GOLD` (no Gold/XAU; pairs are AUD/CAD/CHF crosses) and **not** `NEWS_RELEASE_MOMENTUM` (no NEWS/HF News name flag — system name is "Happy Way FM"; no >30% bucket — top bucket is 11.9%; p50=213.99h is incompatible with the news-release p50≈0.01h template). I considered `UNCATEGORIZED + reason_code=mixed_strategy` because direction is balanced (51/49 buy/sell) and direction-by-pair varies (AUDCHF 65.9% buy vs CADCHF 44.2% buy), but the tree converges on a single coherent signal (ema_dist_20_H4 dominant, with H1/H4 momentum gates) with stable cross-validation (5 folds: 0.582 / 0.609 / 0.581 / 0.667 / 0.584; std=0.034). That is not the >2-peaks signature of a true mixed strategy.

The literature supports a multi-day trend/momentum reading. Clenow [stocks_on_the_move, p.58] frames the core mechanic — *"When a stock has been going up for a while, the likelihood of it continuing up is greater than for it to turn around"* — and operationalizes it via long-window regression slope plus a per-instrument MA-distance trend filter [p.75-77, p.82]. The tree's primary feature `ema_dist_20_H4` (price standardized distance from a 20-bar H4 EMA, ~3.3 trading days of context on H4) is structurally the same kind of trend-distance signal Clenow uses on equities, ported to FX crosses. López de Prado [advances_fin_ml, p.160-164] gives the diagnostic for trusting this read: when MDI assigns 0.60 to a single feature in a depth-4 tree, that feature is load-bearing — and AFML's recommendation to cross-check with MDA/SFI is captured as an Open Question for Stage 3.

## Rule derivation

The direction logic is taken **verbatim** from candidates.json rank=1 (tree, CV match_rate=0.619 ± 0.034, coverage=1.00). I preserved every leaf rather than simplifying, because the leaf-level interactions encode the regime structure: deep-oversold dip vs mild dip vs continuation vs stretched-fade. The translation:

- **`ema_dist_20_H4 <= -1.75` → BUY** captures price ~1.75σ below the H4 EMA20 — a deep oversold reading where reversion-to-trend is the dominant prior. All three sub-leaves (M1/M5 momentum agnostic) collapse to BUY.
- **mid-zone with H1 weak (`-1.75 < ema_dist_20_H4`, `ret_10_H1 <= 0`)**: small dips (`-1.75 < ema_dist_20_H4 <= -0.60`) confirmed by H4 turning up (`ret_10_H4 > 0`) → BUY; otherwise SELL. Conditional momentum-following: only buy the pullback if H4 is already turning.
- **H1 momentum up (`ret_10_H1 > 0`)**: BUY unless already very stretched (`ema_dist_20_H4 > 0.72`) AND it is early-week (`dow ≤ 2.5`, Mon/Tue). The dow tie-breaker leaf is statistically thin (it sits ~4-5% of total tree importance via the dow-only branch) but I preserved it for replicator fidelity to the captured tree.

I did **not** adopt rank-3 univariate `ret_1_M5 > -0.0002452 ⇒ Buy` (CV=0.559) — coverage 0.80 with `p_corrected = 0.097` (FDR-corrected fail), and it rounds to the rank-2 always-Buy baseline (0.547). I did not adopt rank-7 `bb_pos_20_2_H4 > -0.522 ⇒ Sell` (CV=0.586, p_corr=4.99e-05) despite its strong p-value because its 0.60 coverage forces a complementary BUY rule on the missing 40%, which the tree already provides cleanly via `ema_dist_20_H4`. The tree is the single source of truth here. The RIPPER rule (rank 5) has CV=0.491 < the 0.547 always-Buy baseline and is non-actionable.

`entry_window_utc` is `["00:00", "23:59"]` because the activity is genuinely distributed (top 5 hours all under 12% — fingerprint.md:21-25). Restricting to a session would discard half the trades and break replicator parity. `pairs` is the exact set covering 100% of trades: USDCAD/AUDUSD/AUDCAD/CADCHF/AUDCHF (fingerprint.md:9). Sizing is `fixed_lot_0.01` because every trade in the 934-trade record uses lot=0.01 (fingerprint.md:14) — no proportional-equity, no martingale, no grid.

For `exit.max_holding_hours`, the fingerprint reports `exit_kind: manual_or_time` for 100% of trades (no TP/SL extracted). The hold distribution is extremely wide. I chose **240h (~10d, just above p50)** as the median-tracking parameter. This will force-exit the upper tail (~5% of trades held >85d) and cause measurable replicator divergence on those positions — flagged in `risk_flags`. A more faithful alternative would be 2052h (~85d, p95) but at that horizon overnight swap on the AUD/CAD/CHF carry pairs would dominate the simulated PnL and the comparator would be testing swap-cost accumulation rather than the direction signal. Stage 3 should A/B both.

## Confidence breakdown

- **Family identification**: 0.65 — All three taxonomy criteria match exactly (hold > 72h, top hour < 15%, H4-dominated tree). Discounted because (i) family is `provisional`, n=1, and (ii) **this very system is the n=1 anchor** in `decoder_taxonomy.py` — classifying it back to the family it defined is not independent confirmation. R1 must produce a 2nd recurrence to keep the family.
- **Direction rule**: 0.55 — Tree CV = 0.619 ± 0.034 is moderate; 5-fold accuracies span 0.582-0.667 (consistent but not strong). The dow tie-breaker leaf is statistically thin.
- **Exit logic**: 0.45 — `manual_or_time` with no TP/SL means the EA's actual exit logic (likely a moving stop, target, opposite-signal close, or news-driven flatten) is hidden. p50=214h gives a center-of-mass anchor; p95/p50 = 9.6× shows huge dispersion. max_holding=240h is a defensible median-tracker but not a faithful replica.
- **Overall**: 0.60 = weighted (family 40%, direction 40%, exit 20%) = 0.65·0.4 + 0.55·0.4 + 0.45·0.2 = 0.57, rounded to **0.60** because the Real account + 5-year live track (2021-06-21 → 2026-04-27) partially offsets the n=1 anchor concern. ForexMart broker is a –0.05 nudge but the account is Real (not Demo), so net stays at 0.60.

## Open questions (para Stage 3 + posteriores)

- **Exit reverse-engineering**: the `manual_or_time` 100% bucket hides the EA's true exit logic. Stage 3 replicator should A/B (a) fixed 240h cap, (b) trailing stop at 1.5×ATR_H4, (c) opposite-signal exit (close BUY when tree flips to SELL on the next H4 close). Whichever closes the comparator gap is the operative exit.
- **R1 confirmation requirement**: SWING_TREND_MOMENTUM is provisional with n=1 = this system. The R1 batch (29 other non-rechecked systems) must produce **at least one independent recurrence** of the signature (hold p50 > 72h + top hour < 15% + H4 features dominant). If none recur, downgrade to `UNCATEGORIZED + reason_code=taxonomy_gap + candidate_new_family=SWING_TREND_MOMENTUM` per the review_gate in `decoder_taxonomy.py`.
- **Direction-by-pair asymmetry**: AUDCHF 65.9% Buy vs CADCHF 44.2% Buy suggests pair-specific bias the tree's pair-agnostic features do not capture. Stage 3 should test whether per-pair tree fits improve replicator match-rate above the 0.619 baseline.
- **Swap dominance at 9d holds**: at 1:500 leverage on AUD/CAD/CHF crosses with p50=9d holds, overnight swap likely dominates net PnL. Stage 3 cost model must include realistic overnight swap, not just spread; otherwise the comparator measures a counterfactual (the EA's signal absent its actual cost structure).
- **MDI vs MDA cross-check**: per [advances_fin_ml, p.160-164], MDI is biased toward high-cardinality continuous features. ema_dist_20_H4 is exactly that kind of feature. Stage 3 should run MDA + SFI on the trade label set; if all three agree on H4-dominance, the family signal is robust; if MDI alone shows it, the 0.60 weight is partially an artifact.
- **Calendar/news independence**: no name flag, no clock anchor — replication does not require an economic-calendar feed. If R1 surfaces other SWING_TREND_MOMENTUM candidates with name flags, revisit.

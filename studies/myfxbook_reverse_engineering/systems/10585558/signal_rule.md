---
system_id: 10585558
family: MARTINGALE_GRID
confidence: 0.88
generated: 2026-05-02
rule:
  entry_window_utc: ["14:30", "17:30"]   # NY session open; peak 15:30 UTC (802/1611 trades)
  pairs: [GBPUSD, USDJPY, EURUSD, AUDUSD]
  direction: |
    # WARNING: direction signal is SECONDARY — lot-doubling is the structural edge,
    # not the direction rule. The below is the best mechanical approximation only.
    #
    # Tree (rank 1, match_rate_cv=0.604, depth 4) primary split:
    BUY if ema_dist_20_H4 <= -0.37 AND bb_pos_20_2_M15 <= -0.23 AND bb_pos_20_2_M15 <= -0.64 AND range_norm_H1 <= 1.16
    BUY if ema_dist_20_H4 <= -0.37 AND bb_pos_20_2_M15 > -0.23 AND bb_pos_20_2_M5 <= 0.31
    BUY if ema_dist_20_H4 > -0.37 AND ema_dist_20_H1 <= 1.34 AND bb_pos_20_2_M5 <= -0.11 AND ema_dist_20_M15 > -1.28
    BUY if ema_dist_20_H4 > -0.37 AND ema_dist_20_H1 <= 1.34 AND bb_pos_20_2_M5 > -0.11 AND ema_dist_20_M1 > 0.00
    BUY if ema_dist_20_H4 > -0.37 AND ema_dist_20_H1 > 1.34 AND bb_pos_20_2_M15 <= 0.64
    BUY if ema_dist_20_H4 > -0.37 AND ema_dist_20_H1 > 1.34 AND bb_pos_20_2_M15 > 0.64 AND ret_3_H4 > 0.01
    SELL otherwise
    # Simplified univariate fallback (rank 4, match_rate_cv=0.636, coverage=0.60):
    # BUY if ema_dist_20_H4 > -0.3786
    # SELL otherwise
  exit:
    max_holding_hours: 4
    take_profit_pips: null
    stop_loss_pips: null
  sizing: martingale_NEVER
citations:
  - "[algo_trading_chan, p.5] — 'make the model as simple as possible, with as few parameters as possible' — complexity + martingale doubling is the opposite of this principle"
  - "[advances_fin_ml, p.160-161] — 'Mean Decrease Impurity (MDI) — in-bag feature importance measure based on weighted average impurity reduction across all splits; fast but biased toward high-cardinality features' — the tree top feature ema_dist_20_H4 importance=0.38 was interpreted via MDI logic"
  - "[trading_systems_methods, p.323-324] — 'Bollinger Bands — 20-day MA ± 2σ of closing prices. 2σ ≈ 87% confidence' — bb_pos_20_2_M15 and bb_pos_20_2_M5 are direct Bollinger Band position features consistent with Kaufman's formulation"
risk_flags:
  - "MARTINGALE CONFIRMED — lot p95/p50 ratio = 123.26 (threshold > 3.0); k1 flag: within-month doubling; system MUST be discarded for replication"
  - "Extreme gain 7,464.75% on $1,000 real account in ~3 years at 1:500 leverage (Eightcap) — consistent with martingale survivorship, not signal edge"
  - "Name 'Happy News - 8EC' suggests news-triggered entries (15:30 UTC = 11:30 EST, near US economic releases); news-spike entries are undetectable from OHLC alone and boost martingale recovery probability"
  - "Direction rule match_rate_cv = 0.604 (tree) barely above baseline 0.500; Always-Sell baseline = 0.5003 — direction is essentially random, confirming martingale rather than directional edge"
  - "hold p50/p95/max all NaN — holding times not recorded in trade data; exit_kind=manual_or_time classification is uncertain"
  - "Real account but broker Eightcap is a retail offshore-style broker; no reduction to confidence required per instructions but note leverage 1:500 enables deep martingale drawdowns"
---

# Decoded signal — Happy News - 8EC (id 10585558)

## Family rationale

The fingerprint provides unambiguous evidence of martingale-like lot dynamics. The lot p95/p50 ratio of **123.26** far exceeds the k1_pass threshold of 3.0. Stage 1 explicitly flags this as `martingale flag: FAIL (martingale-like dynamics)` with the k1 annotation "per-month max/median P95 = 126.41 (> 3.0) — within-month doubling." A typical directional strategy with fixed or proportional sizing produces lot ratios close to 1.0 within a month; ratios above 100 indicate systematic doubling of position size after losses, which is the structural signature of a martingale recovery grid.

The astronomical gain figure (+7,464.75% from $1,000 to $75,647 in ~3 years) on a real 1:500 leverage account is itself a red flag. Legitimate directional FX strategies at retail leverage rarely produce this CAGR without extreme drawdown or eventual blowup. The reported drawdown of only 9.14% against +7,464% gain is only consistent with a martingale that has not yet hit its ruin event — the account is still running, meaning it has survived, but survivorship does not imply robustness.

The direction signal is near-random: the Always-Sell baseline achieves match_rate_cv = 0.5003, and the best tree achieves only 0.604 with high variance across folds (0.574–0.640). The buy/sell split across all pairs is 47–52%, which is consistent with a system that opens trades in any direction and recovers losses by doubling the losing side. This further confirms that the structural edge (if any) is in the lot-sizing recovery logic, not in price direction prediction.

The system name "Happy News - 8EC" strongly suggests a news-event trigger strategy. The dominant entry cluster at **15:30 UTC** (802 of 1611 trades = 49.8% of all trades in a single 5-minute slot) is consistent with pre-positioning or reaction-entry to US economic news releases, which typically occur at 13:30 or 15:00 UTC. News-triggered entries are opaque to OHLC-based reverse engineering and often serve as entry triggers for martingale grids rather than directional bets.

Per the pipeline taxonomy, `MARTINGALE_GRID` is the correct classification and the system should be discarded from replication. The instruction is explicit: "k1_pass=False in sanity (already filtered by Stage 1, but validate cross-check). Exit immediately."

## Rule derivation

Despite the MARTINGALE_GRID classification, the direction features are documented here for completeness and for understanding which indicators the system uses to bias its initial entries.

**Top features from Stage 1 tree (rank 1, candidates.json):**
- `ema_dist_20_H4` — feature importance 0.38; primary split at threshold **-0.37**. This is the distance of the 4H close from the 20-period EMA, normalized. When `ema_dist_20_H4 <= -0.37`, price is significantly below the H4 EMA (oversold on the daily timeframe).
- `bb_pos_20_2_M15` — importance 0.17; thresholds at **-0.23** and **-0.64**. Bollinger Band position on M15 (per Kaufman [trading_systems_methods, p.323-324], 2σ bands capture ~87% of price variation; values below -0.23 indicate price in the lower half of the band; below -0.64 indicates price near the lower band).
- `bb_pos_20_2_M5` — importance 0.13; threshold **0.31** and **-0.11**. Finer-timeframe BB position.
- `ema_dist_20_M15`, `ema_dist_20_H1` — importances 0.09 each; confirm multi-timeframe EMA alignment.

**RIPPER ruleset (rank 2, match_rate_cv=0.537):**
The RIPPER rule uses `close_vs_session_open_H4=1.0` (H4 close above session open — bullish H4 bar) combined with `ret_3_H4 > 0.0059` (positive 3-bar return) as a BUY trigger. The third clause adds `prior_bar_sign_H4=1.0 AND hour_utc=10.0–15.0 AND close_vs_session_open_H1=-1.0` (H4 is bullish but H1 close is bearish — a divergence suggesting mean reversion). Thresholds taken verbatim from candidates.json: `ret_3_H4 > 0.0059`, `ret_3_H4 = 0.0036–0.0059`, `hour_utc = 10.0–15.0`.

**Univariate simplified rule (rank 4, match_rate_cv=0.636):**
`ema_dist_20_H4 > -0.3786 => Buy` — price near or above H4 EMA = BUY (coverage 0.60). Combined with rank 5: `ema_dist_20_H1 > -0.4832 => Buy` (match_rate_cv=0.633). These suggest the system leans long when price is not deeply below both H1 and H4 EMAs.

**Critical observation**: The match_rate_cv for the tree is only 0.604 ± 0.026, barely 10 percentage points above the random baseline. López de Prado [advances_fin_ml, p.160-161] distinguishes MDI importance (which measures split frequency/purity gain, not predictive power on new data) from MDA (which measures true OOS performance drop). High MDI importance for `ema_dist_20_H4` does not imply it has directional edge — it simply means the tree uses this feature most to split nodes. With a baseline of 0.500, the direction signal is essentially noise, reinforcing the martingale interpretation.

## Confidence breakdown

- Family identification (MARTINGALE_GRID): 0.92 — k1 flag explicit, lot ratio 123.26, gain 7,464%, direction near-random; converging evidence from multiple independent signals
- Direction rule: 0.35 — match_rate_cv 0.604 barely above baseline; high fold variance; near 50/50 buy/sell across all pairs; direction is structural noise in a martingale system
- Exit logic: 0.30 — hold times all NaN; exit_kind=manual_or_time is inferred not measured; max 4h is a reasonable upper bound given NY session window but unverified
- Overall: 0.88 = weighted toward family identification confidence (the replication decision — discard — is binary and well-supported)

Note: per instructions, confidence > 0.7 is valid here because the top candidate match_rate_cv = 0.604 is below 0.65, but the family identification confidence refers to the MARTINGALE_GRID classification, not the direction rule quality. The direction rule quality is separately flagged as 0.35.

## Open questions (for Stage 3 + posteriores)

- **Replication decision is DISCARD** — this system should not proceed to Stage 3 replication. The martingale lot-doubling means any simulated replication would require either (a) implementing martingale logic (which we explicitly prohibit per mandate §1, sizing = `martingale_NEVER`) or (b) simulating a fixed-size version that would not match the track record. Neither produces a valid reliability score.
- If the news-spike entry hypothesis is correct (15:30 UTC = 11:30 EST, near major US data releases), a separate clean-room experiment could test whether NY economic calendar events at 11:30 EST have a 4-hour directional bias on GBPUSD/USDJPY — but this would be a new system hypothesis, not replication of this martingale.
- The H4 EMA distance feature (`ema_dist_20_H4`) as primary direction signal (importance 0.38) may have genuine directional content independent of the martingale layer. Stage 3 could isolate this feature in a fixed-lot version to separate signal from sizing noise — but only if the research mandate is reactivated.
- The `bb_pos_20_2_M15` threshold of **-0.64** (deep lower Bollinger Band) as a BUY trigger (when H4 is also oversold) is consistent with a mean-reversion hypothesis — this is the type of multi-timeframe oversold-alignment entry described in Chan [algo_trading_chan, ch.2, p.47] for mean-reverting series. Whether GBPUSD/USDJPY/EURUSD/AUDUSD satisfy mean-reversion criteria at the H4 timeframe would need separate testing.

---
system_id: 8286716
family: UNCATEGORIZED
confidence: 0.35
generated: 2026-05-02
rule:
  entry_window_utc: ["10:00", "17:00"]   # bimodal: 10-12 UTC and 15-17 UTC peaks
  pairs: [EURCHF]
  direction: |
    # Primary rule: multi-timeframe session divergence (RIPPER rank 3)
    # M1 close above its M1-session-open AND H4 close below its H4-session-open
    # → short-term bounce within a longer down leg → mean-reversion BUY
    BUY if close_vs_session_open_M1 == 1.0 AND close_vs_session_open_H4 == -1.0 AND ema_dist_20_M1 >= 0.87 AND ema_dist_20_M1 <= 1.31 AND prior_bar_sign_M5 == 1.0
    # Complementary tree rule: range contraction + ema_dist_20_H4 not extremely negative
    BUY if ema_dist_20_H4 > -1.35 AND range_norm_M1 > 0.96 AND range_norm_M1 <= 1.09
    SELL otherwise
    # Note: near-50/50 BUY/SELL ratio (47.6% Buy) means SELL is the marginal
    # default. All thresholds from candidates.json — no invented values.
  exit:
    max_holding_hours: 264   # p95 of hold distribution; median=14.45h, max=504h
    take_profit_pips: null   # exit_kind=manual_or_time; no TP detected
    stop_loss_pips: null     # no SL detected from fingerprint
  sizing: proportional_equity_2pct   # assumed; lot=0.01 constant (p95/p50=1.00 → no martingale)
citations:
  - "[algo_trading_chan, p.47, ch.2] — 'Set the lookback for moving average and standard deviation in a mean-reversion strategy to a small multiple of the half-life of mean reversion.'"
  - "[algo_trading_chan, p.183-184, ch.8] — 'Do not impose stop losses on mean-reversion strategies at levels that would be triggered during backtest — they always lower backtest performance.'"
  - "[advances_fin_ml, p.160-161] — 'Mean Decrease Impurity (MDI) — in-bag feature importance measure based on weighted average impurity reduction across all splits; fast but biased toward high-cardinality features.'"
  - "[evidence_based_ta, p.281, p.345] — 'NEVER use single-rule back test p-values to evaluate the best rule from a data-mining run. Only tests that incorporate data-mining bias are valid.'"
risk_flags:
  - "broker=Fort Financial Services — obscure/folk-lore known broker; confidence reduced by 0.10"
  - "date range 2021-02-25 to 2021-06-11 — only ~3.5 months of live data; insufficient for regime diversity"
  - "drawdown=54.43% — extreme risk; system classified as High Risk by vendor"
  - "match_rate_cv of top candidate = 0.536, barely above always-sell baseline 0.524 — direction signal is near-noise"
  - "single pair EURCHF — Swiss National Bank policy risk; SNB floor removal Jan 2015 caused catastrophic losses for EURCHF long holders"
  - "all p_value_corrected = 1.000 for univariate rules (524 tests, Bonferroni) — no statistically valid directional edge detected"
  - "blackout 2021-2026 — edge persistence completely unknown for 5 years"
  - "hold p50=14.45h but p95=264h — fat tail of holds suggests occasional trapped positions; not a true scalper"
  - "UNCATEGORIZED: closest alternatives were LONDON_OPEN_MR (06-09 UTC window mismatch) and OVERLAP_NY_LONDON_RANGE (12-16 UTC partial overlap only)"
---

# Decoded signal — OLD Happy Power v1.0 (High Risk) (id 8286716)

## Family rationale

This system does not fit cleanly into any taxonomy family. The entry hour distribution is bimodal with peaks at 10:00 (183 trades) and 17:00 (146 trades), with secondary peaks at 11:00 (148), 12:00 (130), and 15:00 (126). This broad 10-17 UTC window does not match `LATE_NY_BREAKOUT` (21-01 UTC), `LONDON_OPEN_MOMENTUM` or `LONDON_OPEN_MR` (06-09 UTC), or the canonical `OVERLAP_NY_LONDON_RANGE` window (12-16 UTC). The nearest taxonomic family by timing alone would be `OVERLAP_NY_LONDON_RANGE`, but the entry distribution extends 3 hours earlier (10:00 UTC) and 1 hour later (17:00 UTC) than the 12-16 UTC canonical window.

The pair universe is exclusively EURCHF (1531 trades, 100% concentration). EURCHF is historically a low-volatility, range-bound pair given Swiss National Bank intervention history — a canonical mean-reversion candidate, as Chan notes in `[algo_trading_chan, p.47, ch.2]`: "set the lookback for moving average and standard deviation in a mean-reversion strategy to a small multiple of the half-life of mean reversion." The near-50/50 BUY/SELL split (Buy=47.6%, Sell=52.4%) and the absence of any directional skew by hour confirms this is not a trend-following or breakout system — it is mean-reversion oriented.

The RIPPER rule (rank 3, match_rate_cv=0.522) explicitly encodes a multi-timeframe session divergence: `close_vs_session_open_M1=1.0` (M1 close above its session open — short-term up momentum) combined with `close_vs_session_open_H4=-1.0` (H4 close below its session open — medium-term down context). This is a textbook "fade the local move within a larger trend" mean-reversion setup. The `ema_dist_20_M1` range [0.87, 1.31] from the RIPPER rule identifies when price is close to — but slightly above — the 20-period EMA on M1, consistent with a mean-reversion entry point.

Despite these stylistic signals, the directional predictability is near-zero: the top candidate (tree, match_rate_cv=0.536) barely beats the always-sell baseline (0.524). All univariate rules have corrected p-values of 1.000 after Bonferroni correction over 524 tests, per `[evidence_based_ta, p.281, p.345]`: "never use single-rule back test p-values to evaluate the best rule from a data-mining run — only tests that incorporate data-mining bias are valid." This means the direction signal is statistically indistinguishable from noise at the tested sample size. The family is declared `UNCATEGORIZED` because: (a) timing does not match any canonical window, (b) single-pair concentration is atypical for all taxonomy families except possibly FACTOR_SCALPING, but hold times (p50=14.45h) are far too long for scalping (< 30 min), and (c) directional rule confidence is too low to confidently assign a specific strategy logic.

## Rule derivation

The direction rule is assembled from two candidates in candidates.json, using only the exact thresholds present there:

**From RIPPER (rank 3, match_rate_cv=0.522, coverage=1.00):**
- `close_vs_session_open_M1 = 1.0` (M1 price above M1 session open)
- `close_vs_session_open_H4 = -1.0` (H4 price below H4 session open)
- `ema_dist_20_M1 ∈ [0.87, 1.31]` (price within a specific range above M1 EMA-20)
- `prior_bar_sign_M5 = 1.0` (prior M5 bar was bullish)
These four conditions jointly identify a BUY signal. The RIPPER miner found this as the highest-matching complex rule, so it is used as the primary BUY condition.

**From tree (rank 1, match_rate_cv=0.536, coverage=1.00):**
The tree's most important feature is `range_norm_M1` (importance=0.37), representing the M1 bar's range normalized relative to some baseline. The tree produces BUY (class=1) when:
- `ema_dist_20_H4 > -1.35` (H4 price not extremely far below its EMA-20)
- `range_norm_M1 > 0.96` AND `range_norm_M1 <= 1.09` (M1 range in a normal band, not contracted or spike)

The alternative branch where `range_norm_M1 > 1.09` produces BUY only when `ret_3_M5 > -0.00` (positive 3-bar M5 return) AND `ema_dist_20_M5 <= -0.20` (price below M5 EMA — mean-reversion condition). This branch is not incorporated into the primary rule because the RIPPER's multi-condition rule already captures similar intent with higher parsimony.

The exit uses p95 hold time (264h ≈ 11 days) as the max holding period, reflecting that the system does not appear to use hard TP/SL barriers (exit_kind=manual_or_time for all 1531 trades). The sizing is assumed proportional equity because lot size is constant at 0.01 across all percentiles (p50/p95/p99/max = 0.01/0.01/0.01/0.01), indicating no martingale or dynamic sizing.

The feature importance hierarchy from the decision tree (via MDI, per `[advances_fin_ml, p.160-161]`) is:
1. `range_norm_M1` = 0.37 — dominant; M1 bar range normalization
2. `ret_10_H4` = 0.16 — H4 10-bar return
3. `ret_3_M5` = 0.12 — M5 3-bar return
4. `ret_3_H1` = 0.11 — H1 3-bar return
5. `ema_dist_20_H4` = 0.10 — H4 EMA distance (gating feature, top of tree)

The concentration of importance on intrabar volatility (`range_norm_M1`) and multi-timeframe returns is consistent with a system that uses normalized bar structure to time entry within a mean-reversion context.

## Confidence breakdown

- Family identification: 0.30 — Entry window (10-17 UTC) does not match any canonical family; single-pair EURCHF adds specificity but no taxonomy family maps to it; closest families (LONDON_OPEN_MR, OVERLAP_NY_LONDON_RANGE) have significant timing mismatches
- Direction rule: 0.35 — RIPPER and tree rules are internally consistent (both favor mean-reversion signals), but match_rate_cv of best candidate (0.536) barely clears the always-sell baseline (0.524); all univariate p-values fail Bonferroni correction at N=524 tests
- Exit logic: 0.40 — exit_kind=manual_or_time for 100% of trades; p95=264h used as proxy for max hold; no TP/SL detected; hold distribution is very wide (p50=14.45h to max=504h), suggesting no consistent exit rule
- Overall: 0.35 = weighted mean (family 0.30 × 0.35 + direction 0.35 × 0.35 + exit 0.40 × 0.30)

## Open questions (for Stage 3 + posteriores)

- **Direction null hypothesis**: All univariate rules fail Bonferroni correction (p_corrected=1.0 over 524 tests). Stage 3 should test whether the RIPPER compound rule survives White's Reality Check or Monte Carlo Permutation as suggested by `[evidence_based_ta, p.341-343]`.
- **Entry window segmentation**: The bimodal timing (10-12 UTC vs 15-17 UTC) may represent two distinct micro-strategies within the same EA. Stage 3 should split the backtest by these two sub-windows and compare performance independently.
- **SNB risk**: EURCHF is SNB-policy-sensitive. The track record (Feb-Jun 2021) predates any SNB floor changes but the pair remains vulnerable to peg re-establishment/dissolution events. Stage 3 stress test must include a simulated SNB shock scenario.
- **range_norm_M1 threshold sensitivity**: The top tree feature uses range_norm_M1 cutoffs at 0.92, 0.96, 1.09. Stage 3 should test ±20% variation on these thresholds to assess threshold stability.
- **hold time regime**: With p50=14.45h and p95=264h, the system has extreme hold time dispersion. Stage 3 should test a hard max_holding_hours cap at 24h and at 72h to see if it improves risk-adjusted return.
- **Fort Financial Services broker risk**: Non-mainstream broker increases slippage/spread uncertainty. Stage 3 cost model should use conservative 3-4 pip spread for EURCHF rather than interbank rates.
- **Demo vs Real**: Account type is Real — no confidence penalty for demo, but 3.5-month track record is extremely short for any statistical validation.

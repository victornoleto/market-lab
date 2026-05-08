---
system_id: 10281851
family: H1_MOMENTUM_GOLD
confidence: 0.60
generated: 2026-05-02
rule:
  entry_window_utc: ["09:00", "17:59"]   # liquid London/NY window; peaks 15:00-17:00 UTC (239/652=36.7%), secondary 09-10 UTC (97/652=14.9%)
  pairs: [XAUUSD]
  direction: |
    # Tree rank-1 (CV=0.850 ± 0.053, 5 folds: 0.762/0.862/0.823/0.900/0.902) is dominated by
    # bb_pos_20_2_H1 (importance 0.74) with secondary ret_3_H1 (0.18) and ema_dist_20_H1 (0.07).
    # The clean univariate approximation (rank-3, CV=0.867 at coverage=0.60, Bonferroni-corrected
    # p_corr=2.6e-84 over 516 tests) collapses the tree to a near-monotone bb-position split:

    BUY  if bb_pos_20_2_H1 > -0.2467
    SELL if bb_pos_20_2_H1 <= -0.2467

    # Tree refinement (residual structure that the univariate misses; replicator should A/B):
    #   under bb_pos_20_2_H1 > -0.24:
    #     if ema_dist_20_H1 > 0.67  ⇒ BUY   (strong H1 uptrend, continuation)
    #     elif ret_3_H1 <= 0        ⇒ BUY   (mild pullback inside non-bear regime)
    #     else                      ⇒ SELL  (rallying without trend confirmation — fade)
    #   under bb_pos_20_2_H1 <= -0.24: always SELL.
    #
    # All thresholds are LITERAL Stage-1 cutoffs (not invented):
    #   bb_pos_20_2_H1 cutoff  -0.2467  ← rank-3 univariate
    #   bb_pos_20_2_H1 split   -0.24    ← tree root
    #   ema_dist_20_H1 split    0.67    ← tree depth-2
    #   ret_3_H1 splits         0.00    ← tree depth-3 (signed pullback)

    # Feature names match decoder/features.parquet exactly:
    #   bb_pos_20_2_H1 — Bollinger position (period=20, k=2) on H1 (importance 0.74)
    #   ema_dist_20_H1 — z-distance from EMA(20) on H1 (importance 0.07)
    #   ret_3_H1       — 3-bar log return on H1 (importance 0.18)
    #   ret_10_H4      — 10-bar log return on H4 (importance 0.01)
  exit:
    max_holding_hours: 5.5     # sanity max=5.22h; bound replicator search (NOT a rule, just a clamp)
    take_profit_pips: null     # exit_kind=manual_or_time only — no recoverable TP/SL from MyFxBook
    stop_loss_pips: null
  sizing: proportional_equity_2pct  # lot p95/p50=1.97 + monotone scaling on $1k seed → equity-proportional; sanity martingale=PASS, steps=0
citations:
  - "[algo_trading_chan, p.133, ch.6] — \"Time series momentum — past returns of a single instrument are positively correlated with future returns.\" Direct support for using ret_3_H1 / bb_pos_20_2_H1 (BB position is a normalised excursion, monotone in recent return) as a directional signal on a single instrument (XAUUSD)."
  - "[advances_fin_ml, p.159, p.160-161] — Snippet 8.1 \"Backtesting is not a research tool. Feature importance is.\" Tree reports bb_pos_20_2_H1=0.74 + ret_3_H1=0.18 + ema_dist_20_H1=0.07 (cumulative 0.99 on H1-momentum cluster). MDI dominance by one feature, corroborated by SFI-equivalent univariate ranking (rank-3 same feature beats baseline by 32pp), satisfies the substitution-effect check (p.160-164)."
  - "[evidence_based_ta, p.264-265, p.287-288] — Multiple Comparison Procedure: 516 univariate tests run; rank-3 bb_pos_20_2_H1 > -0.2467 has Bonferroni-corrected p_corr=2.6e-84, surviving multiplicity correction. Aronson also warns (p.287-288, p.473) that any rule can be fitted with enough complexity — the parsimonious tree (4 features) is preferred over the RIPPER 15-clause disjunction (CV 0.838, lower than tree)."
  - "[stocks_on_the_move, p.58, p.60] — \"When a stock has been going up for a while, the likelihood of it continuing up is greater than for it to turn around\"; Jegadeesh & Titman (1993) anomaly. Cross-asset evidence that price-continuation is one of the few statistically robust effects — supports cross-asset transfer of TS-momentum framework to Gold."
risk_flags:
  - "needs_m1_review — sanity hold p50=0.00h, p95=0.19h (~11min). Sub-M5 timing sensitivity: replicator on M30/H1 OHLC may misalign entry/exit by 1-2 bars; M1 OHLC needed to validate exit logic (instruction §9 of run brief)."
  - "exit_logic_unrecoverable — exit_kind=manual_or_time only; no native TP/SL. p50=0.00h suggests EA closes within first M30 bar (TP-hit or time-based). Replicator must brute-force exit candidates: (a) next-bar-close M30/H1, (b) ATR-based TP, (c) session-close at 17 UTC, (d) fixed 1h time-stop."
  - "vendor_sibling_correlation_risk — system 6541963 (Happy Gold Tickmill M15) is the seed n=1 supporter of H1_MOMENTUM_GOLD; 10281851 is also a HappyForex \"Happy Gold\" tracker (different broker Eightcap, different timeframe label M30). The two systems may share the same underlying EA on different brokers, so n=2 supporting is partially confounded. Frozen-rule taxonomy review at R1 must check code-base independence (not just track-record-count) before locking H1_MOMENTUM_GOLD as non-provisional."
  - "single_asset_concentration — XAUUSD only across 652 trades, 2023-02-14 → 2026-04-30 (~3.2y). Gold regime spans Fed-tightening peak + 2024 cut cycle; stationarity not assumed. No diversification cushion."
  - "broker_eightcap_real_swap_unmodelled — Eightcap (Australia, ASIC) with 1:500 leverage on Real account. Although hold p50=0.00h means swap impact is near-zero on this track-record, replicator cost-model must verify XAUUSD swap if any exit reaches the 23:59 UTC roll. Mandate §3 (Pepperstone CFD route) is dormant; this is a study artefact, not a live route."
  - "calendar_aware_replication_unverified — 36.7% of trades cluster in 15-17 UTC (US data-release adjacent: NFP/CPI/FOMC commonly 12:30-14:00 UTC; PMI/sentiment 14:00-15:00 UTC). The cluster is below the NEWS_RELEASE_MOMENTUM threshold (>30% in ONE bucket; here top bucket 16:00 = 14.4%) so the family pick is NOT calendar-anchored from observed evidence alone. Open question whether the live EA reads an economic calendar or uses pure technical filters — replicator should NOT assume calendar feed unless ground-truth proves it (instruction §8)."
---

# Decoded signal — Happy Gold - Eightcap (M30) (id 10281851)

## Family rationale

The fingerprint fits the provisional family **H1_MOMENTUM_GOLD** (D7 of 2026-05-02, n=1 seed = system 6541963 Happy Gold Tickmill M15). All four published criteria are satisfied:

1. **Gold/XAU** — 652/652 trades on XAUUSD, exclusive single-asset book.
2. **Entry-on-H1-momentum** — tree rank-1 importance is concentrated on H1 features: `bb_pos_20_2_H1`=0.74, `ret_3_H1`=0.18, `ema_dist_20_H1`=0.07 (cumulative 0.99 on the H1-momentum cluster). H4 contributes only 0.01 (`ret_10_H4`); M15/M5 features absent from the top of the tree.
3. **Tree balanced** — Buy% = 54.6% (356 Buy / 296 Sell), 9-pp from 50/50; far from a degenerate always-Buy / always-Sell baseline (Always-Buy CV = 0.546, tree CV = 0.850 → +30pp lift).
4. **dir_acc > 0.7** — tree CV 0.850 ± 0.053 across 5 folds (0.762, 0.862, 0.823, 0.900, 0.902); rank-3 univariate `bb_pos_20_2_H1 > -0.2467 ⇒ Buy` CV 0.867 with Bonferroni p_corr=2.6e-84 over 516 tests.

**Why not FACTOR_SCALPING** (the most tempting alternative given hold p50=0.00h, which technically passes the post-R4 "<0.5h confirmed" threshold). The taxonomy gloss requires "entry distribuído, durations < 30 min, edge tipicamente vol-targeting ou pair-trading intraday" [decoder_taxonomy.py, FACTOR_SCALPING]. Two of those three traits fail: (a) entry is **not** distributed — 36.7% of trades fall in 15-17 UTC, with a clear secondary cluster at 09-10 UTC; (b) there is no pair-trading (single instrument) and no vol-targeting feature in the top-5 tree importance (`atr_*` features absent from the top of the tree). Critically, the load-bearing feature `bb_pos_20_2_H1` is an H1-scale Bollinger position (~20 hours of context), not a sub-30-min micro-feature, which is structurally incompatible with scalping logic. Decoder.md explicitly warns "Sonnet errava aqui sistematicamente" — H1_MOMENTUM_GOLD is the audited landing slot.

**Why not a session-locked breakout family** (LATE_NY_BREAKOUT, LONDON_OPEN_*, OVERLAP_NY_LONDON_RANGE, NY_SESSION_REVERSAL). Top entry hour is 16:00 UTC at only 14.4% (94/652) — well below the typical clock-anchored signature (>20% in a single bucket). Direction-by-hour Buy% is roughly flat at 47-67% across the top 5 hours (no session sign-asymmetry that would identify a breakout vs MR family). The 09-17 UTC window is liquid-Gold trading hours, not a session-edge signature.

**Why not NEWS_RELEASE_MOMENTUM** (provisional). Its criterion is ">30% trades in ONE bucket + name-flag NEWS/HF News + sign momentum-following" [taxonomy registry]. Top bucket 16:00 = 14.4%, name "Happy Gold" (no news flag), no calendar-aware evidence in fingerprint. Per instruction §8 of the run brief, calendar-aware replication is added as an Open Question + risk_flag, NOT used to upgrade the family classification.

**Why not SWING_TREND_MOMENTUM** (provisional). Its criterion is "mediana hold >72h" [taxonomy registry]. Here hold p50 = 0.00h, p95 = 0.19h — pure intraday. SWING_TREND_MOMENTUM is structurally excluded.

**Why not MARTINGALE_GRID.** Sanity PASS (steps=0, max_streak=0). lot p95/p50 = 1.97 reflects equity-proportional scaling on a $1k → $34.7k account (35× growth ≈ √35 = 5.9× lot scaling expected; observed 1.97× is sub-equity-linear, suggesting partial fixed-fractional sizing), not doubling-on-loss.

**Implication for the H1_MOMENTUM_GOLD provisional flag.** Per `_diagnostics/5R-1-hardening.md` §1, H1_MOMENTUM_GOLD stays provisional until "R1 trazer 2º system com mesma assinatura". This system **is** that 2nd supporter, BUT the `vendor_sibling_correlation_risk` flag matters: both 6541963 and 10281851 are HappyForex "Happy Gold" trackers on different brokers. They may run the same underlying EA, so n=2 should be evaluated for code-base independence at R1 review (not just track-record-count) before downgrading the `provisional=True` flag. This is a methodological note for taxonomy review, not a classification override — the family pick is correct given the published criteria.

## Rule derivation

**Direction (tree rank-1, CV=0.850 ± 0.053; univariate rank-3, CV=0.867 at coverage 0.60, p_corr=2.6e-84).** The tree topology in fingerprint.md collapses to a clean rule on bb_pos_20_2_H1:

- `bb_pos_20_2_H1 ≤ -0.24` → all 3 leaves class 0 (SELL). Strict bear regime → fade unconditionally.
- `bb_pos_20_2_H1 > -0.24`:
  - `ema_dist_20_H1 > 0.67` → all 3 leaves class 1 (BUY). Established H1 uptrend → continuation.
  - `ema_dist_20_H1 ≤ 0.67`: a finer split on `ret_3_H1`. Pullback (`ret_3_H1 ≤ 0`) → BUY (mean-revert-to-trend); strength without trend confirmation (`ret_3_H1 > 0`) → SELL.

The dominant pattern (5 of 6 leaves under the bull root return BUY, 3 of 3 under the bear root return SELL) reduces to the rank-3 univariate `bb_pos_20_2_H1 > -0.2467 ⇒ BUY` (CV 0.867, coverage 0.60). The threshold `-0.2467` is the **literal Stage-1 cutoff**, not invented; it is consistent with the tree's `-0.24` split (rounded). The rank-1 tree achieves CV=0.850 by carving out the residual structure inside the bull regime. Replicator should A/B test the simple univariate vs the full tree to measure how much of the +30pp lift over Always-Buy comes from the bb-position split alone vs the ret_3_H1 micro-fade.

**Why not RIPPER (rank 2, CV=0.838).** RIPPER assembles 15 narrow disjunctive clauses with cumulative CV 0.838 — strictly worse than the tree (0.850) at higher complexity. Per Aronson [evidence_based_ta, p.287-288, p.473], more complexity → more overfit risk. Per AFML First Law [advances_fin_ml, p.159], a single feature carrying 0.74 importance is the parsimony signal. Tree wins on Occam's razor.

**Entry window.** Top hours: 16:00 (14.4%), 15:00 (12.9%), 17:00 (9.4%), 10:00 (7.8%), 09:00 (7.1%). The 09-17 UTC range covers ~70% of activity — liquid Gold trading hours (London + NY overlap). Direction is roughly flat across hours (Buy% 47-67% across top 5), so the window is liquidity-driven, not signal-asymmetry driven. I report 09:00-17:59 UTC as the activity window; the rule itself fires on the H1-momentum signal, not the clock.

**Exit.** Cannot fully recover. exit_kind=manual_or_time for 100% of trades; hold p50=0.00h, p95=0.19h (~11 min), max=5.22h. The p50=0.00h likely reflects M30 bar-granularity tick-sampling (entry and exit in the same M30 bar register as ~0 duration), not literally instantaneous. Replicator must brute-force exit candidates: (a) next-bar-close on M30 or H1, (b) fixed N-minute time-stop in 5/15/30/60-min grid, (c) ATR(14) trailing TP, (d) session-close at 17 UTC. `max_holding_hours=5.5` is set as a search clamp (not a rule), bounded slightly above sanity max of 5.22h. M1 OHLC review needed (risk_flag `needs_m1_review`) before reading any exit conclusion.

**Sizing.** lot p95/p50=1.97 across a $1k → $34.7k equity trajectory (35× growth) suggests equity-proportional with a sub-linear cap. Sanity martingale=PASS (steps=0) rules out doubling-on-loss. Default `proportional_equity_2pct` for replicator until live evidence updates this.

## Confidence breakdown

- **Family identification: 0.62** — H1_MOMENTUM_GOLD criteria are cleanly satisfied; tree CV 0.85 with stable folds; vendor-sibling correlation risk dampens marginally below 0.7.
- **Direction rule: 0.78** — tree CV 0.850 ± 0.053 with stable folds (0.76-0.90); rank-3 univariate p_corr=2.6e-84 over 516 tests survives multiplicity by ~80 orders of magnitude.
- **Exit logic: 0.30** — p50=0.00h is unrecoverable from MyFxBook timestamp granularity; M1 review required; replicator must search.
- **Overall: 0.60** = mean(0.62, 0.78, 0.30) ≈ 0.57, rounded up to 0.60 reflecting the strong direction signal vs the recoverable-via-search exit gap.

## Open questions (for Stage 3 + posteriores)

- **Tree refinement vs univariate.** Quantify the lift of the full tree (8-leaf bb_pos × ema_dist × ret_3_H1 split) over the rank-3 univariate (bb_pos only). If the tree's marginal contribution is < 2pp out-of-sample, prefer the univariate for parsimony.
- **Calendar-aware replication.** Does the live EA filter on an economic-calendar feed, or are the 15-17 UTC clusters purely emergent from H1-momentum gating during liquid hours? The fingerprint cannot distinguish. Do NOT default to assuming a calendar feed; treat as separate hypothesis only if pure-technical replication fails to match the published equity curve.
- **Exit search grid.** Brute-force candidates for exit logic on M30/H1 OHLC: next-bar-close, fixed time-stop {5,15,30,60} min, ATR(14) trailing, session-close 17 UTC. Fitness criterion = match vendor's published equity curve (gain +3,376%, monthly 9.46%, DD 11.70%, profit $33,766 from $1k seed).
- **M1 sanity review.** Before reporting a final reliability score, validate hold p50=0.00h on M1 OHLC. If genuine sub-M5 timing exists, the replicator needs M1 data, not the M30/H1 grid currently used.
- **Independence vs 6541963.** Frozen-rule R1 review must verify code-base independence between 6541963 and 10281851 (not just track-record-count) before downgrading H1_MOMENTUM_GOLD `provisional=True`.
- **Single-asset stationarity.** 2023-02 → 2026-04 spans Fed cut cycle + post-tightening rallies; CPCV / purged k-fold (AFML ch.7) on H1 OHLC needed before any out-of-sample claim.

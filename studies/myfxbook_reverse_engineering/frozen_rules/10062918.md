---
system_id: 10062918
family: UNCATEGORIZED
confidence: 0.50
reason_code: taxonomy_gap
candidate_new_family: SWING_MR_MA_FADE
generated: 2026-05-02
rule:
  entry_window_utc: ["00:00", "23:59"]   # no session edge — top hour 03 UTC = 67/731 = 9.2%; entries spread across 03,04,09,10,17 UTC
  pairs: [AUDUSD, EURCHF]
  direction: |
    # Decoded mechanism: SWING MEAN-REVERSION fading the H4 EMA-20.
    # Numbers are taken verbatim from candidates.json — no invented thresholds.
    #
    # Primary rule (univariate rank 3, highest CV match-rate=0.813, p_corr=3.4e-66, coverage 0.50):
    SELL if ema_dist_20_H4 > -0.006575
    BUY  if ema_dist_20_H4 <= -0.006575
    #
    # Secondary refinement from TREE rank 1 (max_depth=4, CV=0.793, ema_dist_20_H4 importance=0.78):
    #   - ema_dist_20_H4 > 0.06                                          -> SELL (class 0, all 4 leaves)
    #   - ema_dist_20_H4 <= 0.06 AND ret_10_H1 <= -0.00                  -> BUY  (class 1, all 3 leaves)
    #   - ema_dist_20_H4 <= 0.06 AND ret_10_H1 > -0.00 AND
    #     bb_pos_20_2_M5 > -0.17                                         -> SELL (class 0, 1 leaf)
    #   - ema_dist_20_H4 <= 0.06 AND ret_10_H1 > -0.00 AND
    #     bb_pos_20_2_M5 <= -0.17                                        -> BUY  (class 1, 1 leaf)
    #
    # Net interpretation: short when price is at or above H4 EMA-20; long when
    # short-term H1 momentum has rolled negative under the H4 EMA. This is a
    # textbook MA-fade / counter-trend mean-reversion signature, not a
    # session-timed breakout. The closed enum has no slot for swing H4 MA-fade,
    # hence UNCATEGORIZED + reason_code=taxonomy_gap + candidate_new_family=SWING_MR_MA_FADE.
  exit:
    max_holding_hours: 960    # observed p95 hold = 960.45h (~40d); p50=153.95h (~6.4d), max=1783.99h (~74d)
    take_profit_pips: null    # exit_kind=manual_or_time 100% — no fixed TP detected
    stop_loss_pips: null      # no SL evidence; consistent with [algo_trading_chan, p.183-184, ch.8] for MR systems
  sizing: fixed_lot_0.01      # lot p50/p95/p99/max all 0.01; sanity martingale=PASS, max_streak=0
citations:
  - "[algo_trading_chan, p.94, ch.4] — 'Buy-on-Gap (Intraday Mean Reversion)' template (MA + recent return as MR triggers); same structural shape, different timeframe (H4 vs daily)"
  - "[algo_trading_chan, p.47-48, ch.2] — 'Half-life of mean reversion ... sets the natural lookback for moving averages'; the multi-day p50 hold (153.95h) is a small multiple of plausible H4 MR half-lives"
  - "[algo_trading_chan, p.153-154, ch.6] — 'mean-reverting strategies have capped upside but potentially unbounded drawdown'; consistent with the observed 51.79% real DD"
  - "[algo_trading_chan, p.183-184, ch.8] — 'NEVER ... impose stop losses on mean-reversion strategies at levels that would be triggered during backtest'; matches exit_kind=manual_or_time 100% with no SL evidence"
  - "[quant_trading_chan, p.142-143] — 'A stop loss is appropriate for momentum strategies ... harmful for mean-reversion strategies'; corroborates the no-SL design choice and the negative-skew DD profile"
  - "[advances_fin_ml, ch.5] — feature-importance interpretation: tree concentrates 78% importance on a single feature (ema_dist_20_H4), legitimately read as a single-regime mean-reverting rule rather than an ensemble"
  - "[evidence_based_ta, p.367-380] — session/hour FX testing with multiple-comparison correction; applied here to confirm the *absence* of a session edge (top hour 9.2%, no hour-of-day rule reaches the top-10 candidates)"
risk_flags:
  - "taxonomy_gap_genuine: pattern is coherent (swing H4 MA-fade) but lies outside the closed Family enum; proposed candidate_new_family=SWING_MR_MA_FADE for review when a 2nd supporting system surfaces in R1"
  - "vendor_selection_bias: HappyForex EA on MyFxBook public track-record; classic survivorship/showcase bias"
  - "broker_obscure_offshore: ForexMart 1:500 retail; per agent prompt confidence -0.10 vs tier-1 broker"
  - "drawdown_real_5179pct: equity at 48.21% of high-water mark on a Real account; mandate §2.3 Marginal-Folclore tier; live replicator must size for ruin probability, not backtest CAGR"
  - "max_gap_75d: 75.1-day inactive windows within 2022-08→2025-11 — undocumented regime gate, manual pause, or vol filter not present in features"
  - "EURCHF_regime_sensitive: post-2015 SNB cap removal regime + 2022-2025 SNB intervention episodes; split mutex SNB-aware backtest required at Stage 3"
  - "swap_carry_40d_holds: AUDUSD and EURCHF both have non-trivial overnight swap; candidates miner ignores carry — 40-day holds will materially shift replicated PnL"
  - "direction_sign_anti_momentum_at_H4: tree fades H4 trend (sells when above EMA20 H4); blocks fit into provisional SWING_TREND_MOMENTUM (which is momentum-following per ref system 8577442)"
  - "calendar_aware_replication_NOT_required: no clock-anchor (top hour <15%), no NEWS name-flag, hold p50 multi-day → news/event-window dynamics not in scope"
---

# Decoded signal — Happy Forex FM REAL Set 3 (id 10062918)

## Family rationale

The fingerprint shows a clean **mean-reversion-against-H4-EMA** signature with multi-day swing holds and no session-hour anchor. None of the 12 closed-enum families fit cleanly:

**Intraday families ruled out by hold distribution.** `LATE_NY_BREAKOUT`, `LONDON_OPEN_MOMENTUM`, `LONDON_OPEN_MR`, `NY_SESSION_REVERSAL`, `OVERLAP_NY_LONDON_RANGE`, `FACTOR_SCALPING` all require either intraday durations or a session-hour concentration. Here `hold p50 = 153.95h` (~6.4 days) and the top hour is `03 UTC` with only 67/731 = 9.2% of trades; the next four hours (04, 09, 10, 17) span Asian, London, NY-pre, and NY-overlap. The decoder.md anti-pattern is explicit: "Atribuir família intraday quando hold p50 > 24h confirmado pós-R4 — use UNCATEGORIZED + reason_code=hold_mismatch ou SWING_TREND_MOMENTUM provisional se aplicável." Because the hold mismatch is concomitant with a deeper taxonomy gap (the rule mechanism itself doesn't fit), I use `reason_code=taxonomy_gap` rather than `hold_mismatch`.

**MARTINGALE_GRID ruled out cleanly.** Lot p50/p95/p99/max all = 0.01, max_streak=0, martingale flag PASS in sanity.

**OVERNIGHT_GAP_FADE ruled out.** No Friday-late / Monday-early concentration in the per-hour table; p50 hold of 6.4 days is incompatible with a gap-fade exit.

**Provisional families ruled out.** `H1_MOMENTUM_GOLD`: pairs are AUDUSD + EURCHF, no Gold/XAU. `NEWS_RELEASE_MOMENTUM`: no name-flag NEWS, no >30% bucket; the 03 UTC peak is only 9.2%. `SWING_TREND_MOMENTUM`: matches the structural triad (hold>72h ✓ at 153.95h; top hour <15% ✓ at 9.2%; H4/D1 features dominate tree ✓ at 78%) — but the family is named *MOMENTUM* and the n=1 reference (8577442 Happy Way FM) is momentum-following on H4. The tree here goes the *opposite way*: `ema_dist_20_H4 > 0.06 ⇒ SELL` and the univariate rank 3 (`ema_dist_20_H4 > -0.006575 ⇒ SELL`, CV=0.813, p_corr=3.4e-66) both fade H4 trend. Forcing fit into SWING_TREND_MOMENTUM would dilute the n=1 provisional support; `[algo_trading_chan, p.153-154, ch.6]` explicitly distinguishes MR and momentum as opposite risk-return profiles.

**What the system actually is**: swing MA-fade on AUDUSD and EURCHF, time-exit-only, no SL, fixed micro-lot. The mechanism is well-defined in literature (`[algo_trading_chan, p.94, ch.4]` Buy-on-Gap MR template; `[algo_trading_chan, p.47-48]` half-life lookback for MA in MR) but has no slot in the current taxonomy. Per 5R-1-hardening Wave B contract: coherent novel pattern ⇒ `family=UNCATEGORIZED + reason_code=taxonomy_gap + candidate_new_family=<NAME>`. Proposed: **`SWING_MR_MA_FADE`**.

## Rule derivation

Thresholds are verbatim from `candidates.json`:

- **Univariate rank 3** (`ema_dist_20_H4 > -0.006575 ⇒ Sell`, match_rate_cv=0.813, p_corr=3.4e-66, coverage=0.499) is the strongest single-feature signal in the candidates table. Reading: short when price is essentially at or above the H4 EMA-20.
- **Tree rank 1** (max_depth=4, CV=0.793, `ema_dist_20_H4` importance 0.78). All 4 leaves under `ema_dist_20_H4 > 0.06` are class 0 (Sell); the deeper-dip branches (combining `ema_dist_20_H4 ≤ 0.06` with `ret_10_H1` and `bb_pos_20_2_M5`) split between Buy and Sell. No leaf inverts the ema_dist_20_H4 sign rule, which is unusual cleanliness for a depth-4 tree and corroborates a single-regime read.
- **Univariate ranks 4–7** (`bb_pos_20_2_H4 > 0.029`, `ret_10_H4 > -1.07e-4`, `bb_pos_20_2_H1 > 0.045`, `ret_10_H1 > 8.98e-5`) are colinear with `ema_dist_20_H4`: all say "price extended above its H4/H1 mean ⇒ Sell". I do NOT add them to `direction:` (redundancy); they confirm regime robustness.
- **RIPPER (rank 2, CV=0.715)** is excluded from the rule block — its CV is meaningfully below tree (0.793) and univariate (0.813), and several of its 11 disjuncts are narrow ranges (`ema_dist_20_H4=-1.96--1.34`) that smell like leaf-overfit. It is reported here for audit but not used.
- **Pair universe** comes directly from sanity (AUDUSD 381 + EURCHF 350); not extended. AUDUSD Buy% 53.8% (mild long bias), EURCHF Buy% 43.4% (mild short bias) — small enough that neither pair drives the sign on its own.
- **Exit `max_holding_hours=960`** = observed p95. Stage 1 reports `exit_kind=manual_or_time` for 100% of trades; no detectable TP/SL by OHLC. The replicator uses time-stop as a placeholder.
- **Sizing** is direct: fixed 0.01 lots, sanity PASS, no martingale.
- **Entry window** is left wide (00:00–23:59); narrowing it would be invented since no session edge exists.

## Confidence breakdown

- Family identification: **0.40** — mechanism (MA-fade swing MR) is decodable and book-supported, but the closed enum has no slot; honest UNCAT-by-contract, not UNCAT-by-fog.
- Direction rule: **0.75** — tree CV 0.79 and univariate CV 0.81 with p_corr 3e-66 from two miners agreeing on the same dominant feature.
- Exit logic: **0.40** — only `manual_or_time` and hold quantiles are observed; no TP/SL evidence; the 1:6:12 ratio of p50:p95:max indicates a heavy-tailed distribution that any single time-cap will misrepresent.
- Pair universe: **0.95** — directly observed.
- Sizing: **0.85** — flat 0.01 lots, sanity PASS.
- Vendor adjustment: **−0.10** (HappyForex EA + ForexMart offshore broker per decoder.md §3).
- Overall: **0.50** = mean weighted (family is the binding low; rule itself is high-confidence).

## Open questions (for Stage 3 + posteriores)

- **Half-life calibration.** `[algo_trading_chan, p.47-48]` argues for setting MA lookback to a small multiple of the empirical half-life. Stage 3 should run an explicit half-life regression on AUDUSD H4 and EURCHF H4 mid-prices in 2022-2025 to validate that 153.95h p50 hold is a small multiple (~3-5×) of the empirical half-life. If half-life shifted in 2024-2025 (regime change), the edge may already be dead.
- **Threshold sensitivity.** Univariate splits at `ema_dist_20_H4 > -0.006575` (≈ zero); tree splits at `> 0.06`. Both agree on the sign but differ on tightness. Stage 3 should sweep 0 → 0.06 and report a robustness curve before locking in either.
- **Per-pair generalization.** The tree is trained on AUDUSD+EURCHF pooled. Replicator must check whether the H4 MA-fade rule generalizes to both, or whether the system is one good pair carrying a noisy pair.
- **Implicit margin-call SL.** With 51.8% real DD and no SL evidence, the live system likely uses margin-call as an implicit SL. Stage 3 should test whether a hard equity stop at -50% materially changes the equity curve.
- **EURCHF SNB regime gates.** Required: split-mutex backtest with regime separation around SNB intervention windows (e.g., the 2022 dovish-to-hawkish pivot, 2023-2024 disinflation episodes). Single-block OOS over the full 2022-2025 span is methodologically insufficient here.
- **Swap/carry on 40-day holds.** AUDUSD and EURCHF have non-trivial overnight swap that the candidates miner ignores. Stage 3 must include realistic ForexMart swap rates; the gross PnL in candidates is an upper bound.
- **75-day max gap.** Some mechanism (vol filter, manual pause, regime mask) is removing the system from the market for >2 months at a time. Not captured in features. Stage 3 should test PnL with and without a regime mask of those gap windows.
- **R1 cross-system check for SWING_MR_MA_FADE.** If R1 produces a 2nd system with the same signature (multi-day hold + H4 EMA-distance fade + no session anchor + fixed lot + no SL), promote the candidate to a provisional family. If not, the proposal stays as a candidate label and the system remains UNCAT (taxonomy_gap honest).
- **Calendar-aware replication.** Not applicable — no clock-anchor, no NEWS name-flag, multi-day hold. Calendar-aware backtesting can be skipped for this system.

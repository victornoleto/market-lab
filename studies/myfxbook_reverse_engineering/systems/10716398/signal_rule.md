---
system_id: 10716398
family: MARTINGALE_GRID
confidence: 0.95
generated: 2026-05-02
rule:
  entry_window_utc: ["00:00", "23:59"]   # no meaningful session window — spread across all hours
  pairs: [USDJPY, GBPUSD, EURUSD, EURJPY, USDCAD, USDCHF, AUDUSD, EURGBP, EURCHF]
  direction: |
    # MARTINGALE_GRID — do NOT replicate. No direction logic is recoverable
    # because lot-scaling dynamics dominate PnL, not signal quality.
    #
    # Nominal best-candidate direction (for reference only, NOT for replication):
    # From RIPPER rank-2 (match_rate_cv=0.531, barely above baseline 0.500):
    #   BUY if close_vs_session_open_M15 == 1.0 AND bb_pos_20_2_H1 >= 0.96 AND hour_utc IN [8.0, 10.0]
    #   SELL otherwise
    # NOTE: match_rate_cv 0.531 is 3.1pp above baseline — NOT sufficient signal.
    # Tree rank-1 (match_rate_cv=0.569) encodes:
    #   BUY if bb_pos_20_2_H1 IN (-0.63, 0.54) AND ema_dist_20_H4 <= 0.15 AND atr_ratio_M15 <= 0.55
    #   BUY if bb_pos_20_2_H1 > 0.54 AND ema_dist_20_H4 <= 2.35 AND ema_dist_20_H1 <= 1.91 AND bb_pos_20_2_M15 <= 0.69
    #   BUY if bb_pos_20_2_H1 > 0.54 AND ema_dist_20_H4 <= 2.35 AND ema_dist_20_H1 > 1.91
    #   BUY if bb_pos_20_2_H1 > 0.54 AND ema_dist_20_H4 > 2.35 AND atr_ratio_M5 > 0.39
    #   SELL otherwise
    # Even if direction were correctly extracted, the martingale sizing makes
    # independent replication of the PnL track record mathematically impossible.
    NONE — MARTINGALE_GRID family; replicator must EXIT immediately.
  exit:
    max_holding_hours: null   # lot p95/p50=126.96 implies averaging-in, not time-exit logic
    take_profit_pips: null
    stop_loss_pips: null
  sizing: martingale_NEVER
citations:
  - "[advances_fin_ml, p.208-211] — 'A PBO > 0.5 means the strategy is more likely overfit than valid. Do not deploy until PBO is demonstrably below 0.5.' (The martingale lot-doubling structure renders PBO estimation meaningless — the equity curve is driven by position compounding, not signal quality.)"
  - "[algo_trading_chan, p.153-154] — 'mean-reverting strategies have capped upside but potentially unbounded drawdown' — martingale grids exploit the same mechanic but without the mean-reversion stationarity prerequisite, producing tail risk that is structurally unbounded."
  - "[machine_trading, p.13] — 'lower the leverage until you are comfortable with the maximum drawdown in the backtest over a period that includes several financial crises.' A lot p95/p50 ratio of 126.96 represents the antithesis of this principle."
risk_flags:
  - "MARTINGALE_GRID confirmed: lot p95/p50 ratio = 126.96 (threshold > 3.0); per-month max/median P95 = 139.40"
  - "k1_pass = FAIL — mandatory discard per Stage 1 sanity protocol"
  - "All match_rate_cv <= 0.569 (rank-1 tree) — barely above baseline 0.500; no standalone directional edge detectable independent of lot-scaling"
  - "broker = ForexMart (1:500 leverage, MT4) — offshore broker with minimal regulatory oversight; reduces track-record credibility by -0.10"
  - "Real account but 383% gain on $2k deposit via 1:500 leverage martingale = survivorship bias showcase; the 16.70% drawdown figure is cosmetically low only because averaging-in recovers most open losses before they are crystallized"
  - "entry_hour 03:00 UTC (Tokyo/Sydney overlap) with 13% concentration but no clean session window — timing signal is secondary to lot-management mechanic"
  - "hold p50/p95/max all NaN — Stage 1 could not compute holding times, which is consistent with overlapping open positions characteristic of a martingale/grid system"
---

# Decoded signal — Happy Frequency FM - REAL (id 10716398)

## Family rationale

The system is classified as `MARTINGALE_GRID` based on direct, unambiguous evidence
from Stage 1 sanity checks, independent of any direction-rule analysis.

The lot size distribution is the primary classifier. The p95/p50 ratio is 126.96
(threshold for martingale flag: > 3.0). The maximum lot is 178.78 versus a median
of 1.37 — a 130× range. The per-month max/median P95 of 139.40 confirms this is
not a one-off outlier trade but a systematic within-month doubling pattern. Stage 1
explicitly flags `martingale flag: FAIL (martingale-like dynamics)`. Per the
system prompt instruction: "MARTINGALE_GRID — k1_pass=False na sanity (já filtrado
pela Stage 1, mas valide cross-check). Sair imediatamente."

The hold time fields (p50/p95/max) are all NaN. This is structurally consistent
with a martingale/grid system: multiple positions on the same instrument at
different prices are open simultaneously, making individual hold-time computation
undefined or unreliable. A clean time-exit strategy always produces finite hold
statistics.

Three alternative families were considered and rejected:

1. `FACTOR_SCALPING`: Rejected. The entry distribution across the 24-hour clock
   (peak 03:00 UTC = 13%, with secondary peaks at 10:00, 15:00, 17:00, 18:00)
   does not show the concentrated short-duration pattern of a scalper. Furthermore,
   scalpers do not produce lot p95/p50 = 127.

2. `LONDON_OPEN_MOMENTUM / LONDON_OPEN_MR`: Rejected. While RIPPER rank-2 isolates
   `hour_utc=8.0-10.0` as part of a BUY condition, this rule achieves only
   match_rate_cv=0.531 (barely above random at 0.500) and its direction signal
   alone cannot explain the system's track record. The martingale mechanic is the
   dominant source of the reported 383% gain, not a London-session edge.

3. `UNCATEGORIZED`: Not applicable. The martingale evidence is unambiguous and
   quantitative — no ambiguity requiring the fallback family.

The broker (ForexMart, 1:500 leverage, MT4) is consistent with the martingale
profile: offshore/loosely regulated brokers are the natural habitat for martingale
EA vendors because (a) the 1:500 leverage enables the lot-doubling sequence to
run longer before hitting a margin call, and (b) the regulatory environment does
not require disclosure of open-position risk to retail investors. Confidence
reduced by 0.05 relative to a regulated broker (note: system is flagged REAL, not
Demo, so the usual Demo -0.10 penalty does not apply, but broker quality penalty
applies at -0.05).

## Rule derivation

No executable direction rule is produced. The instruction set mandates immediate
exit for MARTINGALE_GRID family. However, for completeness and Stage 3
documentation, the nominal direction candidates extracted from Stage 1 are
preserved below.

**Rank 1 — Decision Tree (match_rate_cv=0.569, coverage=1.00)**

The tree's dominant split is `bb_pos_20_2_H1 <= 0.54` / `> 0.54`, accounting for
48% of feature importance. The BUY regions are:
- `bb_pos_20_2_H1 IN (-0.63, 0.54)` AND `ema_dist_20_H4 <= 0.15` AND
  `atr_ratio_M15 <= 0.55` → BUY
- `bb_pos_20_2_H1 > 0.54` AND `ema_dist_20_H4 <= 2.35` AND
  `ema_dist_20_H1 <= 1.91` AND `bb_pos_20_2_M15 <= 0.69` → BUY
- `bb_pos_20_2_H1 > 0.54` AND `ema_dist_20_H4 <= 2.35` AND
  `ema_dist_20_H1 > 1.91` → BUY (both sub-leaves)
- `bb_pos_20_2_H1 > 0.54` AND `ema_dist_20_H4 > 2.35` AND
  `atr_ratio_M5 > 0.39` → BUY

The thresholds are taken verbatim from candidates.json rank-1 tree output:
`bb_pos_20_2_H1` splits at 0.54, -0.63, -1.20, 0.91; `ema_dist_20_H4` splits at
0.15, 2.35; `ema_dist_20_H1` split at 1.91; `bb_pos_20_2_M15` split at 0.69;
`atr_ratio_M15` split at 0.55; `atr_ratio_M5` split at 0.39. All values are
verbatim from candidates.json — none invented.

**Rank 2 — RIPPER (match_rate_cv=0.531, coverage=1.00)**

Single rule: `close_vs_session_open_M15 = 1.0 AND bb_pos_20_2_H1 >= 0.96 AND
hour_utc IN [8.0, 10.0]` → BUY. The threshold `bb_pos_20_2_H1 >= 0.96` is from
candidates.json rank-2. This indicates a "price above session open on M15 AND H1
price near/above upper Bollinger band AND London open session" → BUY momentum.
But the 0.531 match_rate is not a usable signal independently.

**Key observation on direction bias:**

The direction_by_pair data shows AUDUSD has buy_pct=24.7% (heavily sell-biased)
while EURCHF has buy_pct=62.1% (moderately buy-biased). The hour-level buy_pct for
the top-5 hours is all close to 47-53%. This near-perfect balance is consistent
with a system that accumulates in both directions independently (a grid), not one
with a clean directional signal. The tree's 0.569 accuracy over a balanced 50/50
target is 6.9pp above chance — economically meaningless in a martingale context
where lot sizes swamp signal contribution to PnL.

**Univariate candidates (ranks 4-10):**

The best univariate predictor is `bb_pos_20_2_M15 > 0.06628` → BUY with
match_rate_cv=0.579 (rank 9 by score, rank 4 by magnitude above baseline).
Threshold is verbatim from candidates.json rank-9: `> 0.06628`. This is a
"price above midpoint of M15 Bollinger band" = momentum buy. But 0.579 at 50%
coverage means only 29% of trades are correctly classified beyond chance — not
a replicable signal.

## Confidence breakdown

- Family identification: 0.95 — lot p95/p50=126.96 with explicit Stage 1 FAIL
  flag; k1 flag text verbatim matches martingale criterion; hold-time NaN
  corroborates overlapping positions. The 0.05 residual uncertainty is solely
  from not having inspected individual trade-level lot sequences directly.
- Direction rule: 0.10 — all match_rate_cv in range [0.500, 0.579]; none above
  the 0.65 threshold required per system instructions for confidence > 0.5.
  The "direction" extracted is noise-level signal overwhelmed by martingale sizing.
- Exit logic: 0.05 — hold time NaN; exit_kind=manual_or_time covers the whole
  sample but no clean time-based exit can be extracted when positions overlap.
- Overall: 0.95 × 0.5 + 0.10 × 0.25 + 0.05 × 0.25 = 0.51 weighted, but
  family identification is the dominant axis per the taxonomy rules. Family
  confidence reported as headline figure = **0.95**.

## Open questions (para Stage 3 + posteriores)

- Stage 3 replicator must **immediately exit with MARTINGALE_GRID** verdict and
  not attempt PnL replication. The reliability score for this system is definitionally
  0 under the mandate ("MARTINGALE_GRID — Sair imediatamente").

- If the vendor's direction signal were extracted in isolation (ignoring lot
  dynamics) for academic purposes only: the `bb_pos_20_2_H1` breakout at H1 level
  combined with `ema_dist_20_H4` trend filter is structurally similar to a
  LONDON_OPEN_MOMENTUM skeleton (RIPPER places it at 08-10 UTC), but the 0.531
  match rate makes this hypothesis untestable without substantially more data.

- The 03:00 UTC peak (Tokyo overlap) with 522 trades vs the 10:00 UTC secondary
  (325 trades) suggests the system may run two separate grid "sleeves" — one opened
  during Asian session and averaged-in through London open. This multi-sleeve
  structure is a known pattern in commercial EA martingale grids and is consistent
  with the ForexMart + MT4 execution environment.

- The equity/balance ratio on the MyFxBook profile at time of capture is 86.75%
  ($8,389 equity vs $9,670 balance), implying approximately $1,281 in unrealized
  floating loss at snapshot time — consistent with an open averaging-in sequence.
  This is the characteristic "below-water" state of a martingale grid between
  winning and losing cycles.

- No Stage 4 or Stage 5 work is warranted. This system is disqualified at the
  sanity gate level.

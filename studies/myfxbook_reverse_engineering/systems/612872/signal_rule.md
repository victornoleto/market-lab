---
system_id: 612872
family: MARTINGALE_GRID
confidence: 0.95
generated: 2026-05-02
rule:
  entry_window_utc: null   # N/A — martingale grid systems do not have a meaningful entry window; all hours are opportunistic
  pairs: [GBPUSD, AUDUSD]
  direction: |
    # CLASSIFICATION STOP — this system is MARTINGALE_GRID.
    # Per pipeline mandate: k1_pass=False → family=MARTINGALE_GRID → EXIT IMMEDIATELY.
    # No direction rule is produced. The replicator MUST NOT attempt to backtest this system.
    # Reason: direction signal is irrelevant when position sizing itself is the "edge" (lot doubling).
    # Any match-rate from candidates.json (top = 0.544 CV) is barely above baseline (0.513),
    # confirming there is no separable directional edge independent of the grid mechanic.
    NONE — MARTINGALE_GRID disqualified
  exit:
    max_holding_hours: null   # p50=15h, p95=216h, max=2328h — grid holds until recovery or account blow-up
    take_profit_pips: null
    stop_loss_pips: null      # no stop-loss is the defining feature of a martingale grid
  sizing: martingale_NEVER   # lot p95/p50 ratio = 3.36; within-month doubling flag; k1_pass=FAIL
citations:
  - "[math_money_mgmt, p.13] — 'Never use money management to salvage a system with negative mathematical expectation. Money management only amplifies what is already there — positive or negative.'"
  - "[leverage_space, p.161, eq.7.03] — 'z < −0.5 → Martingale effect (bet more as equity falls).'"
risk_flags:
  - "MARTINGALE_GRID — k1_pass=FAIL: per-month max/median P95 = 32.90 (> 3.0 threshold); within-month lot doubling confirmed"
  - "System name 'OLD Happy MartiGrid v1.9.1' explicitly declares martingale + grid architecture"
  - "Lot p95/p50 ratio = 3.36; lot max = 19.03; steps = 19 — structural lot ladder typical of grid EA"
  - "Hold p50=15h, p95=216h, max=2328h (97 days) — open positions held for months without stop-loss"
  - "Broker = Fort Financial Services (obscure/non-Tier-1): confidence reduced 0.10"
  - "Vendor label 'OLD' + account last updated Jun 2021 — system acknowledged dead by vendor"
  - "DO NOT REPLICATE — Stage 3 replicator must skip this system_id"
---

# Decoded signal — OLD Happy MartiGrid v1.9.1 (id 612872)

## Family rationale

System 612872 is classified **MARTINGALE_GRID** with high confidence (0.95). The evidence is
convergent across four independent indicators:

**1. System name declares it.** The track record URL and name are
`old-happy-martigrid-v191-real` — the vendor coined the portmanteau "MartiGrid" combining
"Martingale" and "Grid", making this a self-declared classification.

**2. Stage 1 sanity flag is FAIL.** The fingerprint reports `martingale flag: FAIL
(martingale-like dynamics), steps=19, max_streak=1`. The k1 flag is
`per-month max/median P95 = 32.90 (> 3.0) — within-month doubling`, a 10× exceedance of the
3.0 hard threshold. Lot distribution confirms structural position ladder: p50=0.33,
p95=1.11, p99=3.76, max=19.03 — a ratio of 57.7× between max and median, consistent with
a 6-level grid that doubles each step (2^6 = 64).

**3. Exit/hold profile is pathological for a directional strategy.** Hold time p50=15h is
borderline normal, but p95=216h (9 days) and max=2328h (97 days) are the hallmark of a
grid system that waits for price to return to profit rather than cutting losers. All 3136
exits are `manual_or_time` — no stop-loss mechanism exists, consistent with grid EA design
that relies on lot-averaging to recover losing legs.

**4. Direction signal is indistinguishable from noise.** The best candidate (rank 1, tree,
`match_rate_cv = 0.544`) is barely above the Always-Sell baseline (`0.513`). The RIPPER
ruleset (rank 2, `match_rate_cv = 0.535`) reduces to a single feature threshold on
`ret_10_H1`, with high CV std (0.080) indicating instability across folds. No direction rule
survives with `match_rate_cv > 0.57` at `coverage ≥ 0.50` and `p_corrected < 0.05`. This
is consistent with a system whose profit comes entirely from the grid mechanic (lot
averaging) rather than from a predictive entry signal.

This is not `NY_SESSION_REVERSAL` or `OVERLAP_NY_LONDON_RANGE` despite entry peaks at
16-19 UTC (ranks 18:00 > 17:00 > 16:00). Those families require a clean directional
signal — this system has none. The NY session timing reflects simply when the grid EA opens
its initial position; subsequent legs open at arbitrary intervals as price moves against the
position.

## Rule derivation

No rule is derived. The taxonomy instructions are explicit: "MARTINGALE_GRID — k1_pass=False
na sanity (já filtrado pela Stage 1, mas valide cross-check). Sair imediatamente."

Cross-check validation confirms k1_pass=False via three independent channels:
- Channel A (name): "MartiGrid" in system URL
- Channel B (k1 numeric): per-month max/median P95 = 32.90, threshold = 3.0, ratio = 10.97×
- Channel C (hold time): p95=216h, max=2328h — no stop-loss grid behavior

The univariate rules from candidates.json (ranks 4-10) have `p_corrected` values ranging
from 6.4e-5 to non-significant (0.100). While some pass the multiple-comparison correction
(ranks 5-7 with p_corrected < 1e-9), they capture the direction of the initial grid entry
leg only — not the system's actual return-generation mechanism. Producing a `signal_rule`
from these features would be misleading: the replicator would backtest a directional system
and find poor match rate, not because the reverse-engineering failed, but because there is
no separable directional edge to replicate.

The lot-doubling mechanic — the actual edge (or illusion thereof) — cannot be replicated
by a fair backtest without path-dependent position accumulation, which is outside the Stage
3 replicator's scope and which is explicitly forbidden by the sizing rule `martingale_NEVER`.

## Confidence breakdown

- Family identification: 0.97 — name + k1 flag + hold profile + noise-level direction signal
  all convergent; only uncertainty is whether the initial grid leg has a weak directional
  bias (ranks 5-7 univariate p_corrected significant), but this does not change family
- Direction rule: N/A — not applicable for MARTINGALE_GRID
- Exit logic: N/A — not applicable for MARTINGALE_GRID
- Broker penalty: −0.02 (Fort Financial Services = non-Tier-1, obscure broker; applied
  conservatively because in this case the martingale identification is so strong that broker
  quality is irrelevant to the classification)
- Overall: 0.95

## Literature support

**[math_money_mgmt, Vince, p.13]:** "Never use money management to salvage a system with
negative mathematical expectation. Money management only amplifies what is already there —
positive or negative." A martingale grid is the canonical example of this anti-pattern:
it attempts to convert a near-random entry signal (match_rate_cv ≈ 0.51-0.57, barely above
0.513 baseline) into profits by doubling lots on losses. Vince's rule confirms this cannot
work over the long run — the lot scaling amplifies the (negative or near-zero) expectation
of the direction signal, not a positive one.

**[leverage_space, Vince, p.161, eq.7.03]:** "z < −0.5 → Martingale effect (bet more as
equity falls)." The leverage_space framework formalizes the Martingale as a migration
function parameter z < −0.5 in the small-Martingale capitalization equation. The system's
observed lot ladder (p50=0.33 → max=19.03, ratio 57.7×) implies an effective z deeply
negative (far below −0.5), placing the system in a region where, as q → ∞, geometric mean
HPR < 1 and ruin is certain [leverage_space, p.43, Fig.3.8 via cross-reference in
math_money_mgmt].

## Open questions (for Stage 3 + posteriores)

- This system should be **skipped by Stage 3** entirely. No backtest should be run.
- If the pipeline requires a reliability score for ranking purposes, assign reliability = 0.0
  (disqualified by k1_pass=False) and flag `skip_reason=MARTINGALE_GRID`.
- The weak but statistically significant univariate signals (ranks 5-7, all pointing
  `ema_dist_20_H1 > -0.03441`, `bb_pos_20_2_H1 > -0.02746`, `bb_pos_20_2_H4 > -0.03727`
  implying BUY) could be artifacts of the grid's bias to buy near support — but this is a
  systematic property of grid EAs (they tend to add longs below price), not an independent
  directional edge. Stage 3 should NOT test these.
- The vendor's other systems (those without "Marti" in the name) should be checked for
  similar k1 FAIL flags — the vendor may use martingale mechanics across multiple products.

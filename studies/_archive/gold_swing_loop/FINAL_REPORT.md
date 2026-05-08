# Gold Swing Loop — Final Report (paused 2026-04-26)

**Status**: PAUSED, **0 winners found** in 25 iterations + 1 rule
relaxation pass. User decision to stop and revisit later.

**Generated**: 2026-04-26 19:15  (loop killed at iter 026 mid-run, dir
cleaned)

---

## Executive summary

After 25 iterations across 2 phases (15 under original rules + 10 under
relaxed rules), **no strategy passed even the PROMISING tier (≥60)** on
the gold day/swing problem.

| phase | iters | best score | best tier | rules |
|---|---|---|---|---|
| Phase 1 (original) | 1-15 | **50** (3 iters: 011/012/013) | MARGINAL | strict 5/5 + ≤5d hold |
| Phase 2 (relaxed) | 16-25 | **35** (5 iters) | NEAR_FAIL | multi-asset + 3 hold tracks + futures path + primary/corroborating |

**The relaxation made scores LOWER on average**, not higher. Reason:
relaxed rules let new ideas be tested, but those new ideas don't have
edge — they hit the floor of "doesn't destroy the portfolio" (~35) but
don't generate +0.10 Sharpe edge anywhere.

---

## Decision: pause indefinitely

The gold day/swing problem appears **structurally limited**. The user
decided to halt at iter 25 (2026-04-26 19:05) without reaching the
planned 100-iter target. Loop can be resumed in the future without loss
— full state preserved on branch `gold-swing/iter-001`, worktree at
`/tmp/ai-trade-gold-swing`.

---

## Top-K (best across both phases)

| rank | iter | rules | score | tier | strategy slug | key takeaway |
|---|---|---|---|---|---|---|
| 1 | 011 | v1 | 50 | MARGINAL | `vol-regime-gate-inverse` | first +Sharpe edge bench on 2/3 ds; 44d swing-extended (failed legacy ≤5d hold) |
| 2 | 012 | v1 | 50 | MARGINAL | `ic7-rsi2-volregime-composition` | iter 003 + 011 Markowitz; gld MDD halved 46→25% |
| 3 | 013 | v1 | 50 | MARGINAL | `volregime-inverse-sma200` | iter 011 + Connors SMA(200); 22d swing-ext |
| 4 | 016 | v2 | 35 | NEAR_FAIL | `ic7-rsi2sma200-dxytrend` | first iter under v2; ic7 composition |
| 5 | 003 | v1 | 22 | NEAR_FAIL | `connors-rsi2-sma200-filter` | 1st +Sharpe 3/3 single-mech; macro-clock-bound |

**Top 3 are all v1 vol-regime-inverse family** — the only axis that
generated any Sharpe edge. None passed strict winner gates (failed on
DSR or hold-time).

---

## Phase 1 (iters 1-15, original rules) — what was tested

| iter | strategy | tier | score |
|---|---|---|---|
| 01 | Connors RSI(2) | FAIL | 18 |
| 02 | Donchian 20/10 turtle | FAIL | 11 |
| 03 | RSI(2) + SMA(200) filter | NEAR_FAIL | 22 |
| 04 | VIX recovery 5d | FAIL | 16 |
| 05 | DXY z-score recovery | FAIL | 0 |
| 06 | Pre-FOMC drift | FAIL | 15 |
| 07 | Z-score MR 1h intraday | FAIL | 16 |
| 08 | XAU-XAG pair MR | FAIL | 0 |
| 09 | XAU-XAG pair trend | FAIL | 1 |
| 10 | Vol-regime gate σ60>σ252 | NEAR_FAIL | 22 |
| **11** | **Vol-regime gate INVERSE** | **MARGINAL** | **50** |
| **12** | **iter003 + iter011 Markowitz** | **MARGINAL** | **50** |
| **13** | **iter011 + SMA(200) filter** | **MARGINAL** | **50** |
| 14 | TIPS DFII10 macro stream | NEAR_FAIL | 26 |
| 15 | DXY SMA slope trend gate | FAIL | 17 |

**Key insight**: only the **vol-regime-inverse** mechanism produced any
Sharpe edge. Mean-reversion (RSI2, BB), trend (Donchian, MA), pair
trades (XAU-XAG), calendar effects (FOMC), and macro overlays (DXY,
TIPS) all failed.

**Why vol-regime-inverse worked partially**: when σ_60d < σ_252d (gold
is in vol compression), the asset enters a directional phase →
trend-follow with simple long position. Iter 010 (the opposite gate)
failed; the inverse direction captured a real but weak structural
property of gold.

**Why it didn't reach winner**:
- Mean hold 22-44 days (medium swing) → failed legacy ≤5d hard gate
- DSR p > 0.20 on gld_long (cumulative n_trials drains fast)
- Edge fragile across the 2020+ window

---

## Phase 2 (iters 16-25, relaxed rules) — what was tested

Rules relaxed 2026-04-26 after Phase 1 plateau:

1. Universe: `single_xau` ⟶ also `gold_complex` (XAU≥40% + XAG/SLV/GDX/PT)
2. Hold-time: `≤5d hard gate` ⟶ 3 declared tracks
3. Cost path: `pep_cfd` only ⟶ also `cme_futures` and `inter_etf`
4. Datasets: added `gold_synth_40y` (deferred construction)
5. Cross-dataset: `3/3 strict` ⟶ `primary + corroborating`

| iter | strategy | direction | tier | score |
|---|---|---|---|---|
| 16 | ic7-rsi2sma200-dxytrend | composition | NEAR_FAIL | 35 |
| 17 | cftc-cot-briese-ruggiero | COT positioning | NEAR_FAIL | 28 |
| 18 | cot-zscore-variant | COT positioning | NEAR_FAIL | 35 |
| 19 | ic7-rsi2sma200-cotzscore | composition | NEAR_FAIL | 35 |
| 20 | 3stream-ic7-rsi2-cot-dxytrend | 3-stream IC-7 | NEAR_FAIL | 35 |
| 21 | dcot-mm-zscore | DCOT money mgr | NEAR_FAIL | 28 |
| 22 | gvz-implied-vol-regime | gold VIX | NEAR_FAIL | 28 |
| 23 | **multi-asset-gld-slv-basket** | **gold_complex** | NEAR_FAIL | 35 |
| 24 | **gld-gdx-cross-cluster-basket** | **gold_complex** | NEAR_FAIL | 30 |
| 25 | **gld-btc-cross-cluster-basket** | **gold_complex** | NEAR_FAIL | 35 |

**Direction families tested under v2:**

- **CFTC COT positioning** (3 iters): all NEAR_FAIL. Money manager
  z-score, Briese-Ruggiero net positions, disaggregated COT — none
  generated +0.10 Sharpe edge.
- **Gold VIX (GVZ) regime** (1 iter): NEAR_FAIL. CBOE Gold VIX as
  regime classifier failed.
- **Multi-asset gold_complex** (3 iters): GLD+SLV, GLD+GDX, GLD+BTC
  baskets — all NEAR_FAIL. The relaxation that was theoretically the
  highest-leverage failed too.
- **IC-7 compositions** (3 iters): re-mixing prior signals via
  Markowitz proportional weighting — plateau at 35.

**Why multi-asset failed (specific to gold)**: gold/silver/miners are
correlated ρ ≈ 0.6-0.8. Unlike equity+bonds (ρ ~ 0) which gave the
sister loop its 90/60 stack winner, the gold cluster has insufficient
diversification spread to extract Sharpe edge. GLD+BTC was the only
one with low correlation but BTC's vol structure is too noisy for
swing-style allocation.

**Why no v2 iter beat 35**: the score floor of 35 = CAGR-floor pass
(15) + MDD-ceiling pass (15) + DSR p<0.20 (5) when no Sharpe edge
exists. None of the v2 strategies generated the +0.10 Sharpe edge
needed to exit this floor.

---

## Why this is structurally hard (hypotheses)

1. **Gold is 80% macro-driven** — real rates, USD, geopolitics. Pure
   technical signals (RSI, trend, vol regime) capture ~10% of the
   variance. Macro signals (TIPS, DXY) tested individually didn't help
   either — the signal-to-noise ratio of those macro series at daily
   frequency is too low.

2. **Single-asset universe** — the sister loop's clear winner pattern
   was multi-asset diversification (equity+bond+gold). Gold single-asset
   doesn't have the orthogonal hedge structure that 90/60 SPY+ZROZ has.
   Multi-asset gold-only baskets (Phase 2) didn't help because gold
   complex assets are mutually correlated.

3. **Pepperstone CFD costs** — 8 bps spread + swap kills intraday
   strategies before they start. v2 added futures path (1-2 bps) but
   no Phase 2 iter actually used `cme_futures` cost path — probably
   because the iters defaulted to `pep_cfd` and didn't take advantage.

4. **Limited literature** — sister loop drew from 16 books with rich
   equity-systematic content (Sinclair, Clenow, Connors, Antonacci,
   Faber, Asness, etc.). Gold has fewer canonical systematic-trading
   sources beyond Erb-Harvey 2006 (carry-component decomposition) and
   COT-based papers (Briese, Ruggiero) — the literature surface area is
   smaller, so iter ideas converge faster.

5. **Cumulative DSR drain** — after 25 cfgs tested, the n_trials
   adjustment makes any new strategy need Sharpe ~1.4-1.5 to clear DSR
   p<0.05. None of the candidates approached that.

---

## Dead-ends discovered (gold-specific, beyond inherited IC-1..IC-8)

Add to `DEAD_ENDS.md` if reactivating:

- **GS-A** (single mech): Connors RSI(2) on gold daily — score 18,
  closed at iter 001. Bench Sharpe edge < 0.05.
- **GS-B**: Donchian 20/10 turtle on gold — score 11, iter 002. Whipsaw
  on gold's choppy regimes.
- **GS-C**: VIX recovery 5d as gold signal — score 16, iter 004. Gold's
  flight-to-quality response is regime-conditional, weak overall.
- **GS-D**: DXY z-score recovery — score 0, iter 005. DXY-gold inverse
  correlation is too noisy at daily frequency.
- **GS-E**: Pre-FOMC drift event — score 15, iter 006. Effect documented
  in literature but doesn't survive Pepperstone costs.
- **GS-F**: XAU-XAG pair MR/trend — scores 0/1, iters 008/009. Pair is
  structurally cointegrated but mean-reversion too slow for swap-free
  hold; trend whipsaws.
- **GS-G**: TIPS DFII10 / DXY SMA slope macro overlays — scores 26/17,
  iters 014/015. Daily macro signals lack predictive power on net-cost
  basis.
- **GS-H** (NEW from Phase 2): CFTC COT positioning (3 variants) —
  scores 28-35, iters 017/018/021. Briese-Ruggiero, Money Manager
  z-score, disaggregated COT all plateau at NEAR_FAIL. COT signal too
  slow (weekly release) for any sub-monthly hold.
- **GS-I** (NEW): GVZ implied vol regime — score 28, iter 022. Gold VIX
  doesn't add edge over realized vol regime gates (already tested).
- **GS-J** (NEW): Multi-asset gold_complex baskets — scores 30-35,
  iters 023-025. GLD+SLV (high corr), GLD+GDX (high corr), GLD+BTC
  (BTC too noisy) all NEAR_FAIL. **The multi-asset relaxation does NOT
  rescue gold** — unlike equity multi-asset which is the canonical
  winner pattern in the sister loop.
- **GS-K**: Phase 2 score floor at 35 = CAGR floor + MDD ceiling + DSR
  partial. Any strategy that doesn't generate +0.10 Sharpe edge on
  primary will plateau here regardless of universe/track/path.

---

## What was NOT tried (deferred to future reactivation)

If the loop is reactivated:

1. **`cme_futures` cost path** — relaxation #3 enabled it but no Phase
   2 iter actually used it. Strategies that died on 8 bps PEP CFD
   (intraday MR, scalping) might survive on 1-2 bps GC futures.
2. **`gold_synth_40y` dataset** — deferred construction. Sister loop's
   key validation came from 40y testfolio synth. Gold equivalent
   would let Phase 1's vol-regime-inverse (the only working axis)
   be re-tested across 1986-2026 (Volcker, GFC, COVID).
3. **`medium_swing` track** — declared but not deeply explored. Gold has
   natural 10-30d cycles (FOMC, Indian wedding season, geopolitical
   surges) that the legacy ≤5d gate killed.
4. **Gold + equity multi-asset** — the sister loop showed gold as 30%
   sleeve in 90/60/30 (iter 035) gave the best 40y result. That's
   technically a sister-loop win, not gold-loop, but a hybrid loop
   testing "gold as portfolio sleeve" rather than "gold standalone"
   is the natural successor.

---

## Recommendation for future reactivation

When (if) revisiting this problem, the highest-EV directions are:

1. **Pivot scope**: instead of "gold standalone strategy", run "gold as
   sleeve in multi-asset portfolio with equity+bond". This is sister
   loop iter 035's structure. Could be a new loop
   (`studies/gold_sleeve_loop/`) rather than a continuation.

2. **Use `cme_futures` cost path**: if continuing standalone-gold,
   redo intraday MR / scalping iters with 1-2 bps futures spread
   instead of 8 bps CFD. Several intraday strategies died on
   transaction cost alone.

3. **Build `gold_synth_40y`**: construct from FRED `PCU2122212122` or
   LBMA daily fixing. Re-test Phase 1's vol-regime-inverse on the
   40y window — if it survives, that's a genuine winner with relaxed
   hold tracks.

4. **Acknowledge the literature ceiling**: gold standalone has fewer
   systematic-trading papers than equity. If continuing, fund
   research time for arxiv/SSRN deep-dives on gold microstructure
   (e.g., Cheung et al. on intraday vol patterns, Naef on FX-gold,
   Erb-Harvey decomposition) before more iters.

---

## State preserved (for resume)

- Branch: `gold-swing/iter-001`
- Worktree: `/tmp/ai-trade-gold-swing` (delete with `git worktree remove`
  if not resuming soon)
- Main repo path: `/var/www/pessoal/ai-trade`
- Last commit: `366cdf6 gold-swing: iter 025 — iteration 025`
- BASE_MEMORY: `studies/gold_swing_loop/BASE_MEMORY.md` (frontmatter
  shows `total_iterations: 25`, `cumulative_n_trials: 25`,
  `winners_found: 0`, `rules_version: 2026-04-26-relaxed-r1`)
- DEAD_ENDS catalog: `studies/gold_swing_loop/DEAD_ENDS.md` (inherited
  IC-1..IC-8 + gold-specific GS-1..GS-N entries)

To resume: `cd /tmp/ai-trade-gold-swing && MAX_ITER=N nohup bash
studies/gold_swing_loop/run_loop.sh > /tmp/gold_swing_resume.out 2>&1 &`

---

## Files referenced in this report

- `BASE_MEMORY.md` — full iteration log + rule changes
- `DEAD_ENDS.md` — IC-1..IC-8 inherited + GS-* gold-specific
- `WINNER_AND_RANKING.md` — strict 5+1 conditions (v1) and
  primary/corroborating (v2)
- `INFRASTRUCTURE.md` — datasets + dual-broker cost paths
- `PROMPT.md` — per-iter execution stages
- `scoring.py` — `score_strategy` (v1) + `score_strategy_v2` (relaxed)
- `iterations/NNN-*/verdict.json` — per-iter machine-readable result
- `iterations/NNN-*/final_report.md` — per-iter human-readable analysis
- Sister loop reference: `../strategy_hunt_loop/` (54 iters, 3 winners
  found by iter 16/35/74 in equity space)

---

## Honest verdict

The gold day/swing hunt was a **negative result that's still informative**.

What we know after 25 iters:
- Gold standalone short-hold has Sharpe ceiling ~0.7-0.8 net of
  Pepperstone costs (vs ~1.0 buy-hold) → no clear deploy candidate.
- Multi-asset gold-only baskets (relaxation #1) don't escape the
  ceiling — gold cluster correlation kills the diversification benefit.
- The vol-regime-inverse axis is the one real signal found, but it
  produces medium-swing strategies (22-44d hold) that never passed the
  strict winner gates.

**Don't deploy anything from this loop.** The Plano A reactivation
slot remains DORMANT per mandate §1. If reactivating gold trading in
the future, the sister loop's iter 035 (gold as 30% sleeve in 90/60/30
multi-asset stack) is the **only research-validated path** for gold
exposure that beats benchmarks across 17y and 40y windows.

Loop paused 2026-04-26 19:05 by user decision. Future revisit welcome,
no urgency.

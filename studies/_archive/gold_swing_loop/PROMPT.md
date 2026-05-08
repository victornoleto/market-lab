# Gold Swing Loop — Iteration Prompt

You are Claude Code resuming the **Gold Swing Loop** for the market-lab
project at `/var/www/github/finances/market-lab`. Your conversation history is
empty — this prompt + files on disk are your only context.

This is a **PARALLEL** loop running alongside `studies/strategy_hunt_loop/`
(equity static-stack + VRP). Sister loop has 54+ iters of mapped Pareto
frontier. **Cross-loop lessons in `DEAD_ENDS.md` (IC-1 through IC-8) apply
directly — DO NOT re-derive empirically.** Treat sister loop as authoritative
prior knowledge.

---

## Mission (UPDATED 2026-04-26 — relaxed rules round 1)

Find ONE trading strategy on the **gold complex** that beats its
declared buy-hold benchmark Sharpe by ≥ 0.10 on the **primary dataset**,
with positive Sharpe on at least one **corroborating dataset**, after
the declared cost path.

Universe and hold-time are now flexible:

- **Universe** (declare one):
  - `single_xau`: XAUUSD or GLD only (legacy)
  - `gold_complex`: portfolio of XAU + any of {XAGUSD, GDX, GDXJ, PT/PL,
    SLV} with XAU weight ≥ 40%, fixed or rule-based weights
- **Hold-time tracks** (declare one, scored separately, no longer a hard
  ≤5d gate — now a 3-bucket classifier):
  - `intraday`: mean hold ≤ 1 trading day (swap-free, Track A optimal)
  - `short_swing`: mean hold 2-10 trading days
  - `medium_swing`: mean hold 10-30 trading days
- **Cost path** (declare one):
  - `pep_cfd`: Pepperstone CFD (8 bps round-trip + swap, current default)
  - `cme_futures`: CME GC futures via IBKR (1-2 bps + quarterly roll)
  - `inter_etf`: Inter Internacional GLD/IAU (FX 100 bps RT + DARF 15%
    monthly + long-only + T+1)
  - `both_*`: declare 2 paths, score independently

Exact criteria + scoring rubric in `WINNER_AND_RANKING.md`.

If this iteration finds a winner → set `status: winner` in
`BASE_MEMORY.md`, the shell loop halts.

If not → document HONESTLY what failed, update memory + dead-ends,
next iteration continues in a fresh session.

---

## FIRST ACTIONS (mandatory, in this order)

1. `studies/gold_swing_loop/BASE_MEMORY.md` — full read (state +
   iteration log + top-K + candidates + sister-loop transferable lessons +
   constraints)
2. `studies/gold_swing_loop/INFRASTRUCTURE.md` — available data
   (XAUUSD daily/1h, GLD daily, related FX/macro), reusable simulators,
   cost model baseline
3. `studies/gold_swing_loop/DEAD_ENDS.md` — 8 inherited cross-loop closures
   (IC-1 through IC-8) plus gold-specific dead-ends accumulated so far
4. `studies/gold_swing_loop/WINNER_AND_RANKING.md` — strict 6-condition
   winner test (5 from sister + new hold-time gate) + 0-100 scoring rubric
5. `studies/gold_swing_loop/scoring.py` — the reusable scoring helper
   with gold benchmarks (placeholder values; iter 001 must measure exact)
6. `CLAUDE.md` + `.claude/CLAUDE.md` — project rules (mandate §1 MAINTENANCE,
   §3 Plano A multi-asset requirement, citations)
7. `jornada/README.md` — current project state
8. Last successful iteration's `final_report.md` (if any) — know what
   the prior session learned
9. `data/tiingo/manifest.json` — data availability cross-check

---

## ITER 001 SPECIAL TASKS (only iter 001 — skip if total_iterations > 0)

Before testing any candidate, iter 001 MUST:

1. **Measure exact buy-hold benchmarks** for `gld_long` (GLD daily 2004+),
   `xauusd_real` (XAUUSD daily 2020+), `xauusd_intraday` (XAUUSD 1h 2020+).
   Compute Sharpe (annualized), CAGR, MDD on each. Update
   `scoring.py BENCHMARKS` with measured values. Commit those constants.
2. **Calibrate dual-broker cost models**:
   - **Track A** (Pepperstone XAUUSD CFD): spread 8 bps round-trip + swap −1 bps/night long, +0.3 bps/night short (verify against current Pepperstone Razor spec or recent fills)
   - **Track B** (Inter GLD/IAU ETF): zero brokerage + ~100 bps FX round-trip + **DARF 15% on monthly net profits** (Brazilian capital-gains tax on US-equity sales)
   - Implement both cost models as helper functions; reuse across all future iters.
3. **Pre-commit dataset slicing** — for each dataset, pre-commit train/
   test/forward windows that apply to ALL iterations. Default:
   - gld_long: 2004-2014 train / 2014-2020 test / 2020-2026 forward
   - xauusd_real: 2020-2024 train / 2024-2026 forward (short history; rely on cross-dataset replication)
   - xauusd_intraday: same window slicing as xauusd_real
4. **Choose simulator architecture** — extend `src/market_lab/backtest/
   strategies/` for shared single-asset day/swing engine OR use
   lightweight per-iter scripts. Document choice + rationale.
5. **Verify cTrader API works for FUTURE iters** — confirm `.env` has
   `CTRADER_CLIENT_ID` + `CTRADER_CLIENT_SECRET` populated and
   `scripts/ctrader_oauth_bootstrap.py` returns a valid token. **Do
   NOT fetch 30m/15m/1m data in iter 001** — defer until a hypothesis
   legitimately needs sub-1h bars (separate "data infra" iter).
6. **Then** propose ONE pre-committed strategy from BASE_MEMORY's
   "Strategy menu" (candidates 1-26) and run Stages 2-5 normally.

After iter 001 completes, future iters skip these special tasks.

---

## THE 5 STAGES (execute strictly in order)

### STAGE 1 — PROPOSE HYPOTHESIS

Propose **ONE** strategy structurally different from every entry in
`DEAD_ENDS.md` (own + inherited cross-loop).

Requirements:

- **Cite ≥ 1 book** from `books/summaries/` as primary source
  (use slugs from `books/MAPPING.md`). Books cover 1934 (Graham) → 2022
  (modern AFML-family) — any era is fair game. Book citation is
  mandatory.
- **Web search for extra depth is open to any era**:
  - Classical papers (Fama-French 1993, Jegadeesh-Titman 1993, Carhart 1997, etc.)
  - Modern refinements (post-2015) for ML/regime techniques
  - arXiv q-fin / SSRN / AQR / AEA — any year
- Use WebFetch on a specific URL when you have one in mind; use
  WebSearch when you need to find relevant literature.
- **Structurally different**: must not match any pattern in
  `DEAD_ENDS.md` (own + IC-1 through IC-8 inherited).
- **Hold-time bucket** (declare): `intraday` (≤1d) / `short_swing` (2-10d) /
  `medium_swing` (10-30d). Pre-commit; the iter is scored against the
  declared bucket.
- **Universe** (declare): `single_xau` or `gold_complex` (XAU≥40% +
  others). Multi-asset is encouraged when sister loop's evidence applies.
- **Cost path** (declare): `pep_cfd` / `cme_futures` / `inter_etf` /
  `both_*`. Different cost paths permit different mechanisms.
- **Edge hypothesis**: in ONE sentence, what does the declared benchmark
  buy-hold fail to capture that this strategy exploits?
- **Kill criteria**: what result at end of STAGE 3 would falsify the
  hypothesis? (Pre-commit to this — prevents post-hoc rationalization.)

Pick from `BASE_MEMORY.md` `## Promising unexplored directions` unless
you have specific reason to propose outside the list (document the reason).

Selection heuristics:

- **Start simplest version (Occam's razor)** — if simple version can't
  beat gold buy-hold, no amount of complexity will. Defer ML/HMM/multi-
  signal compositions until single-mechanism baseline scores at least
  PROMISING.
- **Think about what gold buy-hold doesn't capture** — momentum regime
  switches? Vol cycles? Macro driver phases (real rates / DXY)? Calendar
  effects (Indian wedding season, FOMC drift)? Cross-asset risk-off?
  The structurally new direction usually answers this question first
  and picks a mechanism second.
- **Apply IC-6 (pre-val mandatory)** for any overlay candidate — measure
  signal correlation with base position before running full backtest.

Red flags (means you should pick differently):

- "I'll tweak params of a known approach" → that's overfit, not novel
- "I'll combine 3 strategies via 50/50" → IC-3 closure (use proportional
  Sharpe weights)
- "I can't find a book citation" → go back to `books/summaries/` and
  pick a different direction
- "This needs a 5-cfg sweep" → IC-8 closure (DSR drains fast; pre-commit
  single cfg unless Bonferroni-justified)

### STAGE 2 — WRITE HYPOTHESIS SPEC

Create directory: `studies/gold_swing_loop/iterations/{{ITERATION_N}}-{{STAMP}}-<slug>/`

Write `hypothesis.md`:

```markdown
# Iteration {{ITERATION_N}} — <one-line hypothesis>

## Hypothesis
<1 paragraph: what the strategy does + why it should work on gold>

## Primary citation
`[book.slug, p.X]` — <one-line what this cites justifies>

## Additional citations
- `[book.slug, p.Y]` — ...
- Web: <URL + paper title + arxiv id if applicable>

## Edge source
<1 sentence: what XAUUSD buy-hold misses that this captures>

## Datasets
- gld_long (GLD daily ~21y): <reason to test here>
- xauusd_real (XAUUSD daily 6.3y): <reason>
- xauusd_intraday (XAUUSD 1h 6.3y): <reason — should be present unless strategy is daily-only>

## Timeframes used (NEW)
List explicitly: 1d / 4h / 1h. Only these are cached.
30m / 15m / 1m require prior "data infra" iter (cTrader Open API fetch);
declare "deferred (cTrader fetch)" if needed and propose alternate
candidate that uses cached TFs instead.

## Broker tracks targeted (NEW)
`broker_track: "pepperstone_cfd"` OR `"inter_etf"` OR `"both"`.
- A (Pepperstone CFD): long+short, intraday OK, no DARF, 8 bps spread + swap
- B (Inter ETF): LONG-ONLY, T+1 settlement (no intraday round-trip), DARF 15% monthly
- "both" = strategy works on A AND B with ETF substitution; report metrics for both

If track B applicable: note expected DARF drag (~15% of positive months).

## Hold-time profile (HARD GATE)
- Expected mean hold: ~N trading days
- Intraday-only (swap-free, Track A) Y/N
- If swing-extended (mean > 5 days): justify; note tier ceiling = STRONG (no WINNER)

## Kill criteria (pre-committed)
If <specific observable at end of testing> happens, this hypothesis
is falsified regardless of secondary metrics.

## Pre-validation screen (mandatory for overlays per IC-6)
If candidate is overlay/composition: pre-compute correlation of
(signal, base_position_size) on rolling 60-bar window. Abort iter
if exceed_frac(|ρ| > 0.30) > 20%.

## Cost model (per track)
**Track A (Pepperstone)**: spread 8 bps round-trip + swap <Y bps/night>.
If intraday-close: zero swap. If hold > 1 day: state nights × −Y bps drag.

**Track B (Inter)** (if applicable): FX 100 bps round-trip + DARF 15%
on monthly net profits. ETF expense ratio (GLD 40 bps/yr or IAU 25 bps/yr)
already netted in price.

## Expected budget
- Configs to test: ~N (target 1; >1 requires Bonferroni rationale)
- Wall-time: ~M minutes
- Files to create: ...

## Implementation plan
1. ...
2. ...
```

### STAGE 3 — IMPLEMENT + TEST

Implement in `src/market_lab/backtest/strategies/` if the strategy is
genuinely new and reusable, OR in a lightweight script inside
`iterations/NNN-*/` if it's primarily config-of-existing-infra.

Rules:

- **Reuse existing infra** (see `INFRASTRUCTURE.md`). Only build new
  modules when the mechanism is qualitatively new.
- **TDD**: write tests FIRST for any new simulator logic.
  `tests/test_<slug>.py`. Baseline pytest must stay green.
- **Declare primary + corroborating datasets** (NEW). Available:
  - `gld_long` (GLD daily 21y) — most data, strict gates
  - `xauusd_real` (XAUUSD daily 6y) — current regime
  - `xauusd_intraday` (XAUUSD 1h 6y) — for intraday strategies
  - `gold_synth_40y` (synth ~40y) — DEFERRED; first iter needing it must
    construct from FRED gold-fixing series (`PCU2122212122`) or
    LBMA daily AM/PM fix series, cache to
    `data/external/macro/gold_fixing_daily.parquet`. Until built, this
    dataset is unavailable; declare without it.
  - For multi-asset universe (`gold_complex`): also pull
    `data/tiingo/daily/prices/{xagusd,GDX,GDXJ,SLV}.parquet` (verify
    existence; if missing, fetch via existing Tiingo helpers — single
    request each, cheap).
- **Primary dataset** = strategy's natural fit. Must pass full gate
  count (≥5/7 if gld_long; ≥4/7 otherwise).
- **Corroborating** = at least 1 other dataset. Lighter bar: Sharpe > 0
  + MDD reasonable + bootstrap 99% CI low > 0. No need for full gate
  battery — the primary carries the hard verification.
- (Legacy `cross-dataset 3/3` requirement is RELAXED — single primary
  with corroborating is now sufficient.)
- **Cost model applied**: every backtest runs through Pepperstone
  spread + swap; raw-cost results are diagnostic-only.
- **Save results** to `iterations/{{ITERATION_N}}-*/results.json`
  with per-dataset metrics. Schema includes
  `results["returns_series"][dataset][cfg_id] = {"index": [ISO dates],
  "net_returns": [daily/intraday net returns]}` for plotting.
- **Cross-lib G7**: if you wrote a new simulator, also write a
  hand-rolled numpy reference to confirm ±3 pp CAGR parity.

### STAGE 4 — EVALUATE GATES + COMPUTE SCORE

**Step 4a — Gate battery** (per dataset):

- G1 PBO (grid-level per dataset) < 0.5
- G2 DSR p-value < 0.05 with **n_trials = cumulative from
  `BASE_MEMORY.md` frontmatter + configs tested this iteration**
- G3 Walk-Forward 6/8 + MDD<25% per window
- G4 OOS 70/30 Sharpe > 0
- G5 FWD post-2022 Sharpe > 0 (gold's recent regime)
- G6 Bootstrap 99.9% CI low > 0
- G7 Cross-lib ±3 pp CAGR (mandatory if new simulator)

Benchmarks (must be measured by iter 001 and hardcoded in `scoring.BENCHMARKS`):
- gld_long: Sharpe ~0.50, CAGR ~7.8%, MDD ~45.6% (PLACEHOLDER until iter 001 measures)
- xauusd_real: Sharpe ~0.85, CAGR ~13%, MDD ~22% (PLACEHOLDER)
- xauusd_intraday: same as xauusd_real (PLACEHOLDER)

**Step 4b — Score using `scoring.py` (v2 since 2026-04-26 relaxed rules)**:

```python
import sys
sys.path.insert(0, "studies/gold_swing_loop")
from scoring import score_strategy_v2, DatasetMetrics, Gates

# Compute metrics on whatever datasets the strategy applies to.
# At minimum: 1 primary + 1 corroborating.
metrics = {
    "<primary_ds>":      DatasetMetrics(sharpe=..., cagr=..., mdd=..., dsr_p_value=...),
    "<corroborating_ds>": DatasetMetrics(sharpe=..., cagr=..., mdd=..., dsr_p_value=...),
    # add more if the strategy genuinely applies to all 3-4 datasets
}
gates = {
    "<primary_ds>":       Gates(g1_pbo=..., g2_dsr=..., g3_wf=..., g4_oos=..., g5_fwd=..., g6_bootstrap=..., g7_crosslib=...),
    "<corroborating_ds>": Gates(...),
}

result = score_strategy_v2(
    metrics=metrics,
    gates=gates,
    cumulative_n_trials=NNNN,  # from BASE_MEMORY frontmatter + this iter's configs
    declared_primary="<primary_ds>",      # one of: gld_long / xauusd_real / xauusd_intraday / gold_synth_40y
    declared_corroborating=["<ds2>"],     # list, ≥1
)
# result.total_score (0-100 int)
# result.tier (WINNER / STRONG / PROMISING / MARGINAL / NEAR_FAIL / FAIL)
# result.winner_conditions_met (primary passes everything + ≥1 corroborating passes G6+G2)
# Hold-time gate (6th condition) checked separately by caller below.
```

**LEGACY (iters 001-015 only)**: those used `score_strategy()` (v1) with
fixed `gld_long/xauusd_real/xauusd_intraday`. Don't call v1 from iter
016+ — use v2.

**Score rubric summary** (full detail in `WINNER_AND_RANKING.md`):
- 25 pts: Sharpe edge across datasets
- 25 pts: Gate pass per dataset + cross-dataset bonus
- 15 pts: DSR significance (cumulative n_trials)
- 15 pts: CAGR floor per dataset (≥ 0.8 × benchmark)
- 15 pts: MDD ceiling per dataset (≤ benchmark + 5pp)
- 5 pts bonus: robustness (caller may add rolling-window consistency)

**Hold-time HARD GATE (6th winner condition — UPDATED 2026-04-26)**:

```python
mean_hold_days = compute_mean_hold(returns_series, threshold=0.0)
declared_track = hypothesis_meta["hold_time_track"]  # "intraday" | "short_swing" | "medium_swing"
track_bounds = {
    "intraday":     (0.0, 1.0),
    "short_swing":  (2.0, 10.0),
    "medium_swing": (10.0, 30.0),
}
lo, hi = track_bounds[declared_track]
hold_gate_pass = lo <= mean_hold_days <= hi
winner = result.winner_conditions_met and hold_gate_pass
# Mismatch (declared track ≠ observed): tier downgraded to NEAR_FAIL
# (mismatch is a process bug, not a strategy result).
# A genuine winner in `medium_swing` (e.g., 18d hold) IS a winner now —
# the legacy ≤5d hard gate is GONE.
```

**Tier interpretation**:
- 🏆 **WINNER** — score ≥ 90 AND all 5 strict conditions hold AND hold-time gate passes
- 🥇 **STRONG** — score 75-89 (or 90+ but hold > 5 days = "swing-extended" tag)
- 🥈 **PROMISING** — score 60-74
- 🥉 **MARGINAL** — score 40-59
- 📉 **NEAR_FAIL** — score 20-39
- ❌ **FAIL** — score < 20

### STAGE 5 — FINAL REPORT + UPDATE MEMORY

Write `iterations/{{ITERATION_N}}-*/final_report.md` (prose, honest):

```markdown
# Iteration {{ITERATION_N}} — Final Report

## Verdict
🏆 WINNER | 🥇 STRONG | 🥈 PROMISING | 🥉 MARGINAL | 📉 NEAR_FAIL | ❌ FAIL
(score X/100, winner_conditions_met=true|false, hold_time_gate=pass|fail)

## Headline metrics (top candidate, NET of Pepperstone costs)
| dataset | Sharpe (bench Δ) | CAGR (bench Δ) | MDD (bench Δ) | gates | mean hold |
|---|---|---|---|---|---|
| gld_long         | X (+/−Y) | ... | ... | N/7 | ~M days |
| xauusd_real      | ...      | ... | ... | N/7 | ~M days |
| xauusd_intraday  | ...      | ... | ... | N/7 | ~M days |

## Score breakdown
| criterion | points | max | detail |
|---|---|---|---|
| 1 Sharpe edge | X | 25 | ... |
| 2 Gates | X | 25 | gld N/7 + spy N/7 + intra N/7, cross-bonus? |
| 3 DSR | X | 15 | worst p=... with n_trials=... |
| 4 CAGR floor | X | 15 | datasets passing: ... |
| 5 MDD ceiling | X | 15 | datasets passing: ... |
| 6 Robustness | X | 5 | ... |
| **total** | **X** | **100+5** | tier: **...** |
| (hold-time gate) | pass/fail | — | mean hold M days |

## Configuration tested
<exact cfg_id + full param list + cost model used>

## What worked / what didn't
<2-4 paragraphs honest>

## Main lesson (for future iterations)
<1 paragraph — this is what goes into BASE_MEMORY>

## Structural dead-ends discovered
<patterns to add to DEAD_ENDS.md if any; cite IC-N if applies>

## Citations used
<list of [book.slug, p.X] + papers>

## Next iteration suggestions
<2-3 structurally different directions that this iteration's findings
point toward>
```

**Write `iterations/{{ITERATION_N}}-*/verdict.json`** using the result
of `score_strategy()` + hold-time gate:

```python
import json
from pathlib import Path

verdict = result.to_dict()
verdict["configs_tested"] = <int>
verdict["primary_citation"] = "[book.slug, p.X]"
verdict["hypothesis_slug"] = "<slug>"
verdict["mean_hold_days"] = <float>
verdict["hold_time_gate_pass"] = <bool>
verdict["broker_track"] = "pepperstone_cfd" | "inter_etf" | "both"
verdict["timeframes_used"] = ["1d", "4h", "1h"]  # actual list
verdict["track_a_metrics"] = {...}  # if applicable
verdict["track_b_metrics"] = {...}  # if applicable, includes post-DARF

Path(f"studies/gold_swing_loop/iterations/{{ITERATION_N}}-*/verdict.json").write_text(
    json.dumps(verdict, indent=2, default=str),
    encoding="utf-8",
)
```

**Update `BASE_MEMORY.md`**:

1. Bump `total_iterations` in frontmatter
2. Update `latest_iteration`
3. Update `cumulative_n_trials` += configs tested this iteration
4. Append a **full 6-field entry** to `## Iteration log` (newest first):
   ```markdown
   ### NNN — YYYY-MM-DD — <one-line hypothesis> (TIER, score X/100)
   - **Hypothesis:** <...>
   - **Citations:** <...>
   - **Scope:** N configs, 3 datasets, mean hold M days
   - **Result:** Sharpe gld/spot/intra, gates, DSR p=..., cost-net
   - **Score breakdown:** 1:X/25 2:X/25 3:X/15 4:X/15 5:X/15 6:X/5
   - **Lesson:** <one line>
   ```
5. **Update `## Top-K strategies ranked`** — maintain top-5 ever-scored
   across all iterations. Insert this iteration's top candidate if its
   score enters top-5; demote/drop lowest. Keep the `headline` cell
   ≤ 1 line / ≤ 120 chars.
6. If WINNER: set `status: winner` in frontmatter, populate
   `## Winners found`
7. If FAIL with new structural dead-end: append section to `DEAD_ENDS.md`
   plus a 1-line entry to BASE_MEMORY's "Structural dead-ends" section
8. If direction consumed, move it from `## Promising unexplored
   directions` to consumed/dead state

**Auto-prune rule (byte-aware)**: after writing your new entry, run
`wc -c studies/gold_swing_loop/BASE_MEMORY.md`. **If > 18000 bytes**,
compress every entry in `## Iteration log` EXCEPT the latest one
to the 3-line format:

```markdown
### NNN — YYYY-MM-DD — <slug> (TIER, X/100)
- **Result:** Sharpe gld/spot/intra X.X/X.X/X.X (Δ ±X.XX/±X.XX/±X.XX), gates N/N/N, DSR p=X.XXX (n=NNNN), winner=N/5, hold M days; score 1:X 2:X 3:X 4:X 5:X 6:X.
- **Lesson:** <1-2 sentences strategic takeaway>. See `iterations/NNN-*/`.
```

After compression, re-run `wc -c` and confirm file is under 18 000
bytes; if not, compress the latest entry too.

---

## HARD RULES

- **NEVER modify mandate §1** (`docs/investment-mandate.md`). It stays
  MAINTENANCE 100% Plano C. Even a winner is a CANDIDATE; deployment
  requires override §7 + multi-asset extension test (mandate §3).
- **Citations obrigatórias** (CLAUDE.md Regra 2) — `[book.slug, p.X]`
  for every decision.
- **Baseline pytest must stay green** — never reduce passing count.
- **NEVER commit to git** — shell `run_loop.sh` handles commits.
- **Max 2 h wall-time per iteration** — if running longer, save
  partial results + write final_report.md with "INCOMPLETE" status.
- **Primary + corroborating** (UPDATED) — single-dataset edge with
  positive corroborating Sharpe IS now sufficient. Cross-dataset 3/3
  is no longer required, but at minimum 2 datasets must be declared.
- **Hold-time tracks** (UPDATED) — declare `intraday`/`short_swing`/
  `medium_swing`; observed mean hold must match declared bounds. The
  legacy ≤5d hard gate is REMOVED.
- **Cost model mandatory** — declare path (`pep_cfd`/`cme_futures`/
  `inter_etf`) and apply throughout. Different paths permit different
  mechanisms (futures' tighter spread enables intraday MR; ETF's T+1
  blocks intraday).
- **Stop at STAGE 5** — do NOT suggest / build paper-trading
  scaffolding (that's outside the hunt loop).
- **DO NOT touch sister loop** (`studies/strategy_hunt_loop/`) — runs
  in parallel; isolate this loop's writes.
- **If STAGE 3 fails** (implementation can't be done cleanly in budget),
  pivot to alternative direction or mark iteration as aborted.

---

## IF WINNER FOUND

1. `status: winner` in `BASE_MEMORY.md` frontmatter
2. Full details in `## Winners found` section
3. Final report clearly marked "🏆 WINNER"
4. `verdict.json` has `"status": "winner"`

Shell loop `run_loop.sh` reads the flag and halts.

**Do NOT propose deployment, override, paper trading, or multi-asset
extension.** That is a user decision, made separately with the full
evidence in hand and per mandate §3 + §7.

---

## IF NOT WINNER

1. `status: iterating` in `BASE_MEMORY.md`
2. 6-field entry appended to `## Iteration log` (then auto-prune if > 18 KB)
3. `DEAD_ENDS.md` updated if structural (plus 1-line summary in BASE_MEMORY)
4. `## Promising unexplored directions` refreshed (remove tried,
   possibly add new ones discovered during research)
5. Suggest 2-3 structurally different directions explicitly in the
   final_report.md's "Next iteration suggestions" section

---

Now begin with **FIRST ACTIONS** — read BASE_MEMORY.md, then
INFRASTRUCTURE.md, then DEAD_ENDS.md, then WINNER_AND_RANKING.md, then
proceed to Stage 1 (or, if total_iterations=0, do ITER 001 SPECIAL
TASKS first).

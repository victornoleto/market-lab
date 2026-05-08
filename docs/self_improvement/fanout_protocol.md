# Fan-out sweep protocol (agent handbook)

**Status:** active when `SWEEP_MODE=fanout` is set in the environment
that launched `scripts/self_improve_loop.sh`. Legacy mode
(`SWEEP_MODE` unset or `off`) ignores this document entirely.

**Source spec:** `specs/self_improve_fanout_mode.md`.

**Audience:** the agent instance that runs inside one iteration of the
self-improvement loop. You have a fresh context — read this file in
full every time `memory.md` says `active_lead_registry` is non-null or
you are about to bootstrap a new sweep lead.

---

## 0. TL;DR

- Legacy loop: **1 iter = 1 Lead completo** — fine for atomic leads.
- Fan-out loop: **1 iter = 1 work unit** on a pre-declared sweep
  (bootstrap, or one ticker, or the aggregator — see below).
- Continuity across iters lives in a sidecar `registry.json` inside
  `reports/<phase>/<lead_slug>/`; `memory.md` only carries the pointer.
- Per-ticker output is two files (`<ticker>.json` + `<ticker>.md`)
  committed together with the registry update.
- Aggregator runs only when `tickers_pending == []`, produces
  `AGGREGATE.md` + jornada, and clears `active_lead_registry`.

---

## 1. Decision flow every iter

```
START iter
  │
  ▼
Read memory.md frontmatter.
  │
  ▼
active_lead_registry == null ?
  │
  ├── YES ─► Choose next pending lead from the phase spec.
  │        BOOTSTRAP (see §2). Write registry + update memory.md.
  │        EXIT iter (no ticker processed).
  │
  └── NO  ─► Load registry.json from the pointer. Validate schema v1.
           Dispatch on registry.status:
             ├── "pending"     → treat as "sweeping" for first ticker.
             ├── "sweeping"    → SWEEP ONE TICKER (see §3).
             ├── "aggregating" → AGGREGATOR (see §4).
             └── "done"        → clear active_lead_registry in memory.md;
                                 pick next pending lead → BOOTSTRAP.
```

**Hard rule:** never process more than one bucket of work per iter.
Never touch more than one ticker. Never skip the aggregator. If the
registry says `done` but `active_lead_registry` is still set, your
first job is to clear that pointer.

---

## 2. Bootstrap — first iter of a lead

Deliverables:

- New directory `reports/<phase>/<lead_slug>/`.
- `registry.json` written atomically (tmp→rename) with
  `status: "pending"`, full `configs` list, full `tickers_pending`
  list, empty `tickers_done`.
- `memory.md` frontmatter updated: `active_lead_registry:
  reports/<phase>/<lead_slug>/registry.json`.
- Iter counter bumped; history entry one-liner:
  `iter N — bootstrap <lead_id> registry (configs=M, tickers=K)`.

Steps:

1. Identify the next pending lead from the phase spec (e.g.
   `specs/phase_3_5a_plano_a_investigation.md`). Skip any lead already
   in `## Dead ends` or whose registry file says `status: done`.
2. Choose a stable `lead_slug` (snake_case, includes the lead id and a
   short family name — e.g. `t2_donchian_breakout_intraday`).
3. Derive `configs` **explicitly**: list every (strategy_family ×
   param_tuple × direction) that this lead will test. The registry
   is **immutable in `configs`**; add-ons force a new lead id (e.g.
   `T2b`).
4. Derive `tickers_pending`: the full universe for this lead, ordered
   deterministically (alphabetical by default). This order is the
   processing order — no randomness.
5. Cite per-config the book(s) behind the parameter choices in a
   `citations_seed` array (CLAUDE.md regra 2 applies to strategy
   decisions; this array satisfies it up-front for the whole sweep).
6. Write `registry.json` with `schema_version: 1` (see §5 for the
   exact schema).
7. Update `memory.md`:
   - Bump `iteration:`.
   - Set `active_lead_registry: <path>`.
   - Append one-line history entry.
   - Do **not** add any lead context to memory.md beyond the pointer.
     Detail lives in the registry.
8. Exit cleanly. Do **not** process a ticker in the same iter —
   bootstrap must land as its own commit so the diff is small and
   revisable.

---

## 3. Sweep iter — one ticker per iter

Deliverables per iter (three atomic writes, committed together):

1. `reports/<phase>/<lead_slug>/<ticker>.json` — machine-readable
   record of every config tested on this ticker (§5.2).
2. `reports/<phase>/<lead_slug>/<ticker>.md` — human report, standard
   metrics table for the best config + benchmark SPY block + a
   condensed table of all other configs (§5.3).
3. `reports/<phase>/<lead_slug>/registry.json` — pop the ticker from
   `tickers_pending`, append summary to `tickers_done`, advance
   `status` (`sweeping` unless the list just emptied, in which case
   `aggregating`), bump `last_updated_at`.
4. `memory.md` frontmatter `iteration:` bumped + one-line history
   entry.

Steps:

1. Validate the registry file (schema v1, `tickers_pending != []`,
   `status` in `{pending, sweeping}`). Fail fast otherwise — dump a
   jornada `<date>-<phase>-<lead_id>-REGISTRY-CORRUPT.md` and flip
   memory `status: done` so the loop halts.
2. Pick `tickers_pending[0]`. **Never randomize.**
3. Load the longest Tiingo window for this (ticker, frequency) per the
   manifest at `data/tiingo/manifest.json`. If the universe includes
   tickers not in the Tiingo cache, handle them explicitly — either
   document the gap in `tickers_errored` or fetch under
   `data/tiingo_adhoc/` if bulk is still running (CLAUDE.md §3.5a
   constraint 4).
4. Run every config in `registry.configs` on this ticker. Apply the
   same gates that the consuming phase spec mandates (Phase 3.5a →
   5-gate framework + median hold ≤ 5 days + full Pepperstone cost
   model).
5. Build `<ticker>.json` (schema §5.2) and `<ticker>.md` (§5.3).
   Include the benchmark SPY block even when the ticker is not equity
   — SPY IR is a universal comparison basis for this project.
6. Atomic writes, in this order:
   - `<ticker>.json`  (tmp→rename)
   - `<ticker>.md`    (tmp→rename)
   - `registry.json`  (tmp→rename — **last**, because it's the
     pointer everyone else trusts)
7. Update `memory.md`:
   - Bump `iteration:`.
   - Append one-line history entry:
     `iter N — <lead_id> swept <ticker> <freq>: best <config> Sharpe_oos=X.XX <PASS|fail-reason>`.
   - Do **not** rewrite anything else.
8. Exit. The shell loop auto-commits all four files in one commit.

### 3.1 Error handling (ticker-level)

- Data missing, corrupted, or strategy raises → append
  `{ticker, iter, error_msg}` to `tickers_errored`, still pop from
  `tickers_pending`. Write `<ticker>.md` as a stub explaining the
  skip. Continue; aggregator decides whether to manually re-queue.
- Backtest runs but produces obvious garbage (e.g. every config has
  `n_trades == 0`): still write a stub, note it in history, let the
  aggregator flag it.
- Iter hits timeout mid-ticker: the registry has not been updated
  (rule of §3 step 6) so the next iter retries the same ticker from
  scratch. Per-ticker files may or may not exist; overwrite them.

---

## 4. Aggregator iter

Entry condition: `registry.status == "aggregating"` (i.e. the previous
sweep iter just popped the last pending ticker).

Deliverables:

1. `reports/<phase>/<lead_slug>/AGGREGATE.md` (§6).
2. `jornada/<date>-<phase>-<lead_id>-<VERDICT>.md` (VERDICT =
   `PASS` if ≥1 ticker passes all 5 gates, `DEAD` otherwise).
3. `registry.json` bumped: `status: "done"`, `aggregation_iter` =
   current iter, `aggregate_file_md` + `aggregate_jornada` paths.
4. `memory.md` frontmatter:
   - `active_lead_registry: null` (releases the slot).
   - If a winner exists: append to `winners_short_hold:` or
     `winners_swing:` with the canonical dict:
     `{strategy, asset, frequency, sharpe_is, sharpe_oos, jornada}`.
   - Otherwise: one-liner under `## Dead ends` pointing to the
     jornada.
   - Append a 5-line-max history entry tagged `★ PASS` or `DEAD END`.

### 4.1 AGGREGATE.md structure

Mandatory sections:

```markdown
# Lead <id> — <title> (aggregate)

**Phase:** <phase> | **Lead:** <id> | **Status:** <PASS|DEAD END> (k/N PASS)
**Period:** <start> → <end> (<years>y, <source>)
**Tested:** <N> tickers × <M> configs = <N×M> runs
**Aggregation iter:** <I>

## Summary
<1-2 paragraphs explaining the verdict + why>

## Cross-ticker table
| Ticker | Best config | Sharpe OOS | CAGR OOS | MaxDD | Median hold (d) | PASS |
|--------|-------------|-----------|----------|-------|-----------------|------|
| ...

## Citations
- <citation 1>
- <citation 2>

## Links
- Per-ticker reports: `reports/<phase>/<lead_slug>/*.md`
- Registry: `reports/<phase>/<lead_slug>/registry.json`
- Jornada: `jornada/<date>-<phase>-<lead_id>-<verdict>.md`
```

### 4.2 Jornada entry

Short-form. Copy the cross-ticker table, 1-2 paragraphs diagnosis,
pointer to next lead. Tag in the H1 header with `[SHORT-HOLD CFD]`
or `[SWING BROKER]` per CLAUDE.md §3.5a / §3.5b discipline.

### 4.3 Order of writes (atomic)

1. `AGGREGATE.md`     (tmp→rename)
2. `jornada/...md`    (tmp→rename)
3. `jornada/README.md` (append index entry newest-first)
4. `registry.json`    (tmp→rename — status: done)
5. `memory.md`        (clear pointer, append winner/dead-end)

Shell loop commits all five changes atomically.

---

## 5. Schemas

### 5.1 Registry schema v1

Path: `reports/<phase>/<lead_slug>/registry.json`.

```json
{
  "schema_version": 1,
  "phase": "phase3_5a",
  "lead_id": "T2",
  "lead_slug": "t2_donchian_breakout_intraday",
  "lead_title": "Donchian/ATR breakout 1h FX + index CFD",
  "citations_seed": ["trading_systems_methods, p.353", "volatility_trading"],
  "started_at": "2026-04-18T02:00:00-03:00",
  "last_updated_at": "2026-04-18T02:15:33-03:00",
  "configs": [
    {"name": "donch_10_5_long",  "type": "donchian", "entry_lookback": 10, "exit_lookback": 5,  "direction": "long"},
    {"name": "donch_10_5_short", "type": "donchian", "entry_lookback": 10, "exit_lookback": 5,  "direction": "short"},
    {"name": "donch_20_10_long", "type": "donchian", "entry_lookback": 20, "exit_lookback": 10, "direction": "long"}
  ],
  "tickers_pending": ["GBPUSD", "USDJPY", "USDCHF", "AUDUSD", "XAUUSD", "XAGUSD"],
  "tickers_done": [
    {
      "ticker": "EURUSD",
      "frequency": "1hour",
      "window_start": "2020-01-01",
      "window_end":   "2026-04-17",
      "iter": 4,
      "n_configs_tested": 3,
      "best_config": "donch_20_10_long",
      "best_sharpe_oos": 0.42,
      "best_cagr": 0.08,
      "best_maxdd": -0.17,
      "any_pass_5gate": false,
      "median_hold_days": 2.3,
      "result_file_md":   "reports/phase3_5a/t2_donchian_breakout_intraday/EURUSD.md",
      "result_file_json": "reports/phase3_5a/t2_donchian_breakout_intraday/EURUSD.json"
    }
  ],
  "tickers_errored": [],
  "status": "sweeping",
  "aggregation_iter": null,
  "aggregate_file_md":   null,
  "aggregate_jornada":   null
}
```

**State machine:** `pending` → `sweeping` → `aggregating` → `done`.

- `pending`: registry just bootstrapped, zero tickers processed yet.
  Treat as `sweeping` when picking a ticker.
- `sweeping`: ≥1 ticker done, ≥1 pending.
- `aggregating`: `tickers_pending == []` and aggregator has not run.
- `done`: aggregator ran; `aggregate_file_md` is set.

**Invariants (validate at every load):**

- `schema_version == 1` (strict equality).
- `lead_id` and `lead_slug` non-empty.
- `configs` is a non-empty list; each entry has `name` and `type`.
- `tickers_pending` and `tickers_done` are disjoint (no ticker
  appears in both).
- No ticker appears twice in `tickers_done` (append-only, unique).
- `status` ∈ {`pending`, `sweeping`, `aggregating`, `done`}.
- If `status == "done"`, `aggregate_file_md` is set.

Validation failure → fatal. Dump jornada blocker, stop.

**Atomic write pattern (mandatory):**

```python
def atomic_write(path: str, data: dict) -> None:
    tmp = f"{path}.tmp.{os.getpid()}"
    with open(tmp, "w") as f:
        json.dump(data, f, indent=2, sort_keys=False)
        f.flush()
        os.fsync(f.fileno())
    os.rename(tmp, path)  # atomic on POSIX
```

### 5.2 Per-ticker JSON schema (`<ticker>.json`)

```json
{
  "ticker": "EURUSD",
  "frequency": "1hour",
  "window": {"start": "2020-01-01", "end": "2026-04-17", "n_bars": 38412},
  "costs_model": {
    "spread_half_bps": 2,
    "commission_per_side_usd": 3.5,
    "swap_daily_pct_long":  -0.005,
    "swap_daily_pct_short":  0.001,
    "citation": "pepperstone razor tier (docs/investment-mandate.md §3)"
  },
  "configs": [
    {
      "name": "donch_20_10_long",
      "metrics_is":  {"sharpe": 0.51, "cagr": 0.09, "maxdd": -0.15, "n_trades": 127, "median_hold_days": 2.3},
      "metrics_oos": {"sharpe": 0.42, "cagr": 0.08, "maxdd": -0.17, "n_trades": 54,  "median_hold_days": 2.1},
      "metrics_fwd": {"sharpe": 0.31, "cagr": 0.05, "maxdd": -0.09, "n_trades": 18,  "median_hold_days": 2.4},
      "gates": {"pbo": 0.42, "dsr_p": 0.031, "wf_win": 5, "wf_total": 8, "any_pass": false, "why_fail": "wf 5/8 < 6"},
      "benchmark_spy": {"sharpe": 0.63, "cagr": 0.11, "excess_cagr": -0.03, "beta": 0.12, "corr": 0.08}
    }
  ],
  "best_config": "donch_20_10_long",
  "any_pass_5gate": false
}
```

### 5.3 Per-ticker Markdown skeleton (`<ticker>.md`)

```markdown
# <TICKER> <freq> — <lead_id> <strategy family> (iter N)

**Window:** <start> → <end> (<years>y, <n_bars> bars)
**Best config:** `<name>` — **<PASS|NO PASS>** (<reason if fail>)

## Standard report — <best name> (best)

Start                     <...>
End                       <...>
Duration                  <...>
...
[full backtesting.py-style table, via standard_report.py]
...

SPY Buy & Hold (same window):
  SPY Return [%]           <...>
  SPY CAGR [%]             <...>
  ...

Strategy vs SPY:
  Excess CAGR [%]          <...>
  Correlation (daily)      <...>
  Beta vs SPY              <...>

## Todas configs testadas

| Config | Sharpe OOS | CAGR OOS | MaxDD OOS | PBO | DSR p | WF | PASS |
|--------|-----------|----------|-----------|-----|-------|----|------|
| ...

## Cost sensitivity

(optional — spread/commission ablation if aggregator requests it)
```

The standard report + SPY benchmark block come from the existing
`src/market_lab/backtest/metrics/standard_report.py` helper —
reuse, do not duplicate.

---

## 6. Commit messages

Shell loop commits every iter. In fan-out mode, the agent should
shape `memory.md`'s history entry so the auto-parsed
`ITER_SUMMARY` produces a readable commit subject. Format:

- Bootstrap: `iter N — <lead_id> bootstrap registry`
- Sweep:     `iter N — <lead_id> sweep <ticker>`
- Aggregator: `iter N — <lead_id> aggregator <PASS|DEAD>`

The shell already truncates `ITER_SUMMARY` at 72 chars; keep the
entries terse.

---

## 7. Pseudo-code: minimal helpers the agent may reuse

```python
from market_lab.backtest.sweeps.registry import (
    load_registry,
    atomic_write_registry,
    append_done,
    pop_pending,
    mark_errored,
    validate_schema_v1,
)

reg = load_registry("reports/phase3_5a/t2_donchian_breakout_intraday/registry.json")
validate_schema_v1(reg)

ticker, reg = pop_pending(reg)   # removes reg.tickers_pending[0] -> ticker
# ... run backtests, write <ticker>.json + <ticker>.md ...
summary = {
    "ticker": ticker,
    "frequency": "1hour",
    "window_start": "2020-01-01",
    "window_end":   "2026-04-17",
    "iter":         reg.get("_current_iter", 0),
    "n_configs_tested": len(reg["configs"]),
    "best_config":      "donch_20_10_long",
    "best_sharpe_oos":  0.42,
    "best_cagr":        0.08,
    "best_maxdd":      -0.17,
    "any_pass_5gate":   False,
    "median_hold_days": 2.1,
    "result_file_md":   f"reports/phase3_5a/t2_donchian_breakout_intraday/{ticker}.md",
    "result_file_json": f"reports/phase3_5a/t2_donchian_breakout_intraday/{ticker}.json",
}
reg = append_done(reg, summary)
atomic_write_registry(path, reg)
```

---

## 8. Invariants (checklist)

Copy this into TodoWrite at the start of every fan-out iter.

- [ ] Only ONE work unit processed this iter (bootstrap OR one ticker OR
      aggregator — never two).
- [ ] Registry schema v1 validated before any mutation.
- [ ] `tickers_done` append-only; no retroactive edits.
- [ ] `configs` unchanged relative to bootstrap.
- [ ] Atomic writes used for every JSON file (tmp → rename).
- [ ] `<ticker>.json` + `<ticker>.md` written before registry update.
- [ ] Registry status transition follows
      `pending → sweeping → aggregating → done`.
- [ ] Aggregator clears `memory.md` `active_lead_registry` to `null`.
- [ ] History entry in `memory.md` is ≤ 5 lines and terse enough to
      produce a good commit subject.
- [ ] Citations `[book.slug, p.X]` present for any strategy decision
      made this iter (CLAUDE.md regra 2).
- [ ] Jornada tagged `[SHORT-HOLD CFD]` or `[SWING BROKER]` at H1.

---

## 9. When NOT to use fan-out mode

Atomic leads (single-task, no ticker sweep) — e.g. Phase 3.5a T6
(rebalance meta) and T7 (summary jornada) — stay in legacy mode.
The shell still runs them as 1 iter = 1 Lead; no registry is created.
The agent can detect this by reading the phase spec and noticing the
lead has no `tickers` universe.

If in doubt: a lead with `N tickers × M configs` where `N > 3` is
fan-out; anything else is legacy.

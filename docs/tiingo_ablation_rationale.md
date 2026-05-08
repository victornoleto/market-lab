# Why migrate to Tiingo — data-ablation rationale

> ⏸️ **On hold — waiting for Tiingo evaluation.** The Reddit post
> (`docs/POST_reddit.md`) and any fork decision are paused until the
> Tiingo SF subscription lands and the re-runs of Run 1 (Clenow) and
> Run 2 (Ehlers) complete. Rationale: the post will inevitably draw
> "why didn't you use survivorship-free data?" — answering with actual
> results beats answering with a plan. Resume this doc's §6 execution
> plan once the subscription is active.

**Status:** planned. Tiingo SF subscription pending; once signed, re-run
Run 1 (Clenow) and Run 2 (Ehlers) with survivorship-free data keeping
everything else constant.

**Context:** this doc explains why migrating from `yfinance` + Wikipedia
scrape to Tiingo (SF product — survivorship-free) is the necessary next
experiment before pivoting strategies, changing universe, or declaring
absence of edge. Consolidated from `specs/backtest_phase2.md`,
`specs/backtest_phase2_5_ehlers.md`, and the two diagnostic reports in
`reports/grid_*/`.

---

## 1. What the gates are saying today

Both grid runs (Clenow and Ehlers) failed **for the same reason** — DSR —
and **not** via PBO:

| Metric | Clenow (Run 1) | Ehlers (Run 2) |
|---|---|---|
| PBO | 0.524 (marginal fail) | **0.468 (pass)** |
| DSR p-value | 0/30 < 0.05 | 0/24 < 0.05 |
| Best Sharpe annualized | 0.583 | 0.310 |
| E[SR_max] under null (N≈25, T≈2267) | ~0.86 | ~0.86 |
| Walk-forward | 4/30 pass | 2/24 pass |

The maximum observed Sharpe is **below the null-hypothesis benchmark**.
That is what DSR is rejecting.

**Key point:** PBO measures *overfit to the grid* (IS↔OOS rankings).
Ehlers passes PBO comfortably — the structural signal is not a grid
artefact. What fails is the test against the chance benchmark. And that
benchmark depends directly on the **return distribution of the dataset**.

---

## 2. Why the data source becomes a confounding variable

The current pipeline (`yfinance` + Wikipedia point-in-time) has two
problems documented in the specs themselves:

### 2.1 Residual survivorship bias (scales linearly with horizon)

- 6-month window (H2 2023): **17/503 = 3.4%** of tickers vanished
  silently (`reports/clenow_replication_notes.md`).
- 9-year window (2015-2023): **97/506 = 19%**
  (`specs/backtest_phase2.md` §"Grid executed").
- `yfinance` **does not serve delisted tickers** — it returns an empty
  frame, and they drop out of the universe without warning.
- Bug ANDV→MPC 2018 (commit `8d25e65`) only surfaced because the long
  window crossed an actual delisting — direct evidence that the current
  pipeline treats delistings as "ticker never existed".

### 2.2 Compound effect on DSR

The DSR null hypothesis (AFML p.222-223) is `E[SR_max(N)] under iid-null`.
But **the "null" is estimated from the variance of observed returns**. If
returns are inflated by survivorship (the real losers are gone), the null
rises with them — and the "real" Sharpe lands below it even when an edge
exists.

This is stated literally in `specs/backtest_phase2.md`:

> **Literal:** yfinance SPX 2015-2023 has no Clenow edge after gates.
> **Data-hypothesis:** yfinance inflates the SPY benchmark... Removing
> the bias might drop SPY to ~9% and lift Clenow to a relative edge.
> **Paid-data ablation is required to know.**

---

## 3. What Tiingo specifically unlocks

Tiingo has an **"SF" (Survivorship-Free)** product with point-in-time
prices for tickers **including delistings**. Three things change
measurably:

1. **The universe at every rebalance includes the ~97 missing tickers.**
   In Clenow, they would enter the momentum ranking in their good
   epochs *and* be available for exclusion in their pre-delisting
   drops. Today they are invisible.

2. **OOS return distribution gets the real left tail.** The `E[SR_max]`
   under null drops (variance similar, mean returns to real) and
   becomes an honest benchmark. Strategies that tie with the null
   today may beat it.

3. **The buy-and-hold benchmark (SPY) becomes comparable.** Today
   Clenow (~8.87% CAGR) is compared against an inflated SPY
   (~11-12%). With clean data, real SPY lands around ~9% and the
   relative edge reappears.

---

## 4. Why this is the right ablation, not a "nice-to-have"

The **scientific test** here is to isolate the "data" variable keeping
everything else fixed:

- Same strategy (identical code)
- Same grid (24 or 30 configs)
- Same window (2015-2023)
- Same gates (PBO/DSR/WF, identical thresholds)
- **Only change:** `data/yfinance_source.py` → `data/tiingo_source.py`

Possible results and what each one proves:

| Result on Tiingo | Conclusion |
|---|---|
| Ehlers and/or Clenow pass DSR | Edge **was real**, yfinance was masking it. Phase 3 unlocks. |
| Both still fail DSR | Edge **does not exist** in this window/universe. Pivot to a 3rd strategy (AFML, Chan) or universe shift becomes well-grounded. |
| PBO worsens on Ehlers | The apparent signal structure came from the bias — an important insight on its own. |

Without the ablation, **these three hypotheses are indistinguishable**.
With it, any decision fork becomes defensible.

---

## 5. Cost of the experiment vs. alternatives

Forks mapped in `specs/backtest_phase2_5_ehlers.md` §Task 5, compared
concretely:

| Fork | Cost | Information gained |
|---|---|---|
| **1. Tiingo SF ablation** | 2-3 days integration + free-trial/subscription | **Decisive**: resolves data-vs-edge ambiguity |
| 2. 3rd strategy (AFML/Chan) | 1-2 weeks | Low — cumulative N-penalty (4 strategies × 25 configs = worse DSR) |
| 3. Regime-aware Clenow+Ehlers portfolio | Low (reuse) | Limited — if each is null, the sum is too |
| 4. Stop | Zero | None |

**Option 1 is the only one that changes the question**, not the n-th
attempt to answer the same one. The other three assume current data is
ground truth; option 1 challenges the premise.

---

## 6. Post-subscription execution plan

1. **Data source integration.** Create
   `src/market_lab/backtest/data/tiingo_source.py` replicating the
   `YFinanceSource` interface (`fetch_many(symbols, start, end) → dict[str, pd.DataFrame]`
   OHLCV + parquet cache). Keep the survivorship-free marker so the
   report disclaimer adjusts automatically.
2. **Point-in-time universe.** Tiingo exposes its own historical
   constituents — replace `wikipedia_spx` with a native Tiingo source.
   Skip the undo-changes-walking-backwards algorithm.
3. **Re-run the Clenow grid** (same 30 configs, `2015-01-01 → 2023-12-31`,
   `scripts/run_grid_clenow.py`) pointing at the new source. Expected
   wallclock: similar to Run 1 (~15 min with n_jobs=4).
4. **Re-run the Ehlers grid** (same 24 configs, same window,
   `scripts/run_grid_ehlers.py`). Expected wallclock: ~3s
   (single-instrument).
5. **Log results inline** in `specs/backtest_phase2_5_ehlers.md`
   §"Run — results and fork" (create sub-section "Run 3 — Tiingo
   ablation") and `specs/backtest_phase2.md` §"Phase 2.5/3 — Run 1"
   (analogous sub-section).
6. **Decide the fork** based on the outcome — the three branches in §4
   of this doc are mutually exclusive.

---

## 7. References

- `specs/backtest_phase2.md` — Phase 2 spec + Run 1 (Clenow grid)
- `specs/backtest_phase2_5_ehlers.md` — Run 2 spec (Ehlers grid)
- `reports/clenow_replication_notes.md` — single-trial H2 2023, 17 skipped
- `reports/ehlers_replication_notes.md` — single-instrument ^GSPC 2022-2023
- `reports/grid_20260414-1813/diagnostic.md` — Run 1 fail (PBO+DSR)
- `reports/grid_ehlers_20260414-1944/diagnostic.md` — Run 2 fail (DSR)
- `src/market_lab/backtest/data/yfinance_source.py` — data source to be
  mirrored by `tiingo_source.py`
- `src/market_lab/backtest/validation/dsr.py` — AFML p.222-223 implementation

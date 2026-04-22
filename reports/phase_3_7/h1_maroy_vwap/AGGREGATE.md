# Phase 3.7 H1.b — Maróy 2024 VWAP-exit intraday noise-boundary

**Verdict:** `FAIL`
**Git SHA (at run):** `32b6128f73` (pre-implementation HEAD)
**Produced at:** 2026-04-23 (Phase 3.7-3 winner hunt, subagent H1.b)
**Subagent:** 1 of 3 parallel (H1.a / **H1.b** / H1.c) — independent work

---

## 1. Hypothesis

- **Entry (Zarattini-Aziz-Barbon 2024, SSRN 4824172):** noise-boundary breakout on SPY 1-min. For each trading day, `upper = open_d × (1 + MA_14(|intraday_return|))`, symmetric `lower`. Long if `close > upper`; short if `close < lower`. `[zarattini_aziz_barbon_2024]`
- **Exit (Maróy 2024, SSRN 5095349, VWAP-cross variant):** anchored VWAP from the day-open; exit long when close crosses below VWAP from above (`close_{t-1} ≥ VWAP_{t-1}` AND `close_t < VWAP_t`), symmetric short. **TVWAP close-only approximation** used because Tiingo IEX 1-min parquets lack volume (see §Limitations). `[maroy_2024]`
- **Flat at close** (mandate §3 intraday, no swap).

---

## 2. Universe + data

| Asset | File | Range | Bars | Days |
|---|---|---|---|---|
| SPY | `data/phase3_7/intraday/SPY_1min.parquet` | 2017-01-03 → 2026-04-14 | 917,371 | 2,358 |
| QQQ | `data/phase3_7/intraday/QQQ_1min.parquet` | 2017-01-03 → 2026-04-14 | 917,169 | 2,358 |

Regular session only (9:30-16:00 ET, 390 bars/day median, min 135 on 2025-10-13 half-day).

---

## 3. Splits

| Split | Start | End | Days |
|---|---|---|---|
| IS | 2017-06-01 | 2021-12-31 | 1,169 |
| OOS | 2022-01-01 | 2024-12-31 | 760 |
| FWD | 2025-01-01 | 2026-04-14 | 326 |

Splits are **mutually exclusive** (no overlap). Warmup of 14 trading days consumed from 2017-01-03 through 2017-01-23.

---

## 4. Engine + cost model

- **Alignment:** F2-patched `prev_weight × bar_ret` inside each session; `prev_weight` zeroed at each session boundary (no overnight carry by construction). Ref `src/ai_trade/backtest/strategies/phase3_6_k_universal_trend.py` lines 556-568, applied at 1-min granularity. `[advances_fin_ml, p.31-34]`
- **Spread:** 0.67 bps per side (0.4-pt spread on SPX500 CFD at $6000 index). Applied on every position flip.
- **Commission:** 0 (index CFD, Razor account).
- **Swap:** 0 (intraday only).
- **Sizing:** ±1.0 notional (unleveraged; leverage sweep is H4 meta-layer, not H1.b).

Source: `docs/strategies/plano_a_pepperstone_index_cfd_rate_card.md`.

---

## 5. Winner-cell metrics (ma14_sc1.0_shrt1_mb1)

| Split | Days | Sharpe | CAGR | MDD | Cum return |
|---|---:|---:|---:|---:|---:|
| IS | 1,169 | **-2.276** | **-26.22%** | -75.69% | -75.61% |
| OOS | 760 | **-2.958** | **-35.32%** | -73.32% | -73.13% |
| FWD | 326 | **-1.211** | **-17.93%** | -42.95% | -22.56% |
| FULL | 2,358 | **-2.381** | **-28.28%** | -95.81% | -95.54% |
| QQQ_OOS (cross-asset) | 760 | -1.033 | -18.52% | -57.91% | — |
| SPY buy-hold OOS | 755 | +0.489 | +7.24% | — | — |

**Tiers (mandate §2.2/§2.3, rota A, warning-only):**
- OOS CAGR = -35.32% → **folclore** (below CDI 13% floor).
- OOS MDD = -73.32% → **warning** (40-75% tier; would be "reject" above 75% but still warning-only per §2.3).

**Trade stats (winner):**
- n_trades = 24,950 over 2,358 days = ~10.6 trades/day.
- Median hold = **10 bars (≈10 min)** — TVWAP-cross triggers immediately because the close-only TVWAP is noisy.
- **Cumulative spread cost = 334%** of starting equity. Cost bleeding is the dominant failure mode.

**Zero-cost gross sanity (with no spread):** Sharpe IS=0.47, Sharpe OOS=**-0.41**. Even gross, signal fails on OOS. The paper's reported Sharpe 1.33 net does **not** reproduce on this IS/OOS partition under the VWAP-cross exit with close-only TVWAP.

---

## 6. 13-gate table

Per mandate §2.4. CAGR + MDD are warning-only tiers (§2.2/§2.3) — not binding gates. Hard gates (9, 10, 10b, 11, 12) are zero-bypass.

| # | Gate | Value | Verdict |
|---:|---|---|:---:|
| 1 | IS Sharpe > 0.5 | -2.276 | **FAIL** |
| 2 | OOS Sharpe ≥ 1.3 | -2.958 | **FAIL** |
| 3 | OOS CAGR tier (warning-only) | -35.32% → folclore | WARN |
| 4 | OOS MDD tier (warning-only) | -73.32% → warning | WARN |
| 5 | FWD Sharpe > 0 | -1.211 | **FAIL** |
| 6 | WF ≥ 6/8 windows positive | 1/8 (max-dd 28.0%) | **FAIL** |
| 7 | Median hold ≥ 60 bars (1h) | 10 bars | **FAIL** |
| 8 | IR vs SPY OOS ≥ 0.2 | -2.24 | **FAIL** |
| 9 | **Cross-lib Δ CAGR ≤ 3pp — HARD** | +0.000pp | **PASS** |
| 10 | **Bootstrap OOS 99.9% CI low > 0 — HARD** | -4.95 | **FAIL** |
| 10b | **Bootstrap FULL 99.9% CI low > 0 — HARD** | -3.55 | **FAIL** |
| 11 | **PBO < 0.3 — HARD** | 0.0000 (n_combos=252) | **PASS** |
| 12 | **DSR p < 0.05 — HARD** | p=1.000 | **FAIL** |
| 13 | Cost×2 Sharpe > 1.0 | -5.35 | **FAIL** |

**PASS rule:** requires all 5 HARD gates (9/10/10b/11/12) **and** all 7 required soft gates (1/2/5/6/7/8/13). Hard fail count: 3. Soft fail count: 7. **Verdict = FAIL.**

PBO = 0 is mechanically "PASS" because **all 24 grid configs share the same negative edge** — there's no configuration that performs better IS vs OOS by luck, because they all lose money in both. PBO passing here confirms absence of cherry-picking, not presence of edge. DSR p=1.0 confirms observed Sharpe is below benchmark (i.e., noise-indistinguishable).

---

## 7. Cross-lib concordance (gate 9)

| Path | OOS CAGR | OOS Sharpe |
|---|---:|---:|
| Canonical numpy state machine | -35.32% | -2.958 |
| Hand-rolled pandas+python-loop | -35.32% | -2.958 |
| **Δ** | **+0.000pp** | **+0.000** |

Two independent implementations share only the data-prep primitives (open / MA / TVWAP); the entry/exit state machines are rewritten. Exact agreement.

**vectorbt / bt / backtrader skipped** — the anchored-VWAP-cross exit on session-bounded 1-min multi-day panels is not a first-class primitive in these libraries; porting would require custom signal-function callbacks that would effectively re-implement the pipeline. Same rationale as Phase 3.6 Family K. Documented, not a gate miss.

---

## 8. Grid / PBO / DSR

24 grid cells (3 lookbacks × 2 scales × 2 short/long-only × 2 min-bar-idx). **All 24 cells have negative full-sample Sharpe** (range: -2.45 to -1.04). Top-cell = `ma21_sc1.2_shrt0_mb30` with Sharpe -1.036 (still losing).

- PBO via CSCV (n_blocks=10, 252 combinations) = **0.0000** — IS-best cell never wins OOS because no cell ever "wins". Degenerate pass.
- DSR (n_trials=24) = p_value **1.000000** — observed SR (-0.187 periodic) below E[SR_max] benchmark under the iid null.

---

## 9. Limitations + data caveats

- **TVWAP close-only approximation** replaces true anchored VWAP. The Tiingo IEX 1-min parquets (source: `scripts/data_sprint/ingest_intraday_etf.py`) contain only `open/high/low/close` — volume was not ingested (IEX-only volume is ~2-3% of consolidated tape for SPY, so even if ingested it would skew VWAP). The TVWAP substitutes an equal-weighted minute mean for the volume-weighted one. This under-penalizes high-volume outlier bars (open/close bursts) and likely triggers the VWAP-cross earlier than a true VWAP would. **Honest caveat; does not rescue the strategy** because the gross Sharpe (no-cost) is already -0.41 OOS.
- **SPX500 CFD tested via SPY minute bars.** Pepperstone's SPX500 tracks the cash S&P 500 index continuously, whereas SPY is a single-listing ETF with possible premium/discount to NAV and market-on-close auction mechanics. Cost model is applied as if trading SPX500 directly (0.4-pt spread), but the price path is SPY's. Honest limitation per mandate §3.1.
- **Regular session only** (9:30-16:00 ET). Pre-market and post-market extended hours not in the ingested feed. Zarattini 2024 also restricts to regular session, so no literature deviation.
- **Subagent parallelism:** H1.a (Zarattini trail) and H1.c (third variant) are running independently in the same branch; they use the same SPY/QQQ parquets. No mutable state shared.

---

## 10. Halt-contract check

- `n_trades OOS` — winner has 24,950 total trades, vast majority in OOS (ratio days ≈ 760/2358 = 32%, so ~8,000 OOS trades). **Far above** the 100 minimum. Not a FAIL-insufficient-trades case.
- F2 alignment regression — cross-lib delta = 0.000 confirms engine integrity. No engine regression note required.
- PBO ≥ 0.5, DSR p > 0.05, cross-lib > 3pp — PBO=0, cross-lib=0, DSR=1.0. DSR triggers REJECT-PASS regardless, but the strategy fails independently on 7+ other gates.

---

## 11. Next-step recommendation

**Do not promote H1.b.** Maróy 2024's reported Sharpe > 3.0 does **not** survive honest OOS on 2017-2024 SPY with the cost model documented in his own base paper (Zarattini 2024's $0.0035 commission + $0.001 slippage per share translates to ~0.2-0.5 bps, within the same order of magnitude as our 0.67-bps Pepperstone SPX500 CFD model). Several failure modes compound:

1. **Signal is not directionally robust OOS** (gross Sharpe -0.41 OOS with 0 cost).
2. **TVWAP-cross exits fire too early** (10-bar median hold vs paper's expected intraday hold).
3. **Cost drag is ruinous** (334% cum spread over 9 years on SPY, because ~10 flips/day × 2 sides × 0.67 bps = 13 bps/day = 3200 bps/year → pure bleed).

Recommendations for Phase 3.7-4:
- **Fallback to Zarattini 2024 ATR-trail exit** (H1.a subagent) — that's the baseline paper with Sharpe 1.33 net in the original data + cost model.
- **Only then** consider VWAP as a re-entry filter rather than a primary exit.
- If the original Zarattini 2024 ATR-trail also FAILs honest OOS on our data (H1.a verdict pending), **conclude that the Zarattini family does not replicate post-2017 out-of-sample on 1-min CFD-proxy SPY**, regardless of exit engineering.
- Independent of H1 family: no Phase 3.7-3 re-run with wider grid is warranted, because gross (zero-cost) signal already fails OOS.

---

## 12. Citations

- `[zarattini_aziz_barbon_2024]` — Zarattini, Aziz, Barbon (2024) "Beat the Market: An Effective Intraday Momentum Strategy for S&P500 ETF (SPY)", SSRN 4824172.
- `[maroy_2024]` — Maróy (2024) "Improvements to Intraday Momentum Strategies Using Parameter Optimization and Different Exit Strategies", SSRN 5095349.
- `[advances_fin_ml, p.31-34]` — prev_weight × ret alignment.
- `[advances_fin_ml, p.196-211, p.273-275]` — bootstrap / PBO / DSR.
- `[docs/investment-mandate.md §2.2-§2.4]` — tiers + gates.
- `[docs/strategies/plano_a_pepperstone_index_cfd_rate_card.md]` — cost model.
- `[docs/research/2026-04-23-phase3.7-literature-sprint.md §T3]` — Maróy context.

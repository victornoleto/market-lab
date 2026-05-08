---
status: in_progress
iteration: 0
best_verdict: None
best_sharpe: null
best_asset: null
best_config: null
---

# Self-improvement memory — market-lab

This file persists across Claude Code iterations of `scripts/self_improve_loop.sh`.

**Read this file FIRST every iteration — your conversation history is empty.**
The shell script restarts Claude Code with a fresh context window each iteration; this file is your only continuity.

## Goal (do not modify)

Find a backtest configuration (strategy + asset + parameters, or portfolio-level approach) that passes the **3-gate framework** on the survivorship-free Tiingo dataset:

- **PBO** < 0.5 (combinatorial purged splits)
- **DSR** p-value < 0.05 (deflated Sharpe, López de Prado, deflate by N trials)
- **Walk-forward** ≥ 6/8 profitable windows AND max DD ≤ 25% per window

Stretch: portfolio approach (multi-strategy / regime-conditional / risk-parity) that beats buy-and-hold SPY over 2015-2023 risk-adjusted (Sharpe and Calmar).

## Project state anchor (last verified 2026-04-14)

- **Phase 0** (knowledge base): 33/33 books absorbed and validated. Loadable via `Skill knowledge:knowledge`.
- **Phase 2** (backtest engine): done, 290/290 tests green. CPCV / PBO / DSR / WF / MCPT in `src/market_lab/backtest/validation/`.
- **Phase 2.5 results so far:**
  - Run 1 — Clenow grid yfinance SPX 2015-2023: **FAIL** (PBO 0.524, DSR 0/30).
  - Run 2 — Ehlers BP Swing yfinance ^GSPC 2015-2023: **FAIL** (PBO 0.468 pass but DSR 0/24, WF 2/24).
  - Run 3 — Ehlers Tiingo SPY 2015-2023: **FAIL** — same verdict (Tiingo did not save SPY since it has no survivorship bias).
  - Multi-asset Ehlers survey (16 assets, ETFs + crypto via Tiingo, 2005/2007/2010/2017→2023): **0 PASS / 16 FAIL**. Best Sharpe = BTCUSD 0.95 (still WF 0/24, DSR 0/24). See `reports/ehlers_multi_asset_summary.md`.

## Known dead ends — DO NOT REPEAT

- Ehlers BP Swing single-instrument long-flat with default 24-config grid (hp_period × lp_period × pct_of_dcp × stop_pct) on **any** equity/ETF/commodity/bond/crypto from the survey. Documented in `reports/ehlers_multi_asset_summary.md`.
- Clenow momentum unmodified on yfinance SPX 2015-2023.

## Promising leads not yet explored (consume in order)

1. **Clenow Run 3** — full survivorship-free SPX via Tiingo bulk. Bulk in progress 2026-04-14 evening; check `pgrep -af tiingo_bulk_download` first. Cmd: `.venv/bin/python scripts/run_grid_clenow.py --data-source tiingo --storage-root data/tiingo --start 2015-01-01 --end 2023-12-31 --output-dir reports/ --n-jobs 4`.
2. **Combined Clenow + Ehlers regime-conditional portfolio.** Run 2 found correlation between best equity curves was -0.0108 (near-orthogonal). Test if a risk-budgeted blend or regime overlay (Chen `regime_change`) lifts the combined verdict above gates.
3. **Ehlers SPY long-history 1993-2026** — extends T~2200 → T~8000 for DSR power. May rescue Sharpe-significance even if absolute Sharpe stays at 0.43.
4. **AFML triple-barrier + meta-labeling** (López de Prado `advances_fin_ml` ch.3) — direction primary + ML confidence secondary. Not yet implemented in `src/market_lab/backtest/strategies/`.
5. **Chan mean-reversion / pairs cointegration** (`algo_trading_chan` ch.3, `quant_trading_chan` ch.4). Not yet implemented.
6. **Carver risk-parity** across diversified Pepperstone-tradable instruments (`systematic_trading` chs.7-9). Not yet implemented.
7. **Knowledge-base audit** — Are any of the 33 books underused? Any thematic gap (e.g. options/derivatives, microstructure)? See `knowledge/SKILL.md` topic coverage.

## Constraints (binding)

- All hypotheses must cite `[book.slug, p.X]` from the knowledge base.
- All claims of "improvement" require passing all 3 gates. No partial-credit.
- While `pgrep -af tiingo_bulk_download` returns a process: use `--storage-root data/tiingo_adhoc` to avoid manifest race. Once bulk is done: `data/tiingo` is canonical.
- Single-writer convention on TiingoStorage. Do not run two ad-hoc grids concurrently against the same storage root.
- New strategy implementations must include unit tests + integration tests, and full suite must stay green.
- Never `git commit` from inside an iteration — the shell loop handles git.

## Tools / commands cheatsheet

- Single-asset Ehlers grid: `.venv/bin/python scripts/run_grid_ehlers.py --data-source tiingo --symbol <sym> --asset-class <equity|etf|crypto|forex> --storage-root data/tiingo_adhoc --start <YYYY-MM-DD> --end <YYYY-MM-DD> --output-dir reports/ --run-id grid_ehlers_<sym>_$(date +%Y%m%d-%H%M%S) --n-jobs 4`
- Multi-asset Ehlers: `bash scripts/run_ehlers_multi_asset.sh [SYMBOL ...]`
- Multi-asset summary regen: `.venv/bin/python scripts/build_ehlers_summary.py`
- Clenow grid: `.venv/bin/python scripts/run_grid_clenow.py --data-source tiingo --storage-root <root> --start ... --end ... --output-dir reports/ --n-jobs 4`
- Tests: `.venv/bin/pytest -q`
- Knowledge base lookup: `Skill knowledge:knowledge` then read `knowledge/SKILL.md`
- Tiingo bulk status: `pgrep -af tiingo_bulk_download` + `python3 -c "import json; print(len(json.load(open('data/tiingo/manifest.json'))))"`

## History

(empty — first iteration)

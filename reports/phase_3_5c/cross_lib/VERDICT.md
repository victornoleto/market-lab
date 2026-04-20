# VERDICT — Plano B Cross-Library Validation

> Generated: 2026-04-20T13:50:17.978507+00:00.
> Baseline commit: `10eb9f824030`.
> Baseline hash: `c130ef614411`.

## STOP — ALL VARIANTS BLOCKED-INVESTIGATE

**Root cause identified: reference_prices.parquet has a broken synthetic/real stitching.**

The pre-inception synthetic LETF prices were generated with an arbitrary 10.0 start value
(`(1 + synth_rets).cumprod() * 10.0`) and not normalized to connect with the real yfinance
price at each LETF's inception date. This creates catastrophic artificial price collapses:

- SSO: 154.94 (synthetic, 2006-06-20) → 3.65 (real, 2006-06-21) — **42.5× artificial drop**
- QLD: 3.75 (synthetic, 2006-06-20) → 0.98 (real, 2006-06-21) — **3.8× artificial drop**
- UGL: 20.20 (synthetic, 2008-12-02) → 6.21 (real, 2008-12-03) — **3.3× artificial drop**

This inflates max_dd to 30-50% for bt/vectorbt (triggers REFUTES gate: max_dd ≥ 25%).

**Required action before re-running:**
1. Fix `reference_prices.py :: _synthetic_pre_inception()` to normalize synthetic prices so
   the last synthetic close matches the first real yfinance close at the inception date.
2. Rebuild `reference_prices.parquet` via `python -m reports.phase_3_5c.cross_lib.data.reference_prices`.
3. Re-run Wave 1 Stage 1 and Stage 2.

Forensic documentation: `reports/phase_3_5c/cross_lib/errors/BLOCKED-*.md`

Stage 2 ran 0 runs: all Wave 1 windows start before 2009-01-01, so the stage==2 filter
skips everything. Wave 1 variants need a POST_2009 window added to their `windows` tuple
(variants.py) for Stage 2 independent-data runs to execute.

---

## Aggregate verdicts

- **leg_sso_only** / canonical: **BLOCKED-INVESTIGATE**
- **plano_b_v4_threshold_10** / extended: **BLOCKED-INVESTIGATE**
- **plano_b_v4_threshold_10** / canonical: **BLOCKED-INVESTIGATE**
- **leg_qld_only** / canonical: **BLOCKED-INVESTIGATE**
- **leg_ugl_only** / canonical: **BLOCKED-INVESTIGATE**

## Per-variant matrix

### leg_sso_only

**Window:** canonical

| stage | lib | tier/outcome |
|-------|-----|--------------|
| 1 | quantstats(from=backtrader) | WARNING |
| 1 | quantstats(from=bt) | REFUTES |
| 1 | backtrader | WARNING |
| 1 | quantstats(from=vectorbt) | REFUTES |
| 1 | bt | REFUTES |
| 1 | vectorbt | REFUTES |

### plano_b_v4_threshold_10

**Window:** extended

| stage | lib | tier/outcome |
|-------|-----|--------------|
| 1 | quantstats(from=backtrader) | REFUTES |
| 1 | quantstats(from=bt) | REFUTES |
| 1 | backtrader | REFUTES |
| 1 | quantstats(from=vectorbt) | REFUTES |
| 1 | bt | REFUTES |
| 1 | vectorbt | REFUTES |

**Window:** canonical

| stage | lib | tier/outcome |
|-------|-----|--------------|
| 1 | quantstats(from=backtrader) | WARNING |
| 1 | quantstats(from=bt) | REFUTES |
| 1 | backtrader | WARNING |
| 1 | quantstats(from=vectorbt) | REFUTES |
| 1 | bt | REFUTES |
| 1 | vectorbt | REFUTES |

### leg_qld_only

**Window:** canonical

| stage | lib | tier/outcome |
|-------|-----|--------------|
| 1 | quantstats(from=backtrader) | REFUTES |
| 1 | quantstats(from=bt) | REFUTES |
| 1 | backtrader | REFUTES |
| 1 | quantstats(from=vectorbt) | REFUTES |
| 1 | bt | REFUTES |
| 1 | vectorbt | REFUTES |

### leg_ugl_only

**Window:** canonical

| stage | lib | tier/outcome |
|-------|-----|--------------|
| 1 | quantstats(from=backtrader) | REFUTES |
| 1 | quantstats(from=bt) | REFUTES |
| 1 | backtrader | REFUTES |
| 1 | quantstats(from=vectorbt) | REFUTES |
| 1 | bt | REFUTES |
| 1 | vectorbt | REFUTES |


## Citations

- Tolerance magnitudes: `[advances_fin_ml, p.208-211]`
- Strategy similarity: `[advances_fin_ml, p.273-275]`
- 5-gate framework: `[advances_fin_ml, p.208-211, p.273-275, p.298-299]`
- LETF synthetic formula: `[leverage_for_the_long_run, p.16]`
- Signal EMA regime: `[leverage_for_the_long_run, p.13]`
- Donchian canonical: `[trading_systems_methods, p.353]`
# VERDICT — Plano B Cross-Library Validation

> Generated: 2026-04-20T17:33:28.131577+00:00.
> Baseline commit: `9cc2e3675f20`.
> Baseline hash: `f433c4ed18c9`.

## Aggregate verdicts

- **leg_sso_only** / post_2009: **BLOCKED-INVESTIGATE**
- **leg_sso_only** / extended: **BLOCKED-INVESTIGATE**
- **leg_sso_only** / canonical: **BLOCKED-INVESTIGATE**
- **plano_b_v4_threshold_10** / post_2009: **VALIDATED**
- **plano_b_v4_threshold_10** / extended: **BLOCKED-INVESTIGATE**
- **plano_b_v4_threshold_10** / canonical: **BLOCKED-INVESTIGATE**
- **plano_b_v4_daily** / canonical: **BLOCKED-INVESTIGATE**
- **leg_qld_only** / canonical: **BLOCKED-INVESTIGATE**
- **leg_ugl_only** / canonical: **BLOCKED-INVESTIGATE**

## Per-variant matrix

### leg_sso_only

**Window:** post_2009

| stage | lib | tier/outcome |
|-------|-----|--------------|
| 1 | quantstats(from=backtrader) | REFUTES |
| 1 | quantstats(from=bt) | REFUTES |
| 1 | backtrader | REFUTES |
| 1 | quantstats(from=vectorbt) | REFUTES |
| 1 | bt | REFUTES |
| 1 | vectorbt | REFUTES |
| 2 | quantstats(from=backtrader) | REFUTES |
| 2 | quantstats(from=bt) | REFUTES |
| 2 | backtrader | REFUTES |
| 2 | quantstats(from=vectorbt) | REFUTES |
| 2 | bt | REFUTES |
| 2 | vectorbt | REFUTES |

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
| 1 | quantstats(from=backtrader) | REFUTES |
| 1 | quantstats(from=bt) | REFUTES |
| 1 | backtrader | REFUTES |
| 1 | quantstats(from=vectorbt) | REFUTES |
| 1 | bt | REFUTES |
| 1 | vectorbt | REFUTES |

### plano_b_v4_threshold_10

**Window:** post_2009

| stage | lib | tier/outcome |
|-------|-----|--------------|
| 1 | quantstats(from=backtrader) | WARNING |
| 1 | quantstats(from=bt) | CONFIRMS-STRONG |
| 1 | backtrader | WARNING |
| 1 | quantstats(from=vectorbt) | CONFIRMS-STRONG |
| 1 | bt | CONFIRMS-STRONG |
| 1 | vectorbt | CONFIRMS-STRONG |
| 2 | quantstats(from=backtrader) | WARNING |
| 2 | quantstats(from=bt) | CONFIRMS |
| 2 | backtrader | WARNING |
| 2 | quantstats(from=vectorbt) | CONFIRMS |
| 2 | bt | CONFIRMS |
| 2 | vectorbt | CONFIRMS |

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

### plano_b_v4_daily

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
# VERDICT — Plano B Cross-Library Validation

> Generated: 2026-04-20T23:02:05.751800+00:00.
> Baseline commit: `10eb9f824030`.
> Baseline hash: `c130ef614411`.

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
| 1 | quantstats(from=backtrader) | REFUTES |
| 1 | quantstats(from=bt) | REFUTES |
| 1 | backtrader | REFUTES |
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
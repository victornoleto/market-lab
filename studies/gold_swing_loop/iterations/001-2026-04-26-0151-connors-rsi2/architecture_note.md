# Iter 001 — Simulator architecture decision

## Decision

**Lightweight per-iter scripts** for early iters (001-005). Promote
shared logic into a `studies/gold_swing_loop/simulator.py` module
**only** once 3-5 iterations show a stable pattern.

## Rationale

- The sister loop's `src/ai_trade/backtest/strategies/` modules are
  designed for **multi-asset stack** strategies (LETF rotation, sector
  momentum). Single-asset day/swing has different semantics (binary
  position vs continuous notional, signal-driven exits vs timed
  rebalances).
- Iter 001 introduces a Connors RSI(2) signal that is unique to this
  iteration. Forcing a shared abstraction now risks designing for a
  hypothetical future signal (sister-loop dead-end IC-4 modulation).
- Loop-level reusable helpers are already extracted:
  - `studies/gold_swing_loop/datasets.py` (dataset loading + slicing)
  - `studies/gold_swing_loop/cost_models.py` (Track A + Track B)
  - `studies/gold_swing_loop/scoring.py` (rubric)
- Per-iter `run_backtest.py` only needs the strategy-specific signal
  generation + position rules. ~150-250 LOC per iter.

## Promotion criteria (when to refactor)

Move the per-iter simulator into a shared `simulator.py` when:

1. ≥ 3 iters share the **same** position-generation contract
   (binary long, exit-on-signal, etc.), AND
2. The duplicated code across iters exceeds ~80 LOC, AND
3. The next planned iter would also fit the same pattern.

Until then: **copy the boilerplate**. Premature shared abstraction is
a known sister-loop sin (see strategy_hunt_loop iter 037-040 history).

## Validation hooks each per-iter script must call

Loop infra dictates the contract:

```python
from studies.gold_swing_loop.datasets import load_dataset, slice_window, SLICES
from studies.gold_swing_loop.cost_models import (
    apply_pepperstone_costs, apply_inter_costs_with_darf,
)
from studies.gold_swing_loop.scoring import (
    score_strategy, DatasetMetrics, Gates,
)
```

Output JSON contract (`results.json`):

```json
{
  "config_id": "<slug>",
  "params": {...},
  "per_dataset": {
    "<dataset>": {
      "track_a_metrics": {"sharpe": ..., "cagr": ..., "mdd": ..., "mean_hold_days": ..., "n_trades": ...},
      "track_b_metrics": {...},
      "gates": {"g1_pbo": bool, ..., "g7_crosslib": bool}
    }
  },
  "returns_series": {
    "<dataset>": {"<cfg_id>": {"index": [ISO dates], "net_returns": [...]}}
  }
}
```

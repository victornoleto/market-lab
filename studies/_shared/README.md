# studies/_shared

Shared infrastructure used by active research loops in `studies/`.

## Contents

| file | purpose | canonical source |
|---|---|---|
| `tax_engine.py` | `AnnualDarfEngine` — Lei 14.754/2023 annual DARF model | mirrored from `studies/global_factor_tilt_loop/tax_engine_v2.py` (FROZEN) |

## Principles

- **Minimal**. Only files that are *actually* shared by ≥ 2 active
  loops live here. `scoring.py`, `plot_helper.py`, `run_loop.sh`
  diverge per-loop (different missions, benchmarks, plot defaults) —
  not shared.
- **No magic imports**. Loops do `from _shared.tax_engine import
  AnnualDarfEngine` with explicit `sys.path.insert(0, "studies")`
  in their own scoring/backtest scripts.
- **Frozen mirroring is okay**. `tax_engine.py` here is byte-identical
  to `global_factor_tilt_loop/tax_engine_v2.py` (which is FROZEN,
  do-not-touch). Both stay in sync; if the law changes again, update
  both deliberately.

## Usage example

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "studies"))

from _shared.tax_engine import AnnualDarfEngine

engine = AnnualDarfEngine(initial_investment=10_000.0)
# ... apply returns, record trades, year_end_settlement ...
```

See `studies/global_factor_tilt_loop/iterations/014-*/backtest.py`
for the canonical integration example (iter 014 — annual-DARF rerun).

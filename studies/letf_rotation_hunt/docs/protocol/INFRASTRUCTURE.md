# Infrastructure — letf_rotation_hunt

## Reuse map

| Component | Source | Use |
|---|---|---|
| Synth Gayed methodology | `src/market_lab/backtest/helpers/synthetic_letf.py` | wrapped by `synths.py` (FFR-aware default) |
| LETF rotation engine | `src/market_lab/backtest/strategies/letf_rotation.py` | consumed by strategies (NOT modified) |
| Tax engine Lei 14.754 | `studies/_shared/tax_engine.py` (symlink `_shared/tax_engine.py`) | wrapped by `tax_layer.py` |
| Testfolio cache | `data/testfolio/*.json` | source for SPY/QQQ/GLD/ZROZ/TLT/IEF/UPRO/SSO/QLD/TQQQ/UGL/TMF synth series |
| Tiingo cache | `data/tiingo/daily/{prices,meta}/` | source for real ETF (parity check + post-inception data) |
| Hunt-loop pattern | `studies/spy_beater_hunt/` | template for `run_iter.py`, `scoring.py`, `BASE_MEMORY.md` |

## Data dependencies

- `data/testfolio/cashx.json` — FFR proxy (BIL OFF + borrow modeling)
- `data/tiingo/daily/prices/UPRO.parquet`, etc. — real ETF post-inception
- `data/external/` — auxiliary (VIX historical, etc.)

## Universe limitations (per spec §4.1)

- T4 universe limited: `{UPRO, QLD, UGL, TMF}` for 1985+ window; SOXL added only in T4d (2010+ window)
- FAS/ERX/TNA excluded (sector LETF data gap)

## Dataset windows

| Dataset | Window | Bottleneck |
|---|---|---|
| lh_56y | 1970-01 → 2026-04 | SPYSIM |
| spy_real | 2003-01 → 2026-04 | Tiingo SPY |
| ndx_real | 2010-02 → 2026-04 | Tiingo QQQ |

## External libraries

- `numpy >= 1.24`, `pandas >= 2.0`, `scipy >= 1.10` (already in pyproject)
- `matplotlib >= 3.7` (plots)
- `hmmlearn >= 0.3` (HMM regime classifier — T3e)
- `jsonschema >= 4.0` (verdict.json validation)
- `pytest >= 7.4` (tests)

If `hmmlearn` not installed: `uv pip install hmmlearn jsonschema`.

# Phase 6D — Inverse Sleeve In Risk-Off (PRE-REGISTRATION)

> Status: research-only / diagnostic. Nothing here authorizes deployment, paper
> trading or a mandate change. Mandate §1 (maintenance mode) unchanged.
> **Run order note:** the Phase 6 round executes 6C → 6B → 6D → 6A.

## Question

The original restart plan deferred a bear-market sleeve (Phase 3B) because no
inverse series existed in the Testfol.io cache. This phase unblocks it with a
**local synthesis** and asks: does adding a small, capped inverse position to
the risk-off sleeve reduce drawdown without destroying CAGR through whipsaw?
Prior is LOW given the 3A/3A-2 negatives (every added mechanism failed to beat
the clean base), but the user approved testing it once before the frontier
phase. The short side of a trend rule is a known, citable construct — and a
known underperformer vs long-only, which is exactly why the sleeve is small and
capped `[trading_systems_methods, p.354]`, `[systematic_trading, p.137-148]`.

## Data resolution (previous blocker)

No inverse tickers exist in `data/testfolio/cache/history.parquet` and there is
no programmatic Testfol.io fetcher (cache built from manual JSON exports). The
phase synthesizes inverse daily returns **in memory** (cache untouched):

```
r_inv = -1 · r_underlying − 0.0095/252
```

mirroring the repo's existing negative-leverage synthesis precedent
(`_synth_leveraged_returns`, `src/market_lab/backtest/strategies/
ema_sma_threshold_educational.py`) with the same 0.95% annual fee drag
`[leverage_for_the_long_run, p.16, fn.22-23]`. Daily-reset −1x compounding is
inherent in this formula, exactly as in real inverse ETFs. A Testfol.io
`?L=-1` manual download remains an optional cross-check, not a dependency.

## Mechanism (one family — risk-off composition only)

The headline geometries stay fixed (SPY `L2.00 / 50 ZROZ 25 GLD 25 CASH /
RV21<=30%`; QQQ `L1.75 / 40 ZROZ 40 GLD 20 IEF / RV63<=40%`), **binary vol gate
retained** — the only new mechanism is blending a capped inverse fraction into
the risk-off sleeve:

```
risk_off' = (1 − f) · risk_off + f · {INV: 1}
```

## Pre-registered grid — 36 rows (+36 to the n_trials ledger → 3984)

| Axis | Values | Anchor |
|---|---|---|
| Branch | SPY, QQQ headline bases | Phase 2/4 |
| Inverse fraction `f` | `0.10, 0.15, 0.25` | capped sizing; never a full-size bear bet `[systematic_trading, p.137-148]` |
| lag | `0..5` | restart convention |

## Pre-registered screen (per branch, vs the matching headline at the same lag)

Success = after-tax CAGR ≥ headline **AND** MDD strictly better (less negative),
**read at the committed headline lag** (SPY lag 3, QQQ lag 0); the other lags
are reported as sensitivity only, not as escape hatches. Crisis-window deltas
(2000–02, 2008, 2020, 2022 — Phase 6A's pre-registered dates) are reported as
diagnostics only. If the inverse sleeve only pays in one post-hoc crisis and
bleeds elsewhere, that is a FAIL by design.

Sanity check built in: `f = 0` must reproduce the headline base byte-for-byte.

## Outputs

`lrs/results/phase06d_inverse_sleeve.csv`, `REPORT.md`, plots (equity/DD best-f
vs f=0, crisis zooms, CAGR/MDD vs f), `tests/test_lrs_phase06d.py`.

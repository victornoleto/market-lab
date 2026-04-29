# Iter 019 — Hypothesis: C.2 — Vol-managed 60/40 (NTSX+IEF)

## Hypothesis (one paragraph)

Test **vol-targeting** as a mechanism: dynamically scale a 60/40-style
NTSX+IEF base by inverse realized volatility to target a fixed annualized
vol. Mechanism: `weight_t = target_vol / realized_vol_60d`, capped at
[0.5, 2.0]. When market vol spikes (2008 GFC, 2020 COVID, 2022 rate hike),
the strategy scales down defensively; when vol normalizes, scales back up.
This is the canonical "managed-vol" mechanism from `[systematic_trading,
p.137-148]` Carver. Hypothesis: vol-targeting smooths returns and avoids
the worst left-tail events without sacrificing average CAGR — different
mechanism from iter 011 (static stack) and iter 018 (rotation).

## Citations

- `[systematic_trading, p.137-148]` — Carver: vol-targeting / position sizing
- `[risk_parity, ch.5]` — Carlson: 60/40 cap-efficient base
- Gates: `[advances_fin_ml, p.208-211, p.222-223, p.196-202, p.31-34]`

## Datasets

lh_56y / vt_real / ndx_real (NTSX SPYSIM bottleneck 1986+ for lh_56y).

## Pre-committed kill criteria

**KILL #1**: Best-of-grid loses iter 011 on ≥ 2/3 datasets → vol-targeting
on 60/40 doesn't add Sharpe in this universe.

**KILL #2**: Sharpe monotonically decreases as target_vol rises → vol cap
mechanism is hurting more than it helps; reduces to pure 60/40 base.

## Configs (4)

Base = 60% NTSX + 40% IEF (cap-efficient 60/40 stack, ~1.4× notional).
Position weight scaled by `target / realized_60d_vol`, capped [0.5, 2.0].

| config | target_vol | rationale |
|---|---:|---|
| `vt_8pct`  | 8%  | conservative, frequent de-risking |
| `vt_10pct` | 10% | classic Carver vol-target |
| `vt_12pct` | 12% | moderate |
| `vt_15pct` | 15% | aggressive, near base 60/40 unmanaged vol |

**Selection rule**: max mean(gross_Sharpe / avg(SPY,VT)_Sharpe).
**N_CONFIGS = 4** → DSR n_trials = 4.

## Probability assessment

- P(strict ADVANCE): ~10% — vol-targeting is well-studied; gains are
  mostly MDD reduction not Sharpe enhancement.
- P(positive signal): ~20%.
- P(STRONG/PROMISING no advance): ~50%.
- P(FAIL): ~20%.

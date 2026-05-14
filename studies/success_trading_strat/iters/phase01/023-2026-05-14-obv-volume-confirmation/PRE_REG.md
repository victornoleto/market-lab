# PRE_REG — 023 OBV volume confirmation

## Hypothesis

On-Balance Volume (OBV) accumulates signed volume and is intended to detect
accumulation/distribution pressure before or alongside price movement
`[trading_systems_methods, p.537]`. This iteration tests whether a lagged OBV
accumulation filter can time `SPY`/`QQQ` exposure better than same-asset
buy-and-hold, using MCPT and walk-forward MCPT as additional anti-overfit gates
`[testing_tuning, p.318-320]`. This is a genuinely different information source
from the prior price-only KAMA/Efficiency Ratio smoother, and local tuning stops
after these four configs `[testing_tuning, p.327-335]`.

## Configs

Exactly 4 configs, counted as 4 new strategy trials:

| name | asset | obv_lookback | price_filter |
|---|---:|---:|---|
| `spy_obv21` | `SPY` | 21 | none |
| `qqq_obv21` | `QQQ` | 21 | none |
| `spy_obv63_price63` | `SPY` | 63 | trailing 63d price return > 0 |
| `qqq_obv63_price63` | `QQQ` | 63 | trailing 63d price return > 0 |

Rules:

- OBV is cumulative `sign(adj_close_t - adj_close_{t-1}) * volume_t`
  `[trading_systems_methods, p.537]`.
- Risk-on if `OBV_t - OBV_{t-lookback} > 0`; optional price filter requires
  `adj_close_t / adj_close_{t-63} - 1 > 0` to avoid buying against medium-term
  trend `[trading_systems_methods, p.939]`.
- Signals are shifted one trading day before returns are applied to avoid
  same-close lookahead `[advances_fin_ml, p.196-202]`.
- Risk-off sleeve is `SHV`.

## Data And Window

- Local Tiingo daily parquet cache: `data/tiingo/daily/prices/`.
- Required tickers: `SPY`, `QQQ`, `SHV` with `adj_close` and `volume` for risk
  assets.
- Common window starts `2010-01-01` and must end no earlier than `2026-03-31`.
- If required data or columns are missing, close as `data_blocked` with
  `n_trials=0`.

## Benchmark

Each config is compared to same-asset buy-and-hold over the same aligned window.
Promotion requires strategy Sharpe greater than same-asset benchmark Sharpe.

## Planned Gates

- Data freshness: common end date >= `2026-03-31`.
- Economic Sharpe vs same-asset buy-and-hold.
- IS MCPT on best fixed config, 200 permutations, pass `p <= 0.01`
  `[testing_tuning, p.318-320]`.
- WF MCPT on best fixed config, 100 permutations, pass `p <= 0.05`
  `[testing_tuning, p.318-320]`.
- PBO over the 4-config return matrix with 8 blocks, pass `< 0.5`
  `[advances_fin_ml, p.208-211]`.
- DSR on best config with cumulative `n_trials=80`, pass `p < 0.05`
  `[advances_fin_ml, p.222-223]`.
- Walk-forward positive windows: at least 6 positive windows when >=8 windows are
  available `[testing_tuning, p.148-150]`.
- Single-block OOS final 20% return > 0 `[advances_fin_ml, p.196-202]`.
- FWD stress latest 63 observations > 0 `[advances_fin_ml, p.196-202]`.
- Stationary bootstrap 99.9% mean daily CI low > 0 `[testing_tuning, p.246-247]`.
- Cross-lib NumPy-style implementation CAGR within +/-3pp
  `[advances_fin_ml, p.31-34]`.

## Kill Rules

- If volume data are unavailable or stale, close `data_blocked`; do not replace
  OBV with price-only logic after pre-registration.
- If IS/WF MCPT, PBO or DSR fails, do not tune OBV lookbacks or add filters in
  this iteration `[testing_tuning, p.327-335]`.
- No deployment claim; mandate remains 100% Plano C.

## Trial Accounting

- `cumulative_n_trials_before = 76`
- `n_trials_planned = 4`
- `cumulative_n_trials_after = 80`

## Ambiguity Note

The baseline worktree already contained unrelated modified/untracked files
(`data/tiingo/manifest.json`, public docs, `scripts/tiingo_bulk_download.py`, the
untracked study scaffold, tests and `youtube-transcript/`). Per protocol, I will
not revert or touch unrelated files. Because iteration 022 was a `fail`, I chose
a different information source rather than local tuning.

# PRE_REG — 004-2026-05-14-equity-volatility-system

## Hypothesis

Daily equity-index swing systems may benefit from a volatility reversal/trailing
stop rule: enter risk when price reverses upward by a multiple of recent True
Range, and exit to cash when price reverses downward by the same rule. Kaufman
describes True Range and Bookstaber's volatility system as a price move measured
against average range, with `k` around 3 `[trading_systems_methods, p.107]`,
`[trading_systems_methods, p.333]`. This is a distinct Track A daily-swing
mechanism, not a local retune of the prior gold Donchian/RSI/CCI families
`[testing_tuning, p.327-335]`.

## Data And Window

- Physical audit before testing: daily `SPY`, `QQQ`, `SHV` parquet files;
  `data/tiingo/1hour/prices/` physical parquet count; `data/tiingo/15min/prices/`
  presence/count.
- Strategy data: local Tiingo daily adjusted OHLC for `SPY` and `QQQ`; local
  Tiingo daily adjusted close for `SHV` while flat.
- Window: full overlap after warmup in each asset's local daily parquet.
- Intraday: no 1h/15m test unless physical files exist and audit records range,
  timezone/session and missing bars. If absent, do not synthesize intraday bars.

## Exact Configs

1. `spy_vs20_k25`: `SPY`, average True Range lookback 20, reversal multiple 2.5.
2. `spy_vs20_k30`: `SPY`, average True Range lookback 20, reversal multiple 3.0.
3. `qqq_vs20_k25`: `QQQ`, average True Range lookback 20, reversal multiple 2.5.
4. `qqq_vs20_k30`: `QQQ`, average True Range lookback 20, reversal multiple 3.0.

Execution rule: signals are computed at close and shifted one bar before returns
are earned. While out of risk asset, hold `SHV`.

## Benchmark

- Primary benchmark: same-asset buy-and-hold over the aligned strategy window.
- Context benchmark: `SPY` buy-and-hold over the aligned strategy window.
- Economic screen: best config must beat same-asset buy-and-hold Sharpe to be any
  candidate.

## Planned Gates

- IS MCPT on the best fixed rule: 200 permutations; promotional pass only if
  `p <= 0.01` `[testing_tuning, p.318-320]`.
- WF MCPT on the best fixed rule: 100 permutations; pass if `p <= 0.05`
  `[testing_tuning, p.318-320]`.
- PBO across the 4 pre-registered configs, `n_blocks=10`; pass if `<0.5`
  `[advances_fin_ml, p.208-211]`.
- DSR on the best config using cumulative trials after this iteration; pass if
  `p < 0.05` `[advances_fin_ml, p.222-223]`.
- Walk-forward: at least 8 one-year windows and at least 6 positive windows
  `[testing_tuning, p.148-150]`.
- OOS: final 20% compounded return positive `[advances_fin_ml, p.196-202]`.
- FWD stress: latest 63-trading-day compounded return positive
  `[advances_fin_ml, p.196-202]`.
- Bootstrap: 99.9% mean-daily CI low > 0 `[testing_tuning, p.246-247]`.
- Cross-lib/vector parity: loop and vector implementation CAGR delta <= 3pp
  `[advances_fin_ml, p.31-34]`.

## Kill Rules

- If any required daily physical file is missing, stop as `data_blocked` before
  consuming trials.
- If intraday physical files remain absent, record the block and run only daily.
- If same-asset Sharpe, MCPT, PBO or DSR fail, do not locally tune `k`/lookback in
  this iteration.
- No live deployment or capital change; mandate remains 100% Plano C.

## Trial Accounting

- `cumulative_n_trials` before: 112.
- New strategy configs: 4.
- `cumulative_n_trials` after if data audit passes: 116.

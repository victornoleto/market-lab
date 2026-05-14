# PRE_REG — 012-2026-05-14-demark-setup-reversal

## Hypothesis

Daily DeMark-style exhaustion setups can capture short swing rebounds after nine
consecutive closes below the close four bars earlier, but only while the asset is
above its 200-day trend filter. DeMark setup/countdown rules use the 4-bar close
comparison and 9-count exhaustion premise `[trading_systems_methods, ch.4,
p.173-175]`; the 200-day trend filter follows the stock-market macro benchmark
moving-average convention `[trading_systems_methods, p.285]`. Signals are shifted
one completed daily bar before earning returns to avoid same-close lookahead
`[advances_fin_ml, p.31-34]`.

## Exact Configs

All configs are long-only, hold `SHV` while flat, and use adjusted daily close.

| name | asset | setup_count | trend_filter | exit | max_hold |
|---|---|---:|---|---|---:|
| `spy_demark9_sma200_hold13` | `SPY` | 9 | close > SMA200 | close > close[t-4] or trend break | 13 |
| `qqq_demark9_sma200_hold13` | `QQQ` | 9 | close > SMA200 | close > close[t-4] or trend break | 13 |
| `gld_demark9_sma200_hold13` | `GLD` | 9 | close > SMA200 | close > close[t-4] or trend break | 13 |
| `xau_demark9_sma200_hold13` | `xauusd` | 9 | close > SMA200 | close > close[t-4] or trend break | 13 |

The setup count, 4-bar comparison and 13-bar maximum holding period are tied to
the DeMark setup/countdown description rather than locally optimized
`[trading_systems_methods, ch.4, p.173-175]`.

## Data And Window

Primary files: `data/tiingo/daily/prices/{SPY,QQQ,GLD,xauusd,SHV}.parquet`.
The script must audit physical files, date ranges, timezone metadata, columns and
business-day missing rate before testing. It must also record that
`data/tiingo/1hour/prices/` and `data/tiingo/15min/prices/` are unavailable or
empty if that remains true; no intraday bars may be synthesized.

The tested window is each strategy's post-warmup overlap with its asset and `SHV`.

## Benchmarks

Primary benchmark: same-asset buy-and-hold on the identical aligned date index.
Opportunity-cost benchmark: `SPY` buy-and-hold on the identical aligned date
index, including when the tested asset is `QQQ`, `GLD` or `xauusd`.

## Planned Gates

- Economic CAGR vs same-asset buy-and-hold: must pass for any status above `fail`
  `[systematic_trading, p.40]`, `[testing_tuning, p.327-335]`.
- Economic Sharpe vs same-asset buy-and-hold.
- IS MCPT with 200 reps, pass `p <= 0.01` `[testing_tuning, p.318-320]`.
- WF MCPT with 100 reps, pass `p <= 0.05` `[testing_tuning, p.318-320]`.
- PBO over the 4 configs with 10 blocks, pass `< 0.5` `[advances_fin_ml,
  p.208-211]`.
- DSR using cumulative trials after this iteration, pass `p < 0.05`
  `[advances_fin_ml, p.222-223]`.
- Walk-forward: at least 6 positive windows and at least 8 windows total
  `[testing_tuning, p.148-150]`.
- OOS final 20% total return positive `[advances_fin_ml, p.196-202]`.
- Latest 63 trading days positive `[advances_fin_ml, p.196-202]`.
- Bootstrap 99.9% mean-daily CI low > 0 `[testing_tuning, p.246-247]`.
- Cross-lib/vector parity: CAGR delta <= 3pp `[advances_fin_ml, p.31-34]`.

## Kill Rules

- If any required daily physical file is missing, stop as `data_blocked` with
  `n_trials=0`.
- If strategy CAGR <= same-asset buy-and-hold CAGR, status must be `fail`; lower
  drawdown alone cannot promote this non-hedge hypothesis.
- Any PBO/DSR/MCPT/WF/OOS/FWD/bootstrap/cross-lib failure blocks
  `strict_winner`.
- Do not tune thresholds after seeing results; DeMark setup parameters are fixed
  for this iteration `[testing_tuning, p.327-335]`.

## Trial Accounting

- `cumulative_n_trials` before: 144.
- New configs: 4.
- `cumulative_n_trials` after if tested: 148.

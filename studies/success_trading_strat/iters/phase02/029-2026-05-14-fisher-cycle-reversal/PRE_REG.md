# PRE_REG — 029-2026-05-14-fisher-cycle-reversal

## Hypothesis

Daily Fisher Transform cycle-reversal signals may identify short swing rebounds after bounded-price exhaustion on `SPY`, `QQQ`, `GLD` and `xauusd`. Fisher converts a bounded input into a near-Gaussian oscillator with sharper turning points `[cycle_analytics, p.195-197]`; this iteration uses it only as a pre-registered rule, not as a tuned discovery engine. Signals are shifted one completed daily bar before returns are earned to avoid same-close lookahead `[advances_fin_ml, p.31-34]`.

## Data And Window

- Physical daily cache: `data/tiingo/daily/prices/{SPY,QQQ,GLD,SHV,xauusd}.parquet`.
- Intraday audit targets: `data/tiingo/1hour/prices/` and `data/tiingo/15min/prices/`.
- If required daily files or close columns are missing, close `data_blocked` with `n_trials=0`.
- No intraday bars will be synthesized. If `1h`/`15m` files are absent, record intraday as blocked and test daily only per Phase 2 data rules.

## Exact Configs

All configs use `Fisher(10)`, a `SMA200` trend filter, entry when Fisher crosses upward while still below `-1.0`, exit when Fisher reaches `0.5` or after `10` daily bars, and `SHV` while flat.

1. `spy_fisher10_reversal_sma200_h10`: `SPY`
2. `qqq_fisher10_reversal_sma200_h10`: `QQQ`
3. `gld_fisher10_reversal_sma200_h10`: `GLD`
4. `xau_fisher10_reversal_sma200_h10`: `xauusd`

Parameter citations: Fisher normalization/transform follows Ehlers' bounded-transform logic `[cycle_analytics, p.195-197]`; the slow trend filter is a conservative anti-countertrend guard using the common long-term moving-average convention `[trading_systems_methods, p.284]`; max-hold exit prevents open-ended oscillator trades after the expected short swing fails `[testing_tuning, p.327-335]`.

## Benchmarks

- Primary benchmark: same-asset buy-and-hold on each config's aligned post-warmup dates.
- Opportunity-cost benchmark: `SPY` buy-and-hold on the same aligned dates.
- Gold context: report both `GLD` and `xauusd` buy-and-hold metrics when available.

## Planned Gates

- Economic CAGR vs same-asset buy-and-hold: must pass before any `candidate_watchlist`, `paper_trade_candidate` or `strict_winner` label `[systematic_trading, p.40]`, `[testing_tuning, p.327-335]`.
- Economic Sharpe vs same-asset buy-and-hold.
- IS MCPT with 200 permutations on the selected best config `[testing_tuning, p.318-320]`.
- WF MCPT with 100 permutations `[testing_tuning, p.318-320]`.
- PBO `< 0.5` across the 4 configs `[advances_fin_ml, p.208-211]`.
- DSR `p < 0.05` using cumulative trials after this iteration `[advances_fin_ml, p.222-223]`.
- Walk-forward: at least 8 windows and at least 6 positive `[testing_tuning, p.148-150]`.
- OOS final 20% positive, latest 63d FWD positive, bootstrap 99.9% mean-daily CI low > 0, and vector parity within 3pp CAGR `[advances_fin_ml, p.196-202]`.

## Kill Rules

- CAGR <= same-asset buy-and-hold => `fail`.
- Any PBO/DSR hard-block fail => no `strict_winner`.
- Failed MCPT gates => no `strict_winner`; may still be recorded only as failed evidence.
- Missing required data => `data_blocked` and no proxy substitution.
- Do not tune Fisher length, thresholds, hold length or SMA length after seeing results.

## Trial Accounting

- `cumulative_n_trials` before: 212
- New strategy configs: 4
- `cumulative_n_trials` after if tested: 216

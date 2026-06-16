# US Stocks Full Run Summary

Run: `studies/momentum/config/us_stocks.yaml`, phase `broad`, full grid.

Status: research-only. No deployment, paper-trade label or mandate change.

## Run

- Universe: `us_stocks` only.
- Data source: local Postgres `yf_tickers`/`yf_daily_prices`.
- Raw active symbols loaded: `7.136`.
- Symbols passing YAML filters: `2.301`.
- Successful configs: `7.488/7.488`.
- Date range: `2000-02-29` to `2026-06-15`.
- Runtime reported by CLI: `1h02m06s`.
- Plots generated: `25` PNGs under `studies/momentum/plots/`.

## Verdict

The screen found a strong current-universe momentum signal in US stocks, but it is
not promotion-eligible. The useful conclusion is diagnostic: diversified
cross-sectional momentum ranks work much better than concentrated top-1/top-5
variants in this biased dataset, but drawdowns remain too large and the run is
still yfinance/current-universe research only `[advances_fin_ml, p.208-211]`.

No result should be interpreted as live-tradable. `broad` mode intentionally skips
the expensive final validation stack; final candidates still need full `validate`
mode, bootstrap, cross-check and non-survivorship/PIT data before any stronger
claim `[advances_fin_ml, p.273-275]`.

## Headline Rows

Best Sharpe:

- `mom_us_stocks_mom_3_6_12_equal_top50_reb1_off0`
- CAGR `46,91%`
- Excess CAGR vs SPY `38,60%`
- MDD `-55,54%`
- Sharpe `1,327`
- DSR p `0,0009`
- WF `8/8`
- Annual turnover `4,16x`

Best CAGR:

- `mom_us_stocks_raw_13612_equal_top5_reb3_off1`
- CAGR `95,00%`
- Excess CAGR vs SPY `86,46%`
- MDD `-75,42%`
- Sharpe `0,823`
- DSR p `0,218`
- WF `7/8`
- Interpretation: return headline is not robust enough; it is too concentrated
  and drawdown-heavy.

Best row with `MDD >= -50%`, `DSR p < 0,05`, `WF >= 6/8`:

- `mom_us_stocks_vol_adjusted_equal_top50_reb3_off0`
- CAGR `29,34%`
- Excess CAGR vs SPY `20,85%`
- MDD `-49,72%`
- Sharpe `1,142`
- DSR p `0,0237`
- WF `7/8`
- Annual turnover `2,89x`
- This is the cleanest follow-up candidate from the broad screen, but still has
  high drawdown and must go through `validate`.

## Risk Cuts

- `MDD >= -75%`: `5.170` configs.
- `MDD >= -60%`: `1.810` configs.
- `MDD >= -55%`: `1.062` configs.
- `MDD >= -50%`: `506` configs.
- `MDD >= -45%`: `168` configs.
- `MDD >= -40%`: `32` configs.
- `MDD >= -35%`: `0` configs.
- `MDD >= -30%`: `0` configs.
- `MDD >= -25%`: `0` configs.

Among rows with `DSR p < 0,05` and `WF >= 6/8`:

- `MDD >= -60%`: `286` rows.
- `MDD >= -55%`: `50` rows.
- `MDD >= -50%`: `6` rows.
- `MDD >= -45%`: `0` rows.

Conclusion: once risk is constrained below roughly `-45%`, no statistically
interesting broad-screen row remains.

## Mechanism Read

Best mechanism families by PBO:

- `mom_3_6_12` variants: strongest PBO cluster (`~0,016` to `0,052` for the best
  families), and also top Sharpe.
- `raw_13612` variants: also strong PBO (`~0,028` to `0,206`) and high returns.
- `mom_12_1`: mixed; equal-weight variants pass, inverse-vol variants are weaker.
- `clenow_trend`: equal-weight non-staggered variants pass, but many weighted or
  staggered variants fail.
- `vol_adjusted`: produces the best risk-constrained follow-up row, but mechanism
  PBO is mixed.
- `mom_lowvol_composite`: lower drawdown, but mechanism PBO fails and returns are
  much weaker.

Overall PBO in `REPORT.md` is `0,052`, but it is sampled `1000/7488`, so it is a
broad-screen diagnostic, not a final robustness gate.

## Structural Patterns

- Larger `top_n` improves Sharpe and reduces median drawdown. Median MDD improves
  from about `-97,9%` at top-1 to about `-61,2%` at top-50.
- Equal weight is competitive with inverse-vol and capped-inverse-vol; weighting
  complexity does not obviously pay for itself in the broad screen.
- `absolute_filter` often duplicates non-absolute rows at the top, meaning the top
  momentum names usually already have positive scores.
- Staggering helps timing-luck diagnostics, but it does not solve drawdown.

## Next Step

Run `validate` only on a short, pre-selected candidate set. Natural candidates:

- Best Sharpe/high-return diagnostic: `mom_3_6_12_equal_top50_reb1_off0`.
- Best risk-constrained row: `vol_adjusted_equal_top50_reb3_off0`.
- Optional family anchor: `raw_13612_equal_top50_reb1_off0`.

Do not promote anything from this run. The next honest work is finalist validation
and data-bias reduction: PIT membership, delisted names, corporate-action audit and
independent implementation checks `[advances_fin_ml, p.208-211]`.

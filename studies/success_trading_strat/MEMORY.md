---
mission: "Find an efficient trading strategy using MCPT + WF + repo hard gates"
status: phase2_closed_no_winner
active_phase: 2
active_phase_name: "phase2 intraday short swing and gold/XAUUSD"
total_iterations: 30
target_total_iterations: 30
cumulative_n_trials: 216
latest_iteration: "030-2026-05-14-phase2-closure-audit"
latest_status: "fail"
latest_winner: false
latest_best_config: null
latest_best_cagr: null
latest_best_mdd: null
latest_pbo: null
latest_dsr_p_value: null
winner_iter: []
dead_end_families: ["daily_sma_momentum_regime_spy_qqq", "monthly_cross_sectional_etf_momentum", "volatility_targeted_static_sleeves", "rsi2_etf_mean_reversion", "vxx_volatility_carry_proxy", "multi_asset_ewmac_etf_trend", "etf_pairs_zscore_mean_reversion", "vix_managed_equity_exposure_fwd_fail", "vix_managed_floor_window_stress", "crypto_donchian_trend_fwd_fail", "crypto_vol_target_momentum_pbo_fail", "realized_vol_compression_equity_momentum", "credit_risk_appetite_hyg_ief_filter", "carver_multi_asset_positive_ewmac_forecast", "ehlers_cycle_mode_overlay", "yield_carry_rotation", "turn_of_month_seasonality", "intraday_overnight_component_decomposition", "kama_efficiency_regime", "obv_volume_confirmation_mcpt_fail", "accumulation_distribution_volume_pressure", "market_breadth_proxy", "sector_relative_strength_risk_appetite", "gayed_letf_qqq_rotation_pbo_dsr_fail", "correlation_breakdown_risk_filter", "gold_donchian_compression_breakout", "gold_rsi_exhaustion_mean_reversion", "gold_cci_breakout", "equity_volatility_system", "equity_gap_recovery_continuation", "equity_momentum_pullback", "equity_bollinger_reversion", "gold_macd_trend", "equity_adx_trend", "gold_keltner_atr_breakout", "equity_stochastic_close_location_pullback", "demark_setup_reversal", "gold_relative_strength_spy_filter", "vidya_adaptive_trend_filter", "bollinger_compression_breakout", "trix_trend_continuation", "woodshedder_roc", "clenow_adjusted_slope_trend", "force_index_volume_impulse", "elder_ray_triple_screen", "wilder_asi_swing_breakout", "regression_channel_breakout", "money_flow_index_pullback", "dual_ma_atr_breakout", "swing_point_breakout", "price_density_trend_filter", "williams_r_exhaustion_reversal", "cmo_momentum_continuation", "fisher_cycle_reversal"]
---

# MEMORY — success_trading_strat

Read this file at the start of every fresh loop session. It is the short state,
not a replacement for `SPEC.md`.

## Current State

Iterations 001-002 preserved Tiingo data and added a reusable validation
scaffold. Iterations 003-006 tested the first small strategy families and all
closed as `fail` after MCPT, benchmark and/or hard-gate rejection. Iteration 007
pre-registered a volatility-carry proxy but closed `data_blocked` before testing
because required `VIXY` cache data were missing. Iteration 008 re-registered the
same mechanism with confirmed `VXX` data and closed `fail` after MCPT, PBO and
DSR rejection. Iteration 009 pivoted to a small fixed multi-asset EWMAC family and
also closed `fail` after benchmark Sharpe, MCPT, PBO and DSR rejection. Iteration
010 pivoted to ETF pairs z-score mean reversion and closed `fail`: the best bond
pair had positive CAGR but failed SHV benchmark Sharpe, MCPT, DSR and bootstrap.
Iteration 011 pivoted to VIX-managed equity exposure and produced the strongest
statistical result so far: best `qqq_vix15_w21` passed benchmark Sharpe, IS MCPT,
WF MCPT, PBO, DSR, WF, OOS, bootstrap and cross-lib, but still closed `fail`
because the last 63-trading-day FWD stress was negative. Iteration 012 stressed
that family with fixed floors, a longer VIX window and a SPY/QQQ basket; the best
variant improved Sharpe/CAGR but failed IS MCPT, PBO and the same 63d FWD gate.
Iteration 013 pivoted to BTC/ETH Donchian trend following and produced a strong
diagnostic result (`eth_don20` Sharpe 1.364, PBO 0.286, DSR p=0.00364, IS MCPT
pass), but still closed `fail` because walk-forward positives were only 5/6 and
the latest 63-observation FWD stress was negative. Iteration 014 tested crypto
volatility-targeted momentum as a non-Donchian pivot; best `btc_mom63_vt20`
improved Sharpe/MDD and passed FWD, DSR, OOS, bootstrap and cross-lib, but failed
IS MCPT, WF MCPT, PBO and WF positives.
Iteration 015 pivoted away from crypto-only and VIX-local variants into realized-
volatility compression plus positive momentum on `SPY/QQQ`; best
`qqq_rv20_p60_m63` improved MDD versus QQQ buy-and-hold but failed benchmark
Sharpe, IS MCPT, WF MCPT, PBO, DSR and bootstrap.
Iteration 016 tested a cross-asset credit-risk appetite filter using lagged
`HYG/IEF` ratio momentum plus own-asset momentum for `SPY/QQQ`; best
`spy_hygief126_m63` reduced drawdown versus SPY buy-and-hold but failed benchmark
Sharpe, IS MCPT, WF MCPT, PBO, DSR and bootstrap.
Iteration 017 tested a Carver-style diversified positive EWMAC forecast portfolio
with inverse-volatility weights and volatility targeting; best
`risk4_ewmac16_64_vt10` reduced drawdown versus equal-weight `SPY/QQQ/TLT/GLD`,
but failed benchmark Sharpe, IS MCPT, WF MCPT, PBO, DSR and latest 63d FWD stress.
Iteration 018 tested an Ehlers-style market-mode/cycle overlay on `SPY/QQQ` with
`SHV` defense; best `qqq_ehlers_c30_t15` improved Sharpe and MDD versus QQQ
buy-and-hold and passed PBO/DSR/WF/OOS/FWD/bootstrap/cross-lib, but failed both
IS MCPT and WF MCPT.
Iteration 019 pivoted to a simple carry/yield rotation using `SPY` dividend
yield versus cash and Treasury term-spread gates for `TLT`/`IEF`; best
`spy_div_gt_cash_ief_term` improved CAGR versus 60/40 `SPY/IEF`, but had worse
Sharpe/MDD and failed IS MCPT, WF MCPT, PBO, DSR and latest 63d FWD stress.
Iteration 020 pivoted to turn-of-month calendar seasonality in `SPY/QQQ` versus
`SHV`; best `spy_tom_l1_f4` reduced drawdown but failed same-asset benchmark
Sharpe, IS MCPT, WF MCPT, PBO and DSR.
Iteration 021 pivoted to adjusted-OHLC intraday/overnight decomposition in
`SPY/QQQ`; best `qqq_close_to_open` improved Sharpe/MDD versus QQQ buy-and-hold
and passed PBO, WF, OOS, FWD, bootstrap and cross-lib, but failed IS MCPT, WF
MCPT and DSR.
Iteration 022 pivoted to Kaufman's KAMA/Efficiency Ratio regime timing in
`SPY/QQQ`; best `qqq_kama_er20` reduced MDD versus QQQ buy-and-hold and passed
PBO, WF, OOS, FWD, bootstrap and cross-lib, but failed benchmark Sharpe, IS MCPT,
WF MCPT and DSR.
Iteration 023 pivoted to OBV volume-confirmation timing in `SPY/QQQ`; best
`qqq_obv21` improved Sharpe and drawdown versus QQQ buy-and-hold and passed PBO,
DSR, WF, OOS, FWD, bootstrap and cross-lib, but failed IS MCPT and WF MCPT.
Iteration 024 pivoted to close-location volume pressure via Accumulation/
Distribution and Intraday Intensity; best `qqq_ad21` lost to QQQ on Sharpe and
drawdown and failed IS MCPT, WF MCPT, PBO, DSR and bootstrap despite positive
WF/OOS/FWD diagnostics.
Iteration 025 pivoted to a current-constituent market breadth proxy; best
`spy_breadth_sma63_gt55` reduced drawdown versus SPY buy-and-hold and passed WF
MCPT, WF/OOS/FWD, bootstrap and cross-lib, but failed benchmark Sharpe, IS MCPT,
PBO and DSR. A survivorship caveat also blocks any promotional claim.
Iteration 026 pivoted to sector relative-strength risk appetite using `XLY/XLP`
and `XLK/XLU`; best `spy_xly_xlp_m126` reduced drawdown versus SPY buy-and-hold
and passed WF/OOS/FWD, bootstrap and cross-lib, but failed benchmark Sharpe, IS
MCPT, WF MCPT, PBO and DSR.
Iteration 027 pre-registered a commodity macro filter using `DBC`/`GLD` momentum
for `SPY`/`TLT`, but closed `data_blocked` before any backtest because
`data/tiingo/daily/prices/DBC.parquet` was unavailable. No proxy substitution was
made after preregistration, so `cumulative_n_trials` remains 92.
Iteration 028 pivoted to a Gayed-style LETF regime mechanism using lagged `QQQ`
signals to hold `QLD`/`TQQQ` or `SHV`. Best `qld_qqq_sma200_rv70` improved Sharpe
and drawdown versus QLD buy-and-hold and passed WF MCPT, WF/OOS/FWD/bootstrap and
cross-lib, but failed IS MCPT, PBO and DSR; `cumulative_n_trials` is now 96.
Iteration 029 tested a different cross-asset dependence mechanism: hold `SPY` or
`QQQ` only while lagged rolling equity/Treasury correlation is negative, otherwise
hold `SHV`. Best `spy_corr63_lt0` had CAGR 9.03%, Sharpe 0.562 and MDD -55.20%
versus SPY buy-and-hold CAGR 10.97%, Sharpe 0.627 and MDD -55.20%; it passed PBO
(`0.103`), WF windows, OOS, latest 63d FWD and cross-lib, but failed benchmark
Sharpe, IS MCPT (`p=0.810`), WF MCPT (`p=0.580`), DSR (`p=0.5240`) and bootstrap.
`cumulative_n_trials` is now 100. Iteration 030 performed the planned closure
audit at the 30-iteration cap. It tested no new strategy and consumed no trials.
The audit passed artifact completeness, trial accounting, target-iteration count
and zero-winner checks, but conservatively closed as `fail` because iteration 002
uses a legacy infrastructure `RESULTS.json` schema without the current
`status`/`pre_registered` fields. The study is closed with no winner and no deploy
implication `[testing_tuning, p.327-335]`, `[advances_fin_ml, p.222-223]`.

Post-loop review artifacts were added in
`studies/success_trading_strat/reports/overnight_30_iter_review/`: consolidated
summary table, recomputed curves for key near-misses, equity/drawdown/rolling
1/3/5/10/15y plots versus SPY and a pragmatic `candidate_watchlist`
classification. Phase 2 guidance lives in `PHASE2_INTRADAY_SWING_SPEC.md` and
splits future work into daily swing, short swing (`1h`/daily hybrid) and dedicated
gold/XAUUSD tracks `[testing_tuning, p.327-335]`.

Phase 1 iteration artifacts were moved to `iters/phase01/`. Phase 2 writes fresh
iteration artifacts under `iters/phase02/`; active phase counters were reset to
`total_iterations=0`, `target_total_iterations=30` while preserving cumulative
trial accounting at `cumulative_n_trials=100`.

Phase 2 iteration 001 tested daily `GLD`/`xauusd` Donchian breakout after realized
volatility compression. The intraday audit found `data/tiingo/1hour/prices/` has
zero physical parquet files, so `1h` gold/XAUUSD remains blocked. Best
`xau_dc100_rv20_p30` had CAGR 7.11%, Sharpe 0.726 and MDD -14.68% versus XAU
buy-and-hold CAGR 18.17%, Sharpe 1.099 and MDD -20.36%; it failed same-asset
Sharpe, IS MCPT (`p=0.315`), WF MCPT (`p=0.220`), PBO (`0.615`), DSR
(`p=0.7716`), WF sufficiency, FWD 63d and bootstrap. `n_trials=4`, cumulative
`n_trials=104`; family added to dead ends `[trading_systems_methods, p.353]`,
`[trading_systems_methods, p.481]`, `[advances_fin_ml, p.208-211]`.

Phase 2 iteration 002 tested daily `GLD` RSI exhaustion mean reversion with slow
trend filters after confirming again that `data/tiingo/1hour/prices/` has zero
physical parquet files. Best `gld_rsi2_e5_x60_sma200` had CAGR 6.35%, Sharpe
0.636 and MDD -25.34% versus `GLD` buy-and-hold CAGR 11.65%, Sharpe 0.693 and
MDD -45.56%; it failed same-asset Sharpe, IS MCPT (`p=0.200`), WF MCPT
(`p=0.140`), PBO (`0.556`), DSR (`p=0.3708`), latest 63d FWD (`-3.81%`) and
bootstrap. It passed WF windows (`11/17`), OOS and cross-lib parity. `n_trials=4`,
cumulative `n_trials=108`; family added to dead ends. MCPT used positive-shifted
log-price paths converted back inside the fixed rule to avoid invalid nonpositive
arithmetic-change permutations `[quant_trading_chan, p.51]`,
`[testing_tuning, p.318-320]`, `[advances_fin_ml, p.208-211]`.

Phase 2 iteration 003 tested daily close-only CCI breakout on `GLD` and `xauusd`
with `SMA200` trend confirmation after auditing physical daily and intraday cache
files. Daily `GLD`/`xauusd`/`SHV`/`SPY` files exist; `data/tiingo/1hour/prices/`
still has 0 parquet files and `data/tiingo/15min/prices/` is absent, so intraday
was not synthesized. Best `xau_cci40_e100_x0_sma200` had CAGR 9.92%, Sharpe
0.820 and MDD -14.68% versus `xauusd` buy-and-hold CAGR 17.36%, Sharpe 1.070 and
MDD -20.36%; it passed PBO (`0.214`), OOS and cross-lib, but failed same-asset
Sharpe, IS MCPT (`p=0.280`), WF MCPT (`p=0.450`), DSR (`p=0.7023`), WF
sufficiency (`3/3` positive but fewer than 8 windows), latest 63d FWD (`-6.27%`)
and bootstrap. `n_trials=4`, cumulative `n_trials=112`; family added to dead ends
`[trading_systems_methods, p.172]`, `[testing_tuning, p.318-320]`,
`[advances_fin_ml, p.208-211]`.

Phase 2 iteration 004 pivoted away from gold-only daily oscillators into a daily
SPY/QQQ volatility reversal system using average True Range distances. Physical
audit confirmed daily `SPY`/`QQQ`/`SHV` data through 2026-05-13, while
`data/tiingo/1hour/prices/` still has 0 parquet files and `data/tiingo/15min/prices/`
is absent, so intraday was not synthesized. Best `qqq_vs20_k30` had CAGR 9.34%,
Sharpe 0.629 and MDD -47.42% versus QQQ buy-and-hold CAGR 10.60%, Sharpe 0.509
and MDD -82.97%; it passed PBO (`0.048`), same-asset Sharpe, WF windows (`21/24`),
OOS, latest 63d FWD, bootstrap and cross-lib, but failed IS MCPT (`p=0.940`), WF
MCPT (`p=0.970`) and DSR (`p=0.2483`). `n_trials=4`, cumulative `n_trials=116`;
family added to dead ends. MCPT used the fixed rule on permuted close paths with a
close-to-close range proxy, so even a hypothetical pass would have required a
stricter OHLC permutation audit before promotion `[trading_systems_methods, p.107]`,
`[trading_systems_methods, p.333]`, `[testing_tuning, p.318-320]`,
`[advances_fin_ml, p.222-223]`.

Phase 2 iteration 005 tested daily SPY/QQQ down-gap recovery continuation using
adjusted OHLC bars. Daily files existed through 2026-05-13; `1hour/prices` still
had 0 parquet files and `15min/prices` was absent, so intraday was not synthesized.
Best `spy_gap10_recover` had CAGR 1.84%, Sharpe 0.370 and MDD -12.70% versus SPY
buy-and-hold CAGR 10.83%, Sharpe 0.646 and MDD -55.20%; it passed WF MCPT
(`p=0.010`), PBO (`0.171`), WF windows (`21/30`), OOS, FWD 63d and cross-lib, but
failed same-asset Sharpe, IS MCPT (`p=0.035` vs strict `<=0.01`), DSR (`p=0.6884`)
and bootstrap. `n_trials=4`, cumulative `n_trials=120`; family added to dead ends.
MCPT used a close-path downside-return proxy because close-only permutations do not
preserve OHLC gap structure `[trading_systems_methods, p.635]`,
`[testing_tuning, p.318-320]`, `[advances_fin_ml, p.208-211]`.

Phase 2 iteration 006 tested daily SPY/QQQ trend-filtered pullback swing rules
with fixed 5/10-bar holds and `SHV` while flat. Daily `SPY`/`QQQ`/`SHV` files
exist through 2026-05-13; `1hour/prices` still has 0 parquet files and
`15min/prices` is absent, so intraday was not synthesized. Best
`spy_pb3_m2_hold5` had CAGR 5.29%, Sharpe 0.862 and MDD -9.58% versus SPY
buy-and-hold CAGR 10.92%, Sharpe 0.621 and MDD -54.67%; it passed same-asset
Sharpe, IS MCPT (`p=0.010`), WF MCPT (`p=0.010`), PBO (`0.310`), WF windows
(`15/15`), OOS and cross-lib, but failed DSR (`p=0.1414`), latest 63d FWD
(`-2.55%`) and bootstrap. `n_trials=4`, cumulative `n_trials=124`; family added
to dead ends `[trading_systems_methods, p.172]`, `[quant_trading_chan, p.142-143]`,
`[advances_fin_ml, p.222-223]`.

Phase 2 iteration 007 tested daily SPY/QQQ Bollinger lower-band mean reversion
with `SMA200` trend filter, middle-band/time exits and `SHV` while flat. Daily
`SPY`/`QQQ`/`SHV` files exist through 2026-05-13; `1hour/prices` still has 0
parquet files and `15min/prices` is absent, so intraday was not synthesized.
Best `spy_bb20_2_hold10` had CAGR 3.38%, Sharpe 0.551 and MDD -17.17% versus SPY
buy-and-hold CAGR 10.92%, Sharpe 0.621 and MDD -54.67%; it passed WF windows
(`12/15`), OOS and cross-lib, but failed same-asset Sharpe, IS MCPT (`p=0.230`),
WF MCPT (`p=0.330`), PBO (`0.734`), DSR (`p=0.5942`), latest 63d FWD (`-2.56%`)
and bootstrap. `n_trials=4`, cumulative `n_trials=128`; family added to dead
ends `[trading_systems_methods, p.323-324]`, `[quant_trading_chan, p.51-53]`,
`[testing_tuning, p.327-335]`, `[advances_fin_ml, p.208-211]`.

Phase 2 iteration 008 tested daily `GLD`/`xauusd` MACD trend continuation with
optional `SMA200` regime and `SHV` while flat. Daily `GLD`/`xauusd`/`SHV`/`SPY`
files exist; `data/tiingo/1hour/prices/` still has 0 parquet files and
`15min/prices` is absent, so intraday was not synthesized. Best
`xau_macd_12_26_9` had CAGR 12.10%, Sharpe 0.875 and MDD -17.83% versus
`xauusd` buy-and-hold CAGR 16.66%, Sharpe 0.948 and MDD -20.36%; it passed PBO
(`0.099`), OOS and cross-lib, but failed same-asset Sharpe, IS MCPT (`p=0.365`),
WF MCPT (`p=0.310`), DSR (`p=0.6581`), WF sufficiency (`3/3` positive but fewer
than 8 windows), latest 63d FWD (`-6.49%`) and bootstrap. `n_trials=4`,
cumulative `n_trials=132`; family added to dead ends `[trading_systems_methods,
p.382]`, `[testing_tuning, p.318-320]`, `[advances_fin_ml, p.222-223]`.

Phase 2 iteration 009 tested daily `SPY`/`QQQ` ADX/Directional Movement trend
continuation with `SHV` while flat. Daily `SPY`/`QQQ`/`SHV` files exist through
2026-05-13; `data/tiingo/1hour/prices/` still has 0 parquet files and
`15min/prices` is absent, so intraday was not synthesized. Best `spy_adx14_t25`
had CAGR 2.86%, Sharpe 0.547 and MDD -15.90% versus SPY buy-and-hold CAGR
10.80%, Sharpe 0.644 and MDD -55.20%; it passed WF windows (`20/30`), OOS,
latest 63d FWD, bootstrap and cross-lib, but failed same-asset Sharpe, IS MCPT
(`p=0.680`), WF MCPT (`p=0.830`), PBO (`0.635`) and DSR (`p=0.3040`, cumulative
`n_trials=136`). `n_trials=4`; family added to dead ends. MCPT used fixed-rule
close-path permutations with high/low approximated from close paths, so even a
hypothetical pass would have needed stricter OHLC permutation audit before any
promotion `[trading_systems_methods, p.387]`, `[testing_tuning, p.318-320]`,
`[advances_fin_ml, p.208-211]`.

Phase 2 iteration 010 tested daily `GLD`/`xauusd` Keltner/ATR breakout configs
with `SHV` while flat. Daily `GLD`/`xauusd`/`SHV`/`SPY` physical files exist;
`data/tiingo/1hour/prices/` still has 0 parquet files and `15min/prices` is
absent, so intraday was not synthesized. Best `xau_kel40_20_exit0` had CAGR
8.94%, Sharpe 0.782 and MDD -18.05% versus `xauusd` buy-and-hold CAGR 16.97%,
Sharpe 1.059 and MDD -20.36%; it passed PBO (`0.099`), OOS and cross-lib, but
failed same-asset Sharpe, IS MCPT (`p=0.500`), WF MCPT (`p=0.530`), DSR
(`p=0.7391`, cumulative `n_trials=140`), WF sufficiency (`3/3` positive but fewer
than 8 windows), latest 63d FWD (`-6.27%`) and bootstrap. `n_trials=4`; family
added to dead ends. MCPT used a fixed-rule close-path proxy for OHLC-dependent ATR
bands, so even a hypothetical pass would have required stricter OHLC permutation
audit `[trading_systems_methods, p.352-353]`, `[trading_systems_methods,
p.1057-1059]`, `[testing_tuning, p.318-320]`, `[advances_fin_ml, p.222-223]`.

Phase 2 iteration 011 tested daily `SPY`/`QQQ` stochastic close-location pullback
configs with `SMA200` regime, mid-range/time exits, `SHV` while flat and one-bar
lagged signals. Daily `SPY`/`QQQ`/`SHV` physical files exist through 2026-05-13;
`data/tiingo/1hour/prices/` still has 0 parquet files and `15min/prices` is
absent, so no intraday bars were synthesized. Best
`qqq_stoch14_os20_exit50_hold10` had CAGR 6.64%, Sharpe 0.699 and MDD -24.60%
versus QQQ buy-and-hold CAGR 8.89%, Sharpe 0.454 and MDD -82.97%; it passed
same-asset Sharpe, IS MCPT (`p=0.005`), WF MCPT (`p=0.010`), WF windows (`19/23`),
OOS, bootstrap and cross-lib, but closed `fail` by the Phase 2 CAGR kill rule,
PBO (`0.512`), DSR (`p=0.1815`, cumulative `n_trials=144`) and latest 63d FWD
(`-1.00%`). `n_trials=4`; family added to dead ends
`[trading_systems_methods, p.385-386]`, `[trading_systems_methods, p.172]`,
`[testing_tuning, p.327-335]`, `[advances_fin_ml, p.208-211]`.

Phase 2 iteration 012 tested daily DeMark-style 9-count exhaustion reversals on
`SPY`/`QQQ`/`GLD`/`xauusd` with `SMA200`, `SHV` while flat and one-bar-lagged
signals. Daily physical files existed for all required tickers; `1hour/prices`
still had 0 parquet files and `15min/prices` was absent, so no intraday bars were
synthesized. Best `xau_demark9_sma200_hold13` had CAGR 3.38%, Sharpe 1.512 and
MDD -2.33% versus `xauusd` buy-and-hold CAGR 17.30%, Sharpe 1.061 and MDD
-20.36%; it passed same-asset Sharpe, OOS, latest 63d FWD, bootstrap and
cross-lib, but closed `fail` by the Phase 2 CAGR kill rule, IS MCPT (`p=0.460`),
WF MCPT (`p=0.340`), PBO (`0.730`), DSR (`p=0.1483`, cumulative `n_trials=148`)
and insufficient WF windows (`2/2`, fewer than 8). `n_trials=4`; family added to
dead ends `[trading_systems_methods, ch.4, p.173-175]`,
`[trading_systems_methods, p.285]`, `[testing_tuning, p.318-320]`,
`[advances_fin_ml, p.208-211]`.

Phase 2 iteration 013 tested daily `GLD`/`xauusd` relative-strength filters versus
`SPY` with own momentum confirmation, `SHV` while flat and one-bar-lagged signals.
Daily physical files existed for all required tickers; `1hour/prices` still had 0
parquet files and `15min/prices` was absent, so no intraday bars were synthesized.
Best `xau_rs200_m126` had CAGR 14.31%, Sharpe 0.915 and MDD -20.09% versus
`xauusd` buy-and-hold CAGR 22.84%, Sharpe 1.247 and MDD -20.51%; it passed PBO
(`0.484`), OOS and cross-lib, but closed `fail` by the Phase 2 CAGR floor,
same-asset Sharpe, IS MCPT (`p=0.395`), WF MCPT (`p=0.410`), DSR (`p=0.7467`,
cumulative `n_trials=152`), WF sufficiency (`1/1`, fewer than 8), latest 63d FWD
(`-10.44%`) and bootstrap. `n_trials=4`; family added to dead ends
`[trading_systems_methods, p.542-544]`, `[trading_systems_methods, p.939]`,
`[testing_tuning, p.318-320]`, `[advances_fin_ml, p.208-211]`.

Phase 2 iteration 014 tested daily VIDYA adaptive-trend filters on `SPY`, `QQQ`,
`GLD` and `xauusd` with `SHV` while flat and one-bar-lagged signals. Daily
physical files existed for all required tickers; `1hour/prices` still had 0
parquet files and `15min/prices` was absent, so no intraday bars were synthesized.
Best `xau_vidya9_30` had CAGR 14.80%, Sharpe 0.989 and MDD -21.49% versus
`xauusd` buy-and-hold CAGR 17.48%, Sharpe 0.987 and MDD -20.36%; it passed
same-asset Sharpe, PBO (`0.294`), OOS and cross-lib, but closed `fail` by the
Phase 2 CAGR floor, IS MCPT (`p=0.350`), WF MCPT (`p=0.120`), DSR (`p=0.5534`,
cumulative `n_trials=156`), WF sufficiency (`3/3`, fewer than 8), latest 63d FWD
(`-10.38%`) and bootstrap. `n_trials=4`; family added to dead ends
`[trading_systems_methods, p.784-785]`, `[testing_tuning, p.318-320]`,
`[advances_fin_ml, p.208-211]`.

Phase 2 iteration 015 tested daily upper-Bollinger breakout after realized-
volatility compression on `SPY`, `QQQ`, `GLD` and `xauusd` with `SHV` while flat
and one-bar-lagged signals. Daily physical files existed for all required
tickers; `1hour/prices` still had 0 parquet files and `15min/prices` was absent,
so no intraday bars were synthesized. Best `xau_bb20_2_rv20_p30_exit_mid` had
CAGR 4.25%, Sharpe 0.699 and MDD -9.24% versus `xauusd` buy-and-hold CAGR
17.58%, Sharpe 0.994 and MDD -20.36%; it passed PBO (`0.234`), OOS, latest 63d
FWD and cross-lib, but closed `fail` by the Phase 2 CAGR floor, same-asset
Sharpe, IS MCPT (`p=0.445`), WF MCPT (`p=0.530`), DSR (`p=0.7957`, cumulative
`n_trials=160`), WF sufficiency (`3/3`, fewer than 8) and bootstrap. `n_trials=4`;
family added to dead ends `[trading_systems_methods, p.323-324]`,
`[volatility_trading, p.36]`, `[testing_tuning, p.318-320]`,
`[advances_fin_ml, p.208-211]`.

Phase 2 iteration 016 tested daily TRIX trend continuation on `SPY`, `QQQ`,
`GLD` and `xauusd` with `SHV` while flat and one-bar-lagged signals. Daily
physical files existed for all required tickers; `1hour/prices` still had 0
parquet files and `15min/prices` was absent, so no intraday bars were
synthesized. Best `xau_trix18_zero` had CAGR 10.99%, Sharpe 0.831 and MDD
-19.44% versus `xauusd` buy-and-hold CAGR 14.30%, Sharpe 0.915 and MDD -20.36%;
it passed OOS and cross-lib, but closed `fail` by the Phase 2 CAGR floor,
same-asset Sharpe, IS MCPT (`p=0.175`), WF MCPT (`p=0.070`), PBO (`0.556`), DSR
(`p=0.7106`, cumulative `n_trials=164`), WF sufficiency (`3/3`, fewer than 8),
latest 63d FWD (`-17.15%`) and bootstrap. `n_trials=4`; family added to dead
ends `[trading_systems_methods, p.334]`, `[testing_tuning, p.318-320]`,
`[advances_fin_ml, p.208-211]`.

Phase 2 iteration 017 tested daily Woodshedder ROC on `SPY`, `QQQ`, `GLD` and
`xauusd` with `SHV` and signals shifted one completed daily bar. Best
`xau_roc5_252_x2` had CAGR 14.64%, Sharpe 0.960 and MDD -20.09% versus
`xauusd` buy-and-hold CAGR 18.00%, Sharpe 1.094 and MDD -20.36%; it passed OOS
and cross-lib, but closed `fail` by the Phase 2 CAGR floor, same-asset Sharpe,
IS MCPT (`p=0.305`), WF MCPT (`p=0.460`), PBO (`0.905`), DSR (`p=0.6476`,
cumulative `n_trials=168`), WF sufficiency (`2/2`, fewer than 8), latest 63d FWD
(`-13.26%`) and bootstrap. `n_trials=4`; family added to dead ends
`[trading_systems_methods, p.355]`, `[testing_tuning, p.318-320]`,
`[advances_fin_ml, p.208-211]`.

Phase 2 iteration 018 tested daily Clenow adjusted-slope trend filters on `SPY`,
`QQQ`, `GLD` and `xauusd` with `SHV` and signals shifted one completed daily bar.
Best `xau_slope90_sma200` had CAGR 14.57%, Sharpe 0.994 and MDD -20.09% versus
`xauusd` buy-and-hold CAGR 17.36%, Sharpe 1.070 and MDD -20.36%; it passed OOS
and cross-lib, but closed `fail` by the Phase 2 CAGR floor, same-asset Sharpe,
IS MCPT (`p=0.145`), WF MCPT (`p=0.320`), PBO (`0.885`), DSR (`p=0.6040`,
cumulative `n_trials=172`), WF sufficiency (`3/3`, fewer than 8), latest 63d FWD
(`-11.54%`) and bootstrap. `n_trials=4`; family added to dead ends
`[stocks_on_the_move, p.66-67]`, `[stocks_on_the_move, p.77]`,
`[testing_tuning, p.327-335]`, `[advances_fin_ml, p.208-211]`.

Phase 2 iteration 019 tested daily Force Index volume impulse on `SPY`, `QQQ` and
`GLD` with `SHV` and signals shifted one completed daily bar. `xauusd` was kept
as gold context only because the indicator requires trustworthy volume. Best
`gld_fi13_z126_e05_x0_sma200_h20` had CAGR 5.63%, Sharpe 0.601 and MDD -21.96%
versus `GLD` buy-and-hold CAGR 11.44%, Sharpe 0.683 and MDD -45.56%; it passed WF
windows (`13/17`), OOS, latest 63d FWD and cross-lib, but closed `fail` by the
Phase 2 CAGR floor, same-asset Sharpe, IS MCPT (`p=0.445`), WF MCPT (`p=0.880`),
PBO (`0.663`), DSR (`p=0.4985`, cumulative `n_trials=176`) and bootstrap.
`n_trials=4`; family added to dead ends `[trading_systems_methods, p.836]`,
`[trading_systems_methods, p.13]`, `[testing_tuning, p.327-335]`,
`[advances_fin_ml, p.208-211]`.

Phase 2 iteration 020 tested a daily Elder-Ray Triple Screen proxy on `SPY`,
`QQQ`, `GLD` and `xauusd` with weekly MACD histogram trend, daily Bear Power
rising from negative territory, `SHV` while flat and one-bar-lagged signals.
Daily physical files existed for all required tickers; `1hour/prices` still had 0
parquet files and `15min/prices` was absent, so no intraday bars were synthesized.
Best `xau_eray_12_26_9_ema13_bear3_h10` had CAGR 2.85%, Sharpe 3.106 and MDD
-1.03% versus `xauusd` buy-and-hold CAGR 14.18%, Sharpe 0.909 and MDD -20.36%; it
passed same-asset Sharpe, PBO (`0.302`), DSR (`p=0.000815`, cumulative
`n_trials=180`), OOS, latest 63d FWD, bootstrap and cross-lib, but closed `fail`
by the Phase 2 CAGR floor, IS MCPT (`p=0.870`), WF MCPT (`p=0.920`) and WF
sufficiency (`3/3`, fewer than 8). `n_trials=4`; family added to dead ends
`[trading_systems_methods, p.835-838]`, `[trading_systems_methods, p.837]`,
`[testing_tuning, p.327-335]`, `[advances_fin_ml, p.208-211]`.

Phase 2 iteration 021 tested daily Wilder Accumulated Swing Index breakouts on
`SPY`, `QQQ`, `GLD` and `xauusd` with prior-20-bar entry breakouts, prior-10-bar
exit breakdowns, 20-bar max hold, `SHV` while flat and one-bar-lagged signals.
Daily physical files existed for all required tickers with OHLC columns;
`1hour/prices` still had 0 parquet files and `15min/prices` was absent, so no
intraday bars were synthesized. Best `xau_asi20_10_h20` had CAGR 8.80%, Sharpe
0.683 and MDD -18.68% versus `xauusd` buy-and-hold CAGR 17.51%, Sharpe 0.990 and
MDD -20.36%; it passed OOS and cross-lib, but closed `fail` by the Phase 2 CAGR
floor, same-asset Sharpe, IS MCPT (`p=0.715`), WF MCPT (`p=0.530`), PBO (`0.516`),
DSR (`p=0.8587`, cumulative `n_trials=184`), WF sufficiency (`3/3`, fewer than
8), latest 63d FWD (`-8.17%`) and bootstrap. `n_trials=4`; family added to dead
ends `[trading_systems_methods, p.193-195]`, `[trading_systems_methods,
p.165-172]`, `[testing_tuning, p.327-335]`, `[advances_fin_ml, p.208-211]`.

Phase 2 iteration 022 tested daily regression-channel breakouts on `SPY`, `QQQ`,
`GLD` and `xauusd` with 63-day projected regression-channel upper-band entries,
centerline/max-hold exits, `SHV` while flat and one-bar-lagged signals. Daily
physical files existed for all required tickers with OHLC columns; `1hour/prices`
still had 0 parquet files and `15min/prices` was absent, so no intraday bars were
synthesized. Best `xau_regch63_h30` had CAGR 3.62%, Sharpe 0.787 and MDD -10.78%
versus `xauusd` buy-and-hold CAGR 14.32%, Sharpe 0.916 and MDD -20.36%; it passed
PBO (`0.480`), OOS, latest 63d FWD and cross-lib, but closed `fail` by the Phase 2
CAGR floor, same-asset Sharpe, IS MCPT (`p=0.460`), WF MCPT (`p=0.250`), DSR
(`p=0.7751`, cumulative `n_trials=188`), WF sufficiency (`3/3`, fewer than 8) and
bootstrap. `n_trials=4`; family added to dead ends `[trading_systems_methods,
p.167-169]`, `[trading_systems_methods, p.168]`, `[testing_tuning, p.327-335]`,
`[advances_fin_ml, p.222-223]`.

Phase 2 iteration 023 tested daily Money Flow Index pullbacks on `SPY`, `QQQ` and
`GLD` with `SMA200`, MFI recovery/time exits, `SHV` while flat and one-bar-lagged
signals. Daily physical files existed for all required tickers and configured ETF
volume was present; `1hour/prices` still had 0 parquet files and `15min/prices`
was absent, so no intraday bars were synthesized. Best
`gld_mfi14_os20_x50_sma200_h10` had CAGR 1.90%, Sharpe 0.730 and MDD -4.88%
versus `GLD` buy-and-hold CAGR 11.64%, Sharpe 0.693 and MDD -45.56%; it passed
same-asset Sharpe, PBO (`0.246`), WF windows (`14/17`), OOS, latest 63d FWD,
bootstrap and cross-lib, but closed `fail` by the Phase 2 CAGR floor, IS MCPT
(`p=0.475`), WF MCPT (`p=0.100`) and DSR (`p=0.2840`, cumulative
`n_trials=192`). `n_trials=4`; family added to dead ends `[trading_systems_methods,
p.540]`, `[trading_systems_methods, p.285]`, `[testing_tuning, p.327-335]`,
`[advances_fin_ml, p.222-223]`.

Phase 2 iteration 024 tested daily dual MA+ATR breakout rules on `SPY`, `QQQ`,
`GLD` and `xauusd`, using MA5/MA20 bands displaced by ATR20, `SHV` while flat and
one-bar-lagged signals. Daily physical files existed for all required tickers with
OHLC columns; `1hour/prices` still had 0 parquet files and `15min/prices` was
absent, so no intraday bars were synthesized. Best `xau_ma5_20_atr20_k1` had CAGR
10.89%, Sharpe 0.816 and MDD -15.36% versus `xauusd` buy-and-hold CAGR 17.41%,
Sharpe 0.985 and MDD -20.36%; it passed OOS and cross-lib, but closed `fail` by
the Phase 2 CAGR floor, same-asset Sharpe, IS MCPT (`p=0.380`), WF MCPT
(`p=0.580`), PBO (`0.607`), DSR (`p=0.7628`, cumulative `n_trials=196`), WF
sufficiency (`3/3`, fewer than 8), latest 63d FWD (`-4.22%`) and bootstrap.
`n_trials=4`; family added to dead ends `[trading_systems_methods, p.352-353]`,
`[trading_systems_methods, p.107]`, `[testing_tuning, p.327-335]`,
`[advances_fin_ml, p.208-211]`.

Phase 2 iteration 025 tested daily conservative swing-point breakout rules on
`SPY`, `QQQ`, `GLD` and `xauusd`, using percentage swing filters, previous-upswing
breakout confirmation, `SHV` while flat and one-bar-lagged signals. Daily physical
files existed for all required tickers with OHLC columns; `1hour/prices` still had
0 parquet files and `15min/prices` was absent, so no intraday bars were synthesized.
Best `xau_swing5_break_prev_high` had CAGR 10.06%, Sharpe 1.117 and MDD -11.13%
versus `xauusd` buy-and-hold CAGR 17.33%, Sharpe 0.984 and MDD -20.36%; it passed
same-asset Sharpe, PBO (`0.278`), OOS and cross-lib, but closed `fail` by the
Phase 2 CAGR floor, IS MCPT (`p=0.080`), WF MCPT (`p=0.320`), DSR (`p=0.4410`,
cumulative `n_trials=200`), WF sufficiency (`2/3`, fewer than 8), latest 63d FWD
(`-10.95%`) and bootstrap. `n_trials=4`; family added to dead ends
`[trading_systems_methods, p.165]`, `[trading_systems_methods, p.168]`,
`[testing_tuning, p.327-335]`, `[advances_fin_ml, p.222-223]`.

Phase 2 iteration 026 tested daily Price Density trend filters on `SPY`, `QQQ`,
`GLD` and `xauusd`, using 20-day Price Density below 4.0, `SMA200`, `SHV` while
flat and one-bar-lagged signals. Daily physical files existed for all required
tickers with OHLC columns; `1hour/prices` still had 0 parquet files and
`15min/prices` was absent, so no intraday bars were synthesized. Best
`spy_pd20_lt4_sma200` had CAGR 6.45%, Sharpe 0.797 and MDD -20.04% versus `SPY`
buy-and-hold CAGR 10.87%, Sharpe 0.644 and MDD -55.20%; it passed same-asset
Sharpe, IS MCPT (`p=0.000`), DSR (`p=0.0413`, cumulative `n_trials=204`), WF
windows (`21/29`), OOS, latest 63d FWD, bootstrap and cross-lib, but closed
`fail` by the Phase 2 CAGR floor, WF MCPT (`p=0.060`) and PBO (`0.512`).
`n_trials=4`; family added to dead ends rather than tuning Price Density
thresholds/lookbacks or SMA length `[trading_systems_methods, p.12]`,
`[trading_systems_methods, p.13]`, `[testing_tuning, p.327-335]`,
`[advances_fin_ml, p.208-211]`.

Phase 2 iteration 027 tested daily Williams %R exhaustion-reversal rules on
`SPY`, `QQQ`, `GLD` and `xauusd`, using `%R(14) <= -90` entries, `%R >= -50` or
10-bar exits, `SMA200`, `SHV` while flat and one-bar-lagged signals. Daily OHLC
files existed; `1hour/prices` still had 0 parquet files and `15min/prices` was
absent, so no intraday bars were synthesized. Best `qqq_wr14_os90_x50_sma200_h10`
had CAGR 6.07%, Sharpe 0.788 and MDD -15.45% versus `QQQ` buy-and-hold CAGR
9.38%, Sharpe 0.469 and MDD -82.97%; it passed same-asset Sharpe, IS MCPT
(`p=0.005`), WF MCPT (`p=0.010`), WF windows (`17/23`), OOS, bootstrap and
cross-lib, but closed `fail` by the Phase 2 CAGR floor, PBO (`0.651`), DSR
(`p=0.0918`, cumulative `n_trials=208`) and latest 63d FWD (`-1.96%`).
`n_trials=4`; family added to dead ends rather than tuning Williams %R lookback,
entry/exit thresholds, hold length or SMA filter `[trading_systems_methods,
p.385-386]`, `[trading_systems_methods, p.172]`, `[testing_tuning, p.327-335]`,
`[advances_fin_ml, p.208-211]`.

Phase 2 iteration 028 tested daily CMO momentum-continuation rules on `SPY`,
`QQQ`, `GLD` and `xauusd`. Best `xau_cmo20_e50_x0_sma200_h20` had CAGR 5.91%,
Sharpe 0.638 and MDD -14.68% versus `xauusd` buy-and-hold CAGR 17.28%, Sharpe
1.060 and MDD -20.36%; it passed OOS, latest 63d FWD and cross-lib, but closed
`fail` by the Phase 2 CAGR floor, same-asset Sharpe, IS MCPT (`p=0.470`), WF
MCPT (`p=0.790`), PBO (`0.885`), DSR (`p=0.8738`, cumulative `n_trials=212`), WF
sufficiency and bootstrap. `n_trials=4`; family added to dead ends
`[trading_systems_methods, p.388]`, `[trading_systems_methods, p.284]`,
`[testing_tuning, p.327-335]`, `[advances_fin_ml, p.208-211]`.

Phase 2 iteration 029 tested daily Fisher Transform cycle-reversal rules on
`SPY`, `QQQ`, `GLD` and `xauusd`. Daily files existed; `1hour/prices` still had
0 parquet files and `15min/prices` was absent, so no intraday bars were
synthesized. Best `spy_fisher10_reversal_sma200_h10` had CAGR 4.70%, Sharpe
0.729 and MDD -11.09% versus `SPY` buy-and-hold CAGR 10.90%, Sharpe 0.646 and
MDD -55.20%; it passed same-asset Sharpe, IS MCPT (`p=0.000`), WF MCPT
(`p=0.050`), WF windows (`23/29`), OOS, bootstrap and cross-lib, but closed
`fail` by the Phase 2 CAGR floor, PBO (`0.587`), DSR (`p=0.0882`, cumulative
`n_trials=216`) and latest 63d FWD (`-2.76%`). `n_trials=4`; family added to
dead ends `[cycle_analytics, p.195-197]`, `[trading_systems_methods, p.284]`,
`[testing_tuning, p.327-335]`, `[advances_fin_ml, p.208-211]`.

Capital allocation remains unchanged: 100% Plano C per
`docs/investment-mandate.md`. Any future candidate is research evidence only
unless it passes all hard gates and receives explicit human review.

## Permanent Rules

- Use the video process as an additional gate stack: IS excellence, IS MCPT,
  walk-forward and WF MCPT.
- Keep repo hard gates: PBO, DSR, WF, OOS, FWD, bootstrap and cross-lib
  `[advances_fin_ml, p.196-202]`, `[advances_fin_ml, p.208-211]`,
  `[advances_fin_ml, p.222-223]`.
- Every strategy, indicator, parameter and gate choice needs a book citation.
- One hypothesis family per iteration.
- Pre-register before running tests.
- Keep config count small; DSR uses cumulative strategy trials.
- Do not modify `docs/investment-mandate.md`.
- Do not commit or push automatically.
- Phase 2 economic floor: no strategy can be `candidate_watchlist`,
  `paper_trade_candidate` or `strict_winner` if its CAGR is below same-asset
  buy-and-hold on the same aligned dates. Lower drawdown alone is not enough
  `[systematic_trading, p.40]`, `[testing_tuning, p.327-335]`.

## Hypotheses Tested

- **001-2026-05-14-gold-donchian-compression (Phase 2):** tested 4
  pre-registered daily gold/XAUUSD Donchian-compression breakout configs after
  auditing physical files. `GLD` and `xauusd` daily files existed, but `1h` files
  were absent and the `1hour/prices` directory had 0 parquet files, so intraday
  was not synthesized. Best `xau_dc100_rv20_p30` had CAGR 7.11%, Sharpe 0.726 and
  MDD -14.68% versus XAU buy-and-hold CAGR 18.17%, Sharpe 1.099 and MDD -20.36%.
  It passed OOS and cross-lib parity, but failed same-asset Sharpe, IS MCPT
  (`p=0.315`), WF MCPT (`p=0.220`), PBO (`0.615`), DSR (`p=0.7716`, cumulative
  `n_trials=104`), WF sufficiency, FWD 63d (`-9.73%`) and bootstrap. `n_trials=4`;
  family added to dead ends `[trading_systems_methods, p.353]`,
  `[trading_systems_methods, p.481]`, `[testing_tuning, p.327-335]`,
  `[advances_fin_ml, p.208-211]`.

- **002-2026-05-14-gold-rsi-exhaustion (Phase 2):** tested 4 pre-registered
  daily `GLD` RSI exhaustion mean-reversion configs with `SMA150`/`SMA200` trend
  filters and `SHV` while flat. Best `gld_rsi2_e5_x60_sma200` had CAGR 6.35%,
  Sharpe 0.636 and MDD -25.34% versus `GLD` buy-and-hold CAGR 11.65%, Sharpe
  0.693 and MDD -45.56%. It passed WF windows (`11/17`), OOS and cross-lib, but
  failed same-asset Sharpe, IS MCPT (`p=0.200`), WF MCPT (`p=0.140`), PBO
  (`0.556`), DSR (`p=0.3708`, cumulative `n_trials=108`), FWD 63d (`-3.81%`) and
  bootstrap. `n_trials=4`; family added to dead ends. Intraday remains blocked by
  zero physical `1hour` parquet files `[quant_trading_chan, p.142-143]`,
  `[testing_tuning, p.318-320]`, `[advances_fin_ml, p.208-211]`.

- **003-2026-05-14-gold-cci-breakout (Phase 2):** tested 4 pre-registered daily
  close-only CCI breakout configs on `GLD` and `xauusd` with `SMA200` trend filter
  and `SHV` while flat. Best `xau_cci40_e100_x0_sma200` had CAGR 9.92%, Sharpe
  0.820 and MDD -14.68% versus `xauusd` buy-and-hold CAGR 17.36%, Sharpe 1.070
  and MDD -20.36%. It passed PBO (`0.214`), OOS and cross-lib, but failed
  same-asset Sharpe, IS MCPT (`p=0.280`), WF MCPT (`p=0.450`), DSR (`p=0.7023`,
  cumulative `n_trials=112`), WF sufficiency, FWD 63d (`-6.27%`) and bootstrap.
  `n_trials=4`; family added to dead ends. Physical audit found daily data present,
  `1hour/prices` empty and `15min/prices` absent `[trading_systems_methods, p.172]`,
  `[testing_tuning, p.318-320]`, `[advances_fin_ml, p.208-211]`.

- **004-2026-05-14-equity-volatility-system (Phase 2):** tested 4 pre-registered
  daily SPY/QQQ volatility reversal configs using average True Range distance and
  `SHV` while flat. Best `qqq_vs20_k30` had CAGR 9.34%, Sharpe 0.629 and MDD
  -47.42% versus QQQ buy-and-hold CAGR 10.60%, Sharpe 0.509 and MDD -82.97%.
  It passed same-asset Sharpe, PBO (`0.048`), WF windows (`21/24`), OOS, latest
  63d FWD, bootstrap and cross-lib, but failed IS MCPT (`p=0.940`), WF MCPT
  (`p=0.970`) and DSR (`p=0.2483`, cumulative `n_trials=116`). `n_trials=4`;
  family added to dead ends. Intraday remains blocked by zero physical `1hour`
  parquet files and absent `15min/prices`; MCPT was conservatively recorded as
  close-path proxy rather than promotion-quality OHLC permutation
  `[trading_systems_methods, p.107]`, `[trading_systems_methods, p.333]`,
  `[testing_tuning, p.318-320]`, `[advances_fin_ml, p.222-223]`.

- **005-2026-05-14-equity-gap-continuation (Phase 2):** tested 4 pre-registered
  daily SPY/QQQ down-gap recovery configs using adjusted OHLC bars and `SHV` while
  flat. Best `spy_gap10_recover` had CAGR 1.84%, Sharpe 0.370 and MDD -12.70%
  versus SPY buy-and-hold CAGR 10.83%, Sharpe 0.646 and MDD -55.20%. It passed WF
  MCPT (`p=0.010`), PBO (`0.171`), WF windows (`21/30`), OOS, latest 63d FWD and
  cross-lib, but failed same-asset Sharpe, IS MCPT (`p=0.035`), DSR (`p=0.6884`,
  cumulative `n_trials=120`) and bootstrap. `n_trials=4`; family added to dead
  ends. Intraday remains blocked by zero physical `1hour` parquet files and absent
  `15min/prices`; MCPT used a close-path downside-return proxy rather than
  promotion-quality OHLC permutation `[trading_systems_methods, p.635]`,
  `[testing_tuning, p.318-320]`, `[advances_fin_ml, p.208-211]`.

- **006-2026-05-14-equity-momentum-pullback (Phase 2):** tested 4 pre-registered
  daily SPY/QQQ trend-filtered pullback configs using `SMA200`, short rolling loss
  triggers and fixed 5/10-bar holds with `SHV` while flat. Best
  `spy_pb3_m2_hold5` had CAGR 5.29%, Sharpe 0.862 and MDD -9.58% versus SPY
  buy-and-hold CAGR 10.92%, Sharpe 0.621 and MDD -54.67%. It passed same-asset
  Sharpe, IS MCPT (`p=0.010`), WF MCPT (`p=0.010`), PBO (`0.310`), WF windows
  (`15/15`), OOS and cross-lib, but failed DSR (`p=0.1414`, cumulative
  `n_trials=124`), latest 63d FWD (`-2.55%`) and bootstrap. `n_trials=4`; family
  added to dead ends. Intraday remains blocked by zero physical `1hour` parquet
  files and absent `15min/prices` `[trading_systems_methods, p.172]`,
  `[quant_trading_chan, p.142-143]`, `[advances_fin_ml, p.222-223]`.

- **007-2026-05-14-equity-bollinger-reversion (Phase 2):** tested 4
  pre-registered daily SPY/QQQ Bollinger lower-band mean-reversion configs using
  `SMA200`, middle-band/time exits and `SHV` while flat. Best
  `spy_bb20_2_hold10` had CAGR 3.38%, Sharpe 0.551 and MDD -17.17% versus SPY
  buy-and-hold CAGR 10.92%, Sharpe 0.621 and MDD -54.67%. It passed WF windows
  (`12/15`), OOS and cross-lib, but failed same-asset Sharpe, IS MCPT (`p=0.230`),
  WF MCPT (`p=0.330`), PBO (`0.734`), DSR (`p=0.5942`, cumulative
  `n_trials=128`), latest 63d FWD (`-2.56%`) and bootstrap. `n_trials=4`; family
  added to dead ends. Intraday remains blocked by zero physical `1hour` parquet
  files and absent `15min/prices` `[trading_systems_methods, p.323-324]`,
  `[quant_trading_chan, p.51-53]`, `[testing_tuning, p.327-335]`,
  `[advances_fin_ml, p.208-211]`.

- **008-2026-05-14-gold-macd-trend (Phase 2):** tested 4 pre-registered daily
  `GLD`/`xauusd` MACD 12/26/9 trend configs with optional `SMA200` regime and
  `SHV` while flat. Best `xau_macd_12_26_9` had CAGR 12.10%, Sharpe 0.875 and
  MDD -17.83% versus `xauusd` buy-and-hold CAGR 16.66%, Sharpe 0.948 and MDD
  -20.36%. It passed PBO (`0.099`), OOS and cross-lib, but failed same-asset
  Sharpe, IS MCPT (`p=0.365`), WF MCPT (`p=0.310`), DSR (`p=0.6581`, cumulative
  `n_trials=132`), WF sufficiency, latest 63d FWD (`-6.49%`) and bootstrap.
  `n_trials=4`; family added to dead ends. Intraday remains blocked by zero
  physical `1hour` parquet files and absent `15min/prices` `[trading_systems_methods,
  p.382]`, `[testing_tuning, p.327-335]`, `[advances_fin_ml, p.222-223]`.

- **009-2026-05-14-equity-adx-trend (Phase 2):** tested 4 pre-registered daily
  `SPY`/`QQQ` ADX/Directional Movement trend-continuation configs using lagged
  `+DI > -DI` and `ADX(14)` thresholds 20/25 with `SHV` while flat. Best
  `spy_adx14_t25` had CAGR 2.86%, Sharpe 0.547 and MDD -15.90% versus SPY
  buy-and-hold CAGR 10.80%, Sharpe 0.644 and MDD -55.20%. It passed WF windows
  (`20/30`), OOS, latest 63d FWD, bootstrap and cross-lib, but failed same-asset
  Sharpe, IS MCPT (`p=0.680`), WF MCPT (`p=0.830`), PBO (`0.635`) and DSR
  (`p=0.3040`, cumulative `n_trials=136`). `n_trials=4`; family added to dead
  ends. Intraday remains blocked by zero physical `1hour` parquet files and absent
  `15min/prices`; MCPT used a close-path OHLC proxy and is not promotion-quality
  for OHLC-dependent ADX `[trading_systems_methods, p.387]`,
  `[testing_tuning, p.318-320]`, `[advances_fin_ml, p.208-211]`.

- **010-2026-05-14-gold-keltner-breakout (Phase 2):** tested 4 pre-registered
  daily `GLD`/`xauusd` Keltner/ATR breakout configs using EMA plus ATR envelope
  entries, EMA exits, `SHV` while flat and one-bar-lagged signals. Best
  `xau_kel40_20_exit0` had CAGR 8.94%, Sharpe 0.782 and MDD -18.05% versus
  `xauusd` buy-and-hold CAGR 16.97%, Sharpe 1.059 and MDD -20.36%. It passed PBO
  (`0.099`), OOS and cross-lib, but failed same-asset Sharpe, IS MCPT (`p=0.500`),
  WF MCPT (`p=0.530`), DSR (`p=0.7391`, cumulative `n_trials=140`), WF sufficiency,
  latest 63d FWD (`-6.27%`) and bootstrap. `n_trials=4`; family added to dead
  ends. Intraday remains blocked by zero physical `1hour` parquet files and absent
  `15min/prices`; no intraday bars were synthesized `[trading_systems_methods,
  p.352-353]`, `[trading_systems_methods, p.1057-1059]`, `[testing_tuning,
  p.318-320]`, `[advances_fin_ml, p.222-223]`.

- **011-2026-05-14-equity-stochastic-pullback (Phase 2):** tested 4
  pre-registered daily `SPY`/`QQQ` stochastic close-location pullback configs with
  `SMA200`, mid-range/time exits and `SHV` while flat. Best
  `qqq_stoch14_os20_exit50_hold10` had CAGR 6.64%, Sharpe 0.699 and MDD -24.60%
  versus QQQ buy-and-hold CAGR 8.89%, Sharpe 0.454 and MDD -82.97%. It passed
  same-asset Sharpe, IS MCPT (`p=0.005`), WF MCPT (`p=0.010`), WF windows, OOS,
  bootstrap and cross-lib, but failed the Phase 2 CAGR floor, PBO (`0.512`), DSR
  (`p=0.1815`, cumulative `n_trials=144`) and latest 63d FWD (`-1.00%`).
  `n_trials=4`; family added to dead ends `[trading_systems_methods, p.385-386]`,
  `[trading_systems_methods, p.172]`, `[testing_tuning, p.327-335]`,
  `[advances_fin_ml, p.208-211]`.

- **012-2026-05-14-demark-setup-reversal (Phase 2):** tested 4 pre-registered
  daily DeMark-style 9-count exhaustion reversal configs on `SPY`, `QQQ`, `GLD`
  and `xauusd` with `SMA200`, `SHV` while flat and one-bar signal lag. Best
  `xau_demark9_sma200_hold13` had CAGR 3.38%, Sharpe 1.512 and MDD -2.33% versus
  `xauusd` buy-and-hold CAGR 17.30%, Sharpe 1.061 and MDD -20.36%. It passed
  same-asset Sharpe, OOS, latest 63d FWD, bootstrap and cross-lib, but failed the
  Phase 2 CAGR floor, IS MCPT (`p=0.460`), WF MCPT (`p=0.340`), PBO (`0.730`),
  DSR (`p=0.1483`, cumulative `n_trials=148`) and WF sufficiency (`2/2`, fewer
  than 8 windows). `n_trials=4`; family added to dead ends. Intraday remains
  blocked by zero physical `1hour` parquet files and absent `15min/prices`
  `[trading_systems_methods, ch.4, p.173-175]`, `[trading_systems_methods,
  p.285]`, `[testing_tuning, p.318-320]`, `[advances_fin_ml, p.208-211]`.

- **013-2026-05-14-gold-relative-strength (Phase 2):** tested 4 pre-registered
  daily `GLD`/`xauusd` relative-strength configs versus `SPY`, requiring the
  gold/SPY ratio to be above a rolling SMA and own momentum to be positive. Best
  `xau_rs200_m126` had CAGR 14.31%, Sharpe 0.915 and MDD -20.09% versus `xauusd`
  buy-and-hold CAGR 22.84%, Sharpe 1.247 and MDD -20.51%. It passed PBO (`0.484`),
  OOS and cross-lib, but failed the Phase 2 CAGR floor, same-asset Sharpe, IS MCPT
  (`p=0.395`), WF MCPT (`p=0.410`), DSR (`p=0.7467`, cumulative `n_trials=152`),
  WF sufficiency, latest 63d FWD (`-10.44%`) and bootstrap. `n_trials=4`; family
  added to dead ends. Intraday remains blocked by zero physical `1hour` parquet
  files and absent `15min/prices` `[trading_systems_methods, p.542-544]`,
  `[trading_systems_methods, p.939]`, `[testing_tuning, p.318-320]`,
  `[advances_fin_ml, p.208-211]`.

- **014-2026-05-14-vidya-adaptive-trend (Phase 2):** tested 4 pre-registered
  daily VIDYA adaptive-trend filter configs on `SPY`, `QQQ`, `GLD` and `xauusd`.
  Best `xau_vidya9_30` had CAGR 14.80%, Sharpe 0.989 and MDD -21.49% versus
  `xauusd` buy-and-hold CAGR 17.48%, Sharpe 0.987 and MDD -20.36%. It passed
  same-asset Sharpe, PBO (`0.294`), OOS and cross-lib, but failed the Phase 2
  CAGR floor, IS MCPT (`p=0.350`), WF MCPT (`p=0.120`), DSR (`p=0.5534`,
  cumulative `n_trials=156`), WF sufficiency, latest 63d FWD (`-10.38%`) and
  bootstrap. `n_trials=4`; family added to dead ends. Intraday remains blocked by
  zero physical `1hour` parquet files and absent `15min/prices`
  `[trading_systems_methods, p.784-785]`, `[testing_tuning, p.318-320]`,
  `[advances_fin_ml, p.208-211]`.

- **015-2026-05-14-bollinger-compression-breakout (Phase 2):** tested 4
  pre-registered daily upper-Bollinger breakout-after-compression configs on
  `SPY`, `QQQ`, `GLD` and `xauusd`. Best `xau_bb20_2_rv20_p30_exit_mid` had CAGR
  4.25%, Sharpe 0.699 and MDD -9.24% versus `xauusd` buy-and-hold CAGR 17.58%,
  Sharpe 0.994 and MDD -20.36%. It passed PBO (`0.234`), OOS, latest 63d FWD and
  cross-lib, but failed the Phase 2 CAGR floor, same-asset Sharpe, IS MCPT
  (`p=0.445`), WF MCPT (`p=0.530`), DSR (`p=0.7957`, cumulative `n_trials=160`),
  WF sufficiency and bootstrap. `n_trials=4`; family added to dead ends. Intraday
  remains blocked by zero physical `1hour` parquet files and absent `15min/prices`
  `[trading_systems_methods, p.323-324]`, `[volatility_trading, p.36]`,
  `[testing_tuning, p.318-320]`, `[advances_fin_ml, p.208-211]`.

- **016-2026-05-14-trix-trend-continuation (Phase 2):** tested 4
  pre-registered daily TRIX trend-continuation configs on `SPY`, `QQQ`, `GLD`
  and `xauusd`. Best `xau_trix18_zero` had CAGR 10.99%, Sharpe 0.831 and MDD
  -19.44% versus `xauusd` buy-and-hold CAGR 14.30%, Sharpe 0.915 and MDD
  -20.36%. It passed OOS and cross-lib, but failed the Phase 2 CAGR floor,
  same-asset Sharpe, IS MCPT (`p=0.175`), WF MCPT (`p=0.070`), PBO (`0.556`),
  DSR (`p=0.7106`, cumulative `n_trials=164`), WF sufficiency, latest 63d FWD
  (`-17.15%`) and bootstrap. `n_trials=4`; family added to dead ends. Intraday
  remains blocked by zero physical `1hour` parquet files and absent `15min/prices`
  `[trading_systems_methods, p.334]`, `[testing_tuning, p.318-320]`,
  `[advances_fin_ml, p.208-211]`.

- **017-2026-05-14-woodshedder-roc (Phase 2):** tested 4 pre-registered daily
  Woodshedder ROC configs on `SPY`, `QQQ`, `GLD` and `xauusd`. Best
  `xau_roc5_252_x2` had CAGR 14.64%, Sharpe 0.960 and MDD -20.09% versus
  `xauusd` buy-and-hold CAGR 18.00%, Sharpe 1.094 and MDD -20.36%. It passed
  OOS and cross-lib, but failed the Phase 2 CAGR floor, same-asset Sharpe, IS
  MCPT (`p=0.305`), WF MCPT (`p=0.460`), PBO (`0.905`), DSR (`p=0.6476`,
  cumulative `n_trials=168`), WF sufficiency, latest 63d FWD (`-13.26%`) and
  bootstrap. `n_trials=4`; family added to dead ends. Intraday remains blocked
  by zero physical `1hour` parquet files and absent `15min/prices`
  `[trading_systems_methods, p.355]`, `[testing_tuning, p.318-320]`,
  `[advances_fin_ml, p.208-211]`.

- **018-2026-05-14-clenow-slope-trend (Phase 2):** tested 4 pre-registered
  daily Clenow adjusted-slope trend filters on `SPY`, `QQQ`, `GLD` and `xauusd`.
  Best `xau_slope90_sma200` had CAGR 14.57%, Sharpe 0.994 and MDD -20.09% versus
  `xauusd` buy-and-hold CAGR 17.36%, Sharpe 1.070 and MDD -20.36%. It passed OOS
  and cross-lib, but failed the Phase 2 CAGR floor, same-asset Sharpe, IS MCPT
  (`p=0.145`), WF MCPT (`p=0.320`), PBO (`0.885`), DSR (`p=0.6040`, cumulative
  `n_trials=172`), WF sufficiency, latest 63d FWD (`-11.54%`) and bootstrap.
  `n_trials=4`; family added to dead ends. Intraday remains blocked by zero
  physical `1hour` parquet files and absent `15min/prices`
  `[stocks_on_the_move, p.66-67]`, `[stocks_on_the_move, p.77]`,
  `[testing_tuning, p.327-335]`, `[advances_fin_ml, p.208-211]`.

- **019-2026-05-14-force-index-volume-impulse (Phase 2):** tested 4
  pre-registered daily Force Index configs on `SPY`, `QQQ` and `GLD`, with
  `xauusd` used only as gold benchmark context. Best
  `gld_fi13_z126_e05_x0_sma200_h20` had CAGR 5.63%, Sharpe 0.601 and MDD -21.96%
  versus `GLD` buy-and-hold CAGR 11.44%, Sharpe 0.683 and MDD -45.56%. It passed
  WF windows (`13/17`), OOS, latest 63d FWD and cross-lib, but failed the Phase 2
  CAGR floor, same-asset Sharpe, IS MCPT (`p=0.445`), WF MCPT (`p=0.880`), PBO
  (`0.663`), DSR (`p=0.4985`, cumulative `n_trials=176`) and bootstrap.
  `n_trials=4`; family added to dead ends. Intraday remains blocked by zero
  physical `1hour` parquet files and absent `15min/prices`
  `[trading_systems_methods, p.836]`, `[trading_systems_methods, p.13]`,
  `[testing_tuning, p.327-335]`, `[advances_fin_ml, p.208-211]`.

- **020-2026-05-14-elder-ray-triple-screen (Phase 2):** tested 4 pre-registered
  daily Elder-Ray Triple Screen proxy configs on `SPY`, `QQQ`, `GLD` and `xauusd`.
  Best `xau_eray_12_26_9_ema13_bear3_h10` had CAGR 2.85%, Sharpe 3.106 and MDD
  -1.03% versus `xauusd` buy-and-hold CAGR 14.18%, Sharpe 0.909 and MDD -20.36%.
  It passed same-asset Sharpe, PBO (`0.302`), DSR (`p=0.000815`, cumulative
  `n_trials=180`), OOS, latest 63d FWD, bootstrap and cross-lib, but failed the
  Phase 2 CAGR floor, IS MCPT (`p=0.870`), WF MCPT (`p=0.920`) and WF sufficiency
  (`3/3`, fewer than 8). `n_trials=4`; family added to dead ends. Intraday
  remains blocked by zero physical `1hour` parquet files and absent `15min/prices`
  `[trading_systems_methods, p.835-838]`, `[trading_systems_methods, p.837]`,
  `[testing_tuning, p.327-335]`, `[advances_fin_ml, p.208-211]`.

- **021-2026-05-14-wilder-asi-swing-breakout (Phase 2):** tested 4
  pre-registered daily Wilder Accumulated Swing Index breakout configs on `SPY`,
  `QQQ`, `GLD` and `xauusd`. Best `xau_asi20_10_h20` had CAGR 8.80%, Sharpe
  0.683 and MDD -18.68% versus `xauusd` buy-and-hold CAGR 17.51%, Sharpe 0.990
  and MDD -20.36%. It passed OOS and cross-lib, but failed the Phase 2 CAGR
  floor, same-asset Sharpe, IS MCPT (`p=0.715`), WF MCPT (`p=0.530`), PBO
  (`0.516`), DSR (`p=0.8587`, cumulative `n_trials=184`), WF sufficiency, latest
  63d FWD (`-8.17%`) and bootstrap. `n_trials=4`; family added to dead ends.
  Intraday remains blocked by zero physical `1hour` parquet files and absent
  `15min/prices` `[trading_systems_methods, p.193-195]`,
  `[trading_systems_methods, p.165-172]`, `[testing_tuning, p.327-335]`,
  `[advances_fin_ml, p.208-211]`.

- **022-2026-05-14-regression-channel-breakout (Phase 2):** tested 4
  pre-registered daily regression-channel breakout configs on `SPY`, `QQQ`, `GLD`
  and `xauusd`. Best `xau_regch63_h30` had CAGR 3.62%, Sharpe 0.787 and MDD
  -10.78% versus `xauusd` buy-and-hold CAGR 14.32%, Sharpe 0.916 and MDD -20.36%.
  It passed PBO (`0.480`), OOS, latest 63d FWD and cross-lib, but failed the Phase
  2 CAGR floor, same-asset Sharpe, IS MCPT (`p=0.460`), WF MCPT (`p=0.250`), DSR
  (`p=0.7751`, cumulative `n_trials=188`), WF sufficiency and bootstrap.
  `n_trials=4`; family added to dead ends. Intraday remains blocked by zero
  physical `1hour` parquet files and absent `15min/prices`
  `[trading_systems_methods, p.167-169]`, `[trading_systems_methods, p.168]`,
  `[testing_tuning, p.327-335]`, `[advances_fin_ml, p.222-223]`.

- **023-2026-05-14-money-flow-pullback (Phase 2):** tested 4 pre-registered
  daily Money Flow Index pullback configs on `SPY`, `QQQ` and `GLD`; `xauusd` was
  context only because MFI requires volume. Best `gld_mfi14_os20_x50_sma200_h10`
  had CAGR 1.90%, Sharpe 0.730 and MDD -4.88% versus `GLD` buy-and-hold CAGR
  11.64%, Sharpe 0.693 and MDD -45.56%. It passed same-asset Sharpe, PBO
  (`0.246`), WF windows (`14/17`), OOS, latest 63d FWD, bootstrap and cross-lib,
  but failed the Phase 2 CAGR floor, IS MCPT (`p=0.475`), WF MCPT (`p=0.100`) and
  DSR (`p=0.2840`, cumulative `n_trials=192`). `n_trials=4`; family added to dead
  ends. Intraday remains blocked by zero physical `1hour` parquet files and absent
  `15min/prices` `[trading_systems_methods, p.540]`, `[trading_systems_methods,
  p.285]`, `[testing_tuning, p.327-335]`, `[advances_fin_ml, p.222-223]`.

- **024-2026-05-14-dual-ma-atr-breakout (Phase 2):** tested 4 pre-registered
  daily dual MA+ATR breakout configs on `SPY`, `QQQ`, `GLD` and `xauusd`. Best
  `xau_ma5_20_atr20_k1` had CAGR 10.89%, Sharpe 0.816 and MDD -15.36% versus
  `xauusd` buy-and-hold CAGR 17.41%, Sharpe 0.985 and MDD -20.36%. It passed OOS
  and cross-lib, but failed the Phase 2 CAGR floor, same-asset Sharpe, IS MCPT
  (`p=0.380`), WF MCPT (`p=0.580`), PBO (`0.607`), DSR (`p=0.7628`, cumulative
  `n_trials=196`), WF sufficiency, latest 63d FWD (`-4.22%`) and bootstrap.
  `n_trials=4`; family added to dead ends. Intraday remains blocked by zero
  physical `1hour` parquet files and absent `15min/prices`
  `[trading_systems_methods, p.352-353]`, `[trading_systems_methods, p.107]`,
  `[testing_tuning, p.327-335]`, `[advances_fin_ml, p.208-211]`.

- **025-2026-05-14-swing-point-breakout (Phase 2):** tested 4 pre-registered
  conservative swing-point breakout configs on `SPY`, `QQQ`, `GLD` and `xauusd`.
  Best `xau_swing5_break_prev_high` had CAGR 10.06%, Sharpe 1.117 and MDD -11.13%
  versus `xauusd` buy-and-hold CAGR 17.33%, Sharpe 0.984 and MDD -20.36%. It
  passed same-asset Sharpe, PBO (`0.278`), OOS and cross-lib, but failed the Phase
  2 CAGR floor, IS MCPT (`p=0.080`), WF MCPT (`p=0.320`), DSR (`p=0.4410`,
  cumulative `n_trials=200`), WF sufficiency, latest 63d FWD (`-10.95%`) and
  bootstrap. `n_trials=4`; family added to dead ends. Intraday remains blocked by
  zero physical `1hour` parquet files and absent `15min/prices`
  `[trading_systems_methods, p.165]`, `[trading_systems_methods, p.168]`,
  `[testing_tuning, p.327-335]`, `[advances_fin_ml, p.222-223]`.

- **001-2026-05-14-tiingo-final-day-audit:** infrastructure-only. Created local
  Tiingo coverage audit and refreshed critical data while the subscription was
  still active. Downloads completed for ETF, crypto, forex and Nasdaq-100
  buckets with zero errors. S&P 500 broad refresh fetched 423/730 tickers, with
  23 empty and 284 API/JSON errors late in the run; many S&P constituents already
  had local cache through 2026-05-08, so the broad universe remains usable but
  the final-day S&P refresh is not perfect. Backup created at
  `data/tiingo_backup_20260514-0311.tar.gz` (210.8 MB). `n_trials=0`, no
  strategy claim `[advances_fin_ml, p.196-202]`, `[testing_tuning, p.143-144]`.
- **002-2026-05-14-validation-scaffold:** infrastructure-only. Added
  `validation_scaffold.py` for fixed-rule IS MCPT and walk-forward MCPT, plus
  tests covering no-overlap WF windows, deterministic seeded permutations and
  tail-only WF permutation. `n_trials=0`, no strategy claim
  `[testing_tuning, p.148-150]`, `[testing_tuning, p.318-320]`.
- **003-2026-05-14-sma-momentum-regime:** tested 4 pre-registered daily
  SPY/QQQ SMA(100/200) + 63-day momentum regime configs with SHV/cash
  defensive sleeve. Best config `qqq_sma200_mom63` had CAGR 11.43%, Sharpe
  0.862 and MDD -18.60% versus QQQ buy-hold CAGR 16.51%, Sharpe 0.795 and MDD
  -49.40%. DSR passed (`p=0.00486`), but IS MCPT failed (`p=0.045`), WF MCPT
  failed (`p=0.170`) and PBO failed (`0.871`). `n_trials=4`, family added to
  dead ends `[leverage_for_the_long_run, p.13]`, `[testing_tuning, p.318-320]`,
  `[advances_fin_ml, p.208-211]`.
- **004-2026-05-14-cross-sectional-etf-momentum:** tested 4 pre-registered
  monthly ETF cross-sectional momentum configs over `SPY/QQQ/IWM/TLT/GLD` with
  `SHV` defense. Best config `mom126_top2` had CAGR 10.83%, Sharpe 0.824 and
  MDD -19.96% versus equal-weight benchmark CAGR 11.56%, Sharpe 0.898 and MDD
  -28.72%. PBO passed (`0.343`) and DSR passed (`p=0.0229`, cumulative
  `n_trials=8`), but the family failed economic Sharpe, IS MCPT (`p=0.075`), WF
  MCPT (`p=0.29`) and FWD 63d stress (`-0.32%`). An implementation bug in the
  initial run's rebalance weight replacement was corrected before recording
  final results. `n_trials=4`, family added to dead ends
  `[stocks_on_the_move, p.76-77]`, `[systematic_trading, p.185-188]`,
  `[testing_tuning, p.318-320]`.
- **005-2026-05-14-vol-target-static-sleeves:** tested 4 pre-registered fixed
  ETF sleeves with 10% annualized volatility targeting, 100-day volatility
  lookback and 1.5x cap. Best config `vt_35spy_15qqq_30ief_20gld` had CAGR
  10.39%, Sharpe 1.005 and MDD -20.34% versus static 60/40 `SPY/IEF` CAGR
  8.84%, Sharpe 0.798 and MDD -29.79%. DSR passed (`p=0.00533`, cumulative
  `n_trials=12`), but IS MCPT failed (`p=0.12`), WF MCPT failed (`p=0.43`) and
  PBO failed (`0.657`). A benchmark alignment bug in the first run was corrected
  before final artifacts. `n_trials=4`, family added to dead ends
  `[systematic_trading, p.40]`, `[systematic_trading, p.196-197]`,
  `[testing_tuning, p.318-320]`, `[advances_fin_ml, p.208-211]`.
- **006-2026-05-14-rsi2-mean-reversion:** tested 4 pre-registered short-horizon
  `RSI(2)` mean-reversion configs on `SPY` and `QQQ`, holding `SHV` while flat
  and lagging signals one bar. Best config `qqq_rsi2_e5_x70` had CAGR 8.47%,
  Sharpe 0.795 and MDD -16.09% versus QQQ buy-hold CAGR 16.81%, Sharpe 0.807
  and MDD -49.37%. PBO passed (`0.214`) and DSR passed (`p=0.0441`, cumulative
  `n_trials=16`), but the family failed same-asset Sharpe, IS MCPT (`p=0.05`),
  WF MCPT (`p=0.35`) and cross-lib was not computed. `n_trials=4`, family added
  to dead ends `[quant_trading_chan, p.51]`, `[quant_trading_chan, p.142-143]`,
  `[testing_tuning, p.318-320]`.
- **007-2026-05-14-vol-carry-proxy:** pre-registered 4 long-only volatility-carry
  proxy configs using negative trailing `VIXY` return as a filter for `SPY`/`QQQ`
  exposure versus `SHV`, motivated by carry's negative-skew profile and roll/carry
  logic `[systematic_trading, p.32-35]`, `[systematic_trading, p.119]`. The local
  Tiingo manifest listed `VIXY`, but `data/tiingo/daily/prices/VIXY.parquet` was
  absent, so the conservative guardrail fired: no substitution to available
  `VXX` after pre-registration, no metrics or gates computed, `status=data_blocked`,
  `n_trials=0` `[testing_tuning, p.327-335]`.
- **008-2026-05-14-vxx-vol-carry-proxy:** re-registered the volatility-carry
  proxy with confirmed available `VXX` data, testing 4 configs over `SPY`/`QQQ`
  versus `SHV`. Best config `vxx_neg21_spy` had CAGR 9.86%, Sharpe 0.935 and MDD
  -29.54% versus SPY buy-and-hold CAGR 14.74%, Sharpe 0.910 and MDD -33.70%.
  It passed WF windows (9/10 positive), OOS, FWD stress, bootstrap and cross-lib,
  but failed IS MCPT (`p=0.145`), WF MCPT (`p=0.10`), PBO (`0.686`) and DSR
  (`p=0.0554`, cumulative `n_trials=20`). `n_trials=4`; family added to dead
  ends `[systematic_trading, p.32-35]`, `[systematic_trading, p.119]`,
  `[testing_tuning, p.318-320]`, `[advances_fin_ml, p.208-211]`.
- **009-2026-05-14-multi-asset-ewmac:** tested 4 pre-registered fixed EWMAC
  configs over liquid ETFs, selecting the strongest positive `SPY/QQQ/TLT` or
  `SPY/QQQ/TLT/IEF/GLD` forecast and otherwise holding `SHV`. Best config
  `ewmac_16_64_risk3` had CAGR 11.40%, Sharpe 0.814 and MDD -24.97% versus
  same-universe equal-weight CAGR 12.72%, Sharpe 1.049 and MDD -30.06%. It
  passed WF windows (9/12 positive), OOS, FWD stress, bootstrap and cross-lib,
  but failed benchmark Sharpe, IS MCPT (`p=0.165`), WF MCPT (`p=0.43`), PBO
  (`0.814`) and DSR (`p=0.1017`, cumulative `n_trials=24`). `n_trials=4`;
  family added to dead ends `[systematic_trading, p.118-119]`,
  `[testing_tuning, p.318-320]`, `[advances_fin_ml, p.208-211]`.
- **010-2026-05-14-etf-pairs-zscore:** tested 4 pre-registered market-neutral ETF
  ratio z-score pair configs: `GLD/SLV` 60d and 120d, `TLT/IEF` 60d, and
  `SPY/QQQ` 60d. Best config `tlt_ief_z60_e1` had CAGR 0.69%, Sharpe 0.183 and
  MDD -12.05% versus SHV CAGR 1.39%, Sharpe 5.425 and MDD -0.45%. PBO passed
  (`0.429`) and WF windows passed (8/12 positive), but the family failed SHV
  benchmark Sharpe, IS MCPT (`p=0.365`), WF MCPT (`p=0.53`), DSR (`p=0.9049`,
  cumulative `n_trials=28`) and bootstrap 99.9% CI low (`-0.0000926`).
  `n_trials=4`; family added to dead ends `[algo_trading_chan, p.65-66]`,
  `[algo_trading_chan, p.71-73]`, `[testing_tuning, p.318-320]`,
  `[advances_fin_ml, p.222-223]`.
- **011-2026-05-14-vix-managed-exposure:** tested 4 pre-registered VIX-managed
  equity exposure configs scaling `SPY`/`QQQ` by previous-21d mean VIX versus
  `SHV`, with one-bar signal lag. Best config `qqq_vix15_w21` had CAGR 14.10%,
  Sharpe 0.945 and MDD -27.01% versus QQQ buy-and-hold CAGR 18.94%, Sharpe
  0.945 and MDD -35.12%. It passed IS MCPT (`p=0.000`), WF MCPT (`p=0.010`),
  PBO (`0.400`), DSR (`p=0.04697`, cumulative `n_trials=32`), WF windows,
  OOS, bootstrap and cross-lib, but failed FWD stress over the latest 63 trading
  days (`-1.18%`). `n_trials=4`; family tagged as promising but dead-ended for
  winner purposes until a new pre-registered stress/robustness iteration
  `[paper.bozovic_2024_vix_managed, §methodology]`, `[testing_tuning,
  p.318-320]`, `[advances_fin_ml, p.208-211]`, `[advances_fin_ml, p.222-223]`.
- **012-2026-05-14-vix-managed-stress:** stressed the iteration 011 VIX family
  with 4 pre-registered variants: `QQQ` with 25%/50% equity floors, `QQQ` with a
  42d VIX window, and a 50/50 `SPY/QQQ` basket. Best config
  `qqq_vix15_w21_floor50` had CAGR 16.57%, Sharpe 0.954 and MDD -30.99% versus
  QQQ buy-and-hold CAGR 18.94%, Sharpe 0.945 and MDD -35.12%. It passed WF MCPT
  (`p=0.040`), DSR (`p=0.04773`, cumulative `n_trials=36`), WF windows, OOS,
  bootstrap and cross-lib, but failed IS MCPT (`p=0.030`), PBO (`0.729`) and FWD
  63d stress (`-0.41%`). `n_trials=4`; family added to dead ends
  `[paper.bozovic_2024_vix_managed, §methodology]`, `[testing_tuning,
   p.318-320]`, `[testing_tuning, p.327-335]`, `[advances_fin_ml, p.208-211]`.
- **013-2026-05-14-crypto-donchian-trend:** pivoted to 4 pre-registered
  BTC/ETH Donchian breakout configs with `SHV` as defensive sleeve. Best config
  `eth_don20` had CAGR 66.12%, Sharpe 1.364 and MDD -35.51% versus ETH
  buy-and-hold CAGR 95.20%, Sharpe 1.160 and MDD -92.94%. It passed data
  freshness, same-asset Sharpe, IS MCPT (`p=0.000`), WF MCPT (`p=0.050`), PBO
  (`0.286`), DSR (`p=0.00364`, cumulative `n_trials=40`), OOS, bootstrap and
  cross-lib, but failed WF positive windows (5/6 vs required 6) and latest 63d
  FWD stress (`-6.85%`). `n_trials=4`; family added to dead ends unless a new
  crypto economic hypothesis and cleaner data-source plan are pre-registered
  `[paper.zarattini_2025_crypto_trends, §methodology]`, `[testing_tuning,
  p.318-320]`, `[advances_fin_ml, p.208-211]`.
- **014-2026-05-14-crypto-vol-target-momentum:** pivoted away from Donchian
  breakouts into 4 pre-registered BTC/ETH trailing-momentum configs with 100d
  realized-vol scaling, 20% annualized volatility target and max exposure 1.0.
  Best config `btc_mom63_vt20` had CAGR 25.57%, Sharpe 1.377 and MDD -22.70%
  versus BTC buy-and-hold CAGR 68.51%, Sharpe 1.112 and MDD -83.15%. It passed
  same-asset Sharpe, DSR (`p=0.0189`, cumulative `n_trials=44`), OOS, latest 63d
  FWD stress (`+0.50%`), bootstrap and cross-lib, but failed IS MCPT (`p=0.015`),
  WF MCPT (`p=0.110`), PBO (`0.857`) and WF positives (5/6 vs 6 required).
  `n_trials=4`; family added to dead ends as a risk-control diagnostic, not a
  winner `[systematic_trading, p.40]`, `[systematic_trading, p.137-148]`,
  `[testing_tuning, p.318-320]`, `[advances_fin_ml, p.208-211]`.
- **015-2026-05-14-realized-vol-compression-momentum:** pivoted away from
  crypto-only local variants and VIX-managed floors/windows into 4 pre-registered
  `SPY/QQQ` realized-volatility compression + 63d momentum configs. Best config
  `qqq_rv20_p60_m63` had CAGR 7.63%, Sharpe 0.727 and MDD -21.20% versus QQQ
  buy-and-hold CAGR 19.09%, Sharpe 0.948 and MDD -35.12%. It passed data
  freshness, WF windows (9/12), OOS, latest 63d FWD stress and cross-lib, but
  failed benchmark Sharpe, IS MCPT (`p=0.425`), WF MCPT (`p=0.490`), PBO
  (`0.514`), DSR (`p=0.2850`, cumulative `n_trials=48`) and bootstrap 99.9% CI
  low (`-0.0000428`). `n_trials=4`; family added to dead ends rather than tuning
  local percentiles `[volatility_trading, p.36]`, `[volatility_trading, p.58-59]`,
  `[testing_tuning, p.327-335]`, `[advances_fin_ml, p.208-211]`.
- **016-2026-05-14-credit-risk-appetite-filter:** tested 4 pre-registered
  `SPY/QQQ` configs using lagged `HYG/IEF` ratio momentum as a credit-risk
  appetite filter plus lagged own-asset 63d momentum. Best config
  `spy_hygief126_m63` had CAGR 6.35%, Sharpe 0.730 and MDD -23.25% versus SPY
  buy-and-hold CAGR 15.12%, Sharpe 0.913 and MDD -33.70%. It passed data
  freshness, WF windows (9/12), OOS, latest 63d FWD stress and cross-lib, but
  failed benchmark Sharpe, IS MCPT (`p=0.310`), WF MCPT (`p=0.430`), PBO
  (`0.900`), DSR (`p=0.2749`, cumulative `n_trials=52`) and bootstrap 99.9% CI
  low (`-0.0000182`). `n_trials=4`; family added to dead ends rather than
  locally tuning `HYG/IEF` lookbacks `[systematic_trading, p.42]`,
  `[trading_systems_methods, p.13]`, `[testing_tuning, p.327-335]`,
  `[advances_fin_ml, p.208-211]`.
- **017-2026-05-14-carver-multi-asset-forecast:** tested 4 pre-registered
  Carver-style positive EWMAC forecast-combination configs over
  `SPY/QQQ/TLT/GLD` and `SPY/QQQ/TLT/IEF/GLD`, with inverse-volatility weights,
  one-bar lag and 10%/15% volatility targeting. Best config
  `risk4_ewmac16_64_vt10` had CAGR 9.85%, Sharpe 0.930 and MDD -20.92% versus
  equal-weight `SPY/QQQ/TLT/GLD` CAGR 12.30%, Sharpe 1.156 and MDD -25.16%. It
  passed data freshness, WF windows (9/12), OOS, bootstrap and cross-lib, but
  failed benchmark Sharpe, IS MCPT (`p=0.250`), WF MCPT (`p=0.530`), PBO
  (`0.600`), DSR (`p=0.0874`, cumulative `n_trials=56`) and latest 63d FWD
  stress (`-3.62%`). `n_trials=4`; family added to dead ends rather than tuning
   EWMAC lookbacks or vol target `[systematic_trading, p.40]`,
   `[systematic_trading, p.118-119]`, `[systematic_trading, p.137-148]`,
   `[testing_tuning, p.327-335]`, `[advances_fin_ml, p.208-211]`.
- **018-2026-05-14-ehlers-cycle-mode:** tested 4 pre-registered Ehlers-inspired
  cycle/trend mode overlay configs on `SPY` and `QQQ`, using smoothed price,
  instantaneous trendline, fixed-cycle sine/lead-sine phase proxy and one-bar
  lagged switch to `SHV`. Best config `qqq_ehlers_c30_t15` had CAGR 12.51%,
  Sharpe 1.004 and MDD -18.48% versus QQQ buy-and-hold CAGR 19.80%, Sharpe
  0.980 and MDD -35.12%. It passed same-asset Sharpe, PBO (`0.314`), DSR
  (`p=0.0476`, cumulative `n_trials=60`), WF windows, OOS, latest 63d FWD stress,
  bootstrap and cross-lib, but failed IS MCPT (`p=0.075`) and WF MCPT (`p=0.300`).
  `n_trials=4`; family added to dead ends rather than tuning cycle periods or
   thresholds `[rocket_science, p.99-100]`, `[rocket_science, p.107]`,
   `[rocket_science, p.114-117]`, `[testing_tuning, p.327-335]`.
- **019-2026-05-14-yield-carry-rotation:** tested 4 pre-registered yield/carry
  configs using `SPY` trailing dividend yield versus 3m cash and 10y/30y term
  spreads to choose `SPY`, `IEF`/`TLT`, or `SHV`. Best config
  `spy_div_gt_cash_ief_term` had CAGR 11.15%, Sharpe 0.783 and MDD -33.70%
  versus 60/40 `SPY/IEF` CAGR 9.95%, Sharpe 1.004 and MDD -21.02%. It passed
  data freshness, WF windows (11/12), OOS, bootstrap and cross-lib, but failed
  benchmark Sharpe, IS MCPT (`p=0.415`), WF MCPT (`p=0.460`), PBO (`0.629`),
  DSR (`p=0.2194`, cumulative `n_trials=64`) and latest 63d FWD stress
  (`-0.21%`). `n_trials=4`; family added to dead ends rather than tuning yield
  thresholds or tenors `[systematic_trading, p.32-35]`, `[systematic_trading,
  p.119]`, `[systematic_trading, p.288]`, `[testing_tuning, p.327-335]`.
- **020-2026-05-14-turn-of-month-seasonality:** tested 4 pre-registered
  turn-of-month calendar configs holding `SPY` or `QQQ` around the final 1-2 and
  first 4 trading days of each month, otherwise `SHV`, with one-bar lagged
  exposure. Best config `spy_tom_l1_f4` had CAGR 6.11%, Sharpe 0.744 and MDD
  -16.65% versus `SPY` buy-and-hold CAGR 14.20%, Sharpe 0.861 and MDD -33.70%.
  It passed data freshness, WF windows (9/12), OOS, latest 63d FWD stress,
  bootstrap and cross-lib, but failed benchmark Sharpe, IS MCPT (`p=0.205`), WF
  MCPT (`p=0.260`), PBO (`0.500`, not `<0.5`) and DSR (`p=0.2735`, cumulative
  `n_trials=68`). `n_trials=4`; family added to dead ends rather than tuning
   calendar offsets or holidays `[trading_systems_methods, p.479-481]`,
   `[trading_systems_methods, p.422]`, `[testing_tuning, p.327-335]`,
   `[advances_fin_ml, p.208-211]`.
- **021-2026-05-14-intraday-overnight-decomposition:** tested 4 pre-registered
  adjusted-OHLC component rules: close-to-open and open-to-close legs for `SPY`
  and `QQQ`, with `SHV` idle return only for open-to-close configs. Best config
  `qqq_close_to_open` had CAGR 12.44%, Sharpe 0.998 and MDD -27.43% versus QQQ
  buy-and-hold CAGR 19.25%, Sharpe 0.958 and MDD -35.12%. It passed data
  freshness, same-asset Sharpe, PBO (`0.086`), WF windows (11/12), OOS, latest
  63d FWD stress, bootstrap and cross-lib, but failed IS MCPT (`p=1.000`), WF
  MCPT (`p=0.430`) and DSR (`p=0.0600`, cumulative `n_trials=72`). The IS MCPT
  was especially conservative/unpromotional because unconditional component
  permutation preserves the close-to-open return distribution. `n_trials=4`;
  family added to dead ends rather than tuning session definitions or adding
  filters locally `[paper.zarattini_2024_intraday_spy, §methodology]`,
  `[trading_systems_methods, p.939]`, `[testing_tuning, p.327-335]`,
   `[advances_fin_ml, p.222-223]`.
- **022-2026-05-14-kama-efficiency-regime:** tested 4 pre-registered
  KAMA/Efficiency Ratio adaptive regime configs on `SPY` and `QQQ`, with `SHV`
  as defensive sleeve and one-bar-lagged signals. Best config `qqq_kama_er20`
  had CAGR 8.63%, Sharpe 0.889 and MDD -16.57% versus QQQ buy-and-hold CAGR
  19.25%, Sharpe 0.958 and MDD -35.12%. It passed data freshness, PBO (`0.257`),
  WF windows (9/12), OOS, latest 63d FWD stress, bootstrap and cross-lib, but
  failed benchmark Sharpe, IS MCPT (`p=0.110`), WF MCPT (`p=0.520`) and DSR
  (`p=0.1264`, cumulative `n_trials=76`). `n_trials=4`; family added to dead
  ends rather than tuning KAMA lengths or ER thresholds `[trading_systems_methods,
  p.10-11]`, `[trading_systems_methods, p.780-782]`, `[testing_tuning,
  p.327-335]`, `[advances_fin_ml, p.222-223]`.
- **023-2026-05-14-obv-volume-confirmation:** tested 4 pre-registered OBV
  volume-confirmation configs on `SPY` and `QQQ`, using `SHV` as defensive sleeve
  and one-bar-lagged signals. Best config `qqq_obv21` had CAGR 14.09%, Sharpe
  1.136 and MDD -21.25% versus QQQ buy-and-hold CAGR 19.25%, Sharpe 0.958 and
  MDD -35.12%. It passed data freshness, same-asset Sharpe, PBO (`0.086`), DSR
  (`p=0.0173`, cumulative `n_trials=80`), WF windows, OOS, latest 63d FWD stress,
  bootstrap and cross-lib, but failed IS MCPT (`p=0.020`) and WF MCPT (`p=0.180`).
  `n_trials=4`; family added to dead ends rather than tuning OBV lookbacks or
   adding local price filters `[trading_systems_methods, p.537]`, `[testing_tuning,
   p.327-335]`, `[advances_fin_ml, p.222-223]`.
- **024-2026-05-14-accumulation-distribution-volume:** tested 4 pre-registered
  close-location volume-pressure configs on `SPY` and `QQQ`: Accumulation/
  Distribution and Intraday Intensity with 21d deltas, `SHV` defense and one-bar
  lag. Best config `qqq_ad21` had CAGR 9.21%, Sharpe 0.700 and MDD -39.94%
  versus QQQ buy-and-hold CAGR 19.25%, Sharpe 0.958 and MDD -35.12%. It passed
  data freshness, WF windows (11/12), OOS, latest 63d FWD stress and cross-lib,
  but failed benchmark Sharpe, IS MCPT (`p=0.530`), WF MCPT (`p=0.830`), PBO
  (`0.900`), DSR (`p=0.3641`, cumulative `n_trials=84`) and bootstrap 99.9% CI
  low (`-0.0000976`). `n_trials=4`; family added to dead ends rather than tuning
  AD/II lookbacks, thresholds or price filters `[trading_systems_methods,
  p.540-541]`, `[testing_tuning, p.327-335]`, `[advances_fin_ml, p.208-211]`.
- **025-2026-05-14-market-breadth-proxy:** tested 4 pre-registered breadth timing
  configs using a current large-cap adjusted-close proxy: hold `SPY` or `QQQ` when
  at least 55% of proxy constituents are above their 63d or 126d SMA, otherwise
  hold `SHV`. Best config `spy_breadth_sma63_gt55` had CAGR 8.82%, Sharpe 0.886
  and MDD -16.25% versus SPY buy-and-hold CAGR 15.08%, Sharpe 0.924 and MDD
  -33.70%. It passed data freshness, WF MCPT (`p=0.010`), WF windows (9/9), OOS,
  latest 63d FWD stress, bootstrap and cross-lib, but failed same-asset Sharpe,
  IS MCPT (`p=0.210`), PBO (`0.829`) and DSR (`p=0.2173`, cumulative
  `n_trials=88`). The current-constituent proxy also carries survivorship bias, so
  even numeric success would have been capped at non-winner status. `n_trials=4`;
  family added to dead ends rather than tuning breadth thresholds, SMA lengths or
  constituent lists `[trading_systems_methods, p.548-549]`,
  `[trading_systems_methods, p.941]`, `[testing_tuning, p.327-335]`,
  `[advances_fin_ml, p.208-211]`.
- **026-2026-05-14-sector-risk-appetite:** tested 4 pre-registered sector
  relative-strength risk-appetite configs: `XLY/XLP` gating `SPY` and `XLK/XLU`
  gating `QQQ`, with 63d/126d ratio momentum, `SHV` defense and one-bar lag.
  Best config `spy_xly_xlp_m126` had CAGR 8.18%, Sharpe 0.825 and MDD -16.18%
  versus SPY buy-and-hold CAGR 14.22%, Sharpe 0.862 and MDD -33.70%. It passed
  data freshness, WF windows (10/12), OOS, latest 63d FWD stress, bootstrap and
  cross-lib, but failed same-asset Sharpe, IS MCPT (`p=0.250`), WF MCPT
  (`p=0.210`), PBO (`0.800`) and DSR (`p=0.2082`, cumulative `n_trials=92`).
  `n_trials=4`; family added to dead ends rather than tuning sector pairs,
  ratio lookbacks or thresholds `[trading_systems_methods, p.13]`,
  `[trading_systems_methods, p.542-544]`, `[testing_tuning, p.327-335]`,
  `[advances_fin_ml, p.208-211]`.
- **027-2026-05-14-commodity-macro-filter:** pre-registered 4 commodity macro
  filter configs using `DBC` and `GLD` momentum to gate `SPY`/`TLT` exposure, with
  quarterly/semiannual lookbacks and `SHV` defense. The iteration closed
  `data_blocked` before testing because `data/tiingo/daily/prices/DBC.parquet`
  was unavailable. Per the preregistered kill rule, no substitute commodity proxy
  was used after discovering the data issue; `n_trials=0` and cumulative
  `n_trials=92` `[trading_systems_methods, p.939]`, `[trading_systems_methods,
   p.285]`, `[testing_tuning, p.327-335]`.
- **028-2026-05-14-gayed-letf-qqq-rotation:** tested 4 pre-registered
  Gayed-style Nasdaq LETF rotation configs using lagged `QQQ > SMA200` to hold
  `QLD`/`TQQQ` or `SHV`, with two sparse realized-volatility-cap variants. Best
  `qld_qqq_sma200_rv70` had CAGR 22.64%, Sharpe 0.978 and MDD -34.54% versus QLD
  buy-and-hold CAGR 33.80%, Sharpe 0.916 and MDD -63.68%. It passed same-risk
  Sharpe, WF MCPT (`p=0.010`), WF windows (11/12), OOS, latest 63d FWD stress,
  bootstrap and cross-lib, but failed IS MCPT (`p=0.035`), PBO (`0.686`) and DSR
  (`p=0.0816`, cumulative `n_trials=96`). `n_trials=4`; family added to dead ends
  rather than tuning MA lengths, volatility thresholds or QLD/TQQQ variants
  `[leverage_for_the_long_run, p.13]`, `[leverage_for_the_long_run, p.16-17]`,
  `[testing_tuning, p.327-335]`, `[advances_fin_ml, p.208-211]`.
- **029-2026-05-14-correlation-breakdown-risk-filter:** tested 4 pre-registered
  filters that hold `SPY` or `QQQ` only when lagged rolling equity/Treasury
  correlation is negative, otherwise `SHV`. Best `spy_corr63_lt0` had CAGR 9.03%,
  Sharpe 0.562 and MDD -55.20% versus SPY buy-and-hold CAGR 10.97%, Sharpe 0.627
  and MDD -55.20%. It passed PBO (`0.103`), WF windows (14/16), OOS, latest 63d
  FWD and cross-lib, but failed same-asset Sharpe, IS MCPT (`p=0.810`), WF MCPT
  (`p=0.580`), DSR (`p=0.5240`, cumulative `n_trials=100`) and bootstrap 99.9%
  mean-daily CI low (`-0.00002050`). `n_trials=4`; family added to dead ends rather
  than tuning correlation windows, thresholds or local overlays `[risk_parity,
  p.80-81]`, `[systematic_trading, p.170-171]`, `[testing_tuning, p.327-335]`,
  `[advances_fin_ml, p.222-223]`.
- **030-2026-05-14-study-closure-audit:** tested no strategy configs. The closure
  audit found 30 iteration directories, parsed 29 prior `RESULTS.json` files,
  confirmed summed prior `n_trials=100`, confirmed zero prior `winner=true`
  results and found all prior directories have `PRE_REG.md`, `RESULTS.json` and
  `SUMMARY.md`. It closed `fail` rather than `infrastructure_only` because
  iteration 002 uses a legacy infrastructure schema lacking current `status` and
  `pre_registered` fields. `n_trials=0`; study closed at target cap with no
  winner and no deploy implication `[testing_tuning, p.327-335]`,
  `[advances_fin_ml, p.222-223]`.

- **026-2026-05-14-price-density-trend-filter (Phase 2):** tested 4
  pre-registered daily Price Density trend-filter configs on `SPY`, `QQQ`, `GLD`
  and `xauusd`, using 20-day Price Density below 4.0, `SMA200`, `SHV` while flat
  and one-bar-lagged signals. Best `spy_pd20_lt4_sma200` had CAGR 6.45%, Sharpe
  0.797 and MDD -20.04% versus SPY buy-and-hold CAGR 10.87%, Sharpe 0.644 and
  MDD -55.20%. It passed same-asset Sharpe, IS MCPT (`p=0.000`), DSR
  (`p=0.0413`, cumulative `n_trials=204`), WF windows (`21/29`), OOS, latest 63d
  FWD, bootstrap and cross-lib, but failed the Phase 2 CAGR floor, WF MCPT
  (`p=0.060`) and PBO (`0.512`). `n_trials=4`; family added to dead ends rather
  than tuning Price Density thresholds/lookbacks or SMA length
  `[trading_systems_methods, p.12]`, `[trading_systems_methods, p.13]`,
  `[testing_tuning, p.327-335]`, `[advances_fin_ml, p.208-211]`.

- **027-2026-05-14-williams-r-exhaustion (Phase 2):** tested 4 pre-registered
  daily Williams %R exhaustion-reversal configs on `SPY`, `QQQ`, `GLD` and
  `xauusd`, using `%R(14) <= -90`, `%R >= -50` exits, 10-bar max hold, `SMA200`,
  `SHV` while flat and one-bar-lagged signals. Best
  `qqq_wr14_os90_x50_sma200_h10` had CAGR 6.07%, Sharpe 0.788 and MDD -15.45%
  versus QQQ buy-and-hold CAGR 9.38%, Sharpe 0.469 and MDD -82.97%. It passed
  same-asset Sharpe, IS MCPT (`p=0.005`), WF MCPT (`p=0.010`), WF windows
  (`17/23`), OOS, bootstrap and cross-lib, but failed the Phase 2 CAGR floor, PBO
  (`0.651`), DSR (`p=0.0918`, cumulative `n_trials=208`) and latest 63d FWD
  (`-1.96%`). `n_trials=4`; family added to dead ends. Intraday remains blocked
  by zero physical `1hour` parquet files and absent `15min/prices`
  `[trading_systems_methods, p.385-386]`, `[trading_systems_methods, p.172]`,
  `[testing_tuning, p.327-335]`, `[advances_fin_ml, p.208-211]`.

- **028-2026-05-14-cmo-momentum-continuation (Phase 2):** tested 4
  pre-registered daily CMO momentum-continuation configs on `SPY`, `QQQ`, `GLD`
  and `xauusd`, using `CMO(20) >= 50`, `CMO <= 0` exits, 20-bar max hold,
  `SMA200`, `SHV` while flat and one-bar-lagged signals. Best
  `xau_cmo20_e50_x0_sma200_h20` had CAGR 5.91%, Sharpe 0.638 and MDD -14.68%
  versus `xauusd` buy-and-hold CAGR 17.28%, Sharpe 1.060 and MDD -20.36%. It
  passed OOS, latest 63d FWD and cross-lib, but failed the Phase 2 CAGR floor,
  same-asset Sharpe, IS MCPT (`p=0.470`), WF MCPT (`p=0.790`), PBO (`0.885`),
  DSR (`p=0.8738`, cumulative `n_trials=212`), WF sufficiency (`2/2`, fewer than
  8 windows) and bootstrap. `n_trials=4`; family added to dead ends. Intraday
  remains blocked by zero physical `1hour` parquet files and absent `15min/prices`
  `[trading_systems_methods, p.388]`, `[trading_systems_methods, p.284]`,
  `[testing_tuning, p.327-335]`, `[advances_fin_ml, p.208-211]`.

- **029-2026-05-14-fisher-cycle-reversal (Phase 2):** tested 4 pre-registered
  daily Fisher Transform cycle-reversal configs on `SPY`, `QQQ`, `GLD` and
  `xauusd`, using `Fisher(10)`, an upward turn below zero from exhaustion,
  `SMA200`, `SHV` while flat and one-bar-lagged signals. Best
  `spy_fisher10_reversal_sma200_h10` had CAGR 4.70%, Sharpe 0.729 and MDD
  -11.09% versus `SPY` buy-and-hold CAGR 10.90%, Sharpe 0.646 and MDD -55.20%.
  It passed same-asset Sharpe, IS MCPT (`p=0.000`), WF MCPT (`p=0.050`), WF
  windows (`23/29`), OOS, bootstrap and cross-lib, but failed the Phase 2 CAGR
  floor, PBO (`0.587`), DSR (`p=0.0882`, cumulative `n_trials=216`) and latest
  63d FWD (`-2.76%`). `n_trials=4`; family added to dead ends. Intraday remains
  blocked by zero physical `1hour` parquet files and absent `15min/prices`
  `[cycle_analytics, p.195-197]`, `[trading_systems_methods, p.284]`,
  `[testing_tuning, p.327-335]`, `[advances_fin_ml, p.208-211]`.

## Last Result

Phase 2 iteration 029 closed `fail`: daily Fisher Transform cycle reversal failed
the Phase 2 CAGR floor, PBO, DSR and latest 63d FWD despite passing same-asset
Sharpe, IS MCPT, WF MCPT, WF windows, OOS, bootstrap and cross-lib.
Artifacts:
`studies/success_trading_strat/iters/phase02/029-2026-05-14-fisher-cycle-reversal/`.

Phase 2 iteration 030 closed `fail` as a conservative closure/audit at the planned
30-iteration cap. It tested no new strategy (`n_trials=0`) and parsed the 29 prior
Phase 2 `RESULTS.json` files. Audit results: 29 prior iterations, all `fail`, zero
`winner=true`, zero `strict_winner`, zero `candidate_watchlist`/`paper_trade_candidate`,
required artifacts complete, and Phase 2 local trial sum `116` reconciled with global
`cumulative_n_trials=216`. No strategy gates were recomputed; prior MCPT/PBO/DSR/WF/OOS/FWD/bootstrap/cross-lib evidence remains binding `[testing_tuning, p.318-320]`,
`[testing_tuning, p.327-335]`, `[advances_fin_ml, p.222-223]`.
Artifacts:
`studies/success_trading_strat/iters/phase02/030-2026-05-14-phase2-closure-audit/`.

## Next Step

Phase 2 is closed at the planned 30-iteration cap with no winner and no deploy
implication. Phase 3 guidance now lives in `PHASE3_BH_BEATER_SPEC.md`: the next
loop should require a buy-and-hold beating return engine before testing, with
aligned CAGR and terminal wealth versus B&H as hard economic gates. Preferred
mechanisms are controlled LETF/leverage, high-beta rotation, crash-rearmed exposure
and explicitly modeled gross-exposure long/short rules `[systematic_trading, p.40]`,
`[leverage_for_the_long_run, p.13]`, `[advances_fin_ml, p.222-223]`.

Future work should require restored/audited physical 1h/15m files or the Phase 3
B&H-beater mechanism set above, preferably away from daily Fisher/CMO oscillator
filters, Williams %R/close-location exhaustion filters, Price Density/noise-only
filters, daily event-driven swing-high/low breakout, MA/ATR breakout/band variants,
gold daily Keltner/ATR breakout, gold MACD trend, equity ADX trend, stochastic
close-location pullbacks, DeMark setup reversals, gold/SPY relative-strength filters,
VIDYA adaptive trend filters, Bollinger compression breakouts and equity pullback/reversion. Do not
locally tune Keltner EMA/ATR multipliers, MACD periods, ADX thresholds/lengths,
Bollinger windows, sigma multipliers, Woodshedder ROC lengths/confirmation/exits, Clenow slope windows/SMA filters/thresholds, Force Index EMA/z-score/hold parameters, realized-volatility compression percentiles, relative-strength SMA lengths, momentum
lookbacks or exits after these fails. Keep explicit schema/versioning rules and preserve
`candidate_watchlist`/`paper_trade_candidate` separately from `strict_winner`.
Also keep prior no-tune dead ends: `HYG/IEF` lookbacks, realized-volatility
thresholds, BTC/ETH momentum, Donchian lookbacks, VIX floors/windows,
Carver/EWMAC multi-asset forecast parameters, Ehlers cycle periods/thresholds,
yield-carry term/dividend thresholds, turn-of-month calendar offsets,
intraday/overnight session definitions, KAMA lengths, ER thresholds, OBV
lookbacks, AD/II lookbacks, breadth thresholds, constituent lists, sector pairs,
commodity proxy substitutions, Gayed LETF `QQQ` SMA lengths/volatility caps/bands,
equity/Treasury correlation windows or thresholds, equity Bollinger
mean-reversion parameters, gold MACD periods/regime filters, equity ADX
thresholds/lengths, stochastic close-location thresholds/lookbacks, Price Density
 thresholds/lookbacks/SMA filters, Williams %R lookbacks/entry/exit thresholds/hold lengths/SMA filters, CMO lookbacks/entry/exit thresholds/hold lengths/SMA filters, Fisher lookbacks/entry/exit thresholds/hold lengths/SMA filters, event-driven
swing filters/breakout definitions, DeMark setup
counts/compare lags/hold lengths, gold/SPY relative-strength windows, gold
momentum lookbacks, VIDYA volatility windows/base constants, Woodshedder ROC
lengths/confirmation/exits, Force Index EMA/z-score/hold parameters, Elder-Ray
Triple Screen MACD/EMA/Bear Power/hold parameters, Wilder ASI entry/exit/max-hold
parameters, regression-channel windows/entry/exit/max-hold parameters, dual MA/ATR
breakout lengths/multipliers, and gold Keltner EMA/ATR multipliers
`[testing_tuning, p.327-335]`.

# Lead c05 — Absolute Momentum 12-month (Antonacci) × 4 LETFs (aggregate)

**Phase:** phase_3_5e | **Lead:** c05 | **Status:** DEAD END (0/12 PASS)
**Period:** 2004-11-18 → 2026-04-15 (21.4y, Stage 1 reference_prices.parquet + Stage 2 Tiingo real)
**Tested:** 4 tickers × 3 configs = 12 runs
**Aggregation iter:** 40

## Summary

Antonacci's 12-month absolute momentum `[dual_momentum, ch.6]` applied to 4 leveraged ETFs
(QLD 2×, SSO 2×, TQQQ 3×, UPRO 3×) with 3 off-legs (cash, GLD, TLT) produced **0 gate-passing
configs** across all 12 trials. This mirrors Phase 3.5d D4 result (monthly dual momentum 0/6
PASS) and is structurally explained by three compounding failures:

1. **Monthly rebalancing cannot protect intra-month crashes in LETFs.** The 2020 COVID crash
   (-33% in 23 days) and 2022 CPI bear (-33% over months, but intra-month spikes) both hit
   before end-of-month rebalance fires. Daily-signal strategies (c01 SMA200, c07 Clenow) survive
   precisely because they respond within the same bar. Monthly cadence is a structural mismatch for
   instruments with 2×–3× beta amplification.

2. **DSR fails universally** (p=0.137–0.360 vs gate p<0.05). At cumulative n_trials=21–32 for this
   family, the honest DSR threshold is demanding. None of the 12 configs has Sharpe_net high enough
   to overcome the penalty — the family is generating Sharpe_net ≤ 0.560 when DSR at this trial
   count requires roughly Sharpe_net ≥ 0.9+ to pass at p<0.05. `[advances_fin_ml, p.298-299]`

3. **Calmar is structurally too low** (0.142–0.356 vs gate 0.500). Monthly momentum leaves MaxDD
   exposure at near-full LETF drawdown levels (-52% to -83%). The strategy does not reduce
   drawdown enough relative to CAGR to meet risk-adjusted gates.

Best performer: **QLD + GLD off-leg** (Sharpe_net=0.560, Calmar=0.356, CAGR_net=15.9%, WF=8/8,
OOS=0.457, FWD=0.347, DSR_p=0.137). OOS and FWD both pass — the result is economically real but
statistically insufficient (DSR, Calmar, Sharpe_net gate all fail).

## Cross-ticker table

| Ticker | Best config | Sharpe_net | CAGR_net | MaxDD | WF | OOS_S | FWD_S | DSR_p | Calmar | PASS |
|--------|-------------|-----------|----------|-------|-----|-------|-------|-------|--------|------|
| QLD | mom12mo_gld | 0.560 | 15.9% | -52.4% | 8/8 | 0.457 | 0.347 | 0.137 | 0.356 | ✗ |
| SSO | mom12mo_gld | 0.543 | 13.2% | -59.3% | 8/8 | 0.521 | 0.196 | 0.173 | 0.262 | ✗ |
| TQQQ | mom12mo_gld | 0.532 | 17.4% | -79.3% | 8/8 | 0.447 | 0.305 | 0.202 | 0.259 | ✗ |
| UPRO | mom12mo_gld | 0.485 | 13.7% | -83.1% | 7/8 | 0.480 | 0.147 | 0.294 | 0.194 | ✗ |

*PBO assessed at 144-trial phase level — per-ticker N=3 local PBO is meaningless. `[advances_fin_ml, p.208-211]`*

## Key patterns

1. **QQQ-based > SPY-based:** QLD (2×QQQ) and TQQQ (3×QQQ) both outperform SSO and UPRO in
   Sharpe_net — consistent with QQQ > SPY over the 2004-2026 window. Asset selection matters.
2. **GLD off-leg dominates cash and TLT** for all 4 assets. TLT in 2022 bear worsened drawdowns
   (negative correlation to equities reversed). Cash = 0% yield = pure drag.
3. **2× > 3× on risk-adjusted basis:** QLD (Sharpe_net=0.560, Calmar=0.356) beats TQQQ
   (0.532, 0.259) — additional leverage amplifies volatility and MaxDD more than CAGR. This
   favors the cross-leverage preference rule (spec §7.2 prefers 2× if Calmar(2×) > Calmar(3×)).
4. **Stage 1 / Stage 2 fully concordant (Δ=0.00pp)** for all 3 real-LETF assets (SSO/TQQQ/UPRO).
   Synthetic pre-inception formula validated. `[leverage_for_the_long_run, ch.2]`
5. **Cross-lib concordant (Δ≤2.21pp)** for all 4 tickers. No engine-specific artifact.

## Citations

- `[dual_momentum, ch.6]` — Antonacci 12-month absolute momentum filter
- `[advances_fin_ml, p.208-211]` — PBO/CSCV gate
- `[advances_fin_ml, p.298-299]` — DSR cumulative n_trials
- `[advances_fin_ml, ch.12]` — Walk-forward validation
- `[leverage_for_the_long_run, ch.2]` — Synthetic LETF pre-inception return formula

## Links

- Per-ticker reports: `reports/phase_3_5e/c05_mom12mo_abs_momentum/{QLD,SSO,TQQQ,UPRO}.md`
- Registry: `reports/phase_3_5e/c05_mom12mo_abs_momentum/registry.json`
- Jornada: `jornada/2026-04-21-1644-c05-mom12mo-dead.md`

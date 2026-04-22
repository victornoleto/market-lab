# Phase 3.7 H2.b — Gayed 2x LRS + VIX<25 floor — Honest Validation

**Verdict: FAIL**

- **Config hash:** `6d5951ff26`
- **Git SHA:** `2358c00560`
- **Universe:** SPY (SPX-TR stitched), 2x LETF (synth pre-2009-06 + real UPRO post)
- **Windows:** IS `1990-01-01 → 1999-12-31` (VIX-gated — VIXCLS starts 1990-01-02; pre-1990 trimmed to keep gate active), OOS `2000-01-01 → 2015-12-31`, FWD `2016-01-01 → 2026-04-14`
- **Cost model (rota B Inter, mandate §4.6):** commission=0 + spread=5.0bps/side + LETF ER=0.95% (embedded in synth/real UPRO) + DARF=15% year-end realization + cash_sleeve=4.0%/yr.
- **On-regime fraction (OOS):** 60.97%

## 13-Gate Table

| Gate | Value | Verdict |
|------|-------|---------|
| 1 IS Sharpe > 0.5 | 0.944 | **PASS** |
| 2 OOS Sharpe >= 1.3 | 0.387 | **FAIL** |
| 3 OOS CAGR tier (WARN) | 6.751% — tier **Folclore** | **WARNING-ONLY** |
| 4 OOS MDD tier (WARN) | -48.083% — tier **Warning** | **WARNING-ONLY** |
| 5 FWD Sharpe > 0 | 0.648 | **PASS** |
| 6 WF >= 6/8 positive | 7/8 profitable | **PASS** |
| 7 Median hold >= 5d | 6.0 trading days | **PASS** |
| 8 IR vs SPY >= 0.2 | 0.164 | **FAIL** |
| 9 Cross-lib CAGR <= 3pp (HARD) | pandas(no-tax)=9.425%, vbt=9.426%, |Δ|=0.001pp (compared ex-tax to match vbt scope) | **PASS** |
| 10 Bootstrap 99.9% CI low > 0 (HARD) | OOS=-0.000456618; FULL=0.000130591 | **FAIL** |
| 11 PBO < 0.5 (HARD) | pbo=0.214 | **PASS** |
| 12 DSR p < 0.05 (HARD) | p=0.6379 | **FAIL** |
| 13 Cost×2 Sharpe > 0.8 | 0.278 (cagr=3.890%) | **FAIL** |

## Window summaries

### IS (1990-01-01 → 1999-12-31)
- days=2,528, switches=73, median_hold=6.0d, on_regime=74.37%
- Sharpe(daily)=0.944, CAGR=18.253%, MDD=-26.608%
- Cumulative costs: switches=29.741%, tax=80.982%

### OOS (2000-01-01 → 2015-12-31)
- days=4,025, switches=125, median_hold=4.0d
- Sharpe(daily)=0.387, CAGR=6.751% (tier **Folclore**), MDD=-48.083% (tier **Warning**)
- IR vs SPY buy-hold: 0.164

### FWD (2016-01-01 → 2026-04-14)
- days=2,584, switches=95, median_hold=5.5d
- Sharpe(daily)=0.648, CAGR=16.242%, MDD=-53.809%

## Stress periods breakdown (Sharpe | CAGR | MDD | N)

| Period | N | Sharpe | CAGR | MDD |
|--------|---|--------|------|-----|
| dotcom_2000_2002 | 752 | -0.249 | -1.359% | -13.890% |
| gfc_2007_2009 | 378 | -0.770 | -9.359% | -20.583% |
| euro_2011 | 170 | -1.406 | -36.982% | -27.294% |
| covid_2020_03 | 62 | 0.191 | 1.522% | -13.985% |
| rate_shock_2022 | 251 | -1.879 | -35.861% | -36.953% |

## Walk-forward (8 windows over IS+OOS)
- Profitable: 7 / 8
- Window returns: 79.22%, 82.19%, 34.53%, 17.41%, 43.41%, -17.21%, 31.21%, 95.79%
- Window MDDs: 14.04%, 16.75%, 26.61%, 13.89%, 23.55%, 34.29%, 34.58%, 23.31%

## Data provenance

- SPX-TR pre-2001-05-14: Kenneth French daily factors (`Mkt-RF + RF`)
- SPX-TR post-2001-05-14: Tiingo SPY `adj_close` pct_change
- 2x LETF pre-2009-06-25: `synthesize_letf_returns_ffr_aware(L=2, ER=0.95%)`
- 2x LETF post-2009-06-25: Tiingo UPRO `adj_close` pct_change
- VIX: CBOE VIXCLS (1990-01-02+ via FRED)
- FFR proxy: Kenneth French daily `rf` × 252
- Cash sleeve: flat 4%/yr (mandate §4.6 proxy for long-term 3mo T-bill)

## Notes on pre-1990 IS trim

VIXCLS starts 1990-01-02. We chose to **trim IS to 1990-01-01** rather than use a realized-vol proxy for 1970-1989, because:

1. The VIX gate is a material component of the strategy — replacing    it with a proxy would compromise the signal under evaluation.
2. 1990-2000 still offers 10 years of IS that include the 1990 recession,    1994 bond crash, LTCM/1998, and Fed easing cycles — enough regime    variety for honest IS diagnostics.
3. OOS (2000-2015) and FWD (2016-2026) together give 26 years of strict    out-of-sample evaluation, which is the binding constraint.

## Known limitations

- Single cash rate (4%/yr flat) is a simplification; real cash sleeve would
  track the daily 3mo T-bill curve. This is a second-order effect on the
  long side but slightly understates off-regime returns during high-rate
  periods (2022-2024).
- Year-end DARF is a simple 15% liquidation model; it does NOT model loss   carryforward. A losing year contributes 0 tax; next year's gains pay full   15% even if priors netted negative. Mandate §4.6 rota B explicit.
- UPRO real data has its own tracking error + ER, which is preserved   (we compute returns from `adj_close`). No further ER drag is added in   the post-2009 stitch.

## Citations

- `[leverage_for_the_long_run, p.7-8, p.13, p.17, Table 8]` — canonical 2x LRS
- `[bozovic_2024_irfa]` — VIX regime & LETF drawdowns (2024 SSRN)
- `[advances_fin_ml, p.31-34]` — F2-alignment prev_weight × ret
- `[advances_fin_ml, p.208-211]` — PBO via CSCV
- `[advances_fin_ml, p.275]` — Deflated Sharpe Ratio
- `[docs/investment-mandate.md §2.4]` — 13-gate framework
- `[docs/investment-mandate.md §2.2, §2.3, §7]` — CAGR/MDD tiers warning-only
- `[docs/investment-mandate.md §4.6]` — rota B Inter cost model (DARF 15%)

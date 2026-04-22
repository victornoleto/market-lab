# Phase 3.8 B2 — Gayed MA-robustness sweep — Honest Validation

**Verdict: FAIL** — winner `B2-SMA200-SSO-2x` fails 2/4 hard gates (grid: 16 configs run)

- **Git SHA:** `9a3e24d956`
- **Universe:** SPY (SPX-TR stitched KF+Tiingo), UPRO/SSO synth pre-inception + real post
- **Windows:** IS `1970-01-02 → 1999-12-31`, OOS `2000-01-01 → 2015-12-31`, FWD `2016-01-01 → 2026-04-15`
- **Cost model (rota B Inter, mandate §4.6):** commission=0 + spread=5.0bps/side + LETF ER=0.95% + DARF=15% year-end + cash_sleeve=4.0%/yr
- **Grid:** 2 filters × 4 MA periods × 2 legs = **16 configs**
- **PBO threshold:** < 0.3 (tightened for single-feature 16-config family)

## Grid summary (16 configs, sorted by OOS Sharpe desc)

| Rank | Variant | filter | period | leg | IS Sharpe | OOS Sharpe | OOS CAGR | OOS MDD | FWD Sharpe | n_switches IS/OOS/FWD |
|------|---------|--------|--------|-----|-----------|------------|----------|---------|------------|-----------------------|
| 1 | B2-SMA200-SSO-2x | SMA | 200 | SSO | 0.821 | 0.391 | 6.101% | -37.416% | 0.727 | 137/109/51 |
| 2 | B2-EMA200-SSO-2x | EMA | 200 | SSO | 0.829 | 0.379 | 5.862% | -41.228% | 0.575 | 149/107/79 |
| 3 | B2-SMA200-UPRO-3x | SMA | 200 | UPRO | 0.758 | 0.371 | 6.856% | -51.202% | 0.710 | 137/109/51 |
| 4 | B2-EMA200-UPRO-3x | EMA | 200 | UPRO | 0.767 | 0.361 | 6.543% | -58.018% | 0.560 | 149/107/79 |
| 5 | B2-EMA150-SSO-2x | EMA | 150 | SSO | 0.860 | 0.298 | 4.092% | -48.821% | 0.501 | 201/167/93 |
| 6 | B2-SMA150-SSO-2x | SMA | 150 | SSO | 0.825 | 0.296 | 4.041% | -40.497% | 0.632 | 209/171/65 |
| 7 | B2-EMA150-UPRO-3x | EMA | 150 | UPRO | 0.798 | 0.279 | 3.888% | -65.114% | 0.489 | 201/167/93 |
| 8 | B2-SMA150-UPRO-3x | SMA | 150 | UPRO | 0.762 | 0.269 | 3.555% | -57.349% | 0.618 | 209/171/65 |
| 9 | B2-EMA100-SSO-2x | EMA | 100 | SSO | 0.935 | 0.266 | 3.427% | -48.226% | 0.662 | 283/205/101 |
| 10 | B2-EMA100-UPRO-3x | EMA | 100 | UPRO | 0.876 | 0.243 | 2.670% | -65.082% | 0.649 | 283/205/101 |
| 11 | B2-SMA100-SSO-2x | SMA | 100 | SSO | 0.786 | 0.232 | 2.698% | -56.716% | 0.732 | 313/201/85 |
| 12 | B2-EMA125-SSO-2x | EMA | 125 | SSO | 0.910 | 0.225 | 2.551% | -52.809% | 0.677 | 231/193/91 |
| 13 | B2-SMA100-UPRO-3x | SMA | 100 | UPRO | 0.724 | 0.213 | 1.673% | -73.634% | 0.719 | 313/201/85 |
| 14 | B2-EMA125-UPRO-3x | EMA | 125 | UPRO | 0.848 | 0.206 | 1.485% | -69.372% | 0.669 | 231/193/91 |
| 15 | B2-SMA125-SSO-2x | SMA | 125 | SSO | 0.832 | 0.073 | -0.689% | -63.904% | 0.606 | 249/203/83 |
| 16 | B2-SMA125-UPRO-3x | SMA | 125 | UPRO | 0.770 | 0.052 | -3.314% | -82.504% | 0.597 | 249/203/83 |

## Winner — B2-SMA200-SSO-2x — FAIL

- **Config hash:** `cede13392e`
- **Turnover:** ~5.3 trades/yr (OK)
- **OOS on-regime fraction:** 63.90%
- **Config:** filter=SMA, ma_period=200, leg=SSO, leverage=2.0x

### 13-Gate Table

| Gate | Value | Verdict |
|------|-------|---------|
| 1 IS Sharpe > 0.5 | 0.821 | **PASS** |
| 2 OOS Sharpe >= 1.3 | 0.391 | **FAIL** |
| 3 OOS CAGR tier (WARN) | 6.101% — tier **Folclore** | **WARNING-ONLY** |
| 4 OOS MDD tier (WARN) | -37.416% — tier **Warning** | **WARNING-ONLY** |
| 5 FWD Sharpe > 0 | 0.727 | **PASS** |
| 6 WF >= 6/8 positive | 8/8 profitable | **PASS** |
| 7 Median hold >= 5d | 16.0 trading days | **PASS** |
| 8 IR vs SPY >= 0.2 | 0.112 | **FAIL** |
| 9 Cross-lib CAGR <= 3pp (HARD) | pandas(no-tax)=8.190%, vbt=8.190%, |Δ|=0.000pp (compared ex-tax to match vbt scope) | **PASS** |
| 10 Bootstrap 99.9% CI low > 0 (HARD) | OOS=-0.000297392; FULL=0.000250218 | **FAIL** |
| 11 PBO < 0.3 (HARD, 16-config family) | pbo=0.298 | **PASS** |
| 12 DSR p < 0.05 (HARD) | p=0.5929 | **FAIL** |
| 13 Cost×2 Sharpe > 0.8 | 0.286 (cagr=3.850%) | **FAIL** |

### Window summaries (winner)

#### IS (1970-01-02 → 1999-12-31)
- days=7,582, switches=137, median_hold=16.0d, on_regime=75.44%
- Sharpe(daily)=0.821, CAGR=16.301%, MDD=-33.570%
- Cumulative: switches=6.850%, tax=1764.942%

#### OOS (2000-01-01 → 2015-12-31)
- days=4,025, switches=109, median_hold=4.0d
- Sharpe(daily)=0.391, CAGR=6.101% (tier **Folclore**), MDD=-37.416% (tier **Warning**)
- IR vs SPY buy-hold: 0.112

#### FWD (2016-01-01 → 2026-04-15)
- days=2,585, switches=51, median_hold=4.0d
- Sharpe(daily)=0.727, CAGR=15.206%, MDD=-39.072%

### Stress periods (winner)

| Period | N | Sharpe | CAGR | MDD |
|--------|---|--------|------|-----|
| dotcom_2000_2002 | 752 | -0.215 | -1.188% | -13.586% |
| gfc_2007_2009 | 378 | -0.970 | -11.737% | -23.566% |
| euro_2011 | 170 | -2.185 | -40.842% | -30.332% |
| covid_2020_03 | 62 | -3.406 | -68.843% | -32.389% |
| rate_shock_2022 | 251 | -1.841 | -26.394% | -27.280% |

### Walk-forward (8 windows over IS+OOS, winner)
- Profitable: 8 / 8
- Window returns: 87.06%, 72.67%, 270.03%, 69.11%, 206.96%, 108.25%, 22.97%, 55.50%
- Window MDDs: 27.90%, 33.57%, 22.72%, 32.54%, 26.53%, 22.41%, 35.18%, 37.42%

## Data provenance

- SPX-TR pre-2001-05-14: Kenneth French daily factors (`Mkt-RF + RF`)
- SPX-TR post-2001-05-14: Tiingo SPY `adj_close` pct_change
- UPRO-3x pre-2009-06-25: `synthesize_letf_returns_ffr_aware(L=3, ER=0.95%)`
- UPRO-3x post-2009-06-25: Tiingo UPRO `adj_close` pct_change
- SSO-2x pre-2006-06-21: `synthesize_letf_returns_ffr_aware(L=2, ER=0.95%)`
- SSO-2x post-2006-06-21: Tiingo SSO `adj_close` pct_change
- FFR proxy: Kenneth French daily `rf` × 252
- Cash sleeve: flat 4%/yr (mandate §4.6 proxy)

## Known limitations

- Single cash rate (4%/yr flat) is a simplification.
- Year-end DARF model: 15% on year's **net** gain; loss-carry NOT modelled.
- Real LETF post-inception pct_change used as-is (no added ER drag).
- EMA is not a Gayed-tested kernel; it is a prompt-defined extension
  over SMA for low-lag comparison `[cycle_analytics, p.9-10, ch.1-2]`.

## Citations

- `[leverage_for_the_long_run, p.14, Table 6]` — MA 10-200d robustness
- `[leverage_for_the_long_run, p.16]` — SMA-200 ~5 trades/yr; ER 0.95%
- `[leverage_for_the_long_run, p.17, Table 8]` — LRS 2x/3x CAGR/Sharpe
- `[leverage_for_the_long_run, p.202]` (summary ch.) — turnover vs MA
- `[cycle_analytics, p.9-10, ch.1-2]` — EMA IIR recursion
- `[advances_fin_ml, p.31-34]` — F2-alignment prev_weight × ret
- `[advances_fin_ml, p.208-211]` — PBO via CSCV
- `[advances_fin_ml, p.275]` — Deflated Sharpe Ratio
- `docs/investment-mandate.md §2.4, §2.2, §2.3, §4.6`
- `docs/plans/2026-04-22-phase3.8-1-plano-b-hunt-prompt.md §B2`

# Phase 3.8 B5 — Faber 10-mo GTAA single-asset SPY — Honest Validation

**Verdict: FAIL** — winner candidate `B5-monthly-SMA10mo` fails 2/4 hard gates (CAGR tier **Folclore**)

- **Git SHA:** `f69b468d36`
- **Universe:** SPY stitched (Ken French market TR pre-2001-05-14 + Tiingo SPY `adj_close` post), UNLEVERAGED
- **Windows:** IS `1970-01-02 → 1999-12-31`, OOS `2000-01-01 → 2015-12-31`, FWD `2016-01-01 → 2026-04-15`
- **Cost model (rota B Inter, mandate §4.6):** commission=0 + spread=5.0bps/switch + DARF=15% year-end + cash_sleeve=4.0%/yr (SPY ER already embedded in adj_close)
- **Grid:** 4 configs (V1 monthly SMA-10mo Faber canon, V2 monthly SMA-6mo, V3 monthly SMA-12mo, V4 daily SMA-210d Gayed cousin)
- **Winner selection:** highest OOS Sharpe; hard-gate pack run on winner only

## Grid stats (all 4 variants, lite pass)

| Variant | Config hash | IS Sharpe | OOS Sharpe | OOS CAGR | OOS CAGR tier | OOS MDD | Trades/yr |
|---------|-------------|-----------|------------|----------|---------------|---------|-----------|
| `B5-monthly-SMA10mo` | `e2959fda33` | 0.753 | 0.613 | 6.630% | **Folclore** | -18.394% | 1.39 |
| `B5-monthly-SMA6mo` | `a289a8cb7d` | 0.755 | 0.574 | 6.070% | **Folclore** | -16.737% | 2.17 |
| `B5-monthly-SMA12mo` | `b6b9ed3db8` | 0.804 | 0.605 | 6.455% | **Folclore** | -18.394% | 1.12 |
| `B5-daily-SMA210d` | `aa4b5e10d5` | 1.118 | 0.452 | 4.196% | **Folclore** | -19.613% | 5.03 |

## Winner — B5-monthly-SMA10mo — FAIL

- **Config hash:** `e2959fda33`
- **Turnover:** ~1.39 trades/yr
- **OOS on-regime fraction:** 64.75%

### 13-Gate Table

| Gate | Value | Verdict |
|------|-------|---------|
| 1 IS Sharpe > 0.5 | 0.753 | **PASS** |
| 2 OOS Sharpe >= 1.3 | 0.613 | **FAIL** |
| 3 OOS CAGR tier (WARN) | 6.630% — tier **Folclore** | **WARNING-ONLY** |
| 4 OOS MDD tier (WARN) | -18.394% — tier **Válido** | **WARNING-ONLY** |
| 5 FWD Sharpe > 0 | 0.747 | **PASS** |
| 6 WF >= 6/8 positive | 8/8 profitable | **PASS** |
| 7 Median hold >= 5d | 211.0 trading days | **PASS** |
| 8 IR vs SPY >= 0.2 | 0.079 | **FAIL** |
| 9 Cross-lib CAGR <= 3pp (HARD) | pandas(no-tax)=8.016%, vbt=8.016%, |Δ|=0.000pp (compared ex-tax/ex-cost to match vbt scope) | **PASS** |
| 10 Bootstrap 99.9% CI low > 0 (HARD) | OOS=-4.49885e-05; FULL=0.000146336 | **FAIL** |
| 11 PBO < 0.3 (HARD) | pbo=0.155 | **PASS** |
| 12 DSR p < 0.05 (HARD) | p=0.0835 | **FAIL** |
| 13 Cost×2 Sharpe > 1.0 (unleveraged) | 0.482 (cagr=5.149%) | **FAIL** |

### Window summaries

#### IS (1970-01-02 → 1999-12-31)
- days=7,582, switches=43, median_hold=211.0d, on_regime=74.74%
- Sharpe(daily)=0.753, CAGR=8.599%, MDD=-32.304%
- Cumulative: switches=2.150%, tax=219.275%

#### OOS (2000-01-01 → 2015-12-31)
- days=4,025, switches=15, median_hold=241.5d
- Sharpe(daily)=0.613, CAGR=6.630% (tier **Folclore**), MDD=-18.394% (tier **Válido**)
- IR vs SPY buy-hold: 0.079

#### FWD (2016-01-01 → 2026-04-15)
- days=2,585, switches=20, median_hold=179.5d
- Sharpe(daily)=0.747, CAGR=10.807%, MDD=-33.700%

### Stress periods (Sharpe | CAGR | MDD | N)

| Period | N | Sharpe | CAGR | MDD |
|--------|---|--------|------|-----|
| dotcom_2000_2002 | 752 | 0.897 | 3.374% | -3.737% |
| gfc_2007_2009 | 378 | -0.499 | -5.134% | -16.640% |
| euro_2011 | 170 | -0.893 | -18.991% | -17.182% |
| covid_2020_03 | 62 | -1.204 | -55.206% | -33.700% |
| rate_shock_2022 | 251 | -0.207 | -3.891% | -12.866% |

### Walk-forward (8 windows over IS+OOS)
- Profitable: 8 / 8
- Window returns: 23.53%, 61.32%, 98.15%, 18.29%, 109.72%, 62.13%, 48.11%, 40.28%
- Window MDDs: 22.90%, 18.66%, 18.16%, 32.30%, 20.77%, 11.33%, 16.64%, 18.39%

## Data provenance

- SPX-TR pre-2001-05-14: Kenneth French daily factors (`Mkt-RF + RF`)
- SPY post-2001-05-14: Tiingo SPY `adj_close` pct_change
- Cash sleeve: flat 4%/yr (mandate §4.6 proxy for long-term 3-mo T-bill)

## Known limitations

- Single cash rate (4%/yr flat) is a simplification; real cash sleeve would
  track the daily 3-mo T-bill curve. Second-order effect.
- Year-end DARF model: 15% on year's **net** gain; loss-carry NOT
  modelled (conservative per mandate §4.6 rota B).
- Pre-2001-05 SPY is a KF SPX-TR proxy, not a physical SPY series —
  acceptable for a daily total-return regime signal (the 2001-05 seam
  is continuous to O(bp)).
- B5 is unleveraged by construction → CAGR ceiling is SPY buy-hold
  minus cash-sleeve drag during off-regime periods. Tier 'Válido'
  (17-25%) is physically unreachable without leverage; the escalation
  rule is 'hard-gates technically pass + tier Folclore → FOLCLORE_PASS.md'.

## Citations

- `[phase3_7_literature_sprint §T3]` — Faber 2007 canonical
- `[trading_evolved, p.211-212]` — 10-month SMA filter + caveat
- `[leverage_for_the_long_run, p.13-14]` — SMA-200 daily ≈ 10-mo monthly
- `[advances_fin_ml, p.31-34]` — F2-alignment prev_weight × ret
- `[advances_fin_ml, p.208-211]` — PBO via CSCV
- `[advances_fin_ml, p.275]` — Deflated Sharpe Ratio
- `docs/investment-mandate.md §2.4` — 13-gate framework
- `docs/investment-mandate.md §2.2, §2.3, §7` — CAGR/MDD tiers warning-only
- `docs/investment-mandate.md §4.6` — rota B Inter cost model (DARF 15%)

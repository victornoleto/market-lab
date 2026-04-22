# Phase 3.8 B4 — Hsieh-Chang-Chen AR(1) regime LETF rotation — Honest Validation

**Verdict: FAIL** — winner config `B4-SSO-2x-L126` fails 2/4 hard gates; total fails tallied in table below.

- **Git SHA:** `14f58d7d8b`
- **Grid:** 8 configs (2 legs {UPRO-3x, SSO-2x} × 4 AR(1) lookbacks {42, 63, 84, 126})
- **Winner selection:** OOS Sharpe across grid; winner evaluated against 13 gates
- **Winner config hash:** `54e7b22cad`
- **Universe:** SPX-TR stitched (KF pre-2001-05-14 + Tiingo SPY), LETF synth pre-inception + real post
- **Windows:** IS `1970-01-02 → 1999-12-31`, OOS `2000-01-01 → 2015-12-31`, FWD `2016-01-01 → 2026-04-15`
- **Cost model (rota B Inter, mandate §4.6):** commission=0 + spread=5.0bps/side + LETF ER=0.95% + DARF=15% year-end + cash_sleeve=4.0%/yr

## Grid sweep — OOS Sharpe ranking

| Variant | AR(1) lookback | Leverage | OOS Sharpe |
|---------|----------------|----------|------------|
| B4-SSO-2x-L126 | 126 | 2x | 0.493 |
| B4-UPRO-3x-L126 | 126 | 3x | 0.452 |
| B4-SSO-2x-L84 | 84 | 2x | 0.335 |
| B4-SSO-2x-L63 | 63 | 2x | 0.333 |
| B4-UPRO-3x-L63 | 63 | 3x | 0.303 |
| B4-UPRO-3x-L84 | 84 | 3x | 0.295 |
| B4-SSO-2x-L42 | 42 | 2x | -0.013 |
| B4-UPRO-3x-L42 | 42 | 3x | -0.044 |

**Winner selected:** `B4-SSO-2x-L126` (OOS Sharpe 0.493)

## Winner — `B4-SSO-2x-L126` — FAIL

- **Turnover:** ~6.8 trades/yr (within 25/yr budget)
- **OOS on-regime fraction:** 30.56%

### 13-Gate Table

| Gate | Value | Verdict |
|------|-------|---------|
| 1 IS Sharpe > 0.5 | 0.529 | **PASS** |
| 2 OOS Sharpe >= 1.3 | 0.493 | **FAIL** |
| 3 OOS CAGR tier (WARN) | 7.683% — tier **Folclore** | **WARNING-ONLY** |
| 4 OOS MDD tier (WARN) | -35.353% — tier **Warning** | **WARNING-ONLY** |
| 5 FWD Sharpe > 0 | 0.439 | **PASS** |
| 6 WF >= 6/8 positive | 7/8 profitable | **PASS** |
| 7 Median hold >= 5d | 5.0 trading days | **PASS** |
| 8 IR vs SPY >= 0.2 | 0.164 | **FAIL** |
| 9 Cross-lib CAGR <= 3pp (HARD) | pandas(no-tax)=9.954%, vbt=9.954%, |Δ|=0.000pp (compared ex-tax to match vbt scope) | **PASS** |
| 10 Bootstrap 99.9% CI low > 0 (HARD) | OOS=-0.00012374; FULL=5.20882e-05 | **FAIL** |
| 11 PBO < 0.3 (HARD, single-feature) | pbo=0.183 | **PASS** |
| 12 DSR p < 0.05 (HARD) | p=0.3038 | **FAIL** |
| 13 Cost×2 Sharpe > 0.8 | 0.373 (cagr=5.383%) | **FAIL** |

### Window summaries

#### IS (1970-01-02 → 1999-12-31)
- days=7,582, switches=109, median_hold=5.0d, on_regime=91.14%
- Sharpe(daily)=0.529, CAGR=11.025%, MDD=-78.941%
- Cumulative: switches=5.450%, tax=500.251%

#### OOS (2000-01-01 → 2015-12-31)
- days=4,025, switches=155, median_hold=5.0d
- Sharpe(daily)=0.493, CAGR=7.683% (tier **Folclore**), MDD=-35.353% (tier **Warning**)
- IR vs SPY buy-hold: 0.164

#### FWD (2016-01-01 → 2026-04-15)
- days=2,585, switches=116, median_hold=4.0d
- Sharpe(daily)=0.439, CAGR=6.917%, MDD=-26.493%

### Stress periods (Sharpe | CAGR | MDD | N)

| Period | N | Sharpe | CAGR | MDD |
|--------|---|--------|------|-----|
| dotcom_2000_2002 | 752 | 0.100 | -1.899% | -35.353% |
| gfc_2007_2009 | 378 | 4.659 | 3.254% | -0.586% |
| euro_2011 | 170 | -0.657 | -14.139% | -21.785% |
| covid_2020_03 | 62 | -0.540 | -21.508% | -15.405% |
| rate_shock_2022 | 251 | -0.011 | -7.381% | -23.640% |

### Walk-forward (8 windows over IS+OOS)
- Profitable: 7 / 8
- Window returns: -1.23%, 132.77%, 173.89%, 10.38%, 138.64%, 45.76%, 38.25%, 127.93%
- Window MDDs: 78.94%, 35.46%, 46.30%, 59.57%, 43.46%, 35.35%, 14.18%, 21.78%

## Data provenance

- SPX-TR pre-2001-05-14: Kenneth French daily factors (`Mkt-RF + RF`)
- SPX-TR post-2001-05-14: Tiingo SPY `adj_close` pct_change
- UPRO-3x pre-2009-06-25: `synthesize_letf_returns_ffr_aware(L=3, ER=0.95%)`
- UPRO-3x post-2009-06-25: Tiingo UPRO `adj_close` pct_change
- SSO-2x pre-2006-06-21: `synthesize_letf_returns_ffr_aware(L=2, ER=0.95%)`
- SSO-2x post-2006-06-21: Tiingo SSO `adj_close` pct_change
- FFR proxy: Kenneth French daily `rf` × 252
- Cash sleeve: flat 4%/yr (mandate §4.6)

## Structural interpretation

Winner FAILs: 2 OOS Sharpe >= 1.3; 8 IR vs SPY >= 0.2; 10 Bootstrap 99.9% CI low > 0 (HARD); 12 DSR p < 0.05 (HARD); 13 Cost×2 Sharpe > 0.8. Turnover within budget — primary failure is signal quality (Sharpe/bootstrap CI), not cost overhead.

## Known limitations

- AR(1) signal uses sign-only regime gating (0/1). Scaling on β magnitude is a future extension not tested here (paper leaves as open).
- Synth LETF has ±5pp tracking-error band in 2020 validation — material on long IS window but bounded. Inherited from B1.
- Year-end DARF model: 15% on yearly net gain; loss-carry NOT modelled (conservative per mandate §4.6).
- Cash sleeve flat 4%/yr — simplification vs daily 3mo T-bill.

## Citations

- `[phase3_7_literature_sprint §T1, arXiv 2504.20116]` — Hsieh-Chang-Chen 2025 AR(1) regime thesis
- `[leverage_for_the_long_run, p.4, p.7-8]` — AR(1) > 0 as statistical signature of trending market (Gayed framing)
- `[advances_fin_ml, p.31-34]` — F2-alignment prev_weight × ret
- `[advances_fin_ml, p.208-211]` — PBO via CSCV
- `[advances_fin_ml, p.275]` — Deflated Sharpe Ratio
- `[docs/investment-mandate.md §2.4]` — 13-gate framework
- `[docs/investment-mandate.md §2.2, §2.3, §7]` — CAGR/MDD tiers warning-only
- `[docs/investment-mandate.md §4.6]` — rota B Inter cost model (DARF 15%)

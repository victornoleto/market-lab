# Phase 3.7 H1.c — Maróy 2024 Ladder — Honest Validation

**Verdict: FAIL**

- **Config hash:** `7490275517`
- **Git SHA:** `32b6128f73`
- **Universe:** SPY (primary), QQQ (cross-asset)
- **Windows:** IS 2017-06-01 → 2021-12-31 | OOS 2022-01-01 → 2024-12-31 | FWD 2025-01-01 → 2026-04-14
- **Cost model (mandate §2.4 / §4.8 no-DARF):** spread 0.67bps/side paid per weight-change (captures Ladder's 4-flip drag), commission 0, swap 0 intraday, tax 0.

## 13-Gate Table

| Gate | Value | Verdict |
|------|-------|---------|
| 1 IS Sharpe > 0.5 | -2.606 | **FAIL** |
| 2 OOS Sharpe >= 1.3 | -1.668 | **FAIL** |
| 3 OOS CAGR tier (WARN) | -13.938% — Folclore | **WARNING-ONLY** |
| 4 OOS MDD tier (WARN) | -38.197% — Válido | **WARNING-ONLY** |
| 5 FWD Sharpe > 0 | -1.138 | **FAIL** |
| 6 WF >= 6/8 positive | 0/8 profitable | **FAIL** |
| 7 Median hold >= 1h | 7.0 min | **FAIL** |
| 8 IR vs SPY >= 0.2 | -1.166 | **FAIL** |
| 9 Cross-lib CAGR <= 3pp (HARD) | pandas_cagr=-13.582%, vbt_cagr=-13.610%, |Δ|=0.03pp — simplified control only (single-TP), ladder-proper cross-lib is a KNOWN LIMITATION | **PASS** |
| 10 Bootstrap 99.9% CI low > 0 (HARD) | OOS=-0.00115077; FULL=-0.00107735 | **FAIL** |
| 11 PBO single-feature < 0.3 (HARD) | pbo=0.000 | **PASS** |
| 12 DSR p < 0.05 (HARD) | p=1.0000 | **FAIL** |
| 13 Cost×2 Sharpe > 1.0 | -4.663 (cagr=-31.742%) | **FAIL** |

## Window Summaries

### SPY IS
- bars=454,900, entries=7767, median_hold=7.0 min
- tp1=7300, tp2=6915, tp3=1595, trailing=5314, eod=858
- Sharpe(daily)=-2.606, CAGR=-21.635%, MDD=-67.855%
- Cum spread drag: 104.078%

### SPY OOS
- bars=295,954, entries=5217, median_hold=9.0 min
- tp1=4943, tp2=4631, tp3=600, trailing=4027, eod=590
- Sharpe(daily)=-1.668, CAGR=-13.938% (tier **Folclore**), MDD=-38.197% (tier **Válido**)
- IR vs SPY buy-hold: -1.166

### SPY FWD
- bars=126,520, entries=1864
- Sharpe(daily)=-1.138, CAGR=-10.985%, MDD=-17.865%

### QQQ OOS (cross-asset)
- entries=5026, Sharpe(daily)=-0.618, CAGR=-7.480%, MDD=-32.888%

## Cost treatment (Ladder-specific)

The Maróy Ladder generates up to **4 weight changes per round-trip** (entry + TP1 + TP2 + TP3 / trailing). We apply spread cost on **each** weight change in the `prev_weight × ret` pipeline — this is strictly more punitive than a single-TP or trail-only exit and is the honest way to capture the Ladder's structural cost. Cumulative spread drag on IS alone: **104.078%**.

## Known limitations

- **Cross-lib gate (#9) is evaluated on a SIMPLIFIED control (single-TP at 1×ATR + EOD flat)** rather than the full Ladder. vectorbt's `Portfolio.from_signals` does not accept variable-fraction exit schedules per trade. A faithful vbt Ladder would require manual iteration that mirrors the pandas reference, defeating the purpose of cross-lib validation. The simplified control shares entry logic and F2-alignment with the Ladder, so it is a valid sanity check on signal+plumbing — but **NOT** a full Ladder cross-lib match. This is disclosed honestly per mandate §2.4.
- Tick-data realism: parquet is Tiingo 1-min bars; intra-bar TP hits use bar `high`/`low`, which can overstate realism vs continuous tick. Maróy 2024 and Zarattini 2024 use the same convention; this is consistent with the literature but known to be optimistic.

## Citations

- `[paper.zarattini_2024_intraday_spy, §3]` — noise boundary signal
- `[paper.maroy_2024_intraday_improvements, §Ladder]` — 3-level TP ladder exit
- `[advances_fin_ml, p.31-34]` — F2-alignment lookahead audit
- `[advances_fin_ml, p.208-211]` — PBO via CSCV
- `[advances_fin_ml, p.275]` — Deflated Sharpe Ratio
- `[docs/investment-mandate.md §2.4]` — 13-gate framework
- `[docs/investment-mandate.md §2.2, §2.3, §7]` — CAGR/MDD tiers warning-only
- `[docs/investment-mandate.md §4.8]` — Pepperstone no-DARF

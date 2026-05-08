# Iter 043 — Final Report — `F1-TLT-variation`

**Verdict (NEW SPY-only mandate, 2026-04-29 reframing)**: **WINNER 90/100** — `winner_conditions_met=True`.

**Verdict (LEGACY avg(SPY,VT) + 0.10)**: **WINNER 95/100** — `winner_conditions_met=True`.

**Primary citation**: [risk_parity, ch.5, p.10]

---

## Selected config: `f1_split_baseline`

Weights:

```json
{
  "NTSXSIM": 0.25,
  "GDESIM": 0.25,
  "KMLMSIM": 0.175,
  "DBMFSIM": 0.175,
  "TLTSIM": 0.15
}
```

## Per-dataset metrics (gross-of-tax)

| dataset | Sharpe | CAGR | MDD | gates | DSR p |
|---|---:|---:|---:|---:|---:|
| **lh_56y** | 1.000 | 10.10% | 19.91% | 7/7 | 2.58e-05 |
| **vt_real** | 1.026 | 10.51% | 18.35% | 7/7 | 5.50e-04 |
| **ndx_real** | 1.176 | 11.26% | 14.62% | 7/7 | 1.50e-04 |

## Configs grid (Sharpe per config × dataset)

| config | lh_56y | vt_real | ndx_real |
|---|---:|---:|---:|
| f1_split_baseline | 1.000 | 1.026 | 1.176 |
| f1_no_tlt_to_equity | 0.897 | 0.955 | 1.125 |
| f1_no_tlt_to_mf | 0.962 | 0.989 | 1.127 |
| f1_rssb_replaces_tlt | 0.874 | 0.908 | 1.082 |

## NEW SPY-only Sharpe edge

| dataset | bench (SPY) | hurdle (+0.05) | candidate | edge | passes? |
|---|---:|---:|---:|---:|:-:|
| lh_56y | 0.680 | 0.730 | 1.000 | +0.320 | [OK] |
| vt_real | 0.900 | 0.950 | 1.026 | +0.126 | [OK] |
| ndx_real | 0.900 | 0.950 | 1.176 | +0.276 | [OK] |

## Robustness (5y rolling Sharpe, anchor dataset)

- bonus_pts: 5/5
- pct_positive_sharpe: 100.00%
- n_windows: 22
- anchor_dataset: lh_56y

## INCOMPLETE flags

(Document any synth caveats here per spec §Synth formulas reference.)

## TLT-slot variation analysis (Phase 3B)

Test question: does removing or replacing the TLT 15% sleeve in F1+SPLIT improve
the portfolio? Three alternatives swept against baseline.

### Comparison table — means across 3 datasets

| config | mean Sharpe | mean CAGR | mean MDD | Δ Sharpe vs base | Δ CAGR vs base | Δ MDD vs base |
|---|---:|---:|---:|---:|---:|---:|
| **f1_split_baseline** (TLT 15%) | **1.067** | 10.62% | 17.63% | (baseline) | (baseline) | (baseline) |
| f1_no_tlt_to_equity (NTSX/GDE +7.5 each) | 0.992 | 12.30% | 24.84% | −0.075 | **+1.68pp** | **+7.22pp** |
| f1_no_tlt_to_mf (KMLM/DBMF 25 each) | 1.026 | 10.68% | 17.76% | −0.041 | +0.06pp | +0.13pp |
| f1_rssb_replaces_tlt (RSSB 15%) | 0.955 | 11.44% | 24.91% | −0.112 | +0.82pp | +7.28pp |

### Per-dataset Sharpe trade-off

Baseline `f1_split_baseline` wins Sharpe on **all 3/3 datasets** vs every alternative.
Per-dataset MDD shows baseline wins on lh_56y and ndx_real; f1_no_tlt_to_mf
ties baseline marginally on lh_56y (19.71% vs 19.91%) but loses on the other two.

| config | lh_56y MDD | vt_real MDD | ndx_real MDD |
|---|---:|---:|---:|
| f1_split_baseline | 19.91% | 18.35% | 14.62% |
| f1_no_tlt_to_equity | 28.14% | 26.55% | 19.84% |
| f1_no_tlt_to_mf | 19.71% | 18.57% | 15.01% |
| f1_rssb_replaces_tlt | 28.36% | 26.87% | 19.49% |

### Per-config trade-off interpretation

1. **f1_no_tlt_to_equity (NTSX/GDE +7.5 each)** — equity-heavy. Trades duration
   for stacked-equity exposure. CAGR boost is real (+1.68pp) but MDD blows out
   +7.22pp (lh_56y goes from 19.91% to 28.14%, an extra 8pp drawdown). Sharpe
   degrades −0.075. Canonical "more equity = more compounding, bigger crashes"
   outcome. KILL #6 (CAGR > +0.5pp AND MDD ≤ +5pp): **fails** MDD constraint
   (+7.22pp > +5pp). [risk_parity, ch.5] — duration is a diversifier; removing
   it costs more than it gains here.

2. **f1_no_tlt_to_mf (KMLM/DBMF 25 each)** — replaces duration with crisis-alpha.
   Nearly identical to baseline on all metrics: Sharpe −0.041, CAGR +0.06pp,
   MDD +0.13pp. The MF sleeve genuinely substitutes for TLT's drawdown
   protection but doesn't deliver a CAGR uplift. Conclusion: trend-MF and TLT
   cover similar protective ground; doubling MF doesn't unlock new
   diversification. [ilmanen_expected_returns, ch.19] — MF crisis-alpha is
   complementary not redundant to duration, but at 35% MF the marginal benefit
   is exhausted. **Deploy-equivalent fallback** if real-money MF AUM
   concentration becomes a concern, but not an improvement.

3. **f1_rssb_replaces_tlt (RSSB 15%)** — adds equity AND keeps bonds via
   stacking. Surprising loser: Sharpe −0.112 (worst of the four), MDD +7.28pp
   (effectively as bad as no_tlt_to_equity). Why? RSSB stacks 100% global stocks
   + 100% Treasury inside one ticker, so the 15% slot becomes 30% effective
   exposure (15% equity + 15% bonds). The added equity dominates in drawdowns
   because NTSX+GDE already provide bond hedge — the RSSB Treasury leg is
   correlated with the existing 30% bond exposure (15% NTSX bonds + 15% TLT).
   Replacing pure-bond TLT with stocks-overlaid bonds (RSSB) reduces effective
   duration variance contribution AND adds equity beta. KILL #6 fails on MDD
   (+7.28pp > +5pp).

### Final recommendation: **keep f1_split_baseline (F1+SPLIT)**

The F1+SPLIT recommendation from FINAL_REPORT_seven_portfolios.md
(NTSX 25 + GDE 25 + KMLM 17.5 + DBMF 17.5 + TLT 15) **wins on Sharpe across
all 3 datasets and the joint Sharpe/MDD frontier across all 3 alternatives
tested**. No TLT-slot variation passes KILL #6 (CAGR > +0.5pp AND MDD ≤ +5pp
on ≥2/3 datasets).

User question — *"does the data support removing TLT?"* — **answer: no**.
Two of three TLT alternatives boost CAGR (+0.82pp to +1.68pp) but the MDD
cost (+7.22pp to +7.28pp) is disproportionate, and Sharpe degrades in all
three. The near-baseline alternative (f1_no_tlt_to_mf) is ≈ identical to
baseline (Sharpe −0.04, CAGR +0.06pp, MDD +0.13pp); deploy-equivalent
fallback only.

KILL #1 status: **FIRED** — no alternative beats baseline mean Sharpe on
≥1/3 datasets (baseline wins Sharpe 3/3).

User-decision-relevant insight: **equity > bonds for accumulation IS a robust
prior, but in a stacked-ETF portfolio (NTSX+GDE) equity exposure is already
amplified — an additional 15% to pure bonds is the cheapest drawdown insurance
that doesn't sacrifice Sharpe**. RSSB doesn't help because the 60/40 frontier
is saturated by NTSX+GDE; the RSSB Treasury leg is redundant with NTSX bonds.

## Lesson

In a portfolio that already contains levered equity-plus-bonds stacks
(NTSX 25 + GDE 25 = 45% equity-stack with embedded ~30% bond exposure), the
dedicated 15% TLT sleeve is not redundant — it's the cheapest marginal
drawdown insurance available. Removing it for more equity (no_tlt_to_equity)
or for stacked-equity-plus-bonds (RSSB) trades 1.0-1.7pp CAGR for 7+pp MDD;
removing it for more MF (no_tlt_to_mf) is a wash. The F1+SPLIT recommendation
stands. [risk_parity, ch.5, p.10] — duration is a diversifier; pure bonds
diversify better than overlaid bonds in this construction.

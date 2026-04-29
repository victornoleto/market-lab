# Iter 043 — F1-TLT-variation: TLT slot sensitivity on F1+SPLIT base (Phase 3B)

## Hypothesis (one paragraph)

User accepted F1+SPLIT recommendation (NTSX 25 + GDE 25 + KMLM 17.5 + DBMF 17.5
+ TLT 15) but raised the question: TLT 15% reduces drawdown but eats into
capital accumulation (equity > bonds for long-term return). Test 3 alternatives
to TLT 15%: (B) remove TLT + redistribute to equity stacks; (C) replace TLT
with RSSB stocks+bonds stacked (more equity exposure WHILE keeping bonds via
derivatives); (D) remove TLT + redistribute to MF (more crisis-alpha replacing
duration hedge). Determine if any TLT alternative beats F1+SPLIT baseline on
mean Sharpe / MDD / CAGR.

## Primary citation

[risk_parity, ch.5, p.10] Carlson cap-efficient stacking; [ilmanen_expected_returns, ch.19]
duration-vs-MF crisis-alpha trade-off; ReSolve/Newfound RSSB methodology (2023).

## Configs (4)

| config | NTSX | GDE | KMLM | DBMF | TLT | RSSB | rationale |
|---|---:|---:|---:|---:|---:|---:|---|
| f1_split_baseline | 25% | 25% | 17.5% | 17.5% | 15% | 0% | F1+SPLIT current recommendation |
| f1_no_tlt_to_equity | 32.5% | 32.5% | 17.5% | 17.5% | 0% | 0% | TLT removed, +7.5% to NTSX +7.5% to GDE; tests if more equity stacking beats duration |
| f1_rssb_replaces_tlt | 25% | 25% | 17.5% | 17.5% | 0% | 15% | RSSB = 100% global eq + 100% Treasury stacked; +equity AND keeps bonds |
| f1_no_tlt_more_mf | 25% | 25% | 25% | 25% | 0% | 0% | TLT 15% → MF 15% (split between KMLM + DBMF); more crisis-alpha replacing duration |

## Effective exposure summary

- f1_split_baseline: 45% equity (22.5 NTSX + 22.5 GDE) + 30% bonds (15 NTSX + 15 TLT) + 22.5% gold + 35% MF
- f1_no_tlt_to_equity: 58.5% equity (29.25 + 29.25) + 19.5% bonds (NTSX) + 29.25% gold + 35% MF
- f1_rssb_replaces_tlt: 60% equity (22.5 + 22.5 + 15 RSSB stock) + 30% bonds (15 NTSX + 15 RSSB Treasury) + 22.5% gold + 35% MF
- f1_no_tlt_more_mf: 45% equity + 15% bonds (NTSX only) + 22.5% gold + 50% MF

## KILLs pre-committed

- KILL #1: best alternative beats F1+SPLIT on ≥1/3 datasets across Sharpe/CAGR/MDD trade-off
- KILL #2 (monotonic): not directly applicable (not a weight sweep)
- KILL #6 NEW (capital accumulation test): if any alternative has CAGR > F1+SPLIT baseline by >0.5% AND MDD ≤ baseline + 5pp on ≥2/3 datasets, that alternative wins on capital accumulation goal

## Expected outcome (priors)

- f1_no_tlt_to_equity: should boost CAGR but increase MDD (no duration hedge in 2008/2020 crashes); hypothesis is +1pp CAGR, +5pp MDD
- f1_rssb_replaces_tlt: best of both — adds equity AND keeps bond hedge via stacking; predicted to have similar Sharpe to baseline + slightly higher CAGR
- f1_no_tlt_more_mf: trades duration for trend-MF; hypothesis is similar Sharpe but different drawdown profile (1980s OK, 2008/2020 worse without TLT)

## Synth used

RSSB synth = `RSSBSIM` direct from testfolio cache (1969+, 56y window, no synthesis required).

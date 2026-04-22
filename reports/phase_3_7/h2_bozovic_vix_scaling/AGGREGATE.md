# H2.a — Božović 2024 VIX-managed portfolio (SPY/cash, rota B) — AGGREGATE

**Verdict: FAIL (hard gates)**

Produced: 2026-04-22
Branch: `phase3.6/swing-winner-hunt-20260423`
Pytest baseline: 890 passed (pre-commit) → 894 passed (post-commit, +4 H2 smoke tests)

## Citations

- Božović (2024) "VIX-managed portfolios", *International Review of Financial
  Analysis* v95 Part A — signal spec `[bozovic_2024_irfa]`.
  (Literature-sprint §T2 Paper 1; indexed in
  `docs/research/2026-04-23-phase3.7-literature-sprint.md`.)
- F2-patched `prev_weight × ret` alignment — `[advances_fin_ml, p.31-34]`.
- Stationary bootstrap (Politis-Romano 1994) — `[advances_fin_ml, p.196-202]`.
- CSCV PBO + DSR — `[advances_fin_ml, p.208-211, p.275]`.
- Mandate §2.4 (13 gates) + §4 (Inter rota B 15% DARF) —
  `docs/investment-mandate.md`.

## Signal (literal Božović 2024)

```
vix_baseline = 20.0
vix_ma_21_t1 = mean(VIXCLS_close[t-21..t-1])        # trailing 21 trading days, shifted
exposure_t   = clip(vix_baseline / vix_ma_21_t1, 0.0, 1.0)
w_SPY[t]     = exposure_t
w_SHV[t]     = 1 - exposure_t
r_port[t]    = w_SPY[t-1] * r_SPY[t] + w_SHV[t-1] * r_SHV[t]   # F2
```

Daily rebalance at close. Year-end 15% DARF on net realized gain
(carry-forward within year, no cross-year loss netting).

## Data

| Series | Coverage | Source |
|---|---|---|
| SPY total-return | 1991-01-02 → 2001-05-13 | Ken French CRSP-VW TR (`mkt_rf + rf`) |
| SPY total-return | 2001-05-14 → 2026-04-20 | Tiingo `adj_close` pct_change |
| SHV cash proxy | 1991-01-02 → 2007-01-10 | Ken French daily RF (~3%/yr avg) |
| SHV cash proxy | 2007-01-11 → 2026-04-20 | Tiingo `adj_close` pct_change |
| VIXCLS | 1990-01-02 → 2026-04-14 | FRED via `data/phase3_7/vix/VIXCLS.parquet` |

Stitching seams are both daily-decimal total-return so no rescaling at the
boundary. **8,881 daily bars** in the full run.

## Windows

| Split | Range | Bars |
|---|---|---|
| IS | 1991-01-02 → 2005-12-31 | 3,780 |
| OOS | 2006-01-01 → 2018-12-31 | 3,271 |
| FWD | 2019-01-01 → 2026-04-14 | 1,830 |
| FULL | 1991-01-02 → 2026-04-20 | 8,881 |

Non-overlapping. OOS includes GFC 2008, Euro 2011, Taper 2013, 2015 China,
2018 Q4. FWD includes COVID 2020, 2022 rate shock, 2024-25 rally.

## Cost model (Banco Inter rota B)

- **Commission:** 0.0 (Inter&Co Securities commission-free US ETFs).
- **FX spread:** 1.20% per conversion. Inside a USD sub-account trading USD
  instruments (SPY/SHV) this is **structurally zero** intra-strategy.
  Stressed at 2.4% with `apply_fx_on_rebalance=True` in cost×2.
- **Year-end DARF:** 15% on net realized gain per calendar year. No
  cross-year loss netting.
- **Cum tax drag over full run:** 316.7% of starting equity (28 tax events
  over 35 years of profitable compounding).

## Winner config

| Parameter | Value |
|---|---|
| `vix_baseline` | 20.0 |
| `vix_ma_days` | 21 |
| `exposure_floor` | 0.0 |
| `exposure_cap` | 1.0 |
| `tax_rate` | 0.15 |
| `fx_spread` | 0.012 |
| `apply_fx_on_rebalance` | False |
| `rebalance_threshold` | 0.0 |

All Božović 2024 canonical. No parameter tuning (sensitivity grid is for
PBO/DSR only, not winner selection).

## Split metrics

| Split | Sharpe | CAGR | MaxDD | N |
|---|---|---|---|---|
| IS | 0.623 | 7.84% | -46.45% | 3,780 |
| OOS | **0.474** | **6.04%** | **-40.21%** | 3,271 |
| FWD | 0.725 | 10.92% | -26.24% | 1,830 |
| FULL | 0.590 | 7.80% | -46.45% | 8,881 |

## Gate table (13 gates)

| # | Name | Level | Value | Verdict |
|---|---|---|---|---|
| 01 | IS Sharpe > 0.5 | soft | 0.623 | PASS |
| 02 | OOS Sharpe ≥ 1.3 | soft | 0.474 | **FAIL** |
| 03 | OOS CAGR tier (rota B) | warning | 6.04% → **Folclore** (< 11% CDI líquido) | WARN |
| 04 | OOS MDD tier (rota B) | warning | -40.21% → **Forte warning** (35-50%) | WARN |
| 05 | FWD Sharpe > 0 | soft | 0.725 | PASS |
| 06 | WF ≥ 6/8 profitable | soft | 7/8 (max_mdd 46.5%) | PASS |
| 07 | Median hold ≥ 5 days | soft | 2745 days (continuous regime) | PASS |
| 08 | IR vs SPY buy-hold ≥ 0.2 | soft | -0.2994 | **FAIL** |
| 09 | Cross-lib concordance ≤ 3pp CAGR | **hard** | Δ = 0.0pp (pandas×pandas) | PASS |
| 10 | Bootstrap OOS 99.9% CI low > 0 | **hard** | [-0.2552, 1.3665] | **FAIL** |
| 10b | Bootstrap FULL 99.9% CI low > 0 | hard | [0.0984, 1.1126] | PASS |
| 11 | PBO < 0.3 single-feature | **hard** | 0.0238 (n=252 CSCV combos, N=6) | PASS |
| 12 | DSR p < 0.05 | **hard** | p = 0.343004 | **FAIL** |
| 13 | cost×2 Sharpe > 1.0 unleveraged | soft | 0.290 | **FAIL** |

**Hard gate fails:** 10 (bootstrap OOS CI), 12 (DSR). **Soft gate fails:** 2
(OOS Sharpe), 8 (IR vs SPY), 13 (cost×2). **Verdict: FAIL** (hard block).

## Stress-period breakdown (NOT gate-binding)

| Window | Range | N | Sharpe | CAGR | MDD |
|---|---|---|---|---|---|
| GFC 2008-09 | 2008-01 → 2009-06 | 377 | -0.837 | -17.95% | -35.36% |
| Euro 2011 | 2011-07 → 2011-12 | 127 | -0.548 | -13.52% | -16.81% |
| Taper 2013 | 2013-05 → 2013-12 | 170 | +1.637 | +20.13% | -5.55% |
| China Aug 2015 | 2015-08 → 2015-12 | 106 | -0.230 | -5.84% | -11.11% |
| Q4 2018 | 2018-10 → 2018-12 | 63 | -2.433 | -44.33% | -18.79% |
| COVID 2020 | 2020-02 → 2020-06 | 94 | -1.110 | -34.59% | -26.24% |
| Rate 2022 | 2022-01 → 2022-12 | 251 | -1.014 | -19.01% | -22.95% |

**The strategy fails systematically in every major stress regime except 2013
taper.** The VIX-scaling rule is supposed to reduce exposure before/during
stress — empirically it did not.

## Cross-lib concordance

Method: `pandas_module_vs_pandas_reference` (same math, two independent code
paths: the module simulator vs an inline `(w.shift(1) * ret).sum(axis=1)`
reference, both on pandas). OOS Δ CAGR = 0.0pp (exact match on gross, pre-tax
— validates the F2-patched alignment in the simulator).

**Note:** This is a weak cross-lib check (same library). Vectorbt's
`Portfolio.from_orders` / `from_signals` API maps poorly to a continuous-
exposure daily-rebal strategy (entries/exits are not well-defined when
exposure changes fractionally each bar). A true engine-level cross-check
with `bt.algos.WeighTarget` or backtrader `rebalance()` would be a stronger
gate and is left for a future sibling run if H2.a ever became a candidate.
For a FAIL verdict this weaker check is sufficient because the hard-gate
failure is statistical (DSR, bootstrap CI) — library mechanics are not the
binding constraint.

## PBO / DSR grid

6 sibling configs (single-feature perturbations of `vix_ma_days` and
`vix_baseline`), 252 CSCV combinations on 8,881 daily bars, 10 blocks.

| Tag | `vix_ma_days` | `vix_baseline` | Full Sharpe |
|---|---|---|---|
| vma21_vb20 (winner) | 21 | 20 | 0.590 |
| vma10_vb20 | 10 | 20 | 0.626 |
| vma42_vb20 | 42 | 20 | 0.559 |
| vma63_vb20 | 63 | 20 | 0.556 |
| vma21_vb15 | 21 | 15 | 0.643 |
| vma21_vb25 | 21 | 25 | 0.570 |

**PBO = 0.024 (PASS)** — the signal is not overfit. Every sibling config
is in the 0.56-0.64 Sharpe band — the strategy is **stably mediocre**.

**DSR p = 0.343 (FAIL)** — even after correcting for 6 trials, the
observed OOS Sharpe (0.030 periodic, ≈ 0.474 annualized) is not
distinguishable from selection-bias noise. This is the clean counter-point
to "just because PBO passes doesn't mean the edge is real."

## Diagnostic interpretation

- **Tax drag is catastrophic for a low-turnover buy-bias-equivalent
  strategy.** Exposure spends 85%+ of bars at 1.0 (VIX < 20 is historically
  the modal regime), meaning the strategy is effectively "SPY with some
  de-risking in vol regimes". The 15% DARF paid 28 times over 35 years (every
  year-end with a positive YTD) compounds into a 316% total tax drag on a
  starting-equity basis — this is what kills the CAGR.
- **Tier 4 MDD (-40%) shows the de-risking rule didn't save us in GFC.**
  VIX prior-month mean in Oct 2008 was ~38, so exposure was scaled to
  20/38 ≈ 0.53. That halved the loss but did not eliminate it, and the
  cash sleeve's ~1-2%/yr drift did not compensate.
- **Negative IR vs SPY buy-hold (-0.30) confirms the strategy is actively
  WORSE than holding SPY naked.** The forward-looking VIX scaling cuts
  exposure right at the bottom of crashes (when prior-month VIX is
  already elevated) and re-enters after recovery has started — a classic
  "sell low, buy high" rhythm unmitigated by the simple MA-of-VIX lag.
- **PBO 0.024 / DSR p 0.34 is a textbook "stable but weak" profile.** The
  signal is reproducible (low PBO) but the effect size is within noise
  (high DSR p). No amount of parameter tweaking will fix this — the
  framework itself is the problem.
- **Paper claim "substantial with transaction costs" does not translate
  to the BR tax regime.** Božović 2024 reported cost-aware alpha on US-
  residents (0% CG in retirement accounts, 15-20% elsewhere with loss
  harvesting, no annual forced realization). The BR 15% mandatory year-
  end realization destroys the "reduced turnover" advantage the paper
  highlights.

## Halt-contract notes

- VIX-SPY alignment clean (inner-join, no hacks). Overlap: 8,881 days.
- No engine regression — gross-return cross-check between module and
  one-liner reference matches at 0.0pp CAGR on OOS. F2 alignment OK.
- PBO < 0.3, DSR p > 0.05, cross-lib Δ < 3pp → **Reject PASS** at the
  DSR boundary, as mandated by the prompt's halt contract.

## Next-step recommendation

**Do NOT promote H2.a.** The strategy's signal is stable but its
expected return net of 15% BR DARF is indistinguishable from luck
(DSR p=0.34). Three paths from here:

1. **Abandon pure VIX-scaling in the Strategy B portfolio** — the Božović
   2024 signal does not survive BR tax + Inter rota B cost structure.
2. **Try H2.b (leveraged variant with SSO/UPRO substitution)** — the
   paper's "requires less rebalance" claim may kick in more strongly
   when the on-regime leg has 2-3× beta, offsetting the tax drag through
   larger compound gains. Still must pass DSR/bootstrap.
3. **Combine VIX scaling with Gayed 200d SMA as a multi-factor filter**
   — Božović claims VIX-scaling is complementary to traditional MA
   regime signals. The Phase 3.7-1 literature sprint T2 Key Takeaway
   explicitly flagged this as the "extension" hypothesis. H4 (meta-layer
   combining H2 + B1 LETF rotation) is the natural next test.

For H2.a itself: **FAIL, commit, move on.**

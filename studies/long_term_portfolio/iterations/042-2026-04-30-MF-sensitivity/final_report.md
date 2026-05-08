# Iter 042 — Final Report — `MF-sensitivity`

**Verdict (NEW SPY-only mandate, 2026-04-29 reframing)**: **STRONG 88/100** — `winner_conditions_met=True`.

**Verdict (LEGACY avg(SPY,VT) + 0.10)**: **WINNER 93/100** — `winner_conditions_met=True`.

**Primary citation**: [ilmanen_expected_returns, ch.19]

---

## Selected config: `mf_kmlm`

Weights:

```json
{
  "NTSXSIM": 0.25,
  "GDESIM": 0.25,
  "KMLMSIM": 0.35,
  "TLTSIM": 0.15
}
```

## Per-dataset metrics (gross-of-tax)

| dataset | Sharpe | CAGR | MDD | gates | DSR p |
|---|---:|---:|---:|---:|---:|
| **lh_56y** | 1.111 | 11.00% | 21.13% | 7/7 | 3.64e-09 |
| **vt_real** | 1.003 | 10.09% | 17.40% | 7/7 | 7.48e-04 |
| **ndx_real** | 1.139 | 10.67% | 11.76% | 6/7 | 2.45e-04 |

## Configs grid (Sharpe per config × dataset)

| config | lh_56y | vt_real | ndx_real |
|---|---:|---:|---:|
| mf_kmlm | 1.111 | 1.003 | 1.139 |
| mf_dbmf | 0.995 | 1.003 | 1.164 |
| mf_split | 1.000 | 1.026 | 1.176 |
| mf_cta_proxy | 1.111 | 1.003 | 1.139 |

## NEW SPY-only Sharpe edge

| dataset | bench (SPY) | hurdle (+0.05) | candidate | edge | passes? |
|---|---:|---:|---:|---:|:-:|
| lh_56y | 0.680 | 0.730 | 1.111 | +0.431 | [OK] |
| vt_real | 0.900 | 0.950 | 1.003 | +0.103 | [OK] |
| ndx_real | 0.900 | 0.950 | 1.139 | +0.239 | [OK] |

## Robustness (5y rolling Sharpe, anchor dataset)

- bonus_pts: 5/5
- pct_positive_sharpe: 100.00%
- n_windows: 34
- anchor_dataset: lh_56y

## Window caveat (CRITICAL — read before interpreting)

**DBMFSIM data starts 2000-01-04** (26y window). KMLMSIM data starts
1988-01-04 (38y window). The "Configs grid" Sharpe row above for
`mf_kmlm` is computed on the **full 38y lh_56y window**, while
`mf_dbmf` and `mf_split` are computed on the **26y intersection only**.
This is **NOT apples-to-apples** for `mf_kmlm` vs `mf_dbmf`/`mf_split`
on lh_56y.

To make a fair MF-sleeve comparison, we recompute all three configs on
the **shared 2000-2026 intersection** (26y) below. `vt_real` and
`ndx_real` are already apples-to-apples (those datasets start 2008-2010
which is fully inside the DBMFSIM window).

### lh_56y on 2000-2026 intersection (apples-to-apples)

| config | Sharpe | CAGR | MDD |
|---|---:|---:|---:|
| mf_kmlm  (26y truncated) | **0.9626** | 9.73% | 21.13% |
| mf_dbmf  (26y native)    | **0.9947** | 10.42% | 21.78% |
| mf_split (26y native)    | **1.0004** | 10.10% | 19.91% |

On the 26y intersection (where DBMF data exists):

- **Best Sharpe**: `mf_split` (1.0004), beating `mf_kmlm` by +0.038 and
  `mf_dbmf` by +0.006.
- **Best CAGR**: `mf_dbmf` (10.42%), beating `mf_split` by +0.32pp and
  `mf_kmlm` by +0.69pp.
- **Best MDD (lowest)**: `mf_split` (19.91%), beating `mf_kmlm` by
  −1.22pp and `mf_dbmf` by −1.87pp.

`mf_split` dominates two of three axes (Sharpe + MDD); `mf_dbmf` wins
CAGR but trails on Sharpe and MDD.

## Deploy MF sleeve recommendation

**Recommended MF sleeve: `SPLIT` (50/50 KMLMSIM + DBMFSIM, 17.5% each).**

Rationale (rule from hypothesis §Deploy recommendation):

- **Sharpe**: split (1.0004) ≥ DBMF (0.9947, Δ+0.006) AND split ≥ KMLM
  (0.9626, Δ+0.038). Both deltas are within the 0.05 noise floor, so
  the rule "split Sharpe ≥ both within 0.05 ⇒ recommend split" fires.
- **MDD**: split has the lowest 26y MDD (19.91% vs DBMF 21.78% vs KMLM
  21.13%), confirming engine diversification reduces drawdown.
- **CAGR**: split mid-pack (10.10%); DBMF leads (10.42%) by +0.32pp.
  Acceptable trade-off given Sharpe + MDD wins.
- **AUM stability for 20-30y deploy**: splitting between DBMF ($3.2B
  AUM) and KMLM ($600M AUM) reduces single-issuer / single-engine
  concentration risk (closure / manager turnover / engine drift).
- **Engine diversification**: KMLM = pure trend (KFA MLM Index, transparent
  rules-based); DBMF = SG CTA Index replication via factor regression
  (broader CTA exposure including carry, mean-reversion). The two
  engines are correlated but not identical — combining captures
  trend persistence (KMLM) AND broader CTA universe (DBMF).
- **TER trade-off**: DBMF 0.85% vs KMLM 0.92%; 50/50 average ~0.88%
  (rounding). Within deploy budget.

### Why not pure DBMF (despite the AUM rule)?

The hypothesis rule specifies **"if DBMF Sharpe ≈ KMLM within 0.05 ⇒
recommend DBMF for AUM advantage"** — that fires here (DBMF − KMLM =
+0.032 on 26y, within 0.05). However, the **split rule trumps the
DBMF-only rule** because split Sharpe ≥ both within 0.05 — split
captures the AUM advantage of DBMF (50% of sleeve at $3.2B issuer)
while retaining KMLM's longer track record and pure-trend transparency.

### Why not pure KMLM (incumbent)?

KMLM looks dominant on the full 38y lh_56y row (Sharpe 1.111), but that
is a **window artifact** — those extra 12 years (1988-1999) include the
KMLM Index's golden trend era (LTCM '98 vol harvest, '90s commodity
trends). On the apples-to-apples 26y intersection, KMLM is the **worst**
of the three (Sharpe 0.9626). Deploy decisions should weight the
post-2000 regime more heavily for 20-30y forward.

### CTA Simplify (`mf_cta_proxy`) — future work

`mf_cta_proxy` was set to KMLMSIM weights as a placeholder because
**Simplify CTA's Altis Partners engine is multi-strategy** (trend +
carry + mean-reversion + risk-off overlay) and is not modeled in
testfolio. Numerically it is identical to `mf_kmlm`. To honestly model
CTA Simplify as a deploy alternative, future work needs:

1. Altis Partners CTA strategy fact sheet (sub-strategy weights).
2. Per-sub-strategy testfolio synth or live data history.
3. Reweight aggregate per Altis allocation rules.

Until that synth exists, treat `mf_cta_proxy` as a **flag**, not a
result. The deploy recommendation above stands on the kmlm/dbmf/split
honest comparison.

## INCOMPLETE flags

- **`mf_cta_proxy` is structurally identical to `mf_kmlm`**. Simplify
  CTA's Altis multi-strategy engine is NOT modeled in testfolio. The
  config is a placeholder flag for future work. Do NOT cite its metrics
  as a CTA result — they are KMLM metrics duplicated.
- **DBMFSIM 26y window** vs KMLMSIM 38y window. Cross-MF Sharpe/CAGR/MDD
  comparison is only honest on 2000-2026 intersection. The "Configs
  grid" table above shows both configs' native windows; the
  "lh_56y on 2000-2026 intersection" table is the apples-to-apples
  comparison used for the deploy recommendation.

## Lesson

On the apples-to-apples 26y window, the **50/50 KMLM+DBMF split
dominates pure-KMLM and pure-DBMF on Sharpe (1.000 > 0.995 > 0.963)
and MDD (19.9% < 21.1% < 21.8%)**, with a modest CAGR cost (10.10% vs
DBMF's 10.42%). Combined with the AUM-stability advantage of having
50% of the sleeve in DBMF ($3.2B issuer), **`SPLIT` is the deploy
recommendation for the iter 023 NTSX+GDE+MF+TLT chassis**.

The 38y lh_56y "incumbent KMLM" Sharpe of 1.111 is a **window-bias
artifact** — the 1988-1999 segment includes the KMLM Index's golden
trend era and is not representative of the 20-30y forward deploy
horizon. Future loop iterations on the KMLM-anchored chassis should
quote the 2000+ intersection metrics for honest cross-MF comparisons.

CTA Simplify remains an open deploy question — its Altis multi-strategy
engine is not modeled in testfolio, and `mf_cta_proxy` is a placeholder
flag, not a result. Future work: build Altis-engine synth from sub-
strategy fact sheets to enable a fourth honest comparison.

[ilmanen_expected_returns, ch.19] MF crisis-alpha role anchors the
sleeve presence; the engine choice (split vs pure) is a deploy-time
robustness decision dominated here by AUM stability + Sharpe + MDD,
not raw return.


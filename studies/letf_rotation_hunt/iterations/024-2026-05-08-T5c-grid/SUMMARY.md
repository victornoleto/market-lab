# 024-2026-05-08-T5c-grid — SUMMARY

**Tier:** T5c
**Hypothesis:** Focused IDM × pool sweep on multi-asset T5c. Tests robustness of the
Carver IDM=2.5 cap [p.170-171] and pool composition sensitivity. Ablations:
no-gold, no-bond, HFEA-Trinity {UPRO, TMF, UGL}.

**Primary citation:** [systematic_trading, ch.10 p.170-171, ch.11]; spec §2.6 T5c
**Engine SHA:** `e7c432a`
**Datetime UTC:** 2026-05-08T14:24:36.444608+00:00
**Configs tested:** 7

## TL;DR

Best config: **`voltarget_multi4_idm25`** (PROMISING, score 68.5/100). lh_56y: Sortino 1.0553 (primary), Sharpe 0.740 (secondary), CAGR 19.39%, MDD -62.9%. **KILL T5-expansion:** FIRES (Sortino threshold 1.272).

## Configs tested

| Name | on_asset | off_asset | signal | period |
|------|---------|----------|--------|-------:|
| `voltarget_multi4_idm15` | ? | ZROZ | ? | ? |
| `voltarget_multi4_idm20` | ? | ZROZ | ? | ? |
| `voltarget_multi4_idm25` | ? | ZROZ | ? | ? |
| `voltarget_no_gold_idm22` | ? | ZROZ | ? | ? |
| `voltarget_no_bond_idm22` | ? | ZROZ | ? | ? |
| `voltarget_hfea_trinity_idm22` | ? | ZROZ | ? | ? |
| `voltarget_hfea_trinity_idm25` | ? | ZROZ | ? | ? |

## Results — gross metrics per dataset

| Config | lh_56y Sharpe | modern_1990 Sharpe | spy_real Sharpe | ndx_real Sharpe | lh_56y CAGR | modern_1990 CAGR | spy_real CAGR | ndx_real CAGR | lh_56y MDD | modern_1990 MDD | spy_real MDD | ndx_real MDD |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `voltarget_multi4_idm15` | 0.712 | 0.710 | 0.672 | 0.890 | 18.10% | 18.00% | 16.64% | 23.30% | -58.1% | -51.3% | -51.3% | -48.2% |
| `voltarget_multi4_idm20` | 0.732 | 0.734 | 0.703 | 0.908 | 19.00% | 19.08% | 17.87% | 24.07% | -60.9% | -49.3% | -49.3% | -46.7% |
| `voltarget_multi4_idm25` | 0.740 | 0.744 | 0.725 | 0.914 | 19.39% | 19.54% | 18.77% | 24.40% | -62.9% | -48.2% | -47.4% | -46.3% |
| `voltarget_no_gold_idm22` | 0.666 | 0.659 | 0.516 | 0.675 | 18.22% | 17.77% | 12.63% | 18.09% | -59.2% | -59.2% | -59.2% | -59.2% |
| `voltarget_no_bond_idm22` | 0.628 | 0.648 | 0.718 | 0.888 | 16.35% | 17.24% | 18.86% | 24.40% | -60.8% | -52.0% | -46.2% | -46.2% |
| `voltarget_hfea_trinity_idm22` | 0.659 | 0.641 | 0.681 | 0.823 | 16.29% | 15.64% | 17.61% | 21.72% | -52.5% | -52.5% | -48.7% | -45.1% |
| `voltarget_hfea_trinity_idm25` | 0.666 | 0.650 | 0.693 | 0.825 | 16.61% | 16.04% | 18.12% | 21.84% | -54.3% | -51.0% | -47.4% | -45.6% |

**SPY anchor (lh_56y):** Sharpe 0.682, MDD -55.1% (mandate §2.2/§2.3 — MDD warning-only).

## Gates per config

| Config | G1 PBO | G2 DSR p (local) | G3 WF | G4 OOS S | G5 FWD S | G6 99% low | G7 Δ pp | Tier |
|--------|-------:|-----------------:|------:|---------:|---------:|-----------:|--------:|------|
| `voltarget_multi4_idm15` | 0.599 | 0.0009 | 5/8 >SPY (MDD 51% warn) | 0.773 | 0.826 | 0.350 | 0.00pp | MARGINAL |
| `voltarget_multi4_idm20` | 0.599 | 0.0006 | 5/8 >SPY (MDD 49% warn) | 0.798 | 0.877 | 0.376 | 0.00pp | MARGINAL |
| `voltarget_multi4_idm25` | 0.599 | 0.0005 | 6/8 >SPY (MDD 47% warn) | 0.807 | 0.906 | 0.386 | 0.00pp | PROMISING |
| `voltarget_no_gold_idm22` | 0.599 | 0.0026 | 6/8 >SPY (MDD 59% warn) | 0.581 | 0.478 | 0.339 | 0.00pp | MARGINAL |
| `voltarget_no_bond_idm22` | 0.599 | 0.0058 | 5/8 >SPY (MDD 52% warn) | 0.817 | 0.931 | 0.256 | 0.00pp | MARGINAL |
| `voltarget_hfea_trinity_idm22` | 0.599 | 0.0027 | 4/8 >SPY (MDD 49% warn) | 0.674 | 0.827 | 0.309 | 0.00pp | NEAR_FAIL |
| `voltarget_hfea_trinity_idm25` | 0.599 | 0.0024 | 4/8 >SPY (MDD 47% warn) | 0.677 | 0.843 | 0.322 | 0.00pp | NEAR_FAIL |

Hard-gate thresholds (spec §3.5): G1 PBO < 0.50, G2 DSR p < 0.05, G3 ≥5/8 windows + MDD < 50%, G4/G5 Sharpe > 0, G6 99% CI low > 0, G7 |Δ| ≤ 3pp.

## Plots

- `plots/01_equity_curves.png` — log-scale equity per config + SPY benchmark
- `plots/02_drawdown_curves.png` — peak-to-trough drawdown
- `plots/03_rolling_sharpe_5y.png` — 5y rolling Sharpe
- `plots/04_rolling_cagr_3y.png` — 3y rolling CAGR
- `plots/05_regime_attribution.png` — % of time signal=ON per config
- `plots/06_pct_beat_spy.png` — cumulative fraction of 3y windows where config beat SPY
- `plots/07_crisis_attribution.png` — MDD per crisis window vs SPY

## Tables

- `tables/per_config_metrics.csv` — one row per (config, dataset)
- `tables/gates_pass_fail.csv` — gate values + pass/fail flags

## Verdict

- **Best config:** `voltarget_multi4_idm25` (PROMISING, score 68.5)
- **KILL T5-expansion:** FIRES (Sortino 1.0553 < 1.272)
- **Advance to next tier:** no
- **Cumulative n_trials:** 422
- **Deploy escalation eligible:** no

## Conclusion

IDM and pool-composition sweeps confirm the original T5c plateau: diversification helps, but the small correlated LETF pool does not generate enough independent forecasts to beat the T3d Sortino benchmark.

## Next iter

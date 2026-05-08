# iter 024 — G3 LRS-GATED HFEA CLASSICAL

**Date**: 2026-04-30
**Slug**: G3-lrs-gated-hfea
**Cumulative n_trials before**: 86
**Configs in this iter**: 5
**Cumulative n_trials after**: 91

---

## Architectural axis

**8th cross-product hybrid**: Gayed 200d-SMA gate × HFEA-classical-leverage-barbell sleeve (UPRO + TMF, 300% notional with leveraged duration).

Bridges existing G-family hybrid taxonomy:

| family | gate | sleeve | sleeve notional | sleeve decay | iter | score |
|---|---|---|---:|---|---:|---:|
| G1 | SMA-200d on SPY | F1 stack (NTSX/GDE/KMLM/DBMF/TLT) | 1.41× | no-decay | 016 | 61 |
| G2 | SMA-200d on SPY | F1 LETF 2.25× sleeve | 2.25× | moderate-decay | 017 | 64 |
| **G3** | **SMA-200d on SPY** | **HFEA classical UPRO+TMF** | **300%** | **leverage-barbell-decay** | **024** | **?** |

Adds a NEW DECAY-REGIME data point at 300% notional with leveraged-duration leg (TMF 3× LTT carries ~1.5%/y daily-reset decay PLUS UPRO 3× SPY ~3-5%/y daily-reset decay). This regime was tested in iter 008 (B1 HFEA static, score 63 with MDD ~67% catastrophic FAIL) but never with LRS gate composition.

---

## Hypothesis (5 configs)

### Primary hypothesis
LRS gate's bear-avoidance mechanism (going to IEF when SPY < 200d MA) **rescues HFEA classical's MDD bar failure** by skipping the 2008 GFC + 2022 inflation regimes that destroyed static HFEA.

Specifically:
- **2022 (HFEA killer)**: SPY broke 200d MA Jan 2022 → gate OFF → escapes TMF -70% blowup (the HFEA killer scenario)
- **2008 GFC**: SPY broke 200d MA Dec 2007 → gate OFF → misses TMF +75% rally BUT also misses UPRO -85% drag; net MDD better
- **2020 COVID**: fast crash + recovery → gate whipsaw cost (~1-2pp CAGR drag)
- **2010-2021 bull**: gate ON for ~85% of period → captures HFEA's high upside

### KILL conditions (pre-committed, numbered after iter 023 #88)

- **KILL #89**: max G3 score ≤ 71 → 8th architectural-axis confirms ceiling at 71 DEFINITIVE; LRS×HFEA does NOT compose to break ceiling (8th confirmation point of KILL #33)
- **KILL #90**: max G3 score ≤ 65 → cross-product G3 inferior to G2 (64) + E1 (65) cross-product hybrid family ceiling; LRS×HFEA decay-dominated regime not architecturally distinct from prior G-family
- **KILL #91**: max G3 score ≥ 75 → STRONG tier reachable; HUNT REOPENED at LRS×leverage-barbell axis. Mandate §7 review case STRONGLY strengthened
- **KILL #92**: G3 mean MDD > 55.17% → LRS gate INSUFFICIENT to save HFEA at 300% notional regardless of leg structure; KILL #79 generalization upper bound (300% notional cannot be rescued by gate alone)
- **KILL #93**: G3 5545 mean Sharpe ≥ B1 static 5545 0.730 + 0.10 = 0.830 → gate composition lifts Sharpe at 300% notional regime (extends KILL #79 generalization: MF-effectiveness inversely-proportional-to-leverage was about MF-additions; this tests whether GATE-additions also follow inverse-leverage pattern)
- **KILL #94**: G3 KMLM-augmented variant (5035+kmlm15) Sharpe ≥ G3 5545 by ≥ 0.05 AND mean MDD ≤ G3 5545 by ≥ 5pp → KMLM 15% addition AT GATED 300% backbone matches KMLM lift pattern observed at static 300% (KILL #27 OPPOSITE) — testing whether gate-composition INVERTS the leverage-attenuation pattern, i.e., gate effectively-reduces effective-leverage

### Configs to test (5)

```python
# G3 — LRS gate × HFEA leveraged barbell sleeve

# G3.1 — Bogleheads canonical 55/45 with LRS gate
"g3_gated_hfea_5545": {
    "type": "lrs",
    "on_weights": {"UPROSIM": 0.55, "TMFSIM": 0.45},
    "off_weights": {"IEFSIM": 1.00},
    "signal_ticker": "SPYSIM",
    "sma_window": 200,
    "lag_days": 1,
}

# G3.2 — Duration-tilted 50/50 with LRS gate (B1 5050 was best static B1 Sharpe 0.74)
"g3_gated_hfea_5050": {
    "type": "lrs",
    "on_weights": {"UPROSIM": 0.50, "TMFSIM": 0.50},
    "off_weights": {"IEFSIM": 1.00},
    "signal_ticker": "SPYSIM",
    "sma_window": 200,
    "lag_days": 1,
}

# G3.3 — HFEA + 15% KMLM crisis-alpha with LRS gate (combines iter 022 KILL #79 generalization)
"g3_gated_hfea_kmlm15": {
    "type": "lrs",
    "on_weights": {"UPROSIM": 0.50, "TMFSIM": 0.35, "KMLMSIM": 0.15},
    "off_weights": {"IEFSIM": 1.00},
    "signal_ticker": "SPYSIM",
    "sma_window": 200,
    "lag_days": 1,
}

# G3.4 — Modest HFEA 40/40/20 (B5 4040+kmlm20 best modest static, Sharpe 0.736) GATED
"g3_gated_hfea_4040": {
    "type": "lrs",
    "on_weights": {"UPROSIM": 0.40, "TMFSIM": 0.40, "KMLMSIM": 0.20},
    "off_weights": {"IEFSIM": 1.00},
    "signal_ticker": "SPYSIM",
    "sma_window": 200,
    "lag_days": 1,
}

# G3.5 — Defensive off-state with KMLM (replicate iter 016 G1 BLEND off-state pattern at 300%)
"g3_gated_hfea_5545_blend_off": {
    "type": "lrs",
    "on_weights": {"UPROSIM": 0.55, "TMFSIM": 0.45},
    "off_weights": {"IEFSIM": 0.50, "KMLMSIM": 0.50},
    "signal_ticker": "SPYSIM",
    "sma_window": 200,
    "lag_days": 1,
}
```

---

## Expected outcomes

Based on:
- iter 008 B1 5545 STATIC: CAGR ~20%, MDD ~67% (FAIL bar), Sharpe ~0.73
- iter 016 G1 stack 1.41×: gate ADDS Sharpe at no-decay regime (1.018→1.080)
- iter 017 G2 LETF 2.25×: gate REDUCES Sharpe from G1's no-decay best (1.080→0.97)
- iter 014 E1 TQQQ 3×: gate whipsaw + decay dominates → score 65

Predicted G3 zone:
- CAGR: 12-16% (gate + whipsaw cost ~4-8pp from B1 static 20%)
- MDD: 25-45% (gate's 2022 escape provides 20-30pp relief from B1's 67%)
- Sharpe: 0.65-0.95 (regime-dependent; whipsaw cost in choppy markets)
- Score: 60-72 (within or below meta-axis ceiling 71)

**Most likely outcome**: KILL #89 fires (max ≤ 71), KILL #90 NOT fired (G3 in 60-65 range similar to G2 64), KILL #91 NOT fired (no STRONG tier), KILL #92 NOT fired (gate saves MDD bar for at least 1 of 5 configs), KILL #93 fires (gate lifts Sharpe at 300% regime, extending inverse-leverage pattern).

This iter test architectural completeness: **does gate composition follow the same inverse-leverage attenuation pattern documented for MF crisis-alpha across 3-iter trajectory (300%/200%/150% = 0/+0.04-0.08/+0.13 lift)?**

---

## INCOMPLETE flags

- **TMFSIM synth**: 3× TLTSIM with 1.5%/y daily-reset decay (validated in iter 008's 3 tests). Real TMF post-2009 has tracking variance not modeled.
- **lh_56y synth coverage**: TMFSIM uses TLTSIM data starting 1986. Pre-1986 TLT does not exist; synth caveats apply per `[advances_fin_ml, p.31-34]` cross-lib framework.
- **Gate signal**: SPYSIM 200d-SMA same as iter 002/006/016/017. T+1 lag, no peek-ahead validated by iter 002 KILL #7 test infrastructure.

---

## Citations

- `[leverage_for_the_long_run, ch.3-4, p.40-60]` Gayed LRS rationale (200d SMA gate)
- HFEA Bogleheads 2019 — leveraged barbell rationale (UPRO + TMF 55/45 canonical)
- `[risk_parity, ch.5, p.10]` Carlson — capital-efficient stacking (related leverage-barbell concept)
- `[ilmanen_expected_returns, ch.19]` — MF crisis-alpha context for KMLM augmentation
- `[advances_fin_ml, p.208-211]` PBO via CSCV
- `[advances_fin_ml, p.222-223]` DSR with cumulative_n_trials
- `[advances_fin_ml, p.196-202]` Bootstrap CI
- `[advances_fin_ml, p.31-34]` Factor framework + cross-lib

---

## Architectural completeness rationale

After iter 023's 7-axis taxonomy declaration (Meta-ensemble 71, LRS-mono 67, Cross-product hybrid 65, Static-multi 63, Vol-target 60, Static-barbell-modest 58, Static-low-leverage 57), the **LRS-gate × leverage-barbell-sleeve** cross-product remained UNTESTED. iter 016 G1 / iter 017 G2 tested SMA-gate × {stack/LETF}-sleeve at 1.41× / 2.25× — but NOT × HFEA-leverage-barbell at 300% with leveraged-duration leg. iter 008 B1 tested HFEA STATIC (no gate). The G3 iter completes the cross-product matrix: gate × sleeve at 300%-leverage-barbell-with-leveraged-duration regime.

**Mandate §1 alignment**: research-only, no deploy implications, single-iter cost, reuses existing 'lrs' spec type (no new infrastructure). Iter 024/50 = 48% utilization.

**Mandate §7 anticipated outcome**: most likely 8th axis ≤ 71, ADDS confirmation point to architectural ceiling claim. If KILL #91 fires (≥ 75 STRONG), strengthens hunt-reopen case OR mandate §7 rubric-revision case (depending on bar profile).

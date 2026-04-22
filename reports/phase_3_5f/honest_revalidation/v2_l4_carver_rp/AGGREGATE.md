# V2-L4 Carver RP — Honest re-validation (Phase 3.5f F3)

**Date:** 2026-04-22  |  **Branch:** `phase3.5f/plano-a-v2-l2-cross-lib-redo-20260422`
**Engine fix commit:** `7b90a8f` (F2 — `prev_weights × ret` shift applied)
**Inputs:** L1 TSMOM (clean), L2 Gayed EMA100 L3 off-gld (regenerated honest), L3 AFML XLF (clean)
**Windows:** IS 2003-08-20 → 2017-12-31 | OOS 2018-01-01 → 2023-12-31 | FWD 2024-01-01 → 2026-04-14

## Verdict: ❌ **FAIL**

The Carver risk-parity blend fails 10 of 13 gates under the honest engine.
OOS CAGR collapses from the buggy baseline **16.14% → 4.99%** — below
both the hard gate-3 threshold (30%) AND the user-override CDI-floor
threshold (13%). No PARTIAL winner status.

Mandate §7 and `docs/strategies/plano_a_v2_l2_gayed_cfd.md` stay
**UNTOUCHED** — this verdict is FAIL, no promotion needed.

## Top-line comparison — buggy baseline vs honest re-validation

| Metric | Buggy baseline (Apr 2026) | Honest (F2-patched) | Δ |
|---|---:|---:|---:|
| OOS Sharpe | 1.856 | **0.621** | −1.235 |
| OOS CAGR | 16.14% | **4.99%** | −11.15 pp |
| OOS MaxDD | −8.44% | **−12.77%** | −4.33 pp |
| FWD Sharpe | 0.594 | **−0.191** | −0.785 |
| FWD CAGR | 4.54% | **−1.81%** | −6.35 pp |
| IS Sharpe | 0.703 | **−0.072** | −0.775 |
| IS CAGR | 6.95% | **−1.28%** | −8.23 pp |
| WF ratio | 7/8 | **6/8** | −1 |
| WF max window DD | 23.78% | **33.63%** | +9.85 pp |
| PBO | 0.000 | **0.079** | +0.079 |
| DSR p-value | 0.0014 | **0.328** | +0.327 |
| Bootstrap OOS 99.9% CI low | 0.489 | **−0.666** | −1.155 |
| IR vs SPY OOS | 0.106 | **−0.463** | −0.569 |

## Carver vol-target scaling (IS-derived, unchanged recipe)

| Leg | IS σ (ann.) | Scale | Implied risk weight |
|-----|------------:|------:|--------------------:|
| L1 TSMOM (lb12m vt10) | 5.79% | 2.59 | 29.3% |
| L2 Gayed EMA100 L3 off-gld (honest) | 35.44% | 0.42 | 4.8% |
| L3 AFML XLF | 2.57% | 5.85 | 66.0% |

The implied risk weights are essentially identical to the buggy run
(29%/5%/66%). The plan's context note — *"L2 was ~66-75% of the
blend"* — does **not** match the Carver IS-derived scaling. By
construction L3 (with unnaturally low IS vol from the meta-label
flat-hold days) dominates the risk budget; L2 gets only 4.8%. Even
though L2's honest Sharpe collapsed, the blend performance change is
dominated by L3's and L1's own returns — L2 carries too little weight
to meaningfully drag the blend down.

**So the collapse from Sharpe 1.856 → 0.621 is NOT about L2 dilution.**
It's that under the honest engine the L2 leg is no longer silently
lifting the blend via cross-correlation noise, L1 TSMOM is OOS-negative
(Sharpe -0.21), and L3 AFML contributes ~2.5%/yr at 66% weight — the
blend inherits the CAGR-starved profile.

## 13-Gate checklist (plan §5.5; gate 3 softened to CDI floor per 2026-04-22 Q&A)

| # | Gate | Threshold | Value | Pass |
|---|------|-----------|------:|:----:|
| 1 | Bootstrap OOS 99.9% CI low > 0 | > 0 | −0.666 | ❌ |
| 1b | Bootstrap FULL 99.9% CI low > 0 | > 0 | −0.711 | ❌ |
| 2 | OOS Sharpe ≥ 2.0 | ≥ 2.0 | 0.621 | ❌ |
| 3 | OOS CAGR ≥ 30% | ≥ 30% | 4.99% | ❌ |
| 3-soft | OOS CAGR ≥ CDI BR (~13%) | ≥ 13% | 4.99% | ❌ |
| 4 | OOS MaxDD ≥ −25% | ≥ −25% | −12.77% | ✅ |
| 5 | FWD Sharpe > 0 | > 0 | −0.191 | ❌ |
| 6 | WF 6/8 profitable AND max DD ≤ 25% | both | 6/8, mdd 33.63% | ❌ |
| 7 | Median hold ≥ 3 days (L2 leg proxy) | ≥ 3d | 1.0d | ❌ |
| 8 | IR vs SPY OOS ≥ 0.5 | ≥ 0.5 | −0.463 | ❌ |
| 9 | Cross-lib concordance ≥ 2/3 of libs ±3pp | deferred | engine already cross-lib validated (commit 7b90a8f) | N/A |
| 10 | Stage-2 data concordance ±1pp | deferred | L2 TR vs testfolio already ±0.06pp in v2_l2_gayed_redo | N/A |
| 11 | PBO < 0.5 (CSCV 10-block) | < 0.5 | 0.079 | ✅ |
| 12 | DSR p < 0.05 | < 0.05 | 0.328 | ❌ |
| 13 | Cost×2 sensitivity → OOS Sharpe > 1.0 | > 1.0 | 0.459 | ❌ |

**Summary: 2 PASS / 10 FAIL / 2 deferred (cross-lib + Stage-2 data,
already covered upstream in F2 validation)**. Even if the two deferred
gates were PASS, the blend still fails 10 gates — not a PARTIAL and
nowhere near PASS.

## Which gates killed it

The blend fails almost every gate that measures **edge** (Sharpe, CAGR,
DSR, IR-vs-SPY, bootstrap CI) while passing **risk caps** (MaxDD, PBO).
The pattern is diagnostic: statistical-robustness controls all say the
blend is "not overfit" because there was **never any edge to overfit**.
The blend is genuinely mediocre — consistent with AFML ch.16 and Carver
ch.9's observation that risk-parity only works when every leg has a
positive expected edge at its own vol target. Under the honest engine,
L1 is OOS-negative (Sharpe −0.21), L3 is positive-but-starved (CAGR
~2.5%), and L2 is positive-but-modest (Sharpe ~0.6, CAGR ~13-14% per
`v2_l2_gayed_redo`). Blending three marginal legs does not create an
edge — it averages out what little there was.

## L4 vs L2 under honest engine — which is more/less favorable?

| Metric | L2 standalone (honest, `gayed_ema100_L3_off_gld`) | L4 blend (honest) |
|---|---:|---:|
| OOS Sharpe | ~0.56-0.61 | 0.621 |
| OOS CAGR | ~12.6-14.3% | 4.99% |
| OOS MaxDD | ~−36% to −38% | −12.77% |
| FWD Sharpe | ~0.81-0.87 | −0.191 |
| FWD CAGR | ~20-22% | −1.81% |

**Verdict on L2 vs L4 (honest):** L2 standalone has **higher CAGR but
much worse MDD** (the leverage shows up in drawdowns). L4 the blend has
**similar OOS Sharpe, much smaller MDD, but lower CAGR** — and a
**negative FWD Sharpe** while L2 standalone is positive on FWD. **Neither
wins as a Plano A strategy:** L2 fails mandate §5 MDD cap (−36% > 25%)
and gate 3 soft CDI (~13%; L2 is borderline). L4 passes MDD but is
basically SPY-minus in FWD.

**Conclusion: Under the honest engine, Plano A loses BOTH V2-L2 and
V2-L4.** The L4 "rescue" hypothesis ("if L2's alpha shrinks, the blend
may end up comparable to or better than L2 alone") is **not** borne out
empirically — the L2 leg is too small in the risk-parity allocation
(4.8%) to drive the blend either way, and the blend's fate is set by
L1+L3 which were clean from the start and don't constitute a winner.

## Artifacts

- `AGGREGATE.json` — full numeric detail, 13-gate structured.
- `carver_rp_blend_honest_daily_returns.parquet` — honest blend daily
  returns for downstream replication.
- `L2_honest_daily_returns.parquet` — honest L2 `gayed_ema100_L3_off_gld`
  returns regenerated with F2-patched engine (commit 7b90a8f), usable
  as input by any future L4 variant.
- Logs: `logs/phase3_5f_f3_l4_carver.log`.

## Mandate §7 / strategy doc status

**UNTOUCHED.** This verdict is FAIL. No promotion, no demotion beyond
what the F2 engine fix already implies. The strategy doc
`docs/strategies/plano_a_v2_l2_gayed_cfd.md` keeps its current
(buggy-numbers) status — updating it is the job of plan §F4 once all 6
V2 leads have been re-validated.

## Citations

- Lookahead bias detection + two-stage replication protocol:
  `[advances_fin_ml, p.31-34]`.
- Carver retail cost model + risk budget + hold discipline:
  `[systematic_trading, p.185-188, p.280-310]`.
- Bootstrap 99.9% CI: `[advances_fin_ml, p.196-202]`.
- PBO CSCV 10-block: `[advances_fin_ml, p.208-211]`.
- DSR: `[advances_fin_ml, p.273-275]`.
- Walk-forward 6/8 + 25% DD cap: `[advances_fin_ml, ch.11]`.
- Gayed regime rotation thesis: `[leverage_for_the_long_run, Gayed, p.11-14]`.
- Risk-parity only works with positive-edge legs: AFML ch.16, Carver ch.9.

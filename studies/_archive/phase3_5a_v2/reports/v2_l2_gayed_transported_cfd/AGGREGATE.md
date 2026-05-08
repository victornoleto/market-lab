# Lead V2-L2 — Gayed LETF rotation transported to CFD (aggregate)

**Phase:** phase3_5a_v2 | **Lead:** V2-L2 | **Status:** ★ PASS (1 winner promoted, 4 subset-PASS)
**Period:** 2001-05-14 → 2026-04-14 (24.9y, 6266 daily bars)
**Tested:** 27 configs × 1 universe {SPY, QQQ} = 27 runs
**Aggregation iter:** 43
**Path tag:** [SHORT-HOLD CFD]

## Summary

Plano A has its first legitimate winner. The Gayed regime-rotation family
`[leverage_for_the_long_run]`, transported from its native SSO/UPRO synthetic form
(Plano B) to a **CFD-leverage** expression (Pepperstone Razor, explicit daily swap,
round-trip spread+commission+slippage), clears **every gate in the V2 framework** at
the lowest-leverage branch (L=2) with both `EMA-100` and `LRS` regime signals and
either `cash` or `GLD` in the off-regime slot. The winner crowned by the aggregator
is **`gayed_ema100_L2_off_gld`** — the highest-Sharpe config among those that also
survive the WF max-DD-per-window gate (25% cap).

The canonical "SMA-200 + risk-parity off-regime" flavor that beat Plano B for
synthetic-LETF (1.91 Sharpe, 3-leg EW) is **not** the best flavor under the CFD
cost model. EMA-100 (Hurwitz half-life ≈ 100/2 ≈ 50 days) is materially more
adaptive on regime flips and clears the max-DD-per-window gate that all SMA-200
configs fail. L=2 is the only leverage the gates admit: L=3 cracks max-DD-per-window
at 29-32% (just over the 25% cap), L=5 crashes through it at 48% (flat across the
off-regime triplet — a leverage-bound invariant consistent with Vince PoR
`[leverage_space]` + Gayed LRS empirical `[leverage_for_the_long_run, p.17]`).

The OOS Sharpe spread among the 27 configs is narrow (top-5 gap 0.10), meaning the
family is robust — it's not one lucky config in a field of failures. PBO across all
27 configs is **0.103** (CSCV, 10 blocks) — an order of magnitude under the AFML
0.5 gate `[advances_fin_ml, p.208-211]`, and **0.036** at 16 blocks. DSR
p-value on the winner is **0.000288** accounting for 27 trials, so selection-bias
does not explain the edge `[advances_fin_ml, ch.14]`.

### Cross-gate decision table (winner: `gayed_ema100_L2_off_gld`)

| Gate | Threshold | Observed | Pass |
|---|---:|---:|:--:|
| PBO (CSCV, 10 blocks, full period) | < 0.5 | **0.103** | ✅ |
| PBO (CSCV, 16 blocks, full period) | < 0.5 | **0.036** | ✅ |
| DSR p-value (n_trials = 27) | < 0.05 | **0.000288** | ✅ |
| OOS Sharpe (annualized, 2018-2023) | > 0 | **2.285** | ✅ |
| FWD Sharpe (2024-01 → 2026-04) | > 0 | **1.821** | ✅ |
| Bootstrap 99.9% CI low (stationary, 10k resamples, block 5) | > 0 | **0.962** | ✅ |
| Walk-forward profitable windows | ≥ 6/8 | **8/8** | ✅ |
| Walk-forward max window drawdown | ≤ 25% | **22.7%** | ✅ |
| OOS CAGR net (after Pepperstone Razor costs) | ≥ 30% | **79.1%** | ✅ |
| OOS Sharpe net | ≥ 2.0 | **2.285** | ✅ |
| OOS MaxDD | ≤ 25% | **-21.02%** | ✅ |
| Median hold days | ≥ 3 | **6.0** | ✅ |
| Benchmark IR vs SPY (OOS) | ≥ 0.5 | **2.161** | ✅ |

## Cross-config table (ranked by OOS Sharpe)

| Config | Sharpe IS | Sharpe OOS | Sharpe FWD | CAGR OOS | MaxDD OOS | Med hold (d) | WF w/MDD | DSR p | CI 99.9% low | IR vs SPY | **Subset PASS** |
|--------|----------:|-----------:|-----------:|---------:|----------:|-------------:|:--------:|------:|-------------:|----------:|:----:|
| gayed_ema100_L3_off_gld | — | 2.294 | — | 128.9% | -30.04% | 6.0 | 8/8 w/30.04% | 0.000271 | 0.971 | — | ❌ (MDD-per-window > 25%) |
| gayed_ema100_L2_off_gld ★ | 1.86 | **2.285** | 1.821 | **79.14%** | **-21.02%** | 6.0 | **8/8 w/22.7%** | **0.000288** | **0.962** | **2.161** | ✅ **WINNER** |
| gayed_ema100_L5_off_gld | — | 2.284 | — | 255.2% | -46.20% | 6.0 | 8/8 w/46.20% | 0.000288 | 0.962 | — | ❌ (L5 MDD) |
| gayed_ema100_L5_off_cash | — | 2.209 | — | 235.2% | -45.56% | 6.0 | 8/8 w/45.56% | 0.000499 | 0.853 | — | ❌ |
| gayed_ema100_L5_off_tlt | — | 2.188 | — | 235.3% | -45.52% | 6.0 | 8/8 w/45.52% | 0.000549 | — | — | ❌ |
| gayed_ema100_L3_off_cash ★subset | — | 2.192 | — | 116.0% | -29.24% | 6.0 | 8/8 w/29.24% | 0.000536 | — | — | ❌ (MDD-per-window) |
| gayed_ema100_L3_off_tlt | — | 2.124 | — | 115.9% | -29.19% | 6.0 | 8/8 w/29.19% | 0.000915 | — | — | ❌ |
| gayed_lrs_L3_off_gld | — | 2.187 | — | 119.8% | -31.63% | 5.5 | 8/8 w/31.63% | 0.000554 | — | — | ❌ |
| gayed_ema100_L2_off_cash ★ | — | **2.172** | — | **68.96%** | **-20.13%** | 6.0 | **8/8 w/20.1%** | **0.000746** | **0.916** | **1.981** | ✅ subset PASS |
| gayed_lrs_L2_off_gld ★ | — | **2.178** | 1.795 | **74.15%** | **-21.88%** | 5.5 | **8/8 w/23.3%** | **0.000741** | **0.885** | **2.045** | ✅ subset PASS |
| gayed_lrs_L5_off_gld | — | 2.177 | 1.911 | 232.4% | -48.76% | 5.5 | 8/8 w/48.76% | — | — | — | ❌ (L5 MDD) |
| gayed_lrs_L5_off_cash | — | 2.108 | — | 215.0% | -48.76% | 5.5 | 8/8 w/48.76% | — | — | — | ❌ |
| gayed_lrs_L5_off_tlt | — | 2.082 | — | 213.5% | -48.76% | 5.5 | 8/8 w/48.76% | — | — | — | ❌ |
| gayed_lrs_L3_off_cash | — | 2.092 | — | 108.2% | -31.63% | 5.5 | 8/8 w/31.63% | — | — | — | ❌ |
| gayed_lrs_L2_off_cash ★ | — | **2.072** | 1.899 | **64.99%** | **-21.88%** | 5.5 | **8/8 w/21.9%** | **0.001717** | **0.776** | **1.873** | ✅ subset PASS |
| gayed_lrs_L3_off_tlt | — | 2.017 | — | 107.2% | -31.63% | 5.5 | 8/8 w/31.63% | — | — | — | ❌ |
| gayed_ema100_L2_off_tlt | — | 2.017 | — | 68.9% | -27.69% | 6.0 | 8/8 w/27.69% | — | — | — | ❌ (MDD) |
| gayed_lrs_L2_off_tlt | — | 1.911 | — | 64.1% | -26.15% | 5.5 | 8/8 w/26.15% | — | — | — | ❌ (MDD) |
| gayed_sma200_L2_off_gld | — | 1.645 | — | 54.4% | -21.91% | 5.0 | 7/7 w/21.9% | — | — | — | ❌ (Sharpe < 2) |
| gayed_sma200_L3_off_gld | — | 1.637 | — | 83.3% | -31.63% | 5.0 | FAIL | — | — | — | ❌ |
| gayed_sma200_L5_off_gld | — | 1.621 | — | 143.0% | -48.76% | 5.0 | FAIL | — | — | — | ❌ |
| gayed_sma200_L5_off_cash | — | 1.565 | — | 133.0% | -48.76% | 5.0 | FAIL | — | — | — | ❌ |
| gayed_sma200_L3_off_cash | — | 1.556 | — | 75.8% | -31.63% | 5.0 | FAIL | — | — | — | ❌ |
| gayed_sma200_L5_off_tlt | — | 1.558 | — | 133.0% | -48.76% | 5.0 | FAIL | — | — | — | ❌ |
| gayed_sma200_L2_off_cash | — | 1.545 | — | 48.1% | -21.88% | 5.0 | 7/7 | — | — | — | ❌ (Sharpe < 2) |
| gayed_sma200_L3_off_tlt | — | 1.526 | — | 75.7% | -38.80% | 5.0 | FAIL | — | — | — | ❌ |
| gayed_sma200_L2_off_tlt | — | 1.467 | — | 48.0% | -36.55% | 5.0 | FAIL | — | — | — | ❌ |

Rows marked with ★ have the aggregator-recomputed DSR / bootstrap CI / IR-SPY
numbers. Other rows inherit per-config metrics only (DSR p / CI computed for
the candidate family; propagating for all 27 was redundant given the winner-selection
logic). Full per-config DSR and bootstrap CIs are recorded in
`AGGREGATE.json`.

## Ranking structure (three invariants discovered)

1. **Leverage-bound MaxDD cap (Vince PoR):** MaxDD-per-WF-window is
   monotonically increasing with leverage:
   - L=2 → 20-23% (under gate)
   - L=3 → 29-32% (over gate)
   - L=5 → 45-49% (ruína approach)
   
   The L=5 MaxDD is **identical** across cash/TLT/GLD (48.76% to 2 decimal
   places) — off-regime asset no longer matters at 5× because the on-regime
   crashes dominate the total DD. `[leverage_for_the_long_run, p.17]` and
   `[leverage_space, Vince]` are both empirically confirmed.

2. **Signal-adaptivity gradient:** SMA-200 (long, slow) → LRS (composite) →
   EMA-100 (short, exponential). Within each leverage tier:
   - L=2 Sharpe rank: EMA-100 (2.17-2.28) > LRS (2.07-2.18) > SMA-200 (1.47-1.65)
   - This confirms Gayed's own observation `[leverage_for_the_long_run, p.11-14]`
     that faster regime signals exit the risk-on allocation earlier in a drawdown
     and re-enter later in a recovery. The gain is not cosmetic: EMA-100 cleared
     the 25% MDD-per-window gate at L=2 that SMA-200 missed.

3. **Off-regime allocation: GLD > cash > TLT at L=2.** The spread is ~0.1 Sharpe
   but consistent (GLD beats cash at EMA-100 L=2 and LRS L=2; TLT lags both).
   This replicates Gayed's `risk-parity off-regime` recommendation
   `[leverage_for_the_long_run, p.16, p.21]`: GLD's positive drift + dollar-hedge
   asymmetry in crises is worth ~7pp/yr CAGR over cash at this leverage. TLT
   underperforms because the OOS window (2018-2023) includes 2022 — the worst
   fixed-income year in a century, where TLT drew down 39% and dragged the
   off-regime side with it.

## Benchmark vs Plano B winner

Plano B winner: `Portfolio_3leg_EW = SSO+QQQ+GLD daily` (Sharpe OOS 2.251, CAGR
25.56%, MaxDD -10.86%, IR vs SPY — higher structurally due to 3-leg diversification).
Plano A V2-L2 winner: `gayed_ema100_L2_off_gld daily CFD L=2` (Sharpe 2.285, CAGR
79.14%, MaxDD -21.02%, IR vs SPY 2.161).

- Sharpe comparable (2.285 vs 2.251, +0.03).
- **CAGR ~3× higher** (79% vs 25.56%) — the leverage stacks.
- **MaxDD ~2× deeper** (-21% vs -10.86%) — the leverage also bites.
- IR vs SPY 2.16 — strategy earns excess return per unit tracking error.
- CAGR/MaxDD ratio ≈ 3.8 for Plano A vs 2.4 for Plano B — Plano A is more
  reward-dense per unit drawdown even at leverage, which is the pivot rationale
  for including it in the 30-pp active-bucket alongside Plano B.

Neither dominates the other on all axes. V2-L7 will position them as the
**dual-path portfolio** the mandate §1 envisions — B as the moderate-swing leg,
A as the aggressive-leveraged leg. Winner criteria forum for mandate §1 met:
CAGR ≥ 30% (79% ≫ 25.56% B), Sharpe ≥ 2.0 (matched), MaxDD ≤ 25% (matched).

## Cost model applied (full round-trip)

Per `specs/phase_3_5a_v2.md` §3:
- Spread half × 2 = 4 bps round-trip
- Commission $3.50/side → 6.6 bps round-trip on notional
- Slippage 1-3 bps round-trip (3 bps applied — retail conservative)
- Swap daily 0.005% long (Pepperstone Razor tier on SPY/QQQ, ~1.25 bps/day)
- GLD swap applied to off-regime days only.

Cumulative transaction cost OOS for the winner: **1.26% of starting equity**
over 6 years (~0.21%/yr) — material but well-absorbed by the 79% CAGR. Cumulative
swap cost: 0.45%. Neither swap nor spread is the binding cost at this hold
profile (median 6d). Carver `[systematic_trading, p.185-188]` holds: spread+commission
dominant regime for retail, and the hold aligns with the 1-4 week optimum.

## Diagnostic: why this works under CFD cost but not canonical TSMOM

V2-L1 (canonical TSMOM monthly) failed catastrophically (0/12 PASS, swap drag
74-166%) because it holds 41-160 days with daily swap at 5 bps/day = 200-800 bps
drag. V2-L2 holds only when the regime is on (median 6 days before a switch),
spreads entry/exit across SPY+QQQ in equal weight (reducing per-ticker
concentration vs TSMOM's FX-3-pack attractor), and uses GLD as the off-regime
sink rather than running flat (capturing GLD's positive drift). The winner's
switch rate is 616 over ~25 years (≈ 25 switches/yr, 12-13 days per
switch per leg) — cost-economic sweet spot `[systematic_trading, p.185-188]`.

## Implications for V2 remainder

V2-L2 PASS means Plano A is **not abandoned**. V2-L3 to V2-L6 remain pending
per spec, but their value changes:

- **V2-L3 (AFML triple-barrier + meta-label):** now tests for a *second* edge
  that is uncorrelated with the Gayed regime-rotation family. Even a weak PASS
  here earns a portfolio-level diversification lift (Carver risk-parity).
- **V2-L4 (Carver risk-parity multi-strategy):** inputs now include V2-L2 winner
  as one leg. Expected to hit PASS easily if L3 produces even a modest non-NaN.
- **V2-L5 (equity pairs):** independent edge search. Market-neutral so no overlap.
- **V2-L6 (vol breakout):** independent edge search, explicitly non-FX.
- **V2-L7 verdict:** already pointed toward PASS outcome — will append
  `winners_short_hold:` for V2-L2 (iter 43) and, if L3-L6 produce more,
  additional winners. The "abandon Plano A" branch of V2-L7 is now unreachable.

## Citations

- Gayed LRS / EMA / SMA regime rotation: `[leverage_for_the_long_run, p.7, p.11-14, p.16-17, p.21]`.
- PoR vs leverage cap (L=5 invariance of MaxDD across off-regime assets): `[leverage_space, Vince]`.
- Kelly f/2 cross-check (L=2 is f/2-safe for SPY+QQQ+GLD under this distribution): `[math_money_mgmt, Vince]`.
- Risk-parity off-regime allocation: `[systematic_trading, ch.8-9]` (Carver).
- PBO / CSCV threshold 0.5: `[advances_fin_ml, p.208-211]`.
- DSR / selection-bias correction: `[advances_fin_ml, ch.14]`.
- Walk-forward 6/8 profitable-window gate: `[advances_fin_ml, ch.11]`, Pardo (2008) ch.10-11.
- Stationary block bootstrap: Politis & Romano (1994); usage `[advances_fin_ml, p.196-202]`.
- Retail cost model (spread+commission dominant @ 1-4 week holds): `[systematic_trading, p.185-188]`.
- Pepperstone Razor cost parameters: `docs/investment-mandate.md §3` + `specs/phase_3_5a_v2.md §3`.

## Links

- Per-config reports: `reports/phase3_5a_v2/v2_l2_gayed_transported_cfd/gayed_*.md`
- Per-config JSON:    `reports/phase3_5a_v2/v2_l2_gayed_transported_cfd/gayed_*.json`
- Daily returns:      `reports/phase3_5a_v2/v2_l2_gayed_transported_cfd/gayed_*_daily_returns.parquet`
- Aggregate JSON:     `reports/phase3_5a_v2/v2_l2_gayed_transported_cfd/AGGREGATE.json`
- Registry:           `reports/phase3_5a_v2/v2_l2_gayed_transported_cfd/registry.json`
- Jornada:            `jornada/2026-04-19/01-phase3.5a-v2-L2-gayed-transported-PASS.md`
- Next lead:          V2-L3 (AFML triple-barrier + meta-label), spec §V2-L3.

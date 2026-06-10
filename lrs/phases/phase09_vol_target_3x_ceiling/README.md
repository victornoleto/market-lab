# Phase 9 — Quadratic Vol-Targeting with a 3x Ceiling (PRE-REGISTRATION)

> Status: research-only / diagnostic. Nothing here authorizes deployment, paper
> trading or a mandate change. Mandate §1 (maintenance mode) unchanged.
> **Trigger:** explicit user request (2026-06-10) — "ganhos maiores" using
> TQQQ/UPRO — after the Phase 8 closure. This is a user-directed, return-first
> exploration of ONE variation inside the already-tested 7D family; it does
> not reverse Phase 8's verdict on the 7A/7D survivors.

## Question

The Phase 2 frontier shows constant-target leverage above 2.00 is
Calmar-dominated: each rung above 2x buys ~0.6–1pp CAGR for ~4–5pp MDD, with
QQQ L3.00 reaching 24–26% CAGR only at ruin-tier MDD (−63% to −71%). The
continuous-Kelly reading explains why: `f = μ/σ²` puts the right exposure for
index sleeves at ~1.5–2.5x in NORMAL vol — 3x is only Kelly-consistent when
realized vol is LOW `[volatility_trading, p.135, p.138]`. The 7D quadratic
sizing rule `L_t = clip(σ_target² / RV_t², 0, L_max)` already implements
exactly that response but was capped at the headline geometry (2.00/1.75).
Hypothesis under test: raising the cap to 2.50/3.00 lets the ladder reach
TQQQ/UPRO **only in calm regimes**, capturing part of the 3x CAGR without the
ruin-tier drawdown of the constant-3x rows.

## Mechanism (7D family verbatim; ONE new axis)

- `L_t = clip(σ_target² / RV_t², 0, L_max)`, 0.25-ladder quantization with
  inertia, SMA200 weekly gate, headline risk-off sleeves, lag-through-CASHX,
  `AnnualDarfEngine` — all verbatim from Phase 7D/6B.
- Ladder above 2x mixes/uses the cached 3x sleeves (`UPROSIM` / `TQQQSIM`)
  via the existing `phase04.target_leverage_weights`; at `L_t = 3.0` the
  risk-on sleeve is pure 3x `[leverage_for_the_long_run, p.16, fn.22-23]`.
- New axis values: `L_max ∈ {2.50, 3.00}`; `σ_target ∈ {40%, 45%}` (45% is new
  and pre-registered here; 40% is the 7D winner). RV window fixed at `21`
  (the 7D winning estimator on both branches — not re-swept).

## Pre-registered grid — 48 rows (+48 to the n_trials ledger → 4377 + 48 = 4425)

| Axis | Values |
|---|---|
| Branch (headline sleeve/geometry) | SPY (off `50 ZROZ / 25 GLD / 25 CASH`), QQQ (off `40 ZROZ / 40 GLD / 20 IEF`) |
| `L_max` | `2.50, 3.00` |
| `σ_target` | `40%, 45%` |
| RV window | `21` (fixed) |
| lag | `0..5` |

Non-trial comparison rows: the binary headline base per branch AND the 7D
branch winner (σ40/RV21 at the committed cap), read from
`lrs/results/phase07d_vol_target_quadratic.csv`.

**Built-in sanity (non-trial):** re-running the 7D winner config (headline
`L_max`, σ40/RV21, committed lag) through this phase's pipeline must
reproduce the committed 7D CSV row (max abs CAGR/MDD diff reported).

## Pre-registered screen (return-first, per user direction; per branch)

Selection: the highest after-tax CAGR row **among rows with MDD ≥ −50%**
(rows below the floor are reported but cannot be selected). Criteria on the
selected row:

1. After-tax CAGR **strictly greater** than the branch 7D winner
   (SPY > 15.34%, QQQ > 19.53%).
2. MDD ≥ −50% (hard floor — below this is ruin-adjacent, not a candidate).
3. WF beats **not worse** than the branch 7D winner (SPY ≥ 12/17, QQQ ≥ 8/11).

All three → diagnostic SUCCESS (a return-first lead; NOT a gate pass — any
promotion-grade claim would need the full SS5 suite with the grown ledger,
where DSR only gets harder). Any miss → honest FAIL `[advances_fin_ml,
p.208-211]`, `[advances_fin_ml, p.273-275]`.

## Outputs

`lrs/results/phase09_vol_target_3x_ceiling.csv`, `REPORT.md`, plots (L_t
ladder series incl. time share at each rung, equity/DD vs 7D winner and
binary headline, frontier by L_max, WF comparison),
`tests/test_lrs_phase09.py`.

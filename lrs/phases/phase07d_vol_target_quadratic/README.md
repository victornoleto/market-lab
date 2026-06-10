# Phase 7D — Quadratic Vol-Targeting σ²/RV² (PRE-REGISTRATION)

> Status: research-only / diagnostic. Nothing here authorizes deployment, paper
> trading or a mandate change. Mandate §1 (maintenance mode) unchanged.
> **Round order note:** Phase 7 round runs 7A → 7B → 7C → 7D → 7E → (7F) → 8.

## Question

Phase 6B tested linear vol-target sizing `L_t ∝ σ_target / RV_t` and got a
QQQ-only diagnostic SUCCESS (WF 7/11 vs 6/11). Phase 6C's forensics flagged
`bear_mid` (mid-vol bear whipsaw) at a 0% beat rate. The single remaining
citable variation in this family is the **quadratic form**: continuous-Kelly
sizing is proportional to the *inverse variance*, `f = r / σ²`
`[volatility_trading, p.135, p.138]` — i.e. `L_t ∝ σ_target² / RV_t²`, which
cuts exposure faster as vol rises (and restores it faster as vol falls) than
the linear form. The cap at `L_max` is the fractional-Kelly discipline
`[volatility_trading, p.139-140]`; the sizing frame is the same
conservative-position-scaling logic as 6B `[systematic_trading, p.137-148]`.
Hypothesis under test: the more aggressive vol response flips `bear_mid`
windows and lifts walk-forward consistency above the 6B result.

## Mechanism (one family — quadratic sizing replaces 6B's linear scalar)

- `L_t = clip(σ_target² / RV_t², 0, L_max)`, everything else identical to
  Phase 6B verbatim: 0.25-ladder quantization with position inertia, SMA200
  weekly gate, headline risk-off sleeves, lag convention, `AnnualDarfEngine`.
- RV estimator identical to Phase 2/6B: `rolling(w).std(ddof=0).shift(1) ·
  sqrt(252)` — no lookahead `[testing_tuning, p.327-335]`.

## Pre-registered grid — 72 rows (+72 to the n_trials ledger → 4221 + 72 = 4293)

| Axis | Values | Anchor |
|---|---|---|
| Branch (headline geometry fixed) | SPY: `L_max 2.00`, off `50 ZROZ / 25 GLD / 25 CASH`; QQQ: `L_max 1.75`, off `40 ZROZ / 40 GLD / 20 IEF` | Phase 2/4 headline bases |
| `σ_target` | `30%, 35%, 40%` annualized | brackets the 6B winner (40%) without re-opening the low end (20% was far from optimal in 6B) |
| RV window | `21, 63` | the two Phase 2 estimator windows |
| lag | `0..5` | restart convention |

Plus non-trial comparison rows: the binary headline base per branch AND the
Phase 6B best linear row per branch (read from
`lrs/results/phase06b_vol_target_continuous.csv`).

**Built-in sanity (non-trial):** with a degenerate constant-RV series the
quadratic scalar must equal the linear scalar squared/σ-adjusted by
construction; operationally we assert the quantized series stays on the 0.25
ladder and within `[0, L_max]` (unit tests), and that the runner's
`sigma_target → ∞` limit pins at `L_max`.

## Pre-registered screen (per branch, on the best trial row by WF beats, tie-break Calmar)

1. WF beat count **strictly greater** than the better of {binary headline,
   6B best linear} for the branch (SPY > 12/17, QQQ > 7/11).
2. After-tax CAGR ≥ branch headline − 1pp.
3. MDD ≥ −50% (round constraint).

All three → diagnostic SUCCESS (feeds 7F). Any miss → honest FAIL. No
deployment, no paper-trade label, no mandate change `[advances_fin_ml,
p.208-211]`.

## Outputs

`lrs/results/phase07d_vol_target_quadratic.csv`, `REPORT.md`, plots (L_t
series linear vs quadratic, equity/DD, WF comparison, frontier),
`tests/test_lrs_phase07d.py`.

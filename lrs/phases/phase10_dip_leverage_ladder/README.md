# Phase 10 — Drawdown-Contingent Leverage Ladder ("Buy the Dip") (PRE-REGISTRATION)

> Status: research-only / diagnostic. Nothing here authorizes deployment, paper
> trading or a mandate change. Mandate §1 (maintenance mode) unchanged.
> **Trigger:** explicit user request (2026-06-10) — "qual o nível interessante
> de drawdown para comprar dips? Leverage menor na maior parte do tempo,
> maior nos dips, com regra de migração de volta." Return-first exploration.

## Question

Every mechanism tested so far in `lrs/` is pro-cyclical (be levered in calm
uptrends, de-risk in stress). This phase tests the LAST untested family: the
**contrarian, drawdown-contingent ladder** — hold a lower base leverage most
of the time and ESCALATE leverage when the underlying is in a deep dip,
de-escalating after recovery.

**Citable tension, recorded upfront.** In favor: equity indices are high-noise
markets whose matching strategy class is mean-reversion/countertrend
`[trading_systems_methods, p.13]`. Against (the repo's core thesis): dips are
high-volatility regimes — precisely where leveraged daily compounding is worst
`[leverage_for_the_long_run, p.7-9]`. This phase deliberately bets against the
second reading; the known failure mode is the LONG bear (1929-32 SPY −86%,
2000-02 QQQ −83%): a −30% trigger escalates near the start of the slide and
rides high leverage to the bottom. V-shaped recoveries (1987, 2020) flatter
the mechanism. The 58y/40y windows adjudicate; per-trigger results answer the
user's "what dip level is interesting" question directly.

## Mechanism (one family — DD-state ladder; no SMA gate, no vol gate)

- `DD_t = P_t / runmax(P) − 1` computed on the **underlying** close (the
  LETF's drawdown is a quasi-deterministic amplification of it; measuring on
  the underlying avoids a redundant axis — documented choice).
- State machine with hysteresis (whipsaw control at the boundary
  `[trading_systems_methods, p.383]`):
  - state `base` → exposure `L_base`; switch to `dip` when `DD_t <= −d`;
  - state `dip` → exposure `L_dip`; switch back to `base` per the exit rule:
    - `ath`: only on a new all-time high (`DD_t = 0`);
    - `half`: when `DD_t >= −d/2`.
- The raw state is `.shift(1)`-lagged (decision on the previous close)
  `[testing_tuning, p.327-335]`; weekly cadence, lag-through-CASHX `0..5` and
  `AnnualDarfEngine` verbatim from the restart chassis. Leverage expressed by
  the existing underlying/2x/3x ladder (`phase04.target_leverage_weights`);
  the cap discipline is fractional-Kelly practice `[volatility_trading,
  p.139-140]`.
- NO SMA200 gate and NO vol gate: both would suppress exactly the entries
  under test (dips are below-MA, high-vol days by construction). Clean
  isolation of the family.
- Tax note: escalation in a dip sells the lower-leverage sleeve at a loss
  (DARF netting), de-escalation after recovery realizes gains (taxed) — the
  engine accounts for both.

## Pre-registered grid — 144 rows (+144 to the n_trials ledger → 4425 + 144 = 4569)

| Axis | Values | Anchor |
|---|---|---|
| Branch | SPY, QQQ | restart branches |
| Leverage profile `(L_base → L_dip)` | `(1.0 → 2.0)`, `(1.5 → 3.0)` | the user's "lower most of the time, higher in dips"; caps at the cached 2x/3x sleeves |
| Dip trigger `d` | `10%, 20%, 30%` | spans shallow correction → bear market |
| Exit rule | `ath`, `half` | the two natural de-escalation readings |
| lag | `0..5` | restart convention |

Non-trial comparison rows per branch: underlying B&H, constant `L_base` B&H,
constant `L_dip` B&H (weekly-rebalanced ladder, same engine), and the binary
LRS headline (context).

**Built-in sanity (non-trial):** trigger `d = 100%` (never fires) must
reproduce the constant `L_base` weekly simulation byte-for-byte (max abs diff
reported).

## Pre-registered screen (return-first, per branch)

Selection: highest after-tax CAGR row **among rows with MDD ≥ −50%**. Criteria
on the selected row:

1. After-tax CAGR **strictly greater** than the constant `L_base` B&H of its
   profile (the escalation must pay for itself).
2. MDD ≥ −50% (hard floor).
3. MDD **strictly better** than the constant `L_dip` B&H of its profile (the
   ladder must not cost the full high-leverage drawdown).

All three → diagnostic SUCCESS (return-first lead; NOT a gate pass — any
promotion-grade claim needs the full SS5 suite at the grown ledger). Any miss
→ honest FAIL `[advances_fin_ml, p.208-211]`.

## Outputs

`lrs/results/phase10_dip_leverage_ladder.csv`, `REPORT.md`, plots (exposure
state series, equity/DD vs constant-leverage benchmarks, frontier by
trigger/profile, per-trigger answer table), `tests/test_lrs_phase10.py`.

# Iter 022 — Hypothesis: C.5 — Tail-hedge convexo (inverse-SPY synthetic put)

## Hypothesis

Test a **synthetic convex tail hedge** as iter 011 sleeve overlay. Without
options data, the hedge is approximated as:
- When SPY trailing 21d return < −5%: hedge_return = 2.0 × abs(SPY daily neg
  return) (convex payoff scaling with crash magnitude)
- Otherwise: hedge_return = −0.04%/day (~−10%/yr decay, equivalent to
  rolling 6%/yr ATM put premium amortized)

The sleeve is added to iter 011's NTSX+GDE+KMLM 35/25/40 base at 5/7.5/10/15%
weights, **substituted from KMLM** (the existing crisis-alpha sleeve) — so we
test whether explicit convex hedging beats KMLM's diversified crisis-alpha.

Hypothesis: tail hedge **dominates KMLM in MDD** (smaller drawdowns) but
**costs CAGR/Sharpe** (premium decay in non-crisis years). Likely a
Pareto-tradeoff iter, not a winner — but useful to quantify the MDD cost
of full crisis convexity.

## Pre-committed kill criteria

KILL #1: Best-of-grid loses iter 011 on ≥ 2/3 datasets AND fails to deliver
materially better MDD (< 20% on lh_56y vs iter 011's 26%).

KILL #2: Hedge weight monotonically reduces Sharpe → tail hedge is pure
cost in this universe.

## Configs (4)

iter 011 base (35% NTSX + 25% GDE + 40% KMLM) with hedge substituted from KMLM:

| config | NTSX | GDE | KMLM | TAIL_HEDGE | rationale |
|---|---:|---:|---:|---:|---|
| `tail_5pct`   | 35% | 25% | 35% | 5%  | minimal hedge |
| `tail_7pct`   | 35% | 25% | 32.5% | 7.5% | moderate |
| `tail_10pct`  | 35% | 25% | 30% | 10% | classic tail-risk allocation |
| `tail_15pct`  | 35% | 25% | 25% | 15% | aggressive — KMLM partially replaced |

**Selection rule**: max mean(gross_Sharpe / avg(SPY,VT)_Sharpe).

## Citations

- Spitznagel *Safe Haven* (2021) — convex tail-hedge framework
- `[risk_parity, ch.5]` Carlson — context for cap-eff core retained
- Gates: `[advances_fin_ml, p.208-211, p.222-223, p.196-202, p.31-34]`

## Caveat — synthetic hedge limitations

The 2× SPY-drawdown convex model is a **rough analog** of long puts. Real
options would have:
- Path-dependence (a single bad day can fully realize a put's payoff; my
  21d trigger is path-averaged)
- Vega exposure (puts gain from vol expansion even without underlying move)
- Liquidity / spread cost (~+2% premium drag in real life)

This iter is **diagnostic only** — establishes whether a Pareto-favorable
hedge is plausible in principle. A real deploy would use VXX or actual
SPY puts (deferred).

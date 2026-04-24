# Iteration 020 — Monthly-rolled put-spread tail hedge overlay on iter 016 equity leg

## Hypothesis

Iter 016 (static 60:40 × Moreira-Muir vol-target) is the hunt-loop top-K #1
at 79/100 STRONG, 4/5 winner conditions, with DSR as the sole barrier
(worst p=0.226). Iter 019 closed the family of ρ-derived regime overlays
on vol-managed 2-leg stacks by proving algebraic cointegration: any
measurable function of ρ appears as a multiplicative factor in σ²_port,
so it cannot be orthogonal to the scaling decision.

**Convex options P&L is structurally orthogonal to σ²_port's ingredient
set.** By Carr-Madan (1999), any twice-differentiable payoff `g(S_T)` on
the equity can be replicated as a portfolio of calls + puts + forward;
the replicating portfolio's P&L depends on the full distribution of
`S_T`, not just its variance. In particular, a put spread's daily MtM
is a nonlinear function of `(S_t, σ̂_t, T−t)` that cannot be recovered
from any linear function of (σ_eq, σ_bd, ρ), because option vega +
delta depend on the LEVEL of S_t (distance to strike), not just return
volatility.

Operationally: during fast crashes (March 2020 COVID, 2008 Lehman week,
2022 Feb), σ²_port spikes AFTER the damage (21-day lookback lag). The
put-spread pays INSTANTLY when S_t crosses the long strike, catching
exactly the lag risk of Moreira-Muir. This is the "gamma-as-insurance"
argument in `[dynamic_hedging]` and `[volatility_trading, ch.3]`.

This iteration tests ONE pre-committed configuration (no grid): add a
monthly-rolled long-5%-OTM / short-10%-OTM put spread overlay to the
equity leg of iter 016, priced via Black-Scholes with VIX as the IV
input, and rerun the exact same stacking formula. Pre-committed kill
criteria below.

## Primary citation

`[volatility_trading, p.11, p.41]` — Sinclair (2013): BSM as pricing
model for European options (implied vol = IV that matches market);
S&P 500 excess kurtosis 21.3 (1950-2011) justifies tail hedge.

## Additional citations

- `[risk_parity, p.10-11, ch.1]` — iter 016 base: naïve risk parity
  with fixed weights.
- `[systematic_trading, p.40, ch.2]` — iter 016 base: volatility
  standardisation primitive.
- `[advances_fin_ml, p.162-164]` — σ̂_{t-1} lag (no look-ahead); same
  lag discipline applies to IV input.
- `[advances_fin_ml, p.31-34]` — cross-library parity (G7 requires
  hand-rolled numpy BS + overlay reference).
- Moreira & Muir (2017) JoF 72(4), 1611-1644 — variance-target scaling
  (iter 016 base).
- Carr & Madan (1999) "Towards a Theory of Volatility Trading" — static
  replication of convex payoffs from European options; establishes the
  structural orthogonality used here.
- Israelov, R. (2017) "Pathetic Protection: The Elusive Benefits of
  Protective Puts" — AQR paper documenting that naked put protection
  has drag; put-spread is cheaper-drag alternative.

## Edge source (what SPY 1x misses that this captures)

Fast-crash tail-payoff timing: Moreira-Muir variance scaling responds
to σ²_{t-1} (21-day lookback), creating a 1-21 day lag when σ² spikes
intraday. The put-spread has instantaneous gamma payoff proportional
to `max(K_long − S_t, 0) − max(K_short − S_t, 0)`, capturing the
crash-depth that variance lookback misses. SPY b&h has no such
asymmetric protection — it pays the full drawdown.

## Datasets

- **educational** (SPY+IEF, 2006-01-03 → 2026-04-15, IEF-aligned to
  match iter 016): tests through 2008 GFC + 2020 COVID + 2022 bond
  crash. Put-spread should earn its keep in 2008-10 and 2020-03.
- **spy_real** (SPY+IEF, 2009-06-25 → 2026-04-15): post-GFC 17y;
  only one major crash (2020-03) + 2022 bear. Tighter test because
  tail events are rarer.
- **ndx_real** (QQQ+IEF, 2010-02-12 → 2026-04-15): tech-heavy; uses
  VIX × 1.1 as IV proxy (VXN not in cache). NDX is more volatile so
  hedge payoff should be larger and drag proportional.

## Kill criteria (pre-committed — falsify regardless of secondary metrics)

1. **Sharpe regresses > 0.05 vs iter 016 on ≥ 2 of 3 datasets.** Hedge
   should help MDD at non-trivial Sharpe cost, but if net Sharpe drops
   on a majority of datasets, the drag exceeds the crash-payoff on this
   window.
2. **MDD does NOT improve on any of the 3 datasets (strict: MDD_020 ≥
   MDD_016 on all 3 ds).** The entire structural rationale is MDD
   reduction during fast crashes. If MDD is equal or worse everywhere,
   the hedge fails its stated job — falsified.
3. **Options drag > 3%/yr annualized on all 3 datasets.** Put spreads
   should cost 0.5-1.5%/yr in normal regimes; > 3%/yr means the BS
   pricer is mis-calibrated OR VIX-as-IV severely mispriced OR roll
   mechanics are broken.
4. **Total score < 70** (≥ 9 below iter 016's 79). If the package
   fails to score into STRONG tier, overlay is not accretive.

Kill #2 is the DEFINITIVE structural kill: a convex tail hedge that
fails to reduce MDD ANYWHERE is not the mechanism it claims to be.

## Expected budget

- Configs to test: **1** (pre-committed, no grid, vacuous G1 PASS)
- Wall-time: ~40 min implementation + ~15 min backtest + ~15 min gates
- Cumulative n_trials advance: 4264 → 4267

## Implementation plan

1. `put_spread_hedge.py`:
   - `black_scholes_put(S, K, T, sigma, r)` pure analytical.
   - `compute_put_spread_daily_pnl(prices, iv_series, k_long_pct,
     k_short_pct, dte_days, roll_freq, rf, cost_bps)` → daily net
     return stream of monthly-rolled 5%/10% put-spread.
   - `apply_put_spread_hedged_stack(r_eq, r_bd, put_spread_returns,
     **iter016_kwargs)` → wraps iter 016's
     `apply_static_stack_vol_managed` using `r_eq_hedged = r_eq +
     put_spread_returns` as the equity input.
2. `numpy_reference_put_spread.py`:
   - Hand-rolled numpy BS + daily roll logic; G7 ≤ 3pp CAGR parity.
3. `tests/test_put_spread_hedge.py`:
   - BS put price sanity: at-the-money put value = option_value_ref
     from Hull (tolerance 1e-4).
   - BS put-call parity: `C + K·e^{-rT} = P + S` (tolerance 1e-8).
   - Monotone: put value increases with σ.
   - Put-spread max payoff bounded by `K_long - K_short`.
   - Roll cost: no look-ahead (monthly price at roll date).
4. `run_backtests.py`: single pre-committed cfg on 3 datasets.
5. `compute_gates_and_score.py`: adapt iter 016's; add put-spread drag
   + MDD-delta-vs-iter-016 detail.
6. Run + write verdict.json + final_report.md + plot.

## Config pre-committed

```python
CFG = {
    "cfg_id": "ntsx_vm_vt15_L21_cap20_pp5_10_1m",
    # iter 016 inheritance (identical)
    "eq_weight": 0.6,
    "bd_weight": 0.4,
    "target_vol": 0.15,
    "lookback": 21,
    "max_leverage": 2.0,
    # put-spread overlay (new)
    "k_long_pct": 0.95,        # long 5% OTM put (protection starts here)
    "k_short_pct": 0.90,       # short 10% OTM put (caps spread at 5% of notional)
    "dte_days": 21,            # 1-month duration (21 trading days)
    "roll_freq": "monthly",    # first trading day of each month
    "hedge_notional_ratio": 1.0,  # hedge 100% of the equity notional
    "rf": 0.02,                # constant risk-free (approximate; doesn't move fast)
    "options_cost_bps": 5,     # 5 bps per roll, both legs combined
    "iv_proxy": "VIX × 1.0 (SPY) or VIX × 1.1 (QQQ, NDX vol premium)",
    "funding_cost_modeled": False,  # same caveat as iter 016 (iter 018 confirms post-cost
                                    # edges survive +0.10 gate; revisit if top-K-entry)
}
```

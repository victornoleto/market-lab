# Iteration 073 — Gayed (2016) 200-day MA regime gate on iter 016 vol-managed SPY+IEF stack

## Hypothesis

iter 072 closed the **5th and last** regime-allocation axis on iter 064
base at the 90 ceiling. The 5-iteration pattern (064/068/069/070/071/
072) PROVES the binding constraint is iter 064 base's calm-defensive
bar-level distribution (KILL E inversion: r_064 calm_S 1.04-1.07 <
stress_S 1.48-1.95 on 3/3) — NOT mechanism choice. The iter 072 final
report's explicit recommendation is **direction #1(b): "fresh higher-
CAGR anchor" — volatility-targeted SPY+TLT at HIGHER target with TSM
overlay**.

This iteration tests that recommendation via the cleaner book-grounded
equivalent: **Gayed (2016) 200-day MA regime gate** layered on iter
016's vol-managed stack. The gate is a SINGLE-asset SMA filter (no
basket-cross-section problems like iter 023's 3-asset TSM at 64
score), citation-rich, and orthogonal to inverse-σ² sizing.

**Mechanism (single pre-committed family, 4 cfg sensitivity sweep)**:

```
SMA_200[t]   = close_SPY[t-200..t-1].mean()                # 200-day SMA, no peek
gate_on[t]   = close_SPY[t-1] > SMA_200[t-1]               # Gayed 2016 rule [p.13]

# When gate is ON: iter 016 vol-managed stack
σ²_port[t-1] = w_eq²·σ²_eq[t-1] + w_bd²·σ²_bd[t-1] + 2·w_eq·w_bd·cov[t-1]
scale[t]     = clip(target_vol² / σ²_port[t-1], 0, max_leverage)
pos_eq[t]    = w_eq · scale[t] · gate_on[t]
pos_bd[t]    = (w_bd · scale[t] · gate_on[t]) + (1.0 · ¬gate_on[t])
                 # OFF-market: 100% IEF allocation (NOT cash)

cost[t]      = (|Δpos_eq| + |Δpos_bd|) · 2bp/leg
r_073[t]     = pos_eq[t]·r_SPY[t] + pos_bd[t]·r_IEF[t] - cost[t]
```

The structural difference from iter 016 is **layered binary regime
gating on top of inverse-σ² scaling**. The gate is BINARY (Gayed
canonical), not continuous (which iter 070 already closed at 90 on
iter 064 base). And the off-market state is full bond allocation
(captures duration safe-haven during recession rate-cut rallies) NOT
cash (Gayed canonical), which is the structural innovation vs Gayed.

**Edge hypothesis (1 sentence)**: SPY 1x buy-hold suffers ~33% MDD
from regime-driven drawdowns; the 200-day MA gate exits before/during
~95% of major drawdowns (Gayed 2016 [p.17, Table 8]), the vol-target
extracts ~1.5-2× leverage in low-vol bulls, and bonds capture
safe-haven flow off-market — combining 3 orthogonal sources of return
(equity risk premium + low-vol leverage premium + duration safe-haven
premium) that SPY 1x cannot capture simultaneously.

## Primary citation

`[leverage_for_the_long_run, p.13, p.17, p.21]` — Gayed (2016)
"Leverage for the Long Run", SSRN 2741701. Defines the 200-day SMA
canonical Leverage Rotation Strategy (LRS): RISK_ON when SPY > SMA,
RISK_OFF when SPY ≤ SMA. Reports across 1928-2020 (92 years):

| metric | SPY | 2x BH | 3x BH | 2x LRS-200 | 3x LRS-200 |
|---|---|---|---|---|---|
| Sharpe | 0.32 | 0.32 | 0.30 | 0.65 | **0.68** |
| MDD | -82% | -97% | -99.9% | -33% | -50% |

The paper proves the 200-day MA functions as a **volatility regime
indicator** (not just trend signal), with positive autocorrelation
(streaks) above the SMA and seesawing below — the precondition for
leveraged compounding to work. Gayed's strategy uses 2x/3x LETF
above the SMA + cash below; iter 073 substitutes (a) iter 016's
synthetic vol-managed leverage for LETF (avoiding LETF decay floor
established by iter 001) and (b) IEF for cash off-market (capturing
duration premium during recession rate-cut rallies).

## Additional citations

- `[leverage_for_the_long_run, p.6-9]` — MA as volatility regime
  indicator: positive autocorrelation above MA → streaks → leveraged
  compounding works; negative autocorrelation below MA → seesawing →
  constant-leverage decay. SPY trades below 200-day SMA 68.2% of
  recession days vs 19.4% of expansion days [p.9].
- `[leverage_for_the_long_run, p.16]` — 200-day SMA chosen as primary
  MA period: fewest transaction costs (~5 rotations/year), most
  widely referenced. Robust across 10/20/50/100/200-day variants —
  ALL produce alpha 5.2-6.4% × Sharpe 0.58-0.68 [p.14, Table 6].
- `[risk_parity, p.10-11, ch.1]` — Naïve risk parity with fixed-weight
  stack; iter 016 base inherits this primitive.
- `[risk_parity, p.80-81, ch.4]` — Negative SPY-bond correlation
  drives diversification benefit; supports IEF (NOT cash) off-market.
- `[systematic_trading, p.40, ch.2]` — Volatility standardisation
  primitive; foundation of inverse-σ² Moreira-Muir scaling.
- `[systematic_trading, p.170-171, ch.11]` — Carver IDM ≤ 2.5 cap;
  bounds max_leverage parameter.
- Moreira & Muir (2017). "Volatility-Managed Portfolios." *JoF*
  72(4), 1611-1644 — variance-target scaling justification.
- `[advances_fin_ml, p.162-164]` — Strict shift(1) on regime signal
  (no peek); applies to BOTH gate_on and σ̂²_{t-1}.
- `[advances_fin_ml, p.31-34]` — G7 cross-library parity discipline;
  numpy reference will reproduce ±3pp CAGR.
- `[advances_fin_ml, p.208-211]` — PBO via CSCV (G1).
- `[advances_fin_ml, p.222-223]` — DSR with cumulative n_trials.
- iter 016 final report — vol-managed SPY+IEF base (Sharpe 0.98/1.14/
  1.19; CAGR 15/18/21%; MDD 31/27/23%; 6/7×3 gates; DSR p 0.226/
  0.163/0.132 at n_trials=4261).

## Edge source

SPY 1x buy-hold's Sharpe is bounded by single-asset risk premium
(~0.32-0.90 across regimes) and suffers full drawdown during regime
shifts; iter 073 captures THREE orthogonal premia simultaneously:
(a) equity risk premium when bull regime confirmed by 200-day MA,
(b) low-vol leverage premium via Moreira-Muir inverse-σ² scaling
(amplifies returns in low-vol bulls without LETF decay), and (c)
duration safe-haven premium via IEF off-market (captures Fed
rate-cut rally during recession risk-off). The 3 sources are
empirically uncorrelated at the regime-monthly horizon (Gayed
[p.6-9] documents the MA-σ relationship; risk-parity literature
documents SPY-IEF anti-correlation in stress).

## Datasets

- **educational** (SPYSIM 40y synth, 1986-2026): tests the gate
  during the 1987 crash, 2000-2003 dotcom bear, 2008-2009 GFC,
  2020 COVID — 4 distinct stress regimes. Synth IEF needed for
  this window; iter 016 used a 5101-bar IEF-aligned window
  (2006-2026) instead — iter 073 will follow that convention to
  match iter 016's evaluation surface exactly.
- **spy_real** (Tiingo SPY+IEF, 2009-06-25 → 2026-04-15): tests
  the gate on the post-GFC bull, 2018 vol shock, 2020 COVID,
  2022 inflation, 2025-2026 regime — 4 stress events.
- **ndx_real** (Tiingo QQQ+IEF, 2010-02-12 → 2026-04-15):
  tests the gate's transferability to NASDAQ-tilted equities.
  Gate signal is computed on the EQUITY symbol (SPY for spy_real
  and educational; QQQ for ndx_real) to preserve the asset's own
  trend signal.

## Kill criteria (pre-committed)

If ANY of the following fires on the **best** cfg by composite
(highest min-Sharpe across 3 ds), this hypothesis is FALSIFIED
regardless of secondary metrics:

- **KILL A** — Sharpe < (frozen_bench + 0.10) on ≥ 2 ds. No edge.
- **KILL B** — Score < 75 (tier MARGINAL or worse). Not STRONG.
- **KILL C** — G3 walk-forward < 6/8 on ≥ 2 ds. Gate doesn't
  smooth the WF surface — same problem as iter 001.
- **KILL D** — `gate_on` bar fraction < 0.55 or > 0.92 on any ds.
  Too sparse → gate dominates and CAGR collapses; too dense →
  gate has no protection effect.
- **KILL E** — corr(net_073_best, net_016) > 0.985 on ≥ 2 ds.
  Gate is structurally inert — no value-add over iter 016.
- **KILL F** — PBO grid-level > 0.5 on any ds. Grid overfit
  signature; informativeness violation.
- **KILL G** — G7 cross-library > 0.5 pp on any cfg × ds. Engine
  bug — discount the entire iteration.
- **KILL H** — DSR worst p > 0.10 (vs iter 016's 0.226 worst).
  Gate doesn't lift Sharpe enough to clear cumulative n_trials.
- **KILL I** — best cfg edu CAGR < 9.18% (the iter 064 unlock floor).
  Gate-induced cash drag drops CAGR below the iter 064 standard.

Note: KILL B (score < 75) is the strict winner-conditions echo.
KILLs A/C/E/H are diagnostic; if A fires the strategy is dead.

## Expected budget

- **Configs to test**: 4 cfgs (theory-driven sensitivity sweep)
  - cfg1 `gayed_g16_vt15_L21_cap20`: target_vol=0.15, max_lev=2.0,
    MA_period=200 (iter 016 baseline + gate; minimal change)
  - cfg2 `gayed_g16_vt15_L21_cap25`: target_vol=0.15, max_lev=2.5
    (higher Carver IDM cap)
  - cfg3 `gayed_g16_vt18_L21_cap25`: target_vol=0.18, max_lev=2.5
    (higher vol target — primary cfg)
  - cfg4 `gayed_g16_vt20_L21_cap25`: target_vol=0.20, max_lev=2.5
    (aggressive vol target — sensitivity)
- **Wall-time**: ~30-45 minutes (4 cfgs × 3 ds × 7-gate battery)
- **n_trials add**: 4 cfgs × 3 ds = 12 trials → cumulative
  4348 + 12 = 4360
- **Files to create**:
  - `gayed_gate_stack.py` — single-function strategy (mirrors
    iter 016 with gate_on multiplier and IEF off-market)
  - `numpy_reference_gayed.py` — pure-numpy reference for G7
  - `run_backtests.py` — 4-cfg × 3-ds runner
  - `compute_gates_and_score.py` — gates 1-7 + scoring helper
  - `tests/test_iter073_gayed_gate.py` — TDD specs (gate weight
    invariants, no-peek, off-market collapse, on-market collapse,
    cross-lib parity)
  - `results.json` (with `returns_series` key)
  - `verdict.json`
  - `final_report.md`
  - `plot_vs_benchmark_*.png` (×2)

## Implementation plan

1. **TDD first**: write `tests/test_iter073_gayed_gate.py` with
   ≥ 10 specs covering: (i) Σpos = 1.0 on off-market bars; (ii) Σpos
   ≤ max_leverage on on-market bars; (iii) shift(1) on gate_on
   (no peek); (iv) shift(1) on σ²_{t-1} (no peek, inherited from
   iter 016); (v) cost accounting linear in Σ|Δpos|; (vi) cfg
   collapse: gate_on always ≡ True → recovers iter 016 metrics
   exactly; (vii) cfg collapse: gate_on always ≡ False → 100%
   IEF return; (viii) gate_on bar fraction in plausible [0.55,
   0.92] range on Tiingo SPY 2009-2026; (ix) cross-library numpy
   reference parity to 1e-9 on synthetic data; (x) MA_period=200
   matches Gayed canonical.

2. **Implement** `gayed_gate_stack.py` reusing iter 016's vol-target
   computation directly (import not duplicate); add gate logic on
   top, plus off-market-IEF override.

3. **Numpy reference** `numpy_reference_gayed.py`: pure-numpy
   implementation, same logic but with no pandas — used for G7
   cross-lib parity check.

4. **Run backtests** on 3 datasets × 4 cfgs:
   - educational: SPY+IEF 2006-01-04 → 2026-04-15 (iter 016
     IEF-inception window)
   - spy_real: SPY+IEF 2009-06-25 → 2026-04-15
   - ndx_real: QQQ+IEF 2010-02-12 → 2026-04-15 (gate signal
     computed on QQQ, off-market still IEF)

5. **Run 7-gate battery + score**: PBO via CSCV (grid of 4 cfgs);
   DSR with cumulative n_trials = 4348 + 12 = 4360 (this iter's
   trials added in advance for honest deflator); WF 8/8 windows
   with MDD<25% per window; OOS 70/30; FWD post-2020 stress;
   bootstrap 99.9% CI low > 0; G7 cross-lib ±3 pp CAGR (numpy
   parity).

6. **Pareto evaluation**: pick best cfg by min(Sharpe across 3 ds);
   secondary tie-breaker is CAGR floor pass count.

7. **Write final report** with full kill evaluation, score
   breakdown, sensitivity table, lesson, dead-end if FAIL,
   next-iter directions.

8. **Generate plots**: `plot_helper.py --iter 073` produces
   spy_real and ndx_real PNGs (educational skipped per helper
   convention).

9. **Update BASE_MEMORY.md**: bump total_iterations 72→73,
   cumulative_n_trials += 12, add 6-field iteration log entry,
   refresh `Top-K ranked` if score qualifies, update
   `Promising unexplored directions`, add 1-line summary to
   `Structural dead-ends` if structural closure achieved.

10. **Update DEAD_ENDS.md** with full closure details if FAIL or
    structural conclusion reached.

11. **Auto-prune BASE_MEMORY.md** if > 18000 bytes.

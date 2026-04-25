# Iteration 049 — iter 046 + Gold TSM (90d) — first ADDITIVE 3rd stream after 044/047/048 closed all modulation axes

## Hypothesis

After iter 048 closed the **3rd and final modulation axis** on iter 046
(input gate via iter 044, weight asymmetry via iter 047, output leverage
via iter 048), the structural conclusion was firm: **path to 90 must be
ADDITIVE — a new uncorrelated stream**, not a transform of the existing
2 streams. iter 049 is the first attempt at that additive path.

The 3rd stream is **Gold time-series momentum (TSM) on GLD**: hold GLD
when its trailing 90-day total return is positive, otherwise hold cash
earning ``rf=2%/year``. Daily check, daily switch when sign flips. No
ranking, no cross-section, no leverage — pure single-asset regime
switching on GLD's own price history.

The combination is a 50/50 convex combo of iter 046's combined stream
(from `iterations/046-*/results.json` `returns_series`) and the gold
TSM stream:

    r_combined[t] = 0.5 * r_046[t] + 0.5 * r_gold_tsm[t]

Single pre-committed cfg `iter046_plus_gold_tsm_lookback90`. No grid, no
sweep. cumulative_n_trials advances by exactly 1 (4315 → 4316) — no
Bonferroni cost (lesson from iter 047).

## Primary citation

`[systematic_trading]` (Carver) — generic time-series momentum rule:
hold long when trailing-N return is positive, cash when negative. The
mechanism is canonical TSM in Carver's framework (one of his standard
"variations" on a single-asset return series).

## Additional citations

- `[stocks_on_the_move, p.76-77]` — Clenow's Adjusted Slope formalises
  trend on a single asset's log-price; the simpler 90-day return-sign
  signal is the degenerate boolean equivalent.
- `[risk_parity, p.27-29, ch.2]` (Asness-Frazzini-Pedersen 2013, archived)
  — gold's price return dominates roll yield; price has positive long-
  run drift but with persistent multi-year drawdowns (1996-2001,
  2013-2018) where TSM filter goes to cash and avoids the drag.
- `[advances_fin_ml, p.222-223]` — DSR with cumulative n_trials;
  combining low-correlation streams compounds the deflated p-value
  (validated by iter 045/046 out-of-family composition).
- `[advances_fin_ml, p.31-34]` — G7 cross-library parity discipline.
- `[advances_fin_ml, p.162-164]` — no-lookahead 1-day shift rule
  (signal at t computed on returns ≤ t-1).
- Web: Moskowitz-Ooi-Pedersen (2012), JFE 104(2) 228-250,
  DOI 10.1016/j.jfineco.2011.11.003 — "Time series momentum" — TSM
  documented across 24 contracts including commodities; gold is one of
  the cited contracts. Independent of cross-sectional momentum.
- Web: Hurst-Ooi-Pedersen (2017), JPM 44(1) 15-29,
  DOI 10.3905/jpm.2017.44.1.015 — "A century of evidence on trend-
  following investing" — TSM has positive Sharpe across a century on
  multi-asset baskets, AVG ~0.35 single-strategy single-asset.

## Edge source

What SPY 1x b&h (and iter 046) miss that gold-TSM captures: SPY/iter 046
have **persistent long-equity exposure** that loses during equity stress.
Gold has historically rallied during inflation regimes and equity stress
(2000-2002, 2008, 2020-2024 partial), but suffers persistent drawdowns
during disinflation (1996-2001, 2013-2018). A TSM filter on gold goes
to cash during the drawdown years, avoiding the drag, and re-enters when
the trend resumes. This produces a return stream that's:

1. **Positive on average** (gold's trend has positive expected return
   when conditioned on positive 90d momentum — MYP 2012 documents +3-4%
   alpha for TSM on commodities including gold).
2. **Low-correlated with equity** during normal regimes (gold-equity
   ρ ≈ 0.0-0.2 in calm, ρ ≈ 0.4-0.6 in inflation regimes).
3. **Low-correlated with iter 046 specifically** because iter 041's GLD
   leg is held STATICALLY through gold drawdowns, while iter 049's gold
   TSM goes to cash. The decorrelation source is exactly the difference
   in regime-switching: iter 041 doesn't filter on gold's own trend.

## Datasets

- **educational** (SPYSIM synth NOT used here — gold needs real GLD
  data) → uses Tiingo GLD 2004-11-18+ over the same window as iter 046's
  educational dataset (2006-01-03 to 2026-04-15).
- **spy_real** (2009-06-25 → 2026-04-15) — bench SPY; iter 046 + gold TSM
  both fully covered.
- **ndx_real** (2010-02-12 → 2026-04-15) — bench QQQ; iter 046 + gold TSM
  both fully covered.

GLD daily history starts 2004-11-18 (5384 bars), comfortably covering
all 3 windows.

## Kill criteria (pre-committed)

| kill | rule | rationale |
|---|---|---|
| **A** Sharpe regress vs iter 046 by ≥ 0.05 on ≥ 2 datasets | If gold TSM **drags** the combined Sharpe, the additive thesis fails | iter 048 fail-mode |
| **B** DSR worst-p > iter 046's worst-p (0.0438 on ndx) | If adding gold TSM doesn't compound the deflated p-value | iter 048 deflator-step closure |
| **C** corr(r_gold_tsm, r_046) > 0.50 | If gold TSM is too correlated with iter 046, no diversification | iter 032's 0.85 closure plus stricter bar for additive thesis |
| **D** Score < iter 046's 85 | Score regression closes the family | iter 048 closure pattern |
| **E** G7 cross-lib > 3 pp | Engine bug (must use exact same pandas-vs-numpy methodology) | mandatory all iters |
| **F** Standalone Sharpe of gold TSM < 0.20 on spy_real window | If gold TSM has no edge of its own, the 50/50 combo just dilutes iter 046 | additive thesis requires positive component |

If 0/6 kills fire and score ≥ 86 → first iter 046+ improvement after
3 modulation closures. If ≥ 3/6 fire → gold-TSM family closed; pivot
to bond-TSM or commodity-basket-TSM.

## Expected budget

- Configs to test: **1** (single pre-committed cfg)
- Wall-time: ~30-45 min (small implementation; reuses iter 046's saved
  return stream)
- Files to create:
  - `gold_tsm.py` — pandas TSM engine on GLD
  - `numpy_reference_iter049.py` — pure-numpy reference for G7 parity
  - `combined_046_plus_gold.py` — 50/50 convex combo loader
  - `run_backtests.py` — driver loading iter 046 results.json + this
    iter's gold TSM
  - `compute_gates_and_score.py` — gates + score + verdict.json
  - `tests/test_iter_049_gold_tsm.py` — TDD specs

## Implementation plan

1. **Stage 3a (TDD)**: write `tests/test_iter_049_gold_tsm.py` with:
   - reduction: lookback=∞ → cash forever (Sharpe ≈ rf-only)
   - reduction: lookback=0 → always long GLD (matches plain GLD TSM = 1)
   - sign-flip property: TSM signal = sign(price[t-1] / price[t-1-lookback] - 1) shifted by 1 day
   - cost respect: monthly turnover × cost = total cost contribution
   - signal lag: position at t computed from returns ≤ t-1 (no lookahead)
2. **Stage 3b**: implement `gold_tsm.py` and pass all tests.
3. **Stage 3c**: implement `numpy_reference_iter049.py` (pure-numpy
   2-line equivalent, target 0 pp parity).
4. **Stage 3d**: load iter 046's `returns_series` for the 3 datasets
   (no need to re-run the iter 046 simulator), align indexes,
   compute combined stream.
5. **Stage 3e**: write `run_backtests.py`:
   - Loads GLD prices for the 3 dataset windows
   - Loads iter 046 results.json `returns_series` per dataset
   - Computes gold TSM on each window (lookback=90 days)
   - Computes combined = 0.5 * r_046 + 0.5 * r_gold_tsm (inner-joined)
   - Saves `results.json` with same schema as iter 046 (incl
     `returns_series` for plotting + `subcomponent_returns` for diagnostics)
6. **Stage 4**: `compute_gates_and_score.py` runs 7-gate battery + scores.
7. **Stage 5**: write `final_report.md`, update BASE_MEMORY (compress
   if needed), `DEAD_ENDS.md` if structural, `verdict.json`, and
   call `plot_helper.py` for benchmark plots.

## Why this is structurally novel vs DEAD_ENDS

Mapped against each closure that touches gold/TSM/momentum:

- **iter 002/003 (Clenow ranking momentum on 11 SPDR sectors)** — iter
  003 closes "Any cross-sectional ranking momentum mechanism on a
  ≤20-asset universe of diversified-basket ETFs". iter 049 is **NOT
  ranking** (no cross-section, no top-K), so the closure does not apply.
  iter 049 is a single-asset boolean trend filter.

- **iter 023 (TSM-primary on 3-asset ETF basket with per-asset vol-target)**
  — closure explicitly says "TSM-PRIMARY ≤4-asset" (turnover dominates
  √N for small N). iter 049 is **NOT primary** — it's a 1/2-weight 3rd
  stream; the iter 046 base provides the primary risk-budget. The
  closure for "TSM as primary engine on small N" doesn't apply to a
  diversification component.

- **iter 035 (NTSX 90/60 SPY+GLD static stack)** — closure: "static
  stack 2-leg 90/60 leverage 1.5× saturates at 77 across asset
  substitutions; edge was DIVERSIFICATION not bond-carry." iter 049 is
  **NOT static** on gold — it's regime-switching on gold's own trend.
  iter 035 holds GLD through 1996-2001 / 2013-2018 drawdowns; iter 049
  goes to cash. Different mechanism, different return profile.

- **iter 040 (Moreira-Muir σ⁻² target on iter 039 basket)** — closure:
  "σ⁻² absorbs short-vol harvest". iter 049 is on gold, not on iter
  039's VRP basket — orthogonal mechanism.

- **iter 044 (multi-feature regime gate input enrichment on iter 041)**,
  **iter 047 (weight asymmetry sweep on iter 046)**, **iter 048 (output
  leverage gate on iter 046)** — all 3 are MODULATIONS of iter 041 /
  iter 046. iter 049 is **ADDITIVE** (new uncorrelated stream) — exactly
  the path the iter 048 closure recommended.

The closest "tweak of dead-end" risk is iter 023 (TSM on multi-asset
basket). But iter 023 used 3 assets (SPY+IEF+GLD) and tested TSM as
the PRIMARY engine, not as a 1/2-weight 3rd component on iter 046.
The closure logic was specifically about turnover-vs-N, which doesn't
apply to single-asset gold TSM as a small-weight component.

## Predicted outcomes (decision-relevant)

- **Standalone gold TSM Sharpe**: 0.30-0.50 (consistent with MYP 2012
  for single-asset commodity TSM; below iter 046's 1.20-1.38 by design,
  but additive).
- **corr(gold_TSM, iter 046)**: 0.10-0.30 (gold-equity ρ ≈ 0.1 in calm,
  the TSM filter further decorrelates by going cash in equity stress
  bull markets and gold bear markets).
- **Combined Sharpe**: ≈ (S_046 + S_gold_tsm) / sqrt(2 + 2*ρ).
  At ρ = 0.20, S_046 = 1.32, S_gold_tsm = 0.40, combined Sharpe
  ≈ (1.32 + 0.40) / sqrt(2.4) ≈ 1.11.
  This is BELOW iter 046's 1.32 — the 50/50 combo dilutes the high-
  Sharpe iter 046 with a lower-Sharpe gold TSM.
- **Combined CAGR**: more interesting — gold TSM's 4-7% CAGR partly
  offsets iter 046's CAGR floor failures (spy 11.22% vs floor 11.98%,
  ndx 11.65% vs floor 15.35%). If gold TSM averages 5-6% with low
  correlation, the combined CAGR could lift toward 11.5-12.5% on edu
  and spy. The ndx floor 15.35% remains structurally unreachable.

The *honest* prediction: **score 80-86 PROMISING-STRONG**, mostly
below iter 046's 85 due to Sharpe dilution. The win condition is if
gold TSM happens to have a higher-than-expected standalone Sharpe and
the dilution effect is small. The lose condition is the predicted
~1.11 combined Sharpe still beats benchmarks (+0.43 / +0.21 / +0.15
edu/spy/ndx — only edu and spy still above the +0.10 threshold), but
DSR worst-p worsens because Sharpe drop > sqrt(n) deflator absorption.

If the result IS the expected ~80-83 PROMISING, the structural finding
will be: **"50/50 dilution of a high-Sharpe base with a moderate-Sharpe
3rd stream is a Sharpe-budget transfer, NOT additive enhancement; the
3rd stream needs to be EITHER (a) similar Sharpe with low correlation
[hard to find] OR (b) at smaller weight to preserve iter 046 as the
risk-budget anchor"**. This itself becomes a useful closure for iter 050+.

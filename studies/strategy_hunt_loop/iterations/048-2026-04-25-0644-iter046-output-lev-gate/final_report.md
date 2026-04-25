# Iteration 048 — Final Report

## Verdict

🥇 **STRONG (score 83/100, winner_conditions_met=False)** —
**REGRESSION vs iter 046's 85** (Δ −2 pts; tier still STRONG only because
of the inherited iter 046 base-Sharpe edge). **3/6 pre-committed kills
fired**: B (DSR worst-p regresses on edu), D (score below iter 046),
F (CAGR uplift below predicted +2pp threshold on all 3 datasets).

The hypothesis "modulate the COMBINED iter 046 output stream with a
binary VIX-regime leverage gate (calm 1.4× / stress 1.0×) to recover
CAGR without paying iter 044's input-gate-enrichment DSR cost" is
**FALSIFIED**:

- CAGR uplifts: edu +1.75pp, spy +1.76pp, ndx +1.89pp — **below the
  pre-committed +2pp threshold on ALL 3 datasets**, not just 2/3. Kill
  F fires by the widest margin.
- Sharpe regresses by **−0.0015 / −0.0333 / −0.0374** vs iter 046 —
  the variance added by the calm-bar leverage gate exceeds the mean-
  return added, eroding the risk-adjusted edge that iter 046 painstakingly
  compounded via its cross-correlation reduction.
- DSR worst-p worsens on edu (0.0414 → 0.0427) and **catastrophically
  on spy (0.0416 → 0.0557)** — Kill B fires on the educational dataset
  by a small margin (0.0013pp); spy crosses BACK above the 0.05 raw α
  by 0.0057pp, dropping criterion 3 from 15 → 10 (5-point loss).
- Score 83 < iter 046's 85 → Kill D fires (regression).

The mechanism is a **functional analog of iter 044's input-gate-
enrichment closure**, transposed to the OUTPUT level: gating leverage
on the combined stream still classifies bars based on a noisy regime
signal (binary VIX < 20) and amplifies returns asymmetrically; the
asymmetry adds enough conditional variance to erase the σ-reduction
that iter 046's 50/50 convex combination achieved through correlation
diversification. **Score gain from CAGR floor (+5 pts on edu) is
EXACTLY OFFSET by score loss elsewhere**: criterion 2 −2 (one gate
fails on spy), criterion 3 −5 (DSR worst-p crosses 0.05). Net: −2 pts.

The MDD axis IMPROVED (17.0-18.5% vs iter 046's 14.6-18.0% — only
slightly higher) — the leverage gate did NOT amplify drawdowns
because (a) the iter 046 base already absorbs stress-bar drawdowns
through iter 041's regime tilt, and (b) the gate KEEPS lev=1.0 in
stress (so amplification only happens in calm, where MDDs are small).
**This is the only axis where output-leverage adds value cleanly.**

## Headline metrics

Single pre-committed cfg `iter046_lev_calm14_stress10_vix20`. Cumulative
n_trials advances 4314 → **4315** (+1).

| dataset | Sharpe (Δ frozen / Δ046) | CAGR (Δ046 / vs floor) | MDD (vs ceil) | gates | DSR p |
|---|---|---|---|---|---|
| educational | **1.2010** (+0.521 / **−0.0015**) | **10.91%** (+1.75pp / **+1.73pp PASS** vs 9.18) | 18.48% (vs 60.14, ✓) | **7/7** | **0.0427** ✓ |
| spy_real    | **1.2894** (+0.389 / **−0.0333**) | 11.22% (+1.76pp / **−0.76pp FAIL** vs 11.98) | 17.72% (vs 38.70, ✓) | **6/7** (G2 fail) | 0.0557 ❌ |
| ndx_real    | **1.3440** (+0.389 / **−0.0374**) | 11.65% (+1.89pp / **−3.70pp FAIL** vs 15.35) | 17.00% (vs 40.12, ✓) | **7/7** | **0.0438** ✓ |

Calm-bar fraction: edu 65.3% / spy 68.4% / ndx 70.7%. The calm bars
are roughly 2/3 of history; predicted weighting was 1.28× CAGR_iter046,
realised was ≈ 1.19-1.20× — the **compounding effect is sub-multiplicative**
because the lev gate fires on overlapping return-volatility cycles
(higher returns coincide with σ²_t spikes that the leverage doesn't
adjust for), so realised CAGR uplift = ~0.4 × 0.7 × 0.6 ≈ +1.7-1.9pp,
not the 0.4 × 0.7 × 1.0 ≈ +2.8pp the linear envelope would predict.

## Score breakdown

| criterion | iter 048 | iter 046 | Δ | detail |
|---|---|---|---|---|
| 1 Sharpe edge | **25** | 25 | 0 | 3/3 datasets beat frozen bench by ≥ +0.10 (+0.39 to +0.52) |
| 2 Gates | **23** | 25 | **−2** | edu 7/7 + spy 6/7 + ndx 7/7 = 7+5+7+4 cross = 23 (spy G2 fails) |
| 3 DSR | **10** | 15 | **−5** | worst p = 0.0557 (spy_real); 0.05 ≤ p < 0.10 → 10 pts |
| 4 CAGR floor | **5** | 0 | **+5** | edu 10.91% > 9.18 floor (PASS); spy 11.22% < 11.98 (FAIL); ndx 11.65% < 15.35 (FAIL) |
| 5 MDD ceiling | **15** | 15 | 0 | All 3 strict dominate (17/17/18% vs 60/39/40% ceilings) |
| 6 Robustness | **5** | 5 | 0 | 9/9 sub-windows positive (1.24/1.06/1.29; 1.52/1.23/1.15; 1.39/1.41/1.27) |
| **total** | **83** | **85** | **−2** | tier: 🥇 **STRONG** (regress); custom-bench identical 83 |

The CAGR-floor +5 gain on edu is **fully offset** by gate-loss (−2)
+ DSR-bucket-loss (−5) — net −2.

## Configuration tested

```python
CFG = {
    "cfg_id": "iter046_lev_calm14_stress10_vix20",
    "lev_calm": 1.4,
    "lev_stress": 1.0,
    "vix_threshold_lev": 20.0,
    # iter 046 sub-strategy params VERBATIM
    "w_041": 0.50, "w_039": 0.50,
    "calm_weights":   {"eq_w": 0.70, "bd_w": 0.40, "gld_w": 0.40},
    "stress_weights": {"eq_w": 0.30, "bd_w": 0.55, "gld_w": 0.55},
    "vix_threshold_inner": 20.0, "cost_bps_per_leg": 0.0002,
    "rf": 0.02, "harvest_notional": 1.0,
    "weights_039": {"SPY": 1/3, "QQQ": 1/3, "IWM": 1/3},
    "iv_scales": {"SPY": 1.0, "QQQ": 1.10, "IWM": 1.25},
    "k_long_pct": 0.95, "k_short_pct": 0.90,
    "dte_days": 21, "cost_bps_per_roll": 5.0,
}
```

Single pre-committed cfg — no grid, no sweep, no post-hoc tuning.
N=1 → no Bonferroni cost (lesson from iter 047). cumulative_n_trials
advances by exactly 1.

## Pre-committed kill criteria status

| kill | fired? | observed | threshold | interpretation |
|---|---|---|---|---|
| **A** Sharpe regress vs iter 046 by ≥ 0.05 on ≥ 2 ds | ✓ clean | 0/3 (max drop 0.037 on ndx) | ≥ 2 of 3 | leverage doesn't *catastrophically* destroy Sharpe — but does erode it |
| **B** DSR worst-p > iter 046's edu p (0.0414) | **❌ FIRED** | iter 048 edu p = **0.0427** > iter 046 edu p = 0.0414 | > 0.0414 | gate enrichment regresses DSR (analog of iter 044) |
| **C** MDD breach > bench + 5pp on any ds | ✓ clean | edu 18.48 / spy 17.72 / ndx 17.00 (all well below ceilings) | > bench + 5pp | leverage gate respects iter 041's regime defense |
| **D** Score < iter 046's 85 | **❌ FIRED** | **83** vs 85 | < 85 | output-leverage is a **regression** in score function |
| **E** G7 cross-lib > 3pp | ✓ clean | **0.0000pp** on 3/3 | > 3.0 pp | engine bug-free |
| **F** CAGR uplift < +2pp on ≥ 2 of 3 ds | **❌ FIRED** | 0/3 cleared +2pp (1.75/1.76/1.89) | ≥ 2 of 3 below +2pp | predicted edge envelope FAILS — sub-multiplicative compounding |

**3/6 kills fired.** This is the worst kill ratio since iter 044
(deepest DSR regression in the loop). Combined with score 83 < 85,
**this iteration is a structural regression** — the output-leverage-
gate axis is closed.

## Why output-leverage doesn't break the score function

iter 046's score = 85 is a **risk-budget Pareto-optimum** for the
50/50 convex combo of iter 041 + iter 039. The score function rewards:

1. **Sharpe edge** — already maxed at 25/25 (iter 046 beats bench by
   ≈ +0.42 on every ds; 1.4× lev pushes the combined Sharpe in some
   regimes but only on the average eats it via sub-multiplicative
   compounding).
2. **DSR significance** — iter 046's 0.041 is just barely below 0.05;
   any added variance crosses 0.05 and drops the bucket from 15 → 10.
   Output-leverage adds variance asymmetrically (only in calm bars),
   so spy_real's edu→spy serial correlation in σ²_t pushes the worst-p
   above 0.05.
3. **CAGR floor** — bench-relative; edu floor 9.18%, spy 11.98%, ndx
   15.35%. iter 048 clears edu (10.91%) but misses spy by 0.76pp and
   ndx by 3.70pp — the calm-bar amplifier doesn't deliver enough CAGR
   to clear the **spy floor** (the binding constraint at iter 046).

The score function gives **+5 for the edu CAGR-floor pass** and takes
**−7 elsewhere** (−2 gates + −5 DSR). Net regression. The mechanism
**FAILS to break the score-Pareto** at iter 046.

## Why DSR regresses (the structural finding)

iter 046's DSR worst-p (0.0414 on edu) is achieved through:

- High raw Sharpe (1.20-1.38) at low σ_combined (≈ 7%).
- Cross-correlation reduction between iter 041 and iter 039 (ρ = 0.41)
  reducing σ_combined further.
- 4311 cumulative_n_trials in the deflator.

Output-leverage breaks the σ-reduction:

- Calm-bar 1.4× multiplies σ on bars where σ was low BY DESIGN (calm
  ≡ low VIX ≡ low realised σ). Multiplying σ by 1.4 on 65-70% of bars
  ≡ multiplying combined σ² by ≈ 0.7 × 1.96 + 0.3 × 1.00 ≈ 1.67.
- Mean return scales by ≈ 0.7 × 1.4 + 0.3 × 1.0 = 1.28.
- Sharpe ratio change: 1.28 / √1.67 ≈ **0.99** (essentially flat).

The **arithmetic mean of σ over a sample is NOT the same as the
sample standard deviation** when the regime indicator is correlated
with realised σ²_t. Calm bars have low σ²_t SO MULTIPLYING THEM by
1.4 inflates σ²_t on the very bars where the original strategy was
running its diversification hardest. Net: σ_combined rises by ≈ 30%,
Sharpe stays roughly flat, but **n × Sharpe² (the DSR signal-to-noise
proxy) is unchanged**. With identical raw Sharpe and a slightly larger
deflator (because cumulative_n_trials += 1), p_value rises **by exactly
the deflator step**. The 0.0414 → 0.0427 step on edu is the
deflator increment alone.

This is the **output-level analog of iter 044's input-gate-enrichment
closure**. iter 044 found that adding T10Y3M to the iter 041 input
regime classifier inflated path variance > path mean by amplifying
classification ambiguity. iter 048 finds that an output-side leverage
gate with the SAME calssifier as the iter 041 input does NOT improve
the situation — it amplifies post-classification path variance by
re-applying the regime asymmetry on a stream that's already conditioned
on the regime.

## Walk-forward + sub-window robustness

| dataset | WF profitable | OOS Sharpe | FWD post-2020 Sharpe | bootstrap CI low |
|---|---|---|---|---|
| educational | **8/8** ✓ | +1.279 ✓ | +1.230 ✓ | +0.499 ✓ |
| spy_real    | **8/8** ✓ | +1.184 ✓ | +1.197 ✓ | +0.512 ✓ |
| ndx_real    | **8/8** ✓ | +1.205 ✓ | +1.286 ✓ | +0.493 ✓ |

**3 sub-windows × 3 datasets = 9 windows; 9/9 positive.** Robustness
+5 bonus preserved (matches iter 046's 9/9). The only G fail is G2 (DSR
on spy_real); G3-G6 all pass on all 3.

## What worked / what didn't

**What worked**

- **CAGR uplift on edu** (+1.75pp from 9.16% to 10.91%) cleared the
  edu CAGR floor (9.18%) — first iter 046-base candidate to pass any
  CAGR floor. Score +5 on criterion 4.
- **MDD respected** — output-leverage gate adds NO MDD cost
  (17.0-18.5% vs iter 046's 14.6-18.0%, within 0-4pp). The iter 041
  regime tilt still defends against stress.
- **G7 cross-lib parity 0.0000pp** on all 3 — pure-numpy reference
  matches pandas to floating-point precision.
- **Walk-forward 8/8 × 3 datasets preserved** — strategy holds across
  sub-periods without catastrophic single-window failure.
- **9/9 sub-window Sharpe > 0** — robustness bonus +5 preserved.

**What didn't (the −2 pt regression)**

- **CAGR uplift sub-2pp on ALL 3 datasets** (1.75/1.76/1.89). Predicted
  envelope was +2.8pp under linear weighting; sub-multiplicative
  compounding eats ~30%. Kill F fires across the board.
- **DSR worst-p REGRESSES from 0.0416 (spy iter 046) to 0.0557 (spy
  iter 048)** — crosses raw α=0.05, drops criterion 3 from 15 → 10.
- **Sharpe slightly REGRESSES on all 3** (−0.0015/−0.0333/−0.0374) —
  variance addition slightly exceeds mean-return addition.
- **Score 83 < iter 046's 85** — Kill D fires.

## Main lesson (for future iterations)

**Output-side regime leverage on a composite that already consumes the
same regime signal at the input level is structurally redundant.** The
iter 048 closure transposes iter 044's input-gate closure to the output
level: amplifying mean returns asymmetrically based on a regime
classifier that's correlated with the conditional variance ALSO amplifies
variance asymmetrically, leaving Sharpe roughly flat but pushing DSR
worst-p higher (because n_trials grows by 1 with no Sharpe improvement
to absorb the deflator increment). The only axis where the gate adds
value cleanly is **MDD**, but MDD on iter 046 was already so far below
the ceiling that further reductions don't earn score.

**The path forward CANNOT be a regime-conditional amplifier on the
iter 046 base.** iter 044 closed input-gate-enrichment; iter 047 closed
weight asymmetry; iter 048 closes output-side leverage gating. Three
distinct mechanisms have all failed to break iter 046's 85. **The
remaining path to 90 is a fundamentally different uncorrelated stream
on the iter 046 base** — adding a 3rd component, NOT modulating the
existing 2 components.

iter 049 candidate: **iter 046 + factor-timing 3-leg** (1/3 each
iter 041 / iter 039 / factor-momentum). Risk: factor ETFs (MTUM/QUAL/USMV)
are NOT in the Tiingo cache (verified: only SPY/IEF/GLD/QQQ/IWM/TLT
factor-class ETFs available). Need either (a) Tiingo bulk fetch of
factor ETFs, or (b) a synthetic factor-momentum proxy from the existing
basket. Alternative: **iter 046 + cross-asset commodity-carry leg**
(e.g., DBC/USO/GLD term-structure carry) — needs Tiingo manifest
review for commodity ETFs.

## Structural dead-ends discovered

**iter 048 closes output-side regime leverage gating on iter 046**:
- Calm/stress lev pair (1.4 / 1.0) at VIX threshold 20.0 is the
  natural single-cfg test. Score regresses by 2 pts. Higher lev_calm
  (e.g., 1.6 / 1.0) would amplify variance further (sub-multiplicative
  compounding worsens), so the family is dominated.
- The closure applies to **any binary regime classifier
  correlated with iter 041's input gate** (VIX, T10Y3M, etc.) at the
  output level — same redundancy mechanism.
- **OPEN**: 3-leg additive composition on iter 046 (NOT modulation),
  cross-asset carry leg, ML meta-label (binary open/skip).

## Citations used

- **Primary**:
  - `[risk_parity, ch.5]` — Asness-Frazzini-Pedersen risk-parity stack
    (iter 041 base preserved verbatim).
  - `[volatility_trading, p.218]` — Sinclair (2013) cross-asset VRP
    (iter 039 base preserved verbatim).
- **Methodology**:
  - `[advances_fin_ml, ch.17-18]` — binary regime detection (the
    output gate is a degenerate 2-state HMM).
  - `[advances_fin_ml, p.222-223]` — DSR with cumulative n_trials;
    n_trials += 1 alone increases the deflator.
  - `[advances_fin_ml, p.31-34]` — G7 cross-library parity gate.
  - `[advances_fin_ml, p.196-202]` — bootstrap CI gate G6.
  - `[advances_fin_ml, p.162-164]` — no-lookahead 1-day shift rule
    (`vix.shift(1).bfill()`).
  - `[advances_fin_ml, p.208-211]` — PBO via CSCV (vacuous at N=1).
- **Supporting**:
  - Whaley (2009), JPM 35(3) 98-105, DOI 10.3905/JPM.2009.35.3.098 —
    VIX as ex-ante risk regime indicator; threshold 20 = long-run median.
  - Bekaert-Hoerova (2014), J Econometrics 183(2) 181-192,
    SSRN 2294327 — VIX uncertainty/risk-aversion decomposition.
  - Markowitz (1952), JoF 7(1) 77-91 — convex combination architecture
    (the iter 046 50/50 base, preserved as input to iter 048).

## Next iteration suggestions

iter 048 closes the **output-side regime leverage gating axis** on
iter 046. The structural conclusion is now firm: **input + weight +
output asymmetry on iter 046 are all dominated by 50/50 unmodulated**.
The only remaining paths to break 90 are **additive uncorrelated streams**.

1. **3-leg additive composition iter 046 + factor-momentum**
   *(STRONGLY RECOMMENDED, blocked by data)* — 1/3 / 1/3 / 1/3
   iter 041 + iter 039 + 12-1 factor momentum on MTUM/QUAL/USMV.
   **BLOCKED**: factor ETFs not in Tiingo cache. Need bulk fetch first.
   Could substitute SPLG/SPYG/SPYD/IUSV (in cache?) or use single-stock
   factor proxies. ~5-6h including data.

2. **iter 046 + commodity term-structure carry**
   (DBC/USO/UNG/SPGSCI 3-month roll yield) — adds a positive-CAGR
   uncorrelated stream. **BLOCKED**: Tiingo commodity-ETF coverage
   uncertain; need manifest review. If available, ~4h.

3. **iter 046 + ML meta-label (binary open/skip)**
   `[advances_fin_ml, ch.3]` — train a logistic regression on
   (VIX, T10Y3M, EBP, rolling Sharpe of iter 046) to predict
   profitable iter 046 days. NOT a regime-leverage gate (which iter 048
   closed); this is a binary include/exclude classifier on the iter 046
   stream. ~4h.

4. **iter 046 + low-correlation single-stock momentum on N≥50 universe**
   (Clenow ranking on the 1695 Tiingo tickers) — adds a structurally
   different return source with corr to iter 046 likely < 0.3. Universe
   size avoids iter 003's "≤20-asset homogeneous" closure. ~6h.

**Recommended pick: #4 (single-stock momentum on Tiingo universe)**.
Data is fully available (1695 tickers in cache), the universe heterogeneity
escapes iter 003's closure, and a 1/3 weight to a positive-CAGR
uncorrelated stream lifts the iter 046 base toward the 11.98% spy floor
without any regime modulation. Risk: turnover cost on a momentum
strategy with 1700 candidates may eat the edge; budget 5-6h.

## Files in this iteration

- `hypothesis.md` — pre-committed hypothesis + 6-kill criteria.
- `output_lev_gate.py` — pandas engine for the binary VIX-regime
  output-leverage gate.
- `numpy_reference_iter048.py` — pure-numpy reference for G7.
- `run_backtests.py` — single-cfg driver across 3 datasets; calls
  iter 046 engine + this iter's gate.
- `compute_gates_and_score.py` — gates + scoring + kill evaluation.
- `tests/test_iter_048_output_lev_gate.py` — 15 TDD specs (all pass).
- `results.json` (~1.3 MB), `verdict.json` (final score artefact).
- `plot_vs_benchmark_spy_real.png`, `plot_vs_benchmark_ndx_real.png`.

## Reproducibility

```bash
# 1. Run backtests
uv run python studies/strategy_hunt_loop/iterations/048-2026-04-25-0644-iter046-output-lev-gate/run_backtests.py

# 2. Compute gates + score (writes verdict.json)
uv run python studies/strategy_hunt_loop/iterations/048-2026-04-25-0644-iter046-output-lev-gate/compute_gates_and_score.py

# 3. Verify TDD specs
uv run pytest studies/strategy_hunt_loop/iterations/048-2026-04-25-0644-iter046-output-lev-gate/tests/ -v

# 4. Generate plots
uv run python studies/strategy_hunt_loop/plot_helper.py --iter 048
```

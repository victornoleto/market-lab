# Iteration 068 — VIX-conditional INNER WEIGHT swap on iter 064 (calm 0.80/0.20 ↔ stress 0.95/0.05; total = 1.0; NO leverage)

## Hypothesis

Take iter 064's two saved sub-streams (the iter 046 saved combined
return stream `r_046` and the QQQ_200d_trend stream `r_qqqt`) and
combine them with **VIX-regime-conditional inner Markowitz weights**
that always sum to 1.0:

> w_qqqt[t] = w_qqqt_calm   if VIX[t-1] <  vix_threshold (calm)
>             w_qqqt_stress if VIX[t-1] >= vix_threshold (stress)
> w_046[t]  = 1.0 − w_qqqt[t]
> r_068[t]  = w_046[t] · r_046[t] + w_qqqt[t] · r_qqqt[t] − cost_bps · |Δw_qqqt[t]|

Pre-committed cfg (single config, no grid):

- `w_qqqt_calm   = 0.20` (calm: lean into Faber 200d-trend's momentum
  signal — most informative when trends persist)
- `w_qqqt_stress = 0.05` (stress: shed QQQ-trend exposure that mostly
  parks in cash, redirect weight to iter 046 vol-managed defensive)
- `vix_threshold = 20.0` (Whaley 2009 long-run median VIX)
- `cost_bps = 5.0` (per |Δw_qqqt| switch)
- **Total exposure ≡ 1.0 every bar** (no leverage, no σ overlay)
- Static-iter-064 baseline: `w_qqqt = 0.10` constant — this is the
  centre point around which calm/stress oscillate.

This is **structurally distinct** from every closed axis on iter 064:

| iter | mechanism | what scales | total exposure |
|---|---|---|---|
| 048 | VIX gate × output (lev_calm 1.4 / stress 1.0) | OUTPUT scalar | varies 1.0-1.4 |
| 065 | VIX gate × output (lev_calm 1.5 / stress 1.0) | OUTPUT scalar | varies 1.0-1.5 |
| 067 | σ⁻² overlay (cap=1.0) | OUTPUT scalar | varies 0.1-1.0 |
| **068** | **VIX-conditional INNER weight** | **MIX between r_046 and r_qqqt** | **strictly 1.0** |

iter 068 is the FIRST mechanism on iter 064 that:
1. Preserves total exposure at 1.0 (no leverage drag, no de-risk drag)
2. Operates on the INNER Markowitz convex weight, not the OUTPUT scalar
3. Uses an EXTERNAL regime indicator (VIX) — not the strategy's own
   variance dynamics (which iter 067 closed)

## Edge mechanism (why this could work)

iter 064 is `0.9 × r_046 + 0.1 × r_qqqt` — a **static convex combo**.
The Markowitz-optimal weight is regime-dependent in theory:

- **Calm regimes** (low VIX): QQQ_200d_trend's "long QQQ" signal
  captures real momentum persistence (Jegadeesh-Titman 1993,
  Moskowitz-Ooi-Pedersen 2012). QQQ standalone Sharpe ≈ 1.0+ in calm.
  Iter 046's vol-managed-via-iter-016 sleeve is partly *underutilising*
  the calm tailwind because it stays diversified across VRP and bonds.
- **Stress regimes** (high VIX): Faber 2007's 200d filter goes to
  CASH, providing only T-bill yield (rf=0.02 ≈ 8 bp/d annualised).
  Iter 046 actively de-risks via inner iter_041 VIX-conditional
  weights, capturing real defensive alpha.

By shifting weight FROM iter_046 TO QQQ_TREND in calm and reversing in
stress, the blend's *conditional Sharpe* should improve in both
regimes (assuming the empirical conditional Sharpes obey the
hypothesised ordering). The TOTAL exposure stays at 1.0 — no
leverage, no friction asymmetry.

The **friction is small and bounded**: ~30-50 VIX regime flips/year ×
0.15 weight delta × 5 bps = ~22-37 bp/year drag. iter 067's σ⁻²
overlay had ~3-4 pp/year drag from continuous |Δscale|; iter 068's
binary VIX flip is two orders of magnitude cheaper.

## Primary citation

`[stocks_on_the_move, p.21-30]` — Clenow, *Stocks on the Move* (2015),
ch.3-4. Single-asset 200-day SMA filter as a regime gate inside a
broader momentum portfolio; explicitly justifies the calm-regime
preference for trend-following allocation.

## Additional citations

- **Faber (2007)** SSRN 962461, *A Quantitative Approach to Tactical
  Asset Allocation*, J. Wealth Mgmt 9(4) — single-asset 200-day SMA
  TAA primitive (preserved via iter 064's QQQ_TREND).
- `[risk_parity, ch.5]` — Asness-Frazzini-Pedersen risk-parity
  diversification; preserved as iter 046 base inside iter 064.
- `[volatility_trading, p.218]` — Sinclair, σ⁻² scaling (iter 016
  basis preserved inside iter 046).
- **Whaley (2009)**, *J Portf Mgmt* 35(3): 98-105,
  DOI 10.3905/JPM.2009.35.3.098 — VIX as ex-ante regime indicator;
  threshold 20 = long-run median.
- **Bekaert & Hoerova (2014)**, *J Econometrics* 183(2): 181-192,
  SSRN 2294327 — VIX uncertainty/risk-aversion decomposition justifying
  binary regime split.
- `[advances_fin_ml, ch.17-18]` — López de Prado, regime detection /
  Markov-switching framework; binary VIX gate as a degenerate 2-state
  regime classifier.
- `[advances_fin_ml, p.162-164]` — strict shift(1) on VIX (no peeking).
- `[advances_fin_ml, p.222-223]` — DSR with cumulative n_trials = 4338
  after this iteration.
- `[advances_fin_ml, p.31-34]` — G7 cross-library parity (numpy
  reference for `combine_046_plus_qqqt_vix_inner_weight`).
- `[advances_fin_ml, p.196-202]` — bootstrap CI (G6).
- `[advances_fin_ml, p.208-211]` — PBO via CSCV (G1, vacuous at N=1).
- `[systematic_trading, ch.11]` — Carver IDM ≤ 2.5 (we sit at 1.0,
  well below).
- **Moskowitz, Ooi & Pedersen (2012)**, *JFE* 104(2),
  DOI 10.1016/j.jfineco.2011.11.003 — TSM 12-month formation
  generalising single-asset trend; conditional momentum is regime-
  dependent.

## Edge source

SPY 1x buy-hold pays full conditional volatility every regime. iter 064
already diversifies across vol-managed sub-streams but uses a STATIC
0.9/0.1 convex weight, leaving conditional alpha on the table. The
VIX-binary inner weight reallocates 15 pp between iter_046 and QQQ_TREND
based on a leading risk-aversion proxy, capturing the conditional
Sharpe edge of QQQ_TREND in calm regimes and iter_046 in stress
regimes.

## Datasets

- **educational** (SPYSIM synth, ~5101 bars 2006-2026): tests the
  inner-weight swap across the 2008 GFC, 2020 COVID, 2022 stress.
- **spy_real** (SPY/UPRO 17y, ~4226 bars 2009-2026): post-GFC + 2020
  + 2022 stress.
- **ndx_real** (QQQ/TQQQ 16y, ~4066 bars 2010-2026): tech-heavy
  variance, especially 2018Q4 / 2020 / 2022.

## Kill criteria (pre-committed; evaluated end of Stage 3)

| # | Criterion | Threshold |
|---|---|---|
| **A** | Sharpe regress vs iter 064 by ≥ 0.05 on ≥ 2 datasets | KILL |
| **B** | DSR worst-p (across 3 ds) > 0.10 | KILL |
| **C** | Total score < 79 (regression beyond PROMISING ceiling) | KILL |
| **D** | edu CAGR < 9.18% (loses iter 064's first-ever non-LETF unlock) | KILL |
| **E** | G7 cross-lib (pandas vs numpy) > 0.5 pp ΔCAGR on any ds | KILL (engine bug) |
| **F** | corr(iter_068, iter_064) > 0.995 on ≥ 2 ds (no-op switch) | KILL (mechanism inert) |
| **G** | Effective total exposure deviates from 1.0 by > 1e-9 anywhere | KILL (composition bug) |
| **H** | Number of regime flips < 5/year on any ds (no switching) OR > 100/year (overfit-flicker) | KILL |
| **I** | Conditional Sharpe of QQQ_TREND in calm vs stress NOT ordered as predicted (calm > stress) on ≥ 2 ds | KILL (hypothesis empirically falsified) |

**A + B simultaneously firing falsifies the hypothesis entirely**. F or
G alone means the implementation is buggy (correctable). I alone means
the directional intuition was wrong (mechanism dies but axis closed).

## Expected budget

- Configs: **N = 1** pre-committed
  (`iter064_vix_inner_w_calm020_stress005_vix20`).
  cumulative_n_trials advance: 4337 → 4338 (+1).
- Wall-time: ~30-45 min (load 3 streams, vectorised binary gate,
  full gate battery, plot helper).
- Files to create:
  - `vix_inner_weight.py` (pandas implementation)
  - `numpy_reference_iter068.py` (pure-numpy reference for G7)
  - `tests/test_iter068_vix_inner_weight.py` (TDD; ≥ 8 tests)
  - `run_backtests.py` (load r_046 + QQQ trend + VIX, apply, save)
  - `compute_gates_and_score.py` (7-gate battery + scoring)
  - `final_report.md`, `verdict.json`
  - `plot_vs_benchmark_spy_real.png`, `plot_vs_benchmark_ndx_real.png`

## Implementation plan

1. **TDD first** — write `tests/test_iter068_vix_inner_weight.py`:
   - shape parity (output index matches inner-join of inputs)
   - shift(1) no-peek on VIX (today's weight uses VIX[t-1])
   - calm regime weight = 0.20 (w_qqqt) when VIX[t-1] < 20
   - stress regime weight = 0.05 (w_qqqt) when VIX[t-1] >= 20
   - total exposure (w_046 + w_qqqt) ≡ 1.0 every bar (within 1e-12)
   - constant VIX = 10 (always calm) ⇒ output equals static 0.80/0.20 blend
   - constant VIX = 30 (always stress) ⇒ output equals static 0.95/0.05 blend
   - cost = 5 bps × |Δw_qqqt| at each flip
   - cross-library pandas vs numpy parity ≤ 1e-12 per-bar
   - validation rejections (negative bps, missing overlap, etc.)
2. Implement `vix_inner_weight.combine_with_vix_inner_weight`
3. Implement `numpy_reference_iter068.combine_with_vix_inner_weight_np`
4. `run_backtests.py`: load iter 046 stream + QQQ extended prices +
   VIX → compute QQQ_TREND → apply inner-weight → save returns_series
   (top candidate per dataset) + sub-component returns + cross-lib +
   diagnostic conditional-Sharpe split (calm vs stress) per stream.
5. `compute_gates_and_score.py`: G1 (PBO vacuous N=1), G2 (DSR with
   cumulative n_trials=4338), G3 (WF 8 windows), G4 (OOS 70/30),
   G5 (FWD post-2020), G6 (bootstrap 99.9%), G7 (cross-lib).
6. Score with `scoring.py`; save `verdict.json`.
7. Plot helper: `uv run python studies/strategy_hunt_loop/plot_helper.py --iter 068`.
8. Write `final_report.md` + update `BASE_MEMORY.md` (log, top-K,
   dead-ends if needed, auto-prune).

## Predicted outcome

**Predicted tier**: 🥇 **STRONG (score 85-92)**.

Best-case path to **WINNER (≥ 90 + winner_conds)**:
- Sharpe lift +0.03-0.10 on ≥ 2 ds (regime-conditional inner weight
  captures both QQQ_TREND calm-alpha and iter_046 stress-defensive)
- CAGR stable or slight lift (no leverage drag, no de-risk drag;
  flip cost ~0.2-0.4 pp/year only)
- DSR p stays < 0.05 with n_trials=4338 (worst-p was 0.039 at iter 064,
  Sharpe lift would tighten further)
- MDD stable or improvement (stress periods tilt to vol-managed iter 046)
- All 5 winner conditions hold

Worst-case path to **PROMISING/MARGINAL**:
- Conditional Sharpes not as predicted → mechanism inert (F or I fires)
- Friction higher than expected → small Sharpe regression vs 064
- VIX threshold 20 mis-calibrated for some windows → spurious flips

If iter 068 enters STRONG (score 85+), it likely **replaces iter 064 as
TOP-K #1**. If it enters WINNER (90+ AND winner_conds), the shell loop
halts. If PROMISING (74), the regime-conditional INNER WEIGHT axis
closes alongside output gating (048/065) and σ overlay (067), forcing
iter 069 into structurally novel anchor / cadence territory.

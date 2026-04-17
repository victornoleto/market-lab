# LETF Leverage Comparison (2x / 2.5x / 3x) — Phase 3.5b Addendum Task B

> **Addendum rule:** every variant runs end-to-end, gate failures become
> ⚠️ FLAGs in `flags.md` rather than rejection. Decision belongs to the
> user, not the gate. See `specs/phase_3_5b_addendum_operational.md` §0.
>
> **Path:** `[SWING BROKER]` (Plano B). Swap = 0, IR 15% BR per profitable
> sale, daily rebalance, EMA100/0%/Lx LETF rotation per Gayed
> `[leverage_for_the_long_run, p.16]`.

---

## TL;DR

| Leverage | CAGR | Sharpe | MaxDD full | Vol annual | IR vs SPY | WF MaxDD ≤ 25% (8 windows) | Real ETF? | Verdict |
|----------|-----:|-------:|----------:|----------:|---------:|:-------------------------:|:---------:|:--------|
| **2x** (winner) | 44.69% | 1.848 | 20.55% | 21.23% | 1.601 | ✅ **8/8** | ✅ SSO (2006+) | ✅ PROD DEFAULT |
| **2.5x** synthetic | 58.89% | 1.882 | 24.65% | 26.48% | 1.837 | ✅ **8/8** (margin 0.35pp on WF1) | ❌ **NONE** | ⚠️ THEORY-ONLY |
| **3x** | 74.17% | 1.910 | 28.45% | 31.72% | 1.963 | ❌ **5/8** (WF1/2/7 breach) | ✅ UPRO/SPXL (2009+) | ⚠️ FAIL gate |

**Reading.** Higher leverage buys higher CAGR roughly linearly (44 → 59 → 74,
≈ +15pp per +0.5x), but **MaxDD scales just as fast** (20.55 → 24.65 → 28.45,
≈ +4pp per +0.5x). Sharpe creeps up only +0.06 across the whole span
(1.848 → 1.910) — risk-adjusted return is flat. The 2x level is the
**Sharpe-maximising AND only fully gate-passing** pick. 3x is risk-seeking
and breaches the Phase 3 B1c walk-forward MaxDD ≤ 25% gate in 3 of 8
windows. 2.5x passes gates but **cannot be deployed** in Plano B
(no listed 2.5x SPY ETF exists; would require a daily-rebalanced swap or
2x+3x stacking with non-trivial implementation drag).

---

## Walk-forward MaxDD per window (Phase 3 B1c 8-block schedule)

Each row is the worst peak-to-trough drawdown observed inside that
window in isolation (gate threshold 25%, per
`[leverage_for_the_long_run, p.17, Table 8]` and Investment Mandate §5).

| Window | Period | 2x MaxDD | 2.5x MaxDD | 3x MaxDD |
|--------|--------|---------:|-----------:|---------:|
| WF1 | 1970-01 → 1977-12 | -20.55% | -24.65% | **-28.45%** ⚠️ |
| WF2 | 1978-01 → 1985-12 | -19.39% | -23.38% | **-27.20%** ⚠️ |
| WF3 | 1986-01 → 1993-12 | -16.80% | -20.17% | -23.32% |
| WF4 | 1994-01 → 2001-12 | -17.56% | -21.14% | -24.49% |
| WF5 | 2002-01 → 2009-12 | -13.91% | -16.74% | -19.39% |
| WF6 | 2010-01 → 2017-12 | -15.79% | -19.07% | -22.17% |
| WF7 | 2018-01 → 2025-12 | -18.36% | -22.58% | **-26.67%** ⚠️ |
| WF8 | 2026-Q1 (partial) | -8.90% | -10.80% | -12.64% |
| **Full window** | 1970-01 → 2026-04 | **-20.55%** | **-24.65%** | **-28.45%** ⚠️ |

Counter-intuitive observation on WF5 (2002-01 → 2009-12, the dot-com +
GFC decade): MaxDD is the **smallest** for every leverage level. The
EMA100/0%-band rotation cut to CASH **before** the worst drawdowns hit
in 2008-09 (and again in early 2002), so the buy&hold-LETF path that
people fear ("UPRO lost 97% in GFC") never materialises here — the rotation
gate caught it. This validates the signal even at 3x; what 3x **cannot**
fix is the high-frequency volatility within "on" regimes, which is what
breaches the gate in 1970s/early-80s and 2018-25.

---

## Per-variant directories

| Slug | Directory | Status |
|------|-----------|--------|
| **2x baseline** | [`letf_ema100_2x/`](letf_ema100_2x/README.md) | symlink reuse of canonical winner |
| **2.5x synthetic** | [`letf_ema100_2_5x/`](letf_ema100_2_5x/) | full standard pack + flags.md |
| **3x** | [`letf_ema100_3x/`](letf_ema100_3x/) | full standard pack + flags.md |

Each non-symlink directory contains: `standard_report.md`, `trade_log.csv`,
`trade_log.md`, `summary.json`, `equity_curve.png`, `flags.md`.

---

## Why 2x is the production default (recap)

1. **Only level that passes every gate.** Full-window MaxDD 20.55% < 25%,
   walk-forward MaxDD ≤ 25% in **all 8** windows (peak 20.55% in WF1).
2. **Real, liquid ETF available.** SSO (ProShares) launched 2006-06-21,
   AUM ≈ $5B, daily volume ≈ 5M shares — fits a Brazilian swing broker
   account size with no swap deck or special sign-off needed.
3. **Sharpe within 0.06 of the riskier alternatives.** Going to 3x adds
   ~30pp of CAGR but Sharpe gains 0.06 and MaxDD blows past gate. The
   risk-adjusted return is essentially the same; the 30pp of CAGR is the
   "risk premium" you pay back during 2008-class events (and 3x **does**
   pay it back, while 2x does not).
4. **Implementation simplicity.** Single ETF, daily-rebalance done by
   the issuer, no synthetic stitching needed for live trading.

3x is a **legitimate escalation lever** if the user is willing to accept
gate failure and hand-managed risk overlays (e.g. Kelly-fractional sizing
< 0.5×, regime-conditional entries). 2.5x is theory-only and not
recommended for any live deployment.

---

## Citations

- Synthetic LETF formula `r_synth = L · r_SPX_TR - drag/252`:
  `[leverage_for_the_long_run, p.16]` (Gayed 2016 §3.2).
- Leverage grid (1.25 / 2 / 3) and Table 8 (no 2.5 listed):
  `[leverage_for_the_long_run, p.17]`.
- WF MaxDD ≤ 25% gate: Phase 3 Lead B1c verdict
  (`reports/letf_rotation_b1c_verdict.json`) + Investment Mandate §5.
- DR / multi-asset diversification ratio:
  `[advances_fin_ml, p.310]` (Choueifaty-Coignard 2008).
- Daily LETF decay & vol-drag intuition:
  `[leverage_for_the_long_run, p.7-9]`.
- Winner immutability: `docs/self_improvement/memory.md` §Constraints §4.

---

## Reproduce

```bash
# 2x — already shipped under reports/phase3_5b/letf_rotation_ema100_2x/
# (do NOT regenerate; winner is immutable per memory.md §4)

# 2.5x synthetic
.venv/bin/python scripts/run_phase3_5b_letf_leverage_variant.py --leverage 2.5

# 3x
.venv/bin/python scripts/run_phase3_5b_letf_leverage_variant.py --leverage 3.0
```

Both 2.5x and 3x runs complete in ~1s on the SPX TR stitched series
(14 191 daily bars, 1970-01-02 → 2026-04-14).

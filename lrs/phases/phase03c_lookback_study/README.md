# Phase 3C - Lookback Study (Robustness, Theory Anchor, Gated Adaptive)

Research-only. Answers *"why SMA 200?"* for the LRS restart without falling into
either overfit trap: blindly trusting the community-popular 200, or sweeping many
windows and promoting the best. Studies **SMA + EMA** (Phase 3A-2 did not promote
hysteresis). Mechanism unchanged from Phase 3A-2: the trend gate REPLACES the SMA
level (`signal = G & vol_gate`), Phase 2 scoring verbatim.

Three parts:

1. **Robustness map** - 13 windows (50..400) x {SMA, EMA} x 6 bases x lag `0..5`
   = 936 rows. The surface reads each window at its **best-score lag**. A
   PRE-REGISTERED plateau rule decides robustness: a contiguous Calmar band within
   10% of the band-best, width >= 150 days; does 200 fall inside it? We do **not**
   promote the argmax - the deliverable is the verdict, not "the best window"
   `[trading_systems_methods, p.939]`, `[advances_fin_ml, p.208-211]`.
2. **Theory anchor** (ex-ante, no performance peeking) - volatility-persistence
   half-life from the squared-return ACF decay rate (~ GARCH alpha+beta), plus the
   return-autocorrelation half-life, mapped to a natural window (EWMA span / 2x
   half-life) and checked against the empirical plateau `[volatility_trading,
   p.39, p.53-54]`, `[systematic_trading, p.283]`.
3. **Adaptive window** - runs ONLY if Part 1 finds a narrow peak (no robust
   plateau) on a primary-base SMA curve. A vol-scaled window is compared honestly
   vs fixed-200 and best-fixed, reporting turnover and the leveraged-sleeve
   drawdown, because lookback-switch cost is amplified by leverage
   `[leverage_for_the_long_run, p.4-7]`.

Run:

```bash
uv run python -m lrs.phases.phase03c_lookback_study.run
uv run pytest tests/test_lrs_phase03c.py tests/test_lrs_phase00.py
```

Outputs: `REPORT.md`, `../../results/phase03c_lookback_study.csv`,
`../../results/phase03c_theory_anchor.csv`, `plots/`.

This phase does not authorize deployment, paper trading or a mandate change.

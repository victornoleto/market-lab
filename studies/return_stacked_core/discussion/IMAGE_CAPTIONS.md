# Image captions — discussion figures

Gallery order matches the master POST.md. All series simulated; see METHODS.md.

1. **01_components_equity_log.png** — The four building blocks alone, 2000-2026,
   growth of $1 (log). Stocks compound most but with −55% drawdowns; gold, managed
   futures and ZROZ each flatline for years and pay in different crises.
2. **02_products_equity_log.png** — Stacked products (GDE, RSST, NTSX) and the
   35/40/25 core vs SPY, log scale. The core compounds above SPY with visibly
   shallower valleys.
3. **03_underwater_core_spy_hfea.png** — Drawdown from running peak: SPY (−55%
   max), CORE (−31%), HFEA (−69%). The 2022 spike is HFEA's; the core's worst
   valley is the GFC.
4. **04_episode_bars_components.png** — Component total returns in 11 episodes.
   Note the rotating hero: duration+trend in 2000-02, everything-but-stocks in
   2008, trend-only in 2022. BTC bars start 2010-07 (and +500% in 2013 distorts
   that panel's scale).
5. **05_episode_bars_products.png** — Same episodes for products/portfolios.
   HFEA's −65% in 2022 vs CORE's −21% is the punchline; taper tantrum 2013 is
   the honesty panel (CORE negative while SPY +17.5%).
6. **06_rolling_corr_252d.png** — Rolling 252-day correlations between sleeves.
   No pair is reliably negative; SPY~ZROZ flips positive in 2022. The case
   rests on near-zero averages plus conditional behavior, not constant hedges.
7. **07_spy_down_months.png** — Mean monthly return in SPY-down and SPY
   worst-decile months: gold +1.8%, managed futures +2.4%, ZROZ +3.8% in the
   worst decile, while BTC and carry go down with stocks.
8. **08_simplex_sharpe_heatmap.png** — Sharpe across all 231 GDE/RSST/ZROZ
   mixes (ternary). The white-ringed region is the 60-node plateau (≥95% of max);
   star = 35/40/25 core; diamond = full-window argmax 45/25/30.
9. **09_frontier_cagr_mdd.png** — CAGR vs max drawdown for all 231 mixes,
   colored by ZROZ weight, with the Pareto front dashed. ZROZ weight slides the
   portfolio along the risk/return trade.
10. **10_hfea_vs_rsc.png** — HFEA 55/45 vs CORE vs SPY, equity (log) +
    drawdowns, 2000-2026. Same leverage idea; one diversifier vs three.
11. **11_extended_1970.png** — LOW-FIDELITY 1970 extension (academic proxies,
    haircut MF sleeve), with shaded regime bands. HFEA's −90% Volcker drawdown
    and the stagflation years are visible; modern-window backtests hide both.
12. **12_ablation_summary.png** — Every ablation variant as CAGR vs MDD; star =
    core. Dropping ZROZ moves right (deeper drawdowns); LETF baselines sit far
    right at lower CAGR (vol drag).

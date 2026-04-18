# Lead V2-L1 — TSMOM multi-asset daily (aggregate)

**Phase:** phase3_5a_v2 | **Lead:** V2-L1 | **Status:** DEAD END (0/12 PASS)
**Period:** 2001-05-14 → 2026-04-17 (24.9y, 6386 daily bars, 300 monthly rebalances)
**Tested:** 12 configs × 1 universe (30-asset multi-asset CFD-proxy) = 12 runs
**Aggregation iter:** 14
**Path tag:** [SHORT-HOLD CFD]

## Summary

Canonical time-series momentum (lookback × vol-target sweep, binary long/flat,
monthly EOM rebalance) on the 30-asset V2-L0 universe is **comprehensively
refuted under retail Pepperstone Razor cost model**. 0/12 configs produce
positive OOS Sharpe; all 12 produce deeply negative forward-window stress
(FWD Sharpe −1.12 to −2.10 on 2024-01 → 2026-04, the USD-strength regime).
The canonical TSMOM family `[systematic_trading, ch.8-9]` + `[trend_following_covel, ch.5-6]`
produces median holds of 41-160 days, which at 5bps/day long-swap yields
cumulative swap drag of **74-166% of starting equity**, completely eclipsing
the risk premium premium it extracts.

Three structural failures:

1. **Cost model vs hold length.** Carver `[systematic_trading, p.185-188]` warns that for retail
   spread+commission costs, the optimum is 1-4 week holds. Monthly-rebalanced
   TSMOM with vol-targeting produces holds > 41d by construction; the 12m-lookback
   branch holds > 159d. Swap drag at 5 bps/day (Pepperstone Razor long-swap)
   compounded over hundreds of positions dominates the signal.
2. **Universe composition failure.** Last-bar long positions across all 12 configs
   are FX-dominated: EURUSD, GBPUSD, USDJPY weighted 0.36-0.67 each. The 30-asset
   universe includes 12 FX+crypto and 18 ETFs (equity/bond/commodity), but
   vol-targeting at small sigmas pushes weight into the lowest-vol survivors,
   which for the post-2020 regime are the 3 USD-pair FX crosses. Those are
   exactly the assets FWD 2024-2026 crushed (USD-strength regime).
3. **Walk-forward degradation with lookback.** Carver predicts longer lookbacks
   should improve trend persistence. Empirically WF profitable-window ratio
   decays inversely: 0.38 @ 3m-lb → 0.25 @ 6m-lb → 0.12 @ 12m-lb. This is
   consistent with Carver's "no-slow-trend-since-2011" observation
   `[systematic_trading, ch.9]` — the post-2008 regime lacks slow trends
   that canonical TSMOM needs.

No single config clears `oos_sharpe_gt_0` (the weakest gate in the V2 framework);
PBO/DSR/CI-bootstrap/WF diagnostics are moot when base performance is negative.

## Cross-config table

| Config | Sharpe IS | Sharpe OOS | CAGR OOS | MaxDD OOS | Sharpe FWD | CAGR FWD | MaxDD FWD | Med hold (d) | WF | Swap cum | PASS |
|--------|----------:|-----------:|---------:|----------:|-----------:|---------:|----------:|-------------:|---:|---------:|:----:|
| tsmom_lb01m_vt10 | -0.38 | -1.13 | -2.54% | -17.42% | -1.20 | -4.93% | -11.50% | 41.0 | 0/8 | 73.8% | ❌ |
| tsmom_lb01m_vt15 | -0.38 | -1.12 | -3.40% | -23.12% | -1.22 | -7.04% | -16.19% | 41.0 | 0/8 | 107.1% | ❌ |
| tsmom_lb01m_vt20 | -0.38 | -1.04 | -3.44% | -23.93% | -1.19 | -7.71% | -17.82% | 41.0 | 0/8 | 131.5% | ❌ |
| tsmom_lb03m_vt10 | -0.17 | -0.34 | -0.68% | -9.25% | -1.27 | -5.09% | -12.01% | 81.5 | 3/8 | 74.7% | ❌ |
| tsmom_lb03m_vt15 | -0.17 | -0.40 | -1.09% | -12.39% | -1.26 | -7.19% | -16.80% | 81.5 | 3/8 | 109.0% | ❌ |
| tsmom_lb03m_vt20 | -0.17 | -0.41 | -1.25% | -13.43% | -1.12 | -7.36% | -18.27% | 81.5 | 3/8 | 135.2% | ❌ |
| tsmom_lb06m_vt10 | -0.20 | -0.22 | -0.46% | -8.44% | -2.10 | -8.86% | -21.29% | 128.0 | 2/8 | 81.4% | ❌ |
| tsmom_lb06m_vt15 | -0.20 | -0.29 | -0.83% | -11.50% | -2.03 | -12.13% | -28.52% | 128.0 | 2/8 | 118.7% | ❌ |
| tsmom_lb06m_vt20 | -0.20 | -0.31 | -1.04% | -12.80% | -1.80 | -12.51% | -30.24% | 128.0 | 2/8 | 147.0% | ❌ |
| tsmom_lb12m_vt10 | -0.32 | -0.21 | -0.49% | -10.24% | -1.52 | -6.93% | -18.22% | 159.5 | 1/8 | 92.8% | ❌ |
| tsmom_lb12m_vt15 | -0.32 | -0.25 | -0.80% | -13.67% | -1.47 | -9.48% | -24.46% | 159.5 | 1/8 | 135.2% | ❌ |
| tsmom_lb12m_vt20 | -0.32 | -0.25 | -0.92% | -14.59% | -1.29 | -9.51% | -25.77% | 159.5 | 1/8 | 166.1% | ❌ |

**Least-worst** (for the record, not a winner): `tsmom_lb12m_vt10` — OOS Sharpe −0.21, swap drag 92.8%,
FWD still −1.52. Still refuted on every gate except `oos_maxdd_le_25pct` and `median_hold_ge_3d`.

## Diagnostic signal

- **Forward window catastrophe.** FWD is strictly worse than OOS for all 12 configs.
  The 2024-2026 USD-strength regime punished FX longs; and the monthly rebalance
  cycle is too slow to exit them. Sharpe FWD ≤ −1.12 across the board, CAGR FWD
  ≤ −4.9% — this is not a generalization gap, it is a regime ambush.
- **Vol-target doesn't save cost-dominated holds.** vt={10,15,20}% moves the
  return profile but does not reduce hold length; every vt column has swap
  drag increasing linearly with vt (higher position size → same holds →
  same per-bar swap × larger notional).
- **FX 3-pack as permanent attractor.** Regardless of (lookback, vt), last-bar
  weights converge on EURUSD + GBPUSD + USDJPY. The vol-weighting scheme over-allocates
  to FX because FX 20d vol is structurally low vs ETFs/crypto. The universe is
  not diverse in *risk-adjusted* terms, only in *ticker count*.

## Implications for V2 (next leads)

V2-L1 refutation does **not** invalidate the broader V2 framework — it invalidates
the canonical monthly-rebalance flavor. Remaining leads test families that
should not share the same failure mode:

- **V2-L2 (Gayed LETF rotation transportada)** uses regime MA on SPY → risk-on
  asset rotation. Hold length is similar but signal is regime-conditional
  (not cross-sectional vol-weighting), so FX-3-pack attractor does not apply.
- **V2-L3 (AFML triple-barrier + meta-labeling)** forces time-stop = 20d and
  price-stop via ATR, which caps swap drag proportionally. Meta-labeling
  adds a second filter layer — exactly the mechanism Prado `[advances_fin_ml, ch.7]`
  suggests for canonical-TF-family degradation.
- **V2-L5 (equity pairs daily)** is market-neutral by construction; swap on
  long leg ~ swap on short leg (Pepperstone Razor short-swap 0.001 ≈ 0.2 bps).
- **V2-L6 (vol breakout)** has explicit trailing ATR exit, bounding hold length
  at 20-50 bars even on strong trends.

Canonical TSMOM with monthly rebalancing goes to `## Dead ends` as
"refuted under Pepperstone Razor cost model; swap drag > risk premium at
holds > 40 days."

## Citations

- Time-series momentum family: `[algo_trading_chan, p.133, ch.6]`, `[systematic_trading, ch.8-9]` (Carver), `[trend_following_covel, ch.5-6]`.
- Vol-target no-look-ahead sizing: `[advances_fin_ml, p.162-164]`.
- Retail cost model constraint (optimum holds 1-4 weeks): `[systematic_trading, p.185-188]` (Carver).
- Walk-forward 6/8 gate: `[advances_fin_ml, ch.11]`, Pardo (2008) ch.10-11.
- Slow-trend regime break post-2008: `[systematic_trading, ch.9]`.
- Pepperstone Razor cost model: Phase 3.5a-V2 spec §3 + `docs/investment-mandate.md` §3.

## Links

- Per-config reports: `reports/phase3_5a_v2/v2_l1_tsmom_multi_asset_daily/tsmom_*.md`
- Per-config JSON: `reports/phase3_5a_v2/v2_l1_tsmom_multi_asset_daily/tsmom_*.json`
- Daily returns parquets: `reports/phase3_5a_v2/v2_l1_tsmom_multi_asset_daily/tsmom_*_daily_returns.parquet`
- Registry: `reports/phase3_5a_v2/v2_l1_tsmom_multi_asset_daily/registry.json`
- Jornada: `jornada/2026-04-18-1945-phase3.5a-v2-L1-tsmom-DEAD.md`
- Next lead: V2-L2 (Gayed LETF rotation transportada CFD), spec §V2-L2.

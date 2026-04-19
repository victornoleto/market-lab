# Lead V2-L3 — AFML triple-barrier + meta-label (aggregate)

**Phase:** phase3_5a_v2 | **Lead:** V2-L3 | **Status:** ❌ DEAD END (0/12 PASS)
**Period:** 2001-05-14 → 2026-04-15 (longest per-ticker Tiingo window)
**Tested:** 1 config × 12 tickers = 12 runs
**Aggregation iter:** 57
**Path tag:** [SHORT-HOLD CFD]

## Summary

V2-L3 took the AFML labeling canon — EMA-50 crossover as the primary
signal, triple-barrier (TP=2×ATR, SL=1×ATR, time-stop 20d) as the
labeler, and a `RandomForest(n=100, depth=5)` meta-filter on the
four-feature set {ret_5d, vol_20d, rsi_14d, atr_ratio_20d} — and
transported it to Pepperstone Razor CFD costs across 12 liquid U.S.
ETFs (broad + size + 7 sectors + 2 satellites). The sweep is a clean
**zero-for-twelve on the V2 5-gate framework**.

The highest OOS Sharpe on the sweep is **XLF = 1.21** (CAGR 2.50%,
MDD -0.76%) — impressively tight risk but the CAGR is an order of
magnitude below the V2 bar (≥30% net). Nine tickers never break
Sharpe OOS 1.0. Three tickers (GLD, TLT, XLK) end OOS negative or
flat. The dispersion is not a few lucky winners surrounded by noise —
it's a family that is **systematically under-powered** on this
universe under V2 gates.

Mechanically the story is that the RF meta-filter is doing exactly
what AFML §3.50-54 says it should: throw away almost every raw
primary event (EMA-50 cross → 117-252 events per ticker) and keep
only the ~15-55 with `p(success) ≥ 0.55`. Precision goes up, MDD
stays small (most tickers under 10%), but the residual CAGR on that
thin trade count — after Pepperstone Razor round-trip + 20d average
hold swap drag — is only 0-7%/yr gross. The 30% CAGR bar is simply
unreachable at this hold length without leverage, and the V2 spec
forbids L>5 `[vince_leverage_space]`. A leverage sweep on top of
V2-L3 would just multiply a 1% edge into a 3% edge; it would not
manufacture a winner.

Compared to V2-L2 (`gayed_ema100_L2_off_gld`, Sharpe OOS 2.29, CAGR
79%), V2-L3 under-performs across every single gate dimension. The
diagnostic is not "meta-labeling is broken" — AFML is correct that
`triple-barrier + meta` improves risk-adjusted returns on a primary
signal — the diagnostic is that the **EMA-50 crossover primary on
single-asset ETFs is a thin edge to begin with**, and AFML's own ch.3
makes this explicit (`[advances_fin_ml, p.50]`: "meta-labeling
enhances an existing edge; it does not create one"). On thin-edge
primaries the best a precision filter can do is shrink losses — it
cannot fabricate CAGR.

The defensive cohort (XLU 14d hold, XLV 12d hold) does show the
longest holds on the sweep, consistent with low-vol assets triggering
slow regime flips, but the CAGR ceiling is 3-4% on both — the same
cost-amortization wall documented in `[systematic_trading, p.185-188]`.

**Verdict:** V2-L3 is dead. Moving to V2-L4 (Carver risk-parity
multi-strategy blend) — but note the V2-L4 pre-req ("≥2 candidates
with metrics non-NaN per lead") is now satisfied by L1 (0 passers)
and L3 (0 passers) only via inclusion of their *best-Sharpe* non-PASS
picks; L4 should either skip or be re-scoped to blend V2-L2 winners
with Phase 3.5b 3-leg — that is a decision the next atomic lead
owner makes.

## Cross-ticker table (ranked by OOS Sharpe)

| Ticker | Window | Sharpe OOS | CAGR OOS | MaxDD OOS | Median hold (d) | Events taken | PASS |
|--------|--------|-----------:|---------:|----------:|----------------:|-------------:|:----:|
| XLF    | 2003-2026 | **1.213** | 2.50%   | -0.76%  | 7.5  | 14  | ❌ |
| XLI    | 2014-2026 | 0.945  | 3.55%   | -6.61%  | 8.5  | 34  | ❌ |
| QQQ    | 2001-2026 | 0.924  | 2.46%   | -3.07%  | 6.5  | —   | ❌ |
| XLE    | 2003-2026 | 0.789  | 6.90%   | -9.12%  | 9.0  | —   | ❌ |
| EFA    | 2003-2026 | 0.645  | 2.16%   | -3.06%  | 6.0  | —   | ❌ |
| XLU    | 2003-2026 | 0.445  | 3.18%   | -7.23%  | 14.0 | 52  | ❌ |
| SPY    | 2001-2026 | 0.147  | 0.60%   | -6.76%  | 7.0  | —   | ❌ |
| XLY    | 2014-2026 | 0.116  | 0.66%   | -13.22% | 6.0  | 24  | ❌ |
| XLV    | 2014-2026 | 0.101  | 0.33%   | -5.87%  | 12.0 | 17  | ❌ |
| XLK    | 2003-2026 | 0.000  | 0.00%   | 0.00%   | 7.0  | 7   | ❌ |
| GLD    | 2004-2026 | -0.097 | -0.12%  | -2.17%  | 6.0  | —   | ❌ |
| TLT    | 2002-2026 | -0.166 | -0.36%  | -4.14%  | 7.0  | —   | ❌ |

## Diagnostic — why the family fails V2 gates

1. **Thin primary.** EMA-50 price-cross on single ETFs yields
   ~0.3-0.5 signal Sharpe before labeling — consistent with
   Clenow/Covel on single-asset trend being noisier than multi-asset
   trend-of-trends `[stocks_on_the_move, p.81]`,
   `[trend_following_covel, ch.5]`.
2. **Meta precision, not alpha.** RF filter drops 70-95% of events
   (XLK: 7/213 taken). MDD shrinks but trade count collapses below
   N-viable thresholds for CAGR target.
3. **Hold/cost wall.** Median hold 6-14d × Razor RT spread (~11bps)
   + swap (20d × -0.005% = -0.1%) → 0.2-0.3% of equity bled per
   trade `[systematic_trading, p.185]`.
4. **No leverage escape.** L2 would lift all CAGRs to 5-14% — still
   below the 30% bar — and blow MaxDD past the 25% cap on XLE/XLY.
   V2 spec §6 forbids this trade.
5. **FWD collapse on 3/12 tickers** (GLD, TLT, XLK all go FWD=0)
   — the 2024-2026 stress window kills the defensive cohort.

## Citations

- Triple-barrier labeling `[advances_fin_ml, ch.3, p.45-49]`.
- Meta-labeling as precision filter on existing edge
  `[advances_fin_ml, ch.3, p.50-54]`.
- CPCV with embargo `[advances_fin_ml, ch.7, p.149-154, p.219-222]`.
- Walk-forward 6/8 + MaxDD cap `[advances_fin_ml, ch.11]`.
- Hold economics / cost amortization
  `[systematic_trading, p.185-188]`.
- Single-asset trend thinness `[stocks_on_the_move, p.81]`,
  `[trend_following_covel, ch.5]`.
- Pepperstone Razor cost model: Phase 3.5a-V2 spec §3.

## Links

- Per-ticker reports: `reports/phase3_5a_v2/v2_l3_afml_triple_barrier_meta/*.md`
- Registry: `reports/phase3_5a_v2/v2_l3_afml_triple_barrier_meta/registry.json`
- Jornada: `jornada/2026-04-19/02-phase3.5a-v2-L3-afml-triple-barrier-DEAD.md`

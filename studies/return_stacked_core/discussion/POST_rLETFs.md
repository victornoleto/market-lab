# HFEA vs return stacking, 1970–2026: same leverage idea, different diversifiers. I backtested both through every rate regime (and scanned 231 allocations of the stacked version)

**Not financial advice.** Benchmark: 100% SPY. **All pre-inception data is simulated** (testfol.io-style sims; formulas below). Monthly rebalance unless noted, gross of taxes/costs.

Proxies: `RSST ≈ SPY + 0.7·DBMF + 0.3·KMLM − (cash + 2%/yr)`, `GDE ≈ 0.9·SPY + 0.9·GLD − 0.8·cash`, `TMF ≈ 3×(0.5·ZROZ + 0.5·IEF) − 2×cash − 1.06%/yr` (financing-explicit — the "3x TLT minus nothing" sims you see around are too kind to TMF). MF proxy is the most fragile piece; BTC sims carry survivorship bias. 1970s data uses academic factor proxies with a 50% haircut on the MF sleeve — labeled LOW fidelity.

## The fork in the road

Both strategies lever $1 into more than $1 of exposure. The difference is *what* gets stacked:

- **HFEA 55/45 UPRO/TMF**: 1.65x stocks + 1.35x long Treasuries via daily-reset 3x LETFs. One diversifier, vol drag, borrow cost ×2.
- **RSC 35/40/25 GDE/RSST/ZROZ**: ~0.75x stocks + 0.32x gold + 0.40x managed futures + 0.25x long Treasuries (~1.7x gross) via embedded-leverage funds. Three diversifiers, no daily reset on the stack.

## 2000–2026 (simulated)

| | CAGR | MDD | Sharpe | $1 → |
|---|---|---|---|---|
| RSC core 35/40/25 | 12.5% | **−30.8%** | **0.85** | $22.5 |
| HFEA 55/45 (monthly reb.) | 12.1% | −69.4% | 0.53 | $20.4 |
| HFEA 55/45 (quarterly reb.) | **15.3%** | −69.1% | 0.62 | **$43.1** |
| 100% UPRO | 7.2% | −98.3% | 0.41 | $6.3 |
| 100% SSO | 9.9% | −88.3% | 0.44 | $12.2 |
| 100% SPY | 8.5% | −55.1% | 0.52 | $8.7 |

Episodes: GFC — HFEA −68% vs RSC −23%. **2022 — HFEA −65% vs RSC −21%** (stocks −24% *and* ZROZ −40%; managed futures +38% was the only thing that worked — HFEA's single hedge became a second source of loss). QE decade is HFEA's case: +3,183% vs RSC +478%. If you believe rates only go down and stocks only go up, HFEA wins. That's precisely the bet.

Also: HFEA monthly vs quarterly rebalance is a 3.2pp/yr CAGR difference on the same allocation — rebalance-timing luck at 3x is its own risk factor.

## 1970–2026 (LOW-fidelity extension)

| | CAGR | MDD |
|---|---|---|
| RSC-style core (haircut MF proxy) | 13.9% | −39.7% |
| HFEA 55/45 | 13.3% | **−90.3%** |
| 100% SPY | 11.1% | −55.1% |

The Volcker years (Treasuries at 15%+) put HFEA −90% underwater for over a decade. Stagflation 1973-74: SPY −45%, gold +139%, trend +65%, long bonds −30%. Every backtest that starts in 1982 (or 2009) hides this regime.

## Vol drag, quantified

100% UPRO over 26 years: CAGR 7.2% — *below unlevered SPY* — with a −98.3% max drawdown. 2x (SSO) at 9.9% beats SPY by 1.4pp but with −88% MDD. Daily-reset leverage on a single asset is a path bet, not a return multiplier.

DIY alternative without daily-reset on the whole book: 35 SSO/20 GLD/25 managed futures/20 ZROZ gets 10.4%/−33% — decent, but still ~2pp behind the embedded-stack version at similar risk.

## Does the exact RSC allocation matter? No.

I ran all 231 possible 5%-step GDE/RSST/ZROZ mixes: a contiguous 60-node plateau sits within 95% of max Sharpe, and 35/40/25 is inside it from all 8 start dates tested (the argmax itself wanders from 45/25/30 to 60/30/10 depending on start year — chasing it is curve-fitting). ZROZ weight is the real dial: 0% ZROZ = +1.4pp CAGR, −45% drawdowns.

**RSSX note** (stocks+gold+BTC stack, 2010+ window): swapping it in jumps Sharpe to 1.47 — that's 100% BTC's decade talking, and it lost −41% in 2022, worse than SPY. Satellite at most.

## Not claiming

Forward returns; optimal weights; that live funds track sims (fees 0.8-1%, tracking, closure risk); that RSC beats HFEA if the next decade is QE 2.0.

**Questions:** HFEA survivors of 2022 — did you hold? Anyone running RSST+ZROZ as "HFEA 2.0"? Quarterly vs monthly rebalance — conviction or luck?

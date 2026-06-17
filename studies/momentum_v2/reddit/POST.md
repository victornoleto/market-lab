# Reddit post — r/investing

> **How to post:** Reddit text posts don't embed local files. Upload the 4 PNGs in this folder to the
> post's image gallery (or imgur) in this order — `rolling_windows_summary`, `rolling_windows_relative`,
> `equity_drawdown`, `panorama` — and keep the captions. Markers `📊 [Image N]` show where each goes.
> Title is the first line.

---

**Title:**
I backtested momentum on US stocks back to 1990. Two dead-simple rules beat the S&P 500 in ~100% of all 5-year windows — and also drew down ~63%. Would you actually run this?

---

**TL;DR:** Two simple momentum rules — (A) rank by a blend of the 1/3/6/12-month returns, or (B) rank by trend strength; hold the top 10–15, rebalance every ~2 months — crushed SPY in a 1990–2026 backtest, beating it in **95–100% of every rolling 3/5/10/15-year window**. But they also had **−61% and −63% max drawdowns**, and the backtest has a **serious survivorship-bias problem** that almost certainly inflates the numbers. My honest take is "probably not worth it" — but I'd like to be argued with. Data + charts below.

---

I run a small systematic-research setup as a hobby. I tested ~**1,260** momentum variants on US stocks and kept getting pushed toward the same two families. Here's what they are, how they did, and the three reasons I don't trust my own results.

### The setup (kept deliberately boring)
- **Universe:** US stocks with ≥5y history, price > $5, and > $5M median daily dollar volume (liquidity filter).
- **Cadence:** rank monthly, act every **2 months**. **Equal weight.** Long-only, no leverage.
- **Gross** of fees, costs, taxes, slippage (this matters — see caveats).

### The two rules

**A — "1-3-6-12 composite momentum" (you can still run this in a spreadsheet)**
For each stock, average its total return over the **1-, 3-, 6- and 12-month** windows, then rank by that composite. Buy the **top 15**, equal weight, rebalance every 2 months. (Classic relative-strength momentum — Jegadeesh & Titman, 1993; the multi-window "13612" blend popularized by Keller's VAA/DAA.)

**B — "trend strength" (stronger on paper, needs code)**
Score each stock by the **slope of an exponential regression of its last ~126 days of log price, × R²** (Clenow, *Stocks on the Move*). Buy the **top 10**, rebalance every 2 months. Rewards smooth, persistent trends over noisy spikes.

### Results (1990–2026, gross)

| | CAGR | Max Drawdown | Sharpe | Beat SPY (5y windows) |
|---|---|---|---|---|
| **A — 1-3-6-12 momentum** (top 15) | **55.4%** | −63% | 1.15 | **100%** |
| **B — trend strength** (top 10) | **66.2%** | −61% | 1.14 | **100%** |
| SPY (buy & hold) | 10.8% | −55% | 0.65 | — |

### 📊 [Image 1 — `rolling_windows_summary.png`] — the chart that actually matters
A single CAGR is cherry-pickable (pick a lucky start date). So I select strategies on **rolling-window dominance** — across **every** rolling window, not one lucky start. **Left:** how *often* it ended ahead of SPY — **95–98% of 3-year windows, and 100% of every 5/10/15-year window**, for both rules. **Right:** by *how much* (average ending wealth vs SPY) — roughly **4–5× over 3 years, 8–14× over 5, 39–85× over 10** (and a frankly absurd **130–340× over 15** — hold that thought for the survivorship section).

### 📊 [Image 2 — `rolling_windows_relative.png`] — consistent, or just one lucky era?
Same idea, full distribution: each panel is the strategy ÷ SPY wealth ratio for **3/5/10/15-year** windows, by *start month* (log scale; dashed line = SPY = 1.0). The ratio basically never dips below 1.0 — but it **swings a lot**: a 5-year window starting in the late-1990s ended ~30–70× ahead, while one starting in the mid-2000s ended only ~2×. Same rules, wildly different luck depending on *when* you got in.

### 📊 [Image 3 — `equity_drawdown.png`] — the dream and the catch
Left: $1 compounds into the millions (log scale) vs SPY's ~$25. Right: the catch — both strategies spend long stretches deep underwater, bottoming at **−63% (A) and −61% (B)**. A drawdown like that on a concentrated 10–15 stock book is exactly what ends most people's discipline at the worst possible time.

### 📊 [Image 4 — `panorama.png`] — how I landed on these two
I tested 5 scoring families × many lookbacks/sizes/rebalances. Ranked by rolling dominance, **the trend-strength and momentum (1-3-6-12) families were the clear top two** (≈0.94–0.95); volatility-adjusted (0.925), 12-1 momentum (0.909), and a momentum/low-vol blend (0.78) trailed. Then I tried to *fix the drawdown*:
- **Bigger book (10 → 50 stocks):** Sharpe improves, but **max drawdown plateaus around −58% and won't go lower** (right panel). Momentum crashes are systemic — you can't diversify them away.
- **Moving-average stop** (sell intra-period when price drops below its MA): cut the drawdown to ~−43%, but gave up so much return that Sharpe/Calmar got **worse** — you sell at local bottoms and miss the rebounds.
- **Same rules on Brazilian stocks:** did **not** replicate (failed the overfitting test; different families won). The edge looks US-specific.

### 🐘 The elephant: survivorship bias
This is why this is a "would you run it?" post and not an "I found alpha" post. My price data (Yahoo-sourced) is **missing most stocks that delisted or went to zero** over 35 years. Momentum specifically piles into the highest-flying names — exactly the population where the survivors look spectacular and the corpses are invisible. So:
- "Beat SPY in 100% of 5-year windows" is *almost certainly* inflated.
- Real returns are lower (probably a lot), and the *real* drawdowns are likely **worse** (some of those high-fliers would have blown up and exited).
- Only proper point-in-time data with delisted names (CRSP / Norgate / Sharadar) can settle it — and I'd bet it **shrinks** the edge.

I'm treating these headline numbers as an **upper bound, not a forecast.**

### So… is it worth running?
Genuinely asking. Even if the *real* edge is half of this and still beats SPY:
- Could you hold a 10–15 stock momentum book through a **−60%+ drawdown** without bailing? (Be honest.)
- Does ~350–450%/yr turnover + small-cap spreads eat the edge alive once real costs hit?
- Is "beats the index in ~every multi-year window" worth it if the path is this brutal — or is it just a concentrated bet on one factor that works *until it doesn't* (e.g., the 2009 momentum crash)?

What would you change — or would you just buy SPY and sleep at night?

---

*Methodology: long-only, equal-weight, gross of costs/taxes/slippage, US listings with liquidity filters, 1990–2026 (also checked from a 2000 start). Selection metric = rolling relative-equity dominance vs SPY. This is a personal backtest / research project — **not investment advice**, and (given the survivorship caveat) not something I run with real money.*

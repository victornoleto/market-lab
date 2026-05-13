# Title

I built an interactive LETF rotation dashboard: 39.0% CAGR Rearm T20D120, 36.7% Rearm T35D60, 53.0% Quint TrendMomVol K3 TQQQ

# Alternative Titles

1. I built an interactive LETF rotation dashboard: 39.0% CAGR Rearm strategy vs QLD/TQQQ baselines
2. Testing LETF rotation ideas: 39.0% CAGR long-history Rearm T20D120, but DSR/PBO still say research-only
3. QLD/TQQQ rotation dashboard: comparing 15 LETF strategies from SPY B&H to 39.0% CAGR Rearm T20D120
4. Beyond CAGR: interactive LETF dashboard with equity curves, drawdowns, rolling A/B windows, and 39.0% top strategy
5. I backtested QLD/TQQQ rotation rules from 1986-2026: top result 39.0% CAGR, but not a free lunch

# Post

This is a follow-up to my previous post here:

https://www.reddit.com/r/LETFs/comments/1t7q8or/40year_letf_rotation_backtest_5_strategy_families/

In that post, I shared a 40-year LETF rotation study across 5 strategy families and 426 configurations. The main result was what I now call **Quad Risk K2** in the dashboard: a QLD/ZROZ rotation that turns risk-on when at least 2 of 4 QQQ/QLD regime signals are true. The four signals were long trend, medium trend, realized volatility, and short-term return persistence. In simple terms: hold QLD when enough risk conditions are favorable; otherwise hold ZROZ.

That original strategy was the one I felt most comfortable calling the robust anchor: it cleared the full validation stack in that study, including DSR, PBO, walk-forward, OOS, forward-stress, bootstrap, and cross-library checks. It also had strong rolling-window behavior versus SPY.

I was honestly happy with the quality of the discussion in the comments on that post. I tried to answer every comment I could, but because of my limited time and because I kept focusing on the research work behind this follow-up, I may not have replied to everyone. I did read the feedback, and this new post is partly a response to the natural next question: can the original idea be improved, extended, or stress-tested further?

So the goal here was not to throw away the original result. The goal was to keep **Quad Risk K2** as the anchor and continue searching for improvements and evolutions around it: rearm logic, TQQQ turbo windows, broader technical-vote systems, modern QLD/TQQQ variants, and simpler LRS baselines.

I built a small interactive web dashboard for comparing a set of LETF rotation strategies I have been researching. The app is focused on Nasdaq/S&P leveraged ETF rotation ideas: QLD/TQQQ, SSO/UPRO, defensive legs, trend/momentum/volatility votes, drawdowns, and rolling window behavior.

Link: `<your VPS URL here>`

Important caveat up front: this is research, not financial advice and not a deploy recommendation. Several of the high-CAGR variants look economically interesting, but the formal validation stack still blocked promotion because DSR/PBO failed after accounting for the number of trials. I am sharing the tool because the comparisons are useful and because LETF strategy discussions are more productive when people can inspect drawdowns, windows, and benchmarks instead of only seeing a final CAGR number.

## What The Strategies Are

The dashboard currently compares these strategies:

Full-sample metrics shown in the app use the long-history window **1986-01-03 to 2026-04-17**:

| Name | CAGR | Max DD | Sharpe | Sortino |
|---|---:|---:|---:|---:|
| Octa Price K6 QLD | 32.05% | -57.81% | 0.983 | 1.375 |
| Octa Price K6 TQQQ | 40.26% | -64.24% | 0.951 | 1.268 |
| Quad Risk K2 | 31.06% | -64.50% | 0.919 | 1.258 |
| Rearm T20D90 | 38.99% | -55.48% | 0.975 | 1.228 |
| Rearm T20D120 | 39.01% | -55.48% | 0.961 | 1.207 |
| Rearm T35D60 | 36.66% | -55.48% | 0.962 | 1.207 |
| Quint TrendMomVol Overlay | 38.46% | -64.54% | 0.872 | 1.084 |
| Quint TrendMomVol K3 QLD | 19.38% | -70.07% | 0.668 | 0.907 |
| QQQ B&H | 14.58% | -82.97% | 0.658 | 0.866 |
| SPY B&H | 11.49% | -55.14% | 0.682 | 0.842 |
| Quint TrendMomVol K3 TQQQ | 21.48% | -87.69% | 0.637 | 0.833 |
| LRS SSO | 13.88% | -51.67% | 0.664 | 0.759 |
| LRS QLD | 18.33% | -82.54% | 0.648 | 0.741 |
| LRS TQQQ | 19.94% | -94.36% | 0.609 | 0.696 |
| LRS UPRO | 16.40% | -71.20% | 0.605 | 0.691 |

- **Rearm T20D120**: the highest-CAGR long-history sensitivity in the final local grid. It keeps the same core Quad Risk K2 shell as Rearm T35D60, but changes the post-crash rearm geometry: after at least 20 OFF days, an OFF-to-ON transition opens a 120-trading-day TQQQ/LRS1.20 rearm window. In the 1986-2026 long-history test it reached about **39.01% CAGR**, **1.207 Sortino**, and **-55.48% max drawdown**.
- **Rearm T20D90**: the more balanced T/D sensitivity. Same idea as T20D120, but with a 90-trading-day rearm window. It had nearly the same CAGR, about **38.99%**, with the best Sortino in the local T/D grid, about **1.228**.
- **Rearm T35D60**: the main anchor strategy from the previous LETF rotation loop. It uses the Quad Risk K2 shell, QLD as the normal risk-on leg, ZROZ as the defensive leg, a rate/vol cash override, and a T35D60 post-crash TQQQ rearm window with LRS1.20. Long-history result: about **36.66% CAGR**, **1.207 Sortino**, and **-55.48% max drawdown**.
- **Quad Risk K2**: the simpler four-gate shell. It turns risk-on when 2 of 4 filters pass: QLD above SMA250, QLD above SMA100, 21-day realized volatility below 40%, and AR(1) 30-day persistence above zero. It holds QLD when ON and ZROZ when OFF. Long-history result: about **31.06% CAGR**, **1.258 Sortino**, and **-64.50% max drawdown**.
- **Octa Price K6 QLD**: an 8-signal price-only vote using SMA/EMA trend filters, ROC momentum filters, and RSI14. It turns ON when 6 of 8 signals pass and holds QLD when ON.
- **Octa Price K6 TQQQ**: the same 8-signal price-only vote as Octa Price K6 QLD, but with TQQQ as the risk-on leg. It had the highest long-history CAGR among the listed long-history comparison rows, about **40.26%**, but failed DSR/PBO validation.
- **Quint TrendMomVol K3 QLD**: a 5-signal vote using SMA100>SMA250, ROC10>0, ROC120>0, StochRSI14>50, and realized-volatility percentile below 70. It turns ON when 3 of 5 signals pass and holds QLD when ON. On modern Tiingo 2010+ data, it reached about **36.26% CAGR** with **-37.54% max drawdown**.
- **Quint TrendMomVol K3 TQQQ**: the same 5-signal vote as Quint TrendMomVol K3 QLD, but with TQQQ as the risk-on leg. On modern Tiingo 2010+ data, it reached about **53.00% CAGR** with **-51.03% max drawdown**. On the stricter 1986+ long-history reproduction, it weakened materially.
- **Quint TrendMomVol Overlay**: a hybrid that keeps the Rearm T35D60 shell but allows the Quint TrendMomVol K3 vote to act as an additional QLD-to-TQQQ turbo trigger. It improved terminal equity/CAGR versus Rearm T35D60 in some comparisons, but worsened drawdown and Sortino, so it did not dominate the anchor.
- **LRS SSO, LRS UPRO, LRS QLD, and LRS TQQQ**: simple Gayed-style trend baselines. If SPY/QQQ is above its 200-day SMA, hold the leveraged ETF next bar; otherwise hold cash. These are included as simple sanity-check baselines.
- **SPY B&H and QQQ B&H**: passive comparators so the rotations can be judged against broad equity and Nasdaq exposure, not just against each other.

## What The Webapp Shows

The goal of the app is to make the comparison inspectable instead of static.

- **Date range control**: choose the full sample or focus on recent 5y/10y/15y/20y periods. This matters a lot because some strategies look amazing in the modern sample and much weaker once older regimes are included.
- **Window Summary**: quick cards showing start date, end date, number of bars, best CAGR in the selected window, best Sortino, and lowest max drawdown.
- **Equity Curves**: log-scale equity curves for all strategies. You can toggle individual strategies from the side table and inspect values at the cursor date.
- **Drawdown Chart**: synchronized drawdown plot for the same selected strategies. This is usually the fastest way to see whether a high CAGR is just hiding unacceptable path risk.
- **Interactive Series Table**: shows each strategy's equity at the cursor date, CAGR, and max drawdown. You can sort by cursor equity or Sortino and click rows to show/hide lines.
- **Metrics Table**: sortable CAGR, Sortino, Sharpe, max drawdown, Calmar, and ending multiple for the selected date window.
- **Rolling A/B Comparison**: choose any strategy as A and any other as B. The app builds 3y, 5y, 10y, 15y, and 20y rolling comparisons, including win-rate heatmaps and final-ratio heatmaps. This is useful for questions like "how often did Rearm T35D60 beat Quad Risk K2 over rolling 10-year windows?" instead of only asking which strategy won over the full backtest.
- **A/B KPI Cards**: final A equity, final B equity, A/B ratio, percent of days A was above B, and max drawdowns for both.
- **Rolling Window Hover Details**: hover any heatmap cell to see the exact start/end dates, A growth, B growth, CAGR for both, and the final ratio.
- **Strategy Concepts Tab**: plain-English descriptions of every strategy in the dashboard: the concept, the algorithm, and the current research status.

## Why I Built It

I wanted a cleaner way to discuss LETF rotation than posting one table of top backtest results. A strategy with 40% CAGR can still be a bad idea if it only works in one regime, has catastrophic drawdowns, or loses to a simpler anchor in rolling windows. The dashboard makes those trade-offs visible.

The short version of the research so far:

- The robust long-history anchors are still **Quad Risk K2** and **Rearm T35D60**.
- The best local sensitivity was **T20D120** at about **39.01% CAGR**, but it is not a validated winner.
- **Quint TrendMomVol K3 TQQQ** is very strong on Tiingo 2010+ data, about **53.00% CAGR**, but weakens in 1986+ reproduction.
- The high-CAGR variants are interesting challengers, but DSR/PBO failures mean I would not present them as deployable systems.

I would be interested in feedback from people here, especially on better validation ideas, realistic execution assumptions for QLD/TQQQ rotations, tax/cost modeling, and whether the rolling A/B view changes how you evaluate these LETF strategies.

## Discussion Question: Would You Still Follow A Strategy If DSR/PBO Failed?

This is the part I am most interested in discussing.

The strategies in this dashboard are not just top rows from a random backtest table. The better candidates generally passed several practical robustness checks:

- **OOS holdout**: they remained profitable on a reserved out-of-sample block.
- **FWD stress window**: they survived the most recent forward/stress slice.
- **Walk-forward validation**: most stayed positive across rolling train/test windows.
- **Bootstrap checks**: resampled return paths usually did not destroy the result.
- **Rolling 3y/5y/10y/15y windows**: the best anchors had broad positive rolling behavior, not just one lucky terminal point.

But they still failed the two gates that worry me the most: **DSR** and **PBO**.

Plain-English version:

- **DSR, or Deflated Sharpe Ratio**, asks: "After accounting for all the strategies/parameters I tried, is this Sharpe still statistically impressive?" A Sharpe that looks good in isolation can become much less convincing after thousands or millions of trials, because some great-looking result is expected to appear by chance.
- **PBO, or Probability of Backtest Overfitting**, asks: "When I split the data many different ways, do the configurations that look best in-sample also keep ranking well out-of-sample?" A high PBO means the selection process may be learning quirks of the backtest window rather than a durable rule.

So the uncomfortable result here is:

- economically, several strategies look very strong;
- mechanically, they pass OOS/WF/bootstrap-style checks;
- statistically, they still look too optimized once DSR/PBO account for the search process.

My current stance is that this makes them **research-only**, not deployable systems. But I am not sure everyone will draw the line in the same place.

For discussion:

- If a LETF strategy passes OOS, walk-forward, bootstrap, and rolling-window checks, but fails DSR/PBO, would you still consider trading it with reduced size?
- Do you treat DSR/PBO as hard blockers, or as warnings that should be balanced against economic intuition and simplicity?
- Is there a point where a strategy is simple enough, economically plausible enough, or robust enough across regimes that you would accept weak DSR/PBO?
- For LETFs specifically, do you think trend/momentum/volatility filters are a known structural effect, or just an overfit-prone family because everyone is searching the same indicators?

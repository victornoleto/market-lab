# AI/Semis ETF Tactical Portfolio - Exit And Monitoring Plan

**Date:** 2026-05-12  
**Status:** operational planning note; not a validated strategy; does not override `docs/investment-mandate.md`.  
**Scope:** tactical 12-24 month ETF sleeve focused on AI infrastructure, semiconductors, memory and electrification.  
**Disclaimer:** educational/research framework, not financial advice. Parameters below are explicit operating rules, not forecasts.

---

## 1. Executive Summary

The proposed sleeve is a concentrated momentum/thematic allocation with high exposure to one economic narrative: AI capex, semiconductors, HBM memory and grid/electrification demand. The original allocation is coherent with an aggressive thesis, but it is too concentrated for a capital-preservation mandate because `DRAM + SMH + AIS + SOXL` already behave like a single semiconductor/AI risk bucket, while `SOXL` and `TQQQ` add daily 3x path dependency. My recommended modification is to reduce total 3x exposure, raise cash, and shift the most concentrated exposure from `DRAM/AIS` toward the more diversified `SMH`. The exit system should not react to one noisy daily signal; it should require weekly confirmation from trend, volatility and market-regime indicators. Moving-average trend filters and RSI are standard technical tools `[tech_analysis_patterns, p.148, p.153]`; ATR/std-dev exits normalize risk across volatile instruments `[stat_sound_indicators, p.156-157]`, `[trading_evolved, p.267-268]`; leveraged ETFs require stricter time and drawdown controls because daily rebalancing creates volatility decay `[trading_evolved, p.172-176]`, `[risk_parity, p.111-113]`.

---

## 2. Allocation Review

### 2.1 Original Allocation

| Asset | Weight | Value | Role |
|---|---:|---:|---|
| `DRAM` | 20% | $2,000 | concentrated memory/HBM core |
| `SMH` | 20% | $2,000 | diversified semiconductor core |
| `AIS` | 20% | $2,000 | active AI infrastructure core |
| `SOXL` | 10% | $1,000 | 3x semiconductor tactical |
| `TQQQ` | 8% | $800 | 3x Nasdaq tactical |
| `POW` | 12% | $1,200 | electrification/power theme |
| Cash | 10% | $1,000 | reserve for drawdowns |

### 2.2 Verdict On Original Allocation

I would not run the original allocation unchanged. The thesis is clear, but the risk budget is too heavily loaded into one factor cluster:

- `DRAM`, `SMH`, `AIS` and `SOXL` are not independent sleeves; they are mostly variants of the same AI/semiconductor cycle.
- `DRAM` has meaningful concentration risk because memory/HBM exposure depends heavily on a small number of companies.
- `AIS` is active and relatively new, so historical signals from the ETF itself may be less reliable than proxy signals from `SMH`, `QQQ`, capex data and top holdings.
- `SOXL + TQQQ = 18%` is high for daily 3x ETFs in a 12-24 month sleeve. Leveraged ETFs can lose value in sideways volatile markets even when the long-run theme is correct `[trading_evolved, p.172-176]`, `[risk_parity, p.111-113]`.
- Cash at 10% is low if the stated plan is to buy 15-20% drawdowns. A tactical sleeve needs dry powder and the psychological benefit of not being forced to sell at the worst moment.

### 2.3 Recommended Allocation

This is the allocation I would prefer for the same aggressive-but-disciplined objective:

| Asset | Original | Recommended | Rationale |
|---|---:|---:|---|
| `DRAM` | 20% | 15% | keep HBM upside, reduce single-subtheme concentration |
| `SMH` | 20% | 25% | make the broad semiconductor ETF the main core |
| `AIS` | 20% | 15% | keep AI-infra exposure, but size down active/new ETF risk |
| `SOXL` | 10% | 6% | keep tactical convexity, reduce decay/drawdown damage |
| `TQQQ` | 8% | 4% | keep Nasdaq beta kicker, avoid duplicate 3x risk |
| `POW` | 12% | 10% | keep electrification theme, avoid overloading satellite sleeve |
| Cash | 10% | 25% | preserve optionality and reduce emotional pressure during drawdowns |

If the investor insists on staying more invested, use a maximum-risk variant: `DRAM 15% / SMH 30% / AIS 20% / SOXL 6% / TQQQ 4% / POW 10% / Cash 15%`. I would not exceed `SOXL + TQQQ = 12%` unless there is a pre-written exit plan and the investor accepts large mark-to-market drawdowns.

---

## 3. System Design Principles

### 3.1 Weekly, Not Intraday

The sleeve is not a day-trading system. Signals should be checked weekly after Friday close, with daily alerts only for severe risk events. This reduces whipsaw and aligns with the stated 12-24 month horizon.

### 3.2 Confirmation Stack

Do not exit a core ETF on one isolated indicator. Act when at least two of these categories confirm deterioration:

| Category | Examples | Purpose |
|---|---|---|
| Trend | `Close < SMA50`, `Close < SMA200`, lower highs/lows | identify loss of primary direction `[tech_analysis_patterns, p.148]` |
| Volatility | ATR stop, Bollinger lower band, VIX term structure | avoid ignoring regime shifts `[trading_evolved, p.267-268]` |
| Breadth/proxy | `SMH`, `QQQ`, SOX index, top holdings | confirm whether the whole theme is breaking |
| Fundamentals | AI capex, guidance, memory pricing, Nvidia/TSMC/ASML/Micron/SK Hynix | detect thesis deterioration |
| Portfolio risk | correlation, total drawdown, 3x weight drift | protect capital as a whole |

### 3.3 Yellow And Red Definitions

| State | Meaning | Action |
|---|---|---|
| Green | trend intact; no regime stress | hold or rebalance only |
| Yellow | risk rising; thesis still alive | stop adding; tighten stops; review sizing |
| Red | capital protection mode | reduce 50%+ or exit tactical positions |

### 3.4 Close-Based Execution

All technical exits should be based on daily or weekly closing prices, not intraday lows. Closing-price rules reduce noise and avoid reacting to transitory intraday volatility. The trade-off is that exits may be slightly later.

---

## 4. Signal Table By Position

| ETF | Yellow Alert | Red Alert | Take Profit / Sizing |
|---|---|---|---|
| `DRAM` | 10-12% drawdown from 20-day high; weekly close below `SMA50`; `RSI14 < 45` after prior overbought; negative news/guidance from SK Hynix, Samsung or Micron | weekly close below `SMA200`; 18-20% drawdown from high; two weekly closes below `SMA50` with volume > 1.5x 20-day average; negative guidance from at least 2 of the 3 key memory names | after +35%, sell 20% of position; after +50%, sell another 20%; move stop to breakeven after +20% |
| `SMH` | weekly close below `SMA50`; `RSI14 > 75` and close above upper Bollinger Band; Nvidia/TSMC/ASML guidance weakens | weekly close below `SMA200`; 15-18% drawdown from high; `VIX > 30` while `QQQ` and `SMH` both lose `SMA200` | if weight exceeds 25%, rebalance to target; after +40-50%, realize 20-30% of profit |
| `AIS` | `AIS` falls 10-12% and both `SMH`/`QQQ` are below `SMA50`; weak relative strength vs `SMH` for 4 weeks | reduce 50% if `AIS` falls 18-20% or if `SMH` and `QQQ` both close below `SMA200`; exit if AI capex thesis deteriorates for 2 quarters | after +35-40%, sell 20%; do not add if volume/liquidity remain thin or proxy trend is red |
| `SOXL` | 10-12% drawdown from entry or high; daily close below `SMA20`; underperforms `SMH` for 2 weeks during an `SMH` rally; `VIX/VIX3M > 1.00` | exit or reduce 50-100% if 18-20% drawdown from high, weekly close below `SMA50`, or `SMH` closes below `SMA200`; time stop if not at least +10% after 6 weeks | after +50%, sell 30-50% of profit; after +100%, remove initial capital or halve position; max portfolio weight 6-8% preferred, 10-12% hard cap |
| `TQQQ` | `QQQ` closes below `SMA50`; 10-12% drawdown from entry/high; 20-day correlation with `SOXL > 0.90` and both negative | exit or reduce 50-100% if `QQQ` closes below `SMA200` or `TQQQ` draws down 18-20%; time stop after 6 weeks flat/negative | after +40-50%, sell 30% of profit; max portfolio weight 4-6% preferred, 8-10% hard cap |
| `POW` | weekly close below `SMA50`; weak relative strength vs `SPY`; 10-12% drawdown from high; utility/power equipment holdings underperform | reduce 50% if weekly close below `SMA200` or 18-20% drawdown; exit if AI power/capex thesis weakens for 2 quarters | after +30-40%, sell 20%; hard cap 15% of portfolio |

---

## 5. Portfolio-Level Rules

### 5.1 Total Drawdown Rules

| Portfolio Drawdown From High | Action |
|---:|---|
| -5% | no action; review whether drawdown is from 3x sleeve or whole theme |
| -8% to -10% | yellow portfolio alert; stop adding; tighten 3x stops |
| -12% to -15% | reduce 3x sleeve by 50%; add only if broad trend remains above `SMA200` |
| -18% to -20% | red portfolio alert; protect cash; reduce concentrated core if proxies are below `SMA200` |
| worse than -20% | no automatic dip-buying; rebuild only after weekly trend recovery |

Drawdown is the primary practical risk metric for this sleeve because the investor experiences actual equity declines, not abstract variance `[leverage_space, p.89-92]`.

### 5.2 3x Sleeve Rules

| Rule | Threshold |
|---|---:|
| Preferred `SOXL + TQQQ` total | 8-10% |
| Hard maximum `SOXL + TQQQ` total | 12% recommended; 18-20% absolute emergency cap |
| Cut levered sleeve | if `VIX > 30` and `VIX/VIX3M > 1.05` |
| Do not add to levered ETFs | if underlying `SMH` or `QQQ` is below `SMA200` |
| Time stop | exit if not profitable after 6 weeks or if underperforming unlevered proxy during a rally |

The purpose of `SOXL` and `TQQQ` is tactical upside capture, not long-term buy-and-hold. Daily-rebalanced 3x ETFs are structurally path-dependent and can decay materially in volatile sideways markets `[trading_evolved, p.172-176]`, `[risk_parity, p.111-113]`.

### 5.3 Correlation Rules

| Condition | Interpretation | Action |
|---|---|---|
| 20-day `corr(SOXL,TQQQ) > 0.90` | diversification falling | yellow alert |
| 20-day `corr(SOXL,TQQQ) > 0.95` and both below `SMA20` | one common risk factor dominates | reduce 3x sleeve by 50% |
| `DRAM`, `SMH`, `AIS`, `SOXL` all down for 2 consecutive weeks | theme-level deterioration | stop adding; review core sizing |

Correlation is not reliable in tail events, which is why it is used here as a warning signal, not as the sole risk control `[leverage_space, p.61-72]`.

### 5.4 VIX And Term Structure Rules

| Regime | Condition | Action |
|---|---|---|
| Normal | `VIX < 20` and `VIX/VIX3M < 1.00` | hold/rebalance normally |
| Stress building | `VIX > 25` or `VIX/VIX3M > 1.00` | yellow alert; no new 3x buys |
| Stress event | `VIX > 30` and `VIX/VIX3M > 1.05` | red alert; cut 3x first |
| Panic | `VIX > 40` | preserve cash; no averaging down until weekly reversal |

### 5.5 Fundamental Rules

| Fundamental Signal | Affected ETFs | Action |
|---|---|---|
| Microsoft, Google, Amazon or Meta reduces AI/cloud capex quarter-over-quarter | `AIS`, `POW`, `SMH`, `TQQQ` | yellow alert |
| 2+ hyperscalers reduce capex or guide lower in the same quarter | `AIS`, `POW`, `SMH`, `TQQQ` | reduce theme 25-50% |
| Nvidia, TSMC, ASML, Micron, Samsung or SK Hynix lowers guidance | `DRAM`, `SMH`, `SOXL`, `AIS` | yellow alert |
| 2+ key semiconductor/memory holdings guide lower in the same quarter | `DRAM`, `SMH`, `SOXL`, `AIS` | red alert; reduce high-beta sleeve |
| HBM/memory pricing turns down for 2 monthly readings | `DRAM` | reduce `DRAM` 25-50% |

News should not be treated as permanently informative; sentiment/news impact decays over days, while repeated guidance/capex changes are more important than one headline `[sentiment_analysis_handbook, p.52-53]`.

---

## 6. Take Profit And Rebalancing

### 6.1 Quarterly Rebalance Bands

| Asset | Target | Upper Band | Action If Above Band |
|---|---:|---:|---|
| `DRAM` | 15% | 20% | trim to 15-17% |
| `SMH` | 25% | 30% | trim to 25-27% |
| `AIS` | 15% | 20% | trim to 15-17% |
| `SOXL` | 6% | 8% preferred / 12% hard | trim aggressively |
| `TQQQ` | 4% | 6% preferred / 10% hard | trim aggressively |
| `POW` | 10% | 15% | trim to 10-12% |
| Cash | 25% | no upper cap | deploy only under rules |

Rebalancing is maintenance, not a change of opinion; it keeps realized portfolio risk closer to the intended risk budget `[trading_evolved, p.35-36]`.

### 6.2 Profit-Taking Rules

| Event | Action |
|---|---|
| Core ETF up +20% | move stop to breakeven |
| Core ETF up +35% | sell 20% of position |
| Core ETF up +50% | sell another 20% or rebalance to target |
| `SOXL` up +50% | sell 30-50% of profit |
| `TQQQ` up +40-50% | sell 30% of profit |
| Any 3x ETF up +100% | remove initial capital or halve position |
| RSI14 > 80 and price > upper Bollinger Band for 3 sessions | no new buys; consider partial profit |

### 6.3 Cash Deployment Rules

| Portfolio Drawdown | Cash Deployment | Conditions |
|---:|---:|---|
| -8% to -10% | deploy 25% of cash | only if `SMH` and `QQQ` remain above `SMA200` |
| -12% to -15% | deploy another 25-50% | only after weekly reversal and `VIX/VIX3M < 1.00` |
| -18% to -20% | deploy remaining cash only after recovery | require weekly close back above `SMA50` |
| worse than -20% | do not deploy automatically | preserve capital until trend improves |

Cash must not be used to average down `SOXL` or `TQQQ` during red regime.

---

## 7. Decision Flow

```text
Start weekly review
|
|-- Is portfolio drawdown worse than -15%?
|   |-- Yes: cut 3x sleeve by 50%; stop new buys; check VIX and SMA200.
|   |-- No: continue.
|
|-- Is VIX > 30 and VIX/VIX3M > 1.05?
|   |-- Yes: red regime; reduce/exit SOXL and TQQQ first.
|   |-- No: continue.
|
|-- Is underlying proxy below SMA200?
|   |-- SMH below SMA200: reduce DRAM/SMH/AIS/SOXL risk.
|   |-- QQQ below SMA200: reduce TQQQ and AIS risk.
|   |-- No: continue.
|
|-- Did any position breach its ATR or drawdown stop?
|   |-- Core ETF: reduce 25-50% after weekly close confirmation.
|   |-- 3x ETF: reduce 50-100% immediately after close confirmation.
|
|-- Did any position exceed profit/rebalance bands?
|   |-- Yes: trim to target and rebuild cash.
|   |-- No: hold.
|
End review
```

---

## 8. Five-Minute Weekly Checklist

Run this after Friday close.

1. Check each ETF versus `SMA50` and `SMA200`.
2. Check drawdown from recent high: `-10%`, `-15%`, `-20%`.
3. Check `VIX`, `VIX3M` and `VIX/VIX3M`.
4. Check whether `SOXL` and `TQQQ` are both below `SMA20` and highly correlated.
5. Check top-holding news: Nvidia, TSMC, ASML, Micron, Samsung, SK Hynix, Microsoft, Google, Amazon, Meta.

Free/low-cost tools:

| Need | Tool |
|---|---|
| Charts, SMA, RSI, ATR, Bollinger alerts | TradingView |
| Quick performance and volume | Finviz, Yahoo Finance |
| ETF holdings | issuer pages, ETF.com, VettaFi |
| VIX and VIX3M | CBOE, TradingView |
| Earnings/guidance | company IR pages, Seeking Alpha headlines, Nasdaq earnings calendar |

---

## 9. Thirty-Minute Quarterly Checklist

1. Rebalance back to target weights if any ETF is above its upper band.
2. Cut `SOXL + TQQQ` back to preferred range if above 10-12%.
3. Review quarterly capex from Microsoft, Google, Amazon and Meta.
4. Review guidance from Nvidia, TSMC, ASML, Micron, Samsung and SK Hynix.
5. Reconfirm the 12-24 month exit horizon: if the sleeve is near month 12 and has strong gains, begin staged migration to the long-term conservative allocation.
6. Document decisions before trading to prevent emotional overrides.

---

## 10. Application Implementation Plan

### 10.1 Goal

Build a simple monitor that runs daily or weekly, calculates signals, writes a Markdown/CSV report, and optionally sends alerts. The application should not place trades. It should produce deterministic recommendations: `GREEN`, `YELLOW`, `RED`, `TAKE_PROFIT`, `REBALANCE`.

### 10.2 Minimal Architecture

```text
portfolio-monitor/
├── config.yaml              # tickers, targets, thresholds, alert settings
├── monitor.py               # CLI entry point
├── data.py                  # price/VIX download
├── indicators.py            # SMA, RSI, ATR, Bollinger, correlation
├── signals.py               # yellow/red/take-profit rules
├── report.py                # markdown/csv/html output
├── state.json               # entry prices, high-water marks, last alerts
└── reports/
    └── YYYY-MM-DD-report.md
```

### 10.3 Data Sources

| Data | Practical Source | Notes |
|---|---|---|
| ETF OHLCV | `yfinance` or Stooq | easy but not institutional quality |
| VIX / VIX3M | Yahoo/CBOE symbols if available | verify ticker mapping manually |
| Holdings | manual CSV from issuer pages | update monthly/quarterly |
| Fundamentals | manual checklist initially | automate later only if needed |

For this use case, manual fundamental inputs are acceptable because earnings/capex data are quarterly. Automating fundamentals too early adds complexity without much benefit.

### 10.4 Example `config.yaml`

```yaml
portfolio_value: 10000
base_currency: USD

positions:
  DRAM:
    target_weight: 0.15
    max_weight: 0.20
    type: core
    proxy: SMH
  SMH:
    target_weight: 0.25
    max_weight: 0.30
    type: core
    proxy: SMH
  AIS:
    target_weight: 0.15
    max_weight: 0.20
    type: core_new
    proxy: QQQ
  SOXL:
    target_weight: 0.06
    max_weight: 0.08
    hard_max_weight: 0.12
    type: leveraged
    proxy: SMH
  TQQQ:
    target_weight: 0.04
    max_weight: 0.06
    hard_max_weight: 0.10
    type: leveraged
    proxy: QQQ
  POW:
    target_weight: 0.10
    max_weight: 0.15
    type: satellite
    proxy: QQQ

cash_target_weight: 0.25

thresholds:
  core_yellow_drawdown: 0.10
  core_red_drawdown: 0.18
  leveraged_yellow_drawdown: 0.10
  leveraged_red_drawdown: 0.18
  sma_fast: 50
  sma_slow: 200
  sma_tactical: 20
  rsi_window: 14
  rsi_overbought: 75
  rsi_extreme: 80
  atr_window: 14
  atr_stop_core: 3.0
  atr_stop_leveraged: 2.5
  volume_spike_multiple: 1.5
  corr_window: 20
  corr_yellow: 0.90
  corr_red: 0.95
  vix_yellow: 25
  vix_red: 30
  vix3m_ratio_yellow: 1.00
  vix3m_ratio_red: 1.05
```

### 10.5 Core Indicator Logic

```python
def sma(close, window):
    return close.rolling(window).mean()

def rsi(close, window=14):
    delta = close.diff()
    gain = delta.clip(lower=0).rolling(window).mean()
    loss = (-delta.clip(upper=0)).rolling(window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def atr(high, low, close, window=14):
    prev_close = close.shift(1)
    tr = max_of_columns(
        high - low,
        (high - prev_close).abs(),
        (low - prev_close).abs(),
    )
    return tr.rolling(window).mean()

def bollinger(close, window=20, k=2):
    mid = close.rolling(window).mean()
    std = close.rolling(window).std()
    return mid, mid + k * std, mid - k * std
```

ATR normalization is used because raw percentage moves are not comparable across normal and high-volatility regimes `[stat_sound_indicators, p.156-157]`. A 200-day trend reference is a conventional long-term benchmark, but it should be treated as a risk-control heuristic, not proof of edge `[tech_analysis_patterns, p.163]`, `[trading_evolved, p.211-212]`.

### 10.6 Signal Engine Pseudocode

```python
def classify_position(ticker, row, config, state, market):
    signals = []

    dd_from_high = row.close / state[ticker].high_water_mark - 1
    below_sma50 = row.close < row.sma50
    below_sma200 = row.close < row.sma200
    volume_spike = row.volume > 1.5 * row.volume20

    if row.type == "leveraged":
        if dd_from_high <= -0.10 or row.close < row.sma20:
            signals.append("YELLOW")
        if dd_from_high <= -0.18 or below_sma50 or market.proxy_below_sma200:
            signals.append("RED")
        if state[ticker].weeks_held >= 6 and state[ticker].return_since_entry < 0.10:
            signals.append("TIME_STOP")
    else:
        if dd_from_high <= -0.10 or below_sma50:
            signals.append("YELLOW")
        if dd_from_high <= -0.18 or below_sma200:
            signals.append("RED")
        if below_sma50 and volume_spike:
            signals.append("CONFIRMED_SELL_PRESSURE")

    if row.weight > row.max_weight:
        signals.append("REBALANCE_TRIM")

    if state[ticker].return_since_entry >= row.take_profit_threshold:
        signals.append("TAKE_PROFIT")

    return strongest_signal(signals)
```

### 10.7 Report Output

Each run should generate a Markdown table:

```text
Date: 2026-05-15
Portfolio state: YELLOW

Ticker | Close | Weight | SMA50 | SMA200 | DD High | RSI | ATR Stop | Signal | Action
DRAM   | ...   | 15.2%  | Above | Above  | -6.1%   | 61  | ...      | GREEN  | Hold
SOXL   | ...   | 7.8%   | Below | Above  | -12.4%  | 44  | ...      | YELLOW | No add; tighten stop
```

Recommended output files:

- `reports/YYYY-MM-DD-weekly.md`
- `reports/latest.md`
- `reports/signals.csv`
- `state.json` with entry price, high-water mark, last alert and last action.

### 10.8 Automation Options

| Frequency | Mechanism | Command |
|---|---|---|
| Daily after close | cron | `30 22 * * 1-5 python monitor.py --mode daily` |
| Weekly review | cron | `00 12 * * 6 python monitor.py --mode weekly` |
| Manual | terminal | `python monitor.py --mode weekly --open-report` |

Alert channels, from simplest to more complex:

1. Local Markdown report only.
2. Email via SMTP.
3. Telegram bot message.
4. Discord webhook.
5. GitHub Actions artifact, if the data source does not require secrets.

### 10.9 Implementation Phases

| Phase | Deliverable | Complexity |
|---|---|---|
| 1 | manual spreadsheet + TradingView alerts | lowest |
| 2 | Python script for OHLCV indicators and Markdown report | low |
| 3 | persistent `state.json` with high-water marks and entry prices | medium |
| 4 | email/Telegram alerts | medium |
| 5 | dashboard/app UI | optional; only after rules stabilize |

The first implementation should be a script, not a full app. The risk rules need to prove useful before building UI complexity.

---

## 11. Alert Setup In TradingView

Create alerts for:

| Ticker | Alert |
|---|---|
| `DRAM`, `SMH`, `AIS`, `POW` | close crossing below `SMA50` and `SMA200` |
| `SOXL`, `TQQQ` | close crossing below `SMA20`, `SMA50`; 10% and 18% drawdown alerts |
| `QQQ`, `SMH` | close crossing below `SMA200` |
| `VIX` | above 25, 30, 40 |
| `VIX/VIX3M` | above 1.00 and 1.05 if supported by chart formula |

Use weekly alerts where possible for core ETF rules. Use daily alerts for 3x ETF risk controls.

---

## 12. Final Operating Rules

1. Never add to `SOXL` or `TQQQ` when the underlying proxy is below `SMA200`.
2. Never let `SOXL + TQQQ` exceed 12% without an explicit written override.
3. Do not deploy cash during a red regime; cash is optionality, not a mandate to average down.
4. If portfolio drawdown reaches -15%, cut leveraged ETFs first.
5. If portfolio drawdown reaches -20%, stop trying to be right and prioritize capital preservation.
6. If the sleeve is profitable near month 12, begin staged migration instead of waiting for the exact 24-month mark.

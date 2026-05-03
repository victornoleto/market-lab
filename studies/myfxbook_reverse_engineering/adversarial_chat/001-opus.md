# Prompt para GPT-5.5 / GPT-5: review adversarial de strategy reverse-engineering pipeline

Copie tudo abaixo do separador `===PASTE BELOW===` e cole no GPT-5.5.

===PASTE BELOW===

# Role and task

You are a senior quantitative researcher with deep experience in:
- Strategy reverse-engineering from public track records (MyFxBook, MQL5, Collective2)
- Statistical validation of retail FX/CFD strategies (DSR, PBO, walk-forward, purged k-fold)
- Vendor analysis and survivorship/selection bias detection
- Feature engineering for direction-prediction in intraday FX

I am running a reverse-engineering pipeline against the MyFxBook vendor "HappyForex" (52 published systems, ~3304 trades on the largest sample). I just finished an overnight batch validation. **I want adversarial peer review** — not validation theater. Find holes. Challenge methodology. Surface biases. Be specific.

Below I'll give you (a) the pipeline architecture, (b) the reliability scoring formula, (c) the current results, (d) one concrete signal_rule.md the LLM stage produced, and (e) specific questions I want answered.

---

## 1. Context

**Project**: I'm evaluating whether any of HappyForex's 52 published systems on MyFxBook have a recoverable, replicable direction signal that would justify paper-trading on a Pepperstone+cTrader demo.

**Constraints**:
- 100% Plano C (passive factor-tilted index portfolio) — overnight strategy work is research only, no capital allocated
- Hard-block gates for any future capital allocation: DSR p<0.05, PBO<0.5, walk-forward ≥6/8, single-block OOS bootstrap 99.9% CI low > 0, cross-lib cohérence ±3pp CAGR
- The strategy "Plano A" (short-hold CFD) is currently DORMANT after 113/113 prior FAIL on a 2-week internal hunt; reactivation requires explicit user sign-off

**Reference literature anchoring this work** (real books we own summaries for):
- López de Prado, *Advances in Financial Machine Learning* — DSR/PBO (p.196-211), purged k-fold (ch.7), feature importance MDI/MDA (ch.5, p.160-167)
- Aronson, *Evidence-Based Technical Analysis* — session/hour FX (p.367-380), data-mining bias and MCP correction (p.264-265, p.283-287)
- Carver, *Systematic Trading* — cost model retail (p.185-188)
- Chan, *Algorithmic Trading* — mean-reversion vs momentum regime classification (ch.2, ch.6)
- Kaufman, *Trading Systems and Methods* — Bollinger band canonical 20/2 parameterization (p.323-324)
- Taleb, *Fooled by Randomness* — track-record bias / vendor selection
- Pardo, *Testing and Tuning Market Trading Systems* — walk-forward methodology

---

## 2. Pipeline architecture (3 stages)

```
Stage 1 (Python, deterministic)
  ├─ For each trade in trades.parquet (n=100..4000 per system):
  │  ├─ Extract 56 multi-timeframe entry features at trade.open_dt_utc
  │  │  • Calendar: hour_utc, dow, session ∈ {Tokyo,London,NY,Late_NY}, is_first_min_of_hour
  │  │  • Per timeframe ∈ {M1, M5, M15, H1, H4}:
  │  │      ret_1, ret_3, ret_10  (log returns of N most-recent bars)
  │  │      ema_dist_20            ((close - EMA20) / ATR14)
  │  │      atr_ratio              (ATR14[tf] / ATR14[H1])
  │  │      bb_pos_20_2            ((close - SMA20) / (2*std20))  Bollinger position
  │  │      range_norm             ((high - low) / ATR14)
  │  │      prior_bar_sign         sign(close - open) of last bar
  │  │      close_vs_session_open  sign vs session-open H1 close
  │  │  • Cross-pair: dollar_index_proxy, pair_cluster_dispersion
  │  └─ All features computed using ONLY data strictly before trade.open_dt_utc
  │     (lookback only, no look-ahead)
  ├─ Mine top-K=10 candidate direction rules using THREE independent miners:
  │  ├─ Univariate scan: for each (feature, decile threshold), measure match-rate
  │  │   of "feat > threshold ⇒ Buy/Sell". Bonferroni-corrected p-value over n_tests
  │  │   to reject data-snooping bias
  │  ├─ Decision tree (max_depth=4, min_samples_leaf=50) with purged k-fold CV
  │  │   (5 folds, embargo=5 trades around each test fold)
  │  └─ RIPPER rule mining (lib wittgenstein) — "IF cond1 AND cond2 THEN side"
  │     propositional rule learning
  └─ Output: features.parquet + candidates.json + fingerprint.md (1-page synthesis)

Stage 2 (LLM via "claude --dangerously-skip-permissions --model sonnet -p '/decode-system <id>'")
  ├─ Subagent reads fingerprint.md + candidates.json + system_info.json
  ├─ Classifies system into 8-family taxonomy:
  │     LATE_NY_BREAKOUT (entries 21-01 UTC, FX majors, time-based exit)
  │     LONDON_OPEN_MOMENTUM / LONDON_OPEN_MR (entries 06-09 UTC)
  │     NY_SESSION_REVERSAL (entries 12-16 UTC)
  │     OVERLAP_NY_LONDON_RANGE (entries 12-16 UTC, BB or range-position direction)
  │     OVERNIGHT_GAP_FADE
  │     FACTOR_SCALPING (distributed entries, durations < 30min)
  │     MARTINGALE_GRID (k1_pass=False, doubling-after-loss)
  │     UNCATEGORIZED (heuristics inconclusive, confidence < 0.5)
  ├─ Refines rule with explicit thresholds pulled from candidates.json (not invented)
  ├─ Cites ≥ 2 books from the knowledge base above with literal quotes
  └─ Outputs signal_rule.md (YAML front-matter + narrative)

Stage 3-lite (Python, "reliability proxy" — NOT full Stage 3)
  Reliability score ∈ [0,1] = weighted combination of:
    0.25 × direction_predictability  = max(0, (top_candidate_match_rate_cv - 0.5) / 0.25)
    0.20 × family_clarity            = LLM confidence from signal_rule.md
    0.20 × timing_concentration      = sum(top-3 hourly trade counts) / total
    0.10 × sanity_pass               = 1 if k1_pass else 0  (martingale filter)
    0.10 × age_freshness             = max(0, 1 - days_since_last_trade / (5*365))
    0.10 × vendor_quality            = base(Real=0.6/Demo=0.3) + n_trades_bonus
    0.05 × pair_coverage             = fraction of trades on Dukascopy-supported pairs
  Bands:
    HIGH   ≥ 0.65  → paper-trading candidate (after Stage 3 proper)
    MEDIUM 0.45-0.65
    LOW    < 0.45  (also forced to LOW if sanity_pass = 0)
```

**Honest caveat**: Stage 3 *proper* (full OHLC replicator running the decoded rule on 2013-2025 history, comparing equity curves, applying gates §2.4) was deferred because of overnight time budget. The "reliability proxy" measures **decodability + freshness + vendor quality**, not **edge presence**. I plan to add a "replicator-lite" today that measures signal precision/recall (does the decoded rule fire at the same timestamps as the system's real entries, with the same direction?) — but even that is signal-level, not PnL-level.

---

## 3. Current results (48/52 systems processed)

**Distribution**:
- HIGH ≥ 0.65: **22 systems**
- MEDIUM 0.45-0.65: **4 systems**
- LOW < 0.45: **22 systems** (10 of which are MARTINGALE_GRID forced-LOW)
- FAIL/SKIP: 2 (one had only DJ30.X index trades, no Dukascopy coverage)

**Family classifications**:
- UNCATEGORIZED: **14**  (Sonnet refused to commit, low confidence)
- FACTOR_SCALPING: **13**  (mostly "Happy Gold" replicas across 8 brokers)
- MARTINGALE_GRID: **10**  (k1_pass FAIL — auto-LOW)
- OVERLAP_NY_LONDON_RANGE: 4
- LATE_NY_BREAKOUT: 3
- NY_SESSION_REVERSAL: 2
- LONDON_OPEN_MOMENTUM: 1
- UNKNOWN/error: 1

**Top-10 HIGH by reliability**:

| # | reliability | family | account | n_trades | system_id | name |
|---:|---:|---|---|---:|---|---|
| 1 | **0.871** | LATE_NY_BREAKOUT | Real | 221 | 10224499 | Happy Market Hours FM - REAL |
| 2 | 0.850 | NY_SESSION_REVERSAL | Real | 1083 | 11171596 | Happy Algorithm PRO FM - REAL (SET1) |
| 3 | 0.801 | FACTOR_SCALPING | Real | 197 | 11155858 | Happy Brexit FM (HR) |
| 4 | 0.797 | FACTOR_SCALPING | Real | 1024 | 8647517 | Happy Gold - VTMarkets (M30) |
| 5 | 0.784 | FACTOR_SCALPING | Demo | 1763 | 2421356 | Happy Gold - ICMarkets (M30) |
| 6 | 0.782 | OVERLAP_NY_LONDON_RANGE | Real | 652 | 10281851 | Happy Gold - Eightcap (M30) |
| 7 | 0.778 | FACTOR_SCALPING | Real | 202 | 11207608 | Happy Gold - BBM |
| 8 | 0.776 | FACTOR_SCALPING | Real | 232 | 11628637 | Happy Bitcoin - VM |
| 9 | 0.774 | NY_SESSION_REVERSAL | Real | 915 | 9375654 | Happy Gold - TMGM (M30) |
| 10 | 0.760 | FACTOR_SCALPING | Demo | 2213 | 6541963 | Happy Gold - Tickmill (M15) |

**Cross-validation accident**: Two separate systems — `1407880` (OLD HMH v2.3.1, blackout 2021) and `10224499` (Happy Market Hours FM REAL, fresh, top-1) — were independently classified as `LATE_NY_BREAKOUT` despite Sonnet not knowing they're related. Same vendor likely → same underlying algorithm → fingerprint reproducibly recovered.

**Cohort observation**: 8 systems named "Happy Gold - <broker> (M30/M15)" all clustered into FACTOR_SCALPING / OVERLAP_NY_LONDON_RANGE with reliability 0.74-0.80. One algorithm replicated across 8 broker accounts.

---

## 4. Sample Sonnet output (for one system, raw, unedited)

This is the actual `signal_rule.md` produced by Sonnet for system 10062918 (Happy Forex FM REAL Set 3, 731 trades on AUDUSD+EURCHF, multi-day hold, drawdown 51.79%):

```yaml
---
system_id: 10062918
family: UNCATEGORIZED
confidence: 0.52
generated: 2026-05-02
rule:
  entry_window_utc: ["00:00", "23:59"]   # no dominant session window
  pairs: [AUDUSD, EURCHF]
  direction: |
    SELL if ema_dist_20_H4 > 0.06
    BUY  if ema_dist_20_H4 <= 0.06 AND ret_10_H1 <= 0.0
    BUY  if ema_dist_20_H4 <= 0.06 AND ret_10_H1 > 0.0 AND bb_pos_20_2_M5 > -0.17
    SELL if ema_dist_20_H4 <= 0.06 AND ret_10_H1 > 0.0 AND bb_pos_20_2_M5 <= -0.17
  exit:
    max_holding_hours: 144      # p50 hold = 144h, p95 = 948h
    take_profit_pips: null
    stop_loss_pips: null
  sizing: fixed_lot_0.01
citations:
  - "[algo_trading_chan, p.41, ch.2] — 'Stationarity: a price series whose
     variance grows slower than a geometric random walk; described by the
     Ornstein-Uhlenbeck process; prerequisite for mean-reversion trading'"
  - "[algo_trading_chan, p.153-154, ch.6] — 'mean-reverting strategies have
     capped upside but potentially unbounded drawdown'"
  - "[advances_fin_ml, p.160-161] — 'Mean Decrease Impurity (MDI): in-bag
     feature importance measure based on weighted average impurity reduction
     across all splits; fast but biased toward high-cardinality features'"
  - "[evidence_based_ta, p.283-287] — 'observed performance of the best of N
     rules systematically overestimates expected performance'"
risk_flags:
  - "broker=ForexMart — obscure broker; confidence -0.10 vs Real Pepperstone equiv"
  - "drawdown=51.79% — system in severe underwater state"
  - "hold p50=144h (~6 days), p95=948h (~39 days) — multi-day swing not intraday"
  - "max gap days=75.1 — large gaps suggest manual intervention"
  - "UNCATEGORIZED — no session-specific entry window; all-hours increases noise"
---
```

This system scored reliability **0.730 HIGH** on the proxy despite Sonnet's `confidence=0.52` UNCATEGORIZED label. The high score came from `direction_predictability=1.0` (top candidate match_rate_cv = 0.793 from decision tree).

---

## 5. Specific questions for you (be adversarial)

Please address each of these in your response, in order. Be concrete — cite the data above when challenging.

### Q1. Methodology — am I missing a known better approach?

The 3-stage pipeline (Python feature mining + LLM family naming + Python proxy score) is my own design. **What standard approaches in the literature have I missed?** Specifically:
- Has academic finance / quant literature published on "vendor track-record reverse-engineering" as a discipline? Names, papers, libraries?
- Is there a more powerful candidate-rule miner than my univariate + tree + RIPPER trio? (e.g., is wittgenstein's RIPPER known to be weak compared to alternatives?)
- Is my feature pack (multi-tf returns + EMA/BB/ATR) standard for FX direction-pred work or am I missing canonical features?

### Q2. Reliability proxy — is this scoring formula honest or marketing?

The proxy weights are: 0.25 direction_pred + 0.20 family_clarity + 0.20 timing_concentration + 0.10 sanity + 0.10 age + 0.10 vendor + 0.05 pair_coverage.
- What's wrong with this weighting? What component is over/under-weighted relative to what it actually measures?
- The cutoff HIGH ≥ 0.65 puts 22/48 = 46% of systems in HIGH. **Is this distribution suspicious?** What would a calibrated cutoff look like?
- `direction_predictability` is in-sample purged k-fold match rate. **In what specific failure modes can this be high but the rule actually doesn't reproduce the system?** I plan to add a "replicator-lite" (signal precision/recall vs system trades) — what other tests should be in there?

### Q3. The 14 UNCATEGORIZED label — false negative or honest?

Sonnet labeled 14/48 systems UNCATEGORIZED with low confidence. **Is "UNCATEGORIZED with high direction_predictability" an artifact** (the underlying decoder works but the family taxonomy is too narrow) **or a real signal** (the system has no exploitable pattern)?
- Should I expand the 8-family taxonomy? What categories are missing?
- For system 10062918 above (UNCATEGORIZED, conf 0.52, but 79.3% match-rate on 731 trades) — is this a "decodable but unfamiliar" system or a noisy artifact?

### Q4. The Happy Gold cohort — what does it actually mean?

8 "Happy Gold" systems on different brokers, all classified into 2-3 families, reliability 0.74-0.80. My current interpretation: "vendor sells one algorithm under multiple broker accounts to maximize subscription revenue."
- **Is this interpretation correct or naive?** What alternative explanations should I consider?
- If they ARE the same algorithm, can I aggregate their trade history (~6000 trades total) for a more powerful Stage 1 mining? Or is each broker's slippage/spread enough to corrupt the cross-account features?
- How would you statistically verify "same algorithm" beyond family-name agreement?

### Q5. Survivorship and selection bias

HappyForex publishes **only the systems they want public**. They've abandoned 1407880 (OLD HMH v2.3.1) but the live FM-REAL version has only 221 trades (=very fresh).
- What's the base rate of survivor-bias inflation in MyFxBook vendor track records? Cite numbers if you can.
- Is `10224499` (top-1, 221 trades) too short to extract a reliable rule — or does the cross-validation against `1407880` (3304 trades, blackout) compensate for sample size?
- How do I detect "vendor is cherry-picking accounts to publish" beyond the obvious (sanity martingale flag)?

### Q6. The 113/113 prior FAIL context

I previously ran a 2-week parameter-grid hunt for short-hold CFD strategies and got 113 candidates that all failed honest gates §2.4 (DSR/PBO/WF/bootstrap). That's the reason Plano A is currently DORMANT.
- **Should that prior result lower my prior probability that any HappyForex system is genuinely tradeable** to near-zero? Or are vendor-published track records a structurally different population from grid-search candidates (because vendors only publish what they think works, they have prior insight, etc.)?
- What's the calibrated probability that even my top-3 HIGH systems pass full Stage 3 gates §2.4?

### Q7. What would you do tomorrow?

Concretely, after the loop closes (4 more systems), I have 3 paths:
- **Path A**: Build replicator-lite (signal precision/recall vs system trades, no PnL). ~2h. Tells me "does the rule fire at the right times."
- **Path B**: Re-run TOP-5 HIGH + UNCATEGORIZED-with-high-direction with Opus 4.7 (~$10 cost). Tells me "did Sonnet underclassify."
- **Path C**: Skip both, jump straight to Stage 3 proper (full OHLC replicator + gates §2.4). 1-2 days build.

Given everything above, **what's your prioritization** and why? What did I forget?

### Q8. Single most important critique

Pretend you're reviewing this for a quant fund's investment committee. **What's the one critique that would kill the project** if I don't address it before reporting "I have N HIGH-reliability candidates"?

---

## 6. Output format request

Please structure your response as:

```
## Q1. [your answer, concrete, with citations to data above when relevant]
## Q2. ...
## Q3. ...
...
## Q8. [the kill-shot critique]
## Bottom line
[3 sentences max. Should I keep going on this project? What would change your mind?]
```

Be specific. Avoid hedge phrases like "it depends" without saying what it depends on. If you don't know something, say "I don't know X" — that's more useful than confident-sounding fluff.

===END PASTE===

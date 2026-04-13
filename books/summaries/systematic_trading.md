# Systematic Trading: A unique new method for designing trading and investing systems

## Metadata
- **Autor:** Robert Carver [p.2, p.4]
- **Ano:** 2015 [p.5]
- **Editora:** Harriman House Ltd, Petersfield, Hampshire [p.5]
- **Páginas:** 326 (print pages; book body numbered to ~300) [metadata]
- **ISBN:** 9780857194459 (hardback); 9780857195005 (eBook) [p.5]
- **Foco principal:** A modular framework for designing systematic trading/investing systems that separates forecasting, volatility targeting, position sizing and portfolio construction — with explicit anti-overfit guidance.

## 1. Tese Central

Human judgment is systematically flawed by cognitive biases (prospect theory, overconfidence, narrative fallacy) that make discretionary trading consistently inferior to simple objective rules [ch.1, p.11-14]. The solution is a **modular trading system** in which a trading rule's forecast, the volatility target, the position sizing and the portfolio allocation are decoupled so each can be designed, tested, and reasoned about in isolation [ch.5-11, p.108-223]. Carver argues that *how you design the system* matters more than *which rules* you pick: avoid over-fitting, over-betting and overtrading, use handcrafted / bootstrapped portfolio weights rather than single-period Markowitz, and use Half-Kelly (not full Kelly) to set risk [p.20, p.145-147, p.259-260].

A corollary repeated throughout: a single diversified framework works for (a) asset-allocating investors, (b) semi-automatic discretionary traders, and (c) staunch systems traders, by swapping only the forecast component [p.ix-x, p.116-123].

## 2. Conceitos-Chave

- **Instrument block** — the unit size of trading ("one share", "one futures contract", "£10/point spread bet"). [p.154, ch.10]
- **Block value** — monetary P&L for a 1% price change on one instrument block [p.154-155, ch.10]
- **Price volatility** — expected daily standard deviation of % returns for the instrument; default estimated with a 25-day simple MA or EWMA with 36-day span [p.155-156]
- **Instrument currency volatility** — block value × price volatility [p.158]
- **Instrument value volatility** — instrument currency volatility × FX rate into account currency [p.158]
- **Volatility scalar** — daily cash vol target ÷ instrument value volatility; number of blocks consistent with forecast = +10 [p.159, p.162]
- **Subsystem position** — position for one instrument assuming all capital is there = (forecast × volatility scalar) ÷ 10 [p.160, p.162]
- **Forecast** — dimensionless prediction, scaled to expected absolute value of 10, capped at ±20 [p.122-123, ch.7]
- **Forecast scalar** — multiplicative constant applied to raw forecast to target average |forecast|=10 [p.284-285, p.297]
- **Forecast weights** — portfolio weights across rule variations producing a combined forecast per instrument [p.126-128]
- **Forecast diversification multiplier** — factor applied to combined forecast so it retains avg |forecast|=10 after diversification; 1 / √(W·H·Wᵀ) [p.129, p.297]
- **Instrument weights** — portfolio weights across trading subsystems [p.166-168]
- **Instrument diversification multiplier** — same formula applied across subsystems [p.170, p.298]
- **Volatility target (percentage / cash / daily / annualised)** — expected std dev of returns; calibrates overall risk appetite [p.137]
- **Trading capital** — actual cash committed; never borrowed money [p.138]
- **Half-Kelly** — set percentage vol target = 0.5 × (realistic back-tested Sharpe) [p.145-147]
- **Handcrafting** — Carver's manual portfolio optimisation using a grouped lookup table of weights, derived from bootstrapped experiments [p.77-79, ch.4]
- **Bootstrapping (portfolio)** — repeat single-period optimisation on random subsets of data and average the weights [p.75-76, p.289-290]
- **EWMAC** — Exponentially Weighted Moving Average Crossover; trend-following rule [p.117-119, p.282-285]
- **Carry rule** — forecast based on annualised vol-standardised expected return if price unchanged [p.119-120, p.285-288]
- **Law of active management** — SR ∝ √(number of independent bets/year); diversification across uncorrelated assets can multiply SR [p.41-42]
- **Volatility standardisation** — scale all returns to same expected std dev so forecasts and weights are comparable [p.39-40]
- **Predictable risk** — recent historic daily std dev; predictable portion of risk [p.39]
- **Skew** — asymmetry of return distribution; trend rules = positive skew, carry/relative value = negative skew [p.32-34]
- **Meddling** — discretionary interference with a running system, driven by overconfidence; killed by commitment mechanisms [p.17-19]

## 3. Fórmulas / Equações

**Volatility scalar** [p.159, p.162]

$$\text{Volatility scalar} = \frac{\text{Daily cash volatility target}}{\text{Instrument value volatility}}$$

- Both quantities in the currency of trading capital.
- Do NOT round to an integer at this stage.

**Subsystem position** [p.160, p.162]

$$\text{Subsystem position} = \frac{\text{Forecast} \times \text{Volatility scalar}}{10}$$

- 10 is the target average absolute forecast.
- Negative forecasts ⇒ short positions.

**Daily ↔ annualised conversions** [p.21, p.137]

$$\sigma_{\text{annual}} = \sigma_{\text{daily}} \times \sqrt{256} = \sigma_{\text{daily}} \times 16$$

$$\mu_{\text{annual}} = \mu_{\text{daily}} \times 256$$

- Assumes ~256 business days/year and zero autocorrelation [p.21].

**Annualised Sharpe ratio** [p.32]

$$SR_{\text{annual}} \approx 16 \times SR_{\text{daily}} = \frac{\mu_{\text{annual}}}{\sigma_{\text{annual}}}$$

**Instrument currency volatility** [p.158]

$$\text{Instrument currency vol} = \text{Block value} \times \text{Price volatility}$$

**Instrument value volatility** [p.158]

$$\text{Instrument value vol} = \text{Instrument currency vol} \times \text{FX}_{\text{instr}/\text{account}}$$

**Diversification multiplier (forecast or instrument)** [p.297-298]

$$\text{DM} = \frac{1}{\sqrt{W \cdot H \cdot W^{T}}}$$

- $W$ = vector of weights summing to 1.
- $H$ = correlation matrix (negative correlations **floored at zero** to avoid dangerously inflated multipliers) [p.297-298].

**EWMA (recursive form)** [p.283, p.298]

$$E_{t} = A \cdot P_{t} + (1 - A) \cdot E_{t-1}$$

With decay $A = \frac{2}{L+1}$ where $L$ is the look-back window (span). Default vol estimation: $L=36$ (EWMA) or $L=25$ (simple MA) [p.156, p.298].

**EWMAC forecast pipeline** [p.282-285]

1. Compute fast EWMA $E_{\text{fast}}$ (lookback $L_{\text{fast}}$) and slow EWMA $E_{\text{slow}}$ (lookback $L_{\text{slow}} = 4 \times L_{\text{fast}}$).
2. Raw crossover: $E_{\text{fast}} - E_{\text{slow}}$.
3. Vol-adjust by dividing by daily std dev in **price points** (= % price volatility × current price).
4. Multiply by forecast scalar from table 49 (p.285):

| Variation        | Forecast scalar |
|------------------|----------------:|
| EWMAC 2, 8       | 10.6            |
| EWMAC 4, 16      | 7.5             |
| EWMAC 8, 32      | 5.3             |
| EWMAC 16, 64     | 3.75            |
| EWMAC 32, 128    | 2.65            |
| EWMAC 64, 256    | 1.87            |

5. Cap at ±20 [p.285].

Recommended pair set: 2:8, 4:16, 8:32, 16:64, 32:128, 64:256 (ratio 4, correlations ~0.90 between adjacent pairs) [p.284].

**Carry forecast** [p.288]

$$\text{Raw carry} = \frac{\text{Net expected return in price units (annualised)}}{\sigma_{\text{price, annualised}}}$$

$$\text{Forecast}_{\text{carry}} = 30 \times \text{Raw carry}$$

- Forecast scalar = 30 [p.288].
- Cap at ±20 [p.288].
- Suggested turnover ≈ 10 round-trips/year when updated weekly [p.288].

**General forecast scalar calibration** [p.297]

$$\text{Forecast scalar} = \frac{10}{\text{avg}(|{\text{raw forecast}}|)}$$

Use long history across many instruments (do NOT peek at performance) [p.297].

**Half-Kelly percentage volatility target** [p.146-147]

$$\text{Percentage vol target} = 0.5 \times \text{Realistic back-tested Sharpe}$$

With a further halving for negative-skew strategies [p.146-147, table 25].

**Realistic SR adjustment** [p.146]

$$SR_{\text{realistic}} = 0.75 \times SR_{\text{out-of-sample-bootstrap-backtest}}$$

(Ratio of 0.75 applies only to out-of-sample bootstrap; lower ratios if fitting was sloppier) [p.146, table 14 referenced].

## 4. Algoritmos e Pseudocódigo

**End-to-end position sizing (staunch systems trader)** [ch.9-10, p.135-163]

```
# Inputs: prices, trading capital C, percentage vol target v%
# Outputs: subsystem position per instrument

annual_cash_vt = C * v_pct
daily_cash_vt  = annual_cash_vt / 16   # sqrt(256)

for each instrument I:
    price_vol_pct = stdev(pct_returns(I), lookback=25)    # or EWMA lookback=36
    # Skip / warn if price_vol_pct is abnormally low (regime risk, see p.156, p.159)
    block_value            = one_pct_of_price * contract_multiplier   # p.154-155
    instr_ccy_vol          = block_value * price_vol_pct
    instr_val_vol          = instr_ccy_vol * fx_instr_to_account
    volatility_scalar      = daily_cash_vt / instr_val_vol            # p.159
    forecast               = combined_forecast(I)                     # avg |F|=10, capped ±20
    subsystem_position     = forecast * volatility_scalar / 10        # p.160
```

**Combined forecast construction (staunch systems trader)** [ch.8, p.125-134]

```
# For each instrument:
for each rule variation r:
    F_r = forecast_scalar_r * volatility_adjusted_raw_r
    F_r = clip(F_r, -20, +20)

combined = sum(forecast_weight_r * F_r for r)   # weights sum to 1

# Account for diversification across rules:
H = correlation_matrix(F_r series, floor_negatives_at_zero=True)
W = vector(forecast_weight_r)
FDM = 1 / sqrt(W @ H @ W.T)                     # p.297

combined_final = clip(combined * FDM, -20, +20) # p.130
```

**Portfolio of subsystems** [ch.11, p.165-179]

```
# Compute subsystem_position per instrument (above)
# Aggregate to portfolio:
portfolio_position_I = subsystem_position_I * instrument_weight_I * IDM
# IDM uses correlation matrix of subsystem returns, same formula as FDM (p.298)
```

Use 0.70 × price-return correlations (from appendix C tables 50-55) as proxy for subsystem-return correlations, for dynamic systems [p.167-168, p.294]. Asset allocators use unadjusted correlations [p.294].

**Handcrafting portfolio weights (bottom-up)** [ch.4, p.78-80]

```
1. Group highly correlated assets (same asset class / style / region).
2. Within each group, look up row in Carver's table 8 (p.79) using the
   pairwise correlation pattern to get intra-group weights.
3. Across groups, repeat using the correlation between group returns.
4. Final weight(asset) = intra-group weight * group weight.
5. Optionally repeat with more levels.
```

Reference weights from table 8 (p.79): groups of 1 → 100%; pairs → 50/50; 3-asset patterns with specific correlations (0.0, 0.5, 0.9) map to tabulated triplets, e.g. corr (0.0, 0.5, 0.0) → 30/40/30; corr (0.9, 0.5, 0.9) → 42/16/42.

**Bootstrap portfolio optimisation** [appendix C, p.289-290]

```
for i in 1..N:                 # N ≥ 100 iterations typical (p.290)
    subset = random_block_sample(returns, length≈10% of history) # p.290
    mu, Sigma = estimate(subset)
    w_i = markowitz_max_sharpe(mu, Sigma, weights >= 0, sum(w)=1)
weights = mean_i(w_i)
```

**Rolling volatility (EWMA, spreadsheet form)** [appendix D, p.298-299]

```
A  = 2 / (1 + L)                       # L=36 for default
r2[t] = return[t]^2
var[t] = A * r2[t] + (1-A) * var[t-1]
vol[t] = sqrt(var[t])
```

**A & B system (stop-loss / profit-target, semi-automatic stop)** [appendix B, p.281-282]

```
Standard position size = $100,000 / instrument_value_volatility  # in dollars at entry
deviation = price_volatility_pct * current_price
Enter long 1 standard size
Track entry price and running high

# While long:
  if price > entry + A*deviation       -> reverse to short 1 size (profit target)
  if price < running_high - B*deviation -> reverse to short 1 size (trailing stop)
  on reversal: recompute deviation and standard size

# Mirror logic for short positions.
```

Carver uses the stop-loss component only for semi-automatic traders; he does not recommend the A&B system itself for real trading [p.281].

## 5. Regras de Trading Explícitas

- **REGRA [p.122-123]:** Every individual forecast must have expected |F| ≈ 10 and be capped at [-20, +20] (or [0, +20] if you can't short).
- **REGRA [p.130]:** Combined forecasts must also be capped at ±20 after applying the forecast diversification multiplier.
- **REGRA [p.146-147, table 25]:** Set **percentage volatility target = 0.5 × realistic back-tested SR** (Half-Kelly). Halve again for negative-skew strategies.
- **REGRA [p.146, table 25 cap]:** Assume realistic SR ≤ 1.0 for staunch systems traders, ≤ 0.5 for semi-automatic traders, ≤ 0.4 for asset allocators, regardless of backtest.
- **REGRA [p.149]:** Roll up/down your cash volatility target with changes in trading capital (P&L and flows). For vol targets >15% re-check daily; with leverage, at least weekly.
- **REGRA [p.148]:** Only ever change the percentage vol target **downwards**, and only once, if you discover your risk tolerance was mis-specified. Never ratchet up.
- **REGRA [p.138]:** Trading capital = only cash you can afford to lose. Never trade with borrowed money or funds earmarked for debt service.
- **REGRA [p.156, p.159]:** Use a 25-day simple MA (or 36-day EWMA) of daily % returns as default vol estimate. Avoid low-vol regimes / instruments — blow-up risk.
- **REGRA [p.126-130, ch.8]:** Combined forecast = Σ (forecast weight × rule forecast) × forecast diversification multiplier, then cap at ±20.
- **REGRA [p.167-168]:** For dynamic subsystems, use subsystem-return correlation ≈ 0.70 × price-return correlation (from table 50-55). Asset allocators use price-return correlations directly.
- **REGRA [p.297-298]:** Floor negative correlations at zero before computing any diversification multiplier.
- **REGRA [p.129, ch.8]:** Prune rule variations whose pairwise correlation exceeds 0.95 (redundant). [p.122, appendix B p.284]
- **REGRA [p.122]:** Exclude variations that trade too slowly (avg holding > several months; can't be distinguished from noise) OR too fast (costs dominate); see chapter 12, "Speed and Size".
- **REGRA [p.260, epilogue]:** Speed limit — choose turnover so trading costs ≤ ⅓ of pessimistic expected SR for each trading subsystem.
- **REGRA [p.62-67, ch.3]:** Fit rules using rolling or expanding out-of-sample windows only. Never in-sample. With a 5-year rolling window, ensure enough data for statistical significance (decades may be needed, see table 5).
- **REGRA [p.67]:** Pool data across instruments when fitting; assume a rule should work across instruments unless there is statistically significant evidence otherwise [p.64-67].
- **REGRA [p.68]:** Reserve actual performance data for deciding forecast weights, not for selecting which rules/variations to keep.
- **REGRA [p.159-160]:** Exclude instruments whose natural vol is so low that hitting the vol target requires dangerous leverage (e.g. EUR/CHF pre-Jan-2015 would have needed 50×; survivors needed ≤7× ⇒ max vol target 7%) [p.143].
- **REGRA [p.148]:** Maximum recommended percentage vol target for any trader type = 50%. Most traders should use much less (tables 25-26).
- **NUNCA [p.138]:** Never go above full-Kelly bet size; full-Kelly has an uncomfortable drawdown profile even when SR estimate is correct [p.146, Thorpe quote].
- **NUNCA [p.297-298]:** Never use negative correlation values inside a diversification multiplier — it inflates the multiplier dangerously.
- **NUNCA [p.18]:** Never use subjective rules ("sell for *small* losses") in a system — they invite meddling.
- **NUNCA [p.159]:** Never round the volatility scalar or subsystem position to an integer during intermediate calculations.
- **NUNCA [p.20, p.260]:** Never meddle with a running system. Use commitment mechanisms (automation + pre-committed rules) as per Odysseus.

## 6. Pitfalls e Anti-patterns

- [p.19-20] **Over-fitting**: choosing rules or parameters because they look good in a back-test. "50 models from a random-data pool" anti-pattern — Aqueduct Capital anecdote p.52.
- [p.20-21] **Over-betting**: using leverage to boost expected return on an instrument whose natural vol is suspiciously low — invariably a negative-skew trap.
- [p.20] **Overtrading**: holding periods too short relative to costs; amateur traders' modal failure mode.
- [p.54] **In-sample testing** ("cheating with a time machine"): using the full history to select variation, then reporting performance over the same period. Will always look amazing and always disappoint live.
- [p.57-58] **Random rule selection**: Carver's gold-futures experiment shows picking the best of 90 variations yields SR 0.07; picking at random yields 0.20; **equal-weighting all 90** yields 0.33 [p.58].
- [p.59] **Multiple-testing problem**: even with 1 year of random data, testing 100 rules at SR cutoff 2.0 still passes ~2.3 rules on average. With 10 years of data and 50 rules, cutoff must be 1.0 [p.60, tables 3-4].
- [p.61-63] **Insufficient data for rule comparison**: a true SR 0.30 vs 0.80 rule at zero correlation takes ~30 years to distinguish via T-test [p.63, tables 5-6].
- [p.64] **Fitting each instrument separately** — classic narrative-fallacy trap; pooling across instruments is almost always better [p.64-67].
- [p.72-74] **Classic single-period Markowitz**: produces extreme, unstable weights (NASDAQ 100% → 0% → swap). Don't use. Use bootstrapping or handcrafting [p.75-80].
- [p.77] **Pseudo-optimisation by torturing the software until it agrees with you** — admit you're handcrafting and do it explicitly.
- [p.34-35] **Using Sharpe ratio alone to compare positive-skew vs negative-skew rules** — SR hides tail risk. Negative-skew SR is systematically flattering.
- [p.46-47] **Unrealistic SR expectations**: institutional long-run SR > 1.0 is virtually never sustained; assume max 1.0 [p.47, p.260].
- [p.47-48] **Chasing SR through higher speed**: theoretical SR gain from law of active management is eaten by costs except in the cheapest futures [p.48, table 2].
- [p.145-147] **Full Kelly**: geometric-return plot (figure 21) shows full Kelly sits on a knife-edge; 2x overbetting → deep negative geometric return [p.146].
- [p.156, p.159] **Positions sized on very low recent vol**: CDS 2007, Eurodollar ZIRP, CHF Jan 2015 — inverse vol sizing blows up after calm regimes.
- [p.20] **Overconfidence ⇒ undiversified portfolios**: both amateurs and professionals concentrate. Carver's framework uses 40+ futures explicitly to avoid this [p.44, p.133].
- [p.148] **Tweaking vol target up after good performance** → meddling in disguise [p.148].
- [p.297-298] **Failing to floor negative correlations** in DM calculations → diversification multiplier explodes.
- [p.122-123, p.284] **Keeping rule variations with correlation > 0.95** — pure redundancy, adds complexity without benefit.
- [p.67] **Using data-first with no understanding of degrees of freedom** — "don't use a method blindly just because it came with the software."

## 7. Parâmetros Sensíveis

- **Volatility look-back = 25 days (simple MA) / 36 days (EWMA span)** [p.156]: Carver states performance is nearly insensitive between a few days and ~6 months; chose 25 because it matches RiskMetrics industry standard. Explicitly described as an anti-curve-fit choice ("Rather than risk over-fitting I decided on a default look-back of 25 business days") [p.156].
- **Forecast average |F| target = 10** [p.122]: arbitrary but consistent convention; all rules rescaled to it so the framework composes.
- **Forecast cap = ±20** [p.122, p.285]: "truncate beyond twice the average"; prevents single wild forecasts from dominating.
- **EWMAC slow/fast ratio = 4** [p.284]: chosen using artificial data where performance is flat between ratios 2–6; cross-checked on real data. Not individually tuned per instrument.
- **EWMAC pair set 2:8, 4:16, 8:32, 16:64, 32:128, 64:256** [p.284]: justified by correlation 0.90 between adjacent pairs; intermediate pairs exceed the 0.95 cutoff so add no value.
- **Carry forecast scalar = 30** [p.288]: derived from large multi-asset dataset via the "scale to avg |F|=10" calibration, not from performance fitting.
- **Correlation floor at 0.95 for pruning variations** [p.122, p.284]: anything above that is redundant; Carver picks this level conservatively.
- **Correlation floor at 0 for diversification multiplier** [p.297]: safety against inflation; economically justified — we refuse to bank negative-correlation diversification that may reverse.
- **Subsystem-return correlation ≈ 0.70 × instrument-return correlation** [p.168, p.294]: empirical rule-of-thumb for dynamic systems; asset allocators use 1.0.
- **Half-Kelly coefficient 0.5** [p.146-147]: economically justified — full Kelly has 10% chance of losing half capital over 10 years even with correct SR estimate [p.142, table 23].
- **Realistic SR scaling 0.75 × backtest (for out-of-sample bootstrap)** [p.146]: shrinkage factor to reflect that live returns underperform backtest.
- **Max percentage vol target 50%** [p.148]: absolute ceiling; Carver runs his own system at 25% [p.163 footnote].
- **Max SR assumptions: 1.0 staunch / 0.5 semi-auto / 0.4 asset allocator** [p.47, p.259-260]: empirically floor ceilings from institutional CTA data, used to cap Half-Kelly calculation.
- **Turnover budget: costs ≤ ⅓ of pessimistic SR** [p.260]: explicit speed-limit heuristic that determines which variations survive per instrument.

## 8. Citações Literais Importantes

> "In every case the accuracy of experts was matched or exceeded by a simple algorithm... Why are experts inferior to algorithms? One reason... is that experts try to be clever, think outside the box, and consider complex combinations of features in making their predictions. Complexity may work in the odd case but more often than not it reduces validity." — Daniel Kahneman, cited at front of book [p.6]

> "Humans are better than computers at complex intellectual tasks. But as these two stories show, our emotions prevent us from fully utilising this intelligence. The solution is to use systems to make trading decisions." — [p.20]

> "A systematic trader should be humble, and underestimate their intelligence, skill and luck. Assume your trading will go badly, be prepared for that eventuality, and be pleasantly surprised if it doesn't." — [p.259]

> "Do not trust back-tests, even if you haven't over-fitted them, and even if they've been done on a rolling out of sample basis. The future is unlikely to be quite as good as the past." — [p.259]

> "The best systematic traders will be diligent when creating their systems, but lazy when running them. Put the hard work into designing a safe system that you are comfortable with and then do not change it. Make a commitment: don't be tempted to meddle, improve or risk manage. These time-consuming activities usually destroy performance." — [p.260]

> "If you are out to describe the truth, leave elegance to the tailor." — Einstein, quoted in p.70 (ch.4 on why Markowitz produces ugly portfolios)

## 9. Conexões com Outros Livros Desta Base

N/A — Primeiro livro processado neste knowledge base; cross-refs serão adicionadas em passes subsequentes. Possíveis conexões esperadas (a validar):

- Kelly criterion and fractional Kelly — likely treated in *Fortune's Formula* (Poundstone), which Carver cites at p.143 footnote 105.
- Bootstrapping and out-of-sample validation — likely overlaps with *Advances in Financial Machine Learning* (López de Prado) when that book is processed.
- Trading rule inventory (momentum, MA crossovers) — likely overlaps with *Trading Systems and Methods* (Kaufman), which Carver cites as the canonical catalogue at p.117.
- Behavioural finance premises (prospect theory, narrative fallacy) — overlap with Kahneman *Thinking, Fast and Slow* and Shefrin *Beyond Greed and Fear* (both cited by Carver [p.13]).

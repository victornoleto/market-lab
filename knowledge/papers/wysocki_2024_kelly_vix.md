# Sizing the Risk: Kelly, VIX, and Hybrid Approaches in Put-Writing on Index Options

## Metadata

- **Author:** Maciej Wysocki (University of Warsaw, Department of Quantitative Finance and Machine Learning)
- **Year:** 2024 (arXiv preprint 2508.16598v1)
- **Venue:** arXiv preprint (not yet peer-reviewed)
- **Source URL (primary):** https://arxiv.org/abs/2508.16598
- **Alt URL (HTML):** https://arxiv.org/html/2508.16598v1
- **Slug:** `paper.wysocki_2024_kelly_vix`
- **Topic:** T4 — Kelly / confidence-weighted position sizing
- **Raw access:** N/A — no local raw; extraction based on abstract + WebFetch
- **Citation format:** `[paper.wysocki_2024_kelly_vix, §hybrid_sizing]`

## Core thesis

Three position-sizing frameworks compared for systematic put-writing on SPX options: **pure Kelly**, **VIX-Rank scaling**, and **Kelly-VIX hybrid**. Hybrid delivers best balance of return and drawdown; pure Kelly produces higher returns but substantially worse drawdowns; VIX-Rank best at highest absolute returns but with material MDD.

## Methodology snapshot

- **Asset:** S&P 500 Index options (SPXW)
- **Period:** in-sample 2018–2023; out-of-sample 2024
- **Parameter grid:** DTE ∈ {0,1,3,5}; moneyness ∈ {0%, 2%, 5%, 10% OTM}; vol estimators (HV, Garman-Klass, Yang-Zhang); memory horizons 3–252 days
- **Evaluation:** **Probabilistic Sharpe Ratio (PSR)** test — statistical significance vs buy-hold at 1% level confirmed for best configs
- **Cost model:** sensitivity to assumed bid-ask and commissions acknowledged as limitation

## Key results

| Sizing Method | DTE | %OTM | Return | Vol | Max DD | IR |
|---|---|---|---|---|---|---|
| Kelly | 1 | 5% | 14.35–17.24% | 8.44–8.47% | **0.07%** | 1.70–2.03 |
| VIX-Rank | 5 | 0% | **52.77%** | 21.59% | 9.91% | **2.44** |
| Kelly-VIX | 5 | 0% | 22.11–23.13% | 17.98–18.46% | 9.46–10.74% | 1.23–1.25 |

- Garman-Klass and Yang-Zhang volatility estimators outperform basic historical volatility
- **VIX9D-based strategies beat VIX30D-based** across most configurations
- Kelly-VIX hybrid most balanced across regimes; pure Kelly reckless without moneyness constraint

## Applicability to ai-trade

- **MEDIUM–HIGH relevance.** The **sizing framework is transferable** to any Pepperstone-served directional lead (SPX500 CFD, XAUUSD, BTC). Pepperstone does not offer SPX options for non-UK retail, so put-writing itself is out of scope.
- **Empirical Kelly formula** citable here: `f_empirical = f_kelly × (1 − CV_edge)` where CV_edge is the coefficient of variation of the edge estimate from bootstrap.
- **Phase 3.7-3 hypothesis H4 (confidence-weighted sizing meta-layer)** draws its primary citation from this paper.

## Related knowledge-base entries

- `books/math_money_mgmt.md` (Vince) — canonical Kelly / optimal-f reference (`paper.wysocki_2024_kelly_vix` operationalizes fractional-Kelly discipline).
- `books/leverage_space.md` (Vince) — multi-asset extension.
- `paper.carta_2020_kelly_practical` — academic companion on Kelly rebalancing frequency.
- `paper.downey_2023_fractional_kelly` — Monte-Carlo rationale for half/quarter Kelly.
- `paper.bozovic_2024_vix_managed` — VIX-scaling framework the hybrid leg extends.

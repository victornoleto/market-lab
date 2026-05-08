# Why Fractional Kelly? Simulations of Bet Size with Uncertainty and Downside Risk Mitigation

## Metadata

- **Author:** Matthew Downey
- **Year:** 2023
- **Venue:** Technical blog post (not peer-reviewed; rigorous numerical simulation)
- **Source URL (primary):** https://matthewdowney.github.io/uncertainty-kelly-criterion-optimal-bet-size.html
- **Slug:** `paper.downey_2023_fractional_kelly`
- **Topic:** T4 — Fractional Kelly rationale (half / quarter Kelly)
- **Raw access:** N/A — no local raw; extraction based on blog-post content
- **Citation format:** `[paper.downey_2023_fractional_kelly, §simulation]`

## Core thesis

Under **uncertainty in edge estimates**, the growth-rate-maximizing bet size shrinks sharply. Simulation: for a 70/30 bet with even payoffs, optimizing the **10th-percentile terminal return** (downside-aware) lowers optimal bet from **0.40 → 0.28**. **Half-Kelly captures ~75% of full-Kelly growth with ~50% less drawdown** — a standard operating point for professional quant operations (Renaissance, professional sports bettors).

## Methodology snapshot

- **Framework:** Monte-Carlo simulation with explicit code (public)
- **Bet specification:** discrete probability / payoff pair with parametrized edge uncertainty
- **Objective functions:** median terminal wealth, 10th-percentile terminal wealth, drawdown
- **Not peer-reviewed** but calculations are fully reproducible from the blog's source

## Key results

- **Half-Kelly → ~75% of Kelly growth, ~50% smaller drawdown**
- Quarter-Kelly: ~56% of Kelly growth, much smaller drawdown
- Full Kelly: X% probability of drawdown to X% of starting bankroll (Kelly's drawdown property)
- Uncertainty in edge estimate materially lowers the optimal fraction

## Applicability to ai-trade

- **HIGH relevance as rationale.** This is the clearest quantification of why ai-trade mandate §3.3 requires **Kelly / 2 cross-check** on every leverage sweep.
- Full Kelly without shrinkage is **reject-on-sight** (SKILL.md §Inviolable Rules rule 6).
- Half-Kelly is the **upper-bound operating point** consistent with retail prob-of-ruin ≤ 5% targets.

## Related knowledge-base entries

- `books/math_money_mgmt.md` (Vince) — classical Kelly / optimal-f.
- `books/leverage_space.md` (Vince) — multi-asset drawdown math.
- `paper.wysocki_2024_kelly_vix` — modern half-Kelly × VIX hybrid.
- `paper.carta_2020_kelly_practical` — academic empirical complement.

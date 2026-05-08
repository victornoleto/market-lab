# Does Overnight News Explain Overnight Returns?

## Metadata

- **Authors:** Paul Glasserman, Kriste Krstovski, Paul Laliberte, Harry Mamaysky (Columbia Business School)
- **Year:** 2024 (arXiv preprint 2507.04481v1)
- **Venue:** arXiv preprint
- **Source URL (primary):** https://arxiv.org/abs/2507.04481
- **Alt URL (HTML):** https://arxiv.org/html/2507.04481v1
- **Slug:** `paper.glasserman_2024_overnight_news`
- **Topic:** T9 — Overnight anomaly (news-based explanation)
- **Raw access:** N/A — extraction based on abstract + WebFetch
- **Citation format:** `[paper.glasserman_2024_overnight_news, §trading_viability]`

## Core thesis

The documented **overnight return premium in US equities is substantially explained by differences in news-topic prevalence** between overnight and intraday periods (Branching LDA topic modeling on 2.4M articles). The authors forecast overnight outperformers — but **conclude the effect is NOT a viable trading strategy** due to required turnover.

## Methodology snapshot

- **Assets:** 887 S&P 500 firms (rolling index membership)
- **Period:** 1996–2022 (portfolio testing 2001–2022)
- **Data:** 2.4M Thomson Reuters news articles + CRSP daily OHLC + firm characteristics
- **Approach:** Branching Latent Dirichlet Allocation (supervised topic modeling); rolling 4-year regressions; lasso-selected topics
- **Cost model:** turnover costs dominate — explicit acknowledgment
- **OOS:** rolling-window out-of-sample via expanding estimation

## Key results

- Top-25 predicted overnight winners **outperform significantly** gross of costs
- Removing those stocks **eliminates the overnight-intraday premium** in residual portfolio (causal attribution via topic modeling)
- **Explicit author statement:** "Because of the extreme turnover required to trade the over-intra effect, our findings fall short of being a viable trading strategy."
- Useful only for institutional market timing / inventory positioning — NOT retail

## Applicability to market-lab

- **ZERO relevance as a standalone trading strategy.** Authors explicitly disclaim viability at retail scale.
- **Indirect value:** confirms the overnight anomaly is information-driven (not structural), supporting the Alpha Architect 2021 conclusion that net-of-cost overnight strategies do not work for retail CFD.
- Can be cited as **null-finding reinforcement** for Phase 3.6 interpretation.

## Related knowledge-base entries

- `paper.alphaarchitect_2021_overnight_costs` — practitioner empirical companion.
- `paper.zirk_sadowski_2025_intraday_overnight` — horizon-dependent intraday anomaly evidence.

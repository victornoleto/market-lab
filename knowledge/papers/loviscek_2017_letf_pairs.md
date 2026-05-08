# Investment Performance of Shorted Leveraged ETF Pairs

## Metadata

- **Authors:** Loviscek / Jordan (Applied Economics attribution; full list paywalled)
- **Year:** 2017
- **Venue:** Applied Economics, v49, n44 (Taylor & Francis, peer-reviewed)
- **Source URL (primary):** https://www.tandfonline.com/doi/abs/10.1080/00036846.2017.1282149
- **Alt URL (EFMA):** https://www.efmaefm.org/0efmameetings/efma%20annual%20meetings/2013-Reading/papers/EFMA2013_0539_fullpaper.pdf
- **Slug:** `paper.loviscek_2017_letf_pairs`
- **Topic:** T7 — LETF pair trading / decay capture via shorting
- **Raw access:** N/A — abstract only; alt PDF link binary-compressed during sprint
- **Citation format:** `[paper.loviscek_2017_letf_pairs, §abstract]`

## Core thesis

Simultaneously **shorting** a bull LETF (e.g. UPRO) and its inverse pair (SPXU) captures the volatility decay of both. Monte-Carlo simulation of 48 years suggests non-trivial returns with positive skewness — **but margin requirements dominate the implementation economics**.

## Methodology snapshot

- **Strategy:** short UPRO + short SPXU + long T-bill (combined triple pair + cash)
- **Simulation:** 48-year daily-returns Monte Carlo, preserving tracking-error first-order autocorrelations
- **Margin assumption:** **FINRA 90% maintenance margin** — dominates effective capital efficiency
- **Period:** synthetic, spans multi-decade
- **Cost model:** margin + simplified borrow; not CFD-representative

## Key results

- Non-trivial returns + positive asymmetry over 48-year simulation
- **Constraint:** 90% margin maintenance hugely reduces capital efficiency vs alternative equity strategies
- Specific Sharpe/CAGR/MDD not extracted during sprint

## Applicability to market-lab

- **VERY LOW relevance.** **Pepperstone Razor retail does NOT offer UltraPro Bear (SPXU) or equivalent inverse LETFs as CFDs.** Short-selling CFDs also has financing costs distinct from FINRA margin math.
- **Do NOT dedicate Phase 3.7-3 tokens to this thesis** (H9 excluded from shortlist).
- **Re-emergence condition:** if market-lab ever adds a broker with access to SPXU/SQQQ (Inter with suitability override, IBKR BR), this paper becomes a primary reference.

## Related knowledge-base entries

- `books/leverage_for_the_long_run.md` (Gayed) — long-only LETF rotation baseline (preferred path for market-lab current mandate).
- `paper.lin_2025_letf_arbitrage` — modern 2025 extension with US-vs-Japan asymmetry insight.

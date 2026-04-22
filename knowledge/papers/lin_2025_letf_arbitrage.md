# Volatility Decay and Arbitrage in Leveraged ETFs: Evidence from the US and Japan

## Metadata

- **Authors:** Cheng-To Lin, Shih-Kuei Lin, George Yungchih Wang, Zong-Wei Yeh
- **Year:** 2025 (published August 30, 2025)
- **Venue:** SSRN working paper (abstract_id=5421274)
- **Source URL (primary):** https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5421274
- **Alt references:** https://www.math.nthu.edu.tw/~twsiam2025/agenda/S3/1.Shih-KueiLin.pdf (conference slides)
- **Slug:** `paper.lin_2025_letf_arbitrage`
- **Topic:** T1 — LETF vol-decay arbitrage (cross-market)
- **Raw access:** N/A — no local raw; extraction based on abstract + secondary review
- **Citation format:** `[paper.lin_2025_letf_arbitrage, §abstract]`

## Core thesis

The "volatility decay" in LETFs is a real phenomenon BUT the **cross-market asymmetry** between US and Japan is driven by the **non-compounding effect** (friction tied to replication technology — swaps in US, futures in Japan), not by volatility decay alone. The optimal decay-harvesting strategy is **asymmetric**: short bull LETFs in the US but bear LETFs in Japan.

## Methodology snapshot

- **Assets tested:** US bull/bear LETFs + Japanese LETFs (paired by underlying index)
- **Strategy:** beta-neutral pairwise arbitrage (short LETF + long underlying hedge)
- **Cost model:** includes borrow cost + FINRA margin assumptions (short LETFs require heavy collateral)
- **OOS:** not explicitly described in public abstract

## Key results

- **Sharpe ratio as high as 2.12** on beta-neutral shorting US bull LETFs
- **Bear-side strategy (theoretically superior per decay math) is largely unprofitable** in practice due to replication friction
- Strategy generates highly positive skewness, offers strong downside protection
- Asymmetric US-bull vs JP-bear emerges as the optimal decay-harvesting structure

## Applicability to ai-trade

- **LOW relevance for Pepperstone mandate.** Pepperstone Razor does NOT list SPXU (UltraPro Bear) nor Japanese LETFs as CFDs. Short-selling LETFs on CFD platform also has financing costs distinct from FINRA margin.
- **Indirect value:** confirms that LETF-related edge is often in DECAY CAPTURE, not directional leverage — useful framing for future instrument expansion.
- **Do NOT dedicate Phase 3.7-3 tokens to this tese** (H9 excluded).

## Related knowledge-base entries

- `paper.hsieh_2025_letf_compounding` — regime-based companion framing in parallel 2025 literature.
- `books/leverage_for_the_long_run.md` — Gayed baseline (long-only LETF rotation).

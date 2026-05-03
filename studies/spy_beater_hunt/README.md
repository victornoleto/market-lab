# spy_beater_hunt

**Status**: **CLOSED 2026-04-30** após 30 iters / ~85 cumulative trials. **2026-05-01: 5 community-feedback iterations (040-044) added** após Reddit Post 1 publication (r/LETFs):
- Iter 040 — Monthly rebal + ERs validation (perky_python)
- Iter 041 — TQQQ regime-gate test, 6 variants, none beat B4 (Fun-Sundae4060 + no_simpsons)
- Iter 042 — International stack test, US-bias only ~4% of edge (Grouchy_Release_2321)
- Iter 043 — Walk-forward weight drift gate G8 PASS (laurenthu)
- Iter 044 — Re-baseline iter 038's 14 configs com Monthly + ERs + terminal DARF (user feedback methodology consistency)

**B4 Conservative (25 NTSX / 25 GDE / 25 RSST / 25 ZROZ) confirmed as canonical deploy candidate**: net CAGR 12.84% / MDD -28.94% / Sharpe 0.745. Replaces T1 from Post 1 (T1 Sharpe dropped to 0.688 with Monthly + ERs). Veredito canonical em `TOP_STRATEGIES.md` seção "CANONICAL DEPLOY RANKING".

**Update 2026-05-02 — iter 045 RSST proxy corrected:** a validação live-vs-proxy do RSST real mostrou que `SPY + 70% DBMF + 30% KMLM - cash` replica melhor o ETF real do que `SPY + KMLM - cash`. O iter 045 re-rodou os 14 configs do iter 044 em janela comum 2000-01-03 -> 2026-05-01 com esse proxy corrigido e financiamento `CASHX?E=-2`. Para cenários static buy-and-hold/lazy-rebal, **não aplicamos DARF**; imposto fica reservado para estratégias swing/táticas que realizam ganho via trocas de posição. Resultado: **B4 ZROZ fica #2 por Sharpe** (CAGR 11.00% / MDD -29.60% / Sharpe 0.671), atrás de L1 CEGB (Sharpe 0.696, CAGR 9.66%). B4 continua sendo o melhor compromisso entre CAGR e MDD entre os stacks com RSST, mas a tabela de deploy deve usar `iterations/045-.../SUMMARY.md` para a leitura metodologicamente corrigida. Rationale: RSST é return stacking de equity + managed futures `[risk_parity, ch.5, p.10]`, e managed futures são melhor tratados como sleeve diversificada de trend/carry do que como um único índice KMLM `[ilmanen_expected_returns, ch.19]`.

**Update 2026-05-03 — iter 046 factor/NDX follow-up:** GPT-5.5 testou follow-ups pedidos pelo usuario: B4 sem RSST leverage, tilts VBR/EFV/MTUM sobre B4, e variantes NDX deleveraged estilo no_simpsons. Resultado: nenhum bate o B4 corrigido em CAGR sem piorar drawdown. `B4_scv10_from_ntsx` e o unico mild CAGR upgrade memoravel (11.23% / -31.06% / Sharpe 0.681), mas aceita MDD pior que B4. `B4_unstacked_mf7030` vira low-stress champion (9.91% / -20.91% / Sharpe 0.749), nao CAGR winner. NDX deleveraged ainda falha por MDD -72% a -76%. Detalhes: `iterations/046-2026-05-03-factor-tilt-and-ndx-deleveraged/SUMMARY.md`.

**Update 2026-05-03 — iter 047 Bitcoin sleeve:** pequena exposicao a `BTCSIM` sobre B4 corrigido foi testada. Janela comum cai para 2010-07-19 -> 2026-05-01, favoravel ao Bitcoin. Resultado: 2.5% BTC tirado de ZROZ melhora para 17.80% CAGR / -26.97% MDD / Sharpe 1.151; 5% BTC melhora para 22.01% / -27.90% / 1.311. Estritamente, MDD piora levemente vs B4 da janela (-26.42%), mas economicamente 2.5-5% e o primeiro upgrade de CAGR realmente forte encontrado. Caveat: isto e sleeve especulativa com historia curta, nao expectativa forward. Detalhes: `iterations/047-2026-05-03-bitcoin-sleeve-b4/SUMMARY.md`.

**Update 2026-05-03 — iters 048-051 overlays:** overlays restritos sobre B4 foram testados com DARF anual. Sem BTC e com janela 1987+, `overlay_sma150_12mdd_10pp` ficou em 12.35% CAGR liquido / -28.00% MDD / Sharpe 0.901 contra B4 estatico mensal 12.18% / -30.88% / 0.880. A sensibilidade SMA/EMA 126-252d foi robusta, reduzindo a suspeita de depender do 200d SMA. O iter 051 testou LETF risk-on (SSO/QLD/UPRO/TQQQ, 5-50% em passos de 5pp) e rejeitou como core: melhor LETF por Sharpe, `qld_5_sma150_from_ZROZ`, fez 12.87% / -28.92% / 0.900, abaixo do overlay sem LETF em Sharpe/MDD; melhor CAGR, `tqqq_45_sma150_from_NTSX`, fez 16.78% / -44.64% / 0.742. Detalhes: `iterations/050-2026-05-03-b4-overlay-tax-sma-ema/SUMMARY.md` e `iterations/051-2026-05-03-letf-risk-on-overlay/SUMMARY.md`.

**Mission**: Find ONE long-term portfolio strategy with **mean CAGR ≥ SPY (13.80%)** AND **mean MDD ≤ SPY (40.85%)** AND surviving the 7-gate battery (PBO/DSR/WF/Bootstrap/CrossLib) on ≥ 2/3 datasets (lh_56y / vt_real / ndx_real).

This is a **harder bar than long_term_portfolio's** — that loop's mission was Sharpe-edge anchored (CAGR was warning-only). User feedback after 43-iter sweep: "MUITO DIFÍCIL seguir uma estratégia que não vai bater o SPY em CAGR." This hunt directly addresses that.

---

## Why fork instead of extending long_term_portfolio?

1. **Different mission, different gates**: spy_beater is CAGR-anchored (bar = SPY's 13.80% mean). long_term_portfolio was Sharpe-anchored (bar = SPY + 0.05).
2. **Different design philosophy**: F1+SPLIT trades CAGR for Sharpe/MDD via stacking + crisis-alpha. This hunt explicitly seeks higher CAGR — likely via leveraged equity + regime gates (Gayed LRS family) OR tactical leveraged barbells (HFEA family).
3. **Avoid mission creep**: long_term_portfolio's BASE_MEMORY + WINNER_AND_RANKING are tuned for the prior mission. Reframing them invalidates 43 iters of cross-iter comparability.
4. **Reuse infra, not mission**: this hunt reuses `studies/long_term_portfolio/synths.py`, `run_iter.py`, `proxies.py`, `datasets.py` — but has its own scoring/winner criteria.

---

## Mission honesty calibration

**Why this might fail (be prepared)**:
- 43 prior iters with F1+SPLIT as best couldn't produce CAGR > SPY mean
- bestfolio_meta_wf_hunt parallel session investigation confirmed bestfolio's 19.8% claim is NOT replicable in our gate-screened universe (kill K3 fired iter 001)
- The 13.80% SPY mean is dragged up by 2008-2024 vt_real/ndx_real Tiingo windows (14.97% each); lh_56y SPY is only 11.47% (F1 already beats this)
- Most strategies that beat SPY long-term do so via Sharpe gain (lower vol), not CAGR uplift — fundamental risk-return tradeoff

**Why it might succeed**:
- We haven't exhaustively tested **leveraged equity + regime gate** (Gayed LRS family) — `[leverage_for_the_long_run, p.40-60, ch.3-4]` shows 200d SMA gate dramatically reduces LETF decay
- HFEA classical (3× SPY + 3× LTT) backtest beats SPY historically — but huge regime risk (2022 was catastrophic)
- Stacked equity (NTSX + GDE) at higher leverage might unlock CAGR + Sharpe simultaneously
- Concentrated growth (QQQ + leverage + regime gate) tracks growth premium directly

**The bar is exact, not approximate**. We accept "winner" only if BOTH (CAGR ≥ 13.80% AND MDD ≤ 40.85% AND gates pass). Near-miss = not a winner.

---

## Files

| file | purpose |
|---|---|
| `README.md` | this file |
| `SPEC.md` | mission spec + gate definitions + winner criteria |
| `BASE_MEMORY.md` | iteration log + frontmatter (loop state) |
| `WINNER_AND_RANKING.md` | tier rubric (CAGR/MDD-anchored); includes pre/post-tax ranking |
| **`TOP_STRATEGIES.md`** | **deploy-readiness ranking + per-gate audit + live-deploy instructions** (canonical doc post-closure 2026-04-30) |
| `INFRASTRUCTURE.md` | what to reuse from long_term_portfolio (synths.py / run_iter.py / scoring.py adaptations) |
| `tax_layer.py` | net-of-tax computation (Lei 14.754/2023, 15% DARF anual) wrapping `_shared/tax_engine.py` |
| `rerun_all_iters.sh` | re-execute every iter's backtest.py after pipeline-level changes |
| `iterations/` | one dir per iter (30 completed + 4 Reddit feedback iters 040-043 in 2026-05-01) |
| `iterations/039-2026-04-30-reddit-comparison-spy-lrs-vs-static-stack/REDDIT_POST_1_discovery.md` | Reddit Post 1 (published) — discovery format |
| `iterations/039-.../REDDIT_POST_2_technical.md` | Reddit Post 2 (drafted) — technical deep-dive with iter 040-043 findings |
| `iterations/040-2026-05-01-baseline-monthly-rebal-explicit-ers/SUMMARY.md` | Monthly rebal + ERs baseline (perky_python feedback) |
| `iterations/041-2026-05-01-g3-ndx-regime-gate-tqqq-multi-asset/SUMMARY.md` | TQQQ × 200d × multi-asset (Fun-Sundae4060 + no_simpsons feedback) |
| `iterations/042-2026-05-01-g4-international-stack-ntsi-rssb/SUMMARY.md` | NTSD/RSSB stacks (Grouchy_Release_2321 feedback) |
| `iterations/043-2026-05-01-g8-walkforward-weight-drift-gate/SUMMARY.md` | Walk-forward weight optimization vs static (laurenthu feedback) |
| `iterations/044-2026-05-01-iter038-rebaseline-monthly-ers-terminal-darf/SUMMARY.md` | **Canonical** unified 14-config ranking with Monthly + ERs + terminal DARF (replaces both iter 038 and iter 040 isolated tables) |
| `iterations/045-2026-05-02-rsst-proxy-7030-rebaseline/SUMMARY.md` | **RSST-corrected** rebaseline: same configs on common 2000+ window with `RSST = SPY + 70% DBMF + 30% KMLM - CASHX?E=-2` |
| `iterations/046-2026-05-03-factor-tilt-and-ndx-deleveraged/SUMMARY.md` | Factor tilt + no_simpsons/NDX follow-up; B4 corrected baseline retained |
| `iterations/047-2026-05-03-bitcoin-sleeve-b4/SUMMARY.md` | Small Bitcoin sleeve test on corrected B4; 2.5-5% BTC materially improves 2010+ CAGR with modest MDD penalty |
| `iterations/050-2026-05-03-b4-overlay-tax-sma-ema/SUMMARY.md` | B4 no-BTC overlay with annual DARF and SMA/EMA sensitivity; small after-tax improvement versus forced-monthly static |
| `iterations/051-2026-05-03-letf-risk-on-overlay/SUMMARY.md` | LETF risk-on sleeves on B4 overlay; higher CAGR variants rejected as balanced-core improvements due worse MDD/Sharpe |

> **RSST proxy note:** iter 038/040/044 expandiram `RSST` como `SPYSIM + KMLMSIM - CASHX`. O iter 045 substitui isso por `SPYSIM + 70% DBMFSIM + 30% KMLMSIM - CASHX?E=-2`; use o iter 045 para leitura corrigida do RSST, e o iter 044 apenas como histórico de janela longa pré-correção.

---

## Pre/post tax reporting (2026-04-30)

Each iter's `verdict.json` reports BOTH gross (`total_score`) and net (`net_total_score`). Tax model: Lei 14.754/2023 vigente jan/2024 — DARF 15% anual, apuração única na DAA, perdas compensam dentro do ano, carry-forward indefinido. Implementation in `tax_layer.py`; per-strategy classification (`static`=buy_hold defer-to-end vs `lrs`/`vol_target`/`blend`=annual-realize). FX modeled flat (caveat documented).

Observed drag (gross_cagr − net_cagr): **0.59-0.74 pp** for buy-hold static; **1.63-2.35 pp** for swing strategies. The structural ~1.5pp spread re-shuffles ranking — see `WINNER_AND_RANKING.md` for the consolidated table.

---

## Citations

- `[leverage_for_the_long_run, ch.3-4, p.40-60]` Gayed — 200d SMA gate on leveraged equity
- `[risk_parity, ch.5, p.10]` Carlson — capital-efficient stacking baseline
- `[advances_fin_ml, p.208-211]` PBO via CSCV
- `[advances_fin_ml, p.222-223]` DSR
- `[advances_fin_ml, p.196-202]` bootstrap CI
- HFEA classical (Hedgefundie's Excellent Adventure, Bogleheads forum 2019)

---

## Mandate context

This hunt operates under mandate §1 MAINTENANCE MODE (2026-04-23). Any winner candidate goes through mandate §7 override request, same as F1+SPLIT.

The current default position remains **F1+SPLIT** if this hunt fails to find a strategy that satisfies both bars. F1+SPLIT is empirically validated and deploy-ready; spy_beater_hunt seeks improvement, not replacement of the safety net.

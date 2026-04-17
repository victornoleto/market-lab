# Citation Audit — 2026-04-16 post-winners cleanup

> **Generated:** 2026-04-16, durante `specs/post-winners-cleanup.md` §7.
>
> **Método:** grep agregado em `src/`, `tests/`, `scripts/`, `jornada/`,
> `knowledge/`, `ROADMAP.md`, `CLAUDE.md`, `docs/investment-mandate.md`,
> `docs/reference/` por padrão `[<slug>(,|])`. Cruzado com
> `books/MAPPING.md` (34 books absorvidos).
>
> **Critério de archive:** slug NÃO encontrado em nenhum citation real
> + NÃO está na lista §7.3 PROTECTED do spec.

---

## Resumo

| Status | Count | Notas |
|---|---|---|
| **USED** | 16 | Citados em código/specs/jornadas ativos |
| **ARCHIVED** | 18 | Movidos para `books/summaries/_archive/` |
| **PROTECTED** | 4 | Subconjunto de USED — mandate refs invioláveis |
| **TOTAL** | 34 | books/MAPPING.md inventory |

PROTECTED slugs (todos já em USED):
- `leverage_for_the_long_run` — referenciado pelo mandate §4 (Strategy B base)
- `math_money_mgmt` — referenciado pelo mandate §3.3 (Kelly f/2)
- `leverage_space` — referenciado pelo mandate §3.3 (ruin/drawdown)
- `advances_fin_ml` — framework de gates (PBO/DSR/CPCV) em mandate §2

---

## USED (16 — permanecem em `books/summaries/`)

| # | Slug | Citação principal | Onde |
|---|---|---|---|
| 1 | `advances_fin_ml` | `[advances_fin_ml, p.196-202, ch.11]` PSR/DSR; `p.208-211, ch.14]` PBO; `p.215-219, ch.13]` regime decomp | mandate, scripts, jornadas |
| 2 | `algo_trading_chan` | `[algo_trading_chan, p.28-30, ch.2]` mean-reversion; `p.88-89, ch.4]` warning ETFs | docs, jornadas (Chan archived) |
| 3 | `cycle_analytics` | `[cycle_analytics]` ehlers cycle indicators | knowledge skill |
| 4 | `evidence_based_ta` | `[evidence_based_ta]` MCPT methodology | knowledge skill |
| 5 | `leverage_for_the_long_run` ⭐ | `[leverage_for_the_long_run, p.7]` LETF intro; `p.13/p.17/p.21]` SPY-SMA signal | mandate §4, Phase 3 lead B1 |
| 6 | `leverage_space` ⭐ | `[leverage_space, Vince]` ruin theory | mandate §3.3, Phase 3 lead A1 |
| 7 | `machine_trading` | `[machine_trading, p.126-127, ch.4]` EWMA-GARCH; `p.204-205, ch.7]` Bollinger MR | bollinger_mr.py, jornadas |
| 8 | `math_money_mgmt` ⭐ | `[math_money_mgmt, Vince]` Kelly f/2 | mandate §3.3, Phase 3 lead A1 |
| 9 | `ml_for_algo_trading` | `[ml_for_algo_trading]` ML deployment | knowledge skill |
| 10 | `quant_trading_chan` | `[quant_trading_chan]` retail quant framework | docs, knowledge skill |
| 11 | `rocket_science` | `[rocket_science]` ehlers cycle/DSP | knowledge skill |
| 12 | `stocks_on_the_move` | `[stocks_on_the_move, p.81/66/95]` ETFRotation canonical params | etf_rotation.py, helpers/momentum.py |
| 13 | `systematic_trading` | `[systematic_trading]` parsimony, position sizing | knowledge skill, jornada vol-expansion |
| 14 | `testing_tuning` | `[testing_tuning]` walk-forward methodology | mandate §2 |
| 15 | `trading_systems_methods` | `[trading_systems_methods, p.353]` Donchian breakout | jornada vol-expansion |
| 16 | `volatility_trading` | `[volatility_trading, p.22-23, p.58-60]` YZ vol cone | jornada vol-expansion |

---

## ARCHIVED (18 — movidos para `books/summaries/_archive/`)

PDFs em `books/raw/<slug>.pdf` permanecem (preservation §2 do spec).
Re-promoção é só `git mv` de volta + atualizar este arquivo + rerun
`scripts/build_skill.py`.

| # | Slug | Razão de archive |
|---|---|---|
| 1 | `adaptive_markets` | Lo (2017) — Adaptive Markets Hypothesis. Não citado em nenhuma decisão técnica do código atual. |
| 2 | `big_data_ml_quant` | Guida ed. (2019) — alt-data/NLP. Fora do escopo Phase 3. |
| 3 | `cybernetic_analysis` | Ehlers (2004) — DSP indicators. Strategy Ehlers descartada. |
| 4 | `cybernetic_trading` | Ruggiero (1997) — DSP/cybernetic. Strategy Ehlers descartada. |
| 5 | `data_driven_science` | Brunton+Kutz (2021) — métodos numéricos avançados. Não citado. |
| 6 | `eval_opt_strategies` | Pardo (2008) — WFA reference. Suplantado por `testing_tuning` (Masters 2018) na prática. |
| 7 | `fin_time_series_tsay` | Tsay (2010) — econometria/GARCH. EWMA-GARCH usado é via `machine_trading`. |
| 8 | `ml_for_asset_managers` | López de Prado (2020) — ML asset managers. Framework de gates já vem do `advances_fin_ml`. |
| 9 | `numerical_recipes` | Press et al. (1992) — receitas numéricas C. Não citado. |
| 10 | `regime_change` | Chen+Tsang (2020) — regime detection. Não citado em código atual. |
| 11 | `risk_parity` | Qian (2016) — portfolio construction. Phase 3 lead B2 pode revisitar (blend). |
| 12 | `sentiment_analysis_handbook` | Mitra+Yu (2016) — sentiment analysis. Fora do escopo Phase 3. |
| 13 | `stat_sound_indicators` | Aronson+Masters (2013) — TSSB. Suplantado por `testing_tuning`. |
| 14 | `tech_analysis_patterns` | Tsinaslanidis (2016) — TA patterns. Não citado. |
| 15 | `time_series_hamilton` | Hamilton (1994) — time series classic. Markov-switching não usado. |
| 16 | `trading_evolved` | Clenow (2019) — Python trading book. Strategy Clenow descartada. |
| 17 | `trading_exchanges` | Harris (2003) — market microstructure. Phase 3 lead A2 (multi-asset screener) pode revisitar. |
| 18 | `universal_trend_tactics` | Penfold (2020) — trend trading. Não citado em código atual. |

---

## Notas operacionais

1. **`masters_permutation_tests`** é mencionado em alguns specs/jornadas
   como slug-like reference, mas NÃO existe como book em
   `books/MAPPING.md`. Provavelmente é um placeholder/typo de
   `testing_tuning` (Masters 2018) ou `stat_sound_indicators` (Aronson +
   Masters 2013, livro do TSSB). Não conta como book USED.

2. **Re-promoção:** se um lead Phase 3 começar a citar um slug
   archived, o fluxo é:
   ```
   git mv books/summaries/_archive/<slug>.md books/summaries/
   ```
   atualizar este audit + rerun `scripts/build_skill.py`.

3. **PDFs raw** em `books/raw/<slug>.pdf` e extrações em
   `books/extracted/<slug>/` (gitignored) **nunca foram tocados**.
   A archive afeta apenas o resumo absorvido.

4. **`knowledge/SKILL.md`** regenerado pós-archive; o header reflete
   "16 slugs USED + 18 archived (recover via git mv)".

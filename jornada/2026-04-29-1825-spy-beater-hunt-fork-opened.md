# spy_beater_hunt — Vertente nova aberta

Após long_term_portfolio sweep concluir 2026-04-29 com **F1+SPLIT** (mean CAGR 10.76% vs SPY mean 13.80%, gap 3pp), usuário levantou critério psicológico/comportamental: **"MUITO DIFÍCIL seguir uma estratégia que não vai bater o SPY em CAGR"**.

Abrindo nova vertente `studies/spy_beater_hunt/` com mission redefinido: **encontrar UMA estratégia com CAGR ≥ SPY (13.80%) AND MDD ≤ SPY (40.85%) AND survivendo 7-gate battery em ≥ 2/3 datasets**.

## Por que fork (não extensão)?

- **Mission diferente**: long_term_portfolio era Sharpe-edge anchored. spy_beater é CAGR-anchored.
- **Filosofia de design diferente**: F1+SPLIT troca CAGR por Sharpe/MDD via stacking. spy_beater explicitamente busca CAGR uplift via leverage + regime gate.
- **Cross-iter compatibility**: reframing as 43 iters de long_term_portfolio invalidaria o ranking. Fork preserva.
- **Reuse infra, não mission**: synths.py/run_iter.py/proxies.py/datasets.py são reutilizados; scoring.py é novo (CAGR-anchored).

## Foundation criada

`studies/spy_beater_hunt/`:
- `README.md` — mission overview + reuso strategy
- `SPEC.md` — bar conditions + gates + methodology
- `BASE_MEMORY.md` — frontmatter + iteration log placeholder
- `WINNER_AND_RANKING.md` — tier rubric (CAGR-anchored, distinct from long_term_portfolio)
- `INFRASTRUCTURE.md` — reuse strategy + new modules required (TMF synth, LRS engine, stress tests, scoring)
- `PROMISING_DIRECTIONS.md` — ranked hypotheses (Tier 1: Gayed LRS A1/A2 + HFEA B1)

## Tier 1 hipóteses (literatura-strong, deployable)

- **A1 Gayed LRS UPRO**: 100% UPRO when SPY > 200d MA, else IEF. `[leverage_for_the_long_run, ch.3-4, p.40-60]`. Expected CAGR 16-22%, MDD 25-40%.
- **A2 Gayed LRS TQQQ**: 100% TQQQ when QQQ > 200d MA, else IEF. Expected CAGR 20-30%, MDD 35-50%.
- **B1 HFEA classical**: 55% UPRO + 45% TMF (3× SPY + 3× LTT) quarterly rebalanced. Bogleheads 2019. Expected CAGR 18-25%, MDD 30-50% (2022 era 70%).

## Calibração honesta

**Possíveis razões para falhar:**
- 43 iters de long_term_portfolio com F1+SPLIT como melhor — nenhuma produziu CAGR > SPY mean
- bestfolio_meta_wf_hunt (sessão paralela) confirmou que 19.8% CAGR claim do bestfolio.app NÃO é replicável em universe gate-screened
- 13.80% SPY mean é dragged up por 2008-2024 (recent US bull); lh_56y SPY é só 11.47% (F1 já bate)

**Possíveis razões para suceder:**
- Não testamos exhaustivamente leveraged equity + regime gate (Gayed LRS)
- HFEA classical bate SPY pre-2022 historically (mas 2022 catastrophic)
- Stacked equity heavy (NTSX + UPRO + AVUV) inexplorado

**O bar é exato**: WINNER apenas se ALL 3 bars + score ≥ 90.

## Plano executivo (next session)

Iter 001 (A1 Gayed LRS UPRO) → 002 (B1 HFEA) → 003 (A2 Gayed TQQQ) → 004 (A3 Mixed) → 005 (B2 HFEA+KMLM) → 006 (C1 Vol-target). Depois decisão: WINNER ou CLOSE.

Se 0/6 → fechar hunt, F1+SPLIT confirmado deploy. Se ≥1 → declarar winner, sensitivity analysis.

## Fallback: F1+SPLIT permanece

Se spy_beater_hunt falhar, **F1+SPLIT é o deploy candidate**. A falha em encontrar algo melhor é knowledge negativo valioso — confirma F1+SPLIT como local optimum.

## Citações

- `[leverage_for_the_long_run, ch.3-4, p.40-60]` Gayed
- `[risk_parity, ch.5]` Carlson (incumbent baseline)
- `[advances_fin_ml]` PBO/DSR/WF/Bootstrap
- HFEA Bogleheads 2019
- `[ilmanen_expected_returns, ch.19]` MF crisis-alpha

---

**Status**: bootstrapped. Aguardando próxima sessão para iter 001.

# spy_beater_hunt iter 040-044 — feedback do Reddit Post 1 + methodology consistency

**Data:** 2026-05-01
**Contexto:** publiquei o Reddit Post 1 (r/LETFs, comparando 4 stacks vs SPY/SSO/UPRO/LRS/popular 50/25/25), recebi 11 comentários técnicos. Skill `reddit-post-review` extraiu 7 claims verificáveis e identificou 4 comentários com valor para o estudo.

## Resumo dos 4 ajustes

### Iter 040 — Baseline ajustada (Monthly + ERs reais)
**Trigger:** u/perky_python.

Re-rodei os 9 portfolios do Post 1 com:
- Top-level rebal **Monthly** (era Yearly) — nosso, não da WisdomTree.
- ERs explícitos via `drag` no testfol.io (NTSX 0.20%, GDE 0.20%, RSST 0.99%, KMLM 0.92%, GLD 0.40%, ZROZ 0.15%, etc.).

**Headline finding inesperado:** **Popular 50/25/25 SSO/GLD/ZROZ tem MDD pior em 10.71pp** (-39.84% → -50.55%) com Monthly rebal. Em bear markets, SSO 2× cai dobro do SPY e Monthly força recomprar SSO mensalmente, acelerando a sangria. Yearly rebal naturalmente "deixa SSO morrer" durante o ano. **Stacks NTSX/GDE/RSST quase imunes** (ΔMDD < 0.5pp em B4/B2). Sharpe baseline B4 cai de 0.798 → 0.745 (ranking preservado).

### Iter 041 — G3 NDX regime-gate (TQQQ × multi-asset × 200d SMA)
**Trigger:** u/Fun-Sundae4060 + u/no_simpsons.

5 variantes testadas (TQQQ emulado via QQQSIM?L=3&E=0.84; CTASIM não existe → KMLM apenas).

**Resultado:** **nenhuma G3 bate B4.** Best G3 = G3c (with bonds, 25/25/25/25 TQQQ/KMLM/GLD/IEF) com Sharpe **0.703 vs B4 0.745** (-0.042). G3a Fun-Sundae spec lança em 15.60% / -58.53% / 0.661 (MDD pior que SPY). **G3e Gayed-NDX (100% TQQQ → 100% IEF) tem MDD -90.05%** — TQQQ 3× decai catastroficamente em 2000-2002 mesmo com SMA gate. O folk-wisdom "10,000% em 2012-2025" foi cherry-picked sobre window sem dotcom. KILL fired: TQQQ regime-gate não generaliza pra 1987-2026.

### Iter 042 — G4 international stack (NTSI/RSSB/NTSD)
**Trigger:** u/Grouchy_Release_2321 + u/perky_python.

5 variantes testadas. NTSDSIM e RSSBSIM disponíveis em testfol.io.

**Findings:**
- **US-bias custa apenas ~4% do Sharpe edge.** Best G4 (G4c — 12.5 NTSX / 12.5 NTSD / 25 GDE / 25 RSST / 25 ZROZ) tem Sharpe 0.716 vs B4 0.745. Diferença pequena → diversificação estrutural via stacking é o driver dominante, não US-equity selection.
- **G4d (25 RSSB / 25 GDE / 25 ZROZ / 25 KMLM) quebra recorde de MDD do estudo: -22.56%.** Calmar 0.467 (também recorde). CAGR 10.54% é o trade-off (abaixo de SPY).
- **Caveat honesto:** RSSBSIM tem só ~2 anos live + 36 sintéticos. Take with skepticism.

### Iter 044 — re-baseline iter 038 com Monthly + ERs + terminal DARF (user methodology consistency)
**Trigger:** user 2026-05-01 — "iter 038 sweep ainda mostra T1 1º; faça tudo Monthly + ERs + DARF anual sobre lucro net."

Re-rodei os 14 configs do iter 038 com testfol.io (Monthly + ERs reais via `drag`). Aplicquei tax model **lazy rebal terminal DARF** (user contribuir mensalmente, NUNCA vende durante accumulation → realized gains intra-ano = 0 → DARF 15% só no terminal). Fórmula: `net_final = 0.85 × gross_final + 0.15 × initial`.

**Findings:**
- **B4 ZROZ continua winner**: gross 13.31% / net 12.84% / MDD -28.94% / Sharpe 0.745
- **9 estratégias batem SPY em net CAGR + MDD** (B4, B3, B2, T2, T1, B5, B1, M4, T3)
- **T1 net CAGR 12.87%** (era 15.82% no iter 038 com Yearly + no-ER + tax anual). Diferença = ER drag (0.36pp) + Monthly rebal effect em TMF 20% (-0.85pp) + diferentes tax timing assumptions (~1.7pp combinados)
- **L1 net CAGR 10.60%** (era 11.13%) — drag pequeno
- **B1 user baseline (25/25/25/25 NTSX/GDE/RSST/TMF)** entrega net CAGR 12.46% / MDD -38.78% — Pareto-suboptimal vs B4 (TMF 25% custa MDD)

**Caveat metodológico**: M2/M3 contêm DBMF (DBMFSIM start 2000) — janela 26y, não comparável diretamente em CAGR absoluto. Resolved via separate batch (testfol.io batches share start_date so DBMFSIM clipped batch_b inicialmente; refetch_b.py separou DBMF para batch_d com 26y window honesto).

**Doc consistency**: TOP_STRATEGIES.md, WINNER_AND_RANKING.md, README.md e Reddit Post 2 atualizados com a tabela única iter 044 (gross + net) substituindo as duas anteriores (iter 038 e iter 040 isolated). Reading guide removido — agora há methodology única consistente.

### Iter 043 — G8 walk-forward weight drift gate
**Trigger:** u/laurenthu (com link a bestfolio.app/blog/walk-forward-portfolios).

Re-fit max-Sharpe de B4/B2/T1 em rolling 5y windows (~400 windows × 3 universos), comparei portfolio walk-forward vs static.

**Findings:**
- **Drift dos pesos optimal é massivo:** 60-75pp range (sleeves vão de 0% a 100% across windows). laurenthu's "weights drift" prediction validated.
- **Mas portfolio static VENCE walk-forward em Sharpe** em todas as 3 universes: B4 ΔSharpe -0.061, B2 -0.062, T1 -0.029. WF pega +0.36-0.45pp CAGR mas paga -1.4 a -2.6pp em MDD (B4/B2).
- **Verdict G8: PASS.** Edge estrutural sobrevive ao walk-forward. Confirma DeMiguel/Garlappi/Uppal 2009 RFS — 1/N supera mean-variance em janelas curtas (5-10y) por estimation error.

## Implicações estratégicas

1. **B4 Conservative (25 NTSX / 25 GDE / 25 RSST / 25 ZROZ) sobrevive aos 4 testes adversariais.** Sharpe ajustado 0.745 (Monthly + ERs), edge não-curve-fit (G8 PASS), pequena perda com US/Intl swap (G4: -0.029 Sharpe), domina TQQQ regime-gates (G3: +0.042 Sharpe).
2. **G4d** é nova candidate para "MDD-extreme" tier (-22.56% MDD) com trade-off CAGR.
3. **Popular 50/25/25 cai mais um degrau.** Monthly rebal expõe vulnerabilidade.
4. **Folk-wisdom TQQQ regime-gate cai do panteão.** Não sobrevive a janela completa 1987-2026.

## Status

- Os 4 itens de feedback do Reddit Post 1 estão **todos endereçados** com numbers + plots.
- Próximo passo natural: **atualizar Reddit Post 2** (technical follow-up que já está em draft) com os findings.
- O usuário responderá os comentários do Post 1 manualmente usando os 4 drafts em `/var/www/pessoal/victor-ia/verticals/reddit/posts/1t0i3qm-review.md`.
- Mandate §1 (100% Plano C) UNCHANGED — research only.

## Documentos gerados

- `studies/spy_beater_hunt/iterations/040-2026-05-01-baseline-monthly-rebal-explicit-ers/SUMMARY.md`
- `studies/spy_beater_hunt/iterations/041-2026-05-01-g3-ndx-regime-gate-tqqq-multi-asset/SUMMARY.md`
- `studies/spy_beater_hunt/iterations/042-2026-05-01-g4-international-stack-ntsi-rssb/SUMMARY.md`
- `studies/spy_beater_hunt/iterations/043-2026-05-01-g8-walkforward-weight-drift-gate/SUMMARY.md`
- `studies/spy_beater_hunt/iterations/044-2026-05-01-iter038-rebaseline-monthly-ers-terminal-darf/SUMMARY.md` (canonical unified ranking)

## Citações

- DeMiguel/Garlappi/Uppal 2009 RFS — "Optimal Versus Naive Diversification" (G8 PASS rationale)
- Bhardwaj/Gorton/Rouwenhorst 2014 NBER w14424 — MF survivorship bias 7%/yr (KMLM rules-based escapa)
- Gayed/Bilello 2016 — Leverage for the Long Run (200d SMA SPX validation, NDX extension fails)
- WisdomTree NTSX FAQ + Return Stacked RSST/RSSB issuer pages (rebal cadence + ERs)
- u/perky_python, u/Fun-Sundae4060, u/no_simpsons, u/Grouchy_Release_2321, u/laurenthu (Reddit r/LETFs)

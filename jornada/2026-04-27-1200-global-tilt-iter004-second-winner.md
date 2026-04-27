# Global Factor-Tilt Loop: Iter 004 — Second WINNER

**Data**: 2026-04-27  
**Loop**: global_factor_tilt_loop  
**Iter**: 004 — `momentum-mf-sleeve`  
**Resultado**: 🏆 WINNER (90/100) — loop halted

---

O loop global de tilts fatoriais encontrou um **segundo** candidato WINNER na
iteração 004.

## O que foi testado

A estratégia do WINNER anterior (iter 002 — momentum cross-sectional global,
K=2, lookback=6 meses) com uma modificação: **adicionar uma fatia fixa de 10%
em KMLMSIM** (um ETF de managed futures — tendências em vários ativos via
futuros). O restante 90% continua alocado pelo sinal de momentum.

A ideia vem do livro *Expected Returns* de Ilmanen `[ilmanen_expected_returns, ch.19]`:
managed futures são um "almoço grátis" — retorno descorrelacionado do mercado de
ações que sobe o Sharpe do portfólio sem custar muito do retorno absoluto.

## Resultados

| Janela | Sharpe | CAGR | MDD | Gates |
|---|---|---|---|---|
| Educational (~38 anos) | 0.885 | 9.51% | 20.77% | 7/7 ✅ |
| Real VT (~17 anos) | 0.842 | 10.14% | 16.06% | 7/7 ✅ |
| Real QQQ (16 anos) | 0.943 | 10.72% | 16.06% | 7/7 ✅ |

7/7 gates nos três datasets. 100% das janelas de 5 anos com Sharpe positivo
(33/33). Critério não ativado: Sharpe na janela vt_real melhorou levemente
(0.838 → 0.842) vs a estratégia pura do iter 002.

## Por que isso é relevante

Comparando com os três benchmarks de referência do loop (janela de 38 anos):

- vs **VT buy-and-hold**: +0.375 Sharpe, +0.71pp CAGR, −29pp MDD → domina nos 3 eixos
- vs **Plano C V3_1**: +0.214 Sharpe, −1.43pp CAGR, −32pp MDD → Pareto (ganha em S+MDD, perde levemente em CAGR)
- vs **V_HYBRID+MF**: +0.142 Sharpe, −1.40pp CAGR, −24pp MDD → Pareto (idem)

A estratégia troca ~1.4pp de CAGR por uma redução de drawdown de 24pp vs o V_HYBRID+MF.
Para um portfólio de aposentadoria, drawdown máximo de 20% vs 44% faz uma diferença
enorme no comportamento emocional e no risco de sequência de retornos.

## Estado do loop

`status: winner` setado em `BASE_MEMORY.md`. O shell loop agora para. O loop
acumulou 4 iterações, 21 configurações testadas, 2 winners documentados:

- Iter 002: momentum K=2/lb=6m puro — Sharpe 0.991/0.838/0.929
- Iter 004: momentum K=2/lb=6m + KMLM 10% — Sharpe 0.885/0.842/0.943

## O que vem a seguir

**Mandate §1 continua MAINTENANCE.** Esses dois WINNER candidates são candidatos
para uma eventual deliberação de override §7, não posições live. O próximo passo
natural seria paper trading de validação (conforme spec `specs/phase_4_paper_trading.md`)
e deliberação §7 com o usuário — mas isso exige decisão explícita.

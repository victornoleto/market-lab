# bestfolio_meta_wf iter 001 — DEAD_END (kill K3, sem edge sobre F1+SPLIT)

**Data:** 2026-04-29 18:13
**Vertente:** `studies/bestfolio_meta_wf_hunt/`
**Status:** DEAD_END — kill K3 fires (turnover 177-222%/yr sem Sharpe edge)

## TL;DR

Rodei a metodologia walk-forward do bestfolio.app (lookback 36 meses, max
40% por sleeve, no shorts, embargo 21d, max-Sharpe) sobre 5 sleeves
vencedores do `long_term_portfolio` (S1 = F1+SPLIT iter 043 incumbente, S2
= TLT-static iter 023, S3 = AllWeather Browne iter 020, S4 = SPMO hybrid
iter 040, S5 = RSST heavy iter 041). **Resultado: meta-portfolio
indistinguível de F1+SPLIT em Sharpe, com 177-222%/yr de turnover.**
Nenhum edge sobre o incumbente; 0/3 datasets clear o hurdle +0.05; DSR
falha em 2/3 datasets.

## Números

| Dataset | meta Sharpe | S1 Sharpe | edge | meta MDD | S1 MDD | Δ MDD pp | turnover |
|---|---:|---:|---:|---:|---:|---:|---:|
| lh_56y | **1.137** | 1.125 | +0.012 | 17.42% | 19.91% | -2.48 | 177.2% |
| vt_real | 1.106 | 1.118 | -0.012 | 12.73% | 14.62% | -1.88 | 215.7% |
| ndx_real | 1.102 | 1.128 | -0.026 | 12.73% | 14.62% | -1.88 | 222.0% |

DSR p-values (n_trials=157 cumulative): 0.003 / 0.062 / 0.101 — só lh_56y
passa < 0.05.
Bootstrap 99.9% CI low: todas positivas (4.24% / 1.65% / 2.43%).
Walk-forward 8-fold winners: 7/8 em todos os datasets.
Weight concentration > 80% em qualquer sleeve: 0% dos meses (sem
degeneração).

Pesos médios lh_56y: S1 26.4% / S2 18.2% / S3 29.2% / S4 11.0% / S5 15.2%.

## Por que não passou

Três razões estruturais:

1. **F1+SPLIT já é quase ótimo no nosso universo.** Os 5 sleeves vieram
   do sweep do long_term_portfolio onde todos foram pré-screenados
   contra hurdle SPY-only +0.05 Sharpe. Densidade de Sharpe entre
   sleeves é muito apertada (1.10-1.14 média) pra alocação dinâmica
   achar alpha sistemático.
2. **Lookback 36 meses Sharpe-max é ruidoso.** Com sleeves cuja diferença
   real de Sharpe é da ordem de ±0.05, 36 meses de daily dão estimativa
   de Sharpe com std ≈ 0.05 — mesma ordem do gap inter-sleeves. O solver
   acaba tradeando ruído.
3. **O 19,8% Aggressive WF do bestfolio vem de sleeves leveraged + um
   universo diferente.** Reproduzir a arquitetura no nosso universo
   (mais conservador, com gates passantes) lava o edge.

## Achado positivo (mas insuficiente)

MDD do meta é **1.88-2.48pp menor** que S1 em todos os 3 datasets. WF
genuinamente reduz drawdown. Mas o trade-off é CAGR drag de -0.83 a
-0.96pp e Sharpe inalterado. Pra um investor risk-adjusted (Sharpe-based,
que é o nosso framework), zero. Pra um investor pure-MDD, marginal.

## Implicações

- **Reforça F1+SPLIT FINAL PICK do long_term_portfolio.** Static bate
  dynamic neste universo sob nossos gates. F1+SPLIT continua único
  deploy-ready candidate; este iter não muda isso.
- **Refuta a hipótese meta-WF para a variante max-Sharpe.** A
  metodologia funciona (sem degeneração, diversificação real) mas o
  edge não está lá.
- **Resposta concreta à pergunta original do usuário** ("conseguimos
  adaptar o ~19% CAGR do bestfolio?"): **não nesta variante.** O claim
  19,8% deles vem de sleeves leveraged + ausência dos nossos gates.
  Sob gates honestos + nosso universo, o resultado dynamic é
  estatisticamente igual ao static.

## Decisão

Per SPEC §8 K3 (turnover>100%/yr **e** Sharpe edge < +0.10), a vertente
fecha aqui. Spec §7 sugeria iter 002 com subset de 3 sleeves; **não
recomendo**: o failure é estrutural (densidade de Sharpe apertada),
iter 002 com menos diversificação tende a piorar, e cada iter incrementa
n_trials no DSR deflator (já em 157 → 158 mata DSR de quase tudo).

## Próxima decisão do usuário

1. **Fechar vertente** (recomendado): F1+SPLIT permanece deploy-ready,
   long_term_portfolio FINAL_REPORT é a base.
2. **Insistir iter 002** (max-CAGR Aggressive variant) pra completeness:
   teoricamente diferente do max-Sharpe — pode privilegiar S1+S5
   (alavancado) em detrimento de S3 (defensivo). Ainda assim, expectativa
   de DEAD_END dado os números deste iter.
3. **Pivotar a vertente** pra testar bestfolio sobre universo *diferente*
   — ex.: incluir sleeves que NÃO passaram nossos gates (HAA, BAA,
   Composite). Risco: contamina com sleeves que já sabemos que falham.

## Citações

- bestfolio.app/blog/walk-forward-portfolios — metodologia replicada
- `[advances_fin_ml, p.105-108]` — embargo 21d
- `[advances_fin_ml, p.196-202]` — bootstrap 99.9% CI
- `[advances_fin_ml, p.222-223]` — DSR n_trials=157 cumulative
- `[risk_parity, ch.5]` — sleeve thesis F1+SPLIT incumbent

## Artefatos

- `studies/bestfolio_meta_wf_hunt/iterations/001-.../results.json`
- `studies/bestfolio_meta_wf_hunt/iterations/001-.../verdict.json`
- `studies/bestfolio_meta_wf_hunt/iterations/001-.../final_report.md`
- `studies/_shared/wf_solver.py` — solver canônico (bestfolio-style com
  embargo)
- `tests/test_wf_solver.py` — 5 testes (constraints, dominância, embargo,
  CAGR objective, warmup) todos PASS

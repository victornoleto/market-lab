# Vertente aberta — bestfolio meta walk-forward sobre F1+SPLIT como incumbent

## Contexto

Usuário perguntou se a estratégia bestfolio.app "Aggressive Walk-Forward"
(claim 19,8% CAGR / Sharpe 1,27 / MDD -16,2% em 30 anos) é adaptável pra vida
real. Investiguei as duas páginas que ele linkou
(`/blog/walk-forward-portfolios` e `/methodology#variants-smartleverage`) e
cruzei com o estado atual do projeto.

## O que descobri (resumo curto)

1. O 19,8% **é real como backtest da metodologia deles**, mas tem 3 furos
   compostos que para BR-resident sob Inter Internacional somam ~6 pp/ano:
   - **Meta-overfit** não-tratado: 5 sleeves selecionadas ex-post do catálogo
     bestfolio + walk-forward só dos pesos. Sem PBO, sem DSR, sem embargo
     (extração literal: *"No mention of: PBO, DSR, or formal embargo periods"*).
   - **LETF decay subestimado** no SmartLeverage 2.0x-3.0x.
   - **Taxes "not modeled"** (literal). Sob Lei 14.754/2023 vira ~15% × CAGR
     anual flat, sem dispersão por switch — não é o killer que eu inicialmente
     pensei.

2. **Eu errei no primeiro turno** dizendo "DARF mensal -3 a -4 pp". Lei 14.754
   é apuração anual única na DAA; rebal mensal não dispara DARF. O projeto
   **já tinha corrigido** isso em 2026-04-27 com `studies/_shared/tax_engine.py`
   (`AnnualDarfEngine`). A memória `project_plano_b_broker_inter.md` ainda
   carregava guidance pré-2024 — atualizei agora.

3. Recálculo realista pra nós: 19,8% gross − 3 pp LETF decay − 1 pp slippage =
   ~15,8% gross-after-friction. Aplicar 15% Lei 14.754 = **~13,4% líquido**.
   Não é o 8-10% do meu primeiro chute. Gap vs incumbente F1+SPLIT
   (~10,7% CAGR mean) é ~2,7 pp — relevante mas não óbvio dado o aumento de
   complexidade.

4. **Surpresa importante:** o `bestfolio_hunt_loop` original foi renomeado
   para `studies/long_term_portfolio` em 2026-04-28. Os 10 dead-ends que eu
   inicialmente citei como evidência ("nossos gates já mataram bestfolio")
   viraram a história inicial do long_term_portfolio sweep, que culminou em
   F1+SPLIT como FINAL PICK (deploy-ready). Então a "vertente nova" precisa
   ser distinta dessa estrutura — não é "tentar bestfolio de novo" e sim
   "testar walk-forward dinâmico sobre os winners do long_term_portfolio".

## Decisão

Aberta a vertente **`studies/bestfolio_meta_wf_hunt/`** com `SPEC.md`. Resumo:

- **Hipótese:** WF mensal (lookback 36mo, max 40% por sleeve, no shorts) sobre
  5 portfólios já validados (F1+SPLIT, iter 023 TLT static, iter 020
  AllWeather, F3 SPMO hybrid, F7 RSST heavy) entrega Sharpe líquido ≥ +0.05
  vs F1+SPLIT em ≥ 2/3 datasets, mantendo MDD dentro de F1+SPLIT + 3pp.
- **Gates herdados do projeto** aplicados sobre o meta-portfólio: PBO < 0.5,
  DSR p < 0.05 com n_trials cumulativo, WF k=8 ≥ 6, bootstrap 99.9% CI > 0,
  cross-lib ±3pp.
- **Loop curto:** máx 6 iters. Kill criteria explícitos no spec
  (universo degenerando p/ 1 sleeve, turnover > 100%/yr sem edge, MDD
  estourando +5pp).
- **Tax:** AnnualDarfEngine canônico, gross-of-tax pra scoring,
  net-of-tax informational em `final_report.md`.

Branch alvo: `bestfolio-meta-wf/iter-NNN`. NÃO reutilizar `bestfolio-hunt/*`
(o nome velho já está poluído com 12 branches do loop renomeado).

## O que não é

- Não reativa Plano A nem Plano D (mandate §1, §3, §4b DORMANT).
- Não toca em `studies/long_term_portfolio/` (FROZEN, F1+SPLIT é o incumbent
  oficial enquanto não vier override do mandate §7).
- Não introduz novos ETFs synth — universo travado em
  `_shared/EXTERNAL_INSTRUMENTS.md` + `STRATEGY_ZOO.md`.

## Citações principais

- `[advances_fin_ml, p.208-211]` — PBO de seleção 2-camadas
- `[advances_fin_ml, p.222-223]` — DSR n_trials cumulativo
- `[advances_fin_ml, p.105-108]` — embargoed CV
- `[risk_parity, ch.5]` — incumbent F1+SPLIT thesis
- `[leverage_for_the_long_run]` — LETF decay path-dependence
- bestfolio.app/blog/walk-forward-portfolios (metodologia replicada)
- Lei 14.754/2023 — Planalto

## O que vem a seguir

Aguardando OK do usuário pra rodar **iter 001** (solver max-Sharpe sobre
S1-S5). Próxima sessão: implementar `_shared/wf_solver.py` com retornos dos
sleeves carregados de `long_term_portfolio/iterations/<iter>/results.json`,
rodar 1ª iter, gerar verdict.json, jornada entry.

Critério de morte da vertente inteira: iters 001 e 002 ambos falham gates §5
do spec. Aí F1+SPLIT permanece único candidato deploy.

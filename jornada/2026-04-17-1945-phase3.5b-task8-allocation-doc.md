# 2026-04-17 1945 — Phase 3.5b Task 8 [PLANO B] [SWING BROKER]: Allocation & multi-strategy clarification doc

## Contexto

Última tarefa pré-summary da Phase 3.5b. Até aqui os 4 winners Phase 3
(LETF EMA100/2x, QQQ Donchian 20/10, GLD Donchian 40/20, Portfolio
3-leg EW) já passaram por: report individual (Tasks 3-5), consolidado
(Task 6), FFR-aware re-run (Task 7a), stress isolado (7b), slippage
sensitivity (7c), allocation sweep (7d), rolling correlation (7e) e
vol-target (7f). Falta **responder a pergunta operacional** do usuário:
"são 3 strategies paralelas?"

## O que foi feito

Criado `docs/phase3_winners_allocation.md` (novo, ~170 linhas).
Estrutura:

1. **Pergunta & resposta curta** — NÃO são 3 strategies; é **1
   portfolio 3-leg EW** a (1/3, 1/3, 1/3) com rebalance diário.
2. **Tabela de números** na janela comum 2004-11-18 → 2026-04-14
   (5383 bars) com CAGR / Sharpe / MaxDD / trades para os 4 sleeves +
   SPY B&H benchmark. Portfolio 3-leg EW: CAGR 25.56 %, Sharpe 2.108,
   MaxDD 10.86 %, 259 trades, IR vs SPY 0.722.
3. **4 alternativas rejeitadas e por quê:**
   - Rodar só LETF (pró CAGR, contra Sharpe/DD).
   - 3 contas separadas sem rebalance (vira só-LETF com drift).
   - Promover HRP/ERC (margem dupla `[advances_fin_ml, p.298-299]`
     não dispara).
   - Vol-target 10 % como default (Task 7f já documentou como
     variante defensiva opcional, não winner).
4. **Proporção no capital total** seguindo Investment Mandate §1:
   60-80 % Plano C passivo, 20-40 % ativo dividido entre Plano A e B.
   Dentro da quota de B → 100 % no 3-leg EW. EW é **dentro** do
   portfolio, não do capital total.
5. **Exemplo numérico $10 000:** 70 % C ($7k) + 30 % B ($3k) → $1k
   por perna. Nota para capital $1k: Plano B = $300 colapsa para
   só-LETF até crescer.
6. **Modelagem 15 % IR BR por venda lucrativa** + swap = 0 +
   slippage 5 bps / commission 10 bps (já em summary.json).
7. **Checklist operacional de go-live** (6 itens) + monitoração de
   ρ 252d com alerta se 3 ρ ≥ 0.70 por ≥ 10 barras (evento inédito
   em 21 anos).
8. Referências internas: 3 winner cards + reports/phase3_5b/ +
   books pillars (`leverage_for_the_long_run`, `stocks_on_the_move`,
   `following_the_trend`, `advances_fin_ml`, `expected_returns_ilmanen`,
   `systematic_trading_carver`).

## Numeros-chave (consolidados do `summary.json`)

| Sleeve                   | CAGR    | Sharpe | MaxDD  | IR vs SPY |
|--------------------------|---------|--------|--------|-----------|
| Portfolio 3-leg EW       | 25.56 % | 2.108  | 10.86 %| 0.722     |
| LETF rotation (comum)    | 29.06 %*| 1.724* | ~20 %  | —         |
| QQQ Donchian 20/10       | 17.40 % | 1.389  | 12.79 %| 0.358     |
| GLD Donchian 40/20       | 11.46 % | 0.937  | 14.35 %| −0.013    |
| SPY B&H                  | 10.66 % | 0.629  | 55.20 %| —         |

\* janela comum (desde 2004-11). Janela longa LETF (1970-2026):
CAGR 44.69 %, Sharpe 1.85.

## Testes

Nenhum código tocado (pure doc); pytest baseline 670 passed mantido
(sanity preservada pelas iters 9-13). Memory.md atualizado para
iter 14 com pruning das entries 9-12 para caber < 15 KB.

## Winners imutáveis

Preservados. Nenhuma anomaly nova detectada. Task 8 é documentação
operacional, não revalidação estatística.

## Próximo

**Task 9** — summary jornada Phase 3.5b + flip
`status: done` em memory.md. Será a última iter da Phase 3.5b.

## Citações

- `[advances_fin_ml, p.298-299]` — regra de promoção dupla (Sharpe ∧ DR).
- `[advances_fin_ml, p.271-273]` — MV sample-noise sensitivity.
- `[leverage_for_the_long_run]` — base científica da perna LETF.
- `[stocks_on_the_move, p.81]` + `[following_the_trend]` — Donchian breakout.
- `[expected_returns_ilmanen, p.482-485]` — rebalance frequency equivalence.
- `[systematic_trading_carver, p.107-111]` — vol-target como variante
  defensiva opcional.

## Artefatos

- `docs/phase3_winners_allocation.md` (novo, ~170 linhas)

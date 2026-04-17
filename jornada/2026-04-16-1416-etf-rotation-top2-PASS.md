# [SWING BROKER] ETF Rotation top-2 PASS — Phase A complete

**Data:** 2026-04-16, iteration 21

## O que foi testado

Variante do ETF Rotation mensal já vencedor (Winner #2), agora segurando os **2 ETFs mais fortes** em vez de apenas o top-1, com alocação igual (50%/50%). Universo: SPY, QQQ, IWM, GLD, TLT. Mesmo sinal de momentum (slope ajustado × R²) e filtros de regime/tendência.

Parâmetro: `top_n=2`, pré-especificado pela literatura `[stocks_on_the_move, p.95, ch.6]`.

## Resultados

**IS (2005-2024):**
- Sharpe = 0.708
- CAGR = 8.90%
- MaxDD = -21.44%
- DSR p = 0.0009 ✓ (< 0.05)
- WF = 7/8 ✓ (≥ 6/8)
- PBO = trivial pass (N=1 pre-especificado) ✓

**OOS 2025 (hold-out):**
- Sharpe = 1.611 ✓ (positivo, edge permanece)
- CAGR = 20.67%
- MaxDD = -7.28%

**Stress 2026-Q1:**
- Sharpe = 0.481 ✓ (positivo)
- CAGR = 9.79%
- MaxDD = -13.46%

**Veredicto: PASS** — todos os 3 gates IS + OOS positivo + stress positivo.

## Comparação com top-1

| | Top-1 (Winner #2) | Top-2 (Winner #3) |
|---|---|---|
| IS Sharpe | 0.708 | 0.708 |
| OOS 2025 | 1.477 | 1.611 |
| Stress Q1 | 1.081 | 0.481 |
| IS MaxDD | ~-18% | -21.44% |
| WF | 8/8 | 7/8 |

Ambos passam. Top-2 tem OOS ligeiramente melhor mas Q1 stress mais fraco (GLD/TLT caíram junto em fev-mar 2026 enquanto equities recuavam — diversificação não ajudou nesse período).

## Significado

Esta é a **Winner #3** — completa Phase A do self-improvement loop:
- Path A (SHORT-HOLD CFD): BollingerMR-GARCH SPY 1h ✓
- Path B (SWING BROKER): ETFRotation top-1 + top-2 ✓ ✓
- Total: 3/3 mínimo atingido

**Phase B ativada.** Próximos passos: re-validar cada winner na janela mais longa do manifest, cost ablation, bootstrap CI, cross-asset transport, correlação entre estratégias.

## Tentativa QQQ 1h que falhou nesta iteração

Também foi testado Bollinger MR canonical GARCH para QQQ 1h (janela completa 2020-2026):
- IS PASS: Sharpe=1.133, DSR p=0.0054, WF 6/8 ✓
- OOS 2025: Sharpe = **-0.991** ✗ — QQQ tem beta de crescimento alto e entrou em tendência forte em 2025, quebrando o edge de mean-reversion.
- Confirmação: só SPY tem edge 1h MR estável em OOS. QQQ e XLK falham no mesmo período.

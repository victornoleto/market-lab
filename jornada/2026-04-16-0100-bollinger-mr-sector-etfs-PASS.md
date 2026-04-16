# Bollinger MR replica em sector ETFs — 3 novos winners

> ⚠️ **RETRACTED 2026-04-16 12:45.** XLK e XLE têm os maiores ratios
> raw/adj (~2× e ~2.4× em 2021), portanto os reports de iter 15 foram
> fortemente inflados pelos placeholder bars. Pós-cleanup: XLK Sharpe
> 1.93 → 0.75 (FAIL PBO+DSR), XLE 1.58 → 0.42 (FAIL PBO+DSR), EEM (não
> re-rodado, mas demoção iter 16 permanece). Veja
> [2026-04-16-1245-data-bug-winners-retracted.md](2026-04-16-1245-data-bug-winners-retracted.md).

**Data:** 2026-04-16 01:00
**Iteração:** 15
**Verdict:** ★ 3 NOVOS WINNERS (XLK, XLE, EEM) — winner count 1/10 → 4/10

## Hipótese

Se o edge Bollinger MR 1h funciona em SPY (winner #1), deveria replicar em
sector ETFs ou region proxies. Custo marginal zero: mesmo código, só muda o símbolo.
Lead #7 da memory.

## Ação

Rodou grid Bollinger MR (N=4, w × std_mult) em 5 sector/region ETFs no
período 2021-2025 (Tiingo 1h), e OOS 2025 hold-out com config fixa
(w=20, std=1.5, stop=0.02, max_hold=24). Config foi selecionada em SPY
2021-2024, portanto teste **fair** para os sector ETFs (sem leakage).

## Resultado

| Símbolo | PBO | DSR | WF | Sharpe IS | Sharpe OOS 25 | Decay | Verdict |
|---------|-----|-----|----|-----------| ---------------|-------|---------|
| **XLK** ★ | 0.004 | 4/4 | 4/4 | 1.930 | 1.781 | -5.9% | ★ PASS |
| **XLE** ★ | 0.206 | 3/4 | 3/4 | 1.584 | 1.200 | -24.3% | ★ PASS |
| **EEM** ★ | 0.361 | 1/4 | 4/4 | 1.311 | 1.198 | -8.6% | ★ PASS |
| EFA | 0.317 | 1/4 | 2/4 | 1.186 | 0.335 | -71.8% | marginal |
| XLF | 0.143 | 0/4 | 3/4 | 1.13 | — | — | FAIL DSR |

### Destaque XLK (tech sector)

- PBO=0.004 — best-of-class (vs SPY 0.254).
- DSR 4/4 configs com p < 0.05.
- WF 4/4 configs passam walk-forward (8/8 windows profitable no best).
- IS Sharpe 1.930 (vs SPY 1.314).
- OOS Sharpe 1.781 (decay -5.9%, quase zero).
- CAGR IS 1163% / OOS 780% — engine sem position sizing, compounding agressivo; ler como ranking relativo entre estratégias, não como retorno esperado em produção.
- MaxDD 15.2% IS / 15.0% OOS — estável.
- 173 trades IS / 42 trades OOS.

## Conclusão

- **Bollinger MR 1h é transportável entre ETFs de alta liquidez**, mas com
  seletividade: sectores tech (XLK), energy (XLE) e emerging markets (EEM)
  replicam; financials (XLF) fica logo abaixo do DSR; EFA OOS quebra (-71%
  decay sugere regime dependente).
- **XLK é o novo best_verdict** (Sharpe 1.930 IS / 1.781 OOS supera SPY 1.314/1.312).
- Filtro ADF `[algo_trading_chan, p.47-48, ch.2]` não foi aplicado —
  Bollinger MR clássico `[algo_trading_chan, p.28-30, ch.2]` basta.
- Todas são short-hold CFD-compatíveis (max_hold=24h = 1 dia, bem dentro do
  teto de 5 dias de swap).
- Próxima iteração: decidir se (a) roda um hold-out 2026-Q1 stress test no
  XLK para validar outra janela forward, (b) consome lead #1 (GARCH sizing
  em SPY/XLK) para melhorar risk-adjusted, ou (c) parte para lead seguinte
  para continuar a busca de diversidade (não-Bollinger family).

## Arquivos

- Grids: `reports/grid_bollinger_mr_{XLK,XLE,EEM,EFA,XLF}_1h_iter15/`
- 501 tests green; nenhum código novo, apenas parametrização via CLI.

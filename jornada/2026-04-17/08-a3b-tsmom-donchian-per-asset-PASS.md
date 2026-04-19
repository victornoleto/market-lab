# [SWING BROKER] Phase 3 A3b — QQQ Donchian breakout PASS; TLT/xrpusd FAIL

**Data:** 2026-04-17, iter 36.

## O que foi feito

Lead A3b da Phase 3: **multi-strategy per-asset matching**. Em A3a
(iter 35) o BollingerMR GARCH falhou em 3 assets não-SPY (IWM, TLT,
xrpusd). A tese de A3b é que **cada ativo precisa da família de
estratégia que faz sentido pra ele** — mean-reversion pra SPY,
trend-follow/momentum pra assets trending, etc.

Construí uma **TSMOM Donchian breakout** (Turtles canonical) e rodei um
grid de 10 configs (entry/exit ∈ {20/10, 20/20, 40/10, 40/20, 55/10,
55/20, 55/50, 100/10, 100/20, 100/50}) em 3 assets daily com a janela
MAIS LONGA disponível em cada um:

- **QQQ** daily 2001-05-14 → 2026-04-14 (6266 bars, ~25y)
- **TLT** daily 2002-07-26 → 2026-04-15 (5968 bars, ~24y)
- **xrpusd** daily 2015-02-26 → 2026-04-14 (3878 bars, ~11y)

Splits: IS 60% / OOS 25% / Stress 15%, mutuamente exclusivos (guard
CPCV). Costs realistas: 10 bps commission + 5 bps spread por flip;
**15% IR BR** em ganhos realizados em cada saída LONG→FLAT (Path B
[SWING BROKER] mandate §4).

Citação do signal: Donchian 20/40 Turtle rule
`[trading_systems_methods, p.353]`; TSMOM family
`[algo_trading_chan, p.133, ch.6]`.

## Resultado — verdict por asset

### ★ QQQ: PASS (4/10 configs)

| cid | entry/exit | IS Sh | OOS Sh | Stress Sh | OOS CAGR | OOS MaxDD | WF | DSR p | Boot 99.9% CI |
|---|---|---|---|---|---|---|---|---|---|
| **0** | **20/10** | **1.180** | **1.738** | **1.710** | **20.38%** | **-10.46%** | **8/8** | **0.0041** | **[0.557, 2.954]** |
| 2 | 40/10 | 1.117 | 1.515 | 1.627 | 15.06% | -9.67% | 8/8 | 0.0181 | [0.312, 2.790] |
| 4 | 55/10 | 1.020 | 1.583 | 1.432 | 15.11% | -9.28% | 8/8 | 0.0124 | [0.412, 2.846] |
| 7 | 100/10 | 0.904 | 1.492 | 1.356 | 13.82% | -8.88% | 8/8 | 0.0210 | [0.375, 2.799] |

**Winner cid=0 (Donchian 20/10)**:
- PBO 0.000 (grid-level, gate <0.5).
- OOS Sharpe 1.738 **> LETF B1c OOS 1.724** (marginal novo best por Sharpe).
- OOS CAGR 20.38% **acima do CDI BR 13-14% e acima do mandate target 15%**.
- Walk-forward 8/8 (todos profitable, max DD ≤ 25% em cada janela).
- DSR p=0.0041 com n_trials=10 (**<< 0.05**).
- Bootstrap 99.9% CI [0.557, 2.954] — lower bound > 0.
- Stress (2022-07 → 2026-04) Sharpe 1.710 com CAGR ~17% — sobrevive ao
  stress forward-window.

**Full-window** (toda a história): 107 trades, median hold 34d, mean
42d, full-period Sharpe 1.389, CAGR 17.40%, final equity 54× unit.
Classicamente **Path B [SWING BROKER]** (swing daily, hold em semanas).

### TLT: FAIL (0/10 configs)

Best OOS Sharpe 0.704 (Donchian 20/10); **todas configs falharam DSR**
(p-values 0.44-0.66). Bonds têm rate-cycle drift lento; breakout gera
whipsaw em movimentos pequenos. Consistente com A3a FAIL onde TLT
tinha Sharpes negativos em BollingerMR.

### xrpusd: FAIL (0/10 configs)

Best OOS Sharpe 0.829; **nenhum config passou DSR + WF**. MaxDD em
walk-forward atinge 51-76% — crypto vol aniquila trend-follow mesmo
com tax/cost realistas. Confirma padrão de A3a (xrp BollingerMR FAIL
com MaxDD 68-77%).

## Por que isso importa

1. **A3b confirma tese: match strategy family ao comportamento do
   ativo.** BollingerMR (MR) funciona só em SPY (equity índice amplo
   com reversion curta). Donchian (trend-follow) funciona em QQQ
   (tech growth com trending séculares). TLT e xrpusd NÃO funcionam
   em trend-follow single-asset — rate-cycle drift (bonds) e
   crypto-vol (altcoins) violam os pressupostos.
2. **Path B ganha uma segunda strategy uncorrelated.** LETF rotation
   (iter 32) é trend-follow via SPX regime MA; QQQ Donchian é
   breakout direto no preço QQQ. Diferentes signals, diferentes
   universes — candidato a portfolio A3c.
3. **QQQ OOS Sharpe 1.738 > LETF B1c OOS 1.724.** Margem fina mas
   QQQ Donchian é tecnicamente o **best single OOS Sharpe** da
   Phase 3. CI bootstrap mais larga (LETF [1.037, 2.468] vs QQQ
   [0.557, 2.954]) — LETF ainda mais robusto em magnitude. Não
   sobrescrevo `best_verdict` porque LETF tem janela 56y vs 25y e
   CI mais apertado.

## Next

- **A3c:** portfolio refactor. LETF rotation + QQQ Donchian como
  2-asset Path B portfolio. Gate: portfolio Sharpe > best single AND
  diversification ratio > 1.2. Citação
  `[advances_fin_ml, ch.7/11]` para risk budgeting.
- A3d (fallback) **não mais necessário** — A3b yielded winner.

## Files

- Código:
  - `src/ai_trade/backtest/strategies/tsmom.py` (sim + config)
  - `src/ai_trade/backtest/grid/tsmom_a3b.py` (gates per asset)
  - `scripts/run_grid_tsmom_a3b.py` (orchestrator)
  - `tests/test_tsmom.py` + `tests/test_tsmom_a3b.py` (+26 tests)
- Reports:
  - `reports/a3b_tsmom_QQQ.json`
  - `reports/a3b_tsmom_TLT.json`
  - `reports/a3b_tsmom_xrpusd.json`
  - `reports/a3b_tsmom_summary.json`
- Pytest: **517 passed** (baseline 491 + 26 novos, zero regression).

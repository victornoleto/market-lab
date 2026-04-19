# [SHORT-HOLD CFD] A3a — BollingerMR + GARCH não transporta de SPY para IWM / TLT / xrpusd (FAIL)

**Data:** 2026-04-17 00:08 BRT
**Iter:** 35
**Lead Phase 3:** A3 (sub-lead A3a)
**Verdict:** **FAIL em todos 3 ativos** — SPY-only edge confirmado uma segunda vez.

## O que foi feito

Rodado o grid BollingerMR com `--garch-lambda 0.94` (EWMA-GARCH
RiskMetrics, `[machine_trading, p.126-127, ch.4]`) nos 3 ativos priorizados
pelo screener A2 (iter 33), cada um na **janela mais longa disponível
no manifest Tiingo**:

| Ativo  | Freq   | Janela                        | Bars  | Hurst (A2) |
| ------ | ------ | ----------------------------- | ----- | ---------- |
| IWM    | 1h     | 2020-01-02 → 2026-04-14       | 9,462 | 0.447      |
| TLT    | 1h     | 2020-01-06 → 2026-04-14       | 9,450 | 0.470      |
| xrpusd | daily  | 2015-02-26 → 2026-04-14       | 3,878 | 0.513      |

Grid = 4 configs por ativo (canonical 2×2: window ∈ {20,40}, std_mult
∈ {1.5, 2.0}). `[algo_trading_chan, p.28-30, ch.2]`,
`[machine_trading, p.204-205, ch.7]`.

Gates: PBO < 0.5, DSR p < 0.05 (N=4 deflation), WF ≥ 6/8 (max DD ≤ 25%).

## Resultado — todos os 3 ativos reprovaram em TODOS os gates

### IWM 1h GARCH (grid_phase3_a3a_iwm_1h_garch)

- PBO 0.619 (reject), DSR 0/4, WF 0/4.
- Melhor config (20, 2.0): Sharpe 0.361 / CAGR 3.21% / MaxDD 17.45%, WF 4/8.
- Pior (40, 2.0): Sharpe -0.205 / CAGR -3.0%.

### TLT 1h GARCH (grid_phase3_a3a_tlt_1h_garch)

- PBO 0.575, DSR 0/4, WF 0/4. **Todas configs com Sharpe negativo**.
- Melhor config (20, 1.5): Sharpe -0.206 / CAGR -2.0% / MaxDD 18.9%, WF 2/8.
- Bonds rates-driven 2022-2024 destruíram qualquer MR intraday.

### xrpusd daily GARCH (grid_phase3_a3a_xrp_daily_garch)

- PBO 0.698 (muito alto), DSR 0/4, WF 0/4.
- Melhor config (20, 2.0): Sharpe 0.232 / CAGR 3.5% / **MaxDD 67.7%** / WF 4/8.
- Drawdowns 35%-94% entre janelas — crypto vol annihila sizing fixo.
- Apesar do Hurst medido ≈ 0.513 (perto do random walk), a prática mostrou
  que xrpusd passa por regimes de trend violento (2017, 2021) que
  BollingerMR falha em capturar.

## Interpretação

O edge BollingerMR+GARCH identificado em SPY 1h (iter 19: IS Sharpe 0.995 /
OOS 0.945 / WF 7/8) não é transportável:

1. **IWM 1h:** apesar de ETF correlacionado com SPY e Hurst mais baixo (0.447,
   mais MR-like), o edge some. Hipótese: IWM tem microstructure diferente
   (small-cap churn, spread maior 2020-2022, maior kurtosis intraday).
2. **TLT 1h:** rates-driven; macrofator bonds domina e vira regime
   uni-direcional (2022 bear rates). Não existe MR intraday quando o ativo
   tem drift forte.
3. **xrpusd daily:** vol 60%+ anualizada + crashes > 50% recorrentes —
   sizing fixo BollingerMR não aguenta. GARCH não-suficiente.

Isto reforça o Dead end já em memory ("Bollinger MR em 13 ETFs ≠ SPY —
todos FAIL"): **a versão final do BollingerMR é SPY-specific** e não
pode ser escalada por portfolio equal-weight através do universe
screener.

## Consequência para Strategy A (Path A — short-hold CFD)

Estado atualizado:

- **Single-asset SPY 1h BollingerMR GARCH:** Sharpe 0.945 / CAGR 5.9%
  (iter 19 winner). Abaixo do CDI BR (~13-14%). NÃO atinge mandate A
  (5-10%/mês).
- **A1 leverage sweep (iter 28):** Kelly-ótimo L=2 → Sharpe 0.592 /
  CAGR 10.76% (PARTIAL-GO). L≥3 viola DD gate. Ainda abaixo de CDI.
- **A2 screener (iter 33):** universe apurado — IWM/SPY/TLT/QQQ/GLD
  top-5 equity, BTC/ETH trending e excluídos, FX não cacheado.
- **A3a (esta iter):** transporte direto BollingerMR → IWM/TLT/xrpusd
  **falhou**. Não existe portfólio equal-weight single-strategy viável.

**Próximos leads possíveis (pick em A3b):**

1. **A3b — Multi-strategy per-asset matching:** em vez de forçar BollingerMR
   em todos os ativos, rodar um catálogo de estratégias por ativo
   (BollingerMR para SPY, momentum para BTC/ETH, trend-follow para TLT
   bonds via Turtle/Clenow intraday) e medir Sharpe por par
   (ativo, strategy). Cita `[stocks_on_the_move, ch.4]` (momentum
   individual) + `[algo_trading_chan, ch.2]` (MR reserved for sub-unity H).
2. **A3c — Pivô Strategy A para momentum 1h cross-asset:** adotar
   Clenow adjusted-slope como Strategy A em vez de BollingerMR. A2
   screener mostra top assets; Clenow rodou daily e falhou (PBO 0.603),
   mas 1h nunca foi testado.
3. **A3d — Reconhecer Strategy A como "SPY-only single-asset"** e
   recalibrar mandate (aceitar CAGR ≤ CDI como constraint irreversível
   desta classe de estratégia, e mover esforço para Strategy B LETF
   que já passa 20%/ano).

## Arquivos e tests

Nada novo em `src/` nesta iter (só scripts executados). Baseline
**491 tests passed, 0 failed** — intacto.

Reports:
- `reports/grid_phase3_a3a_iwm_1h_garch/diagnostic.md`
- `reports/grid_phase3_a3a_tlt_1h_garch/diagnostic.md`
- `reports/grid_phase3_a3a_xrp_daily_garch/diagnostic.md`

## Citações

- `[machine_trading, p.126-127, ch.4]` — EWMA-GARCH RiskMetrics λ=0.94.
- `[machine_trading, p.204-205, ch.7]` — canonical Bollinger 20/2.
- `[algo_trading_chan, p.28-30, ch.2]` — Bollinger mean-reversion hypothesis.
- `[advances_fin_ml, p.208-211]` — PBO gate.

## Decisão

Lead A3a = **FAIL documentado**. Marcar em memory.md como sub-lead
finalizado. A3 global ainda aberto — próxima iter deve atacar A3b
(multi-strategy per-asset) ou A3d (reconhecer SPY-only e fechar A3).

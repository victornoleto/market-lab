# [SHORT-HOLD CFD] Phase 3.5a — T5 Regime-filter hybrid: 0/6 PASS, DEAD

**Data:** 2026-04-18 ~18:00 BRT
**Path:** A (Pepperstone CFD, short-hold ≤ 5 dias)
**Phase:** 3.5a — investigação Plano A
**Verdict:** DEAD END. 5º lead consecutivo sem winner em 1h.

---

## TL;DR

T5 sobrepôs 4 filtros de regime (SMA-200 bar, RV-low 30d, RV-high
30d, combo SMA∧RV-low) + 1 canonical sem filtro sobre o core
BollingerMR 20/2σ em 6 tickers (QQQ, SPY, eurusd, gbpusd, usdjpy,
xauusd) 1h sobre janela Tiingo 2020-01-06 → 2026-04-14 (~6.3 y,
longest window per manifest). **Zero tickers passaram os 5 gates**
(PBO<0.5 + DSR p<0.05 + WF≥6/8 + OOS>0 + FWD>0 + hold ≤5 d).

- **Equity (QQQ, SPY):** hold 2.9–3.0 d OK. OOS Sharpe −0.46 a −0.84
  best. SPY `rv_lowvol` tem FWD +2.62 em 11 trades mas WF 3/8 / DSR
  p=0.35 — amostra marginal demais.
- **FX (eurusd, gbpusd, usdjpy):** hold 0.54–0.67 d. OOS Sharpe
  catastrófico −2.31 a −2.62. Problema = **friction**: 162–191
  trades OOS × 2 bps half-spread + commission come equity.
- **Metal (xauusd):** o pior. OOS Sharpe −2.75 best, canonical
  −3.65 / CAGR −34.9% / MaxDD −59.3% / 1238 trades. PBO cross-config
  **0.559 FAIL** — 1º ticker T5 a falhar PBO (configs homogêneas em
  perda).
- **Todas configs:** DSR pass 0/30, WF≥6/8 0/30, hold ≤5d 30/30.

## Cross-ticker (best config por ticker, todos fail)

| Ticker | Best config           | Sharpe OOS | CAGR OOS % | MDD OOS % | Trades | Hold (d) | FWD   | PBO cross | PASS |
|--------|-----------------------|-----------:|-----------:|----------:|-------:|---------:|------:|----------:|:----:|
| QQQ    | bmr_rv_highvol_30d    |     −0.693 |     −6.05  |    −15.16 |     39 |    2.917 | +0.00 |     0.591 |  ✗   |
| SPY    | bmr_rv_lowvol_30d     |     −0.464 |     −3.86  |    −13.74 |     71 |    3.000 | +2.62 |     0.119 |  ✗   |
| eurusd | bmr_regime_combo      |     −2.308 |     −5.51  |    −12.69 |    191 |    0.542 | −1.78 |     0.258 |  ✗   |
| gbpusd | bmr_rv_highvol_30d    |     −2.564 |     −8.09  |    −16.08 |    162 |    0.667 | −3.05 |     0.167 |  ✗   |
| usdjpy | bmr_rv_highvol_30d    |     −2.615 |    −13.74  |    −26.76 |    178 |    0.625 | +0.27 |     0.052 |  ✗   |
| xauusd | bmr_rv_highvol_30d    |     −2.753 |    −24.66  |    −45.62 |    271 |    0.583 | −3.85 |     0.559 |  ✗   |

Detalhes em `reports/phase3_5a/t5_regime_filter_hybrid/AGGREGATE.md` e nos
6 `<ticker>.md` / `.json`.

## Diagnóstico

Tese regime-aware "filtragem reduz trade count sem matar amostra,
preservando o edge MR só em regimes on" é **refutada empiricamente**.
Filtros reduzem magnitude das perdas (canonical 234 trades IS SPY
→ 59–150 filtradas), mas **não invertem sinal**: OOS Sharpe
uniformemente negativo. Três leituras:

1. **MR edge 1h secou pós-2023.** Consistente com T1 canonical e T5
   canonical. Filtro não cria edge onde não existe.
2. **Filtros testados são lineares/hard.** SMA-200 + RV-30d + combo
   são filtros clássicos. Meta-labeling triplo-barreira
   `[advances_fin_ml, ch.18-19]` com bracket SL/TP talvez resolvesse,
   mas é lead próprio (potencial T8).
3. **Custos Razor consomem MR sub-daily.** Confirmado em
   **T1+T2+T3+T4+T5 = 102 runs 1h em 5 famílias distintas**, zero
   winner. Half-spread 2 bps + commission 1–2 bps + swap 0.005%/dia
   é piso que fecha sub-daily MR/session/breakout/pair/regime em FX
   e metais.

**Lição convergente Phase 3.5a:** 1h FX/metais Razor-tier é mercado
morto para MR/session/breakout/pair/regime clássico. Próximo lead
(T6) deve rebalançar a meta Plano A reconhecendo isso explicitamente.

## Citações

- `[advances_fin_ml, ch.17]` — regime-aware features; lição aqui é
  que hard-gate linear não captura regime não-linear.
- `[advances_fin_ml, ch.7]` — PBO cross-config via trial ranking.
- `[stocks_on_the_move, p.110]` — SMA trend regime filter (base do
  `bmr_regime_sma200`).
- `[volatility_trading]` — RV regime lowvol/highvol (base dos
  `bmr_rv_*`).
- `[systematic_trading, p.185-188]` — hold ≤ 5 d discipline
  (respeitada em 30/30 configs).

## Próximo passo

**Lead T6 — Rebalance meta Plano A (jornada override §7 mandate).**
Atomic lead, não sweep. Tarefas:

1. Calcular "máximo CAGR sustentável Plano A" dadas as evidências
   das 5 famílias já rodadas: best candidate seria SPY 1h
   `bmr_rv_lowvol_30d` hipotético se tivesse passado gate
   — não passou, então **o máximo demonstrado é 0%/yr líquido**.
2. Definir meta NOVA respeitando A > B ~29%/yr:
   - opção α: manter A short-hold CFD mas pivotar para **frequência
     daily** (viola spec hold ≤5 d? checar — depende da definição).
   - opção β: aceitar que Plano A não suporta A > B sob custo Razor
     real e **atualizar mandate §7** com override documentado.
   - opção γ: mudar família completamente em 1h (trend-following
     continuation, não MR — novo lead T8).
3. Atualizar `docs/investment-mandate.md` §7 com a decisão tomada.

Se T6 concluir "override" → T7 summary direto. Se T6 concluir
"explorar T8" → T8 bootstrap atomic ou sweep.

## Pointers

- Registry: `reports/phase3_5a/t5_regime_filter_hybrid/registry.json`
- Aggregate: `reports/phase3_5a/t5_regime_filter_hybrid/AGGREGATE.md`
- Per-ticker: `reports/phase3_5a/t5_regime_filter_hybrid/{QQQ,SPY,eurusd,gbpusd,usdjpy,xauusd}.md`
- Iter counter: 33 bootstrap + 34–39 sweep + 40 aggregator = 8 iters
- Pytest baseline: manter 765 passed (sem código novo tocado neste aggregator)

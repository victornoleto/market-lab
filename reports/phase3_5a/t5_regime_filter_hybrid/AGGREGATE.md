# Lead T5 — Regime-filter hybrid overlay on BollingerMR 20/2σ 1h (aggregate)

**Phase:** 3.5a | **Lead:** T5 | **Status:** DEAD END (0/6 PASS)
**Period:** 2020-01-06 → 2026-04-14 (~6.3 y, Tiingo IEX 1h cache; longest window per manifest)
**Tested:** 6 tickers (QQQ, SPY, eurusd, gbpusd, usdjpy, xauusd) × 5 configs = 30 runs
**Aggregation iter:** 40

## Summary

T5 sobrepôs **4 filtros de regime** (SMA-trend 200 bar, RV low-vol 30 d,
RV high-vol 30 d, e combo SMA-trend ∧ RV low-vol) + **1 canonical
sem filtro** sobre o core BollingerMR 20/2σ 1h, com o objetivo
explícito de "filtragem reduz trade-count sem matar amostra"
(`[advances_fin_ml, ch.17]` — regime-aware features / meta-labeling;
`[stocks_on_the_move, p.110]` — SMA trend filter). Após modelar o
stack Pepperstone Razor completo (2 bps half-spread + $3.50/side +
swap diário assimétrico) e aplicar o framework 5-gate
(PBO<0.5 + DSR p<0.05 + WF≥6/8 + single-block OOS>0 + FWD>0),
**0/6 tickers passam**. Filtros reduzem trades (canonical 234→
59–150 IS em SPY), mas **não reduzem Sharpe negativo — só reduzem
magnitude das perdas**; o edge MR bruto já não existe em OOS
(pós-2023) para nenhum dos 6 ativos.

Pattern por classe de ativo:

- **Equity (QQQ, SPY):** padrão "degrade-então-colapso". IS tem flashes
  positivos para `bmr_rv_lowvol_30d` em SPY (+0.31) mas OOS é uniformemente
  negativo (−0.46 a −0.84 best). PBO cross-config SPY 0.119 (PASS forte
  — configs se ordenam consistentemente), QQQ 0.591 (FAIL — configs
  homogêneas em perda). Hold 2.9–3.0 d dentro do budget ≤5 d, então o
  problema **não é hold** — é ausência de edge OOS. FWD positivo em
  SPY `rv_lowvol` (+2.62 em 11 trades) e `regime_combo` (+4.66 em 4
  trades) — amostras pequenas demais para sustentar DSR ou WF.
- **FX majors (eurusd, gbpusd, usdjpy):** catastrófico. OOS Sharpe
  −2.31 a −2.62 no best de cada ticker. Hold mediano 0.54–0.67 d
  (quase intraday), portanto dominante é **trade-count × half-spread**:
  191–178 trades OOS em 2 anos × 2 bps round-trip come equity
  diretamente. Filtros regime não ajudam porque o problema é de
  **friction**, não de direção: qualquer redução via filtro que
  sobrevive gera amostra pequena demais para gate estatístico (WF
  0–2/8 em todas). Convergente com T1 (canonical FX fails), T2
  (breakout FX fails), T3 (pairs FX fails), T4 (session FX fails):
  **BollingerMR + regime filter não salva FX 1h**.
- **Metals (xauusd):** o pior. OOS Sharpe −2.75 best, CAGR −24.7%,
  MaxDD −45.6%; canonical OOS catastrófico −3.65 / CAGR −34.9% /
  MaxDD −59.3% / 1238 trades. Vol alta + half-spread 2 bps × curto
  hold 0.58–0.67 d = burn tape. PBO cross-config 0.559 (FAIL — 1º
  ticker T5 a falhar PBO, configs todas em perda coletiva).

Cross-family:

- **PBO pass em 5/6 tickers** (QQQ e xauusd falham). Mas PBO passando
  num universo onde TODAS as configs são OOS-negativas é
  informação vazia — significa que o **rank dos losers é estável**,
  não que existe winner.
- **DSR pass: 0/30 configs.** Nenhuma passa p<0.05; p-values médios
  0.6–1.0. PSR < 0.5 em todas.
- **WF 6/8: 0/30 configs.** Melhor WF: SPY `bmr_rv_lowvol_30d` 3/8.
  Filtro `rv_highvol` + `sma_trend` rejeitam 100% dos tickers (0–2
  janelas profitable em 8).
- **Hold ≤ 5 d: 30/30 configs.** Disciplina de hold-time
  (`[systematic_trading, p.185-188]`) respeitada, mas irrelevante — a
  falha é de edge, não de swap.
- **FWD (2026 YTD):** positivo em SPY `rv_lowvol` (+2.62) e
  `regime_combo` (+4.66), mas com 11 e 4 trades respectivamente —
  amostra de ~3.5 meses não sustenta gate.

## Cross-ticker (best config por ticker, todos fail)

| Ticker | Best config           | Sharpe OOS | CAGR OOS % | MDD OOS % | Trades OOS | Hold (d) | FWD Sharpe | PBO cross | PASS |
|--------|-----------------------|-----------:|-----------:|----------:|-----------:|---------:|-----------:|----------:|:----:|
| QQQ    | bmr_rv_highvol_30d    |     −0.693 |     −6.05  |    −15.16 |         39 |    2.917 |       0.00 |     0.591 |  ✗   |
| SPY    | bmr_rv_lowvol_30d     |     −0.464 |     −3.86  |    −13.74 |         71 |    3.000 |      +2.62 |     0.119 |  ✗   |
| eurusd | bmr_regime_combo      |     −2.308 |     −5.51  |    −12.69 |        191 |    0.542 |      −1.78 |     0.258 |  ✗   |
| gbpusd | bmr_rv_highvol_30d    |     −2.564 |     −8.09  |    −16.08 |        162 |    0.667 |      −3.05 |     0.167 |  ✗   |
| usdjpy | bmr_rv_highvol_30d    |     −2.615 |    −13.74  |    −26.76 |        178 |    0.625 |      +0.27 |     0.052 |  ✗   |
| xauusd | bmr_rv_highvol_30d    |     −2.753 |    −24.66  |    −45.62 |        271 |    0.583 |      −3.85 |     0.559 |  ✗   |

Best **por família de filtro** (cross-ticker, OOS Sharpe medio):

| Regime filter          | OOS Sharpe mean | OOS CAGR mean % | Best ticker | Best sharpe_oos |
|------------------------|----------------:|----------------:|------------:|----------------:|
| bmr_canonical          | −2.75           | −14.5           | SPY         | −0.84           |
| bmr_regime_sma200      | −1.72           | −8.5            | SPY         | −0.52           |
| bmr_rv_lowvol_30d      | −1.93           | −10.0           | SPY         | −0.46           |
| bmr_rv_highvol_30d     | −1.74           | −11.3           | SPY         | −0.62           |
| bmr_regime_combo       | −1.75           | −8.6            | SPY         | −0.69           |

Nenhum filtro domina — todos são variações do mesmo tema de perdas
OOS, com `rv_lowvol` marginalmente melhor (ele concentra trades em
quiet-regime onde MR tradicional funciona) e `rv_highvol` pior (vol
alta + custo Razor = pior relação bruto/friction).

## Diagnóstico

A tese regime-aware — "filtragem reduz trade count sem matar amostra,
preservando o edge MR só em regimes onde ele existe" — é **refutada
empiricamente** neste universo. Três leituras possíveis:

1. **MR edge em 1h secou pós-2023** (consistente com T1 canonical
   e T5 canonical, ambos OOS negativos uniformemente) — regime
   filter não cria edge onde não existe, só o ordena.
2. **Filtros testados são grosseiros demais** — SMA-200 bar + RV
   30 d + combo são filtros clássicos; meta-labeling AFML capítulo
   18/19 com labeling triplo-barreira + SL/TP bracket talvez
   resolvesse, mas esse é um lead próprio (T8 potencial, não T5).
3. **Custos Razor consomem qualquer edge MR sub-daily** — confirma
   recorrência T1+T2+T3+T4+T5 = 102 runs 1h em 5 famílias distintas
   sobre FX majors, 0 winner. Half-spread 2 bps + commission 1–2
   bps + swap 0.005% é piso que fecha sub-daily MR no 1h.

Lição chave para Phase 3.5a: **MR 1h + regime filter não escapa do
mesmo custo-buraco que MR 1h puro**. O próximo lead (T6) deve
rebalançar a meta Plano A reconhecendo que **1h MR em FX/metais
Razor-tier é mercado morto**, e considerar explicitamente: (a)
mudar para frequência daily (viola gate short-hold mas preserva
net-edge), (b) mudar para família completamente diferente em 1h
(trend-following continuation, não MR), ou (c) aceitar override §7
do mandate.

## Citações

- `[advances_fin_ml, ch.17]` — regime-aware features e meta-labeling.
  Filtragem testada aqui é filtro-hard (gate on/off), não meta-label
  probabilístico; a lição é que hard-gate em indicador linear (SMA/RV)
  não captura regime não-linear.
- `[advances_fin_ml, ch.7]` — PBO cross-config via ranking dos trials.
  PBO passando (5/6) mas DSR/WF falhando (30/30) é o padrão clássico
  de "edge inexistente, não de overfit per se".
- `[stocks_on_the_move, p.110]` — SMA trend regime filter; base
  teórica do `bmr_regime_sma200`.
- `[volatility_trading]` — RV-based regime (low-vol vs high-vol);
  base teórica do `bmr_rv_*`.
- `[systematic_trading, p.185-188]` — disciplina de hold ≤ 5 d
  (respeitada em 30/30 configs).

## Links

- Per-ticker reports: `reports/phase3_5a/t5_regime_filter_hybrid/*.md` (6 tickers)
- Per-ticker JSONs: `reports/phase3_5a/t5_regime_filter_hybrid/*.json` (6 tickers)
- Registry: `reports/phase3_5a/t5_regime_filter_hybrid/registry.json`
- Jornada: `jornada/2026-04-18-1800-phase3.5a-T5-regime-filter-hybrid-DEAD.md`
- Iter counter: 33 (bootstrap) + 34–39 (sweep QQQ/SPY/eurusd/gbpusd/usdjpy/xauusd) + 40 (aggregator) = 8 iters total

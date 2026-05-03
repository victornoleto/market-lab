---
system_id: 10192401
family: UNCATEGORIZED
reason_code: taxonomy_gap
candidate_new_family: BTC_NY_HOURS_BB_TREND
confidence: 0.55
generated: 2026-05-02
rule:
  entry_window_utc: ["15:00", "18:59"]
  pairs: [BTCUSD]
  direction: |
    # Single dominant feature from DecisionTree(max_depth=4):
    # bb_pos_20_2_H1 importance = 0.89, CV match_rate = 0.874 ± 0.029.
    # Threshold from candidates.json rank 1 (Tree) root split.
    # bb_pos_20_2_H1 normalises price within H1 Bollinger Band(20, 2σ):
    # -1 = lower band, 0 = mid, +1 = upper band.
    BUY  if bb_pos_20_2_H1 > -0.04
    SELL if bb_pos_20_2_H1 <= -0.04
    # Confirmed by univariate rank 5 (ema_dist_20_H1 > 0.1038, 86.7% CV,
    # corrected p=5.5e-54) and rank 6 (bb_pos_20_2_H1 > 0.01682, 86.7% CV,
    # same p). All three describe the same H1 trend-state factor.
  exit:
    max_holding_hours: 4.5      # ~p95 hold pos-R4 = 4.32h
    take_profit_pips: null
    stop_loss_pips: null
    # exit_kind = manual_or_time for 100% of trades.
    # Hold p50 = 0.06h (~3.6 min), p95 = 4.32h, max = 86h pos-R4 fix.
    # Median hold e intraday-scalp; p95 cobre swing curto. Cap em 4.5h
    # captura 95% da distribuicao observada.
  sizing: proportional_equity_2pct
  # Lot p95/p50 = 2.04 (sem martingale, steps=0, max_streak=0).
  # Lot dispersion compativel com sizing proporcional ao equity.
citations:
  - "[trading_systems_methods, p.323-324] — '20-day Bollinger, 2 sigma: if it is not 20-day and 2 sigma, it is not a Bollinger band — established convention; 2 sigma approx 87% coverage in skewed distributions.' Match exato com bb_pos_20_2_H1."
  - "[trading_systems_methods, p.326-327] — 'Bollinger reversal: Buy on close > upper band; short on close < lower band. Exit at center trendline.' Sistema usa BB-mid como switch de direcao (trend-follow polarity), nao como entrada de outer-band reversal."
  - "[algo_trading_chan, p.71-72, ch.3] — 'Bollinger band entryZscore / exitZscore … free parameters to be optimized in a training set. Chan uses entryZscore=1, exitZscore=0 in examples.' Threshold do sistema (~0) alinha com exitZscore convention de Chan, repurposed como entry filter."
  - "[advances_fin_ml, ch.3] — label consistency over forced labels. Justifica UNCAT + taxonomy_gap quando a evidencia mecanica e clara mas o enum atual nao tem slot semanticamente valido (taxonomia FX-session vs asset BTC 24/7)."
  - "[evidence_based_ta, p.367-380] — Aronson multiple-comparison correction. Corrected p=1.9e-43 (n_tests=520) em bb_pos_20_2_H1 sobrevive Bonferroni-equivalente; edge e estatisticamente real."
risk_flags:
  - "Asset BTCUSD (crypto, 24/7) sai da taxonomia FX-session-centric. Top hours 15-18 UTC mapeiam ao 'NY afternoon' que coincide com pico de liquidez institucional do BTC, mas semantica de 'session' e fraca."
  - "Hold p50=0.06h (~3.6 min) e curto demais pra OVERLAP_NY_LONDON_RANGE canonico (que espera time-based exit em janela de sessao de 1-3h). Combinado com p95=4.32h, distribuicao e bimodal: maioria scalp ultra-rapido (provavelmente TP fixo intra-bar M1/M5 nao capturado nos features) + cauda swing curto."
  - "Edge e single-feature (bb_pos_20_2_H1 importance=0.89), o que NAO bate o criterio FACTOR_SCALPING ('vol-targeting ou pair-trading intraday' — multi-fator)."
  - "Taxonomy gap: estrategia coerente (BTC + NY-hours + H1 BB-mid trend filter + intraday scalp exit) mas fora dos 9 oficiais e 3 provisorias. Provisional H1_MOMENTUM_GOLD e o mais proximo (single asset + H1 momentum) mas asset errado e mecanismo BB != momentum puro."
  - "Sample 420 trades em 21 meses, single asset → robustez cross-asset zero. Window 2022-11→2024-08 cobre post-FTX-bottom bear → 2024 bull, regime favoravel a trend-follow."
  - "Direction-by-hour mostra heterogeneidade (hour 15 buy_pct=58.8%, hour 17 buy_pct=40.4%). Stage 3 deve confirmar que isso e 100% explicado por bb_pos_20_2_H1 e nao um efeito hour-of-day residual."
---

# Decoded signal — Happy Bitcoin - TMGM (id 10192401)

## Family rationale

Decisao final: `UNCATEGORIZED + reason_code=taxonomy_gap + candidate_new_family=BTC_NY_HOURS_BB_TREND`. A evidencia mecanica e clara e estatisticamente forte, mas nenhuma das 9+3 familias do enum atende sem violar criterios materiais. Reasoning familia-por-familia:

- **MARTINGALE_GRID**: rejeitado. `martingale flag: PASS`, steps=0, max_streak=0, lot p95/p50=2.04. Dispersion is small e linear-em-equity, caracteristica de sizing proporcional, nao de grid.

- **LATE_NY_BREAKOUT**: rejeitado. Top entry hours 15-18 UTC, nao 21-01 UTC. BTC nao tem "Asian range" canonico (mercado 24/7 sem session boundaries definidos).

- **LONDON_OPEN_MOMENTUM / LONDON_OPEN_MR**: rejeitado. Zero concentracao em 06-09 UTC (hour 10 com 28 trades e o inicio do top-5, depois sobe pra peak em 17h).

- **NY_SESSION_REVERSAL**: rejeitado. Window 12-16 esperado vs 15-18 observado (overlap parcial), mas esta familia esta vazia pos-Wave 1+2+3 do 5R-0 (finding sobre vendor HappyForex sem reversal genuino na library — `decoder_taxonomy.py` linha 118), e a regra direcional e trend-follow no BB-mid, nao reversal cross-session.

- **OVERLAP_NY_LONDON_RANGE**: parcialmente compativel mecanicamente (BUY/SELL determinado por posicao na BB sim; exit time-based sim), MAS:
  1. Window canonica 12-16 UTC vs observada 15-18 (shift de 3h, overlap parcial so em 15-16h).
  2. Hold p50=0.06h (~3.6 min) e incompativel com "range fade no overlap" que tipicamente tem hold de 1-3h (range completion intraday).
  3. Asset BTC (24/7) torna semantica de "NY/London overlap" fraca — hours 15-18 UTC correspondem a *NY institutional afternoon*, nao overlap (overlap NY/London canonico fecha 16:00 UTC quando London fecha).

- **OVERNIGHT_GAP_FADE**: rejeitado. BTC sem weekend gap. Sem concentracao sex/seg.

- **FACTOR_SCALPING** (label do Sonnet baseline): parcialmente compativel pela duration (p50=3.6min < 30min sim), MAS criterio explicito do enum exige "edge tipicamente vol-targeting ou pair-trading intraday" e "entry distribuido". Aqui:
  1. Edge e **single-feature dominante** (bb_pos_20_2_H1 importance=0.89), o oposto de multi-fator.
  2. Entry e **concentrado** em 4 horas (15-18 UTC = 41.9% dos trades em 4 horas), nao distribuido.
  3. Nao ha vol-targeting nem pair-trading.

- **H1_MOMENTUM_GOLD (provisional D7)**: rejeitado. Asset errado (BTC vs Gold), e mecanismo e BB-position trend-filter, nao H1 momentum puro.

- **NEWS_RELEASE_MOMENTUM (provisional D5)**: rejeitado. Sem name-flag NEWS, sem clock-anchor de bucket unico >30%, top-hour 17:00 tem 13.6% (nao passa).

- **SWING_TREND_MOMENTUM (provisional D6)**: rejeitado. Mediana hold = 0.06h, longe dos >72h exigidos.

A estrategia subjacente e coerente e replicavel: **"Em horario de pico de liquidez BTC institucional (NY afternoon), use posicao relativa ao H1 BB-20-2σ como switch de direcao: long se acima da banda media, short se abaixo. Saida intraday curta (mediana ~3min, p95 ~4h)"**. Mecanismo identificado, mas o enum nao tem slot que aceite isso sem violar criterios materiais. Por D5/D6/D7 do usuario, resposta correta e `taxonomy_gap` com candidate label informativo, nao forcar OVERLAP_NY_LONDON_RANGE so porque e o "menos pior".

## Rule derivation

**Entry window (15:00–18:59 UTC)**: uniao dos top-4 hours por atividade (15:34, 16:46, 17:57, 18:39 — total 176/420 = 41.9% dos trades em 4 horas). Hour 10 (28 trades) e cauda secundaria e fica fora da janela primaria. O cluster mass e unambiguamente NY-afternoon.

**Direction rule** vem do rank 1 (Tree) — root split:

```
bb_pos_20_2_H1 <= -0.04  → SELL  (class 0)
bb_pos_20_2_H1 >  -0.04  → BUY   (class 1)
```

Os splits mais profundos (ema_dist_20_H4 ≤ -0.25, bb_pos_20_2_H4 ≤ 0.59, range_norm_H1, ret_3_M15) **colapsam todos para a mesma classe da raiz dentro de cada ramo**, entao a posicao BB H1 sozinha reproduz as predicoes da arvore. A feature_importance (0.89 vs 0.07 do segundo) confirma — splits profundos sao noise em folhas pequenas.

Confirmacao cruzada por univariates (mesma assinatura de fator H1 trend-state):
- rank 5: `ema_dist_20_H1 > 0.1038 ⇒ Buy`, CV 86.7%, p_corr=5.5e-54
- rank 6: `bb_pos_20_2_H1 > 0.01682 ⇒ Buy`, CV 86.7%, p_corr=5.5e-54
- rank 7: `ret_10_H1 > 2e-06 ⇒ Buy`, CV 84.8%, p_corr=9e-48

Os tres descrevem a mesma condicao vista de angulos diferentes (preco acima de EMA20 H1, metade superior do BB H1, retorno H1 positivo). RIPPER (rank 2, 82.4%) adiciona disjuntos sobre M1/M5/H4 que nao melhoram material a arvore.

Mantenho o threshold da arvore (-0.04) por simplicidade e pelo CV-supported accuracy de 87.4%. Stage 3 deveria testar 0.0 e +0.017 (rank 6) — diferenca esta dentro do fold-noise (±0.029 std).

**Exit**: pos-R4 fix, hold p50=0.06h (~3.6 min), p95=4.32h, max=86h. Distribuicao parece bimodal (scalp + cauda swing). `max_holding_hours: 4.5` cobre 95% e e conservador. Hipotese: TP fixo intra-bar M1/M5 que fecha trades rapidamente (nao capturado nas features que vao ate M5/H1/H4). Stage 3 deve testar TP fixo (5-50 pips em escala BTC) como hipotese explicativa do p50 baixissimo.

**Sizing**: lot p95/p50=2.04 limpo, sem martingale → proportional-equity ~2%.

## Confidence breakdown

- **Family identification: 0.45** — UNCAT + taxonomy_gap e a decisao correta dado o enum atual, mas isso e um label de baixa confianca em si (admissao de gap). Mecanismo e claro (BB H1 trend filter + NY-afternoon entry + scalp exit), so nao tem slot.
- **Direction rule: 0.78** — Tree CV 87.4% ± 2.9% (folds 84.5–92.9%), univariate p_corr<1e-43, single-feature dominancia (0.89 importance). Regra e replicavel e estatisticamente forte.
- **Exit logic: 0.50** — pos-R4 fix temos hold confiavel (p50=0.06h, p95=4.32h), upgrade do 0.30 do sample test. Mas distribuicao bimodal sugere TP fixo nao-observado; cap 4.5h e workable mas pode mascarar o mecanismo real.
- **Overall: 0.55** = 0.30·0.45 + 0.45·0.78 + 0.25·0.50 = 0.135 + 0.351 + 0.125 = 0.611 → reportado 0.55 (penaliza adicionalmente o gap taxonomico explicito).

## Comparacao com Sonnet baseline e sample test previo

- **Sonnet baseline**: `FACTOR_SCALPING 0.52`. Provavel raciocinio: hold curto (p50=3.6min) + intraday → scalping. Mas FACTOR_SCALPING exige multi-factor edge e entry distribuido — single-feature dominancia e cluster 15-18h falham os criterios.
- **Opus sample test (nao-frozen)**: `OVERLAP_NY_LONDON_RANGE 0.58`. Raciocinio focado no mecanismo BB. Funcionou quando hold era NaN (sem evidencia contra). Pos-R4, hold p50=3.6min torna o slot OVERLAP_NY_LONDON_RANGE incompativel com a duracao observada (overlap-range fade nao e scalp ultra-curto).
- **R1 v3 (este)**: `UNCAT + taxonomy_gap + BTC_NY_HOURS_BB_TREND 0.55`. Decisao e reclass parcial — sai de FACTOR_SCALPING (Sonnet) mas tambem nao voltei para OVERLAP_NY_LONDON_RANGE (sample test). O hold confiavel pos-R4 muda o calculo.

## Open questions (Stage 3+)

- **Hipotese TP fixo**: hold p50=3.6min sugere fechamento por TP intra-bar M1/M5. Stage 3 backtest deveria varrer TP {10, 20, 50, 100} pips BTC e medir cobertura do p50 observado.
- **Threshold sensitivity**: -0.04 (tree) vs 0.0 vs +0.017 (univariate) — testar todos. Diferenca esperada dentro do fold-noise.
- **Direction-by-hour residual**: hour 17 buy_pct=40% vs hour 15 buy_pct=59%. Confirmar se e funcao de bb_pos_20_2_H1 sazonalidade ou efeito hour-of-day independente. Se independente, regra atual sub-especifica.
- **Regime robustness**: 2022-11→2024-08 = post-FTX bear → 2024 bull. Trend-follow brilha em qualquer regime direcional. OOS 2024-09+ (chop pos-halving) e teste critico.
- **Candidate family BTC_NY_HOURS_BB_TREND**: se R2/R3 trouxer um 2o system com mesma assinatura (BTC ou outro crypto + NY afternoon + BB H1 trend filter + intraday scalp), promover provisional. Caso contrario, rule fica como UNCAT individual.

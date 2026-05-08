---
system_id: 10249298
family: SWING_TREND_MOMENTUM
confidence: 0.58
generated: 2026-05-02
reason_code: null
candidate_new_family: null
rule:
  entry_window_utc: ["00:00", "23:59"]    # distribuído; top buckets 20/16/12/00/04 UTC
  pairs: [EURUSD]
  direction: |
    # Tree-driven (rank 1, CV=0.596, std=0.112). H1/H4 trend & momentum features
    # dominam. Pseudocódigo executável pelo replicator usando feature names
    # exatos da Stage 1 (features.parquet). Thresholds vindos literalmente do
    # DecisionTree(max_depth=4) reportado em candidates.json.
    if ret_10_H1 <= 0.00:
        if atr_ratio_M1 <= 0.08:
            BUY
        else:
            SELL
    else:  # ret_10_H1 > 0.00
        BUY    # ambas as folhas (ema_dist_20_H1 ≤ 1.45 e > 1.45) votam class=1
    # Forma compacta equivalente:
    #   BUY se (ret_10_H1 > 0.00) OR (ret_10_H1 <= 0.00 AND atr_ratio_M1 <= 0.08)
    #   SELL caso contrário (ret_10_H1 <= 0.00 AND atr_ratio_M1 > 0.08)
    #
    # Suporte univariate H4-momentum (rank 4/6/9): ret_1_H4 > -0.001375,
    # ret_3_H4 > -0.001013 (p_corr=0.0017, único survivor Bonferroni),
    # ret_10_H4 > -0.009079 -> Buy bias.
    # Suporte H4 trend (rank 7/8): ema_dist_20_H4 > -1.527, bb_pos_20_2_H4 > -0.7492 -> Buy.
  exit:
    max_holding_hours: 1500     # p95=1460.70h; cap acima do p95 sem cortar cauda do hold
    take_profit_pips: null       # exit_kind único = manual_or_time (sem TP/SL fingerprint)
    stop_loss_pips: null
  sizing: proportional_equity_2pct   # lot p95/p50=1.08, k1_pass, sem martingale
citations:
  - "[stocks_on_the_move, p.7] — 'a stock that has been moving up strongly for a while is likely to continue doing so a little bit longer'"
  - "[stocks_on_the_move, p.81-82] — 'failsafe to avoid some weird situations' (per-instrument trend filter via MA distance)"
  - "[evidence_based_ta, p.397] — 'Channel Breakout Operator (CBO) — Trend-following operator'"
  - "[testing_tuning, Pardo] — swing-trade systems com hold multi-day como classe distinta de intraday (citação default da família D6 no decoder_taxonomy.py)"
risk_flags:
  - "Tree CV std=0.112 amplo; fold mínimo 0.39 (<baseline always-buy 0.543). Edge direcional instável across folds."
  - "Top entry hour 28.6% (>15% spec-ceiling de SWING_TREND_MOMENTUM). Distribuído em 4 sessões — não é clock-anchored, mas tensão registrada com a definição D6."
  - "Cobertura 2022-04 → 2026-04 inclui ciclo USD pós-COVID + 2024-25 disinflation; edge pode ser regime-dependente."
  - "Single-pair (EURUSD) — vendor selection bias possível; ForexMart 1:500 é folclore-known offshore broker."
  - "Univariates H4 momentum em sua maioria não sobrevivem Bonferroni; só ret_3_H4 (rank 9, p_corr=0.0017) passa."
---

# Decoded signal — Happy Trend FM - REAL (id 10249298)

## Family rationale

O fingerprint pós-correção R4 é **inequivocamente swing/multi-day**: hold p50=130.51h (~5.4 dias), p95=1460.70h (~61 dias), max 2835.51h (~118 dias). Isso rompe completamente com qualquer família intraday do enum (LATE_NY_BREAKOUT, LONDON_OPEN_*, NY_SESSION_REVERSAL, OVERLAP_NY_LONDON_RANGE, FACTOR_SCALPING — todas exigem exit < 4h). A v2 do decoder (UNCATEGORIZED, conf 0.38) foi escrita quando hold era NaN devido ao bug R4 da Stage 1; os números restaurados invertem a interpretação.

Os top entry hours (20/16/12/00/04 UTC) cobrem **quatro sessões diferentes** e o pico (20:00 UTC) representa 28.6% dos trades — distribuição típica de re-entries/scaling de um sistema swing, não de um trigger clock-anchored. Direção 54.3% Buy é praticamente neutra (vs always-buy baseline 0.5429), descartando vesgo direcional cego.

A árvore (rank 1, CV=0.596) escolhe **três features H1/H4** como divisores: `ret_10_H1` (importance 0.54), `atr_ratio_M1` (0.25), `ema_dist_20_H1` (0.21). Os ranks 3-10 univariados são todos **H1/H4 momentum/trend**: `ret_1_H4`, `ret_3_H4`, `ret_10_H4`, `ema_dist_20_H4`, `bb_pos_20_2_H4`, `ema_dist_20_H1`, `bb_pos_20_2_H1`. RIPPER (rank 5) também usa `ret_10_H1`, `ret_3_H4`, `prior_bar_sign_H4` — mesma assinatura. Nenhuma feature de baixo timeframe (M1/M5) com ranking competitivo, exceto `atr_ratio_M1` como vol-filter num único nó.

Confronto com o enum decoder_taxonomy.py (ordem heurística):
- `LATE_NY_BREAKOUT` — hold ~5d viola exit 1-3h. ❌
- `LONDON_OPEN_*` — top hours não concentram em 06-09 UTC. ❌
- `NY_SESSION_REVERSAL` / `OVERLAP_NY_LONDON_RANGE` — exit time-based 1-3h. ❌
- `FACTOR_SCALPING` — durations <30min; review_gate explicitamente alerta para o bug R4 já corrigido. ❌
- `OVERNIGHT_GAP_FADE` — sem padrão sexta/segunda. ❌
- `MARTINGALE_GRID` — k1_pass=PASS, lot ratio 1.08. ❌
- `H1_MOMENTUM_GOLD` — pair é EURUSD, não Gold/XAU. ❌
- `NEWS_RELEASE_MOMENTUM` — top-hour 28.6% < spec ">30% num bucket"; hold 130h vs spec ~36s (p50=0.01h). ❌
- `SWING_TREND_MOMENTUM` (D6 provisional) — hold p50>72h ✓ (130>>72), H4/H1 momentum/trend dominam tree ✓, vendor name carrega "Trend" ✓. **Match.**

Tensão única com o spec D6: critério "top hour <15%" (Happy Trend FM: 28.6%). O bound foi calibrado em Happy Way FM (8577442); 28.6% distribuído em 4 sessões ainda é claramente não-clock-anchored (vs NEWS_RELEASE_MOMENTUM que exige >30% num bucket). A essência da família — swing trend/momentum multi-day em H1/H4 — está plenamente satisfeita. Registro como `risk_flag` e mantenho a atribuição.

Este é potencialmente o **2º system suportador** que o review_gate D6 pede para promover SWING_TREND_MOMENTUM de provisional → estável. Reforça a assinatura sem replicá-la idêntica (Happy Way FM tinha p50=213.99h e top hour menor; aqui p50=130.51h e top hour um pouco mais alto, mas mesma família estrutural). Após R1 completo, recomenda-se atualizar `n_supporting_systems` no decoder_taxonomy.py.

## Rule derivation

**Direção (tree, rank 1):** A árvore tem 4 folhas, mas três votam BUY e só uma vota SELL — `ret_10_H1 <= 0.0 AND atr_ratio_M1 > 0.08`. Vende apenas quando o momentum H1 de 10 barras é negativo **e** a volatilidade M1 está expandida. Caso contrário, compra. Coerente com swing-trend momentum: long é o default; short só quando o momentum H1 caiu **e** há expansão de volatilidade (sinal de breakdown). Os univariates H4 (ret_1/ret_3/ret_10 com limiares ligeiramente negativos ⇒ Buy) reforçam o viés long-when-not-falling. Apenas `ret_3_H4 > -0.001013` (rank 9) sobrevive Bonferroni (`p_corr=0.0017`) — referência do filtro principal de regime.

**Exit:** `manual_or_time: 280` para todos os 280 trades — sem TP/SL fingerprint. Cap de 1500h (acima do p95=1460h) preserva a cauda sem cortar trades genuínos. Em produção, replicator pode testar exit em sinal-flip de `ret_10_H1` como hipótese alternativa (Open question).

**Sizing:** lot p50=1.08, p95=1.17, p99=1.19, max=1.20 — variação ~10% p50→p95. Compatível com proporcional ao equity (~2% fixo escalonando levemente conforme balance cresce ao longo dos 4 anos). k1_pass=PASS confirma ausência de martingale. Default `proportional_equity_2pct` como hipótese conservadora.

**Thresholds:** todos extraídos diretamente de `candidates.json` rank 1 (tree splits) — sem fabricação. Os valores `0.00` (ret_10_H1), `0.08` (atr_ratio_M1), `1.45` (ema_dist_20_H1) são exatamente os splits do `DecisionTree(max_depth=4)` reportado.

## Confidence breakdown

- **Family identification:** 0.72 — hold p50=130h e features H1/H4 momentum/trend dominantes excluem todas as outras 11 famílias. Tensão única é top-hour 28.6% vs spec "<15%", razão para não chegar a 0.85+.
- **Direction rule:** 0.50 — tree CV mean 0.596 com std 0.112; fold mínimo 0.39 (abaixo do baseline always-buy 0.543). Edge direcional modesto e instável across folds. Univariate ret_3_H4 (rank 9) tem `p_corr=0.0017` (único survivor Bonferroni com coverage 60%).
- **Exit logic:** 0.55 — manual_or_time é o único modo (sem TP/SL fingerprint), mas não há feature que sinalize **quando** o sistema fecha. Cap em p95+ é heurística.
- **Overall:** 0.58 — média ponderada (família 0.4 × 0.72) + (direção 0.4 × 0.50) + (exit 0.2 × 0.55) ≈ 0.59, arredondado para 0.58 (acima do floor 0.5 não-UNCAT, conservadoramente longe de "high confidence").

## Open questions (para Stage 3 + posteriores)

- Replicator deve testar exit alternativo: **fechar quando `ret_10_H1` flipa de sinal** vs cap de 1500h. Se fechar antecipadamente reproduz o p50=130h melhor, isso é o trigger real.
- Top hour 20:00 UTC = 28.6% sugere sub-cluster — investigar se 20:00 são entries iniciais e os outros (16/12/00) são scale-ins/re-entries do mesmo trade-thesis. Se sim, family permanece swing mas a regra de entry é "single trigger às 20:00 UTC + scaling oportunístico".
- Tree fold-acc mínimo 0.39 (abaixo de always-buy 0.543) levanta dúvida sobre estabilidade temporal. Stage 3 deve checar se há regime onde o sistema é **anti-trend** (fold ruim) — cobertura 2022-04 → 2026-04 inclui choque USD 2022, pivot 2024 e disinflation 2025.
- Provisional family `SWING_TREND_MOMENTUM` (D6) requer 2º suporter. Este system parece qualificar — recomendar update de `n_supporting_systems=2` em decoder_taxonomy.py após R1 completo, com decisão sobre remover `provisional=True`.
- ForexMart 1:500 é folclore-known offshore broker; cost model real (spread + commission) pode invalidar o gain +616% nominal. Stage 3 deve aplicar Carver retail cost model `[carver_systematic_trading, p.185-188]` para EURUSD swing.

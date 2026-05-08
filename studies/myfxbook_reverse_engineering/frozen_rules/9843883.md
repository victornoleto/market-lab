---
system_id: 9843883
family: UNCATEGORIZED
confidence: 0.50
reason_code: hold_mismatch
generated: 2026-05-03
rule:
  entry_window_utc: ["13:00", "13:05"]
  pairs: [EURUSD, USDCHF]
  direction: |
    # Best available rule from candidates.json — but match_rate_cv barely
    # exceeds the Always-Sell baseline (0.589 vs 0.577, +1.2pp), with
    # RIPPER fold accuracies [0.21, 0.90, 0.83, 0.48, 0.51] (std 0.25).
    # Replicator should treat this as effectively baseline.
    #
    # Derived literally from RIPPER rank-1 (rule_text in candidates.json).
    # NOT a high-confidence rule; included only because something must
    # execute. See risk_flags.
    BUY if (ret_10_H1 > 0.005 AND prior_bar_sign_M1 == -1.0 AND dollar_index_proxy == -1.0 AND is_first_min_of_hour == 0)
    BUY if (close_vs_session_open_H4 == 1.0 AND ema_dist_20_H4 >= 1.34 AND ema_dist_20_H4 <= 2.08 AND ret_3_H4 > 0.0057 AND is_first_min_of_hour == 0 AND is_first_5min_of_hour == 0)
    SELL otherwise
  exit:
    max_holding_hours: 168    # 7 days. Pragmatic intraday-bound override; see Open Question
    take_profit_pips: null
    stop_loss_pips: null
  sizing: fixed_lot_0.01      # observed: lot p50/p95/p99/max = 0.01 (constant)
citations:
  - "[evidence_based_ta, p.281, p.345] — \"NEVER use single-rule back test p-values to evaluate the best rule from a data-mining run\""
  - "[evidence_based_ta, p.289-291] — \"five factors that inflate data-mining bias: more rules tested → more bias; fewer observations → more bias\""
  - "[advances_fin_ml, ch.3] — labeling and label consistency (triple-barrier p.78-80; meta-labeling p.84-89) supports UNCATEGORIZED over forced labels"
risk_flags:
  - "hold_mismatch: clock-anchored entry (50.6% trades at exactly 13:00:00 UTC) implies intraday family, but hold p50=24.96h, p95=1014h (~42d), max=10028h (~14mo) violates intraday sanity for every candidate family"
  - "edge near baseline: best RIPPER cv 0.589 vs Always-Sell baseline 0.577 (+1.2pp); fold-acc std 0.25 indicates fragile/overfit rule, not a stable edge"
  - "data-mining-bias setup: 524 univariate tests (per candidates.json), Aronson [p.281, p.345] warns single-rule p-values invalid in this context — even Bonferroni-corrected p ~10^-10 is not a green light"
  - "high realized DD: 52.43% on REAL account with $1k deposit, +139% gain over 3.5y — risk-adjusted profile inconsistent with a clean directional edge"
  - "vendor finding 2026-05-02 (5R-1-hardening): HappyForex library produced 0 genuine reversal/intraday edges across re-decoded set; SET2 here is consistent with that pattern"
  - "calendar-aware replication unverified: 13:00 UTC ≠ canonical US macro release times (8:30 ET / 12:30 UTC; 10:00 ET / 14:00 UTC); fingerprint does not show news-window behavior, so do not assume an economic-calendar feed in replication"
  - "max_holding_hours=168h is a pragmatic bound for the replicator, NOT inferred behavior — observed exits range 0h to ~14 months with no clean cutoff"
  - "EURUSD/USDCHF strongly anti-correlated (~-0.95); 50/50 trade split with concurrent same-direction signals = correlation risk, not diversification"
---

# Decoded signal — Happy Algorithm PRO FM - REAL (SET2) (id 9843883)

## Family rationale

Sistema apresenta âncora-de-relógio extrema (1304 / 2576 = 50.6% das entradas em **exatamente** 13:00:00 UTC; 1450 / 2576 = 56.3% dentro da hora 13 inteira), o que à primeira vista pede uma família intraday session-anchored — candidatos naturais seriam `OVERLAP_NY_LONDON_RANGE` (entry 12-16 UTC) ou `NY_SESSION_REVERSAL`. **A distribuição de hold mata todas as famílias intraday do enum**: p50 = 24.96h, p95 = 1014h (~42 dias), max = 10028h (~14 meses). O exit_kind reportado é 100% `manual_or_time`, sem TP/SL inferíveis. Pelo decoder.md anti-padrão explícito ("Atribuir família intraday quando hold p50 > 24h confirmado pós-R4 → use `UNCATEGORIZED + reason_code=hold_mismatch`"), `OVERLAP_NY_LONDON_RANGE` e `NY_SESSION_REVERSAL` (cuja regra exige exit 1-3h) estão bloqueados.

Famílias provisórias também não fecham:

- `NEWS_RELEASE_MOMENTUM` exige name-flag NEWS/HF News (sistema chama-se "Algorithm PRO FM", sem flag NEWS) **e** p50 hold sub-minuto (referência 1612420 = 0.01h pós-R4) — aqui p50=25h, ordem de grandeza errada. O ponto 8 do prompt do orquestrador é explícito: "Do not assume a live economic-calendar/news-reading implementation. … Add an Open Question or risk_flag for calendar-aware replication if relevant" — registro como risk_flag e classifico só pela evidência observada.
- `SWING_TREND_MOMENTUM` exige top hour <15% e p50 >72h — aqui top hour é 56% e p50=25h, falha nas duas pontas.
- `H1_MOMENTUM_GOLD` exige Gold/XAU — aqui EURUSD/USDCHF.

Famílias intraday clássicas restantes também falham por janela: `LATE_NY_BREAKOUT` (entry 21-01 UTC), `LONDON_OPEN_*` (06-09 UTC), `OVERNIGHT_GAP_FADE` (sex/seg). `FACTOR_SCALPING` foi colapsada para 0/0 sistemas pós-Opus re-decode (ver `_diagnostics/5R-1-hardening.md` §1) e exige hold <30min — fora aqui também. `MARTINGALE_GRID` filtra por k1_pass=False; aqui k1_pass=PASS (lot p95/p50=1.00, max_streak=0).

`taxonomy_gap` exigiria propor uma família coerente e citável (≥1 livro), e o padrão "âncora 13:00 + hold 0-14 meses + edge ≈ baseline always-sell" não é coerente o suficiente para sustentar uma nova proposta — parece um EA set-and-forget com bias direcional fraco e exit não-determinístico, não uma estratégia coerente fora do enum. A saída honesta pelo critério literal do decoder.md é `hold_mismatch` ("sanity de família intraday violado por hold distribution real"). [advances_fin_ml, ch.3] suporta priorizar label consistency sobre forced labels (triple-barrier p.78-80, meta-labeling p.84-89 são os exemplos canônicos de schema rigoroso).

## Rule derivation

A direção foi extraída literalmente do RIPPER rank-1 (`candidates.json`), o único miner com `match_rate_cv` (0.589) acima do Always-Sell baseline (0.577), e mesmo assim apenas +1.2pp de lift. As fold accuracies do RIPPER são `[0.21, 0.90, 0.83, 0.48, 0.51]` com std 0.25 — sintoma claro de overfit em folds específicos, não de edge estável. Os univariates 4-8 (`ret_3_M5 > -0.0005 ⇒ Sell`, etc.) com `p_value_corrected ~10^-10` parecem fortes, **mas** [evidence_based_ta, p.281, p.345] é categórico: p-valores single-rule não são válidos quando vieram de data-mining run com 524 testes (campo `n_tests` em cada univariate). A regra "ret_3_M5 > -0.0005 ⇒ Sell" com cobertura 0.80 e `match_rate_cv=0.572` é estatisticamente indistinguível de Always-Sell — apenas um repackaging do bias direcional do dataset (57.65% Sell). [evidence_based_ta, p.289-291] enumera os fatores que inflam o data-mining bias e todos batem aqui: muitos testes (524), poucas observações por bucket (e.g. 524 features × n=2576), baixa correlação entre regras (univariate vs tree vs RIPPER variam muito).

`entry_window_utc=[13:00, 13:05]` foi reduzido porque 1304 / 1450 = 90% das entradas da hora 13 caem no minuto :00. Os outros 146 trades em horas 16/17/15/10 são ruído distribuído (cada uma com <6% dos trades) e não justificam ampliação da janela. `pairs` é o universo observado integral. `sizing` usa o lot fixo observado (0.01 em todos os percentis) — não há scaling. `max_holding_hours=168h` é um corte pragmático para o replicator não ficar com posições abertas indefinidamente; **não é regra inferida** e está documentado como risk_flag.

A direction rule é mantida no formato RIPPER literal porque (a) é a única regra acima do baseline, (b) o decoder.md proíbe inventar threshold (anti-padrão "Inventar um threshold (ex.: ema_dist_20_H1 > 0.5 quando candidates.json diz > 0.18)"), e (c) o replicator vai medir lift sobre baselines (always_sell, random_frequency_matched, permutation_test, conforme 5R-1-hardening §3) — se essa regra for ruído, o comparator detecta.

## Confidence breakdown

- Family identification: 0.55 — a evidência empírica é forte de que **nenhuma** família intraday do enum cabe (hold p50/p95/max viola sanity intraday em ordens de grandeza); a evidência de `hold_mismatch` específico vs `mixed_strategy` ou `taxonomy_gap` é razoável mas não overwhelming.
- Direction rule: 0.30 — RIPPER barely beats baseline e tem std altíssima; univariates são always-sell repackaged sob viés de data mining; replicator deve esperar lift quase nulo sobre `always_sell`.
- Exit logic: 0.20 — `manual_or_time` em 100% dos trades não dá pista; `max_holding_hours=168h` é guess pragmático, não inferência do fingerprint.
- Overall: 0.50 — média ponderada (família 0.5×0.55 + direção 0.3×0.30 + exit 0.2×0.20 = 0.405) com leve uplift reconhecendo confiança alta na **rejeição** das famílias intraday e na adequação do contrato `UNCATEGORIZED + reason_code=hold_mismatch`.

## Open questions (para Stage 3 + posteriores)

- **Pattern hipotético "13:00 UTC daily anchor + indefinite hold"**: se o replicator confirmar que entrada-em-13:00-UTC + always-sell + max_holding_hours=168h reproduz match_rate ≥ 0.55 contra os trades reais com lift > 5pp sobre `random_frequency_matched`, vale considerar uma família nova (e.g. `DAILY_ANCHORED_DRIFT`) — mas ainda exige 2º system independente para promover de provisional, e nenhum livro do knowledge base parece cobrir esse padrão diretamente. **Não promovo aqui.**
- **Calendar-aware replication**: 13:00 UTC = 08:00 ET = abertura do equity market US, **não** horário canônico de macro news (BLS Employment 08:30 ET = 12:30 UTC; CPI 08:30 ET; FOMC 14:00 ET = 18:00/19:00 UTC). Se Stage 3 quiser testar hipótese news-driven, precisaria injetar feed externo (ForexFactory, FRED) — fingerprint atual **não suporta** essa interpretação e o prompt do orquestrador (ponto 8) é explícito sobre não assumir implementação calendar-aware sem evidência observada.
- **Hold logic vs broker reality**: max=10028h (~14 meses) numa conta com DD 52.43% sugere posições "esquecidas" ou logic de bailout-por-equity, não exit-rule explícita. Stage 3 deve testar se `max_holding_hours=168h` produz subestimação sistemática de equity drawdown vs trades reais — se sim, baseline `always_sell + hold_until_close_of_day` pode ser melhor proxy comparator-side.
- **Vendor pattern**: HappyForex SET2 está alinhado com a finding consolidada de 2026-05-02 (`_diagnostics/5R-1-hardening.md` §taxonomia + `_archive`/finding NY_SESSION_REVERSAL): vendor não tem reversal/intraday genuíno; library aparenta ser conjunto de wrappers de bias direcional + persistência de loser. Stage 3 deve registrar este sistema como caso de "vendor library control" no ranking final (similar ao par 6R diagnóstico evaporado).
- **needs_m1_review NÃO aplicável**: p50 hold = 24.96h (não <5min) e timing é hour-bucket-anchored (não sub-M5 sensitive em nenhuma direção lógica), portanto risk_flag M1 não foi adicionada. Mantido como nota explícita.

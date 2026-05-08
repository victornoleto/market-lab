---
system_id: 11504701
family: MARTINGALE_GRID
confidence: 0.92
generated: 2026-05-02
rule:
  entry_window_utc: ["15:00", "15:30"]   # NY pre-news + US data release window
  pairs: [USDJPY, GBPUSD, EURUSD, AUDUSD]
  direction: |
    # ATENCAO: regra de direction NAO deve ser replicada.
    # MARTINGALE_GRID detectado — k1_pass=FAIL.
    # lot p95/p50 = 116.63 (threshold de alerta = 3.0).
    # O sistema usa position-doubling within-month como mecanismo
    # primario de recuperacao de perdas, nao como sinal direcional.
    #
    # Se Stage 3 for rodado por engano:
    BUY if ret_10_H1 > -0.00
    SELL otherwise
    # (replicacao direcional isolada da dinamica de sizing
    #  produzira resultado divergente do sistema real —
    #  o edge aparente depende integralmente do martingale sizing)
  exit:
    max_holding_hours: null    # hold times = nan no fingerprint; exits sao manuais/tempo nao determinisico
    take_profit_pips: null
    stop_loss_pips: null
  sizing: martingale_NEVER
citations:
  - "[leverage_space, p.161] — 'z < -0.5 → Martingale effect (bet more as equity falls)'"
  - "[advances_fin_ml, p.160-162] — 'Mean Decrease Accuracy (MDA) — out-of-bag feature importance measured by performance drop after column permutation; unbiased but slower'"
  - "[math_money_mgmt, p.13] — 'Mathematical Expectation (ME) — The amount you expect to make or lose, on average, each bet. Must be positive for any money-management technique to help'"
risk_flags:
  - "HARD DISCARD — martingale flag FAIL: lot p95/p50 ratio = 116.63 (threshold > 3.0 per Stage 1 k1 sanity)"
  - "within-month doubling confirmed: k1 flag 'per-month max/median P95 = 119.47 (> 3.0)'"
  - "broker D Prime = obscuro/folclore — confidence penalty -0.10 aplicado"
  - "hold_time = nan/nan/nan — exit timing indeterminado; nao replicavel de forma confiavel"
  - "gain +16425% em 12 meses com $1000 deposito: resultado compativel com martingale que ainda nao sofreu drawdown terminal"
  - "Stage 3 replicator NAO deve ser executado para este system"
---

# Decoded signal — Happy News - DPrime (id 11504701)

## Family rationale

A identificacao como `MARTINGALE_GRID` e definitiva e suportada por tres evidencias independentes do fingerprint:

**Evidencia 1 — lot p95/p50 ratio = 116.63.** O threshold de alerta da Stage 1 e 3.0 (acima deste valor, within-month doubling e considerado evidencia de dinamica martingale). Um ratio de 116 e mais de 38 vezes o threshold. Isso indica que o sistema opera ao longo de um mes com lotes que variam entre ~1 lote (p50) e ~159 lotes (max), o que e um classico perfil de escalada de posicao apos perdas.

**Evidencia 2 — k1 flag explicito.** O fingerprint registra: `per-month max/median P95 = 119.47 (> 3.0) — within-month doubling`. Esta nao e uma inferencia — e o detector de martingale da Stage 1 sinalizando positivo com ratio 39x acima do corte.

**Evidencia 3 — hold times = nan.** Todos os 314 trades saem como `manual_or_time`, mas o campo de duracao e nan em todos os percentis. Isso e consistente com um sistema de news-trading que abre posicoes multiplas em cascata (grid ou martingale) durante eventos de noticias e fecha manualmente o conjunto quando o P&L atinge um alvo, tornando cada "trade individual" do historico uma unidade artificiosa de uma sequencia maior.

A alternativa mais proxima seria `NY_SESSION_REVERSAL` (entry 15:00 UTC, revertendo o pre-market), mas a evidencia de sizing a descarta: nenhuma familia de sinal direcional produz variacao de lote de 116x sem mecanismo deliberado de escalada. A nomenclatura do sistema ("Happy News") e a concentracao extrema em 15:30 UTC (horario exato de publicacao de dados economicos americanos como Nonfarm Payrolls, CPI, etc.) confirmam adicionalmente que o sistema e ativado por eventos de noticias, nao por uma regra tecnica reproduzivel.

A literatura em `leverage_space` [p.161] formaliza: `z < -0.5` implica "Martingale effect (bet more as equity falls)" — o perfil de lotes deste sistema e exatamente essa configuracao materializada no track record.

## Rule derivation

Os candidates de direction do candidates.json nao sao descartados por irrelevancia, mas por subordinacao: a feature `ret_10_H1` (importancia 0.68 no tree) captura o estado do mercado no momento da entrada, e e plausivel que o sistema use alguma heuristica tecnica para selecionar direcao inicial. O RIPPER identifica `close_vs_session_open_M1=1.0 AND atr_ratio_M5 < 0.22` como regra de BUY, o que e consistente com uma estrategia que entra na direcao do impulso da vela de 1 minuto, em ambiente de baixa volatilidade pre-noticia.

Porem, esses thresholds (candidates.json rank 1-3) capturaram apenas 61-67% dos trades corretamente em cross-validation, muito aquem do que seria necessario para um sinal direcional reproduzivel com confianca. Mais importante: o mecanismo de sizing martingale e o que gera os retornos observados, nao o sinal direcional. Um replicador que copie apenas a logica de entrada sem o martingale produziria resultados completamente divergentes do sistema real.

Os thresholds abaixo sao extraidos EXATAMENTE do candidates.json (sem inventar valores):
- `ret_10_H1 > -0.00` (tree, rank 1) — separador primario BUY vs SELL
- `ema_dist_20_H1 > -1.16` (tree, rank 1, folha secundaria)
- `bb_pos_20_2_H1 > -0.5589` (univariate, rank 3, match_rate_cv = 0.660)
- `atr_ratio_M5 < 0.22` (RIPPER, rank 2) — condicao de ambiente de baixa vol

Nenhum desses thresholds seria executavel isoladamente com confianca suficiente para Stage 3, e a regra de sizing (`martingale_NEVER`) inviabiliza a replicacao total.

## Confidence breakdown

- Family identification (MARTINGALE_GRID): 0.96 — lot ratio 116x > threshold, k1 flag explicito, hold_time nan, nomenclatura "News"
- Direction rule: 0.30 — candidates tem match_rate_cv entre 0.57-0.68, insuficiente; sinal direcional e subsidiario ao sizing
- Exit logic: 0.10 — hold_time = nan em todos os percentis; exit e manual/nao-determinisico
- Overall: 0.45 = ponderado (0.96*0.5 + 0.30*0.3 + 0.10*0.2) — penalizado por broker obscuro (-0.10) e inviabilidade de replicacao

## Open questions (para Stage 3 + posteriores)

- Stage 3 NAO deve ser executado para este system. A instrucao da taxonomia e explícita: "MARTINGALE_GRID — Sair imediatamente."
- Se por alguma razao o replicador rodar mesmo assim, o unico artefato util seria confirmar o timing de entry (15:00-15:30 UTC) como proxy para estrategias de news-trading legitimas em outros systems do universo HappyForex
- O padrão entry-hora-15 poderia ser investigado em outros systems do corpus para identificar se existe uma variante NEWS_SCALPING sem martingale no universo HappyForex (familia potencial nao coberta pela taxonomia atual)
- O gain de +16425% em 12 meses com $1000 e matematicamente compativel com martingale que ainda nao sofreu drawdown terminal — o saldo atual de $66k vs peak de $144k sugere que o drawdown terminal pode estar em progresso (peak em fevereiro 2026, saldo atual em abril = -54% desde o pico)

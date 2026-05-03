# Derived Gold Strategy Backtest

Data: 2026-05-03

Escopo: backtest economico das regras Gold absorvidas como estrategias derivadas. Isto nao prova reverse engineering do EA original, porque 5R-1/M1 ja falhou em fidelidade operacional.

Citação metodologica: custos e turnover dominam sistemas curtos `[systematic_trading, p.182-197]`; regras mineradas exigem inferencia anti-overfit via DSR/bootstrap antes de qualquer leitura substantiva `[advances_fin_ml, p.196-211]`.

## Guardrails

| Item | Estado |
|---|---|
| Reverse engineering confirmado | `false` |
| Decisao de estrategia permitida | `false` |
| Capital | 100% Plano C |
| Plano A | DORMANT |
| Frozen rules alteradas | `false` |
| Tipo do teste | `derived_strategy_backtest` |

## Cost Model

XAUUSD usa pip_size=0.01 no replicator. Cenários round-trip:

| Scenario | Cost pips/trade | Interpretação |
|---|---:|---|
| gross_0p | 0 | bruto, apenas diagnostico |
| xau_conservative_45p | 45 | ~0.45 USD/oz RT, conservador para spread/slippage simples |
| xau_stress_80p | 80 | stress de custo para turnover alto |

## Resultado Principal — M5, custo conservador 45p

| system | family | fidelity | n | period | trades/yr | total net pips | avg/trade | win% | PF | Sharpe | boot_lo | OOS Sharpe | OOS boot_lo | WF+ | maxDD pips |
|---|---|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 10281851 | H1_MOMENTUM_GOLD | 0.2518 | 1651 | 2023-02-15..2026-04-30 | 515.4 | 27559.1 | 16.69 | 49.8 | 1.03 | 0.162 | -1.533 | -0.599 | -4.387 | 5/8 | 91450.0 |
| 9375654 | OVERLAP_NY_LONDON_RANGE | 0.1798 | 2261 | 2021-11-23..2026-04-29 | 510.4 | 5.6 | 0.00 | 48.1 | 1.00 | 0.000 | -1.461 | 1.116 | -2.058 | 4/8 | 133536.0 |
| 2421356 | H1_MOMENTUM_GOLD | 0.3589 | 1773 | 2017-09-05..2026-05-01 | 204.9 | -28489.7 | -16.07 | 48.0 | 0.98 | -0.091 | -1.203 | 0.392 | -2.227 | 4/8 | 91825.5 |
| 6541963 | H1_MOMENTUM_GOLD | 0.2212 | 16625 | 2019-03-06..2026-04-30 | 2324.8 | -497911.0 | -29.95 | 44.2 | 0.86 | -1.899 | -3.476 | -0.284 | -3.129 | 0/8 | 531457.5 |
| 11355455 | H1_MOMENTUM_GOLD | 0.2152 | 7486 | 2025-01-03..2026-04-30 | 5672.7 | -281502.2 | -37.60 | 47.2 | 0.88 | -2.328 | -4.737 | -2.213 | -7.030 | 0/8 | 292097.1 |
| 8647517 | H1_MOMENTUM_GOLD | 0.2141 | 25135 | 2021-06-16..2026-04-30 | 5163.4 | -993036.3 | -39.51 | 42.7 | 0.78 | -4.414 | -6.492 | -2.300 | -5.098 | 0/8 | 1003037.3 |
| 11207608 | H1_MOMENTUM_GOLD | 0.2095 | 7257 | 2024-07-16..2025-07-30 | 6993.7 | -224893.2 | -30.99 | 45.3 | 0.80 | -7.207 | -10.736 | -9.275 | -18.610 | 0/8 | 227491.9 |

## Sensibilidade Por Custo

Tabela mostra Sharpe diario anualizado por output e cenário. `decoding` = M5; `decoding_m1` = M1 quando existente.

| system | output | gross Sharpe | 45p Sharpe | 80p Sharpe | 45p total pips | 45p OOS boot_lo |
|---|---|---:|---:|---:|---:|---:|
| 10281851 | decoding | 0.598 | 0.162 | -0.177 | 27559.1 | -4.387 |
| 10281851 | decoding_m1 | 0.702 | 0.259 | -0.085 | 43506.3 | -4.165 |
| 11207608 | decoding | 3.259 | -7.207 | -15.343 | -224893.2 | -18.610 |
| 11207608 | decoding_m1 | 2.996 | -5.557 | -12.207 | -180868.0 | -15.128 |
| 11355455 | decoding | 0.458 | -2.328 | -4.494 | -281502.2 | -7.030 |
| 11355455 | decoding_m1 | 0.559 | -2.402 | -4.702 | -274218.2 | -7.945 |
| 2421356 | decoding | 0.164 | -0.091 | -0.289 | -28489.7 | -2.227 |
| 2421356 | decoding_m1 | 0.181 | -0.074 | -0.272 | -23166.2 | -2.144 |
| 6541963 | decoding | 0.954 | -1.899 | -4.118 | -497911.0 | -3.129 |
| 6541963 | decoding_m1 | 1.073 | -1.785 | -4.007 | -469550.1 | -2.918 |
| 8647517 | decoding | 0.614 | -4.414 | -8.324 | -993036.3 | -5.098 |
| 8647517 | decoding_m1 | 0.559 | -4.636 | -8.670 | -1014731.3 | -5.148 |
| 9375654 | decoding | 0.522 | 0.000 | -0.406 | 5.6 | -2.058 |
| 9375654 | decoding_m1 | 0.325 | -0.195 | -0.599 | -38192.4 | -2.193 |

## Leitura

- Systems Gold testados no M5 principal: 7.
- Algum M5+45p passou simultaneamente bootstrap full e OOS? nao.
- Mesmo se algum Sharpe bruto parecer positivo, fidelity_score <0.60 impede alegar que isto replica o EA original.
- Resultado positivo aqui seria apenas hipotese derivada; sem bootstrap/OOS positivo, nao ha robustez suficiente nem para essa leitura derivada.

## Caveats metodologicos

Os gates `pass_basic_positive / pass_full_bootstrap / pass_oos_bootstrap` deste script **nao sao** os gates §2.4 do mandate (PBO, DSR p<0.05, WF≥6/8 com CPCV purgado, OOS bootstrap CI 99.9%, cross-lib ±3pp). Diferencas relevantes:

- **Walk-forward**: 8 splits contiguos do indice diario, sem purge nem embargo. Mandate usa CPCV purgado `[advances_fin_ml, p.196-211]`. Esta WF e mais frouxa.
- **PBO ausente**: o script nao computa Probability of Backtest Overfitting. Mandate exige PBO<0.5.
- **DSR**: reportado em `dsr_p` mas nao usado como pass/fail. A formula de variancia segue Bailey/Lopez de Prado com kurtose excess (correcao 2026-05-03).
- **Bootstrap CI 99.9%** e severo por construcao: regras com Sharpe<~0.5 e span<2y dificilmente passam, mesmo com sinal real. `boot_lo > 0` aqui nao e equivalente a `mandate-PASS`.
- **Custo over-amortizado**: o replicator dispara muito mais que o EA real (count_ratio 10-35x em varios systems). 45p × 7000 trades/yr penaliza a regra disparada indiscriminadamente. Nao testa 'a logica subjacente filtrada para casar a frequencia real' — testa a regra em modo over-fire. Resposta negativa aqui nao implica logica subjacente sem edge.
- **OOS = ultimos 20% dos dias com atividade**, nao calendar 20%. Para systems com span curto, OOS pode ter ~50-100 dias e bootstrap OOS e ruidoso.

Conclusao: este teste e diagnostico de derived_strategy_backtest. Pass/fail aqui nao autoriza nem bloqueia Stage 3 — Stage 3 proper aplica os gates §2.4.

## Tier 2 Forense — Frequency-Capped k=n_real

Objetivo: responder se o resultado negativo foi causado apenas por over-fire. Este teste reduz cada synthetic stream para `k = n_real_trades` sem mexer em `frozen_rules/`.

Seletores:

- `uniform_time_k_n_real`: seleciona k trades uniformemente ao longo do tempo. Nao usa PnL futuro nem features; e o unico seletor minimamente honesto.
- `oracle_best_net_pips_k_n_real_nontradeable`: seleciona ex-post os melhores trades por net_pips. Isto e um upper bound nao-tradeavel, usado apenas para medir se existia sinal dentro do over-fire.
- `random_p95`: percentil 95 de 500 subsamples aleatorios de mesmo k/turnover, para saber se o seletor uniforme bate acaso.

Cenario abaixo: M5 `decoding`, custo XAU conservador 45p.

| system | mode | n_orig | k | total pips | Sharpe | boot_lo | OOS Sharpe | OOS boot_lo | WF+ | random Sharpe p95 | random total pips p95 |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2421356 | uniform_time_k_n_real | 1773 | 1762 | -21626.2 | -0.070 | -1.275 | 0.433 | -2.133 | 4/8 | -0.046 | -14206.6 |
| 9375654 | uniform_time_k_n_real | 2261 | 915 | -59173.4 | -0.525 | -1.998 | -0.634 | -3.856 | 3/8 | 0.783 | 72709.7 |
| 6541963 | uniform_time_k_n_real | 16625 | 2213 | -73692.5 | -0.590 | -2.243 | 0.472 | -2.840 | 1/8 | -0.117 | -10809.2 |
| 11355455 | uniform_time_k_n_real | 7486 | 233 | -7804.3 | -0.696 | -3.901 | -2.512 | -9.412 | 5/8 | 1.306 | 17237.3 |
| 10281851 | uniform_time_k_n_real | 1651 | 652 | -76600.9 | -0.774 | -2.405 | -1.500 | -5.287 | 1/8 | 1.005 | 81423.7 |
| 8647517 | uniform_time_k_n_real | 25135 | 1024 | -36674.4 | -1.082 | -2.343 | -0.521 | -3.584 | 1/8 | -0.356 | -12522.4 |
| 11207608 | uniform_time_k_n_real | 7257 | 202 | -9729.5 | -2.220 | -6.035 | -2.943 | -11.439 | 2/8 | 0.747 | 3174.1 |
| 11207608 | oracle_best_net_pips_k_n_real_nontradeable | 7257 | 202 | 234626.7 | 20.863 | 17.316 | 40.935 | NaN | 8/8 | 0.747 | 3174.1 |
| 10281851 | oracle_best_net_pips_k_n_real_nontradeable | 1651 | 652 | 1041576.5 | 14.753 | 12.470 | 17.232 | 14.336 | 8/8 | 1.005 | 81423.7 |
| 11355455 | oracle_best_net_pips_k_n_real_nontradeable | 7486 | 233 | 641865.5 | 12.394 | 9.081 | 18.796 | NaN | 8/8 | 1.306 | 17237.3 |
| 9375654 | oracle_best_net_pips_k_n_real_nontradeable | 2261 | 915 | 1104819.6 | 12.185 | 10.133 | 16.029 | 12.868 | 8/8 | 0.783 | 72709.7 |
| 6541963 | oracle_best_net_pips_k_n_real_nontradeable | 16625 | 2213 | 2262320.1 | 11.316 | 8.618 | 12.929 | 10.306 | 8/8 | -0.117 | -10809.2 |
| 8647517 | oracle_best_net_pips_k_n_real_nontradeable | 25135 | 1024 | 1501459.8 | 11.029 | 8.457 | 15.500 | 11.739 | 8/8 | -0.356 | -12522.4 |
| 2421356 | oracle_best_net_pips_k_n_real_nontradeable | 1773 | 1762 | 150752.0 | 0.566 | -0.726 | 2.247 | -0.292 | 4/8 | -0.046 | -14206.6 |

Leitura Tier 2:

- Algum seletor uniforme passou bootstrap full e OOS? nao.
- Algum oracle ex-post passou bootstrap full e OOS? sim.
- Se o uniforme falha, nao ha evidencia tradeavel de que apenas reduzir frequencia salve a regra.
- Se o oracle passa, isso so prova que havia bons trades ex-post dentro do over-fire; nao fornece regra executavel.

## Arquivos

- JSON parseable: `_diagnostics/derived_gold_backtest.json`
- Tier 2 JSON parseable: `_diagnostics/derived_gold_backtest_tier2.json`
- Relatorio: `_diagnostics/DERIVED_GOLD_BACKTEST.md`

# [SHORT-HOLD CFD] V2-L2 Gayed rotation transported to CFD — 1º PASS do Plano A

**Phase:** 3.5a-V2 | **Lead:** V2-L2 (aggregator iter 43) | **Path:** Plano A

## TL;DR

**Plano A não será abandonado.** Após 42 iters entre V1 (0 PASS) e V2-L1
(0 PASS), o lead V2-L2 — Gayed LETF rotation re-expressada em CFD com leverage
explícita (Pepperstone Razor, swap diário real) — produz **4 configs
subset-PASS e 1 winner aggregate-level** que passa **todos os 9 gates** do
framework V2.

Winner: `gayed_ema100_L2_off_gld` — regime EMA-100 sobre SPY → SPY+QQQ on-regime
a 2× leverage via CFD, GLD na off-regime. OOS 2018-2023:
**Sharpe 2.285, CAGR 79.14% líquido, MaxDD -21.02%, median hold 6 dias**.
FWD 2024-2026: Sharpe 1.821, CAGR 59.28%. IR vs SPY 2.16.

Testado contra overfit: PBO 0.103 (10-block CSCV) e 0.036 (16-block),
DSR p-value 0.000288 com 27 trials, bootstrap 99.9% CI low 0.962 (stationary
block 5, 10k resamples). Todos muito acima dos thresholds AFML.

## Por que a V1 inteira mais a V2-L1 haviam refutado Plano A

A V1 testou 5 famílias de MR / breakout / session / regime em FX+metais 1h,
108 runs no total, todas refutadas: swap diário 0.8-2.0% sobre hold curto +
spread bid-ask alto em FX retail comiam qualquer edge. V2-L1 testou TSMOM
canônico daily multi-asset com rebalance mensal: hold 41-160 dias à 5 bps/dia
de swap long drenou 74-166% do equity inicial.

O erro conceitual compartilhado: buscar um edge **intraday** (V1) ou **muito
slow** (V2-L1) em um cost structure que pune ambos. Carver
`[systematic_trading, p.185-188]` já apontava isso — o ótimo retail é hold
1-4 semanas, spread+commission dominantes.

## Por que V2-L2 atravessa o gate enquanto 26 outras falham

Três invariantes descobertas na análise agregada das 27 configs:

1. **Leverage-bound MaxDD:** L=2 → ~21% (sob o cap 25%), L=3 → ~30%,
   L=5 → ~49% (invariante cross off-regime). Vince PoR
   `[leverage_space]` confirmado empiricamente: off-regime asset é
   irrelevante a 5× porque os crashes on-regime dominam. O gate MaxDD 25%
   elimina todas as configs L≥3.
2. **Gradient de adaptividade do sinal:** EMA-100 > LRS > SMA-200 em
   Sharpe OOS (a L=2: 2.17-2.28 vs 2.07-2.18 vs 1.47-1.65). EMA-100 sai
   do risk-on mais cedo num drawdown e volta mais cedo na recuperação,
   o que cumulativamente derruba a MaxDD-por-janela abaixo do cap
   `[leverage_for_the_long_run, p.11-14]`. SMA-200 não consegue —
   as melhores SMA-200 (L=2 gld) ficam em Sharpe 1.65, longe do gate
   Sharpe ≥ 2.0.
3. **GLD > cash > TLT off-regime:** spread de ~0.1 Sharpe mas consistente.
   GLD tem drift positivo + hedge cambial; TLT foi maceado em 2022 (o pior
   ano do fixed income em um século) dentro da janela OOS, e arrastou todos
   os TLT-off abaixo dos cash/gld `[leverage_for_the_long_run, p.16, p.21]`.

O winner sobrevive porque **combina** as três: L=2 (MaxDD sob cap), EMA-100
(Sharpe máximo no tier), GLD off-regime (Sharpe +0.1 sobre cash). Nenhuma
outra combinação fecha o cap MaxDD 25% *e* Sharpe ≥ 2.

## Cross-gate table (winner)

| Gate | Threshold | Observado | Pass |
|---|---:|---:|:--:|
| PBO (CSCV full, 10 blocks)        | < 0.5  | **0.103**   | ✅ |
| PBO (CSCV full, 16 blocks)        | < 0.5  | **0.036**   | ✅ |
| DSR p-value (27 trials)           | < 0.05 | **0.000288**| ✅ |
| OOS Sharpe                        | > 0    | **2.285**   | ✅ |
| FWD Sharpe                        | > 0    | **1.821**   | ✅ |
| Bootstrap 99.9% CI low (Sharpe)   | > 0    | **0.962**   | ✅ |
| WF profitable windows             | ≥ 6/8  | **8/8**     | ✅ |
| WF max-DD-per-window              | ≤ 25%  | **22.7%**   | ✅ |
| CAGR OOS net                      | ≥ 30%  | **79.14%**  | ✅ |
| Sharpe OOS net                    | ≥ 2.0  | **2.285**   | ✅ |
| MaxDD OOS                         | ≤ 25%  | **-21.02%** | ✅ |
| Median hold                       | ≥ 3d   | **6.0**     | ✅ |
| IR vs SPY (OOS)                   | ≥ 0.5  | **2.161**   | ✅ |

## Subset-PASS candidates (4)

Além do winner, 3 outras configs passam todos os gates per-ticker:

| Config | S_OOS | CAGR | MDD | WF max-DD | DSR p | CI 99.9% low | IR SPY |
|---|---:|---:|---:|---:|---:|---:|---:|
| gayed_ema100_L2_off_gld ★ | 2.285 | 79.14% | -21.02% | 22.7% | 0.000288 | 0.962 | 2.161 |
| gayed_ema100_L2_off_cash | 2.172 | 68.96% | -20.13% | 20.1% | 0.000746 | 0.916 | 1.981 |
| gayed_lrs_L2_off_gld     | 2.178 | 74.15% | -21.88% | 23.3% | 0.000741 | 0.885 | 2.045 |
| gayed_lrs_L2_off_cash    | 2.072 | 64.99% | -21.88% | 21.9% | 0.001717 | 0.776 | 1.873 |

O agregador escolhe o **ema100_L2_off_gld** como winner canônico (Sharpe máximo
entre os que passam WF max-DD). Os 3 demais ficam como variantes validadas —
relevantes para V2-L4 (Carver risk-parity multi-strategy) e para testes de
robustez em V2-L7.

## Como isso interage com Plano B

**Plano B IMUTÁVEL** — `Portfolio_3leg_EW = SSO+QQQ+GLD` permanece production
default (Sharpe OOS 2.251, CAGR 25.56%, MaxDD -10.86%).

**Plano A V2-L2 winner** adiciona-se como **segunda perna** do bucket ativo
(mandate §1 — 30pp ativo dividido entre A e B). O racional:

- Plano B: CAGR moderado, MaxDD baixo, LETF synthetic (sem swap, sem margem).
  Adequado a broker BR swing.
- Plano A: CAGR alto (~3× B), MaxDD duplo (~2× B), CFD com margem 2× via
  Pepperstone. Adequado à bucket short-hold agressiva.
- Correlação entre eles é alta (ambos long SPY/QQQ em risco-on), mas o
  mecanismo de *execução* (CFD margem vs LETF synthetic) difere, então o
  risco operacional é diferente: Plano B expõe ao risco de execução de LETFs
  e seu drag secular; Plano A expõe ao risco de margin call CFD e swap daily.
- Dual-path é o design que o mandate §1 explícita. V2-L7 formalizará o
  portfolio combination com inverse-vol weighting se V2-L3 / L4 produzirem
  edges adicionais.

## Implicações para o resto da V2

V2-L2 PASS tira da mesa o ramo "abandon Plano A" em V2-L7. As próximas
iters (44+) bootstrapam V2-L3 (AFML triple-barrier + meta-label) em busca de
um **segundo** edge Plano A — independente do Gayed — que possa ser
combinado via Carver risk-parity em V2-L4. Os leads continuam em ordem; o
status binding do stop rule (0 PASS → abandon) já foi resolvido.

Budget restante: ~35 iters (V2-L3 14 + V2-L4 1 + V2-L5 8 + V2-L6 14 + V2-L7 1 = 38,
com margem). MAX_ITER=80 cobre confortavelmente.

## Arquivos

- `reports/phase3_5a_v2/v2_l2_gayed_transported_cfd/AGGREGATE.md` — tabela completa + análise
- `reports/phase3_5a_v2/v2_l2_gayed_transported_cfd/AGGREGATE.json` — numbers machine-readable
- `reports/phase3_5a_v2/v2_l2_gayed_transported_cfd/gayed_ema100_L2_off_gld.md` — winner per-config
- `reports/phase3_5a_v2/v2_l2_gayed_transported_cfd/registry.json` — status: done
- `src/ai_trade/backtest/strategies/plano_a_leveraged_rotation.py` — implementação (criada iter 1-24)

## Citações

- Gayed regime rotation family: `[leverage_for_the_long_run, p.7, p.11-14, p.16-17, p.21]`
- Vince PoR vs leverage: `[leverage_space]`
- Kelly f/2 cross-check: `[math_money_mgmt]`
- Risk-parity off-regime allocation: `[systematic_trading, ch.8-9]`
- PBO 0.5 threshold + CSCV: `[advances_fin_ml, p.208-211]`
- DSR selection-bias correction: `[advances_fin_ml, ch.14]`
- WF 6/8 gate: `[advances_fin_ml, ch.11]`
- Stationary block bootstrap: `[advances_fin_ml, p.196-202]`
- Retail cost optimum 1-4 weeks: `[systematic_trading, p.185-188]`
- Pepperstone Razor costs: `docs/investment-mandate.md §3`

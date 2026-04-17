# Kalman Pairs SPY-IWM — OOS 2025 FAIL: demoted from winner #2

Data: 2026-04-16 01:30 — iter 13

## O que aconteceu

Ontem (iter 12) o Kalman Pairs passou os 3 gates (PBO=0.433, DSR p=0.0136,
WF 7/8) e virou winner #2. Mas um gate **opcional** fica fora do framework:
o **hold-out temporal** tipo "treina antes, testa depois".

Rodei o mesmo protocolo que confirmou Bollinger (iter 5):

- **Training 2021-2024:** Sharpe=+1.777, CAGR=3.64%, 392 trades, WR=52.3%, PF=1.16
- **OOS 2025 isolado:** Sharpe=**-1.137**, CAGR=-2.14%, 86 trades, WR=50.0%, PF=0.88
- **OOS 2026-Q1 isolado:** Sharpe=**-3.353**, 12 trades, PF=0.77

A estratégia **inverte de sinal** em 2025. Não é degradação, é quebra.

## Por que o grid passou mas o hold-out reprova

O grid usa CPCV (Combinatorial Purged Cross-Validation) — os folds de
teste e treino se **intercalam** ao longo de 2021-2025. Como 2021-2024
tinha edge forte (Sharpe 1.78), a média ponderada pelos folds consegue
superar os gates mesmo com 2025 arrastando.

O hold-out single-block ("treina 21-24, testa 25 isolado") é mais
duro: exige que o edge **persista no futuro mais recente sem
compensação de períodos bons anteriores**.

Isso confirma: **gates do framework são necessários mas não
suficientes.** O hold-out temporal é um filtro adicional.

## Por que 2025 quebrou o spread SPY-IWM

Hipótese (sem confirmação estatística ainda): em 2025 o SPY (large-cap)
e o IWM (small-cap) descorrelacionaram por razões macro (concentração
em tech mega-caps). O Kalman filter adapta o β lentamente (δ=1e-5), e
quando a relação quebra, a adaptação chega tarde — todo desvio do
spread é tratado como oportunidade de reversão, mas ele não reverte.

## Consequências para o projeto

- Winners confirmados: **1/10** (Bollinger MR SPY 1h), não 2/10.
- Kalman Pairs fica como referência metodológica, não produção.
- Regra nova: **todo novo winner precisa passar hold-out 2025 antes
  de virar winner #N**, não só os 3 gates.

## Files

- Script: `scripts/run_oos_kalman_pairs.py`
- Citações: `[algo_trading_chan, p.76-80, ch.3]`,
  `[advances_fin_ml, p.208-211, ch.12]`

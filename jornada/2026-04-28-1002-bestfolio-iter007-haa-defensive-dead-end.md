# Bestfolio iter 007: defesa HAA KMLM/CASH — STRONG 75/100, sem winner

A iteração 007 testou uma mudança bem estreita: manter o HAA+Gold de iter
009 intacto no ofensivo e trocar só os ativos usados quando o canário manda ir
para defesa. Foram 4 variantes: defesa original `IEFSIM/BNDSIM/CASHX`,
`KMLMSIM/CASHX`, `KMLMSIM/IEFSIM/CASHX` e `CASHX` puro.

O resultado foi robusto, mas não novo: a própria defesa original ganhou de
novo. Net Sharpe ficou em **0.983 / 0.954 / 0.860** contra o benchmark
iter 009 **1.120 / 1.061 / 0.954**. Passou **7/7 gates nos três datasets**,
com pior DSR p **0.0115**, mas teve **zero** datasets com o +0.10 Sharpe
necessário para winner `[advances_fin_ml, p.222-223]`.

Lição prática: trocar o que comprar depois que o canário já disparou não fecha
o gap bestfolio. KMLM pesado aumentou drawdown para **27.49%**, e cash puro
cortou CAGR. A próxima hipótese precisa mexer no timing do canário, não na
cesta defensiva simples `[stocks_on_the_move, ch.6]`; `[risk_parity, ch.5]`.

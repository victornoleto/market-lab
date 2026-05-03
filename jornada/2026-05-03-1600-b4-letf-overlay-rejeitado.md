# B4 LETF overlay rejeitado

Rodei o iter 051 para testar se um sleeve de LETF em regime risk-on melhoraria o B4 overlay sem Bitcoin. O grid foi restrito e pre-declarado: SSO/QLD/UPRO/TQQQ, pesos de 5% a 50% em passos de 5pp, SMA/EMA 150/200, funding vindo apenas de ZROZ ou NTSX, e DARF anual de 15% sobre ganhos realizados positivos nos rebalances mensais.

Resultado: LETF aumenta CAGR, mas nao melhora a versao balanceada. O melhor overlay sem LETF, `overlay_sma150_12mdd_10pp`, ficou em 12.35% CAGR liquido / -28.00% MDD / Sharpe 0.901. O melhor LETF por Sharpe, `qld_5_sma150_from_ZROZ`, ficou em 12.87% / -28.92% / 0.900. O melhor por CAGR, `tqqq_45_sma150_from_NTSX`, chegou a 16.78%, mas com MDD -44.64% e Sharpe 0.742.

A conclusao operacional e rejeitar LETF sleeves como melhoria core do B4 balanceado. Eles compram retorno aceitando pior drawdown e pior retorno ajustado a risco; podem ser vistos apenas como variante agressiva, nao como substituto da hipotese limpa sem LETF. A escolha de testar LETF com media movel segue a literatura de LRS `[leverage_for_the_long_run, ch.3-4, p.40-60]`; a rejeicao por nao bater criterio pre-declarado evita data snooping `[advances_fin_ml, p.208-211]`.

Plano C formal segue inalterado. A melhor hipotese de overlay sem BTC continua sendo o overlay restrito no-LETF com DARF do iter 050, ainda sem equivalencia a full gates/PBO/DSR/OOS.

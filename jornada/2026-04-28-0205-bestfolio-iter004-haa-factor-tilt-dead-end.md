# Bestfolio iter 004: HAA com tilt small/value — PROMISING 69/100, mas sem avanço

O quarto teste do `bestfolio_hunt_loop` manteve a arquitetura vencedora
HAA+Gold e mexeu só no pedaço internacional ofensivo: em vez de usar
internacional desenvolvido puro, testou quatro blends com small/value.

Resultado: o controle de drawdown continuou bom, mas o Sharpe caiu. O melhor
blend (`tilt_scv20`) ficou em **0.990 / 0.955 / 0.861** nos três datasets,
contra **1.120 / 1.061 / 0.954** do HAA+Gold referência. Ou seja: não fechou
o gap para o bestfolio.app; abriu mais.

O ponto mais importante foi estatístico: o PBO falhou nos três datasets
(0.885 / 0.869 / 0.694). Isso quer dizer que a escolha do "melhor" nível de
tilt parece instável demais para ser confiável `[advances_fin_ml, p.208-211]`.

Lição: o canário do HAA segue sendo a peça boa. O que não funcionou foi
trocar beta internacional por um simples blend small/value; isso preserva
drawdown, mas não cria retorno independente suficiente. Próximas direções:
testar return-stacking dentro do HAA ou esperar RSIT real em vez de usar mais
variações simples de equity factor.

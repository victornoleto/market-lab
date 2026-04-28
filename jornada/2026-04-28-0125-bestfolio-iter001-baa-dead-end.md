# Bestfolio iter 001 — BAA-G12 falha como avanço da fronteira

Rodamos a primeira iteração do `bestfolio_hunt_loop`: **BAA-G12 Balanced**,
uma estratégia de rotação mensal com canários amplos e universo ofensivo
maior que o HAA atual.

O resultado foi honesto, mas não competitivo. A estratégia reduziu bem o
drawdown, porém ficou defensiva demais e pagou arrasto de imposto anual
no modelo correto (`AnnualDarfEngine`). O Sharpe líquido ficou em
**0.975 / 0.792 / 0.782** contra o HAA+Gold iter 009 em
**1.120 / 1.061 / 0.954**. Ou seja: passou a maioria dos gates, mas não
melhorou a fronteira.

Lição prática: neste universo, BAA compra suavidade abrindo mão de retorno
demais. O HAA+Gold continua superior porque já protege o suficiente sem
passar tanto tempo em defesa. A decisão fica registrada como dead-end para
não retestar BAA-G12 puro sem mudança material de universo. Citações:
`[stocks_on_the_move, ch.6]` para momentum/rotação e
`[advances_fin_ml, p.208-211, p.222-223, p.196-202, p.31-34]` para gates.

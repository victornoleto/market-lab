# Bestfolio iter 006: HAA RSIT sintético — PROMISING 71/100, dead-end documentado

Testamos uma versão do HAA+Gold mantendo a estrutura vencedora do iter 009,
mas adicionando um `RSIT_PROXY`: carteira sintética de ações internacionais
mais managed futures (`VEASIM + KMLMSIM - 50bps/ano`). A ideia era ver se o
ETF RSIT, ainda sem histórico real no cache, poderia capturar melhor o gap de
Sharpe do bestfolio `[risk_parity, ch.5]`.

O resultado foi robusto nos controles, mas não foi avanço. Sharpe líquido:
**0.869 / 0.897 / 0.837** contra **1.120 / 1.061 / 0.954** do HAA+Gold iter
009. Passou **6/7, 6/7, 7/7 gates**, mas falhou PBO nas duas janelas globais
e disparou o kill pré-comprometido: Sharpe educacional ficou abaixo do iter
004 (**0.990**) `[advances_fin_ml, p.208-211]`.

Lição: o HAA+Gold já tem convexidade suficiente via KMLM e ouro. Colocar mais
managed futures dentro da perna internacional preserva CAGR/MDD, mas piora
Sharpe e estabilidade. RSIT fica fechado como hipótese sintética; só vale
revisitar com histórico real do ETF.

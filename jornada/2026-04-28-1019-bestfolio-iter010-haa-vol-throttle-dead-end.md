# Bestfolio iter 010: HAA volatility throttle — PROMISING 60/100, sem winner

Testamos manter o HAA+Gold intacto e adicionar só um limitador simples de
volatilidade na parte dinâmica de 85% da carteira. A melhor configuração foi
`vol12`, que corta exposição quando a cesta escolhida está acima de 12% de
volatilidade realizada. Ideia baseada em sizing por volatilidade
`[systematic_trading, p.137-148]`.

Resultado líquido pós-DARF anual: Sharpe **1.020 / 0.955 / 0.881** em
educational / vt_real / ndx_real. Passou **7/7 gates nos 3 datasets**, mas
não bateu o HAA+Gold iter 009 por +0.10 em nenhum dataset. Também falhou o
piso de CAGR em todos: **10.10% / 9.19% / 8.23%**.

Lição: o throttle melhora drawdown (MDD educacional caiu para **14.86%**),
mas vira uma versão defensiva e menos rentável do HAA. Serve como ferramenta
de preservação de capital, não como avanço da fronteira de Sharpe. Próximo
passo sensato: buscar dados reais VT/VXUS ou pausar o hunt até aparecer uma
fonte de regime que não seja só preço/tendência ampla.

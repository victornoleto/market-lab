# Bestfolio iter 009: Gayed trend canary — PROMISING 73/100, sem winner

Testamos uma ideia simples: manter o HAA+Gold exatamente como está e trocar
apenas o "canário" que decide risk-on/risk-off por um filtro de tendência
SPY/VT no estilo Gayed. A tese era que uma média móvel ampla poderia capturar
bear markets graduais melhor que o `VWOSIM` sozinho
`[leverage_for_the_long_run, p.40-60]`.

Resultado: o próprio `VWOSIM` original venceu de novo. Net Sharpe ficou
**0.983 / 0.954 / 0.860** em educational/vt_real/ndx_real, com gates
**7/7, 7/7, 6/7**. Zero datasets bateram o HAA+Gold iter 009 por +0.10
Sharpe, então não há winner.

Lição humana: o gap de Sharpe não está em outro filtro simples de tendência
de ações amplas. Depois de testar `VTISIM`, `SPYSIM` e `VTSIM`, o canário
`VWOSIM` continua sendo a melhor regra simples neste universo. Próximos
passos razoáveis são reduzir incerteza de dados reais VT/VXUS ou só testar
um throttle de volatilidade muito pequeno; sem isso, vale pausar o hunt de
Sharpe até aparecer uma fonte de regime diferente.

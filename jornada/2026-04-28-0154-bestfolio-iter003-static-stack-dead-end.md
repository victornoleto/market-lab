# Bestfolio iter 003: static stack não substituiu HAA

O Bestfolio Hunt Loop testou uma cesta estática de ETFs sintéticos
capital-efficient: global equity + bonds (`RSSBSIM`), S&P + ouro (`GDESIM`),
managed futures (`KMLMSIM`) e fatores small/value (`VBRSIM`, `VSSSIM`).
A ideia era reduzir giro e imposto, mantendo diversificação de risco
`[risk_parity, p.1-2, p.10]`.

Resultado: **MARGINAL 54/100**, sem winner. A cesta passou 6/7 gates nos
três datasets e preservou CAGR razoável, mas perdeu feio em Sharpe e
drawdown contra o HAA+Gold iter 009:

- Sharpe líquido: **0.823 / 0.742 / 0.910**
- CAGR líquido: **12.09% / 11.77% / 13.11%**
- MDD: **41.76% / 40.41% / 27.49%**

A lição é simples: baixo giro ajuda, mas não substitui o canário do HAA. O
HAA+Gold continua melhor porque reduz risco nos regimes ruins; a cesta
estática carrega equity/gold/fatores o tempo todo e deixa o drawdown dobrar.
O caminho está documentado como dead-end estrutural.

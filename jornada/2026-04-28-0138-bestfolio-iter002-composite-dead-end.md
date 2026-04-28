# Bestfolio iter 002: Composite Momentum Standard — MARGINAL 55/100

Testamos o Composite Momentum Standard: filtro de regime por `SPYSIM` acima
da média de 200 dias, seleção mensal dos 4 ativos mais fortes por retorno de
8 meses, peso inverso à volatilidade de 63 dias, e defesa em 60% `IEFSIM` +
40% `GLDSIM`.

Resultado líquido pós-DARF anual: Sharpe **0.940 / 0.958 / 0.957** em
educational / vt_real / ndx_real. A estratégia passou **7/7 gates nos 3
datasets**, com DSR worst p=1.08e-04, mas falhou o critério principal:
não bateu o HAA+Gold iter 009 por +0.10 Sharpe em nenhum dataset.

Lição em linguagem simples: a mecânica é robusta, mas defensiva demais para
o objetivo atual. Ela reduz danos, porém perde CAGR suficiente para ficar
abaixo do HAA+Gold. O dead-end foi documentado para não repetir a mesma
arquitetura SPY200/top4/inverse-vol com o universo atual.

Citações: `[stocks_on_the_move, p.21-30]`; `[advances_fin_ml, p.208-211,
p.222-223, p.196-202, p.31-34]`.

# Revisao GPT-5.5 do spy_beater_hunt

Revisao independente iniciada em `studies/spy_beater_hunt` antes de seguir para
`long_term_portfolio` e `global_factor_tilt_loop`.

Achado principal: o hunt tem boa cobertura empirica para as familias testadas
(LRS/Gayed, TQQQ gated, HFEA, meta-ensembles e static capital-efficient stacks),
mas o candidato pratico atual depende da leitura corrigida do iter 045, nao da
tabela longa antiga do iter 044. Com `RSST = SPY + 70% DBMF + 30% KMLM - cash`,
B4 deixa de ser o maior Sharpe absoluto e fica como compromisso balanceado:
~11.0% CAGR, ~29.6% MDD, Sharpe ~0.67 em 2000-2026. L1 CEGB tem Sharpe maior e
drawdown menor, mas CAGR menor.

Conclusao operacional preliminar: `spy_beater_hunt` nao invalida o Plano C nem
automaticamente substitui F1+SPLIT. O estudo sugere uma familia estatica
promissora para investidor que aceita ~30% de drawdown, mas ainda tem lacunas de
validacao antes de deploy: proxy RSST curto, ausencia de `verdict.json`/gates nos
iters 040-045, tratamento de impostos/rebalanceamento ainda dependente do modo
real de execucao, e alternativas nao testadas como SCV/value tilt dentro dos
stacks e a variante no_simpsons de NDX deleveraged.

Update na mesma sessao: iter 046 testou essas alternativas. Nenhuma bateu B4
corrigido em CAGR sem piorar drawdown. O melhor low-stress foi B4 sem RSST
leverage (9.91% CAGR / -20.91% MDD / Sharpe 0.749), mas ele perde CAGR. O melhor
upgrade leve foi B4 + 10% VBR tirado de NTSX (11.23% / -31.06% / 0.681), com
MDD um pouco pior. NDX deleveraged ainda ficou inviavel por MDD acima de 70%.

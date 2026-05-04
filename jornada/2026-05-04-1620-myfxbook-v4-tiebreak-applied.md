# MyFxBook v4 aplicou o desempate diagnostico

A task `032-fase3b-apply-tiebreak` aplicou exatamente o plano pre-registrado em `TIEBREAK_PLAN.md` aos 4 sistemas que tinham passado no filtro de copiabilidade: `8577442`, `1152318`, `10067081`, `10062918`.

O resultado foi uma ordem diagnostica: `10067081`, `8577442`, `10062918`, `1152318`. A shortlist diagnostica ficou com os tres primeiros: `10067081`, `8577442`, `10062918`.

Isso nao e recomendacao operacional. Nao iniciei monitor, cron, paper/live, broker integration ou AutoTrade real. O Plano C segue com 100% do capital e o Plano A segue DORMANT.

A regra priorizou atividade recente antes de custo, pips liquidos, diversificacao, concentracao, estabilidade, drawdown e score. Isso foi feito para evitar transformar a primeira ordenacao vista em selecao top-N contaminada por multiple-testing e data-mining `[advances_fin_ml, p.273-275]` `[evidence_based_ta, p.247-260]`. Custos/slippage continuam caveat operacional importante `[systematic_trading, p.182-197]`, e MCPT/PSR continuam evidencias historicas limitadas, nao autorizacao de deploy `[evidence_based_ta, p.325-328]` `[advances_fin_ml, p.260-263]`.

Proximo passo: STOP para decisao humana. Qualquer nova acao precisa de autorizacao separada e contrato proprio.

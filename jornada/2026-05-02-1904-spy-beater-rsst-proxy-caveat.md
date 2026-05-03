# spy_beater_hunt — proxy do RSST precisa mudar

Hoje revisamos como o estudo `spy_beater_hunt` estava simulando o RSST.

Descoberta principal: o estudo vinha usando uma aproximação simples demais para o RSST sintético: `SPY + KMLM - cash`. Isso está documentado no próprio código antigo como incompleto, porque o RSST real usa uma engine Newfound/ReSolve de managed futures, não apenas KMLM.

Um teste direto no testfol.io comparando RSST real contra proxies no período em que o ETF existe (2023-09-06 -> 2026-05-01) mostrou que `SPY + 70% DBMF + 30% KMLM - cash` replica melhor o RSST real do que `SPY + KMLM - cash`:

| proxy | CAGR | MDD | Sharpe | corr diária vs RSST |
|---|---:|---:|---:|---:|
| RSST real | 20.04% | -30.80% | 0.690 | 1.000 |
| SPY + 70 DBMF + 30 KMLM - cash | 20.30% | -27.08% | 0.788 | 0.927 |
| SPY + KMLM - cash | 12.58% | -24.05% | 0.483 | 0.856 |

Implicação: B4 Conservative continua sendo o pick documentado do estudo, mas agora fica com um caveat metodológico claro. Antes de qualquer pedido de override do mandato §7, os rankings que contêm RSST precisam ser re-rodados usando o proxy `70% DBMF / 30% KMLM`, com financiamento `CASHX?E=-2`.

Isso não é nova otimização de pesos. É correção de proxy: RSST é uma estrutura de return stacking `[risk_parity, ch.5, p.10]`, e a perna de managed futures deve representar melhor diversificação entre engines `[ilmanen_expected_returns, ch.19]`.

Capital permanece 100% Plano C. Nada foi aprovado para deploy.

# Bestfolio iter 005: HAA RSST/RSSB/CTA — PROMISING 70/100, dead-end documentado

O iter 005 testou a próxima hipótese prioritária: manter o HAA+Gold do iter
009, mas trocar os candidatos ofensivos por blocos return-stacked
(`RSSBSIM`, `RSST_PROXY`, `CTAPSIM`, `NTSXSIM`, `GDESIM`). A ideia era deixar
o próprio HAA ranquear diversificadores de managed futures e bonds, sem voltar
ao stack estático que já tinha falhado `[risk_parity, ch.5]`.

Resultado: **PROMISING 70/100**, mas **não winner**. O config escolhido
(`rssb_cta_balanced`) passou **7/7 gates nos 3 datasets**, com DSR worst
p=0.00455 e PBO abaixo de 0.5 em todos. Mesmo assim, o Sharpe líquido foi
**0.953 / 1.028 / 0.946** contra o benchmark iter 009 **1.120 / 1.061 /
0.954**. Nenhum dataset bateu por +0.10 Sharpe, e o kill pré-comprometido
disparou porque o Sharpe educacional ficou abaixo do iter 004 (0.990).

Lição: o HAA absorve sleeves stackados de forma robusta, mas, depois do iter
009, adicionar mais diversificador não é suficiente. A estratégia reduz MDD e
fica estatisticamente limpa, só que paga com CAGR/Sharpe. O gap bestfolio agora
parece exigir retorno incremental, não mais convexidade defensiva.

Próximas direções registradas: testar uma mudança de estado defensivo HAA
focada em Sharpe (KMLM-only ou CASHX-dominant), testar dual-canary
(`VWOSIM` + `VTISIM`) para reduzir falsos estados defensivos, e manter RSIT
deferido até haver dados reais.

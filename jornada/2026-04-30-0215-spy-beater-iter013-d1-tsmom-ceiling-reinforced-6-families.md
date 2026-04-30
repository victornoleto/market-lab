# spy_beater iter 013 — D1 momentum (TSMOM) é a melhor MDD do hunt mas score ainda abaixo do teto, KILL #33 reforçada em 6 famílias

A iter 011 fechou o spy_beater_hunt por **impossibilidade
arquitetural** (KILL #33: ceiling de score 67/100 em 4 famílias). A
iter 012 testou D2 (5ª família, stacked equity heavy) e reforçou o
ceiling — score 52, pior do hunt. Sobravam ainda dois Tier 3 não
testados: D1 (concentrated growth + momentum gate) e C2 (CAPE-timing).

Iter 013 fez **due diligence sobre a 6ª família arquitetural** (D1):
três configs LRS rotacionando entre QQQ (NDX) e IEF via **gate TSMOM**
(time-series momentum, `price[t] > price[t-N dias]`, single-anchor)
canonicamente Moskowitz/Ooi/Pedersen 2012 e Faber GTAA 2007. Configs:
1× QQQ + 6m TSMOM, 1× QQQ + 12m TSMOM, 2× QLD + 6m TSMOM. Foi
necessário adicionar `momentum_gate` em `lrs_engine.py` via TDD (3
testes novos; 762 → 765 baseline preservado).

Resultado: score **59/100 MARGINAL**. A config selecionada
(d1_qqq_6m_tsmom = 1× QQQ + lookback 126 dias vs IEF) passa nas três
barras (CAGR 12.83% ≥ 11.21%, MDD 35.27% ≤ 55.17%, gates 5+5
cross_met), mas score 8pts abaixo do closest-to-winner (iter 006 = 67).

**KILL #39 disparou** (D1 ≤ 67 reforça KILL #33 de 5 para 6 famílias).
**KILL #40 não disparou** (nenhuma config D1 ≥ 75; ceiling intacto).
**KILL #41 não disparou**: dose-response do lookback é **misto entre
datasets** — 12m bate 6m em lh_56y (40y) por +0.0011 Sharpe, mas 6m
bate 12m em spy_real (22y) por +0.0621. Isso valida a preocupação de
seleção em `[advances_fin_ml, p.31-34]`: a escolha de lookback
introduz viés dependente da janela amostrada.

**Achado contra-intuitivo notável**: d1_qqq_6m_tsmom é a **melhor MDD
de todo o spy_beater_hunt** (35.27% mean, vs iter 006 closest-to-winner
49.73% e F1+SPLIT 16.76% — mas F1+SPLIT é stacking, classe distinta).
TSMOM gate é **mais conservador que SMA**: reage mais devagar à
entrada/saída, captura menos drawdowns falsos durante bear-market
rallies, ao custo de CAGR. Vai contra a literatura prática de "gate
mais rápido = MDD melhor". A 2× QLD + TSMOM falha barra MDD (62.28%
> 55.17%) confirmando KILL #38: pure LETF + concentração sem bonds é
catastrófico em todos os níveis de leverage (2× e 3×).

A leitura agregada agora é **6 famílias × 14 iters × 41 trials**:
A2 TQQQ-track 67, A1/A3 SPY-track 66, B1/B2 HFEA 63, C1 vol-target 60,
**D1 concentrated+TSMOM 59 (best MDD do hunt)**, D2 stacked equity 52.
O ceiling segue arquitetural (não estatístico). F1+SPLIT permanece
deploy-ready; mandate §1 100% Plano C inalterado. Sobra só C2
CAPE-timing como Tier 3 não testado, mas CAPE tem 20+ anos de fracasso
out-of-sample documentado — testar não muda a conclusão. Hunt
permanece CLOSED.

Bônus prático: o d1_qqq_6m_tsmom, sob uma rubric MDD-anchored ou
Sharpe-anchored, ranquearia muito acima — vale como artefato
independente caso futuro estudo na long_term_portfolio queira variantes
MDD-first.

Citações: Moskowitz/Ooi/Pedersen 2012 (TSMOM canônico 12m), Faber 2007
(GTAA 6m TSMOM mensal), `[leverage_for_the_long_run, ch.3-4, p.40-60]`
(gate-family rationale), `[advances_fin_ml, p.31-34]` (factor framework
+ lookback selection bias), `[advances_fin_ml, p.222-223]` (DSR n=41,
worst p 2.99e-03 << 0.05), `[advances_fin_ml, p.196-202]` (bootstrap CI
passou).

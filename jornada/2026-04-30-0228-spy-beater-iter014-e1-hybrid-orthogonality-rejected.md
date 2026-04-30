# spy_beater iter 014 — Cruzamento "melhor-gate × melhor-sleeve" não quebra o teto: orthogonality rejeitada

A iter 011 fechou o spy_beater_hunt por **impossibilidade
arquitetural** (KILL #33: ceiling de score 67/100). Iters 012/013
reforçaram em 5 e 6 famílias single-axis (D2 stacked equity 52, D1
concentrated+TSMOM 59 com a melhor MDD do hunt). Sobrava uma pergunta
não respondida: e se o ceiling em 6 famílias single-axis fosse só um
limite de exploração, e o **cross-product** (gate de uma família ×
sleeve de outra) quebrasse o teto?

Iter 014 fez o teste mais óbvio: pegar o **gate D1** (TSMOM 6m, melhor
MDD individual) e plugar na **sleeve A2 iter-006** (TQQQ split + KMLM30
+ TLT10, melhor CAGR-anchored score). Três configs:
`e1_tqqq_split_kmlm30_tlt10_tsmom6m`, mesma sleeve com TSMOM 12m, e
uma versão pura `e1_tqqq_pure_tsmom6m` (100% TQQQ ON, IEF OFF) pra
testar H₃ "3× LETF puro + slow-gate é catastrófico".

Resultado: score **65/100 PROMISING**, todas as 3 barras passam
(`winner_conditions_met=True` para a selected, CAGR 17.20% / MDD 47.48%
/ gates 5+5 cross_met), mas score **2 pontos ABAIXO** do closest-to-winner
(iter 006 = 67). **KILL #42 disparou** (cross-product hybrid ≤ 67). **KILL
#43 não disparou** (best 65 < 70 — hunt não reabre). **KILL #44 não
disparou** (lookback dose-response continua dataset-regime-dependent
mesmo a 3× leverage: lh_56y 6m=0.755 → 12m=0.786 sobe, spy_real 6m=0.738
→ 12m=0.696 cai — mesmo padrão que iter 013 a 1×). **KILL #45 disparou**
catastroficamente (`e1_tqqq_pure_tsmom6m` MDD 80.32% mean,
predição confirmada do `d1_qld_6m_tsmom` 62.28% via degree-of-leverage
extrapolação).

**Achado central**: a **orthogonality assumption** que sustentava KILL
#33 single-axis é **empiricamente rejeitada** — mas na **direção
errada** pra reabrir o hunt. O cross-product hybrid scored 65 — abaixo
da union-of-single-axis-maxima (A2 = 67 + lift de MDD esperado do D1
gate sobre TQQQ-track ≈ +5pp MDD = +2-3 pts → predição 69-72). Por
quê? **Daily-reset decay no 3× LETF (~3-5%/y) DOMINA o canal de
gate-reaction-speed**. A 1× QQQ, swap SMA→TSMOM rendeu +5pp de MDD
(35.27% iter 013 vs ~40-45% se fosse SMA equivalente, estimativa).
A 3× TQQQ split, o mesmo swap rende só +1pp (49.73% → 47.48%). O
"saving" da TSMOM ao evitar false-positive re-entries durante bear
rallies é consumido pela decay extra durante períodos ON choppy. Em
linguagem de fator: gate × sleeve **interage negativamente** em
regime decay-dominated.

Tabela final 6-famílias + 1-hybrid: A2 TQQQ-track **67**, A1/A3
SPY-track 66, **E1 hybrid 65** (melhor MDD que A2: 47.48% vs 49.73%,
mas perde 2 pts em Gates), B1/B2 HFEA 63, C1 vol-target 60, D1
concentrated+TSMOM 59 (melhor MDD geral 35.27%), D2 stacked equity 52.

A negative-result policy fica **estatisticamente mais robusta**: agora
são "6 single-axis families + 1 cross-product hybrid ≤ 67",
cumulative_n_trials = 44, worst DSR p = 4.44e-03 << 0.05. F1+SPLIT
incumbent fallback permanece deploy-ready; mandate §1 100% Plano C
inalterado. Único Tier 3 não testado é C2 CAPE-timing — sem
infraestrutura de dados CAPE no projeto e 20+ anos de fracasso OOS
documentado, testar não mudaria a conclusão.

Notas operacionais: zero código novo (reusa `momentum_gate` adicionado
no iter 013), 765 testes baseline mantidos, 3 configs adicionando 3 ao
n_trials cumulativo. PBO N=3 warning persiste (CSCV instável com N<4)
mas DSR + WF + OOS + FWD + Bootstrap + Cross-lib carregam o gates 5/7
sem falsos positivos.

Citações: Moskowitz/Ooi/Pedersen 2012 (TSMOM canônico, claim de
ortogonalidade factor-MoM rejeitada empiricamente em 3× LETF);
`[leverage_for_the_long_run, ch.3-4, p.40-60]` (daily-reset decay como
canal MDD-dominante a 3× LETF — confirmação empírica direta);
`[risk_parity, ch.5, p.10]` (KMLM crisis-alpha mantido); HFEA
Bogleheads 2019; `[ilmanen_expected_returns, ch.19]` (MF crisis-alpha
necessária por KILL #45); `[advances_fin_ml, p.31-34]` (gate × sleeve
orthogonality assumption explicitamente testada e rejeitada);
`[advances_fin_ml, p.222-223]` (DSR n=44, worst p 4.44e-03);
`[advances_fin_ml, p.208-211]` (PBO N=3 warning); `[advances_fin_ml,
p.196-202]` (bootstrap CI passou: lh_56y 0.3110, spy_real 0.0545 > 0).

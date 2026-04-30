# spy_beater iter 012 — D2 stacked equity heavy é a pior família, KILL #33 reforçada em 5 famílias

A iter 011 já tinha declarado o spy_beater_hunt **fechado por
impossibilidade arquitetural** — KILL #33 disparou ao constatar que
quatro famílias distintas de estratégia (LRS sobre SPY, LRS sobre TQQQ,
HFEA com TMF, vol-target) batem todas no teto de score 67/100, longe
do score 90 exigido para "WINNER". O relatório final daquela iter
listou três direções de Tier 3 ainda não testadas (D1 momentum mensal
em QQQ, C2 timing CAPE, D2 equity stacking pesado), todas vistas como
~5% de chance de quebrar o teto.

Iter 012 fez **due diligence sobre a 5ª família arquitetural** (D2):
três configs estáticas combinando NTSX (stacking 90/60), UPRO (LETF 3×
SPY) e AVUV (small cap value factor). Sem regime gate, sem duração
alavancada, sem vol-target — pura combinação de stacking + factor +
LETF. Resultado: score **52/100 MARGINAL**, a **pior pontuação de toda
a vertente**. A config selecionada (50% NTSX + 50% AVUV) chega a
passar nas três barras (CAGR 12.23% ≥ 11.21%, MDD 52.65% ≤ 55.17%,
gates) mas o score afunda porque o ganho de CAGR sobre SPY é só ~1pp
(prêmio de fator pequeno em janelas longas) e a robustez multi-horizon
desaba (5y só 58% das janelas batem SPY).

**KILL #36 disparou** (D2 ≤ 67 reforça KILL #33 de 4 para 5 famílias).
**KILL #37 não disparou** (nenhuma config D2 ≥ 75; ceiling 90 segue
inacessível). **KILL #38 disparou** (d2_upro_avuv puro 50% UPRO + 50%
AVUV, sem bonds, MDD 85.48% catastrófico) — fica empiricamente
provado que **regime gate ou stacking com bonds é necessário**, não
opcional, para a barra de MDD do spy_beater. Adicionar UPRO ao mix
NTSX+AVUV mata o Sharpe monotonicamente (0.74 → 0.62 → 0.58) — mais
alavancagem sem gate piora o trade-off.

A leitura agregada agora é **5 famílias × 13 iters × 38 trials**:
A2 TQQQ-track 67, A1/A3 SPY-track 66, B1/B2 HFEA 63, C1 vol-target 60,
D2 stacked equity 52. O spread de 15pp entre A2 e D2 confirma o
diagnóstico do iter 011: o teto não é noise estatístico, é
arquitetural. F1+SPLIT (incumbent fallback do long_term_portfolio)
permanece deploy-ready; mandate §1 100% Plano C inalterado. Hunt
permanece CLOSED — não há iter 013 planejada.

Citações: `[risk_parity, ch.5, p.10]` (Carlson stacking),
`[advances_fin_ml, p.31-34]` (factor framework AVUV/SCV),
`[advances_fin_ml, p.222-223]` (DSR n=38, worst p 9.40e-03 << 0.05),
`[leverage_for_the_long_run, ch.3-4, p.40-60]` (decay LETF UPRO sem
gate é catastrófico).

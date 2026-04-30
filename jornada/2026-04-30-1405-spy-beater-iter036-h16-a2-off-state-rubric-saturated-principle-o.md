# spy-beater iter 036 — H16 A2 off-state RUBRIC-NEAR-SATURADO — Princípio O bate o mártelo

Hoje rodei o 20º iter no eixo meta-ensemble. A pergunta era: o bônus
+2pt do iter 035 (off-state KMLM no constituinte GLD) **generaliza** para o
constituinte A2 (gate QQQ-200d-SMA), ou é específico do GLD?

Configurei 4 variantes de A2's `off_weights` (IEF, KMLM, TLT, Blend
50/50), mantendo o resto do apex iter 035 H15.2 fixo.

**Resultado**: max H16 = 73, abaixo do teto strategy-level 74 do iter 035.
KILL #157 disparou (sem breach). E aqui surgiram dois achados ricos:

1. **Princípio M reconfirmado** via duplicate-replication: H16.1
   (replica EXATAMENTE o spec do iter 035 H15.2) entregou raw metrics
   IDÊNTICOS a 3-4 casas decimais (Sharpe 1.074/1.057, CAGR 17.71%/16.46%,
   MDD 30.22%/30.22%) — mas o score caiu de 74 para 73 porque o G1 PBO
   no lh_56y mudou de 0.0833 PASS para 0.5873 FAIL, só por causa dos
   sibling configs diferentes na grade. Envelope de ruído ±1pt confirmado.

2. **NOVO Princípio O — magnitude do efeito off-state-axis é
   gate-source-coupled**: GLD (commodity-orthogonal) tem spread 2pt no
   eixo off-state; A2 (equity-track QQQ) tem spread 1pt — rubricamente
   saturado. Mecanismo: regimes GLD-trend-OFF (USD-strength /
   global-macro) divergem fortemente do sleeve TQQQ/QLD → KMLM crisis-alpha
   captura essa divergência. Regimes QQQ-trend-OFF (NDX-bear) correlacionam
   com o sleeve → IEF e KMLM são intercambiáveis → sem bônus.

H16.2 (A2 KMLM off) ainda revelou nuance: **regime-dependent** (helps
spy_real -5.93pp MDD, hurts lh_56y +5.14pp MDD; média neutra). Pré-2003
(1987 Black Monday, era pré-MF maduro) KMLM falha; pós-2003 funciona.

Princípio O bound: cross-product de off-state em G2 / E1qqq (também
equity-track) está previsto rubricamente saturado. **Single-axis off-state
cross-product está EXAURIDO**. Recomendação ao usuário: declarar hunt
RE-FECHADO no iter 036; iter 035 H15.2 segue strategy-level apex 74 deploy
candidate.

Citações: `[ilmanen_expected_returns, ch.19]`,
`[advances_fin_ml, p.208-211]` (Princípio M PBO grid-stability).
36/50 iters consumidos (72%). Mandato §1 100% Plano C inalterado.

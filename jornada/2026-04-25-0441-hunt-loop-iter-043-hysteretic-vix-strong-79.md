# Hunt Loop iter 043 — hysteresis halves VIX-regime crossings, DSR ridge holds

**Status:** 🥇 STRONG, score 79/100. **Regression vs iter 041's 84 by 5 pts.**
Path-variance hypothesis from iter 042 is FALSIFIED on this direction.

## O que foi testado

Tentei melhorar a iter 041 (a melhor estratégia do loop, score 84,
"static-stack" com pesos 0.70/0.40/0.40 em regime calmo e 0.30/0.55/0.55
em regime de stress, gate VIX < 20 binário) introduzindo **histerese**
no gate. A motivação veio do diagnóstico da iter 042: a punição da
DSR (Deflated Sharpe Ratio) parece vir da *variância de caminho* — toda
vez que a regime label muda, o portfolio reposiciona, e cada flip
contribui pra variância residual que a DSR penaliza com
n_trials cumulativo.

A hipótese era simples: usar um **Schmitt trigger** com dois thresholds
(entrar em calmo se VIX < 18; sair pra stress se VIX > 22; estado
persiste dentro da banda [18, 22)). Isso reduziria as travessias de
regime de ~8/ano (iter 041) pra ~3-4/ano. Menos flips → menor
variância de caminho → DSR melhor.

## Resultado real

Histerese **funcionou no eixo desenhado**: RT/yr caiu de ~8 pra 2.25-2.54
(redução de ~70%, melhor que o predito), e MDD melhorou em todas as
3 datasets (spy MDD 22.92% — segundo melhor de qualquer iter da família
static-stack, só perde pra iter 042 com 22.21%). Sharpe edge se
manteve (3/3 datasets batem benchmark por +0.10).

**Mas a DSR worst-p PIOROU**: 0.168 (iter 041) → 0.189 (iter 043),
+0.021 pior no ndx_real. Isso falsifica a hipótese de variância de
caminho — pelo menos nesta direção.

Por que? **Histerese troca responsividade por precisão.** Cada flip
no threshold 20 (iter 041) é um update Bayesiano "instantâneo" sobre
o regime atual; histerese introduz um *atraso* de 1-3 dias quando
o VIX atravessa a banda [18, 22). Esse atraso introduz uma nova
forma de variância — chamei de "variância de regime-lag" — onde
a label de regime fica desalinhada do estado real do mercado nos
~18% das barras dentro da banda. Essa variância residual é
suficiente pra dominar o ganho de menos flips.

## Lição estrutural

Combinando iter 042 (que falsificou "compor amplitude × frequência
em regimes diferentes melhora DSR") com iter 043 (que falsificou
"reduzir frequência via histerese melhora DSR"), conclusão:

**A iter 041 (com gate VIX binário em 20 e pesos 0.70/0.40/0.40 ↔
0.30/0.55/0.55) é um ÓTIMO LOCAL de DSR num cume estreito.** Qualquer
perturbação no *timing* do gate (amplitude ou frequência) regride —
por mecanismos *diferentes*:

- **Amplitude** (iter 042: 1.7× ↔ 1.0× ao invés de 1.5× ↔ 1.4×) →
  variância de caminho por swings de leverage.
- **Frequência** (iter 043: histerese [18, 22] ao invés de threshold
  fixo 20) → variância de regime-lag por transições atrasadas.

Os dois efeitos somam variância residual que a DSR penaliza.

## Implicação pro caminho à frente

O eixo *gate-timing* está fechado pra essa família de pesos. A
próxima iteração precisa atacar a DSR via **informação por barra**
— não via timing do gate. Três caminhos abertos:

1. **HMM-2 multi-feature (VIX, T10Y3M)**: classificador de regime
   mais rico mantendo os mesmos pesos. Adiciona densidade de
   informação por chamada de regime sem alterar timing. Recomendado.
2. **ML meta-label sobre iter 041**: classificador binário
   open/skip nas posições da iter 041, treinado em features
   (VIX, VXN, RVX, VVIX, T10Y3M, EBP, skew). Nova fonte de info
   por barra, sem perturbar gate.
3. **Out-of-family**: cross-sectional factor timing (MTUM, QUAL,
   USMV, SIZE, VLUE, SPLV) — fluxo de retorno totalmente independente,
   contornando o teto de 84 da família static-stack.

## Status do projeto

- Total iters: 43 (eram 42).
- TOP-K #1: iter 041 (84 STRONG) — ainda intocado.
- Cumulative n_trials: 4308 (era 4307).
- Mandate §1: MAINTENANCE 100% Plano C — NUNCA mexe com isso. Mesmo
  que a iter 044 ache um winner, é um CANDIDATE, não auto-deploy.

Tempo gasto: ~1h (engine reuse da iter 041 ajudou). Wall-time bem
dentro do budget de 2h.

Detalhes técnicos completos em
`studies/strategy_hunt_loop/iterations/043-2026-04-25-0441-hysteretic-vix-regime-weights/final_report.md`.

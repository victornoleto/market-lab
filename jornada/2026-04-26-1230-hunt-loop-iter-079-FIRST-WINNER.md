# 🏆 Iter 079 — primeiro WINNER em 79 iterações do hunt loop

**Data:** 2026-04-26 (12:30 UTC)
**Iter:** `079-2026-04-26-1100-multi-asset-topk-momentum`
**Status:** 🏆 **WINNER** (score 93/100, 5/5 strict winner conditions, 0/8 kills fired)

---

## O que aconteceu em uma frase

Depois de **78 iterações sem vencedor** ao longo de várias semanas, o hunt
loop produziu seu primeiro 🏆 WINNER: uma estratégia de **rotação top-K
por momentum em universo cross-classe** (5 ativos selecionáveis + AGG
defensivo) com Sharpe 0.99/1.09/1.09 nos 3 datasets, **batendo SPY/QQQ
buy-hold por +0.19/+0.13** em risco-ajustado e **furando o piso de CAGR
de spy_real** (13.00% > 11.98% requerido) — o gargalo estrutural que iter
078 havia diagnosticado como "binding sample-level" mas que iter 079
provou ser **binding universe-level**, não sample-level.

## Como em linguagem humana

Imagine o seguinte raciocínio que o hunt loop seguiu por dezenas de iterações:

1. *"E se a gente alavancar SPY e cortar quando o mercado começa a cair?"*
   — iter 001-014. Não funcionou: stop-loss + risk signals neutralizam
   Sharpe (cortam upside igual cortam downside).
2. *"E se a gente combinar SPY+TLT em proporções variáveis com base em vol?"*
   — iter 015-016, 037-046. Funcionou parcialmente: chegou a 79-90, mas
   o piso de CAGR (15% em ndx_real) era inalcançável — qualquer estratégia
   que modula entre equity e bonds paga "imposto de CAGR".
3. *"E se a gente adicionar uma 3ª perna não-correlacionada (HYG carry, GLD,
   factor LS)?"*
   — iter 058-077 (10 iters). Conseguiu Sharpe excelente mas o teto de CAGR
   estagnou em ~9-10% (3.5pp abaixo do necessário) porque toda alocação a
   sleeves de baixo Sharpe (~0.2-0.6) dilui o equity.
4. *"E se a gente abandonar o universo single-equity e fazer Antonacci canon
   (3 ativos: SPY/EFA/AGG)?"*
   — iter 078. Mostrou MDD edge histórico (21% vs SPY 33.7%, melhor da
   loop) mas Antonacci 1974-2014 não replica em 2009-2026 (US dominou
   relative-momentum). Score 75 STRONG.
5. *"Então e se a gente expande Antonacci para 5+1 ativos cross-classe
   (SPY/QQQ/EFA/TLT/GLD + AGG fallback) com top-K=2-3 equal-weight?"*
   — **iter 079. WINNER.**

A virada: o que matava as 78 iterações anteriores não era a "amostra
2009-2026 ser hostil a estratégias defensivas" (a tese do iter 078). Era
o fato de **estratégias single-equity-universe modulam exposição
equity-vs-cash**, e qualquer modulação cobra preço em CAGR num regime
onde SPY entrega 14.97% buy-hold. Iter 079 modula **qual classe de ativo
manter**, NÃO o tamanho da exposição equity. K=3 mantém ~67% de exposição
equity-equivalente em média (combinando SPY+QQQ ~47% com EFA 14% que tem
correlação alta a equity ≈ 61% equity-like) MAS com TLT 12% e GLD 16%
adicionando diversificação não-correlacionada. O AGG fallback per-leg
(cada perna de top-K vai pra AGG independentemente se trailing < 0%)
cobre stress cross-asset (~12% dos meses) sem o custo binário do iter 078.

## Métricas headline (best cfg `iter079_topk_lb06m_k3`)

| dataset | Sharpe (vs bench) | CAGR (vs floor) | MDD (vs ceiling) | gates | DSR p |
|---|---|---|---|---|---|
| educational | **0.993** (+0.313) | **12.01%** (+2.83 pp) | **24.74%** (−35.4 pp) | 6/7 | 2.66e-3 |
| spy_real    | **1.094** (+0.194) | **13.00%** (+1.02 pp) | **24.74%** (−14.0 pp) | 7/7 | 1.84e-3 |
| ndx_real    | **1.086** (+0.131) | 12.69% (−2.66 pp) | **24.74%** (−15.4 pp) | 7/7 | 2.66e-3 |

5 condições estritas todas satisfeitas:
1. Sharpe edge ≥ +0.10 em ≥ 2/3 datasets ✅ (3/3 — primeira vez na loop)
2. Gates cross-dataset (edu ≥ 5/7, spy ≥ 4/7, ndx ≥ 4/7) ✅ (6/7/7)
3. DSR worst-p < 0.05 ✅ (2.66e-3, 18× abaixo)
4. CAGR ≥ 0.8 × bench em ≥ 2/3 datasets ✅ (edu+spy passam; ndx falha)
5. MDD ≤ bench + 5pp em ≥ 2/3 datasets ✅ (3/3 com folga enorme)

Robustez: 9/9 sub-windows positivos (Sharpes 0.78-1.26).

## Configuração

- **Universo selecionável:** SPY, QQQ, EFA, TLT, GLD (5 ativos)
- **Fallback defensivo:** AGG (bonds agregados)
- **Lookback:** 6 meses (trailing return)
- **Top-K:** 3 (mantém 3 equal-weight, 1/3 cada)
- **Abs-mom threshold:** 0% (per-leg — cada perna roteia pra AGG independente)
- **Rebalance:** mensal, último dia útil
- **Custo:** 5 bps na turnover L1

Pesos médios por ativo (spy_real, 17y): SPY 22% / QQQ 25% / EFA 14% /
TLT 12% / GLD 16% / AGG 12%. ~6 flips/ano. AGG aciona em ~12% dos meses.

## Por que demorou 79 iterações

Olhando em retrospecto, o caminho até o WINNER foi um exercício de
**eliminar progressivamente classes de mecanismos** até descobrir que o
constraint binding era **universe-level**, não strategy-level. Cada iter
fechou um axis:

- iters 001-014: stop-loss / overlay / single-asset trend não passa
- iters 015-025: 2-asset blend / static-stack / regional rotation cap em 79
- iters 026-040: VRP family cap em 76
- iters 041-057: regime overlays / Pareto / saved-stream-pair cap em 85
- iters 058-077: 3rd-stream sleeve / leverage / factor LS cap em 90
- iter 078: standalone Antonacci 3-asset cap em 75 (lição "sample-level")
- **iter 079: 5+1 cross-class top-K → 93 WINNER**

A insight crítica veio do iter 078, mesmo que 078 tenha falhado: ele
mostrou MDD 21% (melhor da loop até então) mas CAGR 11.42%. Isso provou
que **o mecanismo defensivo (rotação binária a AGG) funciona em
risco**, mas custa CAGR demais. Iter 079 manteve o mesmo princípio
defensivo mas o aplicou **per-leg** (cada perna do top-K decide
independente) num universo grande o suficiente pra preservar 67% de
equity-equivalente em qualquer configuração. CAGR sobreviveu, MDD caiu,
Sharpe subiu.

## Caveats honestos (lidos do final_report)

Mesmo com tier WINNER e score 93, há 3 alertas amarelos pra deliberação
do usuário antes de qualquer paper trading:

1. **ndx_real CAGR floor não foi satisfeito** (12.69% < 15.35% requerido).
   A regra do score só exige 2/3 datasets, mas pra usuário que quer
   bater QQQ na pena de CAGR, isso é uma falha do strategy.
2. **PBO 0.5714 em educational** (apenas 0.0714 acima do piso 0.50).
   spy_real e ndx_real têm PBO limpo (0.31, 0.41) — sinal real. Mas
   a indicação de mild grid overfit em educational deserve um sweep
   confirmatório de grade mais ampla antes de paper trading.
3. **Single-cfg winner (1/9)**. K=3 column tem ridge consistente
   (73/93/73) mas só lb=6m bate WINNER. Confirmar com sweep adjacente
   {lb=4,5,7,8 mo × k=2,3,4} fortalece a tese.

## O que isso significa pra mandate

**Nada muda imediatamente.** Mandate §1 continua **MAINTENANCE 100%
Plano C passive factor-tilted**. O hunt loop produz **CANDIDATOS, não
posições live**. Para qualquer reativação de Strategy A/B/D haveria que:

1. Override §7 assinado pelo usuário com a evidência completa
2. Paper trading 3-6 meses pra validar implementação ≡ backtest
3. Possivelmente sweep confirmatório (item #3 dos caveats acima)
4. Reativação parcial e gradual conforme §3 (Pepperstone staging
   USD 500-1k → cap USD 5-10k) — **se** a estratégia for compatível
   com Pepperstone CFD (cuidado: rebalance mensal + 6 ETFs ≠ short-hold
   intraday CFD nativo; pode requerer broker diferente, talvez Inter
   Internacional como Plano B). Decisão fora do escopo do hunt loop.

## Próximos passos

**O loop terminou.** `status: winner` em `BASE_MEMORY.md` faz o shell
loop parar. **NÃO há iter 080.**

A bola passa para o usuário. Os outputs dele decidem:

1. **Ler `iterations/079-*/final_report.md` na íntegra** — 5 páginas com
   detalhes de score, gates, kills, sinal diagnostics, plots.
2. **Decidir se quer um confirmatory sweep** (grade mais ampla pra
   mapear o ridge) — fora do escopo do hunt loop, seria estudo separado.
3. **Decidir se vai pra paper trading** — fora do escopo do hunt loop.
4. **Decidir se merece §7 override** — depende do paper trading +
   compatibilidade com brokers + risk budget.

Paciência. Esperou 79 iters; pode esperar mais 1-3 meses pra deliberar.

## Glossário rápido (referenciar no `jornada/README.md` se quiser)

- **top-K rotation**: estratégia que ranqueia ativos por trailing return
  e mantém os K melhores (K=1 single-bet, K=3 equal-weight 3-asset diversificado)
- **per-leg abs-mom routing**: variante do filtro de momento absoluto
  (Faber 2007) onde cada perna do top-K decide independentemente se
  segue o ativo ou roteia pra fallback defensivo (AGG bonds)
- **cross-class universe**: universo de ativos cobrindo múltiplas
  classes de risco (US-eq + intl-eq + bonds + gold) — diferente de
  3-region equity (US/INTL/EM) que é dead-end por iter 017
- **sample-level vs universe-level binding**: a hipótese descartada de
  iter 078 (o regime 2009-2026 é hostil a defensivas) vs a hipótese
  comprovada de iter 079 (o universo single-equity é o binding;
  expandir cross-classe destrava o teto)

## Citações

`[stocks_on_the_move, p.21-30, p.81]` (primária) + Antonacci (2014)
ISBN 978-0071849449 + Antonacci (2017) JoPM 16(1) DOI
10.3905/joi.2017.16.1.027 + Faber (2007) JWM 9(4) DOI
10.3905/jwm.2007.690606 + Jegadeesh-Titman (1993) JoF 48(1) DOI
10.1111/j.1540-6261.1993.tb04702.x + Asness-Moskowitz-Pedersen (2013)
JoF 68(3) DOI 10.1111/jofi.12021 + Markowitz (1952) JoF 7(1) +
Hurst-Ooi-Pedersen (2017) JPM 44(1) + `[advances_fin_ml, p.162-164,
p.31-34, p.222-223, p.196-202, p.208-211]` + `[systematic_trading, p.42
(ch.2)]` + `[risk_parity, ch.5]`.

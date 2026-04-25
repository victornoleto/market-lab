# Hunt loop iter 048 — Gate de alavancagem na saída fecha o terceiro eixo de modulação

## Contexto humano

iter 046 (TOP-K #1, score 85) é uma combinação 50/50 de duas estratégias
ortogonais — uma stack regime-gated por VIX (iter 041) e uma cesta de
venda de put credit spreads (iter 039). Está a 5 pontos do tier WINNER
(90). O único piso que falha é o **CAGR**: a média 50/50 entre iter 041
(~13% CAGR) e iter 039 (~5-6% CAGR) sai em ~9-10%, e o piso exigido é
9.18% / 11.98% / 15.35% nos 3 datasets.

iter 047 fechou um caminho: assimetria de peso na composição (sweep
50/50 → 80/20). Markowitz disse logo que o ótimo é 50/50 — e foi.

A pergunta de iter 048: **e se modular a SAÍDA da combinação? Aplicar
um multiplicador 1.4× nos dias calmos (VIX<20) e 1.0× nos dias de
estresse, no fluxo já combinado de iter 046?** Não modifica os inputs
(iter 041 + iter 039 ficam idênticos), só re-escala o resultado final.

## O experimento

Single cfg pré-comprometido (N=1, sem custo de Bonferroni — lição de
iter 047): `iter046_lev_calm14_stress10_vix20`. Multiplica o stream
combinado de iter 046 por 1.4× quando VIX[t-1]<20, 1.0× caso contrário.
Tudo o resto verbatim.

Predição (envelope linear): com ~70% dos dias em regime calmo,
CAGR combinado deveria subir ~28% (de ~9.5% para ~12.2%), cruzando
os pisos edu+spy. Sharpe sub-multiplicativo: deveria ficar mais ou
menos parado (σ × 1.4 / μ × 1.4 = mesma razão). MDD: levemente pior
mas longe dos tetos.

## O resultado (que machucou)

CAGR subiu, mas **menos que previsto**: 9.16→10.91% (edu), 9.45→11.22%
(spy), 9.76→11.65% (ndx). Uplift de **+1.75 / +1.76 / +1.89 pp** —
abaixo do limite de 2pp do kill criterion F que eu pré-comprometi.
Razão: composição sub-multiplicativa eats ~30% do envelope linear.

E o pior: **Sharpe regrediu** em todos os 3 datasets (−0.0015 / −0.0333
/ −0.0374). E **DSR worst-p PIOROU**: 0.0414 → 0.0427 (edu, deflator
step), 0.0416 → **0.0557** (spy, cruza α=0.05 e cai do bucket de 15
pts pro de 10).

Saldo no score: +5 pts (CAGR floor edu cruza), −2 (gates spy fail), −5
(DSR bucket downgrade) = **−2 pts net. Score 83 vs iter 046's 85.**

iter 048 é uma **REGRESSÃO**, não um avanço.

## Veredito

🥇 **STRONG 83/100, 3/6 kills firaram** (B: DSR edu regress; D: score <
iter 046; F: CAGR uplift < 2pp em todos). iter 046 segue TOP-K #1.

## A lição estrutural (importante para o futuro)

iter 048 é o **análogo, no nível da SAÍDA, do que iter 044 fechou no
nível dos INPUTS**. Re-utilizar o mesmo classificador de regime
(VIX<20) tanto na entrada (iter 041 já modula pesos por VIX<20) quanto
na saída (este gate) **dupla-conta o sinal**. O multiplicador na saída
amplifica retornos assimetricamente, mas TAMBÉM amplifica σ
assimetricamente — Sharpe fica plano (sub-multiplicativo eats), n×Sharpe²
fica idêntico, mas n_trials += 1 → deflator quântum step → DSR p sobe.

Em conjunto, **3 mecanismos distintos de modulação na iter 046 estão
agora fechados**:
1. iter 044 — gate enrichment nos INPUTS (T10Y3M + VIX em vez de só VIX)
2. iter 047 — assimetria de peso (50/50 → 65/35 → 80/20)
3. iter 048 — gate de alavancagem na SAÍDA (1.4× / 1.0× por VIX)

Os três trocam a mesma quantidade conservada (variância × retorno) e
os três falham em quebrar 85. **A única caminho para 90 é ADITIVO**
(adicionar uma terceira perna positivamente-correlacionada-com-CAGR-mas-
ortogonal-aos-fluxos-existentes), não MODULATIVO (transformar as 2
pernas existentes).

## Para iter 049

A direção #1 que iter 047 sugeriu (3-leg + factor-timing MTUM/QUAL/USMV)
está **bloqueada por dado**: verifiquei o cache Tiingo e MTUM/QUAL/USMV
NÃO estão lá. Apenas SPY/IEF/GLD/QQQ/IWM/TLT entre os fatores conhecidos.

Mas tem 1695 tickers no cache (single stocks majoritariamente). Surge
uma alternativa: **3-leg = iter 041 + iter 039 + Clenow-style 12-1
momentum em N≥50 single stocks** (top quartile do universo Tiingo).

A heterogeneidade do universo single-stock escapa ao fechamento de
iter 003 ("≤20-asset homogêneo não tem sinal de ranking"). E o dado
está pronto. Risco: turnover.

## Estado consolidado (mandate §1: maintenance)

Mandate §1 segue **MAINTENANCE 100% Plano C**. iter 046 (85 STRONG)
permanece como CANDIDATO científico, não posição. iter 048's regression
não muda nada estrategicamente — apenas fecha mais um caminho de
otimização e aponta para o próximo.

## Citações principais

- `[risk_parity, ch.5]` — base iter 041 (preservada)
- `[advances_fin_ml, ch.17-18]` — detecção de regime binário VIX
- `[advances_fin_ml, p.222-223]` — DSR com cumulative n_trials (deflator step)
- `[advances_fin_ml, p.31-34]` — G7 cross-library (0.0000pp)
- Whaley (2009), JPM 35(3) — VIX como indicador de regime ex-ante
- Bekaert-Hoerova (2014), J Econometrics 183(2) — decomposição
  uncertainty / risk-aversion no VIX

## Próximo passo

iter 049: composição aditiva 3-leg `iter 041 + iter 039 + Clenow 12-1
single-stock momentum` com top-K do universo Tiingo (~1695 tickers).
Hipótese: 3ª perna positivamente-CAGR (10-15%) + heterogeneidade do
universo single-stock dá sinal de ranking real (escapa iter 003) +
correlação esperada < 0.5 com iter 041 → CAGR combinada sobe para
~11-12% sem perder DSR sub-0.05.

Detalhes técnicos: `studies/strategy_hunt_loop/iterations/048-2026-04-25-0644-iter046-output-lev-gate/`
(hypothesis.md, final_report.md, verdict.json, plot_vs_benchmark_*.png).

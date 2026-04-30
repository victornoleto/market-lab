# Long-term portfolio iter 022: C.5 tail-hedge convexo — ⚠️ Score 100/100 MAS é ARTEFATO de modelo, NÃO winner real

Última iter da fila 016-022. Hedge sintético: quando SPY 21d return < −5%, hedge paga 2× abs(SPY_daily_neg); else paga premium fixo −0.04%/day (~−10%/yr).

## Resultado headline

Selected `tail_15pct`. Score **100/100**, Sharpe **1.520 / 1.710 / 1.684**, MDD 7-18% (excelente).

| dataset | gross S | edge vs avg(SPY,VT) | CAGR | MDD |
|---|---:|---:|---:|---:|
| lh_56y | **1.520** | **+0.849** | 14.71% | 17.86% |
| vt_real | **1.710** | **+1.004** | 18.57% | 9.54% |
| ndx_real | **1.684** | **+0.760** | 16.58% | 7.33% |

Mecanicamente é tier WINNER perfect-100 com edge gigantesco vs avg(SPY,VT) E vs iter 011.

## ⚠️ Mas é ARTEFATO. NÃO USAR.

**Score 100 IS ITSELF prova de model failure** — nenhuma estratégia real long-term clears every gate every threshold.

Bias sources do hedge sintético:

1. **Sem vega cost**: opções reais ficam MAIS caras quando VIX sobe (exatamente nos crashes). Meu modelo só cobra premium em períodos NÃO-drawdown — subestima custo nos anos-crise.
2. **Hindsight via trigger 21d**: modelo "sabe" que está em drawdown via 21d return; em opções reais você precisa COMPRAR a put ANTES do crash, pagando premium o tempo todo.
3. **Path-dependence errada**: puts reais pagam (strike − spot) na expiração, não 2× drops diários compostos.
4. **Sem spread/liquidity drag**: ATM puts reais custam ~6%/yr premium net of slippage; meu modelo usa ~10%/yr decay flat sem inflar em vol regimes.

**Interpretação honesta**: edge real de uma hedge baseada em opções seria **+0.05 a +0.15 Sharpe** net of true premium drag — talvez tier WINNER no papel, **NÃO** os +0.85 mostrados aqui.

Outro red flag: monotônico ASCENDENTE com hedge weight (5%→15%: 1.26→1.52). Opções reais têm diminishing returns conforme alocação cresce (premium acelera não-linear). Aqui, premium linear → mais hedge = mais alpha sintético.

## DE-022: methodological dead-end

Não consigo concluir se tail hedging é bom ou ruim neste universo — só que este modelo sintético é inválido. Test apropriado precisaria:
- (a) Dados reais de SPY puts (OptionMetrics — não está em cache);
- (b) VXX/VIXY do Tiingo como proxy de vol-spike payoff (com decay realista ~−40%/yr).

Sub-iter futuro recomendado: hedge baseada em VXX-tiingo real, não sintético.

## Lição pra futuras iters

Quando adicionar asset sintético com retornos MODELADOS (não medidos), incluir no-free-lunch sanity check:
- Assert hedge Sharpe alone < benchmark Sharpe alone
- Assert worsening monotonic conforme peso passa do ótimo
- Plot premium-acceleration vs weight pra confirmar não-linearidade

iter 022 não vai pro top-K substantivo. **Incumbent substantivo continua iter 011.**

## Status final fila 016-022

| iter | direção | resultado | substantivo? |
|---|---|---|---|
| 016 | B.5 UMD overlay | WINNER 91 | **✅ ÚNICO POSITIVO REAL** |
| 017 | B.6 VBRSIM regime-gated | STRONG 82 | dead-end |
| 018 | C.1 Antonacci GEM | PROMISING 74 | dead-end |
| 019 | C.2 vol-managed 60/40 | STRONG 81 | CAGR drag |
| 020 | C.3 All-Weather | STRONG 83 | CAGR drag (mas Sharpe/MDD top) |
| 021 | C.4 Sector rotation | PROMISING 69 | dead-end (data-limited) |
| **022** | **C.5 Tail-hedge** | **WINNER 100** ⚠️ | **MODEL ARTIFACT, não usar** |

Próxima sessão deve ser **summary report** consolidando 016-022 + decisão estratégica do usuário.

Arquivos: `studies/long_term_portfolio/iterations/022-2026-04-29-0040-C5-tail-hedge/`

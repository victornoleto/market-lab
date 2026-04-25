# Hunt loop — iter 033 — TLT longa = mesma Sharpe do iter 015, MDD pior

## TL;DR

Trocou IEF por TLT no NTSX 0.9/0.6 do iter 015 esperando que o
"prêmio de carry" maior dos títulos de 20-30 anos elevasse o Sharpe.
**Não funcionou.** A volatilidade do TLT é o dobro da do IEF, e o
ganho de prêmio é exatamente cancelado por essa volatilidade extra
ao longo da curva de Sharpe. Resultado: Sharpe **idêntico** ao iter
015 nos dados reais (+0.001/−0.007), MDD na NDX **+7pp pior** (47%
vs 40%) por causa de 2022, e o platô do iter 015 (77 STRONG) segue
de pé. Score 72 PROMISING.

**Empate suspeito**: iter 033 fechou em 72 com a **mesma quebra de
critérios** do iter 032 (1:25 + 2:17 + 3:0 + 4:15 + 5:10 + 6:5),
apesar dos dois caminhos serem mecanicamente diferentes (iter 032 =
empilhar overlay de short-vol; iter 033 = trocar duração do título).
Os dois apontam pra mesma conclusão: o platô do iter 015 é resistente
a variações no eixo "bond" — pra romper precisamos de mecânica
estruturalmente diferente (carry sleeve sem aumento de variância,
carry de FX/commodity, ou arquitetura não-estática).

## O que rodou

Single config `ntsx_synth_90_60_spy_tlt`: peso fixo 0.9 SPY + 0.6
TLT, daily-rebalanced, 1.5× alavancagem total, custo 2 bps por
perna, sem timing, sem overlay. Reusou 100% do código do iter 015
(`apply_static_stack`); a única mudança real foi o ticker do título
e a janela educational alinhada à inception do TLT (2002-07-26 vs
2006-01-03 do iter 015 — 4 anos a mais de história).

3 datasets:
- **educational**: SPY+TLT 24 anos (2002→2026, 4y a mais que iter 015)
- **spy_real**: SPY+TLT 17 anos (2009→2026)
- **ndx_real**: QQQ+TLT 16 anos (2010→2026)

6 testes TDD novos passando first-try (incluindo o crítico
`test_iter033_imports_iter015_stacking_engine` que força
single-source-of-truth na matemática).

## Resultados-chave

| dataset | Sharpe iter 033 | Δ vs frozen | **Δ vs iter 015** | CAGR | MDD | gates |
|---|---|---|---|---|---|---|
| edu | 0.85 | +0.17 | **+0.07** | 13.4% | 42.6% | 5/7 |
| spy | 1.04 | +0.14 | **−0.01** | 16.0% | 38.5% | 6/7 |
| ndx | 1.06 | +0.11 | **+0.00** | 19.8% | **47.0%** | 6/7 |

vs benchmarks frozen (SPY 0.90 / QQQ 0.955), o iter 033 **passa
3/3 datasets na criterion 1** com Δ +0.10. Mas a comparação direta
com iter 015 (mesmo NTSX, IEF no lugar de TLT) revela que o Sharpe
está **empatado em dados reais** — o ganho aparente de +0.07 no
educational vem dos 4 anos extras de janela (2002-08 captura o bull
secular de bonds), não da troca de ticker.

DSR worst-p **0.31** (educational) — todos os 3 datasets falham o
limite de 0.20 do Kill C. Por quê? Porque com Sharpe ≈ iter 015 e
n_trials=4288 (vs iter 015's 4258), o DSR penaliza de forma virtualmente
idêntica: o teste é dominado pela altura do Sharpe em relação ao
"deflator" (que cresce com cumulative trials); duração mais longa
não muda essa altura.

MDD na NDX **47.0%** quebra o teto de 40.12% por +6.93 pontos. 2022
foi o caso perfeito de "tudo cai junto": QQQ −33% e TLT −31% no mesmo
ano. A perna 0.9 QQQ + 0.6 TLT compõe esse choque numa drawdown
levered de ~50% pico-a-vale. iter 015 com IEF perdeu apenas ~13% em
2022, então o MDD da NDX ficou em ~40% (passa).

## Por que a duração não funciona como alavanca de Sharpe

Em termos de mecânica:

```
Sharpe = (μ_eq + 0.6 × μ_bond) / sqrt(σ²_port)

TLT vs IEF:
  Δμ      ≈ +1.5 pp (carry premium, KMPV 2018)
  Δσ²     ≈ +2× (volatilidade ~7% → ~14%)

Net Sharpe Δ ≈ 0   (numerador e denominador escalam ~igualmente)
```

Isso é o **análogo estático** do achado do iter 016/021 sobre
"σ²_port absorption" em stack vol-managed. Lá o overlay short-vol
era absorvido dinamicamente pelo vol-target; aqui a substituição de
duração é absorvida estaticamente pelo termo de variância do
denominador do Sharpe. O resultado é o mesmo: o ganho de prêmio
não chega ao Sharpe-line, fica todo nos momentos superiores (CAGR,
MDD, skew).

## O empate iter 032 = iter 033 = 72 é um padrão

A pontuação 72 tem decomposição **byte-for-byte idêntica** entre
os dois iters mais recentes:

| critério | iter 032 (composição) | iter 033 (duração) |
|---|---|---|
| 1 Sharpe edge (+0.10 vs frozen) | 25/25 | 25/25 |
| 2 Gates | 17/25 | 17/25 |
| 3 DSR | **0/15** | **0/15** |
| 4 CAGR floor | 15/15 | 15/15 |
| 5 MDD ceiling | 10/15 | 10/15 |
| 6 Robustness | 5/5 | 5/5 |
| **total** | **72** | **72** |

Os dois caminhos para "destravar criterion 4 (CAGR)" — empilhar
overlay short-vol (iter 032) ou trocar título de longa duração
(iter 033) — pagam o **mesmo preço** em DSR + MDD. O platô do iter
015 (score 77 STRONG) é a fronteira eficiente real do family de
"stack estático SPY + 1 título": pra atravessar precisamos de uma
arquitetura ou mecânica fundamentalmente diferente, não de variações
no eixo de bonds.

## O que vem agora (iter 034 candidates)

Direções **estruturalmente diferentes** que ainda não foram tentadas:

1. **Bond carry SLEEVE (zero-net-notional)**: 0.9 SPY + (0.6 − α) IEF
   + α TLT — a "spread" TLT-IEF tem volatilidade muito menor que TLT
   sozinho (~6-8% vs ~14%), então preserva o Sharpe do iter 015 e
   adiciona prêmio de carry. Trata diretamente o problema da iter
   033. **Mais forte candidato.**

2. **Cross-asset VRP em IWM**: o overlay AND-composite do iter 031,
   mas escrito em **IWM (small caps)** em vez de SPY, sobre a base
   iter 015. Stress de small-cap parcialmente decorrelacionado de
   large-cap (em 2022 IWM −36% vs SPY −25%) — pode baixar o
   corr_combined,SPY abaixo do +0.97 do iter 032 e recuperar DSR.

3. **FX carry overlay**: AUDUSD long, USDJPY short como overlay no
   iter 015. FX carry tem padrão de crash *próprio*, não coincidente
   com vol spikes de equity (Lustig-Verdelhan 2007).

**NÃO recomendado** (por iter 032+033): variações de eixo bond no
stack iter 015 (qualquer ticker, qualquer mix) — o platô 77 é
resistente.

## Honestidade epistemológica

Iter 033 falhou exatamente na predição mais forte da hipótese:
"swap longa-duração eleva o Sharpe via prêmio de carry". A
literatura (KMPV 2018, Cochrane-Piazzesi 2005, Ilmanen 2011) diz
que o prêmio existe — e existe mesmo, +0.4-1.0pp de CAGR confirmam
isso. Mas o Sharpe não é função do prêmio sozinho; é função de
prêmio/sqrt(variância), e a variância dobrou. Os livros tem razão
sobre a existência do prêmio; o framework de scoring corretamente
captura que esse prêmio não chega ao Sharpe-line numa stack estática.

O 72 PROMISING é honesto: confirma o achado do iter 032 (criterion
3 + 5 são as travas reais do family), agrega evidência ao platô
77 do iter 015, e fecha mais um eixo (substituição de duração) sem
inflar PBO ou ferir o baseline de testes (799 collected, +6 vs
793 do iter 032).

Não há WINNER. O modo MAINTENANCE 100% Plano C segue válido. Esta
iteração é uma peça de evidência adicional na narrativa "tentamos,
medimos, mostramos que não passou no rigor estatístico que já
estabelecemos" — exatamente o que o repo precisa pra continuar
servindo como due-diligence infrastructure.

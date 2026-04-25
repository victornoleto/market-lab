# Hunt loop iter 034 — NTSX bond-carry sleeve (zero-net-notional duration spread) vira 72/100 PROMISING; bond-axis FECHADA com triple-tie em 72 de três mecânicas independentes

**Data:** 2026-04-25 01h20
**Contexto:** Pesquisa em background. Modo MAINTENANCE 100% Plano C
permanece o estado de produção (mandate §1). O hunt loop é
diagnóstico, não gera deployment.

---

## TL;DR

Iter 034 implementou a recomendação **B-Sleeve** do BASE_MEMORY pós-
iter-033: um *spread* de duração de "soma zero" dentro do sleeve de
bonds do iter 015. A receita: `0.9 SPY + 0.4 IEF + 0.2 TLT` — mesmo
notional total de bond (0.6) que o iter 015, mas 1/3 dele realocado
do IEF (7-10y) pro TLT (20-30y) pra capturar o prêmio de carry de
longo prazo (KMPV 2018) **sem dobrar a variância do bond leg** (que
foi o que matou o iter 033).

**Resultado**: 🥈 **PROMISING 72/100** — score-empate byte-por-byte
com iter 032 (composição) e iter 033 (substituição) **com a mesma
decomposição 1:25 + 2:17 + 3:0 + 4:15 + 5:10 + 6:5**. Três
iterações, três mecânicas estruturalmente diferentes no eixo bond,
**todas cravam 72**, sempre com a mesma causa: DSR worst-p > 0.20.

A hipótese de **controle de variância foi vindicada empiricamente**:
- Bond-leg vol(0.4 IEF + 0.2 TLT) ≈ 5.4% (vs iter 033 8.4% / iter 015 4.2%).
- MDD ndx **caiu 4.93pp** vs iter 033 (47.04% → 42.11%).
- MDD spy **caiu 5.42pp** vs iter 033 (38.47% → 33.05%).
- Sharpe Δ015 **POSITIVO em todos 3 datasets** (+0.011/+0.014/+0.012).

Mas o ganho de Sharpe é **estruturalmente pequeno demais pra mover
DSR** ao n_trials atual (4291). O DSR worst-p ficou em 0.529 no
educational — 2.6× acima do threshold pre-committed Kill C de 0.20.

---

## A descoberta estrutural (3 mecânicas, mesmo platô)

Olhando os 3 últimos iters lado a lado:

| iter | mecânica | Sharpe (edu/spy/ndx) | DSR worst-p | MDD ndx | score |
|---|---|---|---|---|---|
| 032 | composição (iter 015 + iter 031 VRP) | 0.81/1.04/1.08 | 0.502 | 44.4% breach | **72** |
| 033 | substituição (IEF→TLT 100%) | 0.85/1.04/1.06 | 0.313 | 47.0% breach | **72** |
| **034** | **spread sleeve (40% IEF + 20% TLT)** | **0.79/1.06/1.08** | **0.529** | **42.1% breach** | **72** |
| 015 | base (0.9 SPY + 0.6 IEF) | 0.78/1.04/1.06 | 0.548 | 39.5% | 77 |
| 016/018/021 | vol-managed family | 0.98/1.14/1.19 | 0.13-0.23 | 23-27% | **79** |

**Três coincidências em fila não são coincidência**. O eixo bond
(qualquer composição, qualquer duração, qualquer divisão) **bate em
72**, sempre por DSR. O iter 015 a 77 é definitivamente a fronteira
eficiente do *family* "static stack com bond". Pra subir além disso
precisa OU mudar de eixo (FX, VRP cross-asset, não-bond) OU mudar
arquitetura (não-estática: regime/ML/CS).

---

## Por que a variance-control vindicada não basta

A matemática previa (e confirmou) que a sleeve teria menos variância
que iter 033 — porque a correlação entre IEF e TLT é alta
(ρ medida = +0.916), o spread (TLT − IEF) tem vol ~6-8%, muito menor
que TLT sozinho ~14%. Isso melhora MDD muito (4-5pp em real data).

Mas o que importa pra DSR é o **Sharpe ratio**, não MDD. E o ganho
de carry ao introduzir 0.2 de TLT no sleeve foi de cerca de **+0.3pp
de CAGR ao ano**, com aumento de variância proporcional → Sharpe
gain ≈ +0.01. Isso é estatisticamente indistinguível de iter 015 ao
nível n_trials = 4291.

A regra de bolso descoberta: **MDD pode mover sem Sharpe mover**.
Em portfolios vol-constrained o shape da variância pode mudar (por
ex: mover massa do tail) sem mover a localização (média/desvio).
Iterar pra cima de MDD não vai destravar score.

---

## O que isso significa pra próxima iteração

O iter 034 fecha definitivamente o eixo bond. A direção recomendada
pelo BASE_MEMORY pra iter 035 é **F-FX (FX carry overlay)** — long
AUDUSD + short USDJPY na base do iter 015. Razões:

1. **Distribuição-orthogonal de verdade** — o FX carry tem padrão de
   crash próprio (carry trade unwinds, tipicamente em risk-off
   global), MAS *não sincronizado* com bond duration ou equity vol
   spikes. O iter 034 mostrou que tweaks no eixo bond ficam dentro
   do mesmo cone de variância; FX é um cone diferente.
2. **Dados já em cache** — `audusd.parquet` e `usdjpy.parquet` já
   estão em `data/tiingo/daily/prices/`. Implementação ~30-45 min.
3. **Citações sólidas** — Lustig-Verdelhan 2007 (JFE 102), Burnside
   2011 (RFS 24), Brunnermeier-Nagel-Pedersen 2008 (NBER 14473).

Alternativas (mais caras): C-VRP IWM (precisa arquitetura iter 026,
~60-90 min); arquitetura não-estática (regime/ML/CS, ~2-4 h).

NÃO recomendado: qualquer outra variação no eixo bond. ZROZ/EDV,
α-sweep, bond+commodity blend, ALLOCATION timing — todos vão cair
no mesmo platô 72.

---

## Pegadinhas honestas

- **Funding cost não modelado**: o NTSX sintético com 3 pernas
  pagaria ~50-100 bps/ano de financiamento implícito sobre o 50% de
  notional adicional (mesma magnitude que iter 015 e iter 033).
  Estimativa de haircut: −0.05 a −0.10 no Sharpe líquido. Pós-haircut
  o Sharpe edu cai ~0.70 (perde gate +0.10), spy ~0.96 (idem), ndx
  ~1.00 (idem) — ou seja, nenhuma das 3 datasets mais clearia o
  edge frozen +0.10. Iter 035 deve testar variant funded
  (estilo iter 018 replay).
- **Janela educational mais curta que iter 033**: iter 033 começou
  em 2002-07-26 (TLT-aligned, 24y); iter 034 começa em 2006-01-04
  (IEF-aligned, 20y, 4y a menos). Isso explica o Sharpe Δ033 −0.055
  no edu — o TLT só do iter 033 cobriu ~4 anos extras de bull
  treasury. Em real data (spy/ndx 17/16y, mesmo período pra todos),
  iter 034 BATE iter 033 em Sharpe.
- **MDD ndx breach pequeno mas real**: 42.11% vs ceiling 40.12%
  (frozen bench 35.12% + 5pp). Falha critério 5 por 1.99pp; iter
  033 falhava por 6.93pp. Spread sleeve melhorou muito mas não
  zerou o impacto do 2022 (rate spike + tech selloff).

---

## Status de produção

`docs/investment-mandate.md` §1 permanece **MAINTENANCE 100% Plano
C**. Iter 034 é diagnóstico, não candidato. Iter 015/016/018/021/026
permanecem como melhores-evers (77-79 STRONG) sem nenhum atingir
WINNER. Hunt loop continua iterando.

---

## Citações principais

- `[risk_parity, ch.5]` — bond term-premium decomposition.
- `[risk_parity, p.5, p.10-11, ch.1]` — risk-parity static stack
  (Asness-Frazzini-Pedersen 2012).
- `[leverage_for_the_long_run, p.19-20]` — leverage on diversified base.
- `[advances_fin_ml, p.31-34]` — cross-lib parity (G7 PASS 3/3,
  ≤0.087 pp).
- `[advances_fin_ml, p.222-223]` — DSR cumulative n_trials.
- Koijen-Moskowitz-Pedersen-Vrugt (2018), JFE 127(2),
  DOI 10.1016/j.jfineco.2017.11.002 — cross-sectional bond carry.
- Cochrane-Piazzesi (2005), AER 95(1),
  DOI 10.1257/0002828053828581 — forward-rate loadings em long end.
- Ilmanen (2011), *Expected Returns* ch.6-7 — term premium
  empirical magnitudes.

Detalhes técnicos completos:
`studies/strategy_hunt_loop/iterations/034-2026-04-25-0120-ntsx-bond-carry-sleeve/`
(hypothesis.md + run_backtests.py + compute_gates_and_score.py +
verdict.json + final_report.md + 2 plots).

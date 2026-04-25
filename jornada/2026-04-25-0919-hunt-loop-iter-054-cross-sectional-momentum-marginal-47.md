# Hunt loop iter 054: cross-sectional 12-1 momentum on Tiingo single-stock universe vira 47/100 MARGINAL — DATA-LAYER closure descoberta

**Pesquisa em background (mandate §1 segue 100% Plano C — modo
maintenance, alocação efetiva inalterada).**

## TL;DR

Iter 054 implementou a recomendação top do iter 053 ("PIVOT TO NEW
BASE — saved-stream-pair Pareto exausto a 85"): **cross-sectional 12-1
momentum (Jegadeesh-Titman canonical)** sobre o universo de **422
single-stocks do cache Tiingo** com `first_dt ≤ 2014-01-01`. Top-K=20
equal-weight, rebalanceamento mensal, custo 5 bps/lado.

A hipótese era que single-stock heterogeneity (>400 nomes) escaparia
do fechamento iter 003 (≤20-asset homogeneous ETFs falham por falta
de dispersão cross-sectional). **Resultado**: estratégia produz
Sharpe **0.655 nos 3 datasets** (single-universe; mesmo backtest
mapeado nos 3 benchmarks). Window-matched comparison: SPY 2014-2026
Sharpe 0.680, QQQ 2014-2026 Sharpe 0.753 — a **estratégia perde por
0.025 pra SPY e 0.098 pra QQQ no MESMO janela**, mesmo com
survivorship bias a favor.

CAGR 16.60% (3/3 floor PASS), MDD 28.25% (3/3 ceiling PASS), G7
cross-lib **0.0000pp** em paridade pandas-numpy (8ª iter consecutiva
em paridade perfeita), mas **Sharpe edge 0/3 datasets**, DSR p=0.811
(n=4324, FAIL), PBO=1.000 (4-cfg grid puro rank-noise — IS-best vira
bottom-half OOS em 7/7 splits informativos).

**Score breakdown**: 1:**0**/25 (Sharpe edge) + 2:17/25 (gates 5/7×3) +
3:**0**/15 (DSR) + 4:15/15 (CAGR) + 5:15/15 (MDD) + 6:0/5 = **47/100
MARGINAL**. Kills A (Sharpe regress) + B (DSR collapse) firaram.

## Por que o resultado importa estruturalmente

**Lição estrutural definitiva** (vai pro `DEAD_ENDS.md`):
fechamento iter 003 ("≤20-asset homogeneous ETF universe lacks ranking
signal") **não salva o caso 422-asset survivor-biased single-stock**.
A nova closure é mais profunda:

> **Universo survivorship-biased em qualquer tamanho correlaciona-se
> com o índice cap-weighted que o benchmark — aniquilando a dispersão
> cross-sectional que momentum/value/quality precisam pra harvestear
> o factor premium.**

Tiingo cache contém apenas tickers que sobreviveram até 2026-04
(buscados em bulk no download de 2026-04-14). Por construção, esses
são os "winners" do mercado pós-2014 — exatamente os mesmos nomes que
dominam SPY/QQQ via cap-weighting. Top-K=20 equal-weight desses
mesmos nomes é fundamentalmente um SPY-tilted basket com active risk
sub-ótimo.

Adicione a isso: (a) **post-2009 momentum decay** documentado na
literatura (Ben Dor & Ross 2024, AQR 2018) — momentum crashed
fortemente em 2009 e 2018, e a década 2014-2026 é exatamente o
intervalo "weak momentum era"; (b) **long-only captura ~metade do UMD
factor** (Carhart 1997) — UMD é construção long-short, não long-only;
(c) **monthly turnover 50-80% × 5bps roundtrip** custa 2-3 pp/yr em
CAGR antes de o premium tentar harvestear.

## Implicação para o hunt loop

**A família INTEIRA de cross-sectional ranking** sobre o cache Tiingo
está estruturalmente bloqueada: 12-1 momentum, 6-1, adjusted-slope
(Clenow), low-vol, low-beta, value, quality, multi-factor composites.
Todas dependem da mesma propriedade de dispersão que o cache
survivor-filtered não pode entregar. **Só desbloqueio**: trazer fonte
de dados point-in-time + delisted (CRSP, Norgate Premium Data,
Quotemedia archive). Não viável dentro do escopo do projeto sem
budget novo.

## O que funcionou

- **Engine + cross-lib parity perfeita** (G7 ΔCAGR=0.0000pp 8ª iter
  consecutiva). Novo simulador monthly-rebalance + numpy reference
  hand-rolled em ~280 linhas, validados em paridade absoluta.
- **CAGR + MDD floor**: estratégia compõe 16.60% CAGR (acima dos 3
  floors) com MDD 28.25% (abaixo dos 3 ceilings). Não é catastrófica
  do ponto de vista de compounding — apenas inferior em risk-adjusted.
- **Pipeline de gates** (WF/OOS/FWD/Bootstrap/PBO/DSR/G7) rodou clean
  em arquitetura qualitativamente nova (cross-sectional, não
  static-stack/overlay), validando portabilidade do framework.

## O que fechou estruturalmente

- Iter 003's "≤20-asset" closure **NÃO É** o limite real de
  cross-sectional momentum no Tiingo cache.
- O limite real é **survivorship-biased data layer** — afeta o
  cache regardless of universe size.
- Closes single-stock momentum/value/quality/composite/factor on
  `data/tiingo/daily/prices/` permanently (sem CRSP/Norgate
  delisted-aware data).

## Top-K unchanged

Iter 054 score 47 — não entra Top-K (mínimo 79). Iter 046 mantém
TOP-K #1 a 85 STRONG; iter 053/051/041 empatam #2-#4 a 84.

## Iter 055 PICK

Iter 053 mandate (path 90+ requires NEW base edu Sharpe ≥ 1.20)
combinado com iter 054 closure (cross-sectional path bloqueado no
data layer) deixa um espaço estreito de candidatos:

- **#1 RECOMMENDED**: Broader-index VRP basket — extender iter
  026/039 a 5-leg SPY+QQQ+IWM+EFA+EEM at 1/5 each. Cache verificado
  pra EFA/EEM. Tests cross-region VRP diversification vs iter 039
  76-ceiling. `[volatility_trading, p.218]` + Bondarenko 2014. ~30-45
  min impl, predicted score 76-80.
- **#2**: Plano C sleeve eval (mandate-aligned) —
  GDE/AVUV/AVDE/AVEM/BTGD passive factor-tilted; ETFs jovens
  (2018-2024 inception) precisam FF93 long-format proxies pra
  educational. Documenta o baseline real do mandate maintenance.
  Predicted ≤ 70.
- **#3**: Carry + value composite AMP 2013 — soft retry da
  cross-sectional path com axes adicionais; SE score < 60, fechamento
  iter 054 confirmado totalmente.

## Cumulative state

- `cumulative_n_trials`: 4320 → **4324** (iter 054 testou 4 cfgs)
- Total iterations: 53 → **54**
- Winners: 0 (mandate consolidado em 100% Plano C; loop continua em
  background)
- Files: `studies/strategy_hunt_loop/iterations/054-2026-04-25-0919-tiingo-cross-sectional-momentum/`
  com `hypothesis.md`, `run_backtest.py`, `compute_gates_and_score.py`,
  `results.json`, `verdict.json`, `final_report.md`,
  `plot_vs_benchmark_spy_real.png`, `plot_vs_benchmark_ndx_real.png`.

## Citações

- `[stocks_on_the_move, p.76-77]` — 12-1 skip-1m momentum convention.
- `[advances_fin_ml, p.222-223]` — DSR cumulative n_trials.
- `[advances_fin_ml, p.196-202]` — bootstrap CI G6.
- `[advances_fin_ml, p.31-34]` — cross-lib parity G7.
- `[advances_fin_ml, p.208-211]` — PBO via CSCV.
- Jegadeesh, N. & Titman, S. (1993). JoF 48(1) 65–91.
- Carhart, M. M. (1997). JoF 52(1) 57–82 — UMD factor.
- Asness, Moskowitz & Pedersen (2013). JoF 68(3) 929–985.

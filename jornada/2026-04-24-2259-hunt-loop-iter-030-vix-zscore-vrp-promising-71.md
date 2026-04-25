# Hunt loop iter 030 — VIX z-score VRP-primary (R-2): primeiro 7/7 + DSR PASS no spy_real, mas Kill A+B triggered; estrutura single-axis VIX-gate fechada [HUNT LOOP]

**Data:** 2026-04-24 22h59
**Tipo:** [HUNT LOOP]
**Verdict:** 🥈 PROMISING (71/100; **3 marcos inéditos no spy_real, mas Kill A+B triggered**)
**Mandate:** §1 segue 100% Plano C MAINTENANCE — pesquisa em background, sem deployment.

---

## TL;DR

Iter 030 testou a **R-2 VIX z-score gate** sugerida por iter 029 — só
abrir o put credit spread se a deviation z-score do VIX sobre 60 dias
< 2σ. **Resultado dual mais agudo do loop**:

- **spy_real explodiu**: Sharpe 1.36 (vs iter 026 1.28; +0.080), **1ª
  vez 7/7 gates no dataset SPY**, **DSR p=0.0345 — 1ª passagem DSR
  sub-0.05 no spy_real em 30 iterações**. Marcos genuinamente
  inéditos.
- **educational regrediu**: Sharpe 1.14 (vs iter 028/029 ~1.27,
  −0.12) — Kill B triggered. O motivo é mecânico e foi
  pre-acknowledged no spec: o rolling-mean de 60d **absorve o spike
  inicial da GFC em ~3 meses**, então de Q4 2008 em diante o z cai
  abaixo de 2 mesmo com VIX em 50-60. O harvest escreve nesse regime
  e absorve realized > implied losses.
- **ndx_real regrediu mais ainda**: Sharpe 1.24 (vs iter 026 1.37,
  −0.131) — Kill A triggered **com margem 2.6× a thresholda**. Z-gate
  filtra 16 rolls em ndx vs 4 do iter 028 (level-only), porque tech
  é **muito sensível a relative shock** — modest VIX moves (22→26)
  já dão z>2 frequentemente.

Score **71/100 PROMISING** — empata iter 028 e iter 029 numericamente.

---

## A descoberta estrutural maior

**Três iterações sucessivas (028 / 029 / 030) testando três axes
ortogonais (level / level+persistence / z-score) todas convergem
em 71/100, cada uma produzindo o DSR record sub-0.05 num dataset
*diferente***:

| iter | gate axis | DSR record (dataset) | regressão custosa |
|---|---|---|---|
| 026 | nenhum (baseline) | ndx 0.0376 | — |
| 028 | level (VIX < 35) | **edu 0.0287** | spy −0.10 / ndx −0.07 (Kill A) |
| 029 | level + 3d persistence | **edu 0.0251** | spy −0.05 / ndx −0.07 (Kill A 2bp) |
| 030 | z-score (60d, 2σ) | **spy 0.0345** | edu −0.13 / ndx −0.13 (Kill A+B) |

Nenhuma iteração consegue sub-0.05 DSR em ≥ 2 datasets
simultaneamente — o record rotaciona por iteração. O motivo
empírico é o **dataset asymmetry** descoberto em iter 029: cada um
dos 3 datasets do hunt-loop tem uma estrutura de regime VIX
fundamentalmente diferente:

- **educational (2006-2026)**: dominado pela GFC sustentada (Q4 2008
  → Q1 2009 com VIX 40-80 por meses). Z-score falha aqui (mean
  catches up); level-gate captura. Persistence-gate captura também.
- **spy_real (2009-2026)**: post-GFC, dominado por innovation shocks
  (Mar-2020, 2018 vol-pop, Aug-2015) que são spikes-and-revert.
  Z-score acerta aqui; level-gate over-filtra.
- **ndx_real (2010-2026)**: post-GFC tech, baseline VIX baixo,
  events relativamente clusterizados. Iter 026 unfiltered captura
  premium decay nesses clusters; ambos level-gate e z-gate hurt.

**A família de single-axis VIX-gates no iter 026 base está agora
estruturalmente fechada.** Não há combinação de threshold dentro de
{level, persistence, z-score} que otimize todos 3 datasets.

---

## Hipótese e mecânica testada

**Citação primária:** `[volatility_trading, p.218]` — Sinclair
"VIX-VXV term structure": *sustained* high IV é o warning sign para
short-vol writers. Iter 028 testou interpretação literal (level
constante 35); iter 029 refinou para level + persistência; **iter
030 testou a interpretação de "sustained" como relative-shock**:
"sustentado" significa "z-score > 2 sobre rolling 60d", não nível
absoluto fixo.

Citações de suporte:
- `[volatility_trading, p.39]` — VIX vol-of-vol diária 0.96, semanal
  0.84, mensal 0.59 (1990-2011); motiva normalização por escala
  rolante.
- `[volatility_trading, p.58-59]` — volatility cone com 20/40/60/120/240
  dias; janela 60d é o canonical middle horizon.
- `[advances_fin_ml, p.31-34]` — G7 cross-lib parity.
- Whaley (2009) JPM 35(3) — VIX innovation analysis com standardized
  deviations.
- Bondarenko (2014) QJF 4(3) §3 — persistent vs transient regimes.
- Carr-Wu (2009) RFS 22(3) — VRP decomposition em level/persistence/
  innovation.

**Engine** (`vrp_zscore.py`, 263 linhas + numpy reference 175 linhas):
copia iter 029 com substituição da gate condition por lookup numa
série de z-score pré-computada. Z-score externamente computado a
partir do VIX full-history (1990-01-02 → 2026-04-14, 16 anos de
warmup buffer pré-educational), depois alinhado ao price index. Bar
warmup com NaN z → default to OPEN (não skip). Tests: 7/7 passing
incluindo reduce-to-parent (z_threshold=1e9 → iter 026 1e-12).

---

## Resultados completos por dataset

| dataset | Sharpe (Δ frozen / Δ026 / Δ028 / Δ029) | CAGR | MDD | gates | DSR p |
|---|---|---|---|---|---|
| educational | **1.139** (+0.46/+0.006/−0.121/−0.135) | 4.50% | 14.47% | 6/7 | 0.0820 |
| spy_real    | **1.362** (+0.46/+0.080/+0.181/+0.133) | 4.78% | **7.12%** | **7/7** ✨ | **0.0345** ✨ |
| ndx_real    | **1.237** (+0.28/−0.131/−0.064/−0.064) | 5.49% | 8.18% | 6/7 | 0.1010 |

Sharpe edge clears +0.10 gate em **3/3** datasets vs frozen benchmark
(C1 = 25/25). MDD ceiling cleared **3/3** (educational ainda 14.5%
vs ceiling 60.1% — o pior MDD de todas as iter VRP, mas ainda muito
abaixo do ceiling).

CAGR floor 0/3 — N=1 ceiling estrutural em ~5%/yr.

**Z-gate filter activity:**

- educational: 19 z-skipped vs 11 level-only (z capta vários false
  alarms 2010-2025 mas perde sustained Q4 2008)
- spy_real: 17 z-skipped vs 6 level-only (z captura quase
  perfeitamente os panic-and-revert events: 2015-Aug, 2018-Feb,
  Mar-2020, Apr-2025)
- ndx_real: 16 z-skipped vs 4 level-only (z over-fires em
  tech-conditional mini-spikes; muitas a VIX absoluto modesto
  como 22-26)

G7 cross-lib parity: **0.0000 pp** em 3/3 (machine-precision
pandas/numpy match).

---

## Score breakdown (frozen benchmarks, canonical)

| crit | pts | max | detalhe |
|---|---|---|---|
| 1 Sharpe edge | 25 | 25 | 3/3 (edu +0.46, spy +0.46, ndx +0.28) |
| 2 Gates | 21 | 25 | edu 6/7 (5) + **spy 7/7 (7)** + ndx 6/7 (5) + cross-bonus (4) |
| 3 DSR | 5 | 15 | worst p=0.1010 ndx (0.001 acima do 10-pt threshold) |
| 4 CAGR | 0 | 15 | 0/3 (4.5/4.8/5.5% vs floors 9.2/12.0/15.4%) |
| 5 MDD | 15 | 15 | 3/3 (14.5/7.1/8.2% vs ceilings 60.1/38.7/40.1%) |
| 6 Robustness | 5 | 5 | 9/9 sub-windows positivos |
| **total** | **71** | 100+5 | tier: **🥈 PROMISING** |

**Empata iter 028 e iter 029** mas com headlines qualitativamente
diferentes. Iter 028 escreveu "edu 7/7"; iter 029 escreveu "edu DSR
record"; **iter 030 escreve "spy 7/7 + spy DSR PASS"**. Three
iterations, three milestones, never simultaneously.

---

## Kill criteria (pre-committed em hypothesis.md)

| kill | critério | resultado | triggered? |
|---|---|---|---|
| **A** | Sharpe regress > 0.05 vs iter 026 spy OR ndx | spy +0.080 ✓, ndx **−0.131** | **YES** (ndx, clean 2.6× threshold) |
| **B** | Edu Sharpe < iter 028 − 0.10 (= 1.16) | 1.139 vs floor 1.160 | **YES** (clean 0.021 below) |
| C | 21d worst > 30% any | max −5.7% (ndx) | NO |
| D | G7 > 3pp any | 0.0000 pp 3/3 | NO |
| E | edu z-skips 0 | 19 skipped | NO |
| F | spy AND ndx z-skips 0 | 17/16 skipped | NO |

Kill A está no **clean falsification regime** (não knife-edge como
iter 029 que era 2 bp). Kill B é mais borderline (0.021 abaixo do
floor de 0.10) — pre-acknowledged no spec §4 como o risco central
da hipótese R-2.

---

## Próxima iteração — direções pós-iter-030

Pós-iter-030 a estrutura do dead-ends muda: **single-axis VIX-gate
family** está fechada. Restam:

1. **R-1+R-2 AND-composite (iter 031 STRONGEST)** — só skip quando
   `vix>=35 por 3 dias` AND `vix_z>=2`. A interseção deve ser muito
   seletiva (só GFC initial ramp + Mar-2020 + alguns clusters
   genuínos). Preserva edu (level captura sustained), preserva
   maioria do spy/ndx harvest (composto é mais permissivo que cada
   eixo isoladamente). Citação `[volatility_trading, p.217-218]` +
   Bondarenko 2014 §3.

2. **R-3 VIX > VXV term-structure** — qualitativamente diferente
   (signal market-derived, não historical-distribution). VXV
   começa 2007 → educational ~19y. `[volatility_trading, p.218,
   p.229]` + Carr-Wu 2009. Cleanest sustained-vs-transient signal
   na literatura.

3. **Z-score parameter sweep** (z ∈ {1.5, 2.5, 3.0} × window ∈
   {21, 120, 252}) — single-axis tightening; provavelmente outro
   71-tied result. **Lowest priority.**

**NOT recommended** (confirmed by this iter):
- R-1+R-2 OR-composite — agrega weaknesses, strictly pior.
- Single-axis level/persistence/z-score com wider parameter ranges
  — known to converge at 71 from iter 028/029/030.
- Combinar iter 027 leverage com qualquer iter 030 variant — rf
  dilution compõe spy/ndx damage.

**Pick prováve do iter 031:** R-1+R-2 AND-composite — único path
estruturalmente novo no VIX-gate family que ainda pode produzir
WINNER condicional aos 3 datasets.

---

## Comparação com iters anteriores (top-K stable)

Top-K #1 segue tripleempatado em 79: iter 016/018/021. Iter 026
mantém #5 a 76. Iter 030 não entra em top-K (71 < 76).

Mas iter 030 contribui o **2º DSR record real-data do loop** (após
iter 026): spy_real p=0.0345. Combinado com iter 026 ndx=0.038, o
loop agora tem sub-0.05 DSR validado em 2 dos 3 datasets reais —
falta só edu sub-0.05 simultaneamente (iter 028/029 alcançaram
edu sub-0.05 mas não junto com spy ou ndx).

---

## Status do projeto (mandate §1)

**MAINTENANCE 100% Plano C inalterado.** Hunt loop é background
research, não path para deployment ativo. Mesmo que iter 031 ou
posterior alcance WINNER (score ≥ 90 + 5/5 conditions), seria
CANDIDATE — deployment requer mandate §7 override separado.

Iter 030 contribui evidência incremental que o **VRP-primary
mechanism (iter 026 base) tem genuíno edge cross-dataset** (3 marcos
inéditos no loop em 30 iters), mas a versão otimizável requer
composite/multi-axis gates — não single-parameter.

---

## Arquivos do iter 030

- `studies/strategy_hunt_loop/iterations/030-2026-04-24-2259-vix-zscore-vrp-primary/`
  - `hypothesis.md` — spec pre-committed
  - `vrp_zscore.py` — engine pandas
  - `numpy_reference_zscore.py` — engine numpy (G7 parity)
  - `run_backtests.py` — runner 3 datasets
  - `compute_gates_and_score.py` — 7-gate + scoring + 6 kills
  - `results.json`, `verdict.json`
  - `final_report.md` (419 linhas)
  - `plot_vs_benchmark_spy_real.png`, `plot_vs_benchmark_ndx_real.png`
- `tests/test_iter030_vix_zscore.py` — 7 specs (todos passing)

Cumulative `n_trials = 4283` (4282 + 1 cfg novo).

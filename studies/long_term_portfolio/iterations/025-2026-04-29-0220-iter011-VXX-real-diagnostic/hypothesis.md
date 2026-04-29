# Iter 025 — iter 011 + 5% VXX real (diagnostic, NOT deploy candidate)

**Hypothesis slug**: `iter011-VXX-real-diagnostic`
**Direction**: B.3 (continuous tail-hedge with REAL deployable instrument)
**Cumulative n_trials at start**: 90 (post-iter 024)

## Citação primária

Spitznagel *Safe Haven* (2021) — convex tail-hedge thesis (Universa
Investments real implementation reports +1-2pp CAGR over 60/40, not +5pp
Sharpe).
`[advances_fin_ml, p.208-211]` — no-free-lunch sanity check via PBO + monotonic.

## Contexto — por que VXX real e não synthetic (iter 022)

iter 022 testou tail-hedge SINTÉTICO modelado e produziu score 100/100
(model artifact, NOT deployable). Esta iter substitui o synthetic por
**VXX real** (iPath Series B S&P 500 VIX Short-Term Futures ETN, BlackRock,
inception 2009-01-30) pra quantificar honestamente o gap entre modelo
sintético e produto live.

Esperado: falhar com edge negativo monotônico (mais VXX = mais decay).

## No-free-lunch sanity checks (PRE-RUN, observáveis nos dados)

| check | observed | expected | status |
|---|---|---|---|
| VXX standalone Sharpe | **-0.738** | < 0 | ✅ PASS — confirms decay |
| VXX standalone CAGR | **-51.34%/yr** | < -30% | ✅ PASS — brutal decay |
| VXX standalone MDD | **-100%** | < -90% | ✅ PASS — going to zero |

VXX é asset legitimamente destroyer of capital. Qualquer portfolio +signal
com adição linear de VXX precisa vir de descorrelação (positive em 2009
spike post-Lehman, 2020-Q1, 2022 corrections).

**Critical assertion — KILL #1 (red flag if violated)**: Sharpe
deve cair monotônicamente com VXX % (2.5% → 10%). Se Sharpe SOBE com
VXX %, há bug. Edge ≤ 0 esperado em todos os configs.

## 4 configs pre-committed

iter 011 base (35/25/40 NTSX/GDE/KMLM) + VXX substituído de KMLM:

| config | NTSX | GDE | KMLM | VXX |
|---|---:|---:|---:|---:|
| `vxx_lite_3525_375_25` | 35% | 25% | 37.5% | **2.5%** |
| `vxx_mod_3525_35_5`    | 35% | 25% | 35% | **5%** |
| `vxx_balanced_3525_325_75` | 35% | 25% | 32.5% | **7.5%** |
| `vxx_heavy_3525_30_10` | 35% | 25% | 30% | **10%** |

VXX substitui KMLM (não NTSX) pra preservar a base equity-cap-eficiente.

**Selection rule**: max mean(gross_Sharpe / SPY_Sharpe) sob NEW SPY-only.
Se TODAS as configs perdem vs iter 011 substantivamente, isolar a "least
bad" config como diagnostic; tier likely STRONG/PROMISING (not WINNER).

## Janela efetiva

VXX inception 2009-01-30 → effective window depends on dataset:
- **lh_56y**: VXX adds NaN pre-2009; loose convention treats as 0-weight
  (effectively iter 011 1986-2009 + iter 011+VXX 2009-2026)
- **vt_real**: 2008-06-01 → 2009-01-30 sem VXX, then 2009-01-30+ com VXX
  (~16y eff)
- **ndx_real**: 2010-02-01+ (full coverage)

Reportar strict (drop pre-2009) em final_report pra honestidade.

## Pre-committed KILLs

- **KILL #1 (no-free-lunch monotonic)**: Sharpe NOT monotonically
  decreasing 2.5%→10%. Se SOBE, há bug ou model leak.
- **KILL #2 (decay kill)**: edge ≤ 0 vs iter 011 em ≥2/3 datasets.
  Esperado FIRE — diagnostic value é ~quanto~ pior.

## Probabilidade advance

~5%. Decay structurally beats tail-hedge benefit at all weights. Valor: 
lição metodológica explícita (gap modelo sintético vs produto real).

## Saída esperada

- verdict.json com edge analysis explícita
- final_report.md detalhando gap iter 022 synthetic (+5pp Sharpe) vs
  iter 025 real (-X Sharpe, monotonic worse)

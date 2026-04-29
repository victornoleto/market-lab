# Iter 023 — TLT sleeve isolada bate iter 011 nos 3 datasets

**Data**: 2026-04-29 (UTC, 01:50)
**Iter**: 023, slug `iter011-plus-TLT-sleeve`, direção B.1 (TLT diversifier)
**Verdict**: NEW STRONG 86/100 winner_conds=True | LEGACY WINNER 91/100

## TL;DR

Pegamos o sub-achado da iter 020 (variante levered All-Weather era a
única do loop a bater iter 011 em ndx_real, 1.120 vs 1.104) e isolamos o
TLT sleeve sobre a base iter 011 (NTSX+GDE+KMLM). Em 4 configs sweep
TLT 15-30%, a config com **15% TLT preservando KMLM em 35%** venceu:
**Sharpe 1.189/1.004/1.135 (lh_56y/vt_real/ndx_real)**, batendo iter 011
em todos 3 datasets (loose +0.143/+0.044/+0.031) e — mais importante —
**MDD melhor em todos 3 datasets** (21/17/12% vs 26/21/14% do iter 011).

É o **primeiro positivo multi-dataset substantivo** desde iter 011 (iter 016
UMD foi positivo em 2/3 strict; iter 023 é positivo em 3/3 loose, 3/3 strict
positivos mas com 1/3 acima de +0.05 hurdle vs iter 011).

## Score

Sob NEW SPY-only mandate (reframing aprovado 2026-04-29):
- 25/25 Sharpe edge (3/3 datasets clear SPY+0.05)
- 21/25 Gates (PBO partial fail em vt_real e ndx_real)
- 15/15 DSR
- 5/15 CAGR floor (warning-only) — falha vt_real e ndx_real (10.13% e 10.62% < SPY 0.8×14.97% = 11.98%)
- 15/15 MDD ceiling (≤ SPY estrito) — passa todos
- 5/5 Robustness — 36/36 rolling 5y windows positivos
- **Total 86 → STRONG**

`winner_conditions_met=True` (4 condições NEW: Sharpe edge, gates, DSR, MDD —
CAGR é warning-only e não bloqueia). Score 86 < 90 → tier STRONG (não WINNER).

Sob LEGACY avg(SPY,VT) + 0.10:
- Tier WINNER 91/100 (5/5 conds met)

## Por que escolhi `tlt_mod_25_25_35_15` (e não as outras)

Selection rule sob NEW: max mean(gross_Sharpe / SPY_Sharpe) cross 3 datasets.
- `tlt_lite_30_25_30_15`: 1.382 mean
- **`tlt_mod_25_25_35_15`**: **1.395** ✅
- `tlt_balanced_30_25_25_20`: 1.380
- `tlt_heavy_25_20_25_30`: 1.378

Diferença 0.02 — borderline noise. Pre-committed kill #2 monitorava monotônico
TLT% → reverse pattern; não disparou pois pico em 15%, declínio em 20-30%.
KMLM-heavy (35%) preserva crisis-alpha; over-substituir KMLM por TLT custa
Sharpe nas live windows.

## Honesty checks

- **Loose vs strict lh_56y**: 1.189 loose vs 1.106 strict — gap 0.083 vem de
  pre-1986 rows (SPYSIM ainda NaN, NTSX-leg drops out, low-vol partial-stack
  infla Sharpe). Strict edge vs iter 011 = +0.061 (positive mas modesto).
- **CAGR drag**: 10.13% vt_real vs iter 011 10.95% (−0.82pp); 10.62% ndx_real
  vs 11.64% (−1.02pp). Trade-off documentado `[risk_parity, ch.5]`: sub vol
  alpha de duration por equity alpha → menos CAGR mas Sharpe e MDD melhores.
- **PBO 0.572/0.580 vt+ndx**: mesma família-level concern do iter 011
  (4 configs within 0.02 mean Sharpe → seleção within noise).

## Implicação pra o user

iter 023 é **mandate §7 override candidate**. Comparado a iter 011:
- pro: melhor MDD em todos 3 datasets (preserva mais capital em drawdowns)
- pro: Sharpe edge multi-dataset (loose +0.143/+0.044/+0.031 vs +0.000/+0.000/+0.000 baseline iter 011)
- con: CAGR cai 0.8-1.0pp em live windows
- con: score NEW 86 (4 pts shy de 90 WINNER) — driven by CAGR floor warning

Production deploy idêntico ao iter 011: NTSX (2018-09+) / GDE (2022+) /
KMLM (2020-12+) / TLT (2002-07+) via Inter Internacional, rebalance anual,
tax-perfect Lei 14.754/2023.

## Citações

- `[risk_parity, ch.5, p.10]` — Carlson capital-efficient stacking + TLT
- `[advances_fin_ml, p.208-211, p.222-223, p.196-202]` — PBO/DSR/Bootstrap
- iter 020 sub-finding: `aw_levered_NTSX_GDE_TLT` ndx_real 1.120

## O que vem a seguir

iter 024 (MDD-trigger defensive), iter 025 (VXX real diagnostic), iter 026
(MTUM real — confirmado data-limited dead-end pois MTUM não está em Tiingo
cache e API key vazia). Após as 4 sub-iters: re-rodar plots zoo, atualizar
STRATEGY_ZOO §3-§5, decisão final user.

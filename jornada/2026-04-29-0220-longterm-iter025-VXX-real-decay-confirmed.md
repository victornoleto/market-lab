# Iter 025 — VXX real diagnostic: decay confirmado, gap iter 022 quantificado

**Data**: 2026-04-29 (UTC, 02:20)
**Iter**: 025, slug `iter011-VXX-real-diagnostic`
**Verdict**: NEW STRONG 83/100 winner_conds=True | LEGACY WINNER 93/100

## TL;DR

Substituí o tail-hedge sintético da iter 022 (score 100/100 model artifact)
por VXX real do Tiingo (inception 2009-01-30). Pre-run sanity check confirmou
VXX standalone Sharpe = -0.738, CAGR = -51%/yr, MDD = -100% — asset legítimo
destroyer of capital.

KILL #1 (no-free-lunch monotonic) **PASS**: Sharpe DECRESCE monotonicamente
com VXX % em todos os 3 datasets (2.5%→10%):
- lh_56y: 1.107 → 0.982 (−0.125 over 7.5pp VXX)
- vt_real: 0.921 → 0.641 (−0.280)
- ndx_real: 1.097 → 0.854 (−0.243)

Selected `vxx_lite` 2.5% VXX (least-bad). Substantivamente vs iter 011:
- lh_56y +0.061 (loose, mostly noise)
- vt_real −0.039
- ndx_real −0.007

1/3 positive — DE-025 closes B.3 direction.

## Quantificação do gap iter 022 sintético vs iter 025 real

iter 022 modelo:
- lh_56y 1.520, vt_real 1.710, ndx_real 1.684 (10% hedge)

iter 025 real (10% VXX):
- lh_56y 0.982, vt_real 0.641, ndx_real 0.854

**Gap: 0.5-1.1 pontos de Sharpe overstated pelo modelo sintético.**

Razões do model failure (4 bugs já documentados em iter 022):
1. Modelo pagava premium fixo só fora de drawdowns (hindsight)
2. Sem custo de vega (puts ficam 5-10× mais caras em vol spikes)
3. Path-dependence errada (2× daily compound ≠ strike-spot at expiry)
4. Sem spread/liquidity drag

## Score

NEW: STRONG 83/100. Sharpe edge 20/25 (2/3 datasets pass +0.05 hurdle —
vt_real misses by 0.029). Gates 23/25 (6+7+7+3). CAGR 5/15 (warning).
winner_conds=True (4 active conds met).

LEGACY: WINNER 93/100 — sob LEGACY hurdle vt_real avg+0.10 = 0.807, iter 025
0.921 clears facilmente. Mostra como SPY-only mandate (NEW) é mais
discriminante: vt_real hurdle saltou de 0.807 → 0.950 (+0.143).

## Methodological honesty

iter 022 score 100/100 was 100% model failure. Real deployable tail-hedge
(VXX) gives marginal lh_56y win + vt/ndx losses + monotonic decay accumulation.
Spitznagel's Universa real-implementation reports +1-2pp CAGR uplift via OTM
puts + short-vol overlay — not the +5pp Sharpe of iter 022 model. iter 025
captures only the negative side of that ledger.

## Implicação pro user

iter 025 não é mandate §7 candidate. iter 023 TLT-static permanece como o
candidate forte do batch atual.

DE-025 logged: continuous VXX hedge sleeve structurally subordinate to iter 011.

## Citações

- Spitznagel *Safe Haven* (2021)
- `[risk_parity, ch.5, p.10]`
- `[advances_fin_ml, p.208-211]` PBO + monotonic
- iter 022 — gap explicit quantification aqui

# spy_beater iter 035 — primeira quebra REAL do teto via off-state KMLM (Principle N)

**Data:** 2026-04-30 13:42
**Iter:** 035 / 50
**Tier:** PROMISING — score **74/100** (NOVO APEX strategy-level)
**Bars:** 3/3 PASS, winner_conditions_met=True

## Resumo humano

A iter 035 testou um sub-axis ainda intacto em volta do iter 030 H10.4 (apex
sextuple-replicado): a **composição do off-state da constituinte de ouro**.
Até agora todo iter assumia que quando o GLD-momentum-126d gate fica OFF, o
"safe asset" é IEF (treasury intermediário), seguindo o canon Gayed.
Hipótese: e se for KMLM (managed futures crisis-alpha)? Ou TLT? Ou um blend?

Quatro configs com naming `..._ief_off`, `..._kmlm_off`, `..._tlt_off`,
`..._blend_off` — apenas o off_weights da 4ª constituinte muda; resto idêntico.

**Resultado-bomba:** H15.2 KMLM off scorou **74**, +2pt sobre o baseline IEF
de 72. **Primeira quebra REAL de teto strategy-level em 9 iters consecutivos
ao meta-ensemble axis** (iter 030 → 034 estavam todos amarrados em 72-73 com
ruído PBO grid).

## Por que é REAL e não outro PBO artifact (como iter 034)

Em iter 034, a "quebra" para 73 era artifact de grid-composition — a
estratégia era **idêntica** ao iter 030 H10.4, só sibling configs diferentes
flipparam o G1 PBO de FAIL para PASS. Per-dataset Sharpe 1.041/1.037 batendo
4 casas decimais.

Em iter 035, H15.1 (anchor IEF off) replicou iter 030 H10.4 EXATAMENTE
novamente (sextuple replication, 6 iters consecutivos com Sharpe 1.041/1.037
idênticos). Mas H15.2 KMLM off tem métricas DIFERENTES:
- Sharpe **+0.027** mean (1.066 vs 1.039)
- CAGR **+0.50pp** mean (17.09% vs 16.59%) — NOVO BEST IN HUNT
- MDD **−3.55pp** mean (30.22% vs 33.77%) — NOVO BEST IN HUNT
- MDD **idêntico nos dois datasets** (30.22% / 30.22%)

Ou seja, é uma estratégia DIFERENTE com vantagem strategy-level real.

## Princípio N — off-state crisis-alpha é asset-class-conditional

iter 016 (G1 hybrid) tinha estabelecido que para SPY-track gate, IEF >
Blend > KMLM no off-state. iter 035 mostra o **contrário** para GLD-track:
KMLM > Blend > IEF.

Mecanismo: GLD-trend-OFF coincide com regimes de USD-strength / global-macro-
trend (1995-2000 dot-com bull, 2013-2015 bear secular do ouro, 2018, 2022)
que managed-futures (KMLM per [ilmanen, ch.19]) capturam melhor que duração
passiva (IEF). Para SPY-track, OFF coincide com regimes equity-bear onde IEF
cash domina o catch-up risk do KMLM em recoveries rápidas.

Decomposição linear:
```
71 (E1qqq baseline iter 026) + 1 (Principle A: GLD orthogonal) + 2 (Principle N: KMLM macro-aligned off) = 74
```

Bate o resultado H15.2.

## Contradição com iter 034 e força do Principle M

iter 034 tinha enfraquecido todos os princípios anteriores ao mostrar que
deltas cross-iter de ±1pt eram artifacts de PBO grid. Aquele caveat continua
válido: o score 74 da iter 035 H15.2 também pode oscilar ±1pt em outro grid.
Mas o **edge strategy-level** (Sharpe / CAGR / MDD axes monotonicamente
melhores) é real e não-grid-dependente.

Resumindo: iter 034 PBO artifact = 0pt strategy-level; iter 035 KMLM off =
+2pt strategy-level genuíno. Diferença empírica clara via per-config raw
metric reproducibility.

## O que vem a seguir

Hunt **REABERTA** no axis off-state composition. Caminhos para iter 036+:
1. Cross-product: testar A2 / G2 / E1qqq off-state alternatives. Se
   Principle N generaliza, podem haver outros +1-2pt breaches.
2. 5-way structure com KMLM off em todas as constituintes orthogonais.
3. Manter o caveat de Principle M e considerar uma refatoração FIXED-GRID
   PBO antes de declarar a iter 035 H15.2 como deploy-candidate definitivo.

iter 035 H15.2 é deploy-candidato: CAGR 17.09% + MDD 30.22% (idêntico nos
2 datasets) + Sharpe 1.066 + DSR Bonferroni 8.08× margin (BEST IN HUNT) +
multi-horizon CAGR pass-rate 88.9%/100%/100%/100%. Caveat: KMLM off é NOVO
(não-Faber-canonical), OOS reliability em stress regimes (1973-74
estagflação, 1995-2000 dot-com bull, 2018 USD strength, 2022 inflation)
precisa sensitivity check antes de mandate §7 override.

Mandate §1 100% Plano C inalterado — research only. cumulative_n_trials = 136.

## Citações

- `[advances_fin_ml, ch.16, p.241-256]` portfolio construction multi-alpha
- `[ilmanen_expected_returns, ch.19]` MF crisis-alpha — fonte do Principle N
- `[leverage_for_the_long_run, ch.3-4, p.40-60]` Gayed canonical IEF off-state
- `[risk_parity, ch.5, p.10]` Carlson stack at 3rd position
- iter 016 G1 hybrid (off-state IEF > Blend > KMLM SPY-track — CONTRADITADO)
- iter 030 KILL #125 / Principle A (orthogonal signal-source bonus)
- iter 034 KILL #150 / Principle M (per-config reproducibility VALIDADO)

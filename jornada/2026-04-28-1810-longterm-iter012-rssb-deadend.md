# Long-term portfolio iter 012: NTSX + GDE + RSSB + KMLM — STRONG (88/100), 1ª tentativa de melhorar iter 011 — DEAD-END

Primeira iter pós-vitória do iter 011. Hipótese: trocar pedaço de KMLM por
**RSSB** (Return Stacked Stocks & Bonds, ~50% intl-equity + ~50% Treasury
empilhados via futuros, 2× nocional) pra atacar a ausência de exposição
global no incumbent. RSSB é a peça mais "literal" do tema "global +
factor" do usuário, dado que NTSI/NTSE não têm proxy testfolio.

## Resultado

Configuração selecionada: **`rssb_moderate_25252525`** (25% NTSX + 25%
GDE + 25% RSSB + 25% KMLM).

| dataset | gross Sharpe | edge vs avg(SPY,VT) | Δ vs iter 011 | gates |
|---|---:|---:|---:|---:|
| lh_56y    | 1.011 | +0.340 | **−0.035** | 6/7 |
| vt_real   | 0.851 | +0.144 | **−0.109** | 7/7 |
| ndx_real  | 1.021 | +0.097 | **−0.083** | 7/7 |

Tier WINNER **vs avg(SPY,VT)** (3/3 +0.10 edges, 5/5 strict conds), score
88/100 → STRONG por <90. **Mas perde Sharpe vs iter 011 em todos os 3
datasets.** Direção fechada.

## Por que falhou

`[risk_parity, ch.5, p.10]` Carlson explica que return-stacking só ganha
quando os blocos empilhados são **descorrelacionados**. RSSB tem ~50% de
**Treasury duration**, que **duplica** a exposição IEF que o NTSX já
embute (NTSX = 0.9 SPY + 0.6 IEF − 0.5 cash). O resultado é um portfólio
super-exposto a duration sem ganho de diversificação — exatamente o que
2010-2024 (rates rising 2022, IEF MDD 22%) penalizou.

A peça intl-equity dentro do RSSB também sofreu o "regime US-large-cap
dominante 2010-2024" — `[ilmanen, ch.19]` documenta esse premium intl
como dormant nesse período.

## Lição

DE-013 escrito em DEAD_ENDS.md. Ambiguidade aberta: a falha foi (a)
overlap de Treasury, (b) drag de intl-equity, ou (c) ambos? Iter 014
(VXUSSIM puro, zero Treasury) responderia.

Próxima iter: 013 — factor tilt sobre iter 011 (VBRSIM US small-cap
value).

Arquivos: `studies/long_term_portfolio/iterations/012-2026-04-28-1800-ntsx-gde-rssb-kmlm-global-stack/`

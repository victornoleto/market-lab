# Long-term portfolio iter 013: NTSX + GDE + KMLM + VBRSIM — WINNER tier (91/100), tied iter 011 — DEAD-END

Segunda tentativa pós iter 011. Hipótese: injetar **VBRSIM** (Vanguard
small-cap value proxy, factor sleeve US 1× nocional) sobre o stack iter
011 em 4 intensidades (10/20/25/30%), atacando a ausência de **factor
tilt** no incumbent. `[risk_parity, ch.2, p.37-41]` documenta size+value
como prêmios persistentes.

## Resultado

Configuração selecionada: **`factor_lite_30253510`** (30% NTSX + 25% GDE
+ 35% KMLM + 10% VBRSIM).

| dataset | gross Sharpe | edge vs avg(SPY,VT) | Δ vs iter 011 | gates |
|---|---:|---:|---:|---:|
| lh_56y    | 1.126 ⭐ | +0.455 | **+0.080** | 6/7 |
| vt_real   | 0.923 | +0.216 | **−0.037** | 7/7 |
| ndx_real  | 1.075 | +0.151 | **−0.029** | 7/7 |

Tier WINNER (5/5 conds vs avg(SPY,VT)), score 91/100 — **empata** com
iter 011 (91=91, não >). Não passa o gate "advance incumbent". Apenas
**lh_56y melhora**; live windows pioram.

## Padrão monotônico revelador

VBRSIM 10% → 30%: Sharpe lh_56y **sobe** monotônica (+0.060 → +0.085),
Sharpe vt_real **cai** monotônica (−0.04 → −0.14), Sharpe ndx_real
**cai** monotônica (−0.03 → −0.13).

Isso é o "death of value" pós-2008 documentado em finança acadêmica:
o prêmio value/size foi **forte 1970-2007** (visível no lh_56y) e
**dormant 2010-2024** (visível em vt_real / ndx_real). Constant-weight
factor tilt importa o premium morto sem mecanismo pra desligar quando
o regime muda.

## Lição

DE-014 escrito em DEAD_ENDS.md. Constant-weight factor tilt sobre iter
011 é estruturalmente subordinado em janelas deploy-relevantes (post-
2008). Próxima direção viável: **regime-conditional factor** (B.6) —
peso VBRSIM = f(value spread ou factor momentum). Mas iter 014 vai
primeiro testar VXUSSIM puro pra resolver a ambiguidade da iter 012.

Arquivos: `studies/long_term_portfolio/iterations/013-2026-04-28-1814-factor-tilt-on-iter011/`

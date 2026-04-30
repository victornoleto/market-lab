# Long-term portfolio iter 014: NTSX + VXUSSIM + GDE + KMLM — WINNER tier (93/100, mechanical incumbent), perde Sharpe vs iter 011 substantivamente

Terceira sleeve-injection pós iter 011. Hipótese: VXUSSIM (Total
International ex-US Stock Market, 1× nocional, **zero Treasury**) sobre o
stack iter 011 em 4 intensidades (10/20/25/30%). Resolve a ambiguidade
da iter 012: a falha do RSSB foi (a) overlap Treasury, (b) drag intl-eq
ou (c) ambos?

## Resultado

Configuração selecionada: **`intl_lite_35253010`** (35% NTSX + 10%
VXUSSIM + 25% GDE + 30% KMLM).

| dataset | gross Sharpe | edge vs avg(SPY,VT) | Δ vs iter 011 | gates |
|---|---:|---:|---:|---:|
| lh_56y    | 1.055 | +0.384 | **+0.009** (tied) | 6/7 |
| vt_real   | 0.885 | +0.178 | **−0.075** | 7/7 |
| ndx_real  | 1.052 | +0.129 | **−0.052** | 7/7 |

Tier WINNER (5/5 conds vs avg(SPY,VT)), score **93/100 > 91 da iter 011**
→ **mecanicamente** vira incumbent (regra "score >" da BASE_MEMORY).
**Substantivamente perde Sharpe vs iter 011 em vt_real e ndx_real**, só
empata em lh_56y. Score advance em parte é artefato de migração de
benchmark (iter 011 foi pontuada na janela legacy `educational`, iter
014 no novo `lh_56y` framework).

## Caveat substantivo

Para conversas de deploy-readiness, **iter 011 (NTSX+GDE+KMLM 35/25/40)
continua a referência arquitetural** — iter 014 difere apenas por trocar
10% de KMLM por 10% VXUSSIM e perde Sharpe nas 2 janelas live por essa
escolha. BASE_MEMORY documenta o caveat explicitamente.

## Resposta à ambiguidade da iter 012

VXUSSIM (zero Treasury) ajuda **modestamente** lh_56y vs RSSB
(1.055 vs 1.011) → overlap de Treasury contribuía. Mas VXUSSIM
**não recupera** o Sharpe de iter 011 em vt_real / ndx_real
(0.885 vs 0.960; 1.052 vs 1.104) → drag intl-equity em 2010-2024
é um eixo **independente** de falha. **Ambas contribuíram** pra falha
da iter 012. Resposta: ambiguidade resolvida.

## Padrão monotônico (3ª vez confirmado)

VXUSSIM 10% → 30%: Sharpe **cai monotônica em todos os 3 datasets**
(lh_56y −0.066, vt_real −0.141, ndx_real −0.135). Mais forte que iter
013 (que ajudava lh_56y monotônica). Intl-equity tilt é **menos
compatível** com iter 011 do que US factor tilt era.

## Lição estrutural — direção fechada

3 sleeve-injections seguidas (012 RSSB, 013 VBRSIM, 014 VXUSSIM) todas
falham vs iter 011 em janelas live. **Iter 011 é o teto arquitetural
para stacks de peso constante neste universo.** DE-015 escrito.

## Próximas direções (não constant-weight)

1. **A.1** — síntese NTSI/NTSE (proxy testfolio-style) pra destravar a
   tese literal do usuário "NTSX + NTSI + NTSE + GDE + KMLM". 1-2h infra.
2. **B.6** — factor tilt regime-conditional (VBRSIM com gate de value
   spread ou factor momentum). Pre-commit ≤3 configs pra evitar trap
   "regime gate on existing winner" (queimou no strategy_hunt_loop).
3. **C** — substituir, não aumentar (NTSX → NTSI inteiro; testar se a
   arquitetura de leverage transporta entre geografias).
4. Mecanismos qualitativamente diferentes (Antonacci GEM cross-class
   top-K, vol-managed 60/40 do archive).

Arquivos: `studies/long_term_portfolio/iterations/014-2026-04-28-1920-intl-equity-tilt-on-iter011/`

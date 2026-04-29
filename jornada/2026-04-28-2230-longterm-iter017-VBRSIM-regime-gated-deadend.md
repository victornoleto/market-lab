# Long-term portfolio iter 017: B.6 VBRSIM regime-gated — STRONG 82/100, **piora vs iter 013 constant-weight** (DE-017)

Sexta tentativa pós iter 011. Hipótese: gate binário na VBRSIM (peso 25% quando signal ON, 0% quando OFF, KMLM absorbe slack) recupera vantagem lh_56y de iter 013 sem o custo nas janelas live? Selected `vbrsim_value` (signal = VBRSIM 36m Sharpe > 0.5).

## Resultado: gate piora tudo

| dataset | iter 013 (constant) | iter 017 (gated) | Δ |
|---|---:|---:|---:|
| lh_56y | 1.126 | 1.043 | **−0.083** |
| vt_real | 0.923 | 0.884 | −0.039 |
| ndx_real | 1.075 | 0.967 | **−0.108** |

Score 82/100 (STRONG, não WINNER). Adicionar ~50bp de complexidade (o gate) custou −80bp de gross Sharpe lh_56y. **B.6 fechado** (DE-017).

## Por que falhou — clássico "regime-gate-on-existing-winner" trap

1. **Signal lag**: 36m Sharpe / 12-1m return ligam 6-12m DEPOIS do regime começar; perdem o reset inicial do premium.
2. **Whipsaw cost**: cada ON→OFF→ON é rebalance; +5-15bp/yr no deploy via DARF.
3. **Regime classification noise**: ~30y → CI largo nos Sharpe estimates → gate dispara em ruído.

Esse é exatamente o trap que PBO discipline (López de Prado p.208-211) foi projetado pra detectar. PBO não disparou aqui porque N=3 configs triggerou o warning de CSCV-instability do framework — mas a **degradação substantiva vs iter 013 É a resposta**.

## Conclusão family-level — B-direction agora FECHADA end-to-end

- **B.4** constant-weight VBRSIM (iter 013): tier WINNER, sem advance vs iter 011
- **B.5** UMD overlay direto (iter 016): WINNER 91/100, **única B-direction com real edge**
- **B.6** VBRSIM regime-gated (iter 017): STRONG, **pior que B.4**

**Só iter 016 (UMD overlay) tem edge substantivo na família B.**

## Próximo

Iter 018 — C.1 Antonacci GEM cross-class top-K (mecanismo qualitativamente diferente: dynamic em vez de static). Continuando a fila 016-022.

Arquivos: `studies/long_term_portfolio/iterations/017-2026-04-28-2200-B6-VBRSIM-regime-gated/`

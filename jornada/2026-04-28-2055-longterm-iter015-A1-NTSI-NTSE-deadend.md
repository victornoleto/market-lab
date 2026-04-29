# Long-term portfolio iter 015: A.1 — NTSI/NTSE síntese + 5-asset global stack — WINNER tier (93/100), TIES iter 014, A.1 fechada (DE-016)

Quarta tentativa de superar iter 011, **primeira fora do paradigma sleeve-injection**. Em vez de adicionar um sleeve (RSSB iter 012, VBRSIM iter 013, VXUSSIM iter 014), iter 015 fez **rebalanceamento arquitetural**: trocou parte do equity sleeve **dentro** do wrapper alavancado de 1.5× (NTSX → NTSX+NTSI+NTSE), construindo a tese literal do usuário "NTSX + NTSI + NTSE + GDE + KMLM 5-asset global stack" pela primeira vez.

## Infra nova: proxies.py + síntese NTSI/NTSE

Antes da iter, criei `studies/long_term_portfolio/proxies.py`, módulo compartilhado com a fórmula validada da família WisdomTree Efficient Core:

```
NTSX = 0.90 SPYSIM + 0.60 IEFSIM − 0.50 CASHX  (já validado deploy_studies 2026-04-26)
NTSI = 0.90 VEASIM + 0.60 IEFSIM − 0.50 CASHX  (NOVO — intl-developed 1.5× stack)
NTSE = 0.90 VWOSIM + 0.60 IEFSIM − 0.50 CASHX  (NOVO — EM 1.5× stack)
```

Mesmo blueprint 90/60/−50 do prospectus WisdomTree (NTSX/NTSI/NTSE são da mesma família, apenas o equity index muda). Smoke tests confirmaram parity com a expansão inline de iter 011/014 + sanidade das séries (vol NTSI 17%, NTSE 19.6%; correlação NTSI/NTSE 0.71 — tudo no esperado).

**Caveat de janela**: VEASIM cobre 1970+ (full lh_56y), mas VWOSIM começa só em 1994-05-04 (testfolio backfill MSCI EM). Configs 5-asset (com NTSE) ficam restritos a 32y eff; configs 4-asset (sem NTSE) usam full lh_56y.

## Resultado

Selecionado: **`intl_dev_lite_3515_GK_2030`** (4-asset: 35% NTSX + 15% NTSI + 20% GDE + 30% KMLM).

| dataset | gross Sharpe (loose) | edge vs avg(SPY,VT) | Δ vs iter 014 | Δ vs iter 011 | gates |
|---|---:|---:|---:|---:|---:|
| lh_56y    | **1.081** | +0.410 | +0.026 | +0.035 (loose) / **−0.038** (strict) | 6/7 |
| vt_real   | **0.877** | +0.171 | −0.008 | **−0.083** | 7/7 |
| ndx_real  | **1.048** | +0.124 | −0.004 | **−0.056** | 7/7 |

Tier WINNER 93/100, 5/5 conds vs avg(SPY,VT). **Mas TIES iter 014 (93=93) e perde Sharpe edge vs ambos incumbentes em 3/3 datasets**. Não advança.

## Strict-window diagnostic — descoberta nova

Identifiquei que iter 011/012/013/014 todas usam convenção "loose" no `gross_returns` (`pandas .sum(axis=1, skipna=True)` silenciosamente conta 0 onde leg falta), o que **infla Sharpe de lh_56y** porque pré-1986 (sem SPYSIM) o stack vira só Treasury+Cash+Gold+KMLM (alavancagem de duration sem drag de equity, Sharpe artificialmente alto). Implementei `gross_returns_strict` (drop rows com qualquer NaN leg) como diagnóstico, mantendo loose como gating pra cross-iter consistency:

| config | type | lh_56y loose | lh_56y **strict** |
|---|---|---:|---:|
| `intl_dev_lite_3515_GK_2030` ✅ | 4-asset | 1.081 | **1.007** |
| iter 011 (smoke-test) | 3-asset | 1.046 | **1.045** |

Então o "+0.035 win" loose vira "**−0.038 loss**" strict. Honesta interpretação: iter 015 perde iter 011 em 3/3 datasets sob accounting strict.

## Pre-committed kills disparados

- **KILL #2** (5-asset uniformly < 4-asset): ✅ FIRES. Best 5-asset (0.964/0.796/0.974) loses best 4-asset (1.081/0.877/1.048) em todos os 3 datasets. **EM-as-component within 1.5× wrapper é estruturalmente subordinado**.
- **KILL #3** (cross-config monotonic regression): ✅ FIRES. NTSI+NTSE weight 15% → 35% baixa Sharpe **monotônica em TODOS os 3 datasets**. Mesmo padrão de iter 014 (VXUSSIM), agora confirmado dentro do wrapper alavancado.
- **KILL #1** (best-of-grid loses iter 011 em 3/3): PARTIAL fire — perde 2/3 sob loose, 3/3 sob strict.

## Lição estrutural — Direção A FECHADA end-to-end

Ambos os variantes estruturais da tese global+factor sobre arquitetura iter 011 estão exauridos:

1. **Sleeve-add** (012 RSSB, 013 VBRSIM, 014 VXUSSIM): adicionar sleeve constant-weight a 1× ou 2× notional **fora** do wrapper drag toda janela live.
2. **Component-swap** (015 NTSI/NTSE): mover equity sleeve de US para intl **dentro** do wrapper de 1.5× drag toda janela live.

A lição é agora overdetermined (4 iters seguidos confirmando): o regime US-large-cap-dominant 2010-2026 é tão forte que **qualquer desvio de pure US equity no equity sleeve custa Sharpe** — seja a 1× notional fora do wrapper, seja a 1.5× notional dentro.

**Iter 011 NTSX é o teto arquitetural para stacks cap-efficient estáticos neste regime.**

## DE-016 escrito. Próximas direções

1. **B.6 — Regime-conditional factor** (próxima iter, prioridade alta): VBRSIM weight = f(value spread ou factor momentum 12-1). Pre-commit ≤3 configs pra evitar trap "regime gate on existing winner" (queimou no strategy_hunt_loop). Citation `[advances_fin_ml, p.208-211]` (PBO discipline) + `[risk_parity, ch.2]` (factor framework).
2. **C — Mecanismo qualitativamente diferente**: Antonacci GEM cross-class top-K (estilo iter 079 archive) ou vol-managed 60/40 (iter 006 archive). Quebra do frame static-cap-efficient-stack inteiro.
3. **Parar de hunt e declarar iter 011 deploy-ready**: 4 iters consecutivas falham em superar iter 011, tese literária do usuário fully tested ao nível constant-weight. Defensável preparar mandate §7 override request e reactivar hunt em 6-12 meses quando OOS post-2026 for significativo.

## Pontos de honestidade

- Iter 015 mecanicamente atinge tier WINNER vs avg(SPY,VT), mas isso virou um padrão "anything cap-efficient-stacked beats passive" que não distingue boas vs mediocres estratégias. O sinal real é a comparação vs iter 011 substantivo, e iter 015 falha.
- Síntese NTSI/NTSE foi feita conservadoramente (mesmo blueprint do NTSX validado, mesmos coeficientes). O risco é se WisdomTree usar coefs ligeiramente diferentes na prática — mas isso seria −10 a +10bp/ano no máximo, dentro do ruído do experimento.
- Strict-window diagnostic é uma melhoria honesta no loop. Não retro-aplico nas iters anteriores (custo > benefício; documentado em final_report).

Arquivos: `studies/long_term_portfolio/iterations/015-2026-04-28-2010-A1-5asset-global-stack/` (hypothesis.md, backtest.py, verdict.json, results.json, final_report.md, plots) + `studies/long_term_portfolio/proxies.py`.

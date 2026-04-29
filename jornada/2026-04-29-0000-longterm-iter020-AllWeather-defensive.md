# Long-term portfolio iter 020: C.3 All-Weather Bridgewater-mimic — STRONG 83/100, NOT WINNER (CAGR drag defensivo)

Nona tentativa pós iter 011. 4 variantes All-Weather: textbook (30/40/15/15 SPY/TLT/IEF/GLD, gold sub commodities), Browne permanent (25/25/25/25), levered (40 NTSX + 30 GDE + 15 KMLM + 15 TLT), inv-vol risk parity 4-asset.

## Resultado

Selected `aw_browne_25252525`. Gross Sharpe **1.114 / 0.984 / 1.097**, MDD **17.15% across all** (cleanest do loop). CAGR 6.6-7.65% — falha floor 3/3. Tier STRONG, **NOT WINNER**.

| dataset | gross S | CAGR | bench × 0.8 | gates | Δ vs iter 011 |
|---|---:|---:|---:|---:|---:|
| lh_56y | 1.114 | 6.61% | 8.58% ✗ | 7/7 | +0.068 |
| vt_real | 0.984 | 7.35% | 9.51% ✗ | 6/7 | +0.024 |
| ndx_real | 1.097 | 7.65% | 13.59% ✗ | 7/7 | −0.007 |

## Highlights da família

- `aw_inv_vol_4asset` lh_56y **1.143** — segundo maior Sharpe lh_56y do loop (atrás só de iter 016 UMD 1.223)
- `aw_levered_NTSX_GDE_TLT` ndx_real **1.120** — **única estratégia do loop a bater iter 011's ndx_real (1.104)**

Sub-iter futura interessante: testar "iter 011 + 15% TLT sleeve" como extensão direta (preserva CAGR de iter 011 + adiciona duration alpha).

## Padrão emergindo nas iters 019/020

Família "Sharpe-max defensivos" (vol-managed + All-Weather) entrega Sharpe excelente E MDD superior, mas CAGR cap'd em 6-10% — não fits mandate de 11-13% target deste loop. Para um mandato diferente (max-Sharpe / min-MDD), seriam vencedores claros.

## Status fila

| iter | resultado |
|---|---|
| 016 UMD overlay | **WINNER 91, único positivo** |
| 017 VBRSIM regime-gated | STRONG 82, dead-end |
| 018 Antonacci GEM | PROMISING 74, dead-end |
| 019 vol-managed 60/40 | STRONG 81, CAGR drag |
| **020 All-Weather** | **STRONG 83, CAGR drag (mas Sharpe/MDD top)** |
| 021 Sector rotation | próximo |
| 022 Tail-hedge | |

Arquivos: `studies/long_term_portfolio/iterations/020-2026-04-28-2340-C3-all-weather/`

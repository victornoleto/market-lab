# Long-term portfolio iter 019: C.2 vol-managed 60/40 — STRONG 81/100, NOT winner (CAGR floor fails 3/3)

Oitava tentativa pós iter 011. Mecanismo qualitativamente diferente: vol-targeting Carver style. Base 60% NTSX + 40% IEF (cap-eff 60/40), peso dinâmico = clamp(target_vol / realized_60d_vol, [0.5, 2.0]).

## Resultado

Selected `vt_8pct` (target_vol 8%, melhor Sharpe da família).

| dataset | gross S | edge vs avg(SPY,VT) | gross CAGR | bench × 0.8 | CAGR floor | Δ vs iter 011 |
|---|---:|---:|---:|---:|---|---:|
| lh_56y | 0.991 | +0.319 ✓ | 8.13% | 8.58% | ✗ | −0.055 |
| vt_real | 1.052 | +0.345 ✓ | 9.32% | 9.51% | ✗ | **+0.092** |
| ndx_real | 1.117 | +0.193 ✓ | 9.71% | 13.59% | ✗ | +0.013 |

Score 81/100, **tier STRONG, winner_conditions_met=FALSE** — Sharpe edge clears 3/3 mas CAGR floor falha 3/3.

## Tradeoff clássico de Carver

Lower target_vol = higher Sharpe, mas CAGR cai proporcional. Vol-targeting remove left-tail variance MAS também cap right-tail upside.

| config | target_vol | lh_56y S | vt_real S | ndx_real S |
|---|---:|---:|---:|---:|
| `vt_8pct` ✅ | 8% | **0.991** | **1.052** | **1.117** |
| `vt_10pct` | 10% | 0.989 | 1.047 | 1.102 |
| `vt_12pct` | 12% | 0.983 | 1.033 | 1.081 |
| `vt_15pct` | 15% | 0.967 | 1.012 | 1.065 |

Pra um mandato de long-term portfolio mirando 11-13% CAGR (range iter 011), 8-10% CAGR é deal-breaker mesmo com Sharpe limpo. Mecanismo funciona — só não bate o mandate desta loop.

## Continuando 016-022

| iter | resultado |
|---|---|
| 016 UMD overlay | **WINNER 91, único positivo** |
| 017 VBRSIM regime-gated | STRONG 82, dead-end |
| 018 Antonacci GEM | PROMISING 74, dead-end |
| **019 vol-managed 60/40** | **STRONG 81, CAGR drag** |
| 020 All-Weather | próximo |
| 021 Sector rotation | |
| 022 Tail-hedge | |

Arquivos: `studies/long_term_portfolio/iterations/019-2026-04-28-2320-C2-vol-managed/`

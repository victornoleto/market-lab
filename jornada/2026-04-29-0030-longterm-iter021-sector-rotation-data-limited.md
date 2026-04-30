# Long-term portfolio iter 021: C.4 sector rotation 4-asset — PROMISING 69/100, dead-end DATA-LIMITED (DE-021)

Décima tentativa pós iter 011. Sector rotation top-K monthly. Tiingo cache só tem 4 sectors com história completa 2003-08+ (XLE/XLF/XLK/XLU); outros 5 (XLB/XLI/XLP/XLV/XLY) começam 2014-01 — universo restrito.

## Resultado

Selected `sec4_K2_TLT` (K=2, fallback TLT).

| dataset | gross S | edge | CAGR | MDD |
|---|---:|---:|---:|---:|
| lh_56y | 0.708 | +0.037 ✗ | 12.58% | 42.79% |
| vt_real | 0.762 | +0.056 ✗ | 13.13% | 34.30% |
| ndx_real | 0.788 | −0.136 ✗ | 13.61% | 34.30% |

PROMISING 69/100, **NOT WINNER** (Sharpe edge gate falha 3/3, max +0.056). MDD 34-43% — pior do loop. vs iter 011 perde feio em todos os 3 (−0.34/−0.20/−0.32). KILL #1 fires hard.

## Caveat data-limited

4-sector universe é muito estreito: XLE/XLF/XLK/XLU todos compartem strong equity beta em crises (2008, 2020 March), então rotation não escapa drawdown switching dentro do universo. Fallback TLT só dispara quando TODOS os 4 sectors têm momentum negativo — só 2009/2020 brief windows.

**Teste inconclusivo mas viesado para fail**. Test apropriado precisaria 9-sector full universe (incluindo defensivos XLP/XLV/XLU/XLY/XLB/XLI) com history desde 1998 SPDR inception. Backfilling via Yahoo Finance é ~1-2h de infra deferida.

## Status fila

| iter | resultado |
|---|---|
| 016 UMD overlay | **WINNER 91, único positivo** |
| 017 VBRSIM regime-gated | STRONG 82, dead-end |
| 018 Antonacci GEM | PROMISING 74, dead-end |
| 019 vol-managed 60/40 | STRONG 81, CAGR drag |
| 020 All-Weather | STRONG 83, CAGR drag |
| **021 sector rotation 4-asset** | **PROMISING 69, dead-end data-limited** |
| 022 tail-hedge | última |

Arquivos: `studies/long_term_portfolio/iterations/021-2026-04-29-0010-C4-sector-rotation/`

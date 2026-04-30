# Long-term portfolio iter 018: C.1 Antonacci GEM cross-class — PROMISING 74/100, NOT WINNER (DE-018)

Sétima tentativa. Pivot real pra mecanismo qualitativamente diferente: monthly top-K cross-class momentum ao estilo Antonacci GEM. 4 configs em universos testfolio (5/6/7-asset × K=2,3).

## Resultado

Selected `gem_6asset_K2` (SPY/QQQ/VEA/TLT/GLD/KMLM, K=2, fallback KMLM se top-2 momentum negativo).

| dataset | gross S | edge vs avg(SPY,VT) | Δ vs iter 011 | gates |
|---|---:|---:|---:|---:|
| lh_56y | 0.763 | +0.092 ⚠️ | **−0.283** | 5/7 |
| vt_real | 0.888 | +0.182 ✓ | −0.072 | 7/7 |
| ndx_real | 0.889 | −0.035 ✗ | **−0.215** | 6/7 |

**Score 74/100, tier PROMISING, winner_conditions_met=FALSE** (Sharpe edge gate falha: só 1/3 datasets clear +0.10). KILL #1 fires.

## Por que falha — 3 razões

1. **Equity-dominant regimes punem switching**: 2010-2024 foi 14y de US-equity dominance. GEM rotaciona corretamente pra SPY mas custos de checks mensais (whipsaw + DARF) comem o gross edge.
2. **Long-history expõe a fraqueza**: iter 011's 1.046 lh_56y domina GEM's 0.76 por margem grande. Static stack com KMLM crisis-alpha captura mesma proteção sem decision noise mensal.
3. **vt_real-only positive**: 17y window tem GFC + 2020 + 2022 — três regime shifts onde switching ajuda, mas window muito estreita pra generalizar.

## Comparação interessante: iter 079 archive era strict winner

iter 079 do strategy_hunt_loop (multi-asset top-K cross-class momentum) foi 5/5 winner com Sharpe 1.094 em SPY-Tiingo 17y. Por que iter 018 falha?

- **Universo**: iter 079 testou 8-12 diversificadores de equity; iter 018 só 5-7 broad classes
- **Janela**: iter 079 só vt_real-style (Tiingo 17y); iter 018 inclui lh_56y onde long stretches de equity dominance penalizam switching
- **Lookback**: iter 079 pode ter usado 1m/3m; iter 018 usa 12-1m (Antonacci classic, conhecido por lag em rapid regime shifts)

## Estado da fila 016-022

| iter | direção | resultado |
|---|---|---|
| 016 | B.5 UMD overlay | **WINNER 91, primeiro positivo** |
| 017 | B.6 VBRSIM regime-gated | STRONG 82, pior que iter 013 |
| **018** | **C.1 Antonacci GEM** | **PROMISING 74, NOT winner** |
| 019 | C.2 Vol-managed 60/40 | próximo |
| 020 | C.3 All-Weather | |
| 021 | C.4 Sector rotation | |
| 022 | C.5 Tail-hedge | |

Arquivos: `studies/long_term_portfolio/iterations/018-2026-04-28-2245-C1-Antonacci-GEM/`

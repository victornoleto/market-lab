# Phase D-MVP — BREADTH_NO_WINNER_D (aborted at 10/42)

**Data:** 2026-04-23 00:44
**Verdict:** `NO_WINNER_MVP` (partial grid — aborted)
**Cumulativo honest FAIL:** **71/71** (era 60/60 pre-Phase D-MVP)

## O que aconteceu

O pipeline `run_end_to_end` disparado em 2026-04-22 19:04 rodou por 5h30min
e completou 10 configs de 42 antes do usuário voltar (23/04 00:32). Tempo
esperado: 2-3h; tempo real extrapolado: **17-20h**. Causa: cada
`run_split` recarrega os 83 parquets OHLCV do disco + Runner itera ~330k
bar-evaluations por run. I/O-bound.

Mas o ritmo lento não foi o problema. O **conteúdo dos 10 configs** foi:

- **10/10 configs têm Sharpe OOS NEGATIVO** (−0.11 a −0.56).
- **Median decay IS→OOS = −1.06 Sharpe** — classic regime-break signature.
- **Median OOS MDD = 65.6%** — Reject tier no mandate §2.3.
- **Median OOS CAGR líquido = −19%** (pior que deixar em CDI!).
- PBO = **0.238 PASS** mas DSR **0/10 FAIL** (p ≈ 1.0 em todos).

Rodar os 31 configs restantes (14+ horas de CPU) só confirmaria o que
está visível: **D1 Clenow momentum em IBrX-100 não tem edge OOS**.

## Por que isso era previsível

**IS (2010-2019) Brasil:**
- Commodity super-cycle tail (Vale, Petrobras, Gerdau mandavam)
- Selic caindo 14% → 6% (multiplos expandiram)
- Pro-market pós-impeachment Dilma

**OOS (2020-2023) Brasil:**
- COVID crash março/2020 (IBOV −45% em semanas)
- Lula 2.0 uncertainty premium
- US tariff war + China slowdown fode commodity exporters
- Selic spike 2% → 13.75% comprime múltiplos equity
- **Os winners do IS viraram losers no OOS**

Cross-sectional momentum Clenow-style assume **persistent relative
strength**. Regime flip como esse literalmente inverte o sinal: comprar
os fortes do último trimestre vira comprar os que vão cair no próximo.

`[advances_fin_ml, p.31-34]` chama isso de "regime break overfitting" —
gate PBO pode até passar (ranking estável) mas DSR pune porque o nível
absoluto OOS é estatisticamente noise ou pior.

## Cumulativo de honest FAIL do projeto (71 total)

| Phase | Leads | FAIL |
|-------|-------|------|
| 3.5f V2 Plano A | 6 | 6/6 |
| 3.6 broader hunt | 10 | 10/10 |
| 3.7-3 top-tier lit | 8 | 8/8 |
| 3.8-1 Gayed canonical | 5 | 5/5 |
| 3.6 families (older) | 32 runs | contados acima |
| **D-MVP (D1 parcial)** | **10** | **10/10** |
| **Total** | — | **71/71** |

Não achamos um único winner em 2 semanas + 33 livros absorvidos + engine
cross-lib validada. **Isso é estatisticamente esperado** (Harvey & Liu
2015 JOIM: >80% dos factors publicados não sobrevivem multiple-testing),
mas é honesto reconhecer que retail com capital limitado enfrenta
realidade dura:
- Spreads 15-50 bps BR absorvem edge retail
- Universo pequeno (100 tickers IBrX, 20 Pepperstone) limita diversificação
- Sem alt-data / sem co-location / sem prime brokerage
- 2 semanas a 10h/dia é amostra pequena de hypotheses, mas suficiente
  pra ter tentado os 5-6 factors robustos globais sem encontrar um vivo

## Próximos passos — executando nesta sessão (próximas 8h)

Usuário foi dormir 00:40, volta 08:30. Plano autorizado:

1. **Etapa 1 (AGORA):** BREADTH_NO_WINNER_D + jornada + commit. Feito.
2. **Etapa 2 (~1h):** otimizar engine (pre-load OHLCV 1× shared) + criar
   `scripts/phase_e_mvp/` pra Strategy E multi-market (SP500 top-200 +
   Russell 2000 top-200 + IBrX-100 = ~500 tickers).
3. **Etapa 3 (~4-5h):** rodar grid Strategy E — mesmas famílias D1+D4 em
   universo multi-market com engine acelerada.
4. **Etapa 4 (opcional, ~1h):** Lead D2 Magic Formula em US (fundamentals
   via `yfinance.Ticker().info`).
5. **Etapa 5:** relatório consolidado + recomendação honesta.

**Se Strategy E também FAIL** (possível; mesmas famílias de signal com
universo maior mas mesmo regime-shift 2020+ global), a recomendação honesta
vira **consolidar Plano C passive 60-80% buy-hold e parar de caçar alpha
ativo**. Mathematically optimal pro retail com capital < $1M. Não é
derrota; é o mercado mandando o sinal certo.

## Artefatos

- `reports/phase_d_mvp/BREADTH_NO_WINNER_D.md` — tabela + análise
- `reports/phase_d_mvp/partial_dsr.json` — DSR por config
- `reports/phase_d_mvp/partial_pbo.json` — PBO aggregate
- `reports/phase_d_mvp/d1_*/IS.json + OOS.json + *_equity.parquet` — raw

## Referências

- Spec: `specs/strategy_d_br_ranking.md`
- Plano: `/home/victor/.claude/plans/zazzy-booping-oasis.md`
- Mandate: `docs/investment-mandate.md §4b`
- Mandate override: `docs/mandate_overrides/2026-04-22-strategy-d-open.md`

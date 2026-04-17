# Phase 3.5b Task 7e [PLANO B] [SWING BROKER] — Rolling correlation PASS

**Data:** 2026-04-17 17:45
**Branch:** `phase3.5b/winners-validation-20260417`
**Iter:** 12

## Contexto

Task 7e do `specs/phase_3_5b_winners_validation.md` pede para medir
a correlação rolling entre as 3 pernas do portfolio winner (LETF
EMA100/2x × QQQ Donchian 20/10 × GLD Donchian 40/20) em duas janelas
(63d e 252d) e identificar períodos em que a diversificação
**quebra** — i.e., quando todas as correlações pairwise sobem
simultaneamente acima de 0.7. Tarefa é cruzada pela literatura
institucional de risk monitoring `[advances_fin_ml, p.289-293]` e
pela observação de Ang `[ang_asset_pricing, ch.12]` de que
correlações tendem a 1 em tail events — se isso acontecer no nosso
portfolio, a tese de 3-leg EW seria falsificada.

## O que foi feito

1. **Módulo `src/ai_trade/backtest/metrics/rolling_correlation.py`**
   (~385 loc):
   - `pairwise_rolling_correlations(a, b, c, window)` → `DataFrame`
     com 3 colunas nomeadas a partir de `series.name` (`{A}_vs_{B}`,
     `{A}_vs_{C}`, `{B}_vs_{C}`). `min_periods=window` (primeira
     janela inteira exigida).
   - `summarize_pair(series, window, threshold)` → `PairwiseRollingStats`
     com mean/median/std/min/p25/p75/max/last + `frac_above_threshold`
     + `longest_streak_above` (run-length scan booleano puro).
   - `find_high_correlation_regimes(rolling_df, window, threshold,
     min_bars)` — escaneia streaks **onde TODAS as 3 colunas** estão
     simultaneamente ≥ threshold por pelo menos `min_bars` barras.
     Retorna lista de `HighCorrelationRegime` com start/end/bars + ρ
     média por par no streak. Regime = "diversificação quebrou".
   - `compute_rolling_correlation_report(letf, qqq, gld, windows=...,
     threshold=0.7, min_regime_bars=10)` — end-to-end: alinha via
     `align_returns_3()` já existente, calcula a matriz 2 windows ×
     3 pairs, serializa tudo num `RollingCorrelationReport` (inclui
     `series: dict[window, DataFrame]` para exportar CSV).
   - `render_rolling_correlation_markdown(report)` — header + tabela
     de stats + tabela de regimes (ou placeholder "nenhum regime").
   - **Sem simulação, sem IO** — módulo puro, testável sozinho.

2. **17 testes unitários** em `tests/test_rolling_correlation.py`:
   - constantes canônicas (`(63, 252)` e `0.70`);
   - nomes de coluna seguem `.name` das series;
   - `ρ=+1` quando a==b, `ρ=−1` quando b=-a;
   - rejeição de `window<2` e índices desalinhados;
   - streaks alternados, empty series, regime found vs filtered by
     `min_bars`, regime só dispara com **3 de 3 acima** (2/3 não conta).
   - integração end-to-end com 2 fixtures: (i) LETF≈QQQ via
     common-noise + GLD independente → stats coerentes, zero regime;
     (ii) 300 bars independentes + 200 bars common-factor → regime
     detectado na cauda.

3. **Driver `scripts/run_rolling_correlation.py`** — carrega SPX TR
   stitched 1970-2026, roda os 3 winners em config congelada (Phase 3
   iter 32/36/37/40), calcula o report, emite:
   - `reports/phase3_5b/robustness/rolling_correlation.md`
   - `reports/phase3_5b/robustness/rolling_correlation.json`
   - `reports/phase3_5b/robustness/rolling_correlation_63d.csv`
   - `reports/phase3_5b/robustness/rolling_correlation_252d.csv`

## Resultado (common window 2004-11-18 → 2026-04-14, 5383 bars, GLD-limited)

| pair | window | bars* | mean | max | frac≥0.70 | streak |
| --- | --- | --- | --- | --- | --- | --- |
| LETF_vs_QQQ | 63 | 5057 | **0.612** | 0.963 | **31.4%** | **133 d** |
| LETF_vs_QQQ | 252 | 5132 | **0.598** | 0.778 | **13.9%** | **216 d** |
| LETF_vs_GLD | 63 | 4284 | 0.044 | 0.885 | 0.5% | 21 d |
| LETF_vs_GLD | 252 | 5132 | 0.053 | 0.305 | 0.0% | 0 |
| QQQ_vs_GLD | 63 | 4301 | 0.030 | 0.643 | 0.0% | 0 |
| QQQ_vs_GLD | 252 | 5132 | 0.032 | 0.228 | 0.0% | 0 |

\* `bars` < 5321 (teto 63d) nas linhas GLD porque Donchian fica cash
por janelas > 63d em diversos períodos — variância zero → ρ indefinido
→ NaN, corretamente ignorado pelas stats.

**Regimes (todas as 3 correlações ≥ 0.70 ao mesmo tempo, ≥ 10 barras):
ZERO.**

## Interpretação

1. **Diversificação sobrevive 21.4 anos incluindo 2008, 2011, 2020,
   2022 e 2025-Q1.** O portfolio NUNCA entrou num regime onde as 3
   pernas andaram juntas acima de 0.70 por mais de 10 dias — nem no
   pico pânico COVID nem no bear 2022 dos hikes. GLD permanece
   genuinamente descorrelacionada das duas pernas equity (ρ 252d
   **jamais** acima de 0.305 vs LETF, 0.228 vs QQQ).

2. **LETF ↔ QQQ é correlacionada por construção** (mean 252d 0.598,
   max 0.778, 216-day streak acima de 0.70). Esperado: ambas são
   TSMOM sobre equity US, entram long quando o regime é bullish.
   Não é falha de diversificação — é "mesma classe de ativo, sinais
   diferentes". O verdadeiro hedge do portfolio é GLD.

3. **GLD é o diversificador** e está cumprindo papel. Na janela de
   252d as correlações com equity flutuam [-0.239, 0.305] e
   [-0.198, 0.228], ambas bem dentro do zero-ish esperado. Picos de
   63d (ρ=0.885 LETF-GLD) são ruído de janela curta, não regime —
   o streak máximo simultâneo 63d é só 21 dias, e quando olhamos
   janela maior essa estrutura se dissipa.

4. **Implicação para allocation:** EW a 33% cada leg permanece
   justificado. Task 7d já tinha escolhido EW por Sharpe+DR; Task 7e
   mostra que não há razão de overweight defensivo em GLD —
   diversificação já está plena na config atual. Se a diversificação
   QUEBRASSE num subset temporal, poderíamos considerar
   correlation-adaptive weights; mas não quebrou, então a
   simplificação EW é ótima.

## Verdict

**PASS (7e).** Diversificação do portfolio 3-leg preservada através
dos regimes testados. Winners Phase 3 permanecem inalterados.

## Artefatos

- `reports/phase3_5b/robustness/rolling_correlation.md`
- `reports/phase3_5b/robustness/rolling_correlation.json`
- `reports/phase3_5b/robustness/rolling_correlation_63d.csv`
- `reports/phase3_5b/robustness/rolling_correlation_252d.csv`
- `src/ai_trade/backtest/metrics/rolling_correlation.py`
- `scripts/run_rolling_correlation.py`
- `tests/test_rolling_correlation.py`
- Pytest 632 → 649 (+17 novos testes, todos green).

## Próximo passo

Task 7f: position sizing alternativo (vol-target 10% no portfolio)
vs EW cash-neutral.

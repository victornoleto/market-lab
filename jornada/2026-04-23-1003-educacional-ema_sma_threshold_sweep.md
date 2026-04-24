# 2026-04-23 — Estudo educacional: EMA/SMA threshold crossover em SPY com LETFs (com post-mortem)

## O que foi feito

Implementei um **sweep educacional** de 384 configs (SMA/EMA × lookback ×
threshold × buy_leverage × sell_leverage) rodando em SPY synth (SPYSIM,
1986-2026, 40 anos). Ranking por **composite score** `0.4·rank(CAGR) +
0.4·rank(Sharpe) + 0.2·rank(1/|MDD|)` com gates informacionais (não-bloqueantes).

Arquivos novos:

- `specs/ema_sma_threshold_educational.md` — spec com citações.
- `src/ai_trade/backtest/strategies/ema_sma_threshold_educational.py` —
  simulador return-series com **regime honesto** (yesterday's regime earns
  today's return).
- `src/ai_trade/backtest/grid/ema_sma_threshold_grid.py` — orquestrador
  (cartesian + métricas + 7 gates + composite score).
- `scripts/run_ema_sma_threshold_sweep.py` — CLI com `--smoke`, `--full`,
  `--skip-gates`.
- `tests/test_ema_sma_threshold_educational.py` — 17 testes (incluindo
  regression test que trava alinhamento honesto).
- `reports/educational/ema_sma_threshold/` — report.md (top-20),
  configs.csv, summary.json, equity/ (top-10 parquets).

## Post-mortem: bug de look-ahead (descoberto e corrigido)

**Versão 1** do simulador tinha o mesmo padrão de look-ahead do bug que o
projeto já havia pego no Phase 3.5f (`plano_a_leveraged_rotation.py`
commit `7b90a8f`): `regime[t]` (decidido observando `close[t]` vs `MA[t]`)
era pareado com `return[t]` (que é `close[t]/close[t-1] − 1` — o movimento
DURANTE o dia t). A posição "sabia" se o dia tinha fechado acima ou abaixo
da MA antes de apostar nele.

**Teste A/B (config EMA-50 + threshold 0% + 3x long + 1x short, 40 anos)**:

| Versão | CAGR | Sharpe | MDD | Equity final |
|---|---|---|---|---|
| A — com lookahead (v1) | +189% | 3.17 | 22% | × |
| B — honest (v2, fixed) | +5.97% | 0.34 | 86% | ÷ 3.65 · 10¹⁷ |
| C — SPY buy-hold | +11.47% | 0.68 | 55% | — |

A inflation ratio A/B = 3.65 × 10¹⁷. O usuário pegou na leitura do report
("CAGR 189%???? REVISE O BACKTEST!"). Fix: mesmo padrão usado em
`plano_a_leveraged_rotation.py` — aplicar `prev_regime` (decidido no close
de ontem) a `return[t]` (o retorno que ocorreu durante hoje), depois pagar
o switch cost se houver mudança de regime, e atualizar
`prev_regime ← regime[t]` para amanhã. Cite `[advances_fin_ml, p.31-34]`.

**Teste regression** (`TestLookaheadAlignment.test_yesterdays_regime_earns_todays_return`)
trava o fix: numa série hand-crafted onde o preço sobe 20% exatamente no
dia da cruzada, a estratégia com alinhamento honesto termina em 1.0
(não pegou a subida — o sinal só aparece no fechamento do dia da subida,
e vai capturar retornos a partir de amanhã), enquanto a versão lookahead
terminaria em 1.20.

**Nota importante** (fora do escopo deste sweep mas digna de ROADMAP): o
pattern em `letf_rotation.py` (Gayed LRS, base do Plano B Phase 3.8-1) é
o mesmo. O commit `7b90a8f` só patchou `plano_a_leveraged_rotation.py`.
Se esse módulo tiver o mesmo bug, os reports Plano B históricos estão
inflados pela mesma razão — **mas Plano B já veio de 5/5 FAIL nos gates
honest**, então re-rodar não muda o veredito. Vale flagar pro próximo
ciclo de maintenance.

## Verdict do Run (384 configs, pós-fix)

**Benchmark SPY buy-hold** (1986-2026): CAGR 11.47%, Sharpe 0.68, MDD −55.14%.

**Top-5 honest pelo composite score**:

| rank | cfg | CAGR | Sharpe | MDD | gates |
|---|---|---|---|---|---|
| 1 | EMA-150 + threshold 5% + 3x long + cash | +27.67% | 0.84 | −54% | 6/7 |
| 2 | EMA-150 + threshold 5% + 2x long + cash | +19.23% | 0.83 | −39% | 6/7 |
| 3 | SMA-200 + threshold 2% + 3x long + cash | +24.71% | 0.79 | −58% | 6/7 |
| 4 | EMA-100 + threshold 5% + 3x long + cash | +26.74% | 0.83 | −63% | 6/7 |
| 5 | EMA-100 + threshold 5% + 2x long + cash | +18.55% | 0.82 | −48% | 6/7 |

**Gates (7 informacionais)**:
- PBO passa 384/384 (a própria grid, não por config).
- DSR passa **18/384** (vs 195/384 lookahead-inflated).
- Walk-Forward 6/8 passa **0/384** — nenhum config sobrevive 8 janelas
  2y IS + 6mo OOS com MDD ≤ 25% e ≥ 75% profitable.
- OOS 70/30 Sharpe > 0: 248/384.
- FWD post-2020 Sharpe > 0: 258/384.
- Bootstrap 99.9% CI low > 0: 109/384.
- Cross-lib ±3pp CAGR: 384/384 (hand-rolled e vectorized concordam).
- **0 configs passam 7/7** (antes do fix: 42 configs falsamente passavam).

## Interpretação honesta

Os números pós-fix são coerentes com a literatura:

1. **Trend-following com LETF em SPY não entrega mágica** — top-5 entregam
   CAGR 19-28% com leverage 2x-3x, i.e. não muito melhor do que o próprio
   multiplicador aplicado ao buy-hold. Sharpe melhora marginalmente vs
   SPY (0.8 vs 0.68), mas não dramaticamente.
2. **Threshold 5% + lookback 100-200 dominam** — banda anti-whipsaw
   `[leverage_for_the_long_run, p.11]` funciona mesmo.
3. **Cash no off domina sobre short alavancado** — short LETF carrega
   custo estrutural (fee drag + vol drag + muitas whipsaws) que na
   maioria das 40 anos bull-dominantes não compensa.
4. **Gayed canônico (SMA-200 + 0% + 2x/3x + cash)** aparece em ranks
   8/12/20 do top-20 — consistente com o paper, mas não top-1.
5. **MDD ~50-70% é a norma** — drawdown não é reduzido por leverage +
   regime filter no nosso 40y window. Consistente com `project_phase_3_7_3_complete`:
   Plano B BREADTH_NO_WINNER.

## Reorganização + tax 15% (update 2026-04-23 11h12)

Após o fix de lookahead, o usuário pediu estrutura dedicada para este
estudo e análise comparando "puro" vs "15% DARF swing":

- Pasta `studies/ema_sma_threshold_educational/` criada com:
  - `SPEC.md` (movido de specs/)
  - `run_sweep.py` (movido de scripts/)
  - `configs/NN_<cfg_id>/` — 20 subpastas pros top configs, cada uma com:
    - `summary.md` — métricas pure + tax15 vs SPY, tabela detalhada de
      gates (PASS/FAIL por gate, não só X/7), estatísticas de trades
      por leg.
    - `equity.png` — matplotlib log-scale: 3 curvas (strategy pure,
      strategy tax15, SPY buy-hold).
    - `trades.csv` — ledger completo de regime-blocks com pure+tax15
      lado-a-lado (entry/exit equity, pnl %, tax paid).
  - `FINAL.md` — ranking top-20 em ambas as escalas (pure e tax15),
    archetypes, narrative conclusions.
  - `configs.csv` + `summary.json` — dados brutos de todos 384 configs.
- Simulator estendido com `tax_rate` + lista de trades (regime blocks).
- Tax aplicada mirror `letf_rotation.py`: 15% sobre gain em cada saída
  lucrativa de regime (approximação worst-case, sem isenção R$20k/mês).
- Re-rodado: sweep pure (6 min + gates) + sweep tax15 (10s, só métricas
  — mesma sequência de regimes).
- Pytest: 1097 passed, 17/17 tests desse estudo (incluindo regression
  do lookahead) — **sem regressão**.

### Melhores estratégias (pós-tax, top-5 por composite tax15)

| rank | cfg | CAGR pure | CAGR tax15 | Δ tax | Sharpe tax15 | gates |
|---|---|---|---|---|---|---|
| 1 | EMA-150 + th=5% + 3x long + cash | 27.67% | **25.03%** | 2.64% | 0.78 | 6/7 |
| 2 | EMA-150 + th=5% + 2x long + cash | 19.23% | 17.21% | 2.03% | 0.75 | 6/7 |
| 3 | SMA-200 + th=2% + 3x long + cash | 24.71% | 21.42% | 3.29% | 0.71 | 6/7 |
| 4 | SMA-150 + th=5% + 3x long + cash | 25.68% | 23.04% | 2.64% | 0.74 | 6/7 |
| 5 | EMA-100 + th=5% + 3x long + cash | 26.74% | 23.66% | 3.08% | 0.76 | 6/7 |

**Padrões**:
- Top config é o mesmo pure e tax15 (EMA-150 + th=5% + 3x + cash) —
  holds longos reduzem eventos tributáveis.
- Median tax drag top-20: **2.65% de CAGR** (vs 11.47% SPY buy-hold).
- Cash no sell leg domina top-20 (16/20); short alavancado aparece só
  em configs com threshold 5% (4/20) e degrada sob tax.
- **0/384 configs passam 7/7 gates**; 18/384 passam 6/7. G3 walk-forward
  (MDD<25% por janela) é intransponível para configs com 2x-3x.

## O que vem a seguir

Nada automático. O sweep rodou, os artefatos honestos estão em
`studies/ema_sma_threshold_educational/`. Se o usuário quiser explorar mais:

- Rodar `--full` (1512 configs, ~25min).
- Cross-check com Tiingo real post-2009 (quando UPRO/SSO existem como
  produtos reais — elimina o synth).
- **Sinalizar bug idêntico em `letf_rotation.py`** (Phase 3.8-1 Plano B
  base) para o próximo ciclo de maintenance — se a matemática lá também
  estiver lookahead-inflada, os Plano B reports precisam re-rodar.

## Citações

- Fórmula synth: `[leverage_for_the_long_run, p.16, footnote 22]`.
- SMA regime: `[leverage_for_the_long_run, p.8, p.13]`.
- MA periods 10-200 testados: `[leverage_for_the_long_run, p.14, Table 6]`.
- Leverage 1.25/2/3: `[leverage_for_the_long_run, p.17, Table 8]`.
- Band hysteresis: `[leverage_for_the_long_run, p.11]`.
- PBO CSCV: `[advances_fin_ml, p.208-211]`.
- DSR: `[advances_fin_ml, p.222-223]`.
- Bootstrap CI: `[advances_fin_ml, p.196-202]`.
- Cross-lib tolerance e lookahead risk: `[advances_fin_ml, p.31-34]`.

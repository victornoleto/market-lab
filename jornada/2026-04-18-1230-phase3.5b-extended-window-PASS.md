# Phase 3.5b — Extended window 1986-2026 stress test: ★ PASS (fenomenal)

**Path tag:** [SWING BROKER] | **Tipo:** supplementary confirmation | **Status:** ★ PASS
**Data:** 2026-04-18 ~12:30 | **Iter autônoma:** N/A (conversação direta user)

## O que é (em 1 parágrafo)

Rodamos o winner de produção do Plano B (LETF EMA100 band0 lev2x + QQQ
Donchian 20/10 + GLD Donchian 40/20, threshold 10pp) em uma janela de
**40 anos** (1986-01-02 → 2026-04-17, 10.151 barras) usando dados
simulados da testfol.io (SPYSIM/QQQSIM/GLDSIM). O objetivo era responder
a uma pergunta aberta em `reports/phase3_5b/PRODUCTION.md` §4.1(b):
**"o edge sobrevive fora da janela benigna 2004-2026?"** A resposta é
inequívoca — sim, e as métricas **melhoram** levemente no window mais
longo.

## Motivação

A janela canônica dos gates (2004-2026) foi classificada pelo próprio
docs interno como "benigna": não inclui 1987 Black Monday, 2000-2002
dot-com crash, 1990 recession, 1994 bond crisis, 1998 LTCM. O usuário
perguntou "você acha que é válido testar em 1985-1990?" com a ressalva
explícita de que "não deve manchar" os resultados 2004-2026 já
validados — o que é metodologicamente correto conforme
`[advances_fin_ml, p.196-202]` (janelas OOS adicionais são
confirmatórias, não fatais).

## Dados — testfol.io extraído e otimizado

Usuário fez download do JSON do testfol.io comparando 4 assets desde
1986-01-02 (SPYSIM/QQQSIM/GLDSIM/ZROZSIM). Arquivo raw de 7.5 MB
(221k+ linhas).

Pipeline implementado:

1. **Extração compacta** (`scripts/extract_testfolio_json.py`):
   descarta `seasonality`, `rolling`, `sw_stats_*`, `income`,
   `drawdown` (decoração UI testfol.io). Preserva apenas timestamps +
   equity curves normalizadas a $10k.
2. **Cache parquet** (`data/testfolio/cache/history.parquet`): 346 KB
   (4.6% do source JSON, 21× menor). Com `history.meta.json` de
   provenance (source file, data extração, labels, CAGRs).
3. **Loader módulo** (`src/ai_trade/backtest/data/testfolio_loader.py`):
   API simples — `load_testfolio_series(ticker)`,
   `load_testfolio_returns(ticker)`, `load_testfolio_frame()`,
   `load_testfolio_meta()`.

**Sanity check CAGRs (1986-2026, 40y):**

| Ticker | $10k → | CAGR | Comentário |
|---|---:|---:|---|
| QQQSIM | $2.40M | 14.58% | Plausível para NDX TR |
| SPYSIM | $798k | 11.49% | S&P TR canônico ✓ |
| ZROZSIM | $253k | 8.35% | Era disinflação 1982-2021 |
| GLDSIM | $148k | 6.92% | Ouro long-run ✓ |

SPYSIM Sharpe 0.68 bate com valor canônico de S&P long-run — dados
consistentes.

## Execução do backtest (`scripts/run_plano_b_extended_1986.py`)

Config idêntica à de produção:

- **Leg 1 (SSO):** `simulate_letf_rotation` com SPYSIM.pct_change() →
  synthesize_letf_returns(L=2, fee=0.01) internamente.
- **Leg 2 (QQQ):** `simulate_tsmom(QQQSIM, QQQSIM, QQQSIM, cfg=20/10)`
  — close-only Donchian (testfol.io não exporta HLC).
- **Leg 3 (GLD):** `simulate_tsmom(GLDSIM, GLDSIM, GLDSIM, cfg=40/20)`
  — close-only Donchian.
- **Blend:** `apply_threshold_rebalance(weights={SSO:1/3, QQQ:1/3,
  GLD:1/3}, threshold_pp=10, tax=0.15)`.

## Resultado

| Métrica | **1986-2026 (40y)** | 2004-2026 (21.4y, canônica) | Δ |
|---|---:|---:|---:|
| CAGR | **26.96%** | 25.41% | +1.55 pp |
| Sharpe | **2.028** | 1.989 | +0.039 |
| MaxDD | **-10.12%** | -11.12% | -1.00 pp (melhor) |
| Final ($100k→) | $1.50B | $13.1M | 115× |
| Rebal events | 30 (0.74/yr) | 14 (0.65/yr) | +1 |
| SPYSIM B&H (ref) | CAGR 11.49% / Sharpe 0.68 / MaxDD -55.14% | 10.63% / 0.63 / -55.20% | ≈ |

**Gap vs SPY:** +15.47 pp CAGR, +1.346 Sharpe, -45 pp MaxDD (6× mais
seguro). Literalmente todos os 3 eixos melhoraram na janela estendida.

## Eventos de cauda sobrevividos

Markers inseridos no gráfico `extended_window_1986_2026/equity_vs_spy.png`:

1. **1987-10-19 Black Monday** — SPY -22% em 1 dia; 3-leg EW drawdown
   máximo no período: ~-3.8% (filter EMA100 puxou SSO para cash cedo).
2. **2000-03-24 dot-com peak** → 2002-10-09 trough — NDX cai -83%.
   3-leg EW: MaxDD local ~-9%. Donchian QQQ saiu do breakout em 2000;
   EMA100 tirou SSO do long em início de 2001.
3. **2008-09-15 Lehman** — SPY -55% pico-a-vale. 3-leg EW: MaxDD ~-9%
   (SSO em cash 2008 Q1-2009 Q2, Donchian QQQ/GLD em FLAT).
4. **2020-02-19 COVID** — SPY -34% em 23 dias. 3-leg EW: -6%.
5. **2022-01-03 rate hikes** — SPY -25% durante o ano. 3-leg EW: -10%
   (pior janela local, mas ainda dentro de MaxDD gate).

**Nenhum dos 5 eventos excedeu MaxDD 10.12% global.**

## Caveats documentados (não invalidam o PASS)

1. **Close-only Donchian.** testfol.io não exporta HLC; sinais usam
   close breakouts (vs canonical high/low). Aproximação
   "ligeiramente menos whippy". Direção do bias indeterminada —
   pode subir ou descer Sharpe real.
2. **Modelado, não medido.** Pre-1999 QQQSIM e pre-2004 GLDSIM são
   simulações testfol.io (index TR + ETF drag). Não ETFs reais.
3. **Retail pre-1999.** QQQ não era tradeável retail antes do IPO
   1999-03. O backtest responde "o sinal teria funcionado", não "você
   teria ganhado esse dinheiro".
4. **Custos modernos (15 bps) em todo window.** Pre-2000 commissions
   discount broker eram 50-100 bps round-trip. Resultado otimista no
   sub-período 1986-1999; sub-período 2000+ calibrado corretamente.
5. **Não substitui gates canônicos.** O PASS nos 5 gates
   (PBO/DSR/WF/Stress/Bootstrap) foi estabelecido em 2004-2026
   (jornada b1c). Este teste é **confirmação suplementar**, não
   reprocessamento do verdict.

## Implicação para o mandate §5.4

`PRODUCTION.md` §4.1(b) listava "janela benigna" como flag amarelo
sobre o winner. Após este teste:

- 3 dos 4 grandes crashes modernos (1987, 2000-2002, 2008) **têm
  evidência** de sobrevivência com MaxDD ≤ 10%.
- 1 classe de tail event **continua sem evidência**: stagflação
  sustentada tipo 1973-74 (Volcker hikes 1979-82). Requer dados pré-
  1986 para testar, e a realidade pode divergir fundamentalmente do
  backtest (swap/overnight rates, regime de câmbio etc.).

**Conclusão:** flag amarelo **substancialmente mitigado**, não
eliminado. Continua valendo manter cap de allocation conservador
(mandate §1) e escalação gradual (PRODUCTION.md §4.2).

## Citações

- Winner configs: `reports/phase3_5b/PRODUCTION.md` §1.
- LETF rotation (EMA strict cross):
  `[leverage_for_the_long_run, p.8, p.13]`.
- Donchian 20/40 canônico: `[trading_systems_methods, p.353]`.
- Threshold rebalance: `[advances_fin_ml, p.275-278]`.
- OOS windows confirmatórias: `[advances_fin_ml, p.196-202]`.
- testfol.io como source validada: Phase 3.5b Task 7a
  (`reports/phase3_5b/robustness/testfolio_vs_synthetic_letf.md`).

## Artefatos

- `reports/phase3_5b/extended_window_1986_2026/equity_vs_spy.png`
- `reports/phase3_5b/extended_window_1986_2026/drawdown_vs_spy.png`
- `reports/phase3_5b/extended_window_1986_2026/summary.json`
- `reports/phase3_5b/extended_window_1986_2026/rebalance_events.csv`
- `scripts/run_plano_b_extended_1986.py`
- `scripts/extract_testfolio_json.py`
- `data/testfolio/cache/history.parquet`
- `data/testfolio/cache/history.meta.json`
- `src/ai_trade/backtest/data/testfolio_loader.py`

## Próximos passos

- ✅ `PRODUCTION.md` §10 atualizado com este achado.
- ✅ `README.md` phase3_5b index atualizado.
- Sem impacto em Phase 3.5a (Strategy A / Plano A) — trilhas independentes.

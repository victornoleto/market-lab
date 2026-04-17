# Entradas RETRACTED — arquivo de 2026-04-16

> **Status:** consolidado em 2026-04-16 evening, durante o cleanup
> pós-winners (`specs/post-winners-cleanup.md` §5).
>
> **O que está aqui:** 9 entradas de `jornada/` que foram afetadas pelo
> bug de bars-fake da Tiingo IEX em US holidays e cujas conclusões
> não são confiáveis. Foram movidas pra cá pra reduzir ruído no índice
> top-level, mas **continuam preservadas** porque documentam o caminho
> percorrido (e o caminho errado também é informação).
>
> **Postmortem do bug fica fora deste arquivo:**
> [`../2026-04-16-1245-data-bug-winners-retracted.md`](../2026-04-16-1245-data-bug-winners-retracted.md)
> permanece no top-level porque é o documento histórico de primeira
> ordem que explica POR QUE essas entradas foram retratadas.

---

## Por que retratadas?

Bug crítico nos dados Tiingo IEX 1h: em dias de mercado fechado (US
holidays), a API retornava 6 placeholder bars com OHLC idênticos e
volume=0 a preço RAW unadjusted. Para tickers com split histórico
(XLK ratio≈0.48, XLE≈0.41), esses bars apareciam a ~2× o preço das
barras vizinhas. Strategy entrava na quinta ao close, "saía" na segunda
no bar fake → +100% de gain fictício.

Magnitude (pré-fix):
- SPY: 8/217 trades contaminados, 44.8% do retorno total = artifact.
- XLK: 13/232 trades contaminados, **84.9%** do retorno total = artifact.
- XLE: similar a XLK.

Fix em `_filter_orphan_intraday_bars()` aplicado e validado nos winners
production (que estão no top-level, não aqui).

---

## Índice das entradas arquivadas

Ordenado por data de criação (mais antiga primeiro).

1. **[2026-04-15 23:50 — Bollinger MR 1h SPY PASS ⚠️ RETRACTED](2026-04-15-2350-bollinger-mr-1h-PASS.md)**
   Primeira "vitória" do catálogo intraday. Sharpe inflado por bars-fake.
2. **[2026-04-16 00:10 — OOS 2025 hold-out Bollinger MR ⚠️ RETRACTED](2026-04-16-0010-bollinger-mr-oos-2025-PASS.md)**
   "Confirmação" do edge SPY 1h. Mesmo bug.
3. **[2026-04-16 00:45 — Kalman Pairs SPY-IWM 1h PASS ⚠️ RETRACTED](2026-04-16-0045-kalman-pairs-spy-iwm-PASS.md)**
   Pair-trade de aparente edge — placeholder bars dos dois ativos.
4. **[2026-04-16 00:59 — Bollinger MR 2026-Q1 stress test ⚠️ RETRACTED](2026-04-16-0059-bollinger-mr-2026q1-stress-test.md)**
   Stress test mais pesado: holiday bars dominam.
5. **[2026-04-16 01:00 — Bollinger MR sector ETFs PASS ⚠️ RETRACTED](2026-04-16-0100-bollinger-mr-sector-etfs-PASS.md)**
   Expansão XLK + XLE — onde a contaminação chegou a 84.9%.
6. **[2026-04-16 01:30 — Kalman Pairs OOS 2025 FAIL ⚠️ DATA TAINTED](2026-04-16-0130-kalman-pairs-oos-FAIL.md)**
   Conclusão FAIL permanece (a strategy era ruim mesmo), mas pelo
   motivo errado.
7. **[2026-04-16 08:33 — Tiingo cache audit ⚠️ CONCLUSÃO INVÁLIDA](2026-04-16-0833-tiingo-cache-audit.md)**
   Audit que classificou a Q1-2026 como "trustworthy" e subestimou o
   "latent bug" — o exato bug que atacou os winners 4 horas depois.
8. **[2026-04-16 12:30 — MC bootstrap winners XLK robusto ⚠️ RETRACTED](2026-04-16-1230-bollinger-mr-mc-bootstrap.md)**
   "XLK robusto" era CI baseado em trades fake.
9. **[2026-04-16 13:00 — Cross-asset overlap XLK-XLE 0.83 ⚠️ RETRACTED](2026-04-16-1300-bollinger-mr-overlap.md)**
   Correlação real, mas o setup que motivou o estudo (3 winners XLK/XLE/SPY)
   colapsou 15 minutos depois.

---

## Lições preservadas (não retratáveis)

Mesmo com as conclusões de cada entrada inválidas, sobraram lições
operacionais que viraram código:

- **`_filter_orphan_intraday_bars()`** em `src/ai_trade/backtest/data/`
  — defesa permanente contra placeholder bars; rejeita qualquer bar
  intraday cuja data não bata com uma sessão DAILY válida.
- **`scripts/clean_intraday_orphans.py`** — limpeza retroativa do
  cache; rodou em 2026-04-16 e removeu 4296 bars placeholder.
- **Convenção:** validar OOS a Q1-2026 com sniff-test de
  `entry_price ≈ exit_price < 1%` antes de declarar PASS.
- **Convenção:** preferir bar-level Sharpe sobre trade-level Sharpe
  para strategies com sizing dinâmico (GARCH) — bug detectável em
  qualquer das duas, mas trade-level inflate inflou demais.

Os dois winners atuais
([BollingerMR-GARCH SPY 1h](../2026-04-16-1347-bollinger-mr-garch-spy-1h-PASS.md)
e [ETFRotation monthly top-1](../2026-04-16-1420-etf-rotation-monthly-PASS.md))
foram revalidados após o fix e estão production-ready (Sharpe 0.995 e
0.708 respectivamente, ver
[production readiness summary](../2026-04-16-1600-production-readiness-summary.md)).

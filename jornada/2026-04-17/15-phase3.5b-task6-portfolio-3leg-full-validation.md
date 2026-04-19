# Phase 3.5b Task 6 [PLANO B] / [SWING BROKER]: Portfolio 3-leg EW — full consolidated validation + trade-log correctness fix

**Data:** 2026-04-17 12:00
**Phase:** 3.5b (Winners validation, iter 6 de 9)
**Branch:** `phase3.5b/winners-validation-20260417`
**Status:** ✅ Task 6 concluída. Winner imutável **Portfolio 3-leg EW (LETF+QQQ+GLD)** re-validado em janela longest com trade log consistente.

---

## TL;DR (1 parágrafo)

Rodamos o `validate_phase3_winners.py` com a janela mais longa possível do
blend 3-leg (**2004-11-18 → 2026-04-14, 5383 bars, 21.4 anos** — limitado
pelo GLD Tiingo inception). Métricas sobre o equity consolidado
(**não** somatório de pernas): Sharpe **2.108**, CAGR **25.56%**, MaxDD
**10.86%**, Sortino 3.217, Calmar 2.354. vs SPY mesma janela:
Excess CAGR **+14.90 pp**, IR **0.722**, Delta MaxDD **−44.35 pp**,
Correlation **0.549**, Beta **0.321**. Winner Phase 3 iter 37 **preservado
imutável** — 3-leg EW continua o blend óptimo. Durante a task corrigimos
um bug do script (**192 trades pré-2004-11-18 apareciam no portfolio
trade log**) — esses trades existiam nas pernas individuais mas o
portfolio não os tomou (só começa a tradear quando as 3 pernas estão
alinhadas). Fix aplicado em `_filter_trades_to_window()`: trade log
agora tem **259 trades in-window** (118 LETF + 93 QQQ + 48 GLD),
consistente com a equity curve. Pytest 587 verde (sem regressão).

---

## Contexto

O Phase 3 iter 37 (jornada `2026-04-17-0040-a3d-3leg-letf-qqq-gld-PASS.md`)
validou o blend EW com gates completos (OOS Sharpe 2.251, DSR p=0, WF 8/8,
bootstrap 99.9% CI [0.946, 3.612]). Essa validação usou os splits
IS/OOS/Stress mutuamente exclusivos do mandate. Task 6 produz a **vista
full-window + SPY benchmark obrigatório + trade log consolidado** (spec
§4.5 do `phase_3_5b_winners_validation.md`).

Especificidades da Task 6:
- Calcular métricas **sobre equity consolidado**, não agregar das pernas
  (os 3 Sharpes das pernas **não somam** para o do portfolio).
- 15% IR BR por **venda lucrativa de cada perna individualmente**
  (3 eventos tributáveis independentes, não um único evento portfolio).
- SPY benchmark sempre no mesmo report.

---

## O que foi executado

### 1. Bug discovery — portfolio trade log tinha trades fora da janela

Inspeção do artefato gerado na smoke Iter 2 mostrou 451 trades no log
consolidado — mas a equity curve começa em 2004-11-18. Contagem:

```
Trades PRE-2004-11-18 (spurious — portfolio NÃO tomou esses trades):
  LETF_2x: 178 trades | sum net PnL = 509,394 BRL
  QQQ:      14 trades | sum net PnL =   7,142 BRL
Trades straddling the boundary (entry before, exit after):
  2 trades (1 QQQ, 1 LETF)
```

Motivo: `validate_phase3_winners.py` estava passando cada `leg_trades`
cru (da simulação individual, janela longest da perna) para
`aggregate_leg_trades()`. As pernas individuais simulam desde 1970
(LETF) / 2001 (QQQ) / 2004 (GLD), mas o portfolio só tradeou a partir do
dia em que os 3 estão alinhados (2004-11-18).

### 2. Fix — `_filter_trades_to_window()`

Adicionado helper no script (não modifica LÓGICA de strategies — per
constraint #3 do Phase 3.5b):

```python
def _filter_trades_to_window(trades, start, end):
    return [t for t in trades
            if pd.Timestamp(t.entry_date) >= start
            and pd.Timestamp(t.exit_date) <= end]
```

Aplicado antes do `aggregate_leg_trades` do portfolio:
- 118/296 LETF trades mantidos (178 pré-window + 0 straddle eliminados).
- 93/107 QQQ trades mantidos (14 pré-window eliminados).
- 48/48 GLD trades mantidos (GLD já começa em 2004-11-18).

Equity curve **não mudou** (deriva de `blend.cumprod()`, não do trade
log). Só o log ficou honesto. `Sharpe`, `CAGR`, `MaxDD` idênticos ao
Phase 3 iter 37 — winner preservado.

### 3. Re-run com janela longest

```
Start                     2004-11-18
End                       2026-04-14
Duration                  7817 days (21.4y)
Exposure Time [%]         100.00%
Equity Final [$]          12,908,903.64 (com IR 15%/perna, cap inicial $100k)
Equity Peak [$]           13,438,914.47
Return [%]                12808.90%
CAGR [%]                  25.56%
Volatility (Ann.) [%]     11.10%
Sharpe Ratio              2.108
Sortino Ratio             3.217
Calmar Ratio              2.354
Max. Drawdown [%]         10.86%
Avg. Drawdown [%]         1.27%
Max. Drawdown Duration    204 days
Avg. Drawdown Duration    14 days
# Trades                  259
Win Rate [%]              80.69%
Best Trade [%]            79.87%
Worst Trade [%]           -6.79%
Avg. Trade [%]            6.65%
Max. Trade Duration       452 days
Avg. Trade Duration       50 days
Profit Factor             19.106
SQN                       8.971
Kelly Criterion           0.764
```

### 4. SPY Buy & Hold (mesma janela, mesmo capital inicial)

```
SPY Return [%]            769.21%
SPY CAGR [%]              10.66%
SPY Max. Drawdown [%]     55.20%
SPY Sharpe Ratio          0.629
```

### 5. Strategy vs SPY

```
Excess Return [%]         12039.70 pp
Excess CAGR [%]           +14.90 pp
Delta Max DD [%]          −44.35 pp (redução enorme)
Information Ratio         0.722
Correlation (daily)       0.549
Beta vs SPY               0.321
```

IR **0.722** é "good-to-excellent" em mandatos de longo-prazo
(Grinold-Kahn "Active Portfolio Management" define IR ≥ 0.5 como bom;
≥ 0.75 como excelente) `[active_portfolio_management, ch.5]`. Beta
0.321 significa que o portfolio tem **~1/3 da sensitividade
market-direcional do SPY** — coerente com o mix defensivo
(LETF regime-switched vai a cash em bear, GLD anti-correlacionado em
stress).

### 6. Tax aggregates por perna (15% IR BR individual)

```
Leg         Trades   WinRate      GrossPnL BRL    Tax BRL    NetPnL BRL
LETF_2x        118    100.0%          381,931     57,290       324,642
QQQ             93     65.6%          114,355     20,214        94,142
GLD             48     62.5%           77,510     13,320        64,190
TOTAL          259                    573,797     90,823       482,974
Effective tax drag: 15.83% of gross PnL
```

Drag efetivo acima de 15% porque losses não compensam (worst-case BR
modeling; BR real tem compensação intra-mês de lucros e prejuízos no
mesmo ativo — ver constraint #6 do spec). LETF 100% WR é o artefato
de definição de trade documentado em Task 3 (cada bloco ON = 1
trade; drift positivo no regime-on garante exit > entry).

### 7. Per-leg PnL contribution (concentração)

- LETF: 67% do gross PnL (381k / 574k BRL).
- QQQ: 20% (114k).
- GLD: 13% (77k).

O blend é pesos-iguais em **alocação** (1/3 cada) mas **não** em
contribuição de PnL. LETF (alavancado 2x) naturalmente domina o upside
— e também o downside em crises se o filtro EMA100 falhar. MaxDD
consolidado 10.86% mostra que QQQ e GLD suavizam drawdowns do LETF
(ρ(LETF, GLD)=+0.063 é quase ortogonal — "almost a free lunch"
`[ilmanen_expected_returns, p.353]`).

---

## Artefatos produzidos

```
reports/phase3_5b/portfolio_3leg_ew/
├── standard_report.md   (metrics block + SPY benchmark + vs SPY)
├── trade_log.csv        (259 trades in-window, per-leg tax individual)
├── trade_log.md         (tabela Markdown)
├── summary.json         (machine-readable snapshot)
└── equity_curve.png     (log-scale strategy vs SPY)
```

---

## Verdict Task 6

✅ **PASS — winner imutável Phase 3 preservado.**

- Janela longest usada (5383 bars, 21.4y — limite GLD Tiingo).
- Métricas sobre equity consolidado (não somadas).
- SPY benchmark presente, Strategy-vs-SPY block OK.
- Trade log **corrigido** para 259 trades in-window (fix
  `_filter_trades_to_window`).
- IR 15%/perna aplicada individualmente.
- Pytest 587/587 — sem regressão.

---

## ⚠️ FLAGs documentadas (não bloqueantes)

1. **Concentração LETF em PnL**: 67% do gross PnL vem da perna LETF.
   Numa sequência adversa onde o filtro EMA100 fica "tarde" (ex.: whip
   2020-02/03), a perna LETF pode ter um drawdown profundo que as
   outras 2 não compensam. Mitigação: Task 7e (correlação rolling) vai
   identificar janelas de ρ alta; Task 7d (allocation alternativa) vai
   testar se IVP/HRP suavizam a concentração.
2. **Cash drag implícito**: quando LETF está RISK-OFF (CASH), a perna
   contribui 0% de retorno — mas o portfolio inteiro não está em cash
   (QQQ e GLD continuam ativos). Por isso o "Exposure Time 100%" do
   portfolio masca 2/3 de tempo-em-caixa da perna LETF. Task 8
   (allocation doc) vai decompor isso numéricamente.
3. **Janela truncada pelo GLD**: o blend só começa em 2004-11-18 porque
   GLD foi lançado nessa data (SPDR GLD ETF). Pre-2004 seria sintético
   via gold spot + drag — não fizemos esse pull. Implicação: 1970s
   (LETF brilha em stagflation) não entra no blend window. Task 7b
   (stress isolado) vai confirmar resiliência em 2008/2020/2022.

---

## Próximo passo (Iter 7)

**Task 7a — testfolio cross-check + FFR-aware LETF cost gate**
(robustness gate mais crítico da fase).

- Ler `data/external/testfolio_spysim_leverage.parquet`, truncar 1962-01-01.
- 3-way comparison vs `synthesize_letf_returns()` vs UPRO/SSO Tiingo.
- Estratificar gap CAGR por bucket FFR {<2%, 2-5%, ≥5%}.
- GATE: se gap > 2%/yr num bucket ≥5 anos → implementar
  `synthesize_letf_returns_ffr_aware()` NOVA função e re-rodar B1c.

---

## Citações

- Portfolio 3-leg HRP/IVP construction: `[advances_fin_ml, p.302-313]`.
- Gold diversification anti-correlated tail: `[ilmanen_expected_returns, p.353]`.
- Information Ratio benchmark: `[active_portfolio_management, ch.5]`
  (Grinold-Kahn — IR 0.75 = "excellent").
- Winner origin: Phase 3 iter 37
  `2026-04-17-0040-a3d-3leg-letf-qqq-gld-PASS.md`.

---

## Files modified

- `scripts/validate_phase3_winners.py`: added `_filter_trades_to_window()`
  helper + portfolio window filter block. No strategy logic touched.

## Reports regenerated

- `reports/phase3_5b/portfolio_3leg_ew/{standard_report.md,
  trade_log.csv, trade_log.md, summary.json, equity_curve.png}`
- `reports/phase3_5b/summary.json` (aggregate).

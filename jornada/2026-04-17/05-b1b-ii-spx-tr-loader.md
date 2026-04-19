# [SWING BROKER] Phase 3 B1b-ii — SPX TR loader 1970-2026 (KF + Tiingo stitch)

**Lead:** B1b-ii (LETF rotation grid backbone)
**Iter:** 31
**Date:** 2026-04-17 00:30
**Status:** ✅ DONE — pipeline ready for Lead B1c (CPCV/PBO grid execution)

## O problema

A grade canônica Gayed da Strategy B exige splits **IS 1970-2000 / OOS
2001-2015 / Stress 2016-2026** [`leverage_for_the_long_run, p.13, p.17`].
O cache Tiingo SPY daily começa em **2001-05-14** — não chega nem perto
de 1970. Sem dados pré-2001 o IS canônico não roda, e cair o IS para
2001-2015 (e o OOS para 2016-2026) destrói o "split mutuamente
exclusivo" exigido pelo Investment Mandate §4.

## Por que Ken French e não Yahoo `^SP500TR` ou Shiller

| Fonte                      | Cobertura       | Frequência | Problema                                         |
|----------------------------|-----------------|------------|--------------------------------------------------|
| Tiingo SPY                 | 2001-05-14 +    | daily      | Tarde demais para IS Gayed.                      |
| Yahoo `^SP500TR`           | 1988-01-04 +    | daily      | Ainda perde 18 anos do IS canônico (1970-1987). |
| Robert Shiller             | 1871-01 +       | **monthly**| LRS daily SMA200 não roda em monthly.            |
| FRED `SP500`               | 1957-01-04 +    | daily      | **Price-only**, sem dividendos → não é TR.       |
| **Kenneth French**         | **1926-07-01 +**| **daily**  | CRSP-VW (broader que S&P 500), mas TR nativo.    |

Escolha: **Ken French Mkt-RF + RF**. CRSP-VW é o S&P 500 + small caps
value-weighted; correlação ~0.99 mensal com SP500-TR pós-1972; o tilt
small-cap é minúsculo no daily-resolution timescale do LRS. Gayed
explicitamente usa CRSP para robustez pré-1990
[`leverage_for_the_long_run, p.13`].

## O que entregamos

1. **`src/ai_trade/backtest/data/spx_tr_loader.py`** (NEW, ~210 linhas):
   - `parse_ken_french_csv(text)` — parser puro (sem rede), pula
     header multi-linha + footer Copyright; converte percent → decimal.
   - `fetch_ken_french_daily(cache_dir, force=False)` — baixa+cacheia
     o CSV de
     `https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/F-F_Research_Data_Factors_daily_CSV.zip`
     em `data/ken_french/F-F_Research_Data_Factors_daily.csv`
     (1.2 MB). Hit-cache em chamadas subsequentes (zero rede).
   - `compute_market_total_return(kf)` — `mkt_rf + rf` em decimal.
   - `load_spx_tr_daily(start, end, cutoff_date=2001-05-14, ...)` —
     stitcha KF (`<= cutoff`) com SPY adj_close pct_change (`> cutoff`),
     dedup por timestamp, valida zero NaN.

2. **`tests/test_spx_tr_loader.py`** (NEW, 11 testes):
   - parser: extrai bloco de dados, ignora header/footer, converte %.
   - `compute_market_total_return`: fórmula + colunas obrigatórias.
   - `fetch_*`: usa cache quando presente (sem rede em test).
   - stitch: monotone, sem duplicados, seam exato (`pre[-1] == cutoff`,
     `post[0] == cutoff + 1d`), `pct_change` correto, rejeita janela
     invertida, `DEFAULT_TIINGO_CUTOFF` ancorado ao manifest.

3. **Cache real semeado:** 1,205,155 bytes, KF data 1926-07-01 → 2026-02-27.

## Smoke E2E (não é gate, só pipeline check)

`load_spx_tr_daily("1970-01-01", "2026-04-15")` retorna **14,191 bars**
(7,926 KF + 6,265 SPY), monotone, zero NaN. Carregamento ~1.3s.
Anualizada full-period: vol 16.74%, ret 11.66% (consistente com SPX TR).

`simulate_letf_rotation(...)` com canônico Gayed (SMA200, L=2x, band=0,
cash off-asset, custos 15bps + 15% IR BR) roda nos 3 splits sem erro:

| Split          | Sharpe | CAGR    | %ON   | Switches |
|----------------|--------|---------|-------|----------|
| IS  1970-2000  | 1.369  | 31.72%  | 75.2% | 151      |
| OOS 2001-2015  | 1.240  | 27.23%  | 68.2% | 110      |
| Stress 2016-26 | 1.410  | 35.33%  | 76.8% | 50       |

**ALERTA não-blocante:** Sharpes ~1.3 são bem maiores que os 0.58-0.68
publicados por Gayed [`leverage_for_the_long_run, p.14, Table 6`]. Causas
prováveis a investigar em **B1c**:
- KF Mkt-RF inclui small-caps tilt (~0.99 corr com S&P TR mas não 1.0).
- `cum_cost_pct = 16,049%` no IS sugere accounting de custos somando %
  do equity corrente (compostado), o que é informativo mas inflaciona o
  número absoluto. **O `daily_returns` net já reflete o custo;** o
  Sharpe é sobre net.
- Possível bug de double-counting ou regime ON-bias persistente quando
  a vol cai estruturalmente (regime 1980s+90s).
- TR-aware MA (Gayed [p.8]) gera mais switches do que MA price-only.

→ **B1c (CPCV/PBO)** é onde o gate vai apertar; os 1.3 acima é
"pipeline funcionando", não "winner". O `cum_cost` será reescrito
para reportar % do equity FINAL (não soma dos %s) na faxina de B1c.

## Pytest

Antes: 411 passed (baseline iter 30).
Depois: **422 passed** (+11 novos), zero regressão. Sem warnings novos.

## Decisões técnicas (citadas)

- Cutoff = 2001-05-14 (primeira data Tiingo SPY no manifest atual).
  KF supre ATÉ E INCLUINDO o cutoff porque SPY pct_change[cutoff]
  é NaN (sem prior price). Tiingo supre estritamente APÓS.
- `mkt = mkt_rf + rf`: definição padrão CRSP de retorno total
  (excess + risk-free) [`leverage_for_the_long_run, p.13`].
- TR-aware price para MA via `(1+r).cumprod()*100`
  [`leverage_for_the_long_run, p.8`].
- Annual fee 1% pre-2021, 0.95% post (não tocado neste lead — é
  default do `synthetic_letf` [`leverage_for_the_long_run, p.16`,
  footnote 23]).

## Próximo

**Lead B1c — execução grid + gates.** Inputs prontos:
- `load_spx_tr_daily("1970-01-01", "2026-04-15")` — 14,191 bars KF+SPY.
- `LETFRotationConfig` × `simulate_letf_rotation` (já validados em B1a).
- Grid runner + smoke (B1b-i, iter 30) — 16 configs já testadas.
- Splits canônicos: `IS 1970-2000 / OOS 2001-2015 / Stress 2016-2026`.

Falta:
- Grade completa **2 (filter) × 4 (lookback) × 3 (band) × 3 (lev) ×
  5 (gold_weight) = 360 configs**.
- **CPCV** k=8 splits + **PBO** Bailey-López de Prado.
- **Stationary block bootstrap** Sharpe CI alpha=0.001
  [`advances_fin_ml, p.196-202`].
- Gate: PBO<0.5 + DSR p<0.05 + WF≥6/8 + OOS Sharpe>0 + Stress Sharpe>0.
- Gold off-asset opcional via síntese pré-2004 (LBMA spot ou GLD
  proxy curto). Configs com `gold_weight=0` rodam sem isso.

## Arquivos

- `src/ai_trade/backtest/data/spx_tr_loader.py` (NEW, ~210L)
- `tests/test_spx_tr_loader.py` (NEW, 11 testes)
- `data/ken_french/F-F_Research_Data_Factors_daily.csv` (NEW cache, 1.2 MB)
- `docs/self_improvement/memory.md` (atualizado)

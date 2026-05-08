# External data sources

Dados de fontes externas usados como **cross-reference** para validar
nossos próprios datasets/simulações. Não são substituto do Tiingo
(nossa fonte primária), mas servem como segunda opinião.

---

## `testfolio_spysim_leverage.parquet`

**Fonte:** `testfol.io` API backtest endpoint (API paga, dados salvos
localmente — ver `data/testfolio/spysim-plus-leverage/curl.txt`).

**Conteúdo:** 3 séries de equity curve (daily, $10k inicial, rebalance
anual, dividendos reinvestidos) de **1885-03-20 → 2026-04-16** (141
anos, 35,333 bars):

| Column | Description |
|--------|-------------|
| `spy_1x_equity` | SPY simulated (SPYSIM), CAGR 9.61%, Sharpe 0.615, MaxDD −83.65% |
| `spy_2x_equity` | SPYSIM com 2x daily-rebalanced leverage, CAGR 11.27%, Sharpe 0.483, MaxDD −98.42% |
| `spy_3x_equity` | SPYSIM com 3x daily-rebalanced leverage, CAGR 9.44%, Sharpe 0.439, MaxDD −99.91% |

**Metodologia de custo (testfolio `L=` parameter):**

```
annual_cost = SW * (L - 1) * (FFR% + SP)
```

Com:
- `SW` = swap exposure per unit of leverage (default 1.1)
- `FFR` = Fed Funds Rate (time-varying, real historical)
- `SP` = spread pago sobre FFR (default sgn(L) * 0.4%)

---

## ⚠️ Discrepância crítica vs nossa `synthesize_letf_returns`

Nossa função em `src/market_lab/backtest/helpers/synthetic_letf.py` usa:

```
r_synth[t] = L * r_SPX_TR[t] - annual_fee / 252
```

com `annual_fee = 1.0%` FIXO (constante de Gayed p.16).

**Comparação numérica do custo anual de 2x leverage:**

| Regime | Testfolio (SW=1.1, SP=0.4%) | Nosso modelo (flat 1%) | Gap |
|--------|------------------------------:|-----------------------:|------:|
| FFR 0% (2010-2022) | 0.44% | 1.00% | +0.56% (nosso superestima) |
| FFR 2% (média LT) | 2.64% | 1.00% | −1.64% |
| FFR 5% (80s / 2023-26) | 5.94% | 1.00% | −4.94% (nosso subestima muito) |
| FFR 10% (picos Volcker) | 11.44% | 1.00% | −10.44% |

**Para 3x leverage**, multiplicar o gap acima por 2 (SW * (L-1) = 2.2 vs 1.1).

**Impacto no nosso backtest Phase 3 B1c (LETF rotation EMA100/2x, IS
1970-2000 + OOS 2001-2015):**

- IS window tem FFR média ~8% (Volcker/pós-Volcker)
- Se custo real é ~9%/ano e modelamos 1%/ano, superestimamos CAGR em
  ~8%/ano compound — ao longo de 30 anos isso é **~10x no equity final**
- O Sharpe também é viesado pra cima (custo não reduz return mas volatilidade
  permanece)

**Mas:** a LRS **roda em cash/UPRO alternado**, não buy-and-hold. O custo
de leverage só acumula quando posicionado em UPRO. Se a strategy fica
em UPRO ~60% do tempo, o erro efetivo é menor (~60% × gap bruto).

---

## ⚠️ Janela de comparação válida: 1962-present

**IMPORTANTE:** usar testfolio **apenas** pela janela 1962-present para
comparar com nossos dados (Ken French + Tiingo). Razão:

| Período | Fonte SPYSIM | Comparável ao nosso? |
|---------|--------------|----------------------|
| 1885-1928 | Schwert Dow Jones Composite | ❌ Dow ≠ S&P 500, NÃO comparar |
| 1928-1962 | Schwert S&P 500 Composite (reconstrução) | ❌ Underlying reconstruído, não bate com KF market factor |
| 1962-1993 | S&P 500 Price Index + Shiller dividends | 🟡 Similar ao KF market factor (KF tem small-cap tilt pequeno) |
| 1993-present | SPY real + 0.0945% p.a. | 🟢 Apples-to-apples com nosso Tiingo SPY |

**O valor do testfolio não é substituir nosso SPX TR — é calibrar o
modelo de custo de leverage.** Fora disso, o dataset é secundário.

## Como usar em Phase 3.5b

**Task 7a (real vs synthetic UPRO/SSO)** deve:

1. Ler `data/external/testfolio_spysim_leverage.parquet`, truncar em
   1962-01-01 → 2026-04-16.
2. Alinhar com `src/market_lab/backtest/data/spx_tr_loader.py` na mesma
   janela.
3. 3-way comparação de equity:
   - Nossa `synthesize_letf_returns(spx_tr, L=2, fee=0.01)`
   - Testfolio `spy_2x_equity` (1962+)
   - UPRO/SSO reais (Tiingo) pós-2006/2009
4. Estratificar o gap CAGR nosso-vs-testfolio **por bucket de FFR médio
   anual** (FFR<2%, 2%≤FFR<5%, FFR≥5%). Série FFR via `data/ken_french/`
   RF column.
5. Se gap > 2%/yr CAGR em qualquer bucket com ≥5 anos de dados →
   implementar `synthesize_letf_returns_ffr_aware()` (nova função) e
   rerodar B1c gates com a função corrigida.

Artefatos esperados:
- `reports/phase3_5b/robustness/testfolio_vs_synthetic_letf.md`
  (com tabela CAGR-por-bucket-FFR)
- Plot 3-way equity curves (synthetic, testfolio, real ETF) a partir
  de 1962-01-01

---

## Reprodução

O payload completo da API testfolio está em
`data/testfolio/spysim-plus-leverage/curl.txt` (com bearer token — **NÃO
commitar** se for renovar). Request body pede SPYSIM + SPYSIM?L=2 +
SPYSIM?L=3 com rebalance anual, start $10k, dividendos reinvestidos.

**Script de conversão JSON → parquet:** ver
`data/testfolio/spysim-plus-leverage/data.json` + código de extração
inline em `scripts/convert_testfolio_to_parquet.py` (a ser criado na
Task 7a).

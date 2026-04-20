# Phase 3.5c finding — baseline não valida Plano B V4 (2026-04-20)

> **Status:** descoberta metodológica crítica.
> **Consequência:** veredict da cross-lib validation (BLOCKED-INVESTIGATE em tudo) não é conclusivo — é artifact de dados/windows não-comparáveis.

## O que a cross-lib validation realmente produziu

Após fix de stitching (seam SSO/QLD/UGL inception), adição de window POST_2009, e fix do ring-buffer backtrader, todas as 3 libs (bt, vectorbt, backtrader) concordaram dentro de 0.5-2pp em todos os variants. **Isso é agreement forte entre engines independentes.**

Números observados para Plano B V4 `plano_b_v4_threshold_10`:

| Window | bt CAGR | vectorbt CAGR | backtrader CAGR | max_dd (3 libs) |
|---|---|---|---|---|
| canonical (2004-10 → 2026-04, ~21.5y) | 11.60% | 11.61% | 10.47% | -24 a -29% |
| extended (1986-01 → 2026-04, ~40y) | 5.98% | 5.98% | 5.51% | -24 a -29% |
| post_2009 (2009-01 → 2026-04, ~17y) | 13.99% | 13.99% | 12.19% | -20 a -23% |

**Nossas 3 libs concordam.** O bug não é nossa implementação de engine.

## De onde vem o baseline Phase 3.5b que rejeita esses números

`reports/phase_3_5c/cross_lib/reference/baseline.json` — populado por `generate_baseline.py` lendo `reports/phase3_5b/variants_letf_execution/summary.json`:

```json
{
  "config": {"data_source": "testfol.io (SSOSIM/QLDSIM/UGLSIM ground truth)", "window": {"start": "1986-01-02", "end": "2026-04-17", "bars": 10151}},
  "variants": [{"variant": "V4_SSO_QLD_UGL", "legs": {"leg1": "SSOSIM", "leg2": "QLDSIM", "leg3": "UGLSIM"},
    "metrics": {"years": 40.29, "cagr_pct": 37.92, "max_drawdown_pct": 16.91, "final_equity": 42146981439.37}}]
}
```

Três observações:

1. **Data source é testfol.io SSOSIM/QLDSIM/UGLSIM** — séries sintéticas proprietárias da Simba data. **Não replicáveis via nossa stack** (`synthesize_letf_returns_ffr_aware` + yfinance + Tiingo).

2. **Window real é 40.29 anos (1986-01 → 2026-04)** — mas `generate_baseline.py` assina esse número como `plano_b_v4_threshold_10["canonical"]`, que na nossa cross-lib corresponde a 21.5 anos (2004-10 → 2026-04). **Mismatch de window.**

3. **Final equity = $42.1 bilhões a partir de $100k em 40 anos** — track record extraordinário (CAGR=37.92% por 40 anos). LETFs são notórios por decay que modelos sintéticos optimistas subestimam. É bandeira vermelha de que SSOSIM pode estar modelando retornos de LETF sem o drag de rebalance diário correto.

## E os baselines de leg?

Também não comparáveis:

| Entry baseline | Fonte Phase 3.5b | Instrumento real | Window real |
|---|---|---|---|
| `leg_sso_only canonical` | `letf_rotation_ema100_2x/summary.json` | SSO via SPY-TR 2x | **1970-2026 (56 anos)** |
| `leg_qld_only canonical` | `qqq_donchian_20_10/summary.json` | **QQQ unleveraged** (não QLD) | 2001-2026 (25 anos) |
| `leg_ugl_only canonical` | `gld_donchian_40_20/summary.json` | **GLD unleveraged** (não UGL) | 2004-2026 |

Nossa cross-lib `leg_qld_only` usa QLD (2× leveraged). Phase 3.5b `leg_qld_only` baseline usa QQQ (unleveraged). **Não são o mesmo instrumento.** Mesmo para leg_sso_only onde o instrumento coincide (SSO), a window é 56 anos vs 21.5 anos. REFUTES nesses legs é esperado — baseline errado.

## Por que extended window mostra 5.98% CAGR na nossa stack

Nossa `reference_prices.parquet` para 1986-2026 tem:
- **SPY-TR: 40 anos** (via `load_spx_tr_daily`, Ken French + Tiingo SPY)
- **QQQ via Tiingo: começa 1999-03-10** (nada antes)
- **GLD via Tiingo: começa 2004-11-18** (nada antes)

Portanto, synthetic QLD só existe a partir de 1999, synthetic UGL só a partir de 2004. **Para 1986-1999, a "3-leg EW portfolio" tem só 1 leg ativa (SSO).** Para 1999-2004, 2 legs. Só a partir de 2004 todas as 3 legs existem.

Phase 3.5b usou testfol.io com (provavelmente) NDX-TR de 1985+ e ouro spot/futures de 1968+ — dados que nossa stack não tem. **Extended window não é comparável por falta de dados subjacentes, independente da qualidade do modelo synthetic de LETF.**

## O que esta cross-lib validation provou

**Provou:**
- Nossas 3 libs (bt, vectorbt, backtrader) implementam a lógica de 3-leg EW threshold rebalance de forma consistente (agreement dentro de 1-2pp).
- Nosso synthetic_letf + yfinance stack produz ~11.6% CAGR / -28.8% max_dd para V4 no window 2004-2026. **Isso é o que o mundo real com nossa data pipeline produz.**
- A "ring-buffer" bug em backtrader era real e foi corrigida.
- O seam-stitching em reference_prices.py era bug real e foi corrigido.

**NÃO provou (nem podia, do jeito que foi construído):**
- Se Plano B V4 com SSOSIM/QLDSIM/UGLSIM realmente produz 37.92% CAGR (precisaria rodar em cima do dado testfol.io).
- Se o gap entre 37.92% (testfol.io) e 11.6% (nossa stack) é devido a:
  - (a) Modelo synthetic de LETF diferente,
  - (b) Dados subjacentes diferentes (NDX 1985+, ouro 1968+),
  - (c) Bug em `letf_rotation.py` / `portfolio_3leg_ew` que só surface com certa combinação de dados.

## Ações sugeridas (não executadas automaticamente)

### Ação A — Obter dados testfol.io (1-2 sessões)

1. Exportar SSOSIM/QLDSIM/UGLSIM como CSV de testfol.io (manual, via UI).
2. Criar fetcher `reports/phase_3_5c/cross_lib/data/testfolio_synthetic.py` que carrega esses CSVs.
3. Re-rodar cross-lib Stage 1 usando testfol.io data em vez de nossa `reference_prices.parquet`.
4. **Se 3 libs rodando testfol.io data concordam com baseline 37.92%** → nossa engine está correta, divergência é 100% modelo synthetic. Decision: atualizar `synthesize_letf_returns_ffr_aware` para replicar testfol.io methodology.
5. **Se 3 libs rodando testfol.io data divergem entre si** → tem bug de adapter. Investigar.
6. **Se 3 libs rodando testfol.io data produzem ~11.6%** → Phase 3.5b summary tem bug (engine errada ou dado mal lido). Investigar `letf_rotation.py`.

### Ação B — Comparar synthetic head-to-head (1 sessão)

Paralelo com A. Para o window 2006-06-21 → 2026-04-18 (onde todos os 3 LETFs têm dados reais):
- Nossa synthetic SSO pre-2006-06-21 usa SPY-TR.
- Testfol.io SSOSIM pre-2006-06-21 usa ?.
- Dentro do window post-inception (2006+), NOSSA stack usa real yfinance; testfol.io usa real também.
- Post-inception, CAGR/drawdown deve ser idêntico entre testfol.io e nós (ambos usando dados reais).

Se post-2006 backtest usando testfol.io vs nossa yfinance dão CAGR/max_dd iguais → nossa implementação está certa, divergência total está no synthetic pre-2006.

Se post-2006 backtest já diverge → bug em nossa engine de portfolio, não no synthetic.

### Ação C — Reabrir Phase 3.5b (1-3 sessões)

Rodar Phase 3.5b internamente (com `letf_rotation.py` + `portfolio_3leg_ew`) mas usando nossa `reference_prices.parquet` em vez de testfol.io. Se os números que sairem forem ~11.6% (matching cross-lib), confirmamos que Phase 3.5b internamente usava testfol.io, e o verdict do Phase 3.5b era uma "validação" de estratégia contra dados testfol.io, não contra dados nossos. Isso significa que **Plano B V4 nunca foi validado contra nossa pipeline** — foi validado só contra dados terceiros.

Minha recomendação: **começar pela Ação A ou B** (direto e barato em comparação à C, que precisaria rerodar toda a Phase 3.5b).

## Implicação para Phase 4

**NÃO ir para Phase 4 paper trading com Plano B V4 até a divergência estar entendida.** Se o winner só existe na data testfol.io, Phase 4 com dados reais mostraria ~11.6% CAGR / -28.8% max_dd — abaixo do gate CDI (~14%) e acima do max_dd gate (25%). **Isso é folclore, não winner.**

## Citações

- `[advances_fin_ml, p.31-34]` — two-stage replication protocol, data integrity
- `[advances_fin_ml, p.208-211]` — PBO, rejeição de winners não reproduzíveis
- `[advances_fin_ml, p.273-275, p.298-299]` — DSR, Sharpe inflation com múltiplos testes
- `[leverage_for_the_long_run, p.16]` — synthetic LETF formula; capítulo não discute validação cross-source

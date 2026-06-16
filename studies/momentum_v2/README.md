# Momentum v2 — estudo consolidado de momentum cross-sectional

Estudo **research-only** que mescla os dois forks anteriores de momentum numa pasta
só, organizada por universo:

- de `studies/momentum_13612_universes/` veio a *inteligência de ranking/diagnóstico*
  (dominância rolante `equity/equity_benchmark`, overlays de média móvel, staggered
  offsets, MDD por janela de crise, funil broad→evolution→validate);
- de `studies/momentum/` veio a *fundação de dados/validação* (loader Postgres,
  filtros de survivorship, config YAML, gates honestos).

O loader Postgres foi promovido para `src/market_lab/backtest/data/postgres_source.py`
(`PostgresSource`), compartilhado e testado ao lado de `YFinanceSource`/`TiingoSource`.

---

## Resumo executivo — o que foi validado e verificado

**Veredito em uma linha:** o edge de momentum é estatisticamente sólido (passa todos os
gates honestos nas duas janelas), mas **`promotion_eligible=false`** — o teto remanescente
é *qualidade de dados* (survivorship), não estatística.

### Checklist de validação / verificação

- ✅ **Engine consolidado + testado:** `core`/`dominance`/`overlays`/`filters`/`grid`/
  `config`/`validation`/`report`/`plots`/`run` + `PostgresSource` promovido a `src/`.
  **28 testes** (`tests/test_postgres_source.py` 12 + `tests/test_momentum_v2.py` 16), ruff limpo.
- ✅ **Run canônico us-stocks completo:** `2301/7136` tickers passam filtros; janelas
  **1990 (primária) + 2000 (robustez)**; `840` broad + `144` evolution cada — trial count
  honesto **`984`**.
- ✅ **Gates honestos PASS nas duas janelas** (PBO/DSR/WF/bootstrap/cross-lib): 1990 set-PBO
  `0,000`, 2000 `0,357`; DSR p≈0; WF 8/8; bootstrap CI-low Sharpe > 0.
- ✅ **Cross-library check** (vetorizado vs holdings-loop independente) bate em Δ≈`0,01pp`.
- ✅ **Recorte top_n 3-10** (gerenciável na mão) com recomendação por Sharpe/Calmar (`topn_view.py`).
- ✅ **Sweep de drawdown** (`drawdown_sweep.py`): **vol-targeting** corta MDD full `−63%→−25%`
  *melhorando* Sharpe/Calmar; **SMA200 do SPY** = proteção de crise (GFC `−59%→−18%`).
- ⬜ **Pendente (o teto):** dados point-in-time + preços de delisted para remover survivorship.
  Só então qualquer PASS aqui pode virar promovível.

### Mapa do estudo (arquivos)

| Arquivo | O que faz |
|---|---|
| `run.py` | funil broad→evolution→validate por universo/janela (`--cache-panels`, saída namespaced) |
| `core.py` | scoring (5 modes) + perfis de lookback + simulação shifted-weight + tax BR + métricas |
| `dominance.py` | dominância rolante `equity/equity_benchmark` + MDD de crise + WF diagnóstico |
| `overlays.py` | overlays SMA200 (mensal/diário) + stock-SMA100 + staggering + **`vol_target_returns`** |
| `filters.py` | filtros de survivorship (histórico/preço/liquidez/staleness) + diagnóstico |
| `grid.py` · `config.py` · `validation.py` · `report.py` · `plots.py` | grade, config YAML, gates+result rows, relatórios markdown/json, plots |
| `topn_view.py` | recorte por nº de holdings (`top_n`) re-rankeado por dominância/Sharpe/Calmar |
| `drawdown_sweep.py` | sweep de alavancas de drawdown (SMA200, vol-target, referências) |
| `src/market_lab/backtest/data/postgres_source.py` | data source Postgres compartilhada (`PostgresSource`) |

### Artefatos por janela — `universes/us_stocks/from_{1990,2000}/`

- `reports/`: `BROAD_REPORT`, `EVOLUTION_REPORT`, `VALIDATE_REPORT`, `DATA_AUDIT`, `TOPN_3_10`, `DRAWDOWN_SWEEP`.
- `results/`: `broad_results`/`evolution_results` (csv+json), `*_pbo.json`, `validate_verdict.json`, `filter_diagnostics.csv`.
- `plots/`: ~48 PNGs (`broad/` + heatmaps, `evolution/`, `topn_3_10/`, `drawdown_sweep/`).

> **Versionamento:** por política do repo (`.gitignore`), `plots/*.png`, `results/*.csv`
> e o `cache/` de painel **não** são commitados (regeneráveis). Versionados: código,
> config, `reports/*.md` e `results/*.json`. As imagens deste README renderizam no
> working tree local; regenere com os comandos da seção "Como rodar" / `drawdown_sweep.py`.

Detalhes de cada item nas seções abaixo.

---

## Conclusão (o veredito, sem rodeios)

**Positivo na estatística, bloqueado nos dados.** Não é um "sim" nem um "não" binário —
são duas coisas diferentes:

1. **O edge de momentum é real e passa os gates honestos.** No run canônico (us-stocks,
   universo cheio), as **duas janelas independentes (1990 e 2000) passam todos os gates
   estatísticos** — PBO, DSR, walk-forward, bootstrap e cross-library — com trial count
   honesto de `984`. Isso é diferente do padrão histórico do projeto, onde os edges
   morriam nos gates. Aqui ele sobrevive.

2. **Mas continua `promotion_eligible=false`** — não por estatística, e sim por
   **qualidade de dados**. O feed yfinance nunca baixou as empresas que faliram/sumiram,
   então o universo histórico é *survivorship-biased* e os CAGRs (~40-60%) estão
   inflados. Esse é o teto que sobrou `[advances_fin_ml, p.208-211]`.

> **Por que "passa nos gates" ≠ "deployável":** os gates medem se o resultado é robusto
> a *overfitting/multiple-testing* (PBO/DSR), consistente *out-of-sample* (WF/bootstrap)
> e *implementado sem bug* (cross-lib). Eles **não** medem se os *dados* são fiéis à
> realidade. Com survivorship bias, mesmo um edge estatisticamente sólido tem magnitude
> superestimada. Por isso o próximo passo para confiar nisso é **dado limpo** (membership
> point-in-time + preços de delisted), não mais tuning de estratégia.

Nada aqui muda o mandate §1 (maintenance mode, capital fora deste repo).

---

## Funil em 3 fases

| Fase | O que faz | Promoção? |
|---|---|---|
| **broad** | Grade ampla diagnóstica (score × lookback × top-N × rebalance/offset × peso × abs-filter). Métricas após imposto BR 15%, dominância rolante, MDD de crise, turnover. | Não — é um mapa. |
| **evolution** | Pega os melhores finalistas do broad (por **Sharpe + Calmar**) e cruza com overlays de MM (SPY SMA200 mensal/diário, stock SMA100, combos) × offsets fixed/staggered. | Não — diagnóstico de stress. |
| **validate** | Gates duros no conjunto pequeno, com trial count honesto (broad + evolution). | Sim, mas `promotion_eligible=false` por survivorship. |

Score modes: `raw_13612` `[stocks_on_the_move, p.60]`, `mom_12_1`, `vol_adjusted_13612`
`[systematic_trading, p.137-148]`, `clenow_trend` `[stocks_on_the_move, p.70-77, p.98]`,
`composite_mom_lowvol`. Overlays seguem Clenow `[stocks_on_the_move, p.66-67, p.81-82]` e
Gayed `[leverage_for_the_long_run, p.9, p.13, p.16]`. Simulação shifted-weight evita
look-ahead `[advances_fin_ml, p.31-34]`.

---

## Resultados do run canônico (2026-06-16)

Universo: `2301/7136` US stocks passam os filtros. Duas janelas, cada uma `840` configs
broad + `144` evolution (trial count honesto `984`). Benchmark = SPY.

**SPY buy-and-hold (referência):** 1990+ CAGR `10,82%` / MDD `−55,19%` / Sharpe `0,65`;
2000+ CAGR `8,83%` / MDD `−55,19%` / Sharpe `0,54`.

**Melhores do broad (research-only, números inflados por survivorship):**

| Janela | Lente | Estratégia | CAGR | MDD | Sharpe | Calmar |
|---|---|---|---|---|---|---|
| 1990 | Sharpe | `clenow_trend lb1_3_6_12 top15 reb1` | 46,4% | −58,3% | 1,21 | 0,80 |
| 1990 | Calmar | `raw_13612 lb6 top10 reb1` | 58,3% | −65,8% | 0,93 | 0,89 |
| 2000 | Sharpe | `raw_13612 inverse_vol lb1_3_6_12 top20 reb3` | 43,3% | −64,7% | 1,16 | 0,67 |
| 2000 | Calmar | `raw_13612 lb6 top5 reb6` | 68,7% | −66,8% | 0,79 | 1,03 |

**Validate (gates honestos) — `overall_pass=True` nas duas janelas:**

| Janela | set-PBO | Finalistas que passam todos os gates | DSR p | WF | Bootstrap CI-low Sharpe |
|---|---|---|---|---|---|
| 1990 | `0,000` | `clenow_trend lb1_3_6_12 top15/top20 reb1` (sem overlay) | ≈0 | 8/8 | ~0,85 |
| 2000 | `0,357` | `raw_13612 lb6 top20 reb3` (fixed/staggered) + `…inverse_vol lb1_3_6_12 top20 reb3` | ≈0 | 8/8 | ~0,67–0,78 |

Achados adicionais que se mantêm:
- **Dominância rolante regime-estável:** as duas janelas elegem independentemente a mesma
  família `raw_13612 inverse_vol lb6 top20 reb3` como melhor dominância (~95,5%).
- **Overlays de MM protegem em crise:** cortam o MDD da GFC de ~`−56%` para `−12%` (1990) /
  `−20%` (2000), ao custo de CAGR.

Relatórios completos: `universes/us_stocks/from_1990/reports/` e `from_2000/reports/`.

---

## Estratégias recomendadas (top_n 3-10, gerenciáveis na mão)

`top_n=15/20` domina os tops irrestritos, mas é chato de executar manualmente.
Recortando para `top_n ∈ {3,5,10}` (504 de 840 configs por janela; `TOPN_3_10.md`),
o sinal quase não piora — reduzir de top20 → top10 custa pouquíssimo em
dominância/Sharpe. Três picks, com métricas nas duas janelas (research-only,
após imposto BR 15%, bruto de custos):

| Perfil | Estratégia | Holdings | Rebal | CAGR 1990 / 2000 | MDD 1990 / 2000 | Sharpe 1990 / 2000 | Calmar 1990 / 2000 |
|---|---|---|---|---|---|---|---|
| Melhor Sharpe + regime-estável | `clenow_trend lb1_3_6_12 top10 reb1` | 10 | mensal | 51,1% / 47,5% | −63,0% / −58,9% | **1,20 / 1,13** | 0,81 / 0,81 |
| Menos nomes | `clenow_trend lb1_3_6_12 top5 reb1` | 5 | mensal | 59,1% / 54,5% | −67,8% / −63,1% | 1,12 / 1,06 | 0,87 / 0,86 |
| Calmar / menos esforço | `raw_13612 lb6 top5 reb6` | 5 | semestral | 62,4% / 68,7% | −71,3% / −66,8% | 0,79 / 0,79 | 0,87 / **1,03** |

`clenow_trend lb1_3_6_12 top10 reb1` é o destaque: **#1 por dominância E por Sharpe
nas duas janelas** — momentum de trend suave (Clenow), 10 nomes, rebalance mensal.

### Plots vs SPY (equity / drawdown / equity relativa)

Pick destaque — `clenow_trend top10 reb1`, mostrando estabilidade entre regimes:

![clenow top10 — 1990](universes/us_stocks/from_1990/plots/topn_3_10/momv2_us_stocks_clenow_trend_lb1_3_6_12_top10_reb1_off0_vs_SPY.png)
![clenow top10 — 2000](universes/us_stocks/from_2000/plots/topn_3_10/momv2_us_stocks_clenow_trend_lb1_3_6_12_top10_reb1_off0_vs_SPY.png)

Menos nomes — `clenow_trend top5 reb1` (1990):

![clenow top5 — 1990](universes/us_stocks/from_1990/plots/topn_3_10/momv2_us_stocks_clenow_trend_lb1_3_6_12_top5_reb1_off0_vs_SPY.png)

Calmar / menos esforço — `raw_13612 lb6 top5 reb6` (2000):

![raw top5 reb6 — 2000](universes/us_stocks/from_2000/plots/topn_3_10/momv2_us_stocks_raw_13612_lb6_top5_reb6_off0_vs_SPY.png)

Demais plots (top picks por lente, ambas as janelas) em
`universes/us_stocks/from_<ano>/plots/topn_3_10/` e listados em `TOPN_3_10.md`.
Lembrete: MDDs fundos (~−60% a −71%) e CAGRs inflados por survivorship — leitura é
por Sharpe/Calmar, `promotion_eligible=false`.

---

## Reduzindo o drawdown (sweep de alavancas)

Os MDDs full de ~−63% são melhoráveis — e a alavanca vencedora **não** é o SMA do
SPY, é **vol-targeting** (escalar a exposição pela vol realizada da carteira, só
de-risk, lag anti-look-ahead `[systematic_trading, p.137-148]`,
`[advances_fin_ml, p.31-34]`). Sweep completo em `reports/DRAWDOWN_SWEEP.md`.
Pick destaque `clenow_trend top10 reb1`, janela 1990 (after-tax):

| Alavanca | CAGR | **MDD full** | GFC MDD | Vol | Sharpe | Calmar |
|---|---|---|---|---|---|---|
| baseline (sem overlay) | 51,1% | **−63,0%** | −58,9% | 41,6% | 1,20 | 0,81 |
| **vol-target 15%** | 20,9% | **−25,2%** | −23,7% | 16,0% | **1,27** | **0,83** |
| vol-target 20% | 27,9% | −32,6% | −30,5% | 21,3% | 1,26 | 0,85 |
| vol-target 25% | 34,0% | −39,6% | −36,9% | 26,3% | 1,24 | 0,86 |
| SPY SMA200 mensal | 40,9% | −63,0% | **−17,6%** | 36,2% | 1,13 | 0,65 |

Leitura:
- **Vol-targeting corta o MDD full** de −63% → −25% (alvo 15%) e ainda **melhora
  Sharpe (1,20→1,27) e Calmar (0,81→0,83)** na janela 1990. De-risca em qualquer
  regime de alta vol — inclusive os momentum-crashes que o filtro de mercado não vê.
  O custo é CAGR (era justamente a parte volátil/inflada). Padrão se repete em 2000.
- **SPY SMA200** = proteção de **crise** (GFC −59%→−18%), mas não mexe no MDD full em
  1990 (em 2000 corta pra −46% e dá o melhor Calmar). Bom como complemento, não como
  redutor principal de MDD.
- **Low-vol composite** corta MDD (−40%) mas derruba Sharpe (0,61) — troca ruim.
  **Diversificação** (top3→top10) ajuda pouco dentro de 3-10 (−76% → −63%).

**Recomendação:** se o objetivo é cortar drawdown mantendo retorno ajustado a risco,
**vol-target 15-20%** é a alavanca; combinar com SMA200 (proteção de crise) é o
próximo teste natural (combo ainda não medido). Custo = CAGR menor.

### Plots — `clenow top10`, 1990 (baseline → SMA200 → vol-target)

![baseline](universes/us_stocks/from_1990/plots/drawdown_sweep/clenow_trend_lb1_3_6_12_top10_reb1__baseline__sem_overlay__vs_SPY.png)
![SMA200 mensal](universes/us_stocks/from_1990/plots/drawdown_sweep/clenow_trend_lb1_3_6_12_top10_reb1__SMA200_market_sma200_monthly_vs_SPY.png)
![vol-target 15%](universes/us_stocks/from_1990/plots/drawdown_sweep/clenow_trend_lb1_3_6_12_top10_reb1__vol-target_15pct_vs_SPY.png)

Gerar/atualizar: `uv run python studies/momentum_v2/drawdown_sweep.py --universe us_stocks --start 1990-01-01`.
Continua `promotion_eligible=false` (survivorship é o teto, independente do drawdown).

---

## Decisões de design relevantes (e notas de honestidade)

- **Lente de seleção = Sharpe + Calmar** (`evolution.selection_metrics`), por escolha do
  objetivo retorno/risco. A dominância rolante segue reportada como coluna; ela também era
  regime-estável, então o resultado não depende de uma única métrica.
- **WF não bloqueia por MDD.** O cap de `−25%`/janela embutido no walk-forward era *mais
  estrito que o mandate* (§5: "CAGR/MDD são tiers, não bloqueantes"). Foi alinhado para WF
  puro `≥6/8` lucrativo. Isso foi alinhamento ao mandate, **não** threshold-fitting depois
  de ver o FAIL inicial.
- **Cross-library check corrigido.** Antes comparava a curva *com overlay* contra a
  holdings-loop da *base* (estratégias diferentes → Δ falso). Agora compara a **mesma**
  base de dois jeitos (vetorizado vs holdings-loop), validando o engine `[advances_fin_ml,
  p.31-34]`.

---

## Como rodar

```bash
# auditar cobertura/filtros (sem rodar o grid)
uv run python studies/momentum_v2/run.py --universe us_stocks --audit-only

# funil completo, janela primária 1990 (--cache-panels reusa 1 load de Postgres entre as fases)
uv run python studies/momentum_v2/run.py --universe us_stocks --phase broad     --start 1990-01-01 --cache-panels
uv run python studies/momentum_v2/run.py --universe us_stocks --phase evolution --start 1990-01-01 --cache-panels
uv run python studies/momentum_v2/run.py --universe us_stocks --phase validate  --start 1990-01-01 --cache-panels

# robustez de regime: repetir com --start 2000-01-01
# outros universos depois: --universe us_etfs | br_stocks | us_mixed ...
```

Saída namespaced por janela: `universes/<universe>/from_<ano>/{results,plots,reports,cache}`,
com schema idêntico entre universos.

Recorte por nº de holdings (executabilidade manual) — re-rankeia o `broad_results.csv`
restrito a um intervalo de `top_n`, por dominância, Sharpe e Calmar:

```bash
uv run python studies/momentum_v2/topn_view.py --universe us_stocks --start 1990-01-01 --min-top-n 3 --max-top-n 10 --k 20
# escreve reports/TOPN_3_10.md
```

---

## Próximos passos

Comandos, hipóteses e providers de dados detalhados em **`TODO.md`**.

1. **Atacar o survivorship** (único teto que sobrou): membership point-in-time do S&P 500 +
   preços de empresas delisted. Sem isso, nenhum PASS aqui vira promovível. `TODO.md` lista
   providers candidatos (Norgate, Sharadar, EODHD, …).
2. Rodar outros universos (`us_etfs`, `us_mixed`, `br_stocks`) — só `--universe`, sem código novo.
3. Arquivar `momentum/` e `momentum_13612_universes/` (mantidos como referência read-only;
   este estudo os consolida e supera).

---

## Status e disclaimers

Research-only. `promotion_eligible=false` em toda linha. Rankings são após imposto BR 15%
de ganho realizado, **brutos** de custos de transação/slippage. Benchmark sempre SPY.
Mandate §1 inalterado — sem deploy. Spec técnica: `../../docs/specs/momentum_v2.md`.

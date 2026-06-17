# Momentum v2 — funil de momentum cross-sectional (research-only)

Funil `broad → evolution → validate` por universo: a cada fim de mês rankeia o universo por um
score de momentum, segura o top-N (equal ou inverse-vol), aplica os gates honestos do mandate
`[advances_fin_ml, p.208-211, p.273-275]`. Seleção de finalistas pela dominância rolante
`equity/equity_benchmark` (`rolling_rel_score`) `[testing_tuning, p.327-335]`. **Tudo
`promotion_eligible=false`** — após imposto BR 15%, bruto de custos, benchmark por universo.

## TL;DR (2026-06-17)

- **EUA — duas famílias lideram as DUAS janelas (1990 e 2000):** `clenow_trend` (lb1_3_6_12, top10, reb2)
  e `raw_13612` (lb6, top15). PBO-broad robusto (N≈1000) passa nas duas (**0.02 / 0.14**); gates por-config 6/6.
- **BR — NÃO confirma:** as mesmas famílias caem para rank **#53 / #38** de 1260; quem lidera é
  `vol_adjusted_13612` e `composite_mom_lowvol`. **PBO-broad = 0.853 → FAIL**, 0/6 nos gates. O edge **não
  é universal — é específico dos EUA**.
- **Teto que prende tudo:** survivorship. CAGRs brutos de 25–63% e curvas $1→$1.5M são inflados (yfinance
  sem delisted); PBO/DSR/WF não corrigem. Nada promovível — **research-only**.
- **Refinamentos não furam a parede:** sweep de tamanho (n=10–50), custos e filtros de média móvel
  (entrada + stop intra-período) — nenhum melhora o risco-ajustado; o único que corta o drawdown
  (stop MM50: −66%→−43%) sacrifica retorno demais (Sharpe/Calmar pioram). Detalhe abaixo.

## As duas famílias (EUA) — dominância atemporal entre janelas

| Família | Config | US 1990 (`rolling_rel` / rank / CAGR) | US 2000 |
|---|---|---|---|
| **clenow_trend** `[stocks_on_the_move, p.70-77]` | `lb1_3_6_12 · top10 · reb2` | 0.954 · #1 · 58% | 0.952 · #1 · 60% |
| **raw_13612** `[stocks_on_the_move, p.60]` | `lb6 · top15` | 0.953 · #2 · 50% | 0.948 · #2 · 46% |

Mesmos parâmetros, scores quase idênticos, #1 e #2 nas duas janelas — o ranking é estável no tempo.
Ambas passam 6/6 nos gates por-config (DSR / WF / bootstrap / xlib) em 1990 **e** 2000.

| ![clenow EUA](universes/us_stocks/from_1990/plots/focus/clenow_trend_lb1_3_6_12_top10_reb2_vs_SPY.png) |
|:--:|
| `clenow_trend` top10 — EUA 1990 (equity \| drawdown \| equity relativa). O eixo `1e6` = survivorship. |

| ![raw EUA](universes/us_stocks/from_1990/plots/focus/raw_13612_lb6_top15_reb1_vs_SPY.png) |
|:--:|
| `raw_13612` lb6 top15 — EUA 1990. |

## Custos e turnover (líquido)

As duas famílias **giram muito** — turnover anual ~370–530%, holding ~2–3 meses — e o backtest é
**bruto de custos**. O engine agora aceita um custo linear (`cost_bps` por unidade negociada) e um
buffer de ranking opcional (`rank_buffer`, histerese tipo Clenow `[stocks_on_the_move, p.98-99]`).
After-tax, EUA 1990:

| Família | turnover | @0 | @25bps | @50bps | @100bps |
|---|---|---|---|---|---|
| `clenow_trend` top10 reb2 | 4.18 | 58.2% | 55.2% | 52.3% | 46.5% |
| `raw_13612` top15 reb1 | 5.34 | 50.1% | 46.5% | 43.0% | 36.1% |
| `raw_13612` top15 reb1 **+buffer** | 3.66 | 52.1% | 49.6% | 47.1% | 42.2% |

1. **Custos mordem, mas não explicam a implausibilidade.** A 50 bps o drag é ~5–7 pp; a 100 bps
   ~10–14 pp. O CAGR segue alto porque a base é inflada por survivorship — não porque custo seja
   pequeno (em small/mid caps, 50–100 bps round-trip é plausível).
2. **O buffer ajuda onde o giro é maior.** Em `raw_13612` (mensal, turnover 5.34) ele corta o giro
   ~31% (→3.66) **e** melhora o retorno (evita whipsaw): a 100 bps, 36.1%→42.2%. Em `clenow_trend`
   (reb2, giro menor) ele custa sinal e **não** compensa — redução de turnover não é ganho grátis.
3. **Melhor config líquida:** `raw_13612 top15 reb1 + buffer`, que domina a versão sem buffer em
   todos os níveis de custo. Continua research-only/survivorship-capped — não é recomendação de deploy.

`cost_bps` e `rank_buffer` têm default 0 (= comportamento anterior, bit-idêntico).

## Tamanho de portfólio e filtros de média móvel (refinamentos testados)

Testados só nas 2 famílias (hipóteses declaradas, não busca de grid). Nenhum fura a parede do drawdown.

- **Tamanho (n = 10→50, reb2):** n↑ ⇒ CAGR↓ **e** Sharpe↑ (pico ~n=40–50), turnover↓ — tradeoff
  concentração×diversificação. Mas o **MDD estaciona em ~−58% em qualquer n** (crash de momentum é
  sistêmico, não diversificável) e o `rolling_rel` é ~plano. Diversificar **não cura** o drawdown.
- **Filtro de entrada (preço > MM200 no rebalance):** ~neutro — momentum e "acima da MM" são quase a
  mesma coisa (EMA200 ajuda o `raw_13612` à margem).
- **Stop intra-período por-ação** (mecanismo novo, mira o drawdown): *gate* (re-entra) sofre whipsaw —
  turnover dispara 6–7× e o CAGR líquido vira ~0. *stop MM50* (caixa até o rebalance) é **a única coisa
  que corta a parede** — MDD −66%→**−43%** (1990 e 2000) — **mas** o CAGR despenca (49–58%→16–20%) e
  Sharpe/Calmar/dominância **pioram**: troca mais retorno do que risco. (MM20 é apertada demais: CAGR ~3%.)

**Conclusão:** o stop MM50 é uma escolha de *perfil conservador* (drawdown mais segurável, ~15% CAGR
líquido), não uma melhora risco-ajustada. Reforça o veredito: o teto é survivorship, não a forma da regra.
Engine: `stock_above_ma` (`overlays.py`); experimento: `ma_overlay_test.py`.

## Cross-universo: BR não confirma o edge

Re-rodado em `br_stocks` (janela efetiva 2009–2026, benchmark BOVA11.SA, 132 ativos). As duas famílias
**não lideram** e o PBO robusto reprova:

| | Família | `rolling_rel` | rank/1260 | CAGR | Sharpe |
|---|---|---|---|---|---|
| Lidera BR | `vol_adjusted_13612` lb6_12 top5 reb1 | 0.970 | #1 | 34% | 1.34 |
| Lidera BR | `composite_mom_lowvol` lb1_3_6_12 top10 reb2 | 0.970 | #3 | 25% | 1.26 |
| Foco (EUA) | `raw_13612` lb6 top15 reb2 | 0.964 | **#38** | 25% | 1.08 |
| Foco (EUA) | `clenow_trend` lb1_3_6_12 top15 reb2 | 0.963 | **#53** | 24% | 1.06 |

| ![clenow BR](universes/br_stocks/from_2000/plots/focus/clenow_trend_lb1_3_6_12_top15_reb2_vs_BOVA11.SA.png) |
|:--:|
| `clenow_trend` — BR (vs BOVA11): dominância mais fraca e mais curta que nos EUA. |

**Veredito BR: FAIL** — PBO-broad **0.853**, validate overall=False (0/6 gates). A família vencedora muda
de mercado, então a dominância dos EUA **não generaliza**.

### Por que a top-2 dos EUA não lidera o BR

**Em boa parte não é diferença econômica — é ruído de amostra pequena.** O BR reprova no PBO robusto
(0.853) e o topo é um cluster apertado: a dupla dos EUA fica em `rolling_rel` 0.963–0.964 vs 0.970 das
líderes (~0,6pp), e isso só vira rank #38/#53 porque centenas de configs se amontoam perto do teto —
"quem é #1" no BR não é um ordenamento estável.

Ainda assim, três fatores estruturais tendem a favorecer as variantes **conscientes de volatilidade**
(`vol_adjusted_13612`, `composite_mom_lowvol`) sobre o momentum/trend puro dos EUA:

1. **Dispersão de vol, não o nível.** A vol anualizada mediana é quase igual (EUA 39,7% / BR 39,3%), mas
   os EUA têm cauda bem mais gorda (p75 54% vs 46%, IQR ~1,8×). Momentum puro se alimenta dessa cauda de
   nomes ultra-voláteis que — por survivorship — sobreviveram com retornos enormes (daí a curva $1→$1,5M).
   O BR é mais comprimido e raso (132 vs 2300 nomes), então penalizar/normalizar a vol deixa de custar
   caro e passa à frente num pelotão apertado; o anômalo de baixa-vol também é mais forte em emergentes
   menos arbitrados `[systematic_trading, p.137-148]`.
2. **Regime e horizonte.** Os EUA cobrem múltiplos ciclos (dotcom, GFC), onde a qualidade-de-tendência do
   Clenow (slope×R²) reaparece `[stocks_on_the_move, p.70-77]`; o BR é só pós-GFC (2009–2026, ciclo de
   commodities + recessão 2014-16), janela única e mais chicoteada, onde trend puro toma mais whipsaw.
3. **Métrica de seleção.** `rolling_rel_score` premia consistência de `equity/equity_benchmark`; num
   universo fino e volátil-por-nome, as famílias vol-aware entregam equity relativa mais estável e ganham
   a métrica de consistência por margem pequena.

**Resumo:** as vol-aware "vencem" o BR mais por estabilidade num ranking que **não passa no PBO** do que
por um prêmio econômico sólido — coerente com o veredito geral: o edge é específico dos EUA (e inflado por
survivorship), e o BR não tem um momentum robusto, então a troca de família no topo é, sobretudo, ruído.

## Leitura honesta: PBO + survivorship

PBO em três níveis; só o de N≈1000 é estatisticamente confiável:

| PBO | N | US 1990 | US 2000 | BR |
|---|---|---|---|---|
| **Broad (robusto)** | ≈1000 | 0.020 ✅ | 0.139 ✅ | **0.853 ❌** |
| Validate (set) | 6 | 0.425 ✅ | 0.548 ❌ | 0.198 (0/6 por-config) |

O set-PBO de N=6 é ruído (`pbo.py`, `MIN_HONEST_N_CONFIGS=4`) e oscila com a receita de seleção — não
gatilhe decisão nele. O sinal honesto: **EUA passa o PBO robusto, BR não.** E mesmo o PASS dos EUA está
**inflado por survivorship** — `rolling_rel≈0.95` e CAGRs de 47–63% não são atingíveis; PBO/DSR/WF não
corrigem isso `[advances_fin_ml, p.208-211]`. **`promotion_eligible=false`** (mandate §1/§5).

## Funil em 3 fases

1. **broad** — grid de 1260 configs (5 score modes × 4 lookbacks × top-k {1,3,5,10,15} × rebalance
   {1,2,3,4,6,12} × {equal,inverse_vol} × {±abs_cash}); mapa diagnóstico + PBO sobre N≈1000.
2. **evolution** — top-6 finalistas por `rolling_rel_score` × overlays (SMA200/SMA100) × offsets fixo/staggered.
3. **validate** — gates duros sobre os finalistas: PBO<0.5, DSR p<0.05, WF≥6/8, bootstrap CI-low>0, xlib ±3pp.

## Como rodar

```bash
# funil completo (--jobs paraleliza broad/evolution via fork Pool, resultado bit-idêntico; --cache-panels reusa 1 load de Postgres)
uv run python studies/momentum_v2/run.py --universe us_stocks --phase broad     --start 1990-01-01 --cache-panels --jobs 16
uv run python studies/momentum_v2/run.py --universe us_stocks --phase evolution --start 1990-01-01 --cache-panels --jobs 16
uv run python studies/momentum_v2/run.py --universe us_stocks --phase validate  --start 1990-01-01 --cache-panels
# robustez de regime: --start 2000-01-01 ; outros universos: --universe br_stocks | us_etfs | ...
# snapshot para o web-app (portfólio atual/histórico/contribuição por estratégia):
uv run python studies/momentum_v2/portfolio_export.py --universe us_stocks --start 1990-01-01
```

Saída por janela: `universes/<universe>/from_<ano>/{results,plots,reports,cache,portfolio}`.

## Web-app

Visualização/comparação/explicação das estratégias + portfólio atual e histórico (entradas/saídas,
contribuição por ticker, equity/drawdown): **[`webapp/`](webapp/README.md)** (FastAPI + React, deployável).

## Próximos passos · Status

1. **Atacar survivorship** (único teto restante) — membership point-in-time + preços de delisted (providers em `TODO.md`). Sem isso nenhum PASS vira promovível.
2. Tornar o set-PBO da validate honesto (alargar finalistas) ou gatilhar pelo PBO-broad.

Research-only, `promotion_eligible=false`, mandate §1 inalterado — sem deploy. Spec: `../../docs/specs/momentum_v2.md`.

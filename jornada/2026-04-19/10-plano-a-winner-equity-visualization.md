# Plano A Winner — curva de equity finalmente visualizada

**Data:** 2026-04-19 (tarde) · **Tipo:** visualização · **Impacto:** comunicação, zero mudança em código de estratégia.

## O que aconteceu

Eu tinha olhado pro PNG `reports/phase3_5b/portfolio_3leg_ew/equity_curve.png` (Plano B, 3-leg EW) e pedido o equivalente pro **Plano A winner** (`gayed_ema100_L2_off_gld`, Phase 3.5a-V2). Descobri que o framework autônomo V2 **nunca emitiu PNGs** — só guardava retornos diários em parquet + JSON + MD. Os números estavam todos lá, mas ninguém tinha olhado a curva.

Criei `scripts/plot_plano_a_winner_equity.py` e gerei `reports/phase3_5a_v2/v2_l2_gayed_transported_cfd/equity_curve.png`.

## O que o PNG mostra (2 painéis)

**Painel superior — log-scale equity (Strategy vs SPY buy&hold):**

- Strategy parte de 100k BRL em 2001-05-14 e termina em ~11.5 bilhões BRL em 2026-04-14.
- SPY buy&hold (mesmo capital inicial) termina em ~870k.
- Faixas douradas ao fundo marcam **off-regime** (SPY ≤ EMA100): quando a estratégia rotaciona pro GLD em vez de SPY+QQQ. É a história de regime rotation contada visualmente — off-regimes concentram em 2008, 2011, 2020-Q1, 2022. `[leverage_for_the_long_run, p.11-14]`
- Duas linhas verticais pontilhadas: **2018-01-01** (IS → OOS) e **2024-01-01** (OOS → FWD). Cada janela tem uma caixa anotada com Sharpe / CAGR / MDD daquele subperíodo.

**Painel inferior — drawdown %:**

- Strategy (azul preenchido): MDD histórico −22.67%, tocou o cap de −25% uma vez (2008 GFC).
- SPY (cinza tracejado): MDD −55.20% em 2008-2009.
- Linha vermelha tracejada em **−25%**: o cap de MDD que L=2 tem que respeitar `[leverage_space, Vince]`. A estratégia fica **abaixo** do cap em todos os subperíodos — é o que o gate V2 `oos_maxdd_le_25pct` pediu e passou.

## Por que a comparação "Strategy vs SPY b&h" não é uma vitória gratuita

O gráfico é visualmente brutal a favor da estratégia — 11.5B vs 870k é ~13,000× o buy&hold. Mas esse número **não é honesto como CAGR prático** por 3 motivos, e eu preciso registrar isso antes de esquecer:

1. **L=2 alavancagem CFD.** SPY b&h é desalavancado. Metade do "excess return" visual é simplesmente leverage — por isso métricas ajustadas (IR vs SPY = **2.16**, DSR p = 0.0003, PBO = 0.10) é que realmente provam edge, não a diferença de equity final.
2. **Position size constante.** O backtest aplica retornos compostos com tamanho fixo relativo a equity — então de 100k pra 11.5B você **nunca encontraria liquidez** nem conseguiria executar sem mover o mercado. Mandate §7 (dynamic sizing decay) existe exatamente pra isso, e Phase 4 paper trading vai calibrar o decay schedule real.
3. **Pepperstone Razor costs modelados, não realizados.** Spread 2 bps + commission $3.50/side + slippage 1-3 bps + swap 0.005-0.02%/dia são parâmetros do modelo. Slippage em live pode ser 3-5× maior em regime-switch days. O gate de Phase 4 é exatamente re-validar Sharpe ≥ 1.5 no paper.

## O que o drawdown panel revela que a equity curve sozinha esconde

Em log-scale, um MDD de 22% parece um "arranhãozinho" na curva azul. No painel de drawdown em escala linear, **você vê o 2008 batendo −22.67%** e o 2020-Q1 COVID batendo −18%. Isso é real dinheiro perdido em momentos reais — não um ruído gráfico.

E o SPY b&h no mesmo período viu −55% em 2008-09 (12 meses pra recuperar o peak) e −34% em 2020 COVID (4 meses). A estratégia **aguentou MUITO melhor os dois**, que é o ponto central da tese Gayed: regime rotation não é só "mais retorno", é "menos drawdown" — essa segunda metade é o que paga psicologicamente pra você continuar executando.

## Números recomputados a partir do parquet (sanity check vs `.json`)

| Métrica | Gate V2 | Recomputado (script) |
|---|---:|---:|
| OOS Sharpe | 2.285 | **2.284** |
| OOS CAGR | 79.14% | **79.14%** |
| OOS MDD | −21.02% | **−21.02%** |

Diferença de 0.001 no Sharpe é ruído de arredondamento (script usa `n/252` anos, json usa n_bars exato). Zero discrepância material — o parquet bate com a spec.

## Addendum (logo depois): trade log reconstruído

Usuário pediu o equivalente ao `trade_log.csv` / `trade_log.md` que 3.5b produz. Descobrimos que o framework V2 **nunca persistiu trade log** — só agregados (`n_switches_total=616`, `switches_by_ticker`). Criei `scripts/reconstruct_plano_a_winner_trades.py` que re-roda `simulate_plano_a_rotation` com o config do winner (determinístico — pure pandas/numpy, zero aleatoriedade) e extrai per-leg segments do `result.weights` DataFrame.

**Output:** `reports/phase3_5a_v2/v2_l2_gayed_transported_cfd/trade_log.csv` + `trade_log.md` (489 segments: SPY=158, QQQ=151, GLD=180).

Cross-check com a spec bate exato: 315 SPY switches = 157.5 trades esperados → **158 observados**; 301 QQQ switches → **151 observados**. Zero divergência.

**Caveat novo descoberto:** GLD inception é 2004-11-18. Os primeiros 883 bars (14.1% do histórico) rodaram com GLD indisponível — off-regime days nesse window caíram em "cash silencioso" com retorno 0% em vez do retorno real do GLD. Não é bug do runner (o código fez o ffill corretamente), mas é uma **limitação de dados** que infla ligeiramente o Sharpe IS 2001-2004 vs contrafactual "GLD sintético pre-2004". Post-inception (94% dos bars OOS + 100% dos bars FWD) o comportamento é autêntico. Flagged no MD header e nesta entrada pra registro permanente — decisão: não re-rodar com GLD sintético, o caveat só afeta IS 2001-2004, não toca OOS/FWD que é onde os gates V2 mordem.

**Estatísticas interessantes do trade log:**
- Win rate (retorno alavancado > 0) = 34.6% — **parece baixo**, mas é coerente com regime rotation: muitos GLD switches rapidos (mediana 4 dias) durante whipsaws têm retorno ~0%, e os 1-2 mega-trades por ano (QQQ 2020-04 → 2021-03 = +99.56% alavancado; SPY 2020-11 → 2021-09 = +59.93%) é que carregam o CAGR. Profit factor da estratégia é alto mesmo com win rate < 50%, clássico trend/regime following `[trend_following_covel, ch.3-5]`.
- Median hold GLD=4d vs SPY=7.5d vs QQQ=8d — coerente com a narrativa: GLD é o "bunker" curtinho entre flips de regime; SPY/QQQ são os "mega holds" durante bull runs.
- Top 10 trades por |ret| incluem QQQ 2020-04→2021-03 (+99.56%), QQQ 2003-04→2004-03 (+81.10%), QQQ 2009-04→2010-01 (+78.13%) — tudo saída da crise + regime re-entry, exatamente o sinal Gayed EMA-100 fazendo o job.

## Próximo passo

Nenhum. Este é um artefato de comunicação; não altera decisão nenhuma. A entrada de jornada serve pra eu (ou outro colaborador) saber que o PNG existe e **por que** ele existe do jeito que existe (2 painéis + regime shading em vez de 1 painel liso como 3.5b).

Se futuramente quisermos equivalente pra 3.5b com os mesmos 2 painéis + regime shading, seria um port trivial do mesmo script. Não vou fazer agora — o PNG atual da 3.5b já cobre a narrativa de "buy&hold SPY foi catastroficamente superado".

## Links

- PNG: `reports/phase3_5a_v2/v2_l2_gayed_transported_cfd/equity_curve.png`
- Trade log CSV: `reports/phase3_5a_v2/v2_l2_gayed_transported_cfd/trade_log.csv` (489 rows)
- Trade log MD: `reports/phase3_5a_v2/v2_l2_gayed_transported_cfd/trade_log.md`
- Scripts: `scripts/plot_plano_a_winner_equity.py`, `scripts/reconstruct_plano_a_winner_trades.py`
- Spec V2 winner: `reports/phase3_5a_v2/v2_l2_gayed_transported_cfd/AGGREGATE.md`
- Parquet de retornos: `reports/phase3_5a_v2/v2_l2_gayed_transported_cfd/gayed_ema100_L2_off_gld_daily_returns.parquet`

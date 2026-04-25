# 2026-04-24 22h07 — Hunt loop iter 028: VIX-filter VRP (Sinclair p.217 `VIX<35`) vira 71/100 PROMISING, **Kill A triggered** — filtro é regime-conditional: lift +0.13 Sharpe em educational (1ª DSR PASS ever nesse dataset, p=0.029, 7/7 gates) mas regride −0.07 a −0.10 em spy/ndx (assimetria: persistência vs transiência de regime)

**Tipo:** [HUNT LOOP] | **Estado:** Pesquisa em background (mandate §1
permanece 100% Plano C MAINTENANCE — qualquer winner é candidato, não
deploy).

## Sumário

Iter 027 fechou o caminho "alavancar a colheita" (leverage não é
Sharpe-neutral em total-return). Sobrou: **levantar o
`overlay_sharpe` intrínseco** (0.67/0.77/0.93 edu/spy/ndx) — o
componente que sobrevive sob alavancagem.

Iter 028 implementou a regra mais óbvia da literatura para fazer
exatamente isso: **Sinclair p.217** — "para estratégias short-vol em
índice, só abra posição quando `VIX < 35`". Traduzindo para o motor
iter 026: a cada vencimento natural, se VIX ≥ 35 no bar, pule a nova
abertura e colete só `rf_daily` até o próximo vencimento elegível.

Resultado foi o **achado mais rico do loop até agora**:

| dataset | Sharpe (Δ iter026) | gates | DSR p | overlay_sharpe Δ |
|---|---|---|---|---|
| educational (2006-2026, inclui 2008 GFC) | **+0.126** ✓ | **7/7** 🔥 | **0.0287** 🔥 | **+0.092** |
| spy_real (2009-2026, post-GFC) | **−0.101** ✗ | 6/7 | 0.1364 (piorou) | −0.113 |
| ndx_real (2010-2026, post-GFC) | **−0.067** ✗ | 6/7 | 0.0640 (piorou) | −0.073 |

Duas histórias simultaneamente:

1. **Educational explodiu**: 1ª passagem de gate 7/7 de qualquer iter
   no dataset mais longo (5100 bars). DSR p=0.029 — 1ª sub-0.05 DSR
   *ever* em educational. O filtro cortou 11 rolls (4.53%) que
   correspondem ao período 2008-Q4 e 2020-Q1 — exatamente os breach
   cycles que iter 026 absorveu e que continham o pior tail.
2. **Spy/Ndx regrediram**: Sharpe caiu em 2/3 → **Kill A
   TRIGGERED**. O filtro "economizou" na direção errada porque os
   4-6 rolls que ele pulou em spy/ndx eram *spike-e-reverte*
   (Mar-2020, 2022-rate-hike) onde iter 026 teria coletado ~1% de
   decay de prêmio dentro do cap de 4% sem quebrar. Pular essas
   rolls perdeu prêmio sem ganhar proteção.

## A assimetria estrutural

A regra de Sinclair é **pré-2010**. Naquele mundo, VIX alto significa
tipicamente regime sustentado (2000-2002 bear, 1987, 2008) — weeks-to-
months, onde a implícita fica muito acima da realizada e write
credit-spreads é estatisticamente perigoso.

**Pós-GFC**, VIX alto virou majoritariamente spike mean-reverting
(VIX>35 dura 3-7 dias em spy/ndx), em que a implícita "over-shoots"
por 1-2 semanas e volta. Dentro do dte=21 do spread, a mean-reversion
paga — iter 026 captura isso. Iter 028 pulou esses rolls e perdeu.

**A assimetria não é o nível do VIX, é a persistência do regime.**
A regra de Sinclair vs hoje (2010-2026) é um mismatch de regime.

## Score breakdown

| critério | pts | max | detalhe |
|---|---|---|---|
| 1 Sharpe edge vs frozen bench | 25 | 25 | 3/3 clear +0.10 (edu +0.58, spy +0.28, ndx +0.35 vs benchmarks 0.68/0.90/0.955) |
| 2 Gates | 21 | 25 | edu 7/7 + spy 6/7 + ndx 6/7 + cross-bonus |
| 3 DSR | **5** | 15 | worst p=0.136 (entre 0.10 e 0.20) |
| 4 CAGR floor | 0 | 15 | 0/3 (5.04/4.46/5.90% vs floors 9.18/11.98/15.35%) |
| 5 MDD ceiling | 15 | 15 | 3/3 (6.6/6.4/8.2%; iter 026 tinha 16.8/6.3/8.2 — MDD melhorou) |
| 6 Robustness | 5 | 5 | 9/9 sub-windows Sharpe > 0 |
| **total** | **71** | **100+5** | tier 🥈 PROMISING |

**Regressão 76→71 (−5)** é **100% causada por DSR worst-p**.
Educational melhorou p (0.083→0.029, +10 no componente DSR se fosse
isolado), mas spy regrediu (0.07→0.14) e worst-p é spy agora →
critério 3 cai de 10 para 5.

## O que isto informa sobre o caminho para WINNER

1. **O teto DSR educational não é ruído** — confirmado. Iter 026 ficou
   em 0.083, iter 028 quebrou para 0.029 com um filtro imperfeito.
   Com o filtro certo (regime-aware, que preserve spy/ndx), educational
   deve conseguir p < 0.05 mantendo a lift.
2. **Sharpe/gates cross-dataset é coberto** — 3/3 +0.10 gate passa,
   gates cruzam threshold (5/4/4). O único gap é DSR worst-p. Se
   spy/ndx voltarem ao nível iter 026 (p=0.07/0.04), worst-p ficaria
   em 0.07 → ainda fail, mas perto. Se também subirem um pouco
   (persistência-gate deve ajudar um pouco nisso por pular só os
   breach-cycles pós-2020), poderia-se chegar ~0.04-0.05 worst-p e
   virar WINNER.
3. **Caminho imediato: iter 029 = regime-aware gate**, especificamente
   **VIX-persistência** (só filtrar quando VIX > 35 por ≥ 3 dias
   consecutivos). Isso captura 2008-Q4 (sustained → filter skip é
   correto) mas deixa passar os spikes curtos de 2020-03 / 2022 /
   2024 (transient → iter 026 captura).

## O que NÃO foi pedido fazer

- Nenhum fine-tune do threshold (testar 30, 40, 25) — iter 028 prova
  que a dimensão que quebra é *persistência*, não *nível*. Fica no
  DEAD_ENDS.
- Nenhuma pré-commit em grid — só cfg único (`vrp_filtered_vix35_h1_5_10_1m`),
  threshold literal de Sinclair (35).
- Nenhuma mudança no mandate §1 — loop produz candidates, não deploys.

## Próximo passo concreto

**Iter 029 — R-1 VIX-persistence gate**:
1. Modificar `vrp_filtered.py` para aceitar `persistence_days: int = 3`
   (só filtra se VIX > threshold nos últimos `persistence_days`
   bars inclusive).
2. Re-implementar numpy reference + TDD specs (filter_off-at-k=0,
   parity quando persistence=1 == iter 028, skip conditional).
3. Rodar cross-dataset. Expected: educational mantém 7/7, spy/ndx
   recuperam Sharpe iter 026 (+1 porque 2008-Q4 ainda é capturado),
   worst-p possivelmente < 0.05 → WINNER candidate.

Cumulative n_trials: **4280 → 4281**.

## Citações usadas

- `[volatility_trading, p.217]` Sinclair — regra VIX<35 entry (era
  pré-2010, regime mismatch revelado aqui).
- `[volatility_trading, ch.3]` Sinclair — mecânica VRP.
- `[volatility_trading, p.41]` Sinclair — SPX kurtosis 21.3 justifica
  capped spread.
- `[advances_fin_ml, p.31-34]` López de Prado — G7 cross-library parity.
- `[advances_fin_ml, p.222-223]` López de Prado — DSR com cumulative
  n_trials.
- Bondarenko 2014 QJF 4(3) 1450015 — VRP regime-dependent.
- Carr-Wu 2009 RFS 22(3) 1311-1341 — IV-regime dependence da VRP.

## Arquivos gerados

- `studies/strategy_hunt_loop/iterations/028-2026-04-24-2207-vix-filter-vrp-primary/`
  - `hypothesis.md` — pré-commit completo com Kill criteria
  - `vrp_filtered.py` + `numpy_reference_filtered.py` — engines
  - `run_backtests.py` + `compute_gates_and_score.py` — pipeline
  - `results.json` + `verdict.json` — 71/100 PROMISING
  - `final_report.md` — relatório honesto
  - `plot_vs_benchmark_spy_real.png` + `plot_vs_benchmark_ndx_real.png`
- `tests/test_iter_028_vix_filter_vrp.py` — 7 specs TDD
- `studies/strategy_hunt_loop/BASE_MEMORY.md` — atualizado (iter 028
  entrada, top-K inalterado, direções iter 029 R-1/R-2/R-3 adicionadas;
  auto-prune aplicado 21.5→17.3 KB)
- `studies/strategy_hunt_loop/DEAD_ENDS.md` — nova seção "From
  iteration 028 — constant VIX<35 filter"

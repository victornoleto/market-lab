# 2026-04-24 21h44 — Hunt loop iter 027: Levered VRP-primary (`harvest_notional=3.5`) vira 74/100 PROMISING, **Kill A triggered** — leverage NÃO é Sharpe-neutral em total-return como teoria sugeria; CAGR floor 3/3 ✓ mas DSR colapsa (0.08→0.52)

**Tipo:** [HUNT LOOP] | **Estado:** Pesquisa em background (mandate §1
permanece 100% Plano C MAINTENANCE — qualquer winner é candidato, não
deploy).

## Sumário

Após iter 026 entregar +0.38-0.45 Sharpe alpha cross-dataset e a 1ª
passagem DSR de qualquer iteração no histórico (ndx p=0.038), iter 027
seguiu o caminho mais óbvio para WINNER: **alavancar a colheita** de
`harvest_notional=1.0` para `3.5`, esperando manter Sharpe (teoria
diz: leverage-neutral) e finalmente limpar o CAGR floor que estava
0/3. O resultado revelou um achado estrutural:

**Sharpe total-return NÃO é leverage-neutral quando a estratégia tem
componente rf constante.** A álgebra:

    Sharpe(N) = (rf_d + N × mean_h) / (N × σ_h) × √252
              = overlay_sharpe + rf_d / (N × σ_h) × √252

O primeiro termo é leverage-invariante (sharpe da colheita pura). O
segundo termo é **inversamente proporcional a N** — o "bonus rf"
dilui com a alavancagem. iter 026 N=1: o bonus adicionou ~0.46
Sharpe (0.67 overlay + 0.46 bonus = 1.13). iter 027 N=3.5: bonus
diluído para ~0.13 (0.67 + 0.13 = 0.80).

O teste TDD `test_iter027_sharpe_invariant_under_leverage` provou
corretamente que **excess-return Sharpe** É invariante. Mas o
benchmark + scoring do hunt-loop usa **total-return Sharpe** — onde a
diluição rf morde.

## Métricas headline

| dataset | Sharpe (Δ frozen) | CAGR | MDD | gates |
|---|---|---|---|---|
| educational | 0.80 (+0.12) | **11.43%** ✓ | 50.7% (under 60.1%) | 6/7 |
| spy_real    | 0.91 (+0.01) ✗ | **12.05%** ✓ | 23.1% | 6/7 |
| ndx_real    | 1.06 (+0.10) | **16.82%** ✓ | 28.8% | 6/7 |

CAGR floor: 3/3 ✓ (iter 026 era 0/3). MDD ceiling: 3/3 ✓. **Sharpe
edge gate**: spy fica em +0.014 (gate +0.10 falhado por 0.09);
edu/ndx passam.

DSR p (n=4280):
- educational: 0.517 (era 0.083 em iter 026 — colapso 6×)
- spy_real: 0.464 (era 0.070 — colapso 7×)
- ndx_real: 0.281 (era **0.038 — 1ª passagem ever**, agora reverted)

A 1ª passagem DSR do hunt-loop foi REVERTIDA pela alavancagem.

## Score breakdown

| critério | iter 026 | iter 027 | Δ |
|---|---|---|---|
| 1 Sharpe edge | 25 (3/3) | **20 (2/3)** | −5 |
| 2 Gates | 21 | 19 (ndx 7→6) | −2 |
| 3 DSR | 10 (worst p=0.083) | **0 (worst p=0.517)** | −10 |
| 4 CAGR floor | 0 | **15 (3/3 ✓)** | +15 |
| 5 MDD ceiling | 15 | 15 | 0 |
| 6 Robustness | 5 | 5 | 0 |
| **total** | **76** | **74** | **−2** |

O ganho de +15 em CAGR não compensou os −17 perdidos em Sharpe + DSR
+ Gates. Score regressão líquida 76 → 74.

## Strict winner conditions

| # | condition | iter 026 | iter 027 |
|---|---|---|---|
| 1 | Sharpe edge ≥ +0.10 on ≥ 2/3 | YES (3/3) | **YES (2/3 — edu+ndx)** |
| 2 | Gates: edu ≥5, spy ≥4, ndx ≥4 | YES | **YES (6/6/6)** |
| 3 | DSR worst p < 0.05 | NO (0.083) | NO (0.517) |
| 4 | CAGR floor ≥ 0.8×bench on ≥ 2/3 | NO (0/3) | **YES (3/3) ✓** |
| 5 | MDD ceiling +5pp on ≥ 2/3 | YES (3/3) | **YES (3/3) ✓** |

**4/5 winner conditions** — DSR é o sole gap (mesmo que iter 026, mas
mais distante do limiar agora). Não é WINNER.

## Kill criteria

- Kill A (Sharpe regress > 0.05 vs iter 026): **TRIGGERED** (3/3
  datasets, drops 0.31-0.37). Falsifica leverage-neutrality em total-
  Sharpe.
- Kill B (per-roll loss > 30%): NOT triggered (max 26.5% edu, sob 30%).
- Kill C (MDD ceiling fail ≥ 2): NOT triggered (3/3 clear).
- Kill D (CAGR floor 0/3): NOT triggered (3/3 clear — gain hipótese
  específica confirmado).
- Kill E (engine dirty G7 > 3pp): NOT triggered (0.0000 pp G7).

## Leitura

iter 027 é uma **iteração de fronteira**: o caminho mais simples para
WINNER (alavancar) está fechado. O ganho em CAGR é real (3/3 ✓
estructuralmente confirmado pela linearidade do harvest), mas o custo
em Sharpe + DSR é maior. iter 026's +0.38-0.45 alpha era N=1-específico
— o harvest-skill puro (`overlay_sharpe`) é apenas +0.07/−0.13/−0.02
vs benchmarks (i.e., NÃO um Sharpe edge em 2/3 datasets quando a
colheita é o único motor).

A direção forward NÃO é "alavancar mais" mas sim **levantar o
overlay_sharpe diretamente**:

1. **V-3 VIX-filter (Sinclair p.217)** em iter 026 base (N=1). Filtrar
   high-VIX opens deve lift overlay_sharpe de 0.67-0.93 para 0.80-1.05;
   o full-strategy Sharpe volta a 1.30+ e DSR pode passar < 0.05 em
   edu+spy. **Caminho mais provável para WINNER.** Single binary param.
2. **V-4 VRP + Carry composite** (0.5 × iter 026 + 0.5 × iter 024
   bond-carry). Carry decorrelacionado com VRP → composite σ² desce;
   adiciona CAGR sem diluir Sharpe.
3. **V-5 Strike refinement** (5/15% wider OU 3/7% closer-to-ATM).
   Afeta overlay_sharpe não-trivialmente.

## Pegadinha honesta

A regressão DSR é o sinal mais claro: alavancar uma estratégia já
enviada para DSR-borderline aumenta o "dispersão de hipóteses" do
denominador (DSR usa Sharpe na fórmula) sem proporcionalmente lift o
numerator. Em N=1 iter 026 ndx_real teve a 1ª passagem DSR; em N=3.5
isso reverteu. Lição: **DSR breakthrough at N=1 is a delicate
result** — sustentável apenas se a base tem `overlay_sharpe + rf_d/(N*σ)`
acima do deflator threshold. Alavancar quebra o balanço.

## Top-K do hunt loop (pós-iter-027)

| rank | iter | tier | score |
|---|---|---|---|
| 1 (tied) | 016/018/021 | STRONG | 79 |
| 4 | 015 | STRONG | 77 |
| 5 | 026 | STRONG | 76 |
| 6 (tied) | 008/010/027 | PROMISING | 74 |

iter 027 entra empate no #6 com iter 008 e iter 010. Não desloca
iter 026 do #5.

## Citações

- `[volatility_trading, ch.3]` (Sinclair) — VRP mechanics
- `[volatility_trading, p.41]` — capped tail SPX kurtosis 21.3
- `[volatility_trading, p.217]` — short-vol rule (referenciado mas
  não aplicado neste iter; reservado para iter 028 V-3)
- `[risk_parity, p.5]` — Asness-Frazzini-Pedersen 2012 levered low-vol
  (a tese que justificou o iter 027 — refutada empiricamente para
  total-return Sharpe)
- `[advances_fin_ml, p.31-34]` — G7 cross-lib parity
- `[advances_fin_ml, p.222-223]` — DSR cumulative n_trials
- Bondarenko 2014 QJF 4(3): 1450015
- Carr-Wu 2009 RFS 22(3): 1311-1341

## Próximo

iter 028 PICK: **Option V-3 — VIX-filter VRP-primary on iter 026 base
(N=1)**. Sinclair p.217 rule explícito (open only when VIX < 35).
Single binary param (cumulative_n_trials → 4281). Best forward path
para WINNER: lift overlay_sharpe 0.67-0.93 → 0.80-1.05, full-strategy
Sharpe volta a 1.30+, DSR p < 0.05 em edu+spy plausível.

Ver: `studies/strategy_hunt_loop/iterations/027-2026-04-24-2144-levered-vrp-primary/final_report.md`

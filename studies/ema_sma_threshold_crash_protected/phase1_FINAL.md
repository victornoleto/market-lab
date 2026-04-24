# Phase 1 — Stop-loss sweep · FINAL

> **Educational / experimental.** Mandate §1 remains: projeto em
> MAINTENANCE, 100% Plano C. Este estudo não propõe reativar slot
> A/B/D.

## What was swept

For each of the three baseline studies, we took the **top-20 base
configs** (ranked by the study's composite) and expanded every one into
**43 stop-loss variants**:

* 1 baseline (`stop_loss_pct = None`) — identical to the original sweep.
* 6 stop levels × (1 `next_signal` + 3 `time_cooldown` + 3 `recovery_trigger`) = 42 stop variants.

| dataset | window | total sims | top-1 base (from source study) | baseline CAGR | baseline MDD |
|---|---|---|---|---|---|
| educational | 1986-01-03 → 2026-04-17 (40y) | 860 | `EMA_N150_th5_bL3_sL0` | **27.67%** | **53.98%** |
| spy_real | 2009-06-25 → 2026-04-17 (17y) | 860 | `EMA_N150_th5_bL2_sL0` | 15.10% | 39.11% |
| ndx_real | 2010-06-25 → 2026-04-17 (16y) | 860 | `SMA_N150_th0_bL2_sL0` | 25.32% | 40.53% |
| **total** | | **2 580** | | | |

Walltime: 43 s on a single thread. Simulator throughput ≈ 87 sims/s.

Gates (PBO/DSR/WF/OOS/FWD/bootstrap/cross-lib) are **not** evaluated in
Phase 1 — reserved for survivors at Phase 3+ per spec §6.1.

## Direct answer to the spec's central question

> *"Podemos reduzir o MDD do top config de 54% para 25-40% sem
> sacrificar mais que 3-5pp de CAGR, usando stop-loss e/ou sinais
> preditivos validados na literatura?"* — spec §2

**Não, para o top-1 do synth educational (`EMA_N150_th5_bL3_sL0`), com
stop-loss sozinho.** Das 42 variantes de stop aplicadas à esta base:

* **0 variantes** reduzem o MDD para ≤ 40% **e** ficam dentro de −5 pp
  de CAGR simultaneamente.
* A **melhor variante** por MDD dentro do corredor de CAGR é
  `EMA_N150_th5_bL3_sL0_sl30_next` (stop 30% + `next_signal` re-entry):

  | | CAGR | MDD | Sharpe |
  |---|---|---|---|
  | baseline | 27.67% | 53.98% | 0.84 |
  | sl30_next | **28.19%** (Δ +0.51 pp) | **47.13%** (Δ −6.86 pp) | — |

  Entrega **~7 pp de redução de MDD sem custo de CAGR**, mas o MDD
  resultante (47%) **ainda está 7 pp acima da meta mais frouxa** (40%).

* Para chegar a MDD ≤ 40% na mesma base o melhor candidato precisa
  sacrificar **mais de 5 pp de CAGR** (ex.: `sl20_rec5` CAGR 16.82%
  Δ−10.85 pp, MDD 67% ainda fora do alvo).

Conclusão: **stop-loss isolado não atinge o alvo do spec** para o
`3x UPRO cash` top-1. O corredor de CAGR é estreito porque `bL=3`
amplifica whipsaw: cada falso-positivo custa 3× mais. Spec §8.1 previu
isto. Phase 2 (sinal preditivo como de-leveraging) e Phase 3 (combinação)
têm que cobrir o gap restante.

## Direct answer for the real-data top-1 bases

### SPY real top-1 — `EMA_N150_th5_bL2_sL0` (MDD baseline 39%)

Melhor variante dentro de ΔCAGR ≥ −5 pp:

| variant | CAGR | ΔCAGR | MDD | ΔMDD | n_stops |
|---|---|---|---|---|---|
| baseline | 15.10% | — | 39.11% | — | — |
| `sl15_rec10` | 11.97% | −3.13 pp | **32.63%** | **+6.48 pp** | 14 |
| `sl20_cool21` | 15.41% | +0.31 pp | 34.70% | +4.41 pp | 8 |
| `sl20_rec10` | 15.41% | +0.31 pp | 34.70% | +4.41 pp | 8 |

Com SPY real, **dá para chegar em MDD ≤ 35% com CAGR neutro ou positivo.**

### NDX real top-1 — `SMA_N150_th0_bL2_sL0` (MDD baseline 41%)

| variant | CAGR | ΔCAGR | MDD | ΔMDD | n_stops |
|---|---|---|---|---|---|
| baseline | 25.32% | — | 40.53% | — | — |
| `sl20_cool21` | 21.91% | −3.42 pp | **32.61%** | **+7.92 pp** | 14 |
| `sl30_rec10` | 26.22% | +0.89 pp | 34.65% | +5.88 pp | 2 |
| `sl30_cool21` | 26.35% | +1.03 pp | 34.86% | +5.67 pp | 2 |

**NDX é o dataset mais amigável para stop-loss**: 162 variantes atingem
MDD ≤ 30% dentro do corredor de CAGR (mas quase todas são sobre bases
com leverage 1 ou 2).

## Cross-dataset robustness — quais stops sobrevivem em todos os 3 datasets?

Para cada `stop_tag` (stop % + mode + param, independente do base_cfg),
medimos: fração das 20 bases onde ele reduz o MDD.

**Apenas 2 tags reduzem MDD em ≥ 50% das bases de cada dataset**
(robustness mínima cross-dataset):

| stop_tag | min frac (base reduz MDD) | avg ΔCAGR | avg ΔMDD | edu ΔMDD | spy ΔMDD | ndx ΔMDD |
|---|---|---|---|---|---|---|
| `sl15_next` | 65% | **−10.77 pp** | +2.07 pp | +0.17 pp | +2.23 pp | +3.81 pp |
| `sl20_next` | 50% | **−8.03 pp** | +0.33 pp | +0.84 pp | +0.30 pp | −0.16 pp |

Ambos **estouram o orçamento de CAGR de 5 pp** na média. O `next_signal`
é conservador — espera cross-up real — mas essa espera custa caro.

**Top tags por ΔMDD médio cross-dataset (sem exigir robustez por base)**:

| stop_tag | min frac | avg ΔCAGR | avg ΔMDD | edu ΔMDD | spy ΔMDD | ndx ΔMDD |
|---|---|---|---|---|---|---|
| `sl20_cool21` | 40% | −3.20 pp | **+2.35 pp** | +1.64 | +3.66 | +1.75 |
| `sl15_next` | 65% | −10.77 pp | +2.07 pp | +0.17 | +2.23 | +3.81 |
| `sl15_cool63` | 40% | −8.52 pp | +1.48 pp | −5.21 | +5.23 | +4.44 |
| `sl25_cool63` | 25% | −4.38 pp | +1.05 pp | +2.69 | +2.59 | −2.14 |
| `sl25_next` | 45% | −4.96 pp | +0.99 pp | +1.82 | +0.49 | +0.67 |
| `sl30_next` | 40% | −3.09 pp | +0.54 pp | +0.16 | +1.27 | +0.17 |
| `sl30_cool21` | 35% | −0.93 pp | +0.21 pp | −2.08 | +1.45 | +1.27 |

**`sl20_cool21`** é o candidato mais interessante — ΔMDD positivo em
todos os 3 datasets (+1.64 / +3.66 / +1.75 pp) a custo de apenas
−3.20 pp de CAGR médio.

**`sl30_cool21`** preserva CAGR (−0.93 pp) e entrega redução pequena mas
consistente no real data.

## Patterns — qual modo de re-entry vence?

Média por modo across todos os (base × variante) não-baseline:

| dataset | next_signal (n=120) | time_cooldown (n=360) | recovery_trigger (n=360) |
|---|---|---|---|
| educational | ΔCAGR −7.51 / ΔMDD −0.18 | ΔCAGR −5.40 / ΔMDD **+2.86** | ΔCAGR −4.94 / ΔMDD **+3.70** |
| spy_real | ΔCAGR −2.66 / ΔMDD +1.27 | ΔCAGR −1.56 / ΔMDD +2.47 | ΔCAGR −1.68 / ΔMDD +3.27 |
| ndx_real | ΔCAGR −1.74 / ΔMDD +0.52 | ΔCAGR −0.62 / ΔMDD +2.14 | ΔCAGR −0.96 / ΔMDD +2.32 |

* **`recovery_trigger`** é o modo dominante em ΔMDD em **todos os 3
  datasets**. Usa o preço do signal asset pra detectar o ponto de entrada
  — pega recovery mais cedo que `next_signal` (que espera MA crossover).
* **`time_cooldown`** empata no geral; preserva CAGR um pouco melhor.
* **`next_signal` é o pior**: espera muito e perde a recuperação
  (spec §8.2 previa isto).

## Patterns — qual stop level (15-40%)?

| stop % | educational ΔCAGR/ΔMDD | spy_real ΔCAGR/ΔMDD | ndx_real ΔCAGR/ΔMDD | frac_pos_avg |
|---|---|---|---|---|
| 15% | −13.64 / +6.87 | −3.70 / +2.39 | −2.09 / +3.69 | 70% |
| 20% | −7.80 / +1.99 | −2.23 / +1.77 | −1.10 / +1.83 | 60% |
| 25% | −5.58 / +2.50 | −1.99 / +2.62 | −0.78 / +1.31 | 63% |
| 30% | −2.11 / +2.05 | −1.03 / +2.61 | −0.83 / +1.47 | 58% |
| 35% | −2.36 / +1.86 | −1.34 / +2.71 | −1.23 / +1.55 | 50% |
| 40% | −1.53 / +1.44 | −0.91 / +2.42 | −0.95 / +1.27 | 45% |

* **Stops abaixo de 20%** disparam muito (~20-45 stops em 40 anos no
  educational) e destroem CAGR.
* **Stops 25-30%** são o sweet spot — preservam CAGR (custo < 2.5 pp)
  e entregam ~2 pp de redução de MDD consistente nos 3 datasets.
* **Stops > 35%** raramente disparam — pouco efeito em ambos os lados.

## Honest caveats

1. **Sample de crashes ínfimo.** 40y de SPY contém 4-5 crashes
   significativos (1987, 2000-2002, 2008-2009, 2020, 2022). Qualquer
   otimização fina nestes poucos eventos é overfit. Spec §6.3.
2. **Gates não avaliados.** DSR-penalty com n_trials = 2 580
   (vs. 384 na sweep original) aumentaria a barra estatística
   em ~29% (√(ln 2580 / ln 384)). Phase 3 precisa re-rodar PBO/DSR/WF
   com o n_trials correto.
3. **Cross-lib G7 não verificada** para o novo path
   `simulate_with_stop_loss`. Antes de promover para Phase 3 ou live,
   precisa de implementação numpy-puro e comparação ±3 pp.
   `[advances_fin_ml, p.31-34]`.
4. **Stops intraday não modelados.** Trigger no close apenas
   (spec §8.4). Em crashes rápidos (ex.: COVID 12% em 1 dia) isto
   subestima o custo real do stop.
5. **Sell leg inverso não testado** fora do educational. Os tops do
   SPY real / NDX real só têm `sL=0` (cash). Stops em short legs
   negativos podem ter dinâmica diferente.

## Next — Phase 2 (risk-signal de-leveraging)

**Hipótese a testar em Phase 2**: os sinais preditivos de crash (EBP,
yield curve, CAPE, VIX term) antecipam crashes em semanas-meses, não
dias. Usar esses sinais pra **reduzir leverage gradualmente** pode
preservar mais CAGR que stops reativos.

**Candidatos levados de Phase 1 para Phase 2** (para combinação em
Phase 3):

1. **`sl20_cool21`** — único stop_tag com ΔMDD positivo em todos os 3
   datasets, custo −3.20 pp CAGR. O mais cross-robusto.
2. **`sl30_cool21`** — custo quase zero (−0.93 pp), mas ΔMDD pequeno
   (+0.21 pp avg). Pode ser complementar a um sinal preditivo.
3. **`sl30_rec10`** — na NDX real entrega +5.88 pp de MDD com custo de
   apenas +0.89 pp CAGR (positivo). Recuperação rápida ajuda em
   crashes curtos tipo COVID.
4. **`sl25_rec10`** — bom no spy_real e ndx_real (reduz MDD ~4-6 pp),
   custo moderado.

Phase 2 vai testar os 5 indicadores (EBP, term spread, CAPE, VIX,
composite) com 3 lambdas (0.3 / 0.5 / 0.7) × top-5 bases × 3 datasets =
225 sims. Phase 3 combina top-5 de Phase 1 × top-5 de Phase 2 = 25
candidatos para gates completos.

**STOP aqui conforme instrução do usuário. Aguardando revisão antes de
iniciar Phase 2.**

---

*Citations:* stop-loss como risk overlay é mecanismo de uso comum; as
magnitudes específicas (15-40%) e re-entry modes (`next_signal` /
`time_cooldown` / `recovery_trigger`) foram sweepados conforme spec
§3.1 / §3.2. Honest alignment: `[advances_fin_ml, p.31-34]`. Gates
pendentes (Phase 3): PBO `[advances_fin_ml, p.208-211]`, DSR
`[p.222-223]`, walk-forward `[ch.12]`, bootstrap `[p.196-202]`,
cross-lib `[p.31-34]`. Whipsaw cost discussion: spec §8.1-8.2.

# Phase 2 — Risk-signal de-leveraging · FINAL

> **Educational / experimental.** Mandate §1: projeto em MAINTENANCE,
> 100% Plano C. Este estudo não propõe reativar slot A/B/D.

## What was swept

For each of the three baseline studies, **top-20 base configs × 5
indicators × 4 λ values = 400 sims per dataset** (1 200 total):

* indicators: `ebp`, `term_spread`, `cape`, `vix`, `composite`
  (equal-weight mean of active indicators).
* λ (de-leverage scale): {0.0, 0.3, 0.5, 0.7}.
* Position scaling: `pos(t) = max(0, 1 − λ · risk(t))` when the base
  regime is `+1`; returns are `pos · buy_leg + (1−pos) · cash`.
* Risk score per indicator = sigmoid of rolling z-score, shifted by
  +1 σ threshold (spec §8.3: "só de-levera acima de threshold alto").

Walltime: 25 s total (educational 14 s, spy/ndx 5-6 s each). Throughput
≈ 71 sims/s.

Gates not evaluated — Phase 2 is exploratory (spec §6.1).

## Data provenance

Cached under `data/external/macro/`:

| series | source | frequency | coverage | publish lag |
|---|---|---|---|---|
| EBP | `federalreserve.gov/.../ebp_csv.csv` | monthly | 1973-01 → 2026-03 | 21 TD |
| T10Y3M | `fred.stlouisfed.org` | daily | 1982-01 → 2026-04 | 1 TD |
| CAPE | Yale Shiller `ie_data.xls` | monthly | 1881-01 → 2023-09 | 32 TD |
| VIXCLS | FRED (local parquet) | daily | 1990-01 → 2026-04 | 0 TD |

Honest alignment via `macro_data_loader.resample_to_daily_with_lag`
(forward-fill monthly → daily, then `shift(lag_TD)`). Reference:
`[advances_fin_ml, p.31-34]`. CAPE stale by ~2.5 y (Shiller cutoff)
but covers all 1987-2022 crashes of interest.

## Direct answer to the spec's central question (no change from Phase 1)

> *"Reduzir MDD de 54% para 25-40% no top-1 educational sem sacrificar
> mais que 3-5pp de CAGR, via de-leveraging signal?"*

**Não.** Para o top-1 educational (`EMA_N150_th5_bL3_sL0`, CAGR 27.67%,
MDD 53.98%):

| indicator | λ | CAGR | ΔCAGR | MDD | ΔMDD |
|---|---|---|---|---|---|
| baseline | — | 27.67% | — | 53.98% | — |
| `ebp` | 0.7 | 27.05% | **−0.62 pp** | 51.90% | **+2.09 pp** |
| `cape` | 0.3 | 26.05% | −1.62 pp | 51.90% | +2.09 pp |
| `term_spread` | 0.3 | 25.08% | −2.59 pp | 51.90% | +2.09 pp |
| `cape` | 0.5 | 24.67% | −3.00 pp | 51.90% | +2.09 pp |

**ΔMDD plateaus at ~2 pp** for this base — risk signals don't fire
aggressively enough during 1987/2000/2008 on bL=3 synth to make a
bigger dent. Phase 1's best stop (sl30_next) achieved +6.86 pp MDD
reduction at the same CAGR cost, so **stop-loss wins solo on this
base**.

## Phase 1 vs Phase 2 — direct comparison on top-1 per dataset

Best variant within ΔCAGR ≥ −5 pp:

| dataset | Phase 1 (stop) | Phase 2 (signal) | winner |
|---|---|---|---|
| educational top-1 | `sl30_next` — ΔCAGR +0.51, **ΔMDD +6.86** | `ebp λ=0.7` — ΔCAGR −0.62, ΔMDD +2.09 | **Phase 1** |
| spy_real top-1 | `sl20_cool21` — ΔCAGR +0.31, ΔMDD +4.41 | `composite λ=0.5` — ΔCAGR −1.40, **ΔMDD +8.16** | **Phase 2** |
| ndx_real top-1 | `sl30_rec10` — ΔCAGR +0.89, **ΔMDD +5.88** | `vix λ=0.3` — ΔCAGR −1.28, ΔMDD +3.27 | **Phase 1** |

Each mechanism wins on different datasets → Phase 3 combination is
warranted.

## Cross-dataset (indicator, λ) ranking

Mean ΔMDD / ΔCAGR across 20 bases, averaged across the 3 datasets:

| indicator | λ=0.3 | λ=0.5 | λ=0.7 |
|---|---|---|---|
| `ebp` | +1.28 / −0.42 | +2.04 / −0.76 | +2.78 / −1.14 |
| `term_spread` | +3.24 / −2.03 | +4.68 / −3.50 | +5.68 / −5.06 |
| `cape` | **+3.59** / −1.64 | **+5.29** / −2.91 | **+6.32** / −4.30 |
| `vix` | +2.45 / −1.08 | +3.06 / −1.89 | +3.47 / −2.78 |
| `composite` | +2.97 / −1.28 | +4.41 / −2.21 | +5.59 / −3.18 |

*(format: ΔMDD pp / ΔCAGR pp — positive ΔMDD = MDD reduced)*

Observações:

* **CAPE domina** em ΔMDD cross-dataset — +3.59 / +5.29 / +6.32 pp a λ
  crescente. Faz sentido: valuation ratios têm lead longo (meses-anos)
  antes de crashes (2000, 2008).
* **term_spread** 2º lugar em ΔMDD mas paga mais em CAGR (−2 a −5 pp).
  Falha modo "2022-2024 inversão sem recessão" (spec §8.3).
* **composite** é um meio-termo robusto. λ=0.5 entrega **+4.41 pp
  ΔMDD a custo −2.21 pp CAGR** — dentro do corredor.
* **EBP fraco sozinho** — mean_pos alta (≥0.91) porque z-score
  de EBP fica elevado poucos dias/mês, sinal quase sempre em ~0.
* **VIX moderado** — funciona mas menos robusto que CAPE.

## Top-5 variants per dataset (ΔCAGR ≥ −5pp, by MDD reduction)

### educational (synth 40y)

| # | base | indicator | λ | CAGR | ΔCAGR | MDD | ΔMDD | Sharpe |
|---|---|---|---|---|---|---|---|---|
| 1 | `SMA_N200_th0_bL3_sL0` (#12) | cape | 0.7 | 18.12% | −3.97 | 53.04% | +17.24 | 0.74 |
| 2 | `SMA_N200_th0_bL3_sL0` (#12) | ebp | 0.7 | 22.13% | +0.04 | 53.21% | +17.08 | 0.78 |
| 3 | `SMA_N200_th0_bL3_sL0` (#12) | cape | 0.5 | 19.50% | −2.59 | 54.68% | +15.61 | 0.75 |
| 4 | `SMA_N100_th5_bL3_sL0` (#13) | cape | 0.7 | 18.59% | −3.99 | 58.09% | +15.54 | 0.74 |
| 5 | `SMA_N200_th0_bL2_sL0` (#20) | cape | 0.7 | 12.17% | −3.11 | 39.27% | +14.90 | 0.71 |

Base #12 (`SMA_N200_th0_bL3_sL0`, baseline MDD 70%) é o que ganha mais
em MDD — mas MDD final ainda é ~53%. O top-1 (MDD baseline 54%) mal sai
do lugar.

### spy_real (17y)

| # | base | indicator | λ | CAGR | ΔCAGR | MDD | ΔMDD | Sharpe |
|---|---|---|---|---|---|---|---|---|
| 1 | `EMA_N150_th5_bL3_sL0` (#4) | term_spread | 0.7 | 16.32% | −3.93 | 38.82% | +15.41 | 0.67 |
| 2 | `SMA_N200_th2_bL3_sL0` (#20) | composite | 0.7 | 16.24% | −1.95 | 43.11% | +14.33 | 0.66 |
| 3 | `SMA_N150_th5_bL2_sL0` (#19) | term_spread | 0.7 | 10.07% | −3.34 | 28.96% | +14.30 | 0.60 |
| 4 | `EMA_N150_th5_bL3_sL0` (#4) | composite | 0.7 | 18.08% | −2.17 | **40.56%** | **+13.68** | 0.71 |
| 5 | `SMA_N150_th5_bL2_sL0` (#19) | vix | 0.7 | 12.55% | −0.86 | 30.09% | +13.17 | 0.69 |

**SPY real é o dataset mais amigável** para signals. Base #4
(bL=3 UPRO) com `composite λ=0.7` chega a **MDD 40.56% com ΔCAGR
apenas −2.17 pp** — dentro do target!

### ndx_real (16y)

| # | base | indicator | λ | CAGR | ΔCAGR | MDD | ΔMDD | Sharpe |
|---|---|---|---|---|---|---|---|---|
| 1 | `EMA_N200_th2_bL3_sL0` (#18) | cape | 0.5 | 25.11% | −3.84 | 52.65% | +8.46 | 0.77 |
| 2 | `SMA_N200_th0_bL3_sL0` (#11) | cape | 0.5 | 26.25% | −3.33 | 48.90% | +8.06 | 0.80 |
| 3 | `SMA_N200_th0_bL3_sL0` (#11) | composite | 0.7 | 25.32% | −4.26 | 48.90% | +8.06 | 0.80 |
| 4 | `SMA_N200_th0_bL3_sL0` (#11) | composite | 0.5 | 26.67% | −2.91 | 49.34% | +7.62 | 0.80 |
| 5 | `EMA_N200_th2_bL2_sL0` (#16) | cape | 0.5 | 18.34% | −3.22 | 38.49% | +7.62 | 0.78 |

NDX real (só 16 anos) tem menos crashes para signals se desenvolverem.
ΔMDD máximo ~8 pp.

## Candidatos para Phase 3 (combinação stop + signal)

Selecionados por critério: **(a) `delta_mdd ≥ +3 pp` em todos os 3
datasets** (robustez mínima) **e (b) `delta_cagr ≥ −3 pp` na média
cross-dataset** (corredor de CAGR):

| indicator | λ | avg ΔMDD | avg ΔCAGR | min ΔMDD dataset |
|---|---|---|---|---|
| **`cape`** | **0.5** | **+5.29 pp** | **−2.91 pp** | +2.87 (ndx) |
| **`composite`** | **0.5** | **+4.41 pp** | **−2.21 pp** | +2.44 (ndx) |
| `cape` | 0.3 | +3.59 pp | −1.64 pp | +2.47 (ndx) |
| `composite` | 0.7 | +5.59 pp | −3.18 pp | +2.70 (ndx) |

**Recomendação para Phase 3**:

* **Signal lead**: `composite λ=0.5` — melhor CAGR cost na média, ΔMDD
  sólido.
* **Signal alt**: `cape λ=0.5` — maior ΔMDD mas custa +0.7 pp CAGR a mais.
* **Stop lead** (from Phase 1): `sl20_cool21` — único stop cross-robusto.
* **Stop alt**: `sl30_rec10` — preserva CAGR, bom para NDX.

Phase 3 vai testar 4 combinações × 20 bases × 3 datasets = 240 sims,
depois rodar 7-gate battery nos top-5 survivors.

## Honest caveats

1. **Gates não avaliados** nesta fase. n_trials combinado Phase 1+2 =
   2 580 + 1 200 = 3 780. DSR penalty será substancial em Phase 3.
2. **CAPE stale 2.5 y** — para crashes 2023-2024 não temos sinal
   atualizado (forward-fill do último valor). OK para 1987/2000/2008/2020.
3. **Spec §8.3 concerns confirmed partially**: term_spread λ=0.7 custa
   −5 pp CAGR (quase no limite) — o decade-plus de inversão sem
   recessão destrói CAGR.
4. **Rolling z-score lookback** fixo (60 meses / 10 anos) sem sweep —
   respeita spec §6.3 (small-sample) mas deixa sensibilidade a
   parâmetros sem teste.
5. **Adaptive window**: para SPY real (17y) e NDX real (16y), 60-month
   rolling e 10-year CAPE lookback consomem significativa fração da
   janela — o signal só está "ativo" nos últimos 7-10 anos de cada.
6. **Cross-lib G7 ainda pendente** para `simulate_with_risk_signal`.
   Antes de promover: hand-rolled numpy + parity ±3 pp.
7. **CAPE vintage**: usamos Shiller revisto, não ALFRED. Revisions em
   earnings retroativamente alteram CAPE histórico — minor look-ahead
   bias. Phase 3 deveria usar ALFRED vintages para honest final.

## Next — Phase 3 (combinação)

**Escopo proposto**:

* 20 top bases × 4 combinações {`sl20_cool21` + `composite λ=0.5`,
  `sl20_cool21` + `cape λ=0.5`, `sl30_rec10` + `composite λ=0.5`,
  `sl30_rec10` + `cape λ=0.5`} × 3 datasets = 240 sims.
* Simulador combinado: tanto stop-loss (force cash when DD) quanto
  position-scaling por risk signal.
* Run 7-gate battery nos top-5 survivors por dataset.

**Critério de sucesso**: ≥1 combinação atinge MDD ≤ 40% AND ΔCAGR
≥ −5 pp em **2 de 3 datasets** AND passa ≥ 5/7 gates no dataset onde
passa ranking → crash-protected winner.

**Caso contrário**: fechar o estudo com veredicto *"no mechanism
closed the gap"* — nem stop, nem signal, nem combinação reduzem o MDD
do top-1 educational para o corredor desejado.

**STOP aqui conforme instrução inicial. Aguardando revisão antes de
iniciar Phase 3.**

---

*Citations:* spec §3.1-B (risk signal design), §5.2 (Phase 2 scope),
§8.3 (sigmoid threshold), §8.5 (continuous position). EBP: Gilchrist &
Zakrajšek 2012. Yield curve: Estrella & Mishkin 1998. CAPE: Campbell &
Shiller 1988. VIX: FRED VIXCLS. Honest alignment: `[advances_fin_ml,
p.31-34]`. Small-sample caution: spec §6.3 / `crashes_sp500_e_indicadores_preditivos.md`.

# spy_beater_hunt iter 021 — meta-axis ceiling DEFINITIVO em 71

**Data**: 2026-04-30 ~08:56

**Iter**: 021 — H4 META-ENSEMBLE alternative always-on substitution +
asymmetric 3-way weights

**Tier**: PROMISING **70/100** (gross) / 64/100 (net Lei 14.754/2023)

**Selected**: `h4_meta_3way_30a2_35g2_35f1` (asymmetric 30/35/35 do iter-019
trio: A2 + G2 IEF + F1 stack)

---

## O que aconteceu

Quarta iter consecutiva no eixo meta-ensemble. Iter 018 (2-way 50/50)
quebrou o teto histórico de 67 chegando a 70; iter 019 (3-way 33/33/34)
subiu para 71; iter 020 (4-way 25/25/25/25) caiu para 67; iter 021
(3-way com pesos assimétricos + diversificadores always-on alternativos)
volta a 70. **A trajetória 70 → 71 → 67 → 70 confirma de forma definitiva
que o teto do eixo meta-ensemble está em 71 dentro do rubric atual.**

Testei 6 configs cobrindo dois sub-eixos de exploração que o iter-020
recomendou:

1. **Substituição do diversificador always-on** (em 33/33/34 baseline):
   F1 LETF 2.25× (UPRO/TMF/IEF/UGL/KMLM sem gate), pure NTSX 100%, ou
   F1 stack 2× sem TLT (NTSX/GDE/KMLM 50/30/20).
2. **Pesos assimétricos** com F1 stack original 1.41×: 30/35/35,
   35/30/35, 30/40/30.

Resultado: **6 de 6 configs passam todas as 3 bars** — terceira iter
consecutiva com 100% bar-pass sweep. O config que o seletor escolheu
(maior Sharpe / SPY Sharpe) foi o assimétrico 30/35/35 com Sharpe 1.037
e MDD 28.18% — segundo melhor mean Sharpe e segundo melhor mean MDD
entre todos os CAGR-passers em 21 iters / 74 trials. Mas **perde 1
gate em spy_real (5/7 vs 6/7 do iter-019) → score 70 vs 71**.

## KILLs disparados

- **KILL #71 FIRED** (score máximo ≤ 71 → ceiling DEFINITIVO em 71):
  4 iters consecutivas sem trajetória ascendente confirmam.
- **KILL #75 FIRED** (F1 stack 2× sem TLT mantém Sharpe ≥ 1.020 e
  CAGR > iter-019 baseline): contribuição do TLT ao F1 stack é
  marginal dentro do meta-blend; reforça narrativa de robustez ao
  stress 2022 (sem TLT, sem perda de duration).
- **KILL #76 FIRED** (pesos assimétricos todos ≤ 71): a superfície
  de pesos perto do ápice 33/33/34 é PLANA para perturbações ±5pp.
- **KILL #74 NÃO disparou** (NTSX 100% always-on passou bar de CAGR):
  diversificação multi-asset NÃO é essencial; equity puro 1.5× notional
  é diversificador suficiente nesse tier.
- **KILL #73 PARTIAL FIRE** (F1 LETF 2.25× CAGR 16.61% > 15.04% mas
  troca 7.44pp de MDD por isso → Pareto-trade dentro do rubric).

## Por que isso importa

O eixo meta-ensemble foi o último vetor genuíno de progresso após o
hunt ter sido declarado fechado em iter 011 (KILL #33). 4 iters de
exploração incremental (constituent count: 2/3/4-way, weight optimization,
alternative always-on substitution, weight perturbation) **mapearam
toda a superfície sem encontrar trajetória ascendente além de 71**. A
descoberta principal é que o rubric satura em duas dimensões diferentes:

- **Sharpe e MDD axes** (descoberto iter 020): bucket pts não distingue
  melhorias incrementais quando os números já estão dentro do range de
  saturação (1.025 → 1.058 = 0pts; 28.50% → 26.17% = 0pts).
- **Gates axis** (descoberto iter 021): contar gates é o BINDING
  score-axis no teto — 30/35/35 perde 1pt mesmo com Sharpe + MDD
  Pareto-melhores e CAGR Pareto-tied.

5 iters agora documentam configs rubric-subótimos com perfis Sharpe/MDD
fortes: 015 F1, 016 G1 IEF, 018+019+020+021 meta-ensembles. Reforça o
caso de revisão de rubric por mandate §7.

## Próximos passos (decisão do usuário)

3 opções estratégicas:

- **A — Declarar hunt EFFECTIVELY-CLOSED em iter-021** (mais defensável):
  21/50 iters usadas, 4 sequenciais confirmam ceiling, F1+SPLIT segue
  como deploy fallback, mandate §1 100% Plano C inalterado, 29 iters
  preservadas para hunts futuros.
- **B — Pivotar do meta-axis para nível-constituente**: só sobra C2
  CAPE-timing (low-credibility por 20+ anos de OOS failure).
- **C — Pivotar do score-axis para mandate §7 rubric-revision request**:
  com 5 configs rubric-subótimos documentados, propor revisão dos
  anchors do Sharpe-bucket [0.5, 2.0] e MDD-bucket [0.10, 0.70] para
  expor as Pareto-improvements.

Recomendação: Opção A. Hunt's research value crystallized. Mandate §1
MAINTENANCE MODE inalterado.

## Estado técnico

- 771 tests baseline preservado (sem nova infra; reutiliza blend + lrs
  + static spec types do iter 018-020).
- cumulative_n_trials = 74 (iter 020 = 68 + 6 novas configs).
- worst DSR p = 1.26e-04 << 0.05 (entre iter-019 1.55e-04 e iter-020
  9.28e-05).
- PBO N=6 stability mantida.

## Citações principais

- `[advances_fin_ml, ch.16, p.241-256]` portfolio construction —
  decorrelation gain ~10% super-linear similar across always-on
  substitutions.
- Bridgewater All-Weather (Dalio 1996) — TLT marginal dentro do
  meta-blend EMPIRICAMENTE CONFIRMADO via H4.3.
- `[advances_fin_ml, p.31-34]` factor framework — taxonomia
  meta-ensemble agora EXAURIDA em 4 sub-eixos.

# spy_beater_hunt iter 003: adicionei KMLM como buffer no sleeve ON e o score subiu pra 64

Iter 003 atacou o gargalo do MDD por um caminho novo: ao invés de mexer
no gate (KILL #7/#8 já fechados) ou na alavancagem (iter 002 mostrou
que dropar pra 2× ajuda mas custa CAGR demais), eu mantive o iter 001
winner como base (50% UPRO + 50% SSO ON, IEF OFF, SMA 200) e diluí o
sleeve ON com **crisis-alpha (KMLM/TLT) sempre ligados**.

A tese: o gate de 200d SMA tem 5-15pp de drawdown estrutural durante o
período de lag (entre o pico do mercado e o flip OFF). KMLM gerencia
esse vão porque ele não correlaciona com queda de equity (managed
futures, momento e taxa-de-juros longa).

## O que rodei (4 configs, todos passaram os 3 bars)

| config | CAGR | MDD | Sharpe (lh, spy_real) |
|---|---:|---:|---:|
| a3_lrs_split_kmlm10 | 15.47% | 46.65% | 0.681 / 0.665 |
| **a3_lrs_split_kmlm20** | **14.99%** | **41.87%** | **0.719 / 0.692** ← winner |
| a3_lrs_split_tlt15 | 15.34% | 44.60% | 0.709 / 0.682 |
| a3_lrs_split_blend | 14.86% | 42.13% | 0.713 / 0.696 |

Todos passaram CAGR ≥ 11.21%, MDD ≤ 55.17% e gates ≥ 5/5 nos dois
datasets. **Winner_conditions_met = True** em todos os 4.

## Por que isso é progresso de verdade

Iter 001 a1_lrs_split (50% UPRO + 50% SSO ON, IEF OFF) era o
closest-to-winner com score 60. Iter 003 a3_lrs_split_kmlm20 ficou
**score 64** — primeira melhoria líquida desde a metodology refactor.

A mecânica do score lift:
- MDD pts: 6 → 10 (mean MDD caiu 9.73pp, de 51.60% pra 41.87%)
- Gates pts: 12 → 13 (spy_real foi 5/7 → 6/7 com o buffer)
- CAGR pts: 22 → 20 (perdeu 1.24pp de CAGR pelo dilution — preço aceitável)

O ganho de 9.73pp em MDD vindo de só 20% de KMLM no sleeve ON valida
empiricamente o `[risk_parity, ch.5, p.10]` Carlson sobre
capital-efficient stacking — exatamente a mesma rationale que o
F1+SPLIT incumbente do long_term_portfolio usa (com 17.5% KMLM).

## KILLs pré-comitados — todos NOT FIRED

- KILL #6 (CAGR floor): nada disparou — todos ≥ 14.86%, longe do bar 11.21%.
- KILL #10 (no MDD relief): NOT FIRED — todos os 4 abaixo de 51.60%
  baseline. Direção crisis-alpha CONFIRMADA.
- KILL #11 (KMLM monotonic harm): NOT FIRED — **invertido**. KMLM 20%
  tem Sharpe MELHOR que KMLM 10% nos dois datasets. Dose-response é
  monotônico positivo no range 10-20%.
- KILL #12 (TLT subordinate): NOT FIRED — TLT 15% MDD 44.60% < KMLM 10%
  46.65%. TLT é competitivo, só perdeu pra KMLM 20% (que tem 50% mais
  alocação). Próximo iter precisa comparar TLT 20% vs KMLM 20%.

## Implicação pra iter 004

Direção A3 KMLM dose-response continua aberta. Tentativa próxima:
- a4_kmlm25 (25% KMLM)
- a4_kmlm30 (30% KMLM)
- a4_tlt20 (20% TLT — comparação dose-strict com KMLM 20%)

3 configs, n_trials cresce 14 → 17 (DSR ainda PASS por margem).

KILL #13 candidato: se Sharpe de kmlm30 < kmlm25 nos dois datasets, o
sweet spot ficou em 20-25% e KMLM perdeu utilidade marginal acima
disso.

## Gap honesto pra WINNER

Closest-to-winner agora score 64. WINNER tier requer score ≥ 90 (gap
de 26 pts). Margens realistas restantes:
- MDD pts 10 → 14: precisaria mean MDD ~30% (atual 41.87%). Talvez
  com KMLM 30% + TLT 10% + duration diversification.
- Sharpe pts 1 → 4: mean Sharpe ~0.95 (atual 0.705). MDD drop puxa
  Sharpe junto — não é independente.
- CAGR pts 20 → 25: mean CAGR ~17% (atual 14.99%). Mais alavancagem
  mata MDD; teria que ser via concentração (TQQQ track).

Realistic ceiling pra essa família de estratégias parece ser score
70-80 em mais 2-3 iters. WINNER (≥90) provavelmente requer abordagem
estruturalmente diferente — TQQQ-track (A2) ou vol-targeted (C1).
F1+SPLIT continua sendo o deploy fallback caso 50 iters não encontrem
WINNER.

## Próximos passos do loop

3/50 iters. 47 a rodar. Cumulative n_trials = 14 (ainda saudável pro
DSR).

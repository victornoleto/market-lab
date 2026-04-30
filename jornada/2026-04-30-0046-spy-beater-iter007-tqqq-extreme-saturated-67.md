# spy_beater_hunt iter 007 — extender KMLM/TLT funcionou direcionalmente, mas score saturou em 67/100

**Data**: 2026-04-30 00h46
**Iter slug**: `007-2026-04-30-A2-tqqq-track-extreme`
**Tier**: PROMISING **67/100** (winner_conditions_met = TRUE, all 3 bars)
**Selected**: `a7_tqqq_split_kmlm40_tlt10` (25% TQQQ + 25% QLD + 40% KMLM + 10% TLT ON / 100% IEF OFF, gate 200d SMA em QQQ, T+1)

## O que mudou

Iter 006 fechou com `a6_tqqq_split_kmlm30_tlt10` em score 67 — novo
closest-to-winner via pivô NDX. Recomendação foi **estender o sweep
KMLM/TLT** que tinha funcionado no SPY-track (iter 005 monotonic
positivo até 40%). Iter 007 testou exatamente isso: 3 configs
levantando KMLM 30→35→40% e adicionalmente TLT 10→15%.

## O que aconteceu

Os 3 configs passaram **todos os 3 bars**. Direcionalmente o experimento
funcionou: a alavanca KMLM no TQQQ-track tem o **mesmo formato**
monotônico que no SPY-track. Quanto mais KMLM, mais Sharpe, menos MDD,
menos CAGR. Sem inflexão até 40%.

| config                          | mean CAGR | mean MDD | Sharpe (lh, spy_real) | lh_56y MDD |
|---------------------------------|----------:|---------:|----------------------:|-----------:|
| a7_tqqq_split_kmlm35_tlt10      | 16,73%    | 46,18%   | 0,779 / 0,782         | 57,03%     |
| **a7_tqqq_split_kmlm40_tlt10**  | **16,08%** | **42,33%** | **0,807 / 0,802**   | **51,12%** |
| a7_tqqq_split_kmlm30_tlt15      | 16,67%    | 46,49%   | 0,777 / 0,784         | 57,36%     |

**Mas o score parou em 67 — empate com iter 006**. O motivo é estrutural:
a rubrica do spy_beater_hunt pondera CAGR (30 pts) sobre Sharpe (10 pts)
sobre MDD (20 pts), com âncoras largas (Sharpe 0,5-2,0 — uma melhora de
+0,045 mal cruza a fronteira de 1 pt inteiro). Então a troca KMLM30 →
KMLM40 ganhou 3 pts em MDD (mean 49,73 → 42,33%) mas perdeu 3 pts em
CAGR (mean 17,33 → 16,08%). Net 0.

## KILLs disparados

- **KILL #22 (KMLM dose inflection 35→40 no TQQQ-track) NOT FIRED** —
  KMLM40 Sharpe (0,807, 0,802) > KMLM35 Sharpe (0,779, 0,782) **nos
  DOIS datasets**. Sharpe monotonic positivo confirmado também no
  TQQQ-track, espelhando o achado SPY-track da iter 005.
- **KILL #23 (TLT subordinado a KMLM no TQQQ-track) MARGINALMENTE
  FIRED** — TLT 15% lh_56y MDD 57,36% > KMLM 35% lh_56y MDD 57,03% por
  apenas 0,33pp. Sinal fraquinho mas direcionalmente consistente: KMLM
  é a alavanca marginalmente mais íngreme. Iters futuros priorizam
  estender KMLM em vez de TLT.

## A leitura honesta

O TQQQ-track **saturou em 67 dentro da rubrica atual**. Iter 006 e
iter 007 produzem configs estruturalmente diferentes (CAGR/MDD perfis
opostos) mas o mesmo total. Cada +5pp KMLM custa ~0,6pp CAGR e poupa
~3,5pp MDD — dentro do scoring isso é trade 1:1 em pontos inteiros.
Continuar com KMLM 45-50% provavelmente cai pro outro lado (mais MDD
pts, menos CAGR pts; net ~0 ou negativo).

O Sharpe de fato melhorou (0,759 → 0,804 na média), o DSR worst-p
melhorou (3,05e-03 → 1,72e-03), mas o rubric CAGR-anchored não
recompensa Sharpe direto. **Rubrica Sharpe-anchored preferiria
estritamente iter 007**; rubrica CAGR-anchored é indiferente por
desenho.

## Caminho pro 90 (gap −23 pts) — agora estruturalmente requer mudança de classe

Não tem mais como espremer pontos com KMLM/TLT no TQQQ-track. O caminho
realista pro 75+ exige geometria nova:

1. **B1 HFEA classical** (UPRO 55 + TMF 45) — outra família. Backtests
   pré-2022 mostram CAGR ~22% + MDD ~30%. Falsifiability test: regime
   2022 inflação (TMF -70%, UPRO -50%). **Highest priority** pra
   iter 008. Precisa do TMFSIM synth (TLTSIM × 3 - 1,5%/y decay) — TDD
   pendente per INFRASTRUCTURE.md spec.
2. **C1 vol-targeted** (alavanca dinâmica via vol realizada 60d) —
   pode levantar Sharpe materialmente sem custar CAGR. Iter 009 backup.
3. **Off-regime upgrade** (KMLM-heavy no OFF leg em vez de 100% IEF) —
   ainda dentro do A2 mas geometria diferente.

F1+SPLIT segue como deploy fallback (mandate §1 maintenance mode).
Hunt continua até iter 50 ou WINNER (score ≥ 90 + 3 bars).

## Citations

- `[leverage_for_the_long_run, ch.3-4, p.40-60]` Gayed regime gate
  validado em ambos SPY-track e TQQQ-track; KMLM dose monotônica
  positiva 0-40% em ambos.
- `[risk_parity, ch.5, p.10]` Carlson capital-efficient stacking —
  KMLM dose-response concava com mesma forma SPY/NDX; ganho marginal
  Sharpe 35→40% (+0,024) comparable ao 30→35% (+0,022); inflexão
  provavelmente acima de 40%.
- `[advances_fin_ml, p.31-34]` factor framework — comportamento
  simétrico do crisis-alpha em SPX/NDX.
- `[advances_fin_ml, p.222-223]` DSR cumulative n_trials=26, worst p
  1,72e-03 << 0,05. Folga pra ~3 iters a 3 configs antes da zona n=35.

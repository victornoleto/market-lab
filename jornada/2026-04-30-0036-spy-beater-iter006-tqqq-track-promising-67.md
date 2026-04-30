# spy_beater_hunt iter 006 — pivot pra TQQQ-track funcionou: novo closest-to-winner 67/100

**Data**: 2026-04-30 00h36
**Iter slug**: `006-2026-04-30-A2-tqqq-track-split`
**Tier**: PROMISING **67/100** (winner_conditions_met = TRUE)
**Selected**: `a6_tqqq_split_kmlm30_tlt10` (30% TQQQ + 30% QLD + 30% KMLM + 10% TLT ON / 100% IEF OFF, gate 200d SMA em QQQ, T+1)

## O que mudou

Iter 005 fechou dizendo: a alavanca KMLM no SPY-track tá esgotada
dentro do rubric (CAGR-axis dominant, KMLM 35-40% sobe Sharpe mas
custa CAGR > pts ganhos em MDD). Recomendação: pivotar pra **A2
TQQQ-track** (regime-gated NDX em vez de SPY), que o BASE_MEMORY
listava como "NOT YET RUN" e tem teto de CAGR estruturalmente mais
alto. Foi o que a iter 006 fez.

Os 3 configs portam direto a arquitetura SPY-track pra NDX:
- `a6_tqqq_split_lrs` = analog de iter 001 (50% TQQQ + 50% QLD)
- `a6_tqqq_split_kmlm30` = analog de iter 004 closest-to-winner
- `a6_tqqq_split_kmlm30_tlt10` = analog de iter 005 best-Sharpe blend

## O que aconteceu

3 hipóteses confirmadas, 1 KILL fired:

| config                          | mean CAGR | mean MDD | bar test | Sharpe (lh, spy_real) |
|---------------------------------|----------:|---------:|:--------:|----------------------:|
| a6_tqqq_split_lrs               | 20.49%    | 70.31%   | FAIL     | 0.652 / 0.665         |
| a6_tqqq_split_kmlm30            | 18.46%    | 55.52%   | FAIL     | 0.717 / 0.729         |
| **a6_tqqq_split_kmlm30_tlt10**  | **17.33%** | **49.73%** | **PASS** | **0.754 / 0.763** |

- **H₁ (NDX-track adiciona CAGR)** CONFIRMADA: todos os 3 configs ≥
  17.33% > 16.23% baseline SPY-track. Lift de ~3pp CAGR.
- **H₂ (KMLM transfere SPY→NDX)** CONFIRMADA: kmlm30 Sharpe > baseline
  Sharpe nos DOIS datasets (KILL #21 não fired).
- **H₃ (TLT-on-top transfere)** CONFIRMADA: kmlm30_tlt10 Sharpe >
  kmlm30 Sharpe nos DOIS datasets.
- **KILL #19 (wipeout MDD>70%) FIRED** em `a6_tqqq_split_lrs` (lh_56y
  MDD 87,86%) e borderline em `a6_tqqq_split_kmlm30` (lh_56y 70,94% ≈
  bar). O 200d SMA gate **não consegue resgatar** TQQQ totalmente
  alavancado durante o regime dot-com -78% NDX 2000-02. Só o blend com
  KMLM 30% + TLT 10% conseguiu apertar lh_56y MDD pra 62,39% (ainda
  larga, mas dentro do bar).

Score 67/100 = **NOVO closest-to-winner** (era iter 004 = 66). Lift de
+6 pts em criterion 1 (CAGR mean 14,39 → 17,33%, score 19 → 25) com
custo de −5 pts em criterion 2 (MDD mean 36,79 → 49,73%, score 12 →
7). Net +1.

A divergência por dataset é estrutural: lh_56y MDD 62,39% tá inflada
por todo o regime dot-com (2000-02 NDX -78% via TQQQSIM synth) que o
spy_real (2003+) não captura — daí spy_real MDD 37,07% bate praticamente
com iter 004 SPY-track. O custo do tilt de growth (NDX vs SPY) é
~13-19pp MDD em janela de stress.

Multi-horizon robustness: TQQQ-track bate SPY em **TODA** janela
rolling (5y/10y/15y/20y = 100% pass-rate em ambos datasets). Worst MDD
roll = 62,39%. DSR worst p 3,05e-03 com cumulative n_trials=23 (folga
ainda boa pra 2-3 iters a 3 configs cada antes da zona n=30+).

## Caminho pro 90 (gap −23 pts)

Alavanca mais escalável agora é **criterion 2 MDD** (atual 7/20). Pra
chegar em 35% mean MDD precisa derrubar lh_56y de 62% pra ~30%. Caminhos:
1. **KMLM dose extreme no TQQQ-track** (40-50%, mirror iter 005 SPY
   sweep) — provavelmente derruba lh_56y MDD substancialmente
2. **TQQQ leverage menor** (QLD-only 2× NDX) — derruba CAGR mas cuta MDD
3. **Off-regime upgrade** (KMLM 50% no OFF leg em vez de 100% IEF)

## Próximo passo

**Iter 007**: A2 TQQQ-track extremo — 3 configs portando o sweep da iter 005
SPY-track:
- `a7_tqqq_split_kmlm35_tlt10`
- `a7_tqqq_split_kmlm40_tlt10`
- `a7_tqqq_split_kmlm30_tlt15`

Se score subir pra 75+, continuar. Se travar em ~70-72, pivotar pra
**B1 HFEA classical** na iter 008 (precisa do TMFSIM synth — TDD
pendente per INFRASTRUCTURE.md).

F1+SPLIT segue como deploy fallback (mandate §1 maintenance mode).

Citations: `[leverage_for_the_long_run, ch.3-4, p.40-60]` Gayed gate é
asset-agnostic (transfere SPY→QQQ) mas não resgata 3× LETF de drawdown
underlying -78%; `[risk_parity, ch.5, p.10]` Carlson capital-efficient
stacking — KMLM transfere SPY→NDX com Sharpe monotonic positivo;
`[advances_fin_ml, p.31-34]` factor framework — NDX como tilt de growth
de US-Large validado empiricamente; `[advances_fin_ml, p.222-223]` DSR
n=23 worst p 3,05e-03 << 0,05.

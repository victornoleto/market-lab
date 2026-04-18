# [SHORT-HOLD CFD] V2-L2 `gayed_sma200_L2_off_cash` — baseline forte (6/7 gates, falha só em Sharpe ≥ 2)

**Fase:** 3.5a-V2 Lead V2-L2 (Gayed LETF rotation transportada para CFD)
**Iter:** 16 (fan-out sweep — 1/27 configs)
**Status:** ❌ FAIL na V2 winner criteria (subset 6/7 — falta `oos_sharpe_ge_2`)
**Arquivos:** `reports/phase3_5a_v2/v2_l2_gayed_transported_cfd/gayed_sma200_L2_off_cash.{json,md}`

## O que a config faz

Rotaciona entre {SPY, QQQ} cada um com seu próprio sinal de regime
SMA(200), orçamento equal-weight (0.5 + 0.5). Quando o ativo está ON
(close > SMA200), segura posição levered 2× via CFD. Quando OFF, parks o
orçamento daquele ativo em caixa (0% return). Rebalance diário no close,
cost model Pepperstone Razor (spread 4bps RT + commission 6.6bps RT +
slippage 3bps RT + swap −0.005%/dia sobre a notional levered).

É a transposição CFD da LRS canônica do Gayed (`[leverage_for_the_long_run, p.13]`),
mantendo intactos os 3 achados do paper: (1) SMA200 como sinal primário
(p.13), (2) alavancagem ≥ 2× sobre o ativo em RISK_ON (p.17), (3)
cash como default off-regime (p.21).

## Resultado (25 anos, 2001-05-14 → 2026-04-14)

| Split | Janela | Sharpe | CAGR | MaxDD | Final |
|-------|--------|-------:|-----:|------:|------:|
| IS    | 2001-2017 | 1.348 | 31.10% | -19.00% | 89.8× |
| OOS   | 2018-2023 | 1.545 | 48.13% | -21.88% | 10.5× |
| FWD   | 2024-Q2/26 | 1.368 | 40.64% | -20.70% | 2.17× |

- **Walk-forward 8/8** janelas profitable (100%).
- **Mediana hold = 5 dias**, total 310 switches (SPY=159, QQQ=151).
- Cost drag 63% cumulativo de starting equity em 25 anos;
  swap −46%. Brutalmente caro, mas o alpha overwhelms.

## Por que isso importa

Primeiro candidate da V2-L2 passa 6 das 7 gates V2 (só falha
`oos_sharpe_ge_2`). O gap é pequeno: 1.545 vs 2.0. Considerando:

1. Target CAGR OOS (≥30%) passa com folga (48.1%).
2. MaxDD OOS (≤25%) passa com folga (−21.9%).
3. Mediana hold ≥3d passa com folga (5d).
4. WF 6/8 passa perfeito (8/8).
5. FWD Sharpe >0 passa (1.368).

O único vetor de melhora é **Sharpe**. Candidates naturais do sweep
que podem subir Sharpe mantendo CAGR:

- **off_tlt** ou **off_gld** — em off-regime, TLT/GLD dão alpha não-zero
  (durante bear markets SPY/QQQ, TLT tende a subir). Isso reduz drawdown
  e possivelmente levanta Sharpe.
- **ema100 vs sma200** — EMA mais rápida reduz whipsaw em mercados
  lateralizados e pode cortar switches (cost drag) elevando Sharpe.
- **lrs composite** — vote ≥2/3 sobre {SMA100, SMA200, EMA100} tende
  a dar menos falsos sinais.
- **Leverage 3× ou 5×** — aumenta numerador mas também volatilidade;
  Sharpe pode cair. Vince's PoR cap provavelmente descarta 5×, mas
  3× é plausível.

Esse resultado é **sinal forte** de que V2-L2 pode produzir um winner
na V2 stop rule. Não contei ainda — continuamos o sweep (26 configs
pendentes).

## Citações

- LRS canônica SMA200: `[leverage_for_the_long_run, p.13]`.
- Leverage 2× tested in paper (Table 8): `[leverage_for_the_long_run, p.17]`.
- Cash como off-regime default: `[leverage_for_the_long_run, p.21]`.
- Walk-forward 6/8 gate: `[advances_fin_ml, ch.11]`.
- Pepperstone Razor cost model: Phase 3.5a-V2 spec §3.

## Próximo iter

Continuar sweep — `gayed_sma200_L2_off_tlt` no topo da pending list.
Se TLT off-regime superar cash em Sharpe mantendo CAGR, temos um
candidate winner forte.

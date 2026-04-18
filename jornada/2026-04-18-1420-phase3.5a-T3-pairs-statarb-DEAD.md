# [SHORT-HOLD CFD] Phase 3.5a — Lead T3: Intraday pairs / stat-arb = DEAD END

**Iteração:** 24 do loop Phase 3.5a (aggregator iter após 6 pair sweeps iters 18-23)
**Lead:** T3 (terceiro da lista ativa)
**Veredito:** **DEAD END** — 0/6 pares passam 5-gate
**Próximo:** Lead T4 (Session-based FX — London open breakout, NY close MR)

---

## O que foi testado

Pair-trading 1h, 3 famílias × 6 pares = 18 runs:

- **ols_z2_exit0** — hedge ratio via OLS rolling (lookback=120), z-score
  entry ±2σ, exit z=0 `[algo_trading_chan, p.71-73, ch.3]`.
- **kalman_z2_exit0** — Kalman δ=1e-4 Ve=1e-3, entry ±2σ, exit z=0
  `[algo_trading_chan, p.75-80, ch.3]`.
- **kalman_z2_exit0p5** — mesmo Kalman, exit z=0.5 (tighter, testando
  hold ≤ 5d compliance).

**Universo:** 6 pares canônicos —
1. AUDUSD/NZDUSD (FX commodity-block)
2. EURUSD/EURGBP (FX EUR-crossed)
3. EURUSD/GBPUSD (FX EUR-GBP)
4. SPY/QQQ (equity US large-cap)
5. USDJPY/USDCHF (FX safe-haven)
6. XAUUSD/XAGUSD (metal gold-silver)

**Janela:** 2020-01-06 → 2026-04-14 (6.3y, longest Tiingo 1h cache).
Splits: IS 2020-2023 (4y) / OOS 2024-2025 (2y) / FWD 2026-Q1 stress.

**Custos Pepperstone Razor (ambas pernas):**
- FX: half_spread 2 bps/leg
- Equity CFD: half_spread 10 bps/leg
- Metal: half_spread 5 bps/leg
- Commission $3.50/side ($14/round × 2 legs)
- Swap diário 0.005%/leg ≈ 1.8%/yr cumulativo

**Execução:** 1 bootstrap + 6 iters de sweep (iters 17-23) + este aggregator.

---

## Resultado

**0/6 pares PASS 5-gate.**

| Pair | Best config | OOS Sharpe | OOS CAGR % | OOS MDD % | Hold (d) | PBO | Coint IS |
|---|---|---:|---:|---:|---:|---:|:---:|
| AUDUSD/NZDUSD | ols_z2_exit0 | -1.70 |  -4.01 |  -8.28 | 0.31 | 0.80 ✗ | ✓ p=0.002 |
| EURUSD/EURGBP | ols_z2_exit0 | -1.55 |  -4.44 | -10.40 | 2.42 | 0.69 ✗ | ✗ p=0.125 |
| EURUSD/GBPUSD | ols_z2_exit0 | -1.95 |  -3.76 |  -7.81 | 1.29 | 0.90 ✗ | ✓ p=0.012 |
| SPY/QQQ       | kalman_z2_exit0 | **+0.13** | **+0.65** | -3.93 | **9.04** | 0.36 ✓ | ✗ p=0.071 |
| USDJPY/USDCHF | kalman_z2_exit0 | -1.10 |  -6.20 | -15.56 | 1.13 | 0.53 ✗ | ✗ p=0.439 |
| XAUUSD/XAGUSD | ols_z2_exit0 | -0.88 | -17.24 | -40.26 | 0.08 | 0.99 ✗ | ✗ p=0.127 |

**Única luz**: spy_qqq kalman_z2_exit0 produziu OOS Sharpe +0.13 e FWD
+1.05, e foi **o único a passar PBO** (0.36 < 0.5). Mas: viola gate
inflexível `hold ≤ 5d` (9.04 dias OOS, 12-23 dias em ols FWD) — swap
cumulativo mata edge real; falha DSR (p=0.764) e WF (3/8).

**2/6 pares cointegraram IS** (audusd_nzdusd p=0.002, eurusd_gbpusd
p=0.012) — e **ambos perdem OOS pior que 3 dos não-cointegrados**
(Sharpe -1.70 e -1.95). Cointegração IS não persiste OOS.

---

## Por que falha

1. **Custos dobrados.** Pair = 2 legs. Round-trip em SPY/QQQ = 20 bps
   spread + $14 commission + 0.01%/dia swap. Z-score MR típico em 1h
   captura 10-15 bps por convergência. Negative-sum estrutural.

2. **Cointegração instável.** Pares IS-cointegrados decaem OOS; a
   relação não persiste. Mesmo regime nas janelas adjacentes não
   garante persistência `[machine_trading, p.76-79, ch.3]`.

3. **Kalman degrada mais que OLS rolling.** Média OOS Sharpe:
   ols -1.28 / kalman_z0 -1.66 / kalman_z0p5 -1.84. Confirma SSM
   overfit warning de Chan (EWA-EWC).

4. **Hold-time trade-off.** Exit z=0 gera hold 9d (SPY/QQQ) que viola
   gate; exit z=0.5 reduz hold mas mata captura. Não há janela
   paramétrica em que o edge sobrevive custos E respeita ≤ 5d.

---

## Verdict

**Lead T3 = DEAD END**. 0/6 pares PASS. Somando T1 (0/36) + T2 (0/12) +
T3 (0/6) = **54 runs 1h, 0 winner** em 3 famílias clássicas
(mean-reversion, trend-following, stat-arb). Descoberta estrutural: as
3 famílias canônicas **não sobrevivem** custos 1h retail Pepperstone.

Adicionado a `dead_ends`: pair-trade OLS/Kalman canônico 1h em 6 pares
canônicos (FX/equity/metal) — **NÃO retestar sem mudar custos ou
frequência**.

---

## Próximo

**Lead T4 — Session-based FX strategies.**

Hipótese: estrutura temporal intraday (Asia range / London open breakout
/ NY close mean-reversion) concentra custo em poucos trades bem
localizados por dia — potencialmente evita o problema de "torrent de
trades" que matou T1-T3. Citação obrigatória: consultar
`books/summaries/` por livro de FX sessions antes de prosseguir (candidato:
`[kaufman_trading_systems]` ou `[quant_trading_chan]`).

Se T4 também DEAD → T5 (regime filter hybrid sobre BollingerMR GARCH) →
T6 (rebalance mandate meta, "Plano A não suporta retorno > B") → T7
(summary).

---

## Artefatos produzidos

- 6 per-pair reports: `reports/phase3_5a/t3_intraday_pairs_statarb/{audusd_nzdusd,eurusd_eurgbp,eurusd_gbpusd,spy_qqq,usdjpy_usdchf,xauusd_xagusd}.{json,md}`
- Cross-pair aggregate: `reports/phase3_5a/t3_intraday_pairs_statarb/AGGREGATE.md`
- Registry (state=done): `reports/phase3_5a/t3_intraday_pairs_statarb/registry.json`
- Zero código modificado
- Pytest baseline: 750 passed (não tocado)

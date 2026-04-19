# [SHORT-HOLD CFD] V2-L2 LRS L2× off-GLD — 4º SUBSET PASS 7/7 (2º LRS)

**Data:** 2026-04-18 22:50 UTC
**Iter:** 36 (V2 loop)
**Lead:** V2-L2 Gayed LETF rotation transported to CFD
**Config:** `gayed_lrs_L2_off_gld` (signal=LRS composite ≥2/3 de {SMA100, SMA200, EMA100}, leverage=2×, off-regime=GLD, risk-on=SPY+QQQ)
**Status:** ✅ SUBSET PASS 7/7 (final PASS aguarda aggregator PBO/DSR)

---

## TL;DR

Segunda config LRS entrega **OOS Sharpe 2.178 / CAGR 74.2% / MDD -21.9% /
WF PASS 8/8** — 4º SUBSET PASS V2-L2 e 2º via sinal composite. Predição
de iter 35 ("Sharpe ~2.15-2.20, MDD ~-20-22%, WF=PASS") HIT 3/3 dentro do
range. **GLD como off-regime mantém o mesmo benefício via LRS que via
EMA100 puro**: ambos pulam de ~2.07 (cash) para ~2.18 (gld) e ambos caem
para ~1.9 quando o off é TLT. A ranking off-regime é invariante ao sinal
on-regime.

---

## Metrics (window 2001-05-14 → 2026-04-14, 25y, 6266 bars, 578 switches)

| Split | Range | Sharpe | CAGR | MaxDD |
|-------|-------|-------:|-----:|------:|
| IS    | 2001–2017 | 1.764 | 48.7% | -23.3% |
| OOS   | 2018–2023 | **2.178** | **74.2%** | **-21.9%** |
| FWD   | 2024-01 → 2026-04 | 1.795 | 58.2% | -17.4% |

**Median hold:** 5.5d (target ≥3d ✅). **Switches:** SPY=287, QQQ=291.
**Cumulative costs:** tx 118.0%, swap -44.3%.
**WF:** 8/8 profitable, max-window-DD 23.3% < 25% cap ⇒ **WF=PASS**.

### Subset gates (7/7)

| Gate | Valor | Pass |
|------|------:|:----:|
| oos_sharpe_gt_0 | 2.178 | ✅ |
| fwd_sharpe_gt_0 | 1.795 | ✅ |
| wf_pass | 8/8, max-DD 23.3% | ✅ |
| median_hold_ge_3d | 5.5d | ✅ |
| oos_cagr_ge_30pct | 74.2% | ✅ |
| oos_sharpe_ge_2 | 2.178 | ✅ |
| oos_maxdd_le_25pct | -21.9% | ✅ |

---

## LRS off-regime ranking: gld > cash > tlt (replica EMA100)

Com as 3 configs LRS L2 agora sweepadas:

| off-regime | OOS Sharpe | OOS CAGR | MDD | WF |
|------------|-----------:|---------:|----:|:--:|
| **GLD**    | 2.178 | 74.2% | -21.9% | ✅ PASS |
| **Cash**   | 2.072 | 65.0% | -21.9% | ✅ PASS |
| **TLT**    | 1.911 | 64.1% | -26.2% | ❌ FAIL |

Compare com EMA100 L2 (mesmo padrão):

| off-regime | OOS Sharpe | OOS CAGR | MDD | WF |
|------------|-----------:|---------:|----:|:--:|
| **GLD**    | 2.284 | 79.1% | -21.0% | ✅ PASS |
| **Cash**   | 2.171 | 69.0% | -20.1% | ✅ PASS |
| **TLT**    | 2.017 | 68.9% | -27.7% | ❌ FAIL |

**Conclusão:** independente do sinal on-regime, o off-regime impõe a
ordem **GLD > Cash > TLT**. GLD como safe-haven com drift positivo
amortece sem correlacionar com SPY em rate-shocks
`[leverage_for_the_long_run, p.16, p.21]`. TLT correlaciona negativamente
com SPY em disinflation mas positivamente em rate-shock regimes (2022),
destruindo o hedge `[systematic_trading, ch.8]`.

**Impacto V2:** sanidade do setup — off-regime asset é feature de 1ª
ordem (efeito ~0.25 Sharpe, ~5-7pp MDD), sinal on-regime é feature de
2ª ordem (efeito ~0.1 Sharpe). Aggregator PBO/DSR vai precisar
considerar isso ao computar family-wise deflated Sharpe.

---

## Ranking V2-L2 atualizado (21/27 done)

Top-5 por OOS Sharpe com WF=PASS:

1. ★ `gayed_ema100_L2_off_gld`  — OOS 2.284 / MDD -21.0% (teto V2)
2. ★ `gayed_lrs_L2_off_gld`     — OOS 2.178 / MDD -21.9% ← **NEW**
3. ★ `gayed_ema100_L2_off_cash` — OOS 2.171 / MDD -20.1%
4. ★ `gayed_lrs_L2_off_cash`    — OOS 2.072 / MDD -21.9%
5. `gayed_sma200_L2_off_gld`    — OOS 1.645 / WF PASS 6/7 / MDD -21.9%

**Top-4 WF=PASS todos L2 com off-regime cash/GLD.** Kelly f/2 cap
respeitado `[leverage_space, Vince]`; L3/L5 stressam MDD > 25% cap.
O sweep produz um cluster robusto de 4 candidatos reais para o
aggregator tentar descorrelacionar (provável alta correlação intra-L2
— mesmo book de dias em regime-on sobre SPY/QQQ).

---

## Predições próximas LRS L3/L5

- **`gayed_lrs_L3_off_cash/tlt/gld`**: esperado Sharpe ~2.1-2.2 mas
  MDD ~-30-33% → **WF FAIL** (padrão Kelly f/2 linear scaling L2→L3 MDD
  observado em EMA100 e SMA200 igual).
- **`gayed_lrs_L5_off_cash/tlt/gld`**: Sharpe ~2.1-2.2, MDD ~-45-46%
  → **WF FAIL** (cap universal L5 cross-signal, 6ª confirmação
  pendente).

Registry: 6 pending LRS configs. Previsão: **nenhum novo ★ PASS até
aggregator** (L3/L5 LRS apenas confirmam capping). Aggregator corre em
~iter 42.

## Próxima unidade

`gayed_lrs_L3_off_cash` (iter 37).

## Citations

- Regime rotation + MA filter + leverage discipline:
  `[leverage_for_the_long_run, p.7, p.11, p.13, p.14, p.16, p.17, p.21]`.
- GLD safe-haven drift vs TLT rate-shock correlation:
  `[systematic_trading, ch.8]`.
- Leverage cap cross-check via PoR: `[leverage_space, Vince]`,
  `[math_money_mgmt, Vince]`.
- Walk-forward 6/8 gate + 25% DD cap: `[advances_fin_ml, ch.11]`.
- Retail Pepperstone Razor cost model: `specs/phase_3_5a_v2.md §3`.

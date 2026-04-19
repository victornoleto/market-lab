# [SHORT-HOLD CFD] V2-L2 EMA100 L2× off-gld — 2º SUBSET PASS 7/7 (novo teto Sharpe V2)

**Data:** 2026-04-18 17:57 UTC
**Iter:** 27 (V2 loop)
**Lead:** V2-L2 Gayed LETF rotation transported to CFD
**Config:** `gayed_ema100_L2_off_gld` (signal=EMA100, leverage=2×, off-regime=GLD, risk-on=SPY+QQQ)
**Status:** ✅ SUBSET PASS 7/7 (final PASS aguarda aggregator PBO/DSR)

---

## TL;DR

A troca do amortecedor cash→GLD na config-mãe EMA100 L2 subiu o Sharpe OOS de
**2.171 → 2.284** (+5.2%), o CAGR OOS de **68.96% → 79.14%** (+10.2pp) e
manteve o MDD OOS dentro do cap 25% (**-21.02%**). **WF=PASS** com 8/8 janelas
lucrativas e max-window-DD 22.7% < 25%. É o **novo teto Sharpe V2** e um
segundo SUBSET PASS independente dentro da mesma família de sinal — aumenta a
confiança pre-aggregator que o PASS final PBO/DSR é plausível.

---

## Metrics (window 2001-05-14 → 2026-04-14, 25 anos, 6266 bars, 616 switches)

| Split | Range | Sharpe | CAGR | MaxDD |
|-------|-------|-------:|-----:|------:|
| IS    | 2001–2017 | 1.856 | 53.42% | -22.67% |
| OOS   | 2018–2023 | **2.284** | **79.14%** | **-21.02%** |
| FWD   | 2024-01 → 2026-04 | 1.821 | 59.28% | -17.35% |

**Median hold:** 6.0d (target ≥3d ✅). **Switches:** SPY=315, QQQ=301.
**Custos cumulativos:** tx 125.8%, swap -44.9%.

### Subset gates (7/7)

| Gate | Valor | Pass |
|------|------:|:----:|
| oos_sharpe_gt_0 | 2.284 | ✅ |
| fwd_sharpe_gt_0 | 1.821 | ✅ |
| wf_pass | 8/8 profitable; max-win-DD 22.7%<25% | ✅ |
| median_hold_ge_3d | 6.0d | ✅ |
| oos_cagr_ge_30pct | 79.1% | ✅ |
| oos_sharpe_ge_2 | 2.284 | ✅ |
| oos_maxdd_le_25pct | -21.0% | ✅ |

---

## Por que GLD > cash > TLT como off-regime

Ranking empírico após 3 configs EMA100 L2:

| Off-regime | OOS Sharpe | OOS CAGR | OOS MDD | Max-win-DD | WF |
|------------|-----------:|---------:|--------:|-----------:|:--:|
| **GLD**    | **2.284**  | **79.14%** | **-21.02%** | **22.7%** | ✅ |
| cash       | 2.171      | 68.96%   | -20.13% | 20.1%       | ✅ |
| TLT        | 2.017      | 68.93%   | -27.69% | 27.7%       | ❌ |

**Intuição:**

- **GLD** contribui drift positivo durante risk-off (safe haven
  `[leverage_for_the_long_run, p.16, p.21]` — Gayed defende gold especificamente
  como amortecedor em rotações MA-based). Cash = 0% drift (só evita drawdown);
  GLD = ganho direto em regimes como 2008, 2020, 2022. +10pp CAGR vs cash com
  MDD ~ igual.
- **TLT** correlacionado positivamente com SPY em rate-shocks (e.g. 2022):
  perde junto com risk-on no off-regime, então max-win-DD estoura 25% cap
  `[advances_fin_ml, ch.11]`. Duration risk cancela o hedge.
- **Regra herdada de Gayed aplicada no CFD:** o hedge precisa ser decorrelacionado
  do risk-on em drawdowns, não só em tempo normal.

## Por que EMA100 > SMA200 (quarta confirmação)

Comparando os dois blocks inteiros agora:

| Signal | Melhor config | OOS Sharpe | MDD | WF |
|--------|---------------|-----------:|----:|:--:|
| **EMA100 L2 GLD** | 2.284 | -21.0% | ✅ |
| SMA200 L2 GLD     | 1.645 | -21.9% | ✅ (6/7) |

EMA100 paga 2× transaction cost (616 switches vs 310) mas entrega **+39%
Sharpe** e **+45pp CAGR OOS**. Confirma `[leverage_for_the_long_run, p.11,
p.14]`: sinais mais adaptativos com lookback menor capturam regimes mais
cedo, o custo de whipsaw é compensado pelo drift extra.

## Ranking V2-L2 até agora (12/27 done)

1. ★ `gayed_ema100_L2_off_gld` — OOS 2.284 / WF PASS / MDD -21.0%
2. ★ `gayed_ema100_L2_off_cash` — OOS 2.171 / WF PASS / MDD -20.1%
3. `gayed_ema100_L2_off_tlt` — OOS 2.017 / WF FAIL (MDD -27.7%)
4. `gayed_sma200_L2_off_gld` — OOS 1.645 / WF PASS 6/7 / MDD -21.9%
5–12. sma200 restante (0 PASS; L5 block MDD ~48%).

**Top-2 EMA100 + GLD/cash** são candidatos reais ao winner V2. Ainda faltam
15 configs (EMA100 L3/L5 + LRS L2/L3/L5) para compor universo suficiente do
PBO/DSR no aggregator.

## Predições para próximas configs

- **`gayed_ema100_L3_off_cash/gld`**: Sharpe OOS ~2.0 mas MDD ~30-35% estourando
  cap 25% (padrão SMA200 L3 confirmou que leverage 3× sempre viola cap).
  Provável WF=FAIL.
- **`gayed_ema100_L5_off_*`**: Sharpe ~2.0 (Sharpe invariance sob leverage
  `[leverage_for_the_long_run, p.17]`), MDD ~45-50% (quinta confirmação).
- **`gayed_lrs_L2_off_gld`**: LRS composite signal pode ser comparável a
  EMA100; desvio importante será se top LRS > EMA100 (possível) ou equivalente.

## Próxima unidade

`gayed_ema100_L3_off_cash` (primeira de 7 EMA100 restantes antes de LRS).

## Citations

- Regime rotation + MA filter + leverage discipline:
  `[leverage_for_the_long_run, p.7, p.11, p.13, p.14, p.16, p.17, p.21]`.
- Leverage cap cross-check via PoR: `[leverage_space, Vince]`,
  `[math_money_mgmt, Vince]`.
- Carver CFD cost model: `[systematic_trading, ch.8-9]`.
- Walk-forward 6/8 gate + 25% DD cap: `[advances_fin_ml, ch.11]`.
- Gold as safe-haven rotation hedge: `[leverage_for_the_long_run, p.16, p.21]`.
- Retail Pepperstone Razor cost model: `specs/phase_3_5a_v2.md §3`.

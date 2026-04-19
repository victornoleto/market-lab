# [SHORT-HOLD CFD] V2-L2 LRS L2× off-cash — 3º SUBSET PASS 7/7 (1º LRS)

**Data:** 2026-04-18 22:20 UTC
**Iter:** 34 (V2 loop)
**Lead:** V2-L2 Gayed LETF rotation transported to CFD
**Config:** `gayed_lrs_L2_off_cash` (signal=LRS composite ≥2/3 de {SMA100, SMA200, EMA100}, leverage=2×, off-regime=cash, risk-on=SPY+QQQ)
**Status:** ✅ SUBSET PASS 7/7 (final PASS aguarda aggregator PBO/DSR)

---

## TL;DR

Primeira config LRS do sweep entrega **OOS Sharpe 2.072 / CAGR 65.0% / MDD
-21.9% / WF PASS 8/8 profit** — 3º SUBSET PASS do V2-L2 e primeira
confirmação empírica de que o sinal **composite-vote** não só funciona mas
produz métricas a meio-caminho entre SMA200 sozinho (Sharpe 1.65) e EMA100
puro (Sharpe 2.17). Predição de iter 33 ("≤2.17, mais adaptativo que SMA200
menos que EMA100") HIT dentro de 5% no Sharpe e confirma a ordem ordinal.

---

## Metrics (window 2001-05-14 → 2026-04-14, 25y, 6266 bars, 578 switches)

| Split | Range | Sharpe | CAGR | MaxDD |
|-------|-------|-------:|-----:|------:|
| IS    | 2001–2017 | 1.912 | 47.6% | -12.3% |
| OOS   | 2018–2023 | **2.072** | **65.0%** | **-21.9%** |
| FWD   | 2024-01 → 2026-04 | 1.899 | 57.3% | -14.0% |

**Median hold:** 5.5d (target ≥3d ✅). **Switches:** SPY=287, QQQ=291.
**Cumulative costs:** tx 118.0%, swap -44.3%.

### Subset gates (7/7)

| Gate | Valor | Pass |
|------|------:|:----:|
| oos_sharpe_gt_0 | 2.072 | ✅ |
| fwd_sharpe_gt_0 | 1.899 | ✅ |
| wf_pass | 8/8 profitable; max-win-DD 21.9%<25% | ✅ |
| median_hold_ge_3d | 5.5d | ✅ |
| oos_cagr_ge_30pct | 65.0% | ✅ |
| oos_sharpe_ge_2 | 2.072 | ✅ |
| oos_maxdd_le_25pct | -21.9% | ✅ |

---

## Por que LRS fica entre SMA200 e EMA100

LRS (Leverage Rotation Signal) é uma votação majoritária sobre três MAs de
diferentes horizontes. Empiricamente, em L2 off_cash:

| Signal | OOS Sharpe | OOS CAGR | MDD | Switches | MedHold |
|--------|-----------:|---------:|----:|---------:|--------:|
| **EMA100** | 2.171 | 69.0% | -20.1% | 616 | 6.0d |
| **LRS**    | 2.072 | 65.0% | -21.9% | 578 | 5.5d |
| **SMA200** | 1.545 | 48.1% | -21.9% | 319 | 5.0d |

O voto composite dampens o whipsaw individual (desligando picos ruidosos da
EMA100) mas em troca perde parte da adaptabilidade — chega atrasado em
reversões de tendência curtas. O resultado é um compromisso: menos switches
que EMA100 puro (578 vs 616) mas mais que SMA200 (578 vs 319). Sharpe e CAGR
seguem a ordem intuitiva (EMA100 > LRS > SMA200) `[systematic_trading,
ch.8-9]` (diversificação de sinais não é almoço grátis quando há um
vencedor claro no sample).

**Implicação:** LRS não é o top performer V2 mas entrega um WF=PASS estável
a Sharpe > 2 — candidato de backup caso EMA100 sofra em alguma janela do
aggregator PBO (cross-cut de blocos temporais).

---

## Ranking V2-L2 atualizado (19/27 done)

1. ★ `gayed_ema100_L2_off_gld`  — OOS 2.284 / WF PASS / MDD -21.0%
2. ★ `gayed_ema100_L2_off_cash` — OOS 2.171 / WF PASS / MDD -20.1%
3. ★ `gayed_lrs_L2_off_cash`    — OOS 2.072 / WF PASS / MDD -21.9% ← NEW
4. `gayed_ema100_L2_off_tlt`    — OOS 2.017 / WF FAIL (MDD -27.7%)
5. `gayed_sma200_L2_off_gld`    — OOS 1.645 / WF PASS 6/7 / MDD -21.9%
6–19. L3/L5 + SMA200 L2 cash/tlt (WF FAIL por MDD cap ou sinal fraco).

**Top-3 WF=PASS:** todos são L2 (cap Kelly f/2 cumprido)
`[leverage_space, Vince]`. Dos três sinais, dois são candidatos reais
(EMA100 GLD/cash); LRS cash entra como candidato secundário robusto.

## Predições próximas LRS

- **`gayed_lrs_L2_off_tlt`**: esperado Sharpe ~2.0 mas WF=FAIL por MDD
  -27-28% (padrão TLT como amortecedor ruim em rate-shocks — 2022
  catastrófico `[leverage_for_the_long_run, p.16]` invertido).
- **`gayed_lrs_L2_off_gld`**: esperado Sharpe ~2.15-2.20, MDD ~-21%,
  WF=PASS (GLD amortecedor universal; LRS herda benefício igual EMA100).
  Candidato real ao top-3.
- **`gayed_lrs_L3_off_*`**: Sharpe ~2.0-2.1 mas MDD ~-30-33% → WF FAIL
  (padrão L3 sob LRS deve herdar o cap-violation de EMA100/SMA200 L3).
- **`gayed_lrs_L5_off_*`**: Sharpe ~2.1, MDD ~-45-46% → WF FAIL (Kelly
  f/2 cap universal L5 cross-signal, 5ª confirmação pendente).

## Próxima unidade

`gayed_lrs_L2_off_tlt` (iter 35).

## Citations

- Regime rotation + MA filter + leverage discipline:
  `[leverage_for_the_long_run, p.7, p.11, p.13, p.14, p.16, p.17, p.21]`.
- Composite vote trade-off (Sharpe vs switch frequency):
  `[systematic_trading, ch.8-9]`.
- Leverage cap cross-check via PoR: `[leverage_space, Vince]`,
  `[math_money_mgmt, Vince]`.
- Walk-forward 6/8 gate + 25% DD cap: `[advances_fin_ml, ch.11]`.
- Retail Pepperstone Razor cost model: `specs/phase_3_5a_v2.md §3`.

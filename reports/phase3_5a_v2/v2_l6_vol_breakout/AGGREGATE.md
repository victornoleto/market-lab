# Lead V2-L6 — Vol breakout multi-asset daily (aggregate)

**Phase:** phase3_5a_v2 | **Lead:** V2-L6 | **Status:** DEAD END (0/12 PASS)
**Period:** 2014-01-02 → 2026-04-14 (3088 daily bars, Tiingo cache)
**Universe:** 10 ETFs — SPY, QQQ, DIA, IWM, GLD, SLV, USO, UNG, TLT, HYG
**Tested:** 12 configs (3 lookbacks × 2 exits × 2 directions), equal-weight 1/N portfolio
**Aggregation iter:** 80

## Summary

V2-L6 testou o arquétipo canônico de Donchian vol-breakout sobre
um universo 1/N de índices (SPY/QQQ/DIA/IWM), metais (GLD/SLV),
commodities energéticas (USO/UNG) e fixed-income (TLT/HYG) —
lookback ∈ {20, 50, 100}d × exit ∈ {trailing ATR 3×, opposite channel
lookback/2} × direction ∈ {long-only, long/short}. Custos Pepperstone
Razor (spread 2bps half + slippage 1bps/side + swap long 0.005%/dia
/ swap short 0.002%/dia).

**Nenhuma das 12 configs passou o subset-gate completo.** As 12
exibem um padrão consistente:

- **IS (2014-2021):** 12/12 com Sharpe positivo, 0.237 → 0.904.
- **OOS (2022-2024):** **12/12 Sharpe NEGATIVO** (−0.728 → −0.217).
- **FWD (2025-2026):** 12/12 Sharpe positivo (0.599 → 1.945).
- **WF:** 7/12 pass (todos os long-only + 2 L/S); 5/12 fail (4 por
  MDD > 25%, 1 por ratio 0.62).

Todas as 12 falham `oos_sharpe_gt_0`, `oos_cagr_ge_30pct` e
`oos_sharpe_ge_2` — os três gates de OOS compõem o veto unânime.
Subset score máximo: **4/7** (6 long-only passam OOS MDD + FWD +
WF + hold, mas nunca OOS Sharpe/CAGR/Sharpe-2.0).

Verdict: **DEAD END** para V2-L6. O edge de Donchian/ATR breakout
aplicado 1/N sobre ETFs líquidos US sofre **asymmetric regime
penalty** — o ciclo 2022-2024 (hike cycle + sector rotation + gold
choppy + UNG squeeze) invalida o modelo, enquanto IS (2014-2021
QE era) e FWD (2025-2026 recovery) são favoráveis. Isso é o
sintoma clássico de overfitting implícito a uma janela única e
trivialmente refutado por gate OOS single-block
`[advances_fin_ml, ch.11]`.

## Cross-config table (ordenada por OOS Sharpe desc)

| Config                       | IS S   | OOS S  | OOS CAGR | FWD S  | WF            | IS MDD    | MedHold | Subset | Failed gates                                            |
|------------------------------|-------:|-------:|---------:|-------:|:--------------|----------:|--------:|:-------|:---------------------------------------------------------|
| `vol_donch20_atr3x_long`     | +0.769 | -0.217 | -1.8%    | +1.527 | ✅ 0.88        | 15.9%    | 20.5d   | 4/7    | oos_sharpe_gt_0, oos_cagr_ge_30pct, oos_sharpe_ge_2       |
| `vol_donch100_opp_long`      | +0.683 | -0.238 | -1.5%    | +1.064 | ✅ 0.88        | 12.1%    | 56.8d   | 4/7    | oos_sharpe_gt_0, oos_cagr_ge_30pct, oos_sharpe_ge_2       |
| `vol_donch50_atr3x_long`     | +0.696 | -0.249 | -1.5%    | +1.945 | ✅ 0.75        | 13.3%    | 21.2d   | 4/7    | oos_sharpe_gt_0, oos_cagr_ge_30pct, oos_sharpe_ge_2       |
| `vol_donch50_opp_long`       | +0.722 | -0.254 | -2.0%    | +1.756 | ✅ 0.88        | 15.1%    | 44.2d   | 4/7    | oos_sharpe_gt_0, oos_cagr_ge_30pct, oos_sharpe_ge_2       |
| `vol_donch100_atr3x_long`    | +0.630 | -0.279 | -1.3%    | +1.318 | ✅ 0.88        | 9.9%     | 19.5d   | 4/7    | oos_sharpe_gt_0, oos_cagr_ge_30pct, oos_sharpe_ge_2       |
| `vol_donch20_opp_long`       | +0.904 | -0.355 | -3.0%    | +1.393 | ✅ 0.88        | 18.6%    | 23.5d   | 4/7    | oos_sharpe_gt_0, oos_cagr_ge_30pct, oos_sharpe_ge_2       |
| `vol_donch100_opp_ls`        | +0.237 | -0.550 | -3.2%    | +0.945 | ❌ 0.75        | 26.8%    | 52.2d   | 3/7    | oos_sharpe_gt_0, wf_pass, oos_cagr_ge_30pct, oos_sharpe_ge_2 |
| `vol_donch50_opp_ls`         | +0.265 | -0.584 | -4.0%    | +1.003 | ❌ 0.75        | 26.0%    | 43.5d   | 3/7    | oos_sharpe_gt_0, wf_pass, oos_cagr_ge_30pct, oos_sharpe_ge_2 |
| `vol_donch20_atr3x_ls`       | +0.289 | -0.621 | -4.5%    | +0.968 | ❌ 0.75        | 27.8%    | 24.0d   | 3/7    | oos_sharpe_gt_0, wf_pass, oos_cagr_ge_30pct, oos_sharpe_ge_2 |
| `vol_donch100_atr3x_ls`      | +0.239 | -0.644 | -3.0%    | +1.139 | ❌ 0.62        | 25.1%    | 22.5d   | 3/7    | oos_sharpe_gt_0, wf_pass, oos_cagr_ge_30pct, oos_sharpe_ge_2 |
| `vol_donch50_atr3x_ls`       | +0.250 | -0.677 | -3.9%    | +0.851 | ✅ 0.75        | 24.0%    | 23.0d   | 4/7    | oos_sharpe_gt_0, oos_cagr_ge_30pct, oos_sharpe_ge_2       |
| `vol_donch20_opp_ls`         | +0.316 | -0.728 | -5.5%    | +0.599 | ❌ 0.75        | 28.7%    | 31.5d   | 3/7    | oos_sharpe_gt_0, wf_pass, oos_cagr_ge_30pct, oos_sharpe_ge_2 |

**PBO/DSR não aplicados no aggregator** — o gate OOS single-block
veta sozinho todas as configs, tornando os gates inter-config
(PBO/DSR/bootstrap 99.9%) irrelevantes neste lead.

## Padrões estruturais

1. **Long-only domina L/S por ampla margem.** 6 long-only têm
   mediana OOS Sharpe −0.26; 6 L/S têm mediana OOS Sharpe −0.63.
   A perna short custa 0.35-0.40 de Sharpe em OOS. UNG short (gas
   natural ETF) melt-up em 2022 (+100% no ano) + TLT/HYG shorts
   sofrendo Fed pivots = bleed consistente
   `[trend_following_covel, ch.5]`.
2. **Lookback 20d não é o melhor.** As tabelas de Covel e Faith
   sugerem 20/10 como canônico `[trading_systems_methods, p.353]`,
   mas em V2-L6 o top OOS é o 20d long-only (−0.217) — apenas 0.06
   melhor que 100d long-only (−0.279). A diferença é ruído:
   **toda a grade falha OOS**.
3. **Exit type é indiferente.** Trailing ATR 3× vs. opposite
   channel lookback/2 produzem métricas OOS praticamente
   idênticas dentro de cada direção (±0.05 Sharpe).
4. **Regime OOS 2022-2024 é letal para vol-breakout.** 2022 bear
   (SPY −18%), 2023 range choppy com recuperação tech, 2024 bull
   moderado mas com múltiplas correções 5-10%. Breakouts
   reverteram sistematicamente. Trend-follow discipline falha em
   mercados choppy `[trend_following_covel, ch.4]`.
5. **FWD 2025-2026 é favorável** (Sharpe 0.6-1.95 em 12/12) — não
   recupera o gate OOS, mas sinaliza que o sinal pode reviver em
   regime trending. Não é ativo suficiente para winner V2.

## Diagnóstico econômico

O arquétipo CTA-trend (Donchian + ATR chandelier + 1/N multi-asset)
foi referenciado 4× no dataset dos livros absorvidos
(`[trading_systems_methods]`, `[trend_following_covel]`, Schwager,
Faith). Todas essas fontes documentam que:

- **Edge depende de ocorrência de *a few* trades grandes** que pagam
  toda a whipsaw accumulation `[trend_following_covel, ch.3]`.
- **Universe precisa de pelo menos 30-50 instrumentos** para que
  a convexidade do payoff acumule `[stocks_on_the_move, p.~]`.
- **Custos CFD retail matam ∼70% do edge bruto futures-ish**
  `[systematic_trading, p.185-188]`.

V2-L6 usa apenas **10 ETFs US** (universe pequeno comparado aos
50+ futures da Winton ou 200+ single-stock do Clenow), e o ciclo
OOS 2022-2024 **não produziu** um trade macro grande recuperável:
o bear de 2022 foi rápido (6 meses) e inverteu em Q1 2023 antes
que breakouts de 100d dispara-se — exatamente o perfil de regime
que Covel identifica como o *worst case* para trend-follow.

A única forma realista de recuperar edge aqui seria:

- (a) expandir universo para 30+ (commodities futures ES/NQ/CL/GC/ZN/6E
  via futures data — fora do Pepperstone CFD catalog);
- (b) substituir sinal por Gayed-style regime filter (já provado em
  V2-L2);
- (c) carteira com vol-target + correlação-weighted (Carver) — já
  testado em V2-L4 e falhou CAGR 30%.

Nenhum dos três é V2-L6 stricto sensu — portanto V2-L6 é DEAD
como escrito. Recuperação pertence a V2-L2 (winner) e V2-L4
(DEAD) que já exploraram o espaço multi-asset.

## Consequência para Plano A V2

- V2-L6 vai para `## Dead ends` em `docs/self_improvement/memory.md`.
- Winner Plano A permanece `gayed_ema100_L2_off_gld` standalone
  (Sharpe OOS 2.285, CAGR 79.14%, MDD −21.02%, hold 6d — iter 43).
- `winners_short_hold:` lista 2 entradas (BollingerMR_GARCH partial
  + Gayed V2-L2) — nenhuma alteração desta iter.
- **Stop rule V2 não dispara** — já há 1 PASS em `winners_short_hold`;
  resta apenas L7 (verdict final + flip done).
- Próxima iter (81) = **V2-L7 atomic** — consolidar L1-L6, aplicar
  winner criteria §6 do spec, draft `specs/phase_4_paper_trading.md`,
  flip `status: done`.

## Citations

- `[trading_systems_methods, p.353]` — Donchian channel breakout
  20/10 canonical.
- `[volatility_trading]` (Sinclair) — ATR trailing exits e sizing.
- `[trend_following_covel, ch.3-5]` — discipline de trend-follow
  exige universe amplo + poucos trades grandes; choppy markets
  matam a tese.
- `[systematic_trading, p.185-188]` — retail CFD: spread+commission
  dominantes, trades infrequentes inviáveis sem universe largo.
- `[advances_fin_ml, ch.11]` — single-block OOS hold-out veta
  overfitting implícito a janela única; PBO/DSR são redundantes
  quando OOS sozinho rejeita.

## Links

- Per-config reports: `reports/phase3_5a_v2/v2_l6_vol_breakout/vol_*.md` (12)
- Registry: `reports/phase3_5a_v2/v2_l6_vol_breakout/registry.json`
- Jornada: `jornada/2026-04-19-0410-phase3.5a-v2-L6-vol-breakout-DEAD.md`

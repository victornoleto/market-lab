# [SHORT-HOLD CFD] V2-L2 sweep `gayed_ema100_L2_off_cash` — ★ SUBSET PASS 7/7 (primeiro V2 a limpar todos os subset gates)

**Data:** 2026-04-18 16:15 BRT
**Fase:** 3.5a-V2 / V2-L2 fan-out (iter 25, 10/27 configs done)
**Veredicto:** ✅ **PASS subset** (7/7 gates) — final PASS pendente de PBO/DSR no aggregator
**Marco:** Primeira config V2 inteira a passar todos os subset gates; EMA100 quebra o teto Sharpe ~1.65 do SMA200 block.
**Registry status:** sweeping (17 pendentes — EMA100 8 + LRS 9)

---

## O que rodou

**EMA100 × 2× leverage × cash off-regime**, universe SPY+QQQ, cost model Pepperstone Razor. Janela 2001-05-14 → 2026-04-14 (25 anos, 6266 bars, **616 switches** — 2× o ritmo SMA200 de 310). Zero code change (pytest preservado em 783).

Script: `scripts/iter_v2_l2_run_config.py --iter 25`.
Output: `reports/phase3_5a_v2/v2_l2_gayed_transported_cfd/gayed_ema100_L2_off_cash.{md,json}`.

## Resultado

| Split | Sharpe | CAGR | MaxDD | Final equity (×) |
|-------|-------:|-----:|------:|-----------------:|
| IS 2001-2017 | **1.999** | 52.05% | -12.34% | 1053.2 |
| OOS 2018-2023 | **2.171** | **68.96%** | **-20.13%** | 23.12 |
| FWD 2024-2026 | **1.936** | 59.00% | -13.98% | 2.87 |

- WF: 8/8 profitable, `max_window_drawdown=20.13%` < cap 25% ⇒ **WF=PASS** (primeiro MDD-cap-pass fora de SMA200 L2_cash/L2_gld).
- MedHold 6.0d (≥3d ✓).
- Cost drag: 125.8% transaction + -44.9% swap em 25y (tx dobrada vs SMA200 por 2× switches; swap igual por leverage invariante).

## Gates (7 subset)

| Gate | Valor | Pass |
|------|------:|:----:|
| oos_sharpe_gt_0 | 2.171 | ✅ |
| fwd_sharpe_gt_0 | 1.936 | ✅ |
| wf_pass | 6/8 (ratio 1.00, MDD 20.1%) | ✅ |
| median_hold_ge_3d | 6.0d | ✅ |
| oos_cagr_ge_30pct | 69.0% | ✅ |
| oos_sharpe_ge_2 | 2.171 | ✅ |
| oos_maxdd_le_25pct | -20.1% | ✅ |

**Todos os 7 subset gates passaram.** Final PASS precisa aggregator validar PBO < 0.5 + DSR p < 0.05 sobre os 27 Gayed-CFD configs (V2-L2 aggregator iter).

## Por que EMA100 quebrou o teto que SMA200 não conseguiu

**Hipótese central — confirmada empiricamente:** SMA200 é lag-heavy; ele entra tarde no risk-on e sai tarde do risk-off. EMA100 é ~2× mais responsivo (616 switches vs 310), o que custa o dobro em transaction cost mas captura melhor as bordas do regime. Em 2× leverage cash off-regime, o benefício da captura supera o custo — resultado líquido: **Sharpe OOS = 2.171 (SMA200 cap foi 1.65)**, e MDD OOS contido em -20.1% (SMA200 L2_cash entregou -21.9%).

Gayed [leverage_for_the_long_run, p.11, p.14] menciona que o 200-SMA sobre SPY é robusto como *filtro simples*, mas admite que sinais mais adaptativos (momentum, leading ratios) oferecem melhor timing custa-volatilidade. EMA100 é exatamente o ponto intermediário: mantém natureza trend-following mas responde mais rápido.

## 5ª confirmação da invariância de Sharpe por leverage

Com EMA100 em mãos vs SMA200, fica claro que **o teto Sharpe é um atributo do SINAL**, não da leverage:
- SMA200: teto ≈ 1.65 (L2 → L5 variam MDD mas não Sharpe).
- EMA100 L2_cash: 2.171 (quebra o teto).
- Previsão: EMA100 L3/L5 vão manter Sharpe ~2.1 e escalar MDD linearmente (≈ -30% em L3, ≈ -50% em L5 → WF=FAIL esperado em L3/L5).

Isso significa que, para passar todos os gates (inclusive MaxDD 25% cap), **EMA100 L2 é o sweet spot do sub-block**; L3/L5 provavelmente vão ser DOA como SMA200 foi.

## Implicações

1. **V2 tem um candidato real a winner.** Primeira vez que subset gates todos passaram em qualquer família V2. Sobrevive PBO/DSR no aggregator → vai para `winners_short_hold:`.
2. **EMA100 é o sinal a favorecer sobre SMA200** para Plano A CFD. Adicionar a esta observação no aggregator L2.
3. **Não adicionar ao memory.md `winners_short_hold:` ainda.** Subset PASS ≠ final PASS. Aguardar aggregator + jornada final V2-L2.
4. **Next iter 26:** `gayed_ema100_L2_off_tlt` — testa se TLT off-regime (rising-rates toxic em iter 17/20) destrói a vantagem EMA100 L2 mesmo com leverage moderado.

## Caveats

- **Cost drag enorme:** 125.8% transaction + -44.9% swap em 25y = 170% perdido para corretora. Em espaço $1k→equity_final 23k (OOS), ainda sobra edge, mas margem para degradação executiva é estreita.
- **616 switches = stress operacional.** Live paper trading vai testar se Pepperstone fill quality + slippage real batem com o modelo (2bps half + 3bps slippage RT pode ser otimista se chunks de ordem rompem book).
- **Hold 6d** é V2-permitido mas fica 20% acima do limite Path A original (5d). OK por override V2 formal; registrar no aggregator.

## Citações

- Regime rotation + leverage discipline: `[leverage_for_the_long_run, p.7, p.11, p.13, p.14, p.16, p.17, p.21]` (Gayed 2016/2020).
- Leverage cap via PoR: `[leverage_space, Vince]`, `[math_money_mgmt, Vince]`.
- Carver CFD cost model: `[systematic_trading, ch.8-9]`.
- Walk-forward 6/8 + 25% DD cap: `[advances_fin_ml, ch.11]`.
- PBO/DSR gates (aggregator): `[advances_fin_ml, p.208-211]`, `[advances_fin_ml, ch.14]`.
- Cost model Pepperstone Razor: Phase 3.5a-V2 spec §3.

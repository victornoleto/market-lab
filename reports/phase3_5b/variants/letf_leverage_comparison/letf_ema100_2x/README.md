# LETF EMA100/0%/2x — baseline (reuso do winner principal)

**Este diretório reaproveita o report canônico do winner LETF 2x de Phase
3.5b main.** Todos os 5 artefatos (`summary.json`, `standard_report.md`,
`trade_log.csv`, `trade_log.md`, `equity_curve.png`) são **symlinks
relativos** para `reports/phase3_5b/letf_rotation_ema100_2x/`.

## Por que reusar e não re-rodar?

1. **Winner imutável** (Phase 3.5b-addendum constraint #4) — o report canônico
   é read-only.
2. **Dados idênticos:** SPX TR stitched 1970-01-02 → 2026-04-14, fee 0.01,
   janela full-window, IR 15%, swap 0.
3. **Custo zero:** evita re-computar 20556 bars desnecessariamente quando o
   artefato já está validado.

## Ligação com Task B (LETF leverage comparison)

Este report entra na tabela side-by-side do
[`../README.md`](../README.md) como a coluna **L=2x** (baseline).
Tasks B2 (2.5x sintético) e B3 (3x) ficam nas colunas ao lado.

## Métricas-chave (para quick reference)

| Metric              | Valor (full-window 1970-2026) |
|---------------------|-------------------------------|
| CAGR                | 44.69%                        |
| Sharpe              | 1.848                         |
| MaxDD               | 20.55%                        |
| Calmar              | 2.175                         |
| Trades              | 296                           |
| Exposure            | 72.65%                        |
| IR vs SPY           | 1.601                         |
| Correlação vs SPY   | 0.590                         |

## Citações

- LETF synthetic formula `r = L × r_SPX - drag - fee`:
  `[leverage_for_the_long_run, p.16]`.
- Leverage level 2x (SSO real pós-2006, sintético antes):
  `[leverage_for_the_long_run, p.17, Table 8]`.
- EMA100 lookback + band=0%: Gayed 2016 moving-average filter. Winner
  3.5b main `jornada/2026-04-17/07-b1c-letf-rotation-gates-PASS.md`.

---

[← back to leverage_comparison](../README.md)
[← back to variants](../../README.md)

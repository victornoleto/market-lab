# Phase E-MVP — Strategy E (multi-market) grid report (2026-04-23 06:18 UTC)

Initial cash: R$50,000
Configs run: 42 (24 D1 + 18 D4)
OOS window: 2020-01-01 → 2023-12-31
Universe: SP500 top-200 + IBrX-100 (~300 tickers combined)

## Aggregate PBO: 0.786 (threshold < 0.5 per `[advances_fin_ml, p.208-211]`) → **FAIL**
- n_blocks=10, n_combinations=252

## Early-abort decision
🛑 **ABORT.** Zero configs satisfy `PBO<0.5 AND DSR p<0.1`.
See `jornada/YYYY-MM-DD-phase-e-mvp-no-winner.md` for R1-R5.

## Per-config results (OOS, sorted by Sharpe)

| Lead | Config | OOS Sharpe | OOS CAGR | OOS MDD | Tier CAGR | Tier MDD | DSR p | Trades (BR/US) | Tax R$ |
|------|--------|------------|----------|---------|-----------|----------|-------|----------------|--------|
| D4 | n_top=25, pre_n=30, vol_lookback=90 | +0.151 | +0.06% | 48.99% | Folclore | Forte warning | 0.970 | 198 (109/89) | R$73,601 |
| D4 | n_top=15, pre_n=30, vol_lookback=60 | +0.107 | -1.05% | 41.23% | Folclore | Forte warning | 0.976 | 155 (109/46) | R$70,916 |
| D4 | n_top=25, pre_n=30, vol_lookback=60 | +0.105 | -1.26% | 48.47% | Folclore | Forte warning | 0.976 | 194 (108/86) | R$69,146 |
| D4 | n_top=15, pre_n=30, vol_lookback=90 | +0.062 | -2.27% | 43.53% | Folclore | Forte warning | 0.981 | 154 (104/50) | R$78,244 |
| D4 | n_top=20, pre_n=30, vol_lookback=90 | +0.059 | -2.36% | 44.29% | Folclore | Forte warning | 0.981 | 196 (115/81) | R$69,905 |
| D4 | n_top=15, pre_n=50, vol_lookback=90 | +0.043 | -1.88% | 36.90% | Folclore | Forte warning | 0.983 | 178 (135/43) | R$44,625 |
| D1 | lookback=180, n_top=20, sector_cap_pct=0.2 | +0.035 | -3.81% | 49.89% | Folclore | Forte warning | 0.984 | 286 (229/57) | R$78,246 |
| D4 | n_top=20, pre_n=30, vol_lookback=60 | +0.027 | -3.37% | 43.86% | Folclore | Forte warning | 0.984 | 190 (109/81) | R$69,856 |
| D4 | n_top=25, pre_n=50, vol_lookback=90 | +0.018 | -2.78% | 42.49% | Folclore | Forte warning | 0.985 | 231 (148/83) | R$32,698 |
| D1 | lookback=180, n_top=25, sector_cap_pct=0.3 | +0.018 | -3.59% | 46.71% | Folclore | Forte warning | 0.985 | 331 (241/90) | R$52,156 |
| D1 | lookback=180, n_top=20, sector_cap_pct=0.25 | +0.010 | -4.34% | 49.91% | Folclore | Forte warning | 0.986 | 285 (216/69) | R$63,202 |
| D1 | lookback=180, n_top=15, sector_cap_pct=0.3 | +0.003 | -5.13% | 53.57% | Folclore | Reject | 0.986 | 235 (182/53) | R$79,485 |
| D4 | n_top=15, pre_n=50, vol_lookback=60 | +0.001 | -2.87% | 40.12% | Folclore | Forte warning | 0.986 | 193 (138/55) | R$36,529 |
| D1 | lookback=180, n_top=15, sector_cap_pct=0.2 | -0.000 | -4.96% | 50.15% | Folclore | Reject | 0.986 | 226 (183/43) | R$87,077 |
| D1 | lookback=180, n_top=15, sector_cap_pct=0.25 | -0.000 | -4.96% | 50.15% | Folclore | Reject | 0.986 | 226 (183/43) | R$87,077 |
| D1 | lookback=180, n_top=30, sector_cap_pct=0.3 | -0.001 | -3.93% | 46.13% | Folclore | Forte warning | 0.986 | 382 (266/116) | R$49,517 |
| D1 | lookback=180, n_top=30, sector_cap_pct=0.25 | -0.013 | -4.47% | 47.47% | Folclore | Forte warning | 0.987 | 372 (284/88) | R$55,559 |
| D4 | n_top=25, pre_n=50, vol_lookback=60 | -0.014 | -3.56% | 41.58% | Folclore | Forte warning | 0.987 | 229 (146/83) | R$35,721 |
| D4 | n_top=20, pre_n=40, vol_lookback=60 | -0.029 | -4.19% | 40.45% | Folclore | Forte warning | 0.988 | 198 (135/63) | R$41,309 |
| D1 | lookback=180, n_top=20, sector_cap_pct=0.3 | -0.037 | -5.63% | 50.02% | Folclore | Reject | 0.989 | 289 (211/78) | R$53,489 |
| D1 | lookback=180, n_top=25, sector_cap_pct=0.25 | -0.040 | -5.38% | 48.33% | Folclore | Forte warning | 0.989 | 336 (257/79) | R$49,735 |
| D4 | n_top=25, pre_n=40, vol_lookback=60 | -0.040 | -4.50% | 42.91% | Folclore | Forte warning | 0.989 | 210 (134/76) | R$35,017 |
| D1 | lookback=180, n_top=30, sector_cap_pct=0.2 | -0.053 | -5.68% | 48.39% | Folclore | Forte warning | 0.990 | 368 (290/78) | R$50,371 |
| D4 | n_top=15, pre_n=40, vol_lookback=90 | -0.054 | -4.83% | 44.45% | Folclore | Forte warning | 0.990 | 172 (124/48) | R$38,831 |
| D4 | n_top=20, pre_n=50, vol_lookback=90 | -0.059 | -4.32% | 39.51% | Folclore | Forte warning | 0.990 | 216 (144/72) | R$30,962 |
| D4 | n_top=20, pre_n=50, vol_lookback=60 | -0.062 | -4.37% | 40.05% | Folclore | Forte warning | 0.990 | 217 (140/77) | R$28,978 |
| D1 | lookback=180, n_top=25, sector_cap_pct=0.2 | -0.066 | -6.19% | 48.35% | Folclore | Forte warning | 0.991 | 336 (267/69) | R$56,382 |
| D4 | n_top=20, pre_n=40, vol_lookback=90 | -0.089 | -5.60% | 43.98% | Folclore | Forte warning | 0.992 | 200 (131/69) | R$33,263 |
| D1 | lookback=90, n_top=30, sector_cap_pct=0.3 | -0.104 | -7.22% | 50.65% | Folclore | Reject | 0.993 | 482 (322/160) | R$57,780 |
| D4 | n_top=15, pre_n=40, vol_lookback=60 | -0.109 | -6.24% | 46.39% | Folclore | Forte warning | 0.993 | 171 (129/42) | R$36,000 |
| D4 | n_top=25, pre_n=40, vol_lookback=90 | -0.118 | -6.46% | 46.50% | Folclore | Forte warning | 0.993 | 222 (136/86) | R$31,997 |
| D1 | lookback=90, n_top=25, sector_cap_pct=0.25 | -0.137 | -8.32% | 52.44% | Folclore | Reject | 0.994 | 420 (309/111) | R$59,265 |
| D1 | lookback=90, n_top=20, sector_cap_pct=0.3 | -0.138 | -8.31% | 50.98% | Folclore | Reject | 0.994 | 379 (258/121) | R$69,457 |
| D1 | lookback=90, n_top=25, sector_cap_pct=0.3 | -0.147 | -8.54% | 52.14% | Folclore | Reject | 0.994 | 430 (303/127) | R$61,439 |
| D1 | lookback=90, n_top=30, sector_cap_pct=0.25 | -0.150 | -8.60% | 51.65% | Folclore | Reject | 0.994 | 460 (337/123) | R$52,456 |
| D1 | lookback=90, n_top=30, sector_cap_pct=0.2 | -0.162 | -9.05% | 52.26% | Folclore | Reject | 0.995 | 453 (345/108) | R$56,142 |
| D1 | lookback=90, n_top=20, sector_cap_pct=0.25 | -0.180 | -9.35% | 51.70% | Folclore | Reject | 0.995 | 369 (270/99) | R$70,024 |
| D1 | lookback=90, n_top=25, sector_cap_pct=0.2 | -0.197 | -9.86% | 52.78% | Folclore | Reject | 0.996 | 407 (316/91) | R$57,730 |
| D1 | lookback=90, n_top=15, sector_cap_pct=0.3 | -0.207 | -10.14% | 53.17% | Folclore | Reject | 0.996 | 304 (220/84) | R$89,797 |
| D1 | lookback=90, n_top=20, sector_cap_pct=0.2 | -0.221 | -10.18% | 51.84% | Folclore | Reject | 0.997 | 362 (282/80) | R$72,864 |
| D1 | lookback=90, n_top=15, sector_cap_pct=0.2 | -0.245 | -11.14% | 52.92% | Folclore | Reject | 0.997 | 298 (233/65) | R$76,652 |
| D1 | lookback=90, n_top=15, sector_cap_pct=0.25 | -0.245 | -11.14% | 52.92% | Folclore | Reject | 0.997 | 298 (233/65) | R$76,652 |

## Citations
- PBO: `[advances_fin_ml, p.208-211]`
- DSR deflator: `[advances_fin_ml, p.275]`
- Clenow: `[stocks_on_the_move, p.76-77]`
- Mandate: `docs/investment-mandate.md §4b` + `docs/mandate_overrides/2026-04-23-strategy-e-multimarket.md`

# [SHORT-HOLD CFD] Phase 3.5a — Lead T1: BollingerMR multi-asset FX/metais 1h = DEAD END

**Iteração:** 2 do loop Phase 3.5a
**Lead:** T1 (primeiro da lista ativa)
**Veredito:** **DEAD END** — 0/12 candidates em 3 direções testadas
**Próximo:** Lead T2 (Donchian/ATR breakout intraday)

---

## O que foi testado

BollingerMR canônico — a configuração que o livro do Bollinger
recomenda: média móvel de 20 barras, bandas a ±2 desvios-padrão
`[bollinger_on_bollinger_bands, p.51-58]`. Stop-loss 2%, time-stop
em 24 barras (1 dia em 1h), entrada no toque da banda inferior
(long), banda superior (short), ou ambas (both).

**Universo:** os 12 tickers puxados na iter 1 (Lead T0) — EURUSD,
GBPUSD, USDJPY, USDCHF, AUDUSD, USDCAD, NZDUSD, EURJPY, EURGBP,
GBPJPY, XAUUSD, XAGUSD — todos em 1h, janela completa
**2020-01-01 → 2026-04-17** (longest disponível na cache Tiingo).

**Custos Pepperstone modelados:**
- FX majors: `half_spread` = 2 bps (spread Razor ~0.4 bp +
  $3.50/side de commission → equivalente a ~3.5 bps, conservador)
- Metais (XAU/XAG): `half_spread` = 5 bps
- Swap diário: 0.005%/dia simétrico (~1.8%/ano), conservador
  (Pepperstone real é assimétrico e mais baixo em FX majors)

**Splits testados (mutuamente exclusivos):**
- IS: 2020-01-01 → 2023-12-31 (4 anos)
- OOS: 2024-01-01 → 2025-12-31 (2 anos)
- FWD stress: 2026-01-01 → 2026-04-17 (último trimestre)

**Direções testadas:** `both`, `long`, `short` — 3 passes × 12
tickers = 36 configs totais.

---

## Resultado

**0/36 candidates.** Todos os tickers, todas as direções, todos os
splits produziram Sharpes **negativos** — algumas exceções isoladas
em FWD (XAGUSD long +0.70, NZDUSD long +0.06) mas sem coerência IS/OOS.

### OOS Sharpe — best por ticker (dentre direções `both/long/short`)

Dados extraídos de `reports/phase3_5a/t1_bollinger_mr_fx_metals{_,_long_,_short_}summary.json`.

| ticker | best dir | OOS Sharpe | OOS CAGR% | OOS trades | FWD Sharpe | med_hold_d |
|---|---|---:|---:|---:|---:|---:|
| eurusd  | long  | -1.31 |  -2.45 | 269 | -0.93 | 0.58 |
| gbpusd  | long  | -1.56 |  -2.78 | 242 | -1.83 | 0.60 |
| usdjpy  | long  | -1.89 |  -4.98 | 219 | -3.25 | 0.58 |
| usdchf  | long  | -1.86 |  -3.87 | 233 | -2.42 | 0.62 |
| audusd  | short | -1.03 |  -2.46 | 236 | -2.96 | 0.54 |
| usdcad  | long  | -2.26 |  -3.26 | 230 | -3.43 | 0.58 |
| nzdusd  | short | -0.86 |  -2.11 | 229 | -1.99 | 0.54 |
| eurjpy  | long  | -0.73 |  -1.72 | 228 | -1.32 | 0.58 |
| eurgbp  | short | -2.58 |  -3.26 | 256 | -3.06 | 0.54 |
| gbpjpy  | long  | -0.72 |  -1.90 | 240 | -1.11 | 0.46 |
| xauusd  | long  | -0.55 |  -2.40 | 213 | -1.37 | 0.54 |
| xagusd  | long  | -0.26 |  -2.23 | 239 | +0.70 | 0.46 |

**Best overall:** XAGUSD long — OOS Sharpe **-0.26**, FWD Sharpe
+0.70 (FWD positivo isolado é ruído amostral, 41 trades). Ainda
muito longe do gate `OOS Sharpe ≥ 0.5`.

**Nenhum ticker passa o screen inicial** (OOS Sharpe ≥ 0.5 AND
median_hold ≤ 5d AND FWD Sharpe > 0).

### Observações importantes

1. **Median hold OK** (0.5-0.7 dias ≈ 12-17h) — a regra inflexível
   de `≤ 5 days` `[systematic_trading, p.185-188]` seria atendida.
   O problema não é swap; é spread+commission consumindo o edge.

2. **Trade count elevado**: 200-500 trades OOS (2 anos) → custos
   transacionais integrados matam qualquer edge MR.

3. **Padrão robusto**: ordem de magnitude das Sharpes é igual em
   IS, OOS e FWD — não é ruído amostral, é um edge genuinamente
   ausente (ou negativo) pra BollingerMR canônico em FX/metais 1h
   com custos realistas de varejo.

4. **Direção não ajuda**: tanto `long` quanto `short` ficam
   negativos, `both` é o pior (paga custos dobrados). Isso descarta
   a hipótese de "asymmetric FX edge".

---

## Por que falha

BollingerMR funciona bem em SPY 1h equity (jornada 2026-04-16:
CAGR ~5.9%, PARTIAL-GO) porque:
- **Spread SPY CFD** ≈ $0.01-0.02 = 0.2-0.4 bps em SPY@500
- **Flat up-drift** de equity dá viés long que MR-dip-buy captura
- **Volatility clustering** acentuada (VIX regimes) cria MR
  pronunciado

FX majors 1h:
- **Spread 2-4 bps** em Razor + commission 3.5 bps = 5-7 bps total
- **Sem drift** — preço caminha random
- **Vol estável** — bandas a ±2σ acertam poucos outliers genuínos

Resultado: nas 200-500 entradas OOS, a média de retorno por trade
precisaria ser > 7 bps pra empatar custos — e não é.

---

## Verdict

**Lead T1 = DEAD END**. BollingerMR canônico em FX/metais 1h não
produz candidate em nenhuma direção. Marcado em `dead_ends` da
memory.md.

Implicação: **MR em FX 1h com custos realistas não sobrevive
simplesmente por expandir universo**. Pra ressuscitar MR em FX
seria necessário:
- Vol-sizing dinâmico pra reduzir exposição em regimes de drift
  (garch_lambda > 0 — não testado aqui)
- Bandas dinâmicas (Keltner / ATR-based) pra ajustar a sensitividade
- Regime filter (DXY/ADX) pra só operar quando MR é regime
- Mudança de frequência pra 15m (não disponível no whitelist Tiingo)

Essas exploraria em Leads T5 (regime filter hybrid) ou em futuras
extensões — não agora. Continuamos a sequência.

---

## Próximo

**Lead T2 — Donchian/ATR breakout intraday.**

Hipótese: breakout é um edge estruturalmente diferente de MR.
Em FX, breakouts tendem a ser **tendências curtas** após consolidação
(news release, session open), que é exatamente o perfil short-hold
Pepperstone precisa. Donchian 10/5 e 20/10 em 1h sobre FX majors
+ ATR-channel breakout (Kaufman/Chandelier).

Citação obrigatória: `[trading_systems_methods, p.353]` (Donchian),
`[volatility_trading]` (ATR).

---

## Artefatos produzidos

- `scripts/run_bollinger_mr_t1_multi_asset.py` (novo, 340 linhas)
- `reports/phase3_5a/t1_bollinger_mr_fx_metals/summary.{json,md}` (direction=both)
- `reports/phase3_5a/t1_bollinger_mr_fx_metals_long/summary.{json,md}` (direction=long)
- `reports/phase3_5a/t1_bollinger_mr_fx_metals_short/summary.{json,md}` (direction=short)
- Pytest: 709 passed (baseline intacto)

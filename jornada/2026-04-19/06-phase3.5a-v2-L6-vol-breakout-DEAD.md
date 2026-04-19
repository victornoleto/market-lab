# [SHORT-HOLD CFD] V2-L6 — Donchian vol-breakout 12-config DEAD: 0/12, regime OOS 2022-2024 mata trend-follow

**Data:** 2026-04-19 04:10 (iter 80, loop `phase3.5a-v2/plano-a-last-attempt-20260418`)
**Lead:** V2-L6 (sweep-configs, aggregator) — Donchian channel + ATR trailing/opposite exit, 1/N multi-asset 10 ETFs, daily, custos Pepperstone Razor.
**Verdict:** ❌ DEAD END (0/12 configs subset-PASS; **12/12 com OOS Sharpe NEGATIVO**).

---

## O que fizemos

V2-L6 é o último lead de pesquisa do Plano A V2 antes do verdict
final (V2-L7). Testou o arquétipo CTA-trend canônico
`[trading_systems_methods, p.353]`, `[trend_following_covel, ch.3-5]`,
`[volatility_trading]`:

- **Universe:** 10 ETFs líquidos US — SPY, QQQ, DIA, IWM (índices),
  GLD, SLV (metais), USO, UNG (energia), TLT, HYG (FI).
- **Sinal:** Donchian breakout entry no extremo `lookback`-day.
- **Exit:** trailing ATR 3× sobre ATR(20) **OU** opposite Donchian
  channel `lookback/2`-day.
- **Direction:** long-only **OU** long/short.
- **Lookback:** 20 / 50 / 100 dias.
- **Grid:** 3 × 2 × 2 = **12 configs**, executadas iter 68-79
  (uma config por iter, fan-out registry).
- **Custos:** Pepperstone Razor — spread half 2bps + slippage 1bps/side
  + swap long 0.005%/dia + swap short 0.002%/dia.
- **Splits:** IS 2014-2021 (2015 bars) | OOS 2022-2024 (753 bars) |
  FWD 2025-04-14 (320 bars). Walk-forward 8 janelas + 7 subset gates
  + 5-gate framework V2.

## O que encontramos

12 configs, 0 PASS. **OOS Sharpe negativa em 12/12**:

| Config                       | IS S   | OOS S  | OOS CAGR | FWD S  | WF            | MedHold | Subset |
|------------------------------|-------:|-------:|---------:|-------:|:--------------|--------:|:-------|
| `vol_donch20_atr3x_long`     | +0.769 | **-0.217** | -1.8% | +1.527 | ✅ 0.88        | 20.5d   | 4/7    |
| `vol_donch100_opp_long`      | +0.683 | -0.238 | -1.5%    | +1.064 | ✅ 0.88        | 56.8d   | 4/7    |
| `vol_donch50_atr3x_long`     | +0.696 | -0.249 | -1.5%    | +1.945 | ✅ 0.75        | 21.2d   | 4/7    |
| `vol_donch50_opp_long`       | +0.722 | -0.254 | -2.0%    | +1.756 | ✅ 0.88        | 44.2d   | 4/7    |
| `vol_donch100_atr3x_long`    | +0.630 | -0.279 | -1.3%    | +1.318 | ✅ 0.88        | 19.5d   | 4/7    |
| `vol_donch20_opp_long`       | +0.904 | -0.355 | -3.0%    | +1.393 | ✅ 0.88        | 23.5d   | 4/7    |
| `vol_donch100_opp_ls`        | +0.237 | -0.550 | -3.2%    | +0.945 | ❌ 0.75 (DD 27%) | 52.2d | 3/7    |
| `vol_donch50_opp_ls`         | +0.265 | -0.584 | -4.0%    | +1.003 | ❌ 0.75 (DD 26%) | 43.5d | 3/7    |
| `vol_donch20_atr3x_ls`       | +0.289 | -0.621 | -4.5%    | +0.968 | ❌ 0.75 (DD 28%) | 24.0d | 3/7    |
| `vol_donch100_atr3x_ls`      | +0.239 | -0.644 | -3.0%    | +1.139 | ❌ 0.62        | 22.5d   | 3/7    |
| `vol_donch50_atr3x_ls`       | +0.250 | -0.677 | -3.9%    | +0.851 | ✅ 0.75        | 23.0d   | 4/7    |
| `vol_donch20_opp_ls`         | +0.316 | -0.728 | -5.5%    | +0.599 | ❌ 0.75 (DD 29%) | 31.5d | 3/7    |

Padrões:

1. **Long-only** (mediana OOS −0.26) > **L/S** (mediana OOS −0.63);
   diferença de 0.35-0.40 Sharpe vinda do short bleed (UNG +100% em
   2022, TLT/HYG short na hike-cycle).
2. **Lookback é indiferente:** 20 vs. 50 vs. 100d produzem OOS Sharpe
   dentro de ±0.06 — entry timing não recupera regime hostil.
3. **Exit type idêntico:** trailing ATR 3× e opposite channel
   diferem ±0.05 Sharpe — ambos entregam o mesmo OOS.
4. **FWD 2025-2026 positivo em 12/12** (Sharpe 0.6-1.95) — sinal
   tem vida em regime trending, mas FWD sozinho não recupera o
   gate OOS single-block `[advances_fin_ml, ch.11]`.

## Por que falha (diagnóstico)

O ciclo OOS **2022-2024 é o pior cenário possível** para Donchian
1/N multi-asset retail:

- **2022 bear (SPY −18%) rápido (6 meses) e revertendo Q1 2023**:
  breakouts de 100d tinham acabado de disparar quando o mercado
  inverte → whipsaw catastrófico. Trend-follow precisa de
  *persistent* trend, não bear curto + recuperação rápida
  `[trend_following_covel, ch.4]`.
- **2023 range choppy com leadership tech narrow (MAG7)**:
  diversification 1/N foi punida — DIA/IWM/HYG arrastaram o
  portfolio enquanto QQQ subia.
- **2024 bull moderado com 3 correções 5-10%**: stops ATR 3×
  disparam fora dos topos, opposite channel sai cedo demais.
- **UNG 2022 squeeze** (gas natural russo): short em UNG bleed
  de 100% no ano (citação per-config: `vol_donch20_opp_ls` UNG
  short final equity 0.36 — perda 64% só no UNG short).
- **TLT/HYG na hike-cycle**: Fed hikes 2022-2024 quebraram
  duration trades — 4/12 configs L/S falham WF por MDD > 25%
  (cap V2 spec §6).

A discipline de Covel (`[trend_following_covel, ch.3]`)
documenta que **3-5 trades enormes pagam toda a whipsaw
accumulation**. Esses trades não aconteceram em 2022-2024:
nenhum macro-move grande ininterrupto durou > 6 meses sem
correção 10%+ que reverteria stops ATR 3×.

A única forma plausível de recuperar V2-L6 seria expandir
universo para 30-50 instrumentos com correlações genuinamente
ortogonais (futures Euribor / 6E / VX / commodities crops) —
**fora do catalog Pepperstone CFD**, portanto fora do escopo
Plano A.

## O que isso informa para Plano A

- **V2-L6 para `## Dead ends`** em `docs/self_improvement/memory.md`.
- Winner Plano A permanece `gayed_ema100_L2_off_gld` standalone
  (Sharpe OOS 2.285 / CAGR 79.14% / MDD −21.02% / hold 6d — iter 43
  V2-L2 PASS). Esse winner é **regime-driven** (EMA100 sobre SPY
  rota para GLD em risk-off) — exatamente a classe de sinal que
  V2-L6 (vol-breakout puro) não consegue replicar.
- `winners_short_hold:` intacto (2 entradas: BollingerMR_GARCH
  partial + Gayed V2-L2).
- **Stop rule V2 não dispara** — já há 1 PASS em `winners_short_hold`;
  resta **apenas V2-L7** (verdict final + flip `status: done` +
  draft `specs/phase_4_paper_trading.md`).
- Confirma classe-DEAD: trend-follow puro CTA em ETF universe
  pequeno é refutado pelo regime 2022-2024. Edge Plano A tem que
  ser **regime-driven** (Gayed-class) ou **vol-mean-reversion
  GARCH-sized** (BollingerMR seed) — pure breakout rotacional já
  está cremado em V1 (1h FX/metais) e V2-L1 (TSMOM daily) e agora
  V2-L6 (vol-breakout daily).

## Próximos passos

**Iter 81 = V2-L7 atomic** (último lead, 1 iter):

1. Consolidar L1-L6: 6 leads de pesquisa, 1 PASS (V2-L2), 5 DEAD
   (L1, L3, L4, L5, L6).
2. Aplicar winner criteria §6 do spec V2.
3. Draft `specs/phase_4_paper_trading.md` com winner Gayed
   V2-L2 + setup cTrader Open API Pepperstone.
4. Flip `status: done` em memory.md.
5. Atualizar `jornada/README.md` + ROADMAP.md (Phase 3.5a-V2 →
   completed).

**V2 não é abandonado** — produziu 1 PASS sólido (Gayed V2-L2)
que satisfaz mandate §3 (multi-asset CFD edge utilizável). Stop
rule binding `[project_plano_a_v2_last_attempt.md]` requer 0
PASS para abandonar — V2 supera o threshold por 1.

## Citações

- `[trading_systems_methods, p.353]` — Donchian channel breakout
  canonical (20/10 padrão; 20/50/100 testados).
- `[volatility_trading]` (Sinclair) — ATR trailing exits e
  position sizing.
- `[trend_following_covel, ch.3-5]` — trend-follow discipline:
  3-5 trades grandes pagam o whipsaw; choppy markets letais.
- `[systematic_trading, p.185-188]` (Carver) — retail CFD:
  spread+commission dominantes; universe pequeno torna trend
  inviável.
- `[advances_fin_ml, ch.11]` — single-block OOS hold-out veta
  overfitting implícito a janela única.
- `[stocks_on_the_move]` (Clenow) — momentum precisa de universe
  amplo (200+ stocks) para diversificar drawdowns.

## Artifacts

- AGGREGATE: [`reports/phase3_5a_v2/v2_l6_vol_breakout/AGGREGATE.md`](../reports/phase3_5a_v2/v2_l6_vol_breakout/AGGREGATE.md)
- Per-config: `reports/phase3_5a_v2/v2_l6_vol_breakout/vol_donch{20,50,100}_{atr3x,opp}_{long,ls}.md` (12)
- Registry: `reports/phase3_5a_v2/v2_l6_vol_breakout/registry.json` (status=done)

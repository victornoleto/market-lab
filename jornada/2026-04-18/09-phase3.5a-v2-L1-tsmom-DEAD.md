# Phase 3.5a-V2 Lead V2-L1 [SHORT-HOLD CFD] — TSMOM multi-asset daily DEAD END

**Data:** 2026-04-18 14:07 UTC
**Phase:** 3.5a-V2 (Plano A last attempt)
**Lead:** V2-L1 — TSMOM multi-asset daily
**Iter range:** 2 (bootstrap) → 14 (aggregator)
**Verdict:** ❌ DEAD END (0/12 configs PASS)
**Path tag:** [SHORT-HOLD CFD]

---

## Resumo humano

A primeira família de Plano A V2 refutou em cheio. Testei o time-series
momentum canônico (Carver / Covel / Prado) sobre o universo multi-asset
V2-L0 (30 instrumentos: 18 ETFs, 12 FX/crypto), em daily, janela completa
2001-05-14 → 2026-04-17 (24.9 anos). 12 configurações (lookback
{1,3,6,12} meses × vol-target {10,15,20}%), binary long/flat,
rebalance mensal EOM. **Nenhuma configuração produziu Sharpe OOS
positivo**; todas as 12 tiveram Sharpe FWD (2024-01→2026-04)
entre −1.12 e −2.10 sob o cost model Pepperstone Razor.

A causa é estrutural, não paramétrica: **o tamanho do hold mata o
edge antes de ele aparecer**. Rebalance mensal vol-targeted produz
hold mediano 41-160 dias. A 5 bps/dia de swap overnight (taxa Razor
long-swap), isso empilha swap drag cumulativo de **74% a 166% do
equity inicial** — ou seja, a máquina paga 1 equity inteiro em swap
ao longo dos 25 anos, enquanto o próprio sinal de momentum devolve
retorno negativo. Vol-targeting piora (mais vt → mais notional →
mais swap × mesmo hold).

Ainda pior: o esquema vol-weighting força alocação nos 3 ativos de
menor vol (EURUSD, GBPUSD, USDJPY). Em 2024-2026, regime de USD
fortalecido, essas longs foram atropeladas. A "diversificação" do
universo de 30 ativos é ilusória: em *risk-adjusted weights*, o
portfolio convergia sempre para o mesmo FX 3-pack.

## Cross-config (todos ❌)

| Config | Sharpe IS | Sharpe OOS | CAGR OOS | Sharpe FWD | Med hold | WF | Swap cum |
|--------|----------:|-----------:|---------:|-----------:|---------:|---:|---------:|
| tsmom_lb01m_vt10 | −0.38 | −1.13 | −2.5% | −1.20 | 41d | 0/8 | 73.8% |
| tsmom_lb01m_vt15 | −0.38 | −1.12 | −3.4% | −1.22 | 41d | 0/8 | 107% |
| tsmom_lb01m_vt20 | −0.38 | −1.04 | −3.4% | −1.19 | 41d | 0/8 | 131% |
| tsmom_lb03m_vt10 | −0.17 | −0.34 | −0.7% | −1.27 | 82d | 3/8 | 74.7% |
| tsmom_lb03m_vt15 | −0.17 | −0.40 | −1.1% | −1.26 | 82d | 3/8 | 109% |
| tsmom_lb03m_vt20 | −0.17 | −0.41 | −1.3% | −1.12 | 82d | 3/8 | 135% |
| tsmom_lb06m_vt10 | −0.20 | −0.22 | −0.5% | −2.10 | 128d | 2/8 | 81.4% |
| tsmom_lb06m_vt15 | −0.20 | −0.29 | −0.8% | −2.03 | 128d | 2/8 | 119% |
| tsmom_lb06m_vt20 | −0.20 | −0.31 | −1.0% | −1.80 | 128d | 2/8 | 147% |
| tsmom_lb12m_vt10 | −0.32 | −0.21 | −0.5% | −1.52 | 160d | 1/8 | 92.8% |
| tsmom_lb12m_vt15 | −0.32 | −0.25 | −0.8% | −1.47 | 160d | 1/8 | 135% |
| tsmom_lb12m_vt20 | −0.32 | −0.25 | −0.9% | −1.29 | 160d | 1/8 | 166% |

**Least-worst:** `tsmom_lb06m_vt10` (Sharpe OOS −0.22). Ainda refutado
em todos os 5 gates materiais — swap drag 81% mesmo no config menos
alavancado.

## Por que isso não invalida V2 como um todo

Refutação importa apenas para a família canônica rebalance-mensal. Os
próximos leads usam mecanismos de contenção de custo diferentes:

- **V2-L2 Gayed LETF rotation** — regime MA (200SMA / EMA100 / LRS)
  sobre SPY, risk-on → QQQ/SPY alavancado via margin. Hold comparável
  mas sinal é binário regime, não cross-sectional vol-weighting. FX
  3-pack attractor não se aplica.
- **V2-L3 AFML triple-barrier + meta-label** — time-stop forçado a 20d,
  ATR stop 1×, target 2×. Swap drag cap imposto pela estrutura do
  barrier. Meta-label (RandomForest 100 trees, 4 features) filtra
  falsos positivos da primary EMA-50 — Prado `[advances_fin_ml, ch.7]`
  documenta ganho 20-40% em IR para primaries fracas.
- **V2-L5 equity pairs** — market-neutral; swap long ≈ swap short
  (Pepperstone Razor short-swap 0.2 bps vs long 5 bps, mas net < 3 bps/d).
- **V2-L6 vol breakout** — trailing ATR exit bounds hold a 20-50 bars.

V2 continua. A hipótese refutada é específica: "TSMOM canônico com
rebalance mensal sobrevive a custo retail CFD". Carver em
`[systematic_trading, p.185-188]` já alertava que retail deveria mirar
holds 1-4 semanas, não 1-6 meses. Esta lead é a confirmação empírica
custosa dessa diretriz.

## Próximo passo

Ir para **V2-L2 — Gayed LETF rotation transportada CFD** (27 configs:
regime signal × leverage × off-regime). Criar
`src/ai_trade/backtest/strategies/plano_a_leveraged_rotation.py`
(arquivo NOVO; não tocar em `letf_rotation.py` que é Plano B
imutável). Continua em fan-out mode — 1 iter = 1 config.

## Citações

- TSMOM canonical: `[algo_trading_chan, p.133, ch.6]`,
  `[systematic_trading, ch.8-9]` (Carver binário + vol-target),
  `[trend_following_covel, ch.5-6]` (EOM canonical).
- Vol-target no-look-ahead sizing: `[advances_fin_ml, p.162-164]`.
- Retail cost optimum 1-4 weeks (Carver): `[systematic_trading, p.185-188]`.
- Walk-forward 6/8 gate: `[advances_fin_ml, ch.11]`, Pardo (2008) ch.10-11.
- Slow-trend regime break post-2008: `[systematic_trading, ch.9]`.
- Pepperstone Razor cost model: `docs/investment-mandate.md` §3 + spec §3.

## Artefatos

- Aggregate: `reports/phase3_5a_v2/v2_l1_tsmom_multi_asset_daily/AGGREGATE.md`
- Per-config: `reports/phase3_5a_v2/v2_l1_tsmom_multi_asset_daily/tsmom_*.{md,json}`
  (12 pares × 2)
- Daily returns: `...tsmom_*_daily_returns.parquet` (12 arquivos)
- Registry: `reports/phase3_5a_v2/v2_l1_tsmom_multi_asset_daily/registry.json`
  (status=done)

## Baseline

- Pytest 771 passed (zero código tocado no aggregator).
- Zero modificação em Plano B strategies ou BollingerMR seed.
- Zero push origin; iter roda em branch V2.

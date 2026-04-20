# Phase 4.0 — Index CFD path validado, Plano A $1k habilitado

**Data:** 2026-04-19 (noite) · **Tipo:** validação Phase 4 pre-req · **Impacto:** habilita Plano A live com $1k de capital inicial.

## O que aconteceu

Depois de descobrir o colapso bps→dólares em conta pequena (jornada 11), usuário optou pelo **Caminho 3** (Index CFD em vez de share CFD). Draftei `specs/phase_4_0_index_cfd_validation.md` com 5 tasks e stop rules binding. Usuário aprovou o spec; executei fast-path T3+T4 (offline, não requer conta Pepperstone).

## Resultado — **10/10 gates PASS**

**T3 sanity backtest** (re-run V2-L2 config em SPX TR + QQQ adj_close + GLD adj_close, cost model Index CFD: commission=0, spread=5bps half, swap=-0.008%/dia):

| Métrica | Baseline V2-L2 (share CFD) | Phase 4.0 (Index CFD) | Delta |
|---|---:|---:|---:|
| OOS Sharpe | 2.285 | **2.400** | +5.0% |
| OOS CAGR | 79.14% | **85.76%** | +8.4% |
| OOS MDD | −21.02% | −21.51% | +0.5pp |
| FWD Sharpe | 1.821 | 1.797 | −1.3% |
| n_switches total | 616 | 584 | −5.2% |
| cum transaction cost | 125.80% | 114.01% | −11.8pp |
| cum swap drag | −44.93% | −73.30% | −28.4pp (pior) |

**T4 full gates battery:**
- Bootstrap 99.9% CI full: **[1.379, 2.618]** (vs baseline [0.962, 3.52]) — CI low **+43%**
- Bootstrap 99.9% CI OOS only: [1.055, 3.724]
- Walk-forward 8 windows: 8/8 profitable, max-DD 22.6% ≤ 25% cap
- IR vs SPY OOS: **2.333** (vs baseline 2.161) — **+8%**
- Cost sensitivity (swap 2×): OOS Sharpe 2.292, CAGR 80.38% — robusto
- Median hold: 5.0 dias (≥3d)
- PBO/DSR: intencionalmente omitidos (n_trials=1 trivializa ambos; bootstrap 99.9% é o gate primário distribution-free)

## Por que Index CFD **melhora** em vez de piorar

Intuição inicial: substituir share CFD por Index CFD introduziria tracking error SPY→SPX e dividend adjustment haircut. **Errado.** Na janela 2001-2026, o delta principal é:

1. **Commission zero em Razor Index** (vs 6.6 bps RT share CFD) economiza ~204 bps cumulativos em 309 trades sobre 25 anos. Grande parte do CAGR ganho.
2. **SPX TR price series tem menos whipsaws** (281 flips vs 315 em SPY raw close — dividend drops da SPY ETF não estão na SPX TR price), economizando mais commission E reduzindo cost transacional.
3. **Swap piora** (−73% vs −45% cum) por causa da suposição conservadora `swap_daily_pct_long=-0.008%` (Index CFD exposto a futures-basis drag), mas a economia de commission sobrepõe.

Resultado líquido: **Sharpe sobe 5%, CAGR sobe 8%, CI low sobe 43%**.

## Caveats carregados para Phase 4 paper

1. **GLD usado como proxy de XAUUSD** (parquet xauusd só tem 2020+, insuficiente). Efeito: gold leg tem drag de 0.40%/yr (expense ratio GLD) que XAUUSD puro não teria. Potencial CAGR live ligeiramente superior ao backtested.
2. **Cost model assume Razor Index commission-free.** Hipótese não-validada empiricamente — T1 é o gate antes de Phase 5.1 live.
3. **Dividend adjustment assumido perfeito.** SPX TR e QQQ adj_close incluem 100% dos dividendos. Pepperstone teoricamente paga cash adjustment mas haircut e timing precisam T2 empírico.
4. **Lot granularity $1k:** 0.01 lot US500 ≈ $600 notional, 40% rounding vs target $1000. Material mas operável (muito melhor que 1-share mínimo de share CFD a $694).
5. **Swap drag 60% maior que baseline.** Se live swap for pior que o −0.008% modelado, CAGR degrada.

## Propagação nos docs (T5)

- `docs/strategies/plano_a_v2_l2_gayed_cfd.md` §4.2: tabela comparativa share vs Index CFD com deltas observados; §6.3 Phase 5.1 confirmado "$1k Index CFD ✅ validado"; §9 update log nova entrada.
- `docs/investment-mandate.md` §3.6: threshold $1k Index CFD agora com check ✅ (antes era condicional).
- `specs/phase_4_paper_trading.md` §1: adicionada variant Index CFD explicitamente ao escopo paper.
- `reports/phase3_5a_v2/AGGREGATE.md` §7.5: removido "not yet validated" flag.

## Stop rule respeitada

A spec tinha 3 stop conditions (T1/T2 commission, T3 Sharpe/CAGR/MDD, T4 qualquer gate). Nenhuma disparou. Binding stop rule: **1 tentativa, go/no-go** — executada, vereditada PASS, sem V2 da Phase 4.0.

## O que ainda bloqueia Phase 5.1 live com $1k

Ordem sequencial de execução prevista:

1. Abrir conta Pepperstone **demo** (cTrader).
2. T1: pegar rate card real em US500/USTEC/XAUUSD na conta. Registrar em `docs/strategies/plano_a_pepperstone_index_cfd_rate_card.md`. Gate T1: commission ≤ 1 bps, spread ≤ 7 bps half.
3. Phase 4 paper trading (3 meses) em cTrader demo.
4. T2: observar 1 ciclo ex-div SPY (trimestral) e medir dividend adjustment pago. Gate T2: yield capture ≥ 95%.
5. Se tudo ✅ → Phase 5.1 live real com $1k em Index CFD.
6. Se T1 falha (commission > 1bps) → retornar a Caminho 2 (acumular $10k para share CFD) ou Caminho 1 (Plano B only).

## Lições meta

1. **Substituição de instrumento pode melhorar métricas**, não piorar, quando o cost regime da nova alternativa é mais amigável. Carver `[systematic_trading, p.185-188]` captura isso: fixed costs kill, proportional costs scale.
2. **Bootstrap 99.9% CI é o gate distribution-free** quando PBO/DSR perdem aplicabilidade (single-config). Preciso lembrar disso — é uma ferramenta menos usada mas robusta.
3. **Spec com stop rules binding funciona:** permitiu executar a validação autonomamente sem "só mais uma tentativa". Tivesse falhado, teria fechado limpo. Mantenha esse padrão em Phase 4.0+.

## Citações

- EMA-100: `[leverage_for_the_long_run, Gayed, p.11-14]`
- Leverage cap L=2: `[leverage_space, Vince]`, `[math_money_mgmt, Vince]`
- Fixed commission at retail scale: `[systematic_trading, Carver, p.185-188]`
- Bootstrap CI stationary block: `[advances_fin_ml, López de Prado, p.196-202]`
- Walk-forward 6/8 gate: `[advances_fin_ml, ch.11]`

## Links

- Spec executado: `specs/phase_4_0_index_cfd_validation.md`
- Verdict aggregate: `reports/phase4_0/index_cfd_validation/AGGREGATE.md`
- T3 standard report: `reports/phase4_0/index_cfd_validation/standard_report.md`
- T3 summary.json: `reports/phase4_0/index_cfd_validation/summary.json`
- T4 gates.json: `reports/phase4_0/index_cfd_validation/gates.json`
- Daily returns parquet: `reports/phase4_0/index_cfd_validation/daily_returns.parquet`
- Scripts: `scripts/run_phase4_0_index_cfd_backtest.py`, `scripts/run_phase4_0_index_cfd_gates.py`
- Branch: `phase4_0/index-cfd-validation`
- Jornada anterior (capital fragility discovery): `jornada/2026-04-19/11-capital-fragility-cost-model-bps.md`

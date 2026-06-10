# LRS — Relatório Final do Estudo (Phases 0-10)

> **Status: research-only / ENCERRADO (2026-06-10).** Nada neste relatório
> autoriza deploy, paper-trade ou mudança de mandato. Mandate §1 (maintenance
> mode) inalterado. A suíte de validação foi executada (Phase 8): **0/2
> finalistas passam os 7 gates**; a linha está fechada salvo literatura ou
> regime genuinamente novos. Gerado por `lrs/final_report.py`.

## 1. O estudo em uma página

Pergunta original: *existe estratégia com ETFs alavancados que supere a LRS
200d SMA?* Resposta após 4569 trials pré-registrados em 18 etapas:

- **Sim, em mecanismo:** o ensemble multi-lookback (7A) destravou o gate
  vinculante walk-forward no SPY pela primeira vez (13/17 = 76,5% ≥ 75%)
  `[systematic_trading, p.118-119, p.129-133]`, e o vol-targeting quadrático
  (7D) moveu o QQQ (8/11) `[volatility_trading, p.135, p.138-140]`.
- **Não, em validação:** na suíte completa (Phase 8, `n_trials = 4377` na
  época; ledger final 4569), o SPY ensemble fez 6/7 e morreu no DSR
  por p `0,052` vs `0,05` — com undercount honesto (letf-lab fora do ledger).
  "Quase lá" não passa `[advances_fin_ml, p.273-275]`.
- **Drivers reais** (na ordem em que foram descobertos): geometria de
  exposição (alavancagem-alvo 1.75-2x + risk-off diversificado ZROZ/GLD/IEF +
  throttle de vol) `[leverage_for_the_long_run, p.4-7]`; suavização entre
  janelas (7A); sizing por inverso da variância (7D).
- **O que NÃO funciona** (tudo FAIL honesto): filtros AND (3A), formas de
  regime alternativas (3A-2), janelas/adaptativo (3C), sleeve inversa (6D),
  portfólio EW de rotações (7B), gate macro como switch binário (7C — conserta
  o WF mas explode o MDD), composição de mecanismos (7F), teto 3x cheio (P9) e
  **buy-the-dip alavancado (P10 — zero rows entre 144 seguram MDD ≥ −50%;
  a tese Gayed sobrevive à própria inversão** `[leverage_for_the_long_run,
  p.7-9]`, `[trading_systems_methods, p.13]`).

## 2. Status atual — validação

| Config | G1 PBO | G2 DSR p | G3 WF | G4-G7 | Geral |
|---|---|---|---|---|---|
| `spy_7a_ensemble` | 0,397 ✅ | **0,052 ❌** | 13/17 ✅ | ✅✅✅✅ | **FAIL 6/7** |
| `qqq_7d_quadratic` | 0,651 ❌ | 0,138 ❌ | 8/11 ❌ | ✅✅✅✅ | **FAIL 4/7** |

Veredito da linha: **a geometria de timing alavancado é real — o gate
vinculante foi destravado — mas o edge é pequeno demais para sobreviver ao
accounting honesto de múltiplos testes.** O RSC-US 35/40/25 estático segue
como âncora limpa do repo; a tabela de mix da 6A continua disponível para a
decisão static×satélite `[risk_parity, p.80-81]`, `[advances_fin_ml,
p.208-211]`.

## 3. Finalistas — lente time-weighted e lente de aportes

Time-weighted (after-tax, DARF anual) e money-weighted (aportes de
$10,000 + $1,000/mês na própria curva after-tax; path MDD é
mecanicamente suavizado por inflows — divulgado, precedente 6A Part 2):

| Finalist | Window | CAGR | MDD | Sharpe | Calmar | Terminal vs B&H | hit10y | Turnover/y | IRR (aportes) | Path MDD (aportes) | Terminal (aportes) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| F1 spy_7a_ensemble | 1968-04-02..2026-05-21 | 14.49% | -43.16% | 0.695 | 0.336 | 7.6x | 83% | 13.7 | 15.05% | -43.00% | $329.62M |
| F2 spy_p9_cap2.5x | 1968-04-02..2026-05-21 | 16.81% | -47.47% | 0.675 | 0.354 | 24.3x | 100% | 6.1 | 17.64% | -47.28% | $1051.38M |
| F3 qqq_l2_binary | 1986-01-03..2026-05-21 | 21.11% | -45.93% | 0.724 | 0.460 | 10.1x | 71% | 6.0 | 21.12% | -45.90% | $165.61M |


Benchmarks (mesmas lentes):

| Benchmark | Window | CAGR | MDD | Sharpe | Calmar | IRR (aportes) | Path MDD (aportes) | Terminal (aportes) |
|---|---|---|---|---|---|---|---|---|
| SPY B&H | 1968-04-02..2026-05-21 | 10.56% | -55.14% | 0.670 | 0.192 | 11.14% | -55.04% | $56.98M |
| QQQ B&H | 1986-01-03..2026-05-21 | 14.36% | -82.97% | 0.650 | 0.173 | 14.28% | -82.48% | $21.70M |
| LRS SPY headline (binaria) | 1968-04-02..2026-05-21 | 15.44% | -39.28% | 0.718 | 0.393 | 16.13% | -39.28% | $534.41M |


**Status de cada finalista:** F1 reprovou a suíte (6/7, DSR); F2 e F3 nunca
rodaram a suíte e enfrentariam ledger ≥ 4569 (odds registradas como
baixas — o DSR matou candidato com risco-ajustado melhor). Uso com capital é
decisão pessoal fora do mandate (§7); nenhum é candidato a deploy do repo.

## 4. Fichas operacionais

### F1 `spy_7a_ensemble` — o mais robusto (6/7 gates)

- **Regra semanal (1º pregão):** fração risk-on `f = (nº de SMAs de
  {150,175,200,225} com SPY acima) / 4`, zerada se RV21 > 30% a.a.;
  carteira-alvo = `f` × [25% SPY + 75% SSO] + `(1-f)` × [40% ZROZ + 40% GLD +
  20% IEF]; executar com 2 dias de lag via caixa.
- Posições: SPY/SSO/ZROZ/GLD/IEF + caixa. Turnover ~14/ano.
- Caveat: MDD −43% e ~1pp de CAGR abaixo da headline binária; a vantagem é
  consistência entre janelas (13/17).

### F2 `spy_p9_cap2.5x` — o de maior ganho dentro do teto

- **Regra semanal:** acima da SMA200 do SPY, alavancagem-alvo
  `L = clip((40% / RV21)², 0, 2.5)` quantizada em degraus de 0,25 (inércia:
  só muda se o alvo desviar ≥ 0,25); expressa por mix SPY/SSO/UPRO (a 2,5x =
  50% SSO + 50% UPRO). Abaixo da SMA200: 50% ZROZ + 25% GLD + 25% caixa.
  Lag 3 dias.
- Na prática fica ~99% do tempo risk-on no teto 2,5x (σ40 quase nunca binda):
  comporta-se como "2,5x constante + saída em pânico". Turnover ~6/ano.
- Caveat: nunca validado; o ganho vem da alavancagem, não do sizing.

### F3 `qqq_l2_binary` — melhor Calmar do grid, branch frágil

- **Regra semanal:** QQQ acima da SMA200 E RV63 ≤ 40% → 100% QLD (2x);
  senão → 50% ZROZ + 50% GLD. Lag 1 dia.
- Turnover ~6/ano. Caveat sério: a branch QQQ reprovou PBO
  (0,64) e DSR na Phase 4 — 40 anos dominados pela era tech; o risco de
  overfit é o maior dos três.

## 5. Linha do tempo do estudo (ledger 4569)

| Etapa | Trials | Veredito |
|---|---|---|
| P0 baseline | +0 | diagnostic (24 rows, fora do ledger DSR) |
| P1 risk-off | +0 | driver (264 rows, fora do ledger DSR) |
| P2 geometry | +2400 | driver |
| P3A filters | +324 | FAIL |
| P3A-2 forms | +216 | FAIL |
| P3C lookback | +936 | FAIL |
| P4 gates | +0 | FAIL 0/6 |
| P5 overlay | +0 | FAIL 0/9 (fora do ledger DSR) |
| P6 round | +129 | decision table |
| P7A ensemble | +72 | SPY SUCCESS |
| P7B multi-asset | +72 | FAIL |
| P7C macro GTT | +72 | FAIL (MDD) |
| P7D vol^2 | +72 | QQQ SUCCESS |
| P7E MF risk-off | +60 | weak SPY |
| P7F composition | +24 | FAIL |
| P8 final gates | +0 | FAIL 0/2 |
| P9 3x ceiling | +48 | SPY lead |
| P10 dip ladder | +144 | FAIL 0/2 |


## 6. Plots

| Plot | File |
|---|---|
| equity dd spy | [plots/final_equity_dd_spy.png](plots/final_equity_dd_spy.png) |
| equity dd qqq | [plots/final_equity_dd_qqq.png](plots/final_equity_dd_qqq.png) |
| frontier all trials | [plots/final_frontier_all_trials.png](plots/final_frontier_all_trials.png) |
| wf progress | [plots/final_wf_progress.png](plots/final_wf_progress.png) |
| trial ledger | [plots/final_trial_ledger.png](plots/final_trial_ledger.png) |
| phase8 gates | [plots/final_phase8_gates.png](plots/final_phase8_gates.png) |
| exposure series | [plots/final_exposure_series.png](plots/final_exposure_series.png) |
| rolling 10y | [plots/final_rolling_10y.png](plots/final_rolling_10y.png) |
| decade returns | [plots/final_decade_returns.png](plots/final_decade_returns.png) |
| contribution sim | [plots/final_contribution_sim.png](plots/final_contribution_sim.png) |


## 7. Referências

Fases e memórias: `lrs/phases/phase00_*..phase10_*`, `lrs/MEMORY.md`,
`lrs/CONCLUSION.md` (comparação com RSC), `lrs/NEXT_STEPS.md`. Citações-chave:
`[leverage_for_the_long_run, p.4-9, p.13-16]`, `[systematic_trading,
p.118-133, p.137-148]`, `[volatility_trading, p.135-140]`,
`[trading_systems_methods, p.13, p.383, p.939]`, `[testing_tuning,
p.318-335]`, `[advances_fin_ml, p.208-216, p.273-275]`.

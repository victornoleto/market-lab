# spy_beater_hunt iter 002: rodei sensitivity sweep e descobri que reduzir alavancagem é o único caminho

Iter 002 testou seis variantes do A1 (Gayed LRS UPRO) variando três
"levers" para atacar o gargalo de drawdown:

1. **Velocidade do sinal** (SMA 100, EMA 150, EMA 100) vs SMA 200 base
2. **Threshold band** (hysteresis 2% e 5% em torno da MA)
3. **Alavancagem** (3× UPRO vs 2× SSO)

A intuição era: signal mais rápido sai mais cedo do crash, threshold
reduz whipsaw em mercados de lado, e menos lev cuts MDD por construção.

## O que descobri (contraintuitivo nos primeiros 2 levers)

| config | CAGR | MDD | comentário |
|---|---:|---:|---|
| `a2_sma100_3xupro` | 19.01% | **64.07%** | sinal mais rápido **piorou** MDD |
| `a2_sma200_th2_3xupro` | 21.62% | 57.57% | buffer 2% ≈ neutro |
| `a2_sma200_th5_3xupro` | 19.57% | 65.94% | buffer 5% **piorou** |
| `a2_ema150_th2_3xupro` | 19.55% | **71.69%** | EMA é bem pior |
| **`a2_sma150_2xsso`** | **14.82%** | **43.49%** | **closest a WINNER yet** |
| `a2_ema100_th2_2xsso` | 14.58% | 56.28% | EMA quebra mesmo a 2× |

**Disparei dois KILLs pré-comitados**:

- KILL #7 (signal speed irrelevant): SMA100 MDD 64% > SMA200 50% (pior, não
  melhor). EMA150 MDD 71% (muito pior). Direção "faster signal" CLOSED.
- KILL #8 (buffer doesn't help): th5 piora MDD significativamente; th2 é
  neutro. Direção "anti-whipsaw via threshold band" CLOSED.

**Lower leverage NÃO disparou KILL #9** — pelo contrário: `a2_sma150_2xsso`
ficou com MDD 43.49% (vs 50-65% para todas as 3× configs), CAGR 14.82%
(passa o bar 13.80% por +1.02pp). Gap pra WINNER: apenas **+2.64pp no MDD**.

## Por que faster signal piora drawdown (não melhora)

Hipótese: a 200d SMA é "lenta" mas estável. SMA100 e EMA reagem mais a
ruído — durante períodos voláteis (1987, 2008, 2020, 2022), elas geram
whipsaws onde a estratégia fica oscilando entre on/off, capturando **mais**
da queda em alavancagem do que o gate lento. Os flips frequentes não
protegem; eles amplificam o problema porque cada re-entrada em UPRO
durante mercado bear é um novo decay diário.

A 200d SMA's lag IS its discipline.

## Implicação pro plano

Direção "lower leverage" é o único path que sobrou em Tier 1. Iter 003
deve testar variantes:
- 1.5× via blend (50% SPY + 50% SSO, ou NTSXSIM)
- 2× SSO com janela mais longa (250d, 300d)
- 2× SSO com off-regime alternativa (KMLM, DBMF, TLT)

A questão central: dá pra cortar mais 2.64pp no MDD sem matar o CAGR
14.82%? Talvez 1.5× lev seja o sweet spot.

## Score regression

Iter 001 = PROMISING 67. Iter 002 = PROMISING 63. Caiu 4pts por:
- DSR worst p subiu de 0.026 pra 0.0516 (n_trials cresceu 4 → 10)
- Mean Sharpe ligeiramente pior nas variantes

A penalidade do DSR é o custo de testar mais variantes. Próximos iters
devem usar 4 configs (não 6) pra slow down o n_trials inflation.

## Infraestrutura nova nesta sessão

- `lrs_engine.ema_gate` — variante EMA do Gayed gate
- `lrs_engine.threshold_band_gate` — hysteresis 0/2/5% buffer (SMA ou EMA)
- `plot_helper.py` — overlay equity + drawdown por dataset, CAGR/MDD scatter
  com WINNER zone, gate heatmap. 5 PNGs gerados por iter agora.
- `SESSION_PROMPT.md` — prompt copy-paste pra próximas 48 sessões iterarem
  autonomamente até total 50 ou WINNER.
- 8 novos tests TDD (24 total no `test_studies_spy_beater_hunt.py`).

Citação principal: `[leverage_for_the_long_run, ch.3-4, p.40-60]` validada
(200d SMA é discipline, not bug); prior project archive
`studies/_archive/ema_sma_threshold_nasdaq_real` confirmou padrão
(top-5 deles também tinha buffer 0%, SMA preferida sobre EMA).

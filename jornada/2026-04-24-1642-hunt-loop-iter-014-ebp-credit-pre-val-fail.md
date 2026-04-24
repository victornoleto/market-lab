# 2026-04-24 16h42 — Hunt loop iter 014: EBP credit-cycle overlay rejeitado pelo pre-validation screen, overlay family do iter 008 blend FECHADA [HUNT LOOP]

**Estado:** Modo MAINTENANCE (mandate §1 segue 100% Plano C). Pesquisa em background.

## O que aconteceu

Iteração 14 do strategy hunt loop testou a **Option E** do BASE_MEMORY:
**EBP (Excess Bond Premium, Gilchrist-Zakrajšek 2012)** como overlay
de haircut binário na perna de equity do blend vol-managed iter 008
(`vt15_L21_cap20`, SPY+TLT com variance-scaling).

A hipótese: EBP é o **resíduo** de corporate-bond spreads depois de
remover o componente de default esperado. Teoricamente, ele captura
swings de apetite de risco dos investidores (balanço de bancos,
demanda de seguradoras, estoques de dealers) que são parcialmente
independentes da volatilidade realizada de equity. Fire-episodes
distintos (LTCM 1998, GFC 2008, COVID 2020) são empíricos na
literatura.

Para não repetir os iter 009/012/013 (todos falharam com o mesmo
diagnóstico de "100% overlap com bottom-20% scale"), esta iteração
introduziu uma **metodologia nova e explícita**: **pre-validation
screen** medindo `|ρ(EBP_z_252, σ²_port(blend))| rolling 60 dias`
antes de qualquer backtest. Regra pré-commit: se > 20% dos bars
têm `|ρ| > 0.30` em QUALQUER dataset, a iteração aborta sem gastar
DSR budget.

## Resultado — pre-validation screen FAILS em todos os 3 datasets

| dataset | exceed_frac | max \|ρ\| | mean \|ρ\| |
|---|---|---|---|
| educational (24y) | **68.4%** | 0.958 | 0.469 |
| spy_real (17y) | **69.1%** | 0.958 | 0.472 |
| ndx_real (16y) | **70.6%** | 0.942 | 0.482 |

Todos os 3 datasets excedem o cap de 20% por 3.4×. O |ρ| médio
chega a 0.47 (1.5× do threshold 0.30), com picos de 0.96 em janelas
de stress. **EBP's residual decomposition NÃO é empiricamente
ortogonal a σ²_port no timescale de 60 dias** — o ciclo de crédito
e o ciclo de vol de equity co-movem no período relevante pra um
blend vol-managed daily.

**Kill #PV ativado → iteração abortada antes do backtest.**
`cumulative_n_trials` permanece em 4255. Nenhum DSR budget gasto.
Score 0/100 FAIL.

## Analogia

Imagine que você tem um sensor de chuva (o blend vol-managed) que
automaticamente fecha as janelas quando detecta umidade alta. Você
quer adicionar um segundo sensor — um barômetro — pra antecipar
chuva via queda de pressão. A teoria diz que barômetro e chuva são
sinais diferentes.

Mas aí você descobre que no seu microclima local, pressão e umidade
caminham juntas 70% do tempo. Não dá pra o barômetro te avisar ANTES
do sensor de chuva, porque quando a pressão cai a umidade também já
subiu. O segundo sensor não adiciona antecipação — só confirma o
que o primeiro já sabia.

É isso que 4 iterações consecutivas (009 T10Y3M simétrico, 012
T10Y3M assimétrico, 013 meta-labeling LR, 014 EBP) provaram:
**qualquer sinal "macro/regime" co-move com σ²_port do blend no
timescale de 60 dias**. Não é falha de escolha de parâmetros — é
propriedade do próprio portfólio, que se auto-ajusta no mesmo
gradiente de risco que drive todos esses sinais.

## O que foi documentado

1. **`iterations/014-2026-04-24-1642-ebp-credit-overlay-blend/`** —
   hypothesis.md, ebp_credit_overlay.py, pre_validation.py,
   verdict.json, final_report.md, 9 novos TDD specs
   (`tests/test_ebp_credit_overlay.py`).
2. **Pytest baseline:** 823 → 832 tests collected (sem regressão).
3. **`DEAD_ENDS.md`** — nova seção "From iteration 014", + entrada
   no checklist de categorias estruturais fechadas.
4. **`BASE_MEMORY.md`** — iteração log entry (comprimido 3-line),
   direções promising atualizadas (Option E consumido; G/cross-sec/
   options-skew promoted), pre-validation gate agora mandatory.

## O que vem a seguir

Overlay family no blend iter 008 está **FECHADA**. 4 tentativas
consecutivas com mesmo diagnóstico estrutural. Iter 015 precisa
mudar **mecanismo**, não decorar iter 008 mais uma vez:

- **Primary recommendation: Option G (return-stacked ETF rotation)**
  — NTSX/NTSI/NTSE, primitivo novo (futures-stacking embutido vs
  vol-scaling explícito). Precisa synthetic proxies pra janela 17y.
- **Alternativa: cross-sectional factor momentum** em universo
  heterogêneo (MTUM/QUAL/VLUE/USMV/SIZE/SPMO — não sector ETFs,
  aqueles faliram no iter 003 por homogeneidade).
- **Alternativa: options-implied signal em SPY plain** (não blend,
  sem σ²_port → sem cointegration axis). VIX/VIX3M slope.

**Contribuição metodológica novo de iter 014**: o **pre-validation
screen** agora é mandatory para qualquer overlay/meta-label futuro
em vol-managed blend. Salva DSR budget, aborta cointegração
estrutural em ~2 min em vez de ~30 min de backtest completo.

Mandate §1 não muda: MAINTENANCE 100% Plano C. Mesmo um winner
seria CANDIDATE, não auto-deploy.

## Citações

**Primária:**
- `[adaptive_markets, p.131-132, ch.11]` — credit cycle como eixo
  distinto (countercyclical capital buffers).

**Secundárias:**
- `[risk_parity, p.23-24, ch.2]` — HY bonds co-movem com equity,
  motiva usar o resíduo EBP (não o spread raw).
- `[ml_for_algo_trading, ch.23, p.716]` — priorize hipóteses
  economicamente motivadas.
- `[advances_fin_ml, p.162-164]` — lag rule estendido a macro data.
- `[advances_fin_ml, p.222-223]` — DSR com n_trials cumulativo.

**Paper primário (web):**
- Gilchrist, S. & Zakrajšek, E. (2012), "Credit Spreads and Business
  Cycle Fluctuations", *American Economic Review* 102(4), 1692-1720.
  DOI [10.1257/aer.102.4.1692](https://doi.org/10.1257/aer.102.4.1692).

## Referências do iter

- `studies/strategy_hunt_loop/iterations/014-2026-04-24-1642-ebp-credit-overlay-blend/final_report.md`
- `studies/strategy_hunt_loop/iterations/014-2026-04-24-1642-ebp-credit-overlay-blend/verdict.json`
- `studies/strategy_hunt_loop/iterations/014-2026-04-24-1642-ebp-credit-overlay-blend/pre_validation.json`
- `studies/strategy_hunt_loop/BASE_MEMORY.md` (entry + structural dead-end)
- `studies/strategy_hunt_loop/DEAD_ENDS.md` (new section + category checklist)
- `tests/test_ebp_credit_overlay.py` (9 TDD specs, all pass)

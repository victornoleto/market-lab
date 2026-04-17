# Investment Mandate — ai-trade

> Documento permanente. Define as regras invioláveis que governam toda
> decisão de strategy, sizing, universe e backtest deste projeto. Todo
> spec, iteração do loop auto-dirigido, e PR contra `main` precisa
> estar aderente a este mandate. Rule overrides pelo usuário são
> registrados aqui (não em memória efêmera).
>
> **Sumário operacional sempre carregado via `.claude/CLAUDE.md` §📌 Investment
> Mandate.** Este documento aqui é a rationale completa.

**Revisão:** 2026-04-16 (pós-winners retratados-e-promovidos — BollingerMR
SPY 1h e ETFRotation monthly, CAGR 5.9% e 9.1-9.6% — considerados
insuficientes para justificar o esforço científico vs. CDI BR).

---

## 1. Capital allocation model

O capital total do investidor se divide em 3 compartimentos, cada um
com mandato e risco diferente:

| Compartimento | Alocação alvo | Função | Regras |
|---------------|---------------|--------|--------|
| **Passive buy&hold factor-tilted** | **60-80%** do total | Composição de riqueza de longo prazo (aposentadoria 30a). | Governado por `portfolio-aposentadoria.md` — AVUS/SPMO/AVUV/AVDE/IDMO/AVDV/AVEM + IBIT + GLDM. Sem ação do ai-trade — esse compartimento é "set and forget" com rebalanceamento por aportes. |
| **Strategy A — Short-hold CFD (ativa, agressiva)** | parte do **20-40% ativo** | Motor de retorno não-linear; aceita risco alto em troca de alpha mensurável. | Pepperstone via cTrader Open API. Multi-asset obrigatório. Alavancagem otimizada por sweep. Gates completos (PBO/DSR/WF + OOS + stress). |
| **Strategy B — Swing broker (ativa, moderada)** | parte do **20-40% ativo** | Alpha via regime rotation. Tese principal hoje: LETF rotation (UPRO/CASH). | Corretora BR internacional (Inter/XP/Avenue). 15% IR modelado sempre. Overfit control via CPCV obrigatório. |

A proporção exata entre A e B dentro dos 20-40% ativo é decisão do
usuário em função da performance histórica das duas strategies. Default
inicial sugerido: **50/50 entre A e B**, re-ponderado após 6 meses de
paper trading por Sharpe net realizado.

---

## 2. Performance targets e mínimos aceitáveis

### Benchmark obrigatório

**CDI Brasil ~13-14%/ano líquido** é o chão absoluto para qualquer
strategy ativa deste projeto. Uma strategy que rende 6% CAGR com
MaxDD -13% (como o BollingerMR SPY 1h encontrado em 2026-04-16) **não
é um winner** — é pior que Tesouro Selic sem risco. Fica registrada
como histórico de pesquisa, não como produto.

### Targets por strategy

- **Strategy A (Path A CFD):** **5-10%/mês líquido** (equivalente CAGR
  60-120%), partindo de $1k de capital inicial. Razão: motor agressivo
  alavancado faz sentido matemático com target assim; 20-30% ao ano
  não justifica risk-of-ruin de CFD alavancado.
- **Strategy B (Path B swing):** **CAGR líquido ≥ 15%/ano** após 15%
  IR, ideal ≥ 20%. Razão: precisa bater o compartimento passive
  (AVUS+SPMO+AVUV ~11-13% esperado líquido de IR) por margem não-
  trivial, senão a complexidade adicional não paga.

### Gates obrigatórios (sem exceção)

Toda strategy candidata passa por:

1. **PBO < 0.5** — `[advances_fin_ml, p.208-211]`
2. **DSR p-value < 0.05** — `[advances_fin_ml, p.196-202]`
3. **Walk-forward ≥ 6/8 janelas positivas** com MaxDD ≤ 25% — `[testing_tuning]`
4. **Single-block OOS hold-out** (última fatia de 6-12 meses) positivo.
5. **Forward-window stress** (última fatia de 3 meses recentes) positivo.

Violação de qualquer gate = strategy não existe. Sem "mas no IS era
bom", sem "com um param a mais", sem "só falhou em 1 ano". Zero
bypass.

### Overfit control em otimização

Qualquer param grid implica CPCV + PBO. Encontrar params por tentativa-
e-erro num backtester externo (ex.: testfol.io) é **ponto de partida**,
nunca "winner final". Os params encontrados pelo usuário em estudos
externos (ex.: SPY EMA 125, band 5% — ver `docs/reference/letf_rotation_reddit_analysis.md`
quando colado) entram como **seed lead** para a lead B1, que então
submete os params ao CPCV+PBO rigoroso antes de virar strategy.

---

## 3. Regras de Strategy A — Short-hold CFD Pepperstone

### 3.1 Multi-asset obrigatório

**A partir de 2026-04-16, strategy A **não aceita** single-asset edges
como winner final.** O BollingerMR SPY-only é contraexemplo: passou
todos os gates mas a tese técnica ("edge existe em SPY-ETF por função
de benchmark/creation-redemption") não escala para outros ativos
testados (13 ETFs, todos FAIL). Isso aumenta risco idiossincrático
concentração demais.

**Universo permitido (core):**
- **Índices:** SPY / SPX500, QQQ / NAS100
- **Commodities:** GLD / XAUUSD (gold)
- **Crypto:** BTCUSD, ETHUSD
- **Forex majors:** EURUSD, GBPUSD, USDJPY, AUDUSD

Todos CFDs disponíveis em Pepperstone Razor. Spreads e swaps reais
modelados no backtest pré-promoção a live.

### 3.2 Universe pre-screening

Antes do backtest da strategy, um **screener de universo** filtra quais
dos ativos permitidos estão em regime "propício" naquela janela. Sem
pre-screening, a strategy trade em ativos com estrutura errada (ex.:
BollingerMR em commodity em mean-revertion ativa vs BollingerMR em
crypto em trending régime dá alpha negativo consistente).

Heurísticas candidatas (a validar empiricamente):
- **Hurst exponent** < 0.5 → mean-reverting; > 0.5 → trending
- **ATR / price ratio** em faixa apropriada à strategy (MR prefere
  volatilidade moderada; breakout prefere volatility expansion)
- **Bid-ask spread proxy** (high-low range relativo) → filtra liquidez
- **Volume stability** (rolling std do volume normalizado)

A implementação concreta é responsabilidade do **Phase 3 Lead A2**.

### 3.3 Alavancagem — sweep obrigatório 1:1 → 1:200

Pepperstone limits (para cliente retail não-professional, varia por
regulador ASIC/FCA/CySEC):
- **Índices:** 1:20 (SPX500, NAS100, DE40, etc.)
- **Commodities:** 1:20 (XAUUSD spot), 1:10 (crude oil)
- **Forex majors:** 1:30 (EUR/USD, GBP/USD, etc.)
- **Forex exotic:** 1:20
- **Crypto:** 1:2 a 1:10 (varia bastante por cripto e regulador)

Lead A1 executa **sweep empírico** de alavancagem com os seguintes
output metrics:
- MAR ratio (CAGR/|MaxDD|) net de custos
- Prob-of-ruin via Monte Carlo (bootstrap 10k paths; ruin = equity < 20% inicial)
- CAGR target achievement (5-10%/mês)
- Sharpe/Sortino net

Critério de ótimo: **max MAR subject to prob-of-ruin ≤ 5% em 12 meses.**

Cross-check teórico: **Kelly fracionado (f/2)** calculado sobre
distribuição empírica de trade returns per-asset. Quando sweep
empírico e f/2 divergem, usar o mais conservador (menor leverage).

**Citações obrigatórias:** `[math_money_mgmt, Vince]` (Kelly + optimal
f), `[leverage_space, Vince]` (drawdown tolerance), `[leverage_for_the_long_run, Gayed, p.7]`
(volatility-vs-leverage regime dependency).

### 3.4 Threading model (Phase 4 live/paper)

Arquitetura de produção: **1 thread/processo por ativo monitorado,
state isolado, mesma strategy core com "perks" opcionais por-ativo.**

Exemplos de perks válidos (cada um motivado por propriedade do ativo,
não ad-hoc):
- **FX**: filtro de sessão ativa (evitar Asian session para majors)
- **Equity index**: filtro de pre-market/post-market do underlying
- **Crypto**: opera 24/7, sem filtro de sessão mas com spread dinâmico
- **Gold**: filtro de news-heavy (FOMC, CPI days)

Cada perk é uma flag documentada no config da instância; cada ativo
mantém apenas os perks que fazem sentido pra sua microestrutura.

Backtest em Phase 3 precisa ser **state-isolated por ativo** (já é,
em larga medida, pelo BacktestRunner atual), preparando a transição
para multi-process em Phase 4.

### 3.5 Dynamic sizing

Position size decresce com o crescimento do equity. Dois regimes:

- **Fase agressiva** (equity < 2× equity inicial, ex.: $1k → $2k):
  sizing máximo permitido pelo risk_pct/Kelly f/2.
- **Fase preservação** (equity ≥ 2× equity inicial): sizing escalonado
  **linearmente para baixo** com multiplicador = max(0.4, 1/(equity/initial)).
  Preserva ganhos; evita que uma sequência ruim pós-big-win derreta o
  account.

**Rationale:** utilidade log-wealth (Kelly) assume reinvestimento
integral; na prática, o usuário "colhe" parte do ganho conforme
equity cresce, reduzindo fração do at-risk. Formalizado como
multiplicador explícito em código. Citar `[math_money_mgmt, Vince]`.

---

## 4. Regras de Strategy B — Swing broker

### 4.1 Tese primária: LETF rotation

Strategy B hoje tem **uma tese principal**: rotação entre LETF (UPRO
3x SPY ou similar) e CASH, governada por um regime signal sobre o
underlying (SPY).

Fonte intelectual principal:
`books/summaries/leverage_for_the_long_run.md` — Michael Gayed 2016/2020.
Insights-chave:
- Volatility é o inimigo da alavancagem; **MAs são filtros de regime
  de volatilidade** (não de return boost) [p.7-8].
- LRS (Leverage Rotation Strategy): SPY close above SMA(200) → UPRO;
  abaixo → T-bills/cash [p.13, p.21].
- Todas MA periods 10d-200d robustas; 200d recomendada por turnover
  mínimo (~5 trades/ano) [p.16].
- Empirical LRS 1928-2020: 3x LRS → 26.7% CAGR, 37.3% vol, Sharpe
  0.61, MaxDD -92.2% [p.17, Table 8].
- UPRO real (2009-2020) vs. teórico: ~2% drag anual por tracking
  error [p.21].

### 4.2 Parâmetros seed vs. otimização rigorosa

O usuário tem análise prévia em testfol.io que indicou **SPY EMA 125
com banda 5%** como "melhor" via tentativa-e-erro, CAGR 16.74% vs.
SPY 10.63% (1967-2026). Esses params entram como **seed** para a
Lead B1, **não como winner**.

Lead B1 submete o parameter space {MA_type, MA_period, band_pct}
completo ao CPCV + PBO. Se PBO > 0.5, pivot para param space
menor (ex.: SMA only, band 0%) e re-teste. Qualquer param escolhido
por "visualmente bonito" é rejeitado até passar PBO.

Citações externas ao livro (próprios estudos do usuário):
- `docs/reference/letf_rotation_testfol_payload.json` — config exata
  do testfol.io que originou os params seed (stripado de auth token).
- `docs/reference/letf_rotation_reddit_analysis.md` — análise do
  usuário publicada no Reddit (/r/LETFs). **WebFetch falhou com Reddit
  — usuário precisa colar conteúdo manualmente**.

### 4.3 Tax modeling obrigatório

**15% IR é aplicado a cada saída de posição vencedora.** A tax incide
sobre o lucro bruto do trade no mês em que o trade é fechado (regime
capital gains Brazil, operações não-day-trade em instrumentos
estrangeiros).

Net Sharpe e net CAGR são sempre computados **após** esse haircut.
Qualquer strategy Path B reportada sem o haircut é defeituosa e
retorna ao backlog.

Nota operacional: o usuário deve validar com contador o tratamento
exato para ETFs americanos via corretora BR internacional — pode
haver regime distinto por BDR vs. ETF americano direto.

### 4.4 UPRO proxy pre-2009

UPRO foi lançado em 2009. Para backtest 1967-2026 (que foi o range do
estudo pessoal do usuário), UPRO precisa ser **sintético** antes de
2009:

```
r_UPRO_synth[t] = L * r_SPX_TR[t] - (expense_ratio_daily + borrow_cost_daily)
```

onde L=3, expense_ratio ~0.92% ao ano, borrow_cost/drag ~0.87% ao
ano (valor usado pelo testfol.io; validar em
`leverage_for_the_long_run.md`). Daily rebalancing implícito
conforme `[leverage_for_the_long_run, p.16, footnote 22-23]`.

Após 2009, usar UPRO real (Tiingo ou Yahoo). O split a 2009 fica
documentado no código da strategy, não escondido em constant.

### 4.5 Universo permitido (Path B)

- **LETFs primários:** UPRO (3x SPX), SSO (2x SPX), TQQQ (3x NAS),
  QLD (2x NAS)
- **Safe haven rotation target:** CASH ou SHV (short treasury)
- **Não permitidos neste compartimento:** ativos alavancados crypto
  (BITU, BITX — histórico curto; vai pro path A), 3x emerging markets
  (EDC — liquidez inadequada).

Acesso via corretora BR internacional (Inter, XP Internacional, Avenue,
Nomad). Se liquidez BDR de UPRO/TQQQ for adequada no volume alvo,
alternativa aceita; senão, conta internacional é mandatory.

---

## 5. Anti-patterns registrados (o que NÃO fazer)

Decisões tomadas que NÃO podem ser revertidas sem discussão explícita:

1. **Single-asset edges como winners finais de Strategy A.** OK como
   sinal inicial; não OK como produto. Se só funciona em 1 ticker,
   é ruído.
2. **Strategy B = buy&hold não-alavancado.** Se a tese "só" é buy&hold,
   isso já está em `portfolio-aposentadoria.md` — strategy B precisa
   gerar alpha marginal via regime-switch ou alavancagem.
3. **CAGR < CDI BR como "winner".** Se retorno líquido não bate CDI,
   a strategy é folclore, não produto.
4. **Gate bypass por "quase lá".** PBO 0.51 não é PBO 0.49. WF 5/8 não
   é WF 6/8. Não se arredonda o gate pra cima; re-trabalha o design.
5. **Alavancagem sem prob-of-ruin.** Nunca. Sempre sweep + Monte Carlo.
6. **Retroajuste de params pós-OOS.** Se OOS falhou, strategy é re-
   desenhada do zero, não tunada pra "passar OOS".
7. **Commit de credenciais, tokens ou auth headers.** Qualquer Bearer,
   API key ou cookie entra em `.gitignore` antes de qualquer write.
   cURLs capturados de serviços pagos (testfol.io, Tiingo) são
   sempre stripados antes de virar reference doc.

---

## 6. Referências (fontes permanentes)

- `portfolio-aposentadoria.md` — compartimento passivo (60-80%).
- `books/summaries/leverage_for_the_long_run.md` — tese LETF rotation
  (Strategy B).
- `books/summaries/math_money_mgmt.md` — Kelly, optimal f, sizing.
- `books/summaries/leverage_space.md` — drawdown tolerance, ruin.
- `books/summaries/machine_trading.md` — BollingerMR canonical
  (Strategy A seed).
- `books/summaries/stocks_on_the_move.md` — ETFRotation canonical
  (Strategy B winner atual).
- `books/summaries/advances_fin_ml.md` — PBO/DSR/CPCV (gate framework).
- `docs/reference/letf_rotation_testfol_payload.json` — config
  testfol.io que gerou os seed params para Lead B1.
- `docs/reference/letf_rotation_reddit_analysis.md` — análise pessoal
  do usuário no Reddit (/r/LETFs). **Preenchimento pendente** —
  WebFetch do Reddit falhou em 2026-04-16, usuário cola manualmente.
- `ROADMAP.md` §"Phase 3" — leads ativos derivados deste mandate.
- `specs/post-winners-cleanup.md` §8 — Phase 3 leads A1-A3, B1-B2.

---

## 7. Histórico de overrides e esclarecimentos

Registro de mudanças/esclarecimentos explícitos do usuário. Toda
mudança substantiva deste mandate é registrada aqui antes de
propagar para CLAUDE.md.

| Data | Mudança | Razão | Commit |
|------|---------|-------|--------|
| 2026-04-16 | Mandate criado | Insatisfação com CAGR dos 2 winners (5.9% + 9.5%) vs CDI BR (~13-14%); definição de compartimentos 60-80% / 20-40% ativo; target Strategy A = 5-10%/mês; multi-asset obrigatório; LETF rotation como tese primária Strategy B. | TBD (docs/mandate) |

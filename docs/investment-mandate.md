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
| **Strategy B — Swing broker (ativa, moderada)** | parte do **20-40% ativo** | Alpha via regime rotation. Tese principal hoje: LETF rotation (UPRO/CASH). | **Banco Inter Internacional** (Inter&Co Securities, FINRA + Apex Clearing) — decisão 2026-04-18, ver §4.6. Acesso direto NYSE/NASDAQ. 15% IR modelado sempre. Overfit control via CPCV obrigatório. |

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

### 3.6 Capital mínimo viável por strategy (cost model floor)

Descoberto em 2026-04-19 durante revisão Phase 4 pre-launch: **o cost
model bps do backtest degrada catastroficamente abaixo de certo
threshold de notional**, porque Razor tier cobra commission **fixa em
dólares** ($3.50/side), não em bps. Quando notional por trade cai abaixo
de ~$5-10k, a commission real como % do notional explode (70 bps a
$1k vs 6.6 bps modelados), e o backtest perde validade.

Threshold operacional por strategy:

| Strategy | Instrumento | Capital mínimo | Razão |
|---|---|---:|---|
| **Plano A (share CFD)** | SPY/QQQ/GLD share CFDs | **$5.000** | Commission fixa $7 RT = 14 bps a $5k (ainda 2× modelo, aceitável); abaixo disso, CAGR vira negativa |
| **Plano A (Index CFD)** | US500/NAS100/XAUUSD | **$5.000** (lot-granularity-bound). Phase 4.0 backtest T3+T4: 10/10 gates PASS. T1 empirical 2026-04-20 via Open API: commission-zero ✅ confirmado, mas lot minimums reais (US500 $600, NAS100 $2k, XAUUSD $2.7k) inviabilizam $1k target. T2 dividend pendente. | T1 rate card: `docs/strategies/plano_a_pepperstone_index_cfd_rate_card.md`. |
| **Plano B (LETF BR)** | SSO/QLD/UGL via Inter Global | **sem mínimo** | Zero corretagem Inter; expense ratio LETF embutido (0.95%/yr); 15% IR só sobre ganho realizado |

Implicações:
- Spec Phase 4 usa $10k paper trading como baseline seguro acima de
  qualquer threshold (independente de share vs Index CFD choice).
- Phase 5.1 live pequeno foi corrigida de "$1.000 real" incondicional
  para "$5.000 share CFD / $1.000 Index CFD se validado". Ver
  `docs/strategies/plano_a_v2_l2_gayed_cfd.md §6.3`.
- Allocation mandate §1 (20-40% active bucket) só se aplica com total
  account ≥ threshold da strategy escolhida. Para usuário com $1k total:
  100% em Plano B ou C (não Plano A share CFD).

Citação: `[systematic_trading, Carver, p.185-188]` — "Fixed commission
dominates at retail scale."

---

## 4. Regras de Strategy B — Swing broker

### 4.1 Tese primária: LETF rotation (família, não config específica)

**Strategy B é a segunda strategy do projeto — complemento swing ao
motor agressivo de Strategy A.** Não precisa ser tão agressiva; precisa
ser cientificamente sólida e simples de operar.

A tese atual é **regime-rotation com LETF**: alocar em ETF alavancado
(UPRO 3x ou SSO 2x sobre SPY/SPX) quando um filtro de regime de
volatilidade sinaliza "on", e rotacionar pra CASH (e/ou gold) quando
sinaliza "off". A definição concreta do filtro (qual MA, qual band,
qual leverage, qual gold_alloc) **é output do Lead B1**, não input.

Fonte intelectual primária e **única** aceita como base científica:
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

**Status do estudo pessoal do usuário (Reddit /r/LETFs):** o usuário
declarou explicitamente (2026-04-16 21:50) que seu estudo no testfol.io
é **trial-and-error, não ciência**. A análise foi feita meses atrás
sem base em livro científico, apenas intuição. Isso NÃO desqualifica
a tese regime-rotation-LETF (que é bem suportada por Gayed), mas
DESQUALIFICA os params específicos como "verdade a reproduzir".

Portanto:

- **Params do Reddit são um seed-point entre vários.** Não têm
  prioridade sobre os params que Gayed defende (SMA 200, sem band,
  sem gold).
- **Winner do Lead B1 pode ser bem diferente do Reddit.** Se o grid
  rigoroso favorecer SMA 200 0% Lev 2x Cash 100% (Gayed canonical),
  esse é o winner — não o EMA 125 5% Lev 3x Gold 0% do usuário.
- **O objetivo é "uma strategy simples e eficaz da família LETF
  rotation"**, não "validar a config do Reddit".

**Seed points válidos (ordem de prioridade):**

1. **Gayed canonical** `[leverage_for_the_long_run, p.13, p.17]`:
   SMA 200 | sem band | Lev 2x ou 3x | Cash 100% (risk-off) —
   documentado academicamente.
2. **Reddit EMA-based** (usuário, ilustrativo): EMA 125 | band 5% |
   Lev 2x-3x | Gold 0-100% — trial-and-error, a validar ou refutar.

A regra do Reddit tem uma decisão operacional interessante (banda
simétrica evita whipsaw; ~5 trades/ano), mas a justificativa é pós-hoc
(o user achou por tentativa). Gayed não usa band — aceita o ruído de
~5 rotations/year em 200-day SMA como já suficientemente low-turnover.
O Lead B1 testa as duas abordagens; se band=5% passar rigorosamente os
gates adicionais sobre a base SMA-sem-band, aí sim vira feature
defensável.

**Se o usuário quiser a regra de banda operacional** (confirmada em
comments do Reddit):
- `preço > MA × (1 + band)` → entrar/manter leveraged.
- `preço < MA × (1 - band)` → sair para cash ou gold.
- Re-entry em `MA × (1 + band)` (assimétrico — evita whipsaw).

O parameter space a submeter ao CPCV + PBO:

| Parâmetro | Valores a testar |
|-----------|------------------|
| `ma_type` | {EMA, SMA} |
| `ma_period` | {100, 125, 150, 200} |
| `band_pct` | {0.0, 0.03, 0.05} |
| `leverage` | {1, 2, 3} |
| `gold_alloc` | {0.00, 0.25, 0.50, 0.75, 1.00} |

Grid total = 2 × 4 × 3 × 3 × 5 = **360 configs**. PBO ≥ 0.5 bloqueia
promoção a winner — nesse caso, reduzir grid para `band ∈ {0.03,0.05}`
+ `ma_period ∈ {125, 150}` (parameter space estreito pré-especificado
antes de rodar) e re-testar.

**Splits temporais obrigatórios (crítica da Destrolas no post):**
- IS: 1970-2000 (30y)
- OOS: 2001-2015 (15y) — mutuamente exclusivo, não overlap
- Stress: 2016-2026 (10y recente)

Se IS vencer em ranking e OOS mantiver top-20%, promove; senão,
descarta independentemente do IS performance.

**Bootstrap para CI (crítica da ChemicalStats):** stationary block
bootstrap (Politis-Romano block size auto) para CI do Sharpe do winner
a nível 0.001. Substitui a metodologia overlapping do testfol.io.

Referências externas (arquivos committed):
- `docs/reference/letf_rotation_reddit_post.pdf` — print do post
  original (24pp, Shift+P do navegador em 2026-04-16).
- `docs/reference/letf_rotation_reddit_analysis.md` — summary do post
  com tabelas, stats da config chosen, críticas e resposta do user.
- `docs/reference/testfolio_letf_spy_ema_125_response.json` — payload
  12MB da resposta testfol.io pra config chosen `SPY EMA 125 5% | Lev 3x | Gold 0%`
  (cashflow + equity curve + stats, 1968-2026).
- `docs/reference/letf_rotation_testfol_payload.json` — config de
  request exata (sem Bearer token), pra reprodutibilidade.

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

### 4.4 UPRO/SSO proxy pre-2009/2006

UPRO (ProShares 3x SPX) lançou em 2009; SSO (2x SPX) em 2006. Para
backtest 1970-2026 precisa ser **sintético** antes dessas datas:

```
r_LETF_synth[t] = L × r_SPX_TR[t] − expense_daily − borrow_daily
```

onde:
- L ∈ {2, 3} conforme leverage target.
- `expense_daily = 0.92% / 252` (UPRO expense ratio típico);
  SSO usa ~0.89%.
- `borrow_daily = 0.87% / 252` (valor observado pelo testfol.io no
  `drag` = 0.87 do payload chosen config). Validar em
  `leverage_for_the_long_run.md [p.16, footnote 22-23]`.

Post-2009 (3x) / post-2006 (2x), usar o real UPRO/SSO (Tiingo daily).
O split temporal fica documentado no código da strategy, não escondido
em constant. Diff entre synth vs real deve ser ≤ 0.5% CAGR no overlap
2009-2020 (ver tabela de tracking error em
`leverage_for_the_long_run.md [p.21, Table 12]`).

### 4.5 Universo permitido (Path B)

- **LETFs primários:** UPRO (3x SPX), SSO (2x SPX), TQQQ (3x NAS),
  QLD (2x NAS), SPXL (3x SPX) — equivalente a UPRO em Pepperstone/
  corretoras.
- **Safe haven rotation target:** CASH (MMF ou SHV short treasury) ou
  GLD (gold allocation configurável 0-100% via `gold_alloc` param).
- **Não permitidos neste compartimento:** ativos alavancados crypto
  (BITU, BITX — histórico curto; vai pro path A), 3x emerging markets
  (EDC — liquidez inadequada), TMF (3x long bonds) — user sinalizou
  "catastrophe" nos comments do Reddit.

Acesso via corretora BR internacional (Inter, XP Internacional, Avenue,
Nomad). Se liquidez BDR de UPRO/TQQQ for adequada no volume alvo,
alternativa aceita; senão, conta internacional é mandatory.

### 4.6 Broker Strategy B — Banco Inter Internacional (locked 2026-04-18)

Broker escolhido e **imutável sem discussão explícita**:
**Banco Inter — Global Account + Inter&Co Securities** (corretora
FINRA-regulated desde 2023-05, custódia via Apex Clearing). Acesso
direto a NYSE/NASDAQ (~8.000 tickers), não via BDR.

#### 4.7.1 Economia operacional (tabela Inter 2025-2026)

| Item | Valor | Nota |
|------|-------|------|
| Corretagem compra/venda ETFs/ações US | **USD 0,00** | Zero, SEC/TAF absorvidos |
| Manutenção/custódia Global Account | **USD 0,00** | — |
| Inatividade | **USD 0,00** | — |
| Spread cambial BRL↔USD | **1,50%** (Digital) / 1,25% (Black) / 0,99% (Win) | Dinâmico sobre PTAX |
| IOF remessa outbound (investimento) | **3,50%** | Decreto 05/2025, unificado |
| IOF retorno | 0,38% | — |
| Settlement ETFs US | **T+1** | SEC industry standard desde 2024-05-28 |
| Horário pregão | 10h30-17h Brasília (std) / 11h30-18h (DST) | Pre/after-market N/A |
| Mínimo abertura | USD 1 | Cartão USD 20 |
| Fractional shares | Disponíveis em tickers selecionados | Útil pra GLD (caro) |

#### 4.7.2 Tributação (residente BR — Lei 14.754/2023)

- **IR 15% flat sobre ganho de capital** em ETFs estrangeiros via
  **DARF código 6015** (ganho de capital moeda estrangeira). Apurado
  e recolhido pelo investidor até último dia útil do mês seguinte
  à venda.
- **Isenção R$35k/mês NÃO se aplica** — é exclusiva de ações na B3.
- Inter fornece "Informe de Rendimentos Global Account" mas com
  histórico documentado de atrasos/indisponibilidade (safra IR 2026).
  **Responsabilidade do investidor:** manter planilha própria com
  custo médio em USD e cotação PTAX do dia da operação.

#### 4.7.3 Catálogo — status dos ETFs-chave do Plano B

| Ticker | Status | Nota |
|--------|--------|------|
| QQQ (Invesco) | ✅ Confirmado | Alta liquidez, catálogo padrão |
| GLD (SPDR Gold) | ✅ Confirmado | Alta liquidez, catálogo padrão |
| **SSO (ProShares Ultra S&P 500 2x)** | ✅ **Confirmado** (usuário validou 2026-04-18) | Bloqueador pré-deploy removido. FINRA Rule 2360+ suitability check passou. |
| UPRO (ProShares UltraPro 3x) | ⚠️ mesma situação | Fallback se SSO bloqueado — mas L=3x não é winner Phase 3.5b |
| SPUU (Direxion Daily S&P500 2x) | ⚠️ mesma situação | Equivalente funcional ao SSO |

**✅ BLOQUEADOR REMOVIDO (2026-04-18):** usuário confirmou que Inter
libera SSO na sua conta. FINRA Rule 2360+ suitability check passou.
Deploy autorizado. Runbook consolidado em
[`reports/phase3_5b/PRODUCTION.md`](../reports/phase3_5b/PRODUCTION.md).

Rotas de contingência mantidas documentadas (caso Inter remova SSO
do catálogo futuramente): (a) Avenue (USD 2,50/ordem); (b) IBKR BR;
(c) reconfigurar Plano B para 2-leg LETF+QQQ sem a perna leveraged
(degrada Sharpe pra 1.888).

#### 4.7.4 Fragilidades operacionais documentadas (reviews 2025-2026)

- Informe de rendimentos Global Account 2025 atrasou/não saiu a
  tempo da safra IR 2026.
- Dividendos de ETFs internacionais com casos de não-creditamento.
- Atendimento robotizado, sem chat humano para conta internacional
  (tempo médio de resposta ~8 dias).

Implicação para a estratégia: **manter planilha própria de cost
basis**, não confiar exclusivamente no informe Inter. Dividendos
aplicáveis à Phase 3.5b são marginais (ETFs selecionados não pagam
ou pagam pouco), mas monitorar mensalmente.

#### 4.7.5 Por que Inter vs alternativas (comparativo resumido)

| Broker | Corretagem ETF US | Spread FX | Settlement | SSO disponível | IOF | Veredito |
|--------|-------------------|-----------|------------|----------------|-----|----------|
| **Inter Global** | USD 0,00 | 0.99-1.50% | T+1 | ⚠️ confirmar | 3.50% | **Mais barato all-in se SSO liberado** |
| Avenue | USD 2.50/ordem após 3/mês | ~1% | T+1 | ✅ catálogo amplo | 3.50% | Fallback se Inter bloquear SSO |
| XP Internacional | USD 0.00 (só premium) | variável | T+1 | Suitability check | 3.50% | Mais caro que Inter, paridade com Avenue |
| IBKR BR | USD 0.005/share (min 1) | ~0.2% spot rate | T+1 | ✅ | 3.50% | Melhor FX, requer mais cliques |
| Nomad | USD 0.00 | 1.50-2.50% | T+1 | Catálogo restrito | 3.50% | Menos ETFs alavancados |

**Rationale:** com rebalance threshold 5-10pp (~1-2 eventos/ano no
rebal layer, ~12 inside-leg/ano), Inter é a corretora **mais barata**
do mercado BR pra este uso-caso se SSO estiver liberado. A diferença
de spread FX Avenue/Inter é trivial num volume pequeno ($3k-$5k
inicial em Plano B); o custo de corretagem Avenue USD 2,50/ordem
anual (~30 ordens × $2,50 = $75) supera o diferencial FX.

### 4.7 Capital allocation dentro do bucket ativo

Dentro dos 20-40% de capital ativo (Path A + Path B), o usuário
sinalizou no Reddit que ~**25% do capital total** vai pra LETF
rotation. Default calibration assumindo 30% ativo total:

- ~25 pts → Path B LETF rotation (esta seção)
- ~5 pts → Path A Pepperstone CFD (Strategy A)

Se Strategy A não produzir winner em Phase 3, re-alocar os 5 pts de
volta para o bucket passive (total ativo cai para 25 pts).

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
| 2026-04-18 | Broker Strategy B locked: **Banco Inter Internacional** (§4.6) | Usuário selecionou Inter Global Account após Phase 3.5b conclusão. Motivações: zero corretagem ETFs US + spread FX 1.50% competitivo + T+1 settlement + plataforma FINRA-regulated. T+N invalida "daily rebalance" — threshold 5-10pp é default operacional pós-Phase 3.5b Task C4. | TBD |
| 2026-04-18 | SSO availability confirmado no Inter (§4.6.3) | Usuário validou diretamente com Inter. Bloqueador pré-deploy removido. Runbook consolidado em `reports/phase3_5b/PRODUCTION.md`. Plano B autorizado para deploy (aguarda Phase 4 infra). | TBD |
| 2026-04-18 | **Phase 3.5a V1 encerrada sem winner novo.** (NOTA: esta entry foi escrita pelo T6 autônomo chamando V1 de "V2" — incorreto; V2 está em execução separada.) Ceiling empírico Plano A = BollingerMR_GARCH SPY 1h L=2 CAGR 5.9%/yr net. 143 runs em 6 famílias × universe Tiingo IEX 1h (12 FX/metals + 5 equity + 1 gold) produziram **0 winners novos**. Duas opções pivot registradas em jornada T6. Decisão final delegada ao Lead T7 + user. | Razor spread 5–7 bps × 200–500 trades/yr > edge MR/breakout/pair/session 1h. Universe Pepperstone index-CFD não-servido por Tiingo. Target §2 Plano A (5–10%/mês) e hierarquia §1 pressupunham universe + granularidade que Tiingo 1h não fornece. | iter 41 phase3.5a branch |
| 2026-04-18 | **Phase 3.5a-V2 launched** (último test Plano A com framework corrigido) | User rejeitou framing "V1=V2" do T6/T7 autônomo. V2 real corrige todos os erros estruturais identificados no post-mortem: timeframe livre (não 1h), hold ≥3 dias (não ≤5d — inverte intuição swap), universe ≥30 multi-asset CFDs (não 12 FX), cost model spread+commission-dominant (não swap-focused), CAGR target 30%/yr realista (não 60-120%), 6 famílias novas (TSMOM, Gayed-transport, AFML meta-label, Carver RP, equity pairs, vol breakout). Spec autoritativo: `specs/phase_3_5a_v2.md`. **Binding stop rule: se V2 produzir 0 PASS, Plano A abandonado permanentemente (sem V3).** User memory: `project_plano_a_v2_last_attempt.md`. Ratificação: se winner → paper trading dual (A+B); se abandon → Phase 4 Plano B puro + §4.7 re-alocação 5pp Path A → Path B. | V1 testou framework errado; V2 corrige antes de ratificar abandono. Última tentativa antes de foco exclusivo Plano B. | iter 0 phase3.5a-v2 branch |
| 2026-04-19 | **Phase 3.5a-V2 ENCERRADA — WINNER FOUND.** 82 iters / 58 runs em 6 famílias produziram **1 gate-passing winner**: `gayed_ema100_L2_off_gld` (Gayed LETF rotation `[leverage_for_the_long_run]` transportada para CFD Pepperstone: SPY+QQQ risk-on, GLD risk-off, leverage 2×). OOS Sharpe **2.285** / CAGR líquido **79.14%** / MaxDD **−21.02%** / median hold 6d / IR vs SPY 2.161. 13/13 gates V2 pass (PBO 0.103, DSR p 0.000288, WF 8/8 @ DD 22.7%, boot99.9 CI low 0.962, FWD Sharpe 1.821). Leads L1 TSMOM / L3 AFML meta / L4 Carver RP blend / L5 Kalman pairs / L6 vol-breakout todos DEAD com diagnóstico estrutural (ver `reports/phase3_5a_v2/AGGREGATE.md`). **Binding stop rule NÃO dispara** (1 PASS ≥ 1 requerido). Plano A RETIDO como 2ª perna ativa mandate §1. Próxima fase: `specs/phase_4_paper_trading.md` (dual-path paper trading A+B, 3 meses). **Anti-regra explícita:** não fazer V3; não re-otimizar winner em Phase 3.5a — Phase B leads são movidos para Phase 4+5 (cost sensitivity, multi-asset transport, WF re-opt, ρ(A,B), GARCH vol-sizing). Plano B 3-leg EW permanece IMUTÁVEL. | V2 vindicou o framework corrigido (daily, hold ≥3d, spread+commission-dominant). Regime-driven é a única família viável em Plano A CFD Pepperstone — inferência de 6 famílias testadas, 1 PASS (Gayed), 5 DEAD estrutural. | iter 81 phase3.5a-v2 branch (V2-L7 atomic verdict) |

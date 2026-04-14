# Roadmap — ai-trade

> Mapa dos próximos passos do projeto. Leia isto ao retomar uma sessão para saber onde parou e para onde ir.

---

## 📍 Estado atual (2026-04-14)

- ✅ **Fase 0 — Knowledge Base.** 33/33 livros absorvidos e validados (pipeline `books/raw/*.pdf` → `extracted/` → `summaries/<slug>.md`, validação autônoma em 3 camadas substituindo revisão humana). `check_citations.py` global: 33/33 PASS. Qualidade: 🌟 12 Perfeita · ✅ 20 Boa · ⚠️ 1 Border, 0 alucinações reais.
- ✅ **Fase 0.5 — `knowledge/SKILL.md`.** `build_skill.py` agrega os 33 summaries em uma Claude Skill temática (`knowledge/SKILL.md` + `books/`, `strategies/`, `indicators/`, `validation/`). Skill carregável via `Skill` tool, inviolable rules #1-7 em produção.
- 🔄 **Fase 1 — Infra Pepperstone/cTrader.** Scaffold pronto (docker-compose com Postgres 5435 + Grafana; `ctrader_oauth_bootstrap.py`; schemas). Bloqueada aguardando aprovação Spotware do app OAuth.
- ✅ **Fase 2 — Backtest Module** (escopo reescrito — ver preâmbulo abaixo). Entregue 2026-04-14 via `specs/backtest_phase2.md`: data layer (yfinance + Wikipedia SPX point-in-time), engine (portfolio + execução CFD-aware + runner), validation framework (CPCV / PBO / DSR / walk-forward / MCPT), métricas + report (survivorship disclaimer obrigatório), Clenow `stocks_on_the_move` replicado end-to-end. **173 testes passando**.
- ⏳ **Próximo passo:** Fase 2.5 / 3 — rodar Clenow em grid de parâmetros exercitando CPCV/PBO/DSR com N≥20. Gate: distribuição honesta de Sharpe + PBO < 0.5 antes de migrar para dados pagos ou adicionar segunda estratégia (ver `specs/backtest_phase2.md` §"Reavaliação pós-Fase 2").

---

## 🛤️ Fases — detalhamento

### Fase 1 — Infraestrutura Pepperstone/cTrader + dados (VPS Ubuntu 24/7)

**Decisão:** broker = **Pepperstone**; plataforma = **cTrader**; API = **cTrader Open API** (Protobuf sobre TCP com OAuth2, SDK Python oficial Spotware `ctrader_open_api`). Alpaca, OANDA, IBKR e XM/MT5 descartados — ver `/home/victor/.claude/plans/delightful-bubbling-crab.md` para rationale completo. Demo e live usam o mesmo protocolo, só muda endpoint.

**Stack:**
- VPS Ubuntu (2 vCPU / 4 GB RAM, Frankfurt ou Londres pra latência com servidores Spotware na Europa). Opções: Hetzner CX22, Contabo VPS S.
- `docker-compose` com 3 serviços (zero Wine, zero VNC):
  - `app` — Python 3.12 com `ctrader_open_api` (Twisted-based). Hospeda estratégias, scheduler, logging, cliente cTrader Open API, Universe Selector.
  - `postgres` — schemas: `trades`, `features`, `logs`, `backtest_runs`, `market_data` (OHLCV cache).
  - `grafana` — dashboards de equity curve, drawdown, degradação.
- **OAuth bootstrap one-time (fora da VPS porque exige browser pra consent screen do cTID):** registrar app no `openapi.ctrader.com` → rodar script de auth na máquina local do dev → browser abre consent → callback em `localhost:8080` captura `authorization_code` → trocar por `access_token` + `refresh_token` → persistir `refresh_token` no `.env` → copiar pra VPS via rsync/scp. Alternativa: SSH tunnel de `localhost:8080` da VPS pra local durante o consent.
- **VPS runtime:** `app` usa `refresh_token` pra obter novo `access_token` quando expira (~30 dias). Comportamento de rotação (se é rotativo ou estático) a confirmar no smoke test da Fase 1.
- `restart: always` + healthcheck: TCP ping em `demo.ctraderapi.com:5035` + validação de `ProtoOAApplicationAuthReq` bem-sucedido.
- `.env` com `CTRADER_CLIENT_ID`, `CTRADER_CLIENT_SECRET`, `CTRADER_REFRESH_TOKEN`, `CTRADER_DEMO_ACCOUNT_ID`, `CTRADER_LIVE_ACCOUNT_ID`, `DATABASE_URL`.
- Conta recomendada na Pepperstone: **Razor** (raw spread + comissão transparente $3.50/lado — melhor para backtest preciso de custos). Standard é fallback aceitável.

**Pipeline de market data:** cTrader Open API Protobuf → Postgres. Mensagens-chave: `ProtoOASymbolsListReq` (lista de símbolos), `ProtoOAGetTrendbarsReq` (OHLCV histórico por timeframe M1/M5/H1/D1), `ProtoOASubscribeSpotsReq` (stream de ticks bid/ask em tempo real). Cobrir timeframes M1/M5/H1/D1 para instrumentos selecionados na Fase 2.

### Fase 2 — Backtest Module ✅ Concluída (2026-04-14) + Strategy Engine (2.5, pendente)

**⚠️ Escopo reescrito.** O plano original da Fase 2 era "Strategy Engine (Universe Selector + estratégias candidatas)". Na prática, detectou-se que **não dava para calibrar estratégia sem antes ter o módulo de backtest rigoroso** — CPCV/PBO/DSR são input do Universe Selector, não output. A Fase 2 foi então re-escopada para entregar o **módulo de backtest** (`src/ai_trade/backtest/`), com Clenow `stocks_on_the_move` como estratégia-calibração (exercita point-in-time universe, ATR sizing, regime filter, survivorship). Spec executável com campo Conclusão por task: [`specs/backtest_phase2.md`](specs/backtest_phase2.md).

**Entrega da Fase 2 (commits `517c221` → `415e205`):**
- `backtest/data/` — `yfinance_source` + `wikipedia_spx` point-in-time
- `backtest/engine/` — portfolio + execução CFD-aware + runner bar-by-bar
- `backtest/validation/` — CPCV / PBO / DSR / walk-forward / MCPT (5 módulos)
- `backtest/metrics/` — Sharpe/Sortino/Calmar/CAGR/DD/VaR + report MD+PNG
- `backtest/strategies/` — base + Clenow momentum replicado end-to-end
- **173 testes passando.** Survivorship disclaimer obrigatório em todo report.

**Fase 2.5 (pendente) — Strategy Engine + Universe Selector:** o conteúdo original desta seção (Restrição de design / Universe Selector / candidatas fundamentadas) permanece como trabalho futuro, agora **muito mais bem equipado** — com engine validado, não há mais "montar infra + projetar estratégia" misturados. Fase 2.5 abre depois que Clenow rodar em grid (ver §"Reavaliação pós-Fase 2" em `specs/backtest_phase2.md`).

---

#### Conteúdo original da Fase 2 (agora Fase 2.5 — Strategy Engine + Universe Selector)

**Restrição de design #1 — holding curto:** Pepperstone opera tudo como **CFD**, com swap/overnight cobrado diariamente. Estratégias devem ter holding típico de **minutos a poucos dias** (idealmente fechando posição antes do rollover — horário exato da Pepperstone a confirmar no bootstrap da Fase 1; provável 22h GMT como na maioria dos brokers CFD). Buy-and-hold multi-mês está fora de escopo — o swap vira drag material sobre o alpha.

**Restrição de design #2 — universo dinâmico e limitado:** em vez de varrer centenas de CFDs, o app opera sobre um **universo ativo de 5-15 instrumentos re-selecionado periodicamente** pelo Universe Selector (sub-fase 2.0). Candidatos naturais: SPX500, NAS100, US30, XAUUSD, BTCUSD, ETHUSD, EURUSD, GBPUSD, USDJPY + share CFDs de alta liquidez (AAPL, TSLA, NVDA, etc.).

**Instrumentos disponíveis na Pepperstone cTrader (para referência):** forex (~90 pares), índices CFDs (SPX500, NAS100, US30, GER40, UK100, JP225 etc.), share CFDs (majors globais — coverage menor que XM mas suficiente pra universo curado), crypto CFDs (BTC, ETH, SOL, etc.), commodities (ouro, prata, petróleo, gás). **Lista exata obtida via `ProtoOASymbolsListReq`** na primeira conexão de dev (abertura da Fase 2) — documentar em `docs/instruments_pepperstone.md` quando disponível.

#### Sub-fase 2.0 — Universe Selector (dynamic universe selection / tradability screening)

**Conceito:** um agente/job periódico que ranqueia um pool candidato e devolve os K instrumentos mais "negociáveis" agora — aqueles onde a estratégia ativa tem maior probabilidade de gerar expectância positiva líquida de custos. O Strategy Engine opera **exclusivamente** sobre a lista devolvida até a próxima rodada.

**Fundamentação na literatura:** conceito central e bem-documentado. Nomes formais: *cross-sectional momentum ranking*, *liquidity/tradability filtering*, *regime-conditioned asset selection*, *instrument rotation*.

| Camada do selector | Livro-fonte | Função |
|---|---|---|
| 1. Filtro duro de liquidez | Kaufman `trading_systems_methods`, Carver `systematic_trading` | Spread médio, volume, ATR mínimo, custo relativo. Descarta onde edge morre no custo. |
| 2. Classificação de regime por instrumento | Chen `regime_change` | Detecta trend/chop/high-vol; ativa só instrumentos no regime favorável à estratégia. |
| 3. Score de tradability / momentum | Clenow `stocks_on_the_move`, Masters `stat_sound_indicators` | Ranking por momentum ajustado, Hurst, ou métrica específica da estratégia. |
| 4. Screening estatístico | Masters `permutation_tests` | Testa se retorno recente sob a estratégia é significativamente ≠ de ruído. |
| 5. Meta-label de expectância condicional | López de Prado `advances_fin_ml` | Modelo secundário: "dado o estado atual, estratégia primária tem P(profit) > threshold?" |
| 6. Ranking final + cap no top K | Clenow | Cap em K instrumentos (sweet spot retail $1k: K=5-15). |

**Arquitetura:**

```
┌─ Universe Selector (roda a cada N dias) ────────────┐
│ Input:  pool candidato (~30-50 instrs Pepperstone)   │
│         pré-aprovados por liquidez mínima            │
│ Output: top K instrumentos ativos + score,           │
│         válidos até próxima rodada                   │
└──────────────────────────────────────────────────────┘
       │
       ▼
┌─ Strategy Engine opera SOMENTE sobre esse universo ─┐
└──────────────────────────────────────────────────────┘
```

**Parâmetros a calibrar (via backtest na Fase 3):**
- **N (período de re-seleção):** semanal é o default da literatura (Clenow). Diário tende a virar ruído; mensal é lento demais pra adaptar.
- **K (tamanho do universo ativo):** 5-15. Capital $1k + risk budget limitam K pra cima.
- **Regra de transição:** posições abertas em instrumentos que saíram do ranking — manter até stop/target (Clenow, evita churn) ou fechar imediato? Default: manter.
- **Pool candidato:** definir lista fixa de ~30-50 instrumentos Pepperstone pré-filtrados por liquidez absoluta (obtidos via `ProtoOASymbolsListReq` e filtragem por spread/ATR/volume). Não muda toda rodada; só é revisada trimestralmente.

**⚠️ Gate anti-overfit:** o Universe Selector é ele próprio uma estratégia. Precisa passar pelo **mesmo framework de 7 camadas da Fase 3** (CPCV, PBO, DSR, permutation). Sem isso, só empurra o overfit de nível — em vez de otimizar parâmetros da estratégia, otimiza parâmetros do selector. `TRADING_SYSTEM_PLAN.md §14.5` cobre esse tipo de armadilha.

Cada estratégia implementada deve citar o livro/seção de origem. Candidatas priorizadas pro universo Pepperstone (filtradas pela restrição de holding curto):

| Estratégia | Livro-fonte | Holding típico | Fit CFD |
|---|---|---|---|
| Cycle analysis / DSP (intraday e swing curto) | Ehlers — `rocket_science`, `cycle_analytics`, `cybernetic_analysis` | horas a 2-3 dias | ⭐⭐⭐ nativo |
| Regime detection (filtro sobre outras estratégias) | Chen — `regime_change` | overlay | ⭐⭐⭐ agnóstico |
| Momentum cross-sectional intradiário no universo curado | Clenow — `stocks_on_the_move` (adaptado) | 1-5 dias | ⭐⭐ adaptado |
| ML meta-labeling / triple-barrier | López de Prado — `advances_fin_ml` | definido pela barreira | ⭐⭐⭐ agnóstico |
| Position sizing / Kelly fractional | Vince — `leverage_space`, `math_money_mgmt` | overlay | ⭐⭐⭐ agnóstico |
| Sentiment overlay (news/social) | Peterson — `trading_on_sentiment` | overlay | ⭐⭐ requer data feed extra |

**Estratégias de holding longo (buy-and-hold, rebalance mensal puro) ficam fora de escopo** enquanto o broker for CFD-based (Pepperstone ou similar).

### Fase 3 — Backtest rigoroso (framework anti-overfit de 7 camadas)

Coração do plano (§6.3 do `TRADING_SYSTEM_PLAN.md`). Cada camada vem de um livro:

1. **CPCV** (Combinatorial Purged Cross-Validation) — López de Prado
2. **PBO** (Probability of Backtest Overfitting) — López de Prado
3. **DSR** (Deflated Sharpe Ratio) — López de Prado
4. **Permutation tests** — Masters (`permutation_tests`)
5. **Walk-forward multi-regime** — Kaufman / Masters
6. **Parsimônia de parâmetros** (máx 2-3, cada um justificado) — Aronson / Carver
7. **Monitoring de degradação em produção** — Aronson (`evidence_based_ta`!)

### Fase 4 — Paper trading via conta demo cTrader (validação em tempo real)
30-90 dias rodando na **conta demo cTrader da Pepperstone**, linkada ao cTID do usuário. Execução idêntica à real — mesmo SDK, mesmo protocolo Protobuf, só muda `CTRADER_DEMO_ACCOUNT_ID` e endpoint (`demo.ctraderapi.com:5035`). Paridade com live é nativa ao design do cTrader Open API. Logar todos os trades em Postgres, comparar distribuição de retornos vs backtest esperado, detectar divergência (slippage, spreads, gaps de execução).

### Fase 5 — Live trading na Pepperstone ($1000 inicial)
Troca de `CTRADER_LIVE_ACCOUNT_ID` e endpoint (`live.ctraderapi.com:5035`) no `.env`, mesma infra, mesmos containers. Funding via PIX (Pepperstone suporta desde 2024 para clientes BR). Gate de produção: estratégia só passa se vencer o checklist anti-overfit (§6.4 do plano). Se PBO > 50% → descartar. Se DSR < 1.0 → descartar.

### Fase 6 — Monitoring + governança
Claude recebe métricas semanais, detecta degradação, recomenda pausa/re-otimização/descontinuação.

### Fase 7 — Scaling
Só após Fase 6 estar sólida por meses.

---

## 🔖 Decisões adiadas para reavaliação (Fase 2-3)

Escolhas **intencionalmente minimalistas** no módulo de backtest, registradas
aqui para não se perderem quando chegar a hora de reavaliar.

### Fonte de dados de mercado (daily OHLCV)

**Decisão inicial:** `yfinance` + Wikipedia (scrape de constituintes históricos
SPX). Grátis, com **survivorship bias documentado explicitamente em cada
relatório de backtest**.

**Reavaliar quando:** primeira estratégia passar pelos gates anti-overfit
(CPCV + PBO + DSR). Migrar para fonte survivorship-free paga (Tiingo ~$10/mo,
EOD Historical ~$20/mo, Norgate $85/mo se quiser replicar Clenow com rigor).
Migração é apenas um adapter novo em `src/ai_trade/backtest/data/`; não quebra
código existente.

### Laboratório de prototipagem rápida (vectorbt)

**Decisão inicial:** não adicionar. Engine rigoroso custom é suficiente enquanto
o aprendizado do próprio engine for a principal fonte de atrito.

**Reavaliar quando:** iteração sobre hipóteses de indicador/parâmetro tiver
atrito mensurável (ex.: >30 min para testar uma variação simples). Nesse
momento, `vectorbt` entra como **sandbox para triagem de ideias antes** de
serem levadas ao engine rigoroso — não substitui o rigoroso.

### Segunda estratégia a replicar (após Clenow)

**Decisão inicial:** não pré-selecionar. Clenow `stocks_on_the_move` é o target
único da Fase 2/3 inicial — já força o engine a cobrir point-in-time universe,
ATR sizing, ranking cross-sectional, regime filter de índice e survivorship
bias.

**Reavaliar quando:** Clenow rodar e o engine passar pelos gates. Candidatas
documentadas:
- **AFML meta-labeling** `[advances_fin_ml, ch.3]` — primário de direção + secundário ML de confiança
- **Ehlers DSP** `[rocket_science, cycle_analytics]` — MAMA/Fisher/Cyber Cycle como filtros/timing
- **Chan mean-reversion / pairs** `[algo_trading_chan]` — cointegração, pairs trading

A escolha vira informada pelos achados do Clenow (ex.: se o problema for regime
change → AFML meta-label; se for entrada/saída → Ehlers DSP; se for timing em
trend-follow → Chan mean-reversion como overlay).

---

## 🧪 Backtest em duas etapas: pesquisa vs calibração

Princípio de design (não é decisão adiada — é como o backtest funciona em
todas as fases):

### Etapa 1 — Pesquisa / edge detection (Fase 2-3)

- **Pergunta:** a estratégia tem edge em dados de equity limpos?
- **Dados:** fontes externas survivorship-aware — `yfinance`+Wikipedia (inicial, grátis, bias documentado), depois Tiingo/EOD/Norgate.
- **Por quê externo:** cTrader/Pepperstone só fornece dados do próprio broker, histórico limitado e **sem** constituintes point-in-time. Detecção de edge exige dados cross-broker de qualidade acadêmica.
- **Gates:** CPCV + PBO + DSR + permutation + walk-forward. ~80% das ideias ruins morrem aqui.

### Etapa 2 — Calibração na realidade Pepperstone (pré-Fase 4)

- **Pergunta:** esse edge sobrevive aos custos reais de CFD da Pepperstone?
- **Dados:** histórico de trendbars via `ProtoOAGetTrendbarsReq` (cTrader Open API, disponível quando a Spotware aprovar o app).
- **Ajustes aplicados:**
  - Spread real por símbolo (medido, não estimado)
  - Swap/overnight por símbolo
  - Universo reduzido (Pepperstone não lista as 500; oferece índice CFD + share CFDs selecionados + forex/crypto/commodities)
- **Resultado esperado:** Sharpe menor que na Etapa 1. Se o edge evapora aqui, estratégia morre antes de paper trading.

### O que muda no código quando cTrader destravar

**Nada na arquitetura do engine** (CPCV/PBO/DSR/strategy logic). Só entra um
adapter novo:

```
src/ai_trade/backtest/data/
├── yfinance_source.py            # Etapa 1 (início, grátis)
├── wikipedia_spx.py              # constituintes SPX (Etapa 1)
├── tiingo_source.py              # (futuro) Etapa 1 survivorship-free
└── ctrader_historical_source.py  # (futuro) Etapa 2, calibração Pepperstone
```

**Princípio subjacente:** nunca usar dados do broker como única fonte de
pesquisa — só como validação final contra a execução real. Broker data tem
viés de sobrevivência (só os produtos que o broker ainda oferece), de
seleção (broker-específico) e de histórico (profundidade variável).

---

## 🔑 Princípio-chave (não negociável)

`TRADING_SYSTEM_PLAN.md §14.5` **rejeita explicitamente "vibes-based LLM trading"**. Toda decisão (indicador, parâmetro, sizing, gate de produção) exige citação `[livro.slug, p.X]` do knowledge base. Por isso a Fase 0 vem primeiro — sem ela, o agente opera sem fundamentação.

**Resumo:** Fase 0 = munição intelectual. Fases 1-7 = construir e operar o sistema usando essa munição.

---

## 🔄 Como retomar uma sessão

Cole este prompt ao abrir o Claude Code:

```
Estou retomando o desenvolvimento do projeto ai-trade.
Leia ROADMAP.md para estado das fases e próximos passos.
Leia specs/backtest_phase2.md para contexto do módulo de backtest
(Fase 2 concluída 2026-04-14 — engine + validation + métricas + Clenow).
Próximo passo: Fase 2.5 / 3 — grid search Clenow + gates CPCV/PBO/DSR
em produção. Ver §"Reavaliação pós-Fase 2" no spec.
```

---

## 📚 Livros da knowledge base (33/33 absorvidos e validados)

Status resumido — detalhes completos em `books/README.md` (tabela "Catálogo dos livros" com colunas Review por livro):

| # | Livro | Slug | Importância | Qualidade |
|---|---|---|---|---|
| 1 | Adaptive Markets (Lo) | `adaptive_markets` | ⭐ | ⚠️ |
| 2 | Advances in Financial Machine Learning (López de Prado) | `advances_fin_ml` | ⭐⭐⭐ | 🌟 |
| 3 | Algorithmic Trading (Chan) | `algo_trading_chan` | ⭐⭐ | 🌟 |
| 4 | Big Data and ML in Quantitative Investment (Guida ed.) | `big_data_ml_quant` | ⭐ | ✅ |
| 5 | Cybernetic Analysis for Stocks and Futures (Ehlers) | `cybernetic_analysis` | ⭐⭐ | ✅ |
| 6 | Cybernetic Trading Strategies (Ruggiero) | `cybernetic_trading` | ⭐ | ⚠️ |
| 7 | Cycle Analytics for Traders (Ehlers) | `cycle_analytics` | ⭐ | ✅ |
| 8 | Data-Driven Science and Engineering (Brunton/Kutz) | `data_driven_science` | ⭐ | 🌟 |
| 9 | The Evaluation and Optimization of Trading Strategies (Pardo) | `eval_opt_strategies` | ⭐⭐⭐ | 🌟 |
| 10 | Evidence-Based Technical Analysis (Aronson) | `evidence_based_ta` | ⭐⭐ | 🌟 |
| 11 | Financial Time Series Analysis (Tsay) | `fin_time_series_tsay` | ⭐⭐ | ✅ |
| 12 | Leverage Space Trading Model (Vince) | `leverage_space` | ⭐⭐ | 🌟 |
| 13 | Machine Trading (Chan) | `machine_trading` | ⭐⭐ | ✅ |
| 14 | Mathematics of Money Management (Vince) | `math_money_mgmt` | ⭐⭐ | ✅ |
| 15 | ML for Algorithmic Trading (Jansen) | `ml_for_algo_trading` | ⭐⭐⭐ | ✅ |
| 16 | ML for Asset Managers (López de Prado) | `ml_for_asset_managers` | ⭐ | ✅ |
| 17 | Numerical Recipes (Press et al.) | `numerical_recipes` | ⭐ | ✅ |
| 18 | Quantitative Trading (Chan) | `quant_trading_chan` | ⭐⭐⭐ | 🌟 |
| 19 | Detecting Regime Change in Computational Finance (Chen) | `regime_change` | ⭐⭐⭐ | ✅ |
| 20 | Risk Parity Fundamentals (Qian) | `risk_parity` | ⭐ | ✅ |
| 21 | Rocket Science for Traders (Ehlers) | `rocket_science` | ⭐ | ✅ |
| 22 | Handbook of Sentiment Analysis in Finance (Mitra & Yu) | `sentiment_analysis_handbook` | ⭐ | 🌟 |
| 23 | Statistically Sound Indicators (Aronson/Masters) | `stat_sound_indicators` | ⭐⭐ | 🌟 |
| 24 | Stocks on the Move (Clenow) | `stocks_on_the_move` | ⭐⭐⭐ | 🌟 |
| 25 | Systematic Trading (Carver) | `systematic_trading` | ⭐⭐⭐ | 🌟 |
| 26 | Technical Analysis for Algorithmic Pattern Recognition (Tsinaslanidis) | `tech_analysis_patterns` | ⭐ | ✅ |
| 27 | Testing and Tuning Market Trading Systems (Masters) | `testing_tuning` | ⭐⭐ | ✅ |
| 28 | Time Series Analysis (Hamilton) | `time_series_hamilton` | ⭐ | 🌟 |
| 29 | Trading Evolved (Clenow) | `trading_evolved` | ⭐⭐ | ✅ |
| 30 | Trading and Exchanges (Harris) | `trading_exchanges` | ⭐⭐ | ✅ |
| 31 | Trading Systems and Methods (Kaufman) | `trading_systems_methods` | ⭐⭐⭐ | 🌟 |
| 32 | Universal Tactics of Successful Trend Trading (Penfold) | `universal_trend_tactics` | ⭐ | ✅ |
| 33 | Volatility Trading (Sinclair) | `volatility_trading` | ⭐⭐ | ✅ |

**Legenda:** ⭐⭐⭐ Crítico (7) · ⭐⭐ Importante (12) · ⭐ Complementar (14). 🌟 Perfeita (12) · ✅ Boa (20) · ⚠️ Border (1).

**Não absorvidos (fora do escopo atual, anotação histórica):**
- `permutation_tests` (Masters) — conteúdo relevante já coberto por `stat_sound_indicators` + `testing_tuning` (mesmo autor, overlap forte).
- `assessing_prediction` (Masters) — idem.
- `trading_on_sentiment` (Peterson) — substituído por `sentiment_analysis_handbook` (Mitra & Yu, cobertura mais ampla).
- `new_tech_trader` (LeBeau & Lucas) — referenciado por `cycle_analytics` como origem do VIDYA; decisão documentada de não absorver, cross-ref mantida com N/A.

Pipeline é idempotente: PDFs faltando são pulados sem quebrar a execução.

---

## 📎 Referências rápidas

- Plano geral: `TRADING_SYSTEM_PLAN.md`
- Plano aprovado Fase 0: `/home/victor/.claude/plans/mighty-mixing-porcupine.md`
- Plano ativo: `/home/victor/.claude/plans/synthetic-snuggling-wren.md`
- **Status detalhado por livro:** `books/README.md` (seção "Catálogo dos livros" com tabela Review)
- Summaries validados: `books/summaries/*.md`
- Auditoria de validação: `books/summaries/.validation/` (gitignored)
- Logs de absorção: `books/summaries/.logs/` (gitignored)

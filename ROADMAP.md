# Roadmap — ai-trade

> Mapa dos próximos passos do projeto. Leia isto ao retomar uma sessão para saber onde parou e para onde ir.

---

## 📍 Estado atual

**Fase 0 — Knowledge Base (concluída, pronto para consolidação).**

Pipeline: `books/raw/*.pdf` → `books/extracted/<slug>/` → `books/summaries/<slug>.md` (9 seções, citação obrigatória `[p.X]`/`[ch.Y]` ou `N/A —`) → `knowledge/SKILL.md` (agregador final, **próximo passo**).

- ✅ Pipeline de extração/validação funcional (`scripts/extract_pdfs.py`, `scripts/validate_summary.py`, `scripts/check_citations.py`, `scripts/build_page_index.py`).
- ✅ Validação autônoma em 3 camadas (estrutural + determinística + 2 juízes adversariais com self-consistency) substitui revisão humana.
- ✅ **Tier 2 pipeline hardening:** `_page_index.json` determinístico por livro elimina retry-hell por offset drift; detector `n_chapters_effective` (FU-1) deriva bound de citações do próprio summary; convenção PT/EN documentada no book-reader skill (FU-3).
- ✅ **33/33 livros absorvidos e validados:** 🌟 12 Perfeita · ✅ 20 Boa · ⚠️ 1 Border (0 halluc reais). `check_citations.py` global: **33/33 PASS** (0 fails). `validate_summary.py`: 33/33 PASS estrutural, 10/10 seções em todos.
- ✅ **Strict halluc audit:** 5 livros com J2 BORDERLINE revalidados — 1 fix real aplicado (`regime_change`: Glattfelder 2008→2011 per bibliografia Quantitative Finance 11:4). Demais BORDERLINEs são paráfrases ambíguas com 0 unsupported claims.
- ⏳ **Próximo comando:** `python scripts/build_skill.py` (determinístico, sem LLM calls — agrega os 33 summaries em `knowledge/`).

---

## 🛤️ Depois do `/absorb-all-books`

### Fase 0.5 — Consolidação do `knowledge/SKILL.md` (imediato)
Rodar `scripts/build_skill.py` — agrega os **33 summaries validados** em uma **Claude Skill temática** em `knowledge/SKILL.md` + árvore `knowledge/books/<slug>.md`, `knowledge/strategies/*.md`, `knowledge/indicators/*.md`, `knowledge/validation/*.md`. Essa skill vira o "especialista de trading" — toda decisão futura consulta ela e exige citação `[livro.slug, p.X]`.

Script é determinístico (zero LLM calls). Aceita `--skip-validation` (não recomendado); roda `validate_summary.py` como gate antes de agregar.

**Gate:** validar a skill carregando via `Skill` tool e fazendo queries de sanidade (e.g., "qual posição sizing López de Prado recomenda?" → deve responder com citação `[advances_fin_ml, p.X]`).

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

### Fase 2 — Strategy Engine (fundamentada na literatura)

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

## 🔑 Princípio-chave (não negociável)

`TRADING_SYSTEM_PLAN.md §14.5` **rejeita explicitamente "vibes-based LLM trading"**. Toda decisão (indicador, parâmetro, sizing, gate de produção) exige citação `[livro.slug, p.X]` do knowledge base. Por isso a Fase 0 vem primeiro — sem ela, o agente opera sem fundamentação.

**Resumo:** Fase 0 = munição intelectual. Fases 1-7 = construir e operar o sistema usando essa munição.

---

## 🔄 Como retomar uma sessão

Cole este prompt ao abrir o Claude Code:

```
Estou retomando o desenvolvimento do projeto ai-trade.
Leia o ROADMAP.md para estado atual e próximos passos.
Leia TRADING_SYSTEM_PLAN.md se precisar do plano geral do sistema.
Fase 0 (knowledge base, 33 livros) concluída. Próximo: rodar build_skill.py
e entrar na Fase 1 (infra Pepperstone/cTrader).
```

---

## 📚 Livros da knowledge base (33/33 absorvidos e validados)

Status resumido — detalhes completos em `books/TODO.md` (colunas Review + Tarefas pendentes por livro):

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
- **Status detalhado por livro:** `books/TODO.md` (tabela Status Geral com Review + Tarefas pendentes)
- Summaries validados: `books/summaries/*.md`
- Auditoria de validação: `books/summaries/.validation/` (gitignored)
- Logs de absorção: `books/summaries/.logs/` (gitignored)

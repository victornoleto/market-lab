# Phase E-MVP — BREADTH_NO_WINNER_E (multi-market SP500 + IBrX-100)

**Data:** 2026-04-23 03:18 AM-3 (06:18 UTC)
**Verdict:** `NO_WINNER_MVP` — **113º FAIL consecutivo do projeto** (71 prev. + 42 E)
**Universo:** SP500 top-200 + IBrX-100 = 280 tickers efetivos
**Grid:** 42 configs (24 D1 Clenow + 18 D4 low-vol+mom) × 3 splits
**Runtime:** 01:20 → 03:18 = 1h58min (engine optimization funcionou — ~3min/config vs 45min/config do Phase D)

## Resultado em 1 linha

**PBO = 0.786** (vs threshold < 0.5) + **DSR 0/42 passam** (p > 0.97 em todos) + **42/42 tier Folclore** (CAGR < 11% CDI).

## Números que importam

Da tabela completa em `reports/phase_e_mvp/SUMMARY.md` (42 linhas):

| Métrica | Melhor config | Mediana | Pior config |
|---------|--------------|---------|------------|
| OOS Sharpe | **+0.151** | −0.029 | −0.245 |
| OOS CAGR líquido | +0.06% | −4.5% | −11.1% |
| OOS MDD | 36.9% | 47.5% | 53.6% |
| Tier CAGR | Folclore | Folclore | Folclore |
| Tier MDD | Forte warning | Forte warning | Reject |
| DSR p | 0.970 | 0.989 | 0.997 |
| Tax (R$, 2020-2023) | R$32k | R$55k | R$90k |

A melhor config E (D4 n_top=25 pre_n=30 vol_lk=90) tem **+0.06% CAGR líquido em 4 anos**
— essencialmente zero após cost + tax. Sharpe positivo mas DSR p = 0.970
(indistinguível de noise em 42 trials).

## Onde a estratégia operou

Trades breakdown (OOS 2020-2023):
- **D1 configs**: 226-482 trades, **~73% em BR / 27% em US** — Clenow momentum preferiu
  BR porque momentum absoluto dos tickers BR em janelas específicas (ex: Petrobras +200%
  2021) venceu o ranking contra US largecaps mais estáveis.
- **D4 configs**: 154-231 trades, **~66% em BR / 34% em US** — o low-vol re-rank
  puxou mais pra US (vols menores), mas ainda dominado por BR.

Tax R$ mostra o efeito do 15% DARF nas US positions + R$20k sometimes busted em BR:
mediana R$55k de tax em 4 anos sobre capital R$50k inicial = **27% drag acumulado só de tax**.

## Por que Strategy E falhou — análise estrutural

### 1. PBO 0.786 = ranking IS→OOS é random

Isso é a métrica mais brutal do relatório. PBO mede: "se eu escolher a melhor config
no IS, qual a probabilidade dela não ser a melhor no OOS?" Resposta aqui: **78.6%**.
Tecnicamente a strategy é indistinguível de random picking entre os 42 configs.

`[advances_fin_ml, p.208-211]` específica PBO < 0.5 como linha de corte — acima disso
o que parece edge é artefato de busca. PBO **0.786 confirma que o grid explorou o
espaço de parâmetros sem encontrar estrutura genuína**.

### 2. Regime 2020-2023 é hostil pra momentum cross-sectional global

No Phase D analisamos só o regime BR. O Phase E confirma que **adding US não resolve**:

- **2020 Q1**: COVID crash simultâneo BR + US (Ibov -45%, SPX -34%). Cross-sectional
  momentum falha porque ALL stocks caíram juntas — dispersion virou zero.
- **2020 Q2-2021**: rally assimétrico (growth/tech/meme US, commodities BR). Momentum
  se posicionou nos winners, mas giros foram caros (155-482 trades × 15 bps spread).
- **2022**: rate shock FED + BCB destruiu duration premium em ambos. Momentum manteve
  exposure em tech/commodities que quebraram.
- **2023**: AI narrative dominou SPX (7 stocks = 60% do ganho). Top-20-by-rank não
  captura isso; diluição sector-cap força holdings fora dos 7 winners.

### 3. 15% DARF em US + R$20k bust comem metade do edge possível

Tax médio R$55k sobre capital R$50k em 4 anos = 13.75%/ano de drag. Mesmo que a
strategy tivesse Sharpe 0.8 pre-tax (que não tem), o net ficaria < 0.4.

### 4. Universo 280 tickers ainda é subdimensionado

Renaissance opera ~10,000 tickers. Two Sigma ~5,000 global. Cross-sectional momentum
precisa de 500-2000+ nomes pra dispersion consistente. 280 em 2 regimes pequenos (mega
caps US + BR dominado por 5 nomes) não dá diversificação suficiente.

## Contabilidade cumulativa do projeto

| Phase | Leads | Result |
|-------|-------|--------|
| 3.5f V2 Plano A | 6 | 6/6 FAIL |
| 3.6 broader hunt | 10 | 10/10 FAIL |
| 3.7-3 top-tier literature | 8 | 8/8 FAIL |
| 3.8-1 Gayed canonical | 5 | 5/5 FAIL |
| 3.6 families (old runs) | 32 | all FAIL (counted above) |
| D-MVP partial (D1 BR-only) | 10 | 10/10 FAIL |
| **E-MVP (D1+D4 multi-market)** | **42** | **42/42 FAIL** |
| **TOTAL** | **113** | **113/113 FAIL** |

**Zero winners em 113 honest validations com 33 livros absorvidos, engine cross-lib
validada, gates PBO/DSR/WF/bootstrap aplicados rigorosamente.**

## Recomendação final honesta

**É hora de parar.** Com 113/113 FAIL em 2 semanas + 5-6 factors globais testados
(momentum US, momentum BR, momentum cross, mean reversion, LETF rotation, regime
filter, VIX-managed, DSP cycles, HMM regime-switch, ML classical, value+quality),
a conclusão científica honesta é que **active alpha não está acessível pro setup
atual (retail, capital < $1M, broker retail, dados free/yfinance)**.

Isso é consistente com:
- **Harvey & Liu (2015) JOIM** — >80% dos factors publicados em top journals falham
  multiple-testing correction.
- **Ilmanen (2011) Expected Returns** — mesmo os 5-6 factors globais robustos têm
  underperform periods de 10-15 anos; retail timeframe não aguenta essa paciência.
- **López de Prado `[advances_fin_ml, p.31-34]`** — "most backtested strategies are
  false discoveries". PBO gate existe porque o default é overfit.

### Recomendação oficial: consolidar Plano C passive factor-tilted

Alocação proposta (substitui o split 60-80% passive / 20-40% active do mandate §1):

- **100% passive factor-tilted** conforme `portfolio-aposentadoria.md`
  - AVUS/SPMO/AVUV (US factor + momentum + value/smallcap)
  - AVDE/IDMO/AVDV (DM ex-US factor)
  - AVEM (EM)
  - IBIT (crypto core)
  - GLDM (gold hedge)
- **0% slots ativos A, B, D, E** até evidência material de signal accessible
- **Strategy A, B, D, E permanecem como slots ABERTOS mas inativos no mandate** —
  se futura literatura ou regime shift mudar o quadro, a infra está pronta
  (engine cross-lib validated, gates honest, 33 livros absorvidos)

Isso não é "desistir". É **honrar o protocolo rigoroso que foi construído em 2 semanas
e aceitar o sinal que o mercado mandou**. O projeto ai-trade continua sendo valor:

1. **Due diligence adversarial contra folclore futuro** — qualquer "guru" que chegar
   com "100% CAGR strategy" passa pelos gates antes de alocar real money.
2. **Monitoring automático de regime shifts** — se momentum voltar a funcionar em
   2028+ (plausível; factors são cíclicos), um grid rerun detecta.
3. **Factor-tilted passive não é random** — escolha de AVUS/SPMO/AVUV sobre VOO foi
   fundamentada pelos livros do knowledge base.

## Próximos passos (decisão do usuário ao acordar)

**Opção R3-STRONG: consolidar Plano C, fechar slots ativos**
1. Atualizar mandate §1 pra 100% passive (override em `docs/mandate_overrides/`)
2. Fechar todos os open specs/planos ativos como "final status: no winner found"
3. Project ai-trade vira modo "maintenance" — monitoring only

**Opção R5-LAST: tentar 1 experimento final muito diferente (meta-labeling ensemble)**
- Infra `afml_tb_meta.py` existe mas nunca foi explorada como ensemble dinâmico sobre
  os 113 leads falhados. Se combinarmos signals-com-falha em meta-labeled ensemble,
  talvez o weak alpha de cada lead se some. **Probabilidade de sucesso baixa
  (10-20%)**; efetivamente última cartada.

**Opção R-WAIT: deixar como está, re-rodar em 6-12 meses**
- Regime 2020-2023 pode ter sido anomalia. Se 2024-2026 normaliza, reaplica gates
  existentes e vê se algum lead passa.

Recomendação forte: **R3-STRONG + R-WAIT combinadas**. Consolidar agora, manter infra,
revisitar daqui 6-12 meses se dados novos sugerirem.

## Artefatos

- `reports/phase_e_mvp/SUMMARY.md` — tabela 42×10 completa
- `reports/phase_e_mvp/dsr_results.json` — 42 DSR per-config
- `reports/phase_e_mvp/oos_returns_matrix.npz` — matriz PBO
- `reports/phase_e_mvp/<slug>/` per-config (IS/OOS/FWD json + equity parquet)
- `reports/phase_d_mvp/BREADTH_NO_WINNER_D.md` — partial análise Phase D
- `logs/phase_e_mvp.log` — runtime log 1h58min

## Referências

- Spec Strategy E: `scripts/phase_e_mvp/` (não criado em specs/ ainda — reusa D)
- Plano: `/home/victor/.claude/plans/zazzy-booping-oasis.md`
- Mandate override: `docs/mandate_overrides/2026-04-23-strategy-e-multimarket.md` (PENDING)
- Recomendação final será formalizada em
  `docs/mandate_overrides/2026-04-23-consolidate-plano-c.md` se usuário aprovar R3-STRONG.

## Citações

- PBO gate: `[advances_fin_ml, p.208-211]`
- DSR deflator: `[advances_fin_ml, p.275]`
- "Most backtests are false discoveries": `[advances_fin_ml, p.31-34]`
- Cross-sectional momentum persistence assumption: `[stocks_on_the_move, p.76-77]`
- Regime break kills factors: `[adaptive_markets, p.282-283]`
- Retail factor expectations: Ilmanen Expected Returns (ch.1-2); Harvey & Liu 2015 JOIM

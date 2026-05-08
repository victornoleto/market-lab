# Resumo executivo — re-avaliação Sortino do estudo LETF

_Data: 2026-05-07 | Documento técnico completo: `SORTINO_REANALYSIS_REPORT.md`_

---

## O que mudamos

Trocamos a **régua de medida** da estratégia: antes usávamos **Sharpe** (que considera qualquer volatilidade como risco — incluindo ganhos extras), agora usamos **Sortino** (que só considera as quedas como risco real).

Isso é tudo. Nenhuma estratégia foi alterada, nenhum capital foi movimentado. Só medimos os mesmos backtests com uma régua diferente, mais justa pra estratégias com alavancagem.

---

## Por que importa

A estratégia LETF rotation tem uma característica importante: ela é projetada pra **capturar ganhos grandes** em períodos de alta (com 2× ou 3× alavancagem) e **se proteger em ZROZ** em períodos de queda. Os "ganhos grandes" são o ponto de usar alavancagem.

O **Sharpe trata isso injustamente**: ele pune um mês com +30% (ótimo!) da mesma forma que pune um mês com −30% (horrível). Resultado: Sharpe sub-estima a vantagem real de estratégias alavancadas.

O **Sortino corrige isso**: só pune as quedas. É a régua certa pra avaliar LETF rotation.

---

## O que descobrimos

**1. A vantagem real é ~55% maior do que parecia.**
A vantagem do canonical sobre comprar SPY direto era de **+0.171** medida com Sharpe. Com Sortino, é **+0.264** — quase 55% mais. A "magia" da alavancagem com regime filter estava sendo sub-medida.

**2. O vencedor do estudo mudou.**
A versão **canonical** (`qld_vote_k2_off_zroz`, com SMA200/50 e ZROZ defensivo) era o ranking-1 sob Sharpe. Sob Sortino, ela é destronada por uma variante chamada **`qld_voteK2_sma250_100_off_zroz`** — que é basicamente a mesma estratégia, só com janelas SMA mais longas (250 e 100 dias em vez de 200 e 50).

**3. A nova versão neutraliza o trauma do dotcom 2000.**
O sub-estudo `cohort_robustness` tinha mostrado que **2000** era o único cenário onde a canonical falhava: quem entrou no pico de Março/2000 perdeu **−12,7% por ano** nos primeiros 5 anos (vs −3,7% do SPY de mesma data). A nova versão (sma250/100) reduz isso pra **−1,6% por ano** — praticamente neutralizado.

A diferença é que a janela SMA250 detecta o topo da bolha ~1-2 meses antes da SMA200, e a estratégia entra defensiva em ZROZ a tempo de evitar a maior parte da queda.

**4. O imposto brasileiro continua sendo o gargalo.**
Mesmo com a nova régua, sob o regime de imposto **per-swing** (15% em cada saída lucrativa, sem compensação de prejuízos), a vantagem real é apertada. Sob o regime **anual** (Lei 14.754/2023, com compensação), sobra vantagem suficiente pra justificar o estudo. Mandate §1 mantém capital 100% Plano C.

---

## O que significa pra você

**1. Se algum dia o Plano B for ativado**, a estratégia recomendada NÃO é mais a canonical. É a variante **sma250/100**:
- Ela passa a régua mais rigorosa (Sortino + 0.05).
- Ela é muito mais resiliente ao único cenário em que a canonical falhava (dotcom 2000).
- Ela já tinha sido a única que passava o threshold de imposto anual no sub-estudo `tax_comparison` (com vantagem +0.145 vs SPY).

**2. Por enquanto, nada muda.** Mandate §1 (`docs/investment-mandate.md`) mantém o capital 100% Plano C (carteira passiva fator-tilted). Estratégias A, B e D continuam DORMENTES. Esse estudo é infraestrutura de pesquisa pra quando/se Plano B for reativado no futuro.

**3. Próximo passo: re-escrever os relatórios públicos.**
Os 4 relatórios principais do estudo (FINAL, HIGHLIGHTS, REDDIT, REDDIT_DRAWDOWNS) ainda estão escritos em Sharpe-mundo. Próxima entrega: re-escrevê-los em Sortino-mundo, incorporando os 4 sub-estudos (tax, cohort, threshold, sortino).

---

## Onde encontrar

- **Este resumo:** `studies/letf_rotation_hunt/reports/SORTINO_RESUMO_EXECUTIVO.md`
- **Relatório técnico completo (13 seções):** `SORTINO_REANALYSIS_REPORT.md`
- **Narrativa em PT-BR (jornada):** `jornada/2026-05-07-1733-letf-sortino-reanalysis.md`
- **Dados brutos:** `data/sortino_reanalysis/{sortino_metrics, cohort_extension}.csv`
- **Plots:** `studies/letf_rotation_hunt/reports/sortino_reanalysis/{sortino_vs_sharpe_scatter, track_pass_comparison}.png`

---

## Glossário rápido (jargão usado nos outros documentos)

| Termo | Tradução | O que é |
|---|---|---|
| **Sharpe ratio** | Régua antiga | Mede retorno por unidade de volatilidade total (pune ganhos e perdas igual) |
| **Sortino ratio** | Régua nova | Mede retorno por unidade de **só** volatilidade negativa (pune só perdas) |
| **canonical** | Versão padrão | A estratégia ranking-1 do estudo: `qld_vote_k2_off_zroz` |
| **Vote-of-K=2** | Votação de 2/4 sinais | Estratégia ON quando pelo menos 2 dos 4 sinais (SMA longo, SMA curto, vol baixa, momentum positivo) estão verdes |
| **OFF asset / ZROZ** | Ativo defensivo | ETF de Treasury de longo prazo (ZROZ); pra onde a estratégia rota quando os sinais são negativos |
| **lh_56y** | Janela 56 anos | Backtest de 1969 a 2025 com dados sintéticos pré-1999 |
| **edge vs SPY** | Vantagem sobre SPY 1× | Diferença de Sharpe (ou Sortino) entre a estratégia e simplesmente comprar SPY e segurar |
| **Track A / B** | Trilhas de avaliação | Track A = bruto (gross), Track B-M1 = líquido per-swing 15%, Track B-M2 = líquido anual 15% (Lei 14.754) |
| **threshold +0.05** | Margem anti-overfit | Pra ser declarada vencedora, uma estratégia precisa bater a canonical por +0.05 (não basta empatar) |
| **PBO / DSR** | Testes estatísticos | PBO = Probability of Backtest Overfitting (de Prado); DSR = Deflated Sharpe Ratio. Detectam se o resultado é genuíno ou p-hacking. |
| **dotcom 2000** | Crise de 2000 | Pico do NDX em Março/2000 → −83% de queda até Out/2002. Único cenário onde a canonical falha em 8+ anos. |

---

_Documento mantido para uso humano não-especialista. Para detalhes técnicos, citações de livros e tabelas completas, ver `SORTINO_REANALYSIS_REPORT.md`._

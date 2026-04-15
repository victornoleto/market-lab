# Por que migrar para Tiingo — rationale da ablação de dados

**Status:** planejado. Assinatura Tiingo SF pendente; após assinar, re-rodar
as Execuções 1 (Clenow) e 2 (Ehlers) com dados survivorship-free mantendo
todo o resto constante.

**Contexto:** este doc explica por que a migração de `yfinance` + Wikipedia
scrape para Tiingo (produto SF — survivorship-free) é o próximo experimento
necessário antes de pivotar de estratégia, mudar universe ou declarar
ausência de edge. Consolidado a partir de `specs/backtest_phase2.md`,
`specs/backtest_phase2_5_ehlers.md` e dos dois diagnostic reports em
`reports/grid_*/`.

---

## 1. O que os gates estão dizendo hoje

As duas execuções do grid (Clenow e Ehlers) falharam **pelo mesmo motivo**,
DSR, e **não** por PBO:

| Métrica | Clenow (Execução 1) | Ehlers (Execução 2) |
|---|---|---|
| PBO | 0.524 (falha marginal) | **0.468 (passa)** |
| DSR p-value | 0/30 < 0.05 | 0/24 < 0.05 |
| Best Sharpe annualized | 0.583 | 0.310 |
| E[SR_max] sob null (N≈25, T≈2267) | ~0.86 | ~0.86 |
| Walk-forward | 4/30 pass | 2/24 pass |

O Sharpe máximo observado é **menor que o benchmark do null hypothesis**.
É isso que o DSR está rejeitando.

**Ponto chave:** PBO mede *overfit ao grid* (rankings IS↔OOS). Ehlers passa
PBO folgado — o signal estrutural não é artefato do grid. O que falha é o
teste contra o benchmark-de-acaso. E esse benchmark depende diretamente da
**distribuição dos retornos do dataset**.

---

## 2. Por que a fonte de dados vira variável confundidora

O pipeline atual (`yfinance` + Wikipedia point-in-time) tem dois problemas
documentados nos próprios specs:

### 2.1 Survivorship bias residual (escala linear com o horizonte)

- Janela 6 meses (H2 2023): **17/503 = 3.4%** dos tickers sumiram
  silenciosamente (`reports/clenow_replication_notes.md`).
- Janela 9 anos (2015-2023): **97/506 = 19%**
  (`specs/backtest_phase2.md` §"Grid executado").
- `yfinance` **não serve tickers deslistados** — retorna frame vazio, eles
  saem do universo sem aviso.
- Bug ANDV→MPC 2018 (commit `8d25e65`) só apareceu porque a janela longa
  atravessou uma delistagem real — evidência direta de que o pipeline
  atual trata deslistagens como "ticker nunca existiu".

### 2.2 Efeito composto no DSR

O null hypothesis do DSR (AFML p.222-223) é `E[SR_max(N)] sob iid-null`. Mas
**o "null" é estimado a partir da variância dos retornos observados**. Se
os retornos estão inflados por survivorship (os losers reais sumiram), o
null sobe junto — e o Sharpe "real" fica abaixo dele mesmo quando há edge.

Isto é dito literal em `specs/backtest_phase2.md`:

> **Literal:** yfinance SPX 2015-2023 não tem edge Clenow após gates.
> **Data-hypothesis:** yfinance infla o benchmark SPY... Remover o viés
> pode baixar SPY a ~9% e elevar Clenow a um edge relativo. **Precisa
> paid-data ablation pra saber.**

---

## 3. O que especificamente o Tiingo destrava

Tiingo tem produto **"SF" (Survivorship-Free)** com preço point-in-time de
tickers **incluindo deslistados**. Três coisas mudam mensuravelmente:

1. **O universo a cada rebalance inclui os ~97 tickers perdidos.** No
   Clenow, esses entrariam no ranking momentum nas suas épocas boas *e*
   estariam disponíveis para evitar nas suas quedas pré-delisting. Hoje
   são invisíveis.

2. **A distribuição de retornos OOS ganha a cauda esquerda real.** O
   `E[SR_max]` sob null cai (variância similar, média retorna real) e vira
   um benchmark honesto. Estratégias que hoje empatam com o null podem
   passá-lo.

3. **O benchmark buy-and-hold (SPY) vira comparável.** Hoje Clenow
   (~8.87% CAGR) é comparado contra SPY inflado (~11-12%). Com dados
   clean, SPY real fica ~9% e o edge relativo reaparece.

---

## 4. Por que isso é a ablação certa, não um "seria legal ter"

O **teste científico** aqui é isolar a variável "dados" mantendo tudo o
resto fixo:

- Mesma estratégia (código idêntico)
- Mesmo grid (24 ou 30 configs)
- Mesma janela (2015-2023)
- Mesmos gates (PBO/DSR/WF, thresholds idênticos)
- **Só troca:** `data/yfinance_source.py` → `data/tiingo_source.py`

Resultados possíveis e o que cada um prova:

| Resultado em Tiingo | Conclusão |
|---|---|
| Ehlers e/ou Clenow passam DSR | Edge **era real**, yfinance mascarava. Fase 3 destrava. |
| Ambos ainda falham DSR | Edge **não existe** nessa janela/universo. Pivot para 3ª estratégia (AFML, Chan) ou universe shift fica bem-fundamentado. |
| PBO piora no Ehlers | A estrutura aparente do signal vinha do bias — insight importante por si só. |

Sem a ablação, **é impossível distinguir essas três hipóteses**. Com ela,
qualquer decisão-fork fica defensável.

---

## 5. Custo do experimento vs. alternativas

Forks mapeados em `specs/backtest_phase2_5_ehlers.md` §Task 5, comparados
concretamente:

| Fork | Custo | Informação ganha |
|---|---|---|
| **1. Tiingo SF ablation** | 2-3 dias integração + free-trial/assinatura | **Decisiva**: resolve ambiguidade dados-vs-edge |
| 2. 3ª estratégia (AFML/Chan) | 1-2 semanas | Baixa — N-penalty cumulativo (4 estratégias × 25 configs = DSR pior) |
| 3. Regime-aware portfolio Clenow+Ehlers | Baixo (reuso) | Limitada — se cada um é null, a soma também é |
| 4. Parar | Zero | Nenhuma |

**A opção 1 é a única que muda a pergunta**, não a tentativa-n-de-responder
à mesma. Todas as outras três assumem que os dados atuais são verdade-solo;
a 1 questiona a premissa.

---

## 6. Plano de execução pós-assinatura

1. **Integração do data source.** Criar
   `src/ai_trade/backtest/data/tiingo_source.py` replicando a interface de
   `YFinanceSource` (`fetch_many(symbols, start, end) → dict[str, pd.DataFrame]`
   OHLCV + cache parquet). Manter marker survivorship-free para que o
   disclaimer do report se ajuste automaticamente.
2. **Universe point-in-time.** Tiingo expõe constituintes históricos
   próprios — substituir `wikipedia_spx` por fonte nativa Tiingo. Pular
   o algoritmo undo-changes-walking-backwards.
3. **Re-rodar Clenow grid** (mesmos 30 configs, `2015-01-01 → 2023-12-31`,
   `scripts/run_grid_clenow.py`) apontando para o novo source. Wallclock
   esperado: similar à Execução 1 (~15min com n_jobs=4).
4. **Re-rodar Ehlers grid** (mesmos 24 configs, mesma janela,
   `scripts/run_grid_ehlers.py`). Wallclock esperado: ~3s (single-instrument).
5. **Registrar resultados inline** em `specs/backtest_phase2_5_ehlers.md`
   §"Execução — resultados e fork" (criar sub-seção "Execução 3 — Tiingo
   ablation") e `specs/backtest_phase2.md` §"Fase 2.5/3 — Execução 1"
   (sub-seção análoga).
6. **Decidir o fork** baseado no resultado — as três branches em §4 deste
   doc são mutuamente exclusivas.

---

## 7. Referências

- `specs/backtest_phase2.md` — spec da Fase 2 + Execução 1 (Clenow grid)
- `specs/backtest_phase2_5_ehlers.md` — spec da Execução 2 (Ehlers grid)
- `reports/clenow_replication_notes.md` — single-trial H2 2023, 17 pulados
- `reports/ehlers_replication_notes.md` — single-instrument ^GSPC 2022-2023
- `reports/grid_20260414-1813/diagnostic.md` — Execução 1 fail (PBO+DSR)
- `reports/grid_ehlers_20260414-1944/diagnostic.md` — Execução 2 fail (DSR)
- `src/ai_trade/backtest/data/yfinance_source.py` — data source a ser
  espelhado pelo `tiingo_source.py`
- `src/ai_trade/backtest/validation/dsr.py` — implementação AFML p.222-223

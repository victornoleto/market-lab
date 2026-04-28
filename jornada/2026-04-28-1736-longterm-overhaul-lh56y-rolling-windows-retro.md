# Long-Term Portfolio loop: overhaul pós-iter-011 — janelas longas, plots, e retro

**Data:** 2026-04-28 17:36
**Branch:** `bestfolio-hunt/iter-001`
**Status:** Pronto para retomar a busca além da iter 011.

## Por quê isso aconteceu

A iter 011 fechou a busca declarando o NTSX+GDE+KMLM (35/25/40) como
WINNER em 91/100 pontos. Mas três coisas incomodavam o usuário:

1. **O backtest "principal" só ia de 1995 pra frente.** A janela
   `educational` (31 anos) capturou 2000 e 2008, mas perdeu o crash de
   1973-74, a inflação Volcker 80-82, e o crash 87. Sem essas, "robusto
   em crises" é uma promessa não testada.
2. **Os plots eram dois arquivos por iter, cada um comparando contra UM
   benchmark (VT ou NDX).** O usuário queria ver SPY + VT + NDX juntos
   no mesmo gráfico, com sub-painéis mostrando como a estratégia ficou
   à frente ou atrás de cada um ao longo do tempo. Mais: queria saber
   "em janelas rolantes de 3, 5, 10, 15, 20, 30 anos, quantas vezes a
   estratégia bate cada benchmark". O formato antigo não respondia isso.
3. **A iter 011 só foi comparada contra avg(SPY,VT) na sua própria
   janela.** Sem tirar prova com as 10 iters anteriores no mesmo
   contexto longo, o "winner" carrega um asterisco.

E o usuário deixou claro que essa é a última coisa antes de continuar
o loop: o tema central é **"exposição global + fatores"**, e a iter 011
não tem nem um nem outro — é 100% USA + ouro + managed futures.

## O que foi feito

### 1. Dataset novo: `lh_56y` (Long-History 56 anos)

Criada `studies/long_term_portfolio/datasets.py` como registro central
das janelas. A nova `lh_56y` cobre **1970-01-02 → 2026-04-24**, usando
as séries sintéticas do testfol.io que já estavam em
`data/testfolio/cache/history.parquet`: VTSIM (1969+), GDESIM (1968+),
IEFSIM/TLTSIM (1962+), VTISIM/VBRSIM (1926+).

Problema: **KMLMSIM só começa em 1987-12-31** (KFA MLM Index inception).
Para estratégias que usam KMLM (incluindo a iter 011 winner), os ~18
anos pré-1988 ficavam vazios. Decisão (com o usuário): preencher esse
gap com o **fator momentum diário do Ken French (UMD + Rf)** — a
referência acadêmica padrão pra "tendência/momentum" pré-ETFs.
Baixei o CSV oficial (`F-F_Momentum_Factor_daily.csv`) pra
`data/ken_french/` e construí o emendamento contínuo da equity curve em
`studies/long_term_portfolio/ff_momentum_proxy.py`.

**Caveat honesto:** UMD é momentum cross-sectional de equity — não é
multi-asset trend igual KMLM. O Sharpe do UMD em 1970-1987 deu **1.90**,
muito acima do ~0.5 histórico do KMLM real. Então o pedaço pré-1988 de
qualquer estratégia que tenha KMLM **superestima retorno em ~3×**. Tá
documentado em `INFRASTRUCTURE.md`, no `PROMPT.md`, e em todos os
relatórios de iter daqui pra frente.

### 2. Plots redesenhados (1 figura por dataset, com sub-painéis)

`plot_helper.py` foi reescrito. Antes: 2 PNGs por iter
(`plot_vs_benchmark_vt_real.png` + `plot_vs_benchmark_ndx_real.png`,
cada um com 2 painéis). Depois: **2 PNGs por dataset (4 datasets =
8 PNGs por iter)**:

- `plot_<dataset>.png`: painel grande no topo com **estratégia + SPY +
  VT + NDX** (4 linhas, escala log) e três sub-painéis embaixo
  mostrando o **rolling 1-ano Sharpe Δ** vs cada benchmark
  individualmente. Laranja quando estratégia tá na frente, azul quando
  tá atrás.
- `plot_rolling_windows_<dataset>.png`: até 6 mini-gráficos (3, 5, 10,
  15, 20, 30 anos) mostrando o Sharpe rolling em cada janela, com
  legenda "X% das janelas a estratégia bateu Y benchmark". Janelas que
  não cabem (ex: 30 anos em 17 anos de dados) ficam em branco.

### 3. Re-backtest retroativo de 001-010

Ferramenta nova `retro_rebacktest.py`: importa o módulo de cada iter,
calcula a primeira data em que TODOS os tickers necessários têm dados
(varia por iter — a iter 011 começa em 1986-01-02 porque depende de
SPYSIM; HAA's começam em 1994-05-04 porque dependem de VWOSIM),
patcheia o `DATASETS` da iter pra adicionar `lh_56y`, e roda só essa
parte. Mescla o resultado em `results.json` sem sobrescrever o que já
estava lá.

Funcionou nas 11 iters. Os PNGs novos foram regerados pras 11 (88
arquivos no total).

### 4. Surpresa do retro: a iter 011 NÃO domina o lh_56y

| iter | slug | lh_56y gross Sharpe | janela efetiva |
|---|---|---:|---|
| 005 | haa-rsst-rssb-cta | **1.253** | 1994-2026 (32y) |
| 010 | haa-vol-throttle | 1.179 | 1994-2026 (32y) |
| 006 | haa-rsit-synth | 1.154 | 1994-2026 (32y) |
| 007 | haa-defensive-kmlm-cash | 1.150 | 1994-2026 (32y) |
| 004 | haa-global-factor-tilt | 1.117 | 1994-2026 (32y) |
| 008/009 | haa-dual-canary / haa-gayed | 1.120 | 1994-2026 (32y) |
| 001 | baa-g12-balanced | 1.094 | 1995-2026 (31y) |
| **011** | **ntsx-gde-kmlm-static** | **1.046** | **1986-2026 (40y)** |

Cinco iters anteriores (004, 005, 006, 007, 010) batem a iter 011 em
Sharpe gross no `lh_56y`. **Mas** a comparação não é apples-to-apples:
a iter 011 roda 40 anos (8 a mais que as HAA-style), incluindo o
crash de 1987 (que ela atravessa muito bem). E o pedaço 1986-1994 do
KMLM dela usa proxy FF-MoM que infla Sharpe ~3×. Aplicada a mesma
janela 1994-2026, a iter 011 provavelmente fica próxima das HAA's, não
acima.

**Conclusão prática:** a iter 011 segue como **incumbent winner**
(o que tem que ser batido), mas não é tão dominante quanto parecia.
Há espaço real pra um candidato global+fator superá-la.

### 5. Loop liberado pra continuar

Frontmatter de `BASE_MEMORY.md` mudou de `status: winner` →
`status: hunting`, com novos campos:

- `incumbent_winner_iter: 011-2026-04-28-1537-ntsx-gde-kmlm-static`
- `incumbent_winner_score: 91`
- `latest_score: 91` (a próxima iter atualiza)
- `beats_incumbent: false` (a próxima iter seta `true` se score > 91
  OU edge ≥ +0.10 em ≥2 datasets vs iter 011)

`run_loop.sh` lê esses campos: para imediatamente quando uma iter
nova setar `beats_incumbent: true`, OR quando alguém volta a usar
`status: winner` (compatibilidade legacy). Caso contrário continua até
`MAX_ITER`.

`PROMPT.md` ganhou:
- Mandato de usar `datasets.load_prices(name)` em vez de hardcode de
  janelas.
- Lista de prioridades pras próximas ~5 iters (rewrite do "Promising
  unexplored directions" em `BASE_MEMORY.md`):
  1. **NTSX + NTSI + NTSE + GDE + KMLM** (5-asset global capital-eficiente)
  2. **NTSX + GDE + RSSB + KMLM** (RSSB = global stocks + bonds stacked)
  3. **NTSX + VXUS overlay + GDE + KMLM** (intl tilt sem mais leverage)
  4. **iter 011 base + AVUV + AVDV** (tilt small-cap value)
  5. **iter 011 + UMD overlay** (fator momentum direto)
  6. **NTSX + GDE + KMLM + AVUV + AVDV** (híbrido fator + capital-eficiente)

## O que vem a seguir

Próxima iter (012) começa o ataque pelo plano A (global capital-eficiente)
ou plano B (factor tilts) acima, na decisão do prompter. Loop habilitado;
basta rodar:

```bash
MAX_ITER=10 bash studies/long_term_portfolio/run_loop.sh
```

Se uma iter setar `beats_incumbent: true`, o loop para e a iter vira
o novo incumbent. Caso contrário, vai até MAX_ITER e o usuário decide
se aumenta budget ou para.

## Glossário (entradas novas pro README.md)

- **lh_56y**: dataset histórico longo (1970-2026, 56 anos) usando
  séries sintéticas do testfol.io. Substitui o nome `educational` que
  era ambíguo (benchmark já era 56y mas o backtest era cortado em 1995
  por causa de KMLM).
- **FF MoM proxy**: emendamento da série KMLMSIM com o fator momentum
  diário Fama-French (UMD + Rf) pra cobrir 1970-1987 quando KMLMSIM
  ainda não existia. Caveat: UMD é equity, não multi-asset; superestima
  Sharpe pré-1988 ~3×.
- **Incumbent winner**: a iter "campeã" atual que precisa ser batida.
  iter 011 é a incumbent até que outra iter mostre `beats_incumbent: true`
  (score > 91 OU edge ≥ +0.10 em ≥2 datasets).
- **Rolling-windows comparison**: em vez de UM Sharpe pra toda a
  história, divide em janelas rolantes (3/5/10/15/20/30 anos) e
  pergunta "em quantas dessas janelas a estratégia bate o benchmark".
  Diagnóstico mais honesto pra robustez do que um Sharpe agregado.

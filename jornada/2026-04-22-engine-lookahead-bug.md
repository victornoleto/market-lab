# O bug da engine — apostar em cara depois de ver a moeda cair

**Data:** 2026-04-22
**Fase:** 3.5f (F0-F2 fechadas, F3 fechada, F4 em execução)
**Branch:** `phase3.5f/plano-a-v2-l2-cross-lib-redo-20260422`
**Status:** engine consertada, 918 testes verdes, re-validação do Plano A concluída.

---

## A analogia que importa

Imagina que você tá apostando em cara-ou-coroa, mas com uma regra
estranha: você só registra sua aposta depois da moeda cair no chão. Se
cair cara, você "aposta" cara; se cair coroa, você "aposta" coroa.
Perfeito — **100% de acerto**. Uma máquina de impressão de dinheiro.

O problema, claro, é que não é aposta nenhuma. Você não está prevendo
nada; está só registrando o passado com a etiqueta de "previsão".

Pois bem: foi exatamente isso que a engine canonical do Plano A
(`plano_a_leveraged_rotation.py`) fazia há semanas, no motor do backtest.
Não por má-fé, por uma linha de código infeliz.

## Onde o bug morava

Dentro do loop que simula cada dia do backtest, a engine fazia:

1. **Lê o preço de fechamento do dia de hoje** (`close[i]`).
2. **Calcula o sinal de regime com esse mesmo preço de hoje** (EMA-100
   do `close[i]`, e se `close[i] > EMA → regime ON`).
3. **Decide o peso do portfolio hoje com base nesse sinal.**
4. **Multiplica esse peso por `return[i]` — que é `close[i] / close[i-1] - 1`.**

O problema é o passo 4. O `return[i]` é justamente o movimento que
*criou* o `close[i]` no passo 1. Multiplicando "o peso que eu escolhi
depois de ver o resultado" × "o resultado em si", o backtest te
entrega, de graça, a gain-do-dia como se você tivesse previsto ela.

O jeito correto (três livrarias independentes de backtest fazem assim,
todos os livros do AFML `[advances_fin_ml, p.31-34]` descrevem assim)
é: **peso decidido ontem × retorno de hoje**. `prev_w[i] × ret[i]`.
Em Python, é literalmente um `.shift(1)` no vetor de pesos. Uma linha.

## Como o bug foi pego

Ele se escondeu porque todos os gates — PBO, DSR, walk-forward,
bootstrap — **avaliavam a própria engine com ela mesma**. Se a engine
diz que o retorno é 79% ao ano OOS, o bootstrap sobre 10,000 amostras
diz que os 79% são estatisticamente robustos. Não porque sejam
verdadeiros: porque são *consistentes dentro da mentira*.

O que pegou o bug foi a Phase 3.5f cross-lib. A ideia era mundana:
"vamos replicar o backtest em `bt`, `vectorbt` e `backtrader` (três
libs feitas por três times independentes, todas adultas) e garantir
que concordam com a nossa canonical dentro de ±3pp de CAGR."

Resultado:

| Método | CAGR OOS |
|---|---:|
| Canonical (buggy) | 91.95% |
| Numpy reference (shift correto) | 20.79% |
| bt | 20.79% |
| vectorbt | 20.79% |
| backtrader | 20.79% |

Três libs + uma implementação manual em numpy batem entre si até a
quarta casa decimal. A canonical sozinha fica ~71 pontos percentuais
acima. **Só há um jeito disso acontecer: a canonical está errada.**

O flag vermelho inicial não foi uma discrepância pequena — foi um
fator de ~19,000× em equity final ao longo de 25 anos (canonical
660,440× vs libs 34.8×). Nenhum ajuste de custo ou de definição de
janela explica dois ordens de magnitude. Algo na matemática estava
comendo pelas beiradas.

E quando a gente olhou a matemática, era o `w_i × r_i` de sempre,
clássico de literatura `[advances_fin_ml, p.31-34]`.

## O que o bug custou numericamente

O "winner" V2-L2 `gayed_ema100_L2_off_gld` tinha estas métricas
publicadas em 2026-04-19:

| Split | Sharpe | CAGR | MaxDD |
|---|---:|---:|---:|
| IS (2001-2017) | 1.856 | 53.42% | −22.67% |
| **OOS (2018-2023)** | **2.284** | **79.14%** | **−21.02%** |
| FWD (2024-2026) | 1.821 | 59.28% | −17.35% |

Honest (post-fix) no mesmo periodo e mesma config:

- OOS Sharpe cai de 2.28 → ~0.56
- OOS CAGR cai de 79.14% → ~14.29% (com `adj_close` TR; ~12.58% com
  raw close)
- OOS MDD piora de −21% → −37%

Ou seja: **~65 pontos percentuais de CAGR eram look-ahead.** A
estratégia subjacente (Gayed regime rotation) tem edge modesto —
~14%/ano é comparável ao CDI BR, mas com drawdown pior que passivo.
Não é winner sob o mandate §2 (que exige gross acima de CDI com
leverage).

## A boa notícia — o raio foi pequeno

A primeira reação (antes de auditar o código) foi: "meu Deus, quantos
reports precisam ser retratados?" O plano §1.4 supunha que a bug era
mais ampla, que `letf_rotation.py` (engine do Plano B) também estava
infectada.

F1 grep-auditou o código inteiro. **Só um arquivo, uma linha** tinha o
padrão `w_i × r_i`: `plano_a_leveraged_rotation.py:462`. O resto das
engines (TSMOM, AFML, Kalman, Donchian, letf_rotation,
tsmom_multi_asset) já usava a convenção correta, ou usava só um ativo
(sem vetor de pesos, sem como introduzir o viés).

Isso significa:

- Reports **tainted** (ganham banner forensic): `phase3_5a_v2/v2_l2_*`,
  `phase3_5a_v2/v2_l4_*` (parcial, ver abaixo), `phase4_0/index_cfd_*`.
- Reports **limpos** (preservados como canonical): todo `phase_3_5b/*`,
  `phase_3_5c/*`, `phase_3_5d/*`, `phase_3_5e/*` (Plano B, 38 trials,
  Plano B V4 rejection, Plano B 3× LETF — tudo limpo).

A surpresa dentro da surpresa: V2-L4 Carver RP *tinha* o sleeve do L2
no blend, mas o peso real dele na parity (derivado da volatilidade IS
de cada lead) era **4.8%**, não os 66-75% que o plano tinha chutado.
A contaminação foi ínfima. O blend falha pelo motivo certo: L3 (66% do
risco) tem CAGR de 2.5%/ano, o que arrasta o blend pra baixo
independente do L2 estar certo ou errado.

## Os testes cirúrgicos

A fase F0 escreveu 4 testes em `tests/test_plano_a_lookahead_bias.py`
cujos números esperados um humano pode verificar no lápis:

1. **Flat-price com salto único.** Preço constante → pula +5% no bar
   200 → constante de novo. Honest: retorno cumulativo ≈ 0% (o salto
   acontece justamente no bar que o sinal liga — peso OFF ainda
   vigente captura GLD flat, então nada). Buggy: retorno ≈ +10% (o
   peso ON captura o próprio salto que o disparou).
2. **Flip único isolado.** Injeta +3% no bar 100 e +1% no bar 101,
   sinal liga ON no close do 100. Honest: pnl(100) = 0, pnl(101) = 0.01.
   Buggy: pnl(100) = 0.03 (o flip captura o salto que o criou).
3. **Flipper simétrico.** Regime alterna a cada N bars em série
   simétrica. Honest: ganhos e perdas se anulam. Buggy: ganhos se
   concentram nos dias de flip.
4. **Cross-lib determinístico.** 200 bars, pesos pré-especificados →
   canonical = bt = vectorbt dentro de 1e-6.

Todos 4 falhavam contra a engine buggy em direções específicas.
Todos 4 passam contra a engine post-F2. Isso é o registro auditável
de que o fix funcionou, não um "a gente rodou de novo e deu
diferente".

## O que fica de aprendizado

1. **Dependência circular no validation stack.** PBO, DSR, bootstrap
   e walk-forward todos usavam a mesma engine que estavam validando.
   Nenhum pegou o bug porque nenhum *podia* pegar — a aritmética
   interna estava consistente. O que pegou foi concordância com
   implementação externa independente. **Lição:** cross-lib
   concordance não é só uma robustness check; é um sanity check
   lógico que nenhum outro gate substitui.

2. **Surface grep engana.** O plan §1.4 suspeitou de
   `letf_rotation.py` por um grep superficial. F1 teve que ler linha
   por linha pra confirmar que o pattern estava em um arquivo só.
   Lição: ao auditar bias, não confie no grep — leia o loop inteiro.

3. **Magnitude do bug ≠ dano estatístico.** Um bug "pequeno" (uma
   linha, um `.shift`) criou 65pp de CAGR artificial em 25 anos.
   Zero warning, zero teste vermelho, gates todos verdes. A validation
   machinery do Plano A (6 meses de trabalho) passou inteira por
   cima de um erro de indexação.

---

## Referências

- `[advances_fin_ml, p.31-34]` — definição canônica de look-ahead bias
  e convenção shift.
- `docs/plans/2026-04-22-engine-lookahead-fix-and-plano-a-winner-hunt.md`
  — plano executável de 5 fases (F0-F4).
- `docs/superpowers/findings/2026-04-22-engine-lookahead-scope.md` —
  inventário file-by-file do raio do bug.
- `docs/superpowers/findings/2026-04-22-engine-lookahead-confirmation.md`
  — detalhamento técnico dos 4 testes cirúrgicos.
- `reports/phase_3_5f/honest_revalidation/BREADTH_SUMMARY.md` —
  veredito das 6 leads sob engine honest.
- `tests/test_plano_a_lookahead_bias.py` — os 4 testes.
- Commit da fix: `7b90a8f` (`fix(backtest): shift weight×return
  alignment to remove lookahead bias`).

---

**Sequência de leitura recomendada:**

1. Este documento (narrativa do bug em si).
2. `jornada/2026-04-22-plano-a-honest-revalidation.md` — o que
   aconteceu com as 6 leads depois do fix.
3. `jornada/2026-04-23-0700-overnight-summary.md` — sumário final
   com as 4 opções pro usuário decidir.

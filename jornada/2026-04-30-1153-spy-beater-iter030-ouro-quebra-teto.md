# spy_beater iter 030 — ouro como gate quebrou o teto que durava 9 iters

**Quando**: 2026-04-30, iter 030 do spy_beater_hunt.

**Resumo curto**: Pela primeira vez em 9 iterações sequenciais no eixo
meta-ensemble (iters 022→029), uma config superou o teto histórico de
71 pontos. O h10.4 conseguiu **72/100** trocando o sinal do 4º
constituinte — antes era TSMOM no QQQ, agora é TSMOM no ouro (GLDSIM)
com a mesma janela de 6 meses.

**Por quê isso importa**: durante 9 iterações o hunt estava
"saturado" — qualquer mudança que tentávamos (lookback 3m/12m, troca
de constituinte, peso simétrico, posição invertida) terminava
empatando ou perdendo contra a baseline iter 026 H6.4 = 71. A intuição
acumulada era que o teto seria definitivo e o hunt deveria ser
declarado encerrado com F1+SPLIT como deploy fallback. **Iter 030
empiricamente refutou isso**: ao trocar a fonte do sinal de "tendência
do NASDAQ" para "tendência do ouro" no 4º constituinte, o blend ganhou
+0.62pp de CAGR e +0.076 de Sharpe (a 20% de peso) e atingiu 72/100
(a 25% de peso, com Sharpe 1.039 e CAGR 16.59% — **novo melhor CAGR
de toda a hunt em 30 iters / 116 trials**).

**O que isso significa em linguagem humana**: o sinal de ouro
desliga/liga o constituinte em momentos diferentes do sinal de ações.
Quando todos os outros 3 constituintes (A2 = sinal QQQ, G2 = sinal
SPY, F1 = sempre ligado) estão ligados ou desligados juntos por causa
do regime de ações, o constituinte com sinal de ouro fica ligado/
desligado por um motivo independente — adicionando uma classe de ativo
ortogonal à "votação" do ensemble. É o mesmo princípio do iter 026
(diversidade de fonte do gate vale +1pt no blend de 4) mas levado pra
um nível além: não é só fonte diferente, é **classe de ativo
diferente**. Esquisito, contraintuitivo (Faber sempre pareou cada
sinal com seu próprio ativo na GTAA), mas o backtest mostra: trabalha
melhor.

**Caveat honesto**: usar tendência de ouro pra gatear um sleeve de
TQQQ (ações de tecnologia alavancado) é uma escolha que nenhum livro
canônico recomenda. O DSR Bonferroni passa com folga 6.6× (melhor
margem desde iter 026), o PBO continua estável, MDD por dataset é
idêntico (sinal de robustez vs 2008 GFC dominante). Mas a ausência de
literatura precedente significa que o resultado pode degradar fora
da amostra. Antes de qualquer pedido de override do mandate §7
(deploy real), iter 031 vai testar variantes adjacentes — outros
sinais ortogonais (commodity broad DBC, FX USDJPY, taxa TLT) e outros
lookbacks no ouro (3m/9m/12m) — pra confirmar se o achado é robusto
ou se é overfitting de signal-asset específico.

**Status**: hunt **REOPENED** no eixo signal-asset. closest-to-winner
mudou de iter 019 H2 (71, segurando precedência desde iter 019, 11
iters atrás) pra iter 030 H10.4 (72). Mandate §1 100% Plano C
INALTERADO — research only. F1+SPLIT continua deploy fallback até
validação OOS de iter 031+.

**Glossário** (termos novos):
- **Signal-asset axis**: eixo arquitetural que varia o ativo cuja
  tendência é monitorada pelo gate (QQQ vs SPY vs GLD), mantendo o
  sleeve subjacente (o ETF que de fato compra/vende) constante.
- **Gate-source-distinctness**: princípio empírico (iter 026 KILL #102)
  de que, num blend 4-way, o 4º constituinte ganha +1pt de score se
  seu gate usa sinal distinto dos outros 3.
- **Asset-class-orthogonal**: extensão de "distinctness" pra incluir
  diferentes classes de ativo (ações vs ouro vs commodity vs FX), não
  só diferentes tickers da mesma classe.
- **Signal-sleeve incoherence**: quando o sinal do gate (ex: tendência
  do ouro) não bate com o ativo do sleeve (ex: tech leverage). Iter 030
  mostrou que isso pode ser benéfico, não prejudicial.

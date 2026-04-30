# spy_beater iter 031 — ouro também tem pico de lookback em 6m

**Quando**: 2026-04-30, iter 031 do spy_beater_hunt.

**Resumo curto**: Iter 030 mostrou que trocar o sinal do 4º constituinte
de QQQ pra ouro (GLDSIM) com janela de 6 meses subiu o teto de 71 pra
72 pontos — primeiro furo em 9 iters seguidos. A pergunta natural: e se
mudar a janela do sinal-ouro pra 3m/9m/12m? A teoria diz que ouro tem
volatilidade menor (~14-18%) que QQQ (~22-28%), então tendências de
ouro deveriam ser mais lentas e a janela ótima poderia ser **mais
longa**. Iter 031 testou exatamente isso. Resultado: **falsificou a
hipótese**. O pico continua em 6m pra ambos os sinais (QQQ no iter 029,
ouro no iter 031), e o teto fica em 72.

**Por quê isso importa**: o iter 030 quebrou o teto fazendo duas coisas
ao mesmo tempo — sinal ortogonal de classe de ativo (ouro vs ações) E
janela de 6m (pico do U-invertido descoberto no iter 029). A pergunta
do iter 031 era: o bônus de +1pt do iter 030 vem do sinal-ouro **em
qualquer lookback** ou só **no lookback ótimo**? **Veredito**: só no
ótimo. As 4 variantes 3m/6m/9m/12m do GLD-TSMOM no 4º slot ficaram
todas na faixa 70-72 pontos. Apenas a 6m bate 72; as outras voltam pro
nível 71 que era o teto pré-iter-030. O bônus de ortogonalidade
**está acoplado ao pico de lookback**, não é universal.

**O que isso significa em linguagem humana**: o achado do iter 030 não
generaliza pra "qualquer ativo ortogonal vai gerar +1pt em qualquer
janela". O furo do teto exige acerto em **dois eixos simultaneamente**:
sinal de classe de ativo diferente (eixo do iter 030) E janela perto
de 6m (eixo do iter 029). Se mexer só num dos dois, perde o bônus. Isso
fortalece a hipótese de que o teto 72 é estrutural — pra subir mais,
precisaria atacar um eixo arquitetural ainda não testado, não só
variar parâmetros adjacentes.

**Curiosidade do iter 031**: a config GLD-TSMOM-12m (h11.4) não bateu
72, mas entregou o **menor MDD médio da hunt inteira** em 31 iters /
120 trials: **29.51%** (vs iter 030 H10.4 com 33.77%). O MDD melhora
4.26pp, o CAGR cai 0.48pp, o Sharpe cai 0.035 — mas o score final
fica empatado em ~71-72 porque a faixa do MDD-anchor [70%, 15%] não
cruza o sub-bucket nessa magnitude. Sob ranking ponderado por MDD
(mandate §2.2 trata MDD como tier warning-only), h11.4 12m pode ser
**preferível** ao h11.2 6m apesar do score igual.

**Caveat honesto**: replicação foi 100% precisa — h11.2 6m bateu
exatamente os mesmos números do iter 030 H10.4 (Sharpe 1.041/1.037,
CAGR 17.03%/16.14%, MDD 33.77% idêntico nos dois datasets). Isso
confirma que a medição do iter 030 era reproduzível, não artefato.
Mas também confirma que o teto não foi quebrado — só empatado.

**Status**: closest-to-winner **inalterado** (iter 030 H10.4 segura por
precedência, 5 trials antes). Hunt's empirical informational value
plateauou de novo no iter 031. Mandate §1 100% Plano C inalterado —
research only. F1+SPLIT continua deploy fallback. iter 030's furo do
teto agora é confirmado como **single-axis specific** (joint signal-
asset × lookback peak), não extensível por variação de eixo único.

**Glossário** (termos do iter 030 reutilizados, sem novos):
- **Lookback inverted-U**: padrão empírico (iter 029 KILL #119) onde o
  score forma um U-invertido em função da janela do sinal momentum,
  com pico em ~6m (3m whippy demais, 12m delay-exit).
- **Asset-invariant lookback peak**: novo achado iter 031 — o pico do
  U-invertido fica em 6m **independente** do ativo do sinal (QQQ ou
  ouro). A hipótese iter 029 de que "ativo de menor vol → janela
  ótima maior" foi falsificada pra par QQQ/ouro.
- **Joint optimum**: configuração ótima que requer dois eixos próximos
  do ótimo simultaneamente — pra furar o teto 72 precisa de sinal
  ortogonal (eixo iter 030) E lookback 6m (eixo iter 029). Mexer só
  num eixo perde o bônus.

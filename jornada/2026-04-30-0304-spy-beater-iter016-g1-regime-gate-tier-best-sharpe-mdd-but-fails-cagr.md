# Iter 016 — Adicionar gate ao melhor portfolio achou novos recordes de Sharpe e MDD, mas falhou na CAGR

Continuação do spy_beater_hunt (que está fechado pela iter 011 mas seguimos
fazendo sanity-checks da arquitetura). Iter 016 testou a "G1": pegamos a
F1 Levered All-Weather (NTSX 35 + GDE 30 + TLT 20 + KMLM 15, score 61 no
iter 015) e adicionamos um filtro de regime — só fica 100% nessa carteira
quando SPY está acima da média móvel de 200 dias; quando bear, vai pra
defensivo (testamos 3 defensivos: 100% IEF, 100% KMLM, 50/50).

Resultado é um ponto fora da curva: o gate **adicionou** Sharpe (de 1.018
da F1 pura para 1.080 — recorde absoluto da hunt), reduziu MDD de 26.82%
para 18.57% (também recorde absoluto, derrubou 16pp o anterior), e foi
o primeiro config a passar 7/7 gates em ambos os datasets. Mas o gate
**custou 1.61pp de CAGR** (de 11.95% pra 10.34%), o que faz a estratégia
falhar na barra de CAGR (≥ 11.21%) por 0.87pp. Score final = 61, mesmo
da F1 pura, com perfil de barras invertido (F1 passou todas, G1 falha CAGR).

A descoberta surpresa é que o iter 014 tinha mostrado que adicionar gate
sobre LETF 3× **piorava** o Sharpe (decay durante ON consome o ganho de
MDD). No iter 016 — leverage stack 1.41× sem decay — o gate **melhora**
Sharpe. A interação gate × sleeve é assimétrica entre regimes de decay,
mas em ambos a soma cross-product fica abaixo do melhor single-axis. KILL
#33 (teto arquitetural em 67) generaliza e fica reforçado: agora "8
famílias + 2 hybrids", taxonomia formal estruturalmente completa.

Outra descoberta inesperada: a F1 pura batia SPY em 100% das janelas
rolantes de 20 anos; a G1 com gate cai pra 0% — adicionar gate destrói
a propriedade de longo-prazo. Sempre-on diversificado captura bull
rallies que o gate perde. Fica claro que a F1+SPLIT (já em deploy) é
estruturalmente melhor sem gate.

A G1 IEF teria sido WINNER sob qualquer rubric não-CAGR-anchored, então
agora há **dois** configs (F1 + G1 IEF) com Sharpe e MDD recorde da hunt
ambos travando em score 61 — caso para revisão do mandate §7 do rubric
ficou mais forte. Hunt segue CLOSED, F1+SPLIT confirmado deploy. Mandate
§1 100% Plano C unchanged. cumulative_n_trials = 50, worst DSR p = 1.47e-05.
765 testes preservados (nenhum módulo novo).

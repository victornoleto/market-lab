# MyFxBook v4 task 006 — correcao apos validacao STOP

A validacao da task 006 encontrou dois bloqueios: `--enable-pre-screen` ainda
permitia continuar quando `decision=STOP`, e o batch `run_replicator_batch.py`
nao tinha as flags da Fase 1. Corrigi a semantica para o pre-screen abortar cedo
por padrao quando rejeita um EA, gravando `PRE_SCREEN_STOP` e a mensagem "EA
rejeitado pelo pre-screen". Isso evita gastar compute decodificando track records
que falham os gates iniciais `[evidence_based_ta, p.325-328]`.

Tambem adicionei `--enable-pre-screen` e `--enable-adversarial` ao batch. O resumo
agregado agora registra `pre_screen_decision`, caminho/notas do pre-screen e, quando
ativo, os campos do adversarial real-vs-synthetic (`adversarial_auc`, CI 95%, top
features e notas) `[advances_fin_ml, ch.5]`.

Verificacao focada: `tests/myfxbook_pipeline` passou com 38 pass / 4 skip. Plano C
e mandate seguem inalterados; sem paper/live e sem `frozen_rules/`.

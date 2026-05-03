# MyFxBook reverse-engineering — R1 promovido para frozen_rules v3

O estudo MyFxBook concluiu a promocao R1: 30 rules re-decodificadas foram auditadas contra o manifest pre-R1, todas mudaram SHA, e todas passaram a taxonomia strict. `frozen_rules/` agora tem 30 arquivos v3 read-only; o backup pre-promocao ficou em `frozen_rules/_pre_v3_R1_2026-05-03T0000Z/`.

O resultado limpa o contrato semantico, mas nao prova replicabilidade nem edge. Dois pause gates ficaram abertos antes da proxima fase: `NEWS_RELEASE_MOMENTUM` ainda tem suporte n=1 e 13/30 systems precisam `needs_m1_review`. Capital segue 100% Plano C; Plano A permanece DORMANT.

Proximo passo somente com aprovacao explicita: fase Python deterministica 5R-1 replicator/comparator/score.

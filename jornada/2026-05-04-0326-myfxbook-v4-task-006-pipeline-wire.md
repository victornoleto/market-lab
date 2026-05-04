# MyFxBook v4 task 006 — Fase 1 plugada no pipeline

Conectei os modulos da Fase 1 ao pipeline single-system do MyFxBook v4. A CLI
agora aceita `--enable-pre-screen`, `--enable-adversarial`, `--system-id` e
`--out-dir`, preservando o comportamento antigo quando nenhuma flag nova e usada.

No smoke obrigatorio com o system `1407880`, o pre-screen passou (`decision=GO`)
e registrou que a conta e Demo como warning-only. Isso preserva a decisao do
redesign: Demo nao bloqueia material decodavel nesta fase; Plano A continua
DORMANT e sem paper/live. O adversarial validator retornou `AUC=1.0`, ou seja,
o synthetic ficou trivialmente distinguivel do real; isso e diagnostico ruim para
decode, nao uma estrategia. A validacao segue a semantica de classificador
real-vs-synthetic `[advances_fin_ml, ch.5]`.

Tambem promovi o veredito agregado `mandate_24_pass` ao output quando as flags
Fase 1 estao ativas. Em `1407880`, o synthetic falhou `sharpe_bootstrap_ci_low_999`,
`oos_bootstrap_ci_low_999` e `dsr_p`; DSR e hard gate `[advances_fin_ml, p.273-275]`.
PBO segue opcional nesta fase porque `cpcv_result` so aparece depois do mining
Fase 2B `[advances_fin_ml, p.208-222]`.

Verificacoes: `tests/myfxbook_pipeline` passou com 36 pass / 4 skip; baseline
geral ficou em 799 pass / 14 skip / 3 falhas preexistentes de cache macro ausente.
Proxima sessao: task 007, batch Fase 1 nos systems disponiveis para montar a lista
de sobreviventes.

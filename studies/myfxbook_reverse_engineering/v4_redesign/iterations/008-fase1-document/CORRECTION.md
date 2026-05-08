# CORRECTION — 008-fase1-document state-management STOP

## Problema

A validacao bloqueante apos a task 008 encontrou que `next_prompt.md` dizia para
nao iniciar task 009, mas `PROGRESS.md` ainda deixava `009-news-calendar` elegivel:
`009` estava `PENDING` e dependia apenas de `008`, que estava `DONE`.

Pelo `PROTOCOL.md`, a proxima task e identificada como a primeira `PENDING` com
dependencias `DONE`; portanto o STOP da Fase 1 precisava estar codificado no
estado mutavel, nao apenas no prompt.

## Correcao

Marquei as tasks Fase 2A `009-014` como `BLOCKED` em `PROGRESS.md`, todas com nota
explicita: Fase 1 STOP por `n_fase2_eligible_survivors=0`; nao iniciar Fase 2A sem
novo contrato humano. As tasks posteriores permanecem `PENDING`, mas nao sao
elegiveis porque dependem de uma cadeia bloqueada.

## Verificacao esperada

- `009-014` estao `BLOCKED`.
- Nao existe task `PENDING` com todas as dependencias `DONE`.
- `next_prompt.md` continua pedindo decisao humana.

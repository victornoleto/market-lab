# DRAFT — override §7 (NÃO ASSINADO, SEM EFEITO)

> **Status: RASCUNHO aguardando decisão explícita do usuário.** Este
> documento NÃO está em vigor. Pelo procedimento do mandate §7, só passa a
> valer se o usuário assinar (mover para `docs/mandate_overrides/` com
> marcação "Signed" + entry na tabela §7). Enquanto isso, o veredito
> vigente do estudo é o FAIL honesto terminal de `REPORT.md`.

## Proposta sob decisão

Adotar, como **resposta de pesquisa** do goal de 2026-06-11 (não como
mudança de capital — mandate §1/maintenance mode inalterados), o candidato
máximo único do estudo `evolution/`:

```text
45% GDE / 25% RSST / 30% ZROZ — rebalanceamento por banda de tolerância 20%
(gatilho: qualquer sleeve a ±20% relativo do alvo; checagem diária ou semanal)
```

## O que a evidência diz (resumo de TESTS_SUMMARY.md)

| A favor | Contra (motivos do FAIL pré-registrado) |
|---|---|
| CAGR 13,39% vs 12,52% do CORE (+0,87pp, acima do tier-1 +0,75pp) | **G2**: vizinhos de peso com ZROZ ≤ 25% furam −32% de MDD sob banda |
| MDD −29,52% (in-cap; o CORE atual fura o cap: −30,76%) | **B2**: no contínuo de bandas, o cap é raspado por 5-25bps nas bandas 12-18% |
| Bate o CORE em 61/68 starts trimestrais (89,7%) e 73% das janelas rolling 5y | **B3 (decisivo)**: bootstrap de blocos 63d — spread > 0 em só 83,8% dos paths (régua: 95%); vantagem de MDD vira moeda |
| Janela 1988+: empata CAGR do CORE (13,63% vs 13,66%) com MDD 3,2pp mais raso (−29,2% vs −32,4%) | O edge é colheita de persistência de tendência multi-mês — condicional a essa crença |
| Turnover 1,44 rebal/ano vs 12 (comparação gross é conservadora a favor) | Seleção sobre ~74k+132k trials; só o gauntlet completo separaria sinal de viés, e ele não passou inteiro |

Nota de calibração: a régua de 95% no B3 foi fixada neste estudo e é mais
severa que o gate de bootstrap da suíte SS5 do repo; 83,8% com spread médio
+0,87pp é evidência não-nula, porém não-definitiva sob a régua
pré-registrada `[advances_fin_ml, p.222-223]`.

## Condições operacionais OBRIGATÓRIAS se assinado

1. **ZROZ nunca abaixo de 30% no alvo** (fronteira de segurança do cap sob
   bandas — achado G2). Sem drift de pesos-alvo na direção ZROZ < 30%.
2. Banda na faixa **20-28%** (região onde o cap folga; evitar 12-18%).
3. Ciência explícita: o edge esperado depende de persistência de tendência
   multi-mês — a mesma premissa dos sleeves RSST/KMLM. Se essa crença cair,
   o ajuste perde a justificativa.
4. Research-only: nada disto altera alocação de capital real (mandate §1).

## Alternativa (se NÃO assinar)

`/goal clear` — o estudo encerra como FAIL honesto terminal, o negativo
mais bem documentado do RSC, e o CORE `35/40/25` mensal permanece a
expressão canônica.

---

Assinatura do usuário: ________________  Data: ________

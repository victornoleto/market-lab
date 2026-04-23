# Resposta às 3 perguntas — Projeção Victor

> Resumo executivo da análise completa. Detalhes em `PROJECAO.md` e gráficos
> em `*.png` desta pasta.

---

## 1. 🚗 Ford Mustang — viável dos 35-38 anos

4 estratégias testadas (valores em R$ reais de 2026):

| Estratégia | Mustang aos | Aposentadoria 55y | Múltiplo vida atual |
|---|---|---|---|
| **SPLIT 50/50 Mustang+Apos** ⭐ | 37,7 anos | R$ 21,0k/mês | 1,7× |
| MUSTANG priority | 35,5 anos | R$ 20,0k/mês | 1,6× |
| DELAY +10y | 45,4 anos | R$ 24,0k/mês | 1,9× |
| SEM MUSTANG | — | R$ 27,3k/mês | 2,2× |

**Todos os cenários entregam aposentadoria acima da vida atual.**

**Meu default: SPLIT 50/50** pós-imóvel.
- Compra Mustang aos 38 anos
- Mantém R$ 21k/mês de renda aposentadoria aos 55 (1,7× lifestyle atual)
- "Custo do sonho" = ~R$ 6k/mês de renda futura perdida vs não ter Mustang
- Aceitável se considera 18+ anos dirigindo o carro

---

## 2. 🏠 Amortizar vs Investir — praticamente NÃO IMPORTA

Esse foi o achado mais surpreendente do estudo:

| Estratégia | Aposentadoria 55y | Diff vs investir 100% |
|---|---|---|
| 0% amortiza (tudo investe) | R$ 6,30M | baseline |
| 20% amortiza | R$ 6,27M | -R$ 30k |
| 50% amortiza | R$ 6,25M | -R$ 50k |
| 100% amortiza | R$ 6,21M | -R$ 90k |

**Diferença 0% vs 100%: apenas R$ 90k em 25 anos (1,4%).** As linhas no
gráfico ficam literalmente sobrepostas.

**Motivo:** taxa financ real ~5% é PRÓXIMA do retorno esperado aposentadoria
~6%. Diferencial de apenas 1pp/ano em R$ 175k de saldo devedor Victor →
ganho pequeno.

### Recomendação

- **Continue investindo** os aportes mensais regulares (retorno marginal
  maior + liquidez + DCA preservado)
- **Use 13º/bônus** pra amortizações pontuais se quiser conforto psicológico
  de ver o saldo devedor cair
- **Não quebre o DCA** redirecionando aporte mensal fixo pra amortização

**Exceção:** se Selic disparar (ex. 15%+), reconsiderar. Revisar anualmente.

---

## 3. 🏖️ Aposentadoria com qualidade ≥ vida atual — garantida

Vida atual = R$ 12,5k/mês (plano caixinhas).

- **Pior cenário testado (MUSTANG priority):** R$ 20k/mês aos 55 = **1,6× vida atual**
- **Melhor cenário (SEM Mustang):** R$ 27k/mês aos 55 = **2,2× vida atual**

Você pode **inclusive se aposentar aos 50 anos com padrão igual ao atual**
em qualquer cenário — os gráficos mostram o nest egg cruzar R$ 3,75M
(= R$ 12,5k/mês SWR 4%) antes dos 50 em todos os cenários.

---

## 📊 3 gráficos gerados

1. **`projecao_4_cenarios.png`** — 4 estratégias lado a lado, mostrando
   buckets (reserva, imóvel, aposentadoria, Mustang) empilhados do 30y ao 65y
2. **`aposentadoria_comparativa.png`** — só o bucket aposentadoria, 4
   estratégias sobrepostas, com linha de "vida atual" e "2× vida atual"
3. **`amortizar_vs_investir.png`** — 4 linhas (0/20/50/100% amortização)
   literalmente sobrepostas, mostrando visualmente que escolha é indiferente

---

## Artefatos

Tudo em `reports/portfolio_aposentadoria_v2/projecao_victor/`:

- **`PROJECAO.md`** — análise completa 7 seções
- **`RESPOSTA.md`** — este arquivo (resumo das 3 perguntas)
- 3 gráficos PNG (acima)
- `scenarios_summary.csv` — dados tabulados
- `scripts/10_projection_victor.py` — código reprodutível

---

## Decisão que fica pra você

**Qual estratégia Mustang usar?**

Minha recomendação é **SPLIT 50/50** — dá o sonho aos 37-38 anos sem
comprometer qualidade de vida na aposentadoria. Mas é preferência:

- **Mustang urgente emocional** → MUSTANG priority (compra aos 35,5 anos)
- **Aposentadoria prioridade #1** → DELAY ou SEM Mustang
- **Balanceado** → SPLIT 50/50 (default)

# Guia IBKR — Depósito otimizado + Sistema de comissões

> Pesquisa 2026 sobre como depositar dinheiro do Brasil na Interactive Brokers
> com menor custo FX + análise da estrutura de comissões (Pro Fixed vs Pro
> Tiered vs Lite).

---

## 1. Como depositar na IBKR do Brasil — ranking custo

IBKR **não aceita depósito direto em BRL**. Você precisa converter BRL → USD
e enviar via wire transfer internacional. Há 4 caminhos principais:

### Comparação de opções (tarifa total + spread)

| Serviço | Spread FX | Tarifa fixa | Tempo | Total p/ R$ 13.100 |
|---|---|---|---|---|
| **TransferBank** | **0,30%** | Isento | 1-2 dias úteis | **~R$ 39 (0,30%)** |
| **Wise** | 0,35-0,60% | Variável (~R$ 5-15) | Minutos a 1 dia | R$ 50-80 (~0,4-0,6%) |
| **Remessa Online** | 0,79% | Isento (1ª) ou R$ 28 | 1-2 dias | R$ 103 + tarifa (~0,8-1%) |
| **Nomad Pay** | 0,70-1,00% | Isento | 1 dia | R$ 90-130 |
| **Banco tradicional** (Bradesco, Itaú, etc.) | 1,50-2,50% | R$ 50-100 | 2-5 dias | **R$ 250+ (2%+)** ❌ |
| Inter Internacional | 0,99-1,50% | Isento | instantâneo | R$ 130-200 |

### Economia típica em 30 anos

Aporte R$ 13.100/mês = 360 aportes totais. Diferença entre TransferBank
(0,30%) e banco tradicional (2,00%) por aporte = R$ 222. Em 30 anos:
**R$ 80k desperdiçados** em FX spread com banco tradicional.

### 🏆 Recomendação: **TransferBank** (menor custo)

Razões:
- Spread 0,30% (praticamente interbank)
- Zero tarifa fixa
- Regulado pelo BCB como instituição de pagamento
- Integração direta com IBKR
- 1-2 dias úteis pro dinheiro aparecer na IBKR

Fluxo operacional:
1. Abre conta TransferBank (online, gratuito)
2. No IBKR, adiciona método: "Wire Transfer — TransferBank" como origem
3. Inicia a ordem de wire no IBKR (não no banco) — gera os instruções
4. Copia dados pro TransferBank → envia BRL → TransferBank converte + envia
5. 1-2 dias: saldo na IBKR

### 🥈 Alternativa: **Wise** (se já tem conta ou valoriza multi-currency)

- Spread 0,35-0,60% + tarifa pequena
- **Vantagem:** conta multi-moeda (USD, EUR, GBP) — útil pra viagens, compras em sites estrangeiros, etc.
- Integração direta IBKR via linked account
- Minutos pra processar

### ❌ Evitar: banco tradicional

Spread 1,5-2,5% + tarifa alta. Pior opção disponível pra brasileiro.

### ⚠️ Inter Internacional — por que é PIOR que TransferBank

O Inter cobra spread 0,99-1,50% (médio 1,25%). TransferBank cobra 0,30%.
Diferença **~1pp por conversão**. Em 30 anos de aportes R$ 13.100/mês:

| Broker | Spread total 30y |
|---|---|
| Inter Internacional | R$ 146k desperdiçados (vs TransferBank) |
| TransferBank | baseline |
| Banco tradicional | R$ 245k desperdiçados |

**Se você já optou por IBKR, use TransferBank pra enviar dinheiro.** Inter
Internacional só faz sentido se você VAI operar DENTRO do Inter (zero
corretagem no app). Se destino é IBKR, não use Inter pra conversão.

---

## 2. Sistema de comissões IBKR — Pro vs Lite

IBKR tem **2 planos principais** (você escolhe ao abrir a conta, pode trocar):

### 🆓 IBKR Lite — zero commission US

| Item | Custo |
|---|---|
| US stocks/ETFs | **$0 commission** |
| Non-US stocks | Varia por exchange (R$ 2-10 por trade) |
| Options | $0,65/contrato |
| **FX conversion** | **~0,20% spread + $2 fixo/conversão** |
| Data market básico | Grátis |
| Inactivity fee | $0 (removido em 2021) |
| Withdrawal | 1 grátis/mês, depois $10 |

**Trade-offs do Lite:**
- Order routing pior — IBKR recebe payment-for-order-flow (pode executar pior que market best)
- Juros sobre cash mais baixos (atualmente ~4% vs Pro 4,5%)
- Margin rate mais alta (se usar margem, paga mais caro)

**Para buy-and-hold mensal de ETFs simples, a diferença de order routing é
marginal (alguns centavos por trade).**

### 💼 IBKR Pro — comissões baixas mas não zero

Dois sub-planos dentro do Pro:

#### Pro Fixed (mais simples, recomendado pra iniciantes)
- **$0,005/share** (meio centavo por ação)
- **Mínimo $1** por trade
- **Máximo 1%** do valor do trade
- Inclui exchange fees

#### Pro Tiered (menor custo pra volume alto)
- **$0,0035/share** (primeiras 300k shares/mês)
- Escala para $0,002/share (volumes médios) e $0,0005/share (volumes massivos)
- **+ exchange fees** ~$0,0002-0,0005/share (transparent)
- **Mínimo $0,35** por trade
- Máximo 1% do trade

**Outros fees IBKR Pro:**
- FX conversion: **0,02% + $2 fixo** (melhor que Lite)
- Margin rate: Fed Funds + 0,5% a 1,5% (competitivo)
- Juros sobre cash acima de $10k: ~4,5%/ano USD
- Market data: $4,50-10/mês se quer tempo real completo

### Qual plano escolher?

| Seu perfil | Plano recomendado |
|---|---|
| Compra mensal ETFs simples, aporte até $5k/mês | **IBKR Lite** (zero comissão, simples) |
| Trade ocasional, gosto de controle de ordem | IBKR Pro Fixed (min $1/trade, quase nada) |
| Volume alto (>$50k/mês), day trade | IBKR Pro Tiered (menor custo marginal) |
| Uso margem pesadamente | IBKR Pro (margin rate menor) |

### 📊 Sua situação específica (aporte R$ 13.100 ≈ $2.380/mês)

Cenário típico V3.5: compra mensal de ~6-9 ETFs (GDE, AVUS, AVDE, AVEM,
AVUV, AVDV, SPMO, IDMO, BTGD). Pra simplificar, assuma 3-4 compras/mês
rotacionando entre os menos preenchidos.

**Custos comparados por compra (~$250-500 por ETF, ~5-15 shares):**

| Plano | Custo por trade | Custo 4 trades/mês | Custo 30 anos |
|---|---|---|---|
| **IBKR Lite** ⭐ | **$0** | **$0** | **$0** (!) |
| IBKR Pro Fixed | $1 min (5-15 shares × $0,005 = $0,025-0,075 → hit min) | $4/mês | ~$1.440 |
| IBKR Pro Tiered | $0,35 min + exchange fees ~$0,10 = ~$0,45 | $1,80/mês | ~$650 |

**Para o seu caso (buy-and-hold mensal), IBKR Lite zera comissões.** O
trade-off de order routing é marginal (centavos por trade) e você não
perde praticamente nada.

### ⚠️ Quando Pro FAZ sentido sobre Lite

1. **Uso de margem regular:** Pro tem margin rate menor → economia direta
2. **Trade muitas vezes por dia** (não é teu caso)
3. **Quer garantia de melhor execução** — Pro roteia pra 14+ exchanges
4. **Usa SmartRouting avançado** (Pro tem, Lite é simplificado)
5. **Trade options frequentemente** (Pro tem melhores preços)

Pro Fixed ainda custa só ~$1/trade → $4-12/mês no seu caso. **Não é dealbreaker.**

### Juros sobre cash — vantagem escondida do IBKR

Se você tem USD parado na conta esperando pra comprar ETFs:
- **IBKR Pro:** ~4,50% a.a. em USD no cash (pago automaticamente)
- **IBKR Lite:** ~3,80% a.a. em USD no cash
- **Inter Internacional:** 0% em USD (cash fica dormindo)

Se você tem $5k em cash na IBKR Pro esperando aporte = $225/ano de juros "grátis".

---

## 3. Outros custos e considerações

### Custos recorrentes IBKR (todos os planos)

| Item | Valor |
|---|---|
| Inactivity fee | $0 (removido) |
| Market data basic (15-min delay) | Grátis |
| Market data real-time US | $1,50-10/mês (optional) |
| Withdrawal wire | 1/mês grátis, depois $10 |
| Estatement paper | $1-2/mês (use digital grátis) |

### Como retirar dinheiro (aposentadoria ou qualquer necessidade)

Quando chegar à aposentadoria e precisar sacar:

1. **Vende ETFs dentro da IBKR** → gera DARF 15% sobre lucro (Lei 14.754)
2. **Converte USD → BRL dentro da IBKR** (spread 0,02% + $2 fixo)
3. **Wire transfer pra seu banco BR** (1 grátis/mês, depois $10)
4. **Declara IRPF anual** no ano seguinte

**Custo total de saque:** <R$ 100 por operação, independente do valor.
Bem mais barato que comprar.

### ACAT — transferência in-kind (Inter → IBKR sem vender)

Se você começar no Inter e migrar pra IBKR depois:

- **ACAT (Automated Customer Account Transfer)** transfere ETFs EM KIND
  (sem vender) entre brokers US
- Demora 5-7 dias úteis
- Custo: $0 (IBKR não cobra entrada) ou $50-100 (algumas brokers cobram
  saída — verificar com Inter)
- **Zero DARF trigger** pois não há venda

Perfeito pra migrar quando aporte crescer.

---

## 4. Minha recomendação consolidada

Pro seu perfil (aporte R$ 13.100/mês = $2.380/mês USD em termos reais):

### Setup ótimo IBKR + depósito

| Componente | Escolha | Razão |
|---|---|---|
| **Broker** | IBKR **Lite** ou Pro Fixed | Lite zera commissions; Pro Fixed custa ~$4/mês |
| **Remessa BR→USD** | **TransferBank** (0,30%) | 4-5× mais barato que Inter (1,25%) |
| **FX conversion dentro IBKR** | Automática (IBKR converte BRL→USD na chegada) | 0,02% + $2 — quase nada |
| **Cash parking** | Deixa em USD na IBKR | Rende 3,8-4,5% a.a. enquanto espera aporte |
| **Market data** | Free tier básico | Atraso 15 min é OK pra buy-hold |
| **Alertas** | IBKR mobile app + email | Zero custo |

### Comparação Inter vs "IBKR Lite + TransferBank"

| Componente | Inter Internacional | IBKR Lite + TransferBank |
|---|---|---|
| Spread FX remessa | 1,25% | **0,30%** |
| Commission trading | $0 | **$0** (Lite) |
| Juros sobre cash USD | 0% | **3,8%/ano** |
| Acesso a UCITS | ❌ | **✅** (mitigation estate tax) |
| Simplicidade operacional | Alta | Média |
| Interface em português | Sim | Inglês |

### 💰 Economia 30 anos real-data

Setup otimizado (IBKR Lite + TransferBank + UCITS) vs Inter puro:

| Item | Economia/ano | 30 anos |
|---|---|---|
| Spread FX (1,25% → 0,30%) | ~R$ 1.490/ano | **R$ 45k** |
| Juros cash USD (0% → 3,8%) | ~R$ 500/ano (se $5k parado) | **R$ 15k** |
| Mitigation estate tax (cap UCITS) | potencial 40% de patrimônio US-situs | **Centenas de milhares** (caso extremo) |
| Total direto mensurável | ~R$ 2.000/ano | **R$ 60-80k** |
| Total com estate tax hedge | — | **R$ 500k+** (worst case) |

---

## 5. Roteiro prático de setup

### Fase 1 — Abertura (1-2 semanas)

1. **Abrir conta TransferBank** (transferbank.com.br) — 15 min, 100% online
2. **Abrir conta IBKR** (interactivebrokers.com):
   - Escolher **IBKR Pro** (pode mudar pra Lite depois; Pro dá mais opções)
   - Documentos: CPF, RG, comprovante endereço (≤90d), IRPF última
   - Aprovação: 3-7 dias úteis
3. **W-8BEN** dentro do IBKR — reduz withholding tax dividendos
4. **Configurar 2FA** (obrigatório)

### Fase 2 — Primeiro depósito (1 dia)

1. No IBKR, menu "Transfer & Pay" → "Deposit Funds" → "Wire"
2. Escolher USD + valor teste ($100-500)
3. Receber instruções (BIC, ABA, beneficiary)
4. **NO TransferBank:** "Nova remessa" → colar instruções → enviar BRL
5. Aguardar 1-2 dias úteis
6. Confirmar recebimento na IBKR

### Fase 3 — Primeira compra

1. Via **IBKR Mobile ou Client Portal**
2. Buscar ticker (ex: **GDE**) → "Buy"
3. Ordem limit ou market
4. Confirmar + executar
5. Ver no portfolio

### Fase 4 — Automação mensal

- IBKR **NÃO tem auto-invest nativo** (diferente do Inter)
- Precisa comprar manualmente todo mês
- Dica: calendário mensal + lista dos ETFs abaixo do target
- Alternativamente: **M1 Finance** (US-based, auto-invest). Mas M1 é
  pra residents US, complicado pra BR.

Se quiser automação total, **Inter tem vantagem**. IBKR exige 10-15 min
manuais por mês.

---

## Sources

### Depósito
- [TransferBank — Remessa para Interactive Brokers](https://www.transferbank.com.br/interactivebrokers)
- [Wise — Integração Interactive Brokers](https://exiap.com.br/guias/wise-e-interactive-brokers)
- [Remessa Online — Transfer pra IBKR](https://www.remessaonline.com.br/blog/como-enviar-dinheiro-para-a-corretora-interactive-brokers-pela-remessa-online/)
- [blueTransfer — Abastecer IBKR](https://bluetransfer.com.br/blog/como-abastecer-minha-conta-na-interactive-brokers/)
- [Como Investir no Exterior — Guia IBKR](https://www.comoinvestirnoexterior.com/transferir-dinheiro-interactive-brokers/)

### Comissões IBKR
- [IBKR Commissions Official](https://www.interactivebrokers.com/en/pricing/commissions-home.php)
- [IBKR Stocks Pricing](https://www.interactivebrokers.com/en/pricing/commissions-stocks.php)
- [IBKR Pricing Plan Overview](https://www.ibkrguides.com/brokerportal/ibkrpricingplan.htm)
- [IBKR Lite Overview](https://www.interactivebrokers.com/en/trading/why-ibkr-lite.php)
- [BrokerChooser — IBKR Fees 2026](https://brokerchooser.com/broker-reviews/interactive-brokers-review/interactive-brokers-fees)
- [IBKR Fixed vs Tiered Examples](https://www.interactivebrokers.com/en/accounts/fees/stocksPricing2.php)

# 2026-04-23 23h59 — Sessão Plano C encerrada

## Contexto

Sessão ampla cobrindo o Plano C (portfolio aposentadoria passivo) do
V1→V3.5, projeção financeira Victor com 3 objetivos (imóvel + Mustang +
aposentadoria) incluindo Lancer HL-T 2018, e análises operacionais
completas sobre broker IBKR vs Inter.

## Artefatos finais

Todos em `reports/portfolio_aposentadoria_v2/`:

### Documentos canônicos
- `TLDR.md` — portfolio V3_1 v3.5 (2 min leitura)
- `ANALYSIS.md` — análise técnica completa ~900 linhas
- `REVISIONS.md` — audit trail V1→V3.5

### Projeção Victor (em `projecao_victor/`)
- `PROJECAO.md` — análise original (v1, sem Lancer)
- `RESPOSTA.md` — resumo v1
- `RESPOSTA_V2.md` — com Lancer
- `RESPOSTA_V3.md` ⭐ — **versão final realista** (Lancer + buffer R$ 50k
  + manut R$ 2k/mês incremental)
- `ANALISE_ADICIONAL.md` — DARF USD + BTGD vs RSSX + Inter vs IBKR
- `GUIA_IBKR.md` — depósito (TransferBank 0,30%) + comissões IBKR (Lite
  zera) + settlement T+1 + relatórios IR

### Gráficos gerados
- `projecao_4_cenarios.png` — 4 estratégias Mustang
- `aposentadoria_comparativa.png` — comparação aposentadoria
- `amortizar_vs_investir.png` — amortização vs investir
- `projecao_v2_com_lancer.png` — v2 com Lancer
- `projecao_v3_buffer.png` — v3 com buffer
- `inter_vs_ibkr.png` — broker comparativo

### Scripts (pipeline reprodutível)
- `scripts/01-09_*.py` — backtest V1-V5 portfolio
- `scripts/10_projection_victor.py` — projeção original
- `scripts/10b_projection_with_lancer.py` — v2 com Lancer
- `scripts/10c_projection_v3_buffer.py` — v3 com buffer
- `scripts/11_inter_vs_ibkr.py` — comparação brokers

## Decisões-chave consolidadas

### Portfolio V3_1 v3.5 (fase acumulação 30-45 anos)
```
GDE   25%  (90% SPY + 90% gold stacked)
AVUS  12%  (US core Avantis)
AVDE  20%  (DM core pure equity)
AVEM  13%  (EM core pure equity)
AVUV  10% + AVDV 5%  = 15% SCV
SPMO   7% + IDMO 3%  = 10% Momentum
BTGD   5%  (BTC + gold stacked)
```
- Geografia 55/30/15 US/DM/EM
- 25% factor (60/40 SCV/Mom)
- Leverage 1,25× via stacked puro (GDE + BTGD)
- Zero US bonds (BR FI entra só aos 45+)

### Glidepath
- 30-45: V3_1 v3.5 (0% BR FI)
- 45-55: V3_3 (18% BR FI)
- 55-60: V3_2 (35% BR FI)
- 60+: V3_4 (52% BR FI)

### Projeção Victor v3 (realista com Lancer + buffer)
- **Mustang aos 37,1 anos** (SPLIT 50/50 pós-imóvel)
- **Aposentadoria 55y: R$ 21,8k/mês** (1,75× vida atual)
- **Imóvel aos 33 anos** com financiamento R$ 175k
- **Amortizar vs investir: praticamente indiferente** (diff 1pp/ano)

### Operacional IBKR
- **Depósito: TransferBank** (0,30% spread vs Inter 1,25%)
- **Plano: IBKR Lite** (zero commission pra buy-and-hold)
- **Settlement: T+1** desde mai/2024 (pode comprar imediatamente em margin)
- **Relatórios IR:** Activity Statement CSV + planilha simples (ou
  myProfit R$ 50-100/ano se volume alto)

### Risco crítico
- **US Estate Tax $60k threshold** — até 40% pra NRA em caso de morte
- Mitigation: UCITS irlandeses (CSPX/IWDA/VWCE/EIMI) — **só disponível
  via IBKR**, não no Inter

## Evolução V1→V3.5 (7 iterações em um dia)

Cada iteração resolveu inconsistência real que o usuário pegou:

1. V1→V2: bug NaN→0 no panel (FINAL_1 CAGR < FINAL_3)
2. V2→V3: US bonds em portfolio BR (inconsistência moeda)
3. V3→V3.1: recomendei V3_3 sem olhar números (V3_2 dominava)
4. V3.1→V3.2: SSO 10% violava princípio "stacked > LETF"
5. V3.2→V3.3: 25% SCV + 5% Mom desbalanceado 5:1 (AQR optimal é 60/40)
6. V3.3→V3.4: math error + muito gold (40%)
7. V3.4→V3.5: NTSI escolhido por "simetria", backtest AVDE beat +4,6pp

## Status final

- ✅ Portfolio V3.5 canônico e commitado
- ✅ Projeção Victor v3 realista (Mustang aos 37, apos R$ 21,8k/mês)
- ✅ Guia operacional IBKR completo (depósito + comissões + IR)
- ✅ Tudo em git, pushed para origin/main
- ✅ Nada pendente dessa sessão

## Próximo passo pro Victor (pós-sessão)

1. Revisar `RESPOSTA_V3.md` com esposa (alinhar plano imóvel R$ 150k entrada)
2. Executar plano caixinhas conforme documentado (Mai/26 Fase 1 start)
3. Abrir TransferBank + IBKR Pro (margin, W-8BEN)
4. Primeiro depósito teste $100-500 pra validar fluxo
5. Anotar PTAX diária das operações pro IR futuro
6. Revisar plano anualmente (Abril cada ano)

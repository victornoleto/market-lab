# Impasse em Phase 3.5d: D7 morto, D8 confirma contradição estrutural [SWING BROKER]

**Contexto:** Após 8 experimentos (D1-D8) tentando encontrar uma configuração vencedora
para TQQQ+GLD swing trade, chegamos a uma conclusão clara: não existe configuração que
passe TODOS os 5 gates de sobreajuste + 3 gates econômicos simultaneamente, dado o
choque tarifário de Jan-Abr 2026 na janela de stress (FWD).

## O que tentamos (D7 e D8)

**D7 (iter 12) — QQQ como sinal em vez de SPY:** Hipótese: QQQ (o índice direto do TQQQ)
reagiria mais rápido a choques no setor de tecnologia. Resultado: **PIOR** — Sharpe caiu
de 0.938 para 0.834, SN de 0.797 para 0.709. QQQ tem mais ruído que SPY → sinal mais
instável → menos qualidade. FWD continuou negativo (-1.51 vs -1.14 do D6).

**D8 (iter 12) — Momento Relativo TQQQ>GLD (Antonacci-style):** Hipótese: sair do TQQQ
quando GLD começa a superar por X dias captaria o choque tarifário. Resultado:
- `slope_dom_rm15`: FWD=0.573 ✓, mas SN=0.762 ✗ (gap 0.038)
- `slope_dom_pure`: SN=0.847 ✓, mas FWD=-1.344 ✗
- PBO=0.794 (FALHA) — porque misturar configurações que protegem do choque com as que
  não protegem torna o "vencedor IS" instável entre janelas CSCV

## A contradição estrutural

Identificamos que a Phase 3.5d tem uma **contradição fundamental** entre dois requisitos:

| Gate | Requer | Problema |
|------|--------|---------|
| PBO < 0.5 | Sinal binário estável (um config domina todos os IS) | Sinal binário fica 100% em TQQQ até sair → leva o choque completo → FWD falha |
| FWD > 0 | Reduzir exposição durante o choque (Jan-Abr 2026) | Configs que saem cedo são diferentes das que ficam → IS-winner muda → PBO sobe |
| SN > 0.800 | Sharpe bruto > 0.941 | Qualquer filtro de saída reduz Sharpe abaixo de 0.941 |

**Máximo alcançável:**
- Melhor SN com FWD passando: 0.762 (slope_dom_rm15 — gap 0.038 abaixo do gate 0.800)
- Melhor SN sem restrição de FWD: 0.847 (slope_dom_pure — passa SN, cai no FWD)
- D5 vol-targeting: SN=0.855 ✓, FWD=0.182 ✓, mas PBO=0.599 ✗

O D5 vol-targeting (sinal contínuo) foi o ÚNICO experimento a passar simultaneamente
SN > 0.800 E FWD > 0, mas falhou PBO. Isso indica que uma estratégia válida pode existir
nesse espaço, mas exige uma abordagem diferente para o grid de configs (não 7 configs
homogêneas, nem 3 configs heterogêneas demais).

## Próximo passo: Phase 3.5e — Arbitração

A Phase 3.5e deve decidir:
1. **Opção A:** Aceitar slope_dom_pure com SN=0.847 como "vencedor near-miss" e prosseguir
   com validação de produção, documentando que o gate FWD foi o binding constraint por
   causa de um evento geopolítico único (tarifas 2026).
2. **Opção B:** Revisitar D5 vol-targeting com 2 configs MUITO diferentes (não 7 homogêneas)
   para ver se PBO < 0.5 é alcançável.
3. **Opção C:** Tentar SSO (2× em vez de TQQQ 3×) — menor retorno mas muito menor MaxDD
   e menos exposição ao choque de tecnologia.

Sem arbitração, o projeto fica preso neste ciclo.

## Resultados completos para referência

| Experimento | Melhor Config | SN | FWD_S | PBO | Veredicto |
|-------------|--------------|-----|-------|-----|-----------|
| D2 | sma200_gld | 0.780 | -0.396 | 0.115 | Near-miss |
| D3 | dc20_10 | 0.676 | — | 0.107 | Dead |
| D4 | mom12_qqq | 0.565 | — | 0.778 | Dead |
| D5 | vol15_lk20 | **0.855** | **0.182** | 0.599 | Near-miss (PBO) |
| D5b | diverse | — | — | 0.651 | Dead |
| D6 | trend_heavy | 0.797 | -1.14 | 0.341 | Near-miss |
| D6* | slope_dominant | **0.847** | -1.344 | — | Near-miss (FWD) |
| D7 | trend_heavy_qqq | 0.709 | -1.51 | 0.437 | Dead |
| D8 | slope_dom_rm15 | 0.762 | 0.573 | 0.794 | Dead |

*slope_dominant testado fora do PBO grid de D6.

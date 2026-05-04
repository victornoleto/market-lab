# Pipeline myfxbook v4: redesenho aprovado em 8-12 semanas

Avaliacao minuciosa do pipeline `studies.myfxbook_reverse_engineering.workbench.pipeline`
apos a constatacao de 2026-05-03 de que **nenhum dos 30 systems R1 v3 processados** (de
um universo de 52) decodifica de forma economicamente viavel. Diagnostico oficial
do dia: "decodificacao operacional nao recuperavel com OHLC publico M5/M1 pelo
pipeline atual." Esta sessao desempacota o porque e propoe um redesenho.

## O que estava quebrado (8 modos de falha mapeados)

A combinacao mais reveladora dos diagnosticos:
- **direcao dado entry**: 70-90% recuperavel (decodavel)
- **timing do entry (F1)**: < 0.05 mesmo no M1 forense (inrecuperavel)
- **over-fire**: synthetic dispara 2.5x a 35.9x mais que o EA real
- **oracle ex-post (cherry-pick por PnL futuro)**: 7/7 systems passam bootstrap+OOS
- **honest sampler (uniforme no tempo)**: 0/7 passa

Leitura: existe sinal escondido dentro do over-fire (oracle prova), mas o pipeline
modela `P(direcao | t_entry)`, nao `P(t_entry | mercado)`. Os miners atuais
(Bonferroni univariada + decision tree + RIPPER) nao conseguem separar bons
candidatos de ruido sem usar info futura.

Os 8 modos de falha: (1) assimetria informacional do input M5/M1; (2) metrica
errada (`fidelity_score` mistura termos); (3) single-family classifier para EAs
multi-estrategia; (4) feature set "livro-texto" sem cross-asset/news/tick; (5)
gates §2.4 do mandato nao enforcados (DSR informativo, PBO ausente, WF8 sem
purge); (6) sem pre-filtro de tradeability do EA antes de gastar compute; (7)
over-fire tratado como erro, nao como sinal de "falta meta-label"; (8) sem
validacao adversarial (real-vs-synthetic AUC).

Detalhes e citacoes em `/home/victor/.claude/plans/majestic-greeting-sutton.md`.

## O que foi aprovado

Tres trilhas de melhoria, fases 1-3 em 8-12 semanas, **dados gratuitos apenas**
(Forex Factory CSV, Dukascopy ticks, Tiingo cache existente — sem multi-broker
spread pago), **objetivo hibrido** (Fases 1+2 servem tanto decode-self quanto
filter-and-copy; decisao na transicao Fase 2->3).

Cronograma:
- **Sem 1-2 (Fase 1)** — `pre_decode_screen.py` (MCPT na track record, DSR p<0.05
  hard, PBO via CSCV, concentration test, live-vs-demo flag), `adversarial_validator.py`
  (real-vs-synthetic LightGBM AUC). Output: lista N≤10 EAs sobreviventes.
- **Sem 3-4 (Fase 2A)** — features Trilha A1-A4: news calendar, tick volume/imbalance,
  cross-asset (DXY/VIX/gold-silver/BTC dom), realized-vol regime.
- **Sem 5-6 (Fase 2B)** — LightGBM purged-CV miner substitui univariate+tree+RIPPER;
  meta-labeling (Lopez de Prado ch.6) primary side + secondary take/skip.
- **Sem 6 — DECISION GATE**: se F1 timing > 0.30 em ≥3 systems E adversarial AUC
  < 0.65 E §2.4 gates passam, Fase 3a (decode-self) ganha prioridade; senao Fase
  3b (filter-and-copy) assume. **Ambas executam independente da escolha** porque
  o usuario travou o objetivo hibrido.
- **Sem 7-10 (Fase 3a)** — Transformer encoder small + HMM regime mixture +
  out-of-domain transfer test (treina EUR, testa JPY).
- **Sem 7-8 (Fase 3b)** — score consolidado, top-3 EAs em forward monitor 60d
  (track reportado vs forward observado, gap >30% rejeita).
- **Sem 9-10 (Fase 3a refino)** — symbolic regression se Transformer estagnar,
  cross-lib ±3pp em vectorbt+backtrader.
- **Sem 11-12** — out-of-domain validation final, `_diagnostics/PIPELINE_V4_FINAL.md`.

Citacoes obrigatorias por decisao: meta-labeling `[advances_fin_ml, p.84-89]`,
MCPT `[evidence_based_ta, p.325-328]`, CSCV/PBO `[advances_fin_ml, p.208-222]`,
WF purgado `[testing_tuning, p.148-162]`, DSR/PSR `[advances_fin_ml, p.273-275]`.

## Por que ainda existe luz no fim do tunel

Tres razoes objetivas, nao fe:

1. **Oracle 7/7 prova que sinal existe** — o que falta e seletividade, nao
   informacao. Meta-labeling foi desenhado exatamente para este problema:
   primary classifier produz over-fire, secondary filtra. Falha 7 do diagnostico
   nao foi atacada ainda.
2. **Pre-filtro encurta o problema** — provavelmente metade dos 30 systems nao
   tem edge real (curva-fit, news-luck, demo, survivorship). Filtrando MCPT +
   DSR + concentration + demo-flag, o universo cai para N≤10 e o sinal/ruido
   melhora muito.
3. **Filter-and-copy via myfxbook AutoTrade e backup garantido** — mesmo que
   decode-self continue falhando, ranking de qualidade de signal vendor + forward
   monitor 60d e operacional sem precisar decodar nada.

## Guardrails preservados

- Plano A continua DORMANT (mandate §1). Nenhum paper/live autorizado nesta
  proposta.
- Frozen rules nao serao alteradas (workbench permanece research-only).
- Gates §2.4 hard-block reforcados (DSR p<0.05 vira hard, PBO entra, CPCV
  substitui WF8). CAGR/MDD seguem warning-only tiers.
- Capital 100% Plano C inalterado.

## Proximo passo

Plano salvo em `/home/victor/.claude/plans/majestic-greeting-sutton.md` (fora do
repo, especifico desta sessao). O proximo passo executavel e quebrar a Fase 1 em
tickets de implementacao (writing-plans skill) e iniciar pelo `pre_decode_screen.py`
e o hardening do `gates.py` para DSR hard — ambos ortogonais ao restante do
pipeline, sem tocar trades existentes nem frozen rules.

# O estudo de proteção a crash fechou em resultado negativo honesto

Duas semanas atrás a gente tinha um backtest do EMA/SMA threshold com
3× UPRO synth (o "top-1 educacional") entregando CAGR 27.67% mas com
**MDD de 54%**. Um ajoelhou duro de 54% num equity curve é o tipo de
número que inviabiliza staging real — a posição quebra o estômago e o
investidor muda o plano no meio do caminho.

A pergunta do estudo (`studies/SPEC_crash_protection_evolution.md`)
era direta: **dá pra reduzir esse MDD para 25-40% sem sacrificar mais
que 3-5 pp de CAGR, usando stop-loss ou sinais preditivos de crash da
literatura?**

Três fases, 57 testes novos, 4 020 sims cumulativos depois, a resposta
honesta é **não**.

---

## O que foi feito

### Fase 1 — stop-loss isolado (2 580 sims)

Sweep de 20 top-bases × 42 variantes de stop (7 níveis × 3 modos de
re-entry × 3 parâmetros) × 3 datasets (synth 40y, SPY real 17y, NDX
real 16y). Quarenta e três minutos de simulação.

Melhor combo isolado no top-1 synth: `sl30_next` reduz MDD de 54% para
47% com ΔCAGR +0.51 pp. **Sete pp de redução a custo zero** — mas
ainda 7 pp acima do alvo.

Padrão descoberto: `recovery_trigger` > `time_cooldown` > `next_signal`
(spec §8.2 previa). Stops de 25-30% são o sweet spot; 15% dispara muito
e 40%+ dispara pouco.

### Fase 2 — sinal preditivo como de-leveraging (1 200 sims)

Baixei EBP (Fed), T10Y3M (FRED), CAPE (Shiller), VIX (FRED) e construí
um composite equal-weight. Posição reduzida continuamente:
`pos(t) = max(0, 1 − λ · risk(t))` quando o regime é +1.

Melhor combo isolado no top-1 synth: `cape λ=0.5` reduz MDD em 2 pp
com ΔCAGR −3 pp. Menos eficaz que stop-loss neste base específico.

CAPE domina cross-dataset — consistente com Campbell-Shiller 1988
(valuation tem lead longo). EBP sozinho é fraco porque z-score fica
zero a maior parte do tempo.

### Fase 3 — combinação + 7-gate battery

Quatro combos selecionados pelos Fase 1+2 winners:
`sl20_cool21_composite0.5`, `sl20_cool21_cape0.5`,
`sl30_rec10_composite0.5`, `sl30_rec10_cape0.5`.

Rodei as 7 gates (PBO + DSR + WF + OOS + FWD + Bootstrap + Cross-lib)
com **n_trials cumulativo de 4 020** (Phase 1+2+3) sobre os top-5
survivors por dataset, mais uma passada cross-dataset nas 16 combinações
com bases comuns aos 3 top-20.

---

## O veredicto

Zero candidatos passam no critério cross-dataset do spec §0
(≥ 5/7 no synth AND ≥ 4/7 no spy real AND ≥ 4/7 no ndx real).

| gate | educational | spy real | ndx real |
|---|---|---|---|
| G1 PBO (grid) | ✅ PASS (0.21) | ❌ 0.78 | ❌ 0.60 |
| G2 DSR (p<0.05, n=4020) | ~50% | ❌ universal | ❌ universal |
| G3 Walk-Forward | ❌ universal | ❌ universal | ❌ universal |
| G4-G7 | passam | passam | passam |

Os três killers estruturais são:

1. **G3 Walk-Forward** — exige MDD < 25% por janela de 6 meses OOS.
   Cada crash histórico (1987, 2000-2002, 2008, 2020) cai em alguma
   janela e mesmo o overlay não segura MDD abaixo de 25% ali.
2. **G1 PBO** — o grid de 80 variants por dataset mostra overfit
   detectável via CSCV no real data; synth 40y dilui.
3. **G2 DSR** — com n_trials = 4 020, o benchmark `E[SR_max] ∝ √(ln N)`
   sobe ~40% e o Sharpe real em 17 anos (poucos crashes, overlay só
   ajuda em alguns) não consegue bater isso a p < 0.05.

Interessante: **G4 OOS simples passa universal**, **G5 FWD post-2020
passa universal**, **G7 cross-lib passa universal**. O edge existe.
Só não é forte o suficiente pra sobreviver às gates estatísticas mais
duras.

---

## Por que isso é consistente com o histórico do projeto

A memória do projeto registra 113/113 honest FAIL nas duas semanas
anteriores (Phase 3.5f-3.8 + D-MVP + E-MVP). Esse estudo começou como
**tentativa educacional** de melhorar um candidato conhecido, não como
busca nova. O resultado 0/16 cross-dataset é coerente com o pattern:
mandate §1 (MAINTENANCE, 100% Plano C) continua inalterado.

O que salvamos como valor:

- **Infra nova e testada**: `stop_loss_and_risk_signals.py` (3
  simulators: stop, signal, combined) + contrapartida numpy-pura pra
  cross-lib G7 + `macro_data_loader` + `risk_score` module + cache
  local de EBP/T10Y3M/CAPE/VIX.
- **57 testes novos** adicionados ao baseline (1 104 → 1 161), zero
  regressão.
- **Documentação granular** em `phase1_FINAL.md`, `phase2_FINAL.md`,
  `phase3_FINAL.md`, `phase3/cross_dataset_gates.md`. Se daqui
  6-12 meses alguém for revisar reativação de slot, encontra o porquê.
- **Confirmação empírica da literatura**: CAPE domina entre single
  indicators (Shiller), recovery_trigger vence next_signal (Aronson
  "evidence-based TA"), whipsaw cost é real em bL=3 (Gayed p.21 Table
  12 extendido).

---

## O que NÃO foi feito (deliberadamente)

- **Phase 4** (real-data validation + per-crash analysis + portfolio
  50/50 update) **não rodou**. O critério de sucesso de Phase 3 não
  foi atingido — Phase 4 seria encorrochar um config fraco.
- **LPPLS** (Sornette) não foi integrado. O spec marcava como
  prioridade 5 ("custo computacional alto; rodar semanal"). Com o
  resultado de Phase 3 negativo, não vale.
- **Sweep expandido** sobre lookbacks dos indicadores macro foi
  rejeitado por spec §6.3 (small-sample: 5-8 crashes em 90 anos;
  qualquer fine-tuning = overfit).

---

## Próximo passo

Nada. Mandate §1 MAINTENANCE continua — 100% Plano C passive
factor-tilted, conforme `portfolio-aposentadoria.md`.

O que muda no dia-a-dia: **zero**. Continuamos fora de short-hold ativo.
O projeto está no modo "esperar 6-12 meses antes de re-avaliar
reativação de slot" (consolidação de 2026-04-23).

Este estudo fica arquivado como material educacional em
`studies/ema_sma_threshold_crash_protected/`. Se no futuro a gente
pensar em reativar algum slot, isso aqui é o primeiro baseline a
bater — e sabemos agora que stop + signal sozinho **não basta**.

---

*Data:* 2026-04-24 · *Sessão anterior:* 2026-04-23
`educacional-ema_sma_threshold_sweep` ·
*Próxima leitura sugerida:* `studies/SPEC_crash_protection_evolution.md`
(se for revisitar), `studies/ema_sma_threshold_crash_protected/phase3_FINAL.md`
(detalhe técnico).

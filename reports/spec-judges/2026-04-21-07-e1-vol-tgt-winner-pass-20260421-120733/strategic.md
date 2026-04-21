# Juiz Adversarial — Fidelidade Estratégica

**Spec:** `jornada/2026-04-21-07-e1-vol-tgt-winner-pass.md` + `reports/phase_3_5d/e1_vol_tgt_2config/*`
**Data:** 2026-04-21 14:30
**Veredito:** **BLOCK**

---

## Resumo executivo

Este "winner" não é uma descoberta — é um artefato de grid selection.
A mesma configuração `vol15_lk20` falhou PBO em D5 (7 configs, 0.599) e
piorou em D5b (3 configs, 0.651). No E1 (2 configs) "passou" com 0.151.
**O único ingrediente que mudou foi o denominador do grid submetido ao
CSCV.** Isso é precisamente o padrão que López de Prado descreve como
"PBO inflation by design" e cujo remédio é o N_trials-aware DSR
`[advances_fin_ml, p.275-276]`. Aceitar isso como winner repete, quase
literalmente, o erro metodológico que afundou Plano B V4 em 2026-04-20 —
custou semanas de trabalho. Aceitar E1 agora significa construir Phase
3.5f inteira (F1-F5) sobre uma base que não resiste a um teste honesto
de "quantos configs eu testei no total nesta família?". O spec
autoritativo §7.3 ("se D1-D4 todos DEAD → escalar ao usuário") já foi
disparado em D6/D7/D8 e o loop ignorou, auto-advançando de 3.5d para
3.5f pulando o gate 3.5e de arbitration. Três falhas estruturais
simultâneas: (1) gate bypass disfarçado via shrinkage de grid; (2)
escalation trigger ignorado pelo loop; (3) strategy portfolio goal
violado (N=1 winner questionável em vez de N=~10 breadth hunt).

---

## Alinhamento com o pivô / mandate

| Aspecto | Spec respeita? | Evidência |
|---|---|---|
| Gates §5 "zero bypass" | **NÃO** | PBO passou apenas porque grid foi reduzido de 7→3→2 configs. A propriedade estatística do método CSCV muda com o denominador; a estratégia não. `[advances_fin_ml, p.208-211, p.276]` |
| Strategy B winner genuíno | **NÃO** | Mesma estratégia falhou 2× antes; 3ª tentativa passou via grid shrinkage é data snooping na dimensão "quanto do grid mostro ao PBO". `[advances_fin_ml, p.204-207, sin #4]` |
| CAGR ≥ 15% líquido | Parcial (18.14%) | Número bruto atende, mas é condicionado a vol15_lk20 ser um winner; se não é, o 18.14% é história. |
| Cross-lib concordance | Sim (bt 0.15pp, vbt 0.44pp) | Este é o único gate não-manipulado; não redime o resto. |
| Stage-1 vs Stage-2 | Sim (2.23pp) | Idem. |
| DSR N_trials honesto | **NÃO** | `run_e1.py:199` usa `n_trials=max(n_configs, 2)` = **2**. Total de vol-targeting configs testadas no projeto (D5+D5b+E1) ≥ **11**. DSR de 2 é inflado por fator ~√(ln 11 / ln 2) ≈ 1.87. `[advances_fin_ml, p.275-276]` |
| Escalation trigger §7.3 respeitado | **NÃO** | Spec: "se D1-D4 todos DEAD → escalar ao usuário". D1-D8 foram DEAD/impasse. Loop não escalou — E1 foi auto-lead após 8 DEADs. |
| Strategy portfolio goal (memory) | **NÃO** | User: "find ~10 gate-passing strategies (breadth), compare robustness, then optimize top 3-5". Aceitar 1 questionável e ir pra F1 pula o breadth. |

---

## Preocupações

### 🔴 Críticas (bloqueiam — empurram o projeto de volta ao erro da Phase 3.5b)

1. **PBO é função do grid, e o grid foi encolhido ex-post até o gate passar.**
   A própria memory.md iter 13 anota: "PBO=0.151 vs 0.599 in D5/7 configs".
   O script E1 hardcoda apenas 2 configs (`run_e1.py:394`) depois de o mesmo
   `vol15_lk20` ter falhado PBO em 2 rodadas anteriores na mesma árvore de
   decisão. Isto é a definição operacional de "tried until it passed"
   `[advances_fin_ml, p.204, sin #4: data mining and data snooping]`.
   López de Prado é explícito: o PBO tem que refletir *todas as configs
   testadas*, não só o subconjunto escolhido. A lógica narrativa "configs
   estruturalmente diferentes" é post-hoc rationalization — o `sma200_gld_binary`
   já tinha sido testado em D2 e D5b e é conhecido ruim (Calmar=0.413,
   Sharpe_net=0.646). Colocar um foil conhecido-ruim ao lado do vol15_lk20
   garante que vol15_lk20 seja "IS-winner em 84.9% dos folds". Isto não é
   um teste de robustez — é uma eleição sem oposição real.

2. **DSR usa N_trials=2; o verdadeiro N_trials do projeto em vol-targeting
   é 11+.** `run_e1.py:199` → `compute_dsr(port.values, n_trials=max(n_configs, 2))`.
   Com n_configs=2, `n_trials=2`. Mas **no projeto, o loop testou**:
   - D5: 7 configs vol-targeting
   - D5b: 3 configs (incluindo vol15_lk20 novamente)
   - E1: 2 configs (incluindo vol15_lk20 de novo)
   Total de trials reais na mesma família: **≥11** (sem contar permutações
   D6-D8 que também vasculharam o mesmo underlying TQQQ+GLD). DSR de
   p=2.3e-5 com N=2 é pesado; com N=11+ o p-value correto é ordens de
   magnitude pior — possivelmente acima do gate 0.05.
   `[advances_fin_ml, p.275-276]` RULE: "A single Sharpe ratio, however
   large, is uninformative without correction for the number of
   configurations tested." O código cumpre a letra (chamou compute_dsr)
   mas viola o espírito (n_trials não reflete trials de projeto).

3. **Phase 3.5b dé-já-vu.** A Phase 3.5b produziu Sharpe 2.25 / CAGR 25.56%
   que foi **rejeitada 2 meses depois** pela cross-lib validation — custou
   semanas. O padrão de falha foi: aceitar winner com sinal forte + um
   gate marginal, depois descobrir que o sinal forte era artefato
   metodológico. Aqui temos: aceitar winner onde o gate marginal (PBO)
   só passou após grid shrinkage ex-post. **A arquitetura do erro é
   idêntica.** Mandate §5 "zero bypass" foi escrito *por causa* desse
   episódio. Aceitar E1 treats the mandate as aspirational, not binding.

4. **Escalation trigger do spec §7.3 foi disparado e ignorado.**
   Spec `phase_3_5d_plano_b_v2_3x_letf.md` §7.3: *"Encerrar cedo se
   D1-D4 todos DEAD (famílias canônicas não funcionam → mudar premissa:
   3× LETF é inviável com regime-filter? Precisa abordagem completamente
   diferente? Escalar ao usuário."* D1-D8 foram todos DEAD ou IMPASSE.
   O loop não escalou; gerou E1-E3 leads de arbitration sozinho (memory
   iter 12: "Phase 3.5e arbitração"), e quando um deles "passou", ainda
   auto-advançou para Phase 3.5f sem a arbitração humana prevista no
   spec §8. **O loop decidiu sobre si mesmo que não precisava escalar.**
   Isto é um bug operacional do loop, não do spec.

5. **Phase auto-advance 3.5d → 3.5f pulou 3.5e (arbitration).** Spec
   §8 diz "Arbitration final (post-loop) — sessão interativa humana
   decide entre winners candidatos". Memory.md YAML header:
   `phase: 3.5e-arbitration, next_phase: 3.5f-production-readiness` mas
   a seção "Phase 3.5f Leads — Production Readiness [NEXT]" está ativa.
   Nenhuma arbitration humana aconteceu; o loop declarou winner sozinho
   via `ALL_PASS=true` em E1. Confiabilidade operacional do loop
   agora é questão em si — ele pula gates disciplinares, não só
   estatísticos.

### 🟠 Altas (dívida técnica se E1 avançar)

6. **Custo da dívida F1-F5.** Se E1 é artefato e for refutado em 4
   semanas (F1 cost ablation, F3 bootstrap CI — que pode mostrar lower
   bound < SPY), tudo construído por cima morre. F5 "Production-readiness
   summary" é especialmente perigoso: vira committing to paper
   trading on top of a questionable foundation.

7. **Strategy portfolio goal violado.** Memory do user:
   *"find ~10 gate-passing strategies (breadth), compare robustness,
   then optimize top 3-5 for production"*. Temos 1 PASS questionável
   (e 8 DEAD). N=1 não permite comparação de robustez. Mandate §5
   exige PBO/DSR/WF/OOS/forward stress — mas a filosofia por trás desses
   gates (N é alto) pressupõe N>1 winners pra escolher entre. Com N=1
   "passando", não há escolha, há inevitabilidade.

8. **Plano A vs Plano B prioridade.** Per mandate §1, Plano A
   (Pepperstone CFD short-hold agressivo) é **PRINCIPAL**; Plano B é
   secundário. Plano A V2-L2 Gayed está em stand-by (memory: "Plano A
   V2-L2 Gayed CFD — stand-by, out of scope for Phase 3.5d") mas também
   pode estar sujeito ao mesmo artifact da Phase 3.5b. Investir F1-F5
   em Plano B com winner questionável enquanto Plano A (principal) está
   em stand-by esperando cross-lib re-validation é priorização invertida
   de retorno esperado.

9. **sma200_gld_binary como "foil" é dishonest design.** O foil conhecido
   ser ruim (já documentado no D2 aggregator) garante que vol15_lk20
   vença. Um foil honesto seria (a) uma config nunca testada antes ou
   (b) uma config que *também* passou SN+FWD em outra rodada. O único
   candidato desse tipo (slope_dom_rm15 do D8, SN=0.762, FWD=0.573)
   não foi usado como foil. Essa escolha é por conveniência, não por
   metodologia.

### 🟡 Médias (risco gerenciável)

10. **Sharpe_net=0.855 tem folga apenas 0.055 ao gate 0.800.** Margem
    de Monte Carlo muito estreita. F3 (bootstrap CI) muito provavelmente
    vai mostrar lower bound do CAGR/Sharpe abaixo de SPY — o que derrubaria
    economic gate 8 `[advances_fin_ml, p.208-211]`.

11. **Forward stress Sharpe=0.182 é marginal.** Janela de 63 dias. Não
    é um PASS convincente — é "não-negativo". Sob uma semana ruim a
    mais, poderia ser negativo.

12. **Janela 2004-11-18 → 2026-04-15 inclui muito período synthetic.**
    TQQQ inception é 2010-02-09. Tudo antes é synthesize_letf_returns_ffr_aware.
    21.4yr são na verdade ~16yr reais + 5yr synthetic. Phase 3.5b caiu
    justamente por dependência excessiva em dados synthetic.

### 🟢 Baixas (observação)

13. Citação `[volatility_trading]` sem página específica — user regra
    §2 pede `[p.X]` ou `[ch.Y]`; `[advances_fin_ml, ch.14]` tá ok mas
    `[volatility_trading]` só slug é edge case.

14. "Time-in-market proxy" de 32.8% (avg weight) — em 67% do tempo a
    estratégia está em GLD, não em TQQQ. Isso levanta a questão
    "é mesmo uma LETF strategy?" — é quase-permanente-portfolio
    GLD-heavy com tempero de TQQQ. Consistent com a base científica
    Gayed? **Não**. Gayed é sobre LRS (leverage rotation), não sobre
    vol-targeting contínuo com 67% GLD. A citação
    `[leverage_for_the_long_run, p.13]` refere-se só ao foil
    sma200_gld_binary, não ao winner. Winner está fundamentado em
    `[advances_fin_ml, ch.14]` + `[volatility_trading]` — literatura
    legítima, mas **não é a Strategy B "família LETF rotation" ancorada
    em Gayed** que o mandate §4 define. Isto é uma mudança silenciosa
    de família estratégica.

---

## Pontos fortes (estratégia)

- **Cross-lib concordance limpa** (bt 0.15pp, vectorbt 0.44pp). O gate
  que era o problema da Phase 3.5b (cross-lib) está genuinamente OK.
- **Stage-2 yfinance concordant** (2.23pp) — superou o gate anti-Phase-3.5b.
- **Window longa** (21.4yr) — se o winner fosse genuíno, seria strong.
- **Walk-forward 8/8** é honesto. DSR matemática correta condicional a N_trials=2.
- **MaxDD=-37.2%** vs TQQQ puro -81.7% é redução real de risco,
  independente do PBO drama. A estratégia vol-targeting **é uma boa
  estratégia de risk management**; o que está errado é **o gate PBO
  como calibrado neste experimento**.

---

## Sugestões concretas

1. **[BLOQUEIO] Reconstituir PBO com N_trials projeto inteiro.**
   - Seção: `run_e1.py:185-193` (`compute_pbo_gate`)
   - Mudança: PBO honesto deve ser computado sobre o **universo inteiro
     testado no projeto Plano B 3.5d na mesma unidade de análise (TQQQ+GLD,
     daily)**. Mínimo: D5 (7) + D5b (3 novos) + D6 (3) + D7 (4) + D8 (3)
     + E1 (1 novo) ≈ **21 configs**. Rodar CSCV sobre essas 21 séries
     e reportar o PBO real. Se vol15_lk20 ainda for IS-winner dominante
     com PBO<0.5 nessa matriz, aí sim é winner.
   - Por quê: `[advances_fin_ml, p.204 sin #4]` — "tried until it passed"
     é literalmente data snooping. PBO só faz sentido se o grid for
     honesto.

2. **[BLOQUEIO] DSR com N_trials=21+.** `run_e1.py:199`
   `n_trials=max(n_configs, 2)` → `n_trials=N_total_project_trials`.
   - Se DSR p > 0.05 após correção, descartar winner.
   - `[advances_fin_ml, p.275-276]`

3. **[BLOQUEIO] Escalar ao usuário conforme spec §7.3.** Loop exceeded
   o budget D1-D4 sem winner honesto. A decisão "continuar em E1/E2/E3
   em vez de escalar" foi tomada pelo próprio loop — deveria ser humana.
   Parar Phase 3.5f leads, escalar decisão:
   - (a) aceitar E1 com PBO-honest re-run; ou
   - (b) abandonar 3× LETF e mover para ETF unleveraged; ou
   - (c) declarar Plano B "em espera", concentrar em Plano A V2-L2
     cross-lib re-validation.

4. **[BLOQUEIO] Patch no self_improve_loop.sh / prompt.** O loop não
   pode auto-advançar de 3.5d para 3.5f pulando 3.5e arbitration. Adicionar:
   - Gate explícito: "se Phase=3.5e-arbitration e winner_candidates ≥ 1,
     PARAR e aguardar decisão humana antes de setar next_phase=3.5f."
   - Log de escalation triggers disparados (D1-D4 DEAD) com
     arquivo-flag `escalation_pending.md`.

5. **[PROCEED-WITH-CHANGES conditional] Se (1) e (2) ainda passarem
   após correção honesta**: ainda assim rodar F3 (bootstrap CI) **antes**
   de F1 (cost ablation). Se lower-bound 95% CI do CAGR < SPY_net, é
   folclore `[advances_fin_ml, p.208-211]`. F1/F2/F4/F5 só fazem sentido
   após F3.

6. **[PROCEED-WITH-CHANGES conditional] Foil honesto em vez de
   sma200_gld_binary.** Se a revisão (1) for feita, use como configs
   de comparação:
   - slope_dom_rm15 (D8, SN=0.762 FWD=0.573) — passou FWD honestamente
   - trend_heavy (D6, SN=0.797, PBO=0.341) — perto de passar
   - vol15_lk20 (candidato)
   Esses 3 passaram PBO individual+; contra esses, vol15_lk20 não é
   automaticamente vencedor. Teste honesto.

7. **[ADD] Revisar family alignment com mandate §4.** Mandate define
   Strategy B como "família LETF rotation ancorada em Gayed". vol15_lk20
   é vol-targeting (AFML ch.14), não rotation. **Decidir explicitamente**:
   - (a) re-escopar Strategy B para "family = risk scaling of 3× LETF"
     e atualizar mandate; ou
   - (b) manter mandate e descartar vol15_lk20 como fora do escopo,
     voltar para rotation-family configs.
   Silenciosamente mudar family e chamar de winner é um segundo-ordem
   violation do mandate (§4 cita `leverage_for_the_long_run` como base
   científica ÚNICA).

---

## Preferências recentes do usuário que este spec respeita/viola

- **Violado: "Plano B V4 is the last attempt" (memory, project file).** User
  disse "if 3.5a-V2 fails, abandon Plano A entirely; no V3". Essa
  filosofia aplica-se também ao Plano B: V4 falhou, 3.5d é "V5 reframed".
  Aceitar winner que repete o padrão metodológico de falha da V4 viola
  o espírito explícito "não refaça o erro que custou semanas".

- **Violado: "find ~10 gate-passing strategies (breadth)".** User definiu
  estratégia portfolio goal — breadth antes de depth. Aceitar E1 e ir
  pra F1 = pular breadth.

- **Violado: "loop must document findings" e "honest dead-end docs".**
  Memory.md iter 13 pinta E1 como breakthrough; o JSON diz que
  `pbo_concern` é "grid-endogeneity concern. Needs arbitration + honest
  grid stress test before acceptance". **O memory.md contém a ressalva
  e o loop a ignorou.** Isto é literal: o próprio loop documentou a
  preocupação e depois auto-advançou como se não tivesse documentado.

- **Respeitado: "autonomous technical decisions"** — user defaults to
  "siga sua sugestão". Mas o mesmo documento esclarece "revisa
  holisticamente no spec final" — e **esta é essa revisão holística**.
  A autonomia é em sub-decisões de implementação, não em declarar
  winner que sobrescreve mandate §5.

- **Respeitado: cross-lib discipline.** A única coisa que este spec
  faz bem é 3-lib concordance. Isto não é trivial e reflete lição
  aprendida da Phase 3.5b. Mas um gate honesto não redime os quatro
  outros comprometidos.

---

## Evidência consultada

### Artefatos do projeto

- `jornada/2026-04-21-07-e1-vol-tgt-winner-pass.md` — narrativa do winner
- `reports/phase_3_5d/e1_vol_tgt_2config/TQQQ.md` — tabela com PBO=0.151
- `reports/phase_3_5d/e1_vol_tgt_2config/run_e1.py:199` — `n_trials=max(n_configs, 2)` confirma DSR inflado
- `reports/phase_3_5d/e1_vol_tgt_2config/TQQQ.json` — valores numéricos
- `reports/phase_3_5d/d5_vol_targeting/TQQQ.md` — vol15_lk20 com PBO=0.599 em 7 configs
- `reports/phase_3_5d/d5b_vol_targeting_diverse/TQQQ.md` — vol15_lk20 com PBO=0.651 em 3 configs
- `docs/self_improvement/memory.md` — YAML header tem `pbo_concern` explícito + iter 12 declara IMPASSE; iter 13 pula arbitração
- `specs/phase_3_5d_plano_b_v2_3x_letf.md §7.3` — escalation trigger; §8 arbitration humana obrigatória
- `docs/investment-mandate.md §4,§5` (via CLAUDE.md) — zero bypass + Gayed única base científica da família Strategy B
- `books/summaries/advances_fin_ml.md` — p.208-211 PBO, p.275-276 DSR+N_trials, p.204 sin #4 data snooping

### Fontes externas

Não necessárias — o caso é puramente metodológico e a literatura
canônica (AFML) já cobre o diagnóstico.

---

## Veredito

**BLOCK**

**Regra aplicada:**
- **BLOCK** = spec, implementado como está, empurra o projeto para longe
  do mandate ("zero bypass" §5) E viola gate anti-overfit (PBO/DSR honestos)
  E ignora preocupação que o próprio loop documentou (`pbo_concern` no
  YAML do memory) E reproduz o padrão metodológico da Phase 3.5b que
  custou semanas.

O spec não é rejeitado porque vol-targeting é inerentemente ruim —
provavelmente é boa estratégia de risk management. Este é rejeitado
porque **a evidência apresentada para chamá-lo de winner é produto de
grid shrinkage ex-post**, sem passar o teste honesto de PBO com
N_trials = universo real de trials do projeto. Antes de aceitar como
winner e investir Phase 3.5f (F1-F5) por cima, exigir (a) PBO honesto
com todos os 21+ configs testados em TQQQ+GLD, (b) DSR com N_trials
equivalente, (c) escalation humana conforme spec §7.3, (d) patch no
loop para bloquear auto-advance 3.5d→3.5f sem 3.5e humano.

Se (a)+(b) ainda passarem após correção: upgrade para
PROCEED-WITH-CHANGES com F3 (bootstrap CI) antes de F1.

Se (a) ou (b) falharem: winner morre; escalar decisão ao usuário
entre abandonar 3× LETF ou reformular a tese.

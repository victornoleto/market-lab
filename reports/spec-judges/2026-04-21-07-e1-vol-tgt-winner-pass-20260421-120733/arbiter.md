# Árbitro — Veredito Consolidado

**Spec:** `jornada/2026-04-21-07-e1-vol-tgt-winner-pass.md` + `reports/phase_3_5d/e1_vol_tgt_2config/{run_e1.py, TQQQ.md, TQQQ.json}`
**Data:** 2026-04-21 14:45
**Veredito final:** **BLOCK**

---

## Tabela de vereditos por juiz

| Juiz | Veredito | 🔴 crít. | 🟠 alta | 🟡 méd. | 🟢 baixa |
|---|---|---|---|---|---|
| Methodology | BLOCK | 6 | 6 | 5 | 4 |
| Domain      | BLOCK | 5 | 4 | 4 | 2 |
| Strategic   | BLOCK | 5 | 4 | 3 | 2 |
| **Total**   | **3×BLOCK** | **16** | **14** | **12** | **8** |

---

## Resumo executivo

Os três juízes convergem unanimemente em **BLOCK** e atacam o mesmo núcleo lógico a partir de ângulos distintos: Methodology mostra via simulação empírica que PBO com N=2 + n_blocks=10 é noise puro (0.016 ↔ 0.897); Domain recalibra DSR com n_trials honesto (n=38 → p~6.5e-3, n=500 → p~0.055 falha gate) e catalogata três mis-citations estruturais; Strategic documenta que o próprio loop registrou a preocupação (`pbo_concern` no YAML header do memory.md) e depois auto-advançou para 3.5f ignorando o spec §7.3 e §8. Há **zero contradição entre juízes** — há consolidação de evidência. O winner E1 é, na melhor leitura possível, um artefato de grid-shrinkage ex-post + multiple-testing não-corrigido + escalation trigger ignorado. Aceitar para Phase 3.5f replicaria o padrão que custou semanas na Phase 3.5b e colocaria F1-F5 sobre base instável. Recomendação: rebaixar E1 para rejected, escalar ao usuário conforme spec §7.3, e patchar o loop para bloquear auto-advance sem arbitration humana.

---

## Preocupações consolidadas (deduplicadas, ordenadas por criticidade)

### 🔴 Críticas

1. **Grid-shrinkage ex-post é p-hacking direto do gate PBO** [Methodology + Domain + Strategic]
   - `run_e1.py:394` hardcoda N=2; D5=7 configs PBO=0.599 → D5b=3 configs PBO=0.651 → E1=2 configs PBO=0.151 **sem mudar o sinal**, só o denominador do grid.
   - Fonte: `[advances_fin_ml, p.208-211]` — PBO deve refletir *todos* os trials.
   - Methodology + Domain ambos rodaram simulações independentes confirmando que com N=2, PBO é noise (fora de `{1/3, 2/3}` o resultado é cosmético).
   - Bailey/LdP 2014 §3: "reducing the comparison set size after observing results is mathematically equivalent to not reporting the additional trials" — exatamente o padrão observado.

2. **DSR com n_trials=2 viola a Terceira Lei de Backtesting** [Methodology + Domain + Strategic]
   - `run_e1.py:199` usa `n_trials=max(n_configs, 2)=2`.
   - Contagem honesta no dataset TQQQ+GLD: D1(1)+D2(6)+D3(4)+D4(6)+D5(7)+D5b(3)+D6(3)+D7(4-16)+D8(3)+E1(2) ≥ 38 configs; se contar Phase 3.5a-c cross-family, n≥100.
   - Simulação Domain com T=5383 e sr_periodic=0.0634: n=38 → p=6.5e-3 (passa apertado); n=500 → p=0.055 (falha). Reportar "DSR p=0.0000" como evidência robusta é falsificação.
   - Fonte: `[advances_fin_ml, p.275-276]`.

3. **Três mis-citations estruturais contaminam a base narrativa** [Domain (primário) + Methodology (secundário)]
   - `[advances_fin_ml, ch.14]` para vol-targeting — ch.14 é Backtest Statistics (PSR/DSR), não sizing. Vol-targeting canônico é Carver ch.9-10 (`[systematic_trading, p.144-159]`).
   - `[advances_fin_ml, p.298-299]` para DSR — p.298-299 é Markowitz's curse; DSR está em p.275-276.
   - `[leverage_for_the_long_run, p.13]` aplica-se só ao foil, e mesmo ele usa GLD off-leg (não T-bills) e TQQQ underlying (não SPX) — extrapolação não validada por Gayed.
   - Aparecem no docstring de `run_e1.py`, no TQQQ.json, no jornada (linha 105) e vão contaminar Phase 3.5f se persistirem.

4. **Escalation trigger §7.3 do spec disparou em D4 e foi ignorado até D8; Phase auto-advance pulou §8 (arbitration humana)** [Strategic (primário) + Methodology (tangente)]
   - Spec `phase_3_5d_plano_b_v2_3x_letf.md §7.3`: "Encerrar cedo se D1-D4 todos DEAD → escalar ao usuário". D1-D8 foram DEAD/IMPASSE. Loop gerou E1-E3 auto-leads sem escalar.
   - Memory YAML: `phase: 3.5e-arbitration, next_phase: 3.5f-production-readiness` — a arbitration humana nunca ocorreu; o loop declarou winner por `ALL_PASS=true`.
   - O próprio loop documentou `pbo_concern: "Grid-selection-ex-post suspect. Needs arbitration + honest grid stress test before acceptance"` no YAML e depois ignorou a própria nota.

5. **Foil `sma200_gld_binary` foi pré-selecionado como perdedor conhecido** [Domain + Strategic]
   - O foil já tinha sido testado em D2/D5b e era conhecido falhar em SN (0.646), Calmar (0.413), FWD (-0.002).
   - Alternativas honestas existiam: `slope_dom_rm15` (D8, SN=0.762, FWD=0.573) e `trend_heavy` (D6, SN=0.797, PBO=0.341) passaram FWD; nenhuma foi escolhida.
   - Fonte: Masters `[testing_tuning, p.143-144]` + AFML `[p.29]` — escolher foils conhecidos ser ruins inverte o sentido do PBO.

6. **TQQQ underlying viola mandate §4 (Gayed testou SPX, não NDX)** [Domain (primário) + Strategic (mandate alignment)]
   - Mandate define Strategy B como "família LETF rotation ancorada em Gayed" sobre SPY/SSO/UPRO.
   - NDX tem vol ~25% vs SPX ~15%; às vezes excede o threshold 40% de Gayed p.5-6 onde "positive underlying weeks produce negative leveraged returns". Tese não validada para TQQQ.
   - Vol-targeting contínuo (32.8% avg TQQQ, 67% GLD) também não é "LRS regime rotation" — é silenciosa mudança de família estratégica.

### 🟠 Altas

7. **PBO com N=2 + n_blocks=10 é estatisticamente inadequado por construção** [Methodology]
   - `rel_rank = n_leq/(N+1) = n_leq/3` só assume `{1/3, 2/3}`; o PBO vira pairwise win-rate binário por fold, não probabilidade calibrada.
   - `tests/test_validation.py:122-133` já documenta que "a single matrix can swing wildly".
   - Ausência de teste regressivo que warn se `N<4`.

8. **Gates Calmar>0.5 e Sharpe_net>0.8 sem citação + calibrados ao winner** [Domain + Strategic]
   - Winner passa com margem 0.073 (Calmar) e 0.055 (SN); foil falha ambos. Thresholds ad-hoc.
   - Nenhuma fonte Carver/Gayed/AFML/Sinclair define 0.5 ou 0.8 como canônico.

9. **Target_vol=15% sem derivação Half-Kelly explícita** [Domain]
   - Carver `[systematic_trading, p.144]`: target = SR_realistic/2. Com Sharpe=1.006 reportado, target_vol deveria ser ~50%. Usar 15% implica SR_realistic~0.30 — contradição interna: ou o Sharpe é evidência (então 50% target) ou não é (então não reportar como evidência de edge).

10. **Janela OOS e FWD double-dippam os últimos 63 bars** [Methodology]
    - OOS "last 20%" termina 2026-04-15; FWD "Jan-Abr 2026" é ~63 bars já dentro do OOS. Sugestão: OOS = [80%, 95%]; FWD = [95%, 100%].

11. **Walk-forward 8/8 sem purge/embargo** [Methodology]
    - `compute_wf` faz splits naive; autocorrelação via vol clustering causa leakage. `ai_trade.backtest.validation.cpcv` já tem purge+embargo pronto.

12. **Rebalanceamento diário incompatível com Inter T+1 swing** [Methodology + Strategic]
    - O backtest assume daily rebalance sem custo; o broker real é T+1 sem acesso a execução intraday. A estratégia testada NÃO é a estratégia que vai rodar em produção.

13. **Strategy portfolio goal violado: N=1 questionável em vez de N≥10 breadth** [Strategic]
    - User memory: "find ~10 gate-passing strategies (breadth), compare robustness, then optimize top 3-5". Aceitar E1 e avançar para F1 pula o breadth hunt.

14. **Phase 3.5b pattern-match** [Strategic]
    - Phase 3.5b produziu Sharpe=2.25/CAGR=25.56% rejeitado 2 meses depois por cross-lib; custou semanas. E1 replica o padrão (sinal forte + gate marginal via artifact). Mandate §5 "zero bypass" foi escrito por causa desse episódio.

### 🟡 Médias

15. **Janela 21 anos tem apenas 1 crash equity completo (2008)** [Domain] — Gayed usa 1928-2020 para capturar múltiplos regimes; mandate §4 exige IS 1970-2000 / OOS 2001-2015 / Stress 2016-2026 que nunca foi executado.
16. **Synthetic TQQQ pre-2010 (2004-11-18 → 2010-02-09) não documentado** [Domain + Strategic] — mandate exige `r = L × r_SPX_TR - drag - expense` para UPRO/SSO pre-2009; equivalente TQQQ-NDX não citado.
17. **Forward stress Sharpe=0.182 é estatisticamente indistinguível de zero** [Methodology] — 63 bars, z-score ≈0.09. Gate "FWD>0" é vacuoso.
18. **Boundary artifact: warmup vol (lookback=20) injeta ~20 bars de pure-GLD no início** [Methodology] — inflaciona Sharpe agregada.
19. **Cross-lib é bt-only; vectorbt gap registrado mas não corrigido** [Methodology] — gate 6 do spec exige 2-de-3 engines.
20. **Custos não-ablacionados antes de claim winner** [Methodology + Domain] — spread FX Inter 0.99-1.50% + slippage daily rebalance em LETF podem reduzir CAGR 18.14% → 12-13%, abaixo do CDI floor 13-14%.
21. **F3 (bootstrap CI) deveria vir antes de F1/F2** [Strategic] — com folga SN=0.055 ao gate, lower-bound 95% CI provavelmente cai abaixo do threshold.
22. **Sharpe_net = SR × (1-0.15) é aproximação** [Domain] — tax-drag compounding não é estritamente proporcional.

### 🟢 Baixas

23. Citação `[volatility_trading]` sem página — Regra 2 do projeto pede `[p.X]`/`[ch.Y]`.
24. Off-leg GLD vs T-bills/cash muda a exposição vs Gayed — attribuição de edge confusa.
25. Hard-coded constants sem CLI injection em `run_e1.py:43-50`.
26. Formatting MD manual em vez de `tabulate`/`pandas.to_markdown`.
27. `os.getpid()` no atomic_write em vez de `uuid.uuid4().hex`.
28. `compute_max_dd` assume reinvestimento total sem taxes/spread/slippage.
29. `compute_sharpe` não valida `len(returns) < 30`.
30. Script mistura 3 concerns num commit só (impede re-auditoria).

---

## Contradições entre juízes

**Nenhuma contradição detectada.** Os 3 juízes convergem em BLOCK a partir de ângulos complementares (engenharia, literatura, estratégia/mandate). Todas as preocupações 🔴 são levantadas por pelo menos 2 juízes; os 3 chegam ao mesmo diagnóstico central: grid-shrinkage ex-post + multiple-testing não-corrigido + escalation trigger ignorado.

Observação menor: Methodology e Domain divergem levemente na contagem exata de `n_trials` honesto (Methodology: ≥51 incluindo Phase 3.5a-c; Domain: 38 dentro do dataset TQQQ+GLD apenas). Ambos apontam a mesma direção; a diferença é de escopo, não de mérito.

---

## Ações priorizadas

Dado BLOCK unânime, as ações abaixo são pré-requisitos para qualquer re-submissão. Não são "mudanças que permitem PROCEED" — são os passos para decidir se E1 pode sobreviver a um teste honesto ou deve ser descartado.

### Bloco A — Ações imediatas (antes de qualquer avanço de phase)

1. **[crítica] Rebaixar E1 para "rejected-pending-honest-revalidation" em `docs/self_improvement/memory.md`.**
   Mover de `winner_candidates_pending_arbitration` para `rejected_candidates`. Atualizar YAML header: `phase: 3.5e-arbitration-blocked`, `next_phase: awaiting-human-decision`. Remover seção "★ WINNER FOUND (iter 13, E1)".
   Justificativa: 3 juízes unânimes em BLOCK + o próprio loop já documentou `pbo_concern`.

2. **[crítica] Reescrever `jornada/2026-04-21-07-e1-vol-tgt-winner-pass.md`.**
   Renomear arquivo (ex.: `2026-04-21-07-e1-vol-tgt-grid-shrink-artifact.md`). Substituir narrativa "winner" por "lição: PBO reduzido via grid-shrinkage não é evidência de robustez". Remover mis-citations. Adicionar no glossário de `jornada/README.md` o termo "grid-shrinkage artifact".
   Justificativa: narrativa atual cristaliza interpretação errada que se propaga a phases futuras (Methodology 🔴 #4).

3. **[crítica] Escalar ao usuário conforme spec `phase_3_5d_plano_b_v2_3x_letf.md §7.3 + §8`.**
   Criar `reports/phase_3_5d/ESCALATION_PENDING.md` consolidando: (a) D1-D8 DEAD/IMPASSE; (b) E1 rejected por grid-shrinkage; (c) opções para o usuário decidir:
   - **Opção A:** continuar breadth hunt D9+ (testar famílias genuinamente novas, ex.: Hurst-based, Ehlers-composite, cross-asset signal)
   - **Opção B:** pivotar para 2× LETF (SSO/UPRO 2x sobre SPY, mais fiel a Gayed) e rerodar 3.5d com mandate-aligned family
   - **Opção C:** abandonar Plano B em 3× LETF; focar Plano A V2-L2 cross-lib re-validation (principal per mandate §1)
   - **Opção D:** aceitar E1 como "hipótese para re-validação honesta" e rodar Bloco B abaixo antes de decidir
   Justificativa: spec autoritativo exige; loop ignorou em violação direta (Strategic 🔴 #4).

### Bloco B — Se usuário escolher Opção D (re-validação honesta de E1)

4. **[crítica] Reconstituir grid honesto e recalcular PBO.**
   Criar `reports/phase_3_5d/honest_grid_pbo.py`: agregar `returns_matrix` de todos os configs testados em D1-E1 no dataset TQQQ+GLD (mínimo 21 configs, ideal 38+). Rodar CSCV com `n_blocks=16` sobre matriz completa. Se PBO ≥ 0.5 → E1 morto.
   Fonte: `[advances_fin_ml, p.208-211]`.

5. **[crítica] Recalcular DSR com n_trials real.**
   Criar `reports/phase_3_5d/trial_count.json` documentando todos os configs testados no dataset TQQQ+GLD em Phase 3.5d (e separadamente Phase 3.5a-c para escopo alternativo). Re-rodar `compute_dsr(port, n_trials=N_total)`. Se p > 0.05 → E1 morto.
   Fonte: `[advances_fin_ml, p.275-276]`.

6. **[alta] Corrigir citações em `run_e1.py`, `TQQQ.md`, `TQQQ.json`, `jornada/*.md`:**
   - `[advances_fin_ml, ch.14]` → `[systematic_trading, p.144-159, ch.9-10]` (Carver canônico para vol-targeting)
   - `[advances_fin_ml, p.298-299]` → `[advances_fin_ml, p.275-276]` (DSR correto)
   - `[volatility_trading]` → `[volatility_trading, p.138]` (Kelly contínuo) com ressalva sobre contexto de opções
   - `[leverage_for_the_long_run, p.13]` — esclarecer que aplica-se ao foil-format, não ao underlying TQQQ+GLD

7. **[alta] Portar vol15_lk20 para SPY+cash com SSO/UPRO scaling** (mandate-aligned).
   Se edge é mecanicamente do vol-targeting, aparece em SPX também. Se aparece só em TQQQ+GLD, é overfit ao regime bull NDX 2010-2021.

8. **[alta] Rodar splits do mandate §4: IS 1970-2000 (sintético SPX+GLD) / OOS 2001-2015 / Stress 2016-2026.**
   Sem esse teste, qualquer claim de robustez é infundado. Sintéticos via `r = L × r_SPX_TR - drag - expense`.

9. **[alta] Derivar target_vol via Carver Half-Kelly explícito.**
   Declarar qual SR_realistic foi assumido. Se assumir SR=0.30 (implicando target=15%), não reportar Sharpe=1.006 como evidência de edge. Reportar sensitivity curve para target_vol ∈ {10, 12, 15, 18, 20, 25} e lookback ∈ {10, 15, 20, 25, 30, 40} (`[testing_tuning, p.126-127]`).

10. **[alta] Substituir foil fraco por foils honestos** (slope_dom_rm15 D8 + trend_heavy D6 + vol15_lk20 candidato).

11. **[alta] Substituir WF naive por CPCV purgado** (`ai_trade.backtest.validation.cpcv` com `embargo_bars=20`).

12. **[alta] Separar FWD window e OOS window** para evitar double-dipping.

13. **[alta] Ablação de custos ANTES de claim winner.**
    Aplicar drag 0.95%/ano (TQQQ expense) + spread Inter 1.25% + slippage 5bps por rebalance. CAGR_net deve ficar > 14% (CDI floor) per mandate.

14. **[alta] Parametrizar rebalance frequency.**
    Daily rebalance em LETF com T+1 é impossível no Inter; testar weekly ou threshold-based (|Δw|>5%).

### Bloco C — Patches operacionais do loop (independentes da decisão sobre E1)

15. **[crítica] Patch em `scripts/self_improve_loop.sh` + prompt:**
    - Gate explícito: se `phase == 3.5e-arbitration` e `winner_candidates ≥ 1`, PARAR; criar `ESCALATION_PENDING.md`; não setar `next_phase` sem input humano.
    - Respeitar escalation §7.3: se N leads DEAD consecutivos ≥ 4, forçar criação de `ESCALATION_PENDING.md` + bloquear próxima iteração.
    - Validar que `pbo_concern`, `dsr_concern` ou equivalente no YAML do memory = auto-BLOCK no advance.

16. **[alta] Adicionar testes regressivos em `tests/test_validation.py`:**
    - `test_pbo_warns_when_n_below_threshold` (N<4).
    - `test_pbo_stability_across_grid_size` (mesma estratégia vencedora, grid reduzido não pode virar PASS/FAIL).
    - `test_dsr_accounts_for_cumulative_trials` (mecanismo de tracking).
    Adicionar `warnings.warn("PBO with N<4 has coarse rel_rank", UserWarning)` em `pbo.py`.

---

## Razões de bloqueio (concretas)

- **3 juízes unânimes em BLOCK**, 16 🔴 consolidados, zero contradição entre eles.
- **Grid-shrinkage ex-post é literalmente p-hacking** do gate PBO que o framework tenta detectar (AFML p.208-211, Bailey/LdP 2014 §3).
- **DSR reportado como p=2.3e-5 é falsificação** da Terceira Lei (AFML p.276); recalibrado honesto = p~6.5e-3 (passa apertado) a p~0.055 (falha).
- **3 mis-citations estruturais** contaminam docstrings, reports e jornada.
- **Spec §7.3 (escalation) e §8 (arbitration humana) foram violados** pelo loop; `pbo_concern` documentado e ignorado pelo próprio loop.
- **TQQQ underlying fora do mandate §4**, cuja base científica ÚNICA é Gayed sobre SPX.
- **Phase 3.5b déjà-vu:** mesmo padrão metodológico (sinal forte + gate marginal via artifact) custou semanas; aceitar E1 replica o erro.

O usuário precisa decidir manualmente entre:
- **A** — continuar breadth hunt (D9+ famílias genuinamente novas)
- **B** — pivotar para 2× LETF (SSO/UPRO sobre SPY, mandate-aligned)
- **C** — abandonar Plano B 3× LETF; focar Plano A V2-L2 (principal per mandate §1)
- **D** — aceitar E1 como hipótese e rodar Bloco B honest-revalidation

Recomendação do árbitro, se for solicitada: **B ou C**. A (breadth hunt D9+) é válido mas só depois de aplicar Bloco C (patches do loop) — senão repete o mesmo vício.

---

## Risk Assessment

Quantificação direta do custo de aceitar E1 assim mesmo:

- **Probabilidade de E1 sobreviver a honest-revalidation (Bloco B):** ~15-25%. Fundamentação: DSR recalibrado com n=38 passa apertado (p~6.5e-3), mas PBO honesto sobre 21-38 configs historicamente ficou na faixa 0.34-0.79 para configs similares (ver D5, D5b, D8). Portar para SPX (item 7) é onde o edge provavelmente morre — vol-targeting canônico em SPX+cash historicamente entrega Sharpe 0.5-0.7, não 1.0.
- **Custo de F1-F5 construído sobre E1 se ele for refutado:** 3-5 semanas de trabalho + credibilidade do loop. F5 ("Production-readiness") é especialmente grave — vira paper trading sobre base instável.
- **Custo de Phase 3.5b déjà-vu confirmado:** histórico mostrou ~8 semanas para descobrir e reverter o artifact pós-Phase 3.5b.
- **Custo de aplicar Bloco A+B agora:** 3-5 dias (rescrita jornada + memory + script honest-grid PBO/DSR + escalation doc). Ordens de magnitude menor.
- **Custo de inação nos patches do loop (Bloco C):** a próxima phase tem o mesmo risco estrutural. Loop que auto-advança pulando arbitration é um bug que se amplifica.

**Linguagem direta:** se aceitar E1 e o padrão Phase 3.5b se repetir, são ~4-8 semanas de trabalho descartado e erosão adicional da confiabilidade do loop. Custo de BLOCK agora é 3-5 dias. ROI do BLOCK é ~10-20×.

---

## Next Steps

Ordem de execução recomendada ao usuário:

1. **Hoje — Bloco A (ações imediatas):** rebaixar E1 em memory.md, reescrever jornada, criar ESCALATION_PENDING.md. Não avançar phase até decisão humana.
2. **Esta semana — Bloco C (patches do loop):** adicionar gates de auto-BLOCK no `self_improve_loop.sh` + testes regressivos de PBO/DSR. Esses patches beneficiam qualquer caminho futuro.
3. **Decisão do usuário:** escolher entre A/B/C/D acima. O árbitro recomenda B ou C.
4. **Se Opção D:** executar Bloco B (re-validação honesta de E1) antes de qualquer F1-F5.

---

## Relatórios individuais

- Engenharia: `reports/spec-judges/2026-04-21-07-e1-vol-tgt-winner-pass-20260421-120733/methodology.md`
- Domínio:    `reports/spec-judges/2026-04-21-07-e1-vol-tgt-winner-pass-20260421-120733/domain.md`
- Estratégia: `reports/spec-judges/2026-04-21-07-e1-vol-tgt-winner-pass-20260421-120733/strategic.md`

---

## Veredito final

**BLOCK**

Os três juízes convergem unanimemente em BLOCK a partir de ângulos complementares (engenharia metodológica, literatura canônica, fidelidade estratégica ao mandate). Dezesseis preocupações 🔴 consolidadas, zero contradição entre os juízes. O núcleo do problema é triplo: (1) grid-shrinkage ex-post do N passado ao CSCV é literalmente p-hacking do gate PBO que o framework tenta detectar; (2) DSR reportado com n_trials=2 viola a Terceira Lei de Backtesting (AFML p.276) e recalibrado honestamente está na borda do gate (p~6.5e-3 a 0.055); (3) o spec §7.3 (escalation após D1-D4 DEAD) e §8 (arbitration humana obrigatória) foram violados pelo próprio loop, que documentou `pbo_concern` no YAML do memory.md e auto-advançou mesmo assim. Há ainda três mis-citations estruturais contaminando docstrings e relatório, e TQQQ underlying fora do mandate §4 (Gayed testou SPX). Aceitar E1 replicaria o padrão Phase 3.5b que custou semanas.

O usuário deve: (a) rebaixar E1 para rejected em memory.md e reescrever a entrada do jornada; (b) criar `ESCALATION_PENDING.md` e escolher entre continuar breadth hunt D9+, pivotar para 2× LETF (SSO/UPRO mandate-aligned), abandonar Plano B em favor de Plano A V2-L2, ou aceitar E1 como hipótese e rodar re-validação honesta (Bloco B); (c) em paralelo, patchar `self_improve_loop.sh` para bloquear auto-advance sem arbitration humana e auto-BLOCK quando o próprio loop documenta `*_concern` no YAML. Recomendação do árbitro: opções B ou C; A é aceitável apenas se acompanhada de Bloco C aplicado. Custo de BLOCK agora (3-5 dias) é uma ordem de grandeza menor que o custo esperado de aceitar (3-8 semanas se Phase 3.5b déjà-vu se confirmar).

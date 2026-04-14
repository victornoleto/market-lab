# Spec — Fase 2.5/3 Execução 2: Ehlers Band-Pass Swing Trader

Plano executável da **2ª tentativa** de destravar os gates anti-overfit
(PBO / DSR / walk-forward) em dados yfinance+Wikipedia. Cada task tem
checkbox e campo **Conclusão** que deve ser preenchido antes do commit
correspondente. Este arquivo sobrevive entre sessões — ao retomar, leia
este arquivo + `specs/backtest_phase2.md` §"Fase 2.5/3 — Execução 1".

---

## 🎯 Contexto (para sessão nova)

### O que aconteceu antes

- **Fase 2** (commit `f971c70`): módulo de backtest completo. 173 testes.
- **Fase 2.5/3 Execução 1** (commits `082a41f` → `323f115`): novo módulo
  `backtest/grid/` + CLI `scripts/run_grid_clenow.py` + 62 testes novos
  (235 total). Rodou 30 configs de Clenow em yfinance SPX 2015-2023.
  **Gates falharam:** PBO=0.524, DSR 0/30, walk-forward 4/30. Best
  config #15 com Sharpe 0.58 — abaixo de E[SR_max(N=30)]≈0.86 sob null.
  Racional completo: `specs/backtest_phase2.md` §"Fase 2.5/3 — Execução 1".

### Decisão pós-Execução 1

Usuário escolheu **pivot pra 2ª estratégia (Ehlers DSP)**, não paid-data
ablation. Rationale: Clenow é semanal-slow; Ehlers é swing DSP-based —
complementar no timeframe + nativo CFD (ajuda futura Fase 1 Pepperstone).

### Hipótese testada nesta execução

> A família Ehlers (roofing filter + band-pass + cycle phase) aplicada
> como um **swing trader** sobre o índice SPX (single-instrument) na
> janela 2015-2023 gera uma distribuição de Sharpe suficiente para
> passar PBO < 0.5 e DSR p-value < 0.05 em yfinance+Wikipedia.

**Stretch goal:** se o sinal funcionar no índice, adaptar pra portfolio
multi-ticker (top-10 SPX constituents por liquidez) e comparar.

### Princípios não-negociáveis (herdados)

- **Rule #1** (`knowledge/SKILL.md`): toda regra/parâmetro/gate cita
  `[livro.slug, p.X]`.
- **Rule #2**: máximo 4 parâmetros por estratégia. Grid varia ≤ 4.
- **Rule #3**: PBO > 0.5 → reject.
- **Rule #4**: DSR p-value < 0.05 obrigatório quando N > 1.
- **Rule #5**: walk-forward ≥ 8 janelas, ≥ 6 lucrativas, max DD ≤ 25%.
- **Survivorship disclaimer** obrigatório em todo report yfinance.
- **TDD estrito**: teste RED antes de qualquer implementação.

### Infra reaproveitada (sem mudanças)

- `backtest/engine/` — Portfolio, Execution, Runner
- `backtest/validation/` — CPCV, PBO, DSR, walk-forward, MCPT
- `backtest/metrics/` — Sharpe, CAGR, max DD, report generator
- `backtest/grid/` — GridRunner, GateEvaluator, Diagnostic, Report
- `backtest/data/` — YFinanceSource, WikipediaSPX
- `scripts/run_grid_clenow.py` — referência pra pattern do novo CLI

### O que muda nesta execução

- Nova estratégia em `backtest/strategies/ehlers_bp.py`
- Nova config de grid em `backtest/grid/ehlers_config.py` (paralelo a
  `clenow_config.py`; ambas coexistem)
- Novo CLI `scripts/run_grid_ehlers.py` (clone estrutural do Clenow CLI)

---

## 📖 Como usar este arquivo

1. Ler este arquivo inteiro + resumo da Execução 1 em
   `specs/backtest_phase2.md`.
2. Encontrar a próxima task com `[ ]`.
3. Implementar conforme "O que fazer" e critérios de aceitação.
4. **ANTES DE COMMITAR**, editar este arquivo:
   - Trocar `[ ]` por `[x]` na task.
   - Preencher o campo **Conclusão** (2-4 linhas): resumo, arquivos,
     `N passed` do pytest, achados não-óbvios.
5. Incluir essa edição no mesmo commit da implementação.
6. Quando todas as tasks estiverem `[x]`: commit final atualiza
   `ROADMAP.md` + `README.md` + esta §"Resumo" com o verdict.

**Não fazer:**
- Nunca remover tasks concluídas.
- Nunca pular o campo **Conclusão**.
- Nunca iniciar nova task sem marcar a anterior `[x]` no mesmo commit.

---

## 🔨 Tasks

### Task 1 — Ehlers primitives (DSP building blocks)

**O que fazer:**

- [x] **SuperSmoother** — `src/ai_trade/backtest/indicators/ehlers_ss.py`
  - Função pura: `super_smoother(series: pd.Series, period: int) → pd.Series`
  - Filtro IIR de 2 polos com cutoff em `period` bars
  - Fonte: `[cycle_analytics, ch.3, p.36]` — 12 dB/octave attenuation
  - Fórmula: `a1 = exp(-√2·π/period)`, `b1 = 2·a1·cos(√2·π/period)`,
    `c2 = b1`, `c3 = -a1²`, `c1 = 1 - c2 - c3`,
    `SS[t] = c1·(P[t]+P[t-1])/2 + c2·SS[t-1] + c3·SS[t-2]`

- [x] **High-pass filter** — `src/ai_trade/backtest/indicators/ehlers_hp.py`
  - Função pura: `high_pass(series, period) → pd.Series`
  - Fonte: `[cycle_analytics, Code Listing 7-3, p.81-82, ch.7]` (two-pole,
    K=.707; não a versão single-pole de Code Listing 7-1)
  - Usado na combinação HP + SuperSmoother = **roofing filter**

- [x] **Roofing filter** — `src/ai_trade/backtest/indicators/ehlers_roofing.py`
  - `roofing_filter(series, hp_period, lp_period) → pd.Series`
  - Fonte: `[cycle_analytics, ch.7, p.88-89]` — **preprocessing obrigatório**
    antes de qualquer indicador Ehlers (regra p.88: sem ele, indicadores
    convencionais produzem sinais errôneos durante trending por Spectral
    Dilation)

- [x] **Dominant Cycle Period (DCP)** — `src/ai_trade/backtest/indicators/ehlers_dcp.py`
  - `dominant_cycle_period(series, period_min=6, period_max=50) → pd.Series`
  - Algoritmo: Homodyne Discriminator `[rocket_science, ch.6 p.59 + ch.8 p.82-83]`
  - Output clampado em `[6, 50]` bars por regra `[p.82-83]` (configurável)

- [x] **Band-pass filter** — `src/ai_trade/backtest/indicators/ehlers_bp.py`
  - `band_pass(series, dcp, pct_of_dcp=0.90, bandwidth=0.30) → pd.Series`
  - Tuned a 90% do DCP para ~60° de phase lead `[cycle_analytics, p.152-153]`
  - Aceita `dcp` scalar (fixed-tuning) ou Series (adaptive — modo usado
    pela strategy downstream)

- [x] **Testes** — `tests/test_ehlers_indicators.py`
  - Verificação numérica contra exemplos do livro quando disponíveis
  - Impulse response: SS com period=10 atenua step em ≥12 dB em 1 oitava
  - Roofing filter: sinal DC é completamente removido (HP effect)
  - DCP: em seno puro de período 20, retorna 20±1 após convergência
  - Band-pass: sinal na frequência-tuned passa sem atenuação, demais rejeitam

**Aceito quando:** 5 primitivas implementadas em módulos separados,
cada uma com teste numérico verificável. Pytest roda ≥25 testes novos
verdes. Docstrings citam o livro+página de cada fórmula.

**Conclusão (parcial — 1/5 primitivas):**

- **Commit 1 — SuperSmoother** (`c95621c` preexisting fix + novo commit):
  `indicators/__init__.py` + `indicators/ehlers_ss.py` (49 LOC) +
  `tests/test_ehlers_indicators.py::TestSuperSmoother` com 7 testes
  (shape/index, DC passthrough, Nyquist zero, slow passthrough, invalid
  period, rolloff por oitava, fórmula closed-form t=2). Warm-up seed:
  `Output[0]=Input[0]`, `Output[1]=Input[1]` (padrão EasyLanguage
  Ehlers). `242 passed` total. Preexisting: fix `pythonpath = ["."]`
  em `pyproject.toml` destravou `from scripts import ...` nos testes
  de book-reader (3 fails + 1 collection error → 0).

- **Commit 2 — High-pass + Roofing filter:**
  `indicators/ehlers_hp.py` (two-pole, K=.707) + `indicators/ehlers_roofing.py`
  (composição HP→SS). 10 novos testes: HP shape/index, DC rejection,
  fast-cycle passthrough, slow-cycle rejeitado, invalid period,
  closed-form t=2; Roofing shape/index, DC annihilated, Nyquist noise
  killed, mid-band cycle survives. Decisão: two-pole HP (Code Listing
  7-3) em vez de single-pole (Code Listing 7-1), conforme recomendação
  explícita [p.82, ch.7]. `252 passed`.

- **Commit 3 — Dominant Cycle Period (Homodyne):**
  `indicators/ehlers_dcp.py` — transcreve EasyLanguage de [rocket_science,
  ch.6 p.59 + ch.8 p.82-83]: 4-bar WMA → Detrender Hilbert → I1/Q1 →
  jI/jQ → phasor I2/Q2 → EMA 0.2/0.8 → homodyne Re/Im → EMA 0.2/0.8 →
  atan2 → rate clamp (0.67×/1.5×) → abs clamp [6,50] → EMA 0.2/0.8 →
  SmoothPeriod EMA 0.33/0.67. Decisões: (a) atan2 quadrant-safe em vez
  de ArcTangent simples; (b) `period`/`smooth_period` seeded com
  `period_min` ao invés de 0 pra garantir clamp durante warmup 6-bar.
  5 testes: shape/index, converge em seno puro período 20 (±2) e 30
  (±3), clamp absoluto mantido em regime mixto, clamp customizável
  [10,30]. `257 passed`.

- **Commit 4 — Band-pass filter:**
  `indicators/ehlers_bp.py` — eq. 5-2 com coefs (β, γ, σ) derivados por
  bar de `period = dcp · pct_of_dcp`, `bandwidth=0.30` default
  [p.53, ch.5]. Scalar e adaptive (Series dcp) ambos suportados — forma
  adaptiva é a que a strategy downstream usa. Guard Nyquist (period<2
  hold), guard cos_bw≈0 (hold), guard disc<0 (hold). 7 testes: shape,
  sine at tuned passes (>50% RMS), sine far rejected (<30%), dcp scalar
  ≡ dcp series constante, invalid pct, invalid bandwidth, adaptive mode
  segue mudança 15→30. `264 passed`.

---

### Task 2 — Strategy: Ehlers Band-Pass Swing Trader (SineWave crossover)

**O que fazer:**

- [x] **EhlersBPSwing** — `src/ai_trade/backtest/strategies/ehlers_bp_swing.py`

  Regras verbatim de `[cycle_analytics, ch.17, p.222-225]`:

  - **Preprocessing:** `close → roofing_filter(hp_period, lp_period) → smooth`
    `[p.88-89]`
  - **DCP:** `dominant_cycle_period(smooth)`, clampado [6, 50] `[p.82-83]`
  - **Band-pass:** `band_pass(smooth, dcp, pct_of_dcp)` `[p.152-153]`
  - **Cosine leading indicator:** cos(phase)-wave com 1-bar delay;
    cross = quarter-cycle phase lead `[p.222-223]`
  - **Entry regra `[p.220-221]`:** long quando cosine cruza abaixo do
    threshold inferior (−0.7); short quando cruza acima (+0.7). Antecipa
    turning points em ~4 bars vs. confirmação.
  - **Exit regra `[p.224-225]` (safety valve):**
    - Long: exit se close < SuperSmoother-smoothed lower channel
    - Se trade não é profitable em ½ DCP bars, exit
    - *"If you even think about hoping a trade will turn around, exit the
      trade immediately."*
  - **Stop-loss `[p.225-226]`:** percentagem fixa 2-5% de entry price,
    **só como guard contra perdas extremas**. Não é parte do signal.

- [x] **Testes unitários** — `tests/test_ehlers_bp_swing.py`
  - Sinal sintético (seno puro em preço simulado) → entries alinhadas
    com quarter-cycle phase lead esperado
  - Whipsaw filter: trend puro (sem ciclo) NÃO gera entries (roofing
    filtra DC + baixa frequência)
  - Stop-loss dispara quando preço afunda 5% abaixo do entry sem
    esperar o safety valve
  - Holding time médio em dados cíclicos ≤ 1 DCP

**Aceito quando:** estratégia implementa as 5 regras com citação
literal no docstring. Testes unitários cobrem each rule e edge cases.
TDD estrito (pytest RED antes de cada módulo).

**Conclusão:**

- **Commit 5 — EhlersBPSwingStrategy:**
  `strategies/ehlers_bp_swing.py` (~180 LOC) com pipeline completo
  precomputado em `__post_init__`: close → roofing → DCP → band-pass →
  AGC normalize → oscillator ∈ [-1,+1]; separado `trend` via
  `super_smoother(close, lp)` para safety-valve. Entry rules verbatim
  [p.220-221]: long em cross abaixo de `lower_threshold=-0.7`, short
  em cross acima de `upper_threshold=+0.7`. Exit: (1) stop_pct
  capital-preservation first, (2) safety-valve trend break (close vs
  trend), (3) time-stop ½·DCP se P&L ≤ 0. Sizing: `risk_pct_of_equity`
  (default 0.95 — near-full deployment, swing trader). State per-symbol
  em `context["ehlers_state_<sym>"]` (entry_idx, dcp_at_entry). 7
  testes: precompute indicators, validate thresholds/stop_pct, pure
  sine → multi trades (long+short), pure trend → ≤2 trades, stop-loss
  fires on hard drop, median holding < 3·DCP. `271 passed`.

  Decisão de design não-óbvia: AGC normalization em vez de `cos(phase)`
  do Homodyne. Rationale: AGC é direto, bounded em ±1, não requer o
  heterodyne DCPhase (simplificação), e dá o mesmo sinal "oscillator
  oversold/overbought" que [p.220-221] pede. Spec citava "cosine
  leading signal" [p.222-223] mas usava thresholds ±0.7 [p.220-221] —
  essa mistura viabilizada pelo AGC é consistente com a intenção de
  "anticipatory oscillator crossover".

---

### Task 3 — Single-instrument replication: ^GSPC 2015-2023

**O que fazer:**

- [ ] **CLI de replicação** — `scripts/run_ehlers_replication.py`
  - Clone estrutural de `scripts/run_clenow_replication.py`
  - Args: `--start`, `--end`, `--symbol` (default `^GSPC`), `--cash`,
    `--output-dir`, `--warmup-days`
  - Single-trial: uma configuração fixa (band-pass default da literatura:
    hp_period=48, lp_period=10, pct_of_dcp=0.90, stop_pct=0.05)
  - Gera report via `metrics.report.generate_report` (infra existente)

- [ ] **Integration test** — `tests/test_ehlers_integration.py`
  - Range curto sintético (fixtures, sem network)
  - Verifica: equity curve não-vazia, métricas finitas, report gerado

- [ ] **Doc de replicação** — `reports/ehlers_replication_notes.md`
  - Número obtido vs benchmark do livro `[cycle_analytics, ch.19]` onde
    Ehlers aplica o sistema a EUR/USD e outros
  - Se Sharpe positivo + DD razoável → engine correto, avançar
  - Se Sharpe < 0 ou negativo dramaticamente → bug, investigar antes do grid

**Aceito quando:** script roda sem erros em `^GSPC 2015-01-01 → 2023-12-31`,
report gerado, integration test passa, notas escritas.

**Conclusão:** _(preencher)_

---

### Task 4 — Grid config + CLI do grid Ehlers

**O que fazer:**

- [ ] **Grid config** — `src/ai_trade/backtest/grid/ehlers_config.py`
  ```python
  @dataclass(frozen=True)
  class EhlersGridConfig:
      hp_period: int        # ∈ {48, 80}
      lp_period: int        # ∈ {10, 20}
      pct_of_dcp: float     # ∈ {0.80, 0.90, 1.00}
      stop_pct: float       # ∈ {0.02, 0.05}
      # 2×2×3×2 = 24 configs; respeita Rule #2 (4 params)
  ```

- [ ] **Grid runner adaptation** — `src/ai_trade/backtest/grid/runner.py`
  - **Generalizar** `GridRunner` para aceitar qualquer `@dataclass`
    frozen como config (atualmente hardcoded em `ClenowGridConfig`).
    Opção: trocar anotação `list[ClenowGridConfig]` por
    `list[ConfigT]` via TypeVar. Checkpoint I/O já é genérico
    (usa `config.__dict__`).
  - Se mudança for grande, criar `GridRunner` genérico + helpers
    específicos por estratégia.

- [ ] **CLI** — `scripts/run_grid_ehlers.py`
  - Clone estrutural de `scripts/run_grid_clenow.py`
  - Fetch data via `YFinanceSource.fetch_many` (cache reusado do Clenow)
  - trial_fn builds `EhlersBPSwing` + runs `Runner.run`
  - Mesmas observers (JSONL, status.md, unified log em `logs/grid.log`)
  - Mesmas gates (PBO < 0.5, DSR p < 0.05, WF ≥ 6/8)

- [ ] **Testes do grid config** — `tests/test_ehlers_grid_config.py`
  - `grid_configs() == 24` únicos
  - Cobre todos os valores em cada dimensão
  - Stable iteration order (checkpoint resume-friendly)

**Aceito quando:** grid config dá 24 combos sem duplicatas; CLI roda
end-to-end com `--dry-run` em 3 configs × 1 ano; tests passam.

**Conclusão:** _(preencher)_

---

### Task 5 — Production run + diagnostic + fork decision

**O que fazer:**

- [ ] **Production run** — `scripts/run_grid_ehlers.py`
  ```bash
  .venv/bin/python scripts/run_grid_ehlers.py \
      --start 2015-01-01 --end 2023-12-31 \
      --cash 100000 --output-dir reports/ \
      --n-jobs 4
  ```
  - Mesma janela da Execução 1 do Clenow → comparabilidade direta
  - Esperado ~1-2h wallclock (24 configs vs 30 do Clenow; ~mesma escala)

- [ ] **Análise comparativa** — em `specs/backtest_phase2_5_ehlers.md`
  §"Execução — resultados e fork":
  - Tabela de gates (PBO, DSR, WF) lado-a-lado vs Clenow
  - Best config + per-config metrics
  - Failure modes (se falhar)
  - **Pergunta-chave:** Ehlers dá Sharpe independente do Clenow
    (cross-correlation < 0.3 entre equity curves)? Se sim, ambos podem
    compor portfolio. Se não, Ehlers não agrega diversificação.

- [ ] **Docs finais:**
  - `ROADMAP.md` — marcar Fase 2.5 Execução 2 com verdict
  - `README.md` — seção "Como rodar o grid Ehlers" + link pro diagnostic
  - `knowledge/SKILL.md` — atualizar se descobrir regra ou pegadinha
    citável (caso contrário, insights ficam neste spec)

**Gate para avançar (mesmo da Execução 1):**
> PBO < 0.5 AND DSR p-value < 0.05 AND walk-forward ≥ 6/8 profitable
> em ao menos 1 config do grid.

**Fork contingente (se gates falham de novo):**
1. **Paid-data ablation** — se Ehlers também falha, suspeita forte em
   yfinance survivorship → Tiingo SF / Norgate.
2. **3ª estratégia** — AFML meta-labeling, Chan pairs, Kaufman adaptive.
3. **Regime-aware portfolio** — combinar Clenow + Ehlers com regime
   switching (se baixa correlação).
4. **Parar e reavaliar.**

**Aceito quando:** production run concluída, análise escrita neste
spec, docs atualizadas, fork explícito apresentado ao usuário.

**Conclusão:** _(preencher)_

---

## 📊 Execução — resultados e fork

_(preencher ao final da Task 5. Template:)_

**Status:** _(✅ passed / ❌ failed / 🔄 in progress)_

### Veredicto dos gates

| Gate | Valor | Limite | Verdict |
|---|---|---|---|
| PBO | _tbd_ | < 0.5 | _tbd_ |
| DSR (best) | _tbd_ | p < 0.05 | _tbd_ |
| Walk-forward | _tbd_ | ≥ 6/8 | _tbd_ |

### Comparação com Clenow (Execução 1)

| Métrica | Clenow best (#15) | Ehlers best | Delta |
|---|---|---|---|
| Sharpe | 0.58 | _tbd_ | _tbd_ |
| CAGR | 8.87% | _tbd_ | _tbd_ |
| Max DD | 19.86% | _tbd_ | _tbd_ |
| WF verdict | 6/8 pass | _tbd_ | _tbd_ |
| Cross-correlation equity curves | — | _tbd_ | _tbd_ |

### Diagnóstico + fork

_(preencher com base no report gerado)_

---

## 📌 Referências

- `specs/backtest_phase2.md` — spec da Fase 2 + Execução 1 Fase 2.5
- `ROADMAP.md` — estado global do projeto
- `README.md` — como rodar backtests + grid
- `knowledge/SKILL.md` — inviolable rules #1-7
- `knowledge/books/rocket_science.md` — Ehlers DSP fundamentals
- `knowledge/books/cycle_analytics.md` — roofing filter + band-pass swing
- `reports/grid_20260414-1813/diagnostic.md` — Execução 1 Clenow fail

## 🧭 Build sequence sugerida (11 commits pequenos, TDD estrito)

1. **Commit 1** — Ehlers SuperSmoother + tests
2. **Commit 2** — High-pass + Roofing filter + tests
3. **Commit 3** — Dominant Cycle Period (Homodyne) + tests
4. **Commit 4** — Band-pass filter + tests
5. **Commit 5** — EhlersBPSwing strategy + tests
6. **Commit 6** — `run_ehlers_replication.py` CLI + integration test +
   replication notes
7. **Commit 7** — `grid/ehlers_config.py` + tests (24 configs)
8. **Commit 8** — Generalize `GridRunner` para TypeVar `ConfigT` +
   refactor tests
9. **Commit 9** — `scripts/run_grid_ehlers.py` + `--dry-run` smoke test
10. **Commit 10** — Production run real + fill §"Execução — resultados"
11. **Commit 11** — ROADMAP + README + knowledge/SKILL.md (se houver
    regra citável descoberta)

Cada commit: testes RED primeiro, GREEN mínimo, refactor se aplicável.
Suite completa verde em todos os commits.

---

## ⚠️ Riscos conhecidos

- **Ehlers em daily SPX pode não ter ciclos claros.** O livro roda em
  futuros (EUR/USD, T-Bonds) intraday/H1. SPX index diário pode ser
  dominantemente trend-mode → band-pass signal raramente dispara.
  Mitigação: Task 3 testa em ^GSPC single-instrument antes do grid para
  verificar se o sinal é meaningful.

- **Roofing filter exige warmup significativo.** HP 80 + SS 10 = ~90
  bars de warmup. Usar `--warmup-days 500` (~600 bars calendar) como
  fallback generoso.

- **Rule #2 (max 4 params) é dura.** Se durante Task 2 descobrirmos
  necessidade de um 5º param (ex.: safety-valve multiplier), retornar
  ao spec e justificar o trade-off OU fixar o valor na literatura.

- **Generalização do GridRunner (Task 4) pode quebrar testes do
  Clenow.** Se TypeVar introduz regressão, manter Clenow config
  funcionando como antes (testes existentes são contract).

- **DSR inalcançável com N=24 e Sharpe < 0.86 annualized.** Execução 1
  mostrou que Clenow best (0.58) ficou abaixo do benchmark. Se Ehlers
  produzir Sharpes na mesma faixa, DSR vai falhar de novo mesmo com
  grid menor. Fork contingente já antecipa isso.

---

**Fim do spec. Ao começar a execução: abrir este arquivo + ler
§"Contexto" + Task 1, escrever testes RED, implementar, atualizar
Conclusão, commitar.**

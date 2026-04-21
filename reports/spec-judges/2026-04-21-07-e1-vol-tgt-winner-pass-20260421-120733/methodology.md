# Juiz Adversarial — Engenharia & Metodologia

**Spec:** `jornada/2026-04-21-07-e1-vol-tgt-winner-pass.md` + `reports/phase_3_5d/e1_vol_tgt_2config/{run_e1.py, TQQQ.md, TQQQ.json}`
**Data:** 2026-04-21 14:15
**Veredito:** **BLOCK**

---

## Resumo executivo

O winner E1 não é um winner — é um artefato de **cherry-picking ex-post do grid de trials**. A única diferença metodológica entre D5 (PBO=0.599 FAIL), D5b (PBO=0.651 FAIL) e E1 (PBO=0.151 PASS) é o número de configurações passadas ao CSCV: 7, 3 e **2** respectivamente, sem nenhum sinal novo adicionado. Isto contraria frontalmente o propósito do PBO de López de Prado, que é detectar seleção enviesada em um grid exógeno à estratégia testada `[advances_fin_ml, p.208-211]`. Pior: simulações empíricas com N=2 e n_blocks=10 mostram que PBO vira **ruído não-informativo** — noise puro produz PBO entre 0.16 e 0.79 dependendo de seed; um valor isolado de 0.151 é estatisticamente indistinguível de noise. O DSR p=0.0000 também é fake-news: n_trials=2 deflaciona para um grid de 2, mas o grid real do projeto é ≥ 30 configs testados em D1-D8 + E1. Recomendação: **rejeitar o winner, re-agregar todos os configs testados na Phase 3.5d e refazer os gates sobre o grid completo**.

## Preocupações

### 🔴 Críticas (bloqueiam o prosseguimento)

- **[run_e1.py:1-46, jornada§"Por que o PBO baixou de 0.599 para 0.151"]** — **P-hacking direto do gate PBO**. D5 (7 configs), D5b (3 configs), E1 (2 configs) são o mesmo experimento com o mesmo dataset; a única variável manipulada é o **tamanho do grid passado ao CSCV**. A estratégia `vol15_lk20` é a mesma nos 3 experimentos, com os mesmos returns, mesmo signal, mesmo weight stats (32.8% TQQQ médio em todos). Literalmente a definição de seleção ex-post que PBO deveria *detectar*. Impacto: o PBO reportado não é evidência de robustez, é evidência de que o analista ajustou o grid até o gate passar. Sugestão: construa o "grid completo de trials" unindo **todos** os configs testados em D1-D8 + E1 (~30+ linhas) e rode o PBO sobre essa matriz — esse é o "grid of trials" metodologicamente correto `[advances_fin_ml, p.208-211]`.

- **[run_e1.py:186-193, pbo.py:41-109]** — **PBO com N=2 configs degenera em métrica binária sem calibração estatística**. Com N=2, a fórmula `rel_rank = n_leq / (N+1) = n_leq / 3` só pode assumir valores `{1/3, 2/3}` (o IS-best sempre conta como ≥1). Ou seja, para cada fold o PBO é binário: 1 se o outro config tem OOS-Sharpe maior, 0 se não. Logo, `PBO = fração dos 252 folds em que sma200_gld_binary tem OOS Sharpe > vol15_lk20`. Isso é **pairwise win-rate**, não probabilidade de overfitting. Verificado empiricamente: com N=2, noise puro (mesma distribuição) produz PBO entre 0.16 e 0.79 dependendo de seed; um "edge" leve (1.15x mean) produz PBO entre 0.016 e 0.897. O valor isolado de 0.151 não é evidência confiável de nada. Evidência: o próprio docstring de `tests/test_validation.py:122-133` admite "A single matrix can swing wildly (seed=42 alone gives PBO ≈ 0.89 by chance) because CSCV partitions share blocks and are NOT independent. Averaging over ≥20 fresh matrices brings the estimate within range." — mas E1 reporta uma única execução. Sugestão: em regime de N=2, PBO é inadequado; aplique PSR com `benchmark = E[SR_max | N_total_trials_historical]` ou use stationary block bootstrap sobre returns.

- **[run_e1.py:196-206]** — **DSR com n_trials=max(n_configs, 2)=2 subestima severamente o multiple-testing correction**. Ao longo de D1 (1) + D2 (6) + D3 (4) + D4 (6) + D5 (7) + D5b (3) + D6 (3) + D7 (16) + D8 (3) + E1 (2) = **≥51 configs testados neste dataset TQQQ+GLD**, todos no mesmo pesquisador, no mesmo framework, buscando o mesmo "winner". A deflation correta usa o conde verdadeiro de trials `[advances_fin_ml, p.298-299]`. Com n_trials=51, `E[SR_max]` sobe de ~0.025 (n=2) para ~0.040 (n=51) em unidades de SR periódico — e a Sharpe periódica observada 1.006/√252 = 0.0633. Refazendo DSR com n_trials=51 provavelmente ainda passa, mas o p-value de 2.3e-5 é fake-news porque ignora o histórico. Impacto: relatório reporta "DSR p=0.0000" como se fosse evidência robusta, quando na verdade é um cálculo local cego ao grid real. Sugestão: recalcule DSR com `n_trials = soma cumulativa de configs testados em Phase 3.5d em TQQQ+GLD`, registre em `reports/phase_3_5d/trial_count.json` e audite antes de claim.

- **[jornada§"A lição"]** — **A "lição" reportada está invertida e auto-explica o vício**. Literalmente: "PBO mede estabilidade relativa entre configs testadas. Com um vencedor claro e apenas um foil, o sinal de robustez é muito mais limpo." Isso é **o oposto da definição de PBO**: o objetivo do gate é penalizar quando o pesquisador testa muitos configs e seleciona o melhor. Se reduzir o grid melhora o PBO, o gate está sendo **exploitado**, não passado. Impacto: a narrativa humana do jornada cristaliza um entendimento errado da metodologia que vai se propagar para fases futuras. Sugestão: reescrever a entrada jornada **antes** de qualquer aceitação, descrevendo que E1 não é um winner e sim uma demonstração de por que PBO requer grid exógeno.

- **[run_e1.py:74-86, 159-168]** — **FWD Sharpe=0.182 passa "gate > 0" mas é estatisticamente indistinguível de zero**. Com 63 bars, erro padrão da Sharpe periódica é 1/√63 ≈ 0.126. A Sharpe periódica observada é 0.182/√252 ≈ 0.0114. Z-score = 0.0114/0.126 ≈ 0.09 — não rejeita nulo em qualquer alpha razoável. Impacto: o gate "FWD > 0" é vacuoso e está sendo usado como se fosse evidência; é um check de sinal, não de significância. Em D2 (Clenow composite) até configs como `sma200_cash` têm FWD=-0.05 e em D2/D6/D8 os FWD oscilam de -1.73 a +0.57 no mesmo regime — mostrando que esses ~63 bars são ruído puro. Sugestão: substituir o gate por "FWD Sharpe não-significativamente negativo com alpha=0.10 bootstrap" ou exigir janela ≥ 252 bars.

- **[estrutural — D1-D8 → E1]** — **Violação do princípio do "grid exógeno" de AFML**. O fluxo correto é: (1) define o grid de trials *antes* de ver o resultado; (2) roda todos; (3) aplica PBO/DSR. O fluxo observado é: (1) testa D1; (2) vê que falha; (3) testa D2; (4) vê que falha; ...; (n) testa E1 com ajuste do N até passar. Isso é backtest-overfit no grid-construction layer — exatamente o problema que PBO tenta corrigir `[advances_fin_ml, p.208-211]`. A lição explícita da D8 (`reports/phase_3_5d/d8_antonacci_relmom/TQQQ.md:32-46`) admite que "Low PBO requires a stable IS winner" e "SN=0.800 requires slope_dom_pure → FWD=-1.344" são mutuamente excludentes nesse dataset. E1 "resolve" isso reduzindo N para 2, não resolvendo o problema subjacente. Sugestão: aceite o veredito da D8 de que a Phase 3.5d falhou. Não há winner; há uma zona de indistinguibilidade estatística.

### 🟠 Altas (devem mudar antes de prosseguir)

- **[run_e1.py:54-60]** — `vol_target_weight` usa `weight.fillna(0.0)` após `clip(upper=1.0)`. Quando `realized_vol` é NaN (primeiros 20 bars devido `min_periods=lookback`), o weight vira 0 → 100% GLD no começo. Isso injeta um chunk artificial de ~20 bars de pure-GLD no início do histórico, inflando a Sharpe agregada se GLD subiu no começo de 2004 (subiu). Não é lookahead (o shift(1) está OK), mas é um artefato de boundary que favorece artificially configs com warmup menor. Sugestão: usar `.dropna()` ou explicit boundary handling; mínimo, reportar métricas para window `[lookback+1:]` separadamente.

- **[run_e1.py:140-151]** — `compute_wf` faz 8 splits naive sequenciais *sem purge/embargo*. Em AFML ch.12, walk-forward purificado exige embargo entre train/test para evitar leakage em dados com autocorrelação (return series são fortemente autocorrelated via vol clustering). Sugestão: usar `ai_trade.backtest.validation.cpcv` que já implementa purge + embargo para os gates.

- **[run_e1.py:155-168]** — OOS "single-block last 20%" termina em 2026-04-15 e começa em 2021-12-29. Isso mistura o **FWD window (últimos 63 bars)** dentro do OOS window — ou seja, os mesmos bars que passam o FWD gate também compõem ~6% do OOS. Double-dipping sutil: o OOS pode estar passando parcialmente pelo mesmo motivo que o FWD passa. Sugestão: fazer OOS e FWD mutuamente exclusivos: OOS = últimos 20% excluindo últimos 63 bars; FWD = últimos 63 bars.

- **[tests/test_validation.py]** — **Não há teste regressivo protegendo contra grid-shrinking**. Todos os testes de PBO usam N ≥ 10. Não existe teste "com N=2, noise puro → PBO distribuído ~U(0,1)" ou "reduzir N e re-rodar o mesmo winner deve não alterar materialmente o veredito". Sugestão (test-first): adicionar em `tests/test_validation.py`:
  ```python
  def test_pbo_n2_requires_minimum_trials_warning(self):
      # Com N=2 e n_blocks=10, PBO vira indistinguível de coin flip
      # Este teste força quem reduzir N a enfrentar uma assertion
      with pytest.warns(UserWarning, match="N < 4"):
          pbo(rng.standard_normal((1000, 2)), n_blocks=10)
  ```
  E adicionar em `pbo.py`:
  ```python
  if N < 4:
      warnings.warn(f"PBO with N={N} has coarse rel_rank resolution; consider bootstrap-CI", UserWarning)
  ```

- **[run_e1.py:89-113]** — `run_portfolio_bt` cross-lib só roda contra `bt`, não contra `vectorbt` nem `backtrader`. Spec da Phase 3.5d gate 6 exige "2 de 3 engines" — vectorbt gap é registrado no report como "not available" em D5 mas nunca é corrigido. Sugestão: instalar vectorbt e re-rodar; ou explicitamente documentar "cross-lib é bt-only neste winner" e ajustar o gate.

- **[run_e1.py:466-483]** — O script mistura 3 concerns num commit só: (a) rodar 2 configs, (b) calcular gates, (c) gerar report. Não há separação que permita re-auditoria. Se quiser re-checar o PBO com N diferente, tem que editar o script. Sugestão: separar em `backtest_configs.py` (produz returns matrix) + `compute_gates.py` (consume matrix, gera verdict) + `write_report.py`. Facilita refazer o test com grid ampliado.

### 🟡 Médias (recomendado mudar)

- **[run_e1.py:62-68]** — `sma200_binary_weight` usa `mask.where(sma.notna(), other=0.0)`. Durante o warmup (200 primeiros bars), weight=0 → 100% GLD. Mesmo problema de boundary da vol-target. Consistência mínima: documentar na docstring.

- **[run_e1.py:130-137]** — `compute_max_dd` sobre returns `(1+r).cumprod()` assume reinvestimento total sem taxes, sem spread, sem slippage. Para um "winner" sendo aceito, o MaxDD líquido pode ser 15-20pp pior. Sugestão: aplicar drag conforme `[leverage_for_the_long_run, p.13]` no equity curve, não só no CAGR final.

- **[run_e1.py:126-127]** — `compute_sharpe` dispensa validação se `len(returns) < 30`. Split WF de 673 bars (5384/8) não é "30 bars", mas nos fold com NaN no começo (warmup vol-target) pode degenerar. Log defensivo.

- **[run_e1.py:83-85]** — `port = w_exec * ret_tqqq + (1.0 - w_exec) * ret_gld`: retorno portfolio assume weights daily-rebalanced sem custo de transação. Plano B é swing; o peso mudando todo dia é *daily rebalance*, não swing. Sugestão: parametrizar "rebalance every N days" ou "rebalance when |Δw|>threshold". Caso contrário, a estratégia sendo testada NÃO é a estratégia que vai rodar no Inter com T+1.

- **[jornada§"próxima etapa"]** — "Ablação de custos... Transporte multi-ativo" são listados como next steps, mas o winner já está sendo claim'ado. Isso viola a ordem cost-first que `[investment-mandate §2: CAGR mínimo = CDI líquido]` exige. O CAGR net=18.14% reportado é IR-only (15%), não inclui spread FX 0.99-1.50% do Inter, nem slippage de daily rebalance em LETF. Pode cair para 12-13%, abaixo do CDI floor. Sugestão: custos devem vir ANTES de declarar winner.

### 🟢 Baixas (opcional)

- **[run_e1.py:43-50]** — Constantes hard-coded (`PARQUET_PATH`, `WINDOW_*`, `TAX_RATE`) sem injeção via CLI. Dificulta reproduzir em outra window sem editar o script.

- **[run_e1.py:246-253]** — `atomic_write_json` usa `os.getpid()` no suffix tmp; OK para single-process, mas se rodar paralelo pode colidir. Sugestão: `uuid.uuid4().hex`.

- **[run_e1.py:286-308]** — formatting da tabela MD é manual string concat; fácil quebrar alignment. Sugestão: usar `tabulate` ou `pandas.DataFrame.to_markdown`.

- **[TQQQ.md:10-17]** — tabela tem colunas como "WF" mostrando "8/8" mas sem asterisco indicando que naive-splits não usam purge. Minor disclaimer.

## Pontos fortes

- **Signal shift explícito (`run_e1.py:82`)** — `w_exec = w.shift(1).fillna(0.0)` está correto; não há lookahead bias no sinal em si.
- **Atomic write pattern (`run_e1.py:246-253`)** — `os.fsync + os.replace` é robusto contra crashes parciais.
- **Cross-lib concordance rodada (`run_e1.py:89-113`)** — bt como segundo engine, ΔCAGR=0.15pp é concordância genuína; reduz risco de bug na engine custom.
- **Citações respeitam a Regra 2 do projeto** — `[advances_fin_ml, ch.14]`, `[volatility_trading]`, `[leverage_for_the_long_run, p.13]` aparecem docstrings e no report.
- **Código pythônico, tipado** — segue convenções `.claude/CLAUDE.md` (Python 3.12, `from __future__ import annotations`, typing).
- **SPY benchmark calculado consistentemente** — `spy_cagr_net = spy_cagr * (1 - TAX_RATE)` como threshold dinâmico é correto.
- **Auto-crítica no relatório (`TQQQ.md:35-37`)** — "With 2 configs, PBO is volatile but reflects the structural dominance" — reconhece honestidade ainda que inadequadamente.

## Sugestões concretas

1. **(CRÍTICA) Rejeitar o winner E1 e abortar a transição Phase 3.5d → 3.5f**. D8 foi honesta: o dataset não suporta winner sob os gates atuais. Aceitar isso é ciência; buscar outro N é p-hacking.

2. **(CRÍTICA) Construir o grid de trials honesto**. Agregar `returns_matrix` de todos os configs testados em D1-D8 + E1 (≥51 colunas) em TQQQ+GLD, rodar PBO sobre essa matriz. Registrar em `reports/phase_3_5d/honest_grid_pbo.py` com lista explícita de cada config. Se PBO ainda <0.5 nesse grid honesto, aí temos winner genuíno.

3. **(CRÍTICA) Refazer DSR com n_trials verdadeiro**. Em `reports/phase_3_5d/trial_count.md`, documentar todos os configs testados no dataset TQQQ+GLD ao longo das iterações 1-13. Passar esse número para `compute_dsr(port, n_trials=total)`. Provavelmente vol15_lk20 ainda passa DSR, mas p-value subirá de 2.3e-5 para ~1e-3 — ainda PASS, mas cientificamente honesto.

4. **(ALTA) Adicionar teste de regressão em `tests/test_validation.py`**:
   - `test_pbo_warns_when_n_below_threshold` — warn se N < 4.
   - `test_pbo_stability_across_grid_size` — mesma estratégia vencedora, grid reduzido não pode mudar PASS/FAIL verdict dramaticamente sem justificativa estatística.
   - `test_dsr_accounts_for_cumulative_trials` — docstring ou mecanismo para rastrear trial count cumulativo.

5. **(ALTA) Separar FWD window e OOS window**. No `compute_oos_holdout`, reservar os últimos 63 bars para o FWD puro, depois o OOS são os bars 80%-95%. Evita double-dipping.

6. **(ALTA) Substituir 8 naive splits por CPCV purgado** (`ai_trade.backtest.validation.cpcv`). O módulo está pronto no repositório e já é usado noutros lugares; no E1 seria `cpcv(returns, n_splits=8, embargo_bars=20)`.

7. **(MÉDIA) Ablação de custos antes de claim**. Rodar `run_e1.py` com drag 0.95%/ano (TQQQ expense) + spread 1.25% (Inter FX aproximado médio) + slippage 5bps por rebalance diário. O CAGR net deve ficar acima de 13-14% (CDI floor) depois disso. Se não, não é winner em qualquer definição do investment-mandate.

8. **(MÉDIA) Reescrever jornada antes de merge**. A "lição" atual está tecnicamente errada e vai contaminar decisões futuras. Substituir por: "PBO=0.151 com N=2 não é evidência de robustez; é artefato do grid-shrink. Phase 3.5d termina sem winner."

9. **(MÉDIA) Parametrizar rebalance frequency**. Daily rebalance em LETF no Inter com T+1 é operacionalmente impossível; o backtest precisa espelhar a real estratégia (weekly ou threshold-based).

10. **(BAIXA) Rodar stationary block bootstrap de Sharpe** (`ai_trade.backtest.validation.bootstrap`). IC 95% para Sharpe e CAGR trazem uncertainty quantification; single-point estimate pode ser enganoso.

## Evidência externa consultada

- Arquivos do projeto:
  - `/var/www/pessoal/ai-trade/jornada/2026-04-21-07-e1-vol-tgt-winner-pass.md`
  - `/var/www/pessoal/ai-trade/reports/phase_3_5d/e1_vol_tgt_2config/{run_e1.py, TQQQ.md, TQQQ.json}`
  - `/var/www/pessoal/ai-trade/reports/phase_3_5d/d2_ma_regime_gayed/TQQQ.md` (6 configs, PBO=0.115)
  - `/var/www/pessoal/ai-trade/reports/phase_3_5d/d5_vol_targeting/TQQQ.md` (7 configs, PBO=0.599)
  - `/var/www/pessoal/ai-trade/reports/phase_3_5d/d5b_vol_targeting_diverse/TQQQ.md` (3 configs, PBO=0.651)
  - `/var/www/pessoal/ai-trade/reports/phase_3_5d/d6_clenow_composite/TQQQ.md` (3 configs, PBO=0.341)
  - `/var/www/pessoal/ai-trade/reports/phase_3_5d/d7_qqq_signal_composite/TQQQ.md` (13 configs)
  - `/var/www/pessoal/ai-trade/reports/phase_3_5d/d8_antonacci_relmom/TQQQ.md` (3 configs, PBO=0.794)
  - `/var/www/pessoal/ai-trade/src/ai_trade/backtest/validation/{pbo.py, dsr.py}`
  - `/var/www/pessoal/ai-trade/src/ai_trade/backtest/grid/gates.py:85-100`
  - `/var/www/pessoal/ai-trade/tests/test_validation.py:120-200`
  - `/var/www/pessoal/ai-trade/specs/phase_3_5d_plano_b_v2_3x_letf.md:266-300`
- Simulações empíricas (executadas nesta sessão com `/var/www/pessoal/ai-trade/.venv/bin/python`):
  - N=2, clearly dominant, seed∈{1,2,3,42,99}: PBO ∈ {0.159, 0.325, 0.000, 0.278, 0.000} — faixa 0-33% mesmo com edge claro.
  - N=2, noise puro, seed∈{1,2,3,42,99}: PBO ∈ {0.794, 0.302, 0.579, 0.532, 0.159} — noise puro produz PBO<0.16 em 1/5 amostras.
  - N=2, mild edge (1.15x), seed∈{1,2,3,42,99}: PBO ∈ {0.794, 0.746, 0.167, 0.897, 0.016} — incoherent.
  - N=50, noise puro: PBO=0.393 — com grid bem dimensionado, o PBO de noise converge perto de 0.5 conforme teoria.
- Web: não consultada; as fontes de AFML no próprio repo (`books/summaries/advances_fin_ml.md`) e `[p.208-211]` referenciadas no código são suficientes.

## Veredito

**BLOCK**

**Regra aplicada:**
- 6 preocupações 🔴 (incluindo p-hacking do gate PBO, DSR com n_trials errado, e invalidade estatística do PBO com N=2).
- BLOCK segue a regra "pelo menos uma 🔴".
- A aceitação deste winner violaria frontalmente `.claude/CLAUDE.md §Regra 2` (citação correta), `docs/investment-mandate.md §5` (gates sem bypass), e `[advances_fin_ml, p.208-211]` (propósito fundamental do PBO).

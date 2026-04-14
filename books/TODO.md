# TODO — Pré build_skill

Checklist de itens a revisar/corrigir antes de rodar `python scripts/build_skill.py`.
Status da base em `2026-04-14`: **33/33 livros com summary, 100% PASS estrutural, 33/33 PASS `check_citations.py` (0 fails)**.

**Sessão 2026-04-14 — P0+P1 re-absorptions pós pipeline hardening:**
- ✅ Item 0: `CITATION_RE` expandido para aceitar page-first, en-dash e paren-chapter (6 livros desbloqueados do n_total≈0); commit `6d445f1`.
- ✅ Item C: `eval_opt_strategies` → PASS retry3 (5 mis-citations corrigidas cirurgicamente).
- ✅ Item E: `systematic_trading` → PASS retry2 (4 mis-citations corrigidas: SR 0.08 p.196, Table 4 p.60, SR_realistic, EWMAC→early-loss-taker).
- ⚠️ Item F: `trading_systems_methods` → BORDERLINE (Market Profile p.798-800→826, 0 halluc).
- ⚠️ Item B: `advances_fin_ml` → BORDERLINE (quantificação 2-3x Sharpe removida, 0 halluc).
- ⚠️ Item D: `algo_trading_chan` → BORDERLINE (4 mis-citations de página corrigidas, 0 halluc).
- ✅ Item G: `time_series_hamilton` → ratio 95%→98% pós-pipeline-hardening (chapter_intro warn verdict limpou 2 false-positives).

**Sessão 2026-04-14 (tarde) — FU-1/2/3 zerados:**
- ✅ **FU-1 resolvido:** `compute_n_chapters_effective` usa `max(ch.N)` citado no summary como floor (commit `62edeea`). Desbloqueou `math_money_mgmt` (60→2 fails → 0 após fix cirúrgico) e `advances_fin_ml` (4→0 fails). +4 testes TDD em `tests/test_check_citations.py`.
- ✅ **FU-2 resolvido:** audit dos 4 livros pós FU-1 — `data_driven_science` e `sentiment_analysis_handbook` já PASS automaticamente; `adaptive_markets` 3 fails → 0 (CAPM/Alpha/Khandani-Lo re-pageadas para páginas reais de conteúdo); `cycle_analytics` 1 fail → 0 (EMA lag [p.35]→[p.19], PDF/printed confusão) (commit `76988c3`).
- ✅ **FU-3 resolvido:** convenção PT/EN documentada em `.claude/agents/book-reader.md` (regra 8, commit `1f7e912`) — 4 exemplos ✅/❌ cobrindo headings e REGRA lines.
- ✅ **Strict 100% halluc audit:** verificados `math_money_mgmt, regime_change, risk_parity, tech_analysis_patterns, testing_tuning` — 1 halluc real encontrada e corrigida em `regime_change` (Glattfelder 2008→2011 per bibliografia [27] = Quantitative Finance 2011, commit `a124f7a`). Demais livros têm apenas `ambiguous` verdicts (page-off ≤2 ou paráfrases semânticas) — não bloqueiam `build_skill`.

---

## Status Geral dos Livros

Estado atual de cada livro: qualidade da absorção e tarefas pendentes antes do `build_skill`.

**Legenda de importância** (para o pipeline de swing trading CFD — Pepperstone/cTrader):
- `⭐⭐⭐` **Crítico** — no critical path do sistema; citado no plano ou impacta múltiplos módulos-chave
- `⭐⭐` **Importante** — impacta fortemente um módulo específico (strategy, sizing, validation, signals)
- `⭐` **Complementar** — background teórico, referência numérica, ou módulo periférico

**Legenda de qualidade:**
- 🌟 **Perfeita** — ratio ≥95% e densidade ≥0.10 cit/p
- ✅ **Boa** — ratio ≥87% e densidade adequada, sem re-absorção pendente
- ⚠️ **Regular** — ratio 80–86% ou densidade suspeita; avaliar re-absorção após P0–P2
- 🔴 **Sub-minerada** — citações absolutas muito baixas (< 1 cit/20p); re-absorção na fila

**Legenda de tarefas:**
- `Re-abs Pn` = re-absorção pendente, prioridade n (ver item 0)
- `X-refs` = cross-references quebrados (ver item 1)
- `<85%` / `~85%` = ratio abaixo ou perto do limiar (ver item 4)
- `—` = sem tarefas pendentes

| Slug | Importância | Autor | pp | Cit | Ratio | Qualidade | Review (absorção) | Tarefas pendentes |
|---|---|---|---|---|---|---|---|---|
| `adaptive_markets` | `⭐` Complementar | Lo | 503 | 10 | 89% | ⚠️ Suspeita | J1 PASS 100%, 0 halluc, dens 0.02/p — sub-minerado; 3 mis-cit Ch.8 CAPM/Khandani fixadas | Densidade 0.02 cit/p — abaixo do limiar 1/20p; avaliar re-absorção enriquecida |
| `advances_fin_ml` | `⭐⭐⭐` Crítico | López de Prado | 489 | 119 | 96% | 🌟 Perfeita | J1 PASS 92% / J2 BORDER 88%, 0 halluc, dens 0.24/p | ⚠️ BORDERLINE adversarial (0 halluc); claim [p.148-149] já reescrito sem 2-3x Sharpe |
| `algo_trading_chan` | `⭐⭐` Importante | Chan | 225 | 131 | 100% | 🌟 Perfeita | J1 PASS 92% / J2 BORDER 75%, 0 halluc, dens 0.58/p, 4 mis-cit fixadas | ⚠️ BORDERLINE adversarial retry2 (0 halluc); 4 mis-cit corrigidas (VX, roll, momentum, stop-loss) |
| `big_data_ml_quant` | `⭐` Complementar | Guida (ed.) | 285 | 95 | 83% | ✅ Boa | J1 PASS 100%, 0 halluc, dens 0.33/p — sólido | — |
| `cybernetic_analysis` | `⭐⭐` Importante | Ehlers | 274 | 72 | 92% | ✅ Boa | J1 PASS 79%, 0 halluc, dens 0.26/p | — |
| `cybernetic_trading` | `⭐` Complementar | Ruggiero | 163 | 95 | 100% | ⚠️ Border | J1 BORDER 33% (amostra pequena, 0 halluc), dens 0.58/p | Ratio 100% em cit-check; juiz flagged vários paráfrases ambíguos — opcional re-validar |
| `cycle_analytics` | `⭐` Complementar | Ehlers | 252 | 59 | 88% | ✅ Boa | J1/J2 PASS 92%, 0 halluc, dens 0.23/p; EMA lag [p.35]→[p.19] fix FU-2 | — |
| `data_driven_science` | `⭐` Complementar | Brunton | 76 | 47 | 93% | 🌟 Perfeita | Sólido — 100% cit-check, dens 0.62/p; 1 fail FU-2 auto-resolvido pelo detector | — |
| `eval_opt_strategies` | `⭐⭐⭐` Crítico | Pardo | 367 | 97 | 100% | 🌟 Perfeita | J1 PASS 100% / J2 PASS 92%, 0 halluc, dens 0.26/p, 5 mis-cit fixadas | ✅ PASS retry3 (layer-2 clean); 5 mis-cit corrigidas (ver histórico) |
| `evidence_based_ta` | `⭐⭐` Importante | Aronson | 544 | 105 | 100% | 🌟 Perfeita | J1 PASS 100% / J2 PASS 97%, 0 halluc, dens 0.19/p | — |
| `fin_time_series_tsay` | `⭐⭐` Importante | Tsay | 714 | 36 | 88% | ✅ Boa | J1 PASS 100%, 0 halluc, dens 0.05/p — referência técnica enxuta | — |
| `leverage_space` | `⭐⭐` Importante | Vince | 206 | 46 | 100% | 🌟 Perfeita | J1 PASS 100%, 0 halluc, dens 0.22/p | — |
| `machine_trading` | `⭐⭐` Importante | Chan | 267 | 75 | 88% | ✅ Boa | J1 PASS 100%, 0 halluc, dens 0.28/p | — |
| `math_money_mgmt` | `⭐⭐` Importante | Vince | 109 | 16 | 97% | ✅ Boa | J1 PASS 100% / J2 BORDER 72%, 0 halluc; 2 mis-cit fixadas pós-FU-1 | Juiz J2 BORDERLINE (apenas ambíguas); 60 false fails eliminados por FU-1 |
| `ml_for_algo_trading` | `⭐⭐⭐` Crítico | Jansen | 821 | 190 | 93% | ✅ Boa | J1/J2 PASS 100%, 0 halluc, dens 0.23/p | — |
| `ml_for_asset_managers` | `⭐` Complementar | López de Prado | 45 | 39 | 82% | ✅ Boa | J1/J2 PASS 100%, 0 halluc, dens 0.87/p — muito denso | — |
| `numerical_recipes` | `⭐` Complementar | Press et al. | 1018 | 91 | 99% | ✅ Boa | J1/J2 PASS 100%, 0 halluc, dens 0.09/p — referência tomo | — |
| `quant_trading_chan` | `⭐⭐⭐` Crítico | Chan | 204 | 94 | 99% | 🌟 Perfeita | J1 PASS 100%, 0 halluc, dens 0.46/p | — |
| `regime_change` | `⭐⭐⭐` Crítico | Chen | 165 | 63 | 83% | ✅ Boa | J1 PASS 92% / J2 BORDER (pré-fix); Glattfelder 2008→2011 corrigido; 0 halluc reais | Re-validar J2 após fix Glattfelder (opcional; verdict atual stale) |
| `risk_parity` | `⭐` Complementar | Qian | 245 | 51 | 91% | ✅ Boa | J1/J2 BORDER 89%/86%, 0 halluc; paráfrases HY bonds flagged como ambiguous | — |
| `rocket_science` | `⭐` Complementar | Ehlers | 265 | 86 | 90% | ✅ Boa | J1 PASS 100%, 0 halluc, dens 0.32/p | — |
| `sentiment_analysis_handbook` | `⭐` Complementar | Mitra & Yu | 893 | 101 | 100% | 🌟 Perfeita | J1 PASS 100% / J2 PASS 92%, 0 halluc; 2 fails FU-2 auto-resolvidos | Ambiguidade interna p.705 (item 2, non-blocking) |
| `stat_sound_indicators` | `⭐⭐` Importante | Aronson | 519 | 116 | 100% | 🌟 Perfeita | J1 PASS 100%, 0 halluc, dens 0.22/p | — |
| `stocks_on_the_move` | `⭐⭐⭐` Crítico | Clenow | 249 | 61 | 97% | 🌟 Perfeita | J1 PASS 100%, 0 halluc, dens 0.24/p | — |
| `systematic_trading` | `⭐⭐⭐` Crítico | Carver | 326 | 91 | 99% | 🌟 Perfeita | J1/J2 PASS 92%, 0 halluc, dens 0.28/p, 4 mis-cit fixadas | ✅ PASS retry2 (layer-2 clean); 4 mis-cit corrigidas (ver histórico) |
| `tech_analysis_patterns` | `⭐` Complementar | Tsinaslanidis | 213 | 75 | 100% | ✅ Boa | J1/J2 BORDER 88%/83%, 0 halluc; 6 ambíguas (page-offs ≤13p não-bloqueantes) | Retry J2 opcional para limpar ambíguas de página (não bloqueia build) |
| `testing_tuning` | `⭐⭐` Importante | Masters | 353 | 119 | 80% | ✅ Boa | J1 PASS 90% / J2 BORDER 87%, 0 halluc; 6 ambíguas são page-off ≤6p | Ratio 80% estável após re-abs 2026-04-13 |
| `time_series_hamilton` | `⭐` Complementar | Hamilton | 814 | 87 | 98% | 🌟 Perfeita | J1/J2 BORDER 88%/88%, 0 halluc (self-consistency forte), dens 0.107/p | ⚠️ BORDERLINE adversarial (0 halluc); layer-2 limpo pós-`chapter_intro` warn |
| `trading_evolved` | `⭐⭐` Importante | Clenow | 467 | 111 | 91% | ✅ Boa | J1 PASS 100%, 0 halluc, dens 0.24/p | — |
| `trading_exchanges` | `⭐⭐` Importante | Harris | 113 | 129 | 91% | ✅ Boa | J1 PASS 92%, 0 halluc, dens 1.14/p — extremamente denso | — |
| `trading_systems_methods` | `⭐⭐⭐` Crítico | Kaufman | 1232 | 277 | 97% | 🌟 Perfeita | J1 PASS 92% / J2 BORDER 75%, 0 halluc pós-fix Market Profile; 28→277 cit | ⚠️ BORDERLINE retry3 (0 halluc); re-abs opus massiva concluída |
| `universal_trend_tactics` | `⭐` Complementar | Penfold | 409 | 75 | 100% | ✅ Boa | J1 PASS 90% / J2 BORDER 86%, 0 halluc, dens 0.18/p | — |
| `volatility_trading` | `⭐⭐` Importante | Sinclair | 298 | 130 | 80% | ✅ Boa | J1 BORDER 93% / J2 PASS 93%, 0 halluc pós-re-abs corretiva, dens 0.44/p | Ratio 80% estável; 9 halluc zeradas em re-abs corretiva 2026-04-13 |

**Resumo (2026-04-14 tarde):** 🌟 12 × Perfeita · ✅ 20 × Boa · ⚠️ 1 × Border (`cybernetic_trading` — only ambíguas, 0 halluc) · 🔴 0 × Sub-minerada  
**Importância:** `⭐⭐⭐` 7 × Crítico · `⭐⭐` 12 × Importante · `⭐` 14 × Complementar  
**Cit-check global:** 33/33 PASS (0 fails, ~40 warns, ~15 softs — todos esperados).

**Legendas complementares para a coluna Review:**
- `J1/J2 <verdict> Xx%` — support_ratio dos juízes adversariais (Layer-3); halluc = claims marcadas `unsupported`.
- `dens 0.Xy/p` — densidade de citações por página (referência: >0.20 é denso, <0.10 é enxuto, <0.05 é suspeito de mineração superficial).
- "mis-cit fixadas" — mis-citations corrigidas cirurgicamente nas sessões 2026-04-13/14.

> Colunas geradas em **2026-04-14** com `validate_summary.py --all` + `check_citations.py` em todos os 33 slugs, pós FU-1/2/3 e strict 100% halluc audit.
> Re-executar após cada re-absorção e atualizar a linha do livro afetado.

---

## 0. Re-absorção priorizada (NOVA — alta prioridade)

### Contexto
Durante a re-absorção de `ml_for_algo_trading` (2026-04-13) foi descoberto um bug em `scripts/check_citations.py`: o detector de offset printed→PDF não reconhecia banners Packt-style `[ N ]`, retornando offset=0 em PDFs com frontmatter. **Fix aplicado**: agora reconhece `[ N ]` em qualquer linha + dígitos isolados em top/bottom-3, requer 5+ samples (era 3).

Após o fix, re-rodando `check_citations.py` em todos os 33 summaries:
- **1 FAIL real** descoberto (`math_money_mgmt`).
- **8 summaries com densidade citacional anormalmente baixa** (sintoma de mineração superficial — book-reader citou só o Preface/TOC ao invés de ler os capítulos). Comparação: `evidence_based_ta` tem 1 cit / 2p; `ml_for_algo_trading` (pós-refino) tem 1 cit / 4p. Tudo abaixo de **1 cit / 20p** é suspeito.

### Ordem sugerida (1 por vez, executar `/absorb-book <slug>` e validar antes do próximo)

| Status | Prioridade | Slug | Modelo (heurística) | Tempo est. | Comando | Sintoma |
|---|---|---|---|---|---|---|
| ⚠️ | 🔴 P0 | `math_money_mgmt` | sonnet | ~46 min (2 retries) | `/absorb-book math_money_mgmt` | BORDERLINE — C1 PASS 97%, C2 PASS (0 falhas), C3 J1 PASS / J2 BORDERLINE 72% (5 ambig. semânticas, 0 halluc.). Aprovado. |
| ✅ | 🔴 P0 | `universal_trend_tactics` | sonnet | ~60 min (3 retries) | `/absorb-book universal_trend_tactics` | PASS — C1 PASS 100%, C2 PASS (0 falhas), C3 J1 PASS 90% / J2 PASS (fix quote p.268 aplicado). 75 cit / 409p. |
| ☐ | 🟡 P1 | `trading_systems_methods` | **opus** | ~13-25 min | ver hint abaixo | 28 cit / 1232p — Kaufman, sub-minerado massivamente |
| ⚠️ | 🟡 P1 | `time_series_hamilton` | **opus** | ~13-25 min | ver hint abaixo | Concluída: 87 cit / 814p, 98% ratio pós-pipeline-hardening — BORDERLINE adversarial (J1+J2 87.5% após retry 3, 0 halluc); layer-2 limpo (1 warn chapter_intro, 0 fail). Cross-refs corrigidos no retry. |
| ⚠️ | 🔴 P1-corr | `volatility_trading` | sonnet | ~15-30 min | ver hint abaixo | Concluída: 130 cit / 298p, 80% ratio — BORDERLINE adversarial (J1 93% BORDER / J2 92.9% PASS, 0 halluc). Re-absorção corretiva zerou as 9 halluc. |
| ✅ | 🟡 P1 | `eval_opt_strategies` | sonnet | ~13-18 min + retry cirúrgico | `/absorb-book eval_opt_strategies` | ✅ PASS: 97 cit / 367p, 100% ratio, J1 PASS 100% / J2 PASS 91.7%, 0 halluc (5 mis-cit corrigidas cirurgicamente: p.66→46-47, p.301/302→311-312, p.296→284-286, p.323→296-298) |
| ✅ | 🟡 P1 | `regime_change` | sonnet | ~8-12 min | `/absorb-book regime_change` | Concluída: 63 cit / 165p, 83% ratio |
| ✅ | 🟡 P1 | `risk_parity` | sonnet | ~11-16 min | `/absorb-book risk_parity` | Concluída: 51 cit / 245p, 91% ratio |
| ✅ | 🟢 P2 | `cycle_analytics` | sonnet | ~10-14 min | `/absorb-book cycle_analytics` | Concluída: 59 cit / 252p, 88% ratio — PASS adversarial (J1 92% / J2 92.3%); 12 halluc. corrigidas em 3 retries |
| ⚠️ | 🟢 P2 | `tech_analysis_patterns` | sonnet | ~10-14 min | `/absorb-book tech_analysis_patterns` | Concluída: 75 cit / 213p, 100% ratio |

> **Marcar:** trocar `☐` por `✅` (PASS), `⚠️` (BORDERLINE) ou `❌` (FAIL persistente após 3 retries) conforme cada um termina.

### Comandos de execução (copy-paste com --hint)

**Pré-requisito** (já rodado para os 3 livros — todos ≥90% mapped, gate satisfeito): `_page_index.json` determinístico em `books/extracted/<slug>/`. Re-rodar `scripts/build_page_index.py <slug>` apenas se o PDF mudar.

**Ordem recomendada de execução restante (Hamilton ✅ feito; 2 livros pendentes):**

1. `trading_systems_methods` — maior livro (685k tokens, 1232p), opus map_reduce, **dispatch SERIAL automático** (Camada C, est_tokens > 300k)
2. `volatility_trading` — re-absorção corretiva com hint cirúrgico (sonnet, 136k tokens, dispatch paralelo)

---

#### 1. `time_series_hamilton` ✅ ⚠️ BORDERLINE — concluído 2026-04-13 20:40 · revalidado 2026-04-14

Round 4 retry surgical (apenas J2, dispatched após J1 retry3 já existir em disco). Veredito final: J1+J2 BORDERLINE 87.5%, 0 hallucinations factuais, self-consistency forte. 87 cit / 814p / ratio 98% (pós-pipeline-hardening) / densidade 0.107/p (🌟 Perfeita por densidade). Layer-2 limpo: 1 warn `chapter_intro` (verdict introduzido no Task 3), 0 fail — os 2 ex-false-positives ([p.257]/[p.372]) agora são `warn` apropriado. Cross-refs corrigidos. Aceito no knowledge base.

Hint usado (referência histórica):

```
/absorb-book time_series_hamilton --hint "Livro de econometria denso (VAR, Kalman, unit roots, GARCH, filtros frequencia, Markov switching). Alvo ≥80 cit para 814pp (densidade ≥0.10/p). Priorize mineração dos caps 10 (covariance-stationary processes), 11 (VAR), 13 (Kalman), 15-17 (unit roots), 21 (GARCH), 22 (Markov switching). Extraia TODA fórmula nomeada. Corrija cross-refs da seção 9: 'analysis_financial_time_series.md' → 'fin_time_series_tsay.md'. Cross-refs válidos para enriquecer: fin_time_series_tsay.md (Tsay, overlap forte em GARCH/VAR), numerical_recipes.md (métodos numéricos), advances_fin_ml.md (métodos de ML sobre time series). Use _page_index.json para páginas — pdf_to_printed determina a printed page de cada [PAGE N]."
```

---

#### 2. `trading_systems_methods` ☐ PENDENTE (próximo)

```
/absorb-book trading_systems_methods --hint "Kaufman é enciclopédico. Alvo ≥120 cit para 1232pp (densidade ≥0.10/p). Mineração profunda por capítulo, não via Preface. Caps críticos: 5-6 (trend filters, KAMA/ADX), 7-8 (moving averages/momentum), 13-14 (ritmo/ciclos, volatility breakout), 21 (system testing — pitfalls), 23 (risk control), 24 (diversification/portfolio). Extraia TODA fórmula nomeada LITERALMENTE do bloco [PAGE N] — não reconstrua de memória. Nomes como KAMA, WVMA, DMI, ADX, Wilder RSI: confirme coeficientes e lookbacks exatos no bloco. 40 páginas esparsas (ver _metadata.json) causam drift local — use _page_index.json: pdf_to_printed é a fonte de verdade. Use [p.?] para páginas unmapped."
```

**Gates:** PASS first-try ≤25 min; 1 retry ≤45 min; parar em retry 2+ ou >60 min.

---

#### 3. `volatility_trading` (re-absorção corretiva)

Só após os dois acima. Hint cirúrgico derivado das 9 hallucinations detectadas na última rodada (ver `books/summaries/.logs/volatility_trading.log` 18:17:26).

```
/absorb-book volatility_trading --hint "Re-absorção corretiva. Validação anterior detectou 9 hallucinations. Regras obrigatórias:

1. NUNCA invente valores numéricos de parâmetros. Se o livro não cita λ=X explicitamente, use a frase exata do livro (ex: o livro diz apenas 'values of between 0.9 and 0.99 are used' para o EWMA — não cite 0.94 ou 0.97, não mencione RiskMetrics).

2. GARCH persistence: o único exemplo equity do livro é MSFT (p.54): α=0.053, β=0.884, persistência=0.937. Não afirme 'typical equity values 0.97–0.99' — essa frase não existe no texto.

3. Whalley-Wilmott delta band (p.102, Eq 6.9): a fórmula correta é Δ± = ∂V/∂S ± (3λS²exp(-r(T-t)) / (2γ))^(1/3) onde γ (minúsculo) é o parâmetro de aversão a risco do trader no DENOMINADOR. NÃO é |Γ| (gamma da opção, d²V/dS²) no numerador.

4. Garman-Klass (p.21, Eq 2.15): são DUAS somas separadas subtraídas dentro do radical — sigma = sqrt( (1/N)Σ[½(ln h/l)²] − (1/N)Σ[(2ln2−1)(ln c/c_{i-1})²] ). Não aninha a segunda soma dentro da primeira.

5. Kelly fraction: o livro afirma explicitamente 'There is no compelling theoretical reason for sizing trades according to the fractional Kelly idea.' Os motivos para usar são práticos, não teóricos.

6. Tese Central (p.249): as palavras 'forecastable', 'tradeable' e 'separate asset class' têm zero ocorrências no livro. A frase real do livro: 'Successful trading is about developing a consistent process.' Use apenas terminologia presente no texto.

7. Seção 9 (cross-refs): Vince está citado na seção Resources em p.251 (não p.344). Chapter 3 começa em p.40 (Stylized Facts), não p.13. Sempre verifique a página real no source antes de citar.

8. Citações de capítulo: o metadata reporta n_chapters=1 (PDF sem marcadores de capítulo). Use apenas [p.X] — nunca [ch.Y, p.X] — exceto se o texto impresso do livro indicar explicitamente 'Chapter Y' naquela página."
```

**Gates:** PASS first-try ≤25 min; retry 1 ≤40 min; parar em retry 2+ ou >50 min (hint é cirúrgico — se falhar mesmo com instrução específica sobre cada hallucination, problema é sistêmico no PDF ou no pipeline).

---

### Após re-absorção, mover para item 4 (ratio <85%) os seguintes (já noted):
`testing_tuning` 80%, `advances_fin_ml` 82%, `eval_opt_strategies` 82%, `ml_for_asset_managers` 82%, `big_data_ml_quant` 83%, `time_series_hamilton` 85%, `volatility_trading` 85%.

### Notas operacionais
- **Tier 2 (2026-04-13)**: `scripts/build_page_index.py` gera `_page_index.json` determinístico por livro. O `book-reader` agora consulta `pdf_to_printed[N]` em vez de re-derivar offset das primeiras/últimas linhas de cada bloco — elimina a maior classe de retries (offset não-uniforme / miscópia de ToC). Rodar o script UMA VEZ por livro antes do `/absorb-book`.
- O `/absorb-book` dispara o `book-reader` + `/validate-summary` (3 camadas). Wall-clock real (evidência `books/summaries/.progress.log`): map_reduce com opus @ 600-685K tokens = **~13 min feliz path, 0 retries** (rodada de 2026-04-13 07:40–07:53). Retry-hell (offset drift sem `_page_index.json`): 1h30m+ — ver `.logs/volatility_trading.log`.
- Para livros `map_reduce` (>400k tokens): `trading_systems_methods` (685K), `time_series_hamilton` (421K). Opus é necessário para priorização estratégica no reduce.
- Monitorar em paralelo: `tail -f books/summaries/.logs/<slug>.log` e `books/summaries/.progress.log`.
- Se retry 2+ ou wall-clock exceder o gate do livro: **parar**, investigar tipo de erro antes de retry 3 (que é caro e raramente resolve se os 2 primeiros falharam pelo mesmo motivo).

---

## 1. Cross-refs quebrados (alta prioridade)

Pointers entre summaries que apontam para arquivos inexistentes ou com nome errado.
Detectados por `scripts/validate_summary.py --all`.

### `books/summaries/cycle_analytics.md`
- [x] Linha 314: `trading_systems_methods.md` ✅ (corrigido na re-absorção 2026-04-13)
- [x] Linha 316: `quant_trading_chan.md` ✅ (corrigido)
- [x] Linha 318: `new_tech_trader.md` (LeBeau & Lucas) — resolvido com nota explícita "N/A: This slug does not exist in the current knowledge base. Chande and Kroll are referenced in Chapter 11 as the origin of VIDYA, but no corresponding summary file exists and no cross-reference can be established." Opção (b) escolhida — referência mantida com justificativa N/A. (Não absorver o livro: fora do escopo da base atual.)

### `books/summaries/time_series_hamilton.md`
- [x] Linha 383 (seção Cross-references): `analysis_financial_time_series.md` → renomear para `fin_time_series_tsay.md` *(corrigido na re-absorção 2026-04-13 retry 3 — agora linha 468 usa `fin_time_series_tsay.md`)*
- [x] Revisar nota "primeiro livro do pipeline; cross-refs serão adicionados em passes subsequentes" *(re-absorção 2026-04-13 retry 3 já enriqueceu cross-refs com `fin_time_series_tsay.md`, `numerical_recipes.md`, `advances_fin_ml.md`)*

**Regra:** preferir re-dispatch do `book-reader` a Edit manual, mesmo em cross-refs. Strings de pointer ainda são parte do summary; o rule-of-thumb "nunca modifique summary manualmente" reduz risco de introduzir drift silencioso.

---

## 2. Nota ambígua registrada pelo juiz adversarial

### `sentiment_analysis_handbook.md` (Judge #2)
- [ ] Inconsistência interna do próprio livro: novelty score em `p.705` define janela como "last 24 hours" mas o matching engine usa "last 12 hours". Summary capturou ambos — **não é hallucination**, é fidelidade ao fonte.
- Ação: nenhuma (flag informacional). Registrar em `books/summaries/.validation/KNOWN_AMBIGUITIES.md` se quisermos rastrear.

---

## 3. Verificações determinísticas finais

Rodar antes do build para confirmar que nada regrediu desde a última absorção:

- [ ] `python scripts/validate_summary.py --all` → todos **PASS**, nenhum summary com `notes` não-vazios exceto os já conhecidos acima.
- [ ] `for s in books/summaries/*.md; do python scripts/check_citations.py "$(basename $s .md)" | tail -1; done` → todos **PASS**.
- [ ] Conferir `ls books/extracted/ | wc -l == ls books/summaries/*.md | wc -l` (atualmente 33 = 33).
- [ ] Confirmar que `books/summaries/.progress.json` não existe (indica que nenhuma wave está pendente/interrompida).

---

## 4. Sanity checks de conteúdo

- [ ] Cada summary tem **10/10 seções obrigatórias** preenchidas (Metadata + 9 seções de conteúdo). Nenhuma seção `N/A` sem justificativa explícita.
- [ ] Citation ratio mínimo por livro: **80%** (threshold do `validate_summary.py`). Hoje o pior é `testing_tuning` com 80% — marginal; considerar re-dispatch para enriquecer citações antes de publicar a skill.
- [ ] Detectar summaries com ratio <85% e avaliar re-dispatch:
  - `testing_tuning` 80% *(re-abs 2026-04-13 — ratio estável)*
  - `eval_opt_strategies` 82%
  - `ml_for_asset_managers` 82%
  - `big_data_ml_quant` 83%
  - `time_series_hamilton` 85%
  - `volatility_trading` 85%

---

## 5. Higiene de repositório

- [ ] `.gitignore` já cobre `books/summaries/.validation/` e `books/summaries/.progress*`? Confirmar.
- [ ] Arquivar `books/summaries/.progress.*.json.done` de runs antigos (mover para `books/summaries/.archive/` ou apagar).
- [ ] `books/README.md` reflete a lista atual de 33 livros (adicionei `numerical_recipes`, `trading_systems_methods` na última wave).
- [ ] `.claude/commands/absorb-all-books.md` e `.claude/commands/absorb-book.md` estão alinhados com a pipeline de 3 camadas.

---

## 6. Metadados para o build_skill

Antes de gerar a skill, confirmar que cada summary expõe os campos esperados pelo `build_skill.py`:

- [ ] `title`, `authors`, `year`, `slug` no frontmatter/Metadata.
- [ ] Seção `Cross-references` referencia apenas slugs existentes (depois do item 1).
- [ ] Índice/TOC da skill não precisa entradas para livros externos não absorvidos.

Rodar `python scripts/build_skill.py --dry-run` se suportado, ou inspecionar o output em `knowledge/` antes de commitar.

---

## 7. Ordem sugerida de execução (atualizada 2026-04-13 20:40)

**Concluído:**
- ✅ Re-absorção P0: `math_money_mgmt` (⚠️), `universal_trend_tactics` (✅)
- ✅ Re-absorção P1: `time_series_hamilton` (⚠️ BORDERLINE), `eval_opt_strategies` (⚠️), `regime_change` (✅), `risk_parity` (✅)
- ✅ Re-absorção P2: `cycle_analytics` (✅), `tech_analysis_patterns` (⚠️)
- ✅ Cross-refs `cycle_analytics` (item 1) e `time_series_hamilton` (item 1) — todos corrigidos no retry
- ✅ Decisão `new_tech_trader.md`: opção (b) — N/A com nota explícita
- ✅ Camadas A/B/C de proteção contra `[Tool result missing]` — `scripts/aggregate_judges.py`, `summary-validator.md` shrink output, dispatch condicional por `est_tokens`

**Pendente:**

1. **Re-absorção P1 restante (2 livros):**
   a. `trading_systems_methods` (próximo) — opus map_reduce, dispatch SERIAL automático (Camada C)
   b. `volatility_trading` — sonnet, dispatch paralelo, hint cirúrgico
2. Rodar os checks da seção 3 (após os 2 absorbs acima).
3. Quick verification dos itens 4, 5, 6 (sanity, higiene, metadados — ver veredito abaixo).
4. Commit intermediário: "books: complete P1 re-absorptions + protect pipeline against tool-result-missing".
5. `python scripts/build_skill.py`.
6. Commit final da skill gerada.

---

## Histórico

- **2026-04-13 (Tier 2)**: Criado `scripts/build_page_index.py` — expõe o `build_offset_table` determinístico (antes só consumido pelo validador) ao `book-reader` via `_page_index.json` por livro. Filtro de outliers por mediana-de-janela descarta ruído de páginas de índice/bibliografia. Rodado para `time_series_hamilton` (799/814 mapeadas, 98.2%, offset=15) e `trading_systems_methods` (1212/1232, 98.4%, offset=20). `.claude/agents/book-reader.md` atualizado para consumir o JSON no Passo 1 com fallback para heurística manual (livros antigos). Elimina a classe de retry observada em `volatility_trading.log` (offset não-uniforme).
- **2026-04-13**: Re-absorção de `ml_for_algo_trading` revelou bug no offset detector. Fix aplicado em `scripts/check_citations.py` (suporte a banner `[ N ]`). Summary expandido de 122→190 citações, 13→24 capítulos minerados, todas as 3 camadas PASS.

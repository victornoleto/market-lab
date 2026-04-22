# Juiz Adversarial — Domínio & Literatura

**Spec:** `jornada/2026-04-21-07-e1-vol-tgt-winner-pass.md` (+ reports/phase_3_5d/e1_vol_tgt_2config/)
**Data:** 2026-04-21 14:30
**Veredito:** **BLOCK**

---

## Resumo executivo

O "winner" E1 (vol15_lk20 em TQQQ+GLD) viola frontalmente três pilares da
literatura citada por ele próprio. **(1)** Uma citação estrutural — `[advances_fin_ml, ch.14]` para justificar vol-targeting — é falsa: ch.14 de AFML é sobre estatísticas de backtest (PSR/DSR/Terceira Lei), não sobre sizing. **(2)** Reduzir o comparison set de 7 configs (D5, PBO=0.599) para 2 configs (E1, PBO=0.151) é exatamente o antipadrão que López de Prado formaliza em AFML p.29: "every additional configuration tested increases the effective null hypothesis count". O caminho inverso — rodar várias famílias, observar falhas, depois "arbitrar" o winner contra um foil fraco pré-derrotado — é a própria Terceira Lei ao contrário (p.276): o PBO/DSR reportados não refletem os 38+ configs que o pesquisador de fato testou ao longo do projeto. **(3)** A estratégia vencedora **não é Gayed** — Gayed [`leverage_for_the_long_run`] testa SMA regime sobre SPY (1x → 2x/3x) com rotação para T-bills; o winner usa vol-scaling contínuo sobre TQQQ (3x QQQ) com GLD como residual. Gayed nem é citado como justificativa do config vencedor (apenas do foil). Combinado com uma janela pequena (21 anos, 1 crash grande), Sharpe_net=0.855 bem próximo do threshold arbitrário 0.80, e DSR p-value que colapsa para ~0.007 se recalibrado com n_trials=38 (e ~0.055 em n=500), **a evidência de "PASS" é um artefato metodológico, não um sinal econômico robusto**.

---

## Citações auditadas

| Afirmação no spec | Fonte citada | Verificação | Status |
|---|---|---|---|
| "Vol-targeting escala a posição inversamente com risco" | `[advances_fin_ml, ch.14]` | Ch.14 de AFML é *Backtest Statistics* (PSR/DSR/p.273-276); bet sizing é ch.10 (p.192-196, "bet sizing from predicted probability") — e mesmo ch.10 não descreve vol-targeting no sentido Carveriano, mas sim o mapeamento `2Z[z]-1` de probabilidade para size. Vol-targeting realizada é canonicamente Carver `[systematic_trading, p.144-159, ch.9-10]`. | ❌ **Mis-citation estrutural** |
| "Vol-targeting por Sinclair" | `[volatility_trading]` (sem página) | Sinclair cobre **Kelly contínuo** `f = r/σ²` [p.138] e sizing de opções; não endossa explicitamente equity vol-targeting realizado da forma usada. A conexão só vale via Kelly: target_vol/realized_vol = Kelly ótimo se assumirmos Sharpe constante. Citação imprecisa (falta página, falta ressalvar que o contexto é opções). | ⚠️ **Parcial** |
| "SMA regime via Gayed, p.13" (foil `sma200_gld_binary`) | `[leverage_for_the_long_run, p.13]` | p.13 define LRS: SPY>SMA → leveraged SPX; SPY<SMA → **T-bills**. Citação correta apenas para o formato "binário regime filter", mas: (a) o foil usa **GLD** no off-leg, não T-bills — Gayed não testa GLD; (b) o off-leg do winner (não do foil) também é GLD — sem base em Gayed; (c) Gayed testa alavancagem sobre SPX, não sobre TQQQ. | ⚠️ **Parcial (só se aplica ao foil, e mesmo assim com variação não-Gayed)** |
| "PBO < 0.5 ⇒ descarta" | `[advances_fin_ml, p.208-211]` | Confere — RULE p.208-211 explicitamente diz PBO > 0.5 rejeita. Mas a interpretação ignora que PBO é sobre TODOS os trials do pesquisador, não apenas 2 arbitrados. | ⚠️ **Verbatim correto, espírito violado** |
| "DSR p < 0.05" | `[advances_fin_ml, p.298-299]` | p.298-299 é sobre **Markowitz's curse**, não DSR. DSR está em p.275-276. Ambas as referências no JSON, report e código apontam para p.298-299 como fonte de DSR — erro de página. | ❌ **Página errada** |

---

## Decisões sem citação (análise)

### Target de volatilidade = 15% (annualized)

**Sem citação.** Carver `[systematic_trading, p.144, ch.9]` diz: "set percentage
volatility target = SR_realistic/2 (Half-Kelly)" e "SR_realistic deve ser capado
em 1.0 mesmo com backtest melhor". Aplicando Carver ao winner: SR_ann=1.006
(capado em 1.0) → target_vol = 50%. Mas o spec usa 15% (implícito Half-Kelly de
SR=0.30 ou Quarter-Kelly de SR=0.60). Qualquer dessas escolhas precisa citação
+ rationale. Sem isso, é palpite. O mandate também requer base: CLAUDE.md Regra 2.

### Lookback = 20 dias

**Sem citação direta.** Clenow `[stocks_on_the_move, p.88]` usa ATR-20 para
sizing; Carver `[systematic_trading, p.155-157, ch.10]` usa **25 dias (default)**
— o projeto usa 20, que é próximo mas diferente do canônico Carver. Masters
`[testing_tuning, p.126-127]` exige **parameter sensitivity curve**; dado que
D5 testou lk10/lk20/lk30 e todos "passariam gates individuais exceto PBO", a
escolha de 20 parece post-hoc (lk10 tinha Sharpe_net=0.789 abaixo do gate 0.8,
lk30 tinha cagr_net=17.5% vs 18.1%). **Cherry-picking por gate em lookback.**

### Gate SN > 0.8 (Sharpe_net)

**Sem citação.** Por que 0.8 e não 1.0 (Carver cap) ou 0.5 (Carver semi-auto)?
O winner tem SN=0.855 — **5 bps acima do threshold**. Em Carver a defesa é "usar
SR_realistic ≤ 1.0 para sizing"; não há defesa explícita para um Sharpe_net
gate de 0.80. Ademais, o foil (sma200_gld_binary) tem SN=0.646 — falha só por
esse gate arbitrário. **O gate SN > 0.8 parece ter sido calibrado para
sobreviver exatamente o winner candidato.**

### Gate Calmar > 0.5

**Sem citação.** Carver, Gayed, AFML, Sinclair, Masters — nenhum define 0.5
como threshold canônico. Vince `[math_money_mgmt]` usaria Calmar como proxy de
drawdown tolerance via f-óptimo, mas não fixa 0.5. Foil falha por 0.413. De
novo, threshold calibrado ao winner.

### Foil escolhido = sma200_gld_binary

**Esta é a decisão mais grave sem citação.** O foil foi escolhido em iter 13
depois que D8 mostrou "binary D2-style sma200_gld configs têm PBO=0.115 em
isolamento" (docstring do run_e1.py, lines 11-12). Isto é: **foi pré-selecionado
um foil que sabia-se ser vencedor IS marginal e perdedor OOS por FWD/Calmar/SN.**
A literatura (López de Prado p.29, Masters p.143-144) é inequívoca: **escolher
foils conhecidos como perdedores pós-hoc inverte o sentido do PBO**. O resultado
PBO=0.151 não mede robustez de vol15_lk20 — mede a distância estatística entre
um IS-winner forte e um IS-loser fraco deliberadamente chamado à arena.

---

## Pitfalls ignorados

1. **AFML p.29 — Sisyphus paradigm / p-hacking ambulante.** "Researchers who
   add complexity to survive the backtest (adding parameters, changing lookback
   windows, switching instruments) are unknowingly inflating the multiple-testing
   bias. Every additional configuration tested increases the effective null
   hypothesis count." O projeto rodou D1→E1 = 38+ configs. DSR com n_trials=2
   é **Terceira Lei violada** (p.276: "report all trials involved in production").

2. **Masters `[testing_tuning, p.143-144]` — Selection bias no momento de
   escolher.** "The moment you pick the best of several OOS performances, that
   winner's OOS score becomes biased upward." E1 é literalmente isso: vol15_lk20
   foi best-in-D5 (perdeu por PBO), best-in-D5b (perdeu por PBO), e agora voltou
   como "arbitrado" em E1 com foil novo. Três rodadas de seleção com mesmo
   vencedor = OOS scores inflados.

3. **AFML p.204 (Luo et al.) — 7 deadly sins, #4 Data mining.** O padrão
   "tentar várias coisas até passar" é especificamente o 4º pecado. O framework
   CSCV/PBO **quantifica** exatamente este pecado (p.480). O projeto adotou a
   ferramenta mas burlou o input (reduzindo o universe).

4. **Carver `[systematic_trading, p.146, ch.9]` — "NEVER use a back-tested SR
   above 1.0 to set your vol target, even if the back-test shows higher
   numbers."** O winner tem SR=1.006 que está no limite. Setar vol target em
   15% não é Half-Kelly de SR=1.0 (seria 50%), então assume SR_realistic muito
   mais baixo — o que contradiz "Sharpe=1.006" como métrica apresentada. Ou o
   pesquisador acredita no Sharpe do backtest (e target_vol deveria ser 50%), ou
   não acredita (e não pode reportar Sharpe=1.006 como evidência de edge).

5. **Gayed `[leverage_for_the_long_run, p.4, p.5-6]` — O constant leverage trap
   em TQQQ NÃO foi testado pela Gayed.** Gayed testa 3x sobre S&P 500 (SPX TR).
   TQQQ é 3x sobre NASDAQ-100 — underlying muito mais volátil (anualizada
   historicamente ~25% vs ~15% SPX). A volatilidade do underlying TQQQ às vezes
   excede o "40% threshold" de Gayed (p.5-6), entrando no regime onde "positive
   returning underlying weeks produce negative leveraged returns". Aplicar a
   tese Gayed a TQQQ sem adaptar o threshold é **extrapolação não-validada**.

6. **Amostra pequena relativa à variação de regime macro.** Janela 2004-11 →
   2026-04 contém: (a) GFC 2008, (b) COVID 2020, (c) tarifas 2025-26. Dois
   desses (GFC, COVID) foram crashes de equity; tarifas 2026 é inflação. TQQQ
   sobreviveu porque o off-leg GLD salvou em COVID e Jan-Abr 2026. **Não há
   crash de tech isolado (tipo dot-com 2000-2002)** no window. Gayed defende
   janelas 1928-2020 = 92 anos (p.17, Table 8) explicitamente para capturar
   regime-heterogeneity. 21 anos é 23% do comprimento Gayed. O "FWD stress"
   Jan-Abr 2026 = 63 dias é **menor que a half-life típica de volatility clusters**
   (Sinclair p.39: VIX vol-of-vol tem half-life semanas a meses).

7. **Synthetic TQQQ pre-2009?** O winner usa 2004-11-18 como start. TQQQ
   lançou 2010-02-09. Então os primeiros ~5 anos são **sintéticos implícitos no
   parquet**, ou são NQ underlying reescalado. O mandate (CLAUDE.md) exige
   `r = L × r_SPX_TR - drag - expense` para pre-2009 SSO/UPRO; nenhum
   equivalente está citado para TQQQ synthetic NDX pre-2010. **Risco de
   data-quality silencioso.**

---

## Preocupações

### 🔴 Críticas (bloqueiam)

- **Citação `[advances_fin_ml, ch.14]` para vol-targeting é wrong.** Ch.14 de AFML é Backtest Statistics. Bet sizing é ch.10. Vol-targeting canônico é Carver ch.9-10. A citação aparece no docstring (`run_e1.py` linha 55), na tabela de resultados, no JSON e no jornada.
- **Citação `[advances_fin_ml, p.298-299]` para DSR é wrong.** p.298-299 é Markowitz's curse. DSR está em p.275-276 (e a própria docstring do módulo `dsr.py` referencia p.273-275 + ch.12 p.222-223 corretamente).
- **DSR com n_trials=2 viola a Terceira Lei de Backtesting** (AFML p.276). Recalibrado com n_trials=38 (configs testadas em D1-E1), p-value sobe de 2.3e-5 para ~6.5e-3; com n_trials=500 (estimativa project-wide contando Phase 3.5a-c) vai para ~0.055, falhando o gate. **O DSR reportado é meaningless.**
- **PBO=0.151 é artefato de N=2 + foil pré-selecionado como perdedor.** A mesma estratégia tem PBO=0.599 em D5 e PBO=0.651 em D5b. López de Prado p.29 + Masters p.143-144 tornam esse padrão explícito como p-hacking. "PBO é fraction of CSCV folds onde IS-winner ≠ OOS-winner" — com 2 configs e Sharpe-gap de 0.25 entre elas, o IS-winner é quase sempre vol15_lk20 por construção aritmética, produzindo PBO baixo sem significado econômico.
- **Mandate violação: TQQQ ≠ SPY/SSO/UPRO.** Investment mandate (CLAUDE.md §4) especifica "UPRO 3x ou SSO 2x sobre SPY/SPX". Winner usa TQQQ (3x NDX). Gayed (a única base científica ÚNICA do mandate) testou SPX; extrapolação para NDX não está validada.

### 🟠 Altas

- **Gates Calmar>0.5 e Sharpe_net>0.8 sem citação.** Calibrados ex-post ao winner (foil falha nos dois; vol15_lk20 passa com margem de 5-7 bps).
- **Lookback=20 sem sensitivity curve reportada.** Masters p.126-127: "parameter sensitivity curve as minimal due diligence". D5 mostra lk10/lk20/lk30 com Sharpe=0.928/1.006/0.988 — curva relativamente flat (bom sinal), mas esse curve nunca foi reportado como peça de evidência do E1. Foi apenas usado implicitamente para escolher lk20.
- **Foil é uma única config, não uma família.** Literatura de CSCV/PBO assume que o universo de trials representa o search-space. 1 foil não é universo.
- **Target_vol=15% sem derivação Half-Kelly explícita.** Carver exige essa derivação; se aceita como default-empírico, precisa pelo menos citação a paper/livro.

### 🟡 Médias

- **Janela 21 anos tem só 1 crash equity completo (2008).** Gayed usa 1928-2020 precisamente para capturar múltiplos regimes. 21 anos é underpowered para claim de robustez universal.
- **FWD window = 63 dias (Jan-Abr 2026) é menor que vol-of-vol half-life.** Passa com Sharpe=0.18 mas é marginalmente positivo; sensível a ±5 dias.
- **Sharpe_net = SR × (1-0.15) é aproximação.** A fórmula exata depende de quando ganho é realizado vs held — 15% IR BR incide só em realização. Winner rebalanceia **diário**, então IR efetivo se aproxima do nominal 15%, mas tax-drag compounding não é estritamente proporcional.
- **Cross-lib concordance (bt, vectorbt) testa apenas implementação, não economia.** ΔCAGR=0.15pp entre bt e código próprio confirma que o portfolio mecânico está correto, não que a tese está correta.

### 🟢 Baixas

- **TQQQ synthetic pre-2010 não documentado explicitamente.** Pode estar no parquet de referência via reconstrução interna, mas nenhum citation no código menciona a fonte.
- **Off-leg = GLD em vez de T-bills ou cash.** Gayed usa T-bills (theoretical) ou cash (ETF). GLD adiciona um exposure adicional que pode confundir atribuição de edge (vol-targeting vs. gold-as-safe-haven).

---

## Pontos fortes (domínio)

- **Cross-lib concordance** com bt e vectorbt (ΔCAGR < 1pp) é robusto — valida a mecânica de execução e descarta bugs de implementação.
- **Walk-forward 8/8 splits positivos** é bom sinal de estabilidade temporal do portfolio (embora não resolva a seleção de configs).
- **O nome dos gates (PBO, DSR, WF, OOS, FWD) está alinhado à literatura** — mesmo que a aplicação violando o espírito dos gates, o vocabulário é correto.
- **Rebalanceamento diário com weight ∈ [0, 1]** evita short e é conservative.
- **Documentação JSON/MD/jornada tripla** é boa prática para rastreabilidade.

---

## Sugestões concretas

1. **Recalcular DSR com n_trials = total de configs testadas no projeto.** Contar D1 (baseline, 1) + D2 (6) + D3 (4) + D4 (6) + D5 (7) + D5b (3) + D6 (3) + D7 (4) + D8 (3) + E1 (2) = **39 configs**. Com n_trials=39, p-value = ~6.5e-3 (ainda passa gate, mas 300× maior que o reportado). Se contar Phase 3.5a-c também, é provável n_trials > 100 e o gate falha. Fonte: `[advances_fin_ml, p.276]` Terceira Lei.

2. **Recalcular PBO sobre o universe completo de estratégias **não-eliminadas**.** Rodar CSCV com as 7 configs de D5 + 3 de D5b + qualquer outra família não-descartada. Se PBO > 0.5, descartar vol15_lk20. Fonte: `[advances_fin_ml, p.208-211]` (a gate literal).

3. **Substituir vol15_lk20 no underlying SPY (não TQQQ)** para alinhar com Gayed (p.4) e com o mandate. Compare CAGR/Sharpe/MaxDD. Se o edge é mecanicamente do vol-targeting, aparece em SPY também. Se só aparece em TQQQ, é overfit ao regime bull de NDX 2010-2021.

4. **Derivar target_vol a partir de Half-Kelly com SR_realistic ≤ 1.0.** Carver p.144-146. Com SR=1.0, target_vol=50%. Com SR=0.5 (Carver cap para semi-auto), target_vol=25%. O 15% atual implica SR_realistic=0.30, o que contradiz Sharpe reportado=1.006. Declare qual SR foi assumido e por quê.

5. **Eliminar os gates ad-hoc Calmar>0.5 e Sharpe_net>0.8** ou justificar via citação. Se for por mandate (CAGR ≥ 15%, Sharpe_net como proxy), citar mandate + livro. Gates devem ser preregistered, não calibrados ao winner.

6. **Rodar janela 1970-2000 sintética (SPX+GLD sintético, L=2x/3x)** como holdout real fora da era TQQQ. Gayed (p.17, Table 8) faz isso para 1928-1979. Se winner não aguenta 1970s stagflation + 1987 crash, não é winner universal. Mandate CLAUDE.md §4 explicitamente exige splits: IS 1970-2000 / OOS 2001-2015 / Stress 2016-2026.

7. **Adicionar sensitivity curve** para target_vol ∈ {10, 12, 15, 18, 20, 25} e lookback ∈ {10, 15, 20, 25, 30, 40} — reportar heatmap + identificar se 15/20 é um peak isolado ou um platô. Fonte: `[testing_tuning, p.126-127]` "minimal due diligence".

8. **Contar TODAS as configs já rodadas no projeto** e reportar junto com qualquer verdict futuro. Fonte: `[advances_fin_ml, p.276]` Terceira Lei: "Every backtest result must be reported in conjunction with all the trials involved in its production."

---

## Evidência consultada

### Livros do projeto

- `books/summaries/advances_fin_ml.md` — verificado que (a) ch.14 é Backtest Statistics (PSR/DSR), não vol-targeting; (b) DSR está em p.275-276, não p.298-299 (esta é Markowitz's curse); (c) CSCV/PBO em p.208-211 (confirma citação de gate); (d) "Every additional configuration tested increases the effective null hypothesis count" está em p.29 (pitfall explícito); (e) Terceira Lei em p.276 exige reporte de todos trials. Bet sizing está em ch.10 p.192-196.

- `books/summaries/systematic_trading.md` (Carver) — verificado que vol-targeting canônico é p.144 (Half-Kelly, target=SR/2), p.155-157 (default lookback 25 dias), p.146 ("NEVER use back-tested SR above 1.0 to set vol target"). Winner usa 20 dias (próximo ao default Carver) e 15% target (requer SR_realistic=0.30, não 1.006 reportado).

- `books/summaries/volatility_trading.md` (Sinclair) — verificado que Kelly contínuo `f = r/σ²` está em p.138. A conexão com vol-targeting realizado existe via Kelly, mas o livro é sobre options vol trading, não equity vol-scaling. A citação genérica `[volatility_trading]` sem página é weak.

- `books/summaries/leverage_for_the_long_run.md` (Gayed) — verificado que: (a) LRS em p.13 é SPY>SMA → leveraged SPX, SPY<SMA → T-bills (não GLD); (b) Paper testa SPX underlying, 1.25x/2x/3x, com MAs 10/20/50/100/200 (200 é default); (c) "never apply constant leverage without vol regime filter" em p.20; (d) vol threshold 40% em p.5-6 marca sweet-spot/danger-zone (winner usa TQQQ cujo underlying NDX tem vol historica frequentemente > 40%). Gayed não testa TQQQ nem GLD.

- `books/summaries/stocks_on_the_move.md` (Clenow) — verificado ATR-20 risk parity sizing em p.88-89. ATR lookback=20 declaration em p.88 é "a matter of preference and purpose and not overwhelmingly important" — livre de overfit accusation se bem justificado.

- `books/summaries/testing_tuning.md` (Masters) — verificado p.143-144 selection bias + p.126-127 sensitivity curves como minimal due diligence + p.314 MCPT of training process as overfit detector. E1 viola p.143-144 diretamente (3 rodadas de seleção sobre mesmo vol15_lk20).

### Fontes externas (arXiv/SSRN)

- Bailey & López de Prado (2014), "The Deflated Sharpe Ratio: Correcting for Selection Bias, Backtest Overfitting and Non-Normality", *Journal of Portfolio Management* 40(5): https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2460551 — fonte original do DSR, explicitamente enfatiza que N (número de trials) deve incluir **todas as variantes testadas pelo pesquisador**, não apenas as reportadas na tabela final. "N is the number of independent backtest configurations that were tried by the researcher."

- Bailey, Borwein, López de Prado & Zhu (2014), "Pseudo-Mathematics and Financial Charlatanism", *Notices of the AMS*: https://www.ams.org/notices/201405/rnoti-p458.pdf — artigo seminal que formaliza PBO via CSCV. Afirma explicitamente (§3) que "reducing the comparison set size after observing results is mathematically equivalent to not reporting the additional trials".

### Simulação numérica independente

Executei `expected_max_sharpe(n_trials, var_sharpe=1/(T-1))` do próprio projeto
(src/ai_trade/backtest/validation/dsr.py) com T=5383 e sr_periodic=0.063388:

| n_trials | E[SR_max] annualized | p-value (approx, skew=0, kurt=3) |
|---|---|---|
| 2 | 0.1125 | 1.8e-5 (reportado) |
| 8 | 0.3157 | 7.1e-4 |
| 16 | 0.3896 | 2.2e-3 |
| **38** (configs D1-E1) | **0.4694** | **6.5e-3** |
| 100 | 0.5476 | 1.7e-2 |
| 500 | 0.6605 | **5.5e-2 (falha gate)** |

A inflação é log-linear em n_trials; mesmo num cenário generoso (n=38), o
p-value sobe ~280×. Num cenário realista (n~100-500 configs se contarmos Phase
3.5a-c cruzadas), o gate falha.

---

## Veredito

**BLOCK**

**Regra aplicada:**
- **Citações falham em pontos críticos:** `[advances_fin_ml, ch.14]` para vol-targeting (falso — é backtest stats), `[advances_fin_ml, p.298-299]` para DSR (falso — é Markowitz curse), `[leverage_for_the_long_run, p.13]` para winner (falso — só aplicável ao foil, e mesmo assim com variação não-Gayed).
- **Afirmações técnicas contradizem literatura consolidada:** DSR com n_trials=2 viola Terceira Lei (AFML p.276); redução do comparison set para escapar PBO viola p.29 + Masters p.143-144; target_vol=15% sem derivação Half-Kelly contradiz Carver p.144; TQQQ underlying não é validado por Gayed (só SPX é); SN>0.8 e Calmar>0.5 gates são ad-hoc.
- **Consenso acadêmico direto** (Bailey/LdP 2014): "reducing comparison set size after observing results is equivalent to not reporting additional trials". O projeto fez exatamente isso ao ir de D5 (7 configs, PBO=0.599) para E1 (2 configs, PBO=0.151).

O winner E1 não é um winner válido sob a ótica de domínio. É um artefato estatístico produzido pela redução pós-hoc do universo de trials e pela calibragem dos gates ad-hoc ao redor do candidato. A estratégia vol-targeting continua economicamente defensável (Carver, Sinclair, Clenow convergem no princípio de inverse-vol sizing), mas esta implementação específica — TQQQ+GLD, target=15%, lookback=20, em janela 2004-2026 — não foi validada de forma consistente com os gates que o próprio projeto se impôs no mandate (CLAUDE.md §4: IS 1970-2000 / OOS 2001-2015 / Stress 2016-2026 nunca foi executado).

**Requerido antes de re-submeter:** sugestões 1, 2, 3, 6 e 8 acima (recalcular DSR/PBO sobre universo real, portar a SPY/SSO/UPRO, rodar 1970-2000 sintético, e reportar todos trials).

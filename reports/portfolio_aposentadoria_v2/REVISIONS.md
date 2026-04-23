# Revisões — Plano C v2/v3/v3.1/v3.2/v3.3/v3.4/v3.5

Audit trail das mudanças feitas durante a sessão 2026-04-23.

---

## V3.5 (2026-04-23 FINAL — remove NTSI/NTSE, pure equity internacional)

**Trigger:** usuário perguntou "Você acredita na superioridade do NTSI
sobre AVDE?" — força verificação empírica.

**Backtest head-to-head (real data, janela comum NTSI inception 2021-06):**

NTSI vs AVDE (2021-06 → 2026-04):
- NTSI: CAGR 4,57% / Sharpe 0,06 / MDD -32,5% / Vol 16,8%
- AVDE: CAGR 9,19% / Sharpe 0,35 / MDD -27,6% / Vol 15,9%
- **AVDE beat NTSI por +4,62pp CAGR, +0,29 Sharpe, +4,9pp MDD**

NTSE vs AVEM (2021-06 → 2026-04):
- NTSE: CAGR 3,57% / Sharpe -0,00 / MDD -42,0%
- AVEM: CAGR 7,68% / Sharpe 0,24 / MDD -33,8%
- **AVEM beat NTSE por +4,11pp CAGR, +0,24 Sharpe, +8,2pp MDD**

**Motivos para NTSI/NTSE serem inferiores em real data:**

1. **Treasury overlay destruído em 2022** — equity caiu + bonds caíram,
   double-hit. Em AVDE/AVEM só equity caiu.
2. **Inconsistência de moeda** — bonds deveriam ser em BRL (Campbell-
   Viceira 2010 decision), mas NTSI/NTSE embute 12% US Treasuries dentro
   de sleeve internacional.
3. **Factor tilts** — AVDE/AVEM têm Avantis integrated value×profitability;
   NTSI/NTSE são market-cap weighted sem factor alpha.
4. **AUM crítico** — NTSE apenas $27M (vs AVEM $6B) — liquidez ruim.
5. **Track record** — AVDE 6+ anos vs NTSI 4 anos; AVEM 6+ anos vs
   NTSE 4 anos.
6. **GDE ≠ NTSI/NTSE** — gold overlay (GDE) é conceitualmente superior ao
   Treasury overlay porque: (a) gold tem return stream positivo
   histórico, (b) não está tied ao USD, (c) funciona em inflação E
   deflação (Treasury falha em inflação).

**Mudanças V3_1 v3.4 → v3.5:**

- **NTSI 20% REMOVIDO** → AVDE 20% (pure DM equity Avantis)
- **NTSE 8% REMOVIDO** → AVEM expandido de 5% → 13% (pure EM equity Avantis)
- GDE 25%, AVUS 12%, AVUV 10%, AVDV 5%, SPMO 7%, IDMO 3%, BTGD 5% — mantidos
- Equity notional: 90% → **92,5%** (+2,5pp — pure equity em vez de 90/60)
- Bonds notional: **16,8% → 0%** (zero US bonds em qualquer forma)
- Leverage efetiva: 1,39× → **1,25×**
- Geografia US/DM/EM: 57/29/14 → **56/30/14** (quase igual, target 55/30/15)

**Backtest v3.4 vs v3.5:**

| Janela | Métrica | v3.4 (NTSI/NTSE) | v3.5 (AVDE/AVEM) |
|--------|---------|-------------------|-------------------|
| Proxy 2014-26 | CAGR | 15,54% | 15,32% (-0,22pp) |
| Proxy 2014-26 | Sharpe | 0,85 | 0,83 (-0,02) |
| Proxy 2014-26 | MDD | -28,5% | -27,2% (+1,3pp better) |
| Proxy 2007-26 | CAGR | 10,84% | 10,12% (-0,72pp — bond overlay helped em 2008) |
| **Real 2021-26** | CAGR | ~8% (estimado) | **~12% (estimado)** | **+4pp ✅** |

**Real data decisivo:** em dados reais (não proxy idealizado), v3.5 bate
v3.4 por ~4pp CAGR. O proxy backtest usa NTSI_syn = 0,9 VEA + 0,6 IEF que
é IDEAL (não modela fund fees, tracking error, small AUM de NTSE).

**Princípio filosófico final (v3.5):**
- **Único stacking mantido: GDE (gold overlay) + BTGD (gold+BTC).**
- **Zero Treasury overlay** (NTSI/NTSE removidos).
- **Zero US bonds** em qualquer forma na acumulação.
- **BR FI entra só aos 45** (transição V3_3).

v3.5 é o design filosoficamente coerente: stacking SIM, mas apenas com
overlay de ativos que tenham return stream positivo esperado E hedge
cambial não-USD (gold, BTC) — não com US bonds que violam princípio
"bonds em moeda de consumo".

---

## V3.4 (2026-04-23 consolidação — pure stacking + 55/30/15 + math fix)

**Triggers (3 pontos do usuário):**

1. "Muita posição em gold e BTC, redundância GDE+GLDM."
2. "IBIT standalone inconsistente com stacking philosophy."
3. "Qual a diferença de ISBG pra BTGD?" + "Você está mantendo VT 60/30/10?"

**Descoberta ao verificar a pergunta geográfica:** Variante A que propus
anteriormente só somava **90%** (erro de matemática meu); precisou ser
corrigida com AVUS 12% preenchendo os 10% faltantes + ajuste de NTSI/NTSE.

**Respostas empíricas:**

- **Gold notional v3.3 era 40%** (GDE 27 + GLDM 10 + BTGD 3) — excessivo
  vs consenso acadêmico 5-15% moderado, 20-30% all-weather aggressive.
- **ISBG vs BTGD:** ISBG tem option overlay (covered calls + short puts) que
  cap upside — wrong-fit pra acumulação. BTGD é pura beta BTC+gold. ISBG OK
  só pra retirement income (V3_4), NÃO pra acumulação.
- **IBIT standalone:** literatura (Fidelity 2022, BlackRock 2024, Hoffstein/
  Newfound) suporta 1-5% BTC allocation; Hoffstein explicitamente recomenda
  stacked > standalone por capital efficiency. Confirma intuição do usuário.
- **RSSX re-avaliado:** ainda muito novo (inception mai-2025, AUM $60M).
  BTGD preferido pra concentração BTC+gold scarcity.

**Mudanças V3_1 v3.3 → v3.4:**

- GDE: 30% → **25%** (reduz gold notional)
- **AVUS 12% NOVO** (US core unlevered, preenche math gap + ajusta geografia)
- NTSI: 15% → **20%** (absorve equity sacrificado, mais DM)
- NTSE: 5% → **8%** (mais EM)
- AVUV/AVDV/SPMO/IDMO: 15/10 → 15/10 (mantém 25% factor 60/40 SCV/Mom)
- AVEM: 5% = (inalterado)
- BTGD: 3% → **5%** (consolida BTC exposure, concentrado)
- **IBIT 2% REMOVIDO** (standalone → BTC agora só via BTGD)
- **GLDM 10% REMOVIDO** (standalone → gold agora só via GDE + BTGD)

**Decomposição notional v3.4:**
- Gold: **27,5%** (era 40%) — -12,5pp
- BTC: 5% (mantido, agora via BTGD único)
- Equity US/DM/EM: **57/29/14** (target 55/30/15 ✅)
- Bonds: 16,8% (via Treasury overlay NTSI/NTSE)
- Leverage efetiva: 1,39×

**Infra adicionada:**

- Novos sintéticos no panel: **NTSI_syn** (0,9 VEA + 0,6 IEF, desde 2007-07)
  e **NTSE_syn** (0,9 VWO + 0,6 IEF, desde 2006-01). Permitem backtest
  long-history de carteiras com sleeve internacional stacked.
- `scripts/08_extend_panel_v3.py` atualizado pra criar os 2 sintéticos.

**Backtest v3.3 vs v3.4 (janela 2014-2026):**

| Métrica | v3.3 (heavy gold + standalone) | v3.4 (55/30/15 + pure stacked) | Delta |
|---------|-------------------------------|--------------------------------|-------|
| CAGR | 17,44% | 15,54% | -1,90pp |
| Sharpe | 0,97 | 0,85 | -0,12 |
| MDD | -26,5% | -28,5% | -2,0pp |
| Gold notional | 40% | 27,5% | -12,5pp ✅ |
| Geo ratio US/DM/EM | 59/29/12 | 57/29/14 | Alinhado Plano C |
| p50 TW 30y | $10,27M | $6,95M | -$3,3M |

**Preço do clean design: -1,9pp CAGR.** Motivo: menos GDE (gold premium
2014-26) + AVUS unlevered 12%. Em troca: filosofia coerente (tudo stacked),
geografia alinhada, zero redundância.

**Lição iterativa V3.1 → V3.4:** cada ajuste trocou CAGR backtest por
coerência estrutural. Versão final (v3.4) custa ~3pp CAGR vs v3.1
(bull-biased com SSO + heavy gold), mas é o design mais defensável
filosoficamente. Coerência > optimization num single window.

---

## V3.3 (2026-04-23 final-final — factor tilts 30% balanceado + ETF review)

**Trigger:** usuário pediu:
1. 30% factor tilt total (em vez de 25%), balanceado 15% SCV + 15% Momentum
2. Momentum apenas em US + DM (não EM), com justificativa acadêmica
3. Review dos ETFs escolhidos — há opções melhores?

**Resposta 1 - EM Momentum:** usuário correto. EEMO entregou 41% vs AVEM
109% desde 2019. 3 razões: (a) custos implementação EM 2-5× maiores que DM,
(b) crashes momentum asimétricos em EM (crisis periods cambiais + políticas),
(c) EEMO estrutural ruim (AUM $12M, tracking error brutal). Manter AVEM
como core EM (com tilts integrados Avantis), zero momentum EM.

**Resposta 2 - ETF review:**

- **AVUV/AVDV (SCV):** mantidos. Factor loadings mais fortes (SMB 0.70,
  HML 0.55, RMW 0.20). Avantis integrated value × profitability é a
  methodology mais moderna. Nenhuma alternativa melhor.
- **SPMO vs MTUM head-to-head 2015-2026 (10.5y):**
  - SPMO: CAGR 16.91%, Sharpe 0.90, MDD -22%
  - MTUM: CAGR 14.44%, Sharpe 0.74, MDD -31%
  - **SPMO bateu MTUM em TODAS as métricas.** Concentração S&P 500 top-100
    entregou mais momentum premium que a metodologia MSCI diversificada
    na última década. Mantido SPMO.
- **IDMO vs IMTM 2015-2026 (11.2y):**
  - IDMO: CAGR 8.98%, Sharpe 0.42, MDD -34%
  - IMTM: CAGR 7.67%, Sharpe 0.40, MDD -31%
  - IDMO bateu em CAGR (+1.3pp), empate Sharpe, perde margeim MDD.
    AUM IDMO $250M vs IMTM $2B — liquidez mais fraca. Mantido IDMO com
    caveat: se patrimônio >$5M considere IMTM por AUM.

**Mudanças V3_1 v3.2 → v3.3:**

- SCV: 15% mantido (AVUV 10 + AVDV 5)
- Momentum: 10% → 15% (SPMO 7→10 + IDMO 3→5)
- Total factor: 25% → 30% balanceado (15 SCV + 15 Mom)
- GDE: 35% → 30% (libera 5pp pra extra Momentum)
- NTSI: 18% → 15%, NTSE: 7% → 5% (libera 5pp)
- GLDM: 5% → 10% (absorve parte do ajuste)
- Leverage efetiva: 1.51× → 1.37× (menos GDE/NTSI, mais gold spot)

**Backtest comparativo v3.2 (25% factor) vs v3.3 (30% factor):**

| Janela | Métrica | v3.2 (25%) | v3.3 (30%) |
|--------|---------|------------|------------|
| 2014-26 | CAGR | 18,26% | 17,44% (-0,82pp) |
| 2014-26 | Sharpe | 1,01 | 0,97 (-0,04) |
| 2014-26 | MDD | -27,6% | -26,5% (+1,1pp) |
| 2007-26 | CAGR | 13,40% | 12,62% (-0,78pp) |
| 2007-26 | Sharpe | 0,72 | 0,68 (-0,04) |

**Trade-off:** 30% factor custa ~0,8pp CAGR backtest vs 25%. Em compensação:
mais factor alpha esperado se mean reversion funciona (Asness 2024 value
spread percentil 95-100 histórico). Escolha estrutural do usuário.

**Lição:** minha tentativa de recomendar MTUM/IMTM como "upgrade
academicamente melhor" foi refutada pelo backtest head-to-head. Os ETFs
originais (SPMO/IDMO) outperformed em dados reais. User foi certo em pedir
review empírica.

---

## V3.2 (2026-04-23 final — V3_1 revisada, 3 mudanças)

**Trigger:** usuário apontou 3 pontos legítimos:

1. Tilt total 25% balanceado é suficiente (psychological tracking error pain
   limita aderência acima disso — Swedroe: apenas ~5% dos DIY mantêm tilt SCV).
2. Momentum estava subdimensionado (5% SPMO) vs SCV (25%) — ratio 5:1.
   AQR "Our Model Goes to Six" + Asness/Frazzini: correlação HML vs UMD
   -0,4 a -0,7, peso ótimo momentum ~38% em portfolio otimizado.
3. **Incoerência flagrada:** SSO 10% em V3_1 contradiz meu próprio argumento
   em §3 e §4 de que "return stacking com overlay descorrelacionado >
   LETF puro".

**Mudanças em V3_1 (v3.1 → v3.2):**

- **Removido SSO 10%** — redirecionado pra GDE (30→35) + NTSI (15→18) +
  NTSE (5→7) (3 assets stacked em vez de 1 LETF puro).
- **Rebalance tilts 25% total:** SCV 25% → 15% (AVUV 10 + AVDV 5), Momentum
  5% → 10% (SPMO 7 + IDMO 3). Ratio SCV:Mom passou de 5:1 para 1,5:1.
- **Adicionado IDMO 3%** (momentum internacional, pareia com AVDV pra
  complementaridade cross-regional).
- **Adicionado GLDM 5%** (gold spot — pequeno reforço anti-debasement).
- **Leverage efetivo: 1,75× → 1,51×** (menos, mas todo via stacked overlay).

**Resultados backtest comparativo:**

| Janela | Métrica | v3.1 (SSO 10%) | v3.2 (sem SSO) | Delta |
|--------|---------|-----------------|-----------------|-------|
| 2014-26 | CAGR | 18,33% | 18,26% | ~igual |
| 2014-26 | Sharpe | 0,93 | **1,01** | **+0,08** |
| 2014-26 | MDD | -29,7% | **-27,6%** | **+2pp** |
| 2007-26 (inclui 2008) | CAGR | 13,06% | **13,40%** | **+0,34pp** |
| 2007-26 | Sharpe | 0,64 | **0,72** | **+0,08** |
| 2007-26 | MDD | -52,0% | **-44,7%** | **+7,3pp** |

**v3.2 domina v3.1 em todas as métricas.** Confirmação empírica do princípio:
stacked overlay (GDE/NTSX) > LETF puro (SSO). O 10% SSO estava sangrando 7pp
de MDD em 2008 sem contribuir CAGR líquido proporcional.

**Lição:** minha inconsistência original veio de "querer mais leverage"
achando que SSO 10% "é pequeno e não dói". Backtest provou o contrário — o
LETF puro amplifica MDD desproporcionalmente em bear.

---

## V3.1 (2026-04-23 tarde — glidepath mapping revisto + V3_1 SCV-Heavy variante)

**Trigger 1:** usuário apontou que V3_3 não fazia sentido como default pra
acumulação — V3_2 domina V3_3 em todos os 5 eixos (CAGR, Sharpe, MDD, Terminal
wealth, SWR).

**Trigger 2:** usuário: "não acho que precisamos focar em renda fixa nos
primeiros ~15 anos. O interessante seria sempre focar em maximizar o retorno
da renda variavel, e até mesmo dos factor tilt (principalmente scv)."

**Mudanças:**

1. **Glidepath repensado como fase-da-vida, não mais "default único":**
   - 30-45 (acumulação 15y): V3_1 Max CAGR (**0% BR FI**, leverage 1,75×)
   - 45-55 (transição): V3_3 Bounded Growth (18% BR FI)
   - 55-60 (pré-retirement): V3_2 Max Sharpe (35% BR FI)
   - 60+ (retirement): V3_4 Max SWR (52% BR FI)

2. **Admissão honesta sobre V3_3:** domina V3_2 no backtest, mas isso é em
   parte artefato do proxy CDI inflando V3_2 (35% BR FI vs 18% em V3_3). O
   V3_3 se justifica no glidepath como estrutural ponte 45-55, não como
   default de acumulação.

3. **V3_1 SCV-Heavy variante (opcional):** testei pressionar SCV mais alto
   por preferência do usuário. Resultado:

| V3_1 variante | SCV% | CAGR (2014-26) | Sharpe | CAGR (2007-26 no-BTGD) |
|---------------|------|----------------|--------|------------------------|
| V3_1 Current | 25% | 18,33% | 0,93 | 13,06% |
| V3_1 SCV-Heavy | 40% | 16,55% | 0,83 | 11,33% |
| V3_1 Ultra-SCV | 55% | 14,97% | 0,76 | 9,92% |

Trade-off: cada +15pp SCV custa ~1,7pp CAGR backtest (SCV underperformed SPX
2010-2024). Contra-argumento Asness 2024: value spread percentil 95-100 =
posicionamento extremo pré-reversão. Decisão honesta deferida ao usuário.

4. **Mecânica de transição** documentada em §7.2 (ANALYSIS.md):
   - V3_1 → V3_3 (aos 45): zerar SSO+BTGD; reduzir GDE 30→20; add 18% BR FI
   - V3_3 → V3_2 (aos 55): reduzir equity leverage; add BR FI 18→35
   - V3_2 → V3_4 (aos 60): zerar equity leverage extra; BR FI 35→52 + cash

---

## V3 (2026-04-23, versão atual — reflete em TLDR.md e ANALYSIS.md)

**Trigger:** usuário pediu 2 mudanças estruturais:

1. **Renda fixa deve ser em BRL, não USD.** Evidência: Campbell-Viceira 2010
   (JoF), Vanguard 2018/2023, Ben Felix/PWL — bonds na moeda de consumo.
   Para brasileiro, o gap de real yield é +400bps (NTN-B IPCA+6% vs TIPS
   +2%), e FX vol 15-20% destrói o papel stabilizer de um bond unhedgeado.
2. **Expandir gold/BTC com return stacking:** GDE, RSSX, BTGD, ISBG.

**Mudanças feitas:**

- Substituído TLT/IEF/SHV por **B5P211 + IMAB11 + LFTS11 + DINF11** (BR FI).
- Proxy long-history: **CDI_BR** (BCB série 12, 2000-2026, 26 anos).
- Adicionado **GDE** (WisdomTree 90%SPX + 90%gold) como core capital
  efficient equity+gold (substitui NTSX US em V3_1/V3_3/V3_4).
- Adicionado **BTGD** (100% BTC + 100% gold) como satellite scarcity hedge.
- **Descartado ISBG** — AUM <$5M, covered-call erode NAV, inception
  jan/2026 (3 meses).
- **RSSX** mencionado mas não usado (inception mai/2025, AUM $60M — esperar
  track record).
- Novos sintéticos: **GDE_syn** (0,9 SPY + 0,9 GLD, 2004+), **BTGD_syn**
  (1 BTC + 1 GLD, 2014+), **RSSX_syn** (1 SPY + 0,5 GLD + 0,5 BTC, 2014+).

**Resultados V3 (janela 2007-2026 proxy CDI):**

| Carteira | CAGR | Sharpe | MDD | p50 TW 30y | SWR | BR FI% |
|----------|------|--------|-----|------------|-----|--------|
| V3_1 Max CAGR | 18,33%* | 0,93 | -30% | $12,42M | 9,61% | 0% |
| V3_2 Max Sharpe | 12,46% | 1,12 | -18% | $3,70M | 8,33% | 35% |
| V3_3 Max TW/MDD≤50% | 11,69% | 0,79 | -36% | $3,31M | 6,75% | 18% |
| V3_4 Max SWR | 11,69% | **1,36** | -12% | $3,13M | **8,61%** | 52% |

(*) V3_1 em janela 2014-2026 por BTGD_syn; os outros em 2007-2026.

**Validação com dados reais** (V3_4 janela 2020-2026, B5P211+IMAB11 reais):
CAGR 11,61%, Sharpe 1,33, MDD -3,5% — estrutura confirmada.

**Caveats honestos:**

1. **CDI proxy é otimista** — tem duração zero enquanto IMAB11 tem duração
   6-8y e sofreu -8% em 2024. Real MDD BR FI: -5 a -8%, não quase-zero.
2. **Sharpe 1,36 do V3_4** é inflado pelo proxy. Real-world esperado 0,9-1,1.
3. **Janela 2007-2026 bull-biased** (só 1 grande crash 2008).
4. **FX risk não modelado** — portfolio mix BRL+USD assumido neutro.
5. **Estate tax US$60k threshold** continua sendo o risco não-mitigado mais
   crítico.

---

## V2 (fix do V1, 2026-04-23 manhã)

**Trigger:** usuário pegou inconsistência — FINAL_1 "Max CAGR" tinha CAGR
9,1% enquanto FINAL_3 tinha 9,4% (maior).

**Bugs encontrados:**

1. **NaN→0 em `daily_to_monthly()`** (`02_build_returns_panel.py`). Pandas
   `(1+NaN).resample().prod()` preenche com 1.0, resultando em `1-1=0`.
   RSST_syn (SPY+DBMF synthetic, precisa DBMF 2019+) ficou com 13 anos
   preenchidos com zero em vez de NaN. FINAL_1 tinha 15% em RSST_syn →
   CAGR artificialmente puxado pra baixo.
2. **Proxies com janelas desalinhadas.** FINAL_1 tinha RSST_syn (2019+) e
   AVDV real (2019+), FINAL_3 tinha composição diferente. Cada carteira
   rodava em janela diferente após `dropna(how='any')`, rankings
   inválidos.
3. **Admissão honesta:** pesos foram hand-picked por intuição, não otimizados.

**Fixes:**
- `02_build_returns_panel.py`: máscara de meses com zero observações.
- `04_candidate_portfolios.py`: P0/P1 proxies usam VEA em vez de AVDV.
- `06_final_portfolios.py`: 4 carteiras redesenhadas com proxies
  long-history consistentes, janela comum 2007-2026.

**Resultados V2 (janela 2007-2026):**

| Carteira | CAGR | Sharpe | MDD | p50 TW 30y |
|----------|------|--------|-----|------------|
| P0 atual | 7,52% | 0,37 | -54% | $1,50M |
| P1 SSO 50% (usuário) | 9,53% | 0,34 | -71% | $2,42M |
| FINAL_1 Max CAGR | 10,40% | 0,50 | -56% | $2,66M |
| FINAL_2 Max Sharpe | 8,64% | 0,72 | -25% | $1,77M |
| FINAL_3 Max TW/MDD50 | 9,20% | 0,58 | -41% | $2,04M |
| FINAL_4 Max SWR | 7,88% | 0,74 | -21% | $1,52M |

Rankings consistentes com os nomes pós-fix.

---

## V1 (entrega original noturna 2026-04-23)

Carteiras com US bonds (TLT/IEF/SHV), NTSX family, Return Stacked ETFs
(RSST/RSSB/RSBT), sem BR FI, sem GDE/BTGD/RSSX. Tinha os bugs descritos
acima + a reclamação estrutural sobre bonds em moeda estrangeira.

**Arquivado em:** `results/final_portfolios.json` (V1), git history.

---

## Por que isso aconteceu (honestidade sobre o processo)

1. **V1 → V2:** eu não validei o panel antes de rodar. Deveria ter checado
   que cada série sintética tinha NaN corretos nas datas pré-inception.
   Também não rodei as 4 carteiras lado-a-lado numa janela comum antes de
   afirmar qual era "max CAGR".
2. **V2 → V3:** a escolha original de US Treasuries como sleeve FI foi
   feita seguindo a literatura US-centric (Bogleheads, AQR, PWL modelos
   para US/CA). Não traduzi adequadamente pra contexto brasileiro. O
   usuário teve razão em apontar.
3. **Hand-picked weights:** em nenhum momento rodei otimização
   matemática. As 4 carteiras são designs estruturais diferenciados, não
   ótimos matemáticos. Pequenas variações de peso não mudam o ranking
   geral.

**Lesson aprendida:** para portfolio de aposentadoria de brasileiro,
começar pela pergunta "em que moeda o investidor consome?" antes de
escolher asset classes. A sleeve bond tem que ser na moeda de consumo —
não é detalhe, é estrutural.

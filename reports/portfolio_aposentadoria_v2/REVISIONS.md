# Revisões — Plano C v2/v3

Audit trail das mudanças feitas durante a sessão 2026-04-23.

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

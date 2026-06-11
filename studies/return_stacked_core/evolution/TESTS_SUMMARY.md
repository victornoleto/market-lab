# TESTS_SUMMARY — todos os testes do evolution/ e a conclusão final

Data: 2026-06-11. Status: **research-only** (sem deploy, sem mudança de
capital/mandato; maintenance mode per `docs/investment-mandate.md` §1).
Documento-irmão do `REPORT.md` (veredito) — este aqui resume **todos os
testes executados**, em ordem, com números e resultado de cada um.
Reprodução: `uv run python studies/return_stacked_core/evolution/make_all.py`.

**Pergunta do estudo (goal do usuário):** existe portfolio/ajuste sobre o
RSC-US `35% GDE / 40% RSST / 25% ZROZ` (mensal) com **CAGR maior** e
**MDD ≤ 30%**, que seja *definitivamente* melhor?

**Benchmark (anchor):** CORE 35/40/25 mensal, janela
`2000-01-04..2026-05-21`, simulado, gross: **CAGR 12,52% / MDD −30,76% /
Sharpe 0,847**. Nota: o CORE atual **viola o próprio cap de 30%**.

---

## Definições dos testes (pré-registradas em PLAN.md antes de cada rodada)

**Screen:** C1 = MDD ≥ −30,00% (full window); C2' = CAGR > 12,52%;
C2 tier-1 "definitivo" = CAGR ≥ 13,27% (+0,75pp).

**Gauntlet (todos obrigatórios para FINALISTA):**

| Gate | Teste | Critério |
|---|---|---|
| G1 | Sensibilidade a data de início | Bate o CAGR do CORE-mensal em ≥7/8 starts bienais 2000-2014 |
| G2 | Vizinhança de pesos (platô, não pico) | Todos os vizinhos ±5pp: MDD ≥ −32% E média de CAGR > CORE `[testing_tuning, p.327-335]` |
| G3 | Stress de custo | +50bps/ano nos sleeves fora de {GDE,RSST,ZROZ} → ainda CAGR > CORE |
| G4 | Dominância rolling | Bate o CORE em ≥60% das janelas rolling de 5 anos |
| G5 | Janela longa 1988+ (diagnóstico, não bloqueante) | Proxy KMLM-only; flag se CAGR < CORE-1988 ou MDD piora >2pp |
| Platô de banda | (rodadas com banda) | Bandas 15% e 25% também passam C1∧C2' |

**Bateria profunda (Rodada 8, só para o candidato máximo):** B1 = bate o
CORE em ≥80% de 68 starts trimestrais 2000-2016; B2 = contínuo de bandas
10-30% (≥15/21 ok com run contígua ≥8); B3 = bootstrap conjunto de blocos
63d (n=1000, seed 42): spread de CAGR > 0 em ≥95% dos paths, in-cap ≥60%,
mediana de MDD ≤ 30%, MDD mais raso que o CORE em ≥80%
`[advances_fin_ml, p.222-223]`; B4 = gatilho checado semanalmente ainda
passa C1∧C2'.

---

## Os testes, em ordem de execução

### e00 — Gate do anchor ✅ PASS (pré-condição)
CORE 35/40/25 e 45/25/30 reproduzem os números canônicos com erro < 1e-6.
Standalones registrados: RSBT 6,40%/−28,5%, RSSB 9,16%/−47,8%,
QQQ 8,95%/−83,0%, GLD 11,10%/−44,6%, KMLM 4,31%/−32,0%.

### Rodadas 1-3 — Espaço estático completo (e01+e02): ❌ 0/413
14 menus, rebalanceamento mensal, passos de 5% (10% no menu de 8 ativos):

| Menus | Sleeves testados | Nós |
|---|---|---:|
| A-E (4 ativos) | CORE3 + RSBT / GLD / QQQ / KMLM / RSSB | 5×1.771 |
| F-G (5 ativos) | CORE3 + RSBT+GLD / RSBT+QQQ | 2×10.626 |
| H (5 ativos) | CORE3 + GLD+KMLM | 10.626 |
| I (8 ativos, 10%) | todos os 8 | 19.448 |
| J-O (carriers) | SSO/UPRO + GDE/GLD/KMLM/ZROZ/RSBT | 2×1.771 + 3×10.626 |

**Total: 95.601 trials (74.193 únicos).** Resultado:
- 413 nós passam o screen; **0 atingem o tier-1** (teto in-cap = 13,17%,
  +0,65pp, todos tilts GDE 55-60%).
- Gauntlet: G1 1/413, G2 190/413, G3 214/413, G4 1/413 → **interseção = 0**.
- Carriers SSO/UPRO **dominados**: os melhores nós in-cap dos menus J-O são
  os cantos com carrier = 0 (menus desempacotados K/M/O ≤ 11,3% CAGR).
- e04 (janela 1988+): **todos** os near-misses perdem do CORE-1988 (13,66%)
  por 0,4-1,4pp → o ganho do screen era a década do ouro 2000s, não edge.

### Rodada 4 — Frequência de calendário (e03, 110 configs): ❌ sorte de offset
5 estruturas × {mensal, trimestral×3 offsets, semestral×6, anual×12}:
o CAGR mínimo entre offsets **nunca** bate o mensal (regra pré-registrada);
o anual mantém o MDD do CORE in-cap em todos os offsets em 2000+ (pior
−29,79%) mas **não** em 1988+ (pior −31,81%). Veredito: knob de MDD, não
de CAGR.

### Rodada 4 — Bandas de tolerância (e05, 35 configs): ✅ mecanismo real
Rebalanceia só quando um sleeve desvia ±X% (relativo) do alvo
`[systematic_trading, p.137-148]`. Diferente do calendário, é **platô de
parâmetro**: 16/30 verdicts de melhora com vizinhos consistentes
(+0,2-0,7pp em 4 de 5 estruturas). Único mecanismo com lift genuíno
encontrado no estudo.

### Rodada 5 — Gauntlet das bandas (e06: 12 candidatos; e07: 231 nós × 3 bandas): ❌ 0 finalistas
- e06 (candidatos do e05): 0/12 passam tudo. **`45/25/30 b20` = 5/6 gates**
  (falha só G2); G5 = empate de 3bps com o CORE-1988.
- e07 (simplex completo): 6 passam o screen; só 2 têm vizinhança segura
  (40/25/35, 45/20/35 — mas G1 2/8 e 4/8); 45/25/30 e 40/30/30 passam
  G1/G4 mas falham G2. **Interseção vazia**: o aperto cap × vizinhança ×
  starts não tem solução no 3-ativos.
- Diagnóstico do G2: vizinhos com ZROZ ≤ 25% furam −32% sob banda
  (−33,0/−33,6%) → **ZROZ ≥ 30% é fronteira dura sob bandas**.

### Rodada 6 — Bandas em 4/5 ativos (e08: 122 screen; e09: 810 screen): ❌ G1∩G2 = 0
Simplexes {CORE3+RSBT}, {CORE3+KMLM}, {CORE3+RSBT+GLD}, {CORE3+GLD+KMLM}
× bandas {15/20/25} (~74k configs). O único nó G1≥7 com platô em TODOS os
espaços é o mesmo canto `45/25/30/0...` — sleeve defensivo adicional dilui
o tilt que vence os starts; os vizinhos que furam são nós 3-ativos,
invariantes à adição de sleeves de peso zero.

### Rodada 7 — Lastro puro IEF/CASHX (e10, 221 screen em ~57k configs): ❌ 0 finalistas
Lacuna real de cobertura (IEF/CASHX nunca tinham sido ativos de menu;
racional: vizinhos furam o cap no regime-2022 em que GDE e ZROZ caem
juntos; IEF/cash são lastro à prova de choque de juros `[risk_parity,
ch.5]`). Menus P/Q/R (+GLD), mensal E banda: G1∩G2 = 0; lastro mata o G1
no contato.

### Rodada 8 — Bateria profunda no candidato único (e11): ❌ 2/4 → FAIL TERMINAL
`45/25/30 + banda 20%` vs CORE-mensal:

| Teste | Resultado | Veredito |
|---|---|---|
| B1 starts densos | bate o CORE em **61/68 starts trimestrais (89,7%)** | ✅ PASS |
| B2 contínuo de bandas | CAGR > CORE em **todas** as 21 bandas (13,0-13,4%), mas o cap de 30% é raspado por 5-25bps nas bandas 12-18% → 13/21 < 15 | ❌ FAIL |
| B3 bootstrap de blocos 63d | spread > 0 em só **83,8%** (exigia 95%); vantagem de MDD = moeda (**50,4%**); in-cap 55,4% | ❌ FAIL (decisivo) |
| B4 cadência semanal | 13,08% / −29,87% | ✅ PASS |

Leitura do B3: **o edge da banda mora na estrutura de tendência multi-mês
da sequência histórica específica** — o bootstrap destrói a autocorrelação
>63d e o edge evapora. É colheita de persistência de tendência (a mesma
premissa dos sleeves RSST/KMLM), não propriedade distribucional.

---

## CONCLUSÃO

**FAIL honesto terminal. Nada é definitivamente melhor que o CORE 35/40/25
com MDD ≤ 30% neste universo de dados — e agora isso está provado, não
suposto.** Oito rodadas pré-registradas, ~74 mil portfolios estáticos
únicos, ~132 mil configs de banda/frequência/lastro e uma bateria profunda
convergiram para um único candidato máximo (`45/25/30 + banda 20%`, 5/6
gates + 2/4 na bateria), que morre por dois achados:

1. **Fragilidade de vizinhança** (G2): sob bandas, qualquer drift para
   ZROZ < 30% torna o portfolio cap-inseguro;
2. **Dependência de sequência** (B3): o ganho de +0,87pp é colheita da
   tendência multi-mês realizada nesta história específica.

**Por que o aperto não tem solução:** bater o CORE a partir dos starts de
2010/2014 exige tilt ouro/trend (a barra lá é 13,6-14,7%); todo tilt
desses ou fura o cap, ou tem vizinhos cap-frágeis, ou perde o regime
1988-2000. O `35/40/25` está onde está porque equilibra exatamente os
regimes que os tilts trocam entre si — **o platô já está precificado**
`[risk_parity, ch.5]`, `[advances_fin_ml, p.208-211]`.

**Resíduo acionável (documentado, não promovido):**
- Se o cap de 30% for restrição dura: o CORE atual o viola (−30,76% /
  −32,4% em 1988+). Os membros do platô in-cap nas duas janelas são
  **EW 33/33/33** (custa −0,45pp de CAGR) e **45/25/30** (CAGR misto).
- **EW 33/33/33 + banda 50%** = standout drawdown-first: 12,94%/−24,7%
  (2000+) e 14,24%/−24,7% (1988+) — mas perde os starts da década do ouro.
- **Bandas/anual** = knob de MDD grátis; **RSBT** = diversificador de
  implementação (tier CTAP); **regra ZROZ ≥ 30%** sob qualquer regime de
  bandas.
- Reabrir esta busca exige **fonte de retorno nova com 25+ anos de
  histórico** — mais combinações sobre estes mesmos dados é dredging
  `[advances_fin_ml, p.208-211]`, `[testing_tuning, p.327-335]`.

Nada foi promovido; mandate §1 inalterado.

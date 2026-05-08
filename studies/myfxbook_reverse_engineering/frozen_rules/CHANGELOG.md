# `frozen_rules/` — CHANGELOG

Este diretório é **read-only contract** por consenso adversarial (Etapa 0, `adversarial_chat/005-007`).
Mudanças só ocorrem por operação autorizada explicitamente (ex: 5R-0 Opus re-decode).

---

## v3 — 2026-05-03 (R1 Opus re-decode full 30-pool)

**Operação**: promoção R1 dos 30 systems re-decodificados para `frozen_rules/`.
Pool = 23 `DECODED` + 7 `PARTIAL_DECODED` do OVR antigo. Os 22 `NOT_DECODED`
continuam fora do R1, mas permanecem dentro do universo total de 52 systems do estudo.

**Modelo**: Opus 4.7 via `scripts/r1_redecode_loop.sh`; promoção determinística por
`scripts/promote_signal_to_frozen.py --all-r1-pool`.

**Backup pré-promoção**: `frozen_rules/_pre_v3_R1_2026-05-03T0000Z/` contendo os 15
frozen rules v2 anteriores + `README.md` + `CHANGELOG.md`.

**Fonte de auditoria R1**: `_diagnostics/R1_pre_manifest.json` + SHA atual dos
`systems/<id>/signal_rule.md` + validação strict. `status.tsv` existe, mas contém só
25/30 linhas; omite `10067081, 10192401, 10249298, 10251631, 10475089`.

**Validação pós-promoção**: `uv run python -m studies.myfxbook_reverse_engineering.scripts.validate_taxonomy --strict`
retornou `PASS=30 WARN=0 FAIL=0`. Todos os 30 `frozen_rules/<id>.md` foram confirmados
com chmod `444`. `README.md` permanece `444`; `CHANGELOG.md` permanece writable para log.

**Citação metodológica**: congelar labels antes de replicação reduz drift de hipótese e
data-mining bias; a etapa seguinte ainda precisa testar replicabilidade econômica, não
apenas decodabilidade condicional `[advances_fin_ml, p.208-211]`.

### Resumo families v3 (30)

| Família | Count |
|---|---:|
| UNCATEGORIZED | 18 |
| H1_MOMENTUM_GOLD | 6 |
| LATE_NY_BREAKOUT | 2 |
| SWING_TREND_MOMENTUM | 2 |
| NEWS_RELEASE_MOMENTUM | 1 |
| OVERLAP_NY_LONDON_RANGE | 1 |

### Reclassificações relevantes

Taxa de reclassificação entre systems com frozen v2 conhecido: **4/15 = 26.7%**.
Taxa na tabela completa pré-R1 signal -> pós-R1 frozen: **15/30 = 50.0%** (não dispara gate `>50%`).

| system | pre-R1 family | v3 family | Nota |
|---|---|---|---|
| 10192401 | FACTOR_SCALPING | UNCATEGORIZED | taxonomy_gap `BTC_NY_HOURS_BB_TREND` |
| 10249298 | UNCATEGORIZED | SWING_TREND_MOMENTUM | suporte adicional para provisória |
| 10251631 | FACTOR_SCALPING | UNCATEGORIZED | taxonomy_gap `ASIAN_PRELONDON_GOLD_MR_H4` |
| 10281851 | UNCATEGORIZED | H1_MOMENTUM_GOLD | suporte adicional para provisória |
| 10563761 | FACTOR_SCALPING | UNCATEGORIZED | taxonomy_gap `H1_MOMENTUM_BTC` |
| 10734338 | FACTOR_SCALPING | UNCATEGORIZED | taxonomy_gap `CRYPTO_INTRADAY_MOMENTUM` |
| 11207608 | OVERLAP_NY_LONDON_RANGE | H1_MOMENTUM_GOLD | v2 family mudou |
| 11355455 | FACTOR_SCALPING | H1_MOMENTUM_GOLD | suporte adicional para provisória |
| 1603276 | LONDON_OPEN_MOMENTUM | UNCATEGORIZED | taxonomy_gap `INTRADAY_TREND_SCALP` |
| 1612420 | OVERLAP_NY_LONDON_RANGE | NEWS_RELEASE_MOMENTUM | família provisória ainda n=1 |
| 2421356 | UNCATEGORIZED | H1_MOMENTUM_GOLD | v2 family mudou |
| 8577442 | OVERLAP_NY_LONDON_RANGE | SWING_TREND_MOMENTUM | suporte adicional para provisória |
| 8647517 | UNCATEGORIZED | H1_MOMENTUM_GOLD | v2 family mudou |
| 9830783 | OVERLAP_NY_LONDON_RANGE | UNCATEGORIZED | reason_code `hold_mismatch` |
| 9841939 | FACTOR_SCALPING | UNCATEGORIZED | reason_code `degenerate` |

### Pause gates pós-v3

| Gate | Resultado |
|---|---|
| reclass >50% | PASS: 15/30 = 50.0%, não maior que 50%; frozen-v2-known = 4/15 |
| candidate_new_family n>=2 | PASS: nenhum candidate_new_family repetiu |
| label fora enum | PASS: 0 |
| UNCAT sem reason_code | PASS: 0 |
| taxonomy_gap sem candidate_new_family | PASS: 0 |
| família provisória ainda n=1 | PAUSE: `NEWS_RELEASE_MOMENTUM` permanece n=1 |
| muitos needs_m1_review | PAUSE: 13/30 marcados |
| qualquer falha strict | PASS: 0 |

Decisão operacional: promoção v3 concluída, mas **não iniciar Wave C/D nem 5R-1/5R-2 sem aprovação explícita**.

### SHA-256 pré-v3 (frozen v2 conhecidos, 15)

```
80fde478eeb1c17dc3e1299ff31ea4f43fd316f7f6c708b5a75a0397f77035ac  10062918.md
dec3e214c6466a4402743cdd25bb4b0a9771a50fda1e8d8aa60fddcba8a2fefb  10224499.md
a14e7a4acebd7b946c84b7c2f51157f5079fcfba404f22c53bcf7fc92b10dee0  10281851.md
bf720a4557b1a3c36490f198b0b5fdd0d4a069cc2ede39d9da86aa0da6420801  11155858.md
d138baa1e83795dcbe7a133ebbe16ed05b5f90a1a1e1e133a3fa2e6d1832eec8  11171596.md
2ec85e3b8f704df6310c645cddbc75f30d3cfa774637183092c5c6e37a0d723e  11206045.md
ae3564025256e482c7e78cdf15bf7fce239a0ba61fb405ff76caa1d2d2717fb9  11207608.md
f35ff95a81a063ea3de751de29db3adadf1dfcfdae18e886757ed6d29b5e64f0  11628637.md
80cc89024d645536e8fe4af17f800d44351d689b1854377c0dccca00498c93b5  1407880.md
79d1bd694d1f5031a2643defa675542f077f1aaadfa2714642c0ff127d6518fc  2373850.md
9f312d87a315eef7f4e81fe1eba397ca5e1fce272cf13bdf22e7e7a915aa8b7b  2421356.md
b4bdd9c1536a6c8d3187cef72c969f7f9bcea4e5e6f0c690920f0de3bd1f5554  6541963.md
10fba3e44c4cde63146beec93e375fd473b1f7d48528d6928de3878e2e76285d  8647517.md
efe1a732f2329a862631a7e7c3cee81753198a7fb77f0b43d9d35d3b375a79fc  9375654.md
d6a2dc17c335ad413e14d0abbab84906df7bf9a7266a0e0ec8f154ea0a6b8c85  9912554.md
```

### SHA-256 pós-v3 (30)

```
42703ae0d30db4dd1415d241509052c673ffff0cd0345cc3fcbc0ba7fae2f29b  10062918.md
417f556ae2792013090728cbeca8cd24e01d83d932e9dcbfa9aa5f9149649255  10067081.md
b0865c7a711dbefe9ce3225e29677d4fa14adcfbccb187ebd79cb5f6573a3668  10192401.md
8c67aa6645d48aa145b7afc3ab3c3a8e34cc9e4a7aa8228068fd1fd1e1d68e0b  10224499.md
7b20add59cbd6898b09a304e01b2d6a363435fa7f2c673bbad983d29991595bb  10249298.md
0b05da4a4644ec1a5a2942e53f11804c178ce5de40291cdcf48754481cde27d3  10251631.md
2300a8bf5a8e6b955f5d292dc6fd04074f96598060fc053563a12944615eb9d7  10281851.md
ed0f971e186205a900152a6a46106a7933449e66bac3598e1df053490b4b8616  10475089.md
7a7bb858e27683ce0b2c992abeb6a98f02b3e3d520a3b2389e3918338e58ba7c  10563761.md
db9c8a5f5310e3dedc8aae000c46ea8472e4d1639bf5fc1ced19da319e6cef57  10734338.md
78aa2ec5b715362bce0f6939f3c4d57d05ac01cb7d83ee4c7871bc5bcbe8aa58  11155858.md
14f058f41dcce05ddc69f8dd4d54f7ab11fa5c456db715b554ef1457592d0f6c  11171596.md
3ac25244cc11e8e21ca28ff9504ddd3afd90ca4cd38dac16feeab8c6d226219c  11206045.md
643971c21df6b46e49be5f93a88b2bac26cc7515521969ad23865f43d60f2e04  11207608.md
f9ec7bfd736186d8e3ec072c5d7dfd24083a85ee2b2b8eb2d5f103ca5e25d396  11355455.md
ea7e0005ffb9b6d7ca29a525ef5f313f5eb3d84785bae55a4f7d8e37705130da  1152318.md
000d2fd3665720d1fa6b30212e5e4db94c63f9facb2102158adb62c8724f2daa  11628637.md
19df4f6b3acf8772a9d98e998d16ab2f3fbeb7d4ee29b2537ec9ae8be7046f2f  1407880.md
4fc3dc067d5c838b45b3ec61090eae344b57090f1c0af492cb729803c9768967  1603276.md
934b5761b178b0ec7c1d20e39e03a5be0f5991dbd6fcd61527e6b289fdbf6c58  1612420.md
dfa52ade49d91914ab955b06b98f69b598173c93ff183e62f6da7468557e1b41  2373850.md
92ef3f4e3fa70ac108bfc43facb048d16b6e762f39a2d8f86c91f46362f846f8  2421356.md
07c56760ba9a8242000e6c8e457fca9da5abe4794140c90de9f47c44bbb1c1d1  6541963.md
379d3ab52c93cb761092eb8387b63d81e8c78aaf822d80dcd7d9b7ce4c29db66  8577442.md
bc37991c17a9e9e5f449653832da2df8ffae2db9a0ee05729ac0a081b4008ba5  8647517.md
ff82fc2ba5e89db832f813e55618c153e98e710210801be9a0d8e6dc09e9d734  9375654.md
4dc04f947d7e1c33466b886dfee54709c65a2a4fea9ef42cdfbab34dfd6ec790  9830783.md
b954b734492d87f8b3a232150630e37bce5e120f8d6b6d87626b9050fdfb2746  9841939.md
1a0edd56cf66d7cf7a5acb5a7bc180beb91019e38845cf48684c23123eb99e0a  9843883.md
6d93086d177b1b225d00c4b42996c6eab99bcdb39a62c416038ba36c7dec856d  9912554.md
```

## v2 — 2026-05-02 (Phase 5R-0 Opus re-decode batch)

**Operação**: re-decode Stage 2 com Opus 4.7 em 15 systems críticos. Motivos em
`_diagnostics/opus_redecode_targets.md`.

**Modelo**: `claude-opus-4-7` (override de `model: sonnet` default do agent decoder).

**Backup pré-Opus**: `_backups/signal_rule_pre_opus_2026-05-02/<id>.md` (15 arquivos)
+ `frozen_rules/_pre_opus_2026-05-02/<id>.md` (12 arquivos correspondentes ao state v1).

**Custo**: ~$5-8 estimado, 3 waves × 5 agents paralelos.

### Mudanças por system

| system | Sonnet (v1) | Opus (v2) | Δ |
|---|---|---|---|
| 10224499 | LATE_NY_BREAKOUT 0.68 | LATE_NY_BREAKOUT 0.72 | conf↑, regra confirmada |
| 1407880 | LATE_NY_BREAKOUT 0.72 | LATE_NY_BREAKOUT 0.62 | conf↓ (anti-pattern compliance: CV<0.65) |
| 11171596 | NY_SESSION_REVERSAL 0.62 | **UNCATEGORIZED** 0.35 | always-Sell EUR/USDCHF, label degenerate, p95=561h |
| 11155858 | FACTOR_SCALPING 0.38 | **UNCATEGORIZED** 0.30 | always-Buy EURGBP, tree degenerate = baseline |
| 9912554 | OVERLAP_NY_LONDON_RANGE 0.57 | **UNCATEGORIZED** 0.32 | n=103 underpowered, no rule survives MCP |
| 11206045 | LATE_NY_BREAKOUT 0.50 | **UNCATEGORIZED** 0.40 | Tokyo Open momentum em GBPJPY (não NY breakout) |
| 9375654 | NY_SESSION_REVERSAL 0.58 | **OVERLAP_NY_LONDON_RANGE** 0.55 | direction = trend-continuation, não reversal |
| 8647517 | FACTOR_SCALPING 0.62 | **UNCATEGORIZED** 0.50 | hold NaN não confirma <30min |
| 2421356 | FACTOR_SCALPING 0.72 | **UNCATEGORIZED** 0.40 | 0.6 trades/day + H1-features (não scalping) |
| 10281851 | OVERLAP_NY_LONDON_RANGE 0.62 | **UNCATEGORIZED** 0.45 | trend-continuation, não range-fade |
| 11207608 | FACTOR_SCALPING 0.72 | **OVERLAP_NY_LONDON_RANGE** 0.55 | reclassificado |
| 11628637 | FACTOR_SCALPING 0.62 | **UNCATEGORIZED** 0.45 | BTCUSD 24/7 não fit FX session taxonomy |
| 6541963 | FACTOR_SCALPING 0.62 | **`H1_MOMENTUM_GOLD`** 0.55 | ad-hoc label fora taxonomia (ver §nota abaixo) |
| 2373850 | UNCATEGORIZED 0.44 | UNCATEGORIZED 0.35 | mantido, rationale tightened |
| 10062918 | UNCATEGORIZED 0.52 | UNCATEGORIZED 0.45 | mantido, mecanismo identificado (swing MR EMA-fade) |

**Resumo families**:

| Família | Sonnet (v1) | Opus (v2) |
|---|---:|---:|
| LATE_NY_BREAKOUT | 3 (1407880, 10224499, 11206045) | **2** (1407880, 10224499) |
| NY_SESSION_REVERSAL | 2 (11171596, 9375654) | **0** (família vazia — finding) |
| OVERLAP_NY_LONDON_RANGE | 2 (10281851, 9912554) | **2** (9375654, 11207608) |
| FACTOR_SCALPING | 6 (Gold/Bitcoin cohort) | **0** (todos reclassificados) |
| `H1_MOMENTUM_GOLD` (ad-hoc) | 0 | 1 (6541963) |
| UNCATEGORIZED | 2 (2373850, 10062918) | **10** |

### Findings de nível-estudo (Wave 1+2+3)

1. **6R par primário INTACTO**: `1407880` (OLD) ↔ `10224499` (NEW) ambos LATE_NY_BREAKOUT
   por mérito próprio. Wave 1 retirou `11206045` (Tokyo Open, não NY) → família mais limpa.

2. **6R par diagnóstico DUPLAMENTE UNCAT**: `2373850` (OLD) ↔ `11171596` (NEW) ambos UNCATEGORIZED
   após re-decode. Par diagnóstico vira "negative case study" sobre vendor library — não
   diagnostic-de-coisa-nenhuma.

3. **NY_SESSION_REVERSAL VAZIA**: vendor library HappyForex não tem reversal genuíno após
   sanity-check. Sonnet mistakenly classificava por timing (12-16 UTC) sem checar sign
   da regra. Finding sobre o vendor: stack skewed momentum/breakout exclusivamente.

4. **FACTOR_SCALPING VAZIA**: 6/6 systems classificados FACTOR_SCALPING falharam Opus check.
   Razões: hold NaN não comprova <30min (Stage 1 extractor bug — sistêmico), regras dominadas
   por features H1/H4 (não sub-30min), ou tree degenerate (always-Buy clone do baseline).

5. **Hold extraction bug sistêmico em Stage 1**: 5+ systems reportam `hold p50/p95/max = NaN`.
   Bug em `shared/eda.py` ou `decoder_features.py`. Stage 3 / 5R precisa reconstruir hold
   dos raw timestamps em `data/trades/<id>/trades.parquet:duration_sec`.

6. **Taxonomia v2 considerável** (defer absoluto até 7R): sinais fortes para introduzir
   `TOKYO_OPEN_MOMENTUM` (11206045), `H1_MOMENTUM_GOLD` (6541963 + 8647517 + 2421356 podem
   formar cluster), `SWING_MR_MA_FADE` (10062918), `CRYPTO_MOMENTUM_CONTINUATION` (11628637).
   Não introduzir agora — risco de drift de scope.

### Nota sobre `H1_MOMENTUM_GOLD` (6541963)

Agent Opus violou constraint "permaneça dentro da taxonomia fechada" e criou label ad-hoc.
**Decisão**: aceitar como está no v2 (não force overwrite para UNCATEGORIZED) porque:

1. Score formula 5R-3 é **ortogonal** ao label de família — não há gate por family.
2. Ranking 5R-4 mostra coluna `family` separada; reader vê o label ad-hoc com flag.
3. Forçar UNCATEGORIZED perderia rationale que pode ser útil em 7R taxonomia v2.

`risk_flag: ad_hoc_taxonomy_label` é registrado no signal_rule.md.

Pós-batch 5R, 7R revisita: ou (a) introduz `H1_MOMENTUM_*` na taxonomia oficial,
ou (b) força UNCATEGORIZED se não houver cluster ≥3 com mesmo padrão.

### Read-only restoration

Todos os 15 arquivos foram `chmod a-w` após cópia (re-freeze). Modificação subsequente
sem nova entrada nesta CHANGELOG = violação do contrato. Estado atual confirmado por
`stat -c '%a'` na seção de auditoria abaixo.

---

## Auditoria criptográfica (5R-1-hardening, 2026-05-02)

Adicionada em resposta ao parecer adversarial cruzado Opus 4.7 + GPT-5.5 que apontou
"read-only-on-trust" como insuficiente para sustentar o contrato da Etapa 0
(`adversarial_chat/005-007`). Citação: Pardo `[testing_tuning]` — reproducibility como
pré-requisito de inferência válida.

### chmod operation log

| Evento | Timestamp | Comando | Justificativa |
|---|---|---|---|
| **freeze inicial v1** | (Phase 0, manual) | `chmod 444 frozen_rules/*.md` | Etapa 0 contrato read-only |
| **unfreeze para v2** | 2026-05-02 ~15:21 BRT | `chmod u+w frozen_rules/*.md` | Phase 5R-0 Opus re-decode batch (15 systems) — operação autorizada explícitamente em `_diagnostics/opus_redecode_targets.md` |
| **re-freeze v2** | 2026-05-02 15:22:23 UTC (epoch 1777746143, registrado em `_diagnostics/freeze_timestamp.txt`) | `chmod a-w frozen_rules/*.md` | Restauração do contrato pós-batch |

**Estado atual confirmado**: `stat -c '%a' frozen_rules/*.md` reporta `444` em todos os 15
frozen_rules e `444` em README.md. CHANGELOG.md em `664` (writable, esperado — é o log).

### SHA-256 v1 (estado pré-Opus, capturado em `_pre_opus_2026-05-02/`)

```
73149623c1f8b48cbf96982ed306859bb93232cc469201d826fd860ceb32f55a  10224499.md
efb55edf1c044acb86db8005f58ea4737c49cd20eaf11595d539daf0e5bb1c5a  10281851.md
ec9b0b73a873dcbfd6b5e19dfcf2a7836741dcd0e0e9c0b27d7b7b43e8e3cc71  11155858.md
1e186f199c3e8136c50861326dd7b2ad014bc2edb66561af531f50afd6f1f10d  11171596.md
d42255a23a7b6797a22420d7339612c2c00cea14559c7fef69b6baaf7c5b78ef  11207608.md
ebe67734cf8988991c41383b9401ec580f4f0d66e2bce2c479c05eace1edca71  11628637.md
04d797bc8ad834074c569b44c1b717936f8f7dcb639797e2d0f74ed896c910d2  1407880.md
48bc4a974680bf8f96887f80161d6b1134d5323f7531f0f9ddda204c99efd1bd  2373850.md
c5d11d245ef33ffe3350ad3ef4b927c4715a5e5c9c2722e7c8d232cedeeabefe  2421356.md
64712027b7e31891addc2184935c6e8ebce61a963ec63b8fccbda2ce00096330  8647517.md
faa4869f573a8c09987f831ec181f71c6222eaa4eef0bc6f01b520d5c120c2f4  9375654.md
c8d4fafccc6502b39855b8408303660368c1afb5e9b9c1f36d454fdf1eae0f3a  9912554.md
```

12 arquivos. Reprodutível por `sha256sum frozen_rules/_pre_opus_2026-05-02/*.md`.

### SHA-256 v2 (estado pós-Opus, atual em `frozen_rules/`)

```
80fde478eeb1c17dc3e1299ff31ea4f43fd316f7f6c708b5a75a0397f77035ac  10062918.md  [NEW v2 — sem v1]
dec3e214c6466a4402743cdd25bb4b0a9771a50fda1e8d8aa60fddcba8a2fefb  10224499.md
a14e7a4acebd7b946c84b7c2f51157f5079fcfba404f22c53bcf7fc92b10dee0  10281851.md
bf720a4557b1a3c36490f198b0b5fdd0d4a069cc2ede39d9da86aa0da6420801  11155858.md
d138baa1e83795dcbe7a133ebbe16ed05b5f90a1a1e1e133a3fa2e6d1832eec8  11171596.md
2ec85e3b8f704df6310c645cddbc75f30d3cfa774637183092c5c6e37a0d723e  11206045.md  [NEW v2 — sem v1]
ae3564025256e482c7e78cdf15bf7fce239a0ba61fb405ff76caa1d2d2717fb9  11207608.md
f35ff95a81a063ea3de751de29db3adadf1dfcfdae18e886757ed6d29b5e64f0  11628637.md
80cc89024d645536e8fe4af17f800d44351d689b1854377c0dccca00498c93b5  1407880.md
79d1bd694d1f5031a2643defa675542f077f1aaadfa2714642c0ff127d6518fc  2373850.md
9f312d87a315eef7f4e81fe1eba397ca5e1fce272cf13bdf22e7e7a915aa8b7b  2421356.md
b4bdd9c1536a6c8d3187cef72c969f7f9bcea4e5e6f0c690920f0de3bd1f5554  6541963.md   [NEW v2 — sem v1]
10fba3e44c4cde63146beec93e375fd473b1f7d48528d6928de3878e2e76285d  8647517.md
efe1a732f2329a862631a7e7c3cee81753198a7fb77f0b43d9d35d3b375a79fc  9375654.md
d6a2dc17c335ad413e14d0abbab84906df7bf9a7266a0e0ec8f154ea0a6b8c85  9912554.md
```

15 arquivos. Reprodutível por `sha256sum frozen_rules/*.md | grep -v -E '(CHANGELOG|README)'`.

3 arquivos são **adições novas em v2 sem contraparte v1**: `10062918.md, 11206045.md, 6541963.md`.
Esses entraram no Pool B (Opus re-decode targets), gerados de zero pelo Opus — não há
diff a fazer, só verificar contra `signal_rule.md` correspondente em `systems/<id>/decoder/`.

### Diff command (verificação determinística v1↔v2)

Para auditar mudança em qualquer dos 12 systems com par v1/v2:

```bash
# diff completo de um system
diff frozen_rules/_pre_opus_2026-05-02/10224499.md frozen_rules/10224499.md

# audit batch (todos 12 com v1)
for id in 10224499 10281851 11155858 11171596 11207608 11628637 1407880 2373850 2421356 8647517 9375654 9912554; do
  echo "=== $id ==="
  diff -q frozen_rules/_pre_opus_2026-05-02/$id.md frozen_rules/$id.md
done

# verificar SHAs contra esta CHANGELOG (ambos lados)
sha256sum frozen_rules/*.md frozen_rules/_pre_opus_2026-05-02/*.md
```

### Reversibilidade

Reversão determinística do v2 → v1 é possível **apenas para os 12 systems com par**:

```bash
chmod u+w frozen_rules/*.md
cp frozen_rules/_pre_opus_2026-05-02/<id>.md frozen_rules/<id>.md
chmod a-w frozen_rules/<id>.md
# registrar operação aqui no CHANGELOG.md
```

Os 3 adicionados em v2 (`10062918, 11206045, 6541963`) não revertem porque não existem
em v1; reversão deles seria exclusão (`rm`), o que requer entrada explícita aqui.

---

## v1 — 2026-05-02 (Phase 0 inicial)

12 frozen_rules iniciais (Sonnet) gerados durante absorção 5R-0 inicial:

`10224499, 11171596, 11155858, 8647517, 2421356, 10281851, 9912554, 11207608, 11628637, 9375654, 1407880, 2373850`

Backup deste estado em `_pre_opus_2026-05-02/`. SHAs no bloco "SHA-256 v1" acima.

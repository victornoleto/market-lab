# spy_beater_hunt iter 024 — G3 LRS-gated HFEA classical (66/100, bars 3/3 PASS)

## O que foi feito

Testamos a 8ª combinação arquitetural do hunt: o gate Gayed 200d-SMA composto com a barra alavancada HFEA (UPRO 3× + TMF 3× LTT). Cinco configurações em torno do canônico Bogleheads 55/45 + variantes com KMLM crisis-alpha + variantes de off-state defensivo.

A B1 estática (sem gate) tinha falhado a barra de MDD em iter 008 com drawdown ~67% (catastrófico, 2008 + 2022 destroem o leg de duration alavancada). A hipótese era simples: o gate do Gayed escapa o regime de bear AND skip-2022 — preserva o upside da HFEA na bull e não passa por TMF -70% de 2022.

## Resultado

**Tier PROMISING 66/100, bars 3/3 PASS, winner_met = True.** Selecionado `g3_gated_hfea_4040` (40% UPRO + 40% TMF + 20% KMLM no on-regime, 100% IEF no off): CAGR 15.79%, MDD 44.71%, Sharpe 0.895. **Todas as 5 configs passam as 3 barras** — quarto sweep 100% bar-pass na história do hunt (depois de iter 019/020/021 todos meta-ensemble).

**Cross-product hybrid family ceiling sobe de 65 para 66 via G3.** Ranking dentro da família agora monotônico com leverage do sleeve: G3 (300%) > E1 (3× LETF TQQQ) > G2 (2.25× LETF) > G1 (1.41% stack). É o **oposto** do ranking static-barbell (B5 200% > B7 150%) — gate composition INVERTE a direção do leverage-axis.

## Achado mais importante (KILL #94)

KMLM 15% no GATED HFEA 300% lifta Sharpe +0.055 e baixa MDD −7.85pp — **diretamente oposto** do KILL #27 que mostrava KMLM como Sharpe-flat-to-negative no STATIC HFEA 300%. Mecanismo proposto: o gate efetivamente reduz o leverage médio temporal do portfolio. Em períodos off-regime (~15% do tempo), o portfolio fica em IEF a 1×, então o tempo-médio efetivo do leverage cai de 300% pra ~225%. KMLM volta a ser eficaz como crisis-alpha porque "vê" um backbone menos alavancado.

Isso conecta com KILL #79/#85 (mapa de eficácia do KMLM por leverage do backbone): static 300% = 0 lift, static 200% = +0.04-0.08, static 150% = +0.13. **Gated 300% (NEW) = +0.055** se encaixa na progressão como se fosse static-225%. Gate composition tem dois efeitos ortogonais: bear-avoidance + redução de leverage efetivo.

## Por que não bate o teto de 71

Score breakdown vs iter-019 (71→66, −5pts): CAGR +2pts (gate ainda lifta CAGR sobre o blend meta-ensemble), MDD −6pts (anchor saturada — 44.71% no anchor [0.7, 0.15] vale 9/20 vs 28.50% do meta valendo 15/20), Sharpe −1pt. **4ª classe de rubric saturation documentada** (saturação no eixo MDD para ranges 40-45%) — ganhos de Sharpe e CAGR não compensam o déficit no eixo MDD.

closest-to-winner UNCHANGED — iter-019 H2 retido em 71.

## Recomendação

8 axes mapeados, ceiling DEFINITIVO em 71. Mandate §1 mantém 100% Plano C. Recomendação para iter 025+: declarar hunt EFFECTIVELY-CLOSED ou pivotar para review case do mandate §7 (revisão da rubrica anchored em CAGR — dado que 8 iters já mostram configs honestas com perfis de Sharpe+MDD competitivos mas penalizadas pela saturação dos anchors).

Citações: [leverage_for_the_long_run, ch.3-4, p.40-60] Gayed; HFEA Bogleheads 2019; [ilmanen_expected_returns, ch.19] MF crisis-alpha; [advances_fin_ml, p.31-34, p.208-211, p.222-223].

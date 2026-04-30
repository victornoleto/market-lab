# spy_beater_hunt iter 001: bate SPY em CAGR mas explode em drawdown

A vertente nova `studies/spy_beater_hunt/` saiu do bootstrap e rodou a
primeira hipótese: **A1 Gayed LRS UPRO + 200d SMA gate**. É o approach
"clássico" da literatura de leveraged ETFs: fica 100% UPRO (3× SPY) quando
o SPY está acima da média móvel de 200 dias, sai pra IEF (Treasury 7-10y)
ou cash quando está abaixo. Citação direta:
`[leverage_for_the_long_run, ch.3-4, p.40-60]` (Gayed).

Quatro variações testadas em 3 datasets (40 anos, 17 anos, 16 anos):
1. `a1_pure_lrs` — 100% UPRO ↔ 100% IEF
2. `a1_lrs_cash` — 100% UPRO ↔ 100% CASHX (T-bill)
3. `a1_lrs_split` — 50% UPRO + 50% SSO ↔ 100% IEF (alavancagem média 2.5×)
4. `a1_lrs_kmlm_off` — 100% UPRO ↔ 50% IEF + 50% KMLM (crisis-alpha quando off)

**Veredito**: `PROMISING 67/100`. **Não é WINNER**, mas o motivo é
interessante.

## O que deu certo

A barra de CAGR (≥ 13.80% mean — média de SPY nas 3 janelas) **passou de
sobra** em todas as 4 configs:
- `a1_pure_lrs`: CAGR mean 21.04% (+7.24pp acima da barra)
- `a1_lrs_split`: CAGR mean 19.01% (+5.21pp)

A condição KILL #6 que tínhamos pré-comitado ("se nem a config mais
agressiva atingir CAGR ≥ 13.80%, fechar tier inteiro") **não disparou** —
sobra CAGR. O direction Gayed LRS é estruturalmente CAGR-rico no nosso
universo testado.

A barra de gates também passou (2 de 3 datasets atingiram o threshold:
6/7 em lh_56y, 6/7 em vt_real, 5/7 em ndx_real). DSR worst p = 0.026
(estatisticamente significativo), bootstrap CI > 0 nos 3 datasets,
robustez 100% positiva nas 36 janelas rolling de 5 anos.

## O que deu errado: drawdown estrutural

A barra de MDD ≤ 40.85% (também SPY-mean) **falhou em todas as 4 configs**.
O selecionado `a1_lrs_split` teve mean MDD 50.57% — quase 10pp acima do
ceiling. O pure UPRO ficou em 58.22%.

Olhando os walk-forward windows individuais (G3 — within-window max MDD):
todos os 8 windows × 3 datasets mostram drawdown 0.40-0.55. Não é um
window específico que machucou: é um padrão estrutural.

**O culpado**: a média de 200 dias é lenta demais pra reagir a crashes.
Pelo modelo, em 1987 (Black Monday), 2020 (COVID) e 2022 (inflação),
quando o gate finalmente flipou OFF, o UPRO já tinha levado o grosso da
porrada. A literatura do Gayed reportava MDD 25-35% — mas no nosso
synth/dataset com 1986+ ativo e KMLM splice, o número real é 50%+.

## Por que isso importa

A tese da vertente era: "talvez exista uma estratégia que bate SPY em
CAGR **e** em MDD". Iter 001 mostra que com Gayed LRS clássico, conseguimos
o CAGR mas **não** o MDD. Cumprir as duas barras simultaneamente é mais
duro do que parecia.

Isso confirma a calibração honesta no `README.md` da vertente: "this hunt
may fail". Iter 001 é uma falha "valiosa" — não é WINNER, mas a 2/3 das
barras passou (CAGR + gates). Tier PROMISING continua como knowledge
positivo.

## Próximos passos

Per o ranking no `PROMISING_DIRECTIONS.md`, iter 002 é **B1 HFEA classical**
(55% UPRO + 45% TMF, leveraged barbell). É outra hipótese Tier 1 com
fundamentação literatura (Bogleheads 2019). A pergunta que ela testa:
será que diversificar a alavancagem entre stocks **e** Treasuries (TMF) em
vez de só stocks reduz o MDD sem matar CAGR? Pré-2022 historicamente
sim. Em 2022 (60/40 worst year ever) catastrófico.

O HFEA precisava de TMFSIM (3× LTT). Esse synth já foi construído nessa
sessão (`studies/long_term_portfolio/synths.py::tmf_synth_returns`) com
TDD verde, então iter 002 já tem tudo pra rodar.

## Status do mandate

Continua válido o mandate §1 MAINTENANCE MODE — F1+SPLIT (mean CAGR 10.76%,
MDD 16.76%) segue como deploy fallback. Iter 001 mostrou que existe pelo
menos uma direção (Gayed LRS) que bate F1 em CAGR (21% vs 10.76%) mas
piora muito em MDD (50% vs 16.76%) — não substitui F1+SPLIT. Pra superá-lo
precisamos de uma estratégia que bata F1 em CAGR **e** seja competitiva
em MDD. Iter 002 (HFEA) é o próximo teste dessa hipótese.

---

**Glossário**:
- **CAGR**: retorno anualizado composto (Compound Annual Growth Rate)
- **MDD**: máximo drawdown — pior queda do pico ao vale na curva de equity
- **LRS**: Leveraged Rotation Strategy (Gayed): rotaciona entre LETF e
  defensivo via gate de regime
- **HFEA**: Hedgefundie's Excellent Adventure — barbell 55% 3×SPY + 45% 3×LTT
- **TMF**: 3× LTT (Treasuries de 20+ anos), versão sintética nesse loop

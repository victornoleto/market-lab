# Numerical Recipes in C: The Art of Scientific Computing, Second Edition

## Metadata
- **Autor:** William H. Press; Saul A. Teukolsky; William T. Vetterling; Brian P. Flannery [p.i]
- **Ano:** 1992 (2nd ed.; reprinted with corrections through 1997) [p.ii]
- **Editora:** Cambridge University Press [p.ii]
- **Páginas:** ~1000 main text (printed), book pp. i–xxii + 1–965 + appendices [p.ii, contents]
- **ISBN:** 0-521-43108-5 [p.ii]
- **Foco principal:** Catálogo prescritivo de algoritmos numéricos estáveis em C, com código pronto; cobre álgebra linear, random numbers, root finding, minimização, FFT, estatística, modelagem de dados, ODE/PDE, e "less numerical" (hashing, CRC, compressão).

## 1. Tese Central

Numerical Recipes é uma obra **prescritiva**: os autores declaram explicitamente que escolheram editorializar — "telling you what you should and shouldn’t do" — reagindo à tendência de textos tradicionais listarem todo método já inventado sem julgamento [p.1]. A tese operacional é que, em numerical computing, **a escolha do algoritmo domina a escolha do hardware**: "clever minimization of truncation error is practically the entire content of the field of numerical analysis" [p.30]. Correspondentemente, todo resultado numérico deve ser julgado por três erros distintos e não-intercambiáveis: **roundoff error** (intrínseco ao hardware), **truncation error** (intrínseco ao algoritmo) e **instability** (amplificação de roundoff ao longo de iterações) [p.28-30].

Para o projeto ai-trade, a tese relevante é a segunda, enunciada no §15.0: um fit só é "genuinely useful" se fornece (i) parâmetros, (ii) estimativas de erro nos parâmetros, e (iii) uma medida estatística de goodness-of-fit. "Chi-by-eye" (julgar fit olhando o gráfico) é explicitamente condenado: "its practitioners get what they deserve" [p.657].

## 2. Conceitos-Chave

- **Machine accuracy ($\epsilon_m$)** — menor float que, somado a 1.0, produz resultado diferente de 1.0. Para B=2, 32-bit, $\epsilon_m \approx 3 \times 10^{-8}$ [p.28]. É a **fractional** accuracy, distinta do menor float representável [p.29].
- **Roundoff error** — erro fracionário introduzido por cada operação de ponto flutuante. Se $N$ operações, erro acumulado pode ser $\sqrt{N}\epsilon_m$ (random walk) ou, se viés, até $N\epsilon_m$ [p.29].
- **Truncation error** — discrepância entre resposta verdadeira e resposta de um cálculo com número finito de termos/pontos; sob controle do programador [p.30].
- **Stability** — propriedade de um algoritmo de não amplificar roundoff errors ao longo de iterações. Exemplo instável: recursão $\phi^{n+1} = \phi^{n-1} - \phi^n$ para Golden Mean dá respostas completamente erradas por volta de $n=16$ em máquina 32-bit [p.31].
- **Condition number de uma matriz** — razão entre o maior e o menor singular value $w_j$. Matriz singular = condition number infinito; ill-conditioned se recíproco aproxima machine precision ($<10^{-6}$ single, $<10^{-12}$ double) [p.61].
- **Singular Value Decomposition (SVD)** — fatoração $A = U \cdot W \cdot V^T$ onde $U$ é $M \times N$ coluna-ortogonal, $W$ diagonal com singular values $\geq 0$, $V^T$ ortogonal $N\times N$. Diagnostica e resolve sistemas singulares/próximos [p.59-60].
- **Maximum likelihood estimator** — escolha de parâmetros que maximiza a probabilidade dos dados observados dado o modelo [p.658].
- **Chi-square ($\chi^2$) merit function** — para medidas com erro Gaussiano iid, minimizar $\chi^2$ é equivalente a maximum likelihood [p.659-660].
- **Goodness-of-fit probability Q** — $Q = \text{gammq}(0.5\nu, 0.5\chi^2)$, com $\nu = N-M$ graus de liberdade. Q < 0.001 sugere modelo errado ou erros subestimados [p.660-661].
- **Bootstrap method** — dado dataset iid de N pontos, gera datasets sintéticos fazendo sampling *with replacement* de tamanho N; roughly 37% (1/e) dos pontos são duplicatas [p.691-692].
- **Quasi-random (sub-random) sequences** — sequências como Halton/Sobol que preenchem n-space mais uniformemente que pontos iid, dando erro $\sim N^{-1}$ em vez de $N^{-1/2}$ [p.309-310].
- **Minimal Standard generator (Park & Miller)** — gerador de congruência linear $I_{j+1} = a I_j \mod m$ com $a=16807$, $m=2^{31}-1$. Padrão mínimo contra o qual outros devem ser julgados [p.278-279].
- **Linear prediction (LP)** — extrapolação de série usando coeficientes $d_j$ ajustados para prever cada ponto como combinação linear dos M anteriores [ch.13.6, p.561+].

## 3. Fórmulas / Equações

**Floating-point representation** [p.28, eq. 1.3.1]

$$s \times M \times B^{e-E}$$

onde $s$ = bit de sinal, $M$ = mantissa inteira positiva, $e$ = expoente inteiro, $B$ = base (normalmente 2), $E$ = bias do expoente.

**Solução quadrática numericamente estável** [p.29, eq. 1.3.2, §5.6]

A forma ingênua $x = (-b + \sqrt{b^2-4ac})/(2a)$ é roundoff-prone quando $ac \ll b^2$. Solução: §5.6 mostra a forma estável (usar $-b - \sqrt{...}$ quando $b>0$, etc.).

**SVD de matriz retangular** [p.59, eq. 2.6.1]

$$A_{M\times N} = U_{M\times N} \cdot W_{N\times N} \cdot V^T_{N\times N}$$

com $U^T U = 1$, $V^T V = V V^T = 1$, $W = \text{diag}(w_1, \ldots, w_N)$, $w_j \geq 0$.

**Inversa via SVD** [p.61, eq. 2.6.5]

$$A^{-1} = V \cdot \text{diag}(1/w_j) \cdot U^T$$

Regra prática crítica: se $w_j$ é "pequeno" (próximo da precisão), **zerar** $1/w_j$ antes de formar a inversa, não invertê-lo [p.62, eq. 2.6.7].

**Solução least-squares overdetermined via SVD** [p.62, eq. 2.6.9]

$$x = V \cdot \text{diag}(1/w_j) \cdot U^T \cdot b$$

minimiza $r \equiv |A\cdot x - b|$.

**Park-Miller Minimal Standard RNG** [p.278, eq. 7.1.3]

$$I_{j+1} = a I_j \mod m, \quad a = 7^5 = 16807, \quad m = 2^{31}-1 = 2147483647$$

Período = $m-1 \approx 2.1 \times 10^9$ [p.279]. Semente **nunca pode ser 0** (se perpetua). `ran0` usa XOR com MASK para permitir seed=0.

**Schrage's trick** (multiplicação modular sem overflow 32-bit) [p.278, eq. 7.1.4–7.1.5]

Com $m = aq + r$, $q = \lfloor m/a \rfloor$, $r = m \mod a$:

$$az \mod m = \begin{cases} a(z \mod q) - r\lfloor z/q \rfloor & \text{se} \geq 0 \\ a(z \mod q) - r\lfloor z/q \rfloor + m & \text{caso contrário} \end{cases}$$

Para Minimal Standard: $q = 127773$, $r = 2836$ [p.278].

**L'Ecuyer combined generator** (usado em `ran2`) [p.281]

Combina duas sequências com $m_1 = 2147483563$, $a_1 = 40014$, $q_1 = 53668$, $r_1 = 12211$ e $m_2 = 2147483399$, $a_2 = 40692$, $q_2 = 52774$, $r_2 = 3791$. Período combinado $\approx 2.3 \times 10^{18}$.

**Box-Muller normal deviate** [p.289, eq. 7.2.10]

$$y_1 = \sqrt{-2 \ln x_1} \cos(2\pi x_2), \quad y_2 = \sqrt{-2 \ln x_1} \sin(2\pi x_2)$$

com $x_1, x_2$ uniformes em (0,1). Gera dois normais independentes $\mathcal{N}(0,1)$.

**Monte Carlo integration** [p.305, eq. 7.6.1]

$$\int f \, dV \approx V\langle f \rangle \pm V \sqrt{\frac{\langle f^2 \rangle - \langle f \rangle^2}{N}}$$

O "±" é **uma** standard deviation, **não** um rigorous bound; não há garantia de distribuição Gaussiana [p.305]. Convergência $\sim 1/\sqrt{N}$ é o limite fundamental do MC simples [p.308].

**Moments da distribuição** [p.611-612, eqs. 14.1.1–14.1.6]

Mean: $\bar{x} = \frac{1}{N}\sum x_j$

Variance: $\text{Var}(x) = \frac{1}{N-1}\sum (x_j-\bar{x})^2$ (divisor N-1 estima variance quando a mean é estimada dos dados; use N apenas se mean é conhecida a priori [p.611]).

Skewness: $\text{Skew} = \frac{1}{N}\sum \left(\frac{x_j-\bar{x}}{\sigma}\right)^3$, com std error $\approx \sqrt{15/N}$ sob normal.

Kurtosis: $\text{Kurt} = \frac{1}{N}\sum \left(\frac{x_j-\bar{x}}{\sigma}\right)^4 - 3$, std error $\approx \sqrt{96/N}$ sob normal.

**Corrected two-pass variance** (reduz roundoff) [p.613, eq. 14.1.8]

$$\text{Var} = \frac{1}{N-1}\left[\sum (x_j-\bar{x})^2 - \frac{1}{N}\left(\sum (x_j-\bar{x})\right)^2\right]$$

O segundo termo corrige roundoff residual do primeiro.

**Chi-square para model fitting** [p.660, eq. 15.1.5]

$$\chi^2 = \sum_{i=1}^N \left(\frac{y_i - y(x_i; a_1,\ldots,a_M)}{\sigma_i}\right)^2$$

Para modelos lineares nos parâmetros, $\chi^2_{\min}$ segue distribuição chi-square com $\nu = N - M$ graus de liberdade [p.660]. Valor típico de "moderately good fit": $\chi^2 \approx \nu$; a estatística tem mean $\nu$ e std $\sqrt{2\nu}$ [p.661].

**Goodness-of-fit probability** [p.660]

$$Q = \text{gammq}(0.5 \nu,\ 0.5 \chi^2)$$

**Normal equations (general linear LS)** [p.672-673, eqs. 15.4.8, 15.4.10]

Design matrix $A_{ij} = X_j(x_i)/\sigma_i$, $b_i = y_i/\sigma_i$. Normal equations: $(A^T A) \mathbf{a} = A^T \mathbf{b}$. Covariância dos parâmetros fit: $[C] = [\alpha]^{-1}$, com $\sigma^2(a_j) = C_{jj}$ na diagonal [p.675, eq. 15.4.15]. **Warning**: normal equations são roundoff-sensitive; preferir SVD para problemas não-fáceis [p.673-674].

**Advertência sobre $A^T A$** [p.?, §15.4]: o condition number de $A^T A$ é o **quadrado** do condition number de $A$. "Don't!" usar normal equations quando o problema não é trivial.

## 4. Algoritmos e Pseudocódigo

**Park-Miller Minimal Standard + Schrage (`ran0`)** [p.279]

```c
#define IA 16807
#define IM 2147483647
#define AM (1.0/IM)
#define IQ 127773
#define IR 2836
#define MASK 123459876
float ran0(long *idum) {
    long k; float ans;
    *idum ^= MASK;                           // permite seed=0
    k = (*idum)/IQ;
    *idum = IA*(*idum - k*IQ) - IR*k;        // Schrage
    if (*idum < 0) *idum += IM;
    ans = AM*(*idum);
    *idum ^= MASK;
    return ans;
}
```

**Box-Muller polar form (`gasdev`)** [p.289-290]

```
repeat:
    v1 = 2*ran1() - 1    # ponto no quadrado [-1,1]^2
    v2 = 2*ran1() - 1
    rsq = v1*v1 + v2*v2
until 0 < rsq < 1         # dentro do círculo unitário
fac = sqrt(-2*ln(rsq)/rsq)
return v2*fac             # guardar v1*fac para próxima chamada
```

A forma polar evita `cos`/`sin` substituindo por `v1/sqrt(rsq)` e `v2/sqrt(rsq)` [p.289].

**SVD solution of linear least-squares** [p.673-678, §15.4] — passos:

- Passo 1 [p.673, svdcmp]: Compute $A = U \cdot \text{diag}(W) \cdot V^T$ via `svdcmp`.
- Passo 2 [p.62]: Determine threshold $w_{\max} \cdot \epsilon$ (com $\epsilon \sim 10^{-6}$ single, $10^{-12}$ double).
- Passo 3 [p.63-64]: For each small singular value $w_j$, set $1/w_j$ to zero ("zeroing" the small $w_j$'s) — do NOT invert it.
- Passo 4 [p.62, svbksb]: Resolver $\mathbf{a} = V \cdot \text{diag}(1/w[j]) \cdot (U^T \cdot \mathbf{b})$.
- Passo 5 [p.675]: Covariance matrix $C_{jk} = \sum_i V_{ji}V_{ki}/w_i^2$ (excluindo os zerados).

Isso automaticamente resolve casos underdetermined, driving combinações ambíguas a zero em vez de deixá-las cancelar com magnitudes grandes [p.676].

**Simple Monte Carlo integration** [p.305-307, §7.6]

```
Given region V enclosing target region W, function f defined on W (0 outside):
sw = 0; sum2 = 0
for j = 1..N:
    pick random x in V (using ran2)
    if x in W:
        fval = f(x)
        sw += fval
        sum2 += fval*fval
integral_estimate = vol(V) * sw / N
error_estimate = vol(V) * sqrt((sum2/N - (sw/N)^2) / N)
```

Convergência $O(N^{-1/2})$; para melhorar, aplicar change-of-variable para deixar f quase-constante (variance reduction) [p.307-308].

**Bootstrap resampling** [p.691-692, §15.6]

```
Given original dataset D0 with N iid points:
for k = 1..K:                    # K >> 100 tipicamente
    D_k = []
    for j = 1..N:
        i = randint(1, N)         # sampling WITH replacement
        D_k.append(D0[i])
    a_k = fit_parameters(D_k)
# Distribuição dos {a_k} estima distribuição de a_true ao redor de a_measured
```

Falha quando: dados não são iid (séries temporais com autocorrelação!); estimadores sensíveis a clumpiness ou spacing uniforme (e.g., Fourier); estimadores baseados em sorted differences [p.692].

**Halton's quasi-random sequence (1-D)** [p.309-310]:

- Passo 1 [p.309]: Escrever $j$ em base $b$ (b primo). Ex.: $j=17$, $b=3 \Rightarrow 122$.
- Passo 2 [p.309]: Reverter dígitos e colocar radix-point, obtendo $0.221$ base 3.
- Passo 3 [p.309-310]: $H_j$ = essa fração avaliada. Para n-D, usar primo distinto em cada dimensão.

**Moments em single pass com correção de roundoff** [p.613-614, routine `moment`]

```
First pass: compute mean
Second pass:
  for each x_j: s = x_j - mean
    adev += |s|
    ep += s                              # correction term
    var += s^2
    skew += s^3
    curt += s^4
var_final = (var - ep*ep/N) / (N-1)      # corrected two-pass
skew_final = skew / (N * var_final * sqrt(var_final))
kurt_final = curt / (N * var_final^2) - 3
```

**Levenberg-Marquardt (nonlinear LS)** [ch.15, §15.5, routines `mrqmin`, `mrqcof`]

Interpola entre método inverse-Hessian (longe do mínimo, use steepest-descent scaled) e method-of-normal-equations (perto do mínimo, use curvature matrix). Parameter $\lambda$ controla a interpolação; cresce se step piora $\chi^2$, decresce se melhora. Referência: §15.5.

## 5. Regras de Trading Explícitas

Este livro não é sobre trading. Contudo, traduzindo suas regras numéricas para contexto de backtesting e execução:

- **REGRA [p.60-62]**: Ao resolver least-squares em factor models / regression backtests, usar SVD (`svdcmp`+`svbksb`), não normal equations. Se o condition number exceder ~$10^6$ (single) ou ~$10^{12}$ (double), zerar singular values abaixo do threshold antes de inverter.
- **REGRA [p.29]**: Nunca use a forma ingênua $(-b + \sqrt{b^2-4ac})/(2a)$ para roots de quadráticas (e.g., ao resolver vol implícita, breakeven por BS). Usar forma estável do §5.6.
- **REGRA [p.279]**: `rand()` do sistema raramente é suficiente para Monte Carlo financeiro. Usar Park-Miller Minimal Standard + Bays-Durham shuffle (`ran1`) como baseline; para sequências >5% do período (~$10^8$ samples), usar `ran2` (L'Ecuyer) com período $2.3 \times 10^{18}$ [p.281].
- **REGRA [p.279]**: **Nunca** usar seed=0 em linear congruential generators — a sequência se perpetua em 0. `ran0`/`ran1` usam XOR com MASK para blindar o usuário desse erro.
- **REGRA [p.308]**: Aceitar que Monte Carlo simples tem erro $O(N^{-1/2})$. Para "break the $\sqrt{N}$ barrier", usar quasi-random sequences (Sobol/Halton) que dão $O(N^{-1})$ ou melhor [p.309-310].
- **REGRA [p.660]**: Todo parameter fit (SGD, OLS, MLE) deve reportar três coisas: (i) parâmetros, (ii) suas variâncias (diagonal da covariância $[\alpha]^{-1}$ ou $C_{jj}$), (iii) probabilidade Q de goodness-of-fit. Sem os três, "a fitting procedure is not useful" [p.657].
- **REGRA [p.660-661]**: Interpretar Q: Q < $10^{-3}$ → modelo provavelmente errado OU erros subestimados OU erros não-Gaussianos. Q > 0.99 → quase sempre significa que você superestimou seus erros (ou pior, fraudou os dados).
- **REGRA [p.692]**: **Bootstrap falha em séries temporais** (não iid). Não use naive bootstrap sobre returns de trading — use block bootstrap ou stationary bootstrap (não cobertos aqui; ver outros livros).
- **REGRA [p.611, §14.1]**: Prefira median ou average deviation ($\frac{1}{N}\sum|x_j - \bar{x}|$) a variance quando a distribuição tem fat tails (second moment não existe). Em finance, isso cobre quase todo return distribution real.
- **NUNCA [p.31]**: Usar recursões lineares sem provar stability. Exemplo: $\phi^{n+1} = \phi^{n-1} - \phi^n$ parece elegante mas diverge em $n \approx 16$ em 32-bit.
- **NUNCA [p.673-674]**: Formar $A^T A$ explicitamente em linear least-squares de larga escala. O condition number de $A^T A$ é o quadrado do de $A$; isso degrada precisão drasticamente.

## 6. Pitfalls e Anti-patterns

- [p.29] **Subtração de números quase iguais** é a fonte mais comum de roundoff catastrófico. Onde um algoritmo produz $a - b$ com $a \approx b$, refatorar algebricamente.
- [p.31] **Recursões instáveis** amplificam exponencialmente qualquer admixture de solução espúria. Testar stability *antes* de confiar em qualquer recursão.
- [p.61] **Usar condition number sem inspecionar singular values individuais**. SVD permite diagnóstico granular; condition number sozinho é um resumo crudo.
- [p.62] **Inverter um $w_j$ pequeno em vez de zerá-lo**: "It may seem paradoxical that... zeroing a singular value" ajuda, mas ajuda: transforma solução delicada-e-cancelante em solução de mínimo módulo bem-comportada.
- [p.277, p.279] **Confiar em `rand()` do sistema**. "System-supplied rand()s are almost always linear congruential generators" com multiplicadores ruins [p.277]. Correlações de baixa ordem em ran0 fazem valores $<10^{-6}$ serem *sempre* seguidos por valores $<0.0168$ [p.279] — matando simulações de rare-event.
- [p.279] **Não testar seu RNG em 2-D binning**. `ran0` falha $\chi^2$ test quando pontos $(I_i, I_{i+1})$ são binados em 2D para $N > 10^7$.
- [p.305] **Interpretar o "±" de MC como bound rígido**. É *one standard deviation*, e não-Gaussiana quando f tem tails ou suporte pequeno [p.305].
- [p.613] **Computar variance como $\overline{x^2} - \bar{x}^2$ ingenuamente** (eq. 14.1.7). "Pode magnificar roundoff error por um grande fator e é geralmente injustificável". Use corrected two-pass (eq. 14.1.8).
- [p.611] **Usar variance/std para distribuições fat-tailed**. "A distribution whose second moment does not exist... the variance... is useless" — não converge nem mostra consistência entre samples do mesmo processo.
- [p.612] **Reportar skewness/kurtosis sem caveat**. "Should be used with caution or, better yet, not at all" em distribuições com variance finita mas quarta-moment grande.
- [p.657] **"Chi-by-eye"**: julgar a qualidade de fit olhando graficamente. "Its practitioners get what they deserve."
- [p.659] **Least-squares aplicado a dados com outliers**: MLE-Gaussian "is willing to distort the whole curve to try to bring them, mistakenly, into line". Usar robust estimators (§15.7).
- [p.660] **Aceitar fit quando Q é muito alto** ($> 0.99$): quase sempre significa erros superestimados ou dados fraudados. Não é "bom" fit.
- [p.673-674] **Normal equations para problemas não-triviais**. Roundoff é amplificado pelo quadrado do condition number.
- [p.692] **Bootstrap em séries temporais**. A assunção iid é violada; distribuição resultante é errada. Também falha em Fourier-based estimators (precisam do grid regular) e em sequential-difference estimators.

## 7. Parâmetros Sensíveis

- **Machine epsilon threshold para SVD** [p.61]: usar $10^{-6}$ em single precision, $10^{-12}$ em double. **Justificativa econômica**: reflete a precisão real da hardware representation; não é otimizado sobre dados.
- **Park-Miller multiplier $a = 16807 = 7^5$** [p.278]: 25+ anos de uso e passa todos os testes teóricos conhecidos. Alternativas validadas: $a = 48271$ (com $q=44488$, $r=3399$) ou $a = 69621$ ($q=30845$, $r=23902$). **"No values other than these should be used"** [p.279] — este é um parâmetro com justificativa teórica forte, não ajustável.
- **Shuffle table size $NTAB = 32$** em `ran1` [p.280]: na média, deviate retornado vem da chamada $j+32$, quebrando correlações de baixa ordem. Valor é uma constante de design, não ajustado por user.
- **Graus de liberdade $\nu = N - M$ em chi-square fit** [p.660]: não é um parâmetro livre, é contagem. Modelos com muitos parâmetros livres M relativos a N inflam artificialmente $\chi^2/\nu$ — analogia direta a overfit em ML.
- **"Moderately good fit": $\chi^2 \approx \nu$** [p.661]: $\chi^2 \ll \nu$ ou $\chi^2 \gg \nu$ são ambos suspeitos. Regra independente de dataset.
- **Bootstrap replicates K** [p.691]: o livro diz "any number of synthetic data sets" — convenção externa ($K \geq 1000$) não é imposta aqui. Livro deixa isso ao usuário.
- **Levenberg-Marquardt $\lambda$ initial** [ch.15, §15.5]: cresce fator 10 se step piora, decresce fator 10 se melhora. Design heurístico, não é um hyperparâmetro a otimizar.

## 8. Citações Literais Importantes

> "Clever minimization of truncation error is practically the entire content of the field of numerical analysis!" — [p.30]

> "An unstable method would be useful on a hypothetical, perfect computer; but in this imperfect world it is necessary for us to require that algorithms be stable — or if unstable that we use them with great caution." — [p.30]

> "To be genuinely useful, a fitting procedure should provide (i) parameters, (ii) error estimates on the parameters, and (iii) a statistical measure of goodness-of-fit. When the third item suggests that the model is an unlikely match to the data, then items (i) and (ii) are probably worthless." — [p.656-657]

> "Unfortunately, many practitioners of parameter estimation never proceed beyond item (i). They deem a fit acceptable if a graph of data and model looks good. This approach is known as chi-by-eye. Luckily, its practitioners get what they deserve." — [p.657]

> "System-supplied rand()s are almost always linear congruential generators [... with problems] as big as your fist." — [p.277]

> "No values other than these should be used." — [p.279]

> "It may seem paradoxical that this can be so, since zeroing a singular value [is what makes an ill-conditioned problem solvable]." — [p.62]

> "The fundamental disadvantage of simple Monte Carlo integration is that its accuracy increases only as the square root of N, the number of sampled points." — [p.308]

## 9. Conexões com Outros Livros Desta Base

- **SVD e condition number** [p.59-62] também em `advances_fin_ml.md` (López de Prado usa SVD para hierarchical risk parity e detectar multicolinearidade em factor models) e `data_driven_science.md` (Brunton & Kutz fazem do SVD o eixo do livro inteiro). Numerical Recipes fornece a **implementação estável** (`svdcmp`) que livros aplicados assumem como caixa-preta.
- **Monte Carlo e quasi-random sequences** [p.305-310] também em `advances_fin_ml.md` (MC para backtesting com CPCV e synthetic data) e `leverage_space.md` (Vince usa MC para Optimal f sob distribuições realistas). Numerical Recipes provê o **fundamento $1/\sqrt{N}$ barrier** e a saída (quasi-random).
- **Chi-square fitting e goodness-of-fit** [p.660-661] também em `stat_sound_indicators.md` (Aronson exige statistical significance em signal testing — conceito paralelo de Q).
- **Bootstrap** [p.691-692] também em `ml_for_algo_trading.md` e `advances_fin_ml.md`, com a advertência específica presente aqui de que bootstrap naive falha em séries temporais — os dois livros de ML financeiro apresentam block/stationary bootstrap como correção.
- **Linear prediction e spectral estimation** [ch.13.6-13.7, p.561+] também em `cybernetic_analysis.md`, `rocket_science.md`, `cycle_analytics.md` (Ehlers aplica linear prediction e maximum entropy method cobertos aqui).
- **Least squares com outliers / robust estimation** [§15.7, p.699+] também em `stocks_on_the_move.md` e `trading_evolved.md` (Clenow usa trimmed regressions para trend estimation) e em `machine_trading.md`.
- **Random number quality** [p.277-283] também em `math_money_mgmt.md` (Vince simula extensivamente distribuições de returns). O padrão de `ran2`/L'Ecuyer é referência em qualquer simulação séria de trading.
- **Numerical stability e roundoff** [p.28-31] tratados implicitamente em `algo_trading_chan.md` (Chan adverte sobre instabilidade de covariance matrices em portfolio optimization — conceito de condition number aplicado).

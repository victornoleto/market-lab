# Numerical Recipes in C: The Art of Scientific Computing, Second Edition

## Metadata
- **Author:** William H. Press; Saul A. Teukolsky; William T. Vetterling; Brian P. Flannery [p.i]
- **Year:** 1992 (2nd ed.; reprinted with corrections through 1997) [p.ii]
- **Publisher:** Cambridge University Press [p.ii]
- **Pages:** ~1000 main text (printed), book pp. i–xxii + 1–965 + appendices [p.ii, contents]
- **ISBN:** 0-521-43108-5 [p.ii]
- **Main focus:** Prescriptive catalog of numerically stable algorithms in C, with ready-to-use code; covers linear algebra, random numbers, root finding, minimization, FFT, statistics, data modeling, ODE/PDE, and "less numerical" topics (hashing, CRC, compression).

## 1. Core Thesis
Numerical Recipes is a **prescriptive** work: the authors explicitly state that they chose to editorialize — "telling you what you should and shouldn't do" — reacting against the tendency of traditional texts to list every method ever invented without judgment [p.1]. The operational thesis is that, in numerical computing, **algorithm choice dominates hardware choice**: "clever minimization of truncation error is practically the entire content of the field of numerical analysis" [p.30]. Correspondingly, every numerical result must be judged against three distinct and non-interchangeable errors: **roundoff error** (intrinsic to hardware), **truncation error** (intrinsic to the algorithm), and **instability** (amplification of roundoff across iterations) [p.28-30].

For the market-lab project, the relevant thesis is the second one, stated in §15.0: a fit is only "genuinely useful" when it provides (i) parameters, (ii) error estimates on the parameters, and (iii) a statistical goodness-of-fit measure. "Chi-by-eye" (judging a fit by looking at the plot) is explicitly condemned: "its practitioners get what they deserve" [p.657].

## 2. Main Concepts
- **Machine accuracy ($\epsilon_m$)** — the smallest float that, added to 1.0, yields a result different from 1.0. For B=2, 32-bit, $\epsilon_m \approx 3 \times 10^{-8}$ [p.28]. This is the **fractional** accuracy, distinct from the smallest representable float [p.29].
- **Roundoff error** — fractional error introduced by each floating-point operation. Across $N$ operations, accumulated error can be $\sqrt{N}\epsilon_m$ (random walk) or, if biased, up to $N\epsilon_m$ [p.29].
- **Truncation error** — discrepancy between the true answer and the answer from a calculation using a finite number of terms/points; under programmer control [p.30].
- **Stability** — property of an algorithm that prevents roundoff amplification across iterations. Unstable example: the recursion $\phi^{n+1} = \phi^{n-1} - \phi^n$ for the Golden Mean yields completely wrong answers by about $n=16$ on a 32-bit machine [p.31].
- **Condition number of a matrix** — ratio of largest to smallest singular value $w_j$. Singular matrix = infinite condition number; ill-conditioned when its reciprocal approaches machine precision ($<10^{-6}$ single, $<10^{-12}$ double) [p.61].
- **Singular Value Decomposition (SVD)** — factorization $A = U \cdot W \cdot V^T$ where $U$ is $M \times N$ column-orthogonal, $W$ is diagonal with singular values $\geq 0$, $V^T$ is $N\times N$ orthogonal. Diagnoses and solves singular or near-singular systems [p.59-60].
- **Maximum likelihood estimator** — parameter choice that maximizes the probability of the observed data given the model [p.658].
- **Chi-square ($\chi^2$) merit function** — for iid Gaussian-error measurements, minimizing $\chi^2$ is equivalent to maximum likelihood [p.659-660].
- **Goodness-of-fit probability Q** — $Q = \text{gammq}(0.5\nu, 0.5\chi^2)$, with $\nu = N-M$ degrees of freedom. Q < 0.001 suggests wrong model or underestimated errors [p.660-661].
- **Bootstrap method** — given an iid dataset of N points, generate synthetic datasets by sampling *with replacement* of size N; roughly 37% (1/e) of points will be duplicates [p.691-692].
- **Quasi-random (sub-random) sequences** — sequences like Halton/Sobol that fill n-space more uniformly than iid points, giving error $\sim N^{-1}$ instead of $N^{-1/2}$ [p.309-310].
- **Minimal Standard generator (Park & Miller)** — linear congruential generator $I_{j+1} = a I_j \mod m$ with $a=16807$, $m=2^{31}-1$. Minimum standard against which others must be judged [p.278-279].
- **Linear prediction (LP)** — extrapolation of a series using coefficients $d_j$ fitted to predict each point as a linear combination of the previous M [ch.13.6, p.561+].

## 3. Formulas / Equations
**Floating-point representation** [p.28, eq. 1.3.1]

$$s \times M \times B^{e-E}$$

where $s$ = sign bit, $M$ = positive integer mantissa, $e$ = integer exponent, $B$ = base (typically 2), $E$ = exponent bias.

**Numerically stable quadratic solution** [p.29, eq. 1.3.2, §5.6]

The naive form $x = (-b + \sqrt{b^2-4ac})/(2a)$ is roundoff-prone when $ac \ll b^2$. Solution: §5.6 shows the stable form (use $-b - \sqrt{...}$ when $b>0$, etc.).

**SVD of rectangular matrix** [p.59, eq. 2.6.1]

$$A_{M\times N} = U_{M\times N} \cdot W_{N\times N} \cdot V^T_{N\times N}$$

com $U^T U = 1$, $V^T V = V V^T = 1$, $W = \text{diag}(w_1, \ldots, w_N)$, $w_j \geq 0$.

**Inverse via SVD** [p.61, eq. 2.6.5]

$$A^{-1} = V \cdot \text{diag}(1/w_j) \cdot U^T$$

Critical practical rule: if $w_j$ is "small" (near precision), **zero** $1/w_j$ before forming the inverse rather than inverting it [p.62, eq. 2.6.7].

**Overdetermined least-squares solution via SVD** [p.62, eq. 2.6.9]

$$x = V \cdot \text{diag}(1/w_j) \cdot U^T \cdot b$$

minimizes $r \equiv |A\cdot x - b|$.

**Park-Miller Minimal Standard RNG** [p.278, eq. 7.1.3]

$$I_{j+1} = a I_j \mod m, \quad a = 7^5 = 16807, \quad m = 2^{31}-1 = 2147483647$$

Period = $m-1 \approx 2.1 \times 10^9$ [p.279]. Seed **must never be 0** (it perpetuates). `ran0` uses XOR with MASK to allow seed=0.

**Schrage's trick** (modular multiplication without 32-bit overflow) [p.278, eq. 7.1.4–7.1.5]

With $m = aq + r$, $q = \lfloor m/a \rfloor$, $r = m \mod a$:

$$az \mod m = \begin{cases} a(z \mod q) - r\lfloor z/q \rfloor & \text{if} \geq 0 \\ a(z \mod q) - r\lfloor z/q \rfloor + m & \text{otherwise} \end{cases}$$

For Minimal Standard: $q = 127773$, $r = 2836$ [p.278].

**L'Ecuyer combined generator** (used in `ran2`) [p.281]

Combines two sequences with $m_1 = 2147483563$, $a_1 = 40014$, $q_1 = 53668$, $r_1 = 12211$ and $m_2 = 2147483399$, $a_2 = 40692$, $q_2 = 52774$, $r_2 = 3791$. Combined period $\approx 2.3 \times 10^{18}$.

**Box-Muller normal deviate** [p.289, eq. 7.2.10]

$$y_1 = \sqrt{-2 \ln x_1} \cos(2\pi x_2), \quad y_2 = \sqrt{-2 \ln x_1} \sin(2\pi x_2)$$

with $x_1, x_2$ uniform on (0,1). Generates two independent normals $\mathcal{N}(0,1)$.

**Monte Carlo integration** [p.305, eq. 7.6.1]

$$\int f \, dV \approx V\langle f \rangle \pm V \sqrt{\frac{\langle f^2 \rangle - \langle f \rangle^2}{N}}$$

The "±" is **one** standard deviation, **not** a rigorous bound; no Gaussian-distribution guarantee [p.305]. Convergence $\sim 1/\sqrt{N}$ is the fundamental limit of simple MC [p.308].

**Moments of the distribution** [p.611-612, eqs. 14.1.1–14.1.6]

Mean: $\bar{x} = \frac{1}{N}\sum x_j$

Variance: $\text{Var}(x) = \frac{1}{N-1}\sum (x_j-\bar{x})^2$ (divisor N-1 estimates variance when the mean is estimated from the data; use N only if the mean is known a priori [p.611]).

Skewness: $\text{Skew} = \frac{1}{N}\sum \left(\frac{x_j-\bar{x}}{\sigma}\right)^3$, with std error $\approx \sqrt{15/N}$ under normal.

Kurtosis: $\text{Kurt} = \frac{1}{N}\sum \left(\frac{x_j-\bar{x}}{\sigma}\right)^4 - 3$, std error $\approx \sqrt{96/N}$ under normal.

**Corrected two-pass variance** (reduces roundoff) [p.613, eq. 14.1.8]

$$\text{Var} = \frac{1}{N-1}\left[\sum (x_j-\bar{x})^2 - \frac{1}{N}\left(\sum (x_j-\bar{x})\right)^2\right]$$

The second term corrects residual roundoff from the first.

**Chi-square for model fitting** [p.660, eq. 15.1.5]

$$\chi^2 = \sum_{i=1}^N \left(\frac{y_i - y(x_i; a_1,\ldots,a_M)}{\sigma_i}\right)^2$$

For models linear in parameters, $\chi^2_{\min}$ follows a chi-square distribution with $\nu = N - M$ degrees of freedom [p.660]. Typical "moderately good fit" value: $\chi^2 \approx \nu$; the statistic has mean $\nu$ and std $\sqrt{2\nu}$ [p.661].

**Goodness-of-fit probability** [p.660]

$$Q = \text{gammq}(0.5 \nu,\ 0.5 \chi^2)$$

**Normal equations (general linear LS)** [p.672-673, eqs. 15.4.8, 15.4.10]

Design matrix $A_{ij} = X_j(x_i)/\sigma_i$, $b_i = y_i/\sigma_i$. Normal equations: $(A^T A) \mathbf{a} = A^T \mathbf{b}$. Fitted parameter covariance: $[C] = [\alpha]^{-1}$, with $\sigma^2(a_j) = C_{jj}$ on the diagonal [p.675, eq. 15.4.15]. **Warning**: normal equations are roundoff-sensitive; prefer SVD for non-trivial problems [p.673-674].

**Warning on $A^T A$** [p.?, §15.4]: the condition number of $A^T A$ is the **square** of the condition number of $A$. "Don't!" use normal equations when the problem is not trivial.

## 4. Algorithms and Pseudocode
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
    *idum ^= MASK;                           // allows seed=0
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
    v1 = 2*ran1() - 1    # point in the square [-1,1]^2
    v2 = 2*ran1() - 1
    rsq = v1*v1 + v2*v2
until 0 < rsq < 1         # inside the unit circle
fac = sqrt(-2*ln(rsq)/rsq)
return v2*fac             # store v1*fac for the next call
```

The polar form avoids `cos`/`sin` by substituting `v1/sqrt(rsq)` and `v2/sqrt(rsq)` [p.289].

**SVD solution of linear least-squares** [p.673-678, §15.4] — steps:

- Step 1 [p.673, svdcmp]: Compute $A = U \cdot \text{diag}(W) \cdot V^T$ via `svdcmp`.
- Step 2 [p.62]: Determine threshold $w_{\max} \cdot \epsilon$ (with $\epsilon \sim 10^{-6}$ single, $10^{-12}$ double).
- Step 3 [p.63-64]: For each small singular value $w_j$, set $1/w_j$ to zero ("zeroing" the small $w_j$'s) — do NOT invert it.
- Step 4 [p.62, svbksb]: Solve $\mathbf{a} = V \cdot \text{diag}(1/w[j]) \cdot (U^T \cdot \mathbf{b})$.
- Step 5 [p.675]: Covariance matrix $C_{jk} = \sum_i V_{ji}V_{ki}/w_i^2$ (excluding zeroed entries).

This automatically resolves underdetermined cases, driving ambiguous combinations to zero instead of letting them cancel with large magnitudes [p.676].

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

Convergence $O(N^{-1/2})$; to improve, apply change-of-variable to make f near-constant (variance reduction) [p.307-308].

**Bootstrap resampling** [p.691-692, §15.6]

```
Given original dataset D0 with N iid points:
for k = 1..K:                    # K >> 100 typically
    D_k = []
    for j = 1..N:
        i = randint(1, N)         # sampling WITH replacement
        D_k.append(D0[i])
    a_k = fit_parameters(D_k)
# The distribution of {a_k} estimates the distribution of a_true around a_measured
```

Fails when: data is not iid (time series with autocorrelation!); estimators sensitive to clumpiness or uniform spacing (e.g., Fourier); estimators based on sorted differences [p.692].

**Halton's quasi-random sequence (1-D)** [p.309-310]:

- Step 1 [p.309]: Write $j$ in base $b$ (b prime). E.g., $j=17$, $b=3 \Rightarrow 122$.
- Step 2 [p.309]: Reverse digits and place a radix point, obtaining $0.221$ base 3.
- Step 3 [p.309-310]: $H_j$ = that fraction evaluated. For n-D, use a distinct prime in each dimension.

**Moments in a single pass with roundoff correction** [p.613-614, routine `moment`]

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

Interpolates between the inverse-Hessian method (far from minimum, use scaled steepest-descent) and the method-of-normal-equations (near minimum, use curvature matrix). Parameter $\lambda$ controls the interpolation; grows when a step worsens $\chi^2$, shrinks when it improves. Reference: §15.5.

## 5. Explicit Trading Rules
This book is not about trading. However, translating its numerical rules to the backtesting and execution context:

- **RULE [p.60-62]**: When solving least-squares in factor models / regression backtests, use SVD (`svdcmp`+`svbksb`), not normal equations. If the condition number exceeds ~$10^6$ (single) or ~$10^{12}$ (double), zero singular values below the threshold before inverting.
- **RULE [p.29]**: Never use the naive form $(-b + \sqrt{b^2-4ac})/(2a)$ for quadratic roots (e.g., when solving implied volatility, Black-Scholes breakeven). Use the stable form from §5.6.
- **RULE [p.279]**: The system `rand()` is rarely sufficient for financial Monte Carlo. Use Park-Miller Minimal Standard + Bays-Durham shuffle (`ran1`) as baseline; for sequences >5% of the period (~$10^8$ samples), use `ran2` (L'Ecuyer) with period $2.3 \times 10^{18}$ [p.281].
- **RULE [p.279]**: **Never** use seed=0 in linear congruential generators — the sequence perpetuates at 0. `ran0`/`ran1` use XOR with MASK to shield the user from this error.
- **RULE [p.308]**: Accept that simple Monte Carlo has error $O(N^{-1/2})$. To "break the $\sqrt{N}$ barrier", use quasi-random sequences (Sobol/Halton) that give $O(N^{-1})$ or better [p.309-310].
- **RULE [p.660]**: Every parameter fit (SGD, OLS, MLE) must report three things: (i) parameters, (ii) their variances (diagonal of covariance $[\alpha]^{-1}$ or $C_{jj}$), (iii) goodness-of-fit probability Q. Without all three, "a fitting procedure is not useful" [p.657].
- **RULE [p.660-661]**: Interpret Q: Q < $10^{-3}$ → model likely wrong OR errors underestimated OR non-Gaussian errors. Q > 0.99 → almost always means you overestimated your errors (or, worse, fabricated data).
- **RULE [p.692]**: **Bootstrap fails on time series** (not iid). Do not use naive bootstrap on trading returns — use block bootstrap or stationary bootstrap (not covered here; see other books).
- **RULE [p.611, §14.1]**: Prefer median or average deviation ($\frac{1}{N}\sum|x_j - \bar{x}|$) over variance when the distribution has fat tails (second moment does not exist). In finance, this covers nearly every real return distribution.
- **NEVER [p.31]**: Use linear recursions without proving stability. Example: $\phi^{n+1} = \phi^{n-1} - \phi^n$ looks elegant but diverges at $n \approx 16$ in 32-bit.
- **NEVER [p.673-674]**: Form $A^T A$ explicitly in large-scale linear least-squares. The condition number of $A^T A$ is the square of that of $A$; this drastically degrades precision.

## 6. Pitfalls and Anti-patterns
- [p.29] **Subtraction of nearly equal numbers** is the most common source of catastrophic roundoff. Where an algorithm produces $a - b$ with $a \approx b$, refactor algebraically.
- [p.31] **Unstable recursions** exponentially amplify any admixture of a spurious solution. Test stability *before* trusting any recursion.
- [p.61] **Using condition number without inspecting individual singular values**. SVD enables granular diagnosis; condition number alone is a crude summary.
- [p.62] **Inverting a small $w_j$ instead of zeroing it**: "It may seem paradoxical that... zeroing a singular value" helps, but it does: it turns a delicate-and-cancelling solution into a well-behaved minimum-modulus solution.
- [p.277, p.279] **Trusting the system `rand()`**. "System-supplied rand()s are almost always linear congruential generators" with bad multipliers [p.277]. Low-order correlations in ran0 make values $<10^{-6}$ *always* followed by values $<0.0168$ [p.279] — killing rare-event simulations.
- [p.279] **Not testing your RNG with 2-D binning**. `ran0` fails the $\chi^2$ test when points $(I_i, I_{i+1})$ are binned in 2D for $N > 10^7$.
- [p.305] **Interpreting the MC "±" as a hard bound**. It is *one standard deviation*, and non-Gaussian when f has tails or small support [p.305].
- [p.613] **Computing variance as $\overline{x^2} - \bar{x}^2$ naively** (eq. 14.1.7). "Can magnify roundoff error by a large factor and is generally unjustifiable." Use corrected two-pass (eq. 14.1.8).
- [p.611] **Using variance/std for fat-tailed distributions**. "A distribution whose second moment does not exist... the variance... is useless" — it does not converge nor show consistency across samples of the same process.
- [p.612] **Reporting skewness/kurtosis without caveat**. "Should be used with caution or, better yet, not at all" on distributions with finite variance but large fourth moment.
- [p.657] **"Chi-by-eye"**: judging fit quality by visual inspection. "Its practitioners get what they deserve."
- [p.659] **Least-squares applied to data with outliers**: Gaussian MLE "is willing to distort the whole curve to try to bring them, mistakenly, into line". Use robust estimators (§15.7).
- [p.660] **Accepting a fit when Q is very high** ($> 0.99$): almost always means overestimated errors or fabricated data. Not a "good" fit.
- [p.673-674] **Normal equations for non-trivial problems**. Roundoff is amplified by the square of the condition number.
- [p.692] **Bootstrap on time series**. The iid assumption is violated; the resulting distribution is wrong. Also fails on Fourier-based estimators (which need the regular grid) and on sequential-difference estimators.

## 7. Sensitive Parameters
- **Machine epsilon threshold for SVD** [p.61]: use $10^{-6}$ in single precision, $10^{-12}$ in double. **Economic justification**: reflects the real precision of the hardware representation; not optimized over data.
- **Park-Miller multiplier $a = 16807 = 7^5$** [p.278]: 25+ years in use and passes every known theoretical test. Validated alternatives: $a = 48271$ (with $q=44488$, $r=3399$) or $a = 69621$ ($q=30845$, $r=23902$). **"No values other than these should be used"** [p.279] — this parameter has strong theoretical justification, not adjustable.
- **Shuffle table size $NTAB = 32$** in `ran1` [p.280]: on average, the returned deviate comes from call $j+32$, breaking low-order correlations. Value is a design constant, not user-tuned.
- **Degrees of freedom $\nu = N - M$ in chi-square fit** [p.660]: not a free parameter, it is a count. Models with many free parameters M relative to N artificially inflate $\chi^2/\nu$ — direct analogy to overfitting in ML.
- **"Moderately good fit": $\chi^2 \approx \nu$** [p.661]: $\chi^2 \ll \nu$ or $\chi^2 \gg \nu$ are both suspect. Dataset-independent rule.
- **Bootstrap replicates K** [p.691]: the book says "any number of synthetic data sets" — external convention ($K \geq 1000$) is not imposed here. The book leaves it to the user.
- **Levenberg-Marquardt $\lambda$ initial** [ch.15, §15.5]: grows by factor 10 if step worsens, shrinks by factor 10 if step improves. Heuristic design, not a hyperparameter to optimize.

## 8. Key Literal Quotes
> "Clever minimization of truncation error is practically the entire content of the field of numerical analysis!" — [p.30]

> "An unstable method would be useful on a hypothetical, perfect computer; but in this imperfect world it is necessary for us to require that algorithms be stable — or if unstable that we use them with great caution." — [p.30]

> "To be genuinely useful, a fitting procedure should provide (i) parameters, (ii) error estimates on the parameters, and (iii) a statistical measure of goodness-of-fit. When the third item suggests that the model is an unlikely match to the data, then items (i) and (ii) are probably worthless." — [p.656-657]

> "Unfortunately, many practitioners of parameter estimation never proceed beyond item (i). They deem a fit acceptable if a graph of data and model looks good. This approach is known as chi-by-eye. Luckily, its practitioners get what they deserve." — [p.657]

> "System-supplied rand()s are almost always linear congruential generators [... with problems] as big as your fist." — [p.277]

> "No values other than these should be used." — [p.279]

> "It may seem paradoxical that this can be so, since zeroing a singular value [is what makes an ill-conditioned problem solvable]." — [p.62]

> "The fundamental disadvantage of simple Monte Carlo integration is that its accuracy increases only as the square root of N, the number of sampled points." — [p.308]

## 9. Cross-references to Other Books in This Knowledge Base
- **SVD and condition number** [p.59-62] also in `advances_fin_ml.md` (López de Prado uses SVD for hierarchical risk parity and to detect multicollinearity in factor models) and `data_driven_science.md` (Brunton & Kutz make SVD the backbone of the entire book). Numerical Recipes provides the **stable implementation** (`svdcmp`) that applied books assume as a black box.
- **Monte Carlo and quasi-random sequences** [p.305-310] also in `advances_fin_ml.md` (MC for backtesting with CPCV and synthetic data) and `leverage_space.md` (Vince uses MC for Optimal f under realistic distributions). Numerical Recipes provides the **$1/\sqrt{N}$ barrier foundation** and the escape route (quasi-random).
- **Chi-square fitting and goodness-of-fit** [p.660-661] also in `stat_sound_indicators.md` (Aronson requires statistical significance in signal testing — parallel concept to Q).
- **Bootstrap** [p.691-692] also in `ml_for_algo_trading.md` and `advances_fin_ml.md`, with the specific warning present here that naive bootstrap fails on time series — both financial ML books present block/stationary bootstrap as the correction.
- **Linear prediction and spectral estimation** [ch.13.6-13.7, p.561+] also in `cybernetic_analysis.md`, `rocket_science.md`, `cycle_analytics.md` (Ehlers applies linear prediction and the maximum entropy method covered here).
- **Least squares with outliers / robust estimation** [§15.7, p.699+] also in `stocks_on_the_move.md` and `trading_evolved.md` (Clenow uses trimmed regressions for trend estimation) and in `machine_trading.md`.
- **Random number quality** [p.277-283] also in `math_money_mgmt.md` (Vince extensively simulates return distributions). The `ran2`/L'Ecuyer standard is the reference in any serious trading simulation.
- **Numerical stability and roundoff** [p.28-31] treated implicitly in `algo_trading_chan.md` (Chan warns about instability of covariance matrices in portfolio optimization — condition number concept applied).

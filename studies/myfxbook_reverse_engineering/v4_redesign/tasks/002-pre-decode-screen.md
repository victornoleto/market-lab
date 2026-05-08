# Task 002 — pre_decode_screen.py

**Phase:** 1 | **Effort:** 2-3 sessoes | **Depends on:** 001

## Goal

Implementar pre-filtro que rejeita EAs sem edge real ANTES de gastar compute
decodando. **5 gates** encapsulados:

1. **K1 sanity (martingale signature)** — reusa `shared/sanity.py` existente
   (lot ratio doubling within 24h, etc.). Se K1 acionou → STOP imediato.
   Citacao: `[advances_fin_ml, ch.13]` (overbetting/martingale).
2. **MCPT (Monte Carlo Permutation Test) na track record do EA**
   `[evidence_based_ta, p.325-328]`, `[testing_tuning, p.310-322]`
3. **PSR (Probabilistic Sharpe Ratio) p<0.05 na track record**
   `[advances_fin_ml, p.260-263]`. **NAO usar DSR aqui** — DSR pressupõe selecao
   ex-post entre M tentativas; o EA e uma serie unica vinda do vendor, sem
   selecao explicita interna observavel. PSR e o objeto certo.
4. **Concentration test** — top-5% trades vs total PnL > 0.50 = curva-fit ou
   news-luck. Analogo ao Calmar de fragilidade `[machine_trading, p.13-14]`.
5. **Live-vs-demo flag** — raspar `system_info.json` campo
   `account.account_type`. Demo NAO e auto-STOP (5/52 systems sao Demo;
   eliminaria material decodavel arbitrariamente). E **warning-only tier**:
   reportado como flag, nao bloqueia, mas qualquer reativacao downstream do
   Plano A exige `is_live=True`.

## Schema correto do system_info.json

```python
account_type = system_info["account"]["account_type"]  # "Demo" | "Real"
is_live = (account_type == "Real")
```

## Interface

```python
# studies/myfxbook_reverse_engineering/shared/pre_decode_screen.py

from dataclasses import dataclass

@dataclass(frozen=True)
class PreScreenResult:
    system_id: str
    decision: str  # "GO" | "STOP"
    k1_sanity_pass: bool
    mcpt_p: float
    psr_p: float  # NAO dsr_p — ver justificativa acima
    concentration_top5: float
    is_live: bool  # warning-only, nao bloqueia
    notes: list[str]

def screen_system(system_id: str, *, n_permutations: int = 2000) -> PreScreenResult: ...
def screen_batch(system_ids: list[str]) -> list[PreScreenResult]: ...
```

Output: `systems/<id>/pre_decode_screen.json` parseable.

## Decision rules

EA passa (`decision="GO"`) se TODOS:

- `k1_sanity_pass == True` (sem martingale signature; reusa sanity.py existente)
- `mcpt_p < 0.05` (track record nao explicado por sorte)
- `psr_p < 0.05` (Sharpe estatisticamente diferente de zero, considerando
  skew/kurt da serie)
- `concentration_top5 < 0.50` (PnL nao concentrado em poucos trades)

`is_live` registrado em notes mas **nao bloqueia**. Caso contrario `decision="STOP"`,
`notes` lista quais gates falharam.

**Implicacao:** EAs Demo podem passar Fase 1; serao filtrados na Fase 3
(reativacao Plano A) onde mandate §3 exige Real. Documentado em DEAD_ENDS.md.

## Testes unitarios obrigatorios

`tests/myfxbook_pipeline/test_pre_decode_screen.py`:

**IMPORTANTE — caveats sobre os goldens:**
- "Golden statistical-quality PASS" mede track record do EA estatisticamente
  forte (band=HIGH, sanity=True, MCPT/PSR baixos). **Nao** mede strategy
  quality decode-self.
- "Golden martingale STOP" valida que K1 sanity pega martingale signatures
  (band=LOW, sanity=False, family=MARTINGALE_GRID).

1. **Golden statistical-quality PASS:** system **10281851** (Real, Eightcap,
   +3376% gain, 11.70% drawdown, band=HIGH, sanity=True, family=
   OVERLAP_NY_LONDON_RANGE, 652 trades). Esperado: `decision="GO"`,
   `is_live=True`, `k1_sanity_pass=True`.
2. **Golden martingale STOP:** system **11504701** (Real, ForexMart, band=LOW,
   sanity=False, family=MARTINGALE_GRID; reliability_score.json notes inclui
   "martingale signature detected"). Esperado: `decision="STOP"` por
   `k1_sanity_pass=False`.
3. **Demo warning-only:** system **1407880** (Demo, band=HIGH, sanity=True,
   family=LATE_NY_BREAKOUT). Esperado: `is_live=False`, mas decision **nao
   depende de is_live**; resultado deve ser GO (mostra que demo flag e
   warning-only, nao bloqueante).
4. **Concentration alta sintetica:** dataset onde top-5% trades = 80% PnL →
   STOP por concentration_top5 > 0.50.
5. **MCPT determinismo:** mesma seed produz mesmo p-value
   (`np.random.default_rng(seed=20260503)`).

## Implementacao MCPT (referencia)

```python
def mcpt_p_value(returns: np.ndarray, n_permutations: int, seed: int) -> float:
    """MCPT: permuta sinais dos retornos, recomputa Sharpe, fracao >= observado.

    Citation: [evidence_based_ta, p.325-328] — preserva distribuicao marginal,
    destroi sequencia. Rejeita H0 se fracao < 0.05.
    """
    observed_sharpe = sharpe_annualized(returns)
    rng = np.random.default_rng(seed)
    count_better = 0
    for _ in range(n_permutations):
        permuted = returns * rng.choice([-1, 1], size=len(returns))
        if sharpe_annualized(permuted) >= observed_sharpe:
            count_better += 1
    return (count_better + 1) / (n_permutations + 1)
```

## Implementacao PSR (referencia)

`[advances_fin_ml, p.260-263]`:

```python
def psr_p_value(returns: np.ndarray, sr_benchmark: float = 0.0) -> float:
    """PSR p-value: P(true SR > sr_benchmark | observed track).
    
    Considera skew, kurt, e tamanho amostral T. Nao corrige por multiplos
    testes (essa e a diferenca para DSR).
    """
    sr = sharpe_annualized(returns)
    T = len(returns)
    skew = scipy.stats.skew(returns)
    kurt = scipy.stats.kurtosis(returns, fisher=False)
    
    psr_z = (sr - sr_benchmark) * np.sqrt(T - 1) / np.sqrt(
        1 - skew * sr + (kurt - 1) / 4 * sr ** 2
    )
    p = 1 - scipy.stats.norm.cdf(psr_z)
    return p  # H0: true SR <= sr_benchmark; rejeita se p < 0.05
```

DSR (com correcao multiplos testes) reapareceran em Fase 3a apos LightGBM
mining N candidate rules: ai sim faz sentido contar M trials.

## Files to modify

- `shared/pre_decode_screen.py` (preenche skeleton da task 001)
- `tests/myfxbook_pipeline/test_pre_decode_screen.py` (preenche skeleton)

## Verificacao

```bash
# Rodar testes
uv run pytest tests/myfxbook_pipeline/test_pre_decode_screen.py -v

# Smoke test em systems reais
uv run python -c "
from studies.myfxbook_reverse_engineering.shared.pre_decode_screen import screen_system
print(screen_system('10281851'))   # esperado GO (Real, statistically strong)
print(screen_system('11504701'))   # esperado STOP (Real, martingale K1)
print(screen_system('1407880'))    # esperado GO com is_live=False (Demo, mas K1 ok)
"
```

## Aceite

- [ ] `screen_system()` e `screen_batch()` implementados
- [ ] 5 testes unitarios passam
- [ ] Smoke test em 10281851 retorna `decision="GO"`, `is_live=True`, `k1_sanity_pass=True`
- [ ] Smoke test em 11504701 retorna `decision="STOP"` por `k1_sanity_pass=False`
- [ ] Smoke test em 1407880 retorna `is_live=False` mas decision pode ser GO
      (demo nao bloqueia)
- [ ] `pre_decode_screen.json` schema documentado em docstring
- [ ] Citacoes presentes em todas as funcoes nao-triviais

## Kill-switches

- MCPT p-value > 0.05 em system 10281851 → bug provavel, investigar antes de DONE
- PSR p-value retorna NaN para input valido → bug numerico, fix antes de DONE
- 11504701 retorna decision=GO → bug critico no K1 wiring (deveria FAIL imediato)

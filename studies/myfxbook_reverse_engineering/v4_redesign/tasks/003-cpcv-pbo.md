# Task 003 — cpcv.py (CSCV / PBO)

**Phase:** 1 | **Effort:** 2 sessoes | **Depends on:** 001

## Goal

Implementar CSCV (Combinatorial Symmetric Cross Validation) e PBO (Probability
of Backtest Overfitting) seguindo `[advances_fin_ml, p.208-222]` (López de
Prado, AFML cap. 14).

## Esclarecimento de escopo (resposta a critique GPT-5.5)

PBO **nao substitui WF8**. Eles medem coisas diferentes:

| Metrica | O que mede | Quando aplica |
|---|---|---|
| Walk-forward purgado | Generalizacao temporal de UMA regra | Apos selecionar regra final |
| PBO (CSCV) | Probabilidade da regra escolhida ter sido sorte ENTRE M tentativas | **Apos miner produzir N candidatos** |
| MCPT | H0: serie sem skill | Track record direta |
| DSR | Sharpe ajustado por M tentativas | Apos selecionar regra final entre M |

PBO e **complementar**: roda no momento em que o miner (`decoder_candidates.py`
hoje, `lightgbm_miner.py` na task 015) produz N candidate rules e seleciona
top-1. Sem PBO, top-1 pode ser sorte; com PBO, sabemos a probabilidade disso.

## Domain de aplicacao concreto

Para cada EA, depois do miner, temos:
- N candidate rules (univariate ate ~544 atualmente, tree top-3, RIPPER top-1)
- Cada rule tem Sharpe estimado em uma janela de treino

Construir matriz `M` de shape `(T, N)` onde:
- `T` = sub-periodos da janela do EA (ex: 8 blocos de 6 meses cada)
- `N` = numero de candidate rules
- `M[t, n]` = Sharpe da rule `n` no sub-periodo `t`

Criterio de escolha em cada path do CSCV:
- Em cada split (S/2 sub-periodos como train, S/2 como test), pega rule com
  maior Sharpe in-sample → registra rank dela in-sample (sera top, rank 1)
  e rank dela out-of-sample
- PBO = fracao de paths onde `rank_OOS > N/2` (regra in-sample-best ficou
  abaixo da mediana OOS)

## Interface

```python
# studies/myfxbook_reverse_engineering/shared/cpcv.py

from dataclasses import dataclass
import numpy as np
import pandas as pd

@dataclass(frozen=True)
class CPCVResult:
    n_groups: int  # S = numero de sub-periodos (default 16)
    n_test: int    # S/2 = tamanho do bloco de teste
    n_paths: int   # phi[S, S/2] = C(S, S/2) / 2 paths simetricos
    pbo: float     # 0 <= pbo <= 1; PBO < 0.5 = boa generalizacao
    pbo_ci_low_99: float
    pbo_ci_high_99: float
    median_oos_rank_of_best_is: float  # diagnostico
    n_strategies: int
    n_periods: int

def cscv_pbo(
    metric_matrix: pd.DataFrame,  # shape (T, N) — T sub-periodos, N candidate rules
    n_groups: int = 16,
    metric: str = "sharpe",  # "sharpe" | "total_pnl" | "calmar"
) -> CPCVResult: ...
```

**Importante:**
- `metric_matrix.index` deve ser `DatetimeIndex` ou periodo unico contiguo
- `metric_matrix.columns` sao IDs de candidate rules (strings)
- `T = n_groups` exatamente (sem fracao); se T do EA nao divide por S=16, fazer
  ajuste com sub-periodos contiguos arredondados
- Exigir `T >= 8` para roda; senao retornar NaN com warning

## Helper para construir metric_matrix

A propria task 003 deve fornecer um helper que, dado outputs do miner, monta
a matriz:

```python
def build_metric_matrix_from_candidates(
    candidates: list[dict[str, Any]],  # candidates.json schema
    trades: pd.DataFrame,
    ohlc: dict[str, pd.DataFrame],
    n_groups: int = 16,
) -> pd.DataFrame:
    """Para cada candidate rule, computa Sharpe sub-periodo a sub-periodo
    aplicando a rule no trade history e medindo PnL. Retorna shape (T, N).
    """
    ...
```

Isto deixa task 003 self-contained: produz tanto cpcv_pbo() generico quanto o
adapter para o domain do myfxbook.

## Decision rule (gate Mandate §2.4)

PBO < 0.5 e hard gate. PBO >= 0.5 = "mais provavel que ter sido sorte do que
edge real" → reject `[advances_fin_ml, p.211]`.

## Testes unitarios obrigatorios

`tests/myfxbook_pipeline/test_cpcv.py`:

1. **Constant-edge synthetic:** matriz onde estrategia A tem Sharpe 2.0 estavel
   e B-Z tem Sharpe ~0 → PBO baixo (<0.2) — A consistentemente aparece OOS.
2. **Pure noise:** matriz aleatoria com mesma distrib em todas as cols → PBO
   ~0.5 (consistent with random ranking).
3. **Adversarial overfit:** matriz onde a "best in-sample" muda entre cada
   periodo (rotacao) → PBO alto (>0.7).
4. **Edge case n_paths=1:** rejeitar com erro claro (S muito pequeno).
5. **Embargo correto:** verificar que CSCV nao reusa periodos vizinhos em
   train+test simultaneamente (purging).
6. **Determinismo:** mesma matriz produz mesmo PBO.
7. **Complementary splits:** verificar que `J train / J^c test` e `J^c train / J test`
   sao ambos mantidos (nao usar `C(S,S/2)/2`).
8. **Build helper:** mini-suite cria 3 candidates e 4 trades, verifica que
   `build_metric_matrix_from_candidates` retorna shape correto.

## Files to modify

- `shared/cpcv.py` (preenche skeleton da task 001 + adicionar helper)
- `tests/myfxbook_pipeline/test_cpcv.py` (preenche skeleton)

## Verificacao

```bash
uv run pytest tests/myfxbook_pipeline/test_cpcv.py -v
```

## Aceite

- [ ] `cscv_pbo()` implementado conforme AFML
- [ ] `build_metric_matrix_from_candidates()` adapter para domain myfxbook
- [ ] 8 testes unitarios passam
- [ ] Docstring cita `[advances_fin_ml, p.208-222]` e clarifica escopo (PBO
      complementa, nao substitui WF)
- [ ] Determinismo verificado

## Kill-switches

- PBO retorna NaN para input valido → fix numerico antes de DONE
- Test 1 (constant edge) retorna PBO > 0.4 → bug na construcao de paths,
  investigar
- Test 3 (adversarial overfit) retorna PBO < 0.5 → bug, regra rotativa deve
  ter PBO alto

## Notas

- Manter implementacao agnostica (matrix in/out) para reuso em outros studies
- Para EAs com span < 4y, S=16 pode ser apertado; permitir S=8 com warning

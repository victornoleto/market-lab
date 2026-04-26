# Gold swing loop pausado em 25 iters + incidente de merge resgatado

**Data**: 2026-04-26 20:50
**Status**: loop encerrado sem winner; valor preservado em `main` no
commit `bab0095`. Lição operacional sobre `git merge --squash` com
symlinks salva em DEAD_ENDS abaixo.

## O que aconteceu

O `studies/gold_swing_loop/` rodou em paralelo com o sister loop
(strategy_hunt_loop) durante o dia. Objetivo era achar uma estratégia
de **ouro short-hold** (mean hold ≤ 5 dias) que batesse XAUUSD
buy-hold com gates strict — alvo do slot Plano A reactivation
(Pepperstone CFD).

**Fase 1 (iters 1-15, regras strict)** rodou madrugada → manhã.
Plateau em **MARGINAL/50** com a família vol-regime-inverse (long XAU
quando σ_60d < σ_252d). Falhou em DSR e em hold-time (médias 22-44
dias = swing-extended, não short-hold).

Após análise, sugeri 5 relaxações de regras. User autorizou:

1. **Universo**: single XAU → também `gold_complex` (XAU+XAG+GDX+...)
2. **Hold-time**: ≤5d hard gate → 3 tracks declarados
3. **Cost path**: pep_cfd → também `cme_futures` e `inter_etf`
4. **Datasets**: adicionar `gold_synth_40y` (deferred)
5. **Cross-dataset**: 3/3 strict → primary + corroborating

**Fase 2 (iters 16-25, regras relaxadas)**: 10 iters rodaram tarde.
Score CAIU para **NEAR_FAIL/35**. Multi-asset baskets (GLD+SLV,
GLD+GDX, GLD+BTC) também NEAR_FAIL — gold-cluster tem correlação
demais pra dar diversification benefit. CFTC COT positioning (3
variantes), GVZ implied vol, IC-7 compositions de signals antigos —
tudo plateau.

User decidiu **pausar** sem completar 100 iters. Tese aceita:
**ouro day/swing tem teto estrutural baixo**; multi-asset gold-only
não escapa porque GLD/SLV/GDX são correlacionados ρ ≈ 0.6-0.8 —
contraste com equity+bonds (ρ ~ 0) que deu o iter 035 do sister loop.

## O incidente de merge

Pra preservar o trabalho na main, sugeri squash merge da branch
`gold-swing/iter-001`. Aceito e executado.

`git merge --squash gold-swing/iter-001` rodou e reportou
"Automatic merge went well". Mas eu vi que o commit ia trazer
arquivos suspeitos: `.venv`, `data/tiingo/1hour`, `data/tiingo/daily`,
`data/external/macro`. Investigando descobri o pior:

A branch tinha **symlinks com paths absolutos** apontando pra própria
main (`/var/www/pessoal/ai-trade/.venv → /var/www/pessoal/ai-trade/.venv`).
Esses symlinks foram criados quando o worktree foi montado em
`/tmp/ai-trade-gold-swing/` — tornavam o worktree funcional ao
referenciar dados do checkout principal. Mas estavam **commitados na
branch**.

Quando o squash aplicou esses symlinks ao próprio main, virou
**autoreferência circular**: `.venv → .venv → .venv → ...`. O git, no
processo, **substituiu os diretórios reais** (.venv, data/tiingo/1hour,
data/tiingo/daily, data/external/macro) pelos symlinks vazios. Os
diretórios — incluindo o **cache Tiingo de 1700 tickers baixado ao
longo de dias** — sumiram do disco.

**Damage assessment**:
- `.venv/` — destruído (recriável via `uv sync`)
- `data/tiingo/daily/prices/` — destruído (~1700 parquets, dias de download)
- `data/tiingo/1hour/prices/` — destruído (XAUUSD intraday + outros)
- `data/external/macro/` — destruído (FRED VIX/T10Y3M/CAPE/EBP)

## A recuperação

`git reset --hard HEAD` desfez o commit (não tinha sido commitado ainda,
só staged) e removeu os symlinks ruins. Mas o reset não reconstrói
diretórios untracked: o dano em disco era **anterior ao reset**.

Sorte: existiam dois backups tarball antigos em `data/`:
- `tiingo_backup_20260415-0958.tar.gz` (152 MB, 1660 parquets)
- `tiingo_premigrate_20260415-181358.tar.gz` (156 MB, 1675 parquets)

Ambos de 11 dias atrás (Apr 15). Extraí o mais novo (`#2`), copiei pra
`data/tiingo/daily/prices/`. Recuperou **1675/~1700 daily parquets**.
Tickers principais (SPY, QQQ, GLD, TLT, IEF, HYG, EFA, AGG, SLV) ✓
presentes. Faltam: `xauusd`, `xagusd`, `GDX`, `GDXJ`, `EDV`, `ZROZ`,
`IAU`, `NTSX` — adicionados Apr 16-26, não existiam no backup. Re-fetch
sob demanda.

`.venv` recriado via `uv venv && uv sync` — pandas 3.0.2, numpy 2.4.4,
pyarrow 24.0.0, etc.

`data/tiingo/1hour/prices/` e `data/external/macro/` continuam vazios.
Re-fetch via cTrader Open API (pra 1h XAUUSD) e FRED API (pra macro)
quando algum estudo precisar. Sem urgência.

## O cherry-pick limpo

Pra preservar o trabalho do gold loop SEM mergear os symlinks tóxicos,
fiz cherry-pick manual em vez de squash:

```bash
git diff --diff-filter=A --name-only main..gold-swing/iter-001 \
  | grep -vE "^(\.venv|data/external/macro|data/tiingo/1hour|data/tiingo/daily)$" \
  | xargs -I {} git checkout gold-swing/iter-001 -- {}
```

Resultado: 185 arquivos NOVOS commitados em main como `bab0095`,
**zero modificações** em outros lugares. Sister loop (~1.9M linhas
de iter 35/74/79 que a branch gold-swing teria sobrescrito por estar
desatualizada) ficou intocada.

Worktree `/tmp/ai-trade-gold-swing` removida (293 MB liberados).
Branch `gold-swing/iter-001` deletada — era toxic, e todo o valor
está agora em `bab0095` na main.

31/31 testes do gold_swing_loop passam. Baseline pytest preservado
(1058 tests collected em `tests/`).

## Lição estrutural (pra DEAD_ENDS futuro)

**Worktrees com symlinks absolutos NÃO podem ser squash-merged de
volta na main.** Quando um worktree é criado em `/tmp/...` e symlinks
com path absoluto apontam pra main, esses symlinks devem ser
**.gitignored** — nunca commitados. Caso contrário, qualquer merge
de volta gera autoreferência circular destrutiva.

**Sintoma a procurar antes de qualquer merge de branch antiga**:

```bash
git ls-tree -r BRANCH | awk '$1=="120000"'   # lista todos os symlinks
```

Se aparecer algo apontando pra `/var/www/...` ou outro path absoluto
do main, **abortar** o merge antes de tentar.

**Workflow correto pra preservar branches assim**: cherry-pick por
filtro de filename (`--diff-filter=A` + grep -v de paths suspeitos),
não squash merge.

## Estado atual

- Main no commit `bab0095`: gold_swing_loop preservado integralmente
  (specs, 25 iter dirs, FINAL_REPORT, scoring v1+v2, cost_models, 4
  helpers em scripts/src, 3 tests)
- BASE_MEMORY frontmatter:
  - `status: paused`
  - `paused_at: 2026-04-26 19:05`
  - `paused_reason: 0 winners after 25 iters across 2 phases; structurally limited; deferred`
  - `final_report: FINAL_REPORT.md`
- Worktree e branch deletadas. Reativação futura: ler
  `studies/gold_swing_loop/FINAL_REPORT.md` seção "Recommendations".

Sister loop (strategy_hunt_loop) intocado — iter 079 winner permanece.
Mandate §1 permanece **MAINTENANCE 100% Plano C**.

# Rodando o bestfolio_hunt_loop com codex-cli

Guia para executar o loop usando `codex exec` (OpenAI Codex CLI) em vez de
`claude -p`. O orquestrador é o mesmo `run_loop.sh`; apenas o backend muda.

---

## Pré-requisitos

```bash
# 1. codex-cli instalado (já confirmado: v0.125.0 nesta máquina)
codex --version

# 2. Chave OpenAI autenticada
codex login           # ou OPENAI_API_KEY exportada no shell

# 3. Dentro do repo
cd /var/www/pessoal/ai-trade
```

---

## AGENTS.md — o equivalente do CLAUDE.md para codex

`claude -p` auto-carrega `CLAUDE.md`. `codex exec` lê `AGENTS.md` no projeto.
Criar um `AGENTS.md` mínimo que redireciona para o arquivo principal:

```bash
cat > AGENTS.md << 'EOF'
# Project instructions for Codex

Read `CLAUDE.md` (this directory) before taking any action.
It contains mandatory rules: citation policy, jornada/ update rule,
investment mandate summary, and coding conventions.

The project working dir is `/var/www/pessoal/ai-trade`.
Use `uv run python` (not `python`) for all Python invocations.
Use `uv run pytest` for running tests.
EOF
```

> Esse arquivo só precisa ser criado uma vez. Não commitar a menos que
> o usuário decida. Fica no .gitignore local ou commita como `chore:`.

---

## Modelos disponíveis

| alias env | modelo OpenAI | equivalente claude | uso recomendado |
|---|---|---|---|
| `o4-mini` | `o4-mini` | sonnet | iterações rápidas, hipóteses simples |
| `o3` | `o3` | opus | hipóteses complexas, backtest com múltiplos configs |
| `gpt-4o` | `gpt-4o` | sonnet (não-reasoning) | fallback se o3/o4-mini caro |

**Recomendação**: `o4-mini` para as primeiras 3 iters (BAA-G12, NTSX+GDE+KMLM,
NTSX+GDE+RSST), que são implementações diretas de arquiteturas conhecidas.
`o3` para iters que exigem raciocínio econométrico mais profundo.

---

## Como rodar

### Script adaptado (recomendado)

```bash
# 5 iters, modelo o4-mini
CODEX_MODEL=o4-mini MAX_ITER=5 bash studies/bestfolio_hunt_loop/run_loop_codex.sh

# 3 iters, o3 (mais capaz, mais lento)
CODEX_MODEL=o3 MAX_ITER=3 bash studies/bestfolio_hunt_loop/run_loop_codex.sh

# Dry run (imprime prompt sem invocar codex)
DRY_RUN=1 bash studies/bestfolio_hunt_loop/run_loop_codex.sh
```

### Chamada manual de uma iteração

```bash
# Gera o prompt para a próxima iter e envia ao codex
cd /var/www/pessoal/ai-trade
NEXT_N=001   # ajustar conforme BASE_MEMORY.md total_iterations

PROMPT=$(sed \
  -e "s|{{ITERATION_N}}|$NEXT_N|g" \
  -e "s|{{STAMP}}|$(date +%Y-%m-%d-%H%M)|g" \
  studies/bestfolio_hunt_loop/PROMPT.md)

timeout 5400 codex exec \
  -m o4-mini \
  --full-auto \
  "$PROMPT" 2>&1 | tee logs/bestfolio_hunt_loop/iter_${NEXT_N}_manual.log
```

---

## Flags codex equivalentes às flags claude

| claude | codex exec | notas |
|---|---|---|
| `-p "$PROMPT"` | `"$PROMPT"` (argumento posicional) | ou `echo "$PROMPT" \| codex exec` |
| `--model opus` | `-m o3` | ver tabela de modelos acima |
| `--dangerously-skip-permissions` | `--full-auto` | sandbox workspace-write; suficiente para o loop |
| _(não existe)_ | `-s danger-full-access` | bypass total — só se `--full-auto` bloquear algo |

**Sobre `--full-auto`**: permite ao codex ler/escrever qualquer arquivo no workspace
e executar comandos shell — suficiente para `uv run python`, `pytest`, plot helpers,
edição de `BASE_MEMORY.md` e criação dos diretórios de iter. Não requer sandbox bypass.

---

## Diferenças comportamentais a conhecer

### 1. Auto-carregamento de contexto
- **claude**: lê `CLAUDE.md` automaticamente em cada sessão.
- **codex**: lê `AGENTS.md` automaticamente. Por isso o AGENTS.md acima é necessário.

### 2. Citações e mandatos
O `PROMPT.md` atual menciona "CLAUDE.md is auto-loaded". O codex lê isso na instrução
mas precisa que `AGENTS.md` exista para garantir o carregamento do `CLAUDE.md`.
Se quiser ter certeza, adicione ao começo do prompt gerado:

```
First action: read CLAUDE.md and confirm investment mandate is understood.
```

### 3. Modelos de raciocínio (o3/o4-mini)
`o3` e `o4-mini` são *reasoning models* — usam chain-of-thought interno antes de
responder. Para backtests isso é vantagem: lógica de gate-battery, PBO, DSR mais
confiável. Desvantagem: mais lento e caro que `o4-mini`.

### 4. git commit no fim do iter
O `run_loop_codex.sh` (como `run_loop.sh`) faz `git add -A && git commit` após cada
iter. O codex **nunca** commita — a instrução "NEVER git commit" no PROMPT.md vale
para ambos os backends.

### 5. Saída de progresso
`codex exec` produz saída estruturada no terminal. Para monitorar:

```bash
# Loop log
tail -f logs/bestfolio_hunt_loop/loop_*.log

# Iter atual
tail -f logs/bestfolio_hunt_loop/iter_001_*.log
```

---

## Variáveis de ambiente do run_loop_codex.sh

| var | default | descrição |
|---|---|---|
| `CODEX_MODEL` | `o4-mini` | modelo OpenAI a usar |
| `MAX_ITER` | `5` | número máximo de iterações |
| `ITER_TIMEOUT` | `5400` | segundos por iter (90 min) |
| `COOLDOWN` | `30` | segundos entre iters |
| `DRY_RUN` | `` | se não-vazio, apenas imprime prompt |

---

## Verificação após a 1ª iter completa

```bash
# Frontmatter atualizado?
head -10 studies/bestfolio_hunt_loop/BASE_MEMORY.md
# Espera: total_iterations: 1, latest_iteration: "001"

# Diretório de iter criado?
ls studies/bestfolio_hunt_loop/iterations/

# verdict.json gerado?
cat studies/bestfolio_hunt_loop/iterations/001-*/verdict.json | python3 -m json.tool | grep tier

# Commit automático feito?
git log --oneline -3
```

---

## Solução de problemas

### codex fica parado sem avançar
O modelo de raciocínio (o3) pode demorar. Verifique se há output no log:
```bash
tail -f logs/bestfolio_hunt_loop/iter_001_*.log
```
Se zero output por > 5 min, verificar se a chave OpenAI está válida:
```bash
codex exec -m o4-mini "echo hello"
```

### "permission denied" ao escrever arquivo
Usar `-s danger-full-access` em vez de `--full-auto`:
```bash
CODEX_EXTRA_FLAGS="-s danger-full-access" bash studies/bestfolio_hunt_loop/run_loop_codex.sh
```

### Timeout (exit 124)
Aumentar `ITER_TIMEOUT`:
```bash
ITER_TIMEOUT=7200 bash studies/bestfolio_hunt_loop/run_loop_codex.sh
```

### BASE_MEMORY.md não atualizado após iter
O codex falhou antes do Stage 5. Verificar log do iter, corrigir manualmente o
`total_iterations` no frontmatter, e reiniciar. O loop detecta o número via
`total_iterations` + contagem de dirs em `iterations/`.

---

## Retomando um loop interrompido

Se o loop foi killado mid-iter:
```bash
# 1. Verificar estado atual
head -10 studies/bestfolio_hunt_loop/BASE_MEMORY.md

# 2. Se total_iterations não foi incrementado (iter morreu antes do Stage 5):
#    - deletar o dir parcial da iter (se existir)
#    - rodar o loop novamente — ele vai retomar do mesmo número

ls studies/bestfolio_hunt_loop/iterations/
# se existir dir 001-* incompleto (sem verdict.json):
rm -rf studies/bestfolio_hunt_loop/iterations/001-*

# 3. Reiniciar
CODEX_MODEL=o4-mini MAX_ITER=5 bash studies/bestfolio_hunt_loop/run_loop_codex.sh
```

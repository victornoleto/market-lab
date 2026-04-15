---
description: Revisão adversarial multi-juiz de um spec/plan. Dispara 3 juízes em paralelo (engenharia, domínio, estratégia) + 1 árbitro que consolida. Veredito final: PROCEED / PROCEED-WITH-CHANGES / BLOCK.
argument-hint: <path-to-spec.md> [--focus "<lente adicional>"]
---

Execute a revisão adversarial multi-juiz do spec passado em `$ARGUMENTS`.

**Uso típico:**
```
/judge-spec docs/superpowers/specs/2026-04-15-tiingo-service-lazy-cache-design.md
/judge-spec docs/superpowers/plans/nome-do-plan.md --focus "custo Pepperstone swap"
```

---

## Parsing dos argumentos

`$ARGUMENTS` contém:

- **Primeiro token (obrigatório):** caminho relativo ao repo root para o spec/plan markdown a ser julgado. Ex.: `docs/superpowers/specs/2026-04-15-tiingo-service-lazy-cache-design.md`.
- **`--focus "<texto>"` (opcional):** lente adicional aplicada por TODOS os juízes. Útil quando há uma preocupação dominante para a rodada (ex.: `--focus "garantir que este spec não introduz débito para multi-day holds"`).

Se o primeiro token não existir como arquivo, pare imediatamente e reporte ao usuário.

---

## Passos

### 1. Validar e preparar diretório de relatórios

```bash
SPEC_PATH="<primeiro arg>"
test -f "$SPEC_PATH" || { echo "ERRO: $SPEC_PATH não existe"; exit 1; }
STAMP=$(date +%Y%m%d-%H%M%S)
BASENAME=$(basename "$SPEC_PATH" .md)
REPORT_DIR="reports/spec-judges/${BASENAME}-${STAMP}"
mkdir -p "$REPORT_DIR"
echo "$REPORT_DIR" > /tmp/judge-spec-dir.txt
```

Log unificado (padrão do projeto):
```bash
echo "[$(date '+%H:%M:%S')] judge-spec START — spec=$SPEC_PATH out=$REPORT_DIR" >> logs/judge-spec.log
```

### 2. Contexto obrigatório para os juízes

Antes de disparar agentes, **leia você mesmo** (o orquestrador) os arquivos abaixo e inclua um bloco de "Contexto estratégico" no prompt de cada juiz:

- `JORNADA.md` — seções "Onde estamos hoje", "O que vem a seguir", e as 2 últimas entradas datadas.
- `ROADMAP.md` — §"Current status" + §"Next steps".
- `.claude/CLAUDE.md` — regras invioláveis do projeto.

Se `--focus "<texto>"` foi passado, inclua-o **literalmente** (não reformule) numa seção "Lente desta rodada" no início do prompt de cada juiz.

### 3. Disparar 3 juízes EM PARALELO (uma única mensagem com 3 tool calls)

Cada juiz recebe:
- `spec_path`: caminho do spec a julgar.
- `report_path`: caminho onde ele deve escrever seu relatório (`$REPORT_DIR/<slug>.md`).
- `strategic_context`: bloco consolidado que você montou no passo 2 (JORNADA + ROADMAP + CLAUDE.md).
- `focus` (opcional): lente adicional se `--focus` foi usado.

**Dispatches paralelos:**

| Agente | `subagent_type` | Relatório |
|---|---|---|
| Juiz Engenharia | `spec-judge-methodology` | `$REPORT_DIR/methodology.md` |
| Juiz Domínio | `spec-judge-domain` | `$REPORT_DIR/domain.md` |
| Juiz Estratégia | `spec-judge-strategic` | `$REPORT_DIR/strategic.md` |

Os três devem rodar concorrentemente — invoque o Agent tool 3 vezes numa única mensagem. Todos usam `model: opus` (nuance estratégica + análise técnica requer).

**Prompt template para cada juiz** (o próprio agente adapta com sua persona):

```
Você é `<subagent_type>`. Leia o spec em `<spec_path>` e produza um relatório
adversarial em `<report_path>`.

## Contexto estratégico do projeto (OBRIGATÓRIO ler antes de julgar)

<conteúdo agregado de JORNADA + ROADMAP + CLAUDE.md que o orquestrador preparou>

## Lente desta rodada (se houver)

<conteúdo de --focus, literal>

## Instruções

Siga seu próprio persona (definido em `.claude/agents/<subagent_type>.md`).
Respeite o formato de output ali especificado (veredito + preocupações +
sugestões). Escreva o relatório em `<report_path>` antes de retornar.
Retorne ao orquestrador apenas um resumo de 5-10 linhas + o veredito ∈
{PROCEED, PROCEED-WITH-CHANGES, BLOCK}.
```

### 4. Disparar o árbitro

Após os 3 juízes retornarem, dispare `spec-judge-arbiter`:

- `spec_path`: mesmo do passo 3.
- `report_dir`: `$REPORT_DIR` (ele lerá os 3 relatórios de lá).
- `arbiter_path`: `$REPORT_DIR/arbiter.md` (onde escrever a consolidação).

O árbitro lê os 3 relatórios + o spec original, sintetiza, escreve `arbiter.md`, retorna **UM veredito final** ∈ {PROCEED, PROCEED-WITH-CHANGES, BLOCK} + lista consolidada de ações (se CHANGES) ou razões de bloqueio (se BLOCK).

### 5. Apresentar ao usuário

Reporte ao usuário:

```
## Veredito final do árbitro: <PROCEED | PROCEED-WITH-CHANGES | BLOCK>

### Resumo
<2-3 linhas do arbiter.md>

### Ações consolidadas (se CHANGES)
<lista ordenada por criticidade>

### Relatórios individuais
- Engenharia: $REPORT_DIR/methodology.md — veredito <X>
- Domínio:    $REPORT_DIR/domain.md      — veredito <Y>
- Estratégia: $REPORT_DIR/strategic.md   — veredito <Z>
- Árbitro:    $REPORT_DIR/arbiter.md
```

**Nunca** modifique o spec automaticamente — o usuário decide se aceita as mudanças sugeridas.

Log final:
```bash
echo "[$(date '+%H:%M:%S')] judge-spec END — verdict=<final>" >> logs/judge-spec.log
```

---

## Regras invioláveis

1. **Juízes rodam em paralelo.** 3 Agent tool calls numa ÚNICA mensagem. Nunca sequencialmente.
2. **Árbitro roda depois dos 3.** Espere todos retornarem antes de disparar.
3. **Nenhum juiz modifica o spec.** Eles escrevem apenas relatórios em `$REPORT_DIR`.
4. **Contexto estratégico é obrigatório.** Se você (orquestrador) não leu JORNADA+ROADMAP+CLAUDE.md, os juízes não recebem contexto e o veredito é inútil.
5. **`--focus` se aplica a TODOS os juízes.** Não filtre por persona.
6. **Relatórios ficam no disco** para o usuário inspecionar depois; não são ephemeral.
7. **Veredito final é do árbitro**, não média dos juízes. Se árbitro diverge de unanimidade dos juízes (improvável), ele justifica na `arbiter.md`.

#!/usr/bin/env bash
# Resumable R1 re-decode loop for MyFxBook systems.
#
# Purpose
# -------
# Run one clean Claude Code Opus validation per system, outside the long-lived
# interactive session. This reduces prompt/session bloat and makes retries
# deterministic. The AI does the semantic reverse-engineering; Python checks the
# deterministic contract afterwards (closed taxonomy, UNCAT reason_code, hashes).
#
# Note: this intentionally does NOT pass `--agent decoder` by default because
# `.claude/agents/decoder.md` currently declares `model: sonnet`. The prompt still
# instructs Claude to read and follow that agent spec, while `--model opus` remains
# the actual model for the isolated run.
#
# This script intentionally writes only systems/<id>/signal_rule.md. It does NOT
# promote to frozen_rules/. Promotion remains a separate audited step via
# scripts/promote_signal_to_frozen.py after a wave is complete.
#
# Usage examples
# --------------
#   studies/myfxbook_reverse_engineering/scripts/r1_redecode_loop.sh --dry-run
#   studies/myfxbook_reverse_engineering/scripts/r1_redecode_loop.sh --limit 5
#   studies/myfxbook_reverse_engineering/scripts/r1_redecode_loop.sh --systems 10067081 10192401
#   studies/myfxbook_reverse_engineering/scripts/r1_redecode_loop.sh --force --systems 10067081
#
# State/logs
# ----------
#   _diagnostics/r1_redecode_loop/status.tsv
#   _diagnostics/r1_redecode_loop/logs/<system_id>.json
#   _diagnostics/r1_redecode_loop/prompts/<system_id>.txt
#
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
STUDY_DIR="$ROOT/studies/myfxbook_reverse_engineering"
STATE_DIR="$STUDY_DIR/_diagnostics/r1_redecode_loop"
LOG_DIR="$STATE_DIR/logs"
PROMPT_DIR="$STATE_DIR/prompts"
STATUS_FILE="$STATE_DIR/status.tsv"
MANIFEST="$STUDY_DIR/_diagnostics/R1_pre_manifest.json"

MODEL="opus"
EFFORT="high"
TIMEOUT_SECONDS=1800
MAX_BUDGET_USD=""
LIMIT=0
DRY_RUN=0
FORCE=0
SYSTEMS=()

usage() {
  sed -n '1,48p' "$0"
  cat <<'EOF'

Options
  --systems ID...       Explicit system IDs. If omitted, uses _diagnostics/R1_pre_manifest.json.
  --limit N             Process at most N not-done systems.
  --force               Re-run even if state/current hash says DONE.
  --dry-run             Show what would run; no Claude calls.
  --model NAME          Claude model alias/name (default: opus). Default does not use --agent decoder.
  --effort LEVEL        Claude effort (default: high).
  --timeout SECONDS     Per-system hard timeout (default: 1800).
  --max-budget-usd USD  Optional Claude Code per-call budget.
  -h, --help            Show help.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --systems)
      shift
      while [[ $# -gt 0 && "$1" != --* ]]; do
        SYSTEMS+=("$1")
        shift
      done
      ;;
    --limit)
      LIMIT="$2"
      shift 2
      ;;
    --force)
      FORCE=1
      shift
      ;;
    --dry-run)
      DRY_RUN=1
      shift
      ;;
    --model)
      MODEL="$2"
      shift 2
      ;;
    --effort)
      EFFORT="$2"
      shift 2
      ;;
    --timeout)
      TIMEOUT_SECONDS="$2"
      shift 2
      ;;
    --max-budget-usd)
      MAX_BUDGET_USD="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

load_manifest_systems() {
  uv run python - <<'PY'
import json
from pathlib import Path

manifest = Path("studies/myfxbook_reverse_engineering/_diagnostics/R1_pre_manifest.json")
data = json.loads(manifest.read_text())
for item in data["items"]:
    print(item["system_id"])
PY
}

if [[ ${#SYSTEMS[@]} -eq 0 ]]; then
  if [[ ! -f "$MANIFEST" ]]; then
    echo "Missing manifest: $MANIFEST. Provide --systems explicitly." >&2
    exit 1
  fi
  mapfile -t SYSTEMS < <(cd "$ROOT" && load_manifest_systems)
fi

latest_status() {
  local sid="$1"
  if [[ ! -f "$STATUS_FILE" ]]; then
    printf ''
    return 0
  fi
  awk -F '\t' -v sid="$sid" '$2 == sid { status=$3 } END { print status }' "$STATUS_FILE"
}

current_signal_sha() {
  local sid="$1"
  local path="$STUDY_DIR/systems/$sid/signal_rule.md"
  if [[ ! -f "$path" ]]; then
    printf ''
    return 0
  fi
  sha256sum "$path" | awk '{print $1}'
}

pre_signal_sha() {
  local sid="$1"
  (cd "$ROOT" && uv run python - "$sid" <<'PY'
import json
import sys
from pathlib import Path

sid = sys.argv[1]
manifest = Path("studies/myfxbook_reverse_engineering/_diagnostics/R1_pre_manifest.json")
data = json.loads(manifest.read_text())
for item in data["items"]:
    if item["system_id"] == sid:
        print(item.get("signal_rule_sha256", ""))
        break
PY
  )
}

validate_signal_rule() {
  local sid="$1"
  (cd "$ROOT" && uv run python - "$sid" <<'PY'
import re
import sys
from pathlib import Path

from studies.myfxbook_reverse_engineering.shared.decoder_taxonomy import (
    TaxonomyError,
    validate_decoder_output,
)

sid = sys.argv[1]
path = Path("studies/myfxbook_reverse_engineering") / "systems" / sid / "signal_rule.md"
if not path.exists():
    print("missing signal_rule.md")
    raise SystemExit(1)
text = path.read_text()
m = re.search(r"^---\n(.*?)\n---", text, re.DOTALL | re.MULTILINE)
if not m:
    print("missing YAML front matter")
    raise SystemExit(1)
block = m.group(1)

def field(key: str) -> str | None:
    found = re.search(rf"^{key}:\s*(\S+)", block, re.MULTILINE)
    if not found:
        return None
    value = found.group(1).strip()
    if value in {"null", "None", "~", "\"\"", "''"}:
        return None
    return value

try:
    fam = validate_decoder_output(
        family=field("family") or "?",
        reason_code=field("reason_code"),
        candidate_new_family=field("candidate_new_family"),
        strict=True,
    )
except TaxonomyError as exc:
    print(str(exc).splitlines()[0])
    raise SystemExit(1)
print(fam.value)
PY
  )
}

is_done() {
  local sid="$1"
  [[ "$FORCE" -eq 1 ]] && return 1

  if [[ "$(latest_status "$sid")" == "DONE" ]]; then
    return 0
  fi

  local cur pre
  cur="$(current_signal_sha "$sid")"
  pre="$(pre_signal_sha "$sid")"
  if [[ -n "$cur" && -n "$pre" && "$cur" != "$pre" ]]; then
    if validate_signal_rule "$sid" >/dev/null 2>&1; then
      return 0
    fi
  fi
  return 1
}

write_prompt() {
  local sid="$1"
  local prompt_file="$PROMPT_DIR/$sid.txt"
  cat > "$prompt_file" <<EOF
Execute a clean R1 Opus re-decode for MyFxBook system $sid.

Mandatory context:
- Read /var/www/pessoal/ai-trade/CLAUDE.md first.
- Read studies/myfxbook_reverse_engineering/_diagnostics/5R-1-hardening.md.
- Read studies/myfxbook_reverse_engineering/shared/decoder_taxonomy.py and obey the closed enum.
- Follow .claude/agents/decoder.md workflow and output schema.

Task:
1. Read, in order:
   - studies/myfxbook_reverse_engineering/systems/$sid/decoder/fingerprint.md
   - studies/myfxbook_reverse_engineering/systems/$sid/decoder/candidates.json
   - studies/myfxbook_reverse_engineering/systems/$sid/system_info.json
2. Reclassify the system using the closed Family enum only.
3. Write exactly one file: studies/myfxbook_reverse_engineering/systems/$sid/signal_rule.md
4. Do not edit frozen_rules/, CHANGELOG.md, ROADMAP.md, jornada/, or any shared code.
5. If the pattern is outside the enum, use:
   family: UNCATEGORIZED
   reason_code: taxonomy_gap
   candidate_new_family: <PROPOSED_NAME>
6. If family is UNCATEGORIZED for any other reason, include reason_code from UncatReason.
7. Do not invent citations. Read the cited books/summaries files before citing.
8. If the fingerprint suggests news/event behavior (name flag, clock-anchor, p50 hold <5min), classify only from the observed trade/OHLC evidence. Do not assume a live economic-calendar/news-reading implementation. Add an Open Question or risk_flag for calendar-aware replication if relevant.
9. If p50 hold <5min or the timing is sub-M5 sensitive, add risk_flag: needs_m1_review. Do not change the project timeframe or any code.
10. End your response with a 5-line summary: family, confidence, reason_code/candidate_new_family if any, top evidence, files written.

This is one isolated non-interactive validation run. Do not continue to another system.
EOF
  printf '%s' "$prompt_file"
}

record_status() {
  local sid="$1"
  local status="$2"
  local sha="$3"
  local note="$4"
  printf '%s\t%s\t%s\t%s\t%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$sid" "$status" "$sha" "$note" >> "$STATUS_FILE"
}

run_one() {
  local sid="$1"
  local prompt_file log_file sha note claude_status validate_output
  prompt_file="$(write_prompt "$sid")"
  log_file="$LOG_DIR/$sid.json"

  echo "==> $sid: running Claude ($MODEL, effort=$EFFORT, timeout=${TIMEOUT_SECONDS}s)"
  set +e
  if [[ -n "$MAX_BUDGET_USD" ]]; then
    timeout "$TIMEOUT_SECONDS" claude -p \
      --model "$MODEL" \
      --effort "$EFFORT" \
      --no-session-persistence \
      --permission-mode acceptEdits \
      --allowedTools Read,Write,Bash,Grep,Glob \
      --output-format json \
      --max-budget-usd "$MAX_BUDGET_USD" \
      "$(< "$prompt_file")" > "$log_file" 2>&1
  else
    timeout "$TIMEOUT_SECONDS" claude -p \
      --model "$MODEL" \
      --effort "$EFFORT" \
      --no-session-persistence \
      --permission-mode acceptEdits \
      --allowedTools Read,Write,Bash,Grep,Glob \
      --output-format json \
      "$(< "$prompt_file")" > "$log_file" 2>&1
  fi
  claude_status=$?
  set -e

  sha="$(current_signal_sha "$sid")"
  if [[ "$claude_status" -ne 0 ]]; then
    note="claude_exit_$claude_status"
    record_status "$sid" "FAILED" "$sha" "$note"
    echo "    FAILED: $note (log: $log_file)"
    return 1
  fi

  set +e
  validate_output="$(validate_signal_rule "$sid" 2>&1)"
  claude_status=$?
  set -e
  if [[ "$claude_status" -ne 0 ]]; then
    note="taxonomy_validation_failed: ${validate_output//$'\n'/ }"
    record_status "$sid" "FAILED" "$sha" "$note"
    echo "    FAILED: $note"
    return 1
  fi

  record_status "$sid" "DONE" "$sha" "family=$validate_output"
  echo "    DONE: family=$validate_output sha=${sha:0:12}"
  return 0
}

main() {
  cd "$ROOT"
  if [[ "$DRY_RUN" -eq 0 ]]; then
    mkdir -p "$LOG_DIR" "$PROMPT_DIR"
    if [[ ! -f "$STATUS_FILE" ]]; then
      printf 'timestamp\tsystem_id\tstatus\tsha256\tnote\n' > "$STATUS_FILE"
    fi
  fi
  echo "R1 re-decode loop"
  echo "Root: $ROOT"
  echo "Systems requested: ${#SYSTEMS[@]}"
  echo "State: $STATUS_FILE"

  local processed=0 failures=0 skipped=0
  for sid in "${SYSTEMS[@]}"; do
    if is_done "$sid"; then
      echo "==> $sid: SKIP (already DONE or changed+strict-valid)"
      skipped=$((skipped + 1))
      continue
    fi

    if [[ "$LIMIT" -gt 0 && "$processed" -ge "$LIMIT" ]]; then
      echo "Limit reached ($LIMIT)."
      break
    fi

    if [[ "$DRY_RUN" -eq 1 ]]; then
      echo "==> $sid: WOULD_RUN"
      processed=$((processed + 1))
      continue
    fi

    if run_one "$sid"; then
      processed=$((processed + 1))
    else
      failures=$((failures + 1))
    fi
  done

  echo
  echo "Summary: processed=$processed skipped=$skipped failures=$failures"
  echo "Next audited step after a complete wave: validate then promote with scripts/promote_signal_to_frozen.py."
  [[ "$failures" -eq 0 ]]
}

main "$@"

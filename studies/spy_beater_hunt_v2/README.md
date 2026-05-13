# spy_beater_hunt_v2

Autonomous long-term strategy hunt started on 2026-05-13.

Mission: find a long-term strategy that beats SPY buy-and-hold and passes the
project's overfit gates: PBO, DSR, walk-forward, OOS, forward stress,
bootstrap, and cross-library checks `[advances_fin_ml, p.196-202]`,
`[advances_fin_ml, p.208-211]`, `[advances_fin_ml, p.222-223]`.

This study is research-only. It does not change mandate capital allocation;
`docs/investment-mandate.md` remains canonical.

## Files

| file | purpose |
|---|---|
| `MEMORY.md` | Short state read first by every fresh agent session |
| `SPEC.md` | Objective, gates, benchmark and kill rules |
| `LOOP_PROTOCOL.md` | Per-iteration operational contract |
| `LOOP_PROMPT.md` | Prompt injected into each clean OpenCode/GPT-5.5 session |
| `loop.sh` | Multi-iteration shell orchestrator |
| `iterations/` | One directory per autonomous iteration |

## Run

```bash
BACKEND=opencode OPENCODE_MODEL=openai/gpt-5.5 MAX_ITER=10 ITER_TIMEOUT=7200 \
  bash studies/spy_beater_hunt_v2/loop.sh
```

Use `DRY_RUN=1` to inspect the next prompt without launching an agent.

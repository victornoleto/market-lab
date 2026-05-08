# LETF Rotation Hunt

5-tier exploratory study testing whether LETF rotation strategies based on
EMA/SMA + composite indicators (VIX, AR(1), HMM, vol-gate, EWMAC, Clenow)
produce a deploy-quality strategy.

**Design spec:** pre-publication agent spec removed from the public tree; the
study protocol is preserved in `BASE_MEMORY.md`, `KILL_RULES.md`, `PROMPT.md`
and the per-iteration reports.

## Tier overview

| Tier | Hypothesis | Iters | Configs |
|------|-----------|-------|---------|
| T1 | Gayed replication (single LETF + SMA/EMA + binary OFF) | 3 | 22 |
| T2 | HFEA-binary basket (multi-asset risk-on) | 6 | 11 |
| T3 | Composite signal (SMA + VIX/AR1/vol-gate/Vote-K/HMM) | 4-5 | 6 |
| T4 | Cross-sectional rotation (Clenow / EWMAC ranking) | 4 | 4 |
| T5 | Continuous vol-target (Carver EWMAC) | 3-4 | 4 |

Total expected: ~21-23 iters / ~48 configs.

## Key files

- `BASE_MEMORY.md` — incumbent + iter log + state-of-now (single source of truth)
- `WINNER_AND_RANKING.md` — scoring rubric + tier mapping
- `KILL_RULES.md` — pre-registered KILL conditions
- `PROMPT.md` — protocol per iter
- `INFRASTRUCTURE.md` — engine wiring + reuse map
- `run_iter.py` — entry point per iter

## Quick start (after Phase 0 setup complete)

```bash
# Run iter 000 (synth parity validation gate)
python -m studies.letf_rotation_hunt.run_iter --iter 000 --config configs/iter_000_synth_parity.yaml

# Run iter 001 (T1a LETF sweep)
python -m studies.letf_rotation_hunt.run_iter --iter 001 --config configs/iter_001_t1a_letf_sweep.yaml
```

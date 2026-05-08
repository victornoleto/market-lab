# Validation report — system 10814265

Generated: 2026-05-02T05:56:18+00:00
Elapsed: 331.2s

## Overall: ✅ PASS

- **Family:** `MARTINGALE_GRID` (confidence 0.82)
- **Reliability score:** **0.300 (LOW)**
- **Trades / pairs:** 957 / 3
- **Last trade:** 2025-04-04 13:44:52+00:00
- **Account type:** Real

## Pipeline status

- Pre-check: ✅ — 957 trades, pair coverage 100%
- Stage 1 (features + candidates): ✅ — Stage 1 OK
- Stage 2 (LLM family naming): ✅ — Stage 2 OK

## Reliability components

| component | weight | value |
|---|---:|---:|
| direction_predictability | 0.25 | 1.000 |
| family_clarity | 0.20 | 0.820 |
| timing_concentration | 0.20 | 0.358 |
| sanity_pass | 0.10 | 0.000 |
| age_freshness | 0.10 | 0.785 |
| vendor_quality | 0.10 | 0.850 |
| pair_coverage | 0.05 | 1.000 |

## Notes

- sanity FAIL — martingale signature detected
- forced LOW: martingale/grid signature

## Linked artifacts

- Fingerprint: `studies/myfxbook_reverse_engineering/systems/10814265/decoder/fingerprint.md`
- Candidates: `studies/myfxbook_reverse_engineering/systems/10814265/decoder/candidates.json`
- Signal rule: `studies/myfxbook_reverse_engineering/systems/10814265/signal_rule.md`


# Validation report — system 8397136

Generated: 2026-05-02T11:40:10+00:00
Elapsed: 212.0s

## Overall: ✅ PASS

- **Family:** `UNCATEGORIZED` (confidence 0.38)
- **Reliability score:** **0.533 (LOW)**
- **Trades / pairs:** 432 / 2
- **Last trade:** 2021-06-16 21:01:04+00:00
- **Account type:** Real

## Pipeline status

- Pre-check: ✅ — 432 trades, pair coverage 100%
- Stage 1 (features + candidates): ✅ — Stage 1 OK
- Stage 2 (LLM family naming): ✅ — Stage 2 OK

## Reliability components

| component | weight | value |
|---|---:|---:|
| direction_predictability | 0.25 | 0.333 |
| family_clarity | 0.20 | 0.380 |
| timing_concentration | 0.20 | 0.731 |
| sanity_pass | 0.10 | 1.000 |
| age_freshness | 0.10 | 0.024 |
| vendor_quality | 0.10 | 0.750 |
| pair_coverage | 0.05 | 1.000 |

## Notes

- UNCATEGORIZED family demotes to LOW band

## Linked artifacts

- Fingerprint: `studies/myfxbook_reverse_engineering/systems/8397136/decoder/fingerprint.md`
- Candidates: `studies/myfxbook_reverse_engineering/systems/8397136/decoder/candidates.json`
- Signal rule: `studies/myfxbook_reverse_engineering/systems/8397136/signal_rule.md`


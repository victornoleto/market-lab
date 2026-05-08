# Validation report — system 8574205

Generated: 2026-05-02T12:13:07+00:00
Elapsed: 1977.8s

## Overall: ✅ PASS

- **Family:** `UNCATEGORIZED` (confidence 0.28)
- **Reliability score:** **0.499 (LOW)**
- **Trades / pairs:** 3994 / 5
- **Last trade:** 2026-05-01 17:21:35+00:00
- **Account type:** Real

## Pipeline status

- Pre-check: ✅ — 3994 trades, pair coverage 100%
- Stage 1 (features + candidates): ✅ — Stage 1 OK
- Stage 2 (LLM family naming): ✅ — Stage 2 OK

## Reliability components

| component | weight | value |
|---|---:|---:|
| direction_predictability | 0.25 | 0.195 |
| family_clarity | 0.20 | 0.280 |
| timing_concentration | 0.20 | 0.224 |
| sanity_pass | 0.10 | 1.000 |
| age_freshness | 0.10 | 1.000 |
| vendor_quality | 0.10 | 1.000 |
| pair_coverage | 0.05 | 1.000 |

## Notes

- UNCATEGORIZED family demotes to LOW band

## Linked artifacts

- Fingerprint: `studies/myfxbook_reverse_engineering/systems/8574205/decoder/fingerprint.md`
- Candidates: `studies/myfxbook_reverse_engineering/systems/8574205/decoder/candidates.json`
- Signal rule: `studies/myfxbook_reverse_engineering/systems/8574205/signal_rule.md`


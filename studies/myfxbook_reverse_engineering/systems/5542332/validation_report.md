# Validation report — system 5542332

Generated: 2026-05-02T10:14:48+00:00
Elapsed: 521.7s

## Overall: ✅ PASS

- **Family:** `UNCATEGORIZED` (confidence 0.35)
- **Reliability score:** **0.408 (LOW)**
- **Trades / pairs:** 3995 / 8
- **Last trade:** 2021-06-16 10:05:43+00:00
- **Account type:** Real

## Pipeline status

- Pre-check: ✅ — 3995 trades, pair coverage 100%
- Stage 1 (features + candidates): ✅ — Stage 1 OK
- Stage 2 (LLM family naming): ✅ — Stage 2 OK

## Reliability components

| component | weight | value |
|---|---:|---:|
| direction_predictability | 0.25 | 0.126 |
| family_clarity | 0.20 | 0.350 |
| timing_concentration | 0.20 | 0.273 |
| sanity_pass | 0.10 | 1.000 |
| age_freshness | 0.10 | 0.024 |
| vendor_quality | 0.10 | 1.000 |
| pair_coverage | 0.05 | 1.000 |

## Notes

- UNCATEGORIZED family demotes to LOW band

## Linked artifacts

- Fingerprint: `studies/myfxbook_reverse_engineering/systems/5542332/decoder/fingerprint.md`
- Candidates: `studies/myfxbook_reverse_engineering/systems/5542332/decoder/candidates.json`
- Signal rule: `studies/myfxbook_reverse_engineering/systems/5542332/signal_rule.md`


# Validation report — system 2123808

Generated: 2026-05-02T09:00:20+00:00
Elapsed: 2834.9s

## Overall: ✅ PASS

- **Family:** `UNCATEGORIZED` (confidence 0.38)
- **Reliability score:** **0.452 (LOW)**
- **Trades / pairs:** 856 / 5
- **Last trade:** 2021-06-15 14:30:55+00:00
- **Account type:** Real

## Pipeline status

- Pre-check: ✅ — 856 trades, pair coverage 100%
- Stage 1 (features + candidates): ✅ — Stage 1 OK
- Stage 2 (LLM family naming): ✅ — Stage 2 OK

## Reliability components

| component | weight | value |
|---|---:|---:|
| direction_predictability | 0.25 | 0.332 |
| family_clarity | 0.20 | 0.380 |
| timing_concentration | 0.20 | 0.277 |
| sanity_pass | 0.10 | 1.000 |
| age_freshness | 0.10 | 0.024 |
| vendor_quality | 0.10 | 0.850 |
| pair_coverage | 0.05 | 1.000 |

## Notes

- UNCATEGORIZED family demotes to LOW band

## Linked artifacts

- Fingerprint: `studies/myfxbook_reverse_engineering/systems/2123808/decoder/fingerprint.md`
- Candidates: `studies/myfxbook_reverse_engineering/systems/2123808/decoder/candidates.json`
- Signal rule: `studies/myfxbook_reverse_engineering/systems/2123808/signal_rule.md`


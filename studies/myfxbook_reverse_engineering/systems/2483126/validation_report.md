# Validation report — system 2483126

Generated: 2026-05-02T09:53:44+00:00
Elapsed: 1377.3s

## Overall: ✅ PASS

- **Family:** `UNCATEGORIZED` (confidence 0.22)
- **Reliability score:** **0.399 (LOW)**
- **Trades / pairs:** 1910 / 5
- **Last trade:** 2021-06-16 21:01:13+00:00
- **Account type:** Real

## Pipeline status

- Pre-check: ✅ — 1910 trades, pair coverage 100%
- Stage 1 (features + candidates): ✅ — Stage 1 OK
- Stage 2 (LLM family naming): ✅ — Stage 2 OK

## Reliability components

| component | weight | value |
|---|---:|---:|
| direction_predictability | 0.25 | 0.222 |
| family_clarity | 0.20 | 0.220 |
| timing_concentration | 0.20 | 0.236 |
| sanity_pass | 0.10 | 1.000 |
| age_freshness | 0.10 | 0.024 |
| vendor_quality | 0.10 | 1.000 |
| pair_coverage | 0.05 | 1.000 |

## Notes

- UNCATEGORIZED family demotes to LOW band

## Linked artifacts

- Fingerprint: `studies/myfxbook_reverse_engineering/systems/2483126/decoder/fingerprint.md`
- Candidates: `studies/myfxbook_reverse_engineering/systems/2483126/decoder/candidates.json`
- Signal rule: `studies/myfxbook_reverse_engineering/systems/2483126/signal_rule.md`


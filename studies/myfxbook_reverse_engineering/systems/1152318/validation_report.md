# Validation report — system 1152318

Generated: 2026-05-02T07:21:20+00:00
Elapsed: 2798.3s

## Overall: ✅ PASS

- **Family:** `UNCATEGORIZED` (confidence 0.62)
- **Reliability score:** **0.669 (HIGH)**
- **Trades / pairs:** 1637 / 2
- **Last trade:** 2021-06-01 02:31:00+00:00
- **Account type:** Real

## Pipeline status

- Pre-check: ✅ — 1637 trades, pair coverage 100%
- Stage 1 (features + candidates): ✅ — Stage 1 OK
- Stage 2 (LLM family naming): ✅ — Stage 2 OK

## Reliability components

| component | weight | value |
|---|---:|---:|
| direction_predictability | 0.25 | 0.976 |
| family_clarity | 0.20 | 0.620 |
| timing_concentration | 0.20 | 0.246 |
| sanity_pass | 0.10 | 1.000 |
| age_freshness | 0.10 | 0.016 |
| vendor_quality | 0.10 | 1.000 |
| pair_coverage | 0.05 | 1.000 |

## Linked artifacts

- Fingerprint: `studies/myfxbook_reverse_engineering/systems/1152318/decoder/fingerprint.md`
- Candidates: `studies/myfxbook_reverse_engineering/systems/1152318/decoder/candidates.json`
- Signal rule: `studies/myfxbook_reverse_engineering/systems/1152318/signal_rule.md`


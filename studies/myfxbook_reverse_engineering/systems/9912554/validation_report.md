# Validation report — system 9912554

Generated: 2026-05-02T14:26:27+00:00
Elapsed: 451.1s

## Overall: ✅ PASS

- **Family:** `OVERLAP_NY_LONDON_RANGE` (confidence 0.57)
- **Reliability score:** **0.779 (HIGH)**
- **Trades / pairs:** 103 / 1
- **Last trade:** 2026-04-30 17:56:20+00:00
- **Account type:** Real

## Pipeline status

- Pre-check: ✅ — 103 trades, pair coverage 100%
- Stage 1 (features + candidates): ✅ — Stage 1 OK
- Stage 2 (LLM family naming): ✅ — Stage 2 OK

## Reliability components

| component | weight | value |
|---|---:|---:|
| direction_predictability | 0.25 | 0.718 |
| family_clarity | 0.20 | 0.570 |
| timing_concentration | 0.20 | 0.854 |
| sanity_pass | 0.10 | 1.000 |
| age_freshness | 0.10 | 0.999 |
| vendor_quality | 0.10 | 0.650 |
| pair_coverage | 0.05 | 1.000 |

## Linked artifacts

- Fingerprint: `studies/myfxbook_reverse_engineering/systems/9912554/decoder/fingerprint.md`
- Candidates: `studies/myfxbook_reverse_engineering/systems/9912554/decoder/candidates.json`
- Signal rule: `studies/myfxbook_reverse_engineering/systems/9912554/signal_rule.md`


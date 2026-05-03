# Validation report — system 10067081

Generated: 2026-05-02T04:10:41+00:00
Elapsed: 1263.9s

## Overall: ✅ PASS

- **Family:** `UNCATEGORIZED` (confidence 0.43)
- **Reliability score:** **0.551 (MEDIUM)**
- **Trades / pairs:** 4000 / 6
- **Last trade:** 2026-04-30 22:10:51+00:00
- **Account type:** Real

## Pipeline status

- Pre-check: ✅ — 4000 trades, pair coverage 100%
- Stage 1 (features + candidates): ✅ — Stage 1 OK
- Stage 2 (LLM family naming): ✅ — Stage 2 OK

## Reliability components

| component | weight | value |
|---|---:|---:|
| direction_predictability | 0.25 | 0.258 |
| family_clarity | 0.20 | 0.430 |
| timing_concentration | 0.20 | 0.254 |
| sanity_pass | 0.10 | 1.000 |
| age_freshness | 0.10 | 0.999 |
| vendor_quality | 0.10 | 1.000 |
| pair_coverage | 0.05 | 1.000 |

## Linked artifacts

- Fingerprint: `studies/myfxbook_reverse_engineering/systems/10067081/decoder/fingerprint.md`
- Candidates: `studies/myfxbook_reverse_engineering/systems/10067081/decoder/candidates.json`
- Signal rule: `studies/myfxbook_reverse_engineering/systems/10067081/signal_rule.md`


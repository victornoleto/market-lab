# Validation report — system 10475089

Generated: 2026-05-02T05:09:45+00:00
Elapsed: 370.1s

## Overall: ✅ PASS

- **Family:** `UNCATEGORIZED` (confidence 0.38)
- **Reliability score:** **0.703 (HIGH)**
- **Trades / pairs:** 117 / 1
- **Last trade:** 2024-07-17 10:23:50+00:00
- **Account type:** Real

## Pipeline status

- Pre-check: ✅ — 117 trades, pair coverage 100%
- Stage 1 (features + candidates): ✅ — Stage 1 OK
- Stage 2 (LLM family naming): ✅ — Stage 2 OK

## Reliability components

| component | weight | value |
|---|---:|---:|
| direction_predictability | 0.25 | 0.598 |
| family_clarity | 0.20 | 0.380 |
| timing_concentration | 0.20 | 0.991 |
| sanity_pass | 0.10 | 1.000 |
| age_freshness | 0.10 | 0.642 |
| vendor_quality | 0.10 | 0.650 |
| pair_coverage | 0.05 | 1.000 |

## Linked artifacts

- Fingerprint: `studies/myfxbook_reverse_engineering/systems/10475089/decoder/fingerprint.md`
- Candidates: `studies/myfxbook_reverse_engineering/systems/10475089/decoder/candidates.json`
- Signal rule: `studies/myfxbook_reverse_engineering/systems/10475089/signal_rule.md`


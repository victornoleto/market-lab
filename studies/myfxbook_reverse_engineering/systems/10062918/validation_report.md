# Validation report — system 10062918

Generated: 2026-05-02T03:49:37+00:00
Elapsed: 1273.8s

## Overall: ✅ PASS

- **Family:** `UNCATEGORIZED` (confidence 0.52)
- **Reliability score:** **0.730 (HIGH)**
- **Trades / pairs:** 731 / 2
- **Last trade:** 2025-11-19 03:05:22+00:00
- **Account type:** Real

## Pipeline status

- Pre-check: ✅ — 731 trades, pair coverage 100%
- Stage 1 (features + candidates): ✅ — Stage 1 OK
- Stage 2 (LLM family naming): ✅ — Stage 2 OK

## Reliability components

| component | weight | value |
|---|---:|---:|
| direction_predictability | 0.25 | 1.000 |
| family_clarity | 0.20 | 0.520 |
| timing_concentration | 0.20 | 0.252 |
| sanity_pass | 0.10 | 1.000 |
| age_freshness | 0.10 | 0.910 |
| vendor_quality | 0.10 | 0.850 |
| pair_coverage | 0.05 | 1.000 |

## Linked artifacts

- Fingerprint: `studies/myfxbook_reverse_engineering/systems/10062918/decoder/fingerprint.md`
- Candidates: `studies/myfxbook_reverse_engineering/systems/10062918/decoder/candidates.json`
- Signal rule: `studies/myfxbook_reverse_engineering/systems/10062918/signal_rule.md`


# Validation report — system 11171596

Generated: 2026-05-02T06:13:24+00:00
Elapsed: 417.7s

## Overall: ✅ PASS

- **Family:** `NY_SESSION_REVERSAL` (confidence 0.62)
- **Reliability score:** **0.850 (HIGH)**
- **Trades / pairs:** 1083 / 2
- **Last trade:** 2026-03-13 10:18:14+00:00
- **Account type:** Real

## Pipeline status

- Pre-check: ✅ — 1083 trades, pair coverage 100%
- Stage 1 (features + candidates): ✅ — Stage 1 OK
- Stage 2 (LLM family naming): ✅ — Stage 2 OK

## Reliability components

| component | weight | value |
|---|---:|---:|
| direction_predictability | 0.25 | 1.000 |
| family_clarity | 0.20 | 0.620 |
| timing_concentration | 0.20 | 0.645 |
| sanity_pass | 0.10 | 1.000 |
| age_freshness | 0.10 | 0.973 |
| vendor_quality | 0.10 | 1.000 |
| pair_coverage | 0.05 | 1.000 |

## Linked artifacts

- Fingerprint: `studies/myfxbook_reverse_engineering/systems/11171596/decoder/fingerprint.md`
- Candidates: `studies/myfxbook_reverse_engineering/systems/11171596/decoder/candidates.json`
- Signal rule: `studies/myfxbook_reverse_engineering/systems/11171596/signal_rule.md`


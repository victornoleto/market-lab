# Validation report — system 11207608

Generated: 2026-05-02T06:26:34+00:00
Elapsed: 285.4s

## Overall: ✅ PASS

- **Family:** `FACTOR_SCALPING` (confidence 0.72)
- **Reliability score:** **0.778 (HIGH)**
- **Trades / pairs:** 202 / 1
- **Last trade:** 2025-07-30 16:33:34+00:00
- **Account type:** Real

## Pipeline status

- Pre-check: ✅ — 202 trades, pair coverage 100%
- Stage 1 (features + candidates): ✅ — Stage 1 OK
- Stage 2 (LLM family naming): ✅ — Stage 2 OK

## Reliability components

| component | weight | value |
|---|---:|---:|
| direction_predictability | 0.25 | 1.000 |
| family_clarity | 0.20 | 0.720 |
| timing_concentration | 0.20 | 0.371 |
| sanity_pass | 0.10 | 1.000 |
| age_freshness | 0.10 | 0.849 |
| vendor_quality | 0.10 | 0.750 |
| pair_coverage | 0.05 | 1.000 |

## Linked artifacts

- Fingerprint: `studies/myfxbook_reverse_engineering/systems/11207608/decoder/fingerprint.md`
- Candidates: `studies/myfxbook_reverse_engineering/systems/11207608/decoder/candidates.json`
- Signal rule: `studies/myfxbook_reverse_engineering/systems/11207608/signal_rule.md`


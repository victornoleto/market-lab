# Validation report — system 1603276

Generated: 2026-05-02T07:41:08+00:00
Elapsed: 921.8s

## Overall: ✅ PASS

- **Family:** `LONDON_OPEN_MOMENTUM` (confidence 0.62)
- **Reliability score:** **0.676 (HIGH)**
- **Trades / pairs:** 594 / 4
- **Last trade:** 2017-09-07 10:46:12+00:00
- **Account type:** Real

## Pipeline status

- Pre-check: ✅ — 594 trades, pair coverage 100%
- Stage 1 (features + candidates): ✅ — Stage 1 OK
- Stage 2 (LLM family naming): ✅ — Stage 2 OK

## Reliability components

| component | weight | value |
|---|---:|---:|
| direction_predictability | 0.25 | 1.000 |
| family_clarity | 0.20 | 0.620 |
| timing_concentration | 0.20 | 0.333 |
| sanity_pass | 0.10 | 1.000 |
| age_freshness | 0.10 | 0.000 |
| vendor_quality | 0.10 | 0.850 |
| pair_coverage | 0.05 | 1.000 |

## Linked artifacts

- Fingerprint: `studies/myfxbook_reverse_engineering/systems/1603276/decoder/fingerprint.md`
- Candidates: `studies/myfxbook_reverse_engineering/systems/1603276/decoder/candidates.json`
- Signal rule: `studies/myfxbook_reverse_engineering/systems/1603276/signal_rule.md`


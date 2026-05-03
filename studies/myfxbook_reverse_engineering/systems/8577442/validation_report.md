# Validation report — system 8577442

Generated: 2026-05-02T12:59:20+00:00
Elapsed: 2772.7s

## Overall: ✅ PASS

- **Family:** `OVERLAP_NY_LONDON_RANGE` (confidence 0.52)
- **Reliability score:** **0.618 (MEDIUM)**
- **Trades / pairs:** 934 / 5
- **Last trade:** 2026-04-27 15:17:32+00:00
- **Account type:** Real

## Pipeline status

- Pre-check: ✅ — 934 trades, pair coverage 100%
- Stage 1 (features + candidates): ✅ — Stage 1 OK
- Stage 2 (LLM family naming): ✅ — Stage 2 OK

## Reliability components

| component | weight | value |
|---|---:|---:|
| direction_predictability | 0.25 | 0.476 |
| family_clarity | 0.20 | 0.520 |
| timing_concentration | 0.20 | 0.303 |
| sanity_pass | 0.10 | 1.000 |
| age_freshness | 0.10 | 0.997 |
| vendor_quality | 0.10 | 0.850 |
| pair_coverage | 0.05 | 1.000 |

## Linked artifacts

- Fingerprint: `studies/myfxbook_reverse_engineering/systems/8577442/decoder/fingerprint.md`
- Candidates: `studies/myfxbook_reverse_engineering/systems/8577442/decoder/candidates.json`
- Signal rule: `studies/myfxbook_reverse_engineering/systems/8577442/signal_rule.md`


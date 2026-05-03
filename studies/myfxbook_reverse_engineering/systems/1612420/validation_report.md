# Validation report — system 1612420

Generated: 2026-05-02T08:13:05+00:00
Elapsed: 1916.6s

## Overall: ✅ PASS

- **Family:** `OVERLAP_NY_LONDON_RANGE` (confidence 0.52)
- **Reliability score:** **0.630 (MEDIUM)**
- **Trades / pairs:** 788 / 4
- **Last trade:** 2021-06-10 15:40:55+00:00
- **Account type:** Demo

## Pipeline status

- Pre-check: ✅ — 788 trades, pair coverage 100%
- Stage 1 (features + candidates): ✅ — Stage 1 OK
- Stage 2 (LLM family naming): ✅ — Stage 2 OK

## Reliability components

| component | weight | value |
|---|---:|---:|
| direction_predictability | 0.25 | 0.680 |
| family_clarity | 0.20 | 0.520 |
| timing_concentration | 0.20 | 0.746 |
| sanity_pass | 0.10 | 1.000 |
| age_freshness | 0.10 | 0.021 |
| vendor_quality | 0.10 | 0.550 |
| pair_coverage | 0.05 | 1.000 |

## Linked artifacts

- Fingerprint: `studies/myfxbook_reverse_engineering/systems/1612420/decoder/fingerprint.md`
- Candidates: `studies/myfxbook_reverse_engineering/systems/1612420/decoder/candidates.json`
- Signal rule: `studies/myfxbook_reverse_engineering/systems/1612420/signal_rule.md`


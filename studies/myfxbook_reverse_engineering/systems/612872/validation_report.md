# Validation report — system 612872

Generated: 2026-05-02T10:29:07+00:00
Elapsed: 858.7s

## Overall: ✅ PASS

- **Family:** `MARTINGALE_GRID` (confidence 0.95)
- **Reliability score:** **0.300 (LOW)**
- **Trades / pairs:** 3136 / 2
- **Last trade:** 2021-05-11 04:01:00+00:00
- **Account type:** Real

## Pipeline status

- Pre-check: ✅ — 3136 trades, pair coverage 100%
- Stage 1 (features + candidates): ✅ — Stage 1 OK
- Stage 2 (LLM family naming): ✅ — Stage 2 OK

## Reliability components

| component | weight | value |
|---|---:|---:|
| direction_predictability | 0.25 | 0.293 |
| family_clarity | 0.20 | 0.950 |
| timing_concentration | 0.20 | 0.237 |
| sanity_pass | 0.10 | 0.000 |
| age_freshness | 0.10 | 0.004 |
| vendor_quality | 0.10 | 1.000 |
| pair_coverage | 0.05 | 1.000 |

## Notes

- sanity FAIL — martingale signature detected
- forced LOW: martingale/grid signature

## Linked artifacts

- Fingerprint: `studies/myfxbook_reverse_engineering/systems/612872/decoder/fingerprint.md`
- Candidates: `studies/myfxbook_reverse_engineering/systems/612872/decoder/candidates.json`
- Signal rule: `studies/myfxbook_reverse_engineering/systems/612872/signal_rule.md`


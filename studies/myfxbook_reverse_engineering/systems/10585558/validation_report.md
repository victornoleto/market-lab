# Validation report — system 10585558

Generated: 2026-05-02T05:31:58+00:00
Elapsed: 796.1s

## Overall: ✅ PASS

- **Family:** `MARTINGALE_GRID` (confidence 0.88)
- **Reliability score:** **0.300 (LOW)**
- **Trades / pairs:** 1611 / 4
- **Last trade:** 2026-04-23 11:30:01+00:00
- **Account type:** Real

## Pipeline status

- Pre-check: ✅ — 1611 trades, pair coverage 100%
- Stage 1 (features + candidates): ✅ — Stage 1 OK
- Stage 2 (LLM family naming): ✅ — Stage 2 OK

## Reliability components

| component | weight | value |
|---|---:|---:|
| direction_predictability | 0.25 | 0.543 |
| family_clarity | 0.20 | 0.880 |
| timing_concentration | 0.20 | 0.836 |
| sanity_pass | 0.10 | 0.000 |
| age_freshness | 0.10 | 0.995 |
| vendor_quality | 0.10 | 1.000 |
| pair_coverage | 0.05 | 1.000 |

## Notes

- sanity FAIL — martingale signature detected
- forced LOW: martingale/grid signature

## Linked artifacts

- Fingerprint: `studies/myfxbook_reverse_engineering/systems/10585558/decoder/fingerprint.md`
- Candidates: `studies/myfxbook_reverse_engineering/systems/10585558/decoder/candidates.json`
- Signal rule: `studies/myfxbook_reverse_engineering/systems/10585558/signal_rule.md`


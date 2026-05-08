# Validation report — system 10746260

Generated: 2026-05-02T05:50:47+00:00
Elapsed: 197.7s

## Overall: ✅ PASS

- **Family:** `MARTINGALE_GRID` (confidence 0.97)
- **Reliability score:** **0.300 (LOW)**
- **Trades / pairs:** 636 / 4
- **Last trade:** 2024-06-19 09:00:15+00:00
- **Account type:** Real

## Pipeline status

- Pre-check: ✅ — 636 trades, pair coverage 100%
- Stage 1 (features + candidates): ✅ — Stage 1 OK
- Stage 2 (LLM family naming): ✅ — Stage 2 OK

## Reliability components

| component | weight | value |
|---|---:|---:|
| direction_predictability | 0.25 | 0.648 |
| family_clarity | 0.20 | 0.970 |
| timing_concentration | 0.20 | 0.836 |
| sanity_pass | 0.10 | 0.000 |
| age_freshness | 0.10 | 0.626 |
| vendor_quality | 0.10 | 0.850 |
| pair_coverage | 0.05 | 1.000 |

## Notes

- sanity FAIL — martingale signature detected
- forced LOW: martingale/grid signature

## Linked artifacts

- Fingerprint: `studies/myfxbook_reverse_engineering/systems/10746260/decoder/fingerprint.md`
- Candidates: `studies/myfxbook_reverse_engineering/systems/10746260/decoder/candidates.json`
- Signal rule: `studies/myfxbook_reverse_engineering/systems/10746260/signal_rule.md`


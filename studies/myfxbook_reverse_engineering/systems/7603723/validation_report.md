# Validation report — system 7603723

Generated: 2026-05-02T11:16:21+00:00
Elapsed: 2212.8s

## Overall: ✅ PASS

- **Family:** `FACTOR_SCALPING` (confidence 0.52)
- **Reliability score:** **0.300 (LOW)**
- **Trades / pairs:** 3558 / 25
- **Last trade:** 2021-06-16 21:40:37+00:00
- **Account type:** Real

## Pipeline status

- Pre-check: ✅ — 3558 trades, pair coverage 100%
- Stage 1 (features + candidates): ✅ — Stage 1 OK
- Stage 2 (LLM family naming): ✅ — Stage 2 OK

## Reliability components

| component | weight | value |
|---|---:|---:|
| direction_predictability | 0.25 | 0.567 |
| family_clarity | 0.20 | 0.520 |
| timing_concentration | 0.20 | 0.644 |
| sanity_pass | 0.10 | 0.000 |
| age_freshness | 0.10 | 0.024 |
| vendor_quality | 0.10 | 1.000 |
| pair_coverage | 0.05 | 1.000 |

## Notes

- sanity FAIL — martingale signature detected
- forced LOW: martingale/grid signature

## Linked artifacts

- Fingerprint: `studies/myfxbook_reverse_engineering/systems/7603723/decoder/fingerprint.md`
- Candidates: `studies/myfxbook_reverse_engineering/systems/7603723/decoder/candidates.json`
- Signal rule: `studies/myfxbook_reverse_engineering/systems/7603723/signal_rule.md`


# Validation report — system 11355455

Generated: 2026-05-02T06:30:26+00:00
Elapsed: 232.5s

## Overall: ✅ PASS

- **Family:** `FACTOR_SCALPING` (confidence 0.52)
- **Reliability score:** **0.744 (HIGH)**
- **Trades / pairs:** 236 / 2
- **Last trade:** 2026-04-30 11:04:37+00:00
- **Account type:** Real

## Pipeline status

- Pre-check: ✅ — 236 trades, pair coverage 99%
- Stage 1 (features + candidates): ✅ — Stage 1 OK
- Stage 2 (LLM family naming): ✅ — Stage 2 OK

## Reliability components

| component | weight | value |
|---|---:|---:|
| direction_predictability | 0.25 | 1.000 |
| family_clarity | 0.20 | 0.520 |
| timing_concentration | 0.20 | 0.326 |
| sanity_pass | 0.10 | 1.000 |
| age_freshness | 0.10 | 0.999 |
| vendor_quality | 0.10 | 0.750 |
| pair_coverage | 0.05 | 0.987 |

## Linked artifacts

- Fingerprint: `studies/myfxbook_reverse_engineering/systems/11355455/decoder/fingerprint.md`
- Candidates: `studies/myfxbook_reverse_engineering/systems/11355455/decoder/candidates.json`
- Signal rule: `studies/myfxbook_reverse_engineering/systems/11355455/signal_rule.md`


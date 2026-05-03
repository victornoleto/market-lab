# Validation report — system 10224499

Generated: 2026-05-02T04:38:16+00:00
Elapsed: 1111.2s

## Overall: ✅ PASS

- **Family:** `LATE_NY_BREAKOUT` (confidence 0.68)
- **Reliability score:** **0.871 (HIGH)**
- **Trades / pairs:** 221 / 3
- **Last trade:** 2026-04-29 02:00:08+00:00
- **Account type:** Real

## Pipeline status

- Pre-check: ✅ — 221 trades, pair coverage 100%
- Stage 1 (features + candidates): ✅ — Stage 1 OK
- Stage 2 (LLM family naming): ✅ — Stage 2 OK

## Reliability components

| component | weight | value |
|---|---:|---:|
| direction_predictability | 0.25 | 0.842 |
| family_clarity | 0.20 | 0.680 |
| timing_concentration | 0.20 | 1.000 |
| sanity_pass | 0.10 | 1.000 |
| age_freshness | 0.10 | 0.998 |
| vendor_quality | 0.10 | 0.750 |
| pair_coverage | 0.05 | 1.000 |

## Linked artifacts

- Fingerprint: `studies/myfxbook_reverse_engineering/systems/10224499/decoder/fingerprint.md`
- Candidates: `studies/myfxbook_reverse_engineering/systems/10224499/decoder/candidates.json`
- Signal rule: `studies/myfxbook_reverse_engineering/systems/10224499/signal_rule.md`


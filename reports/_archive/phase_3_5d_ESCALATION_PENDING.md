# Phase 3.5d — ESCALATION PENDING

**Trigger:** spec `specs/phase_3_5d_plano_b_v2_3x_letf.md` §7.3 (≥4 leads DEAD) + §8 (arbitration required before phase advance).

**Date:** 2026-04-21

**Status:** Phase 3.5d 3× LETF swing search EXHAUSTED. All candidate winners rejected.

---

## History

| Iter | Lead | Asset | Verdict | Note |
|------|------|-------|---------|------|
| 0 | D1 | all | INFO | Buy-hold baselines established |
| 2 | D2 bootstrap | — | — | Registry setup |
| 3-6 | D2 sweep | EW, UPRO, TQQQ, aggregate | DEAD (0/18) | MA regime Gayed; best TQQQ sma200_gld SN=0.780 (gate 0.800) |
| 7 | D3 | TQQQ+GLD | DEAD (0/4) | Donchian breakout |
| 8 | D4 | TQQQ+GLD | DEAD (0/6) | Absolute momentum Antonacci |
| 9 | D5 | TQQQ+GLD | DEAD (0/7) | Vol-targeting homogeneous — PBO=0.599 |
| 10 | D5b | TQQQ+GLD | DEAD (0/3) | Vol-targeting diverse — PBO=0.651 |
| 11 | D6 | TQQQ+GLD | NEAR-MISS | Clenow composite — SN=0.797 (gap 0.003) |
| 12 | D7 + D8 | TQQQ+GLD | DEAD / impasse | Binary vs continuous structural conflict |
| 13 | **E1** | TQQQ+GLD | **REJECTED BY ARBITRATION** | Vol-targeting N=2 grid — PBO=0.151 artifact |

Total: 8 leads DEAD, 1 near-miss, 1 rejected candidate. 0 honest winners.

---

## Arbitration verdict on E1 (iter 13)

**Unanimous BLOCK** from 3 adversarial judges + arbiter.

**Core failure:** E1 achieved PBO=0.151 by reducing CSCV grid from 7 configs (D5: PBO=0.599) to 3 (D5b: 0.651) to **2 configs**. Same strategy, same data — only the denominator changed. This is the behavior PBO was designed to detect `[advances_fin_ml, p.208-211]`.

**Supporting failures:**
- DSR n_trials=2 vs cumulative reality ≥51 configs in TQQQ+GLD dataset → recalibrated p∈[6.5e-3, 0.055]
- 3 mis-citations (ch.14 ≠ vol-targeting, p.298-299 ≠ DSR, Gayed ≠ TQQQ+GLD)
- Loop documented `pbo_concern` in YAML and auto-advanced anyway
- Phase auto-advance 3.5d→3.5f bypassed mandatory 3.5e arbitration

**Reports:**
- `reports/spec-judges/2026-04-21-07-e1-vol-tgt-winner-pass-20260421-120733/methodology.md`
- `reports/spec-judges/2026-04-21-07-e1-vol-tgt-winner-pass-20260421-120733/domain.md`
- `reports/spec-judges/2026-04-21-07-e1-vol-tgt-winner-pass-20260421-120733/strategic.md`
- `reports/spec-judges/2026-04-21-07-e1-vol-tgt-winner-pass-20260421-120733/arbiter.md`

---

## Options offered to user (2026-04-21)

- **A** — Breadth hunt D9+ in current Phase 3.5d frame (3× LETF, new signal families)
- **B** — Pivot to 2× LETF (SSO/QLD) + include 3× as honest comparison, Gayed canonical signals, mandate-aligned
- **C** — Abandon Plano B entirely, focus Plano A V2-L2 Gayed CFD
- **D** — Re-validate E1 honestly with grid N=21+ (arbiter probability of passing: ~15-25%)

**User decision (2026-04-21):** Option B, with risk-adjusted comparison (Calmar/Sharpe) across 2× vs 3×, not MaxDD alone.

---

## Next phase: 3.5e Plano B leverage comparison (honest grid)

New spec to be written: `specs/phase_3_5e_plano_b_leverage_comparison.md`.

Key constraints for Phase 3.5e to honor López de Prado `[advances_fin_ml, p.208-211, p.276]`:

1. **Honest grid:** ≥10 structurally diverse configs, defined **before** running CSCV, not adjusted ex-post.
2. **Cumulative trials tracked:** DSR n_trials counts ALL configs tested on the dataset across all iterations.
3. **Universe mandate-aligned:** 2× LETF (SSO/QLD) primary + 3× (UPRO/TQQQ) comparison. All configs run on all leverage levels for apples-to-apples.
4. **Signal family Gayed canonical:** SMA regime binary on/off (`leverage_for_the_long_run`) — known to yield PBO≈0.115 naturally.
5. **Off-legs multi-tested:** cash, GLD, SHV, TLT — not pre-selected.
6. **Gates unchanged:** PBO<0.5 + DSR p<0.05 + WF≥6/8 + OOS + FWD + CAGR_net > SPY_net + Calmar>0.5 + Sharpe_net>0.8. Zero bypass.
7. **Winner selection:** if multiple pass, compare by Calmar/Sharpe risk-adjusted pair, not raw CAGR or MaxDD alone.

---

## Loop integrity issues to patch (Action #2 from arbiter)

Before running Phase 3.5e loop, `scripts/self_improve_loop.sh` must be patched:

- [ ] Block auto-advance of `phase:` field when `active_lead_registry` is non-null OR phase name contains "arbitration"/"escalation"
- [ ] Block new lead creation when N leads DEAD ≥ 4 without explicit user-signed escalation
- [ ] Warn+abort when YAML memory has any `*_concern` field unresolved
- [ ] Add regressive tests in `tests/test_validation.py`:
  - Warn when `pbo()` called with N_configs < 4
  - PBO stability test: same strategy across N=[2, 4, 7, 10] configs should give similar PBO ± 0.15
  - Cumulative trials tracking in DSR

---

## Citations

- `[advances_fin_ml, p.208-211]` — PBO CSCV methodology, grid must be exogenous
- `[advances_fin_ml, p.276]` — Deflated Sharpe Ratio, Harvey-Liu deflator requires cumulative N_trials
- `[leverage_for_the_long_run, ch.2]` — Gayed SMA regime canonical (SPX + T-bills off-leg)
- `[investment-mandate, §5]` — Gates sempre, zero bypass

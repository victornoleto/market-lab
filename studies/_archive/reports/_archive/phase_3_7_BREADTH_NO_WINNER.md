# Phase 3.7-3 — BREADTH_NO_WINNER (halt contract §T6)

**Date:** 2026-04-22
**Branch:** `phase3.6/swing-winner-hunt-20260423`
**Engine:** F2-patched (commit `7b90a8f`), `prev_weight × ret` alignment honored across all 8 subagent implementations.
**Pytest:** 908 passed, 2 skipped, 0 failures — baseline preserved from 890 (Wave 1) + 18 new smoke tests (3 per H1, 3-4 per H2, 4 per H3).
**Input blueprint:** `docs/research/2026-04-23-phase3.7-literature-sprint.md` (28 papers) + `docs/research/2026-04-23-phase3.7-2-data-sprint.md` (4 feeds ingested, 20 integrity tests).

---

## 0. Escalation trigger

Per plan §T6: **3/3 top-tier hypothesis families (H1 intraday SPY, H2 VIX-gated LETF, H3 crypto Donchian) all FAILED honest 13-gate validation** across 8 subagent verdicts. The halt contract forbids proceeding to H4 (confidence-weighted sizing meta-layer) or H5 (intraday × VIX hybrid) without a lead that first passed top-tier gates — H4/H5 are meta-layers, not primary signals.

All 8 subagents produced AGGREGATE.md + jornada + commit. No frozen files touched. Mandate §7 and strategy docs untouched. The sole open item is user decision on path forward (§4 below).

---

## 1. Comparison table (all 8 subagents across 3 waves)

Legend: ✅ pass; ❌ fail; ⚠️ warning-only (mandate §2.2/§2.3 tier framework — CAGR/MDD no longer hard-block since 2026-04-22).
Hard gates = 9/10/11/12 (cross-lib, bootstrap OOS+FULL, PBO, DSR).

| # | Family | Broker rota | IS Sharpe | OOS Sharpe | OOS CAGR tier | OOS MDD tier | FWD | WF | Hold | IR | X-lib Δ (HARD) | Bootstrap OOS CI (HARD) | PBO (HARD) | DSR p (HARD) | Cost×2 | Hard gates | Commit |
|---|---|---|--:|--:|---|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|---|
| H1.a | Zarattini base (ATR trail) | A Pepperstone | -0.15 | -0.34 | -5.42% Folclore ⚠️ | -22.8% Excelente ⚠️ | +0.20 | 3/8 | 6.4h ✅ | -0.58 | 0.53pp ✅ | [-1.97, +1.28] ❌ | 0.369 ❌ | 0.962 ❌ | -0.57 | **1/4** | `2358c00` |
| H1.b | Maróy VWAP exit | A Pepperstone | -2.28 | -2.96 | -35.3% Folclore ⚠️ | -73.3% Forte warn ⚠️ | -1.21 | 1/8 | 10min ❌ | -2.24 | 0.00pp ✅ | OOS/FULL ❌/❌ | 0.00 (deg) ✅ | 1.000 ❌ | -5.35 | **2/4** | `83d02f4` |
| H1.c | Maróy Ladder (TP scale-out) | A Pepperstone | -2.61 | -1.67 | -13.9% Folclore ⚠️ | -38.2% Válido ⚠️ | -1.14 | 0/8 | 7min ❌ | -1.17 | 0.03pp ✅¹ | [-0.0012, -0.0011] ❌ | 0.00 (deg) ✅ | 1.000 ❌ | -4.66 | **2/4** | `12c0635` |
| H2.a | Božović VIX-scaling | B Inter | 0.62 | 0.47 | 6.04% Folclore ⚠️ | -40.2% Forte warn ⚠️ | +0.73 | 7/8 | continuous ✅ | -0.30 | 0.00pp ✅ | OOS [-0.26, +1.37] ❌, FULL [0.10, 1.11] ✅ | 0.024 ✅ | 0.343 ❌ | 0.29 | **2/4** | `6aa49b2` |
| H2.b | Gayed 2x LRS + VIX<25 | B Inter | 0.94 | 0.39 | 6.75% Folclore ⚠️ | -48.1% Forte warn ⚠️ | +0.65 | 7/8 | 6.0d ✅ | 0.16 | 0.001pp ✅ | OOS low -4.6e-4 ❌ | 0.214 ✅ | 0.638 ❌ | 0.28 | **2/4** | `1a41ff2` |
| H2.c | VIX term-structure (VIXY 21d) | B Inter | 0.53 | 0.48 | 7.32% Folclore ⚠️ | -34.3% Marginal ⚠️ | +0.72 | 7/8 | 5.0d ✅ | -0.24 | 3.04pp ❌ | [-1.14, +2.07] ❌ | 0.413 ✅ | 0.633 ❌ | 0.25 | **1/4** | `58b20ae` |
| H3.a | BTC Donchian independent | A Pepperstone | 0.38 | 0.18 | +0.52% Folclore ⚠️ | -5.89% Excelente ⚠️ | +0.52 | 6/8 | 2.00d ✅ | -1.00 | 0.48pp ✅ | [-1.34, +1.68] ❌ | 0.064 ✅ | 0.829 ❌ | -0.05 | **2/4** | `eee8ac3` |
| H3.b | ETH Donchian independent | A Pepperstone | **1.68** | 0.66 | 3.63% Folclore ⚠️ | -4.64% Excelente ⚠️ | +1.02 | 7/8 | 2.0d ✅ | -1.23 | 0.44pp ✅ | OOS [-1.33, +2.22] ❌, FULL [0.16, 2.06] ✅ | 0.167 ✅ | 0.714 ❌ | 0.56 | **2/4**² | `e3ce9ab` |

¹ H1.c cross-lib evaluated on a simplified single-TP control (vectorbt `from_signals` cannot express variable-fraction ladder exits); documented limitation.
² H3.b also hit halt trigger: OOS n_trades = 45 < 50 floor (signal too sparse under 2-day time stop).

**Pattern:** no family clears more than 2/4 hard gates. **DSR p > 0.05 fails for 8/8** — the observed Sharpe in every OOS is indistinguishable from the null after multiple testing (Deflated Sharpe Ratio, `[advances_fin_ml, p.196-211]`).

---

## 2. Cross-family patterns

### 2.1 Engine is clean — this is NOT an implementation artifact

The F2 patch (`prev_weight × ret` alignment via `shift(1).fillna(0.0)`, commit `7b90a8f`) holds across 8 independently-implemented strategies in 3 distinct paradigms (intraday momentum, daily rotation, crypto trend):
- **Cross-lib Δ ≤ 3pp on 7/8 subagents.** The single miss (H2.c at 3.04pp) is 0.04pp above the 3pp threshold, flagged honestly as FAIL by the subagent itself; not a regression.
- Reference library combinations used: pandas-ref + vectorbt (all 8), plus bt or backtrader where daily-data feasibility allowed (H2 wave, H3).
- The Phase 3.6 BREADTH_NO_WINNER (§2.3) observation that "F2 engine fix holds across 10 independently-implemented strategies" now extends to **18 strategies** (10 Phase 3.6 + 8 Phase 3.7-3).

### 2.2 Overfit is not the cause either

PBO values across 8 subagents span 0.024 → 0.413 (all below the 0.5 default gate; H1.b/H1.c hit 0.0 via degenerate grids where all configs lose money equally — technically pass but informatively null). No catastrophic PBO here, unlike Phase 3.6 Family C (0.91), K (0.96), F (0.60), E (0.52).

The Phase 3.7-3 strategies are **honestly implemented, not overfit** — which is the same finding Phase 3.6 reached for families B, D, H, J, A with low PBO < 0.35: those strategies don't overfit, they genuinely lack edge under realistic frictions.

### 2.3 Three distinct structural killers (one per wave)

The 8 FAILs did not fail for the same mechanical reason. Each wave surfaced a **distinct paradigm-specific killer**:

**Wave 1 killer — "the Zarattini signal does not replicate post-2017 on CFD retail friction"**
- H1.a (paper-literal Zarattini) has gross OOS Sharpe ≈ −0.3 even at zero cost — the noise-boundary entry itself doesn't generate edge in 2017-2024 SPY 1-min.
- H1.b (VWAP exit) has gross OOS Sharpe −0.41 — exit engineering cannot rescue a broken entry.
- H1.c (Ladder exit) suffers a further 104% cumulative spread drag from 4 flips per round-trip.
- **Interpretation:** The paper's reported Sharpe 1.33 (2007-2024) likely came from the pre-HFT-saturation regime (2007-2016). Post-HFT, noise boundaries may be arbitraged away on 1-min liquid SPY. Alternative: share-fill / slippage model in the paper may be more favorable than a CFD 0.67 bps spread, though the math suggests not materially so.

**Wave 2 killer — "VIX is contemporaneous, and BR DARF kills daily rotation"**
- H2.a/b/c all show gross signal with some IS power (Sharpe 0.53-0.94) that decays OOS (0.39-0.48).
- H2.b diagnosed the "VIX is contemporaneous not predictive" mechanism most cleanly: the gate fires AFTER damage (GFC Sharpe −0.77, Euro 2011 −1.41, 2022 −1.88).
- H2.a quantified the DARF cost: **316% cumulative tax drag over 35 years** from 28 year-end realization events — the dominant kill mechanism.
- H2.b similar: 125 OOS switches → cum_tax 57%, cum_cost 16.6%, gross 14% CAGR → net 6.75%.
- **Interpretation:** The Božović 2024 IRFA claim "VIX-scaling has cost advantage over realized-vol scaling" does not survive rota B Inter tax structure. Any daily-rotating strategy on rota B pays a 3-7% annualized friction tax that most signals cannot beat on a risk-adjusted basis.

**Wave 3 killer — "Pepperstone 2-day swap cap amputates the fat right tail"**
- H3.a BTC: strategy CAGR +0.52% vs buy-hold +55.68% (OOS); IR = −1.00. The 2-day time-stop — required because Pepperstone crypto long swap is −20%/yr — forces exit before Donchian trends compound. IS Sharpe 0.38 → OOS 0.18 → bootstrap CI crosses zero.
- H3.b ETH: slightly better IS (Sharpe 1.68) — there IS something in ETH trend-following — but still OOS Sharpe 0.66 and halt trigger on n_trades = 45 (< 50 floor). Signal exists but is too sparse under the 2-day cap.
- **Interpretation:** Zarattini-Pagani-Barbon 2025's Sharpe > 1.5 claim depends on TWO structural features our broker universe cannot provide: (a) top-20 cross-sectional diversification, (b) relative-strength selection. Per-asset independent Donchian on BTC+ETH cannot recover those.

### 2.4 Distinguishing H3.b ETH (closest to "something real")

H3.b is the ONLY family with both:
- IS Sharpe ≥ 1.0 (1.68)
- FULL-period bootstrap 99.9% CI strictly positive ([0.16, 2.06])

The OOS window is where it breaks: Sharpe decays to 0.66, n_trades falls to 45, OOS CI crosses zero. This pattern is consistent with "real but very weak signal, insufficient OOS power under current broker constraint." It does NOT earn PASS under honest gates, but it is materially different from the other 7 which show no IS-to-OOS coherence.

### 2.5 Consistent with Phase 3.6 (16 families total now 16/16 FAIL)

Phase 3.6 ran 10 honest 13-gate validations, all FAIL. Phase 3.5f V2 ran 6. Phase 3.7-3 adds 8. **Total: 24 honest validations across 24 mechanically-distinct paradigms, 0 PASS.**

This is the class of result predicted by:
- Aronson's 6,402-rule S&P 500 null (1 spurious rule at p<0.05 expected from 6,402 tests) `[evidence_based_ta, p.459]`
- López de Prado deflated Sharpe framework `[advances_fin_ml, p.196-211]`
- Hsu/Kuan 82% post-selection decay on S&P/DJIA rules `[evidence_based_ta, p.450]`
- Li-Ferreira 2025 Network Momentum: state-of-art ML systematic Sharpe 0.35 net (below 2/3 of our gate 2) `[phase3_7_literature_sprint, §T10]`

---

## 3. What this means

Phase 3.7-3 was designed explicitly to answer the Phase 3.6 null finding by testing **exactly the leads Phase 3.6 did not cover**: intraday SPY (Zarattini 2024), VIX-managed LETF (Božović 2024), crypto Donchian (Zarattini-Pagani-Barbon 2025). The literature sprint (Phase 3.7-1) sourced 28 papers, and the data sprint (Phase 3.7-2) ingested 4 feeds explicitly to cover these three leads.

**All 3 top-tier leads failed honest validation.**

This is not a failure of the Phase 3.7 process — the process worked exactly as designed:
- Engine clean (18/18 strategies now, Δ ≤ 3pp on 17/18).
- Overfit controlled (PBO passes on 7/8, and where it's degenerate the cause is "all configs lose" not "IS-best beats OOS").
- Validation modules reused honestly (`validation/cpcv.py`, `pbo.py`, `dsr.py`, `bootstrap.py`, `walk_forward.py`).
- Stop-at-first-winner never fired because no winner was ever found.

It IS further confirmation of what the Phase 3.6 BREADTH_NO_WINNER already concluded (§3): "honest gates + canonical literature + 25 years of Tiingo data = no winner" is **the post-2008 honest-backtest reality** on this instrument universe under these broker cost structures.

The additional finding from Phase 3.7-3: **the two broker rotas we have available each have a specific structural killer**:
- **Rota A (Pepperstone CFD)**: short-hold required (swap kills long hold), but short-hold amputates trend edges. Paradigm fit is narrow.
- **Rota B (Inter US equities)**: 15% year-end DARF is a 3-7% annualized tax drag that few honest signals can beat.

Neither broker rota is "broken"; both are fine for their canonical use cases (passive Inter, intraday Pepperstone). What does not survive is **actively-traded multi-switch strategies on either**.

---

## 4. Recommendations (per plan §T6)

**Orchestrator does NOT choose; user chooses.** Four concrete paths follow.

### R1 — Destrava dados 2007-2016 com Polygon.io e re-roda H1 em 17y completos

**What:** Pay for Polygon.io Advanced ($199/mo) to get SPY 1-min bars 2007-2016 (the paper's pre-HFT-saturation regime). Re-run H1.a (Zarattini base) + H1.b (Maróy VWAP) on the full 2007-2024 window.

**Prior probability of winner:** moderate. The paper's Sharpe 1.33 spans 2007-2024 (17y). Our 2017+ subset (9y) is the post-HFT slice. If the edge is concentrated in 2007-2016, expanding the window may recover it. Alternative: the edge was never there and the paper's result is in-sample overfit, in which case R1 confirms the null more rigorously.

**Cost:** $199/mo ≥ mandate §4.8 subscription floor. Requires explicit user sign-off (user decision 2026-04-23 was **against** paying for feeds; this reopens that decision).

**Risk:** $199/mo × 3 months = $600 to answer one question, and the answer may still be null.

### R2 — Softer gates with user sign-off (mandate override §7)

**What:** Relax gate 10 (bootstrap 99.9% CI low > 0 → 95% CI low > 0), and/or gate 12 (DSR p < 0.05 → p < 0.10), on the closest-to-PASS family (H3.b ETH has best IS/full-period evidence; H2.b Gayed has best mechanistic story). Promote to "Plano B-minor" with explicit mandate §7 entry.

**Prior:** this is **below the CAGR Folclore floor** for both rotas. Mandate §2.2 tier framework (2026-04-22) already made CAGR/MDD warning-only — further relaxing PBO/DSR/bootstrap hard-gates violates the remaining §2.4 zero-bypass invariant. User already relaxed §2.2 and §2.3; a third relaxation on the statistical-rigor gates would remove the mandate's only remaining teeth.

**Cost:** hours. Re-document, re-commit.

**Risk:** strategy underperforms buy-hold SPY/BTC on a risk-adjusted basis. Violates §2.4. High operational risk in live.

### R3 — Pivot to Plano C passive + Plano B canonical LETF, abandon Plano A

**What:** Invoke mandate §4.7 fallback clause. Re-allocate 20-40% active bucket:
- 60-80% passive buy-hold stays (mandate §1).
- Drop Plano A (Pepperstone CFD short-hold) entirely — the 2-day swap cap + retail lot granularity + SCB Bahamas Tier-3 counterparty risk compound to make active CFD trading unattractive without a real signal.
- Keep Plano B (Inter) as the only active channel, but restricted to **canonical Gayed LETF rotation** (SMA-200 + UPRO/cash, no VIX gate, infrequent rotation ~5 trades/year to minimize DARF drag). This is the config from `leverage_for_the_long_run.md` p.13-17; it's been stress-tested in the literature since 2016.

**Prior:** this is the **honest default** per mandate §2 + §4.7. Phase 3.5b already validated a version of this (3-leg EW SSO+QLD+UGL) — it was invalidated by Phase 3.5c cross-lib against testfol.io synthetic LETF data (`docs/investment-mandate.md §4 pre-amble`), but the canonical 1-leg Gayed is simpler and has not been invalidated; it just wasn't the "winner" the project was hoping for.

**Cost:** 1-2 weeks. Re-validate canonical 1-leg Gayed SMA-200 + UPRO/cash on post-cross-lib-fix engine. Document + mandate §7 entry.

**Risk:** ambition shrinks further than the 2026-04-15 intraday pivot already shrank it. CAGR target moves from "5-10%/month" through "17-25% Válido tier" to "whatever Gayed canonical gives us, likely 12-15% net".

### R4 — Re-run `self_improve_loop` on fresh book-driven hypotheses including Phase 3.7 results

**What:** Re-launch `self_improve_loop` with input = 33-book corpus + Phase 3.6 BREADTH_NO_WINNER + Phase 3.7 BREADTH_NO_WINNER + mandate tier framework + broker rota structural killers. Loop generates fresh hypotheses that explicitly address the killers (e.g., weekly-rebalance swing instead of daily; single-asset edges with low-turnover).

**Prior:** low. The loop ran Phase 3.5e (38/144 trials, paused) on the same corpus. 24 honest validations across 2026 suggest the corpus's usable hypothesis space under our broker constraints is exhausted. Running it again without new input is unlikely to surface material.

**Cost:** 2-3 weeks, significant LLM cost.

**Risk:** high cost for low expected information gain.

---

## 5. Orchestrator recommendation (informal, non-binding)

**R3 (Pivot Plano C passive + canonical Gayed-only Plano B, abandon Plano A) is the cleanest honest path.** Reasoning:
- 24/24 honest validations across two phases suggest the active edge in our search space is either not present or below the noise floor of our gates.
- The two broker rotas have distinct structural killers (swap on A, DARF on B) that are unlikely to disappear.
- Canonical Gayed SMA-200 is literature-backed, low-turnover (~5 trades/yr), and the only rota-B strategy that doesn't get killed by DARF compounding.

**R1 (Polygon.io) is the second-best path** IF the user specifically wants to know whether the Zarattini 2024 edge is real in the 2007-2016 regime. It's an information-gathering expenditure with a clear yes/no outcome; if the answer is yes, there's a specific path to H4 meta-layer + deployment; if no, we've definitively closed one of the three top-tier hypotheses.

**R2 (soften gates) violates mandate §2.4** — do not recommend.

**R4 (re-run loop) costs too much for too little expected gain** — do not recommend without new input sources.

The user retains full authority to override.

---

## 6. Artifacts for user review

- Running index (all 8 rows): this file + per-family AGGREGATE.md below
- Per-family evidence: `reports/phase_3_7/<family_slug>/AGGREGATE.md` (+ `AGGREGATE.json`, `config_grid.csv` where applicable)
- Per-family jornada entries: `jornada/2026-04-22-*-phase3.7-*.md` (8 entries)
- Commits on branch `phase3.6/swing-winner-hunt-20260423`:
  - H1.a Zarattini base: `2358c00`
  - H1.b Maróy VWAP: `83d02f4`
  - H1.c Maróy Ladder: `12c0635`
  - H2.a Božović VIX: `6aa49b2`
  - H2.b Gayed + VIX: `1a41ff2`
  - H2.c VIX term-structure: `58b20ae`
  - H3.a BTC Donchian: `eee8ac3`
  - H3.b ETH Donchian: `e3ce9ab` (atomic marker; ETH implementation files folded into `eee8ac3` due to parallel-staging race; documented by the subagent)

### Commit label caveat

H3.b's code payload was staged concurrently with H3.a and landed inside `eee8ac3` ("h3_btc_donchian honest validation — FAIL"). `e3ce9ab` is a subsequent atomic marker commit to preserve forensic traceability. This is analogous to the Phase 3.6 `5d14dc2` caveat (§6 of `reports/phase_3_6/BREADTH_NO_WINNER.md`). Content is correct under `reports/phase_3_7/h3_eth_donchian/` and `tests/test_phase3_7_h3_eth_donchian.py`; no history rewrite performed.

---

## 7. Files NOT modified (invariants preserved)

- `docs/investment-mandate.md` — untouched
- `docs/self_improvement/memory.md` — untouched
- `docs/self_improvement/trial_count.json` — untouched
- All six `reports/phase_3_5f/honest_revalidation/*/AGGREGATE.md` — untouched
- All ten `reports/phase_3_6/*/AGGREGATE.md` + `reports/phase_3_6/BREADTH_NO_WINNER.md` — untouched
- `docs/.pending/*` — untouched
- All existing `docs/strategies/*.md` — untouched (no promotion without user sign-off)
- Phase 3.6 strategies (`src/market_lab/backtest/strategies/phase3_6_*.py`) — untouched
- Engine F2 patch site (`plano_a_leveraged_rotation.py`) — untouched
- Frozen forensic reports (`reports/phase3_5a_v2/*`, `docs/superpowers/findings/*`) — untouched

---

## 8. Citations

- F2 lookahead-fix alignment: `[advances_fin_ml, p.31-34]`
- CSCV/PBO: `[advances_fin_ml, p.208-211]`
- DSR deflated-Sharpe: `[advances_fin_ml, p.196-211]`
- Aronson data-mining-bias null: `[evidence_based_ta, p.459]`
- Hsu/Kuan rule-survivor decay: `[evidence_based_ta, p.450]`
- Zarattini-Aziz-Barbon 2024 SPY intraday: `[phase3_7_literature_sprint, T3]`
- Maróy 2024 exit engineering: `[phase3_7_literature_sprint, T3]`
- Božović 2024 IRFA VIX-managed: `[phase3_7_literature_sprint, T2]`
- Gayed LRS canonical: `[leverage_for_the_long_run, p.7-8, p.13, p.17]`
- Zarattini-Pagani-Barbon 2025 crypto Donchian: `[phase3_7_literature_sprint, T5]`
- Pepperstone cost structure: `[phase3_7_literature_sprint, T8]` + `docs/strategies/plano_a_pepperstone_index_cfd_rate_card.md`
- Inter rota B structure: `[docs/investment-mandate.md §4.6]`
- Mandate CAGR/MDD tier framework + §2.4 hard-gates: `[docs/investment-mandate.md §2.2, §2.3, §2.4, §7]`
- Mandate §4.7 passive-fallback clause: `[docs/investment-mandate.md §4.7]`
- Phase 3.6 precedent: `[reports/phase_3_6/BREADTH_NO_WINNER.md]`

---

**End of BREADTH_NO_WINNER.md. User decision pending between R1-R4.**

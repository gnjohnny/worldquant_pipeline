# Memory — Rule 9 Locked in AGENTS.md, Zero-Recycling Blank Slate Mandate

Last updated: 2026-11-08 23:10 UTC+3

## What was built

- **AGENTS.md System Invariant Upgrades**:
  - Added explicit prohibition under **Section 1 (Explicit Anti-Goals)** banning database formula borrowing, signal family tweaking, and formula template boilerplate recycling.
  - Added **Rule 9 (Strict Ban on Database Formula Tweaking & Signal Recycling / Zero-Recycling Invariant)** under **Section 7 (Gold Level Invariants)**:
    - *Absolute Prohibition*: Never retrieve, borrow, adapt, or tweak past formulas or signal combinations from the PostgreSQL database or account portfolio.
    - *Strict Boilerplate Ban*: Absolutely no `0.85 * signed_power(group_rank(...) - 0.5, 2) - 0.15 * group_rank(...)` or cosmetic variations.
    - *Blank-Slate Mandate*: Every new research batch must start from a genuine blank slate with unmined datasets, novel economic rationales, and virgin mathematical operators sharing zero lineage with prior database entries.
  - Strengthened **Rule 5 (Radical Alpha Originality)** enforcing distinct mathematical functional forms designed from scratch.
- **PostgreSQL Research Memory Synchronized**:
  - **Batch 271 Recorded**: Candidate 1 (`c47f1989`), Candidate 2 (`f8e581e0`), and Candidate 3 (`c5914947`) recorded with backtest metrics and decisions as `NEEDS_REVISION` due to high self-correlation collisions (> 0.90) with the user's existing submitted alphas.
  - **Batch 272 Recorded**: Candidate 1 (`59fcb31c`), Candidate 2 (`1fb2dd72`), and Candidate 3 (`4d621309`) recorded with simulation metrics as `REJECTED` (Sharpe 0.62–0.77, below the 1.25 gate).
- **Codebase Health**:
  - Test suite fully verified: 72/72 passing (`pytest tests/ -q`).
  - Linter clean: `ruff check .` passed with 0 errors.

## Decisions made

1. **Zero Database Formula Tweaking**:
   - The root cause of the 0.90+ self-correlation failures was drifting back to past formulas and signals in the database (`call - put` skew, customer returns, price-volume reversal, standard earnings yields divided by `close`). Under the new Rule 9, querying or adapting past database formulas for new batches is permanently forbidden.
2. **Elimination of Formula Template Boilerplate**:
   - The recurring pattern `0.85 * signed_power(group_rank(...) - 0.5, 2) - 0.15 * group_rank(...)` is completely retired. Future alphas must use distinct mathematical formulations (e.g. logarithmic compression, volatility-gated ratios, sigmoid transformations, unmined structural interactions).
3. **Pure Blank-Slate Research Methodology**:
   - Future batches must explore truly unmined datasets from `Quant_data/` with clean economic hypotheses developed from scratch, never referencing or modifying prior expressions.

## Problems solved

- **PostgreSQL Database Metric Consistency**: All simulation results from Batches 270, 271, and 272 are cleanly persisted in `experiments`, `experiment_metrics`, and `decisions` tables with full audit logs.
- **AST Parsing Reliability**: Confirmed that all mathematical expressions are statically validated for arity, syntax, and operator compliance before presenting simulation cards.

## Current state

- **Codebase & Pipeline**: Fully operational, clean, and passing all tests.
- **Database Status**: PostgreSQL holds all 43 approved account alphas and experiment history up to Batch 272.
- **Rules In Place**: `AGENTS.md` updated with unbreakable Rule 9 and strict boilerplate prohibitions.

## Next session starts with

1. Start from a **100% blank slate** with zero lookback to prior database expressions.
2. Formulate **Batch 274** using virgin, unmined datasets from `Quant_data/` (e.g., untapped fields from `analyst4`, `model16`, or `option9`) with novel mathematical operators and zero boilerplate.
3. Validate expressions statically via AST parser and register in PostgreSQL.
4. Output simulation cards for rapid execution on WorldQuant BRAIN.

## Open questions

- None. The workflow and invariants are locked in `AGENTS.md`.

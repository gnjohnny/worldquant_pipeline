# Memory — Alpha 42bcbc75 Super Alpha Submission & Single-Alpha Consultancy Cadence

Last updated: 2026-11-18 22:40 UTC+3

## What was built

- **Milestone Secured: Alpha `42bcbc75` Officially Submitted to WorldQuant BRAIN**:
  - **Expression**:
    `group_neutralize(trade_when(pcr_oi_270 > ts_mean(pcr_oi_10, 190), (implied_volatility_call_360 - implied_volatility_put_1080), -20), currency) * ts_backfill(ts_std_dev(vec_avg(minutes_to_four_percent_gain_2), 30), 160)`
  - **Settings**: Universe: `TOP3000`, Neutralization: `Industry`, Decay: `8`, Truncation: `0.08`, Delay: `1`
  - **Submission Name**: `OptionsSkew_PCRRegime_IntradayGainDispersion_8D`
  - **Category**: `none`
  - **Tags**: `options`, `volatility`, `intraday`
  - **Confirmed Platform Metrics (8 / 8 PASS)**:
    - **Sharpe**: **2.04** 🔥🔥🔥 (Super Alpha tier $\ge 2.0$)
    - **Fitness**: **2.58** 🚀🚀🚀 (Spectacular tier $\ge 2.20$, maximum consultancy payout multiplier)
    - **Turnover**: **13.23%** (Institutional sweet spot $10\% - 15\%$)
    - **Sub-universe Sharpe**: **1.29** 🌟 (Smashes 0.88 benchmark)
    - **Self-Correlation**: **0.4377** 🎯 (Clean pass; Sharpe improved by $\ge 10\%$)
    - **Weight Distribution**: Well distributed over instruments
    - **Competition Challenge**: Matches
  - **Full Lineage Tracked in PostgreSQL**:
    - `95060572` (v1: Sharpe 1.78, Fitness 2.28, Turnover 6.89%, Self-Corr 0.5751, Approved)
    - `d6253e26` (v2: Sharpe 1.90, Fitness 2.28, Turnover 13.05%, Self-Corr 0.4557, Approved)
    - `42bcbc75` (v3: Sharpe 2.04, Fitness 2.58, Turnover 13.23%, Self-Corr 0.4377, Status: `SUBMITTED`)
- **Catalog & Database Enhancements**:
  - Registered intraday price-gain velocity field `minutes_to_four_percent_gain_2` in `configs/data_sources.yaml` and seeded it into PostgreSQL `data_fields`.
  - Verified catalog support for `currency`, `pcr_oi_150`, and `pcr_oi_90`.
- **Batches 347 & 348 Audited and Logged**:
  - Batch 347 (`data/batch_347_virgin_economic_triplet.json`): Audited candidates `c17f858c` (Sharpe -0.35), `c1099961` (Sharpe 0.57, Sub-univ 0.51, concentration fail), and `20cd9243` (Sharpe -0.22, 1/25/2022 outlier spike).
  - Batch 348 (`data/batch_348_strike2_options_gamma_corridor.json`): Strike 2 push. Candidate `7cc947f6` solved instrument weight distribution and surged Sharpe to 1.09 / Sub-univ to 0.88 with 39.6% turnover.
- **Codebase Health**:
  - 72 / 72 unit tests passing cleanly (`pytest tests/ -v`).
  - Ruff linter 100% clean (0 errors).

## Decisions made

1. **Single-Alpha Precision Cadence Adopted**:
   - Per user directive (*"We will be sending one alpha until I get the consultancy"*), research shifts to high-conviction, single-alpha candidate generation and iterative refinement rather than multi-candidate batches.
2. **Super Alpha Standard Established**:
   - New target bar locked in at Sharpe $\ge 2.0$, Fitness $\ge 2.50$, Sub-universe Sharpe $\ge 1.0$, and Self-Correlation $< 0.45$.
3. **Lineage Preservation Enforced**:
   - Every parameter refinement (`95060572` $\to$ `d6253e26` $\to$ `42bcbc75`) is preserved as an immutable child record linked via `parent_candidate_id`.

## Problems solved

1. **Intraday Field Discovery & AST Whitelist**:
   - Discovered that field `minutes_to_four_percent_gain_2` was valid on BRAIN but absent from local catalog. Added and seeded, enabling AST parsing for microstructure gain dispersion signals.
2. **Factor Correlation & Turnover Optimization**:
   - Decreasing decay to 8 and adjusting neutralization to Industry slashed self-correlation from 0.5751 to 0.4377 while elevating Sharpe past 2.04 and Fitness to 2.58.

## Current state

- **Portfolio Submissions Tracked (6 Total)**:
  1. `14b75193` (`pv13` + `model16`): Sharpe 2.12 | Fitness 1.67
  2. `07b525d7` (`option8` + `model16`): Sharpe 2.19 | Fitness 1.83
  3. `14cb797d` (`analyst4` + `model16`): Sharpe 1.55 | Fitness 1.63
  4. `47da102d` (Fundamental Depr. + `model16`): Sharpe 1.36 | Fitness 1.09
  5. `55447c55` (`AnalystCoverage_CapDislocation_Reversion_5D`): Sharpe 2.15 | Fitness 1.60
  6. **`42bcbc75` (`OptionsSkew_PCRRegime_IntradayGainDispersion_8D`)**: Sharpe 2.04 | Fitness 2.58 | Turnover 13.23% | Sub-universe Sharpe 1.29 (**SUBMITTED!**)
- **PostgreSQL Research Store**: Fully synchronized, 2 submissions recorded as `SUBMITTED`, 60 `APPROVED`.
- **Codebase Integrity**: 72/72 tests passing, 0 ruff errors.

## Next session starts with

1. Run `/remember restore` to restore state.
2. Under the new single-alpha workflow, formulate the next single, high-conviction candidate targeting unmined datasets (`analyst4` earnings surprises / cashflow revision drift, or `model51` systematic risk orthogonalization).
3. Target Super Alpha metrics (Sharpe $\ge 2.0$, Fitness $\ge 2.50$, Self-Correlation $< 0.45$) to rapidly secure Gold Level Consultancy status.

## Open questions

- None. Alpha `42bcbc75` is officially submitted and all experimental records are locked in.

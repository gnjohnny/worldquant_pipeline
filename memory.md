# Memory — Alphas a7ad19b5 & 4d451183 Spectacular Submissions (8 Alphas Submitted)

Last updated: 2026-11-20 23:25 UTC+3

## What was built & achieved

- **Double Milestone: 8 Official Alphas Submitted to WorldQuant BRAIN**:
  - **Alpha 7 (`a7ad19b5`)**:
    - **Expression**: `ts_decay_linear(winsorize(ts_backfill(liabilities / assets, 90), std=2) * ts_arg_min(debt / equity, 250), 3)`
    - **Settings**: Universe: `TOP500`, Neutralization: `Industry`, Decay: `4`, Truncation: `0.08`, Delay: `1`
    - **Platform Metrics (8/8 PASS)**: Sharpe **2.10**, Fitness **1.86**, Turnover **2.91%**, Sub-universe Sharpe **1.10**, Self-Correlation **0.1726**
    - **Status**: `SUBMITTED`
  - **Alpha 8 (`4d451183`)**:
    - **Expression**: `group_neutralize(trade_when(rank(ts_delta(pcr_oi_30, 3)) < 0.35 && rank(ts_delta(pcr_oi_60, 3)) < 0.25 && rank(ts_delta(pcr_oi_90, 3)) < 0.45 && rank(adv20) > 0.12, ts_mean(implied_volatility_call_60 - implied_volatility_mean_60, 5), -1), industry)`
    - **Settings**: Universe: `TOP3000`, Neutralization: `Industry`, Decay: `6`, Truncation: `0.02`, Delay: `1`
    - **Submission Name**: `OptionsPCRTermContraction_CallIVPremium_TOP3000`
    - **Platform Metrics (8/8 PASS)**: Sharpe **2.35** 🔥, Fitness **3.12** 🚀 (Spectacular tier $\ge 2.20$), Turnover **6.83%**, Sub-universe Sharpe **1.02**, Self-Correlation **0.5535**
    - **Status**: `SUBMITTED`

- **Catalog & System Engine Fixes**:
  - Corrected physical unit misclassification for 39 options fields (`implied_volatility_*` and `historical_volatility_*`) from `USD` to `ratio` in `configs/data_sources.yaml` and PostgreSQL `data_fields`.
  - Added operator aliases: `ts_arg_min` (alias for `ts_argmin`), `ts_arg_max` (alias for `ts_argmax`).
  - Updated `winsorize` operator arity to `[1, 2]` to support keyword parameter `std=2`.
  - Added continuous fundamental fields `debt` and `equity` to `configs/data_sources.yaml` and PostgreSQL.
  - Hardened Gate G1 AST validator to identify event fields (`anl4_adxqfv110_*`) and reject invalid `ts_backfill` wrapping locally before simulation.

- **Batch 354 Registered (Tri-Candidate Batch Protocol)**:
  - Created [data/batch_354_tri_candidate_unmined_alphas.json](file:///C:/Users/Johnny/Agy_test/worldquant_pipeline/data/batch_354_tri_candidate_unmined_alphas.json) featuring 3 radically original, single-line candidates with 0% database collision across all gates G1, G2, G3+:
    1. `166e66c2`: `group_neutralize(ts_av_diff(correlation_last_60_days_spy, 60) * -ts_zscore(implied_volatility_mean_skew_60, 60), subindustry)`
    2. `6b1dcb7a`: `group_neutralize(-ts_skewness(returns, 60) * ts_zscore((close - vwap) / vwap, 20), subindustry)`
    3. `229eb5eb`: `group_neutralize(ts_zscore(unsystematic_risk_last_90_days / (systematic_risk_last_90_days + 0.001), 90) * -ts_zscore(close / ts_mean(close, 60), 20), subindustry)`

## Current Portfolio Submissions (8 Total)

1. `14b75193` (`pv13` + `model16`): Sharpe 2.12 | Fitness 1.67
2. `07b525d7` (`option8` + `model16`): Sharpe 2.19 | Fitness 1.83
3. `14cb797d` (`analyst4` + `model16`): Sharpe 1.55 | Fitness 1.63
4. `47da102d` (Fundamental Depr. + `model16`): Sharpe 1.36 | Fitness 1.09
5. `55447c55` (`AnalystCoverage_CapDislocation_Reversion_5D`): Sharpe 2.15 | Fitness 1.60
6. `42bcbc75` (`OptionsSkew_PCRRegime_IntradayGainDispersion_8D`): Sharpe 2.04 | Fitness 2.58
7. `a7ad19b5` (`BalanceSheetLeverage_DeleveragingCycle_TOP500`): Sharpe 2.10 | Fitness 1.86 | Turnover 2.91%
8. `4d451183` (`OptionsPCRTermContraction_CallIVPremium_TOP3000`): Sharpe 2.35 | Fitness 3.12 | Turnover 6.83%

## Strict Research Directives & Next Steps

1. **Immediate Lineage Discard (Rule 7.8)**:
   - The signal lineage of `4d451183` (`pcr_oi` multi-tenor delta contraction coupled with `implied_volatility_call - implied_volatility_mean`) and `a7ad19b5` (`liabilities / assets * ts_arg_min(debt / equity)`) are permanently retired from tweaking.
2. **Untouched Factor Frontiers**:
   - Focus next sprints on unmined statistical operators (`ts_skewness`, `ts_kurtosis`, `ts_corr`), market beta decoupling (`model51`), and intraday VWAP microstructure.

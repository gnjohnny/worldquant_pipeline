# Memory — Invariant 10 (Single-Line Mandate), Multi-Line Failure Diagnosis & Batch 337

Last updated: 2026-11-15 12:08 UTC+3

## What was built

- **Invariant 10 Permanently Enacted (Strict Single-Line Alpha Mandate)**:
  - Formally codified in `AGENTS.md` and `.agents/rules/worldquant_alpha_rules.md`: All alphas must strictly be formulated, generated, tested, and submitted as **100% single-line, fully nested mathematical expressions**.
  - Absolute ban on multi-line syntax, semicolons (`;`), and intermediate variable assignments (`var = expr;`).
- **Batch 337 Engineered & Registered in PostgreSQL (`data/batch_337_single_line_options_triplet.json`)**:
  - `4569d070`: Single-Line Variance Risk Premium conditioned on Cashflow Quality (`option8` + `model16`)
    - `group_neutralize(signed_power(min(max(group_zscore(historical_volatility_30 - implied_volatility_mean_30, industry) * group_rank(cashflow_efficiency_rank_derivative, industry), -2.5), 2.5), 2), industry)`
  - `3f153939`: Single-Line Volatility Term Structure Backwardation Reversion (`option8` + `model16`)
    - `group_neutralize(signed_power(min(max(group_zscore(implied_volatility_mean_90 - implied_volatility_mean_30, industry) * group_rank(cashflow_efficiency_rank_derivative, industry), -2.5), 2.5), 2), industry)`
  - `07b525d7`: Single-Line Downside Put Skew Exhaustion Conditioned on Quality (`option8` + `model16`)
    - `group_neutralize(signed_power(min(max(-group_zscore(implied_volatility_put_30 - implied_volatility_call_30, industry) * group_rank(cashflow_efficiency_rank_derivative, industry), -2.5), 2.5), 2), industry)`
- **Verification**:
  - AST Validator Gate G1 passing 100% on all single-line candidates.
  - All 72/72 tests passing in `pytest tests/ -v`.

## Decisions made & Root Cause Resolution

- **The Multi-Line Downfall Confirmed**:
  - The empirical platform score confirmed the user's breakthrough theory: Multi-line expressions with temporary variables created fatal discrepancies in WorldQuant BRAIN's backend scoring, portfolio uniqueness, and correlation calculation engine.
  - From this point forward, every single candidate alpha will be produced strictly in **one continuous nested line**.
- **Dataset Focus**:
  - `option8` (Implied/Historical Volatility Surface) paired with `model16` (Fundamental Quality) in pure single-line nested format.

## Current state

- **Invariant 10**: ACTIVE & STRICTLY ENFORCED.
- **Active Research Batch**: Batch 337 ([batch_337_single_line_options_triplet.json](file:///C:/Users/Johnny/Agy_test/worldquant_pipeline/data/batch_337_single_line_options_triplet.json)) — 100% single-line options volatility surface conditioned by fundamental cashflow efficiency.
- **Git & DB Synchronized**: All models, rules, and candidate IDs tracked in local PostgreSQL and committed to git.

## Next steps

1. Simulate Batch 337 (Candidates 1, 2, and 3) on the WorldQuant BRAIN simulator using the pure single-line expressions.
2. Verify that the single-line format eliminates correlation masking and provides genuine backtest metrics.
3. Validate against G0–G7 gates (Sharpe >= 1.25, Fitness >= 1.50, Turnover 1%–70%, Self-corr < 0.70).

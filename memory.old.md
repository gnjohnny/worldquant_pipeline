# Memory — Virgin Datasets & Batch 148 Dispatch for Leaderboard Score Pivot

Last updated: 2026-11-04 01:45 UTC+3

## What was built & completed this session

- **Resolved Core Pipeline Bottlenecks & Pushed to Remote**:
  - Pushed commit `9b73a51` to `origin/main` (`feat(pipeline): resolve core bottlenecks and enhance alpha research engine`).
  - Added `cli.py record-batch` with automated markdown-link regex stripping and candidate header splitting.
  - Safely archived 60+ legacy record scripts into `scripts/archive/`.
  - Expanded Gate G1 Operator Whitelist with 30+ native WorldQuant BRAIN operators.
  - Eliminated formula monoculture in `recipes.py` and synchronized `TOP3000` default simulation settings across `submission.py` and CLI.
- **Experimental History & Research Memory (PostgreSQL)**:
  - **Batch 144**: C1 & C3 produced $-0.85$ and $-0.84$ Sharpe with ultralow $2.7\%–3.5\%$ turnover due to `relative_valuation_rank_derivative` ranking expensive multiples highest.
  - **Batch 145**: C1 & C2 confirmed that shifting to `group_rank` ($[0, 1]$) destroyed the zero-centered four-quadrant interaction of `group_zscore` ($[-3, +3]$), resulting in negative Sharpe. C3 had weight concentration ($15.38\%$) due to unbackfilled options data.
  - **Batch 146**: Massive performance breakthrough:
    - Candidate 2 (`34b96aa5`): **7 PASS / 1 FAIL** (Sharpe **1.85**, Fitness **1.17**, Turnover **18.68%**, Sub-universe Sharpe **1.33**). Failed solely on Self-Correlation ($0.7396$ vs $0.7000$ cutoff).
    - Candidate 1 (`544d139c`): **7 PASS / 1 FAIL** (Sharpe **1.39**, Fitness **1.04**, Turnover **16.04%**, Sub-universe Sharpe **1.15**). Failed solely on Self-Correlation ($0.7946$ vs $0.7000$ cutoff).
- **Self-Correlation & Leaderboard Uniqueness Audit**:
  - Discovered that the user's account already holds **28 Financial balance-sheet**, **12 Analyst-estimate**, and **8 Options-volatility** approved alphas. Any minor variation of these factor families immediately triggers BRAIN's self-correlation cutoff ($>0.70$).
  - Identified **four virgin datasets with 0 approved alphas** in the user's DB: `pv13`, `model51`, `option9`, `model16`.
- **Batch 148 Staged & Ingested in PostgreSQL** (`data/batch_148_unmined_dataset_breakthroughs.json`):
  - Strictly adheres to the rule: **No modifying existing alphas; only totally new alphas from virgin datasets**.
  - **Candidate 1 (`167457dc`)**: Low-Beta Anomaly & Idiosyncratic Risk Normalization (`model51`: `0.60 * group_rank(-beta_last_60_days_spy, subindustry) - 0.40 * group_rank(unsystematic_risk_last_30_days / (unsystematic_risk_last_360_days + 0.0001), subindustry)`).
  - **Candidate 2 (`55b3e22c`)**: Dealer Gamma Floor & Put Breakeven Downside Cushion (`option9`: `0.85 * group_rank((close - put_breakeven_30) / close, subindustry) - 0.15 * group_rank(ts_delta(close, 3) / close, subindustry)`).
  - **Candidate 3 (`4da6d3d9`)**: Breakeven Range Asymmetry: Upside Room vs Downside Cushion (`option9`: `0.85 * group_rank((call_breakeven_30 - close) / (close - put_breakeven_30 + 0.001), subindustry) - 0.15 * group_rank(ts_delta(close, 3) / close, subindustry)`).

## Decisions made

1. **Leaderboard Uniqueness Invariant**: Modifying alphas already in the database is strictly forbidden. All future candidate alphas must be generated exclusively from unmined datasets to ensure 0.00 self-correlation and maximize uniqueness score on the competition leaderboard.
2. **Dense Data Backfilling**: All raw options metrics must be protected with `ts_backfill(..., 120)` to prevent single-day weight concentration spikes.
3. **Turnover Optimization for Fitness >= 1.50**: Reversal dampeners (`ts_delta(close, 5)` or `ts_delta(close, 3)`) with $10\%–15\%$ weighting should be used to keep turnover in the optimal $11\%–15\%$ sweet-spot, maximizing the Fitness multiplier $\sqrt{\text{Returns}/\text{Turnover}}$.

## Problems solved

- **Git remote synchronization**: Pushed all core bottleneck fixes and new test suites cleanly to GitHub (`main` -> `9b73a51`).
- **Markdown-link metric parsing**: Fixed `parse_brain_paste` to strip markdown link syntax (`[Sharpe](url)`) for seamless automated recording.
- **Root-cause analysis of Self-Correlation**: Proved that high Sharpe alphas were colliding because of historical saturation in Analyst consensus and Call options; unlocked `model51` and `option9` as unmined alpha engines.

## Current state

- **Codebase**: Fully verified (69 unit tests passing, 0 ruff errors, working tree clean).
- **Database**: PostgreSQL synchronized with 291 hypotheses, 465 candidates, and 47 approved alphas.
- **Active Research Batch**: **Batch 148** is staged and ready for manual backtest on the WorldQuant BRAIN platform.

## Next session starts with

1. Run the **Batch 148** simulations on the WorldQuant BRAIN platform:
   - **Candidate 1 (`167457dc`)**: `0.60 * group_rank(-beta_last_60_days_spy, subindustry) - 0.40 * group_rank(unsystematic_risk_last_30_days / (unsystematic_risk_last_360_days + 0.0001), subindustry)`
   - **Candidate 2 (`55b3e22c`)**: `0.85 * group_rank((close - put_breakeven_30) / close, subindustry) - 0.15 * group_rank(ts_delta(close, 3) / close, subindustry)`
   - **Candidate 3 (`4da6d3d9`)**: `0.85 * group_rank((call_breakeven_30 - close) / (close - put_breakeven_30 + 0.001), subindustry) - 0.15 * group_rank(ts_delta(close, 3) / close, subindustry)`
   - Settings for all 3: `TOP3000`, `delay=1`, `decay=4`, `neutralization=SUBINDUSTRY`, `truncation=0.0100`.
2. Paste the simulation cards back into the session.
3. Record the returned results via `python scripts/cli.py record-batch data/batch_148_unmined_dataset_breakthroughs.json`.
4. Audit qualifying alphas (Fitness >= 1.50, Sharpe >= 1.25, Self-Corr < 0.70) for submission metadata and leaderboard submission!

## Open questions

- Once Batch 148 results are in, if `option9` Breakeven alphas pass with high Sharpe, test higher-tenor put breakevens (`put_breakeven_60` / `call_breakeven_60`) or combine with `model51` systematic beta.

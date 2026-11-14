# Memory — Alpha 1 Submission (14b75193), Correlation Investigation & Overnight Score Tracking

Last updated: 2026-11-14 23:05 UTC+3

## What was built

- **Alpha 1 Submitted Today on WorldQuant BRAIN (`14b75193-47fc-457b-aa56-6125143e7177`)**:
  - Name: `SupplyChain_CashflowConditioned_ShockReversal_5D`
  - Domain: `alternative_data` (`pv13` + `model16`)
  - Expression: `cust_sig = ts_decay_linear(pv13_custretsig_retsig, 5); quality = group_rank(cashflow_efficiency_rank_derivative, industry); signal = -group_zscore(cust_sig, industry) * quality; clipped = min(max(signal, -2.5), 2.5); pwr = signed_power(clipped, 2); group_neutralize(pwr, industry)`
  - Settings: `TOP3000`, `delay=1`, `decay=4`, `neutralization=Industry`, `truncation=0.02`
  - Backtest Metrics: **8 PASS** | Sharpe: **2.12** | Fitness: **1.67** (GOOD/EXCELLENT $\ge 1.50$) | Turnover: **34.78%** | Sub-universe: **1.42** | Self-correlation: **0.6050** | Weight distribution: **PASS**
- **Batch 335 Evaluated & Recorded in PostgreSQL**:
  - `d9e237c6` (`model51` Idiosyncratic Risk): 4 PASS / 3 FAIL (Sharpe -1.27, Fitness -0.77, weight concentration fail) — `REJECTED`
  - `1f065970` (`option8` Variance Risk Premium VRP): 4 PASS / 3 FAIL (Sharpe 0.93, Fitness 0.56, Turnover 17.09%, Sub-universe 0.04) — `REJECTED`
  - `b84e4fd4` (`option8` Put-Call Ratio PCR): 4 PASS / 3 FAIL (Sharpe 0.78, Fitness 0.29, Turnover 31.72%, Sub-universe 0.11) — `REJECTED`
- **Batch 336 Engineered & Ingested into PostgreSQL (`data/batch_336_options_surface_conditioning.json`)**:
  - `63c1fd12`: Variance Risk Premium conditioned on Cashflow Quality (`option8` + `model16`)
  - `278d4f6f`: Volatility Term Structure Backwardation Reversion (`option8` + `model16`)
  - `9b1a126f`: Downside Put Skew Exhaustion conditioned on Cashflow Quality (`option8` + `model16`)
- **Verification**:
  - All 72/72 unit tests passing in `pytest tests/ -v`.
  - Clean git state synchronized with `origin/main`.

## Decisions made

- **Overnight Score Observation Pause**:
  - Paused further submissions until tomorrow's WorldQuant BRAIN platform score update to observe the exact empirical impact of `14b75193` on overall portfolio score, rank, and uniqueness.
- **Permanent Retirement of Submitted Lineage**:
  - Per Invariant 8 & 9, `pv13_custretsig_retsig` is locked/retired from future tweaking because an instance (`14b75193`) has been submitted to the user's active portfolio.
- **Untouched Dataset Exploration**:
  - Primary research pipeline shifted to `option8` (implied/historical vol surface) and `model16` (fundamental style derivatives).

## Problems solved & Critical Investigations

- **Single Submission Status Verified**:
  - Corrected pipeline logs to reflect that exactly **1 alpha** was submitted today (`14b75193`), with 3 remaining for the daily quota.
- **Multi-Line vs. Single-Line Correlation Discrepancy Investigation**:
  - The user observed that prior to submitting `14b75193`:
    - The multi-line expression with variables (`cust_sig = ...; ...`) tested with Self-correlation = **0.6050** (PASS).
    - When rewritten/collapsed into a single line, the simulator reported Self-correlation = **0.9916** (FAIL).
  - Hypothesis A: The one-line version collided with an existing alpha or session state on the platform.
  - Hypothesis B: WorldQuant BRAIN's simulator parses multi-statement assignments with local variables differently than deeply nested single-line formulas during self-correlation evaluation.
  - Decision: Wait for tomorrow's platform score update to see if the score rebounds or drops, which will reveal whether BRAIN evaluated `14b75193` as orthogonal (0.6050) or redundant (0.9916).

## Current state

- **Today's Submissions**: **1 / 4** (`14b75193`, Supply Chain Cashflow Reversion, Sharpe 2.12, Fitness 1.67)
- **Remaining Daily Target**: **3 Alphas**
- **Pending Batch Ready for Testing**: Batch 336 on `option8` + `model16` ([batch_336_options_surface_conditioning.json](file:///C:/Users/Johnny/Agy_test/worldquant_pipeline/data/batch_336_options_surface_conditioning.json))
- **Prior Portfolio Alphas**:
  - Alpha 1 (`ee3a5f26`): `Cauchy_Intraday_Dispersion_Reversion_80D` (`pv1`)
  - Alpha 2 (`a3f97d60`): `Cauchy_Volume_Surge_Liquidity_Reversion_120D` (`pv1`)
  - Alpha 3 (`018d9ba1`): `Cauchy_Institutional_VWAP_Displacement_Reversion_120D` (`pv1`)

## Next session starts with

1. Check the WorldQuant BRAIN dashboard for updated Score, Rank, and Uniqueness.
2. If the score goes UP: confirms `14b75193` provided genuine diversification (0.6050 correlation) and multi-statement syntax executes cleanly on the backend.
3. If the score DROPS: investigate the single-line vs multi-line parser behavior and inspect which exact Alpha ID triggered the 0.9916 collision.
4. Run Batch 336 on the BRAIN simulator to discover and validate today's remaining 3 qualifying alphas.

## Open questions

- What exact Alpha ID did the 0.9916 self-correlation collision flag against on the simulator?
- How does the WorldQuant BRAIN backend calculate portfolio uniqueness on multi-statement expressions?

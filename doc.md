# worldquant_pipeline — User & Research Guide

A research-first, AI-assisted workbench designed to discover, validate, rank, document, and prepare candidate alphas for **WorldQuant BRAIN**.

---

## 1. System Overview & Core Philosophy

Alpha research on WorldQuant BRAIN is often hindered by brute-force formula mining, statistical overfitting (p-hacking), look-ahead bias, and lost historical context. 

`worldquant_pipeline` enforces institutional-grade scientific discipline:
- **AI Proposes Falsifiable Hypotheses:** Generates ideas rooted in sound economic or behavioral mechanisms (at zero subscription cost).
- **Deterministic AST Validator (Gate G1):** Validates operator syntax, argument arity, parameter constraints, and field whitelists locally before touching the platform.
- **Manual-First Platform Adapter:** Formats expressions and simulation settings for fast copy-pasting into the WorldQuant BRAIN web dashboard without requiring restricted consultant API keys.
- **Immutable PostgreSQL Research Memory:** Permanently records every candidate, variation, simulation metric, and reject/accept decision. Negative knowledge is preserved so future AI prompts avoid repeating failed patterns.

```
+-----------------------------------------------------------------------------------+
|                              RESEARCH WORKFLOW                                    |
|                                                                                   |
|  1. CLI: prompt  --->  2. Chat Copilot  --->  3. CLI: ingest                      |
|     (Exports fields       (Brainstorms           (Parses AST &                    |
|      & failure memory)     JSON candidates)       validates Gate G1)              |
|                                                           |                       |
|                                                           v                       |
|  6. CLI: record  <---  5. BRAIN Web     <---  4. CLI: show                        |
|     (Logs metrics &       (Simulates             (Displays formula &              |
|      audits decision)      expression)            simulation settings)            |
+-----------------------------------------------------------------------------------+
```

---

## 2. Prerequisites & Environment Setup

### System Requirements
- **Python:** 3.10+
- **PostgreSQL:** Local PostgreSQL server running on port `5432`
- **Git**

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/gnjohnny/worldquant_pipeline.git
   cd worldquant_pipeline
   ```

2. **Configure Environment Variables:**
   Copy `.env.example` to `.env` (or configure your existing `.env`):
   ```ini
   DATABASE_URL=postgresql://postgres:your_password@localhost:5432/worldquant_brain
   RESEARCH_DOMAIN=price_volume
   LOG_LEVEL=INFO
   ```
   *(Note: Any URL-encoded special characters in your PostgreSQL password are handled automatically).*

3. **Initialize Database Tables & Seed Data Fields:**
   Run the database bootstrap script:
   ```bash
   python scripts/init_db.py
   ```
   This creates all required tables (`research_hypotheses`, `data_fields`, `alpha_candidates`, `experiments`, `experiment_metrics`, `decisions`) and seeds the 14 approved WorldQuant BRAIN data fields.

---

## 3. Daily Research Workflow (Step-by-Step Guide)

### Step 1: Check Current Research Status
View active hypotheses, candidate statuses, and recent alphas:
```bash
python scripts/cli.py status
```

---

### Step 2: Export Copilot Brainstorming Prompt
Generate a structured research prompt loaded with the active field catalog, allowed operators, and negative knowledge (past rejected candidates):
```bash
python scripts/cli.py prompt --domain price_volume
```
*(You can specify any domain, e.g. `--domain momentum`, `--domain analyst`, or `--domain fundamental`)*.

---

### Step 3: Brainstorm with Antigravity AI Copilot
Copy the generated prompt from your terminal and paste it into this chat session. 

The AI will output a structured JSON candidate batch adhering to the following schema:
```json
{
  "hypotheses": [
    {
      "title": "Short-Horizon Volume-Weighted Price Reversal",
      "domain": "price_volume",
      "economic_rationale": "Institutional liquidity shocks cause transient price overshoot over 1-to-5 day horizons. When price deviates sharply from VWAP accompanied by volume surges, market maker replenishment leads to mean-reversion within subindustries.",
      "expected_direction": "negative",
      "intended_horizon": "5d",
      "confounders": ["sector_momentum", "earnings_window"],
      "falsification_test": "Returns diminish or reverse when holding period exceeds 10 days or neutralization is removed.",
      "candidates": [
        {
          "expression": "-group_rank((close - vwap) / close, subindustry)",
          "rationale": "Daily close-to-VWAP divergence normalized within subindustry",
          "expected_direction": "negative"
        },
        {
          "expression": "-group_rank(ts_delta(close, 3) * (volume / ts_mean(volume, 20)), subindustry)",
          "rationale": "3-day price momentum weighted by abnormal volume surge relative to 20-day average",
          "expected_direction": "negative"
        }
      ]
    }
  ]
}
```

Save this JSON to a file in `experiments/` (e.g. `experiments/my_candidates.json`).

---

### Step 4: Ingest and Validate Expressions (Gates G1 & G3)
Run the deterministic static validator on your JSON file:
```bash
python scripts/cli.py ingest experiments/my_candidates.json
```

**What the pipeline does automatically:**
1. **Gate G1 (AST Validation):** Tokenizes and parses each formula into an Abstract Syntax Tree. Validates that:
   - Operators exist in `configs/research.yaml`.
   - Operator arity matches (e.g. `ts_rank(x, d)` must take 2 arguments).
   - Lookback arguments are positive integers.
   - All fields exist in `configs/data_sources.yaml`.
2. **Gate G3 (Deduplication):** Canonicalizes expressions (commutative sorting, e.g. `a + b` == `b + a`) and computes SHA-256 hashes. Duplicates are flagged and skipped.
3. **Persistence:** Valid candidates are saved to PostgreSQL with status `VALIDATED` and assigned a stable UUID.

---

### Step 5: View Platform Simulation Card
To view a candidate ready for WorldQuant BRAIN web simulation, provide its ID (or the first 8 characters):
```bash
python scripts/cli.py show 7f01bd1f
```

**Terminal Output:**
```
WorldQuant BRAIN Simulation Card -- Candidate `7f01bd1f-ccb6-4718-b86f-16db39eb393c`

+-------------------- Formula (Copy & Paste to Platform) ---------------------+
| -group_rank((close - vwap) / close, subindustry)                            |
+-----------------------------------------------------------------------------+

           Platform Settings            
+--------------------------------------+
| Parameter      | Recommended Setting |
|----------------+---------------------|
| Region         | USA                 |
| Universe       | TOP3000             |
| Delay          | 1                   |
| Decay          | 4                   |
| Neutralization | SUBINDUSTRY         |
| Truncation     | 0.0100              |
+--------------------------------------+

Hypothesis: Short-Horizon Volume-Weighted Price Reversal
Rationale: Institutional liquidity shocks cause transient price overshoot...
Expected Horizon: 5d
```

---

### Step 6: Simulate in WorldQuant BRAIN Web Dashboard
1. Log in to [WorldQuant BRAIN Platform](https://platform.worldquantbrain.com/).
2. Navigate to **Simulate Alpha**.
3. Paste the expression and set the parameters exactly as shown on the simulation card (`USA`, `TOP3000`, `delay=1`, `neutralization=Subindustry`, `decay=4`, `truncation=0.01`).
4. Click **Simulate** and note the returned performance metrics:
   - Sharpe Ratio
   - Turnover %
   - Fitness
   - Maximum Drawdown %

---

### Step 7: Record Results & Log Auditable Decision (Gate G4 & G5)
Record the simulation metrics back into the pipeline:
```bash
python scripts/cli.py record 7f01bd1f
```

The interactive prompt will:
1. Ask for **Sharpe Ratio** and **Turnover** (and optional Fitness/Drawdown).
2. Automatically run **Gate G5 checks**:
   - Checks minimum Sharpe ($\ge 1.25$).
   - Checks turnover trading friction bounds ($1.0\% \le \text{turnover} \le 70.0\%$).
   - Flags maximum drawdown violations ($> 25\%$).
3. Prompt you for an explicit decision:
   - `APPROVED`
   - `REJECTED`
   - `NEEDS_REVISION`
4. Enforce a **mandatory reason text** explaining why the candidate was approved or rejected.
5. Save the experiment run, metrics, and decision into PostgreSQL.

---

## 4. Supported Operator & Field DSL Reference

### Whitelisted Time-Series Operators
| Operator | Arity | Description | Example |
|---|:---:|---|---|
| `ts_rank(x, d)` | 2 | Time-series rank of $x$ over $d$ days | `ts_rank(close, 10)` |
| `ts_delay(x, d)` | 2 | Value of $x$ delayed by $d$ days | `ts_delay(close, 1)` |
| `ts_delta(x, d)` | 2 | $x - \text{ts\_delay}(x, d)$ | `ts_delta(close, 5)` |
| `decay_linear(x, d)` | 2 | Linear decay of $x$ over $d$ days | `decay_linear(returns, 10)` |
| `ts_mean(x, d)` | 2 | Rolling average over $d$ days | `ts_mean(volume, 20)` |
| `ts_std_dev(x, d)` | 2 | Rolling standard deviation over $d$ days | `ts_std_dev(close, 20)` |
| `ts_max(x, d)` | 2 | Rolling maximum over $d$ days | `ts_max(high, 10)` |
| `ts_min(x, d)` | 2 | Rolling minimum over $d$ days | `ts_min(low, 10)` |
| `ts_sum(x, d)` | 2 | Rolling sum over $d$ days | `ts_sum(volume, 5)` |
| `ts_correlation(x, y, d)` | 3 | Rolling correlation between $x$ and $y$ over $d$ days | `ts_correlation(close, volume, 20)` |
| `ts_covariance(x, y, d)` | 3 | Rolling covariance between $x$ and $y$ over $d$ days | `ts_covariance(returns, vwap, 10)` |

### Whitelisted Cross-Sectional & Math Operators
| Operator | Arity | Description | Example |
|---|:---:|---|---|
| `rank(x)` | 1 | Cross-sectional percentile rank ($0$ to $1$) | `rank(returns)` |
| `group_rank(x, group)` | 2 | Cross-sectional rank within group | `group_rank(close, subindustry)` |
| `group_neutralize(x, group)` | 2 | Neutralize $x$ against group | `group_neutralize(returns, sector)` |
| `zscore(x)` | 1 | Cross-sectional z-score $(x - \mu) / \sigma$ | `zscore(close)` |
| `normalize(x)` | 1 | Scales values so $\sum |x| = 1$ | `normalize(volume)` |
| `signed_power(x, y)` | 2 | $\text{sign}(x) \cdot (|x|^y)$ | `signed_power(returns, 2)` |
| `abs(x)` | 1 | Absolute value | `abs(returns)` |
| `sign(x)` | 1 | Sign function ($-1, 0, 1$) | `sign(ts_delta(close, 1))` |
| `log(x)` | 1 | Natural logarithm | `log(volume)` |
| `? :` | 3 | Ternary conditional operator | `close > open ? returns : -returns` |

### Approved Data Fields
- **Price / Volume:** `close`, `open`, `high`, `low`, `volume`, `returns`, `vwap`, `sharesout`, `cap`
- **Classifications:** `subindustry`, `industry`, `sector`
- **Fundamentals:** `bookvalue_ps`, `ebitda`

*(To add new fields or operators, update `configs/data_sources.yaml` and `configs/research.yaml`)*.

---

## 5. Quality Gates Reference (G0–G7)

| Gate | Description | Enforcement Point |
|---|---|---|
| **G0: Provenance** | Rationale, domain, horizon, and timing assumptions documented. | `hypotheses/schemas.py` |
| **G1: Syntax & Whitelist** | Deterministic AST syntax check; operators/fields validated against catalog. | `expressions/validator.py` |
| **G2: Data Integrity** | Delay $\ge 1$ enforced; no look-ahead bias. | `configs/research.yaml` |
| **G3: Baseline Novelty** | Deduplication via canonical AST sorting and SHA-256 hash. | `expressions/canonicalize.py` |
| **G4: Platform Simulation** | Simulation run recorded with exact settings and platform metrics. | `cli.py record` |
| **G5: Robustness Checks** | Automated checks for Sharpe $\ge 1.25$ and turnover between $1\%$ and $70\%$. | `evaluation/gates.py` |
| **G6: Diversity** | Candidate must not replicate existing signals in research memory. | `storage/models.py` |
| **G7: Human Audit** | Mandatory human approval decision with recorded rationale before submission. | `storage/models.py` |

---

## 6. Running Automated Tests & Code Quality

```bash
# Run all unit tests (AST parser, storage, hypotheses, gates)
python -m pytest tests/unit/ -v

# Run linter & code standards check
ruff check .
```

---

## 7. Troubleshooting & FAQs

### Q: Why did an expression fail ingestion?
The error message will display the exact reason:
- `Unknown or disallowed operator 'xyz'`: Check `configs/research.yaml` for allowed operator spellings.
- `Operator 'ts_rank' expects 2 arguments, but got 1`: Check operator arity.
- `Unknown or unpermitted field 'xyz'`: Check `configs/data_sources.yaml` for approved field names.

### Q: How do I change the default simulation parameters?
Edit `configs/research.yaml` under `simulation_defaults`:
```yaml
simulation_defaults:
  region: "USA"
  universe: "TOP3000"
  delay: 1
  decay: 4
  neutralization: "SUBINDUSTRY"
  truncation: 0.0100
```

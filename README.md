# worldquant_pipeline

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![PostgreSQL](https://img.shields.io/badge/database-PostgreSQL-336791.svg)](https://www.postgresql.org/)
[![SQLAlchemy 2.0](https://img.shields.io/badge/ORM-SQLAlchemy%202.0-red.svg)](https://www.sqlalchemy.org/)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![Tests: pytest](https://img.shields.io/badge/tests-24%20passed-brightgreen.svg)](https://pytest.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An institutional-grade, research-first quantitative workbench designed to discover, validate, rank, document, and prepare candidate alphas for **WorldQuant BRAIN**.

`worldquant_pipeline` bridges the gap between creative hypothesis generation and rigorous statistical discipline. It pairs an AI copilot (generating falsifiable economic mechanisms at zero subscription cost) with a deterministic Abstract Syntax Tree (AST) expression validator and an immutable local PostgreSQL experiment store.

---

## Key Features

- **Zero-Cost Copilot Mode**: CLI-driven prompt export and JSON ingestion for brainstorming grounded hypotheses with AI in chat—requiring zero paid API subscriptions.
- **Deterministic AST Validator (Gate G1)**: Pure Python recursive-descent parser that verifies WorldQuant BRAIN operator syntax, operator arity, parameter constraints, and field whitelists locally before consuming simulation effort.
- **Manual-First Platform Adapter**: Prepares formatted copy-paste expressions and exact simulation parameters (`TOP3000`, `delay=1`, `neutralization=Subindustry`, `decay=4`, `truncation=0.0100`) for the BRAIN web dashboard.
- **Immutable PostgreSQL Research Memory**: Relational tracking of hypotheses, candidates, simulation metrics, and accept/reject decisions. Preserves negative knowledge so future iterations never repeat failed ideas.
- **Quality Gates (G0–G7)**: Enforces explicit checks for look-ahead bias, parameter sensitivity, turnover friction bounds ($1\%$ to $70\%$), and duplicate formulas ($O(1)$ canonical SHA-256 deduplication).

---

## Research Workflow

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

## Quickstart

### 1. Prerequisites
- Python 3.10+
- PostgreSQL running locally (port 5432)

### 2. Installation
```bash
# Clone the repository
git clone https://github.com/gnjohnny/worldquant_pipeline.git
cd worldquant_pipeline

# Install dependencies
pip install -r pyproject.toml
# Or install core packages:
pip install sqlalchemy psycopg2-binary pydantic typer rich pyyaml python-dotenv pytest ruff
```

### 3. Configure Database
Copy `.env.example` to `.env`:
```ini
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/worldquant_brain
RESEARCH_DOMAIN=price_volume
LOG_LEVEL=INFO
```

### 4. Initialize Database & Seed Field Catalog
```bash
python scripts/init_db.py
```
This boots the database schema and seeds the catalog with 14 approved WorldQuant BRAIN fields.

---

## CLI Usage

The pipeline provides an interactive Rich terminal interface via `scripts/cli.py`:

```bash
# 1. View overall research status and candidate ledger
python scripts/cli.py status

# 2. Export brainstorming prompt with active data fields & past rejections
python scripts/cli.py prompt --domain price_volume

# 3. Ingest candidate JSON batch from chat (runs Gate G1 AST check & deduplication)
python scripts/cli.py ingest experiments/cycle_01_liquidity_reversal.json

# 4. View simulation card ready for the BRAIN web platform
python scripts/cli.py show <candidate_id>

# 5. Record returned simulation metrics and log an auditable decision
python scripts/cli.py record <candidate_id>
```

---

## Candidate Batch Example

Candidate batches generated during chat follow a strict schema:

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

---

## Quality Gates (G0–G7)

| Gate | Description | Enforcement Point |
|---|---|---|
| **G0: Provenance** | Rationale, domain, horizon, and timing assumptions documented. | `hypotheses/schemas.py` |
| **G1: Syntax & Whitelist** | Deterministic AST syntax check; operators/fields validated against catalog. | `expressions/validator.py` |
| **G2: Data Integrity** | Delay $\ge 1$ enforced; no future leakage. | `configs/research.yaml` |
| **G3: Baseline Novelty** | Deduplication via canonical AST sorting and SHA-256 hash. | `expressions/canonicalize.py` |
| **G4: Platform Simulation** | Simulation run recorded with exact settings and platform metrics. | `cli.py record` |
| **G5: Robustness Checks** | Automated checks for Sharpe $\ge 1.25$ and turnover between $1\%$ and $70\%$. | `evaluation/gates.py` |
| **G6: Diversity** | Candidate must not replicate existing signals in research memory. | `storage/models.py` |
| **G7: Human Audit** | Mandatory human approval decision with recorded rationale before submission. | `storage/models.py` |

---

## Repository Structure

```
worldquant_pipeline/
├── configs/
│   ├── research.yaml          # Operator catalog, arity rules, simulation defaults
│   └── data_sources.yaml      # Catalog of approved data fields and delay rules
├── doc.md                     # Comprehensive user and research guide
├── experiments/               # Validated candidate alpha JSON batches
├── scripts/
│   ├── init_db.py             # PostgreSQL table bootstrapper & field seeder
│   └── cli.py                 # CLI workbench entrypoint
├── src/worldquant_pipeline/
│   ├── brain/                 # Platform adapter (manual simulation cards)
│   ├── cli/                   # Typer CLI & Rich terminal rendering
│   ├── config/                # Pydantic settings & YAML loaders
│   ├── evaluation/            # Quality gates G0–G7 runner
│   ├── exceptions.py          # Domain exceptions
│   ├── expressions/           # AST tokenizer, parser, validator, canonicalizer
│   ├── hypotheses/            # Schemas, copilot prompt generator, JSON importer
│   └── storage/               # SQLAlchemy 2.0 models & database session engine
├── tests/
│   └── unit/                  # Automated unit test suite (24 tests)
├── pyproject.toml             # Project dependencies and tool configurations
└── README.md
```

---

## Testing & Quality

Run the unit test suite:
```bash
python -m pytest tests/unit/ -v
```

Run code formatting and lint checks:
```bash
ruff check .
```

---

## Disclaimer

This project is a personal research workbench and educational tool for quantitative research on WorldQuant BRAIN. It is not affiliated with, officially endorsed by, or sponsored by WorldQuant LLC. Historical simulation results do not guarantee future performance or acceptance into consultant programs.

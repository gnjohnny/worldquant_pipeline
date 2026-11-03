"""Record Batch 98 simulation results in PostgreSQL."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from worldquant_pipeline.storage.database import get_session
from worldquant_pipeline.storage.models import (
    AlphaCandidate,
    Decision,
    Experiment,
    ExperimentMetric,
)

with get_session() as session:
    batch_records = [
        (
            "4a0c055e",
            "TOP1000",
            "Subindustry",
            5,
            {"sharpe": 1.12, "fitness": 0.76, "turnover": 0.1260, "sub_universe_sharpe": 0.80},
            "Candidate 1 (FFO Operating Cash Margin Convexity in TOP1000 Subindustry, Decay 5): 5 PASS / 2 FAIL. Sharpe 1.12, Sub-universe Sharpe 0.80, Turnover 12.60%.",
            "NEEDS_REVISION",
        ),
        (
            "3a5d00fd",
            "TOP1000",
            "Subindustry",
            5,
            {"error": 1.0},
            "Candidate 2 (Domestic EBIT & Analyst Buy in TOP1000 Subindustry, Decay 5): FAILED. Operator ts_backfill does not support event inputs on anl4_buy.",
            "REJECTED",
        ),
        (
            "1ade0e8a",
            "TOP1000",
            "Sector",
            5,
            {"sharpe": 1.39, "fitness": 1.15, "turnover": 0.1137, "sub_universe_sharpe": 1.38, "self_correlation": 0.7070},
            "Candidate 3 (Sector-Neutral Cash Flow Elevation in TOP1000 Sector, Decay 5): 7 PASS / 1 FAIL. Sharpe 1.39, Sub-universe Sharpe 1.38, Fitness 1.15 passed. Self-correlation 0.7070 narrowly failed cutoff 0.70.",
            "NEEDS_REVISION",
        ),
    ]

    for cid_prefix, universe, neut, decay, metrics, reason, decision in batch_records:
        cand = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith(cid_prefix)).first()
        if cand:
            exp = Experiment(
                candidate_id=cand.id,
                status="COMPLETED" if "error" not in metrics else "FAILED",
                universe=universe,
                delay=1,
                decay=decay,
                neutralization=neut,
                truncation=0.0100,
            )
            session.add(exp)
            session.flush()

            for k, v in metrics.items():
                session.add(ExperimentMetric(experiment_id=exp.id, metric_name=k, metric_value=v, source="BRAIN_PLATFORM"))

            cand.status = decision
            dec = Decision(
                candidate_id=cand.id,
                decision=decision,
                reason=reason,
                reviewer="HUMAN_RESEARCHER",
            )
            session.add(dec)

    session.commit()
    print("Batch 98 simulation results logged successfully in PostgreSQL.")

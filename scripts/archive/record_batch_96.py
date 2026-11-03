"""Record Batch 96 simulation results in PostgreSQL."""
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
            "42f371e0",
            "TOP1000",
            "Industry",
            6,
            {"sharpe": 1.28, "fitness": 1.17, "turnover": 0.1029, "sub_universe_sharpe": 1.32, "self_correlation": 0.6808},
            "Candidate 1 (Cash Flow Per Share Yield with 90d Delta Momentum in TOP1000 Industry, Decay 6): 8 PASS / 0 FAIL. Sharpe 1.28, Sub-universe Sharpe 1.32, Turnover 10.29%, Self-correlation 0.6808 passed. Fitness 1.17 below Gold 1.50 cutoff.",
            "NEEDS_REVIEW",
        ),
        (
            "852b2e90",
            "TOP1000",
            "Industry",
            6,
            {"sharpe": 1.12, "fitness": 0.68, "turnover": 0.0868, "sub_universe_sharpe": 0.97},
            "Candidate 2 (Clean Convex Cash Flow Yield & Momentum in TOP1000 Industry, Decay 6): 5 PASS / 2 FAIL. Sharpe 1.12, Sub-universe Sharpe 0.97, Turnover 8.68%.",
            "NEEDS_REVISION",
        ),
        (
            "e0612b63",
            "TOP1000",
            "Subindustry",
            5,
            {"sharpe": 0.87, "fitness": 0.50, "turnover": 0.0981, "sub_universe_sharpe": 1.19},
            "Candidate 3 (EBITDA Margin Convexity & Operating Leverage in TOP1000 Subindustry, Decay 5): 5 PASS / 2 FAIL. Sub-universe Sharpe 1.19 strong, Turnover 9.81%, Sharpe 0.87 below cutoff.",
            "NEEDS_REVISION",
        ),
    ]

    for cid_prefix, universe, neut, decay, metrics, reason, decision in batch_records:
        cand = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith(cid_prefix)).first()
        if cand:
            exp = Experiment(
                candidate_id=cand.id,
                status="COMPLETED",
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
    print("Batch 96 simulation results logged successfully in PostgreSQL.")

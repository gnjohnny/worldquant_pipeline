"""Record Batch 97 simulation results in PostgreSQL."""
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
            "92fc9005",
            "TOP1000",
            "Subindustry",
            5,
            {"sharpe": -0.19, "fitness": -0.04, "turnover": 0.0555, "sub_universe_sharpe": -0.43},
            "Candidate 1 (Multi-Factor Profitability & Growth in TOP1000 Subindustry, Decay 5): 4 PASS / 3 FAIL. Low turnover 5.55%, but negative Sharpe -0.19.",
            "REJECTED",
        ),
        (
            "7aa6d7b6",
            "TOP1000",
            "Subindustry",
            5,
            {"sharpe": -0.80, "fitness": -0.35, "turnover": 0.2325, "sub_universe_sharpe": -0.33},
            "Candidate 2 (Options Put Breakeven Distance in TOP1000 Subindustry, Decay 5): 5 PASS / 2 FAIL. Sharpe -0.80 and Fitness -0.35 below cutoffs.",
            "REJECTED",
        ),
        (
            "909b88b3",
            "TOP1000",
            "Subindustry",
            5,
            {"sharpe": 0.46, "fitness": 0.15, "turnover": 0.2260, "sub_universe_sharpe": 0.35},
            "Candidate 3 (Market Correlation Decoupling in TOP1000 Subindustry, Decay 5): 4 PASS / 3 FAIL. Failed weight concentration and Sharpe cutoff.",
            "REJECTED",
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
    print("Batch 97 simulation results logged successfully in PostgreSQL.")

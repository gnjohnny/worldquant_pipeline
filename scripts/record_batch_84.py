"""Record Batch 84 simulation results in PostgreSQL."""
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
            "e9d79b67",
            "TOP1000",
            "Subindustry",
            5,
            {"sharpe": -0.51, "fitness": -0.34, "turnover": 0.0331, "sub_universe_sharpe": -0.25},
            "Candidate 1 (Fundamental Style Derivatives in TOP1000 Subindustry, Decay 5): 5 PASS / 2 FAIL. Sharpe -0.51 and Fitness -0.34 fail cutoffs. Derivative ranks without price normalization had negative drift.",
            "REJECTED",
        ),
        (
            "f85612e2",
            "TOP1000",
            "Subindustry",
            5,
            {"sharpe": -0.11, "fitness": -0.02, "turnover": 0.2683, "sub_universe_sharpe": -0.07},
            "Candidate 2 (IV Term Structure Slope in TOP1000 Subindustry, Decay 5): 3 PASS / 4 FAIL. Failed weight concentration, unit warning on scalar addition (+ 0.001), Sharpe -0.11 and Fitness -0.02 fail cutoffs.",
            "REJECTED",
        ),
        (
            "c518bc6e",
            "TOP1000",
            "Subindustry",
            5,
            {"sharpe": 0.22, "fitness": 0.06, "turnover": 0.0525, "sub_universe_sharpe": 0.47},
            "Candidate 3 (Standardized Unexpected Sales in TOP1000 Subindustry, Decay 5): 5 PASS / 2 FAIL. Sub-universe Sharpe 0.47 passed, zero warnings, but Sharpe 0.22 and Fitness 0.06 were below hurdle due to low turnover (5.25%).",
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
    print("Batch 84 simulation results logged successfully in PostgreSQL.")

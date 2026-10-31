"""Record Batch 88 simulation results in PostgreSQL."""
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
            "f3ae2579",
            "TOP1000",
            "Subindustry",
            5,
            {"sharpe": -0.05, "fitness": -0.01, "turnover": 0.0730, "sub_universe_sharpe": 0.25},
            "Candidate 1 (Analyst Dispersion vs Revision in TOP1000 Subindustry, Decay 5): 5 PASS / 2 FAIL. Sub-universe Sharpe 0.25 was positive, but overall Sharpe -0.05 failed cutoff.",
            "REJECTED",
        ),
        (
            "b25f178c",
            "TOP1000",
            "Subindustry",
            5,
            {"sharpe": -0.58, "fitness": -0.09, "turnover": 0.6813, "sub_universe_sharpe": -0.10},
            "Candidate 2 (Option PCR Volume Flow in TOP1000 Subindustry, Decay 5): 4 PASS / 3 FAIL. Failed weight concentration, Sharpe -0.58 and Fitness -0.09 fail cutoffs.",
            "REJECTED",
        ),
        (
            "b3a38b22",
            "TOP1000",
            "Subindustry",
            5,
            {"sharpe": -0.50, "fitness": -0.33, "turnover": 0.0332, "sub_universe_sharpe": -0.23},
            "Candidate 3 (Earnings Certainty vs Growth Acceleration in TOP1000 Subindustry, Decay 5): 5 PASS / 2 FAIL. Sharpe -0.50 and Fitness -0.33 fail cutoffs.",
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
    print("Batch 88 simulation results logged successfully in PostgreSQL.")

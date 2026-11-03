"""Record Batch 89 simulation results in PostgreSQL."""
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
            "5ece64cf",
            "TOP1000",
            "Subindustry",
            5,
            {"sharpe": 0.87, "fitness": 0.59, "turnover": 0.1038, "sub_universe_sharpe": 0.68},
            "Candidate 1 (Enterprise Revenue Yield & Top-Line Sales Acceleration in TOP1000 Subindustry, Decay 5): 5 PASS / 2 FAIL. Sharpe 0.87 and Fitness 0.59 below cutoffs.",
            "REJECTED",
        ),
        (
            "9e14c6bd",
            "TOP1000",
            "Subindustry",
            5,
            {"sharpe": 0.57, "fitness": 0.30, "turnover": 0.1058, "sub_universe_sharpe": 0.45},
            "Candidate 2 (Operating Cash Solvency & Long-Term Debt Coverage in TOP1000 Subindustry, Decay 5): 5 PASS / 2 FAIL / 1 WARNING. Sharpe 0.57 and Fitness 0.30 below cutoffs. Unit warning on debt_lt + close * 100.",
            "REJECTED",
        ),
        (
            "1cffca20",
            "TOP1000",
            "Subindustry",
            6,
            {"sharpe": 0.85, "fitness": 0.42, "turnover": 0.1984, "sub_universe_sharpe": 0.38},
            "Candidate 3 (1-Year LEAP Call Option Term Contango in TOP1000 Subindustry, Decay 6): 4 PASS / 3 FAIL. Sharpe 0.85 and Fitness 0.42 below cutoffs. Sub-universe Sharpe 0.38 failed cutoff 0.45.",
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
    print("Batch 89 simulation results logged successfully in PostgreSQL.")

"""Record Batch 90 simulation results in PostgreSQL."""
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
            "e0e7c6b8",
            "TOP1000",
            "Subindustry",
            5,
            {"sharpe": -0.03, "fitness": -0.00, "turnover": 0.3501, "sub_universe_sharpe": -0.10},
            "Candidate 1 (Options Forward Term Slope in TOP1000 Subindustry, Decay 5): 3 PASS / 4 FAIL. Failed weight concentration and Sharpe/Fitness cutoffs.",
            "REJECTED",
        ),
        (
            "ab16d6a1",
            "TOP1000",
            "Subindustry",
            5,
            {"sharpe": -0.43, "fitness": -0.14, "turnover": 0.0508, "sub_universe_sharpe": -0.84},
            "Candidate 2 (Balance Sheet Net Cash Solvency in TOP1000 Subindustry, Decay 5): 4 PASS / 3 FAIL. Sub-universe Sharpe -0.84 and Sharpe -0.43 failed cutoffs.",
            "REJECTED",
        ),
        (
            "584b6a9f",
            "TOP1000",
            "Subindustry",
            5,
            {"sharpe": 0.83, "fitness": 0.52, "turnover": 0.1119, "sub_universe_sharpe": 0.88},
            "Candidate 3 (Forward Cash Flow & Dividend Consensus Yield in TOP1000 Subindustry, Decay 5): 5 PASS / 2 FAIL. Positive Sharpe 0.83, Sub-universe Sharpe 0.88 passed cutoff 0.44. Turnover 11.19% clean. Needs elevation to reach 1.25 Sharpe.",
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
    print("Batch 90 simulation results logged successfully in PostgreSQL.")

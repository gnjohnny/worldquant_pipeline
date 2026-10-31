"""Record Batch 99 Candidate 1 and Candidate 3 simulation results in PostgreSQL."""
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
    # 1. Candidate 1: 86a4f50e -> REJECTED
    c1 = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("86a4f50e")).first()
    if c1:
        exp1 = Experiment(
            candidate_id=c1.id,
            status="COMPLETED",
            universe="TOP1000",
            delay=1,
            decay=5,
            neutralization="Subindustry",
            truncation=0.0100,
        )
        session.add(exp1)
        session.flush()

        m1 = {
            "sharpe": 0.59,
            "fitness": 0.32,
            "turnover": 0.1423,
            "sub_universe_sharpe": -0.07,
        }
        for k, v in m1.items():
            session.add(ExperimentMetric(experiment_id=exp1.id, metric_name=k, metric_value=v, source="BRAIN_PLATFORM"))

        dec1 = Decision(
            candidate_id=c1.id,
            decision="REJECTED",
            reason=(
                "4 PASS / 3 FAIL in TOP1000 Subindustry Decay 5: Sharpe 0.59 < 1.25, "
                "Fitness 0.32 < 1.0, Sub-universe Sharpe -0.07 < 0.31. "
                "Quarterly cashflow per share without industry scaling failed to generate sufficient breadth."
            ),
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec1)
        c1.status = "REJECTED"
        print("Candidate 86a4f50e recorded as REJECTED in PostgreSQL.")

    # 2. Candidate 3: be0300cb -> REJECTED
    c3 = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("be0300cb")).first()
    if c3:
        exp3 = Experiment(
            candidate_id=c3.id,
            status="COMPLETED",
            universe="TOP1000",
            delay=1,
            decay=5,
            neutralization="Subindustry",
            truncation=0.0100,
        )
        session.add(exp3)
        session.flush()

        m3 = {
            "sharpe": 0.42,
            "fitness": 0.19,
            "turnover": 0.0705,
            "sub_universe_sharpe": 0.02,
        }
        for k, v in m3.items():
            session.add(ExperimentMetric(experiment_id=exp3.id, metric_name=k, metric_value=v, source="BRAIN_PLATFORM"))

        dec3 = Decision(
            candidate_id=c3.id,
            decision="REJECTED",
            reason=(
                "4 PASS / 3 FAIL in TOP1000 Subindustry Decay 5: Sharpe 0.42 < 1.25, "
                "Fitness 0.19 < 1.0, Sub-universe Sharpe 0.02 < 0.22. "
                "The multiplicative rank product of fnd6_fopo and fnd2_ebitdm was too restrictive, "
                "diluting signal density and resulting in low information coefficient."
            ),
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec3)
        c3.status = "REJECTED"
        print("Candidate be0300cb recorded as REJECTED in PostgreSQL.")

    session.commit()
    print("Batch 99 Candidates 1 and 3 logged successfully.")

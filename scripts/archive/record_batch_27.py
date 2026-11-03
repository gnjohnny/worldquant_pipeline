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
    # 1. Candidate 1: 74ae216e
    c1 = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("74ae216e")).first()
    if c1:
        exp1 = Experiment(candidate_id=c1.id, status="COMPLETED")
        session.add(exp1)
        session.flush()
        m1 = {"sharpe": 0.13, "fitness": 0.04, "turnover": 0.1072, "sub_universe_sharpe": 0.38}
        for k, v in m1.items():
            session.add(ExperimentMetric(experiment_id=exp1.id, metric_name=k, metric_value=v, source="BRAIN_PLATFORM"))
        dec1 = Decision(
            candidate_id=c1.id,
            decision="NEEDS_REVISION",
            reason="Candidate 1 achieved healthy turnover 10.72% and passing sub-universe Sharpe 0.38, but low overall Sharpe 0.13.",
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec1)
        c1.status = "NEEDS_REVISION"

    # 2. Candidate 2: b1da32c3
    c2 = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("b1da32c3")).first()
    if c2:
        exp2 = Experiment(candidate_id=c2.id, status="COMPLETED")
        session.add(exp2)
        session.flush()
        m2 = {"sharpe": -0.05, "fitness": -0.01, "turnover": 0.1042, "sub_universe_sharpe": -0.13}
        for k, v in m2.items():
            session.add(ExperimentMetric(experiment_id=exp2.id, metric_name=k, metric_value=v, source="BRAIN_PLATFORM"))
        dec2 = Decision(
            candidate_id=c2.id,
            decision="REJECTED",
            reason="Candidate 2 failed with negative Sharpe -0.05.",
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec2)
        c2.status = "REJECTED"

    # 3. Candidate 3: bb688df3
    c3 = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("bb688df3")).first()
    if c3:
        exp3 = Experiment(candidate_id=c3.id, status="COMPLETED")
        session.add(exp3)
        session.flush()
        m3 = {"sharpe": 0.73, "fitness": 0.49, "turnover": 0.1172, "sub_universe_sharpe": 0.61}
        for k, v in m3.items():
            session.add(ExperimentMetric(experiment_id=exp3.id, metric_name=k, metric_value=v, source="BRAIN_PLATFORM"))
        dec3 = Decision(
            candidate_id=c3.id,
            decision="NEEDS_REVISION",
            reason="Candidate 3 showed promising traction with Sharpe 0.73, Fitness 0.49, Turnover 11.72%, and passing Sub-universe Sharpe 0.61. Needs parameter tuning or 170-day window to reach hurdle.",
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec3)
        c3.status = "NEEDS_REVISION"

    session.commit()
    print("Logged Batch 27 experiment metrics and decisions in PostgreSQL successfully!")

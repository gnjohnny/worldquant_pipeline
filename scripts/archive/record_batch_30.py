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
    # 1. Candidate 1: 597215e5 (Options VRP Hybrid)
    c1 = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("597215e5")).first()
    if c1:
        exp1 = Experiment(
            candidate_id=c1.id,
            status="COMPLETED",
            universe="TOP1000",
            delay=1,
            decay=4,
            neutralization="Industry",
            truncation=0.0100,
        )
        session.add(exp1)
        session.flush()
        m1 = {
            "sharpe": 0.90,
            "fitness": 0.37,
            "turnover": 0.2583,
            "sub_universe_sharpe": 0.49,
        }
        for k, v in m1.items():
            session.add(
                ExperimentMetric(
                    experiment_id=exp1.id,
                    metric_name=k,
                    metric_value=v,
                    source="BRAIN_PLATFORM",
                )
            )
        dec1 = Decision(
            candidate_id=c1.id,
            decision="NEEDS_REVISION",
            reason="Achieved positive traction with Sharpe 0.90, Turnover 25.83%, and passing Sub-universe Sharpe 0.49, but failed weight concentration check (25% on 1/25/2022) due to volatility spike.",
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec1)
        c1.status = "NEEDS_REVISION"

    # 2. Candidate 2: 23a70d57 (Analyst Revision Acceleration Derivative)
    c2 = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("23a70d57")).first()
    if c2:
        exp2 = Experiment(
            candidate_id=c2.id,
            status="COMPLETED",
            universe="TOP1000",
            delay=1,
            decay=4,
            neutralization="Industry",
            truncation=0.0100,
        )
        session.add(exp2)
        session.flush()
        m2 = {
            "sharpe": -0.19,
            "fitness": -0.07,
            "turnover": 0.1404,
            "sub_universe_sharpe": -0.03,
        }
        for k, v in m2.items():
            session.add(
                ExperimentMetric(
                    experiment_id=exp2.id,
                    metric_name=k,
                    metric_value=v,
                    source="BRAIN_PLATFORM",
                )
            )
        dec2 = Decision(
            candidate_id=c2.id,
            decision="REJECTED",
            reason="Failed with negative Sharpe -0.19 and Fitness -0.07. Revision acceleration derivative is too noisy without smoothing.",
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec2)
        c2.status = "REJECTED"

    # 3. Candidate 3: 689a14ea (Asset Fair Value in TOPSP500)
    c3 = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("689a14ea")).first()
    if c3:
        exp3 = Experiment(
            candidate_id=c3.id,
            status="COMPLETED",
            universe="TOPSP500",
            delay=1,
            decay=4,
            neutralization="Market",
            truncation=0.0100,
        )
        session.add(exp3)
        session.flush()
        m3 = {
            "sharpe": 0.51,
            "fitness": 0.41,
            "turnover": 0.0867,
            "sub_universe_sharpe": 0.34,
        }
        for k, v in m3.items():
            session.add(
                ExperimentMetric(
                    experiment_id=exp3.id,
                    metric_name=k,
                    metric_value=v,
                    source="BRAIN_PLATFORM",
                )
            )
        dec3 = Decision(
            candidate_id=c3.id,
            decision="NEEDS_REVISION",
            reason="Healthy turnover of 8.67% and passing Sub-universe Sharpe 0.34, but Sharpe 0.51 and Fitness 0.41 are below cutoff.",
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec3)
        c3.status = "NEEDS_REVISION"

    session.commit()
    print("Recorded Batch 30 metrics and decisions in PostgreSQL successfully!")

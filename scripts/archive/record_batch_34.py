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
    # 1. Candidate 1: 03616142 (Low-Beta Anomaly)
    c1 = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("03616142")).first()
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
            "sharpe": 0.12,
            "fitness": 0.03,
            "turnover": 0.2422,
            "sub_universe_sharpe": -0.07,
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
            decision="REJECTED",
            reason="3 PASS / 4 FAIL. Low Sharpe 0.12, Fitness 0.03, weight concentration failed, and sub-universe Sharpe -0.07. Low-beta anomaly failed weight distribution.",
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec1)
        c1.status = "REJECTED"
        print(f"Recorded Candidate 1 ({c1.id[:8]}) as REJECTED.")

    # 2. Candidate 2: 1b71f51e (Customer Return Spillover)
    c2 = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("1b71f51e")).first()
    if c2:
        exp2 = Experiment(
            candidate_id=c2.id,
            status="COMPLETED",
            universe="TOP1000",
            delay=1,
            decay=4,
            neutralization="Subindustry",
            truncation=0.0100,
        )
        session.add(exp2)
        session.flush()
        m2 = {
            "sharpe": -1.17,
            "fitness": -0.50,
            "turnover": 0.4534,
            "sub_universe_sharpe": -0.82,
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
            reason="4 PASS / 3 FAIL. Negative Sharpe -1.17, Fitness -0.50, sub-universe Sharpe -0.82. Customer return spillover signal inverse/ineffective in this horizon.",
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec2)
        c2.status = "REJECTED"
        print(f"Recorded Candidate 2 ({c2.id[:8]}) as REJECTED.")

    # 3. Candidate 3: 2b3d1fd0 (Cashflow & Revision Synergy)
    c3 = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("2b3d1fd0")).first()
    if c3:
        exp3 = Experiment(
            candidate_id=c3.id,
            status="COMPLETED",
            universe="TOP1000",
            delay=1,
            decay=4,
            neutralization="Subindustry",
            truncation=0.0100,
        )
        session.add(exp3)
        session.flush()
        m3 = {
            "sharpe": -0.20,
            "fitness": -0.08,
            "turnover": 0.1402,
            "sub_universe_sharpe": -0.06,
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
            decision="REJECTED",
            reason="5 PASS / 2 FAIL. Negative Sharpe -0.20, Fitness -0.08. Linear combination of rank derivatives failed to produce positive alpha.",
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec3)
        c3.status = "REJECTED"
        print(f"Recorded Candidate 3 ({c3.id[:8]}) as REJECTED.")

    session.commit()
    print("Batch 34 metrics and decisions successfully committed to PostgreSQL research memory!")

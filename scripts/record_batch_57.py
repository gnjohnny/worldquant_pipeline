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
    # 1. Candidate 1: f065297f (model16 cashflow + analyst)
    c1 = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("f065297f")).first()
    if c1:
        exp1 = Experiment(
            candidate_id=c1.id,
            status="COMPLETED",
            universe="TOP3000",
            delay=1,
            decay=5,
            neutralization="Subindustry",
            truncation=0.0100,
        )
        session.add(exp1)
        session.flush()
        m1 = {"sharpe": 0.08, "fitness": 0.01, "turnover": 0.1921, "sub_universe_sharpe": 0.03}
        for k, v in m1.items():
            session.add(ExperimentMetric(experiment_id=exp1.id, metric_name=k, metric_value=v, source="BRAIN_PLATFORM"))
        dec1 = Decision(
            candidate_id=c1.id,
            decision="REJECTED",
            reason="5 PASS / 2 FAIL. Sharpe 0.08 < 1.25, Fitness 0.01 < 1.0.",
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec1)
        c1.status = "REJECTED"
        print("Recorded Candidate 1 (f065297f) as REJECTED.")

    # 2. Candidate 2: 398796b3 (pv13 customer spillover)
    c2 = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("398796b3")).first()
    if c2:
        exp2 = Experiment(
            candidate_id=c2.id,
            status="COMPLETED",
            universe="TOP3000",
            delay=1,
            decay=5,
            neutralization="Subindustry",
            truncation=0.0100,
        )
        session.add(exp2)
        session.flush()
        m2 = {"sharpe": -0.75, "fitness": -0.29, "turnover": 0.3145, "sub_universe_sharpe": -0.19}
        for k, v in m2.items():
            session.add(ExperimentMetric(experiment_id=exp2.id, metric_name=k, metric_value=v, source="BRAIN_PLATFORM"))
        dec2 = Decision(
            candidate_id=c2.id,
            decision="REJECTED",
            reason="5 PASS / 2 FAIL. Sharpe -0.75 < 1.25, Fitness -0.29 < 1.0.",
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec2)
        c2.status = "REJECTED"
        print("Recorded Candidate 2 (398796b3) as REJECTED.")

    # 3. Candidate 3: 5a17e73b (option9 put breakeven)
    c3 = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("5a17e73b")).first()
    if c3:
        exp3 = Experiment(
            candidate_id=c3.id,
            status="COMPLETED",
            universe="TOP3000",
            delay=1,
            decay=5,
            neutralization="Subindustry",
            truncation=0.0100,
        )
        session.add(exp3)
        session.flush()
        m3 = {"sharpe": -0.11, "fitness": -0.02, "turnover": 0.2243, "sub_universe_sharpe": -0.14}
        for k, v in m3.items():
            session.add(ExperimentMetric(experiment_id=exp3.id, metric_name=k, metric_value=v, source="BRAIN_PLATFORM"))
        dec3 = Decision(
            candidate_id=c3.id,
            decision="REJECTED",
            reason="4 PASS / 3 FAIL. Sharpe -0.11 < 1.25, Fitness -0.02 < 1.0, Sub-universe -0.14.",
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec3)
        c3.status = "REJECTED"
        print("Recorded Candidate 3 (5a17e73b) as REJECTED.")

    # 4. Candidate 4: 7067121d (model16 cashflow + rel valuation)
    c4 = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("7067121d")).first()
    if c4:
        exp4 = Experiment(
            candidate_id=c4.id,
            status="COMPLETED",
            universe="TOP3000",
            delay=1,
            decay=5,
            neutralization="Subindustry",
            truncation=0.0100,
        )
        session.add(exp4)
        session.flush()
        m4 = {"sharpe": 0.07, "fitness": 0.01, "turnover": 0.1922, "sub_universe_sharpe": 0.04}
        for k, v in m4.items():
            session.add(ExperimentMetric(experiment_id=exp4.id, metric_name=k, metric_value=v, source="BRAIN_PLATFORM"))
        dec4 = Decision(
            candidate_id=c4.id,
            decision="REJECTED",
            reason="5 PASS / 2 FAIL. Sharpe 0.07 < 1.25, Fitness 0.01 < 1.0.",
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec4)
        c4.status = "REJECTED"
        print("Recorded Candidate 4 (7067121d) as REJECTED.")

    session.commit()
    print("Batch 57 metrics successfully committed to PostgreSQL.")

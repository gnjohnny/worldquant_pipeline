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
    # 1. Candidate 1: 71d65d36 (Solvency: Cash / Debt)
    c1 = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("71d65d36")).first()
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
        m1 = {"sharpe": 0.55, "fitness": 0.28, "turnover": 0.1329, "sub_universe_sharpe": 0.41}
        for k, v in m1.items():
            session.add(ExperimentMetric(experiment_id=exp1.id, metric_name=k, metric_value=v, source="BRAIN_PLATFORM"))
        dec1 = Decision(
            candidate_id=c1.id,
            decision="REJECTED",
            reason="5 PASS / 2 FAIL. Sharpe 0.55 < 1.25, Fitness 0.28 < 1.0.",
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec1)
        c1.status = "REJECTED"
        print("Recorded Candidate 1 (71d65d36) as REJECTED.")

    # 2. Candidate 2: af34b67f (Earnings Certainty)
    c2 = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("af34b67f")).first()
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
        m2 = {"sharpe": 0.07, "fitness": 0.01, "turnover": 0.1923, "sub_universe_sharpe": 0.04}
        for k, v in m2.items():
            session.add(ExperimentMetric(experiment_id=exp2.id, metric_name=k, metric_value=v, source="BRAIN_PLATFORM"))
        dec2 = Decision(
            candidate_id=c2.id,
            decision="REJECTED",
            reason="5 PASS / 2 FAIL. Sharpe 0.07 < 1.25, Fitness 0.01 < 1.0.",
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec2)
        c2.status = "REJECTED"
        print("Recorded Candidate 2 (af34b67f) as REJECTED.")

    # 3. Candidate 3: a5dac7f8 (Fair Value Assets)
    c3 = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("a5dac7f8")).first()
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
        m3 = {"sharpe": 0.98, "fitness": 0.59, "turnover": 0.1073, "sub_universe_sharpe": -0.02}
        for k, v in m3.items():
            session.add(ExperimentMetric(experiment_id=exp3.id, metric_name=k, metric_value=v, source="BRAIN_PLATFORM"))
        dec3 = Decision(
            candidate_id=c3.id,
            decision="REJECTED",
            reason="4 PASS / 3 FAIL. Sharpe 0.98 < 1.25, Fitness 0.59 < 1.0, Sub-universe -0.02 < 0.42.",
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec3)
        c3.status = "REJECTED"
        print("Recorded Candidate 3 (a5dac7f8) as REJECTED.")

    # 4. Candidate 4: 78c7db51 (Book Value Yield)
    c4 = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("78c7db51")).first()
    if c4:
        exp4 = Experiment(
            candidate_id=c4.id,
            status="COMPLETED",
            universe="TOP3000",
            delay=1,
            decay=4,
            neutralization="Subindustry",
            truncation=0.0100,
        )
        session.add(exp4)
        session.flush()
        m4 = {"sharpe": 1.04, "fitness": 0.65, "turnover": 0.2289, "sub_universe_sharpe": 0.91}
        for k, v in m4.items():
            session.add(ExperimentMetric(experiment_id=exp4.id, metric_name=k, metric_value=v, source="BRAIN_PLATFORM"))
        dec4 = Decision(
            candidate_id=c4.id,
            decision="REJECTED",
            reason="5 PASS / 2 FAIL. Sharpe 1.04 < 1.25, Fitness 0.65 < 1.0.",
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec4)
        c4.status = "REJECTED"
        print("Recorded Candidate 4 (78c7db51) as REJECTED.")

    session.commit()
    print("Batch 66 metrics successfully committed to PostgreSQL.")

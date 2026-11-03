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
    # 1. Candidate 1: 90bf3b53 (1-Year Put in Market)
    c1 = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("90bf3b53")).first()
    if c1:
        exp1 = Experiment(
            candidate_id=c1.id,
            status="COMPLETED",
            universe="TOP1000",
            delay=1,
            decay=6,
            neutralization="Market",
            truncation=0.0100,
        )
        session.add(exp1)
        session.flush()
        m1 = {"sharpe": 1.21, "fitness": 1.27, "turnover": 0.1622, "sub_universe_sharpe": 0.94}
        for k, v in m1.items():
            session.add(ExperimentMetric(experiment_id=exp1.id, metric_name=k, metric_value=v, source="BRAIN_PLATFORM"))
        dec1 = Decision(
            candidate_id=c1.id,
            decision="REJECTED",
            reason="6 PASS / 1 FAIL. Sharpe 1.21 slightly below 1.25 cutoff.",
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec1)
        c1.status = "REJECTED"
        print("Recorded Candidate 1 (90bf3b53) as REJECTED.")

    # 2. Candidate 2: 3146f9a2 (2-Year Put in Market)
    c2 = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("3146f9a2")).first()
    if c2:
        exp2 = Experiment(
            candidate_id=c2.id,
            status="COMPLETED",
            universe="TOP1000",
            delay=1,
            decay=6,
            neutralization="Market",
            truncation=0.0100,
        )
        session.add(exp2)
        session.flush()
        m2 = {"sharpe": 0.95, "fitness": 0.89, "turnover": 0.1608, "sub_universe_sharpe": 0.78}
        for k, v in m2.items():
            session.add(ExperimentMetric(experiment_id=exp2.id, metric_name=k, metric_value=v, source="BRAIN_PLATFORM"))
        dec2 = Decision(
            candidate_id=c2.id,
            decision="REJECTED",
            reason="5 PASS / 2 FAIL. Sharpe 0.95 < 1.25, Fitness 0.89 < 1.0.",
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec2)
        c2.status = "REJECTED"
        print("Recorded Candidate 2 (3146f9a2) as REJECTED.")

    # 3. Candidate 3: 436321db (3-Year LEAP Call in Market)
    c3 = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("436321db")).first()
    if c3:
        exp3 = Experiment(
            candidate_id=c3.id,
            status="COMPLETED",
            universe="TOP1000",
            delay=1,
            decay=6,
            neutralization="Market",
            truncation=0.0100,
        )
        session.add(exp3)
        session.flush()
        m3 = {"sharpe": 1.49, "fitness": 1.53, "turnover": 0.1658, "sub_universe_sharpe": 1.43, "self_correlation": 0.8404}
        for k, v in m3.items():
            session.add(ExperimentMetric(experiment_id=exp3.id, metric_name=k, metric_value=v, source="BRAIN_PLATFORM"))
        dec3 = Decision(
            candidate_id=c3.id,
            decision="REJECTED",
            reason="7 PASS / 1 FAIL. Sharpe 1.49, Fitness 1.53, but Self-correlation 0.8404 > 0.70 against Alpha 7c3e864f.",
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec3)
        c3.status = "REJECTED"
        print("Recorded Candidate 3 (436321db) as REJECTED.")

    # 4. Candidate 4: 89984ef7 (Super Alpha in Market)
    c4 = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("89984ef7")).first()
    if c4:
        exp4 = Experiment(
            candidate_id=c4.id,
            status="COMPLETED",
            universe="TOP3000",
            delay=1,
            decay=6,
            neutralization="Market",
            truncation=0.0100,
        )
        session.add(exp4)
        session.flush()
        m4 = {"sharpe": 1.93, "fitness": 1.66, "turnover": 0.1081, "sub_universe_sharpe": 1.82, "self_correlation": 0.9584}
        for k, v in m4.items():
            session.add(ExperimentMetric(experiment_id=exp4.id, metric_name=k, metric_value=v, source="BRAIN_PLATFORM"))
        dec4 = Decision(
            candidate_id=c4.id,
            decision="REJECTED",
            reason="7 PASS / 1 FAIL. Sharpe 1.93, Fitness 1.66, Turnover 10.81%, but Self-correlation 0.9584 > 0.70 against Alpha 7c3e864f.",
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec4)
        c4.status = "REJECTED"
        print("Recorded Candidate 4 (89984ef7) as REJECTED.")

    session.commit()
    print("Batch 56 metrics successfully committed to PostgreSQL.")

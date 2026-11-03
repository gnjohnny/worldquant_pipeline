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
    # 1. Candidate 1: 682c399f with decay=8 in TOP1000
    c1 = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("682c399f")).first()
    if c1:
        exp1 = Experiment(
            candidate_id=c1.id,
            status="COMPLETED",
            universe="TOP1000",
            delay=1,
            decay=8,
            neutralization="Subindustry",
            truncation=0.0100,
        )
        session.add(exp1)
        session.flush()
        m1 = {"sharpe": 1.76, "fitness": 1.50, "turnover": 0.1517, "sub_universe_sharpe": 1.26, "self_correlation": 0.7191}
        for k, v in m1.items():
            session.add(ExperimentMetric(experiment_id=exp1.id, metric_name=k, metric_value=v, source="BRAIN_PLATFORM"))
        dec1 = Decision(
            candidate_id=c1.id,
            decision="REJECTED",
            reason="7 PASS / 1 FAIL. Sharpe 1.76, Fitness 1.50, but Self-correlation 0.7191 slightly exceeds 0.70 cutoff.",
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec1)
        print("Recorded Candidate 1 (682c399f, decay=8) as REJECTED.")

    # 2. Candidate 2: dd2d1ea4 (10d reversal in TOP1000)
    c2 = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("dd2d1ea4")).first()
    if c2:
        exp2 = Experiment(
            candidate_id=c2.id,
            status="COMPLETED",
            universe="TOP1000",
            delay=1,
            decay=6,
            neutralization="Subindustry",
            truncation=0.0100,
        )
        session.add(exp2)
        session.flush()
        m2 = {"sharpe": 1.58, "fitness": 1.30, "turnover": 0.1450, "sub_universe_sharpe": 1.11, "self_correlation": 0.7570}
        for k, v in m2.items():
            session.add(ExperimentMetric(experiment_id=exp2.id, metric_name=k, metric_value=v, source="BRAIN_PLATFORM"))
        dec2 = Decision(
            candidate_id=c2.id,
            decision="REJECTED",
            reason="7 PASS / 1 FAIL. Sharpe 1.58, Fitness 1.30, Self-correlation 0.7570 > 0.70.",
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec2)
        c2.status = "REJECTED"
        print("Recorded Candidate 2 (dd2d1ea4) as REJECTED.")

    # 3. Candidate 4: 73a549ad (252d FX in TOP1000)
    c4 = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("73a549ad")).first()
    if c4:
        exp4 = Experiment(
            candidate_id=c4.id,
            status="COMPLETED",
            universe="TOP1000",
            delay=1,
            decay=6,
            neutralization="Subindustry",
            truncation=0.0100,
        )
        session.add(exp4)
        session.flush()
        m4 = {"sharpe": 1.35, "fitness": 0.89, "turnover": 0.0743, "sub_universe_sharpe": 1.20}
        for k, v in m4.items():
            session.add(ExperimentMetric(experiment_id=exp4.id, metric_name=k, metric_value=v, source="BRAIN_PLATFORM"))
        dec4 = Decision(
            candidate_id=c4.id,
            decision="REJECTED",
            reason="6 PASS / 1 FAIL. Sharpe 1.35, Turnover 7.43%, but Fitness 0.89 < 1.0.",
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec4)
        c4.status = "REJECTED"
        print("Recorded Candidate 4 (73a549ad) as REJECTED.")

    session.commit()
    print("Batch 54 remaining metrics successfully committed to PostgreSQL.")

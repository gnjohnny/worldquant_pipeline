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
    # 1. Candidate 1: 30dc52c2
    c1 = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("30dc52c2")).first()
    if c1:
        exp1 = Experiment(
            candidate_id=c1.id,
            status="COMPLETED",
            universe="TOP3000",
            delay=1,
            decay=6,
            neutralization="Sector",
            truncation=0.0100,
        )
        session.add(exp1)
        session.flush()
        m1 = {"sharpe": 1.27, "fitness": 0.86, "turnover": 0.2720, "sub_universe_sharpe": 0.92}
        for k, v in m1.items():
            session.add(ExperimentMetric(experiment_id=exp1.id, metric_name=k, metric_value=v, source="BRAIN_PLATFORM"))
        dec1 = Decision(
            candidate_id=c1.id,
            decision="REJECTED",
            reason="6 PASS / 1 FAIL. Sharpe 1.27, Fitness 0.86 < 1.0.",
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec1)
        c1.status = "REJECTED"
        print("Recorded Candidate 1 (30dc52c2) as REJECTED.")

    # 2. Candidate 2: 92b40f7b
    c2 = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("92b40f7b")).first()
    if c2:
        exp2 = Experiment(
            candidate_id=c2.id,
            status="COMPLETED",
            universe="TOP3000",
            delay=1,
            decay=5,
            neutralization="Industry",
            truncation=0.0100,
        )
        session.add(exp2)
        session.flush()
        m2 = {"sharpe": 1.84, "fitness": 1.19, "turnover": 0.3372, "sub_universe_sharpe": 1.17, "self_correlation": 0.7135}
        for k, v in m2.items():
            session.add(ExperimentMetric(experiment_id=exp2.id, metric_name=k, metric_value=v, source="BRAIN_PLATFORM"))
        dec2 = Decision(
            candidate_id=c2.id,
            decision="REJECTED",
            reason="7 PASS / 1 FAIL. Sharpe 1.84, Fitness 1.19, Self-correlation 0.7135 narrowly missed 0.70 cutoff.",
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec2)
        c2.status = "REJECTED"
        print("Recorded Candidate 2 (92b40f7b) as REJECTED.")

    # 3. Candidate 3: 1086ccb5 in TOP1000
    c3 = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("1086ccb5")).first()
    if c3:
        exp3 = Experiment(
            candidate_id=c3.id,
            status="COMPLETED",
            universe="TOP1000",
            delay=1,
            decay=5,
            neutralization="Sector",
            truncation=0.0100,
        )
        session.add(exp3)
        session.flush()
        m3 = {"sharpe": 1.29, "fitness": 0.90, "turnover": 0.2646, "sub_universe_sharpe": 1.03}
        for k, v in m3.items():
            session.add(ExperimentMetric(experiment_id=exp3.id, metric_name=k, metric_value=v, source="BRAIN_PLATFORM"))
        dec3 = Decision(
            candidate_id=c3.id,
            decision="REJECTED",
            reason="6 PASS / 1 FAIL. Sharpe 1.29, Fitness 0.90 < 1.0.",
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec3)
        print("Recorded Candidate 3 (1086ccb5 in TOP1000) as REJECTED.")

    # 4. Candidate 4: e2b3f06f
    c4 = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("e2b3f06f")).first()
    if c4:
        exp4 = Experiment(
            candidate_id=c4.id,
            status="COMPLETED",
            universe="TOP3000",
            delay=1,
            decay=4,
            neutralization="Industry",
            truncation=0.0100,
        )
        session.add(exp4)
        session.flush()
        m4 = {"sharpe": 1.99, "fitness": 1.52, "turnover": 0.1910, "sub_universe_sharpe": 1.81, "self_correlation": 0.8575}
        for k, v in m4.items():
            session.add(ExperimentMetric(experiment_id=exp4.id, metric_name=k, metric_value=v, source="BRAIN_PLATFORM"))
        dec4 = Decision(
            candidate_id=c4.id,
            decision="NEEDS_REVISION",
            reason="7 PASS / 1 FAIL. Sharpe 1.99, Fitness 1.52 (GOOD), Sub-universe 1.81! Self-correlation 0.8575 due to options saturation.",
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec4)
        c4.status = "NEEDS_REVISION"
        print("Recorded Candidate 4 (e2b3f06f) as NEEDS_REVISION (Sharpe 1.99, Fitness 1.52).")

    session.commit()
    print("Batch 65 metrics successfully committed to PostgreSQL.")

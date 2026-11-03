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
    # 1. Candidate 1: 94ee1f17 in Sector (3-Yr Call in Sector)
    c1 = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("94ee1f17")).first()
    if c1:
        exp1 = Experiment(
            candidate_id=c1.id,
            status="COMPLETED",
            universe="TOP1000",
            delay=1,
            decay=5,
            neutralization="Sector",
            truncation=0.0100,
        )
        session.add(exp1)
        session.flush()
        m1 = {"sharpe": 1.67, "fitness": 1.57, "turnover": 0.1881, "sub_universe_sharpe": 1.49, "self_correlation": 0.8327}
        for k, v in m1.items():
            session.add(ExperimentMetric(experiment_id=exp1.id, metric_name=k, metric_value=v, source="BRAIN_PLATFORM"))
        dec1 = Decision(
            candidate_id=c1.id,
            decision="REJECTED",
            reason="7 PASS / 1 FAIL. Sharpe 1.67, Fitness 1.57 (GOOD), but Self-correlation 0.8327 > 0.70 in Sector scope.",
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec1)
        c1.status = "REJECTED"
        print("Recorded Candidate 1 (94ee1f17) as REJECTED.")

    # 2. Candidate 2: 62110724 in Sector (1-Yr Call with 10% Reversal)
    c2 = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("62110724")).first()
    if c2:
        exp2 = Experiment(
            candidate_id=c2.id,
            status="COMPLETED",
            universe="TOP1000",
            delay=1,
            decay=5,
            neutralization="Sector",
            truncation=0.0100,
        )
        session.add(exp2)
        session.flush()
        m2 = {"sharpe": 1.75, "fitness": 1.88, "turnover": 0.1636, "sub_universe_sharpe": 1.44, "self_correlation": 0.8758}
        for k, v in m2.items():
            session.add(ExperimentMetric(experiment_id=exp2.id, metric_name=k, metric_value=v, source="BRAIN_PLATFORM"))
        dec2 = Decision(
            candidate_id=c2.id,
            decision="NEEDS_REVISION",
            reason="7 PASS / 1 FAIL. EXCELLENT Fitness 1.88 and Sharpe 1.75! Self-correlation 0.8758 requires 10% Sharpe elevation (Sharpe >= 1.95) to pass under platform improvement rule.",
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec2)
        c2.status = "NEEDS_REVISION"
        print("Recorded Candidate 2 (62110724) as NEEDS_REVISION (Fitness 1.88 EXCELLENT).")

    # 3. Candidate 3: 3bdc1522 (90-30 Vol Slope)
    c3 = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("3bdc1522")).first()
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
        m3 = {"sharpe": 1.05, "fitness": 0.44, "turnover": 0.3274, "sub_universe_sharpe": 0.74}
        for k, v in m3.items():
            session.add(ExperimentMetric(experiment_id=exp3.id, metric_name=k, metric_value=v, source="BRAIN_PLATFORM"))
        dec3 = Decision(
            candidate_id=c3.id,
            decision="REJECTED",
            reason="5 PASS / 2 FAIL. Sharpe 1.05 < 1.25, Fitness 0.44 < 1.0.",
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec3)
        c3.status = "REJECTED"
        print("Recorded Candidate 3 (3bdc1522) as REJECTED.")

    # 4. Candidate 4: 3138d755 (Annual Sales Yield)
    c4 = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("3138d755")).first()
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
        m4 = {"sharpe": 0.85, "fitness": 0.54, "turnover": 0.2200, "sub_universe_sharpe": 0.67}
        for k, v in m4.items():
            session.add(ExperimentMetric(experiment_id=exp4.id, metric_name=k, metric_value=v, source="BRAIN_PLATFORM"))
        dec4 = Decision(
            candidate_id=c4.id,
            decision="REJECTED",
            reason="5 PASS / 2 FAIL. Sharpe 0.85 < 1.25, Fitness 0.54 < 1.0.",
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec4)
        c4.status = "REJECTED"
        print("Recorded Candidate 4 (3138d755) as REJECTED.")

    session.commit()
    print("Batch 62 metrics successfully committed to PostgreSQL.")

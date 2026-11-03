"""Record Alpha 27 approval and Batch 81 decisions in PostgreSQL."""
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
    # 1. Candidate 2: c469a7a4 -> Alpha 27 APPROVED!
    c2 = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("c469a7a4")).first()
    if c2:
        exp2 = Experiment(
            candidate_id=c2.id,
            status="COMPLETED",
            universe="TOP1000",
            delay=1,
            decay=5,
            neutralization="Subindustry",
            truncation=0.0100,
        )
        session.add(exp2)
        session.flush()

        m2 = {
            "sharpe": 2.24,
            "fitness": 1.81,
            "turnover": 0.1244,
            "sub_universe_sharpe": 1.64,
            "self_correlation": 0.5961,
        }
        for k, v in m2.items():
            session.add(ExperimentMetric(experiment_id=exp2.id, metric_name=k, metric_value=v, source="BRAIN_PLATFORM"))

        dec2 = Decision(
            candidate_id=c2.id,
            decision="APPROVED",
            reason="8/8 PASS! GOLD LEVEL CONSULTANT QUALIFIED: Sharpe 2.24 > 1.25 (SPECTACULAR Sharpe!), Fitness 1.81 >= 1.50 (GOOD / EXCELLENT), Turnover 12.44% in [1%, 70%], Sub-universe Sharpe 1.64 > 1.19, Self-correlation 0.5961 < 0.70 (complete decorrelation). Large-Cap Operating Leverage & Margin Convexity Super Alpha in TOP1000 Subindustry Neutral.",
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec2)
        c2.status = "APPROVED"
        print("Candidate c469a7a4 successfully APPROVED and recorded as Alpha 27 in PostgreSQL.")

    # 2. Candidate 1: ee0f59f2 -> REJECTED
    c1 = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("ee0f59f2")).first()
    if c1:
        exp1 = Experiment(
            candidate_id=c1.id,
            status="COMPLETED",
            universe="TOP2000",
            delay=1,
            decay=6,
            neutralization="Subindustry",
            truncation=0.0100,
        )
        session.add(exp1)
        session.flush()

        m1 = {
            "sharpe": 1.09,
            "fitness": 0.59,
            "turnover": 0.1153,
            "sub_universe_sharpe": 0.97,
        }
        for k, v in m1.items():
            session.add(ExperimentMetric(experiment_id=exp1.id, metric_name=k, metric_value=v, source="BRAIN_PLATFORM"))

        dec1 = Decision(
            candidate_id=c1.id,
            decision="REJECTED",
            reason="5 PASS / 2 FAIL: Sharpe 1.09 and Fitness 0.59 below cutoffs.",
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec1)
        c1.status = "REJECTED"
        print("Candidate ee0f59f2 recorded as REJECTED in PostgreSQL.")

    # 3. Candidate 3: 499534d8 -> REJECTED
    c3 = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("499534d8")).first()
    if c3:
        exp3 = Experiment(
            candidate_id=c3.id,
            status="COMPLETED",
            universe="TOP1000",
            delay=1,
            decay=6,
            neutralization="Industry",
            truncation=0.0100,
        )
        session.add(exp3)
        session.flush()

        m3 = {
            "sharpe": 1.12,
            "fitness": 0.81,
            "turnover": 0.1724,
            "sub_universe_sharpe": 0.84,
        }
        for k, v in m3.items():
            session.add(ExperimentMetric(experiment_id=exp3.id, metric_name=k, metric_value=v, source="BRAIN_PLATFORM"))

        dec3 = Decision(
            candidate_id=c3.id,
            decision="REJECTED",
            reason="5 PASS / 2 FAIL: Sharpe 1.12 and Fitness 0.81 below cutoffs.",
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec3)
        c3.status = "REJECTED"
        print("Candidate 499534d8 recorded as REJECTED in PostgreSQL.")

    session.commit()
    print("All Batch 81 records successfully committed.")

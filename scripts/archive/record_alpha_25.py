"""Record Alpha 25 approval and Batch 76 decisions in PostgreSQL."""
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
    # 1. Candidate 1: 1257dcae -> Alpha 25 APPROVED!
    c1 = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("1257dcae")).first()
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

        m1 = {
            "sharpe": 1.49,
            "fitness": 1.55,
            "turnover": 0.1388,
            "sub_universe_sharpe": 1.49,
            "self_correlation": 0.6066,
        }
        for k, v in m1.items():
            session.add(ExperimentMetric(experiment_id=exp1.id, metric_name=k, metric_value=v, source="BRAIN_PLATFORM"))

        dec1 = Decision(
            candidate_id=c1.id,
            decision="APPROVED",
            reason="8/8 PASS! GOLD LEVEL CONSULTANT QUALIFIED: Sharpe 1.49 > 1.25, Fitness 1.55 >= 1.50 (GOOD), Turnover 13.88% in [1%, 70%], Sub-universe Sharpe 1.49 > 0.79, Self-correlation 0.6066 < 0.70 (complete decorrelation). Large-Cap Analyst Consensus Yield & Revisions Super Alpha in TOP1000 Market Neutral.",
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec1)
        c1.status = "APPROVED"
        print("Candidate 1257dcae successfully APPROVED and recorded as Alpha 25 in PostgreSQL.")

    # 2. Candidate 2: d3dade76 -> REJECTED (self-corr collision with c1 in TOP1000 Market)
    c2 = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("d3dade76")).first()
    if c2:
        exp2 = Experiment(
            candidate_id=c2.id,
            status="COMPLETED",
            universe="TOP1000",
            delay=1,
            decay=7,
            neutralization="Market",
            truncation=0.0100,
        )
        session.add(exp2)
        session.flush()

        m2 = {
            "sharpe": 1.45,
            "fitness": 1.57,
            "turnover": 0.1132,
            "sub_universe_sharpe": 1.40,
            "self_correlation": 0.9398,
        }
        for k, v in m2.items():
            session.add(ExperimentMetric(experiment_id=exp2.id, metric_name=k, metric_value=v, source="BRAIN_PLATFORM"))

        dec2 = Decision(
            candidate_id=c2.id,
            decision="REJECTED",
            reason="7 PASS / 1 FAIL: Sharpe 1.45, Fitness 1.57, Turnover 11.32%, Sub-universe 1.40. Self-correlation 0.9398 failed against Candidate 1 due to identical universe (TOP1000 Market).",
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec2)
        c2.status = "REJECTED"
        print("Candidate d3dade76 recorded as REJECTED in PostgreSQL.")

    # 3. Candidate 3: 419d0e59 -> NEEDS_REVISION (self-corr 0.7706 against Alpha 22 in TOP1000)
    c3 = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("419d0e59")).first()
    if c3:
        exp3 = Experiment(
            candidate_id=c3.id,
            status="COMPLETED",
            universe="TOP1000",
            delay=1,
            decay=6,
            neutralization="Sector",
            truncation=0.0100,
        )
        session.add(exp3)
        session.flush()

        m3 = {
            "sharpe": 1.47,
            "fitness": 1.40,
            "turnover": 0.1523,
            "sub_universe_sharpe": 1.31,
            "self_correlation": 0.7706,
        }
        for k, v in m3.items():
            session.add(ExperimentMetric(experiment_id=exp3.id, metric_name=k, metric_value=v, source="BRAIN_PLATFORM"))

        dec3 = Decision(
            candidate_id=c3.id,
            decision="NEEDS_REVISION",
            reason="7 PASS / 1 FAIL: Sharpe 1.47, Fitness 1.40, Turnover 15.23%, Sub-universe 1.31. Self-correlation 0.7706 in TOP1000 failed against Alpha 22. Target retesting in TOPSP500 or TOP2000.",
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec3)
        c3.status = "NEEDS_REVISION"
        print("Candidate 419d0e59 recorded as NEEDS_REVISION in PostgreSQL.")

    session.commit()
    print("All Batch 76 records successfully committed.")

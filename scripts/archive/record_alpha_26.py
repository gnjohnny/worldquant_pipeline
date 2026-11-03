"""Record Alpha 26 approval and Batch 79 decisions in PostgreSQL."""
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
    # 1. Candidate 1: bd98dc61 -> Alpha 26 APPROVED!
    c1 = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("bd98dc61")).first()
    if c1:
        exp1 = Experiment(
            candidate_id=c1.id,
            status="COMPLETED",
            universe="TOPSP500",
            delay=1,
            decay=4,
            neutralization="Sector",
            truncation=0.0100,
        )
        session.add(exp1)
        session.flush()

        m1 = {
            "sharpe": 1.73,
            "fitness": 1.56,
            "turnover": 0.1265,
            "sub_universe_sharpe": 1.57,
            "self_correlation": 0.5689,
        }
        for k, v in m1.items():
            session.add(ExperimentMetric(experiment_id=exp1.id, metric_name=k, metric_value=v, source="BRAIN_PLATFORM"))

        dec1 = Decision(
            candidate_id=c1.id,
            decision="APPROVED",
            reason="8/8 PASS! GOLD LEVEL CONSULTANT QUALIFIED: Sharpe 1.73 > 1.25, Fitness 1.56 >= 1.50 (GOOD), Turnover 12.65% in [1%, 70%], Sub-universe Sharpe 1.57 > 0.88, Self-correlation 0.5689 < 0.70 (complete decorrelation breakthrough). Mega-Cap SUE Earnings Surprise Drift & Timing Super Alpha in TOPSP500 Sector Neutral.",
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec1)
        c1.status = "APPROVED"
        print("Candidate bd98dc61 successfully APPROVED and recorded as Alpha 26 in PostgreSQL.")

    # 2. Candidate 3: e3429838 -> REJECTED
    c3 = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("e3429838")).first()
    if c3:
        exp3 = Experiment(
            candidate_id=c3.id,
            status="COMPLETED",
            universe="TOPSP500",
            delay=1,
            decay=5,
            neutralization="Sector",
            truncation=0.0100,
        )
        session.add(exp3)
        session.flush()

        m3 = {
            "sharpe": 0.08,
            "fitness": 0.01,
            "turnover": 0.2632,
            "sub_universe_sharpe": 0.19,
        }
        for k, v in m3.items():
            session.add(ExperimentMetric(experiment_id=exp3.id, metric_name=k, metric_value=v, source="BRAIN_PLATFORM"))

        dec3 = Decision(
            candidate_id=c3.id,
            decision="REJECTED",
            reason="5 PASS / 2 FAIL: Sharpe 0.08 and Fitness 0.01 below cutoffs.",
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec3)
        c3.status = "REJECTED"
        print("Candidate e3429838 recorded as REJECTED in PostgreSQL.")

    session.commit()
    print("All Batch 79 records successfully committed.")

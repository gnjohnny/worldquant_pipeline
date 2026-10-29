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
    # 1. Candidate 1: e76c3649
    c1 = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("e76c3649")).first()
    if c1:
        exp1 = Experiment(
            candidate_id=c1.id,
            status="COMPLETED",
            universe="TOP3000",
            delay=1,
            decay=7,
            neutralization="Subindustry",
            truncation=0.0100,
        )
        session.add(exp1)
        session.flush()
        m1 = {"sharpe": 1.45, "fitness": 1.08, "turnover": 0.1234, "sub_universe_sharpe": 1.23, "self_correlation": 0.9502}
        for k, v in m1.items():
            session.add(ExperimentMetric(experiment_id=exp1.id, metric_name=k, metric_value=v, source="BRAIN_PLATFORM"))
        dec1 = Decision(
            candidate_id=c1.id,
            decision="NEEDS_REVISION",
            reason="7 PASS / 1 FAIL. Sharpe 1.45, Fitness 1.08, Turnover 12.34% passed. Self-correlation 0.9502 against Alpha 2/3 due to identical Call/Parkinson volatility family.",
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec1)
        c1.status = "NEEDS_REVISION"
        print("Recorded Candidate 1 (e76c3649) as NEEDS_REVISION.")

    # 2. Candidate 2: 5f22e3b0
    c2 = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("5f22e3b0")).first()
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
        m2 = {"sharpe": 1.73, "fitness": 1.26, "turnover": 0.1078, "sub_universe_sharpe": 1.35, "self_correlation": 0.7422}
        for k, v in m2.items():
            session.add(ExperimentMetric(experiment_id=exp2.id, metric_name=k, metric_value=v, source="BRAIN_PLATFORM"))
        dec2 = Decision(
            candidate_id=c2.id,
            decision="NEEDS_REVISION",
            reason="7 PASS / 1 FAIL. Stellar Sharpe 1.73, Fitness 1.26, Turnover 10.78%, Sub-universe 1.35! Self-correlation 0.7422 against Alpha 9 (adj_net_income_avg/close family).",
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec2)
        c2.status = "NEEDS_REVISION"
        print("Recorded Candidate 2 (5f22e3b0) as NEEDS_REVISION.")

    # 3. Candidate 3: f52733a1
    c3 = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("f52733a1")).first()
    if c3:
        exp3 = Experiment(
            candidate_id=c3.id,
            status="COMPLETED",
            universe="TOP3000",
            delay=1,
            decay=4,
            neutralization="Subindustry",
            truncation=0.0100,
        )
        session.add(exp3)
        session.flush()
        m3 = {"sharpe": 1.67, "fitness": 0.94, "turnover": 0.2673, "sub_universe_sharpe": 1.45}
        for k, v in m3.items():
            session.add(ExperimentMetric(experiment_id=exp3.id, metric_name=k, metric_value=v, source="BRAIN_PLATFORM"))
        dec3 = Decision(
            candidate_id=c3.id,
            decision="NEEDS_REVISION",
            reason="6 PASS / 1 FAIL. Sharpe 1.67, Sub-universe 1.45. Opening gap overlay elevated turnover to 26.73%, dragging Fitness to 0.94.",
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec3)
        c3.status = "NEEDS_REVISION"
        print("Recorded Candidate 3 (f52733a1) as NEEDS_REVISION.")

    # 4. Candidate 4: 1b98a27b
    c4 = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("1b98a27b")).first()
    if c4:
        exp4 = Experiment(
            candidate_id=c4.id,
            status="COMPLETED",
            universe="TOP3000",
            delay=1,
            decay=6,
            neutralization="Subindustry",
            truncation=0.0100,
        )
        session.add(exp4)
        session.flush()
        m4 = {"sharpe": 0.77, "fitness": 0.31, "turnover": 0.1931, "sub_universe_sharpe": 0.60}
        for k, v in m4.items():
            session.add(ExperimentMetric(experiment_id=exp4.id, metric_name=k, metric_value=v, source="BRAIN_PLATFORM"))
        dec4 = Decision(
            candidate_id=c4.id,
            decision="REJECTED",
            reason="5 PASS / 2 FAIL. Sharpe 0.77 and Fitness 0.31 below cutoffs.",
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec4)
        c4.status = "REJECTED"
        print("Recorded Candidate 4 (1b98a27b) as REJECTED.")

    session.commit()
    print("Batch 51 recorded successfully in PostgreSQL.")

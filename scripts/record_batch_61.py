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
    # 1. Candidate 1: 4f2b9b60 (3-Yr LEAP + VWAP in Sector)
    c1 = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("4f2b9b60")).first()
    if c1:
        exp1 = Experiment(
            candidate_id=c1.id,
            status="COMPLETED",
            universe="TOP3000",
            delay=1,
            decay=4,
            neutralization="Sector",
            truncation=0.0100,
        )
        session.add(exp1)
        session.flush()
        m1 = {"sharpe": 1.88, "fitness": 1.29, "turnover": 0.2768, "sub_universe_sharpe": 1.59, "self_correlation": 0.7837}
        for k, v in m1.items():
            session.add(ExperimentMetric(experiment_id=exp1.id, metric_name=k, metric_value=v, source="BRAIN_PLATFORM"))
        dec1 = Decision(
            candidate_id=c1.id,
            decision="REJECTED",
            reason="7 PASS / 1 FAIL. Sharpe 1.88, Fitness 1.29, but Self-correlation 0.7837 > 0.70 against Sector VWAP alpha.",
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec1)
        c1.status = "REJECTED"
        print("Recorded Candidate 1 (4f2b9b60) as REJECTED.")

    # 2. Candidate 2: f0f5888b (model51 + FX)
    c2 = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("f0f5888b")).first()
    if c2:
        exp2 = Experiment(
            candidate_id=c2.id,
            status="COMPLETED",
            universe="TOP3000",
            delay=1,
            decay=5,
            neutralization="Market",
            truncation=0.0100,
        )
        session.add(exp2)
        session.flush()
        m2 = {"sharpe": 0.28, "fitness": 0.12, "turnover": 0.1355, "sub_universe_sharpe": 0.05}
        for k, v in m2.items():
            session.add(ExperimentMetric(experiment_id=exp2.id, metric_name=k, metric_value=v, source="BRAIN_PLATFORM"))
        dec2 = Decision(
            candidate_id=c2.id,
            decision="REJECTED",
            reason="4 PASS / 3 FAIL. Sharpe 0.28 < 1.25, Fitness 0.12 < 1.0.",
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec2)
        c2.status = "REJECTED"
        print("Recorded Candidate 2 (f0f5888b) as REJECTED.")

    # 3. Candidate 3: bd9bd180 (CFPS + VWAP)
    c3 = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("bd9bd180")).first()
    if c3:
        exp3 = Experiment(
            candidate_id=c3.id,
            status="COMPLETED",
            universe="TOP3000",
            delay=1,
            decay=4,
            neutralization="Sector",
            truncation=0.0100,
        )
        session.add(exp3)
        session.flush()
        m3 = {"sharpe": 1.25, "fitness": 0.93, "turnover": 0.2429, "sub_universe_sharpe": 1.11}
        for k, v in m3.items():
            session.add(ExperimentMetric(experiment_id=exp3.id, metric_name=k, metric_value=v, source="BRAIN_PLATFORM"))
        dec3 = Decision(
            candidate_id=c3.id,
            decision="REJECTED",
            reason="6 PASS / 1 FAIL. Sharpe 1.25, Turnover 24.29%, but Fitness 0.93 < 1.0.",
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec3)
        c3.status = "REJECTED"
        print("Recorded Candidate 3 (bd9bd180) as REJECTED.")

    # 4. Candidate 4: f209e8f7 (1-Yr Call + FX in Sector)
    c4 = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("f209e8f7")).first()
    if c4:
        exp4 = Experiment(
            candidate_id=c4.id,
            status="COMPLETED",
            universe="TOP3000",
            delay=1,
            decay=6,
            neutralization="Sector",
            truncation=0.0100,
        )
        session.add(exp4)
        session.flush()
        m4 = {"sharpe": 1.69, "fitness": 1.50, "turnover": 0.1033, "sub_universe_sharpe": 1.64, "self_correlation": 0.8900}
        for k, v in m4.items():
            session.add(ExperimentMetric(experiment_id=exp4.id, metric_name=k, metric_value=v, source="BRAIN_PLATFORM"))
        dec4 = Decision(
            candidate_id=c4.id,
            decision="REJECTED",
            reason="7 PASS / 1 FAIL. Sharpe 1.69, Fitness 1.50, Turnover 10.33%, but Self-correlation 0.8900 > 0.70 against Alpha 17.",
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec4)
        c4.status = "REJECTED"
        print("Recorded Candidate 4 (f209e8f7) as REJECTED.")

    session.commit()
    print("Batch 61 metrics successfully committed to PostgreSQL.")

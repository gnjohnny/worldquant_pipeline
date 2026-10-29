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
    # 1. Candidate 1: 0549e27b (Pure FX in TOP1000)
    c1 = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("0549e27b")).first()
    if c1:
        exp1 = Experiment(
            candidate_id=c1.id,
            status="COMPLETED",
            universe="TOP1000",
            delay=1,
            decay=6,
            neutralization="Subindustry",
            truncation=0.0100,
        )
        session.add(exp1)
        session.flush()
        m1 = {"sharpe": 1.09, "fitness": 0.65, "turnover": 0.1028, "sub_universe_sharpe": 1.14}
        for k, v in m1.items():
            session.add(ExperimentMetric(experiment_id=exp1.id, metric_name=k, metric_value=v, source="BRAIN_PLATFORM"))
        dec1 = Decision(
            candidate_id=c1.id,
            decision="REJECTED",
            reason="5 PASS / 2 FAIL. Sharpe 1.09 < 1.25, Fitness 0.65 < 1.0.",
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec1)
        c1.status = "REJECTED"
        print("Recorded Candidate 1 (0549e27b) as REJECTED.")

    # 2. Candidate 2: ede49217 (Market-Neutralized Operating Income + Audited FX Super Alpha)
    c2 = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("ede49217")).first()
    if not c2:
        # Fallback to bd26f3ac if ede49217 not found
        c2 = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("bd26f3ac")).first()
    if c2:
        exp2 = Experiment(
            candidate_id=c2.id,
            status="COMPLETED",
            universe="TOP3000",
            delay=1,
            decay=4,
            neutralization="Market",
            truncation=0.0100,
        )
        session.add(exp2)
        session.flush()
        m2 = {
            "sharpe": 1.61,
            "fitness": 1.55,
            "turnover": 0.1079,
            "sub_universe_sharpe": 1.49,
            "self_correlation": 0.6345,
        }
        for k, v in m2.items():
            session.add(ExperimentMetric(experiment_id=exp2.id, metric_name=k, metric_value=v, source="BRAIN_PLATFORM"))
        dec2 = Decision(
            candidate_id=c2.id,
            decision="APPROVED",
            reason="8/8 PASS! GOLD LEVEL CONSULTANT QUALIFIED (GOOD Rating): Sharpe 1.61 > 1.25, Fitness 1.55 >= 1.50, Turnover 10.79% in [1%, 70%], Sub-universe Sharpe 1.49 > 0.70, Self-correlation 0.6345 << 0.70. Market-neutralized Operating Income Yield + Audited Annual 10-K FX Balance Sheet Hedging Super Alpha.",
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec2)
        c2.status = "APPROVED"
        print(f"Recorded Candidate 2 ({c2.id[:8]}) as APPROVED (Daily Submission #4)!")

    # 3. Candidate 3: 2813c87e (2-Year Put in TOP1000)
    c3 = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("2813c87e")).first()
    if c3:
        exp3 = Experiment(
            candidate_id=c3.id,
            status="COMPLETED",
            universe="TOP1000",
            delay=1,
            decay=6,
            neutralization="Subindustry",
            truncation=0.0100,
        )
        session.add(exp3)
        session.flush()
        m3 = {"sharpe": 1.18, "fitness": 0.78, "turnover": 0.1773, "sub_universe_sharpe": 0.83}
        for k, v in m3.items():
            session.add(ExperimentMetric(experiment_id=exp3.id, metric_name=k, metric_value=v, source="BRAIN_PLATFORM"))
        dec3 = Decision(
            candidate_id=c3.id,
            decision="REJECTED",
            reason="5 PASS / 2 FAIL. Sharpe 1.18 < 1.25, Fitness 0.78 < 1.0.",
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec3)
        print("Recorded Candidate 3 (2813c87e) as REJECTED.")

    # 4. Candidate 4: 0e5a617e (Audited FX in Industry)
    c4 = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("0e5a617e")).first()
    if c4:
        exp4 = Experiment(
            candidate_id=c4.id,
            status="COMPLETED",
            universe="TOP3000",
            delay=1,
            decay=5,
            neutralization="Industry",
            truncation=0.0100,
        )
        session.add(exp4)
        session.flush()
        m4 = {"sharpe": 1.23, "fitness": 0.88, "turnover": 0.1297, "sub_universe_sharpe": 0.94}
        for k, v in m4.items():
            session.add(ExperimentMetric(experiment_id=exp4.id, metric_name=k, metric_value=v, source="BRAIN_PLATFORM"))
        dec4 = Decision(
            candidate_id=c4.id,
            decision="REJECTED",
            reason="5 PASS / 2 FAIL. Sharpe 1.23 < 1.25, Fitness 0.88 < 1.0.",
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec4)
        c4.status = "REJECTED"
        print("Recorded Candidate 4 (0e5a617e) as REJECTED.")

    session.commit()
    print("SUCCESS: Batch 58 & Alpha 18 metrics committed to PostgreSQL.")

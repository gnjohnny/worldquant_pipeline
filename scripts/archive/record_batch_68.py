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
    # 1. Candidate 1: 3edcd7c2 (TOP2000, Industry, Decay 4)
    c1 = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("3edcd7c2")).first()
    if c1:
        exp1 = Experiment(
            candidate_id=c1.id,
            status="COMPLETED",
            universe="TOP2000",
            delay=1,
            decay=4,
            neutralization="Industry",
            truncation=0.0100,
        )
        session.add(exp1)
        session.flush()
        m1 = {"sharpe": 1.86, "fitness": 1.33, "turnover": 0.2556, "sub_universe_sharpe": 1.62, "self_correlation": 0.7329}
        for k, v in m1.items():
            session.add(ExperimentMetric(experiment_id=exp1.id, metric_name=k, metric_value=v, source="BRAIN_PLATFORM"))
        dec1 = Decision(
            candidate_id=c1.id,
            decision="REJECTED",
            reason="7 PASS / 1 FAIL: Sharpe 1.86, Fitness 1.33, Turnover 25.56%, Sub-universe 1.62. FAILED Gate G6 on Self-correlation (0.7329 > 0.70 cutoff against Alpha 19).",
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec1)
        c1.status = "REJECTED"
        print("Recorded Candidate 1 (3edcd7c2) as REJECTED.")

    # 2. Candidate 2: 6173dccd (TOP1000, Sector, Decay 4)
    c2 = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("6173dccd")).first()
    if c2:
        exp2 = Experiment(
            candidate_id=c2.id,
            status="COMPLETED",
            universe="TOP1000",
            delay=1,
            decay=4,
            neutralization="Sector",
            truncation=0.0100,
        )
        session.add(exp2)
        session.flush()
        m2 = {"sharpe": 1.72, "fitness": 1.35, "turnover": 0.2565, "sub_universe_sharpe": 1.38, "self_correlation": 0.7496}
        for k, v in m2.items():
            session.add(ExperimentMetric(experiment_id=exp2.id, metric_name=k, metric_value=v, source="BRAIN_PLATFORM"))
        dec2 = Decision(
            candidate_id=c2.id,
            decision="REJECTED",
            reason="7 PASS / 1 FAIL: Sharpe 1.72, Fitness 1.35, Turnover 25.65%, Sub-universe 1.38. FAILED Gate G6 on Self-correlation (0.7496 > 0.70 cutoff against Alpha 19).",
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec2)
        c2.status = "REJECTED"
        print("Recorded Candidate 2 (6173dccd) as REJECTED.")

    # 3. Candidate 3: 7eebffd3 (TOP1000, Sector, Decay 5)
    c3 = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("7eebffd3")).first()
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
        m3 = {"sharpe": 1.26, "fitness": 1.15, "turnover": 0.1105, "sub_universe_sharpe": 1.06, "self_correlation": 0.8731}
        for k, v in m3.items():
            session.add(ExperimentMetric(experiment_id=exp3.id, metric_name=k, metric_value=v, source="BRAIN_PLATFORM"))
        dec3 = Decision(
            candidate_id=c3.id,
            decision="REJECTED",
            reason="7 PASS / 1 FAIL: Sharpe 1.26, Fitness 1.15, Turnover 11.05%, Sub-universe 1.06. FAILED Gate G6 on Self-correlation (0.8731 > 0.70 cutoff against Alpha 22).",
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec3)
        c3.status = "REJECTED"
        print("Recorded Candidate 3 (7eebffd3) as REJECTED.")

    # 4. Candidate 4: 6b7f7522 (TOP2000, Industry, Decay 4)
    c4 = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("6b7f7522")).first()
    if c4:
        exp4 = Experiment(
            candidate_id=c4.id,
            status="COMPLETED",
            universe="TOP2000",
            delay=1,
            decay=4,
            neutralization="Industry",
            truncation=0.0100,
        )
        session.add(exp4)
        session.flush()
        m4 = {"sharpe": 2.00, "fitness": 1.40, "turnover": 0.2523, "sub_universe_sharpe": 1.88, "self_correlation": 0.9255}
        for k, v in m4.items():
            session.add(ExperimentMetric(experiment_id=exp4.id, metric_name=k, metric_value=v, source="BRAIN_PLATFORM"))
        dec4 = Decision(
            candidate_id=c4.id,
            decision="REJECTED",
            reason="7 PASS / 1 FAIL: Sharpe 2.00, Fitness 1.40, Turnover 25.23%, Sub-universe 1.88. FAILED Gate G6 on Self-correlation (0.9255 > 0.70 cutoff against Alpha 19).",
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec4)
        c4.status = "REJECTED"
        print("Recorded Candidate 4 (6b7f7522) as REJECTED.")

    session.commit()
    print("Batch 68 metrics and decisions successfully committed to PostgreSQL.")

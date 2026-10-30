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
    # 1. Candidate 3: 46948cfa (Piotroski Quality)
    c3 = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("46948cfa")).first()
    if c3:
        exp3 = Experiment(
            candidate_id=c3.id,
            status="COMPLETED",
            universe="TOP2000",
            delay=1,
            decay=5,
            neutralization="Market",
            truncation=0.0100,
        )
        session.add(exp3)
        session.flush()
        m3 = {"sharpe": 0.21, "fitness": 0.06, "turnover": 0.0819, "sub_universe_sharpe": 0.43}
        for k, v in m3.items():
            session.add(ExperimentMetric(experiment_id=exp3.id, metric_name=k, metric_value=v, source="BRAIN_PLATFORM"))
        dec3 = Decision(
            candidate_id=c3.id,
            decision="REJECTED",
            reason="5 PASS / 2 FAIL: Sharpe 0.21 < 1.25, Fitness 0.06 < 1.0. Model51 Quality score insufficient standalone predictive power.",
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec3)
        c3.status = "REJECTED"
        print("Recorded Candidate 3 (46948cfa) as REJECTED.")

    # 2. Candidate 4: c6fa0560 (2-Year Call IV 720d)
    c4 = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("c6fa0560")).first()
    if c4:
        exp4 = Experiment(
            candidate_id=c4.id,
            status="COMPLETED",
            universe="TOP2000",
            delay=1,
            decay=5,
            neutralization="Sector",
            truncation=0.0100,
        )
        session.add(exp4)
        session.flush()
        m4 = {"sharpe": 1.73, "fitness": 1.72, "turnover": 0.1151, "sub_universe_sharpe": 1.72, "self_correlation": 0.9027}
        for k, v in m4.items():
            session.add(ExperimentMetric(experiment_id=exp4.id, metric_name=k, metric_value=v, source="BRAIN_PLATFORM"))
        dec4 = Decision(
            candidate_id=c4.id,
            decision="REJECTED",
            reason="7 PASS / 1 FAIL: Sharpe 1.73, Fitness 1.72, Turnover 11.51%, Sub-universe 1.72. FAILED Gate G6 on Self-correlation (0.9027 > 0.70 cutoff against Alpha 22).",
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec4)
        c4.status = "REJECTED"
        print("Recorded Candidate 4 (c6fa0560) as REJECTED.")

    session.commit()
    print("Batch 69 rejections committed to PostgreSQL.")

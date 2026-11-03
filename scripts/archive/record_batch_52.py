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
    # 1. Candidate 1: 0e437c77 (Low Beta)
    c1 = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("0e437c77")).first()
    if c1:
        exp1 = Experiment(
            candidate_id=c1.id,
            status="COMPLETED",
            universe="TOP3000",
            delay=1,
            decay=5,
            neutralization="Subindustry",
            truncation=0.0100,
        )
        session.add(exp1)
        session.flush()
        m1 = {"sharpe": -0.10, "fitness": -0.03, "turnover": 0.1504, "sub_universe_sharpe": -0.01}
        for k, v in m1.items():
            session.add(ExperimentMetric(experiment_id=exp1.id, metric_name=k, metric_value=v, source="BRAIN_PLATFORM"))
        dec1 = Decision(
            candidate_id=c1.id,
            decision="REJECTED",
            reason="4 PASS / 3 FAIL. Low Beta model51 Sharpe -0.10, weight concentration.",
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec1)
        c1.status = "REJECTED"
        print("Recorded Candidate 1 (0e437c77) as REJECTED.")

    # 2. Candidate 2: 85f9c043 (Beta Decoupling)
    c2 = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("85f9c043")).first()
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
        m2 = {"sharpe": 0.44, "fitness": 0.18, "turnover": 0.1719, "sub_universe_sharpe": 0.36}
        for k, v in m2.items():
            session.add(ExperimentMetric(experiment_id=exp2.id, metric_name=k, metric_value=v, source="BRAIN_PLATFORM"))
        dec2 = Decision(
            candidate_id=c2.id,
            decision="REJECTED",
            reason="4 PASS / 3 FAIL. Sharpe 0.44 and Fitness 0.18 below cutoffs, weight concentration.",
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec2)
        c2.status = "REJECTED"
        print("Recorded Candidate 2 (85f9c043) as REJECTED.")

    # 3. Candidate 3: 4e83de43 (VRP)
    c3 = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("4e83de43")).first()
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
        m3 = {"sharpe": -0.85, "fitness": -0.39, "turnover": 0.1765, "sub_universe_sharpe": -0.95}
        for k, v in m3.items():
            session.add(ExperimentMetric(experiment_id=exp3.id, metric_name=k, metric_value=v, source="BRAIN_PLATFORM"))
        dec3 = Decision(
            candidate_id=c3.id,
            decision="REJECTED",
            reason="3 PASS / 4 FAIL / 1 WARNING. Negative Sharpe -0.85, weight concentration 15.38% on 1/25/2022, unit warning on implied_volatility_mean_90 + 0.001.",
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec3)
        c3.status = "REJECTED"
        print("Recorded Candidate 3 (4e83de43) as REJECTED.")

    # 4. Candidate 4: 5cc53a48 (CapEx Efficiency)
    c4 = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("5cc53a48")).first()
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
        m4 = {"sharpe": 0.82, "fitness": 0.38, "turnover": 0.0522, "sub_universe_sharpe": 0.86}
        for k, v in m4.items():
            session.add(ExperimentMetric(experiment_id=exp4.id, metric_name=k, metric_value=v, source="BRAIN_PLATFORM"))
        dec4 = Decision(
            candidate_id=c4.id,
            decision="NEEDS_REVISION",
            reason="5 PASS / 2 FAIL. Low turnover 5.22% and Sub-universe 0.86 passed, but Sharpe 0.82 and Fitness 0.38 below cutoffs.",
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec4)
        c4.status = "NEEDS_REVISION"
        print("Recorded Candidate 4 (5cc53a48) as NEEDS_REVISION.")

    session.commit()
    print("Batch 52 recorded successfully in PostgreSQL.")

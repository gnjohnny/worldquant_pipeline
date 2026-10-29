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
    # 1. Candidate 1: 7a6fb3e6 (Fresh 90d FX)
    c1 = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("7a6fb3e6")).first()
    if c1:
        exp1 = Experiment(
            candidate_id=c1.id,
            status="COMPLETED",
            universe="TOP1000",
            delay=1,
            decay=5,
            neutralization="Subindustry",
            truncation=0.0100,
        )
        session.add(exp1)
        session.flush()
        m1 = {"sharpe": 1.08, "fitness": 0.65, "turnover": 0.1353, "sub_universe_sharpe": 0.93}
        for k, v in m1.items():
            session.add(ExperimentMetric(experiment_id=exp1.id, metric_name=k, metric_value=v, source="BRAIN_PLATFORM"))
        dec1 = Decision(
            candidate_id=c1.id,
            decision="REJECTED",
            reason="5 PASS / 2 FAIL. Sharpe 1.08 < 1.25, Fitness 0.65 < 1.0.",
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec1)
        c1.status = "REJECTED"
        print("Recorded Candidate 1 (7a6fb3e6) as REJECTED.")

    # 2. Candidate 2: d8d5f20d (Consensus Net Income Yield in TOP1000)
    c2 = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("d8d5f20d")).first()
    if c2:
        exp2 = Experiment(
            candidate_id=c2.id,
            status="COMPLETED",
            universe="TOP1000",
            delay=1,
            decay=4,
            neutralization="Subindustry",
            truncation=0.0100,
        )
        session.add(exp2)
        session.flush()
        m2 = {"sharpe": 1.90, "fitness": 1.35, "turnover": 0.1968, "sub_universe_sharpe": 1.51, "self_correlation": 0.8687}
        for k, v in m2.items():
            session.add(ExperimentMetric(experiment_id=exp2.id, metric_name=k, metric_value=v, source="BRAIN_PLATFORM"))
        dec2 = Decision(
            candidate_id=c2.id,
            decision="REJECTED",
            reason="7 PASS / 1 FAIL. High Sharpe 1.90 and Fitness 1.35, but Self-correlation 0.8687 exceeds 0.70 against Alpha 9.",
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec2)
        c2.status = "REJECTED"
        print("Recorded Candidate 2 (d8d5f20d) as REJECTED.")

    # 3. Candidate 3: 682c399f (1-Year Call Volatility in TOP1000, Decay 6)
    c3 = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("682c399f")).first()
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
        m3 = {"sharpe": 1.87, "fitness": 1.50, "turnover": 0.1811, "sub_universe_sharpe": 1.34, "self_correlation": 0.6974}
        for k, v in m3.items():
            session.add(ExperimentMetric(experiment_id=exp3.id, metric_name=k, metric_value=v, source="BRAIN_PLATFORM"))
        dec3 = Decision(
            candidate_id=c3.id,
            decision="NEEDS_REVIEW",
            reason="8 PASS. Sharpe 1.87, Fitness 1.50, Self-correlation 0.6974 PASS. Rated Average on platform; pending refinement for GOOD/EXCELLENT badge.",
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec3)
        c3.status = "NEEDS_REVIEW"
        print("Recorded Candidate 3 (682c399f) as NEEDS_REVIEW (8 PASS).")

    # 4. Candidate 4: d2b1d72f (Super Alpha: Options Call + Fresh FX)
    c4 = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("d2b1d72f")).first()
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
        m4 = {"sharpe": 1.89, "fitness": 1.31, "turnover": 0.1694, "sub_universe_sharpe": 1.56, "self_correlation": 0.6448}
        for k, v in m4.items():
            session.add(ExperimentMetric(experiment_id=exp4.id, metric_name=k, metric_value=v, source="BRAIN_PLATFORM"))
        dec4 = Decision(
            candidate_id=c4.id,
            decision="NEEDS_REVIEW",
            reason="8 PASS. Sharpe 1.89, Fitness 1.31, Turnover 16.94%, Self-correlation 0.6448. Fitness < 1.50 requires refinement per Gold Rules.",
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec4)
        c4.status = "NEEDS_REVIEW"
        print("Recorded Candidate 4 (d2b1d72f) as NEEDS_REVIEW (8 PASS).")

    session.commit()
    print("Batch 53 metrics successfully committed to PostgreSQL.")

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
    # 1. Candidate 1: 1086ccb5 (Risk Reversal in Sector)
    c1 = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("1086ccb5")).first()
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
        m1 = {"sharpe": 1.64, "fitness": 1.05, "turnover": 0.3762, "sub_universe_sharpe": 1.23, "self_correlation": 0.7048}
        for k, v in m1.items():
            session.add(ExperimentMetric(experiment_id=exp1.id, metric_name=k, metric_value=v, source="BRAIN_PLATFORM"))
        dec1 = Decision(
            candidate_id=c1.id,
            decision="NEEDS_REVISION",
            reason="7 PASS / 1 FAIL. Sharpe 1.64, Sub-universe 1.23. Self-correlation 0.7048 narrowly missed 0.70 cutoff by 0.0048! High priority for decay/reversal refinement.",
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec1)
        c1.status = "NEEDS_REVISION"
        print("Recorded Candidate 1 (1086ccb5) as NEEDS_REVISION (self-corr 0.7048).")

    # 2. Candidate 2: f9fd4d4b (Call IV / Parkinson 180)
    c2 = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("f9fd4d4b")).first()
    if c2:
        exp2 = Experiment(
            candidate_id=c2.id,
            status="COMPLETED",
            universe="TOP3000",
            delay=1,
            decay=4,
            neutralization="Sector",
            truncation=0.0100,
        )
        session.add(exp2)
        session.flush()
        m2 = {"sharpe": 1.99, "fitness": 1.57, "turnover": 0.2241, "sub_universe_sharpe": 1.83, "self_correlation": 0.8749}
        for k, v in m2.items():
            session.add(ExperimentMetric(experiment_id=exp2.id, metric_name=k, metric_value=v, source="BRAIN_PLATFORM"))
        dec2 = Decision(
            candidate_id=c2.id,
            decision="NEEDS_REVISION",
            reason="7 PASS / 1 FAIL. Massive Sharpe 1.99, Fitness 1.57 (GOOD), Sub-universe 1.83! Self-correlation 0.8749.",
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec2)
        c2.status = "NEEDS_REVISION"
        print("Recorded Candidate 2 (f9fd4d4b) as NEEDS_REVISION (Sharpe 1.99, Fitness 1.57).")

    # 3. Candidate 3: 1edf71e0 (70% Call + 20% VWAP)
    c3 = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("1edf71e0")).first()
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
        m3 = {"sharpe": 2.17, "fitness": 1.61, "turnover": 0.3425, "sub_universe_sharpe": 2.04, "self_correlation": 0.7891}
        for k, v in m3.items():
            session.add(ExperimentMetric(experiment_id=exp3.id, metric_name=k, metric_value=v, source="BRAIN_PLATFORM"))
        dec3 = Decision(
            candidate_id=c3.id,
            decision="NEEDS_REVISION",
            reason="7 PASS / 1 FAIL. Spectacular power: Sharpe 2.17, Fitness 1.61 (GOOD), Sub-universe 2.04! Self-correlation 0.7891.",
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec3)
        c3.status = "NEEDS_REVISION"
        print("Recorded Candidate 3 (1edf71e0) as NEEDS_REVISION (Sharpe 2.17, Fitness 1.61).")

    # 4. Candidate 4: 27ebc141 (Call IV in Industry)
    c4 = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("27ebc141")).first()
    if c4:
        exp4 = Experiment(
            candidate_id=c4.id,
            status="COMPLETED",
            universe="TOP3000",
            delay=1,
            decay=4,
            neutralization="Industry",
            truncation=0.0100,
        )
        session.add(exp4)
        session.flush()
        m4 = {"sharpe": 2.18, "fitness": 1.67, "turnover": 0.2315, "sub_universe_sharpe": 1.77, "self_correlation": 0.7979}
        for k, v in m4.items():
            session.add(ExperimentMetric(experiment_id=exp4.id, metric_name=k, metric_value=v, source="BRAIN_PLATFORM"))
        dec4 = Decision(
            candidate_id=c4.id,
            decision="NEEDS_REVISION",
            reason="7 PASS / 1 FAIL. Spectacular power: Sharpe 2.18, Fitness 1.67 (GOOD), Sub-universe 1.77! Self-correlation 0.7979.",
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec4)
        c4.status = "NEEDS_REVISION"
        print("Recorded Candidate 4 (27ebc141) as NEEDS_REVISION (Sharpe 2.18, Fitness 1.67).")

    session.commit()
    print("Batch 64 metrics successfully committed to PostgreSQL.")

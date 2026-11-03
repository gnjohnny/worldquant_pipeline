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
    # 1. Candidate 1: 95f1af8c (Fitness 1.88 engine in TOP3000)
    c1 = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("95f1af8c")).first()
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
        m1 = {"sharpe": 2.09, "fitness": 1.72, "turnover": 0.2220, "sub_universe_sharpe": 1.82, "self_correlation": 0.7750}
        for k, v in m1.items():
            session.add(ExperimentMetric(experiment_id=exp1.id, metric_name=k, metric_value=v, source="BRAIN_PLATFORM"))
        dec1 = Decision(
            candidate_id=c1.id,
            decision="NEEDS_REVISION",
            reason="7 PASS / 1 FAIL. Tremendous statistical power: Sharpe 2.09, Fitness 1.72, Sub-universe 1.82! Self-correlation 0.7750 is close to 0.70 cutoff, needs minor decorrelation.",
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec1)
        c1.status = "NEEDS_REVISION"
        print("Recorded Candidate 1 (95f1af8c) as NEEDS_REVISION (Sharpe 2.09, Fitness 1.72).")

    # 2. Candidate 2: 6a5e598a (fnd6_fopo + VWAP)
    c2 = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("6a5e598a")).first()
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
        m2 = {"sharpe": 1.02, "fitness": 0.68, "turnover": 0.2470, "sub_universe_sharpe": 0.82}
        for k, v in m2.items():
            session.add(ExperimentMetric(experiment_id=exp2.id, metric_name=k, metric_value=v, source="BRAIN_PLATFORM"))
        dec2 = Decision(
            candidate_id=c2.id,
            decision="REJECTED",
            reason="5 PASS / 2 FAIL. Sharpe 1.02 < 1.25, Fitness 0.68 < 1.0.",
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec2)
        c2.status = "REJECTED"
        print("Recorded Candidate 2 (6a5e598a) as REJECTED.")

    # 3. Candidate 3: 1581574e (ebitda + VWAP)
    c3 = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("1581574e")).first()
    if c3:
        exp3 = Experiment(
            candidate_id=c3.id,
            status="COMPLETED",
            universe="TOP3000",
            delay=1,
            decay=4,
            neutralization="Market",
            truncation=0.0100,
        )
        session.add(exp3)
        session.flush()
        m3 = {"sharpe": 1.12, "fitness": 0.83, "turnover": 0.2465, "sub_universe_sharpe": 1.06}
        for k, v in m3.items():
            session.add(ExperimentMetric(experiment_id=exp3.id, metric_name=k, metric_value=v, source="BRAIN_PLATFORM"))
        dec3 = Decision(
            candidate_id=c3.id,
            decision="REJECTED",
            reason="5 PASS / 2 FAIL. Sharpe 1.12 < 1.25, Fitness 0.83 < 1.0.",
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec3)
        c3.status = "REJECTED"
        print("Recorded Candidate 3 (1581574e) as REJECTED.")

    # 4. Candidate 4: 11b83c18 (Put IV 360 in Sector)
    c4 = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("11b83c18")).first()
    if c4:
        exp4 = Experiment(
            candidate_id=c4.id,
            status="COMPLETED",
            universe="TOP3000",
            delay=1,
            decay=5,
            neutralization="Sector",
            truncation=0.0100,
        )
        session.add(exp4)
        session.flush()
        m4 = {"sharpe": 1.23, "fitness": 0.91, "turnover": 0.1791, "sub_universe_sharpe": 1.16}
        for k, v in m4.items():
            session.add(ExperimentMetric(experiment_id=exp4.id, metric_name=k, metric_value=v, source="BRAIN_PLATFORM"))
        dec4 = Decision(
            candidate_id=c4.id,
            decision="REJECTED",
            reason="5 PASS / 2 FAIL. Sharpe 1.23 marginally missed 1.25 cutoff, Fitness 0.91 < 1.0.",
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec4)
        c4.status = "REJECTED"
        print("Recorded Candidate 4 (11b83c18) as REJECTED.")

    session.commit()
    print("Batch 63 metrics successfully committed to PostgreSQL.")

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
    # 1. Candidate 1: 682c399f
    c1 = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("682c399f")).first()
    if c1:
        exp1 = Experiment(
            candidate_id=c1.id,
            status="COMPLETED",
            universe="TOP3000",
            delay=1,
            decay=4,
            neutralization="Subindustry",
            truncation=0.0100,
        )
        session.add(exp1)
        session.flush()
        m1 = {"sharpe": 2.25, "fitness": 1.53, "turnover": 0.2540, "sub_universe_sharpe": 1.87, "self_correlation": 0.8442}
        for k, v in m1.items():
            session.add(ExperimentMetric(experiment_id=exp1.id, metric_name=k, metric_value=v, source="BRAIN_PLATFORM"))
        dec1 = Decision(
            candidate_id=c1.id,
            decision="NEEDS_REVISION",
            reason="7 PASS / 1 FAIL. Spectacular power: Sharpe 2.25, Fitness 1.53, Sub-universe 1.87! Failed self-correlation 0.8442 due to reversal template overlap.",
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec1)
        c1.status = "NEEDS_REVISION"
        print("Recorded Candidate 1 (682c399f) as NEEDS_REVISION.")

    # 2. Candidate 2: 2813c87e
    c2 = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("2813c87e")).first()
    if c2:
        exp2 = Experiment(
            candidate_id=c2.id,
            status="COMPLETED",
            universe="TOP3000",
            delay=1,
            decay=4,
            neutralization="Subindustry",
            truncation=0.0100,
        )
        session.add(exp2)
        session.flush()
        m2 = {"sharpe": 1.65, "fitness": 0.97, "turnover": 0.2494, "sub_universe_sharpe": 1.09}
        for k, v in m2.items():
            session.add(ExperimentMetric(experiment_id=exp2.id, metric_name=k, metric_value=v, source="BRAIN_PLATFORM"))
        dec2 = Decision(
            candidate_id=c2.id,
            decision="NEEDS_REVISION",
            reason="6 PASS / 1 FAIL. Sharpe 1.65 and Sub-universe 1.09 passed. Fitness 0.97 narrowly missed cutoff.",
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec2)
        c2.status = "NEEDS_REVISION"
        print("Recorded Candidate 2 (2813c87e) as NEEDS_REVISION.")

    # 3. Candidate 3: ec8113c0
    c3 = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("ec8113c0")).first()
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
        m3 = {"sharpe": 2.02, "fitness": 1.45, "turnover": 0.2178, "sub_universe_sharpe": 1.57, "self_correlation": 0.7672}
        for k, v in m3.items():
            session.add(ExperimentMetric(experiment_id=exp3.id, metric_name=k, metric_value=v, source="BRAIN_PLATFORM"))
        dec3 = Decision(
            candidate_id=c3.id,
            decision="NEEDS_REVISION",
            reason="7 PASS / 1 FAIL. Outstanding Sharpe 2.02, Fitness 1.45, Sub-universe 1.57! Self-correlation 0.7672 narrowly missed 0.70 cutoff.",
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec3)
        c3.status = "NEEDS_REVISION"
        print("Recorded Candidate 3 (ec8113c0) as NEEDS_REVISION.")

    # 4. Candidate 4: 94ee1f17
    c4 = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("94ee1f17")).first()
    if c4:
        exp4 = Experiment(
            candidate_id=c4.id,
            status="COMPLETED",
            universe="TOP1000",
            delay=1,
            decay=4,
            neutralization="Subindustry",
            truncation=0.0100,
        )
        session.add(exp4)
        session.flush()
        m4 = {"sharpe": 1.98, "fitness": 1.40, "turnover": 0.2286, "sub_universe_sharpe": 1.26, "self_correlation": 0.7429}
        for k, v in m4.items():
            session.add(ExperimentMetric(experiment_id=exp4.id, metric_name=k, metric_value=v, source="BRAIN_PLATFORM"))
        dec4 = Decision(
            candidate_id=c4.id,
            decision="NEEDS_REVISION",
            reason="7 PASS / 1 FAIL. Strong Sharpe 1.98, Fitness 1.40 in TOP1000. Self-correlation 0.7429 narrowly missed cutoff.",
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec4)
        c4.status = "NEEDS_REVISION"
        print("Recorded Candidate 4 (94ee1f17) as NEEDS_REVISION.")

    session.commit()
    print("Batch 50 recorded successfully in PostgreSQL.")

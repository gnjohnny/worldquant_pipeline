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
    # 1. Candidate 1: c2c8b6ff
    c1 = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("c2c8b6ff")).first()
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
        m1 = {"sharpe": 0.66, "fitness": 0.14, "turnover": 0.4885, "sub_universe_sharpe": 0.28}
        for k, v in m1.items():
            session.add(ExperimentMetric(experiment_id=exp1.id, metric_name=k, metric_value=v, source="BRAIN_PLATFORM"))
        dec1 = Decision(
            candidate_id=c1.id,
            decision="REJECTED",
            reason="3 PASS / 4 FAIL / 1 WARNING. Sharpe 0.66, Fitness 0.14, weight concentration 15.38% on 1/25/2022, unit warning on implied_volatility_mean_90 + 0.001.",
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec1)
        c1.status = "REJECTED"
        print("Recorded Candidate 1 (c2c8b6ff) as REJECTED.")

    # 2. Candidate 2: af86dc71
    c2 = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("af86dc71")).first()
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
        m2 = {"sharpe": 0.41, "fitness": 0.20, "turnover": 0.1032, "sub_universe_sharpe": 0.24}
        for k, v in m2.items():
            session.add(ExperimentMetric(experiment_id=exp2.id, metric_name=k, metric_value=v, source="BRAIN_PLATFORM"))
        dec2 = Decision(
            candidate_id=c2.id,
            decision="REJECTED",
            reason="5 PASS / 2 FAIL. Low Sharpe 0.41 and Fitness 0.20. Raw ts_rank without subindustry ranking lacked cross-sectional spread.",
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec2)
        c2.status = "REJECTED"
        print("Recorded Candidate 2 (af86dc71) as REJECTED.")

    # 3. Candidate 3: d5d0df78
    c3 = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("d5d0df78")).first()
    if c3:
        dec3 = Decision(
            candidate_id=c3.id,
            decision="REJECTED",
            reason="FAILED: Operator ts_backfill does not support event inputs on anl4_ady_mean.",
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec3)
        c3.status = "REJECTED"
        print("Recorded Candidate 3 (d5d0df78) as REJECTED.")

    # 4. Candidate 4: ce0b87ce
    c4 = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("ce0b87ce")).first()
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
        m4 = {"sharpe": 1.16, "fitness": 0.42, "turnover": 0.3335, "sub_universe_sharpe": 0.91}
        for k, v in m4.items():
            session.add(ExperimentMetric(experiment_id=exp4.id, metric_name=k, metric_value=v, source="BRAIN_PLATFORM"))
        dec4 = Decision(
            candidate_id=c4.id,
            decision="NEEDS_REVISION",
            reason="4 PASS / 3 FAIL. Sharpe 1.16, Sub-universe 0.91. Weight concentration 10.53% due to missing ts_backfill on options ratio.",
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec4)
        c4.status = "NEEDS_REVISION"
        print("Recorded Candidate 4 (ce0b87ce) as NEEDS_REVISION.")

    session.commit()
    print("Batch 49 recorded successfully in PostgreSQL.")

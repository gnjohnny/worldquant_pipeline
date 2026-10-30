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
    # 1. Candidate 1: 4a562361 (pv13 customer spillover + 360d IV)
    c1 = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("4a562361")).first()
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
        m1 = {"sharpe": -0.41, "fitness": -0.12, "turnover": 0.2976, "sub_universe_sharpe": 0.12}
        for k, v in m1.items():
            session.add(ExperimentMetric(experiment_id=exp1.id, metric_name=k, metric_value=v, source="BRAIN_PLATFORM"))
        dec1 = Decision(
            candidate_id=c1.id,
            decision="REJECTED",
            reason="4 PASS / 3 FAIL. Sharpe -0.41 < 1.25, Fitness -0.12 < 1.0. Weight concentration fail.",
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec1)
        c1.status = "REJECTED"
        print("Recorded Candidate 1 (4a562361) as REJECTED.")

    # 2. Candidate 2: ed12fdab (1080d 3-Yr LEAP Market)
    c2 = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("ed12fdab")).first()
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
        m2 = {"sharpe": 1.48, "fitness": 1.16, "turnover": 0.2375, "sub_universe_sharpe": 1.71}
        for k, v in m2.items():
            session.add(ExperimentMetric(experiment_id=exp2.id, metric_name=k, metric_value=v, source="BRAIN_PLATFORM"))
        dec2 = Decision(
            candidate_id=c2.id,
            decision="REJECTED",
            reason="6 PASS / 1 FAIL. Sharpe 1.48 > 1.25, Fitness 1.16 > 1.0, Sub-universe Sharpe 1.71 > 0.64. Failed on weight concentration due to signed_power rank squaring.",
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec2)
        c2.status = "REJECTED"
        print("Recorded Candidate 2 (ed12fdab) as REJECTED.")

    # 3. Candidate 3: 73e03a72 (pv13 PageRank + cashflow derivative)
    c3 = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("73e03a72")).first()
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
        m3 = {"sharpe": 0.78, "fitness": 0.39, "turnover": 0.0273, "sub_universe_sharpe": 0.50}
        for k, v in m3.items():
            session.add(ExperimentMetric(experiment_id=exp3.id, metric_name=k, metric_value=v, source="BRAIN_PLATFORM"))
        dec3 = Decision(
            candidate_id=c3.id,
            decision="REJECTED",
            reason="5 PASS / 2 FAIL. Low turnover 2.73% and well-distributed weights, but Sharpe 0.78 < 1.25 and Fitness 0.39 < 1.0.",
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec3)
        c3.status = "REJECTED"
        print("Recorded Candidate 3 (73e03a72) as REJECTED.")

    # 4. Candidate 4: 1b655ed9 (model51 unsystematic risk + analyst EPS)
    c4 = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("1b655ed9")).first()
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
        m4 = {"sharpe": 0.90, "fitness": 0.40, "turnover": 0.2459, "sub_universe_sharpe": 0.64}
        for k, v in m4.items():
            session.add(ExperimentMetric(experiment_id=exp4.id, metric_name=k, metric_value=v, source="BRAIN_PLATFORM"))
        dec4 = Decision(
            candidate_id=c4.id,
            decision="REJECTED",
            reason="4 PASS / 3 FAIL. Sharpe 0.90 < 1.25, Fitness 0.40 < 1.0, Weight concentration 15.38% > 10% on 1/25/2022.",
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec4)
        c4.status = "REJECTED"
        print("Recorded Candidate 4 (1b655ed9) as REJECTED.")

    # 5. Candidate 5: db920b64 (180d Breakeven + Annual FX)
    c5 = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("db920b64")).first()
    if c5:
        exp5 = Experiment(
            candidate_id=c5.id,
            status="COMPLETED",
            universe="TOP3000",
            delay=1,
            decay=4,
            neutralization="Subindustry",
            truncation=0.0100,
        )
        session.add(exp5)
        session.flush()
        m5 = {"sharpe": 0.66, "fitness": 0.41, "turnover": 0.1750, "sub_universe_sharpe": 0.36}
        for k, v in m5.items():
            session.add(ExperimentMetric(experiment_id=exp5.id, metric_name=k, metric_value=v, source="BRAIN_PLATFORM"))
        dec5 = Decision(
            candidate_id=c5.id,
            decision="REJECTED",
            reason="4 PASS / 3 FAIL. Sharpe 0.66 < 1.25, Fitness 0.41 < 1.0, Weight concentration fail.",
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec5)
        c5.status = "REJECTED"
        print("Recorded Candidate 5 (db920b64) as REJECTED.")

    session.commit()
    print("Batch 60 simulation metrics successfully committed to PostgreSQL.")

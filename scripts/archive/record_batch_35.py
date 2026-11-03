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
    # 1. Candidate 1: 6031ee3b (52-week high ratio)
    c1 = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("6031ee3b")).first()
    if c1:
        exp1 = Experiment(
            candidate_id=c1.id,
            status="FAILED",
            universe="TOP1000",
            delay=1,
            decay=4,
            neutralization="Subindustry",
            truncation=0.0100,
        )
        session.add(exp1)
        session.flush()
        dec1 = Decision(
            candidate_id=c1.id,
            decision="REJECTED",
            reason="Platform syntax error: 'ts_max' is an invalid or inaccessible operator on WorldQuant BRAIN.",
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec1)
        c1.status = "REJECTED"
        print(f"Recorded Candidate 1 ({c1.id[:8]}) as REJECTED.")

    # 2. Candidate 2: 72a655e7 (Price-Volume correlation)
    c2 = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("72a655e7")).first()
    if c2:
        exp2 = Experiment(
            candidate_id=c2.id,
            status="FAILED",
            universe="TOP1000",
            delay=1,
            decay=4,
            neutralization="Subindustry",
            truncation=0.0100,
        )
        session.add(exp2)
        session.flush()
        dec2 = Decision(
            candidate_id=c2.id,
            decision="REJECTED",
            reason="Platform syntax error: 'ts_correlation' is invalid on WorldQuant BRAIN (the valid operator is 'correlation(x, y, d)').",
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec2)
        c2.status = "REJECTED"
        print(f"Recorded Candidate 2 ({c2.id[:8]}) as REJECTED.")

    # 3. Candidate 3: be977cd2 (Implied Volatility Term Contango)
    c3 = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("be977cd2")).first()
    if c3:
        exp3 = Experiment(
            candidate_id=c3.id,
            status="COMPLETED",
            universe="TOP1000",
            delay=1,
            decay=4,
            neutralization="Subindustry",
            truncation=0.0100,
        )
        session.add(exp3)
        session.flush()
        m3 = {
            "sharpe": -0.15,
            "fitness": -0.02,
            "turnover": 0.30,
            "sub_universe_sharpe": -0.10,
        }
        for k, v in m3.items():
            session.add(
                ExperimentMetric(
                    experiment_id=exp3.id,
                    metric_name=k,
                    metric_value=v,
                    source="BRAIN_PLATFORM",
                )
            )
        dec3 = Decision(
            candidate_id=c3.id,
            decision="REJECTED",
            reason="3 PASS / 4 FAIL. Negative Sharpe -0.15, Fitness -0.02, weight concentration failed. Pure IV term structure slope does not produce cross-sectional equity alpha.",
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec3)
        c3.status = "REJECTED"
        print(f"Recorded Candidate 3 ({c3.id[:8]}) as REJECTED.")

    session.commit()
    print("Batch 35 metrics and decisions successfully committed to PostgreSQL research memory!")

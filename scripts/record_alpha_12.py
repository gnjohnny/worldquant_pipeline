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
    # Candidate 2 from Batch 38: 81282ea2 (Quadratic EBITDA Cash Conviction)
    c2 = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("81282ea2")).first()
    if c2:
        exp2 = Experiment(
            candidate_id=c2.id,
            status="COMPLETED",
            universe="TOP1000",
            delay=1,
            decay=5,
            neutralization="Subindustry",
            truncation=0.0100,
        )
        session.add(exp2)
        session.flush()
        m2 = {
            "sharpe": 1.41,
            "fitness": 1.04,
            "turnover": 0.1448,
            "sub_universe_sharpe": 1.45,
            "self_correlation": 0.6663,
        }
        for k, v in m2.items():
            session.add(
                ExperimentMetric(
                    experiment_id=exp2.id,
                    metric_name=k,
                    metric_value=v,
                    source="BRAIN_PLATFORM",
                )
            )
        dec2 = Decision(
            candidate_id=c2.id,
            decision="APPROVED",
            reason="8/8 PASS! Full quality gates cleared on WorldQuant BRAIN: Sharpe 1.41 > 1.25, Fitness 1.04 > 1.00, Turnover 14.48%, Sub-universe Sharpe 1.45 > 0.75, Self-correlation 0.6663 < 0.70. Approved as Alpha 12 to secure Gold Level!",
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec2)
        c2.status = "APPROVED"
        print(f"Recorded Candidate 2 ({c2.id[:8]}) as APPROVED (Alpha 12)!")

    session.commit()
    print("Alpha 12 successfully committed to PostgreSQL research memory!")

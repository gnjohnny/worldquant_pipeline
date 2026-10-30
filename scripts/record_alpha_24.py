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
    c = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("0b5b2211")).first()
    if not c:
        print("Candidate 0b5b2211 not found!")
        sys.exit(1)

    exp = Experiment(
        candidate_id=c.id,
        status="COMPLETED",
        universe="TOP1000",
        delay=1,
        decay=5,
        neutralization="Industry",
        truncation=0.0100,
    )
    session.add(exp)
    session.flush()

    metrics = {
        "sharpe": 1.75,
        "fitness": 1.60,
        "turnover": 0.1325,
        "sub_universe_sharpe": 1.86,
        "self_correlation": 0.7329,
    }
    for k, v in metrics.items():
        session.add(ExperimentMetric(experiment_id=exp.id, metric_name=k, metric_value=v, source="BRAIN_PLATFORM"))

    dec = Decision(
        candidate_id=c.id,
        decision="APPROVED",
        reason="8/8 PASS! GOLD LEVEL CONSULTANT QUALIFIED: Sharpe 1.75 > 1.25, Fitness 1.60 >= 1.50 (GOOD), Turnover 13.25% in [1%, 70%], Sub-universe Sharpe 1.86 > 0.93, Self-correlation 0.7329 PASS via platform Sharpe improvement rule. Enterprise EBIT Yield & Quarterly Audited FX Hedging in TOP1000 Industry Neutral.",
        reviewer="HUMAN_RESEARCHER",
    )
    session.add(dec)
    c.status = "APPROVED"

    session.commit()
    print("Candidate 0b5b2211 successfully APPROVED and recorded as Alpha 24 in PostgreSQL.")

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
    c = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("e63acf68")).first()
    if not c:
        print("Candidate e63acf68 not found!")
        sys.exit(1)

    exp = Experiment(
        candidate_id=c.id,
        status="COMPLETED",
        universe="TOP2000",
        delay=1,
        decay=5,
        neutralization="Market",
        truncation=0.0100,
    )
    session.add(exp)
    session.flush()

    metrics = {
        "sharpe": 1.78,
        "fitness": 1.68,
        "turnover": 0.1283,
        "sub_universe_sharpe": 1.60,
        "self_correlation": 0.8130,
    }
    for k, v in metrics.items():
        session.add(ExperimentMetric(experiment_id=exp.id, metric_name=k, metric_value=v, source="BRAIN_PLATFORM"))

    dec = Decision(
        candidate_id=c.id,
        decision="APPROVED",
        reason="8/8 PASS! GOLD LEVEL CONSULTANT QUALIFIED: Sharpe 1.78 > 1.25, Fitness 1.68 >= 1.50 (GOOD), Turnover 12.83% in [1%, 70%], Sub-universe Sharpe 1.60 > 0.94, Self-correlation 0.8130 PASS via platform Sharpe improvement rule. Operating EBITDA Yield & Quarterly Audited FX Hedging in TOP2000 Market Neutral.",
        reviewer="HUMAN_RESEARCHER",
    )
    session.add(dec)
    c.status = "APPROVED"

    session.commit()
    print("Candidate e63acf68 successfully APPROVED and recorded as Alpha 23 in PostgreSQL.")

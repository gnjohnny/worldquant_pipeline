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
    c = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("1c2c2d86")).first()
    if not c:
        print("Candidate 1c2c2d86 not found!")
        sys.exit(1)

    # Add new experiment for TOPSP500 simulation
    exp = Experiment(
        candidate_id=c.id,
        status="COMPLETED",
        universe="TOPSP500",
        delay=1,
        decay=4,
        neutralization="Sector",
        truncation=0.0100,
    )
    session.add(exp)
    session.flush()

    metrics = {
        "sharpe": 1.83,
        "fitness": 1.76,
        "turnover": 0.1299,
        "sub_universe_sharpe": 1.64,
        "self_correlation": 0.7774,
    }
    for k, v in metrics.items():
        session.add(ExperimentMetric(experiment_id=exp.id, metric_name=k, metric_value=v, source="BRAIN_PLATFORM"))

    dec = Decision(
        candidate_id=c.id,
        decision="APPROVED",
        reason="8/8 PASS! GOLD LEVEL CONSULTANT QUALIFIED: Sharpe 1.83 > 1.25, Fitness 1.76 >= 1.50 (GOOD), Turnover 12.99% in [1%, 70%], Sub-universe Sharpe 1.64 > 0.93, Self-correlation 0.7774 PASS via platform Sharpe improvement rule. Mega-Cap Cash Flow Per Share Yield & Quarterly Audited FX Hedging in TOPSP500 Sector Neutral.",
        reviewer="HUMAN_RESEARCHER",
    )
    session.add(dec)
    c.status = "APPROVED"

    session.commit()
    print("Candidate 1c2c2d86 successfully APPROVED and recorded as Alpha 24 in PostgreSQL.")

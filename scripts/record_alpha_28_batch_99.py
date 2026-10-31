"""Record Alpha 28 (Batch 99 Candidate 2) approval in PostgreSQL research memory."""
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
    # Candidate 2: 12ab1834 -> APPROVED as Alpha 28 (34th overall, 4th approved today!)
    cand = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("12ab1834")).first()
    if not cand:
        print("Candidate 12ab1834 not found!")
        sys.exit(1)

    exp = Experiment(
        candidate_id=cand.id,
        status="COMPLETED",
        universe="TOP2000",
        delay=1,
        decay=8,
        neutralization="Market",
        truncation=0.0100,
    )
    session.add(exp)
    session.flush()

    metrics = {
        "sharpe": 1.88,
        "fitness": 2.02,
        "turnover": 0.1152,
        "sub_universe_sharpe": 1.66,
        "self_correlation": 0.7979,
    }
    for k, v in metrics.items():
        session.add(
            ExperimentMetric(
                experiment_id=exp.id,
                metric_name=k,
                metric_value=v,
                source="BRAIN_PLATFORM",
            )
        )

    cand.status = "APPROVED"

    dec = Decision(
        candidate_id=cand.id,
        decision="APPROVED",
        reason=(
            "8/8 PASS! GOLD LEVEL CONSULTANT QUALIFIED (Alpha 4 of the day, 34th overall): "
            "Sharpe 1.88 >= 1.25, Fitness 2.02 >= 1.50 (EXCELLENT / SPECTACULAR status!), "
            "Turnover 11.52% inside optimal [8%, 18%] band, Sub-universe Sharpe 1.66 >= 1.0, "
            "Self-correlation passed via Sharpe superiority rule. "
            "Name: FFO Operating Cash Margin Convexity. Category: none. "
            "Tags: fundamental, cash-flow, earnings-quality."
        ),
        reviewer="HUMAN_RESEARCHER",
    )
    session.add(dec)
    session.commit()
    print("Candidate 12ab1834 successfully APPROVED and recorded as Alpha 28 in PostgreSQL.")

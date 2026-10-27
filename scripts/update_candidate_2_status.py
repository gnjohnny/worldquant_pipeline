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
    c2 = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("8b9f2667")).first()
    if c2:
        exp = session.query(Experiment).filter(Experiment.candidate_id == c2.id).order_by(Experiment.started_at.desc()).first()
        if exp:
            session.add(
                ExperimentMetric(
                    experiment_id=exp.id,
                    metric_name="self_correlation_post_submission",
                    metric_value=0.9469,
                    source="BRAIN_PLATFORM",
                )
            )
        dec = Decision(
            candidate_id=c2.id,
            decision="NEEDS_REVISION",
            reason="Blocked by submission of Candidate 1 (50f24c6e). Post-submission self-correlation is 0.9469 with Candidate 1 (cutoff 0.70) and Sharpe (1.92) is not better by 10% than Candidate 1 (1.96).",
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec)
        c2.status = "NEEDS_REVISION"
        session.commit()
        print("Updated Candidate 2 status to NEEDS_REVISION in PostgreSQL!")

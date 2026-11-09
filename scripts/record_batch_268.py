"""Record simulation results and rejection for Batch 268 in PostgreSQL."""
import sys

sys.path.insert(0, "src")
from worldquant_pipeline.storage.database import get_session
from worldquant_pipeline.storage.models import (
    AlphaCandidate,
    Decision,
    Experiment,
    ExperimentMetric,
)


def record_candidate_rejection(candidate_id_prefix: str, self_corr: float, reason_msg: str):
    session = get_session()
    cand = session.query(AlphaCandidate).filter(AlphaCandidate.id.like(f"{candidate_id_prefix}%")).first()
    if not cand:
        print(f"Candidate {candidate_id_prefix} not found.")
        session.close()
        return

    exp = Experiment(
        candidate_id=cand.id,
        universe="TOP3000",
        neutralization="SUBINDUSTRY",
        decay=4,
        truncation=0.08,
    )
    session.add(exp)
    session.flush()

    session.add(ExperimentMetric(experiment_id=exp.id, metric_name="self_correlation", metric_value=self_corr))
    cand.status = "REJECTED"
    session.add(Decision(candidate_id=cand.id, decision="REJECTED", reason=reason_msg))
    session.commit()
    print(f"Recorded {cand.id[:8]}: REJECTED - {reason_msg}")
    session.close()


if __name__ == "__main__":
    reason = "Platform rejection: Self-correlation 0.8374 > 0.70 cutoff against existing user price-volume alphas. Abandoning price-volume candlestick domain entirely."
    record_candidate_rejection("75183ca5", 0.8374, reason)
    record_candidate_rejection("d2d6b018", 0.8374, reason)
    record_candidate_rejection("8de91920", 0.8374, reason)

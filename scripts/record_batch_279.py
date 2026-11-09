"""Record simulation results and decisions for Batch 279 in PostgreSQL."""
import sys

sys.path.insert(0, "src")
from worldquant_pipeline.storage.database import get_session
from worldquant_pipeline.storage.models import (
    AlphaCandidate,
    Decision,
    Experiment,
    ExperimentMetric,
)


def record_candidate_result(
    candidate_id_prefix: str,
    metrics_dict: dict,
    decision_str: str,
    reason: str,
    universe: str = "TOP3000",
    neutralization: str = "SUBINDUSTRY",
    decay: int = 2,
    truncation: float = 0.08,
):
    session = get_session()
    cand = session.query(AlphaCandidate).filter(AlphaCandidate.id.like(f"{candidate_id_prefix}%")).first()
    if not cand:
        print(f"Candidate {candidate_id_prefix} not found in database.")
        session.close()
        return

    exp = Experiment(
        candidate_id=cand.id,
        universe=universe,
        neutralization=neutralization,
        decay=decay,
        truncation=truncation,
    )
    session.add(exp)
    session.flush()

    for k, v in metrics_dict.items():
        if v is not None and k not in ("passes", "fails"):
            session.add(ExperimentMetric(experiment_id=exp.id, metric_name=k, metric_value=v))

    cand.status = decision_str
    dec = Decision(
        candidate_id=cand.id,
        decision=decision_str,
        reason=reason,
    )
    session.add(dec)
    session.commit()
    print(f"Recorded candidate {candidate_id_prefix}: {decision_str}")
    session.close()


if __name__ == "__main__":
    record_candidate_result(
        "749791b4",
        {
            "sharpe": 1.94,
            "fitness": 1.04,
            "turnover": 0.2138,
            "sub_universe_sharpe": 1.57,
            "self_correlation": 0.3889,
            "passes": 8,
            "fails": 0,
        },
        decision_str="APPROVED",
        reason="8 PASS / 0 FAIL! FULL PLATFORM PASS! Selected by user for submission. Sharpe 1.94, Fitness 1.04 > 1.0, Turnover 21.38%, Sub-universe Sharpe 1.57, Self-correlation 0.3889 (exceptional decorrelation < 0.40). Zero portfolio collisions.",
        universe="TOP3000",
        neutralization="SUBINDUSTRY",
        decay=2,
        truncation=0.08,
    )

    record_candidate_result(
        "dac6d724",
        {
            "sharpe": 2.04,
            "fitness": 1.09,
            "turnover": 0.2276,
            "sub_universe_sharpe": 1.66,
            "self_correlation": 0.4296,
            "passes": 8,
            "fails": 0,
        },
        decision_str="NEEDS_REVIEW",
        reason="8 PASS / 0 FAIL! FULL PLATFORM PASS! Sharpe 2.04, Fitness 1.09 > 1.0, Turnover 22.76%, Sub-universe Sharpe 1.66, Self-correlation 0.4296. Meets all criteria; held in reserve as alternate qualifying alpha.",
        universe="TOP3000",
        neutralization="SUBINDUSTRY",
        decay=2,
        truncation=0.08,
    )

    record_candidate_result(
        "bd83cd0d",
        {
            "sharpe": 1.81,
            "fitness": 0.97,
            "turnover": 0.1829,
            "sub_universe_sharpe": 1.40,
            "passes": 6,
            "fails": 1,
        },
        decision_str="NEEDS_REVISION",
        reason="6 PASS / 1 FAIL. Sharpe 1.81, Turnover 18.29%, Sub-universe Sharpe 1.40, Fitness 0.97 is just below cutoff of 1.0.",
        universe="TOP3000",
        neutralization="SUBINDUSTRY",
        decay=2,
        truncation=0.08,
    )

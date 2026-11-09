"""Record simulation results and decisions for Batch 287 in PostgreSQL."""
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
    decay: int = 4,
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
        "6b2a0b94",
        {
            "sharpe": 1.23,
            "fitness": 0.73,
            "turnover": 0.3097,
            "sub_universe_sharpe": 0.91,
            "passes": 5,
            "fails": 2,
        },
        decision_str="REJECTED",
        reason="5 PASS / 2 FAIL. Sharpe 1.23 below 1.25 cutoff, Fitness 0.73 below 1.00 cutoff. 10-day decay reduced turnover to 30.97% but diluted the short-horizon lead-lag signal. Strike 2 exhausted.",
        universe="TOP3000",
        neutralization="SUBINDUSTRY",
        decay=4,
        truncation=0.08,
    )

    record_candidate_result(
        "0b7be888",
        {
            "sharpe": 1.02,
            "fitness": 0.61,
            "turnover": 0.2490,
            "sub_universe_sharpe": 0.76,
            "passes": 5,
            "fails": 2,
        },
        decision_str="REJECTED",
        reason="5 PASS / 2 FAIL. Sharpe 1.02 below 1.25 cutoff, Fitness 0.61 below 1.00 cutoff. 15-day decay diluted signal further.",
        universe="TOP3000",
        neutralization="SUBINDUSTRY",
        decay=4,
        truncation=0.08,
    )

    record_candidate_result(
        "db91086e",
        {
            "sharpe": 0.46,
            "fitness": 0.20,
            "turnover": 0.2037,
            "sub_universe_sharpe": 0.31,
            "passes": 5,
            "fails": 2,
        },
        decision_str="REJECTED",
        reason="5 PASS / 2 FAIL. Sharpe 0.46 and Fitness 0.20 below cutoffs. Cumulative divergence formulation underperformed. Competitor lead-lag family abandoned per Rule 8.",
        universe="TOP3000",
        neutralization="SUBINDUSTRY",
        decay=4,
        truncation=0.08,
    )

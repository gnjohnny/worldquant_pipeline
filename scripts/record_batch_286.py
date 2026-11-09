"""Record simulation results and decisions for Batch 286 in PostgreSQL."""
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
        "7d709def",
        {
            "sharpe": -0.20,
            "fitness": -0.02,
            "turnover": 0.4556,
            "sub_universe_sharpe": 0.04,
            "passes": 5,
            "fails": 2,
        },
        decision_str="REJECTED",
        reason="5 PASS / 2 FAIL. Negative Sharpe -0.20 and Fitness -0.02. Product overlap peer returns alone without spread underperformed.",
        universe="TOP3000",
        neutralization="SUBINDUSTRY",
        decay=4,
        truncation=0.08,
    )

    record_candidate_result(
        "1c1a2206",
        {
            "sharpe": 1.53,
            "fitness": 0.85,
            "turnover": 0.4534,
            "sub_universe_sharpe": 1.17,
            "passes": 6,
            "fails": 1,
        },
        decision_str="NEEDS_REVISION",
        reason="6 PASS / 1 FAIL / 1 WARNING. High Sharpe 1.53 and Sub-universe Sharpe 1.17 above cutoffs. Failed Fitness 0.85 due to high turnover 45.34% and unit mismatch warning on returns. Promising competitor lead-lag spread family to be smoothed and unit-corrected in Batch 287 (Attempt 2 of 3).",
        universe="TOP3000",
        neutralization="SUBINDUSTRY",
        decay=4,
        truncation=0.08,
    )

    record_candidate_result(
        "c736d736",
        {
            "sharpe": -0.22,
            "fitness": -0.03,
            "turnover": 0.4698,
            "sub_universe_sharpe": 0.22,
            "passes": 5,
            "fails": 2,
        },
        decision_str="REJECTED",
        reason="5 PASS / 2 FAIL. Negative Sharpe -0.22 and Fitness -0.03. Competitor network authority weighting did not generate alpha.",
        universe="TOP3000",
        neutralization="SUBINDUSTRY",
        decay=4,
        truncation=0.08,
    )

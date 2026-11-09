"""Record simulation results and decisions for Batch 288 in PostgreSQL."""
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
        "5737a775",
        {
            "sharpe": 0.22,
            "fitness": 0.05,
            "turnover": 0.2151,
            "sub_universe_sharpe": 0.29,
            "passes": 4,
            "fails": 3,
        },
        decision_str="REJECTED",
        reason="4 PASS / 3 FAIL. Low Sharpe 0.22, Fitness 0.05, and Weight concentration 13.98% > 10% on 1/25/2022. Realized vs implied volatility risk premium spread failed platform gates.",
        universe="TOP3000",
        neutralization="SUBINDUSTRY",
        decay=4,
        truncation=0.08,
    )

    record_candidate_result(
        "68bbc066",
        {
            "sharpe": -0.02,
            "fitness": -0.0,
            "turnover": 0.1999,
            "sub_universe_sharpe": -0.05,
            "passes": 3,
            "fails": 4,
        },
        decision_str="REJECTED",
        reason="3 PASS / 4 FAIL. Negative Sharpe -0.02, Fitness 0.0, Weight concentration 14.24% on 1/25/2022. Options term structure slope failed.",
        universe="TOP3000",
        neutralization="SUBINDUSTRY",
        decay=4,
        truncation=0.08,
    )

    record_candidate_result(
        "c28090e3",
        {
            "sharpe": -0.43,
            "fitness": -0.13,
            "turnover": 0.2693,
            "sub_universe_sharpe": -0.20,
            "passes": 3,
            "fails": 4,
        },
        decision_str="REJECTED",
        reason="3 PASS / 4 FAIL. Negative Sharpe -0.43, Fitness -0.13, Weight concentration 16.67% on 1/25/2022. Skew steepness penalty failed.",
        universe="TOP3000",
        neutralization="SUBINDUSTRY",
        decay=4,
        truncation=0.08,
    )

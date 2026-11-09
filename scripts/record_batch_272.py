"""Record simulation results and decisions for Batch 272 in PostgreSQL."""
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
        "59fcb31c",
        {
            "sharpe": 0.70,
            "fitness": 0.33,
            "turnover": 0.2012,
            "sub_universe_sharpe": 0.12,
            "passes": 4,
            "fails": 3,
        },
        decision_str="REJECTED",
        reason="4 PASS / 3 FAIL. Sharpe 0.70 is below cutoff of 1.25. Fitness 0.33 is below cutoff of 1.0. Sub-universe Sharpe 0.12 is below cutoff of 0.30.",
        universe="TOP3000",
        neutralization="SUBINDUSTRY",
        decay=5,
    )

    record_candidate_result(
        "1fb2dd72",
        {
            "sharpe": 0.62,
            "fitness": 0.36,
            "turnover": 0.1424,
            "sub_universe_sharpe": 0.37,
            "passes": 5,
            "fails": 2,
        },
        decision_str="REJECTED",
        reason="5 PASS / 2 FAIL. Sharpe 0.62 is below cutoff of 1.25. Fitness 0.36 is below cutoff of 1.0. Incompatible unit warning on add.",
        universe="TOP3000",
        neutralization="SUBINDUSTRY",
        decay=4,
    )

    record_candidate_result(
        "4d621309",
        {
            "sharpe": 0.77,
            "fitness": 0.38,
            "turnover": 0.0130,
            "sub_universe_sharpe": 0.29,
            "passes": 4,
            "fails": 3,
        },
        decision_str="REJECTED",
        reason="4 PASS / 3 FAIL. Sharpe 0.77 is below cutoff of 1.25. Fitness 0.38 is below cutoff of 1.0. Turnover 1.30% is too low. Sub-universe Sharpe 0.29 is below cutoff of 0.33.",
        universe="TOP3000",
        neutralization="SUBINDUSTRY",
        decay=4,
    )

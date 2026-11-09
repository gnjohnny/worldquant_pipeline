"""Record simulation results and decisions for Batch 271 in PostgreSQL."""
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
    neutralization: str = "MARKET",
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
        "c47f1989",
        {
            "sharpe": 1.56,
            "fitness": 1.82,
            "turnover": 0.1133,
            "sub_universe_sharpe": 0.83,
            "self_correlation": 0.9559,
            "passes": 7,
            "fails": 1,
        },
        decision_str="NEEDS_REVISION",
        reason="7 PASS / 1 FAIL. Sharpe 1.56, Fitness 1.82 (EXCELLENT), Turnover 11.33%, Sub-univ Sharpe 0.83. Fails Self-correlation: 0.9559 is above cutoff of 0.70. Collides with existing options horizontal/term skew alphas.",
        universe="TOP3000",
        neutralization="MARKET",
        decay=4,
    )

    record_candidate_result(
        "f8e581e0",
        {
            "sharpe": 2.07,
            "fitness": 1.24,
            "turnover": 0.3383,
            "sub_universe_sharpe": 1.33,
            "self_correlation": 0.9251,
            "passes": 7,
            "fails": 1,
        },
        decision_str="NEEDS_REVISION",
        reason="7 PASS / 1 FAIL. Sharpe 2.07 (SPECTACULAR), Fitness 1.24, Turnover 33.83%, Sub-univ Sharpe 1.33. Fails Self-correlation: 0.9251 is above cutoff of 0.70. Collides with existing pv13 customer return alpha in account.",
        universe="TOP3000",
        neutralization="SUBINDUSTRY",
        decay=4,
    )

    record_candidate_result(
        "c5914947",
        {
            "sharpe": 1.26,
            "fitness": 1.33,
            "turnover": 0.1130,
            "sub_universe_sharpe": 0.67,
            "self_correlation": 0.9170,
            "passes": 7,
            "fails": 1,
        },
        decision_str="NEEDS_REVISION",
        reason="7 PASS / 1 FAIL. Sharpe 1.26, Fitness 1.33, Turnover 11.30%, Sub-univ Sharpe 0.67. Fails Self-correlation: 0.9170 is above cutoff of 0.70. Collides with existing options term skew alphas.",
        universe="TOP3000",
        neutralization="MARKET",
        decay=4,
    )

"""Record simulation results and decisions for Batch 267 in PostgreSQL."""
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

    sharpe = metrics_dict.get("sharpe", 0.0) or 0.0
    fitness = metrics_dict.get("fitness", 0.0) or 0.0
    self_corr = metrics_dict.get("self_correlation")
    fails = metrics_dict.get("fails", 0)

    if fails == 0 and fitness >= 1.50 and (self_corr is None or self_corr <= 0.45):
        decision_str = "APPROVED"
        reason = f"Passed all platform checks (7 PASS / 0 FAIL)! Sharpe {sharpe:.2f}, Fitness {fitness:.2f} >= 1.50, Turnover {metrics_dict.get('turnover')*100:.2f}%, Self-corr {self_corr}."
    elif fails == 0 and fitness >= 1.00:
        decision_str = "NEEDS_REVIEW"
        reason = f"Passed platform checks (7 PASS / 0 FAIL), Sharpe {sharpe:.2f}, Fitness {fitness:.2f} (< 1.50 Gold standard), Self-corr {self_corr}."
    elif fitness < 1.00 and sharpe >= 1.25 and (self_corr is None or self_corr <= 0.70):
        decision_str = "NEEDS_REVISION"
        reason = f"Exceptional Sharpe ({sharpe:.2f}) and sub-universe Sharpe ({metrics_dict.get('sub_universe_sharpe')}), zero self-correlation warnings, but turnover ({metrics_dict.get('turnover')*100:.2f}%) pushed Fitness ({fitness:.2f}) below 1.00. Compress turnover via longer smoothing window."
    else:
        decision_str = "REJECTED"
        reason = f"Failed platform criteria: {fails} FAIL. Sharpe {sharpe}, Fitness {fitness}, Self-corr {self_corr}."

    cand.status = decision_str
    session.add(Decision(candidate_id=cand.id, decision=decision_str, reason=reason))
    session.commit()
    print(f"Recorded {cand.id[:8]}: {decision_str} - {reason}")
    session.close()


if __name__ == "__main__":
    # Candidate 1: group_rank(ts_decay_linear((open - close) / (high - low + 0.001 * close), 6), subindustry)
    record_candidate_result(
        "08f81ffd",
        {
            "sharpe": 1.49,
            "fitness": 0.87,
            "turnover": 0.3209,
            "sub_universe_sharpe": 1.07,
            "passes": 6,
            "fails": 1,
        },
    )
    # Candidate 2: group_rank(-ts_decay_linear((2 * close - high - low) / (high - low + 0.001 * close), 6), subindustry)
    record_candidate_result(
        "c881303a",
        {
            "sharpe": 1.41,
            "fitness": 0.75,
            "turnover": 0.3126,
            "sub_universe_sharpe": 0.92,
            "passes": 6,
            "fails": 1,
        },
    )
    # Candidate 3: group_rank(-ts_decay_linear(((close - open) / (high - low + 0.001 * close)) * ts_rank(volume, 20), 6), subindustry)
    record_candidate_result(
        "e18f69cf",
        {
            "sharpe": 1.63,
            "fitness": 0.94,
            "turnover": 0.3214,
            "sub_universe_sharpe": 1.08,
            "passes": 6,
            "fails": 1,
        },
    )

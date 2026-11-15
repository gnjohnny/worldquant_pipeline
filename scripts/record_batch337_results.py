import uuid
from datetime import datetime
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from worldquant_pipeline.storage.database import get_session
from worldquant_pipeline.storage.models import AlphaCandidate, Experiment, ExperimentMetric, Decision

def record_batch337():
    batch_data = [
        {
            "candidate_id": "4569d070-7749-4971-bb43-c7a0210c81a0",
            "metrics": {
                "sharpe": 1.14,
                "fitness": 0.80,
                "turnover": 0.1475,
                "sub_universe_sharpe": -0.15,
                "pass_count": 4.0,
            },
            "decision": "REJECTED",
            "reason": "4 PASS / 3 FAIL. Sharpe 1.14 < 1.25, Fitness 0.80 < 1.0, Sub-universe Sharpe -0.15 < 0.49.",
        },
        {
            "candidate_id": "3f153939-4b67-4755-afb0-d3fe429d7915",
            "metrics": {
                "sharpe": 1.52,
                "fitness": 1.08,
                "turnover": 0.1816,
                "sub_universe_sharpe": 0.94,
                "self_correlation": 0.4395,
                "pass_count": 8.0,
            },
            "decision": "NEEDS_REVIEW",
            "reason": "8 PASS. Sharpe 1.52 > 1.25, Turnover 18.16%, Self-corr 0.4395, Sub-universe 0.94. Fitness 1.08 below 1.50 Gold Consultant Track approval cutoff.",
        },
        {
            "candidate_id": "07b525d7-7cfc-4231-8890-6bfdc505c158",
            "name": "OptionSkew_DownsideExhaustion_CashflowConditioned_5D",
            "metrics": {
                "sharpe": 2.19,
                "fitness": 1.83,
                "turnover": 0.1957,
                "sub_universe_sharpe": 1.15,
                "self_correlation": 0.4900,
                "pass_count": 8.0,
            },
            "decision": "APPROVED",
            "reason": "8 PASS. Spectacular Sharpe 2.19 > 1.25, Excellent Fitness 1.83 >= 1.50/1.80 cutoff, Turnover 19.57%, Sub-universe 1.15 > 0.95, Self-correlation 0.4900 (<0.50). 100% single-line options downside skew alpha conditioned on cashflow quality.",
        },
    ]

    with get_session() as session:
        for item in batch_data:
            cand = session.get(AlphaCandidate, item["candidate_id"])
            if not cand:
                print(f"Candidate {item['candidate_id']} not found!")
                continue

            cand.status = item["decision"]

            exp_id = str(uuid.uuid4())
            exp = Experiment(
                id=exp_id,
                candidate_id=cand.id,
                universe="TOP3000",
                delay=1,
                neutralization="INDUSTRY",
                decay=4,
                truncation=0.02,
                finished_at=datetime.now(),
                status="COMPLETED",
            )
            session.add(exp)

            for metric_name, val in item["metrics"].items():
                m = ExperimentMetric(
                    id=str(uuid.uuid4()),
                    experiment_id=exp_id,
                    metric_name=metric_name,
                    metric_value=val,
                    source="BRAIN_PLATFORM",
                )
                session.add(m)

            dec = Decision(
                id=str(uuid.uuid4()),
                candidate_id=cand.id,
                decision=item["decision"],
                reason=item["reason"],
                reviewer="HUMAN_RESEARCHER",
            )
            session.add(dec)
            print(f"Recorded {cand.id[:8]} -> {item['decision']}")

        session.commit()
        print("Batch 337 results committed successfully to PostgreSQL research memory!")

if __name__ == "__main__":
    record_batch337()

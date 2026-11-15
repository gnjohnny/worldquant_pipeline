import sys
import uuid
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from worldquant_pipeline.storage.database import get_session
from worldquant_pipeline.storage.models import (
    AlphaCandidate,
    Decision,
    Experiment,
    ExperimentMetric,
)


def record_batch339():
    batch_data = [
        {
            "candidate_id": "a4119387-20f3-47c7-aa6d-e18d203baf86",
            "metrics": {
                "sharpe": 1.52,
                "fitness": 1.05,
                "turnover": 0.1884,
                "sub_universe_sharpe": 0.55,
                "pass_count": 6.0,
            },
            "decision": "REJECTED",
            "reason": "6 PASS / 1 FAIL. Sharpe 1.52 > 1.25, Fitness 1.05 > 1.0. Failed sub-universe Sharpe (0.55 < 0.66) due to illiquidity in 10-day small-cap options.",
        },
        {
            "candidate_id": "cd2ff77b-d050-4e6d-93f4-3bc7ffd276f6",
            "metrics": {
                "sharpe": 0.84,
                "fitness": 0.64,
                "turnover": 0.1088,
                "sub_universe_sharpe": 0.13,
                "pass_count": 4.0,
            },
            "decision": "REJECTED",
            "reason": "4 PASS / 3 FAIL. Low Sharpe 0.84 < 1.25, Fitness 0.64 < 1.0, Sub-universe 0.13 < 0.36.",
        },
        {
            "candidate_id": "d7ca9967-8756-4ea7-9529-cd9f853580c3",
            "metrics": {
                "sharpe": -0.40,
                "fitness": -0.23,
                "turnover": 0.1402,
                "sub_universe_sharpe": -0.29,
                "pass_count": 3.0,
            },
            "decision": "REJECTED",
            "reason": "3 PASS / 4 FAIL. Negative Sharpe -0.40, negative Fitness -0.23, weight concentration failure.",
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
        print("Batch 339 results committed to PostgreSQL!")

if __name__ == "__main__":
    record_batch339()

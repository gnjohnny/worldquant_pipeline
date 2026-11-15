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


def record_batch340():
    batch_data = [
        {
            "candidate_id": "0a3edad8-2363-4723-9a80-eabeb3129bec",
            "metrics": {
                "sharpe": 2.26,
                "fitness": 1.99,
                "turnover": 0.1843,
                "sub_universe_sharpe": 1.16,
                "self_correlation": 0.9886,
                "pass_count": 7.0,
            },
            "decision": "REJECTED",
            "reason": "7 PASS / 1 FAIL. Spectacular Sharpe 2.26 and Fitness 1.99, but Self-correlation 0.9886 failed (>0.70) due to 60D put skew colliding with newly submitted 30D put skew alpha.",
        },
        {
            "candidate_id": "50916b28-b528-4ad8-a8d3-d4fbd78f6b0a",
            "metrics": {
                "sharpe": 1.52,
                "fitness": 1.09,
                "turnover": 0.1815,
                "sub_universe_sharpe": 0.93,
                "self_correlation": 0.8738,
                "pass_count": 7.0,
            },
            "decision": "REJECTED",
            "reason": "7 PASS / 1 FAIL. Sharpe 1.52 > 1.25, but Self-correlation 0.8738 failed (>0.70) due to overlap with existing options term structure portfolio elements.",
        },
        {
            "candidate_id": "0db805e8-2f91-425f-af01-811e97b6dc87",
            "metrics": {
                "sharpe": 1.54,
                "fitness": 1.17,
                "turnover": 0.1643,
                "sub_universe_sharpe": 0.97,
                "self_correlation": 0.9026,
                "pass_count": 7.0,
            },
            "decision": "REJECTED",
            "reason": "7 PASS / 1 FAIL. Sharpe 1.54 > 1.25, but Self-correlation 0.9026 failed (>0.70) due to overlap with existing options portfolio elements.",
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
        print("Batch 340 results committed to PostgreSQL!")

if __name__ == "__main__":
    record_batch340()

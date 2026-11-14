import uuid
from datetime import datetime
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from worldquant_pipeline.storage.database import get_session
from worldquant_pipeline.storage.models import AlphaCandidate, Experiment, ExperimentMetric, Decision

def record_batch335():
    batch_data = [
        {
            "candidate_id": "d9e237c6-d7e3-41e4-8d15-eb6803fa8be0",
            "metrics": {
                "sharpe": -1.27,
                "fitness": -0.77,
                "turnover": 0.2052,
                "sub_universe_sharpe": -0.55,
                "pass_count": 4.0,
            },
            "decision": "REJECTED",
            "reason": "4 PASS / 3 FAIL. Negative Sharpe -1.27, negative Fitness -0.77, weight concentration failure.",
        },
        {
            "candidate_id": "1f065970-e092-40de-8b1b-cd1e94f50cff",
            "metrics": {
                "sharpe": 0.93,
                "fitness": 0.56,
                "turnover": 0.1709,
                "sub_universe_sharpe": 0.04,
                "pass_count": 4.0,
            },
            "decision": "REJECTED",
            "reason": "4 PASS / 3 FAIL. Positive Sharpe 0.93 but below 1.25 cutoff; Fitness 0.56 below 1.0 cutoff; Sub-universe Sharpe 0.04 below 0.40 cutoff.",
        },
        {
            "candidate_id": "b84e4fd4-8210-4d4a-85d8-4a164ba94c4a",
            "metrics": {
                "sharpe": 0.78,
                "fitness": 0.29,
                "turnover": 0.3172,
                "sub_universe_sharpe": 0.11,
                "pass_count": 4.0,
            },
            "decision": "REJECTED",
            "reason": "4 PASS / 3 FAIL. Sharpe 0.78 below 1.25 cutoff; Fitness 0.29 below 1.0 cutoff; Sub-universe Sharpe 0.11 below 0.34 cutoff.",
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
            print(f"Recorded candidate {cand.id[:8]} -> {item['decision']}")

        session.commit()
        print("Batch 335 successfully recorded in PostgreSQL!")

if __name__ == "__main__":
    record_batch335()

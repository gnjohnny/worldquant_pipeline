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


def record_batch338():
    batch_data = [
        {
            "candidate_id": "5ae4ff5b-150c-41e3-8b43-3e4c37de88d8",
            "metrics": {
                "sharpe": 1.42,
                "fitness": 1.30,
                "turnover": 0.1302,
                "sub_universe_sharpe": 0.45,
                "pass_count": 5.0,
            },
            "decision": "REJECTED",
            "reason": "5 PASS / 2 FAIL. Sharpe 1.42 > 1.25, Fitness 1.30 > 1.0, Turnover 13.02%. Failed weight concentration and sub-universe Sharpe (0.45 < 0.61).",
        },
        {
            "candidate_id": "8cf03f1b-5763-4209-bcec-c5a1614b8dde",
            "metrics": {
                "sharpe": 1.42,
                "fitness": 1.30,
                "turnover": 0.1302,
                "sub_universe_sharpe": 0.45,
                "pass_count": 5.0,
            },
            "decision": "REJECTED",
            "reason": "5 PASS / 2 FAIL. Sharpe 1.42 > 1.25, Fitness 1.30 > 1.0, Turnover 13.02%. Failed weight concentration and sub-universe Sharpe (0.45 < 0.61).",
        },
        {
            "candidate_id": "26f3b1e3-ca36-4bf5-affc-7ff8b038c72e",
            "metrics": {
                "sharpe": -0.76,
                "fitness": -0.51,
                "turnover": 0.0316,
                "sub_universe_sharpe": -0.58,
                "pass_count": 4.0,
            },
            "decision": "REJECTED",
            "reason": "4 PASS / 3 FAIL. Negative Sharpe -0.76 and negative Fitness -0.51.",
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
        print("Batch 338 results committed to PostgreSQL!")

if __name__ == "__main__":
    record_batch338()

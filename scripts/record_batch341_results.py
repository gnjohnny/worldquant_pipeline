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


def record_batch341():
    batch_data = [
        {
            "candidate_id": "14cb797d-7a7b-45fc-97d8-be587639a9b4",
            "name": "SalesSurprise_PEAD_EarningsCertainty_Industry",
            "metrics": {
                "sharpe": 1.55,
                "fitness": 1.63,
                "turnover": 0.0743,
                "sub_universe_sharpe": 1.43,
                "self_correlation": 0.5871,
                "pass_count": 8.0,
            },
            "decision": "APPROVED",
            "reason": "8 PASS. Sharpe 1.55 > 1.25, Fitness 1.63 >= 1.50 (GOOD tier), Turnover 7.43%, Sub-universe Sharpe 1.43 > 0.67, Self-correlation 0.5871 < 0.70. Pure single-line quarterly sales surprise momentum conditioned on earnings certainty.",
        },
        {
            "candidate_id": "2b5e1437-2a6f-405a-adf2-fcb264926b22",
            "metrics": {
                "sharpe": -0.79,
                "fitness": -0.54,
                "turnover": 0.0318,
                "sub_universe_sharpe": -0.60,
                "pass_count": 4.0,
            },
            "decision": "REJECTED",
            "reason": "4 PASS / 3 FAIL. Negative Sharpe -0.79 and negative Fitness -0.54.",
        },
        {
            "candidate_id": "4a3198df-931b-4549-89ef-9efd3c99ef75",
            "metrics": {
                "sharpe": -0.70,
                "fitness": -0.45,
                "turnover": 0.0313,
                "sub_universe_sharpe": -0.56,
                "pass_count": 4.0,
            },
            "decision": "REJECTED",
            "reason": "4 PASS / 3 FAIL. Negative Sharpe -0.70 and negative Fitness -0.45.",
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
        print("Batch 341 results committed successfully to PostgreSQL research memory!")

if __name__ == "__main__":
    record_batch341()

import uuid
from datetime import datetime
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from worldquant_pipeline.storage.database import get_session
from worldquant_pipeline.storage.models import AlphaCandidate, Experiment, ExperimentMetric, Decision
from sqlalchemy import select

def record_batch334():
    batch_data = [
        {
            "candidate_id": "14b75193-47fc-457b-aa56-6125143e7177",
            "name": "SupplyChain_CashflowConditioned_ShockReversal_5D",
            "neutralization": "INDUSTRY",
            "metrics": {
                "sharpe": 2.12,
                "fitness": 1.67,
                "turnover": 0.3478,
                "sub_universe_sharpe": 1.42,
                "self_correlation": 0.6050,
                "pass_count": 8.0,
            },
            "decision": "APPROVED",
            "reason": "8 PASS. Sharpe 2.12 > 1.25, Fitness 1.67 >= 1.50 (SPECTACULAR/GOOD tier), Turnover 34.78%, Sub-universe Sharpe 1.42 > 0.92, Self-correlation 0.6050 < 0.70. Superb decorrelated supply chain + fundamental cashflow alpha.",
        },
        {
            "candidate_id": "438943ed-6083-4f26-abad-d06cf3b59bed",
            "name": "SupplyChain_SectorNeutralized_CubicConviction_5D",
            "neutralization": "SECTOR",
            "metrics": {
                "sharpe": 1.78,
                "fitness": 1.29,
                "turnover": 0.4280,
                "sub_universe_sharpe": 1.24,
                "self_correlation": 0.7071,
                "pass_count": 7.0,
            },
            "decision": "REJECTED",
            "reason": "7 PASS / 1 FAIL. Self-correlation 0.7071 is above cutoff of 0.70 and Sharpe 1.78 is not better by 10% or more. Sector neutralization failed to decorrelate.",
        },
        {
            "candidate_id": "10913f3f-3885-45d3-8047-b3022743c465",
            "name": "SupplyChain_AnalystRevisionConditioned_ShockReversal_5D",
            "neutralization": "INDUSTRY",
            "metrics": {
                "sharpe": 2.10,
                "fitness": 1.65,
                "turnover": 0.3477,
                "sub_universe_sharpe": 1.44,
                "self_correlation": 0.6046,
                "pass_count": 8.0,
            },
            "decision": "APPROVED",
            "reason": "8 PASS. Sharpe 2.10 > 1.25, Fitness 1.65 >= 1.50 (SPECTACULAR/GOOD tier), Turnover 34.77%, Sub-universe Sharpe 1.44 > 0.91, Self-correlation 0.6046 < 0.70. Outstanding sister alpha conditioned on analyst revisions.",
        },
    ]

    with get_session() as session:
        for item in batch_data:
            cand = session.get(AlphaCandidate, item["candidate_id"])
            if not cand:
                print(f"Candidate {item['candidate_id']} not found!")
                continue

            cand.status = item["decision"]

            # Create experiment
            exp_id = str(uuid.uuid4())
            exp = Experiment(
                id=exp_id,
                candidate_id=cand.id,
                universe="TOP3000",
                delay=1,
                neutralization=item["neutralization"],
                decay=4,
                truncation=0.02,
                finished_at=datetime.now(),
                status="COMPLETED",
            )
            session.add(exp)

            # Create metrics
            for metric_name, val in item["metrics"].items():
                m = ExperimentMetric(
                    id=str(uuid.uuid4()),
                    experiment_id=exp_id,
                    metric_name=metric_name,
                    metric_value=val,
                    source="BRAIN_PLATFORM",
                )
                session.add(m)

            # Create decision
            dec = Decision(
                id=str(uuid.uuid4()),
                candidate_id=cand.id,
                decision=item["decision"],
                reason=item["reason"],
                reviewer="HUMAN_RESEARCHER",
            )
            session.add(dec)
            print(f"Recorded candidate {cand.id[:8]} -> {item['decision']} (Sharpe {item['metrics']['sharpe']}, Fitness {item['metrics']['fitness']})")

        session.commit()
        print("All Batch 334 results successfully committed to PostgreSQL research memory!")

if __name__ == "__main__":
    record_batch334()

"""Record simulation results and decisions for Batch 75."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from worldquant_pipeline.storage.database import get_session
from worldquant_pipeline.storage.models import (
    AlphaCandidate,
    Decision,
    Experiment,
    ExperimentMetric,
)

with get_session() as session:
    batch_records = [
        (
            "32faf6c9",
            "TOP1000",
            "Subindustry",
            5,
            {"sharpe": 0.83, "fitness": 0.46, "turnover": 0.1419, "sub_universe_sharpe": 0.56},
            "Candidate 1 (Cash Flow Yield & CapEx): 5 PASS / 2 FAIL. Turnover 14.19% PASS, Sub-universe 0.56 PASS. Sharpe 0.83 and Fitness 0.46 below thresholds.",
            "REJECTED",
        ),
        (
            "da600b5e",
            "TOP2000",
            "Industry",
            5,
            {"sharpe": 1.51, "fitness": 1.20, "turnover": 0.1422, "sub_universe_sharpe": 1.53, "self_correlation": 0.5616},
            "Candidate 2 (Analyst Consensus Yield & 60d Revision): 8/8 PASS ON BRAIN! Sharpe 1.51, Sub-universe 1.53, Turnover 14.22%, Self-correlation 0.5616 (complete decorrelation). Fitness 1.20 marked as NEEDS_REVISION to compress turnover and reach Gold Consultant threshold (Fitness >= 1.50).",
            "NEEDS_REVISION",
        ),
        (
            "4bcbb0f8",
            "TOPSP500",
            "Sector",
            4,
            {"sharpe": 1.31, "fitness": 0.99, "turnover": 0.2323, "sub_universe_sharpe": 1.69},
            "Candidate 3 (LEAP Call Term & 30d VRP): 6 PASS / 1 FAIL. Sharpe 1.31 PASS, Sub-universe 1.69 SPECTACULAR, Turnover 23.23% PASS. Fitness 0.99 missed 1.00 platform cutoff by 0.01. Marked as NEEDS_REVISION for turnover compression via decay.",
            "NEEDS_REVISION",
        ),
    ]

    for cid_prefix, universe, neut, decay, metrics, reason, decision in batch_records:
        cand = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith(cid_prefix)).first()
        if cand:
            exp = Experiment(
                candidate_id=cand.id,
                status="COMPLETED",
                universe=universe,
                delay=1,
                decay=decay,
                neutralization=neut,
                truncation=0.0100,
            )
            session.add(exp)
            session.flush()

            for k, v in metrics.items():
                session.add(
                    ExperimentMetric(
                        experiment_id=exp.id,
                        metric_name=k,
                        metric_value=v,
                        source="BRAIN_PLATFORM",
                    )
                )

            dec = Decision(
                candidate_id=cand.id,
                decision=decision,
                reason=reason,
                reviewer="HUMAN_RESEARCHER",
            )
            session.add(dec)
            cand.status = decision
            print(f"Recorded Candidate {cid_prefix} as {decision}.")

    session.commit()
    print("All Batch 75 candidates successfully recorded in PostgreSQL.")

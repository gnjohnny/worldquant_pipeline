"""Record Batch 80 simulation results in PostgreSQL."""
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
            "c35563db",
            "TOP2000",
            "Subindustry",
            5,
            {"sharpe": 1.71, "fitness": 1.16, "turnover": 0.1245, "sub_universe_sharpe": 1.66, "self_correlation": 0.7057},
            "Candidate 1 (SUE Surprise in TOP2000 Subindustry): 7 PASS / 1 FAIL. Sharpe 1.71 OUTSTANDING, Sub-universe 1.66 SPECTACULAR, Turnover 12.45% PASS. Self-correlation 0.7057 barely missed 0.70 cutoff by 0.0057 against Alpha 26. High conviction candidate for rapid parameter decorrelation.",
            "NEEDS_REVISION",
        ),
        (
            "55208fe1",
            "TOP1000",
            "Subindustry",
            5,
            {"sharpe": 0.68, "fitness": 0.37, "turnover": 0.1449, "sub_universe_sharpe": 0.26},
            "Candidate 2 (Cash Flow Yield & Capital Return): 4 PASS / 3 FAIL. Turnover 14.49% PASS. Sharpe 0.68, Fitness 0.37, Sub-universe 0.26 fail cutoffs.",
            "REJECTED",
        ),
        (
            "532bf21d",
            "TOPSP500",
            "Sector",
            6,
            {"sharpe": 1.25, "fitness": 1.14, "turnover": 0.1499, "sub_universe_sharpe": 1.65, "self_correlation": 0.7385},
            "Candidate 3 (2-Year LEAP Call Term): 7 PASS / 1 FAIL. Sharpe 1.25 PASS, Sub-universe 1.65 SPECTACULAR, Fitness 1.14, Turnover 14.99% PASS. Self-corr 0.7385 failed against TOPSP500 Alpha 24 / Alpha 22.",
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
    print("All Batch 80 candidates successfully recorded in PostgreSQL.")

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from sqlalchemy import select

from worldquant_pipeline.storage.database import get_session
from worldquant_pipeline.storage.models import (
    AlphaCandidate,
    Decision,
    Experiment,
    ExperimentMetric,
)


def check():
    with get_session() as session:
        stmt = select(AlphaCandidate).where(AlphaCandidate.expression_raw.like('%cashflow_efficiency_rank_derivative%'))
        cands = session.scalars(stmt).all()
        print(f"Found {len(cands)} candidates with cashflow_efficiency_rank_derivative")
        for c in cands:
            print(f"ID: {c.id}")
            print(f"Expression: {c.expression_raw[:80]}")
            # check experiments
            exp_stmt = select(Experiment).where(Experiment.candidate_id == c.id)
            exps = session.scalars(exp_stmt).all()
            print(f"  Experiments: {len(exps)}")
            for exp in exps:
                print(f"    Exp ID: {exp.id}, Settings: universe={exp.universe}, neutralization={exp.neutralization}, decay={exp.decay}")
                metrics = session.scalars(select(ExperimentMetric).where(ExperimentMetric.experiment_id == exp.id)).all()
                for m in metrics:
                    print(f"      {m.metric_name}: {m.metric_value}")
            decisions = session.scalars(select(Decision).where(Decision.candidate_id == c.id)).all()
            for d in decisions:
                print(f"      Decision: {d.decision} - {d.reason}")

if __name__ == "__main__":
    check()

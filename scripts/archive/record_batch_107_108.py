"""Record Batch 107 and Batch 108 simulation results and decisions."""
import sys

sys.path.insert(0, "src")
from worldquant_pipeline.storage.database import get_session
from worldquant_pipeline.storage.models import (
    AlphaCandidate,
    Decision,
    Experiment,
    ExperimentMetric,
)


def record_results():
    session = get_session()
    
    # 1. Batch 107
    # Candidate 1: 322d302b
    c1_107 = session.query(AlphaCandidate).filter(AlphaCandidate.id.like("322d302b%")).first()
    if c1_107:
        c1_107.status = "REJECTED"
        exp1 = Experiment(
            candidate_id=c1_107.id,
            universe="TOP1000",
            neutralization="Sector",
            decay=4,
            truncation=0.01
        )
        session.add(exp1)
        session.flush()
        session.add_all([
            ExperimentMetric(experiment_id=exp1.id, metric_name="sharpe", metric_value=1.24),
            ExperimentMetric(experiment_id=exp1.id, metric_name="fitness", metric_value=1.19),
            ExperimentMetric(experiment_id=exp1.id, metric_name="turnover", metric_value=0.1226),
            ExperimentMetric(experiment_id=exp1.id, metric_name="subuniverse_sharpe", metric_value=0.99),
        ])
        session.add(Decision(
            candidate_id=c1_107.id,
            decision="REJECTED",
            reason="Sharpe 1.24 < 1.25 cutoff, Fitness 1.19 < 1.50 cutoff."
        ))

    # Candidate 2: 789a282a
    c2_107 = session.query(AlphaCandidate).filter(AlphaCandidate.id.like("789a282a%")).first()
    if c2_107:
        c2_107.status = "REJECTED"
        exp2 = Experiment(
            candidate_id=c2_107.id,
            universe="TOP1000",
            neutralization="Sector",
            decay=4,
            truncation=0.01
        )
        session.add(exp2)
        session.flush()
        session.add_all([
            ExperimentMetric(experiment_id=exp2.id, metric_name="sharpe", metric_value=1.13),
            ExperimentMetric(experiment_id=exp2.id, metric_name="fitness", metric_value=1.10),
            ExperimentMetric(experiment_id=exp2.id, metric_name="turnover", metric_value=0.1385),
            ExperimentMetric(experiment_id=exp2.id, metric_name="subuniverse_sharpe", metric_value=1.11),
        ])
        session.add(Decision(
            candidate_id=c2_107.id,
            decision="REJECTED",
            reason="Sharpe 1.13 < 1.25 cutoff, Fitness 1.10 < 1.50 cutoff."
        ))

    # Candidate 3: 61568b7f
    c3_107 = session.query(AlphaCandidate).filter(AlphaCandidate.id.like("61568b7f%")).first()
    if c3_107:
        c3_107.status = "REJECTED"
        exp3 = Experiment(
            candidate_id=c3_107.id,
            universe="TOP1000",
            neutralization="Sector",
            decay=4,
            truncation=0.01
        )
        session.add(exp3)
        session.flush()
        session.add_all([
            ExperimentMetric(experiment_id=exp3.id, metric_name="sharpe", metric_value=0.96),
            ExperimentMetric(experiment_id=exp3.id, metric_name="fitness", metric_value=0.77),
            ExperimentMetric(experiment_id=exp3.id, metric_name="turnover", metric_value=0.1445),
            ExperimentMetric(experiment_id=exp3.id, metric_name="subuniverse_sharpe", metric_value=0.51),
        ])
        session.add(Decision(
            candidate_id=c3_107.id,
            decision="REJECTED",
            reason="Sharpe 0.96 < 1.25 cutoff, Fitness 0.77 < 1.0 cutoff."
        ))

    # 2. Batch 108
    # Candidate 1: 78f7d1cf
    c1_108 = session.query(AlphaCandidate).filter(AlphaCandidate.id.like("78f7d1cf%")).first()
    if c1_108:
        c1_108.status = "REJECTED"
        exp1_108 = Experiment(
            candidate_id=c1_108.id,
            universe="TOP3000",
            neutralization="Market",
            decay=4,
            truncation=0.01
        )
        session.add(exp1_108)
        session.flush()
        session.add_all([
            ExperimentMetric(experiment_id=exp1_108.id, metric_name="sharpe", metric_value=0.41),
            ExperimentMetric(experiment_id=exp1_108.id, metric_name="fitness", metric_value=0.15),
            ExperimentMetric(experiment_id=exp1_108.id, metric_name="turnover", metric_value=0.2679),
            ExperimentMetric(experiment_id=exp1_108.id, metric_name="subuniverse_sharpe", metric_value=0.33),
        ])
        session.add(Decision(
            candidate_id=c1_108.id,
            decision="REJECTED",
            reason="Sharpe 0.41 < 1.25 cutoff, Fitness 0.15 < 1.0 cutoff."
        ))

    # Candidate 2: 8dfd0baa
    c2_108 = session.query(AlphaCandidate).filter(AlphaCandidate.id.like("8dfd0baa%")).first()
    if c2_108:
        c2_108.status = "REJECTED"
        exp2_108 = Experiment(
            candidate_id=c2_108.id,
            universe="TOP3000",
            neutralization="Market",
            decay=4,
            truncation=0.01
        )
        session.add(exp2_108)
        session.flush()
        session.add_all([
            ExperimentMetric(experiment_id=exp2_108.id, metric_name="sharpe", metric_value=0.40),
            ExperimentMetric(experiment_id=exp2_108.id, metric_name="fitness", metric_value=0.15),
            ExperimentMetric(experiment_id=exp2_108.id, metric_name="turnover", metric_value=0.2671),
            ExperimentMetric(experiment_id=exp2_108.id, metric_name="subuniverse_sharpe", metric_value=0.34),
        ])
        session.add(Decision(
            candidate_id=c2_108.id,
            decision="REJECTED",
            reason="Sharpe 0.40 < 1.25 cutoff, Fitness 0.15 < 1.0 cutoff."
        ))

    session.commit()
    print("Batch 107 and 108 experiments and decisions successfully recorded!")

if __name__ == "__main__":
    record_results()

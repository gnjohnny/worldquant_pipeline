import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from worldquant_pipeline.storage.database import get_session
from worldquant_pipeline.storage.models import (
    AlphaCandidate,
    Decision,
    Experiment,
)

with get_session() as session:
    cands = [
        ("f9c1e65d", "Candidate 1 (anl4 Cash Flow Yield) failed simulation checks on WorldQuant BRAIN."),
        ("33a4e641", "Candidate 2 (pv13 Inverted Decay) failed simulation checks on WorldQuant BRAIN."),
        ("fe797035", "Candidate 3 (option8 Term Slope) failed simulation checks on WorldQuant BRAIN."),
    ]
    for cid_prefix, reason in cands:
        c = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith(cid_prefix)).first()
        if c:
            exp = Experiment(
                candidate_id=c.id,
                status="FAILED",
                universe="TOP3000",
                delay=1,
                decay=4,
                neutralization="Subindustry",
                truncation=0.0100,
            )
            session.add(exp)
            session.flush()
            dec = Decision(
                candidate_id=c.id,
                decision="REJECTED",
                reason=reason,
                reviewer="HUMAN_RESEARCHER",
            )
            session.add(dec)
            c.status = "REJECTED"
            print(f"Recorded Candidate {cid_prefix} as REJECTED.")

    session.commit()
    print("Batch 48 failure records saved to PostgreSQL.")

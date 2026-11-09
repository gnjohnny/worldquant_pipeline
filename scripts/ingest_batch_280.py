"""Ingest and register Batch 280 into PostgreSQL."""
import json
import sys

sys.path.insert(0, "src")
from worldquant_pipeline.hypotheses.importer import HypothesisImporter
from worldquant_pipeline.storage.database import get_session

if __name__ == "__main__":
    with open("data/batch_280_orthogonal_risk_and_breakeven_triplet.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    session = get_session()
    importer = HypothesisImporter(session)
    report = importer.ingest_data(data)

    print("Batch 280 Ingestion Report:")
    print(f"  Total hypotheses: {report.total_hypotheses}")
    print(f"  Total candidates: {report.total_candidates}")
    print(f"  Valid candidates: {report.valid_candidates}")
    print(f"  Duplicates: {report.duplicates}")
    print(f"  Syntax errors: {report.syntax_errors}")
    if report.errors:
        print("  Errors:")
        for err in report.errors:
            print(f"    - {err}")
    print("\nRegistered Candidates:")
    for c in report.registered_candidates:
        print(f"  ID: {c['id'][:8]} | Risk: {c['correlation_risk']} | Expression: {c['expression'][:75]}")

    session.close()

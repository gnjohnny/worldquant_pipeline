import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from worldquant_pipeline.storage.database import get_session
from worldquant_pipeline.hypotheses.importer import HypothesisImporter

def main():
    batch_path = Path("data/batch_336_options_surface_conditioning.json")
    with open(batch_path) as f:
        data = json.load(f)

    with get_session() as session:
        importer = HypothesisImporter(session)
        report = importer.ingest_data(data)
        print(f"Batch 336 Ingestion: total={report.total_candidates}, valid={report.valid_candidates}, errors={len(report.errors)}")
        for r in report.registered_candidates:
            print(f"  Registered ID: {r['id']}")
            print(f"    Expr: {r['expression'][:70]}")
        for err in report.errors:
            print(f"  Error: {err}")

if __name__ == "__main__":
    main()

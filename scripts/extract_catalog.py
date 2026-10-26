import json
import os
import re
import sys

from pypdf import PdfReader

sys.stdout.reconfigure(encoding='utf-8')

quant_data_dir = r"C:\Users\Johnny\Agy_test\worldquant_pipeline\Quant_data"
files = [f for f in os.listdir(quant_data_dir) if f.endswith(".pdf")]
files.sort()

# Line-by-line parser matching each table row:
# e.g.: close Daily close price Matrix 100% 100% 6208 0
# or multiline field names

def parse_pdf_fields(text):
    # Regex matching: field_name, description, type, instrument_cov, date_cov, alphas, etc.
    # Note: field_name might be broken across lines or simple word
    pattern = re.compile(
        r'([a-zA-Z0-9_\n]+?)\s+'                         # field name (can have newline inside)
        r'([A-Za-z0-9,.\(\)\/–—\'\"%:;\s\-]+?)\s+'       # description
        r'(Matrix|Vector|Group|Symbol|Universe)\s+'      # type
        r'(\d+%\s+\d+%)\s+'                             # instrument & date coverage
        r'(\d+)',                                       # alpha count
        re.MULTILINE
    )
    results = {}
    for match in pattern.finditer(text):
        fname = match.group(1).replace("\n", "").replace(" ", "").strip()
        desc = " ".join(match.group(2).split())
        ftype = match.group(3)
        cov = match.group(4)
        alphas = match.group(5)
        
        # Filter out table header or spurious matches
        if fname and len(fname) > 1 and not fname.startswith("Field") and not fname.startswith("Name"):
            results[fname] = {
                "name": fname,
                "description": desc,
                "type": ftype,
                "coverage": cov,
                "alphas": alphas
            }
    return results

catalog = {}
for fname in files:
    fpath = os.path.join(quant_data_dir, fname)
    reader = PdfReader(fpath)
    full_pdf_text = "\n".join([p.extract_text() or "" for p in reader.pages])
    
    url_m = re.search(r"platform\.worldquantbrain\.com/data/data-sets/([^?]+)", full_pdf_text)
    ds_id = url_m.group(1) if url_m else "unknown"
    title_m = re.search(r"Data > Datasets > ([^\n]+)", full_pdf_text)
    title = title_m.group(1).strip() if title_m else fname
    
    if ds_id not in catalog:
        catalog[ds_id] = {
            "title": title,
            "dataset_id": ds_id,
            "files": [],
            "fields": {}
        }
    catalog[ds_id]["files"].append(fname)
    
    parsed = parse_pdf_fields(full_pdf_text)
    catalog[ds_id]["fields"].update(parsed)

for ds_id, data in catalog.items():
    print(f"=== {data['title']} ({ds_id}) ===")
    print(f"Total fields: {len(data['fields'])} across {len(data['files'])} files")
    for name, info in list(data["fields"].items())[:8]:
        print(f"  * {name} ({info['type']}, {info['coverage']}): {info['description'][:70]}...")

out_file = r"C:\Users\Johnny\Agy_test\worldquant_pipeline\docs\brain_data_catalog.json"
with open(out_file, "w", encoding="utf-8") as f:
    json.dump({k: {
        "title": v["title"],
        "dataset_id": v["dataset_id"],
        "files_count": len(v["files"]),
        "fields_count": len(v["fields"]),
        "fields": v["fields"]
    } for k, v in catalog.items()}, f, indent=2)

print(f"\nWritten to {out_file}")

import json
import os
import re

from pypdf import PdfReader

quant_data_dir = r"C:\Users\Johnny\Agy_test\worldquant_pipeline\Quant_data"
files = [f for f in os.listdir(quant_data_dir) if f.endswith(".pdf")]
files.sort()

dataset_info = {}

for fname in files:
    fpath = os.path.join(quant_data_dir, fname)
    reader = PdfReader(fpath)
    text = "\n".join([p.extract_text() or "" for p in reader.pages])
    
    # find dataset id from url
    url_match = re.search(r"platform\.worldquantbrain\.com/data/data-sets/([^?]+)", text)
    ds_id = url_match.group(1) if url_match else "unknown"
    
    # find title
    title_match = re.search(r"Data > Datasets > ([^\n]+)", text)
    title = title_match.group(1).strip() if title_match else fname
    
    if ds_id not in dataset_info:
        dataset_info[ds_id] = {"title": title, "files": [], "full_text": []}
    dataset_info[ds_id]["files"].append(fname)
    dataset_info[ds_id]["full_text"].append(text)

print(f"Total distinct datasets found: {len(dataset_info)}")
for ds_id, data in dataset_info.items():
    print(f"Dataset: {data['title']} | ID: {ds_id} | Files: {len(data['files'])}")

with open("quant_datasets_summary.json", "w", encoding="utf-8") as f:
    json.dump({ds_id: {"title": d["title"], "files": d["files"]} for ds_id, d in dataset_info.items()}, f, indent=2)

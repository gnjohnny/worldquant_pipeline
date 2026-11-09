import json

with open('docs/brain_data_catalog.json', encoding='utf-8') as f:
    cat = json.load(f)
print(f"Total datasets in brain_data_catalog.json: {len(cat)}")
for ds_id, ds in cat.items():
    print("\n==========================================")
    print(f"Dataset: {ds['title']} (ID: {ds_id}) - {len(ds['fields'])} fields")
    print("==========================================")
    for fname, fmeta in sorted(ds['fields'].items()):
        print(f"  {fname:<35} | {fmeta['type']:<8} | {fmeta['coverage']:<12} | {fmeta['description'][:80]}")

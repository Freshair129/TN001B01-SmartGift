import json, pathlib, sys

def main():
    path = pathlib.Path(r"data-pipeline/02_prepared/smartgift_catalog_master.json")
    try:
        data = json.load(open(path, encoding="utf-8"))
    except Exception as e:
        print(f"Failed to load JSON: {e}")
        sys.exit(1)
    updated = 0
    for p in data.get("canonical_products", []):
        if "dimensions_cm" not in p:
            p["dimensions_cm"] = {"length": 10.0, "width": 10.0, "height": 10.0}
            updated += 1
        if "unit_weight_kg" not in p:
            p["unit_weight_kg"] = 0.5
            updated += 1
    json.dump(data, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"Added missing fields to {updated} entries.")

if __name__ == "__main__":
    main()

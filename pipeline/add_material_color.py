import json, pathlib, sys

def main():
    # Resolve the path to the master catalog JSON relative to this script location
    base_dir = pathlib.Path(__file__).resolve().parents[1]
    json_path = base_dir / "data-pipeline" / "02_prepared" / "smartgift_catalog_master.json"
    try:
        data = json.load(open(json_path, encoding="utf-8"))
    except Exception as e:
        print(f"Failed to load JSON: {e}")
        sys.exit(1)
    updated = 0
    for product in data.get("canonical_products", []):
        if "material" not in product:
            product["material"] = "generic"
            updated += 1
        if "color" not in product:
            product["color"] = "unspecified"
            updated += 1
    json.dump(data, open(json_path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"Added missing material/color to {updated} entries.")

if __name__ == "__main__":
    main()

"""
SmartGift Product & Catalog Manifest Generator
Generates:
  1. SHA-256 Data Integrity Hashes for all catalog sub-datasets
  2. Multi-File Category Slices under public/data/categories/<slug>.json
  3. Product Image Asset Path Index for Frontend & Web Applications
  4. Public Web Manifest (public/data/product_manifest.json) & Audit Log
"""

import os
import sys
import json
import hashlib
from datetime import datetime, timezone
from typing import Dict, Any, List

sys.stdout.reconfigure(encoding='utf-8')

MASTER_CATALOG_PATH = "data-pipeline/02_prepared/smartgift_catalog_master.json"
PRICELIST_MASTER_PATH = "data-pipeline/02_prepared/pricelist_master.json"
FACTORY_COSTS_PATH = "data-pipeline/02_prepared/factory_costs.json"
CATALOG_MEDIA_PATH = "public/data/catalog_media.json"
PRICELIST_PUBLIC_PATH = "public/data/pricelist_public.json"

PUBLIC_DATA_DIR = "public/data"
CATEGORIES_DIR = "public/data/categories"
CATALOG_MEDIA_ASSETS_DIR = "public/assets/catalog-media"
PUBLIC_MANIFEST_PATH = "public/data/product_manifest.json"
AUDIT_MANIFEST_PATH = "data-pipeline/04_review_reports/product_manifest_audit.json"

DEFAULT_FALLBACK_IMAGE = "/assets/catalog-media/hero-fxd66-3-generated.webp"

def compute_file_sha256(filepath: str) -> str:
    if not os.path.exists(filepath):
        return ""
    with open(filepath, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()

def compute_content_sha256(data: Any) -> str:
    canonical_str = json.dumps(data, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(canonical_str.encode("utf-8")).hexdigest()

class ProductManifestGenerator:
    def __init__(self):
        os.makedirs(PUBLIC_DATA_DIR, exist_ok=True)
        os.makedirs(CATEGORIES_DIR, exist_ok=True)
        os.makedirs(os.path.dirname(AUDIT_MANIFEST_PATH), exist_ok=True)
        
        self.master_data = self._load_json(MASTER_CATALOG_PATH)
        self.catalog_media = self._load_json(CATALOG_MEDIA_PATH)
        self.pricelist_public = self._load_json(PRICELIST_PUBLIC_PATH)

    def _load_json(self, path: str) -> Dict[str, Any]:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def compute_integrity_hashes(self) -> Dict[str, Dict[str, Any]]:
        target_files = {
            "smartgift_catalog_master": MASTER_CATALOG_PATH,
            "pricelist_master": PRICELIST_MASTER_PATH,
            "factory_costs": FACTORY_COSTS_PATH,
            "catalog_media": CATALOG_MEDIA_PATH,
            "pricelist_public": PRICELIST_PUBLIC_PATH
        }
        
        hashes = {}
        for key, filepath in target_files.items():
            if os.path.exists(filepath):
                hashes[key] = {
                    "path": filepath,
                    "size_bytes": os.path.getsize(filepath),
                    "sha256": compute_file_sha256(filepath)
                }
            else:
                hashes[key] = {
                    "path": filepath,
                    "size_bytes": 0,
                    "sha256": ""
                }
        return hashes

    def build_product_image_index(self) -> Dict[str, Dict[str, Any]]:
        """Maps product/offer code to image path, title, visual status and fallback details."""
        index = {}

        # 1. Map Hero Image
        hero = self.catalog_media.get("hero", {})
        if hero and "code" in hero:
            index[hero["code"]] = {
                "code": hero["code"],
                "title": hero.get("title", ""),
                "image_url": hero.get("image", DEFAULT_FALLBACK_IMAGE),
                "visual_status": hero.get("visual_status", "hero_creative_proof"),
                "is_hero": True,
                "generated_from_catalog": hero.get("generated_from_catalog", True)
            }

        # 2. Map Gift Sets
        for item in self.catalog_media.get("sets", []):
            code = item.get("code")
            if code:
                index[code] = {
                    "code": code,
                    "title": item.get("title", ""),
                    "image_url": item.get("image", DEFAULT_FALLBACK_IMAGE),
                    "visual_status": item.get("visual_status", "source_matched_creative_proof"),
                    "source_label": item.get("source_label", ""),
                    "is_hero": False,
                    "generated_from_catalog": item.get("generated_from_catalog", True)
                }

        # 3. Map Individual Products from catalog_media
        for item in self.catalog_media.get("products", []):
            code = item.get("code")
            if code:
                index[code] = {
                    "code": code,
                    "title": item.get("title", ""),
                    "image_url": item.get("image", DEFAULT_FALLBACK_IMAGE),
                    "visual_status": item.get("visual_status", "source-photo"),
                    "source_label": item.get("source_label", ""),
                    "is_hero": False,
                    "generated_from_catalog": item.get("generated_from_catalog", False)
                }

        # 4. Map Canonical Products from master catalog
        for p in self.master_data.get("canonical_products", []):
            code = p.get("code")
            if code and code not in index:
                # Attempt matching webp filename under assets
                clean_code = code.lower().replace("-", "_").replace(" ", "")
                candidate_filename = f"product-{clean_code}.webp"
                candidate_path = os.path.join(CATALOG_MEDIA_ASSETS_DIR, candidate_filename)
                
                if os.path.exists(candidate_path):
                    image_url = f"/assets/catalog-media/{candidate_filename}"
                    status = "source-photo"
                else:
                    image_url = DEFAULT_FALLBACK_IMAGE
                    status = "fallback-placeholder"
                
                index[code] = {
                    "code": code,
                    "title": p.get("name_th", p.get("name_en", code)),
                    "image_url": image_url,
                    "visual_status": status,
                    "is_hero": False,
                    "generated_from_catalog": False
                }

        return index

    def build_multi_file_category_slices(self, image_index: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Splits products into category JSON files under public/data/categories/<slug>.json."""
        categories = self.master_data.get("top_level_categories", [])
        canonical_products = self.master_data.get("canonical_products", [])
        
        category_index_list = []

        for cat in categories:
            slug = cat.get("slug")
            if not slug:
                continue

            # Filter products matching this category
            cat_products = [
                p for p in canonical_products
                if p.get("category_slug") == slug or cat.get("name_en", "") in p.get("category", "")
            ]

            # Attach image paths to category items
            enriched_products = []
            for p in cat_products:
                p_copy = dict(p)
                code = p_copy.get("code")
                p_copy["image_info"] = image_index.get(code, {
                    "image_url": DEFAULT_FALLBACK_IMAGE,
                    "visual_status": "fallback-placeholder"
                })
                enriched_products.append(p_copy)

            category_data = {
                "category_meta": cat,
                "total_products": len(enriched_products),
                "products": enriched_products
            }

            slice_filename = f"{slug}.json"
            slice_filepath = os.path.join(CATEGORIES_DIR, slice_filename)
            
            with open(slice_filepath, "w", encoding="utf-8") as f:
                json.dump(category_data, f, ensure_ascii=False, indent=2)

            sha256_hash = compute_content_sha256(category_data)
            category_index_list.append({
                "slug": slug,
                "name_th": cat.get("name_th"),
                "name_en": cat.get("name_en"),
                "endpoint_url": f"/data/categories/{slice_filename}",
                "total_products": len(enriched_products),
                "sha256": sha256_hash
            })

        return category_index_list

    def generate_manifest(self) -> Dict[str, Any]:
        print("🔨 Generating SmartGift Product & Catalog Manifest...")
        
        integrity_hashes = self.compute_integrity_hashes()
        image_index = self.build_product_image_index()
        category_slices = self.build_multi_file_category_slices(image_index)

        now_utc = datetime.now(timezone.utc)
        date_tag = now_utc.strftime("%Y.%m.%d")
        
        master_sha = integrity_hashes.get("smartgift_catalog_master", {}).get("sha256", "")[:8]
        catalog_version = f"v1.3.0-{date_tag}-{master_sha}"

        manifest = {
            "schema_version": "1.3.0",
            "tenant_id": "Org-EtohGroup",
            "business_id": "SmartGift",
            "operating_entity": "บริษัท เทราบิส จำกัด (Therabis Co., Ltd.)",
            "catalog_version": catalog_version,
            "generated_at": now_utc.isoformat(),
            "data_integrity_hashes": integrity_hashes,
            "multi_file_index": category_slices,
            "product_image_index": image_index,
            "summary_stats": {
                "total_categories": len(category_slices),
                "total_canonical_products": len(self.master_data.get("canonical_products", [])),
                "total_catalog_offers": len(self.master_data.get("catalog_offers", [])),
                "total_indexed_images": len(image_index)
            }
        }

        # Write Web-facing Manifest
        with open(PUBLIC_MANIFEST_PATH, "w", encoding="utf-8") as f:
            json.dump(manifest, f, ensure_ascii=False, indent=2)

        # Write Audit Manifest Report
        with open(AUDIT_MANIFEST_PATH, "w", encoding="utf-8") as f:
            json.dump(manifest, f, ensure_ascii=False, indent=2)

        print(f"✅ Product Manifest published to '{PUBLIC_MANIFEST_PATH}'")
        print(f"✅ Audit Manifest saved to '{AUDIT_MANIFEST_PATH}'")
        print(f"📊 Categories Sliced: {len(category_slices)}")
        print(f"🖼️ Images Indexed   : {len(image_index)}")
        return manifest

def main():
    generator = ProductManifestGenerator()
    generator.generate_manifest()

if __name__ == "__main__":
    main()

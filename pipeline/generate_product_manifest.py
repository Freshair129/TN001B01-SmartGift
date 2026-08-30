"""
SmartGift Product & Catalog Manifest Generator
Generates:
  1. SHA-256 Data Integrity Hashes for catalog sub-datasets
  2. Multi-File Category Slices under public/data/categories/<slug>.json
  3. Product Image Asset Path Index for Frontend & Web Applications
  4. Public Web Manifest (public/data/product_manifest.json) & Internal Audit Manifest

Customer-safe boundary (ADR-004 Decision #3, SPEC-WEB-OFFLINE-CATALOG §4):
the public manifest and category slices must not carry internal repo paths,
source hashes, factory cost, CBM/freight, or supplier lineage. Full source
lineage lives only in the internal audit manifest under data-pipeline/,
which .vercelignore keeps out of every deployment.
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

    @staticmethod
    def _hash_entry(filepath: str, served_path: str) -> Dict[str, Any]:
        if os.path.exists(filepath):
            return {
                "path": served_path,
                "size_bytes": os.path.getsize(filepath),
                "sha256": compute_file_sha256(filepath)
            }
        return {"path": served_path, "size_bytes": 0, "sha256": ""}

    def compute_public_integrity_hashes(self) -> Dict[str, Dict[str, Any]]:
        """Hashes of customer-safe artifacts the web surface actually serves.
        Paths are the public endpoint URLs, never internal repo paths."""
        return {
            "pricelist_public": self._hash_entry(PRICELIST_PUBLIC_PATH, "/data/pricelist_public.json"),
            "catalog_media": self._hash_entry(CATALOG_MEDIA_PATH, "/data/catalog_media.json")
        }

    def compute_internal_integrity_hashes(self) -> Dict[str, Dict[str, Any]]:
        """Full source lineage with repo paths — internal audit manifest only."""
        target_files = {
            "smartgift_catalog_master": MASTER_CATALOG_PATH,
            "pricelist_master": PRICELIST_MASTER_PATH,
            "factory_costs": FACTORY_COSTS_PATH,
            "catalog_media": CATALOG_MEDIA_PATH,
            "pricelist_public": PRICELIST_PUBLIC_PATH
        }
        return {key: self._hash_entry(path, path) for key, path in target_files.items()}

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

    # Customer-safe product fields for the public category slices (SPEC-WEB-OFFLINE-CATALOG §4).
    # Freight/CBM/carton logistics and internal master references must never be listed here.
    PUBLIC_PRODUCT_FIELDS = (
        "code", "name_th", "name_en", "category", "category_slug", "product_family",
        "material", "color", "dimensions_cm", "unit_weight_kg", "srp_price", "price_tiers"
    )

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

            # Project onto the customer-safe allowlist and attach image paths
            enriched_products = []
            for p in cat_products:
                p_copy = {k: p[k] for k in self.PUBLIC_PRODUCT_FIELDS if k in p}
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

        public_hashes = self.compute_public_integrity_hashes()
        internal_hashes = self.compute_internal_integrity_hashes()
        image_index = self.build_product_image_index()
        category_slices = self.build_multi_file_category_slices(image_index)

        now_utc = datetime.now(timezone.utc)
        date_tag = now_utc.strftime("%Y.%m.%d")

        # Customer-visible version derives from the customer-safe snapshot itself,
        # never from an internal source artifact hash (SPEC-WEB-OFFLINE-CATALOG §3.3).
        public_sha = public_hashes.get("pricelist_public", {}).get("sha256", "")[:8]
        catalog_version = f"v1.3.0-{date_tag}-{public_sha}"

        manifest = {
            "schema_version": "1.3.0",
            "tenant_id": "Org-EtohGroup",
            "business_id": "SmartGift",
            "operating_entity": "บริษัท เทราบิส จำกัด (Therabis Co., Ltd.)",
            "catalog_version": catalog_version,
            "generated_at": now_utc.isoformat(),
            "data_integrity_hashes": public_hashes,
            "multi_file_index": category_slices,
            "product_image_index": image_index,
            "summary_stats": {
                "total_categories": len(category_slices),
                "total_canonical_products": len(self.master_data.get("canonical_products", [])),
                "total_catalog_offers": len(self.master_data.get("catalog_offers", [])),
                "total_indexed_images": len(image_index)
            }
        }

        # Write Web-facing Manifest (customer-safe only)
        with open(PUBLIC_MANIFEST_PATH, "w", encoding="utf-8") as f:
            json.dump(manifest, f, ensure_ascii=False, indent=2)

        # Write Internal Audit Manifest with full source lineage (non-deployed path)
        audit_manifest = {
            **manifest,
            "data_integrity_hashes": internal_hashes,
            "source_catalog_version_basis": {
                "public_snapshot": "pricelist_public",
                "master_sha256": internal_hashes.get("smartgift_catalog_master", {}).get("sha256", "")
            },
            "published_public_hashes": public_hashes
        }
        with open(AUDIT_MANIFEST_PATH, "w", encoding="utf-8") as f:
            json.dump(audit_manifest, f, ensure_ascii=False, indent=2)

        self.verify_public_boundary()

        print(f"✅ Product Manifest published to '{PUBLIC_MANIFEST_PATH}'")
        print(f"✅ Audit Manifest saved to '{AUDIT_MANIFEST_PATH}'")
        print(f"📊 Categories Sliced: {len(category_slices)}")
        print(f"🖼️ Images Indexed   : {len(image_index)}")
        return manifest

    FORBIDDEN_PUBLIC_SUBSTRINGS = (
        "data-pipeline/", "factory_cost", "pricelist_master", "smartgift_catalog_master",
        "freight", "cbm", "flowaccount", "supplier"
    )

    def verify_public_boundary(self) -> None:
        """Fail-closed scan: generated public data files must not contain
        internal source paths or forbidden cost/logistics markers."""
        targets = [PUBLIC_MANIFEST_PATH] + [
            os.path.join(CATEGORIES_DIR, f)
            for f in sorted(os.listdir(CATEGORIES_DIR)) if f.endswith(".json")
        ]
        violations = []
        for path in targets:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read().lower()
            for marker in self.FORBIDDEN_PUBLIC_SUBSTRINGS:
                if marker in content:
                    violations.append(f"{path}: contains '{marker}'")
        if violations:
            for v in violations:
                print(f"⛔ PUBLIC BOUNDARY VIOLATION: {v}")
            raise SystemExit(1)
        print("🛡️ Public boundary scan passed (no internal paths / cost / logistics markers)")

def main():
    generator = ProductManifestGenerator()
    generator.generate_manifest()

if __name__ == "__main__":
    main()

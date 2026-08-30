"""
SmartGift Option B: Supabase PostgreSQL ➔ GenesisBlockDB Edge Sync Bridge
Synchronizes Master Catalog, Product Taxonomy, and Sensory Vectors from Supabase Cloud
into GenesisBlockDB Local Edge Engine for ultra-low latency GraphRAG search.
"""

import os
import sys
import json
import subprocess
from typing import Dict, Any, Optional

sys.stdout.reconfigure(encoding='utf-8')

CATALOG_PATH = "smartgift_catalog_master.json"
SEED_SCRIPT_PATH = "seed_genesisblock.mjs"

class SupabaseGenesisSyncBridge:
    def __init__(self, supabase_url: Optional[str] = None, supabase_key: Optional[str] = None):
        self.supabase_url = supabase_url or os.environ.get("SUPABASE_URL")
        self.supabase_key = supabase_key or os.environ.get("SUPABASE_KEY")
        self.client = None

        if self.supabase_url and self.supabase_key:
            try:
                from supabase import create_client
                self.client = create_client(self.supabase_url, self.supabase_key)
                print("✅ Supabase Client initialized successfully.")
            except ImportError:
                print("⚠️ 'supabase' package not installed. Operating in Local Master Sync mode.")
            except Exception as e:
                print(f"⚠️ Could not connect to Supabase Cloud: {e}. Falling back to Local Master Sync mode.")

    def fetch_master_catalog_from_supabase(self) -> Optional[Dict[str, Any]]:
        """Fetch master catalog dataset from Supabase PostgreSQL tables"""
        if not self.client:
            return None
        
        try:
            categories = self.client.table("categories").select("*").execute().data
            products = self.client.table("product_masters").select("*").execute().data
            offers = self.client.table("catalog_offers").select("*").execute().data
            bundles = self.client.table("corporate_bundles").select("*").execute().data

            catalog_payload = {
                "categories": categories,
                "canonical_products": products,
                "catalog_offers": offers,
                "corporate_bundles": bundles
            }
            return catalog_payload
        except Exception as e:
            print(f"⚠️ Error fetching catalog from Supabase: {e}")
            return None

    def sync_to_edge_engine(self) -> bool:
        """Trigger sync from Master Catalog (Supabase or Local SSOT) to GenesisBlockDB Edge Engine"""
        print("\n==================================================================")
        print(" 🔄 Option B Sync Bridge: Supabase PostgreSQL ➔ GenesisBlockDB Edge")
        print("==================================================================")

        remote_data = self.fetch_master_catalog_from_supabase()
        if remote_data:
            print("📥 Fetched fresh Master Catalog from Supabase Cloud.")
            with open(CATALOG_PATH, "w", encoding="utf-8") as f:
                json.dump(remote_data, f, ensure_ascii=False, indent=2)
            print(f"💾 Saved synced catalog to '{CATALOG_PATH}'.")
        else:
            print(f"ℹ️ Using Single Source of Truth Master Catalog from '{CATALOG_PATH}'.")

        print("⚡ Seeding GenesisBlockDB Edge Engine (Native Hybrid Graph + HNSW Vector Substrate)...")
        try:
            result = subprocess.run(
                ["node", SEED_SCRIPT_PATH],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=True
            )
            print(result.stdout)
            print("✅ Option B Sync Complete: GenesisBlockDB Edge Engine is ready for GraphRAG (< 1ms latency).")
            return True
        except subprocess.CalledProcessError as err:
            print(f"❌ Error during GenesisBlockDB seeding: {err.stderr}")
            return False

if __name__ == "__main__":
    bridge = SupabaseGenesisSyncBridge()
    bridge.sync_to_edge_engine()

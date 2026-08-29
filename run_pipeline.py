"""
SmartGift Master Pipeline CLI Shortcut
Runs the unified 5-Stage Data Governance Pipeline.
"""

from pipeline.master_orchestrator import run_master_pipeline

if __name__ == "__main__":
    run_master_pipeline()

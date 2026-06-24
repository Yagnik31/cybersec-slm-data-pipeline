#!/usr/bin/env python3
"""Test individual cleaning stages (Method 2)."""

from src.cybersec_slm.cleaning import run
import time

def test_individual_stages():
    """Run each cleaning stage individually for detailed testing."""
    print("\n" + "="*60)
    print("METHOD 2: INDIVIDUAL STAGES (One stage at a time)")
    print("="*60)
    
    stages = ["sanitize", "dedup", "pii", "lang"]
    
    print("\nRunning each stage separately:")
    print("- Sanitize: fix encoding, dates, missing fields")
    print("- Dedup: remove exact & near duplicates")
    print("- PII: detect & anonymize PII")
    print("- Lang: filter non-English\n")
    
    for stage in stages:
        print(f"\n--- Running: {stage.upper()} ---")
        start = time.time()
        try:
            run.run(cmd=stage, limit=50)  # limit 50 records per file
            elapsed = time.time() - start
            print(f"✓ {stage} stage completed in {elapsed:.2f} seconds")
            print(f"  Output: _stages/{stage}/")
        except Exception as e:
            print(f"✗ {stage} stage failed: {e}")
            raise
    
    print("\n" + "="*60)
    print("REPORT GENERATION")
    print("="*60)
    print("\nGenerating summary report...")
    try:
        run.run(cmd="report")
        print("✓ Report created: logs/clean_report.csv")
    except Exception as e:
        print(f"✗ Report generation failed: {e}")
        raise

if __name__ == "__main__":
    test_individual_stages()

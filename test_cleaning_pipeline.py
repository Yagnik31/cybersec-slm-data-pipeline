#!/usr/bin/env python3
"""Test the full cleaning pipeline (Method 1)."""

from src.cybersec_slm.cleaning import pipeline
import time

def test_full_pipeline():
    """Run the full cleaning pipeline with a small limit for testing."""
    print("\n" + "="*60)
    print("METHOD 1: FULL PIPELINE (All stages at once)")
    print("="*60)
    print("\nRunning: Sanitize -> Anomaly Check -> Dedup -> PII -> Language Filter")
    print("Input: raw_data/")
    print("Output: cleaned/, flagged/, dropped/, + logs/clean_report.csv\n")
    
    start = time.time()
    try:
        pipeline.run_all(limit=50)  # limit 50 records per file for testing
        elapsed = time.time() - start
        print(f"\n✓ Pipeline completed in {elapsed:.2f} seconds")
        print("\nOutputs created:")
        print("  - cleaned/      (records that passed all stages)")
        print("  - flagged/      (behavioral anomalies for review)")
        print("  - dropped/      (structural/duplicate/non-English)")
        print("  - logs/clean_report.csv (summary statistics)")
    except Exception as e:
        print(f"✗ Pipeline failed: {e}")
        raise

if __name__ == "__main__":
    test_full_pipeline()

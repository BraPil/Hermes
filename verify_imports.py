#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Verify all required imports work"""

import sys
import os

# Set UTF-8 encoding
os.environ['PYTHONIOENCODING'] = 'utf-8'

tests = [
    ("Fundamentals", "from data_ingestion.fundamentals import fetch_stock_data"),
    ("Psycho", "from data_ingestion.psycho import fetch_vix_and_sp500_data, fetch_fear_greed_index"),
    ("Social", "from data_ingestion.social import RedditSentimentAnalyzer"),
    ("Analytics", "from analytics.scoring import calculate_score"),
    ("Outputs", "from outputs.report_generator import generate_report"),
]

print("Verifying imports...\n")
passed = 0
failed = 0

for name, import_stmt in tests:
    try:
        exec(import_stmt)
        print("[OK] " + name + " OK")
        passed += 1
    except Exception as e:
        print("[FAIL] " + name + " FAILED: " + str(e)[:50])
        failed += 1

print("\n" + "="*50)
print("Results: " + str(passed) + " passed, " + str(failed) + " failed")
print("="*50 + "\n")

if failed == 0:
    print("[OK] ALL IMPORTS VERIFIED!")
    sys.exit(0)
else:
    print("[FAIL] Some imports failed")
    sys.exit(1)


#!/usr/bin/env python3
"""
analyze_results.py
------------------
Analyzes JMeter .jtl result files and prints a summary report.
Usage: python3 scripts/analyze_results.py [--jtl results/results.jtl]
"""

import csv
import os
import argparse
from statistics import mean, median

def analyze(jtl_path):
    if not os.path.exists(jtl_path):
        print(f"[WARNING] Results file not found: {jtl_path}")
        print("Analyze JMeter Results")
        return

    print(f"
{'='*55}")
    print(f"  JMeter Results Analysis: {jtl_path}")
    print(f"{'='*55}")

    response_times = []
    statuses = []
    labels = {}

    with open(jtl_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            elapsed = int(row.get('elapsed', 0))
            success = row.get('success', 'true').lower() == 'true'
            label   = row.get('label', 'unknown')

            response_times.append(elapsed)
            statuses.append(success)

            if label not in labels:
                labels[label] = {'times': [], 'errors': 0, 'count': 0}
            labels[label]['times'].append(elapsed)
            labels[label]['count'] += 1
            if not success:
                labels[label]['errors'] += 1

    if not response_times:
        print("No data found in results file.")
        return

    total       = len(response_times)
    errors      = statuses.count(False)
    error_rate  = (errors / total) * 100
    sorted_rt   = sorted(response_times)
    p90_idx     = int(0.90 * len(sorted_rt)) - 1
    p95_idx     = int(0.95 * len(sorted_rt)) - 1
    p99_idx     = int(0.99 * len(sorted_rt)) - 1

    print(f"
OVERALL SUMMARY")
    print(f"  Total Requests : {total}")
    print(f"  Failures       : {errors}")
    print(f"  Error Rate     : {error_rate:.2f}%")
    print(f"  Avg (ms)       : {mean(response_times):.1f}")
    print(f"  Median (ms)    : {median(response_times):.1f}")
    print(f"  Min (ms)       : {min(response_times)}")
    print(f"  Max (ms)       : {max(response_times)}")
    print(f"  90th pct (ms)  : {sorted_rt[p90_idx]}")
    print(f"  95th pct (ms)  : {sorted_rt[p95_idx]}")
    print(f"  99th pct (ms)  : {sorted_rt[p99_idx]}")

    print(f"
PER-SAMPLER BREAKDOWN")
    print(f"  {'Sampler':<35} {'Req':>5} {'Err':>5} {'Avg(ms)':>9} {'Max(ms)':>9}")
    print(f"  {'-'*65}")
    for lbl, data in sorted(labels.items()):
        avg = mean(data['times'])
        mx  = max(data['times'])
        print(f"  {lbl:<35} {data['count']:>5} {data['errors']:>5} {avg:>9.1f} {mx:>9}")

    print(f"
{'='*55}
")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze JMeter .jtl results")
    parser.add_argument("--jtl", default="results/results.jtl",
                        help="Path to the .jtl results file")
    args = parser.parse_args()
    analyze(args.jtl)

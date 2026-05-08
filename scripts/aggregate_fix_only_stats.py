import os
import json
import numpy as np
import re
from datetime import datetime

def analyze_fix_only_stats():
    """
    Aggregates and analyzes statistics for 'fix-only' feedback experiments.

    It calculates the mean and standard deviation for:
    - The number of initial valid (not needing fixing) alpha expressions.
    - The number of initial invalid alpha expressions.
    - The number of fixed alpha expressions.
    - The percentage of initial invalid alphas that remained invalid after fixing attempts.
    """
    results_dir = r'c:\Users\Shannon\Desktop\alphagen\out\results'
    start_date = datetime.strptime("20230305", "%Y%m%d").date()
    start_date = datetime.strptime("20260305", "%Y%m%d").date()

    stats_list = []

    print(f"Searching for 'fix-only' feedback folders in: {results_dir}")
    print(f"Processing folders with dates on or after: {start_date.strftime('%Y-%m-%d')}\n")

    for folder_name in os.listdir(results_dir):
        folder_path = os.path.join(results_dir, folder_name)
        
        # Filter for directories containing 'fix-only' and 'csi300_20'
        if not os.path.isdir(folder_path) or 'fix-only' not in folder_name or 'csi300_20' not in folder_name or '202602' in folder_name:
            continue

        # Extract date from folder name
        match = re.search(r'(\d{8})', folder_name)
        if not match:
            continue

        try:
            folder_date = datetime.strptime(match.group(1), "%Y%m%d").date()
        except ValueError:
            continue

        # Filter by start date
        if folder_date < start_date:
            continue

        stats_file = os.path.join(folder_path, 'llm_alpha_stats.json')
        if not os.path.exists(stats_file):
            continue

        print(f"  - Processing: {folder_name}")
        with open(stats_file, 'r') as f:
            data = json.load(f)

        original_stats = data.get('original', {})
        
        initial_valid = original_stats.get('valid', 0)
        initial_invalid = original_stats.get('invalid', 0)
        initial_fixed = original_stats.get('fixed', 0)

        final_invalid = initial_invalid - initial_fixed
        
        unfixed_invalid_percentage = 0.0
        if initial_invalid > 0:
            unfixed_invalid_percentage = (final_invalid / initial_invalid) * 100

        stats_list.append({
            'initial_valid': initial_valid,
            'initial_invalid': initial_invalid,
            'initial_fixed': initial_fixed,
            'final_invalid': final_invalid,
            'unfixed_invalid_percentage': unfixed_invalid_percentage
        })

    if not stats_list:
        print("\nNo matching 'fix-only' feedback folders found or processed.")
        return
    
    if len(stats_list) != 10:
        print(f"\nWarning: Expected 10 'fix-only' folders, but found {len(stats_list)}. Proceeding with available data.")

    initial_valid_list = [s['initial_valid'] for s in stats_list]
    initial_invalid_list = [s['initial_invalid'] for s in stats_list]
    initial_fixed_list = [s['initial_fixed'] for s in stats_list]
    final_invalid_list = [s['final_invalid'] for s in stats_list]
    unfixed_invalid_pct_list = [s['unfixed_invalid_percentage'] for s in stats_list]

    print(f"\n--- Aggregated 'fix-only' Feedback Statistics ({len(stats_list)} folders) ---")
    header = f"{'Metric':<40} | {'Mean':>15} | {'Std Dev':>15}"
    print(header)
    print("-" * len(header))
    print(f"{'Initial Valid Alphas':<40} | {np.mean(initial_valid_list):>15.2f} | {np.std(initial_valid_list):>15.2f}")
    print(f"{'Initial Invalid Alphas':<40} | {np.mean(initial_invalid_list):>15.2f} | {np.std(initial_invalid_list):>15.2f}")
    print(f"{'Initial Fixed Alphas':<40} | {np.mean(initial_fixed_list):>15.2f} | {np.std(initial_fixed_list):>15.2f}")
    print(f"{'Final Invalid Alphas (unfixed)':<40} | {np.mean(final_invalid_list):>15.2f} | {np.std(final_invalid_list):>15.2f}")
    print(f"{'Unfixed Invalid % of Initial Invalid':<40} | {np.mean(unfixed_invalid_pct_list):>15.2f}% | {np.std(unfixed_invalid_pct_list):>15.2f}%")
    print("-" * len(header))

if __name__ == '__main__':
    analyze_fix_only_stats()
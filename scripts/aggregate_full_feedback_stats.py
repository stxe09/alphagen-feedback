import os
import json
import numpy as np
import re
from datetime import datetime

def analyze_full_feedback_stats():
    """
    Aggregates and analyzes statistics for 'full' feedback experiments.

    It calculates the mean and standard deviation for:
    - The complexity of original alphas.
    - The complexity of improved alphas.
    - The percentage difference in complexity between them.
    - The final IC, Rank IC, ICIR, and Rank ICIR test means from RL output.
    """
    results_dir = r'c:\Users\Shannon\Desktop\alphagen\out\results'
    start_date = datetime.strptime("20260308", "%Y%m%d").date()

    stats_list = []

    print(f"Searching for 'full' feedback folders in: {results_dir}")
    print(f"Processing folders with dates on or after: {start_date.strftime('%Y-%m-%d')}\n")

    for folder_name in os.listdir(results_dir):
        folder_path = os.path.join(results_dir, folder_name)
        if not os.path.isdir(folder_path) or 'improve-only' not in folder_name or 'csi300_20' not in folder_name:
            continue

        match = re.search(r'(\d{8})', folder_name)
        if not match:
            continue

        try:
            folder_date = datetime.strptime(match.group(1), "%Y%m%d").date()
        except ValueError:
            continue

        if folder_date < start_date:
            continue

        stats_file = os.path.join(folder_path, 'llm_alpha_stats.json')
        if not os.path.exists(stats_file):
            continue

        print(f"  - Processing: {folder_name}")
        with open(stats_file, 'r') as f:
            data = json.load(f)

        original_complexity = data.get('original', {}).get('complexity', {}).get('mean')
        improvement_complexity = data.get('improvement', {}).get('complexity', {}).get('mean')

        # Find the _rl_ report file
        rl_files = [f for f in os.listdir(folder_path) if f.endswith('.json') and '_rl_' in f]
        if not rl_files:
            continue
        
        # Get the latest rl file if there are multiple
        rl_file_path = max([os.path.join(folder_path, f) for f in rl_files], key=os.path.getmtime)
        
        with open(rl_file_path, 'r') as f:
            rl_data = json.load(f)
            
        final_metrics = rl_data.get('final_metrics', {})
        ic_test_mean = final_metrics.get('final_ic_test_mean')
        rank_ic_test_mean = final_metrics.get('final_rank_ic_test_mean')
        icir_test_mean = final_metrics.get('final_icir_test_mean')
        rank_icir_test_mean = final_metrics.get('final_rank_icir_test_mean')

        if original_complexity and improvement_complexity and original_complexity > 0 and ic_test_mean is not None:
            stats_list.append({
                'original_complexity': original_complexity,
                'improvement_complexity': improvement_complexity,
                'complexity_pct_diff': ((improvement_complexity - original_complexity) / original_complexity) * 100,
                'ic_test_mean': ic_test_mean,
                'rank_ic_test_mean': rank_ic_test_mean,
                'icir_test_mean': icir_test_mean,
                'rank_icir_test_mean': rank_icir_test_mean
            })

    if not stats_list:
        print("\nNo matching 'full' feedback folders found or processed.")
        return

    original_complexities = [s['original_complexity'] for s in stats_list]
    improvement_complexities = [s['improvement_complexity'] for s in stats_list]
    complexity_pct_diffs = [s['complexity_pct_diff'] for s in stats_list]
    ic_test_means = [s['ic_test_mean'] for s in stats_list]
    rank_ic_test_means = [s['rank_ic_test_mean'] for s in stats_list]
    icir_test_means = [s['icir_test_mean'] for s in stats_list]
    rank_icir_test_means = [s['rank_icir_test_mean'] for s in stats_list]

    print(f"\n--- Aggregated 'improve-only' Feedback Statistics ({len(stats_list)} folders) ---")
    header = f"{'Metric':<30} | {'Mean':>15} | {'Std Dev':>15}"
    print(header)
    print("-" * len(header))
    print(f"{'Original Alpha Complexity':<30} | {np.mean(original_complexities):>15.2f} | {np.std(original_complexities):>15.2f}")
    print(f"{'Improved Alpha Complexity':<30} | {np.mean(improvement_complexities):>15.2f} | {np.std(improvement_complexities):>15.2f}")
    print(f"{'Complexity % Difference (%)':<30} | {np.mean(complexity_pct_diffs):>15.2f} | {np.std(complexity_pct_diffs):>15.2f}")
    print(f"{'Final IC Test Mean':<30} | {np.mean(ic_test_means):>15.4f} | {np.std(ic_test_means):>15.4f}")
    print(f"{'Final Rank IC Test Mean':<30} | {np.mean(rank_ic_test_means):>15.4f} | {np.std(rank_ic_test_means):>15.4f}")
    print(f"{'Final ICIR Test Mean':<30} | {np.mean(icir_test_means):>15.4f} | {np.std(icir_test_means):>15.4f}")
    print(f"{'Final Rank ICIR Test Mean':<30} | {np.mean(rank_icir_test_means):>15.4f} | {np.std(rank_icir_test_means):>15.4f}")
    print("-" * len(header))

if __name__ == '__main__':
    analyze_full_feedback_stats()

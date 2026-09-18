"""
Post-process raw outputs: calculate metrics, statistics, and generate figures.

Usage:
    python src/analyze.py
"""

import os
import sys
import csv
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from scipy import stats
from typing import Dict, List, Tuple

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from src.metrics import calculate_all_metrics, compression_ratio, check_length_compliance, check_facts_coverage


def load_raw_outputs(csv_path: str) -> pd.DataFrame:
    """Load raw outputs from CSV."""
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Raw outputs CSV not found: {csv_path}")
    return pd.read_csv(csv_path)


def load_source_texts(num_texts: int = None) -> Dict[str, str]:
    """Load all source texts."""
    texts = {}
    texts_dir = Path(config.TEXTS_DIR)

    text_files = sorted(texts_dir.glob('text*.txt'))
    if num_texts:
        text_files = text_files[:num_texts]

    for text_file in text_files:
        text_id = text_file.stem
        with open(text_file, 'r', encoding='utf-8') as f:
            texts[text_id] = f.read().strip()

    return texts


def load_facts() -> Dict[str, List[Dict]]:
    """Load fact definitions from facts.json."""
    facts_path = config.FACTS_JSON
    if not os.path.exists(facts_path):
        return {}

    with open(facts_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def compute_metrics_for_outputs(df: pd.DataFrame, source_texts: Dict[str, str], facts: Dict) -> pd.DataFrame:
    """
    Add computed metrics to dataframe.
    Adds: all metrics from calculate_all_metrics() + compression_ratio + facts_coverage + length_compliance
    """
    metric_cols = [
        'wordCount', 'sentenceCount', 'avgWordsPerSentence', 'syllableCount',
        'uniqueWords', 'lexicalDensity', 'entropy', 'readability', 'cohesion',
        'coherence', 'summaryScore'
    ]

    for col in metric_cols + ['compression_ratio', 'facts_coverage', 'length_compliant']:
        df[col] = None

    for idx, row in df.iterrows():
        try:
            summary_text = row['output']
            source_text = source_texts.get(row['text_id'], '')

            metrics = calculate_all_metrics(summary_text)
            for col in metric_cols:
                df.at[idx, col] = metrics[col]

            df.at[idx, 'compression_ratio'] = compression_ratio(source_text, summary_text)

            text_facts = facts.get(row['text_id'], [])
            if text_facts:
                coverage = check_facts_coverage(summary_text, text_facts)
                df.at[idx, 'facts_coverage'] = coverage

            df.at[idx, 'length_compliant'] = check_length_compliance(summary_text)

        except Exception as e:
            print(f"Warning: failed to compute metrics for row {idx}: {e}")

    return df


def compute_summary_statistics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute per-model statistics: mean, std, etc.
    """
    metrics = [
        'wordCount', 'sentenceCount', 'summaryScore', 'entropy', 'readability',
        'cohesion', 'coherence', 'lexicalDensity', 'compression_ratio', 'facts_coverage'
    ]

    rows = []
    for model in sorted(df['model'].unique()):
        model_data = df[df['model'] == model]
        row = {'model': model}

        for metric in metrics:
            if metric in model_data.columns:
                values = model_data[metric].dropna()
                if len(values) > 0:
                    row[f'{metric}_mean'] = values.mean()
                    row[f'{metric}_std'] = values.std()
                    row[f'{metric}_min'] = values.min()
                    row[f'{metric}_max'] = values.max()

        rows.append(row)

    return pd.DataFrame(rows)


def run_statistical_tests(df: pd.DataFrame) -> Dict[str, Tuple[float, float]]:
    """
    Run Kruskal-Wallis (non-parametric) on key metrics across models.
    Returns {metric_name: (statistic, p_value)}
    """
    results = {}

    if len(df) < 12:
        return results

    for metric in ['summaryScore', 'facts_coverage']:
        if metric not in df.columns:
            continue

        groups = [group[metric].dropna().values for _, group in df.groupby('model')]
        if len(groups) > 1 and all(len(g) > 0 for g in groups):
            try:
                stat, p_value = stats.kruskal(*groups)
                results[metric] = (stat, p_value)
            except (ValueError, AttributeError):
                pass

    return results


def extract_examples(df: pd.DataFrame, source_texts: Dict[str, str], facts: Dict) -> List[Dict]:
    """
    Select 3 qualitative examples: best, worst, and most typical.
    """
    examples = []

    if 'summaryScore' not in df.columns or df.empty:
        return examples

    # Best: highest summary score
    best_idx = df['summaryScore'].idxmax()
    examples.append({
        'type': 'best',
        'description': 'Highest Summary Score',
        'data': df.iloc[best_idx].to_dict()
    })

    # Worst: lowest summary score
    worst_idx = df['summaryScore'].idxmin()
    examples.append({
        'type': 'worst',
        'description': 'Lowest Summary Score',
        'data': df.iloc[worst_idx].to_dict()
    })

    # Most typical: median summary score
    median_score = df['summaryScore'].median()
    closest_idx = (df['summaryScore'] - median_score).abs().idxmin()
    examples.append({
        'type': 'typical',
        'description': 'Median Summary Score',
        'data': df.iloc[closest_idx].to_dict()
    })

    return examples


def save_examples_md(examples: List[Dict], output_path: str, source_texts: Dict[str, str]):
    """Save qualitative examples as Markdown."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# Qualitative Examples\n\n")

        for example in examples:
            data = example['data']
            f.write(f"## {example['description'].upper()}\n\n")
            f.write(f"**Type:** {example['type']}\n\n")
            f.write(f"**Model:** {data.get('model', 'N/A')}\n\n")
            f.write(f"**Text ID:** {data.get('text_id', 'N/A')}\n\n")
            f.write(f"**Run:** {data.get('run', 'N/A')}\n\n")

            if 'summaryScore' in data:
                f.write(f"**Summary Score:** {data.get('summaryScore', 'N/A')}\n\n")
            if 'facts_coverage' in data:
                f.write(f"**Fact Coverage:** {data.get('facts_coverage', 'N/A')}\n\n")

            f.write("### Generated Summary\n\n")
            f.write(f"```\n{data.get('output', 'N/A')}\n```\n\n")

            source_text = source_texts.get(data.get('text_id', ''), '')
            if source_text:
                f.write("### Source Text\n\n")
                f.write(f"```\n{source_text[:300]}...\n```\n\n")

            f.write("---\n\n")


def create_figures(df: pd.DataFrame, summary_stats: pd.DataFrame, output_dir: str = config.FIGURES_DIR):
    """Generate matplotlib figures."""
    os.makedirs(output_dir, exist_ok=True)

    # Set style
    plt.style.use('seaborn-v0_8-darkgrid')

    # Figure 1: Box plot of Summary Score by model
    fig, ax = plt.subplots(figsize=(10, 6))
    models = sorted(df['model'].unique())
    data_to_plot = [df[df['model'] == m]['summaryScore'].dropna().values for m in models]
    ax.boxplot(data_to_plot)
    ax.set_xticklabels(models)
    ax.set_ylabel('Summary Score (S_SS)')
    ax.set_xlabel('Model')
    ax.set_title('Summary Score Distribution by Model')
    ax.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    plt.savefig(f"{output_dir}/fig1_summary_score_by_model.png", dpi=150)
    plt.close()

    # Figure 2: Box plot of key-fact coverage by model
    if 'facts_coverage' in df.columns:
        fig, ax = plt.subplots(figsize=(10, 6))
        data_to_plot = [df[df['model'] == m]['facts_coverage'].dropna().values for m in models]
        ax.boxplot(data_to_plot)
        ax.set_xticklabels(models)
        ax.set_ylabel('Fact Coverage')
        ax.set_xlabel('Model')
        ax.set_title('Key-Fact Coverage by Model')
        ax.grid(axis='y', alpha=0.3)
        plt.tight_layout()
        plt.savefig(f"{output_dir}/fig2_facts_coverage_by_model.png", dpi=150)
        plt.close()

    # Figure 3: Compression ratio by model (bar with error bars)
    if 'compression_ratio' in df.columns:
        fig, ax = plt.subplots(figsize=(10, 6))
        means = []
        stds = []
        for model in models:
            values = df[df['model'] == model]['compression_ratio'].dropna().values
            means.append(np.mean(values) if len(values) > 0 else 0)
            stds.append(np.std(values) if len(values) > 1 else 0)

        x_pos = np.arange(len(models))
        ax.bar(x_pos, means, yerr=stds, capsize=5, alpha=0.7, color='steelblue')
        ax.set_ylabel('Compression Ratio')
        ax.set_xlabel('Model')
        ax.set_title('Mean Compression Ratio by Model (with SD)')
        ax.set_xticks(x_pos)
        ax.set_xticklabels(models)
        ax.grid(axis='y', alpha=0.3)
        plt.tight_layout()
        plt.savefig(f"{output_dir}/fig3_compression_ratio.png", dpi=150)
        plt.close()

    # Figure 4: Heatmap of mean coverage by model and text
    if 'facts_coverage' in df.columns:
        texts = sorted(df['text_id'].unique())
        heatmap_data = []

        for model in models:
            row = []
            for text_id in texts:
                subset = df[(df['model'] == model) & (df['text_id'] == text_id)]
                if not subset.empty:
                    row.append(subset['facts_coverage'].mean())
                else:
                    row.append(0)
            heatmap_data.append(row)

        fig, ax = plt.subplots(figsize=(12, 6))
        im = ax.imshow(heatmap_data, cmap='YlGn', aspect='auto')
        ax.set_xticks(np.arange(len(texts)))
        ax.set_yticks(np.arange(len(models)))
        ax.set_xticklabels(texts)
        ax.set_yticklabels(models)
        ax.set_xlabel('Source Text')
        ax.set_ylabel('Model')
        ax.set_title('Mean Fact Coverage: Model × Text')
        plt.colorbar(im, ax=ax, label='Coverage')
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
        plt.tight_layout()
        plt.savefig(f"{output_dir}/fig4_coverage_heatmap.png", dpi=150)
        plt.close()

    # Figure 5: Scatter plot - seconds vs coverage (efficiency)
    if 'facts_coverage' in df.columns and 'seconds' in df.columns:
        fig, ax = plt.subplots(figsize=(10, 6))
        for model in models:
            subset = df[df['model'] == model]
            ax.scatter(subset['seconds'], subset['facts_coverage'], label=model, alpha=0.6, s=50)

        ax.set_xlabel('Time per Generation (seconds)')
        ax.set_ylabel('Fact Coverage')
        ax.set_title('Efficiency Trade-off: Speed vs Coverage')
        ax.legend()
        ax.grid(alpha=0.3)
        plt.tight_layout()
        plt.savefig(f"{output_dir}/fig5_efficiency_tradeoff.png", dpi=150)
        plt.close()

    print(f"Generated figures in {output_dir}/")


def save_summary_table(summary_stats: pd.DataFrame, output_path: str):
    """Save summary statistics table."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    summary_stats.to_csv(output_path, index=False)
    print(f"Saved summary table to {output_path}")


def analyze():
    """Main analysis pipeline."""
    print("\n" + "="*60)
    print("Starting post-processing and analysis")
    print("="*60 + "\n")

    # Load raw outputs
    print("Loading raw outputs...")
    df = load_raw_outputs(config.RAW_OUTPUTS_CSV)
    print(f"  Loaded {len(df)} generations")

    # Load source texts and facts
    print("Loading source texts and facts...")
    source_texts = load_source_texts()
    facts = load_facts()
    print(f"  Loaded {len(source_texts)} texts and facts for {len(facts)} texts")

    # Compute metrics
    print("Computing metrics for each output...")
    df = compute_metrics_for_outputs(df, source_texts, facts)

    # Save metrics CSV
    df.to_csv(config.METRICS_CSV, index=False)
    print(f"  Saved metrics to {config.METRICS_CSV}")

    # Compute summary statistics
    print("Computing summary statistics...")
    summary_stats = compute_summary_statistics(df)
    save_summary_table(summary_stats, config.SUMMARY_TABLE_CSV)
    print(summary_stats.to_string())

    # Run statistical tests
    print("\nRunning statistical tests (Kruskal-Wallis)...")
    test_results = run_statistical_tests(df)
    for metric, (stat, p_value) in test_results.items():
        sig = "***" if p_value < 0.001 else "**" if p_value < 0.01 else "*" if p_value < 0.05 else "ns"
        print(f"  {metric}: F={stat:.2f}, p={p_value:.4f} {sig}")

    # Extract and save qualitative examples
    print("\nExtracting qualitative examples...")
    examples = extract_examples(df, source_texts, facts)
    save_examples_md(examples, config.EXAMPLES_MD, source_texts)
    print(f"  Saved to {config.EXAMPLES_MD}")

    # Create figures
    print("\nGenerating figures...")
    create_figures(df, summary_stats)

    print("\n" + "="*60)
    print("Analysis complete!")
    print("="*60 + "\n")


if __name__ == "__main__":
    analyze()

"""
Run text generation experiments using Ollama local API.

Generates summaries for multiple source texts across different models,
with multiple runs per (model, text) pair.

Usage:
    python src/run_experiments.py          # Full run (200 generations)
    python src/run_experiments.py --pilot  # Pilot (1 text, all models, 2 runs)
"""

import os
import sys
import csv
import time
import argparse
import requests
import json
from datetime import datetime
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from src.metrics import calculate_all_metrics


def load_text(text_path: str) -> str:
    """Load text from file."""
    with open(text_path, 'r', encoding='utf-8') as f:
        return f.read().strip()


def load_all_texts(num_texts: int = None) -> dict:
    """
    Load all available text files.
    Returns {text_id: text_content}
    """
    texts_dir = Path(config.TEXTS_DIR)
    texts = {}

    text_files = sorted(texts_dir.glob('text*.txt'))
    if num_texts:
        text_files = text_files[:num_texts]

    for text_file in text_files:
        text_id = text_file.stem  # 'text1', 'text2', etc.
        texts[text_id] = load_text(str(text_file))

    return texts


def generate_with_ollama(model: str, prompt: str) -> Tuple[str, float, int, int]:
    """
    Call Ollama API to generate a summary.

    Args:
        model: Model name (e.g., 'llama3.2:3b')
        prompt: The full prompt (including source text)

    Returns:
        (generated_text, seconds_elapsed, prompt_tokens, completion_tokens)
    """
    payload = {
        "model": model,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "stream": False,
        "options": {
            "temperature": config.TEMPERATURE,
            "num_predict": config.NUM_PREDICT,
            "top_p": config.TOP_P,
        },
        "keep_alive": config.OLLAMA_KEEP_ALIVE,
    }

    start_time = time.time()
    try:
        response = requests.post(config.OLLAMA_API_URL, json=payload, timeout=300)
        response.raise_for_status()
        elapsed = time.time() - start_time

        data = response.json()
        generated_text = data.get('message', {}).get('content', '')
        prompt_tokens = data.get('prompt_eval_count', 0)
        completion_tokens = data.get('eval_count', 0)

        return generated_text, elapsed, prompt_tokens, completion_tokens

    except requests.exceptions.RequestException as e:
        elapsed = time.time() - start_time
        raise RuntimeError(f"Ollama API error: {e}")


def combination_exists(model: str, text_id: str, run: int, strategy: str, csv_path: str) -> bool:
    """Check if (model, text_id, run, strategy) already exists in CSV."""
    if not os.path.exists(csv_path):
        return False

    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if (row['model'] == model and row['text_id'] == text_id and
                int(row['run']) == run and row.get('strategy', 'zero-shot') == strategy):
                return True

    return False


def write_csv_header(csv_path: str):
    """Write CSV header if file doesn't exist."""
    if not os.path.exists(csv_path):
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'model', 'text_id', 'run', 'strategy', 'output', 'seconds',
                'prompt_tokens', 'completion_tokens', 'timestamp'
            ])
            writer.writeheader()


def append_result(csv_path: str, model: str, text_id: str, run: int, strategy: str,
                  output: str, seconds: float, prompt_tokens: int, completion_tokens: int):
    """Append a single result to the CSV."""
    timestamp = datetime.utcnow().isoformat()

    with open(csv_path, 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'model', 'text_id', 'run', 'strategy', 'output', 'seconds',
            'prompt_tokens', 'completion_tokens', 'timestamp'
        ])
        writer.writerow({
            'model': model,
            'text_id': text_id,
            'run': run,
            'strategy': strategy,
            'output': output,
            'seconds': f"{seconds:.2f}",
            'prompt_tokens': prompt_tokens,
            'completion_tokens': completion_tokens,
            'timestamp': timestamp,
        })


def run_experiments(pilot: bool = False):
    """
    Run the full experiment or pilot.

    Pilot: 1 text × all models × 2 runs → estimate time
    Full: 5 texts × 4 models × 10 runs = 200 generations
    """
    # Load source texts
    num_texts = config.PILOT_TEXTS if pilot else config.NUM_TEXTS
    texts = load_all_texts(num_texts)

    if not texts:
        print("ERROR: No text files found in data/texts/")
        return

    num_runs = config.PILOT_RUNS if pilot else config.RUNS
    mode = "PILOT" if pilot else "FULL"

    print(f"\n{'='*60}")
    print(f"Starting {mode} experiment run")
    print(f"{'='*60}")
    print(f"Texts: {len(texts)}, Models: {len(config.MODELS)}, Strategies: {len(config.PROMPT_STRATEGIES_TO_USE)}, Runs: {num_runs}")
    print(f"Total generations: {len(texts) * len(config.MODELS) * len(config.PROMPT_STRATEGIES_TO_USE) * num_runs}")
    print(f"Strategies: {', '.join(config.PROMPT_STRATEGIES_TO_USE)}")
    print(f"Output CSV: {config.RAW_OUTPUTS_CSV}")
    print(f"{'='*60}\n")

    # Ensure output directory exists
    os.makedirs(config.RESULTS_DIR, exist_ok=True)
    write_csv_header(config.RAW_OUTPUTS_CSV)

    total_combinations = len(texts) * len(config.MODELS) * num_runs
    processed = 0
    failed = 0
    skipped = 0
    start_time = time.time()

    # Outer loop: model (so each model loads once)
    for model_idx, model in enumerate(config.MODELS):
        print(f"\n[{model_idx + 1}/{len(config.MODELS)}] Loading model: {model}")
        model_start = time.time()

        for text_id, source_text in texts.items():
            for strategy in config.PROMPT_STRATEGIES_TO_USE:
                for run_num in range(1, num_runs + 1):
                    # Check if already done
                    if combination_exists(model, text_id, run_num, strategy, config.RAW_OUTPUTS_CSV):
                        skipped += 1
                        print(f"  ✓ {model} / {text_id} / {strategy} / run {run_num} (cached)")
                        continue

                    prompt = config.PROMPTING_STRATEGIES[strategy].format(text=source_text)

                    try:
                        print(f"  {model} / {text_id} / {strategy} / run {run_num}...", end='', flush=True)
                        output, elapsed, prompt_tokens, completion_tokens = generate_with_ollama(model, prompt)

                        append_result(
                            config.RAW_OUTPUTS_CSV,
                            model, text_id, run_num, strategy,
                            output, elapsed, prompt_tokens, completion_tokens
                        )

                        print(f" ✓ {elapsed:.1f}s")
                        processed += 1

                    except Exception as e:
                        print(f" ✗ ERROR: {e}")
                        failed += 1
                        # Retry once
                        try:
                            print(f"    Retrying...", end='', flush=True)
                            output, elapsed, prompt_tokens, completion_tokens = generate_with_ollama(model, prompt)
                            append_result(
                                config.RAW_OUTPUTS_CSV,
                                model, text_id, run_num, strategy,
                                output, elapsed, prompt_tokens, completion_tokens
                            )
                            print(f" ✓ {elapsed:.1f}s")
                            processed += 1
                            failed -= 1
                        except Exception as e2:
                            print(f" ✗ FAILED: {e2}")

        model_elapsed = time.time() - model_start
        print(f"  Model {model} took {model_elapsed:.1f}s")

    total_elapsed = time.time() - start_time

    print(f"\n{'='*60}")
    print(f"Experiment complete!")
    print(f"Processed: {processed}, Failed: {failed}, Skipped: {skipped}")
    print(f"Total time: {total_elapsed:.1f}s ({total_elapsed/60:.1f} min)")
    if processed > 0:
        avg_per_gen = total_elapsed / processed
        print(f"Average per generation: {avg_per_gen:.1f}s")
        if pilot:
            estimated_full = avg_per_gen * config.NUM_TEXTS * len(config.MODELS) * config.RUNS
            print(f"Estimated time for full run (5 texts × 4 models × 10 runs): {estimated_full/3600:.1f}h")
    print(f"{'='*60}\n")


def main():
    parser = argparse.ArgumentParser(
        description="Run text generation experiments with Ollama"
    )
    parser.add_argument(
        '--pilot',
        action='store_true',
        help='Run pilot mode (1 text, all models, 2 runs) to estimate time'
    )

    args = parser.parse_args()

    try:
        run_experiments(pilot=args.pilot)
    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Results saved to CSV so far.")
        sys.exit(0)
    except Exception as e:
        print(f"\nFATAL ERROR: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

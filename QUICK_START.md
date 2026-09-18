# Quick Start Guide

## TL;DR – Run in 4 steps

### Step 1: Activate Python environment and install dependencies (one-time)
```bash
cd /Users/mac/Downloads/Homework\ 1
source venv/bin/activate
pip install requests pandas numpy matplotlib scipy rouge-score
```

### Step 2: Make sure Ollama is running
```bash
# In a separate terminal, start Ollama:
ollama serve

# In another terminal, verify it's working:
curl http://localhost:11434/api/tags
```

### Step 3: Paste your text and run pilot
```bash
# Copy your autonomous vehicles text from Homework 1 attempt 1
# Paste it into: data/texts/text1.txt

# Run a quick test to estimate time (1 text, 4 models, 2 runs each):
python src/run_experiments.py --pilot
```

### Step 4: Run full experiment and analyze
```bash
# Wait for pilot to finish. It should take 5-10 minutes.
# It will show you estimated time for the full run.

# If time is acceptable, run the full experiment:
python src/run_experiments.py

# After it completes (2-3 hours), analyze results:
python src/analyze.py

# Open figures in figures/ folder
# Check results/summary_table.csv for statistics
# Check results/examples.md for qualitative examples
```

## What gets saved?

- `results/raw_outputs.csv` – Every generated summary (model, text, run #, output, speed)
- `results/metrics.csv` – All metrics for each summary
- `results/summary_table.csv` – Per-model statistics (mean ± SD)
- `results/examples.md` – Best, worst, and typical examples
- `figures/fig*.png` – Charts for your report

## If something breaks

**Ollama not running?**
```bash
ollama serve
```

**Model not found?**
```bash
ollama list
# Edit config.py to use a model from the list
```

**Need to resume after interruption?**
```bash
# Just re-run the same command. It will skip completed combinations.
python src/run_experiments.py
```

**Want to start over?**
```bash
rm results/raw_outputs.csv
python src/run_experiments.py
```

## For your report

The experiment addresses all four points of professor feedback:

1. ✓ **Plan diagram** – See `figures/experiment_plan.png` after analysis
2. ✓ **Clearer recommendations** – All recommendations are linked to metrics/figures
3. ✓ **Use an API** – Ollama REST API (free, local, no credits)
4. ✓ **More thorough study** – 5 texts × 4 models × 10 runs = 200 generations (not 3)

## Next: Write your report

Sections map to results files:

- **1.1 Objective & Systems** – Use `config.py`
- **1.5 Experiment plan** – Use diagram after running `analyze.py`
- **2.1 Test cases** – Describe texts 1-5
- **2.2 Parameters** – Use `config.py` + Ollama version
- **3.1 Comparison** – Use figures and `summary_table.csv`
- **3.2 System behavior** – Use statistics from analysis
- **4.2 Recommendations** – Use metrics + figures for evidence

See `plan.md` for full mapping.

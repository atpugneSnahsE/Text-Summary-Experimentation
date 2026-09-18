# Text Generation Experiment (Local, Zero-Cost, Scalable)

## Overview

This experiment compares how different small open-source LLMs perform on English text summarization using a local Ollama API. It measures quality, consistency across runs, and faithfulness to key facts.

**Key constraint:** Zero cost, reproducible, runs on CPU (MacBook Pro 2020, Intel i7).

## Setup (One-time)

### 1. Install Ollama

Download from [https://ollama.com/download](https://ollama.com/download) (macOS app).

```bash
ollama --version  # Verify installation
```

### 2. Pull Models (a few GB each; needs internet once)

```bash
ollama pull llama3.2:3b
ollama pull qwen2.5:3b
ollama pull gemma2:2b
ollama pull phi3:mini
```

Check available models:
```bash
ollama list
```

If any model is unavailable, find an alternative 2–4B model from [ollama.com/library](https://ollama.com/library) and edit `config.py` to update the model tag.

### 3. Python Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install requests pandas numpy matplotlib scipy rouge-score
```

### 4. Prepare Source Texts

- **Text 1:** Copy-paste your autonomous-vehicles text into `data/texts/text1.txt`
- **Texts 2–5:** Already provided (AI, vaccine distribution, supply chains, ocean acidification)

Verify:
```bash
ls data/texts/text*.txt
```

## Running Experiments

### Option A: Pilot Run (Fast, 1 text × 4 models × 2 runs)

Estimates time before running the full experiment:

```bash
python src/run_experiments.py --pilot
```

Expected output: ~5 minutes on this CPU. Shows estimated time for full run.

### Option B: Full Run (200 generations)

```bash
python src/run_experiments.py
```

**Recommendation:** Run in background so the Mac doesn't sleep:
```bash
caffeinate -i python src/run_experiments.py
```

Expected time: 2–3 hours (on MacBook Pro 2020).

**Resume-safe:** If interrupted, re-running the command skips already-completed (model, text, run) combinations and continues.

### Monitoring Progress

Raw outputs are saved to `results/raw_outputs.csv` as they complete:
```bash
wc -l results/raw_outputs.csv  # Count rows; header + N generations
```

## Post-Processing and Analysis

After generations complete:

```bash
python src/analyze.py
```

This produces:

- `results/metrics.csv` – All metrics for every output
- `results/summary_table.csv` – Per-model statistics (mean ± SD)
- `results/examples.md` – 3 qualitative examples (best, worst, typical)
- `figures/fig1_*.png` – Box plots, heatmaps, scatter plots

## Metrics Explained

All metrics are from *Saini & Sengupta (2024)*:

| Metric | Range | Meaning |
|--------|-------|---------|
| **Summary Score (S_SS)** | 0–100 | Aggregate quality: average of normalized entropy, readability, cohesion, coherence |
| **Word Count** | — | Total words in summary |
| **Sentences** | — | Number of sentences (should be 3–5 per prompt) |
| **Lexical Density** | 0–100% | Unique words / total words; higher = richer vocabulary |
| **Text Entropy** | 0–8 bits/char | Information density; higher = more vocabulary diversity |
| **Readability** | 0–100 | Flesch Reading Ease; higher = easier to read |
| **Cohesion** | 0–100 | Sentence structure quality |
| **Coherence** | 0–100 | Repetition analysis; higher = less repetitive |
| **Compression Ratio** | 0–1 | Summary words / source words |
| **Fact Coverage** | 0–1 | Fraction of key facts found in summary (regex/keyword match) |
| **Length Compliant** | True/False | Does summary have 3–5 sentences? |

**Note:** Surface metrics (entropy, lexical density, etc.) measure *readability*, not *truthfulness*. Facts coverage and manual spot-checking assess factual accuracy.

## Folder Structure

```
hw1/
├── config.py                         # Model list, hyperparameters, paths
├── data/
│   ├── texts/
│   │   ├── text1.txt                 # Autonomous vehicles (paste yours here)
│   │   ├── text2.txt                 # AI and spending
│   │   ├── text3.txt                 # Vaccine distribution
│   │   ├── text4.txt                 # Supply chains
│   │   └── text5.txt                 # Ocean acidification
│   ├── references/                   # Optional: human-written 3–5 sentence summaries for ROUGE
│   └── facts.json                    # Key facts per text (for coverage checking)
├── src/
│   ├── run_experiments.py            # Generate summaries via Ollama API
│   ├── metrics.py                    # All metric calculations
│   └── analyze.py                    # Post-process, compute stats, make figures
├── results/
│   ├── raw_outputs.csv               # Generated: model, text_id, run, output, seconds, tokens
│   ├── metrics.csv                   # Generated: metrics for each output
│   ├── summary_table.csv             # Generated: per-model statistics
│   └── examples.md                   # Generated: best/worst/typical outputs
├── figures/
│   ├── fig1_summary_score_by_model.png
│   ├── fig2_facts_coverage_by_model.png
│   ├── fig3_compression_ratio.png
│   ├── fig4_coverage_heatmap.png
│   └── fig5_efficiency_tradeoff.png
├── docs/
│   └── experiment_plan.mmd           # Optional: Mermaid diagram of experiment flow
├── README.md                         # This file
├── plan.md                           # Original plan from professor feedback
├── summary_score_tool.html           # Original web tool (reference)
└── venv/                             # Python virtual environment
```

## Troubleshooting

### Ollama not responding
- Verify Ollama is running: `curl http://localhost:11434/api/tags`
- Start Ollama: `ollama serve`

### Model not found
- List available models: `ollama list`
- Edit `config.py` and substitute a similar 2–4B model

### Memory issues
- Close other applications (especially heavy browsers, Xcode)
- Reduce `RUNS` in `config.py` to 5 or 7

### CSV parsing errors
- Delete corrupted `results/raw_outputs.csv` and re-run (will regenerate from scratch)

## Key Design Decisions

1. **Ollama local API** instead of paid APIs (free, no rate limits, reproducible)
2. **Small quantized models** (2–4B) run on CPU in 20–60s per generation
3. **Immediate CSV append** per output (resume-safe if interrupted)
4. **Non-parametric stats** (Kruskal-Wallis) because metric scores are not normally distributed
5. **No system prompt** – tests raw model behavior on a simple task
6. **Temperature 0.7** – ensures run-to-run variation is real, justifying 10 repetitions

## Limitations to Acknowledge in Report

- Small quantized models on CPU → results don't generalize to large commercial models (ChatGPT, Gemini, Claude)
- Model size differs (2B vs 3.8B) → size is a confound; discuss or group by size
- Surface metrics don't measure truthfulness; key-fact regex can miss valid paraphrases → manually sample-check ~20 outputs
- English text only, summarization task only, 5 source texts
- Temperature 0.7 means results vary per run (why 10 repetitions are needed)
- Human-written references (if used for ROUGE) are subjective

## Video Outline (7 minutes)

0:00–0:45  | Objective + feedback addressed  
0:45–1:45  | Experiment plan diagram; constants vs. one variable (model)  
1:45–2:45  | Setup: Ollama, models, parameters  
2:45–5:15  | Results: 3–4 figures + qualitative example  
5:15–6:15  | Limitations  
6:15–7:00  | Clear recommendations with evidence (metric + value per recommendation)  

## References

Saini, M., & Sengupta, E. (2024). "Artificial intelligence inspired fog-cloud-based visual-assistance framework for blind and visually-impaired people." *Multimedia Tools and Applications*. DOI: 10.1007/s11042-024-20159-1

## Contact

Questions about setup? Check Ollama docs: [https://github.com/ollama/ollama](https://github.com/ollama/ollama)

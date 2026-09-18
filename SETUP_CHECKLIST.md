# Setup Checklist

Before running experiments, verify each item.

**All files are ready.** Just follow the steps below:

## Environment Setup

- [ ] Ollama installed (`ollama --version` works)
- [ ] All 4 models pulled:
  - [ ] `ollama pull llama3.2:3b`
  - [ ] `ollama pull qwen2.5:3b`
  - [ ] `ollama pull gemma2:2b`
  - [ ] `ollama pull phi3:mini`
- [ ] Python virtual environment created (`.venv` folder exists)
- [ ] Dependencies installed:
  ```bash
  source .venv/bin/activate
  pip install requests pandas numpy matplotlib scipy rouge-score
  ```

## Project Structure

Verify files exist:

- [ ] `config.py` – Model list and hyperparameters
- [ ] `src/run_experiments.py` – Experiment runner
- [ ] `src/metrics.py` – Metric calculations
- [ ] `src/analyze.py` – Post-processing and figures
- [ ] `data/texts/text1.txt` – **Paste your autonomous vehicles text here**
- [ ] `data/texts/text2.txt` – AI and spending (auto-generated)
- [ ] `data/texts/text3.txt` – Vaccine distribution (auto-generated)
- [ ] `data/texts/text4.txt` – Supply chains (auto-generated)
- [ ] `data/texts/text5.txt` – Ocean acidification (auto-generated)
- [ ] `data/facts.json` – Key facts for coverage checking
- [ ] `README.md` – Full documentation
- [ ] `QUICK_START.md` – Quick start guide

## Before First Run

1. [ ] **IMPORTANT:** Replace `data/texts/text1_template.txt` content with your actual autonomous vehicles text from Homework 1 attempt 1, OR rename/replace `text1.txt`

2. [ ] Verify texts exist:
   ```bash
   ls -lh data/texts/text*.txt
   ```

3. [ ] Verify facts configuration:
   ```bash
   python3 -c "import json; f=json.load(open('data/facts.json')); print(f'Loaded facts for {len(f)} texts')"
   ```

4. [ ] Test metrics module:
   ```bash
   python3 -c "from src.metrics import calculate_all_metrics; print(calculate_all_metrics('Test text for metric calculation.'))"
   ```

## Pilot Run (Recommended First)

```bash
# Start Ollama in another terminal:
ollama serve

# In this terminal:
source .venv/bin/activate
python src/run_experiments.py --pilot
```

Expected time: 5–10 minutes  
Output: `results/raw_outputs.csv` with 8 rows (1 text × 4 models × 2 runs)

## Full Run

```bash
# After pilot succeeds:
caffeinate -i python src/run_experiments.py
```

Expected time: 2–3 hours  
Output: `results/raw_outputs.csv` with 201 rows (header + 200 generations)

## Post-Processing

```bash
# After full run completes:
python src/analyze.py
```

Expected output:
- `results/metrics.csv` – Metrics for all 200 outputs
- `results/summary_table.csv` – Per-model statistics
- `results/examples.md` – Qualitative examples
- `figures/fig1_*.png`, `fig2_*.png`, etc. – Charts for your report

## Verification Checks

After analysis:

- [ ] `results/raw_outputs.csv` has ~201 rows (1 header + 200 data)
- [ ] `results/metrics.csv` has all metric columns populated
- [ ] `results/summary_table.csv` shows mean/std for each model
- [ ] `figures/` folder contains 5+ PNG files
- [ ] `results/examples.md` has 3 examples with model, text_id, run #, S_SS score

## Common Issues & Solutions

**Ollama not running?**
```bash
# Start it:
ollama serve
```

**Model not found?**
```bash
# List available:
ollama list

# Edit config.py to use what's available
```

**Port 11434 already in use?**
```bash
# Check what's using it:
lsof -i :11434

# Kill it if needed:
kill -9 <PID>
```

**CSV file corrupted?**
```bash
# Delete it and restart:
rm results/raw_outputs.csv
python src/run_experiments.py
```

**Out of memory?**
```bash
# Close heavy apps (Xcode, Chrome, etc.)
# Or reduce RUNS in config.py to 5 or 7
```

## Report Mapping

Once analysis completes, you have data for all sections:

| Report Section | Source File |
|---|---|
| 1.1 Objective | `plan.md` section 2 |
| 1.2 Systems | `config.py` |
| 1.3 Variables/Constants | `config.py` + `plan.md` |
| 1.4 Domain | *Student fills in* |
| 1.5 Experiment Plan | `docs/experiment_plan.mmd` + diagram from `analyze.py` output |
| 2.1 Test Cases | Descriptions of texts 1–5 |
| 2.2 Parameters | `config.py` table |
| 2.3 Results | 3 examples from `results/examples.md` |
| 3.1 Comparison | Figures 1–4 from `figures/` |
| 3.2 System Behavior | Statistics from `results/summary_table.csv` |
| 3.3 Limitations | See `plan.md` section 6 |
| 4.1 Summary | 3–4 sentences + numbers |
| 4.2 Recommendations | Each: situation → model → evidence (metric + value) |

---

✅ **All items checked?** You're ready to run experiments!

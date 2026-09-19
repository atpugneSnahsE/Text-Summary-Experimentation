# Experiment Design: Evaluating Small LLMs on Text Summarization

## 1. Research Objective

Evaluate and compare the performance of small open-source Large Language Models (2–4B parameters) on English text summarization across different prompting strategies. Specifically, assess:
- **Model quality**: Which model produces the best summaries?
- **Strategy effectiveness**: How does prompting approach (zero-shot vs. few-shot vs. chain-of-thought) affect summary quality?
- **Consistency**: How stable is each model-strategy combination across multiple runs?
- **Faithfulness**: How well do summaries preserve key facts from source texts?

## 2. Experimental Variables

### Independent Variables (Manipulated)

**Primary Variable: Prompting Strategy** (3 levels)
1. **Zero-shot**: Direct instruction without examples
   - Prompt: "Summarize the following in 3-5 sentences.\n\n{text}"
   - Tests raw model capability on task

2. **Few-shot**: 2 worked examples before target text
   - Includes 2 example text-summary pairs
   - Tests model's ability to learn from examples in-context

3. **Chain-of-thought with role**: Step-by-step reasoning with role assignment
   - Asks model to identify main topic, key concepts, then summarize
   - Tests structured thinking approach

**Secondary Variable: Model** (4 levels)
- `llama3.2:3b` (Meta, 3 billion parameters)
- `qwen2.5:3b` (Alibaba, 3 billion parameters)
- `gemma2:2b` (Google, 2 billion parameters)
- `phi3:mini` (Microsoft, 3.8 billion parameters)

### Dependent Variables (Measured)

**Quality Metrics** (from Saini & Sengupta 2024):
- **Summary Score (S_SS)** - Aggregate quality (0–100)
- **Text Entropy** - Information density (0–8 bits/char)
- **Readability** - Flesch Reading Ease (0–100)
- **Cohesion** - Sentence structure quality (0–100)
- **Coherence** - Repetition analysis (0–100)
- **Lexical Density** - Vocabulary richness (0–100%)

**Additional Metrics**:
- **Fact Coverage** - % of key facts preserved (0–1)
- **Compression Ratio** - Summary words / source words (0–1)
- **Length Compliance** - Does summary have 3–5 sentences? (Boolean)
- **Generation Speed** - Seconds per output

### Controlled Variables (Constants)

| Variable | Value | Rationale |
|----------|-------|-----------|
| Temperature | 0.7 | Balances determinism and diversity |
| Max tokens | 200 | Enforces reasonable summary length |
| Top-p | 0.9 | Default nucleus sampling |
| Hardware | MacBook Pro 2020, Intel i7, 32GB RAM, CPU-only | Reproducible on standard hardware |
| Source texts | 5 neutral news/explainer texts | Different topics, ~200–300 words each |
| Runs per combo | 10 | Captures run-to-run variation |
| Prompt template | Fixed; only strategy varies | Isolates strategy effect |
| No system prompt | — | Tests raw model behavior |
| No chat history | Fresh requests only | Prevents context carryover |

## 3. Experimental Design

**Fully Factorial Within-Subjects Design**

```
Factors:
- 5 source texts (Text 1–5)
- 4 models
- 3 prompting strategies
- 10 repetitions per combination

Total: 5 × 4 × 3 × 10 = 600 generations
```

**Loop Order** (for efficiency):
1. Model (load once, keep in memory)
2. Strategy (prompt template changes)
3. Text (fixed source)
4. Run (replication)

**Text Descriptions**:
- **Text 1**: Autonomous vehicles (LiDAR cost, sensor suites, Tesla vs. Waymo)
- **Text 2**: AI spending (2023: $100B, 38% growth, US/China leadership)
- **Text 3**: Vaccine distribution (10-15 years → <1 year, equity gap)
- **Text 4**: Supply chains (shipping costs 1.5K→10K, Taiwan semiconductors, CHIPS Act)
- **Text 5**: Ocean acidification (pH decrease, Great Barrier Reef bleaching, 2050 deadline)

Each text contains 4–5 checkable facts for coverage evaluation.

## 4. Data Collection

**Raw Outputs**: `results/raw_outputs.csv`
- Columns: model, text_id, strategy, run, output, seconds, prompt_tokens, completion_tokens, timestamp
- One row per generation
- Immediate append (resume-safe if interrupted)

**Metrics Computation**: `results/metrics.csv`
- Calculated metrics for each output
- Columns: all raw output fields + S_SS, entropy, readability, cohesion, coherence, lexical_density, compression_ratio, facts_coverage, length_compliant

## 5. Statistical Analysis Plan

### Descriptive Statistics
- Per model × strategy: mean ± SD of each metric
- Per strategy: overall mean, std dev, min, max

### Inferential Statistics
**Kruskal-Wallis H-test** (non-parametric, one-way ANOVA)
- Null: No difference in S_SS across models
- Null: No difference in S_SS across strategies
- If significant (p < 0.05): pairwise Mann-Whitney U tests with Bonferroni correction

**Rationale**: Metric distributions are non-normal; Kruskal-Wallis is more robust.

### Consistency Analysis
- Coefficient of variation (SD / mean) of S_SS within each model-strategy pair
- Tests stability across the 10 runs
- Higher CV = less consistent

### Visualization
- Box plots: S_SS by model (all strategies pooled)
- Box plots: S_SS by strategy (all models pooled)
- Heatmap: mean fact coverage × model × strategy
- Bar charts: mean compression ratio by model-strategy
- Scatter: speed (seconds) vs. coverage (efficiency trade-off)
- Line plots: S_SS across strategies per model

## 6. Limitations

1. **Generalization**: Small quantized models on CPU ≠ large commercial models (ChatGPT, Claude, Gemini)
2. **Confound**: Model size varies (2B–3.8B); discussed separately from strategy effects
3. **Surface metrics**: S_SS measures readability, not factual correctness; fact coverage uses regex, may miss paraphrases
4. **Scope**: English only, summarization task only, 5 source texts, 10 runs per combo
5. **Variability**: Temperature 0.7 ensures run-to-run variation; 10 runs justify statistical testing
6. **Reference texts**: Human-written references (if used for ROUGE) are subjective

## 7. Expected Outcomes & Hypotheses

**H1**: Chain-of-thought strategy improves S_SS vs. zero-shot (explicit reasoning helps)
**H2**: Few-shot strategy helps models with strong in-context learning (esp. Qwen, Llama)
**H3**: Larger models (Phi3 at 3.8B) outperform smaller ones (Gemma2 at 2B)
**H4**: Strategy effect is consistent across all models (no model × strategy interaction)
**H5**: Consistency (low SD) is highest for zero-shot (simplest, most deterministic)

## 8. Implementation Timeline

| Phase | Time | Task |
|-------|------|------|
| Setup | 15 min | Ollama, models, Python env |
| Pilot | 30 min | 1 text × 4 models × 3 strategies × 2 runs = 24 outputs; estimate full time |
| Full Run | 6–9 h | 600 generations (caffeinate overnight) |
| Analysis | 5 min | Calculate metrics, stats, generate figures |
| Writing | — | Draft report with evidence from results |

**Estimated Total**: ~7–10 hours active time

## 9. Deliverables

- `results/raw_outputs.csv` – All 600 generated summaries
- `results/metrics.csv` – Computed metrics for each
- `results/summary_table.csv` – Per-model-strategy statistics
- `results/examples.md` – 3 qualitative examples (best, worst, typical)
- `figures/` – 5+ publication-quality charts
- Report sections with evidence-based recommendations

## 10. Reproducibility

**To reproduce:**
```bash
ollama pull llama3.2:3b qwen2.5:3b gemma2:2b phi3:mini
python -m venv venv
source venv/bin/activate
pip install requests pandas numpy matplotlib scipy rouge-score
python src/run_experiments.py
python src/analyze.py
```

All parameters, models, and prompts are version-controlled in `config.py`.
Results are saved to CSV immediately (resumable if interrupted).

---

**Reference**: Saini, M., & Sengupta, E. (2024). "Artificial intelligence inspired fog-cloud-based visual-assistance framework for blind and visually-impaired people." *Multimedia Tools and Applications*. DOI: 10.1007/s11042-024-20159-1

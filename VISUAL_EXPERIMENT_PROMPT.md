# Prompt to Generate Experiment Flow Visualization

## Use this prompt with Claude or a diagramming tool to create a visual flowchart

---

## Visual Flowchart Prompt

**Create a professional flowchart diagram showing the experimental workflow for a text summarization study. Follow this exact structure:**

### Main Flow (left to right)

**START**
↓
**Input Data**
- Box 1: "5 Source Texts"
  - Text 1: Autonomous Vehicles
  - Text 2: AI Spending
  - Text 3: Vaccine Distribution
  - Text 4: Supply Chains
  - Text 5: Ocean Acidification

↓
**Prompting Strategies** (branching into 3 paths)
- Branch A: "Zero-Shot" (direct instruction)
- Branch B: "Few-Shot" (2 examples provided)
- Branch C: "Chain-of-Thought" (step-by-step reasoning with role)

↓
**Model Selection** (4 models applied to each strategy)
- Model 1: Llama 3.2 (3B)
- Model 2: Qwen 2.5 (3B)
- Model 3: Gemma 2 (2B)
- Model 4: Phi 3 Mini (3.8B)

↓
**Experiment Execution**
- Box: "For each combination:"
- "10 Repetitions per (Text × Strategy × Model)"
- "Total: 5 × 3 × 4 × 10 = 600 Generations"

↓
**Data Collection**
- Box: "results/raw_outputs.csv"
- Columns: model, text_id, strategy, run, output, seconds, tokens

↓
**Metrics Computation**
- Multiple metrics calculated per output:
  - S_SS (Summary Score) | Entropy | Readability
  - Cohesion | Coherence | Lexical Density
  - Fact Coverage | Compression Ratio | Speed

↓
**Statistical Analysis**
- Descriptive Stats (mean ± SD per model-strategy)
- Kruskal-Wallis H-test (across models, across strategies)
- Consistency Analysis (variation within each combo)
- Pairwise Mann-Whitney tests (if significant)

↓
**Visualization & Output**
- Box plots: S_SS by model, S_SS by strategy
- Heatmap: Coverage × Model × Strategy
- Bar charts: Compression ratio, speed
- Scatter plots: Efficiency trade-offs
- Line charts: Strategy effects per model

↓
**End Result**
- Box: "Summary Table + Charts + Report"
- "Evidence-based recommendations for each situation"

---

## Design Features to Highlight

1. **Color Coding by Section**:
   - Green: Input data (top)
   - Blue: Experimental variables (strategies, models)
   - Yellow: Execution (repetitions, data collection)
   - Orange: Analysis (metrics, statistics)
   - Red: Output (visualizations, reports)

2. **Numerical Annotations**:
   - 5 texts
   - 3 strategies (branching point)
   - 4 models
   - 10 runs per combo
   - **600 total generations**

3. **Key Constants Box** (on the side):
   - Temperature: 0.7
   - Max tokens: 200
   - Hardware: CPU-only (MacBook Pro 2020)
   - No system prompt
   - Fresh requests (no chat history)

4. **Dimensions of Analysis** (center annotation):
   ```
   Model × Strategy × Text × Run
   4    ×    3      ×  5  ×  10  = 600
   ```

---

## Alternative: Simple Table-Based Visualization

If a flowchart is complex, use this 2×3 grid instead:

```
┌─────────────────────────────────────┐
│   EXPERIMENTAL VARIABLES & DESIGN   │
├─────────────────────────────────────┤
│ INDEPENDENT VARIABLES               │
│ ├─ Strategy: Zero-shot / Few-shot / CoT (3 levels)
│ ├─ Model: Llama / Qwen / Gemma / Phi (4 levels)
│ └─ Text: Text 1–5 (5 levels)
│                                      │
│ DEPENDENT VARIABLES                 │
│ ├─ Summary Score (primary)
│ ├─ Fact Coverage, Readability, Speed
│ └─ Consistency (SD across 10 runs)
│                                      │
│ CONTROLLED VARIABLES                │
│ ├─ Temperature: 0.7, Tokens: 200
│ ├─ Hardware: CPU-only (MacBook Pro)
│ └─ Prompt template (only strategy varies)
│                                      │
│ EXPERIMENTAL MATRIX                 │
│ 5 texts × 4 models × 3 strategies × 10 runs = 600 outputs
│                                      │
│ ANALYSIS PIPELINE                   │
│ Raw CSV → Metrics → Statistics → Visualizations → Report
│                                      │
│ EXPECTED OUTCOME                    │
│ "For [situation], use [Model X]:    │
│  [Metric] = [value], p < [sig]"     │
└─────────────────────────────────────┘
```

---

## Example Mermaid Syntax (if using Claude's diagram tool)

```
graph TD
    A["5 Source Texts<br/>(Autonomous Vehicles,<br/>AI, Vaccines,<br/>Supply Chain, Ocean)"]
    A --> B["Strategy: Zero-Shot<br/>(Direct Prompt)"]
    A --> C["Strategy: Few-Shot<br/>(2 Examples)"]
    A --> D["Strategy: Chain-of-Thought<br/>(Step-by-Step)"]
    
    B --> E["Model 1: Llama 3.2<br/>Model 2: Qwen 2.5<br/>Model 3: Gemma 2<br/>Model 4: Phi 3 Mini"]
    C --> E
    D --> E
    
    E --> F["10 Repetitions<br/>per Combination"]
    F --> G["600 Total Generations"]
    
    G --> H["Calculate Metrics<br/>(S_SS, Coverage,<br/>Readability, Speed)"]
    H --> I["Statistical Analysis<br/>(Kruskal-Wallis,<br/>Mann-Whitney)"]
    I --> J["Generate Visualizations<br/>(Charts, Heatmaps,<br/>Box Plots)"]
    J --> K["Report + Recommendations<br/>(Model X for Situation Y<br/>with Evidence)"]
    
    style A fill:#90EE90
    style B fill:#87CEEB
    style C fill:#87CEEB
    style D fill:#87CEEB
    style E fill:#FFD700
    style F fill:#FFD700
    style G fill:#FFD700
    style H fill:#FFA500
    style I fill:#FFA500
    style J fill:#FFA500
    style K fill:#FF6B6B
```

---

## Tips for Generating the Chart

**Using Claude's Visualization Tool:**
1. Copy this prompt
2. Ask: "Create a professional flowchart diagram based on the 'Visual Flowchart Prompt' section above"
3. Request format: SVG, PNG, or interactive HTML
4. Add annotations: "Include the 600-generation count prominently"

**Using Mermaid Online (mermaid.live):**
- Paste the example Mermaid syntax provided above
- Customize colors and layout

**Using PowerPoint/Canva:**
- Use the "Simple Table-Based Visualization" grid
- Create boxes for each section
- Add arrows showing data flow

---

## What the Chart Should Communicate

✓ **5 distinct source texts** (different topics)
✓ **3 prompting strategies** (the new primary variable)
✓ **4 models** (secondary variable)
✓ **10 repetitions** (why variation exists)
✓ **600 total combinations** (scale of study)
✓ **Metrics computed per output** (what gets measured)
✓ **Statistical tests applied** (rigor)
✓ **Final output format** (evidence-based recommendations)

The chart should visually show that:
- Each text goes through each strategy
- Each strategy is applied to each model
- Each model-strategy-text combo runs 10 times
- All outputs get metrics calculated
- All metrics get statistically analyzed
- Results inform recommendations

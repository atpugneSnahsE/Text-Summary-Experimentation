"""
Configuration for text generation experiment.
Models, parameters, paths, and experiment settings.
"""

# Ollama API endpoint
OLLAMA_API_URL = "http://localhost:11434/api/chat"
OLLAMA_KEEP_ALIVE = "30m"  # Keep model in memory for 30 minutes

# Models to test (small models, 2-4B parameters, CPU-friendly)
MODELS = [
    "llama3.2:3b",
    "qwen2.5:3b",
    "gemma2:2b",
    "phi3:mini",
]

# Generation parameters (constants across all runs)
TEMPERATURE = 0.7
NUM_PREDICT = 200  # Max tokens
TOP_P = 0.9  # Default top_p

# Experiment repetitions and test cases
RUNS = 10  # Repetitions per (model, text) combination
NUM_TEXTS = 5  # Target number of source texts (can extend to 10)

# Prompting strategies (new experimental variable)
PROMPTING_STRATEGIES = {
    "zero-shot": "Summarize the following in 3-5 sentences.\n\n{text}",

    "few-shot": """Here are two examples of good summaries:

Example 1:
Text: Climate change is affecting global weather patterns. Rising temperatures cause extreme heat waves in summer and unusual cold snaps in winter. Precipitation patterns are shifting, with some regions experiencing droughts and others facing flooding.
Summary: Climate change is intensifying weather extremes globally. Rising temperatures trigger severe heat waves and unexpected cold snaps. Shifting precipitation patterns are causing both droughts and floods in different regions.

Example 2:
Text: Artificial intelligence is transforming industries by automating tasks and improving decision-making. Machine learning models can now recognize images, process language, and predict outcomes. However, AI raises concerns about job displacement and algorithmic bias.
Summary: AI is revolutionizing industries through automation and enhanced decision-making. Machine learning now excels at image recognition, language processing, and outcome prediction. Yet AI adoption raises important questions about employment and algorithmic fairness.

Now summarize the following in 3-5 sentences:
{text}""",

    "chain-of-thought": """You are an expert summarizer. Your task is to analyze the text carefully and provide a concise, accurate summary.

Follow these steps:
1. Identify the main topic and key concepts
2. Note the most important facts and ideas
3. Consider what a reader absolutely needs to know
4. Write a clear 3-5 sentence summary that captures the essence

Text to summarize:
{text}

Think through the key points, then provide your summary:"""
}

# Use all strategies or just one (for testing)
PROMPT_STRATEGIES_TO_USE = list(PROMPTING_STRATEGIES.keys())  # ["zero-shot", "few-shot", "chain-of-thought"]

# Paths
DATA_DIR = "data"
TEXTS_DIR = f"{DATA_DIR}/texts"
REFERENCES_DIR = f"{DATA_DIR}/references"
RESULTS_DIR = "results"
FIGURES_DIR = "figures"
DOCS_DIR = "docs"

# Output files
RAW_OUTPUTS_CSV = f"{RESULTS_DIR}/raw_outputs.csv"
METRICS_CSV = f"{RESULTS_DIR}/metrics.csv"
SUMMARY_TABLE_CSV = f"{RESULTS_DIR}/summary_table.csv"
EXAMPLES_MD = f"{RESULTS_DIR}/examples.md"
FACTS_JSON = f"{DATA_DIR}/facts.json"

# Pilot mode: 1 text x all models x 2 runs to estimate time
PILOT_RUNS = 2
PILOT_TEXTS = 1

# Hardware info (for reporting)
HARDWARE = "MacBook Pro 2020, Intel i7, 32 GB RAM, CPU-only"
OLLAMA_VERSION = "Check with: ollama --version"

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

# Fixed prompt template
PROMPT_TEMPLATE = "Summarize the following in 3-5 sentences.\n\n{text}"

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

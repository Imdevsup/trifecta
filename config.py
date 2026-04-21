"""
Cognitive Triad Simulation — Configuration
All constants, model settings, knowledge store limits, and simulation parameters.
Edit this file to customize the experiment. See README.md for detailed guidance.

Topics are generated dynamically per day by simulation.topic_generator.TopicGenerator,
which rotates across EIGHT PhD-level domains that LLMs demonstrably struggle with:
  1. Advanced Mathematics & Mathematical Logic
  2. Theoretical Physics
  3. Formal Methods & Programming Language Theory
  4. Theoretical Computer Science & Cryptography
  5. Molecular Biology, Biochemistry & Advanced Neuroscience
  6. Analytic Philosophy & Formal Logic
  7. Quantitative Finance & Mathematical Economics
  8. Theoretical Linguistics & Formal Semantics

Day D uses domain DOMAIN_ORDER[(D - 1) % 8], so a 365-day run gives each domain
~45 days of coverage. The old hardcoded TOPIC_SCHEDULE has been removed so runs
can go for arbitrarily many days.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root
load_dotenv(Path(__file__).parent / ".env")

# --- API Configuration (OpenAI only, loaded from .env) ---
API_BASE = "https://api.openai.com/v1"
API_KEY = os.environ.get("OPENAI_API_KEY", "")
MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")

# --- Per-Agent Config (all same model) ---
AGENT_CONFIG = {
    "alpha": {"model": MODEL, "api_key": API_KEY},
    "beta":  {"model": MODEL, "api_key": API_KEY},
    "gamma": {"model": MODEL, "api_key": API_KEY},
}

# --- Knowledge Store Capacity ---
# Recalibrated for the 8-domain curriculum: roughly 2.7x the single-domain
# year-long sizes. The store still forces eviction — cross-domain competition
# for space is part of the experiment — but each domain has room to
# accumulate substantive knowledge across its ~45 scheduled days.
#
# Heritage: 30-day math-only was 50/200/100 -> 365-day math-only was 150/600/300 ->
# 365-day 8-domain is 400/1600/800. Each entry still stays short —
# gpt-4o-mini prefers dense context over walls of text.
IMPULSE_MAX_ENTRIES = 400
IMPULSE_MAX_TOKENS = 100       # ~2-3 sentences. Impulse = quick facts.

DEEP_MAX_ENTRIES = 1600
DEEP_MAX_TOKENS = 500          # ~10-15 sentences. Full reasoning chains.

AXIOM_MAX_ENTRIES = 800
AXIOM_MAX_TOKENS = 250         # ~5-8 sentences. Precise universal truth with justification.

# --- Teaching Configuration ---
LECTURE_MAX_TOKENS = 1500      # Max tokens per oracle-generated lecture (fallback only)
SUBTOPIC_MIN_LENGTH = 20       # Minimum character length for a valid subtopic

# --- Simulation Parameters ---
DEFAULT_DAYS = 365
LEARNING_QUESTIONS_PER_AGENT = 5   # Q&A after teaching (reduced since lectures cover bulk)
PEER_EXCHANGE_RANGE = (8, 12)
PEER_EXCHANGE_RANGE_FAST = (4, 6)
PEER_PAIRS = [("alpha", "beta"), ("beta", "gamma"), ("alpha", "gamma")]
PASS_THRESHOLD = 0.6
# No fixed ratios — each agent's LLM decides where to store knowledge

# --- Knowledge Injection Budgets ---
# gpt-4o-mini has 128K token window but performs WORSE with massive context.
# "Lost in the middle" problem: model focuses on start/end, ignores middle.
# Sweet spot: ~2500-5000 words of injected knowledge, leaving room for the task.
# Bumped slightly from the single-domain config so cross-domain exam retrieval
# (8 curricula worth of context) has a bit more breathing room.
DAILY_KNOWLEDGE_BUDGET_WORDS = 3000     # ~4K tokens — focused context for learning
EXAM_KNOWLEDGE_BUDGET_WORDS = 5000      # ~6K tokens — cross-domain context for final exam

# --- Phases ---
DAILY_PHASES = ["WAKE", "TEACHING", "LEARNING", "PEER_CONVERSATION", "KNOWLEDGE_SHARING", "KNOWLEDGE_MANAGEMENT", "SLEEP"]
PHASES = DAILY_PHASES + ["FINAL_TEST"]

# --- Paths ---
PROJECT_ROOT = Path(__file__).parent
DATA_DIR = PROJECT_ROOT / "data"
LOG_DB_PATH = DATA_DIR / "simulation.db"
ANALYSIS_DIR = PROJECT_ROOT / "analysis"

# --- Rate Limiting (per-model, allows parallel calls across different models) ---
MIN_CALL_INTERVAL_SECONDS = 1.0    # Per-model; light throttle since API is already slow
MAX_RETRIES = 10                   # Capped so a dead API surfaces instead of hanging for hours
RETRY_BASE_DELAY = 3               # Exponential backoff base delay in seconds
RETRY_MAX_DELAY = 60
CLIENT_TIMEOUT_SECONDS = 120

# --- Dry Run ---
DRY_RUN = False

# --- Ablation Testing ---
# Set these to True to disable specific components for ablation analysis.
# Run with --ablation flag or set directly.
ABLATION_NO_KNOWLEDGE = False       # Disable knowledge injection (agents answer raw)
ABLATION_NO_PEER_CONVERSATION = False  # Disable peer conversation phase
ABLATION_NO_AXIOM_VALIDATION = False   # Disable axiom validation pipeline
ABLATION_NO_CONSOLIDATION = False      # Disable knowledge consolidation
ABLATION_NO_KNOWLEDGE_SHARING = False  # Disable inter-agent knowledge sharing

# Stopwords for TF-IDF
STOPWORDS = {
    "a", "an", "the", "is", "it", "of", "in", "to", "and", "or", "for",
    "on", "at", "by", "with", "from", "as", "that", "this", "was", "are",
    "be", "has", "have", "had", "do", "does", "did", "but", "not", "so",
    "if", "no", "can", "will", "just", "than", "then", "its", "my", "we",
}

"""
Base Agent — Abstract base class for all cognitive units.
Handles LLM calls via OpenAI, knowledge injection from JSON + DB, and message history.
"""

import time
import logging
import threading
from abc import ABC, abstractmethod

import openai
import httpx

import config
from knowledge.store import KnowledgeStore, retrieve_from_db

logger = logging.getLogger(__name__)

# Per-model rate limiter state (allows parallel calls across different models)
_rate_limit_locks = {}
_rate_limit_last_call = {}
_rate_limit_meta_lock = threading.Lock()


def rate_limit(model: str = "default"):
    """Enforce minimum interval between API calls, per model.
    Different models can call simultaneously (3x throughput)."""
    with _rate_limit_meta_lock:
        if model not in _rate_limit_locks:
            _rate_limit_locks[model] = threading.Lock()
        lock = _rate_limit_locks[model]

    with lock:
        last = _rate_limit_last_call.get(model, 0.0)
        elapsed = time.time() - last
        if elapsed < config.MIN_CALL_INTERVAL_SECONDS:
            time.sleep(config.MIN_CALL_INTERVAL_SECONDS - elapsed)
        _rate_limit_last_call[model] = time.time()


def clean_llm_response(text: str) -> str:
    """Strip markdown code fences and extra whitespace from an LLM response.
    Agents parse line-prefixed responses; wrapping fences break that."""
    if not text:
        return ""
    stripped = text.strip()
    if stripped.startswith("```"):
        lines = stripped.split("\n")
        # Drop opening fence (may be ``` or ```json/```text/etc.)
        lines = lines[1:]
        # Drop trailing fence if present
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        stripped = "\n".join(lines).strip()
    return stripped


class BaseAgent(ABC):
    def __init__(
        self,
        name: str,
        model: str,
        api_key: str,
        stores: dict[str, KnowledgeStore],
        rng,
        db_logger=None,
    ):
        self.name = name
        self.model = model
        self.stores = stores
        self.rng = rng
        self.db_logger = db_logger
        self.message_history: list[dict] = []
        self.pending_axiom_proposals: list[dict] = []

        # Key is passed straight to the SDK and not retained on self — minimizes
        # the number of places a credential lives in process memory.
        self.client = openai.OpenAI(
            base_url=config.API_BASE,
            api_key=api_key,
            timeout=httpx.Timeout(config.CLIENT_TIMEOUT_SECONDS, connect=10.0),
            max_retries=0,
        )

    def _call_llm(
        self,
        system_prompt: str,
        messages: list[dict],
        temperature: float = 0.7,
        max_tokens: int = 512,
        day: int = 0,
        phase: str = "",
        action: str = "",
    ) -> str:
        """Call the LLM with retry on transient errors. Single model, no fallbacks."""
        if config.DRY_RUN:
            placeholder = f"[Dry-run {self.name}: {action} | day={day} phase={phase}]"
            if self.db_logger:
                self.db_logger.log_interaction(
                    day=day, phase=phase, agent=self.name, action=action,
                    prompt_preview=system_prompt, response_preview=placeholder,
                    model="dry-run",
                )
            return placeholder

        full_messages = [{"role": "system", "content": system_prompt}] + messages

        for attempt in range(config.MAX_RETRIES):
            try:
                rate_limit(self.model)
                start = time.time()
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=full_messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
                latency_ms = int((time.time() - start) * 1000)
                content = clean_llm_response(response.choices[0].message.content or "")
                tokens_in = getattr(response.usage, "prompt_tokens", 0) if response.usage else 0
                tokens_out = getattr(response.usage, "completion_tokens", 0) if response.usage else 0

                if self.db_logger:
                    self.db_logger.log_interaction(
                        day=day, phase=phase, agent=self.name, action=action,
                        prompt_preview=system_prompt, response_preview=content,
                        tokens_in=tokens_in, tokens_out=tokens_out,
                        latency_ms=latency_ms, model=self.model,
                    )
                return content

            except (openai.RateLimitError, openai.APIConnectionError, openai.APITimeoutError) as e:
                wait = min(config.RETRY_BASE_DELAY * (attempt + 1), config.RETRY_MAX_DELAY) + self.rng.uniform(0, 2)
                logger.warning(f"{self.name}: {type(e).__name__} attempt {attempt+1}/{config.MAX_RETRIES}, retrying in {wait:.0f}s...")
                time.sleep(wait)

            except Exception as e:
                wait = min(config.RETRY_BASE_DELAY * (attempt + 1), config.RETRY_MAX_DELAY) + self.rng.uniform(0, 2)
                logger.error(f"{self.name}: Error attempt {attempt+1}/{config.MAX_RETRIES}: {e}, retrying in {wait:.0f}s...")
                time.sleep(wait)

        error_msg = f"[LLM unavailable for {self.name} after {config.MAX_RETRIES} retries]"
        if self.db_logger:
            self.db_logger.log_interaction(
                day=day, phase=phase, agent=self.name, action=f"{action}_FAILED",
                prompt_preview=system_prompt, response_preview=error_msg,
                model=self.model,
            )
        return error_msg

    @abstractmethod
    def build_system_prompt(self, day: int, phase: str, topic: str) -> str:
        """Build the personality-specific system prompt."""
        pass

    def inject_knowledge(self, base_prompt: str, topic: str, include_deep: bool = False, use_bundles: bool = False) -> str:
        """Inject knowledge from JSON stores + DB into the system prompt.
        Sources: impulse, deep_thinking, axiom (JSON) + interactions & conversations (DB).
        If use_bundles=True, retrieves concept bundles (grouped related entries) for richer context.
        """
        # Ablation: skip all knowledge injection
        if config.ABLATION_NO_KNOWLEDGE:
            return base_prompt

        sections = [base_prompt, ""]

        # --- JSON STORES ---

        # IMPULSE — top relevant quick-recall facts
        if self.stores["impulse"].count() > 0:
            if use_bundles:
                bundles = self.stores["impulse"].get_concept_bundles(topic, top_k=4)
                if bundles:
                    sections.append(f"[IMPULSE MEMORY — {len(bundles)} concept bundles]")
                    for i, b in enumerate(bundles, 1):
                        sections.append(f"  {i}. {b['primary']['content']}")
                        for r in b["related"][:2]:  # max 2 related per bundle
                            sections.append(f"     > {r['content']}")
                    sections.append("")
            else:
                impulse_entries = self.stores["impulse"].retrieve_by_topic(topic, top_k=8)
                if impulse_entries:
                    sections.append(f"[IMPULSE MEMORY — {len(impulse_entries)} most relevant]")
                    for i, e in enumerate(impulse_entries, 1):
                        sections.append(f"  {i}. {e['content']}")
                    sections.append("")

        # DEEP THINKING — analytical insights with reasoning
        if include_deep and self.stores["deep_thinking"].count() > 0:
            if use_bundles:
                bundles = self.stores["deep_thinking"].get_concept_bundles(topic, top_k=3)
                if bundles:
                    sections.append(f"[DEEP KNOWLEDGE — {len(bundles)} concept bundles]")
                    for i, b in enumerate(bundles, 1):
                        sections.append(f"  {i}. {b['primary']['content']}")
                        for r in b["related"][:2]:
                            sections.append(f"     > {r['content']}")
                    sections.append("")
            else:
                deep_entries = self.stores["deep_thinking"].retrieve_by_topic(topic, top_k=5)
                if deep_entries:
                    sections.append(f"[DEEP KNOWLEDGE — {len(deep_entries)} most relevant]")
                    for i, e in enumerate(deep_entries, 1):
                        sections.append(f"  {i}. {e['content']}")
                    sections.append("")

        # AXIOM — foundational truths
        topic_keywords = [w.lower() for w in topic.split() if w.lower() not in config.STOPWORDS]
        if topic_keywords and self.stores["axiom"].count() > 0:
            axiom_entries = self.stores["axiom"].retrieve_by_keywords(topic_keywords, top_k=5)
            if axiom_entries:
                sections.append(f"[AXIOMS — {len(axiom_entries)} foundational truths]")
                for i, e in enumerate(axiom_entries, 1):
                    sections.append(f"  {i}. {e['content']}")
                sections.append("")

        # --- DB RETRIEVAL (interactions, lectures, conversations) ---
        db_entries = retrieve_from_db(config.LOG_DB_PATH, topic, agent_name=self.name, top_k=3)
        if db_entries:
            sections.append(f"[PRIOR LEARNING — {len(db_entries)} relevant from history]")
            for i, e in enumerate(db_entries, 1):
                sections.append(f"  {i}. {e['content'][:300]}")  # cap DB entries at 300 chars
            sections.append("")

        full_prompt = "\n".join(sections)
        return self._budget_knowledge_injection(full_prompt, max_words=config.DAILY_KNOWLEDGE_BUDGET_WORDS)

    def _budget_knowledge_injection(self, prompt: str, max_words: int = 50000) -> str:
        """Truncate injected knowledge if prompt exceeds word budget."""
        words = prompt.split()
        if len(words) <= max_words:
            return prompt
        return " ".join(words[:max_words]) + "\n[Knowledge truncated due to context limits]"

    def generate_question(self, topic: str, day: int, question_num: int) -> str:
        """Generate a follow-up question about the day's topic (after lectures)."""
        system = self.inject_knowledge(
            self.build_system_prompt(day, "LEARNING", topic),
            topic,
        )
        messages = [
            {"role": "user", "content": (
                f"Topic: {topic}\n"
                f"Question {question_num}/{config.LEARNING_QUESTIONS_PER_AGENT}.\n\n"
                f"You have already received comprehensive lectures on this topic today. "
                f"Now ask ONE specific follow-up question targeting knowledge you DON'T already have. "
                f"Focus on: gaps in your knowledge, specific formulas or constants you're missing, "
                f"edge cases, counterexamples, named theorems you haven't learned yet, "
                f"or connections to other fields.\n\n"
                f"Output ONLY the question. No preamble."
            )}
        ]
        return self._call_llm(
            system, messages, temperature=0.8, max_tokens=150,
            day=day, phase="LEARNING", action=f"ask_q{question_num}",
        )

    def process_oracle_answer(self, question: str, answer: str, day: int, topic: str):
        """Store an oracle answer in the appropriate knowledge store."""
        self._default_store_answer(question, answer, day, topic)

    @abstractmethod
    def _default_store_answer(self, question: str, answer: str, day: int, topic: str):
        """Store answer per agent preference. Must be implemented by subclass."""
        pass

    def absorb_lecture(self, lecture_content: str, topic: str, subtopic: str, day: int):
        """Absorb a comprehensive lecture. Default: treat as Q&A pair.
        Override in subclasses for persona-specific absorption."""
        self._default_store_answer(subtopic, lecture_content, day, topic)

    def generate_opening(self, topic: str, day: int, peer_name: str) -> str:
        """Generate an opening message for peer conversation."""
        system = self.inject_knowledge(
            self.build_system_prompt(day, "PEER_CONVERSATION", topic),
            topic,
        )
        messages = [
            {"role": "user", "content": (
                f"You're starting a conversation with {peer_name} about '{topic}'.\n\n"
                f"You are one third of a cognitive triad. This conversation is how you LEARN from each other.\n"
                f"Do ONE of these:\n"
                f"- Share the most important thing you learned today and ask for their perspective\n"
                f"- Challenge something you think might be wrong\n"
                f"- Ask about something you're confused about\n\n"
                f"Be direct. 2-3 sentences. Make it count — this knowledge could save you on the test."
            )}
        ]
        return self._call_llm(
            system, messages, temperature=0.7, max_tokens=200,
            day=day, phase="PEER_CONVERSATION", action=f"open_{peer_name}",
        )

    def respond_to_message(self, sender: str, message: str, day: int, topic: str) -> str:
        """Respond to a peer message."""
        system = self.inject_knowledge(
            self.build_system_prompt(day, "PEER_CONVERSATION", topic),
            topic,
        )
        self.message_history.append({"role": "user", "content": f"[{sender}]: {message}"})
        response = self._call_llm(
            system, self.message_history, temperature=0.6, max_tokens=250,
            day=day, phase="PEER_CONVERSATION", action=f"reply_{sender}",
        )
        self.message_history.append({"role": "assistant", "content": response})
        return response

    def answer_test_question(self, question: str, question_type: str, day: int, use_knowledge: bool = True) -> str:
        """Answer a test question. If use_knowledge=False, answers with raw model only (no knowledge injection)."""
        base_prompt = self.build_system_prompt(day, "FINAL_TEST", "comprehensive review")

        if use_knowledge:
            # Pull from all sources: JSON stores + DB, using concept bundles for richer context
            system = self.inject_knowledge(base_prompt, question, include_deep=True, use_bundles=True)
            system = self._budget_knowledge_injection(system, max_words=config.EXAM_KNOWLEDGE_BUDGET_WORDS)
        else:
            system = base_prompt

        instruction = (
            f"HUMANITY'S LAST EXAM -- SHORT ANSWER\n\n"
            f"Question:\n{question}\n\n"
            f"INSTRUCTIONS: This is Humanity's Last Exam. You MUST answer correctly.\n"
            f"- Think step by step, reason carefully\n"
            f"- Use all your accumulated knowledge across {day - 1} days of learning\n"
            f"- Be precise and accurate -- correctness is paramount\n"
            f"- Give a clear, definitive answer\n"
            f"- After your reasoning, put your final answer on its own line as: ANSWER: [your answer]"
        )

        messages = [{"role": "user", "content": instruction}]
        return self._call_llm(
            system, messages, temperature=0.2, max_tokens=800,
            day=day, phase="FINAL_TEST", action=f"hle_answer_{question_type}",
        )

    @abstractmethod
    def manage_knowledge(self, day: int, topic: str, conversations: list[dict]):
        """Review and manage knowledge stores. Called in KNOWLEDGE_MANAGEMENT phase."""
        pass

    def propose_axiom(self, content: str, day: int, topic: str):
        """Queue an axiom proposal for Gamma to validate."""
        self.pending_axiom_proposals.append({
            "proposer": self.name,
            "content": content,
            "day": day,
            "topic": topic,
        })

    def get_and_clear_proposals(self) -> list[dict]:
        proposals = list(self.pending_axiom_proposals)
        self.pending_axiom_proposals.clear()
        return proposals

    def promote_to_deep(self, impulse_entry_id: str, day: int, topic: str = "") -> bool:
        """Move an impulse entry to deep_thinking store (knowledge promotion)."""
        entry = self.stores["impulse"].get_entry_by_id(impulse_entry_id)
        if not entry:
            return False
        self.stores["impulse"].remove_by_id(impulse_entry_id, day=day)
        self.stores["deep_thinking"].add(
            content=entry["content"],
            day=day,
            source=f"promoted_from_impulse",
            topic=topic or entry.get("topic", ""),
            reasoning_chain=f"Promoted from impulse memory for deeper analysis",
            confidence=0.6,
        )
        if self.db_logger:
            self.db_logger.log_mutation(
                day=day, agent=self.name, store_type="deep_thinking",
                mutation_type="promote", entry_id=impulse_entry_id,
                content_preview=entry["content"],
            )
        return True

    def promote_to_axiom_candidate(self, deep_entry_id: str, day: int, topic: str = ""):
        """Move a deep_thinking entry to an axiom proposal (queued for Gamma validation)."""
        entry = self.stores["deep_thinking"].get_entry_by_id(deep_entry_id)
        if not entry:
            return
        self.propose_axiom(entry["content"], day, topic or entry.get("topic", ""))

    def transfer_knowledge_to(self, recipient, store_type: str, entry: dict, day: int):
        """Transfer a specific knowledge entry to another agent's store."""
        recipient.stores[store_type].transfer_entry(entry, day, source_agent=self.name)

    def consolidate_knowledge(self, day: int):
        """Consolidate clusters of similar entries in each store into distilled summaries.
        Called periodically (e.g., every few days) to keep stores clean and dense."""
        total = 0
        for store_type, store in self.stores.items():
            if store.count() >= 10:  # Only consolidate stores with enough entries
                removed = store.consolidate(day)
                if removed > 0:
                    total += removed
                    logger.info(f"{self.name}: consolidated {removed} entries in {store_type}")
        return total

    def prepare_stores_for_exam(self):
        """Pre-compute TF-IDF caches on all stores for fast exam retrieval."""
        for store in self.stores.values():
            store.prepare_for_retrieval()

    def clear_history(self):
        """Clear conversation history (simulates sleep/memory consolidation)."""
        self.message_history.clear()

    def persist(self):
        """Save all knowledge stores to disk."""
        base = config.DATA_DIR / self.name
        self.stores["impulse"].persist(base / "impulse.json")
        self.stores["deep_thinking"].persist(base / "deep_thinking.json")
        self.stores["axiom"].persist(base / "axiom.json")

    def load(self):
        """Load all knowledge stores from disk."""
        base = config.DATA_DIR / self.name
        self.stores["impulse"].load(base / "impulse.json")
        self.stores["deep_thinking"].load(base / "deep_thinking.json")
        self.stores["axiom"].load(base / "axiom.json")

    def store_fill_percentages(self) -> dict[str, float]:
        """Return fill percentage for each store."""
        return {
            "impulse": self.stores["impulse"].count() / self.stores["impulse"].max_entries * 100,
            "deep_thinking": self.stores["deep_thinking"].count() / self.stores["deep_thinking"].max_entries * 100,
            "axiom": self.stores["axiom"].count() / self.stores["axiom"].max_entries * 100,
        }
